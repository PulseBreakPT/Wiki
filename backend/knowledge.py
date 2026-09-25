import re
import difflib
from fastapi import APIRouter, HTTPException, Query, Request, Response
from core import db, normalize, current_publication, public_entity
from models import Entity, EntityDetail, SearchResult, Source, PublicationHistory, TimelineEntry
from models import PublicationDiff

router = APIRouter(prefix='/api/v1', tags=['Arquivo público'])


@router.get('/stats')
async def stats():
    counts = await db.entity_search.aggregate([{'$group': {'_id':'$type', 'count':{'$sum':1}}}]).to_list(20)
    return {'entities':await db.entity_search.count_documents({}), 'sources':await db.sources.count_documents({}),
            'assertions':sum(x['assertion_count'] for x in await db.entity_search.find({}, {'_id':0,'assertion_count':1}).to_list(10000)),
            'types':{x['_id']:x['count'] for x in counts}}


@router.get('/entities', response_model=SearchResult)
async def entities(q: str = Query('', max_length=100), type: str = '', label: str = '', cursor: str = Query('', max_length=100),
                   limit: int = Query(12, ge=1, le=48), ids: str = Query('', max_length=4000)):
    filters = {}
    if type:
        filters['type'] = type
    if label:
        filters['label'] = label
    if ids:
        filters['id'] = {'$in':ids.split(',')[:100]}
    term = normalize(q.strip())
    suggestion = None
    if term:
        filters['search_text'] = {'$regex':re.escape(term)}
        if not await db.entity_search.count_documents(filters):
            candidates = await db.entity_search.find({k:v for k,v in filters.items() if k!='search_text'}, {'_id':0,'name':1,'aliases':1}).limit(200).to_list(200)
            names = [name for x in candidates for name in [x['name'],*x.get('aliases',[])]]
            lookup = {normalize(name):name for name in names}
            matches = difflib.get_close_matches(term, list(lookup), n=1, cutoff=0.66)
            if matches:
                suggestion = lookup[matches[0]]
                filters['search_text'] = {'$regex':re.escape(matches[0])}
    total = await db.entity_search.count_documents(filters)
    if cursor:
        filters['slug'] = {'$gt':cursor}
    items = await db.entity_search.find(filters, {'_id':0}).sort('slug',1).limit(limit+1).to_list(limit+1)
    return {'items':items[:limit], 'total':total, 'next_cursor':items[limit-1]['slug'] if len(items)>limit else None, 'suggestion':suggestion}


@router.get('/featured', response_model=list[Entity])
async def featured():
    names = ['jason-duval','lucia-caminos','vice-city','leonida-keys']
    items = await db.entity_search.find({'id':{'$in':names}}, {'_id':0}).to_list(4)
    return sorted(items, key=lambda x:names.index(x['id']))


async def detail_for(pub):
    assertions = await db.assertions.find({'id':{'$in':pub['assertion_ids']}}, {'_id':0}).to_list(40)
    order = {id:i for i,id in enumerate(pub['assertion_ids'])}
    assertions.sort(key=lambda x:order[x['id']])
    sources = {s['id']:s for s in await db.sources.find({'id':{'$in':[c['source_id'] for c in assertions]}}, {'_id':0}).to_list(40)}
    for assertion in assertions:
        assertion['source'] = sources.get(assertion['source_id'])
    related_ids = set(c['related_entity_id'] for c in assertions if c.get('related_entity_id'))
    # Incoming links are derived from currently published assertions, never drafts.
    incoming = await db.assertions.find({'related_entity_id':pub['entity_id']}, {'_id':0,'id':1,'entity_id':1}).limit(100).to_list(100)
    for link in incoming:
        current = await current_publication(link['entity_id'])
        if current and link['id'] in current['assertion_ids']:
            related_ids.add(link['entity_id'])
    related = await db.entity_search.find({'id':{'$in':list(related_ids)}}, {'_id':0}).limit(20).to_list(20)
    return {**await public_entity(pub), 'assertions':assertions, 'related':related}


@router.get('/entities/{slug}', response_model=EntityDetail)
async def entity_detail(slug: str, request: Request, response: Response, version: int | None = Query(None, ge=1)):
    identity = await db.entities.find_one({'slug':slug}, {'_id':0})
    if not identity:
        raise HTTPException(404,'Esta entidade não existe no arquivo publicado.')
    pub = await db.publications.find_one({'entity_id':identity['id'], **({'version':version} if version else {})}, {'_id':0}, sort=[('version',-1)])
    if not pub:
        raise HTTPException(404,'Publicação não encontrada.')
    etag = f'"{pub["id"]}"'
    if request.headers.get('if-none-match') == etag:
        return Response(status_code=304, headers={'ETag':etag})
    response.headers['ETag'] = etag
    return await detail_for(pub)


@router.get('/entities/{slug}/history', response_model=list[PublicationHistory])
async def history(slug: str):
    identity = await db.entities.find_one({'slug':slug}, {'_id':0})
    if not identity:
        raise HTTPException(404,'Entidade não encontrada.')
    return await db.publications.find({'entity_id':identity['id']}, {'_id':0, 'outbox':0}).sort('version',-1).limit(100).to_list(100)


@router.get('/sources', response_model=list[Source])
async def sources():
    published_ids = await db.publications.distinct('assertion_ids')
    source_ids = await db.assertions.distinct('source_id', {'id':{'$in':published_ids}})
    return await db.sources.find({'id':{'$in':source_ids}}, {'_id':0}).limit(100).to_list(100)


@router.get('/entities/{slug}/diff', response_model=PublicationDiff)
async def publication_diff(slug: str, from_version: int = Query(..., ge=1), to_version: int = Query(..., ge=1)):
    identity = await db.entities.find_one({'slug':slug}, {'_id':0})
    if not identity:
        raise HTTPException(404,'Entidade não encontrada.')
    versions=[]
    for version in [from_version,to_version]:
        pub=await db.publications.find_one({'entity_id':identity['id'],'version':version}, {'_id':0})
        if not pub:
            raise HTTPException(404,'Uma das publicações não existe.')
        versions.append(pub)
    before,after=versions
    changes=[]
    for field,label in [('name','Nome'),('summary','Resumo'),('type','Tipo'),('aliases','Nomes alternativos')]:
        a,b=before['snapshot'].get(field),after['snapshot'].get(field)
        if a!=b:
            changes.append({'field':label,'before':', '.join(a) if isinstance(a,list) else a,'after':', '.join(b) if isinstance(b,list) else b})
    claim_sets=[]
    for pub in versions:
        claims=await db.assertions.find({'id':{'$in':pub['assertion_ids']}}, {'_id':0}).to_list(40)
        mapping={}
        for claim in claims:
            key=claim['property']
            while key in mapping:
                key+=' (outra afirmação)'
            mapping[key]=claim
        claim_sets.append(mapping)
    old,new=claim_sets
    dimensions=[('value','Valor'),('excerpt','Excerto'),('source_id','Fonte'),('locator','Localização'),('origin','Origem'),('nature','Natureza'),('verification','Verificação'),('applicability','Aplicabilidade'),('related_entity_id','Relação'),('spoiler','Spoiler')]
    for prop in sorted(set(old)|set(new)):
        a,b=old.get(prop),new.get(prop)
        if not a or not b:
            changes.append({'field':prop,'before':a['value'] if a else None,'after':b['value'] if b else None})
        else:
            for field,label in dimensions:
                if a.get(field)!=b.get(field):
                    def display(value):
                        return None if value is None else ('Sim' if value else 'Não') if isinstance(value,bool) else str(value)
                    changes.append({'field':f'{prop} / {label}','before':display(a.get(field)),'after':display(b.get(field))})
    return {'entity_id':identity['id'],'from_version':from_version,'to_version':to_version,'changes':changes}


@router.get('/timeline', response_model=list[TimelineEntry])
async def timeline():
    return await db.timeline.find({}, {'_id':0}).sort('date',-1).to_list(100)
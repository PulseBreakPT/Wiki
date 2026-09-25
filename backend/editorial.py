from urllib.parse import urlparse
from fastapi import APIRouter, Depends, HTTPException
from pymongo.errors import DuplicateKeyError
from core import db, uid, now, current_publication
from models import DraftInput, Draft, SourceInput, Source
from auth import require

router = APIRouter(prefix='/api/v1/editorial', tags=['Redação privada'])
staff = require('administrador','editor','investigador','jornalista','colaborador','moderador')
editors = require('administrador','editor')


async def audit(action, target, user):
    await db.audit_events.insert_one({'id':uid(),'action':action,'target':target,'user_id':user['id'],'user_name':user['name'],'created_at':now()})


async def validate_draft(data):
    for assertion in data.assertions:
        if not await db.sources.find_one({'id':assertion.source_id}):
            raise HTTPException(422,'Todas as afirmações precisam de uma fonte existente.')
        if assertion.related_entity_id and not await current_publication(assertion.related_entity_id):
            raise HTTPException(422,'A entidade relacionada não está publicada.')
    if data.snapshot.image and not (data.snapshot.image.startswith('/media/') or urlparse(data.snapshot.image).scheme=='https'):
        raise HTTPException(422,'A imagem deve usar um endereço HTTPS ou o arquivo de imagens.')
    if data.entity_id:
        pub = await current_publication(data.entity_id)
        if not pub or pub['version'] != data.base_version:
            raise HTTPException(409,'A publicação mudou. Abra a versão atual antes de editar.')
        if pub['snapshot']['slug'] != data.snapshot.slug:
            raise HTTPException(422,'O endereço estável não pode ser alterado nesta versão.')
    elif await db.entities.find_one({'slug':data.snapshot.slug}):
        raise HTTPException(409,'Já existe uma entidade com este endereço.')


@router.get('/drafts', response_model=list[Draft])
async def drafts(user=Depends(staff)):
    return await db.drafts.find({}, {'_id':0}).sort('updated_at',-1).limit(100).to_list(100)


@router.post('/drafts', response_model=Draft, status_code=201)
async def create_draft(data: DraftInput, user=Depends(staff)):
    await validate_draft(data)
    doc = {**data.model_dump(), 'id':uid(), 'entity_id':data.entity_id or uid(), 'status':'rascunho',
           'author_id':user['id'], 'author_name':user['name'], 'created_at':now(), 'updated_at':now(), 'revision':1}
    result = Draft(**doc)
    await db.drafts.insert_one(doc)
    await audit('draft.created',result.id,user)
    return result


@router.put('/drafts/{draft_id}', response_model=Draft)
async def update_draft(draft_id: str, data: DraftInput, revision: int, user=Depends(staff)):
    draft = await db.drafts.find_one({'id':draft_id}, {'_id':0})
    if not draft:
        raise HTTPException(404,'Rascunho não encontrado.')
    if draft['status'] not in ('rascunho','devolvido'):
        raise HTTPException(409,'A revisão submetida é imutável. Devolva-a ao autor antes de editar.')
    if draft['author_id'] != user['id'] and user['role'] not in ('editor','administrador'):
        raise HTTPException(403,'Só o autor ou um editor pode alterar este rascunho.')
    await validate_draft(data)
    updates = {**data.model_dump(exclude={'entity_id'}), 'updated_at':now(), 'status':'rascunho'}
    result = await db.drafts.update_one({'id':draft_id,'revision':revision,'status':{'$in':['rascunho','devolvido']}}, {'$set':updates,'$inc':{'revision':1}})
    if result.modified_count != 1:
        raise HTTPException(409,'Outro editor alterou o rascunho. Atualize a página.')
    await audit('draft.updated',draft_id,user)
    return await db.drafts.find_one({'id':draft_id}, {'_id':0})


@router.post('/drafts/{draft_id}/submit', response_model=Draft)
async def submit(draft_id: str, user=Depends(staff)):
    draft = await db.drafts.find_one({'id':draft_id}, {'_id':0})
    if not draft:
        raise HTTPException(404,'Rascunho não encontrado.')
    if draft['author_id']!=user['id'] and user['role'] not in ('editor','administrador'):
        raise HTTPException(403,'Apenas o autor ou um editor pode submeter.')
    result = await db.drafts.update_one({'id':draft_id,'status':{'$in':['rascunho','devolvido']}}, {'$set':{'status':'em_revisao','updated_at':now()}})
    if not result.modified_count:
        raise HTTPException(409,'Este rascunho já foi submetido.')
    await audit('draft.submitted',draft_id,user)
    return await db.drafts.find_one({'id':draft_id}, {'_id':0})


@router.post('/drafts/{draft_id}/review', response_model=Draft)
async def review(draft_id: str, approve: bool, user=Depends(editors)):
    result = await db.drafts.update_one({'id':draft_id,'status':'em_revisao'}, {'$set':{'status':'aprovado' if approve else 'devolvido', 'reviewer_id':user['id'], 'reviewer_name':user['name'], 'updated_at':now()}})
    if not result.modified_count:
        raise HTTPException(409,'A revisão já não está pendente.')
    await audit('draft.approved' if approve else 'draft.returned',draft_id,user)
    return await db.drafts.find_one({'id':draft_id}, {'_id':0})


@router.post('/drafts/{draft_id}/publish')
async def publish(draft_id: str, user=Depends(editors)):
    draft = await db.drafts.find_one({'id':draft_id}, {'_id':0})
    if not draft:
        raise HTTPException(404,'Rascunho não encontrado.')
    existing = await db.publications.find_one({'id':draft_id}, {'_id':0,'id':1,'version':1})
    if existing:
        await db.drafts.update_one({'id':draft_id}, {'$set':{'status':'publicado'}})
        return {'id':existing['id'],'version':existing['version'],'message':'Publicação já concluída.'}
    if draft['status']!='aprovado':
        raise HTTPException(409,'É necessária revisão aprovada antes da publicação.')
    current = await current_publication(draft['entity_id'])
    if (current['version'] if current else 0) != draft['base_version']:
        raise HTTPException(409,'Conflito: uma versão mais recente já foi publicada.')
    if not current:
        try:
            await db.entities.update_one({'id':draft['entity_id']}, {'$setOnInsert':{'id':draft['entity_id'],'slug':draft['snapshot']['slug'],'type':draft['snapshot']['type'],'schema_version':1}}, upsert=True)
        except DuplicateKeyError:
            raise HTTPException(409,'O endereço já pertence a outra entidade.')
    assertion_ids=[]
    for index, assertion in enumerate(draft['assertions']):
        assertion_id=f'{draft_id}-{index}'
        assertion_ids.append(assertion_id)
        await db.assertions.update_one({'id':assertion_id}, {'$setOnInsert':{**assertion,'id':assertion_id,'entity_id':draft['entity_id'], 'recorded_at':now(),'reviewed_by':draft['reviewer_name']}}, upsert=True)
    origins = {a['origin'] for a in draft['assertions']}
    natures = {a['nature'] for a in draft['assertions']}
    label = 'Rumour' if 'rumor' in natures else 'Official' if origins=={'oficial'} else 'Datamined' if origins=={'datamining'} else 'Analysis' if 'interpretacao' in natures else 'Reported'
    pub={'id':draft_id,'entity_id':draft['entity_id'],'version':draft['base_version']+1,
         'snapshot':{**draft['snapshot'],'label':label},'assertion_ids':assertion_ids,'created_at':now(),
         'reason':draft['reason'],'author_name':draft['author_name'],'reviewer_name':draft['reviewer_name'],
         'outbox':{'id':uid(),'status':'pending','attempts':0}}
    # Atomic publication + outbox in ONE MongoDB document, including standalone MongoDB.
    # Immutable assertions are staged first; only this envelope makes them public.
    try:
        await db.publications.insert_one(pub)
    except DuplicateKeyError:
        raise HTTPException(409,'Esta versão já foi publicada por outro editor.')
    await db.drafts.update_one({'id':draft_id}, {'$set':{'status':'publicado','updated_at':now()}})
    await audit('publication.created',draft_id,user)
    return {'id':draft_id,'version':pub['version'],'message':'Publicação concluída. Atualização da pesquisa em processamento.'}


@router.get('/sources', response_model=list[Source])
async def all_sources(user=Depends(staff)):
    return await db.sources.find({}, {'_id':0}).limit(200).to_list(200)


@router.post('/sources', response_model=Source, status_code=201)
async def add_source(data: SourceInput, user=Depends(staff)):
    if data.url.scheme not in ('https','http'):
        raise HTTPException(422,'Endereço inválido.')
    doc={**data.model_dump(mode='json'),'id':uid(),'accessed_at':now(),'published_at':None}
    result=Source(**doc)
    await db.sources.insert_one(doc)
    await audit('source.created',result.id,user)
    return result


@router.get('/health')
async def editorial_health(user=Depends(staff)):
    return {'pending_events':await db.publications.count_documents({'outbox.status':'pending'}),
            'failed_events':await db.publications.count_documents({'outbox.status':'failed'}),
            'drafts':await db.drafts.count_documents({'status':{'$ne':'publicado'}}),
            'published':await db.publications.count_documents({})}
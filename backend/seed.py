"""Small, sourced editorial corpus. No invented game statistics or test records."""
from core import db, now, project

SOURCE_URL = 'https://www.rockstargames.com/VI/only-in-leonida'
SOURCE_ID = 'rockstar-people-places'

ENTITIES = [
    ('jason-duval', 'Jason Duval', 'personagem', ['Jason'], 'Depois de uma passagem pelo exército, Jason encontrou nas Keys uma vida entre pequenos criminosos e traficantes locais.', 'jason', '50% 35%'),
    ('lucia-caminos', 'Lucia Caminos', 'personagem', ['Lucia', 'Lúcia'], 'Determinada a mudar de vida após sair da prisão, Lucia vê num futuro com Jason uma possível saída.', 'lucia', '50% 35%'),
    ('vice-city', 'Vice City', 'local', ['VC', 'cidade'], 'As ruas de néon de Vice City fazem parte do estado de Leonida, o cenário apresentado pela Rockstar para GTA VI.', 'vice-city', 'center'),
    ('leonida-keys', 'Leonida Keys', 'local', ['Keys', 'ilhas'], 'Um dos destinos apresentados oficialmente em Leonida. A história de Jason e os negócios de Brian estão ligados às Keys.', 'keys', 'center'),
    ('cal-hampton', 'Cal Hampton', 'personagem', ['Cal'], 'Amigo de Jason e associado de Brian, Cal prefere ficar em casa a ouvir as comunicações da Guarda Costeira.', 'cal', 'center'),
    ('brian-heder', 'Brian Heder', 'personagem', ['Brian'], 'Um veterano do contrabando nas Keys, com um estaleiro e uma ligação próxima a Jason.', 'brian', 'center'),
    ('boobie-ike', 'Boobie Ike', 'personagem', ['Boobie'], 'Uma figura de Vice City com negócios no imobiliário, num clube e num estúdio de gravação.', 'boobie', 'center'),
    ('grassrivers', 'Grassrivers', 'local', ['rios'], 'Grassrivers é um dos destinos de Leonida identificados no catálogo oficial de locais e imagens da Rockstar.', 'grassrivers', 'center'),
    ('port-gellhorn', 'Port Gellhorn', 'local', ['Gellhorn'], 'Port Gellhorn integra os destinos de Leonida apresentados no material oficial de Grand Theft Auto VI.', 'port', 'center'),
    ('ambrosia', 'Ambrosia', 'local', ['Ambrósia'], 'Ambrosia é um local de Leonida com uma secção própria na apresentação oficial e imagens promocionais dedicadas.', 'ambrosia', 'center'),
    ('mount-kalaga', 'Mount Kalaga', 'local', ['Mount Kalaga National Park', 'parque nacional', 'montanha'], 'Mount Kalaga é apresentado entre os destinos de Leonida. A galeria oficial identifica o parque nacional com o mesmo nome.', 'kalaga', 'center'),
    ('leonida', 'Leonida', 'local', ['estado', 'Leonida state'], 'O estado onde se desenrola a conspiração criminal que envolve Jason e Lucia. Inclui as ruas de néon de Vice City.', 'vice-city', 'center'),
]


def claim(entity, prop, value, excerpt, related=None, spoiler=False, source=SOURCE_ID):
    return {'id': f'{entity}-{prop.lower().replace(" ", "-")}', 'entity_id': entity,
            'property': prop, 'value': value, 'source_id': source, 'excerpt': excerpt,
            'locator': f'Secção {dict((x[0], x[1]) for x in ENTITIES)[entity]}',
            'origin': 'oficial', 'nature': 'declaracao', 'verification': 'pendente',
            'applicability': 'Apresentação oficial pré-lançamento. Não confirma mecânicas nem valores da versão jogável.',
            'method': 'Consulta da página oficial e comparação com o excerto original em inglês.',
            'related_entity_id': related, 'spoiler': spoiler,
            'reviewed_by': 'Importação inicial documentada; revisão humana pendente', 'recorded_at': now()}


def initial_claims():
    claims = [
      claim('jason-duval', 'Percurso', 'Serviu no exército antes de se instalar nas Keys.', 'After a stint in the Army trying to shake off his troubled teens, he found himself in the Keys doing what he knows best, working for local drug runners.'),
      claim('jason-duval', 'Local associado', 'Leonida Keys', 'he found himself in the Keys doing what he knows best', 'leonida-keys'),
      claim('jason-duval', 'Ligação narrativa', 'Lucia Caminos', 'Meeting Lucia could be the best or worst thing to ever happen to him.', 'lucia-caminos'),
      claim('lucia-caminos', 'Passado', 'Esteve na penitenciária de Leonida.', 'Fighting for her family landed her in the Leonida Penitentiary. Sheer luck got her out.', spoiler=True),
      claim('lucia-caminos', 'Ligação narrativa', 'Jason Duval', 'A life with Jason could be her way out.', 'jason-duval'),
      claim('lucia-caminos', 'Ligação a Liberty City', 'Viveu em Liberty City com a mãe.', 'Lucia wants the good life her mom has dreamed of since their days in Liberty City'),
      claim('vice-city', 'Estado', 'Leonida', 'Only in Leonida. Home to the neon-soaked streets of Vice City and beyond.', 'leonida'),
      claim('vice-city', 'Presença oficial', 'Vice City integra os locais apresentados para GTA VI.', 'Explore Vice City'),
      claim('leonida-keys', 'Presença oficial', 'Destino apresentado oficialmente em Leonida.', 'Explore Leonida Keys'),
      claim('cal-hampton', 'Amizade', 'Jason Duval', 'Jason’s friend and a fellow associate of Brian’s', 'jason-duval'),
      claim('cal-hampton', 'Associado', 'Brian Heder', 'Jason’s friend and a fellow associate of Brian’s', 'brian-heder'),
      claim('brian-heder', 'Atividade', 'Contrabando através do seu estaleiro nas Keys.', "Brian's a classic drug runner from the golden age of smuggling in the Keys. Still moving product through his boat yard with his third wife, Lori"),
      claim('brian-heder', 'Ligação a Jason', 'Permite que Jason viva numa das suas propriedades.', 'Brian’s letting Jason live rent-free at one of his properties', 'jason-duval'),
      claim('boobie-ike', 'Negócios', 'Imobiliário, clube e estúdio de gravação.', 'a legitimate empire spanning real estate, a strip club, and a recording studio'),
      claim('boobie-ike', 'Local associado', 'Vice City', 'Boobie is a local Vice City legend', 'vice-city'),
      claim('grassrivers', 'Presença oficial', 'Destino apresentado oficialmente em Leonida.', 'Explore Grassrivers'),
      claim('port-gellhorn', 'Presença oficial', 'Destino apresentado oficialmente em Leonida.', 'Explore Port Gellhorn'),
      claim('ambrosia', 'Presença oficial', 'Destino apresentado oficialmente em Leonida.', 'Explore Ambrosia'),
      claim('mount-kalaga', 'Presença oficial', 'Destino apresentado oficialmente em Leonida.', 'Explore Mount Kalaga'),
      claim('leonida', 'Cenário', 'Estado onde se desenrola a conspiração que envolve Jason e Lucia.', 'in the middle of a criminal conspiracy stretching across the state of Leonida', source='rockstar-gta-vi'),
    ]
    return claims


async def seed_archive():
    for collection, field in [('entities','id'),('entities','slug'),('assertions','id'),('sources','id'),('publications','id'),('entity_search','id'),('drafts','id'),('users','email'),('users','id')]:
        await db[collection].create_index(field, unique=True)
    await db.publications.create_index([('entity_id', 1), ('version', -1)], unique=True)
    await db.publications.create_index([('outbox.status', 1), ('outbox.next_attempt', 1)])
    await db.entity_search.create_index([('type', 1), ('slug', 1)])
    await db.entity_search.create_index([('name', 'text'), ('aliases', 'text'), ('summary', 'text')], weights={'name': 10, 'aliases': 8, 'summary': 2}, default_language='portuguese')
    await db.sessions.create_index('expires_at', expireAfterSeconds=0)
    await db.sessions.create_index('token_hash', unique=True)
    await db.login_attempts.create_index('created_at', expireAfterSeconds=900)
    sources = [
      {'id':SOURCE_ID, 'title':'Grand Theft Auto VI — Only in Leonida', 'url':SOURCE_URL},
      {'id':'rockstar-gta-vi','title':'Grand Theft Auto VI — Apresentação oficial','url':'https://www.rockstargames.com/VI'},
      {'id':'rockstar-media','title':'Grand Theft Auto VI — Galeria oficial','url':'https://www.rockstargames.com/VI/media/screenshots'},
    ]
    for source in sources:
        await db.sources.update_one({'id':source['id']}, {'$setOnInsert':{**source, 'publisher':'Rockstar Games', 'accessed_at':now(), 'published_at':None,
          'rights':'© Rockstar Games. Material promocional disponibilizado na galeria oficial para download e partilha; sem licença aberta declarada. Citações curtas para referência editorial.'}}, upsert=True)
    claims = initial_claims()
    for item in ENTITIES:
        entity_id, name, type_, aliases, summary, image, position = item
        if await db.publications.find_one({'entity_id':entity_id}):
            continue
        await db.entities.update_one({'id':entity_id}, {'$setOnInsert':{'id':entity_id,'slug':entity_id,'type':type_,'schema_version':1}}, upsert=True)
        own_claims = [c for c in claims if c['entity_id']==entity_id]
        for assertion in own_claims:
            await db.assertions.update_one({'id':assertion['id']}, {'$setOnInsert':assertion}, upsert=True)
        pub = {'id':f'initial-{entity_id}', 'entity_id':entity_id, 'version':1,
               'snapshot':{'slug':entity_id,'name':name,'type':type_,'aliases':aliases,'summary':summary,
                           'image':f'/media/{image}.webp','image_position':position,'label':'Official'},
               'assertion_ids':[c['id'] for c in own_claims], 'created_at':now(),
               'author_name':'Importação de fontes oficiais', 'reviewer_name':'Revisão humana pendente',
               'reason':'Entrada inicial a partir de material oficial. O rótulo Official identifica a origem, não verificação independente.',
               'outbox':{'id':f'event-initial-{entity_id}','status':'pending','attempts':0}}
        await db.publications.update_one({'id':pub['id']},{'$setOnInsert':pub},upsert=True)
        await project(pub)
    events = [
      {'id':'trailer-1','date':'2023-12-04','title':'O primeiro olhar sobre Leonida','summary':'O primeiro trailer de Grand Theft Auto VI apresenta Vice City e o estado de Leonida.','source_url':'https://www.youtube.com/watch?v=QdBZY2fkU-0','type':'Trailer'},
      {'id':'trailer-2','date':'2025-05-06','title':'Jason, Lucia e as pessoas de Leonida','summary':'O segundo trailer e a apresentação oficial dão nome às personagens e aos locais do novo capítulo.','source_url':'https://www.youtube.com/watch?v=VQRLujxTm3c','type':'Trailer'},
    ]
    for event in events:
        await db.timeline.update_one({'id':event['id']}, {'$setOnInsert':event}, upsert=True)
"""Small, sourced editorial corpus. No invented game statistics or test records."""
from core import db, now, project, current_publication

SOURCE_URL = 'https://www.rockstargames.com/VI/only-in-leonida'
SOURCE_ID = 'rockstar-people-places'
CORPUS_REVISION = 2

ENTITIES = [
    ('jason-duval', 'Jason Duval', 'personagem', ['Jason'], 'Depois de uma passagem pelo exército, Jason encontrou nas Keys uma vida entre pequenos criminosos e traficantes locais.', 'jason', '50% 35%'),
    ('lucia-caminos', 'Lucia Caminos', 'personagem', ['Lucia', 'Lúcia'], 'Determinada a mudar de vida após sair da prisão, Lucia vê num futuro com Jason uma possível saída.', 'lucia', '50% 35%'),
    ('vice-city', 'Vice City', 'local', ['VC', 'cidade'], 'As ruas de néon de Vice City fazem parte do estado de Leonida, o cenário apresentado pela Rockstar para GTA VI.', 'vice-city', 'center'),
    ('leonida-keys', 'Leonida Keys', 'local', ['Keys', 'ilhas'], 'Um dos destinos apresentados oficialmente em Leonida. A história de Jason e os negócios de Brian estão ligados às Keys.', 'keys', 'center'),
    ('cal-hampton', 'Cal Hampton', 'personagem', ['Cal'], 'Amigo de Jason e associado de Brian, Cal prefere ficar em casa a ouvir as comunicações da Guarda Costeira.', 'cal', 'center'),
    ('brian-heder', 'Brian Heder', 'personagem', ['Brian'], 'Um veterano do contrabando nas Keys, com um estaleiro e uma ligação próxima a Jason.', 'brian', 'center'),
    ('boobie-ike', 'Boobie Ike', 'personagem', ['Boobie'], 'Uma figura de Vice City com negócios no imobiliário, num clube e num estúdio de gravação.', 'boobie', 'center'),
    ('dre-quan-priest', "Dre'Quan Priest", 'personagem', ["Dre'Quan", 'DreQuan Priest'], 'Empreendedor ligado à música de Vice City, focado em transformar o projeto Only Raw Records num nome relevante da cena local.', '', 'center'),
    ('real-dimez', 'Real Dimez', 'organizacao', ['Bae-Luxe', 'Roxy'], 'Dupla de rap formada por Bae-Luxe e Roxy, amigas desde o liceu e atualmente ligadas à Only Raw Records.', '', 'center'),
    ('raul-bautista', 'Raul Bautista', 'personagem', ['Raul'], 'Assaltante de bancos experiente que procura parceiros dispostos a assumir riscos cada vez maiores.', '', 'center'),
    ('moreland-850-shotgun', 'Moreland 850 Shotgun', 'arma', ['Moreland 850'], 'Espingarda identificada pela comunidade em imagens promocionais oficiais de GTA VI.', '', 'center'),
    ('duke-arms-556', 'Duke Arms 556 Assault Rifle', 'arma', ['Duke Arms 556', '556 Assault Rifle'], 'Espingarda de assalto identificada pela comunidade em imagens promocionais oficiais de GTA VI.', '', 'center'),
    ('duke-arms-ar15', 'Duke Arms AR-15 Carbine', 'arma', ['AR-15 Carbine'], 'Carabina identificada pela comunidade em imagens promocionais oficiais de GTA VI.', '', 'center'),
    ('vom-feuer-carbine-rifle', 'Vom Feuer Carbine Rifle', 'arma', ['Carbine Rifle'], 'Carabina identificada pela comunidade no Trailer 2 de GTA VI.', '', 'center'),
    ('girardi-es9', 'Girardi ES9', 'arma', ['ES9'], 'Pistola identificada pela comunidade em imagens promocionais oficiais de GTA VI.', '', 'center'),
    ('klose-k17', 'Klose K17', 'arma', ['K17'], 'Pistola identificada pela comunidade em imagens promocionais oficiais de GTA VI.', '', 'center'),
    ('morgan-revolver', 'Hawk & Little Morgan Revolver', 'arma', ['Morgan Revolver'], 'Revólver identificado pela comunidade em imagens promocionais oficiais de GTA VI.', '', 'center'),
    ('shrewsbury-grenade-launcher', 'Shrewsbury Grenade Launcher', 'arma', ['Grenade Launcher'], 'Lança-granadas identificado pela comunidade no Trailer 2 de GTA VI.', '', 'center'),
    ('progen-emerus', 'Progen Emerus', 'veiculo', ['Emerus'], 'Supercarro identificado pela comunidade na apresentação Extended Look de GTA VI.', '', 'center'),
    ('grotti-furia', 'Grotti Furia', 'veiculo', ['Furia'], 'Supercarro identificado pela comunidade no primeiro trailer de GTA VI.', '', 'center'),
    ('pegassi-tempesta', 'Pegassi Tempesta', 'veiculo', ['Tempesta'], 'Supercarro identificado pela comunidade no Trailer 2 de GTA VI.', '', 'center'),
    ('pegassi-zorrusso', 'Pegassi Zorrusso', 'veiculo', ['Zorrusso'], 'Supercarro identificado pela comunidade no primeiro trailer de GTA VI.', '', 'center'),
    ('vapid-aleutian', 'Vapid Aleutian', 'veiculo', ['Aleutian'], 'SUV identificado pela comunidade no Trailer 2 de GTA VI.', '', 'center'),
    ('pfister-astron', 'Pfister Astron', 'veiculo', ['Astron'], 'SUV identificado pela comunidade no Trailer 2 de GTA VI.', '', 'center'),
    ('fathom-fr36', 'Fathom FR36', 'veiculo', ['FR36'], 'Coupé identificado pela comunidade na apresentação Extended Look de GTA VI.', '', 'center'),
    ('vapid-benson', 'Vapid Benson', 'veiculo', ['Benson'], 'Veículo comercial identificado pela comunidade na apresentação Extended Look de GTA VI.', '', 'center'),
    ('grassrivers', 'Grassrivers', 'local', ['rios'], 'Grassrivers é um dos destinos de Leonida identificados no catálogo oficial de locais e imagens da Rockstar.', 'grassrivers', 'center'),
    ('port-gellhorn', 'Port Gellhorn', 'local', ['Gellhorn'], 'Port Gellhorn integra os destinos de Leonida apresentados no material oficial de Grand Theft Auto VI.', 'port', 'center'),
    ('ambrosia', 'Ambrosia', 'local', ['Ambrósia'], 'Ambrosia é um local de Leonida com uma secção própria na apresentação oficial e imagens promocionais dedicadas.', 'ambrosia', 'center'),
    ('mount-kalaga', 'Mount Kalaga', 'local', ['Mount Kalaga National Park', 'parque nacional', 'montanha'], 'Mount Kalaga é apresentado entre os destinos de Leonida. A galeria oficial identifica o parque nacional com o mesmo nome.', 'kalaga', 'center'),
    ('leonida', 'Leonida', 'local', ['estado', 'Leonida state'], 'O estado onde se desenrola a conspiração criminal que envolve Jason e Lucia. Inclui as ruas de néon de Vice City.', 'vice-city', 'center'),
]

ENTITY_LABELS = {
    'moreland-850-shotgun': 'Reported',
    'duke-arms-556': 'Reported',
    'duke-arms-ar15': 'Reported',
    'vom-feuer-carbine-rifle': 'Reported',
    'girardi-es9': 'Reported',
    'klose-k17': 'Reported',
    'morgan-revolver': 'Reported',
    'shrewsbury-grenade-launcher': 'Reported',
    'progen-emerus': 'Reported',
    'grotti-furia': 'Reported',
    'pegassi-tempesta': 'Reported',
    'pegassi-zorrusso': 'Reported',
    'vapid-aleutian': 'Reported',
    'pfister-astron': 'Reported',
    'fathom-fr36': 'Reported',
    'vapid-benson': 'Reported',
}


def claim(entity, prop, value, excerpt, related=None, spoiler=False, source=SOURCE_ID,
          origin='oficial', nature='declaracao', verification='pendente',
          applicability=None, method=None, locator=None):
    return {'id': f'{entity}-{prop.lower().replace(" ", "-")}', 'entity_id': entity,
            'property': prop, 'value': value, 'source_id': source, 'excerpt': excerpt,
            'locator': locator or f'Secção {dict((x[0], x[1]) for x in ENTITIES)[entity]}',
            'origin': origin, 'nature': nature, 'verification': verification,
            'applicability': applicability or 'Apresentação oficial pré-lançamento. Não confirma mecânicas nem valores da versão jogável.',
            'method': method or 'Consulta da fonte e reformulação editorial do facto documentado.',
            'related_entity_id': related, 'spoiler': spoiler,
            'reviewed_by': 'Importação inicial documentada; revisão humana pendente', 'recorded_at': now()}


def initial_claims():
    claims = [
      claim('jason-duval', 'Percurso', 'Serviu no exército antes de se instalar nas Keys.', 'After a stint in the Army trying to shake off his troubled teens, he found himself in the Keys doing what he knows best, working for local drug runners.'),
      claim('jason-duval', 'Origem social', 'Cresceu rodeado de burlões e criminosos.', 'A apresentação oficial descreve a infância de Jason num meio ligado a burlões e criminosos.'),
      claim('jason-duval', 'Local associado', 'Leonida Keys', 'he found himself in the Keys doing what he knows best', 'leonida-keys'),
      claim('jason-duval', 'Ligação narrativa', 'Lucia Caminos', 'Meeting Lucia could be the best or worst thing to ever happen to him.', 'lucia-caminos'),
      claim('lucia-caminos', 'Passado', 'Esteve na penitenciária de Leonida.', 'Fighting for her family landed her in the Leonida Penitentiary. Sheer luck got her out.', spoiler=True),
      claim('lucia-caminos', 'Treino', 'O pai ensinou-a a lutar desde muito nova.', 'A apresentação oficial diz que o pai de Lucia a ensinou a lutar desde muito pequena.'),
      claim('lucia-caminos', 'Ligação narrativa', 'Jason Duval', 'A life with Jason could be her way out.', 'jason-duval'),
      claim('lucia-caminos', 'Ligação a Liberty City', 'Viveu em Liberty City com a mãe.', 'Lucia wants the good life her mom has dreamed of since their days in Liberty City'),
      claim('vice-city', 'Estado', 'Leonida', 'Only in Leonida. Home to the neon-soaked streets of Vice City and beyond.', 'leonida'),
      claim('vice-city', 'Presença oficial', 'Vice City integra os locais apresentados para GTA VI.', 'Explore Vice City'),
      claim('leonida-keys', 'Presença oficial', 'Destino apresentado oficialmente em Leonida.', 'Explore Leonida Keys'),
      claim('cal-hampton', 'Amizade', 'Jason Duval', 'Jason’s friend and a fellow associate of Brian’s', 'jason-duval'),
      claim('cal-hampton', 'Associado', 'Brian Heder', 'Jason’s friend and a fellow associate of Brian’s', 'brian-heder'),
      claim('cal-hampton', 'Hábitos', 'Acompanha comunicações da Guarda Costeira a partir de casa.', 'O perfil oficial mostra Cal a acompanhar comunicações da Guarda Costeira a partir de casa.'),
      claim('brian-heder', 'Atividade', 'Contrabando através do seu estaleiro nas Keys.', "Brian's a classic drug runner from the golden age of smuggling in the Keys."),
      claim('brian-heder', 'Família', 'Vive e trabalha com a sua terceira mulher, Lori.', 'O perfil oficial apresenta Lori como a terceira mulher de Brian e parceira no estaleiro.'),
      claim('brian-heder', 'Ligação a Jason', 'Permite que Jason viva numa das suas propriedades.', 'Brian’s letting Jason live rent-free at one of his properties', 'jason-duval'),
      claim('boobie-ike', 'Negócios', 'Imobiliário, clube e estúdio de gravação.', 'a legitimate empire spanning real estate, a strip club, and a recording studio'),
      claim('boobie-ike', 'Local associado', 'Vice City', 'Boobie is a local Vice City legend', 'vice-city'),
      claim('boobie-ike', 'Parceria', "Dre'Quan Priest e Only Raw Records", "O perfil oficial destaca a parceria de Boobie com Dre'Quan através da Only Raw Records.", 'dre-quan-priest'),
      claim('dre-quan-priest', 'Perfil', 'É apresentado como um empreendedor mais focado no negócio do que no crime.', "O perfil oficial caracteriza Dre'Quan como alguém mais orientado para negócios do que para uma identidade de gangster."),
      claim('dre-quan-priest', 'Objetivo', 'Entrar e crescer na indústria musical de Vice City.', 'O perfil oficial indica que entrar na indústria musical sempre foi o objetivo de Dre’Quan.'),
      claim('dre-quan-priest', 'Artistas', 'Assinou a dupla Real Dimez.', "O perfil oficial confirma que Dre'Quan assinou a dupla Real Dimez.", 'real-dimez'),
      claim('dre-quan-priest', 'Parceria', 'Trabalha com Boobie Ike e a sua estrutura de entretenimento.', "A apresentação oficial liga o trabalho inicial de Dre'Quan ao clube de Boobie.", 'boobie-ike'),
      claim('real-dimez', 'Membros', 'Bae-Luxe e Roxy.', 'A apresentação oficial identifica Bae-Luxe e Roxy como as duas integrantes de Real Dimez.'),
      claim('real-dimez', 'História', 'As duas são amigas desde o liceu.', 'A apresentação oficial diz que Bae-Luxe e Roxy são amigas desde o liceu.'),
      claim('real-dimez', 'Primeiro êxito', 'Ganharam projeção com uma colaboração com o rapper DWNPLY.', 'A apresentação oficial associa a primeira projeção da dupla a uma colaboração com DWNPLY.'),
      claim('real-dimez', 'Editora', 'Estão ligadas à Only Raw Records de Dre’Quan.', 'A apresentação oficial confirma a ligação atual de Real Dimez à Only Raw Records.', 'dre-quan-priest'),
      claim('raul-bautista', 'Atividade', 'É um assaltante de bancos experiente.', 'O perfil oficial apresenta Raul como um assaltante de bancos experiente.'),
      claim('raul-bautista', 'Recrutamento', 'Procura pessoas dispostas a aceitar riscos elevados em golpes maiores.', 'O perfil oficial descreve Raul como alguém que procura novos parceiros para golpes de maior risco.'),
      claim('raul-bautista', 'Perfil de risco', 'A sua imprudência aumenta a pressão a cada golpe.', "O perfil oficial associa a imprudência de Raul a golpes progressivamente mais arriscados."),
      claim('raul-bautista', 'Referência cruzada', 'É também listado pela Grand Theft Wiki entre as personagens conhecidas de GTA VI.', 'A página comunitária de GTA VI lista Raul entre as personagens conhecidas.', source='grand-theft-wiki-gta6', origin='comunidade', nature='declaracao', applicability='Referência comunitária usada apenas para confirmação cruzada.', locator='Grand Theft Auto VI > Characters'),
      claim('moreland-850-shotgun', 'Aparição documentada', 'Identificada pela GTABase em imagens oficiais.', 'Registo comunitário baseado em screenshots promocionais.', source='gtabase-weapons', origin='comunidade', nature='interpretacao', applicability='Identificação visual comunitária; o nome pode mudar até ao lançamento.', locator='GTA 6 Weapons > Shotguns'),
      claim('duke-arms-556', 'Aparição documentada', 'Identificada pela GTABase em imagens oficiais.', 'Registo comunitário baseado em screenshots promocionais.', source='gtabase-weapons', origin='comunidade', nature='interpretacao', applicability='Identificação visual comunitária; o nome pode mudar até ao lançamento.', locator='GTA 6 Weapons > Assault Rifles'),
      claim('duke-arms-ar15', 'Aparição documentada', 'Identificada pela GTABase em imagens oficiais.', 'Registo comunitário baseado em screenshots promocionais.', source='gtabase-weapons', origin='comunidade', nature='interpretacao', applicability='Identificação visual comunitária; o nome pode mudar até ao lançamento.', locator='GTA 6 Weapons > Assault Rifles'),
      claim('vom-feuer-carbine-rifle', 'Aparição documentada', 'Identificada pela GTABase no Trailer 2.', 'Registo comunitário associado ao Trailer 2.', source='gtabase-weapons', origin='comunidade', nature='interpretacao', applicability='Identificação visual comunitária; o nome pode mudar até ao lançamento.', locator='GTA 6 Weapons > Assault Rifles'),
      claim('girardi-es9', 'Aparição documentada', 'Identificada pela GTABase em imagens oficiais.', 'Registo comunitário baseado em screenshots promocionais.', source='gtabase-weapons', origin='comunidade', nature='interpretacao', applicability='Identificação visual comunitária; o nome pode mudar até ao lançamento.', locator='GTA 6 Weapons > Handguns'),
      claim('klose-k17', 'Aparição documentada', 'Identificada pela GTABase em imagens oficiais.', 'Registo comunitário baseado em screenshots promocionais.', source='gtabase-weapons', origin='comunidade', nature='interpretacao', applicability='Identificação visual comunitária; o nome pode mudar até ao lançamento.', locator='GTA 6 Weapons > Handguns'),
      claim('morgan-revolver', 'Aparição documentada', 'Identificada pela GTABase em imagens oficiais.', 'Registo comunitário baseado em screenshots promocionais.', source='gtabase-weapons', origin='comunidade', nature='interpretacao', applicability='Identificação visual comunitária; o nome pode mudar até ao lançamento.', locator='GTA 6 Weapons > Handguns'),
      claim('shrewsbury-grenade-launcher', 'Aparição documentada', 'Identificada pela GTABase no Trailer 2.', 'Registo comunitário associado ao Trailer 2.', source='gtabase-weapons', origin='comunidade', nature='interpretacao', applicability='Identificação visual comunitária; o nome pode mudar até ao lançamento.', locator='GTA 6 Weapons > Heavy Weapons'),
      claim('progen-emerus', 'Aparição documentada', 'Identificado pela GTABase na apresentação Extended Look.', 'Registo comunitário associado ao Extended Look.', source='gtabase-vehicles', origin='comunidade', nature='interpretacao', applicability='Identificação visual comunitária; detalhes finais podem mudar.', locator='GTA 6 Vehicles > Super Cars'),
      claim('grotti-furia', 'Aparição documentada', 'Identificado pela GTABase no Trailer 1.', 'Registo comunitário associado ao Trailer 1.', source='gtabase-vehicles', origin='comunidade', nature='interpretacao', applicability='Identificação visual comunitária; detalhes finais podem mudar.', locator='GTA 6 Vehicles > Super Cars'),
      claim('pegassi-tempesta', 'Aparição documentada', 'Identificado pela GTABase no Trailer 2.', 'Registo comunitário associado ao Trailer 2.', source='gtabase-vehicles', origin='comunidade', nature='interpretacao', applicability='Identificação visual comunitária; detalhes finais podem mudar.', locator='GTA 6 Vehicles > Super Cars'),
      claim('pegassi-zorrusso', 'Aparição documentada', 'Identificado pela GTABase no Trailer 1.', 'Registo comunitário associado ao Trailer 1.', source='gtabase-vehicles', origin='comunidade', nature='interpretacao', applicability='Identificação visual comunitária; detalhes finais podem mudar.', locator='GTA 6 Vehicles > Super Cars'),
      claim('vapid-aleutian', 'Aparição documentada', 'Identificado pela GTABase no Trailer 2.', 'Registo comunitário associado ao Trailer 2.', source='gtabase-vehicles', origin='comunidade', nature='interpretacao', applicability='Identificação visual comunitária; detalhes finais podem mudar.', locator='GTA 6 Vehicles > SUVs'),
      claim('pfister-astron', 'Aparição documentada', 'Identificado pela GTABase no Trailer 2.', 'Registo comunitário associado ao Trailer 2.', source='gtabase-vehicles', origin='comunidade', nature='interpretacao', applicability='Identificação visual comunitária; detalhes finais podem mudar.', locator='GTA 6 Vehicles > SUVs'),
      claim('fathom-fr36', 'Aparição documentada', 'Identificado pela GTABase na apresentação Extended Look.', 'Registo comunitário associado ao Extended Look.', source='gtabase-vehicles', origin='comunidade', nature='interpretacao', applicability='Identificação visual comunitária; detalhes finais podem mudar.', locator='GTA 6 Vehicles > Coupes'),
      claim('vapid-benson', 'Aparição documentada', 'Identificado pela GTABase na apresentação Extended Look.', 'Registo comunitário associado ao Extended Look.', source='gtabase-vehicles', origin='comunidade', nature='interpretacao', applicability='Identificação visual comunitária; detalhes finais podem mudar.', locator='GTA 6 Vehicles > Commercial Vehicles'),
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
      {'id':'gtabase-weapons','title':'GTA 6 Weapons List','url':'https://www.gtabase.com/gta-6/weapons/','publisher':'GTABase','rights':'Fonte comunitária consultada para referência factual. Texto do VI Archive é reformulado e não reproduz a página de origem.'},
      {'id':'gtabase-vehicles','title':'GTA 6 Cars & Vehicles Database','url':'https://www.gtabase.com/gta-6/vehicles/','publisher':'GTABase','rights':'Fonte comunitária consultada para referência factual. Texto do VI Archive é reformulado e não reproduz a página de origem.'},
      {'id':'grand-theft-wiki-gta6','title':'Grand Theft Auto VI','url':'https://www.grandtheftwiki.com/GTA_VI','publisher':'Grand Theft Wiki','rights':'Fonte comunitária consultada para confirmação cruzada. O VI Archive usa redação própria e mantém ligação para a origem.'},
    ]
    default_rights = '© Rockstar Games. Material promocional disponibilizado na galeria oficial para download e partilha; sem licença aberta declarada. Referência editorial com redação própria.'
    for source in sources:
        await db.sources.update_one({'id':source['id']}, {'$setOnInsert':{**source,
          'publisher':source.get('publisher', 'Rockstar Games'), 'accessed_at':now(), 'published_at':source.get('published_at'),
          'rights':source.get('rights', default_rights)}}, upsert=True)
    claims = initial_claims()
    for item in ENTITIES:
        entity_id, name, type_, aliases, summary, image, position = item
        await db.entities.update_one({'id':entity_id}, {'$setOnInsert':{'id':entity_id,'slug':entity_id,'type':type_,'schema_version':1}}, upsert=True)
        own_claims = [c for c in claims if c['entity_id']==entity_id]
        for assertion in own_claims:
            await db.assertions.update_one({'id':assertion['id']}, {'$setOnInsert':assertion}, upsert=True)

        current = await current_publication(entity_id)
        if current:
            # Only advance records that are still managed by the checked-in baseline.
            # Human/editorial publications remain authoritative and are never overwritten here.
            managed_authors = {'Importação de fontes oficiais', 'Importação editorial documentada'}
            if current.get('author_name') not in managed_authors or current.get('version', 0) >= CORPUS_REVISION:
                continue
            version = current['version'] + 1
            pub_id = f'seed-r{CORPUS_REVISION}-{entity_id}'
            reason = f'Atualização do corpus editorial de base para a revisão {CORPUS_REVISION}.'
        else:
            version = 1
            pub_id = f'initial-{entity_id}'
            reason = 'Entrada inicial a partir de fontes rastreáveis; o rótulo distingue origem oficial de identificação comunitária.'

        label = ENTITY_LABELS.get(entity_id, 'Official')
        pub = {'id':pub_id, 'entity_id':entity_id, 'version':version,
               'snapshot':{'slug':entity_id,'name':name,'type':type_,'aliases':aliases,'summary':summary,
                           'image':f'/media/{image}.webp' if image else '','image_position':position,'label':label},
               'assertion_ids':[c['id'] for c in own_claims], 'created_at':now(),
               'author_name':'Importação editorial documentada', 'reviewer_name':'Revisão humana pendente',
               'reason':reason,
               'outbox':{'id':f'event-{pub_id}','status':'pending','attempts':0}}
        await db.publications.update_one({'id':pub['id']},{'$setOnInsert':pub},upsert=True)
        stored = await db.publications.find_one({'id':pub['id']}, {'_id':0})
        if stored:
            await project(stored)
    events = [
      {'id':'extended-look','date':'2026-08-27','title':'An Extended Look','summary':'A Rockstar publicou uma apresentação alargada de Grand Theft Auto VI, capturada integralmente em jogo na PlayStation 5.','source_url':'https://www.rockstargames.com/VI/an-extended-look','type':'Apresentação'},
      {'id':'preorders-2026','date':'2026-06-25','title':'Pré-encomendas abertas','summary':'As pré-encomendas globais de Grand Theft Auto VI abriram, com lançamento anunciado para 19 de novembro de 2026.','source_url':'https://www.rockstargames.com/newswire/article/5171972o3ak5oa/pre-order-grand-theft-auto-vi-on-june-25','type':'Anúncio'},
      {'id':'release-date-2026','date':'2025-11-06','title':'Nova data de lançamento','summary':'A Rockstar anunciou 19 de novembro de 2026 como a nova data de lançamento de Grand Theft Auto VI.','source_url':'https://www.rockstargames.com/VI','type':'Anúncio'},
      {'id':'trailer-2','date':'2025-05-06','title':'Jason, Lucia e as pessoas de Leonida','summary':'O segundo trailer e a apresentação oficial dão nome às personagens e aos locais do novo capítulo.','source_url':'https://www.youtube.com/watch?v=VQRLujxTm3c','type':'Trailer'},
      {'id':'trailer-1','date':'2023-12-04','title':'O primeiro olhar sobre Leonida','summary':'O primeiro trailer de Grand Theft Auto VI apresenta Vice City e o estado de Leonida.','source_url':'https://www.youtube.com/watch?v=QdBZY2fkU-0','type':'Trailer'},
    ]
    for event in events:
        await db.timeline.update_one({'id':event['id']}, {'$setOnInsert':event}, upsert=True)
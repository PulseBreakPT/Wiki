import os
import uuid
import unicodedata
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

ROOT = Path(__file__).parent
load_dotenv(ROOT / '.env')
load_dotenv(ROOT.parent / 'frontend' / '.env')
client = AsyncIOMotorClient(os.environ['MONGO_URL'])
db = client[os.environ['DB_NAME']]
ORIGIN = os.environ['REACT_APP_BACKEND_URL'].rstrip('/')


def now():
    return datetime.now(timezone.utc).isoformat()


def uid():
    return str(uuid.uuid4())


def normalize(value):
    return ''.join(c for c in unicodedata.normalize('NFKD', value.lower()) if not unicodedata.combining(c))


async def current_publication(entity_id):
    return await db.publications.find_one({'entity_id': entity_id}, {'_id': 0}, sort=[('version', -1)])


async def public_entity(pub):
    snapshot = pub['snapshot']
    return {**snapshot, 'id': pub['entity_id'], 'version': pub['version'],
            'updated_at': pub['created_at'], 'assertion_count': len(pub['assertion_ids'])}


async def project(pub):
    """Rebuildable, monotonic projection. The envelope is the publication authority."""
    data = await public_entity(pub)
    data['search_text'] = normalize(' '.join([data['name'], *data['aliases'], data['summary']]))
    old = await db.entity_search.find_one({'id': data['id']}, {'_id': 0, 'version': 1})
    if not old:
        await db.entity_search.update_one({'id': data['id']}, {'$setOnInsert': data}, upsert=True)
    else:
        await db.entity_search.update_one({'id': data['id'], 'version': {'$lt': data['version']}}, {'$set': data})
    await db.publications.update_one({'id': pub['id']}, {'$set': {'outbox.status': 'done', 'outbox.processed_at': now()}})
"""Independent, restart-safe projection worker; publication envelopes are the outbox."""
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from core import db, now, project


async def run_once():
    events=await db.publications.find({'outbox.status':'pending', '$or':[{'outbox.next_attempt':{'$exists':False}},{'outbox.next_attempt':{'$lte':now()}}]}, {'_id':0}).sort('created_at',1).limit(50).to_list(50)
    for event in events:
        try:
            await project(event)
        except Exception:
            attempts=event['outbox'].get('attempts',0)+1
            logging.exception('Projection failed for publication %s',event['id'])
            await db.publications.update_one({'id':event['id']},{'$set':{'outbox.status':'failed' if attempts>=8 else 'pending', 'outbox.attempts':attempts,'outbox.next_attempt':(datetime.now(timezone.utc)+timedelta(seconds=min(300,2**attempts))).isoformat()}})


async def main():
    while True:
        try:
            await run_once()
        except Exception:
            logging.exception('Worker iteration failed; retrying')
        await asyncio.sleep(1)


if __name__=='__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
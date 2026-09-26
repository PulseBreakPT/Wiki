"""Export the checked-in official corpus, without importing MongoDB or executing seed_archive.

Only the corpus declarations and pure claim factories are evaluated. Changes to the
seed's database operations are never executed by an APK build. This is a snapshot
of repository content, NOT an export of a deployed database or a live API mock.
"""
import ast
import json
import os
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'backend' / 'seed.py'
OUTPUT = ROOT / 'frontend' / 'public' / 'data' / 'archive.json'


def corpus_timestamp():
    if os.environ.get('SOURCE_DATE_EPOCH'):
        return datetime.fromtimestamp(int(os.environ['SOURCE_DATE_EPOCH']), timezone.utc).isoformat()
    try:
        return subprocess.check_output(
            ['git', 'log', '-1', '--format=%cI', '--', 'backend/seed.py'],
            cwd=ROOT, text=True, stderr=subprocess.DEVNULL,
        ).strip() or datetime.fromtimestamp(SOURCE.stat().st_mtime, timezone.utc).isoformat()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return datetime.fromtimestamp(SOURCE.stat().st_mtime, timezone.utc).isoformat()


def export_corpus():
    tree = ast.parse(SOURCE.read_text(encoding='utf-8'))
    timestamp = corpus_timestamp()
    scope = {'now': lambda: timestamp}
    declarations = []
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id in {'SOURCE_ID', 'SOURCE_URL', 'ENTITIES'} for t in node.targets
        ):
            declarations.append(node)
        elif isinstance(node, ast.FunctionDef) and node.name in {'claim', 'initial_claims'}:
            declarations.append(node)
    # Trusted, version-controlled Python declarations; deliberately no imports or async seed function.
    exec(compile(ast.Module(body=declarations, type_ignores=[]), str(SOURCE), 'exec'), scope)
    seed = next(n for n in tree.body if isinstance(n, ast.AsyncFunctionDef) and n.name == 'seed_archive')
    records = {}
    for node in seed.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in {'sources', 'events'}:
                    records[target.id] = eval(compile(ast.Expression(node.value), str(SOURCE), 'eval'), scope)
    if set(records) != {'sources', 'events'}:
        raise ValueError('Corpus layout changed: update the offline exporter before building.')
    rights = next(
        node.value for node in ast.walk(seed)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
        and node.value.startswith('© Rockstar Games.')
    )
    sources = [{**s, 'publisher': 'Rockstar Games', 'accessed_at': timestamp, 'rights': rights}
               for s in records['sources']]
    source_by_id = {s['id']: s for s in sources}
    claims = scope['initial_claims']()
    entities, history = [], {}
    for entity_id, name, kind, aliases, summary, image, position in scope['ENTITIES']:
        image_path = f'/media/{image}.webp'
        if not (ROOT / 'frontend' / 'public' / image_path.lstrip('/')).is_file():
            raise ValueError(f'Missing offline image: {image_path}')
        own = [{**c, 'source': source_by_id[c['source_id']]} for c in claims if c['entity_id'] == entity_id]
        entity = dict(id=entity_id, slug=entity_id, name=name, type=kind, aliases=aliases,
                      summary=summary, image=image_path, image_position=position, label='Official',
                      version=1, updated_at=timestamp, assertion_count=len(own), assertions=own)
        entities.append(entity)
        history[entity_id] = [{
            'id': f'initial-{entity_id}', 'entity_id': entity_id, 'version': 1,
            'created_at': timestamp, 'author_name': 'Importação de fontes oficiais',
            'reviewer_name': 'Revisão humana pendente',
            'reason': 'Entrada inicial a partir de material oficial. O rótulo Official identifica a origem, não verificação independente.',
            'snapshot': {k: v for k, v in entity.items() if k != 'assertions'},
            'assertion_ids': [c['id'] for c in own],
        }]
    entity_ids = {e['id'] for e in entities}
    if len(entity_ids) != len(entities) or len({c['id'] for c in claims}) != len(claims):
        raise ValueError('Duplicate identifiers in offline corpus.')
    if any(c.get('related_entity_id') and c['related_entity_id'] not in entity_ids for c in claims):
        raise ValueError('Unresolved entity relation in offline corpus.')
    return {
        'schema_version': 1, 'snapshot_at': timestamp, 'origin': 'backend/seed.py',
        'notice': 'Conteúdo incluído nesta edição; não sincroniza com um servidor. Datas referem-se à edição do corpus, não a uma nova verificação das fontes.',
        'entities': entities, 'history': history, 'sources': sources,
        'timeline': sorted(records['events'], key=lambda event: event['date'], reverse=True),
        'featured_ids': ['jason-duval', 'lucia-caminos', 'vice-city', 'leonida-keys'],
        'stats': {'entities': len(entities), 'sources': len(sources), 'assertions': len(claims),
                  'types': dict(Counter(e['type'] for e in entities))},
    }


if __name__ == '__main__':
    corpus = export_corpus()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(corpus, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Offline corpus: {corpus["stats"]["entities"]} entities, {corpus["stats"]["assertions"]} assertions -> {OUTPUT}')

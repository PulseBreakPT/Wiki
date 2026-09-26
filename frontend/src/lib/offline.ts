import {Entity, Revision, Source} from '../types';

export const OFFLINE = process.env.REACT_APP_OFFLINE === 'true';
type Corpus = {
  schema_version: number; snapshot_at: string; notice: string;
  entities: Entity[]; history: Record<string, Revision[]>; sources: Source[];
  timeline: unknown[]; featured_ids: string[];
  stats: {entities: number; sources: number; assertions: number; types: Record<string, number>};
};
let corpusPromise: Promise<Corpus> | undefined;

async function loadCorpus(): Promise<Corpus> {
  if (!corpusPromise) {
    corpusPromise = fetch('/data/archive.json').then(async response => {
      if (!response.ok) throw new Error('O conteúdo desta edição não está disponível. Reinstale o APK.');
      const data = await response.json();
      if (data.schema_version !== 1 || !Array.isArray(data.entities)) throw new Error('Edição offline incompatível.');
      return data;
    }).catch(error => {corpusPromise = undefined; throw error;});
  }
  return corpusPromise;
}
const normalize = (value: string) => value.normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
const searchable = (entity: Entity) => normalize([entity.name, ...entity.aliases, entity.summary].join(' '));
const summary = ({assertions, related, ...entity}: Entity) => entity;

// A small local edit-distance matcher for misspelled names; never fabricates records.
function similarity(a: string, b: string): number {
  let row = Array.from({length: b.length + 1}, (_, i) => i);
  for (let i = 1; i <= a.length; i++) {
    const next = [i];
    for (let j = 1; j <= b.length; j++) next[j] = Math.min(next[j - 1] + 1, row[j] + 1, row[j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
    row = next;
  }
  return 1 - row[b.length] / Math.max(a.length, b.length, 1);
}

export async function offlineRequest<T>(path: string, options: RequestInit = {}): Promise<T> {
  const abort = () => {if (options.signal?.aborted) throw new DOMException('Pedido cancelado.', 'AbortError');};
  abort();
  const [route, query = ''] = path.split('?');
  if ((options.method || 'GET').toUpperCase() !== 'GET' || route.startsWith('/auth') || route.startsWith('/editorial')) {
    throw new Error('Login e redação não estão disponíveis na edição offline.');
  }
  const data = await loadCorpus();
  abort();
  const params = new URLSearchParams(query);
  let result: unknown;
  if (route === '/stats') result = data.stats;
  else if (route === '/featured') result = data.featured_ids.map(id => data.entities.find(e => e.id === id)).filter(Boolean).map(e => summary(e!));
  else if (route === '/timeline') result = data.timeline;
  else if (route === '/sources') {
    const published = new Set(data.entities.flatMap(e => e.assertions?.map(c => c.source_id) || []));
    result = data.sources.filter(s => published.has(s.id));
  } else if (route === '/entities') {
    const ids = params.get('ids')?.split(',');
    const candidates = data.entities.filter(e => (!params.get('type') || e.type === params.get('type')) &&
      (!params.get('label') || e.label === params.get('label')) && (!ids || ids.includes(e.id)));
    const term = normalize((params.get('q') || '').trim()).slice(0, 100);
    let matches = candidates.filter(e => !term || searchable(e).includes(term));
    let suggestion: string | null = null;
    if (term && !matches.length) {
      const names = candidates.flatMap(e => [e.name, ...e.aliases]);
      const closest = names.map(name => ({name, score: similarity(term, normalize(name))})).sort((a, b) => b.score - a.score)[0];
      if (closest?.score >= 0.66) {
        suggestion = closest.name;
        matches = candidates.filter(e => searchable(e).includes(normalize(closest.name)));
      }
    }
    matches.sort((a, b) => a.slug < b.slug ? -1 : a.slug > b.slug ? 1 : 0);
    const total = matches.length;
    const cursor = params.get('cursor');
    if (cursor) matches = matches.filter(e => e.slug > cursor);
    const rawLimit = Number(params.get('limit') || 12);
    const limit = Number.isFinite(rawLimit) ? Math.max(1, Math.min(48, Math.floor(rawLimit))) : 12;
    result = {items: matches.slice(0, limit).map(summary), total,
      next_cursor: matches.length > limit ? matches[limit - 1].slug : null, suggestion};
  } else {
    const match = route.match(/^\/entities\/([^/]+)(?:\/(history|diff))?$/);
    const entity = match && data.entities.find(e => e.slug === decodeURIComponent(match[1]));
    if (!entity || !match) throw new Error('Esta entidade não existe na edição offline.');
    if (match[2] === 'history') result = data.history[entity.id] || [];
    else if (match[2] === 'diff') {
      const from = Number(params.get('from_version')), to = Number(params.get('to_version'));
      if (from !== entity.version || to !== entity.version) throw new Error('Esta publicação não está incluída na edição offline.');
      result = {entity_id: entity.id, from_version: from, to_version: to, changes: []};
    } else {
      if (params.has('version') && Number(params.get('version')) !== entity.version) throw new Error('Esta publicação não está incluída na edição offline.');
      const linked = new Set(entity.assertions?.map(c => c.related_entity_id).filter(Boolean));
      data.entities.forEach(e => {if (e.assertions?.some(c => c.related_entity_id === entity.id)) linked.add(e.id);});
      result = {...entity, related: data.entities.filter(e => linked.has(e.id)).map(summary)};
    }
  }
  return JSON.parse(JSON.stringify(result)) as T;
}

import {api} from './api';
import {Entity, SearchResult} from '../types';

export async function fetchAllEntities(type: string): Promise<SearchResult> {
  const items: Entity[] = [];
  const seen = new Set<string>();
  let cursor = '';
  let total = 0;
  let suggestion: string | undefined;
  do {
    const suffix = cursor ? `&cursor=${encodeURIComponent(cursor)}` : '';
    const page = await api<SearchResult>(`/entities?type=${encodeURIComponent(type)}&limit=48${suffix}`);
    total = page.total;
    suggestion = page.suggestion;
    for (const item of page.items) if (!seen.has(item.id)) { seen.add(item.id); items.push(item); }
    if (!page.next_cursor || page.next_cursor === cursor) break;
    cursor = page.next_cursor;
  } while (items.length < total);
  return {items, total, suggestion};
}

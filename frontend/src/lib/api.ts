import {OFFLINE, offlineRequest} from './offline';
const ROOT = process.env.REACT_APP_BACKEND_URL;
if (!OFFLINE && !ROOT) throw new Error('REACT_APP_BACKEND_URL não configurado.');
export const API = OFFLINE ? '' : `${ROOT}/api/v1`;
let csrf = '';
export const setCsrf = (token: string) => { csrf = token; };
export async function api<T = any>(path: string, options: RequestInit = {}): Promise<T> {
  if (OFFLINE) return offlineRequest<T>(path, options);
  const response = await fetch(`${API}${path}`, {...options, credentials: 'include', headers: {'Content-Type': 'application/json', ...(csrf ? {'X-CSRF-Token': csrf} : {}), ...options.headers}});
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(typeof data.detail === 'string' ? data.detail : 'Não foi possível concluir o pedido. Verifique os campos.');
  }
  return response.json();
}
const rawBase = process.env.PUBLIC_URL || '/';
const PUBLIC_BASE = rawBase === '/' ? '' : rawBase.replace(/\/$/, '');

/** Resolve files from public/ correctly both in the packaged APK and under GitHub Pages /Wiki. */
export function assetUrl(path: string): string {
  if (!path) return '';
  if (/^https?:\/\//i.test(path) || path.startsWith('data:') || path.startsWith('blob:')) return path;
  const normalized = path.startsWith('/') ? path : `/${path}`;
  return `${PUBLIC_BASE}${normalized}`;
}

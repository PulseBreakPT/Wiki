const {spawn, spawnSync} = require('node:child_process');
const path = require('node:path');
const frontend = path.resolve(__dirname, '..');

// Only the development entry point chooses a default. Production builds keep their explicit mode.
function previewMode(env) {
  const flag = env.REACT_APP_OFFLINE;
  if (flag && flag !== 'true' && flag !== 'false') throw new Error('REACT_APP_OFFLINE deve ser true ou false.');
  if (flag === 'true') return 'offline';
  if (flag === 'false') {
    if (!env.REACT_APP_BACKEND_URL) throw new Error('Modo online solicitado sem REACT_APP_BACKEND_URL. Configure o backend ou use o modo offline.');
    return 'online';
  }
  return env.REACT_APP_BACKEND_URL ? 'online' : 'offline';
}

function startPreview() {
  process.chdir(frontend);
  process.env.NODE_ENV = 'development';
  // Read the same .env precedence CRA uses, without writing or replacing any configuration.
  require('react-scripts/config/env');
  const mode = previewMode(process.env);
  const env = {...process.env, REACT_APP_OFFLINE: String(mode === 'offline')};
  if (mode === 'offline') {
    console.log('[preview] Edição offline: a preparar o arquivo local, sem backend.');
    const corpus = spawnSync('python3', [path.resolve(frontend, '../scripts/export_offline.py')], {
      cwd: frontend, stdio: 'inherit', env,
    });
    if (corpus.error) throw corpus.error;
    if (corpus.status !== 0) throw new Error('Não foi possível preparar o corpus offline; arranque interrompido.');
  } else {
    console.log('[preview] Backend configurado: modo online preservado.');
  }
  // Spawn CRACO directly: calling yarn start here would recurse into this wrapper.
  const child = spawn(process.execPath, [require.resolve('@craco/craco/dist/bin/craco.js'), 'start'], {
    cwd: frontend, stdio: 'inherit', env,
  });
  for (const signal of ['SIGINT', 'SIGTERM']) process.on(signal, () => child.kill(signal));
  child.on('error', error => {console.error(error.message); process.exitCode = 1;});
  child.on('exit', (code, signal) => {process.exitCode = code ?? (signal === 'SIGINT' || signal === 'SIGTERM' ? 0 : 1);});
}

module.exports = {previewMode, startPreview};
if (require.main === module) {
  try { startPreview(); } catch (error) { console.error(error.message); process.exitCode = 1; }
}

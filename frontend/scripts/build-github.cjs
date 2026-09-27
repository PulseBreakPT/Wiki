const {spawnSync} = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');

function run(command, args, options = {}) {
  const result = spawnSync(command, args, {cwd: root, stdio: 'inherit', ...options});
  if (result.error) throw result.error;
  if (result.status !== 0) process.exit(result.status || 1);
}

run('python3', ['../scripts/export_offline.py']);
run(process.execPath, [require.resolve('@craco/craco/dist/bin/craco.js'), 'build'], {
  env: {
    ...process.env,
    REACT_APP_OFFLINE: 'true',
    REACT_APP_LIVE_CHANNEL: 'true',
    REACT_APP_BACKEND_URL: '',
    PUBLIC_URL: '/Wiki',
    BUILD_PATH: 'build-github',
    GENERATE_SOURCEMAP: 'false',
    CI: 'false',
  },
});

const output = path.join(root, 'build-github');
const notices = path.join(output, 'licenses');
fs.mkdirSync(notices, {recursive: true});
for (const name of ['barlow-condensed', 'dm-sans', 'ibm-plex-sans', 'jetbrains-mono', 'unbounded']) {
  const license = path.join(root, 'node_modules', '@fontsource', name, 'LICENSE');
  fs.copyFileSync(license, path.join(notices, `${name}.txt`));
}

// GitHub Pages has no SPA rewrite rule. Serving the app as 404.html keeps BrowserRouter deep links working.
fs.copyFileSync(path.join(output, 'index.html'), path.join(output, '404.html'));
fs.writeFileSync(path.join(output, '.nojekyll'), '');
console.log('GitHub live bundle built for /Wiki. The Android app can consume it without an APK update.');

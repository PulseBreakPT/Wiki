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
  env: {...process.env, REACT_APP_OFFLINE: 'true', REACT_APP_BACKEND_URL: '', PUBLIC_URL: '/',
    BUILD_PATH: 'build-offline', GENERATE_SOURCEMAP: 'false',
    // Existing site hook/style warnings are not new Android build errors. TS errors remain fatal.
    CI: 'false'},
});
const output = path.join(root, 'build-offline');
const notices = path.join(output, 'licenses');
fs.mkdirSync(notices, {recursive: true});
for (const name of ['barlow-condensed', 'dm-sans', 'ibm-plex-sans', 'jetbrains-mono', 'unbounded']) {
  const license = path.join(root, 'node_modules', '@fontsource', name, 'LICENSE');
  fs.copyFileSync(license, path.join(notices, `${name}.txt`));
}
const assets = path.resolve(root, '../android/app/src/main/assets/www');
fs.mkdirSync(assets, {recursive: true});
// Delete generated assets only; never source, signing material or repository metadata.
for (const entry of fs.readdirSync(assets)) fs.rmSync(path.join(assets, entry), {recursive: true, force: true});
fs.cpSync(output, assets, {recursive: true});
console.log('Offline frontend copied to Android assets. No hosted URL is required.');

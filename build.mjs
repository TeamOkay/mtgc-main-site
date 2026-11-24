// Builds public/index.html: the shell with the three games, the Firebase config and the platform layer embedded.
import fs from 'node:fs';
import { cityMaps } from './src/cities.mjs';
const rd = f => fs.readFileSync(f, 'utf8');
const SHIM = '<script>(function(){var p=window.parent;window.TG_GID="__TGID__";window.claude={use:function(n){try{return p.claude.use(n)}catch(e){return Promise.resolve(null)}}}})();</script>';
const games = {};
const rr0 = rd('src/rail-rush.html'), ni = rr0.indexOf('const NETS='), nj = rr0.indexOf('\n', ni);
if (ni < 0) throw new Error('NETS not found in rail-rush.html');
const NETS = new Function('return ' + rr0.slice(ni + 'const NETS='.length, nj).replace(/;\s*$/, ''))();
const built = cityMaps(NETS);
for (const k of ['rail-rush', 'area-claiming', 'ticket-to-ride']) {
  let s = rd(`src/${k}.html`);
  if (k === 'rail-rush') {
    if (s.split('/*__MAPS__*/{}').length !== 2) throw new Error('rail-rush MAPS placeholder missing');
    s = s.replace('/*__MAPS__*/{}', () => JSON.stringify(built).replace(/<\//g, '<\\/'));
  }
  const i = s.toLowerCase().indexOf('<head>') + '<head>'.length;
  games[k] = s.slice(0, i) + SHIM + s.slice(i);
}
/* Map editor: embeds the built-in Rail Rush cities (read from rail-rush.html) so they can be opened and copied there. */
{
  let ed = rd('src/map-editor.html');
  if (ed.split('/*__BUILTINS__*/{}').length !== 2) throw new Error('map-editor placeholder missing');
  const cities = JSON.stringify(built).replace(/<\//g, '<\\/');
  const k0 = ed.toLowerCase().indexOf('<head>') + '<head>'.length;
  ed = ed.replace('/*__BUILTINS__*/{}', () => cities);
  games['map-editor'] = ed.slice(0, k0) + SHIM + ed.slice(k0);
}
/* Admin page: same wrapper as the other pages; only shown to admins (see firestore.rules: admins/{uid}). */
{
  const ad = rd('src/admin.html'), k0 = ad.toLowerCase().indexOf('<head>') + '<head>'.length;
  games['admin'] = ad.slice(0, k0) + SHIM + ad.slice(k0);
}
const blob = JSON.stringify(games).replace(/<\//g, '<\\/').split(String.fromCharCode(8232)).join('\\u2028').split(String.fromCharCode(8233)).join('\\u2029');
let shell = rd('src/shell.html');
if (shell.split('__HTML__').length !== 2 || shell.split('/*__PLATFORM__*/').length !== 2) throw new Error('shell placeholders missing');
const platform = rd('src/firebase-config.js') + '\n' + rd('src/platform.js');
if (platform.includes('</script')) throw new Error('platform contains </script');
const head = '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">' +
  '<style>body{margin:0;font:14px system-ui,sans-serif}[hidden]{display:none!important}img{max-width:100%}</style>';
shell = shell.replace('__HTML__', () => blob).replace('/*__PLATFORM__*/', () => platform);
fs.mkdirSync('public', { recursive: true });
fs.writeFileSync('public/index.html', head + shell);
console.log('built public/index.html', fs.statSync('public/index.html').size, 'bytes');

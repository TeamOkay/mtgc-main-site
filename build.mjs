// Builds public/index.html: the shell with the three games, the Firebase config and the platform layer embedded.
import fs from 'node:fs';
const rd = f => fs.readFileSync(f, 'utf8');
const SHIM = '<script>(function(){var p=window.parent;window.TG_GID="__TGID__";window.claude={use:function(n){try{return p.claude.use(n)}catch(e){return Promise.resolve(null)}}}})();</script>';
const games = {};
for (const k of ['rail-rush', 'area-claiming', 'ticket-to-ride']) {
  const s = rd(`src/${k}.html`), i = s.toLowerCase().indexOf('<head>') + '<head>'.length;
  games[k] = s.slice(0, i) + SHIM + s.slice(i);
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

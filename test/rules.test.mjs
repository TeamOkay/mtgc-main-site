/* Security-rules checks for the admin entry. NOT run in the build sandbox (the emulator download is blocked there), so run it locally:
     npm i --no-save firebase-tools @firebase/rules-unit-testing firebase
     npx firebase emulators:exec --only firestore --project demo-tg "node test/rules.test.mjs"   (needs Java)
   Expect every line to print ok. */
import fs from 'node:fs';
import { initializeTestEnvironment, assertSucceeds, assertFails } from '@firebase/rules-unit-testing';
const env = await initializeTestEnvironment({ projectId: 'demo-tg', firestore: { rules: fs.readFileSync('firestore.rules', 'utf8'), host: '127.0.0.1', port: 8080 } });
await env.withSecurityRulesDisabled(async ctx => {
  const d = ctx.firestore();
  await d.doc('admins/boss').set({ at: 1 });
  await d.doc('maps/m1').set({ owner: 'someone', name: 'Private map', share: 'private', json: '{}' });
  await d.doc('maps/m1/challenges/c1').set({ pub: false, title: 'x' });
});
const real = u => env.authenticatedContext(u, { firebase: { sign_in_provider: 'password' } }).firestore();
const guest = u => env.authenticatedContext(u, { firebase: { sign_in_provider: 'anonymous' } }).firestore();
let bad = 0;
const t = async (name, p) => { try { await p; console.log('ok  ', name); } catch (e) { bad++; console.log('FAIL', name, String(e).slice(0, 120)); } };
await t('admin can read their own admins entry', assertSucceeds(real('boss').doc('admins/boss').get()));
await t('others cannot read an admins entry', assertFails(real('other').doc('admins/boss').get()));
await t('nobody can list admins', assertFails(real('boss').collection('admins').get()));
await t('an admin cannot write admins from the client', assertFails(real('boss').doc('admins/friend').set({ at: 1 })));
await t('a user cannot make themselves admin', assertFails(real('other').doc('admins/other').set({ at: 1 })));
await t('admin can read another user\'s private map', assertSucceeds(real('boss').doc('maps/m1').get()));
await t('admin can list all maps', assertSucceeds(real('boss').collection('maps').get()));
await t('admin can read private map challenges', assertSucceeds(real('boss').doc('maps/m1/challenges/c1').get()));
await t('a normal user cannot read a private map', assertFails(real('other').doc('maps/m1').get()));
await t('a normal user cannot list all maps', assertFails(real('other').collection('maps').get()));
await t('a guest with the admin uid is not an admin', assertFails(guest('boss').doc('maps/m1').get()));
await t('games stay readable and writable for signed-in users (unchanged)', assertSucceeds(real('other').doc('games/g1').set({ name: 'x' })));
await env.cleanup();
console.log(bad ? bad + ' failed' : 'all ok');
process.exit(bad ? 1 : 0);

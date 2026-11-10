/* Unit test for the activity stamp in platform.js (no browser): fake Firestore classes, fake clock. */
global.window = {}; global.document = {}; global.localStorage = {};
require('../src/platform.js');
let now = 1000000; Date.now = () => now;
const log = [];
class DR { constructor(path, fs) { this.path = path; this.firestore = fs; }
  set(d) { log.push(['set', this.path, d]); return Promise.resolve(); }
  update(d) { log.push(['update', this.path, d]); return Promise.resolve(); }
  delete() { log.push(['delete', this.path]); return Promise.resolve(); } }
class CR { constructor(path, fs) { this.path = path; this.firestore = fs; } add(d) { log.push(['add', this.path, d]); return Promise.resolve(); } }
const fs = { doc: p => new DR(p, fs) };
window.TGPatchFirestore({ firestore: { DocumentReference: DR, CollectionReference: CR } });
let fail = 0; const ck = (n, c) => { if (!c) fail++; console.log((c ? 'PASS ' : 'FAIL ') + n); };
const stamps = () => log.filter(l => l[0] === 'update' && l[1].match(/^games\/[^/]+$/) && l[2].lastActive !== undefined);
(async () => {
  await new DR('games/g1/events/e1', fs).set({ a: 1 });
  ck('write inside a game stamps games/g1.lastActive', stamps().length === 1 && stamps()[0][1] === 'games/g1' && stamps()[0][2].lastActive === now);
  await new DR('games/g1/players/p', fs).update({ x: 1 });
  ck('second write within 5 min does not stamp again', stamps().length === 1);
  now += 301000; await new CR('games/g1/events', fs).add({ b: 1 });
  ck('after 5 minutes the next write stamps again', stamps().length === 2 && stamps()[1][2].lastActive === now);
  await new DR('games/g2', fs).update({ spectators: true });
  ck('writing the game doc itself counts (other game)', stamps().length === 3 && stamps()[2][1] === 'games/g2');
  await new DR('games/g3/members/u', fs).delete();
  ck('delete inside a game counts', stamps().length === 4 && stamps()[3][1] === 'games/g3');
  await new DR('hides/x', fs).set({ a: 1 });
  ck('writes outside games are ignored', stamps().length === 4);
  now += 400000; await new DR('games/g1', fs).update({ status: 'ended', endedAt: 1 });
  ck('ending a game does not stamp it', stamps().length === 4);
  await new DR('games/g1', fs).update({ lastActive: 5 });
  ck('an explicit lastActive write is not double-stamped (only the write itself)', stamps().length === 5);
  console.log(fail ? fail + ' failed' : 'all passed'); process.exit(fail ? 1 : 0);
})();

// Structure of the built-in city maps offered by the Map Editor.
import fs from 'node:fs';
import { cityMaps } from '../src/cities.mjs';
const rr = fs.readFileSync(new URL('../src/rail-rush.html', import.meta.url), 'utf8'), i = rr.indexOf('const NETS='), j = rr.indexOf('\n', i);
const NETS = new Function('return ' + rr.slice(i + 'const NETS='.length, j).replace(/;\s*$/, ''))();
const M = cityMaps(NETS); let n = 0, bad = 0;
const ok = (name, cond, info) => { n++; if (!cond) { bad++; console.log('FAIL', name, info ?? ''); } else console.log('PASS', name); };
const L = (k, id) => M[k].lines.find(l => l.id === id);
const nm = (k, id) => M[k].regions.find(r => r.id === id)?.name;
const ends = (k, o) => nm(k, o[0]) + ' > ' + nm(k, o[o.length - 1]);
ok('six maps', Object.keys(M).sort().join() === 'boston-augmented,boston-base,montreal-augmented,montreal-base,toronto-augmented,toronto-base', Object.keys(M));
ok('names', M['toronto-base'].name === 'Toronto-Base' && M['boston-augmented'].name === 'Boston-Augmented' && M['montreal-base'].name === 'Montréal-Base');
// Toronto
ok('Toronto-Augmented is the original', M['toronto-augmented'].lines.length === NETS.toronto.lines.length && M['toronto-augmented'].regions.length === NETS.toronto.regions.length);
ok('Toronto-Base has Lines 1, 2, 4, 5, 6 only', M['toronto-base'].lines.map(l => l.id).sort().join() === '1,2,4,5,6');
ok('Toronto-Base drops stations not on those lines', M['toronto-base'].regions.length < NETS.toronto.regions.length && M['toronto-base'].regions.every(r => r.lines.length));
// Boston
const BA = 'boston-augmented', BB = 'boston-base';
ok('Boston-Base lines', M[BB].lines.map(l => l.name).sort().join() === 'Blue Line,Green Line,Mattapan Trolley,Orange Line,Red Line', M[BB].lines.map(l => l.name));
for (const k of [BA, BB]) {
  const r = L(k, 'Red');
  ok(k + ' Red trunk Alewife > JFK/UMass', ends(k, r.order) === 'Alewife > JFK/UMass', ends(k, r.order));
  ok(k + ' Red branches A (to Ashmont) and B (to Braintree)', r.branches.length === 2 && r.branches[0].name === 'A' && ends(k, r.branches[0].order) === 'JFK/UMass > Ashmont' && r.branches[1].name === 'B' && ends(k, r.branches[1].order) === 'JFK/UMass > Braintree');
  const g = L(k, 'Green'), br = n => g.branches.filter(b => b.name === n);
  ok(k + ' Green trunk Copley > Government Center', ends(k, g.order) === 'Copley > Government Center', ends(k, g.order));
  ok(k + ' Green B to Boston College, C to Cleveland Circle', br('B').length === 1 && ends(k, br('B')[0].order) === 'Copley > Boston College' && br('C').length === 1 && ends(k, br('C')[0].order) === 'Copley > Cleveland Circle');
  ok(k + ' Green D: Copley > Riverside and Government Center > Union Square', br('D').length === 2 && ends(k, br('D')[0].order) === 'Copley > Riverside' && ends(k, br('D')[1].order) === 'Government Center > Union Square');
  ok(k + ' Green E: Copley > Heath Street and Government Center > Medford/Tufts', br('E').length === 2 && ends(k, br('E')[0].order) === 'Copley > Heath Street' && ends(k, br('E')[1].order) === 'Government Center > Medford/Tufts');
  ok(k + ' D and E pieces are grouped as one branch each', br('D').every(b => b.group === 'D') && br('E').every(b => b.group === 'E') && g.branches.filter(b => b.group).length === 4);
  ok(k + ' every branch starts on its trunk', M[k].lines.every(l => (l.branches || []).every(b => l.order.includes(b.order[0]))));
  ok(k + ' Mattapan kept separate', ends(k, L(k, 'Mattapan').order) === 'Ashmont > Mattapan');
}
const s = L(BA, 'Silver');
ok('Boston-Augmented Silver trunk South Station > Silver Line Way', ends(BA, s.order) === 'South Station > Silver Line Way', ends(BA, s.order));
ok('Silver branches SL1, SL2, SL3 as currently laid out', s.branches.map(b => b.name).join() === 'SL1,SL2,SL3' && s.branches[0].order.join() === NETS.boston.lines.find(l => l.id === 'SL1').order.slice(3).join() && s.branches[2].order.join() === NETS.boston.lines.find(l => l.id === 'SL3').order.slice(3).join());
ok('Boston-Augmented keeps the bus lines', ['66', '31', '47', '110', '94-96', '39'].every(id => L(BA, id)));
ok('old Red/Green/Silver pieces are gone', !['RedA', 'RedB', 'GreenB', 'GreenC', 'GreenD', 'GreenE', 'SL1', 'SL2', 'SL3'].some(id => L(BA, id)));
// Montréal
for (const k of ['montreal-augmented', 'montreal-base']) {
  const r = L(k, 'REM');
  ok(k + ' REM trunk Brossard > Bois-Franc', ends(k, r.order) === 'Brossard > Bois-Franc', ends(k, r.order));
  ok(k + ' REM A3 to Anse-à-l\'Orme, A4 to Deux-Montagnes', r.branches.length === 2 && r.branches[0].name === 'A3' && ends(k, r.branches[0].order) === "Bois-Franc > Anse-à-l'Orme" && r.branches[1].name === 'A4' && ends(k, r.branches[1].order) === 'Bois-Franc > Deux-Montagnes');
}
ok('Montréal-Base lines', M['montreal-base'].lines.map(l => l.id).sort().join() === '1,2,4,5,REM', M['montreal-base'].lines.map(l => l.id));
ok('Montréal-Augmented keeps buses', ['439', '747', '815', '209', '215', '121'].every(id => L('montreal-augmented', id)));
// Montréal-Augmented edits
{ const k = 'montreal-augmented', st = id => M[k].regions.find(r => r.id === id), l121 = L(k, '121');
  ok('Montpellier replaces Côte-Vertu & Muir on the 121 and is kept as an interchange', st('montpellier') && !st('cote-vertu-muir') && l121.order.includes('montpellier'), l121.order.length);
  ok('Montpellier is on the REM and the 121', st('montpellier').lines.sort().join() === '121,REM', st('montpellier').lines);
  const ends2 = (id, a, b, n) => { const o = L(k, id).order; return o[0] === a && o[o.length - 1] === b && o.length === n && L(k, id).rail === false; };
  ok('141: Saint-Michel to Honoré-Beaugrand, 33 of 49 intermediate stops removed (18 stops left)', ends2('141', 'saint-michel', 'honore-beaugrand', 18), L(k, '141').order.length);
  ok('141 passes through the 439 station at Pie-IX & Bélanger', L(k, '141').order.includes('pie-ix-belanger') && st('pie-ix-belanger').lines.includes('439'));
  ok('12: Île-des-Sœurs, Campus Bell, LaSalle', L(k, '12').order.join() === 'ile-des-surs,campus-bell,lasalle');
  ok('35: Monk to Place-Saint-Henri, 5 of 14 intermediate stops removed (11 left)', ends2('35', 'monk', 'place-saint-henri', 11), L(k, '35').order.length);
  ok('206 now ends at Des Sources & Anselme-Lavigne (10 of 19 stops removed, 9 left), not at Pierrefonds–Roxboro', ends2('206', 'fairviewpointe-claire', 'des-sources-anselme-lavigne', 9) && !st('pierrefondsroxboro').lines.includes('206'), L(k, '206').order.length);
  ok('206 shares the Des Sources & Anselme-Lavigne stop with the 209', L(k, '206').order.includes('des-sources-anselme-lavigne') && st('des-sources-anselme-lavigne').lines.sort().join() === '206,209');
  ok('every new bus stop has coordinates in the Montréal area and is on its line', ['141', '12', '35', '206'].every(id => L(k, id).order.every(s => { const r = st(s); return r && r.c[0] < -73.4 && r.c[0] > -74 && r.c[1] > 45.3 && r.c[1] < 45.8 && r.lines.includes(id); })));
  ok('no two stops share a position by accident', (() => { const seen = new Map(); for (const id of ['141', '12', '35', '206']) for (const s of L(k, id).order) { const r = st(s), key = r.c.join(); if (seen.has(key) && seen.get(key) !== s) return false; seen.set(key, s); } return true; })());
  ok('121 thinned from 20 to 10 stops, all interchanges kept', l121.order.length === 10 && ['sauve', 'montpellier', 'cote-vertu'].every(s => l121.order.includes(s)), l121.order.length);
  ok('121 order runs Sauvé, Montpellier, Côte-Vertu', l121.order[0] === 'sauve' && l121.order.indexOf('montpellier') > 0 && l121.order.indexOf('montpellier') < 9 && l121.order[9] === 'cote-vertu');
  ok('215 lost one stop and keeps Côte-Vertu and Bois-Franc', L(k, '215').order.length === 5 && L(k, '215').order[0] === 'cote-vertu' && L(k, '215').order[4] === 'bois-franc');
  ok('Côte-Vertu moved south-west of its original spot', st('cote-vertu').c[1] < 45.5143 - 0.005 && st('cote-vertu').c[0] < -73.6835 - 0.01, st('cote-vertu').c);
  { const ids = ['cote-vertu', 'du-college', 'de-la-savane', 'namur', 'plamondon', 'cote-sainte-catherine', 'snowdon'], c = ids.map(s => st(s).c), a = c[0], b = c[6];
    const dev = Math.max(...c.map(p => { const t = ((p[0] - a[0]) * (b[0] - a[0]) + (p[1] - a[1]) * (b[1] - a[1])) / (Math.pow(b[0] - a[0], 2) + Math.pow(b[1] - a[1], 2)); return Math.hypot((a[0] + t * (b[0] - a[0]) - p[0]) * 78.3, (a[1] + t * (b[1] - a[1]) - p[1]) * 111.2); }));
    ok('Orange stations from Côte-Vertu to Snowdon lie on a straight line', dev < 0.05, dev); }
  { const o = l121.order.map(s => st(s).c), mi = l121.order.indexOf('montpellier'), ang = (a, b) => Math.atan2((b[1] - a[1]) * 111.2, (b[0] - a[0]) * 78.3) * 180 / Math.PI, bend = Math.abs(ang(o[mi], o[9]) - ang(o[0], o[mi]));
    ok('121 bends less than 25 degrees at Montpellier', bend < 25, bend); }
  { const o = l121.order.map(s => st(s).c), km = (a, b) => Math.hypot((b[0] - a[0]) * 78.3, (b[1] - a[1]) * 111.2), g = o.slice(1).map((c, i) => km(o[i], c));
    ok('121 stops are mostly evenly spaced', Math.max(...g) / Math.min(...g) < 2.5, g.map(x => x.toFixed(2)).join(' ')); }
  ok('removed stops are gone from the map', !st('cote-vertu-lebeau') && !st('pierrefondsroxboro').lines.includes('206') && !st('gouin-2e-avenue'));
  ok('new buses show on their stations', st('lasalle').lines.includes('12') && st('monk').lines.includes('35') && st('saint-michel').lines.includes('141'));
  ok('Montréal-Base unaffected', !M['montreal-base'].lines.some(l => ['12', '35', '141', '121'].includes(l.id)) && M['montreal-base'].regions.some(r => r.id === 'montpellier')); }
// consistency: region.lines match the lines
for (const k of Object.keys(M)) ok(k + ' station line lists are consistent', M[k].regions.every(r => r.lines.every(id => { const l = L(k, id); return l && (l.order.includes(r.id) || (l.branches || []).some(b => b.order.includes(r.id))); })) && M[k].lines.every(l => l.order.concat(...(l.branches || []).map(b => b.order)).every(id => M[k].regions.some(r => r.id === id))));
console.log(`${n - bad}/${n}`); process.exit(bad ? 1 : 0);

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
  ok('Montpellier and Côte-Vertu & Muir are merged', st('montpellier') && !st('cote-vertu-muir') && l121.order.includes('montpellier') && !l121.order.includes('cote-vertu-muir') && l121.order.length === 20, l121.order.length);
  ok('Montpellier is on the REM and the 121', st('montpellier').lines.sort().join() === '121,REM', st('montpellier').lines);
  ok('141 runs Saint-Michel to Honoré-Beaugrand', L(k, '141') && L(k, '141').order.join() === 'saint-michel,honore-beaugrand' && L(k, '141').rail === false);
  ok('12 runs Île-des-Sœurs to LaSalle', L(k, '12').order.join() === 'ile-des-surs,lasalle' && L(k, '12').rail === false);
  ok('35 runs Monk to Place-Saint-Henri', L(k, '35').order.join() === 'monk,place-saint-henri' && L(k, '35').rail === false);
  ok('new buses show on their stations', st('lasalle').lines.includes('12') && st('monk').lines.includes('35') && st('saint-michel').lines.includes('141'));
  ok('Montréal-Base unaffected', !M['montreal-base'].lines.some(l => ['12', '35', '141', '121'].includes(l.id)) && M['montreal-base'].regions.some(r => r.id === 'montpellier')); }
// consistency: region.lines match the lines
for (const k of Object.keys(M)) ok(k + ' station line lists are consistent', M[k].regions.every(r => r.lines.every(id => { const l = L(k, id); return l && (l.order.includes(r.id) || (l.branches || []).some(b => b.order.includes(r.id))); })) && M[k].lines.every(l => l.order.concat(...(l.branches || []).map(b => b.order)).every(id => M[k].regions.some(r => r.id === id))));
console.log(`${n - bad}/${n}`); process.exit(bad ? 1 : 0);

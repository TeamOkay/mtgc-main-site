// Builds the built-in city maps offered by the Map Editor ("Edit a city") from the original Rail Rush networks (NETS in rail-rush.html).
// Each city comes in two variants:
//   <City>-Augmented  every line of the original city (Boston, Montréal: Red, Green, Silver and the REM merged into branching lines)
//   <City>-Base       only the main rail lines
// Output format = the Map Editor's import format: { name, regions, lines[{ id, name, color, rail, order, branches?: [{ name, group?, order }] (pieces with the same group are one branch) }] }.
// A branch's first station is the station where it leaves the line's trunk.

const RAIL = /^(\d|A\d?|LSE|LSW|UP|Red[AB]|Orange|Blue|Green[BCDE]|Mattapan)$/;   // how Rail Rush has told rail from bus

import { mtlBuses, thinEven, respace } from './mtl-buses.mjs';

export function cityMaps(NETS) {
  const out = {};
  const get = (c, id) => { const l = NETS[c].lines.find(x => x.id === id); if (!l) throw new Error(`line ${c}/${id} not found`); return l; };
  const at = (o, id, what) => { const i = o.indexOf(id); if (i < 0) throw new Error(`station ${id} not on ${what}`); return i; };
  const upto = (o, id, w) => o.slice(0, at(o, id, w) + 1);
  const from = (o, id, w) => o.slice(at(o, id, w));
  const same = (a, b, w) => { if (a.join() !== b.join()) throw new Error('trunk mismatch: ' + w); };
  const plain = (c, id) => { const l = get(c, id); return { id: l.id, name: l.name, color: l.color, rail: RAIL.test(l.id), order: l.order.slice() }; };

  function build(name, city, lines, extra = [], over = {}, names = {}) {
    const used = new Set();
    lines.forEach(l => { l.order.concat(...(l.branches || []).map(b => b.order)).forEach(i => used.add(i)); });
    const regions = NETS[city].regions.concat(extra).filter(r => used.has(r.id)).map(r => {
      const ls = lines.filter(l => l.order.includes(r.id) || (l.branches || []).some(b => b.order.includes(r.id))).map(l => l.id);
      return Object.assign({}, r, over[r.id] ? { c: over[r.id] } : {}, names[r.id] ? { name: names[r.id] } : {}, { lines: ls });
    });
    return { name, regions, lines };
  }
  // Replace `ids` (original lines) by `merged`, placed where the first of them was; every other line is kept as it was.
  function swap(city, ids, merged) {
    const out = []; let done = false;
    NETS[city].lines.forEach(l => {
      if (ids.includes(l.id)) { if (!done) { out.push(...merged); done = true; } } else out.push(plain(city, l.id));
    });
    return out;
  }

  /* ---- Toronto ---- */
  out['toronto-augmented'] = build('Toronto-Augmented', 'toronto', NETS.toronto.lines.map(l => plain('toronto', l.id)));
  out['toronto-base'] = build('Toronto-Base', 'toronto', ['1', '2', '4', '5', '6'].map(id => plain('toronto', id)));

  /* ---- Boston ---- */
  const RA = get('boston', 'RedA'), RB = get('boston', 'RedB');
  const red = { id: 'Red', name: 'Red Line', color: RA.color, rail: true,
    order: upto(RA.order, 'jfk-umass', 'RedA'),
    branches: [{ name: 'A', order: from(RA.order, 'jfk-umass', 'RedA') }, { name: 'B', order: from(RB.order, 'jfk-umass', 'RedB') }] };
  same(upto(RB.order, 'jfk-umass', 'RedB'), red.order, 'Red');
  const GB = get('boston', 'GreenB'), GC = get('boston', 'GreenC'), GD = get('boston', 'GreenD'), GE = get('boston', 'GreenE');
  const gtrunk = GB.order.slice(0, at(GB.order, 'copley', 'GreenB') + 1).reverse();   // Copley ... Government Center
  if (gtrunk[0] !== 'copley' || gtrunk[gtrunk.length - 1] !== 'government-center') throw new Error('Green trunk');
  const north = (l, w) => l.order.slice(0, at(l.order, 'government-center', w) + 1).reverse();   // Government Center -> toward Union Sq / Medford
  const green = { id: 'Green', name: 'Green Line', color: GB.color, rail: true, order: gtrunk, branches: [
    { name: 'B', order: from(GB.order, 'copley', 'GreenB') },
    { name: 'C', order: from(GC.order, 'copley', 'GreenC') },
    { name: 'D', group: 'D', order: from(GD.order, 'copley', 'GreenD') },
    { name: 'D', group: 'D', order: north(GD, 'GreenD') },
    { name: 'E', group: 'E', order: from(GE.order, 'copley', 'GreenE') },
    { name: 'E', group: 'E', order: north(GE, 'GreenE') }] };
  const S1 = get('boston', 'SL1'), S2 = get('boston', 'SL2'), S3 = get('boston', 'SL3');
  const strunk = upto(S1.order, 'silver-line-way', 'SL1');
  same(upto(S2.order, 'silver-line-way', 'SL2'), strunk, 'SL2'); same(upto(S3.order, 'silver-line-way', 'SL3'), strunk, 'SL3');
  const silver = { id: 'Silver', name: 'Silver Line', color: S1.color, rail: false, order: strunk, branches: [
    { name: 'SL1', order: from(S1.order, 'silver-line-way', 'SL1') },
    { name: 'SL2', order: from(S2.order, 'silver-line-way', 'SL2') },
    { name: 'SL3', order: from(S3.order, 'silver-line-way', 'SL3') }] };
  let bl = swap('boston', ['RedA', 'RedB'], [red]);
  bl = bl.flatMap(l => l.id === 'GreenB' ? [green] : ['GreenC', 'GreenD', 'GreenE'].includes(l.id) ? [] : l.id === 'SL1' ? [silver] : ['SL2', 'SL3'].includes(l.id) ? [] : [l]);
  out['boston-augmented'] = build('Boston-Augmented', 'boston', bl);
  const pick = ids => ids.map(id => bl.find(l => l.id === id));
  out['boston-base'] = build('Boston-Base', 'boston', pick(['Red', 'Orange', 'Blue', 'Green', 'Mattapan']));

  /* ---- Montréal ---- */
  const MA = get('montreal', 'A'), M3 = get('montreal', 'A3');
  const rem = { id: 'REM', name: 'REM', color: MA.color, rail: true, order: upto(MA.order, 'bois-franc', 'A'), branches: [
    { name: 'A3', order: M3.order.slice() }, { name: 'A4', order: from(MA.order, 'bois-franc', 'A') }] };
  if (M3.order[0] !== 'bois-franc') throw new Error('A3 start');
  const ml = swap('montreal', ['A', 'A3'], [rem]);
  // Augmented-only edits: the 121's Côte-Vertu & Muir stop is the REM's Montpellier station, and three short bus links are added.
  const b121 = ml.find(l => l.id === '121'), mi = at(b121.order, 'cote-vertu-muir', '121');
  b121.order[mi] = 'montpellier';
  const reg = id => NETS.montreal.regions.find(r => r.id === id), over = {};
  // Côte-Vertu moves south-west so the 121 runs straight from Sauvé through Montpellier; the Orange stations out to Snowdon are re-laid evenly on a straight line from it.
  over['cote-vertu'] = [-73.702, 45.506];
  const oOrder = get('montreal', '2').order, oi = oOrder.indexOf('cote-vertu'), osn = oOrder.indexOf('snowdon');
  Object.assign(over, respace(oOrder.slice(oi, osn + 1), ['cote-vertu', 'snowdon'], id => over[id] || reg(id).c));
  const pos = id => over[id] || reg(id).c, isIC = id => id === 'montpellier' || reg(id).lines.length > 1;
  // Straighten a bus route between its anchors, drop `remove` non-interchange stops evenly, then space the rest evenly.
  const thinBus = (l, anchors, remove) => {
    Object.assign(over, respace(l.order, anchors, pos));
    l.order = thinEven(l.order.map(id => ({ id })), x => pos(x.id), x => isIC(x.id), remove).map(x => x.id);
    Object.assign(over, respace(l.order, anchors, pos));
  };
  thinBus(b121, ['sauve', 'montpellier', 'cote-vertu'], 10);
  thinBus(ml.find(l => l.id === '215'), ['cote-vertu', 'bois-franc'], 1);
  const mb = mtlBuses(reg, { '141': 33, '35': 5, '206': 10, '209': 11 });   // buses 141, 35, 206 and the 209's southern stretch thinned; 12 as is
  // the 815 is replaced by the 209, which now runs Pierrefonds–Roxboro > Des Sources > YUL (northern stops as they were)
  const s209 = mb.lines.find(l => l.id === '209'), l209 = ml.find(l => l.id === '209');
  if (l209.order[0] !== 'des-sources' || s209.order[0] !== 'des-sources') throw new Error('209 start');
  l209.order = s209.order.slice(1).reverse().concat(l209.order);
  ml.splice(ml.findIndex(l => l.id === '815'), 1);
  ml.push(...mb.lines.filter(l => l.id !== '209'));
  out['montreal-augmented'] = build('Montréal-Augmented', 'montreal', ml, mb.regions, over, { 'pie-ix-d-amos': 'Pie-IX & Henri-Bourassa' });
  out['montreal-base'] = build('Montréal-Base', 'montreal', ['1', '2', '4', '5', 'REM'].map(id => ml.find(l => l.id === id)), [], over);
  return out;
}

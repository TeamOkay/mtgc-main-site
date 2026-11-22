// Stop-by-stop Montréal bus lines added to Montréal-Augmented: 141, 12, 35, 48/49, the (2026-network) 206, and the 209's stretch from Des Sources to YUL.
// Stop names/order come from STM route listings. STM's coordinate file was not reachable, so stops are placed APPROXIMATELY:
// items with `c` (or an existing station `id`) are anchors; the stops between two anchors are spaced evenly along the straight line.
// Replace with real GTFS stop coordinates when available.
const slug = s => s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/&/g, ' ').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
const E = id => ({ id });                       // an existing station (the stop is merged into it)
const S = (n, c) => (c ? { n, c } : { n });     // a new stop (c = approximate [lon, lat] anchor)
const K = (n, c) => Object.assign(S(n, c), { keep: true });   // a new stop that thinning never removes

export const ROUTES = [
  { id: '141', name: '141 Saint-Michel / Honoré-Beaugrand (bus)', color: '#7cb342', stops: [
    E('saint-michel'),
    S('Jean-Talon & 13e Avenue'), S('Jean-Talon & 15e Avenue'), S('Jean-Talon & 17e Avenue'), S('Jean-Talon & 18e Avenue'),
    E('pie-ix-belanger'),                                   // Bélanger / Pie-IX
    S('Bélanger & 24e Avenue'), S('Bélanger & 26e Avenue'), S('Bélanger & 28e Avenue'), S('Bélanger & 30e Avenue'), S('Bélanger & 33e Avenue'),
    S('Bélanger & 35e Avenue'), S('Bélanger & Viau (Institut de Cardiologie)'), S('Bélanger & 40e Avenue'), S('Bélanger & 43e Avenue'),
    S("Bélanger & de l'Assomption"), S('Bélanger & Châtelain'), S('Bélanger & de Pontoise'), S('Bélanger & Lacordaire'), S('Bélanger & Valdombre'),
    S("Bélanger & d'Avila"), S('Bélanger & Dumesnil'), S('Bélanger & Daveluy'), S('Bélanger & Langelier'), S('Bélanger & Jean-Milot'),
    S('Bélanger & Étienne-Bouchard'), S('Des Halles & Bélanger', [-73.5600, 45.5960]), S('Des Halles & Jean-Talon', [-73.5560, 45.5990]),
    S("Jean-Talon & des Galeries-d'Anjou", [-73.5520, 45.6030]), S("Métropolitain & des Galeries d'Anjou"), S('Bourgneuf & Bertin'), S('Bourgneuf & Bodinier'),
    S('De Châteauneuf & Goncourt', [-73.5455, 45.6045]), S('De Châteauneuf & Joseph-Renaud'), S('De Châteauneuf & Talcy'), S('De Châteauneuf & Rabelais'),
    S('De Châteauneuf & de la Loire'), S('De Châteauneuf & de Fougeray'), S('De Châteauneuf & des Ormeaux'),
    S('Des Ormeaux & Georges', [-73.5415, 45.6015]), S('Des Ormeaux & Chaumont'), S('Des Ormeaux & Yves-Prévost'), S('Des Ormeaux & Éric'),
    S('Des Ormeaux & Sentennes'), S('Des Ormeaux & Tiffin'), S('Des Ormeaux & de Grosbois'), S('Des Ormeaux & de Forbin-Janson'),
    S('Des Ormeaux & Sherbrooke', [-73.5375, 45.5978]), S('Sherbrooke & Baldwin'), S('Sherbrooke & Saint-Donat'),
    E('honore-beaugrand')] },
  { id: '12', name: '12 Île-des-Sœurs / LaSalle (bus)', color: '#5e35b1', stops: [
    E('ile-des-surs'), S('Campus Bell', [-73.5430, 45.4685]), E('lasalle')] },       // LaSalle = Gaétan-Laberge / Gilberte-Dubé
  { id: '35', name: '35 Monk / Place-Saint-Henri (bus)', color: '#ff7043', stops: [
    E('monk'),                                              // Monk / Allard
    S('Allard & Laurendeau'), S('Laurendeau & Egan'), S('Laurendeau & Springland'), S('Laurendeau & de Sève'),
    S('Laurendeau & Jolicoeur', [-73.5828, 45.4555]), S('Laurendeau & Jacques-Hertel'), S('Laurendeau & le Caron'), S("Laurendeau & de l'Église", [-73.5775, 45.4620]),
    S('Saint-Rémi & Cabot'), S('Saint-Rémi & Sainte-Émilie'), S('Saint-Rémi & Notre-Dame', [-73.5815, 45.4720]), S('Notre-Dame & de Courcelle'),
    S('Square Sir-George-Étienne-Cartier', [-73.5885, 45.4745]), S('Saint-Jacques & Saint-Philippe', [-73.5882, 45.4762]),
    E('place-saint-henri')] },
  { id: '48', name: '48/49 Henri-Bourassa / Pie-IX (bus)', color: '#827717', stops: [   // the 48 Perras and 49 Armand-Bombardier share this stretch (the 48's stops, towards Pie-IX)
    E('henri-bourassa'), S('Henri-Bourassa & Christophe-Colomb'), S('Henri-Bourassa & de Saint-Firmin'), S('Henri-Bourassa & Saint-Michel'), S('Henri-Bourassa & de Bruxelles'),
    E('pie-ix-d-amos')] },                                  // Henri-Bourassa / Pie-IX = the 439's last station (renamed in cities.mjs)
  { id: '206', name: '206 Roger-Pilon (Fairview–Pointe-Claire / Des Sources) (bus)', color: '#00897b', elbow: true, stops: [   // elbow: straight up from the first stop, then one right turn to the last
    E('fairviewpointe-claire'),
    S('Brunswick & Auto Plaza'), S('Saint-Jean & Blue Haven'), S('Blue Haven & des Pins'), S('Blue Haven & Jourdain'), S('Blue Haven & Viking'),
    S('Blue Haven & Lake'), S('Lake & Hemingway'), S('Hemingway & Greenfield'), S('Baffin & Roger-Pilon'),
    S('Roger-Pilon & Tecumseh'), S('Roger-Pilon & Fredmir'), S('Roger-Pilon & Manuel'), S('Roger-Pilon & Westpark'),
    S('Westpark & Wilson'), S('Westpark & Anselme-Lavigne'), S('Anselme-Lavigne & Oslo'), S('Anselme-Lavigne & Greenview'),
    E('des-sources-anselme-lavigne')] },
  { id: '209', name: '209 Des Sources (bus)', color: '#3949ab', stops: [   // the stretch Des Sources -> YUL only (merged into the 209 in cities.mjs; the 815 is gone)
    E('des-sources'),
    S('Des Sources & Transcanadienne'), S('Des Sources & Avro'), S("Des Sources & de l'Aviation"), S('Des Sources & Gérald-Hervey'), S('Des Sources & Reverchon'),
    S('Des Sources & 1733'), S('Des Sources & Belmont'), S('Des Sources & Chanteclerc', [-73.7820, 45.4455]),
    S('Bord-du-Lac & Lakebreeze'), S("Bord-du-Lac & de l'Église"), S('Bord-du-Lac & Lake'), S('Bord-du-Lac & Thrush'), S('Bord-du-Lac & Neptune', [-73.7600, 45.4408]),
    S('Dawson & Stream', [-73.7518, 45.4420]), S('Dawson & Saint-Louis'), S('Dawson & Thorncrest'), S('Dawson & École Dorval-Jean-XXIII'), S('Dawson & Claude'),
    S('Dawson & Fénelon'), S('Dawson & Lepage'), S('Dawson & Garden', [-73.7510, 45.4467]), S('Dorval & Dawson'), S('Dorval & Carson'),
    K('Terminus Dorval', [-73.7468, 45.4479]),
    E('yul-aeroport-montreal-trudeau')] },
];

/** Builds { lines, regions } for the routes above. `byId` looks up an existing station by id. */
export function mtlBuses(byId, remove = {}) {
  const lines = [], regions = [], seen = new Set();
  for (const R of ROUTES) {
    const pts = R.stops.map(s => {
      if (s.id) { const r = byId(s.id); if (!r) throw new Error('missing station ' + s.id + ' for ' + R.id); return { id: s.id, c: r.c }; }
      return { id: slug(s.n), n: s.n, c: s.c || null, keep: !!s.keep };
    });
    pts.forEach((p, i) => {
      if (p.c) return;
      let a = i - 1, b = i + 1; while (!pts[a].c) a--; while (!pts[b].c) b++;
      const t = (i - a) / (b - a); p.c = [pts[a].c[0] + (pts[b].c[0] - pts[a].c[0]) * t, pts[a].c[1] + (pts[b].c[1] - pts[a].c[1]) * t].map(v => Math.round(v * 1e4) / 1e4);
      p.guess = true;
    });
    // elbow routes: new stops are spread evenly along an L (north from the first stop to the last stop's latitude, then east)
    const onL = list => { const A = list[0].c, B = list[list.length - 1].c, up = Math.abs(B[1] - A[1]) * 111.2, right = Math.abs(B[0] - A[0]) * 78.3, tot = up + right;
      list.forEach((p, i) => { if (!p.n) return; const d = tot * i / (list.length - 1);
        p.c = d <= up ? [A[0], A[1] + (B[1] - A[1]) * (d / up)] : [A[0] + (B[0] - A[0]) * ((d - up) / right), B[1]]; p.c = p.c.map(v => Math.round(v * 1e4) / 1e4); }); };
    if (R.elbow) onL(pts);
    let keep = pts;
    if (remove[R.id]) keep = thinEven(pts, p => p.c, p => !p.n || p.keep, remove[R.id]);
    if (R.elbow) onL(keep);
    keep.forEach(p => { if (p.n) { if (seen.has(p.id) || byId(p.id)) throw new Error('duplicate stop id ' + p.id); seen.add(p.id); regions.push({ id: p.id, name: p.n, c: p.c, lines: [], pt: 1 }); } });
    lines.push({ id: R.id, name: R.name, color: R.color, rail: false, order: keep.map(p => p.id) });
  }
  return { lines, regions };
}

const dist = (a, b) => Math.hypot((a[0] - b[0]) * 0.7, a[1] - b[1]);
/** Drops `remove` stops from `items` ({c}), never a stop for which isMand() is true, leaving the spacing along the line as even as possible. */
export function thinEven(items, posOf, isMand, remove) {
  const n = items.length, s = [0]; for (let i = 1; i < n; i++) s.push(s[i - 1] + dist(posOf(items[i - 1]), posOf(items[i])));
  const mand = items.map((x, i) => (i === 0 || i === n - 1 || isMand(x)) ? i : -1).filter(i => i >= 0);
  const free = n - mand.length, extras = Math.max(0, Math.min(free, free - remove)), total = s[n - 1];
  const segs = []; for (let k = 0; k + 1 < mand.length; k++) segs.push({ a: mand[k], b: mand[k + 1], m: mand[k + 1] - mand[k] - 1, len: s[mand[k + 1]] - s[mand[k]] });
  let used = 0; segs.forEach(g => { g.q = total ? g.len * extras / total : 0; g.e = Math.min(g.m, Math.floor(g.q)); used += g.e; });
  while (used < extras) { const g = segs.filter(x => x.e < x.m).sort((x, y) => (y.q - y.e) - (x.q - x.e))[0]; if (!g) break; g.e++; used++; }
  const keep = new Set(mand);
  segs.forEach(g => { const taken = new Set(); for (let j = 1; j <= g.e; j++) { const t = s[g.a] + g.len * j / (g.e + 1); let best = -1, bd = 1e9; for (let i = g.a + 1; i < g.b; i++) if (!taken.has(i) && Math.abs(s[i] - t) < bd) { bd = Math.abs(s[i] - t); best = i; } taken.add(best); keep.add(best); } });
  return items.filter((_, i) => keep.has(i));
}
/** Spaces the stops between consecutive anchors (ids in `anchors`) evenly along straight legs. Returns { id: [lon, lat] }. */
export function respace(order, anchors, posOf) {
  const out = {}, ai = order.map((id, i) => anchors.includes(id) ? i : -1).filter(i => i >= 0);
  for (let k = 0; k + 1 < ai.length; k++) { const a = ai[k], b = ai[k + 1], pa = posOf(order[a]), pb = posOf(order[b]);
    for (let i = a + 1; i < b; i++) { const t = (i - a) / (b - a); out[order[i]] = [Math.round((pa[0] + (pb[0] - pa[0]) * t) * 1e4) / 1e4, Math.round((pa[1] + (pb[1] - pa[1]) * t) * 1e4) / 1e4]; } }
  return out;
}

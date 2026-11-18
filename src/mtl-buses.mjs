// Stop-by-stop Montréal bus lines added to Montréal-Augmented: 141, 12, 35 and the (2026-network) 206.
// Stop names/order come from STM route listings. STM's coordinate file was not reachable, so stops are placed APPROXIMATELY:
// items with `c` (or an existing station `id`) are anchors; the stops between two anchors are spaced evenly along the straight line.
// Replace with real GTFS stop coordinates when available.
const slug = s => s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/&/g, ' ').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
const E = id => ({ id });                       // an existing station (the stop is merged into it)
const S = (n, c) => (c ? { n, c } : { n });     // a new stop (c = approximate [lon, lat] anchor)

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
  { id: '206', name: '206 Roger-Pilon (Fairview–Pointe-Claire / Pierrefonds-Roxboro) (bus)', color: '#00897b', stops: [
    E('fairviewpointe-claire'),
    S('Brunswick & Auto Plaza'), S('Saint-Jean & Blue Haven', [-73.8245, 45.4790]), S('Blue Haven & des Pins'), S('Blue Haven & Jourdain'), S('Blue Haven & Viking'),
    S('Blue Haven & Lake'), S('Lake & Hemingway'), S('Hemingway & Greenfield'), S('Baffin & Roger-Pilon', [-73.7995, 45.4838]),
    S('Roger-Pilon & Tecumseh'), S('Roger-Pilon & Fredmir'), S('Roger-Pilon & Manuel'), S('Roger-Pilon & Westpark'),
    S('Westpark & Wilson'), S('Westpark & Anselme-Lavigne'), S('Anselme-Lavigne & Oslo'), S('Anselme-Lavigne & Greenview'),
    E('des-sources-anselme-lavigne'),                       // Anselme-Lavigne / des Sources
    S('Des Sources & Belcourt'), S('14e Rue & 19e Avenue'), S('14e Rue & 18e Avenue'), S('14e Rue & 15e Avenue'), S('14e Rue & 13e Avenue'),
    S('11e Avenue & 14e Rue'), S('11e Avenue & 11e Rue'), S('11e Avenue & 9e Rue'), S('Centre-Commercial & 4e Avenue'), S('Gouin & 2e Avenue'),
    E('pierrefondsroxboro')] },                             // Gouin / 4e Avenue = the Pierrefonds–Roxboro station
];

/** Builds { lines, regions } for the routes above. `byId` looks up an existing station by id. */
export function mtlBuses(byId) {
  const lines = [], regions = [], seen = new Set();
  for (const R of ROUTES) {
    const pts = R.stops.map(s => {
      if (s.id) { const r = byId(s.id); if (!r) throw new Error('missing station ' + s.id + ' for ' + R.id); return { id: s.id, c: r.c }; }
      return { id: slug(s.n), n: s.n, c: s.c || null };
    });
    pts.forEach((p, i) => {
      if (p.c) return;
      let a = i - 1, b = i + 1; while (!pts[a].c) a--; while (!pts[b].c) b++;
      const t = (i - a) / (b - a); p.c = [pts[a].c[0] + (pts[b].c[0] - pts[a].c[0]) * t, pts[a].c[1] + (pts[b].c[1] - pts[a].c[1]) * t].map(v => Math.round(v * 1e4) / 1e4);
      p.guess = true;
    });
    pts.forEach(p => { if (p.n) { if (seen.has(p.id) || byId(p.id)) throw new Error('duplicate stop id ' + p.id); seen.add(p.id); regions.push({ id: p.id, name: p.n, c: p.c, lines: [], pt: 1 }); } });
    lines.push({ id: R.id, name: R.name, color: R.color, rail: false, order: pts.map(p => p.id) });
  }
  return { lines, regions };
}

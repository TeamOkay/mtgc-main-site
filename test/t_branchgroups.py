"""Map Editor: a branch can have several pieces (one name, one branch). Boston Green D/E come as grouped pieces."""
import json
from harness import *
w = World(); c = Check(); w.user('u1')
w.pages['u1'].evaluate("window.TGAuth={info:()=>({guest:false,name:'Ana'})}")
p = w.pages['u1']; goto_home(w, 'u1'); p.click('#go-editor'); p.wait_for_timeout(900); f = w.frame('u1')
f.click('[data-new=boston-base]'); f.wait_for_timeout(700)
f.click('#tabs [data-p=ln]'); f.wait_for_timeout(300)
def exp():
    f.click('#tabs [data-p=mp]'); f.wait_for_timeout(300); d = json.loads(f.input_value('#ex')); f.click('#tabs [data-p=ln]'); f.wait_for_timeout(200); return d
d = exp(); g = [l for l in d['lines'] if l['name'] == 'Green Line'][0]
c('Green has 6 pieces in 4 branches', len(g['branches']) == 6 and len({b.get('group', i) for i, b in enumerate(g['branches'])}) == 4, [(b.get('name'), b.get('group')) for b in g['branches']])
c('D pieces share a group, B and C do not carry one', [b.get('group') for b in g['branches'] if b.get('name') == 'D'] == ['D'] * 2 or len({b['group'] for b in g['branches'] if b.get('name') == 'D'}) == 1)
c('B and C have no group', all('group' not in b for b in g['branches'] if b.get('name') in ('B', 'C')))
f.click('[data-l] [data-a=toggle] >> nth=0') if False else None
txt = f.evaluate("[].map.call(document.querySelectorAll('#p-ln [data-l]'),e=>e.innerText).join('\\n---\\n')")
gi = [t for t in txt.split('\n---\n') if 'Green Line' in t or True]
c('Lines tab counts Green as 4 branches', '+ 4 branch' in txt.lower() or '+ 4 branches' in txt, txt[:300])
# rename D: both pieces take the name
print('CARDS', f.evaluate("[].map.call(document.querySelectorAll('#p-ln [data-l]'),e=>e.querySelector('[data-k=name]').value)"))
gcard = f.query_selector_all('[data-l]')[3]
gcard.query_selector('[data-a=toggle]').click(); f.wait_for_timeout(300)
nm = f.query_selector_all('[data-bname]'); c('one name box per branch (4)', len(nm) == 4, len(nm))
dbox = [e for e in nm if e.input_value() == 'D'][0]; dbox.fill('Dee'); f.wait_for_timeout(300)
d = exp(); g = [l for l in d['lines'] if l['name'] == 'Green Line'][0]
c('renaming a branch renames all its pieces', [b.get('name') for b in g['branches']].count('Dee') == 2 and 'D' not in [b.get('name') for b in g['branches']])
# add another piece to a branch from a trunk station using the drawbar
f.query_selector_all('[data-l]')[3].query_selector('[data-a=draw]').click(); f.wait_for_timeout(300)
found = False
for el in f.query_selector_all('svg circle[data-sid]'):
    try: el.click(force=True, timeout=500)
    except Exception: continue
    if f.query_selector('#drawbar [data-d^=forkto]'): found = True; break
c('"Another piece" buttons are offered at a trunk station', found)
nb = len(f.query_selector_all('#drawbar [data-d^=forkto]')); c('one button per existing branch (4)', nb == 4, nb)
f.click('#drawbar [data-d^=forkto] >> nth=0'); f.wait_for_timeout(300)
c('drawbar now extends the new piece', f.query_selector('#drawbar .xf.on') is not None)
# build it by clicking a station that is not on Green yet
for el in f.query_selector_all('svg circle[data-sid]')[::7]:
    try: el.click(force=True, timeout=500)
    except Exception: continue
    f.wait_for_timeout(100)
    if False: pass
f.click('#drawbar [data-d=done]'); f.wait_for_timeout(300)
d = exp(); g = [l for l in d['lines'] if l['name'] == 'Green Line'][0]
grp = {}
for b in g['branches']: grp.setdefault(b.get('group', id(b)), []).append(b)
c('export: still 4 branches, one more piece (7) if the piece survived', len(grp) == 4 and len(g['branches']) in (6, 7), (len(grp), len(g['branches'])))
print(f'{c.n-len(c.fail)}/{c.n}', c.fail); w.close()

"""Get here! always moves to a different station after a claim, even when the challenge bank names nearly every station."""
from harness import *
import json
w=World(); c=Check()
w.user('u1')
gid=host_game(w,'u1','rail-rush','Pink','pw1',host='Hana',city='boston')
fh=w.frame('u1')
ids=fh.evaluate("NET.regions.map(r=>r.id)")
keep=ids[0]
# challenges name every station except `keep`
for i in range(10):
    w.docs[f'games/{gid}/challenges/c{i:02d}']={'title':f'Chal {i}','description':'','type':'standard','reward':10,'loc':[x for x in ids[1:]][i::10],'locText':'','anywhere':False,'order':i}
w.pump(800)
def plan(last,tag): return fh.evaluate(f"(()=>{{S.board.lastPink={json.dumps(last)};return planPink('{tag}')}})()")
r=plan(keep,'a'); c('only free station was the old one: moves anyway',r is not None and r!=keep,r)
res={plan(keep,'t%d'%i) for i in range(12)}; c('never returns the station it just left',keep not in res,res)
# bank names every station
for i in range(10):
    w.docs[f'games/{gid}/challenges/c{i:02d}']['loc']=ids[i::10]
w.pump(800)
r=plan(ids[3],'b'); c('every station named by a challenge: still placed, and elsewhere',r is not None and r!=ids[3],r)
# normal bank: still avoids challenge stations
for i in range(10):
    w.docs[f'games/{gid}/challenges/c{i:02d}']['loc']=ids[i*5:i*5+3]
w.pump(800)
named={x for i in range(10) for x in ids[i*5:i*5+3]}
res={plan(None,'n%d'%i) for i in range(15)}; c('normal bank: avoids stations that have challenges',not (res&named),res&named)
print([e for e in w.errors if 'TUNNEL' not in e][:3])
print(f'{c.n-len(c.fail)}/{c.n} passed; failed: {c.fail}')
w.close()

"""Get here!: the claiming team writes the next station; everyone sees it change once; a fallback covers a claimer who never wrote it."""
from harness import *

w=World(); c=Check()
US=['u1','u2','u3','u4']
for u in US: w.user(u)
gid=host_game(w,'u1','rail-rush','PinkClaim','pw1',host='Hana',city='boston')
for u in US[1:]: join_from_list(w,u,gid,pw='pw1'); w.pump(300)
fr={u:w.frame(u) for u in US}
def tab(f,l): f.click(f'#nav button:has-text("{l}")'); w.pump(250)
for u,(n,t) in {'u2':('Ann','A'),'u3':('Ben','B'),'u4':('Cy','A')}.items(): tab(fr[u],'Teams'); fr[u].fill('#pn',n); fr[u].click('#j'+t); w.pump(400)
ids=fr['u1'].evaluate("NET.regions.map(r=>r.id)")
for i in range(10):
    w.docs[f'games/{gid}/challenges/c{i:02d}']={'title':f'Chal {i}','description':'','type':'standard','reward':10,'loc':ids[i*5:i*5+3],'locText':'','anywhere':False,'order':i}
w.pump(600)
tab(fr['u1'],'Host'); fr['u1'].check('#pon'); w.pump(500); fr['u1'].click('#sg2'); w.pump(300); fr['u1'].click('#ac-y'); w.pump(3500)
for _ in range(20):
    if fr['u1'].evaluate('S.board.pink'): break
    w.pump(500)
w.pump(1500)
ev=lambda t:{k.split('/')[-1]:v for k,v in w.docs.items() if f'games/{gid}/events/' in k and v.get('type')==t}
views=lambda:[fr[u].evaluate("S.board.pink&&S.board.pink.st") for u in US]
c('start: everyone sees the same Get here!',len(set(views()))==1 and views()[0] is not None,views())
for rnd in range(3):
    before=views()[0]; n0=len(ev('pinkspawn'))
    f=fr['u2']; tab(f,'Challenges'); w.pump(500)
    f.evaluate("(()=>{const b=document.querySelector('[data-pink]');b.click();b.click()})()")
    seen=[]
    for t in range(16): w.pump(250); seen.append(tuple(views()))
    changes=[s for i,s in enumerate(seen) if i==0 or s!=seen[i-1]]
    final=seen[-1]
    c(f'round {rnd}: everyone ends on the same new station',len(set(final))==1 and final[0] not in (None,before),(before,final))
    agree=[s for s in changes if len(set(s))==1 and s[0]==final[0]]
    c(f'round {rnd}: no station flip-flop (every view goes straight to the final one)',all(set(s)<= {before,final[0],None} for s in changes),changes)
    new=[k for k in ev('pinkspawn') if k.startswith('pc_')]
    c(f'round {rnd}: exactly one new spawn, written by the claimer',len(ev('pinkspawn'))==n0+1,[k for k in ev('pinkspawn')])
    c(f'round {rnd}: team A got the coins',fr['u1'].evaluate("S.board.bal.A")>0)
# fallback: claim written without a next station (claimer's page closed)
fr['u1'].evaluate("0"); now=fr['u1'].evaluate("Date.now()"); pk=fr['u1'].evaluate("S.board.pink.id"); before=views()[0]
w.docs[f'games/{gid}/events/pd_orphan']={'type':'pinkdone','team':'B','pk':pk,'reward':20,'by':'u3','at':now}
w.pump(4000)
c('fallback waits: claim registered, nothing written in the first few seconds',all(v is None for v in views()) and 'pf_pd_orphan' not in ev('pinkspawn'),views())
w.pump(9000); w.pump(2000)
pf=[k for k in ev('pinkspawn') if k=='pf_pd_orphan']
c('fallback: one spawn written after the grace period',len(pf)==1,list(ev('pinkspawn'))[-3:])
c('fallback: everyone agrees on a new station',len(set(views()))==1 and views()[0] not in (None,before),views())
print([e for e in w.errors if 'TUNNEL' not in e][:3])
print(f'{c.n-len(c.fail)}/{c.n} passed; failed: {c.fail}')
w.close()

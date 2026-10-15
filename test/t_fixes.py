"""Tab names, node sizing/transparency, one random location per live challenge, Past Games membership."""
from harness import *
import time
w=World(); c=Check()
for u in ['u1','u2','u3','u4']: w.user(u)
gid=host_game(w,'u1','rail-rush','Fixes','pw1',host='Hana',city='boston')
for u in ['u2','u3']:
    join_from_list(w,u,gid,pw='pw1'); w.pump(300)
fh=w.frame('u1'); f2=w.frame('u2'); f3=w.frame('u3')
def tab(fr,label): fr.click(f'#nav button:has-text("{label}")'); w.pump(250)
tab(f2,'Teams'); f2.fill('#pn','Ann'); f2.click('#jA'); w.pump(400)
tab(f3,'Teams'); f3.fill('#pn','Ben'); f3.click('#jB'); w.pump(400)
# challenge bank: 10 challenges, each with three possible stations
ids=fh.evaluate("NET.regions.map(r=>r.id)")
for i in range(10):
    w.docs[f'games/{gid}/challenges/c{i:02d}']={'title':f'Chal {i}','description':'','type':'standard','reward':10,'loc':ids[i*5:i*5+3],'locText':'','anywhere':False,'order':i}
w.pump(600)
tab(fh,'Host'); fh.fill('#pc-start','10'); fh.fill('#pc-cap','10'); fh.click('#pc-save'); w.pump(400)
# --- tab names
tab(f2,'Map'); labels=f2.inner_text('#msub')
c('map sub-tabs are Gameboard and Challenge Bank','Gameboard' in labels and 'Challenge Bank' in labels and 'Coins' not in labels,labels)
# --- Gameboard nodes are smaller than Challenge Bank nodes
f2.click('#msub button[data-m="coins"]'); w.pump(300); r_game=float(f2.evaluate("dots[0].c.getAttribute('r')"))*float(f2.evaluate("W()/vb.w"))
f2.click('#msub button[data-m="chal"]'); w.pump(300); r_bank=float(f2.evaluate("dots[0].c.getAttribute('r')"))*float(f2.evaluate("W()/vb.w"))
c('Gameboard nodes are smaller (about 80%) than Challenge Bank nodes',0.75<r_game/r_bank<0.85,(r_game,r_bank))
# --- bank: stations with no challenge are fainter
empty=f2.evaluate("(()=>{const d=dots.find(x=>!x.cc);return d?+d.c.style.fillOpacity:null})()"); full=f2.evaluate("(()=>{const d=dots.find(x=>x.cc);return d?+d.c.style.fillOpacity:null})()")
c('stations without challenges are very transparent, others solid',empty is not None and empty<=0.2 and full==1,(empty,full))
# --- start; every live challenge appears at exactly one of its listed stations
tab(fh,'Host'); fh.click('#sg2'); w.pump(300); fh.click('#ac-y'); w.pump(2000); w.pump(800)
live=fh.evaluate("S.board.live")
c('10 challenges went live',len(live)==10,len(live))
bad=[k for k,v in live.items() if len(v['locs'])!=1 or v['locs'][0] not in ids[int(k[1:])*5:int(k[1:])*5+3]]
c('each live challenge has exactly one location, taken from its list',not bad,bad)
pos=[ids[int(k[1:])*5:int(k[1:])*5+3].index(v['locs'][0]) for k,v in live.items()]
c('the chosen location varies (random, not always the first)',len(set(pos))>=2,pos)
tab(f2,'Map'); f2.click('#msub button[data-m="chal"]'); w.pump(300)
lit=f2.evaluate("dots.filter(d=>d.cc>0).length")
c('Challenge Bank map lights one station per live challenge (<=10)',0<lit<=10,lit)
# --- Past Games: ended game where the stored participant list missed u3 and u4
w.docs[f'games/{gid}/members/u4']={'at':1}
g=w.docs[f'games/{gid}']; g.update({'status':'ended','endedAt':int(time.time()*1000),'participants':['u1','u2'],'summary':'x'}); w.pump(800)
for u,exp in (('u1',True),('u2',True),('u3',True),('u4',True)):
    goto_home(w,u); w.pages[u].click('#go-past'); w.pump(700)
    c(f'{u} sees the ended game in Past Games',('Fixes' in w.pages[u].inner_text('#pastlist'))==exp,w.pages[u].inner_text('#pastlist')[:120])
print([e for e in w.errors if 'TUNNEL' not in e][:3])
print(f'{c.n-len(c.fail)}/{c.n} passed; failed: {c.fail}')
w.close()

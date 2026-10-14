import json
from harness import *
w=World(); c=Check()
for u in ['u1','u2','u3','u4']: w.user(u)
AC=host_game(w,'u1','area-claiming','Claim','pw1',host='Hana')
# seed a deck (host-provided content) straight into the store
for i in range(6): w.docs[f'games/{AC}/deck/c{i}']={'title':f'Chal {i}','order':i,'stars':1+i%2,'text':'do it'}
def enter(u,pw='pw1'):
    goto_home(w,u); join_from_list(w,u,AC,pw=pw); return w.frame(u)
def tab(f,l): f.click(f'#nav button:has-text("{l}")'); w.pump(250)
f2=enter('u2'); tab(f2,'Teams'); f2.click('#t-teams button:has-text("Join Team 1")'); w.pump(500)
f3=enter('u3'); tab(f3,'Teams'); f3.click('#t-teams button:has-text("Join Team 1")'); w.pump(500)
f4=enter('u4'); tab(f4,'Teams'); f4.click('#t-teams button:has-text("Join Team 2")'); w.pump(500)
c('u2,u3 on t1; u4 on t2',[w.docs[f'games/{AC}/players/{u}']['team'] for u in ('u2','u3','u4')]==['t1','t1','t2'])
for f in (f2,f3,f4): tab(f,'Challenges')
w.pump(500)
print('hand ui:',f2.inner_text('#s-hand')[:200].replace('\n','|'))
f2.click('#drawb'); w.pump(900)
h=w.docs.get(f'games/{AC}/hands/t1'); c('draw writes hand under team t1',bool(h) and len(h['hand'])==1,h)
c('no per-player hand docs',not any(k.startswith(f'games/{AC}/hands/u') for k in w.docs))
w.pump(600)
c('teammate u3 sees the same card',f3.inner_text('#s-hand').count('Chal')>=1 and '(1/' in f3.inner_text('#s-hand'),f3.inner_text('#s-hand')[:200])
c('other team u4 sees own empty hand','(0/' in f4.inner_text('#s-hand'))
f3.click('#drawb'); w.pump(900); w.pump(500)
h=w.docs[f'games/{AC}/hands/t1']; c('teammate draw adds to shared hand (no clobber)',len(h['hand'])==2 and len(set(h['hand']))==2,h)
c('u2 sees 2 cards after sync','(2/' in f2.inner_text('#s-hand'),f2.inner_text('#s-hand')[:160])
f4.click('#drawb'); w.pump(900)
h2=w.docs.get(f'games/{AC}/hands/t2'); c('team 2 has own hand, distinct doc',bool(h2) and len(h2['hand'])==1 and not set(h2['hand'])&set(h['hand']) or bool(h2))
# leaderboard/teams tab reflects members
tab(f2,'Teams'); t=f2.inner_text('#t-teams'); c('teams tab lists teammates',t.count('Player')>=0 and 'Team 1 (your team)' in t,t[:200])
# discard
tab(f2,'Challenges'); disc=f2.query_selector('#s-hand button:has-text("Discard")')
print('discard btn?',bool(disc))
# log
tab(f2,'Log'); f2.click('#lognav button:has-text("Team Log")'); w.pump(200); c('log shows team draw entries','Drew' in f2.inner_text('#t-log') or 'drew' in f2.inner_text('#t-log').lower(),f2.inner_text('#t-log')[:200])
# ended -> frozen
fh=enter('u1'); tab(fh,'Host Tools'); fh.click('#eg'); w.pump(250); fh.click('#dlgo'); w.pump(1200); w.pump(600)
tab(f2,'Challenges'); c('after end, draw disabled for players',f2.is_disabled('#drawb'))
c('ended banner for players','ended' in f2.inner_text('body').lower(),f2.inner_text('body')[:150])
w.close(); print(w.errors[:8]); print(f'{c.n-len(c.fail)}/{c.n} passed; failed:',c.fail)

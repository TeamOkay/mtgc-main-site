import time
from harness import *
w=World(); c=Check()
for u in ['u1','u2','u3']: w.user(u)
G=host_game(w,'u1','rail-rush','Slow game','pw1',host='Hana',city='montreal')
join_from_list(w,'u2',G,pw='pw1')
DAY=86400000
def now(): return int(time.time()*1000)
def gd(): return w.docs['games/'+G]
c('new game is stamped with lastActive',abs(gd().get('lastActive',0)-now())<60000,gd().get('lastActive'))
def card(u): 
    p=w.pages[u]; goto_home(w,u); p.click('#go-ongoing'); p.wait_for_timeout(500); return p
# fresh game: no idle tag, no reset button
p3=card('u3'); c('fresh game shows no idle tag',p3.inner_text('#ongoinglist').count('Idle ·')==0)
# 2 days idle
gd()['lastActive']=now()-2*DAY; w.pump(600)
p3=card('u3'); t3=p3.inner_text('#ongoinglist'); c('outsider sees idle tag with time left','Idle 2 days' in t3 and 'ends in 5 days' in t3,t3)
c('outsider has no Still playing button',p3.query_selector(f'button[data-r="{G}"]') is None)
p2=card('u2'); w.pump(800); p2=card('u2')
c('member sees Still playing button on Ongoing',p2.query_selector(f'button[data-r="{G}"]') is not None)
p1=card('u1'); c('host sees Still playing button on Ongoing',p1.query_selector(f'button[data-r="{G}"]') is not None)
# in-game banner for a member
p2.click(f'button[data-e="{G}"]'); p2.wait_for_timeout(1200); w.pump(500)
c('in-game banner shown to member','Nothing has happened in this game for 2 days' in p2.inner_text('#idlebar') and not p2.is_hidden('#idlebar'),p2.inner_text('#idlebar'))
p2.click('#idle-reset'); p2.wait_for_timeout(800); w.pump(500)
c('reset sets lastActive to now',abs(gd()['lastActive']-now())<60000,gd()['lastActive'])
c('banner hides after reset',p2.is_hidden('#idlebar'))
p3=card('u3'); c('idle tag gone after reset',p3.inner_text('#ongoinglist').count('Idle ·')==0)
# reset from the list by a member
gd()['lastActive']=now()-3*DAY; w.pump(600); p1=card('u1'); w.pump(500)
p1.click(f'button[data-r="{G}"]'); p1.wait_for_timeout(800); w.pump(400)
c('list reset works for host',abs(gd()['lastActive']-now())<60000)
# outsider cannot get a banner for a game they are not in (shell frame only opens for entrants); legacy games get a grace stamp
w.docs['games/gLegacy']={'type':'rail-rush','name':'Old','createdBy':'u1','createdAt':now()-30*DAY,'status':'active','city':'montreal'}
w.pump(900)
c('legacy game without stamp is NOT ended',w.docs['games/gLegacy']['status']=='active')
c('legacy game gets a fresh stamp',abs(w.docs['games/gLegacy'].get('lastActive',0)-now())<60000,w.docs['games/gLegacy'])
# 7 idle days: an outsider (u3, not in the game) opening the site ends it
w.docs['games/g1']=None; del w.docs['games/g1']
w.docs[f'games/{G}/players/u2']={'name':'Pam'}
gd()['lastActive']=now()-8*DAY; w.pump(1200); w.pump(800)
g=gd(); c('game ended after 8 idle days',g['status']=='ended',g)
c('ended for inactivity',g.get('endReason')=='inactive' and g.get('endedBy')=='inactivity' and 'inactivity' in g.get('summary',''),g)
c('participants include host, joiner and player',set(g.get('participants',[]))>={'u1','u2'},g.get('participants'))
c('outsider u3 is not a participant','u3' not in g.get('participants',[]))
goto_home(w,'u1'); w.pages['u1'].click('#go-past'); w.pages['u1'].wait_for_timeout(600)
c('Past Games shows it for the host','after 7 days of inactivity' in w.pages['u1'].inner_text('#pastlist'),w.pages['u1'].inner_text('#pastlist')[:200])
goto_home(w,'u3'); w.pages['u3'].click('#go-past'); w.pages['u3'].wait_for_timeout(600)
c('Past Games empty for the outsider','after 7 days of inactivity' not in w.pages['u3'].inner_text('#pastlist'))
p3=card('u3'); c('ended game gone from Ongoing',G not in p3.inner_html('#ongoinglist'))
# an active game 6 days idle is left alone
w.docs['games/gSix']={'type':'rail-rush','name':'Six','createdBy':'u1','createdAt':now()-9*DAY,'lastActive':now()-6*DAY,'status':'active','city':'montreal'}
w.pump(900); c('6 days idle stays active and shows 1 day left','active'==w.docs['games/gSix']['status'] and 'ends in 1 day' in card('u3').inner_text('#ongoinglist'))
# the ended game opens read-only with the inactivity wording
goto_home(w,'u1'); w.pages['u1'].click('#go-past'); w.pages['u1'].wait_for_timeout(400)
w.pages['u1'].click(f'button[data-o="{G}"]'); w.pages['u1'].wait_for_timeout(1500); f=w.frame('u1')
c('ended banner mentions inactivity','after 7 days of inactivity' in f.inner_text('#rob'),f.inner_text('#rob')[:120])
w.close(); print(w.errors[:6]); print(f'{c.n-len(c.fail)}/{c.n} passed; failed:',c.fail)

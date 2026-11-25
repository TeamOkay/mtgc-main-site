"""Admin phase 1: Admin button only for admins; games list/details/maps/stats; opening a game is invisible and read-only."""
from harness import *
import time
w=World(); c=Check()
for u in ['u1','u2','u8']: w.user(u)
gid=host_game(w,'u1','rail-rush','Admin Test','pw1',host='Hana',city='boston')
join_from_list(w,'u2',gid,pw='pw1'); w.pump(300)
fh=w.frame('u1'); f2=w.frame('u2')
def tab(fr,l): fr.click(f'#nav button:has-text("{l}")'); w.pump(250)
tab(f2,'Teams'); f2.fill('#pn','Ann'); f2.click('#jA'); w.pump(400)
ids=fh.evaluate("NET.regions.map(r=>r.id)")
for i in range(4): w.docs[f'games/{gid}/challenges/c{i}']={'title':f'Chal {i}','description':'','type':'standard','reward':10,'loc':ids[i*5:i*5+3],'locText':'','anywhere':False,'order':i}
w.pump(500)
tab(fh,'Host'); fh.check('#sg2') if False else None
fh.click('#sg2'); w.pump(300); fh.click('#ac-y'); w.pump(3500)
w.docs[f'games/gold']={'type':'area-claiming','name':'Old Area','createdBy':'u1','hostName':'Hana','createdAt':int(time.time()*1000)-3*86400000,'lastActive':int(time.time()*1000)-3*86400000,'status':'ended','endedBy':'inactivity','salt':'s','passHash':'SECRETHASH'}
w.docs['maps/m1']={'owner':'u1','name':'My Map','share':'private','json':'{"x":1}','updated':1}
w.docs['admins/u9']={'at':1}
w.user('u9'); w.pump(900)
# ---- who sees the button
c('non-admin: no Admin button',w.pages['u8'].is_hidden('#go-admin'))
c('admin: Admin button shown',w.pages['u9'].is_visible('#go-admin'))
p=w.pages['u9']; p.click('#go-admin'); w.pump(900)
fa=w.frame('u9'); c('admin page opens',fa is not None and fa.inner_text('#who')=='admin',fa and fa.inner_text('#who'))
# ---- games list
txt=fa.inner_text('#main'); c('lists both games','Admin Test' in txt and 'Old Area' in txt,txt[:200])
c('shows idle/ended-by-inactivity info','inactivity' in txt)
c('never shows password hashes','SECRETHASH' not in fa.inner_text('body') and 'passHash' not in fa.inner_text('body'))
fa.fill('#q','old area'); w.pump(200); t2=fa.inner_text('#main'); c('search filters',('Old Area' in t2) and ('Admin Test' not in t2),t2[:120])
fa.fill('#q',''); fa.select_option('#fs','active'); w.pump(200); t2=fa.inner_text('#main'); c('status filter',('Admin Test' in t2) and ('Old Area' not in t2))
fa.select_option('#fs',''); fa.select_option('#ft','area-claiming'); w.pump(200); t2=fa.inner_text('#main'); c('type filter',('Old Area' in t2) and ('Admin Test' not in t2))
fa.select_option('#ft','')
fa.click(f'[data-det="{gid}"]'); w.pump(1200); t3=fa.inner_text(f'#d-{gid}')
c('details: players with teams','Ann' in t3 and 'Team A' in t3,t3[:400])
c('details: host, events and challenges shown','Hana' in t3 and 'Challenges' in t3 and 'Events by type' in t3,t3[:300])
# ---- maps and stats
fa.click('.tabs [data-t="maps"]'); w.pump(700); tm=fa.inner_text('#main'); c('maps tab lists a private map with its owner','My Map' in tm and 'Private' in tm and 'u1' in tm,tm[:150])
fa.click('.tabs [data-t="stats"]'); w.pump(500); ts=fa.inner_text('#main'); c('stats: totals','2' in ts and 'games in total' in ts and 'ended by inactivity' in ts,ts[:200])
# ---- opening a game: no password, invisible, read-only
w.pump(500)
ev0=sorted(k for k in w.docs if f'games/{gid}/events/' in k); la0=w.docs[f'games/{gid}'].get('lastActive')
fa.click('.tabs [data-t="games"]'); w.pump(300); fa.click(f'[data-open="{gid}"]'); w.pump(1500)
fg=w.frame('u9'); c('admin enters the game without a password',p.query_selector('#pf') is None and fg is not None and fg.evaluate("typeof S!=='undefined'"))
c('game shows the admin view note',fg is not None and 'Admin view' in fg.evaluate("document.getElementById('me').innerText"))
tab(fg,'Teams'); w.pump(400); c('no team buttons for the admin',fg.query_selector('#jA') is None)
c('admin is not a member',f'games/{gid}/members/u9' not in w.docs)
c('admin has no player entry',f'games/{gid}/players/u9' not in w.docs)
# background writers are off for the admin, on for a player
fg.evaluate("S.chalCfgTest=1")
n_before=len([k for k in w.docs if f'games/{gid}/events/' in k])
live=f2.evaluate("Object.keys(S.board.live)")
if live:
    sk=[k for k,v in w.docs.items() if f'games/{gid}/events/' in k and v.get('type')=='spawn' and any(pk['c']==live[0] for pk in v.get('picks',[]))][0]
    G=w.docs[f'games/{gid}']; G['chalCfg']=dict(G.get('chalCfg') or {},expireOn=True,expireMin=30); w.docs[sk]['wt']=int(time.time()*1000)-31*60000; w.pump(900)
    fg.evaluate("checkExpiry()"); w.pump(900)
    c('admin page does not write an expiry',not any(v.get('type')=='expire' and v.get('by')=='u9' for k,v in w.docs.items() if f'games/{gid}/events/' in k))
    c('(control) the admin page counts as view-only, a player page does not',fg.evaluate("VIEW()") is True and f2.evaluate("VIEW()") is False)
else: c('has live challenges',False,live)
fg.evaluate("(()=>{window.__rp=window.parent.TG.requirePassword(S.gid).then(r=>{window.__rpv=r});return 1})()"); w.pump(500)
c('join attempt shows the admin notice',p.query_selector('#ov:not([hidden])') is not None and 'admin' in p.inner_text('#ov').lower(),p.inner_text('#ov')[:100])
p.click('#ok'); w.pump(400); c('...and is refused',fg.evaluate("window.__rpv")is False)
w.pump(600)
c('no members/players ever written for the admin',not any(k.endswith('/u9') for k in w.docs if k.startswith(f'games/{gid}/')))
print([e for e in w.errors if 'TUNNEL' not in e][:3])
print(f'{c.n-len(c.fail)}/{c.n} passed; failed: {c.fail}')
w.close()

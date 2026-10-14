import json,sys
from harness import *
w=World(); c=Check()
U={u:w.user(u) for u in ['u1','u2','u3','u4','u5']}
def tab(f,label): f.click(f'#nav button:has-text("{label}")'); w.pump(200)
def raw(): return json.dumps(w.docs)

# ---------- 1. hosting ----------
RR=host_game(w,'u1','rail-rush','Rush','secret',host='Hana',city='toronto')
AC=host_game(w,'u1','area-claiming','Claim','secret',host='Hana') if (goto_home(w,'u1') or True) else None
goto_home(w,'u1'); TR=host_game(w,'u1','ticket-to-ride','Ride','secret',host='Hana',city='montreal')
import copy
G=copy.deepcopy(w.games())
c('3 games created',len(G)==3)
c('host recorded as creator',all(g['createdBy']=='u1' for g in G.values()))
c('city stored',G[RR]['city']=='toronto' and G[TR]['city']=='montreal' and 'city' not in G[AC])
c('status active, spectators off',all(g['status']=='active' and g['spectators'] is False for g in G.values()))
c('password never stored in plaintext','secret' not in raw())
c('salted hash present',all(len(g['passHash'])==64 and len(g['salt'])==32 for g in G.values()))
c('area has 2 default teams',sum(1 for k in w.docs if k.startswith(f'games/{AC}/teams/'))==2)
c('TR frame loads, host tag',w.frame('u1') is not None and w.frame('u1').is_visible('#hostTag'))
c('TR blank body',  'not built yet' in w.frame('u1').inner_text('body'))

# ---------- 2. ongoing list ----------
p=U['u2']; p.click('#go-ongoing'); w.pump(300)
txt=p.inner_text('#ongoinglist')
c('u2 sees all 3 games',all(n in txt for n in ('Rush','Claim','Ride')),txt)
c('Locked tag shown',txt.count('Locked')==3)
c('u2 not shown as host','You are hosting' not in txt)
goto_home(w,'u1'); U['u1'].click('#go-ongoing'); w.pump(300)
c('u1 sees hosting tag + Resume',U['u1'].inner_text('#ongoinglist').count('You are hosting')==3 and 'Resume' in U['u1'].inner_text('#ongoinglist'))
c('host resume needs no password',join_from_list(w,'u1',RR,pw=None)==False and w.frame('u1') is not None)
goto_home(w,'u1')

# ---------- 3. password gate (spectators off) ----------
pr=join_from_list(w,'u2',RR,pw='wrong'); c('wrong password prompts',pr)
c('wrong password rejected, error shown','not the password' in p.inner_text('#pe'))
c('no frame entered after wrong pw',w.frame('u2') is None or not p.query_selector('iframe:not([hidden])'))
p.fill('#pw','secret'); p.click('#pf button[type=submit]'); w.pump(1200)
c('right password enters',w.frame('u2') is not None and 'Rush' in p.inner_text('#crumb'))
c('member doc written',f'games/{RR}/members/u2' in w.docs)
f2=w.frame('u2')
c('non-host has no Host tab','Host' not in f2.inner_text('#nav').split('\n'))
goto_home(w,'u2'); pr=join_from_list(w,'u2',RR,pw='secret'); c('member re-entry skips prompt',pr==False)
goto_home(w,'u2')
# cancel path
p3=U['u3']; p3.click('#go-ongoing'); w.pump(200); p3.click(f'button[data-e="{RR}"]'); p3.wait_for_selector('#pf'); p3.click('#px'); w.pump(300)
c('cancel keeps u3 out',w.frame('u3') is None and f'games/{RR}/members/u3' not in w.docs)

# ---------- 4. Rail Rush: teams, start, coins ----------
f2=None; join_from_list(w,'u2',RR); f2=w.frame('u2'); tab(f2,'Teams')
f2.fill('#pn','Uma'); f2.click('#jA'); w.pump(600)
c('u2 on team A',w.docs.get(f'games/{RR}/players/u2',{}).get('team')=='A' and w.docs[f'games/{RR}/players/u2']['name']=='Uma')
# u4 joins B using password from the team-join prompt after entering with spectators ON
fh=w.frame('u1') if False else None
goto_home(w,'u1'); join_from_list(w,'u1',RR); fh=w.frame('u1'); tab(fh,'Host'); 
fh.check('#acc-spec'); w.pump(600)
c('spectators flag saved',w.games()[RR]['spectators'] is True)
goto_home(w,'u4'); U['u4'].click('#go-ongoing'); w.pump(400)
c('u4 list shows Spectators welcome',"Spectators welcome" in U['u4'].inner_text('#ongoinglist'))
prompted=join_from_list(w,'u4',RR); c('spectator enters with no prompt',prompted==False and w.frame('u4') is not None)
f4=w.frame('u4'); tab(f4,'Teams')
c('spectator sees watching notice','watching' in f4.inner_text('#me').lower())
f4.fill('#pn','Bo'); f4.click('#jB'); w.pump(500)
c('team join prompts for password',U['u4'].query_selector('#pf') is not None)
c('not yet on a team',w.docs.get(f'games/{RR}/players/u4',{}).get('team') is None)
U['u4'].fill('#pw','nope'); U['u4'].click('#pf button[type=submit]'); w.pump(300)
c('wrong team password rejected','not the password' in U['u4'].inner_text('#pe'))
U['u4'].fill('#pw','secret'); U['u4'].click('#pf button[type=submit]'); w.pump(1000)
c('after right password joins team B',w.docs.get(f'games/{RR}/players/u4',{}).get('team')=='B',w.docs.get(f'games/{RR}/players/u4'))
c('u4 now member',f'games/{RR}/members/u4' in w.docs)
c('typed name survives the password prompt',w.docs[f'games/{RR}/players/u4']['name']=='Bo',w.docs[f'games/{RR}/players/u4'])
# another team-click needs no more prompt
f4.click('#jA'); w.pump(600); c('member switches team without prompt',w.docs[f'games/{RR}/players/u4']['team']=='A' and U['u4'].query_selector('#pf') is None)
f4.click('#jB'); w.pump(500)
# lobby state
c('players see waiting-to-start','Waiting to start' in f2.inner_text('#lob') if f2.is_visible('#lob') else False, f2.inner_text('body')[:200])
# START (host) with confirm dialog
tab(fh,'Map'); fh.click('#sg'); w.pump(300)
c('start asks for confirmation',fh.is_visible('#ac-y'))
fh.click('#ac-n'); w.pump(300)
c('cancel does not start',not any(v.get('type')=='start' for k,v in w.docs.items() if f'games/{RR}/events/' in k))
fh.click('#sg'); w.pump(200); fh.click('#ac-y'); w.pump(1200)
c('start event written once',sum(1 for k,v in w.docs.items() if f'games/{RR}/events/' in k and v.get('type')=='start')==1)
w.pump(800)
c('host lobby hidden after start',not fh.is_visible('#lob'))
c('player lobby hidden after start (propagated)',not f2.is_visible('#lob'))
tab(fh,'Host'); c('host panel says Started','Started' in fh.inner_text('#gst'))
c('Start button disabled once started',fh.is_disabled('#sg2'))
# grant coins and see balance on a player
n0=f2.inner_text('#bal'); fh.click('#hostcoins [data-g="A"][data-d="10"]'); w.pump(900)
c('coin grant reaches team A player',f2.inner_text('#bal')!=n0,(n0,f2.inner_text('#bal')))
# teams rename
fh.fill('#tn_A','Reds'); fh.click('[data-sv="A"]'); w.pump(700); tab(f2,'Teams')
c('rename propagates','Reds' in f2.inner_text('#teams'))

# ---------- 5. change password ----------
tab(fh,'Host'); fh.click('#acc-pw'); w.pump(300)
ph=U['u1']; c('change-password dialog opens',ph.query_selector('#nf') is not None)
ph.fill('#np','ab'); ph.click('#nf button[type=submit]'); c('too-short rejected',ph.query_selector('#nf') is not None)
ph.fill('#np','newpass'); ph.click('#nf button[type=submit]'); w.pump(800)
c('hash changed',w.games()[RR]['passHash']!=G[RR]['passHash'])
c('plain new password not stored','newpass' not in raw())
goto_home(w,'u2'); 
# u5 must use new pw to join team (spectators on)
pr5=join_from_list(w,'u5',RR); print('u5 prompted',pr5,'spectators',w.games()[RR]['spectators'],U['u5'].inner_text('body')[:200].replace('\n','|')); f5=w.frame('u5'); tab(f5,'Teams'); f5.fill('#pn','Eve'); f5.evaluate("S.board.started=false;document.getElementById('jA').disabled=false"); f5.click('#jA'); w.pump(500)  # teams lock after start (see t_lock.py); unlock locally to exercise the password prompt
U['u5'].fill('#pw','secret'); U['u5'].click('#pf button[type=submit]'); w.pump(300)
c('old password rejected after change','not the password' in U['u5'].inner_text('#pe'))
U['u5'].fill('#pw','newpass'); U['u5'].click('#pf button[type=submit]'); w.pump(1000)
c('new password accepted',w.docs.get(f'games/{RR}/players/u5',{}).get('team')=='A')
c('existing member u2 unaffected',join_from_list(w,'u2',RR)==False)
goto_home(w,'u2')

# ---------- 6. spectators off again locks out non-members ----------
tab(fh,'Host'); fh.uncheck('#acc-spec'); w.pump(600)
c('spectators off saved',w.games()[RR]['spectators'] is False)
goto_home(w,'u3'); pr=join_from_list(w,'u3',RR); c('non-member refused: game already started (no password prompt)',(not pr) and 'started' in U['u3'].inner_text('#ov').lower()); U['u3'].click('#ok'); w.pump(200)

# ---------- 7. Area Claiming ----------
goto_home(w,'u2'); join_from_list(w,'u2',AC,pw='secret'); fa=w.frame('u2')
tab(fa,'Teams'); c('area teams listed','Team 1' in fa.inner_text('#t-teams') and 'Team 2' in fa.inner_text('#t-teams'))
fa.click('#t-teams button:has-text("Join Team 1")'); w.pump(700)
c('u2 on t1 (member so no extra prompt)',w.docs.get(f'games/{AC}/players/u2',{}).get('team')=='t1',w.docs.get(f'games/{AC}/players/u2'))
goto_home(w,'u3'); join_from_list(w,'u3',AC,pw='secret'); fa3=w.frame('u3'); tab(fa3,'Teams'); fa3.click('#t-teams button:has-text("Join Team 2")'); w.pump(700)
c('u3 on t2',w.docs.get(f'games/{AC}/players/u3',{}).get('team')=='t2')
goto_home(w,'u1'); join_from_list(w,'u1',AC); fha=w.frame('u1'); tab(fha,'Host Tools')
fha.click('#hostteams button:has-text("Add team")'); w.pump(700)
nt=[k for k in w.docs if k.startswith(f'games/{AC}/teams/')]; c('host added team',len(nt)==3,nt)
inp=fha.query_selector_all('#hostteams input[type=text], #hostteams input:not([type=color])')
inp[2].fill('Greens'); fha.query_selector_all('#hostteams button:has-text("Save")')[2].click(); w.pump(700)
c('team renamed',any(v.get('name')=='Greens' for k,v in w.docs.items() if k.startswith(f'games/{AC}/teams/')))
tab(fa,'Teams'); c('new team visible to players','Greens' in fa.inner_text('#t-teams'))
fa.click('#t-teams button:has-text("Join Greens")'); w.pump(700)
c('player switches to new team',w.docs[f'games/{AC}/players/u2']['team'] not in ('t1',None))
# isolation
c('area players not in rail',f'games/{RR}/teams/t1' not in w.docs)

# ---------- 8. Ticket to Ride ----------
goto_home(w,'u2'); join_from_list(w,'u2',TR,pw='secret'); ft=w.frame('u2')
c('TR visible to player, not host',ft is not None and not ft.is_visible('#hostbox') and 'Montréal' in ft.inner_text('#city'))
goto_home(w,'u1'); join_from_list(w,'u1',TR); fth=w.frame('u1'); c('TR host controls',fth.is_visible('#hostbox'))

# ---------- 9. End game ----------
# Rail: started; end it
goto_home(w,'u1'); join_from_list(w,'u1',RR); fh=w.frame('u1'); tab(fh,'Host')
c('end button enabled immediately',not fh.is_disabled('#eg'))
fh.click('#eg'); w.pump(300); c('end asks to confirm',fh.is_visible('#ac-y')); fh.click('#ac-n'); w.pump(300)
c('cancel keeps active',w.games()[RR]['status']=='active')
fh.click('#eg'); w.pump(200); fh.click('#ac-y'); w.pump(1200)
g=w.games()[RR]; c('rail ended',g['status']=='ended',g)
c('participants = team players + host',set(g['participants'])>={'u1','u2','u4','u5'} and 'u3' not in g['participants'],g.get('participants'))
c('summary text',bool(g.get('summary')),g.get('summary'))
w.pump(600); c('player frame becomes read-only (ended banner)', f2.is_visible('#rob') or 'ended' in f2.inner_text('body').lower())
# Area: end with nothing claimed, never "started"
goto_home(w,'u1'); join_from_list(w,'u1',AC); fha=w.frame('u1'); tab(fha,'Host Tools')
c('area end button enabled immediately',not fha.is_disabled('#eg'))
fha.click('#eg'); w.pump(300); c('area end asks to confirm',fha.is_visible('#dlgo')); fha.click('#dlgc'); w.pump(300)
c('area cancel keeps active',w.games()[AC]['status']=='active')
fha.click('#eg'); w.pump(200); fha.click('#dlgo'); w.pump(1200)
ga=w.games()[AC]; c('area ended',ga['status']=='ended',ga)
c('area participants',set(ga['participants'])>={'u1','u2','u3'},ga.get('participants'))
# TR end
goto_home(w,'u1'); join_from_list(w,'u1',TR); fth=w.frame('u1'); fth.click('#eg'); w.pump(250); c('TR end confirms',fth.is_visible('#ac-y')); fth.click('#ac-y'); w.pump(1000)
gt=w.games()[TR]; c('TR ended',gt['status']=='ended' and 'u2' in gt['participants'],gt)
c('TR ended banner shown to host',fth.is_visible('#ended'))
# ongoing now empty; past lists
goto_home(w,'u2'); U['u2'].click('#go-ongoing'); w.pump(400)
c('ended games leave Ongoing','Rush' not in U['u2'].inner_text('#ongoinglist') and 'No games are running' in U['u2'].inner_text('#ongoinglist'))
goto_home(w,'u2'); U['u2'].click('#go-past'); w.pump(500); pt=U['u2'].inner_text('#pastlist')
c('u2 past shows all 3',all(n in pt for n in ('Rush','Claim','Ride')),pt)
goto_home(w,'u3'); U['u3'].click('#go-past'); w.pump(500); pt3=U['u3'].inner_text('#pastlist')
c('u3 (spectator in Rail, team in Area) sees only Area',('Claim' in pt3) and 'Rush' not in pt3 and 'Ride' not in pt3,pt3)
goto_home(w,'u5'); U['u5'].click('#go-past'); w.pump(500); c('u5 sees Rush',('Rush' in U['u5'].inner_text('#pastlist')))
# open a past game: read-only
U['u2'].click(f'button[data-o="{RR}"]'); w.pump(1500); f=w.frame('u2')
c('past game opens read-only frame',f is not None and not (f.query_selector('#sg') and f.is_visible('#sg')))
print('past rail body:',f.inner_text('body')[:300].replace('\n','|'))
goto_home(w,'u2')
# hide / purge
U['u2'].click('#go-past'); w.pump(300)
U['u2'].click(f'button[data-h="{TR}"]'); w.pump(250); c('hide asks to confirm',U['u2'].is_visible('#cn-yes'))
U['u2'].click('#cn-no'); w.pump(200); c('cancel keeps listed','Ride' in U['u2'].inner_text('#pastlist'))
U['u2'].click(f'button[data-h="{TR}"]'); w.pump(250); U['u2'].click('#cn-yes'); w.pump(900)
c('u2 hid TR',f'hides/{TR}__u2' in w.docs and 'Ride' not in U['u2'].inner_text('#pastlist'))
c('TR still exists (host has not hidden)',f'games/{TR}' in w.docs)
goto_home(w,'u1'); U['u1'].click('#go-past'); w.pump(500)
c('host still sees TR',"Ride" in U['u1'].inner_text('#pastlist'))
U['u1'].click(f'button[data-h="{TR}"]'); w.pump(250); U['u1'].click('#cn-yes'); w.pump(1500)
c('all participants hid -> game purged',f'games/{TR}' not in w.docs and not any(k.startswith(f'games/{TR}/') for k in w.docs),[k for k in w.docs if TR in k])
c('hides cleaned up',not any(k.startswith(f'hides/{TR}') for k in w.docs))
c('other ended games untouched',f'games/{RR}' in w.docs and f'games/{AC}' in w.docs)
def hide_all(gid,users):
    for u in users:
        goto_home(w,u); U[u].click('#go-past'); w.pump(400)
        U[u].click(f'button[data-h="{gid}"]'); w.pump(250); U[u].click('#cn-yes'); w.pump(1200)
hide_all(RR,['u1','u2','u4','u5'])
c('Rail purged with no residue',not any(RR in k for k in w.docs),[k for k in w.docs if RR in k])
hide_all(AC,['u1','u2','u3'])
c('Area purged with no residue',not any(AC in k for k in w.docs),[k for k in w.docs if AC in k])
c('nothing left in store',not w.docs,list(w.docs)[:5])
w.close()
print(w.errors[:10]); print(f'{c.n-len(c.fail)}/{c.n} passed; failed:',c.fail)

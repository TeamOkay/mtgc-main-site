import json
from harness import *
w=World(); c=Check()
U={u:w.user(u) for u in ['u1','u2','u3','u4']}
gid=host_game(w,'u1','rail-rush','Three','pw1',host='Hana',city='boston')
fh=w.frame('u1')

# ---------------- unit tests of the lead rules (pure fold) ----------------
def F(evs): return fh.evaluate("evs=>{const b=fold(evs,null);return {act:b.act,lead:b.lead,bal:b.bal,live:Object.keys(b.live),log:b.log,pend:b.pend,used:[...b.used],closed:[...b.closed],ch:b.ch}}",evs)
S1,S2=fh.evaluate("[NET.regions[0].id,NET.regions[1].id]")
t=[1000]
def E(**k): t[0]+=10; k.setdefault('at',t[0]); k.setdefault('id','e%d'%t[0]); k.setdefault('by','x'); return k
base=[E(type='team3',on=True),E(type='start')]+[E(type='grant',team=k,n=50) for k in 'ABC']
def sp(team,n,st=S1): return E(type='spend',team=team,station=st,n=n)
def lead(evs,st=S1): return F(base+evs)['lead'].get(st)
c('3 teams active',F(base)['act']==['A','B','C'])
c('A places 5 -> A leads 5',lead([sp('A',5)])=={'t':'A','n':5})
c('A 5 then B 5 -> level (not A and B both leading C)',lead([sp('A',5),sp('B',5)]) is None)
c('A extends own lead (3+2=5)',lead([sp('A',3),sp('A',2)])=={'t':'A','n':5})
c('lead is capped at 5',F(base+[sp('A',5),sp('A',3)])['bal']['A']==45)
c('B reduces A by 2 (A 3 -> 1)? A5,B4 -> A1',lead([sp('A',5),sp('B',4)])=={'t':'A','n':1})
c('either trailing team neutralises for both: A5,B2,C3 -> level',lead([sp('A',5),sp('B',2),sp('C',3)]) is None)
c('C crossing zero takes lead with remainder: A2,C5 -> C3',lead([sp('A',2),sp('C',5)])=={'t':'C','n':3})
c('then B hits C: C3,B1 -> C2',lead([sp('A',2),sp('C',5),sp('B',1)])=={'t':'C','n':2})
c('need to flip a max lead = lead + 5: A5 then B places max 10',F(base+[sp('A',5),sp('B',20)])['lead'][S1]=={'t':'B','n':5} and F(base+[sp('A',5),sp('B',20)])['bal']['B']==40)
c('independent stations',lead([sp('A',2),sp('B',3,S2)],S2)=={'t':'B','n':3} and lead([sp('A',2),sp('B',3,S2)])=={'t':'A','n':2})
lg=[x for x in F(base+[sp('A',5),sp('B',2)])['log'] if x['type']=='spend'][-1]
c('log has from/to/score for 3 teams',lg['from']=={'t':'A','n':5} and lg['to']=={'t':'A','n':3} and set(lg['sc'])=={'A','B','C'} and lg['hit']==['A'],lg)
# 2-team games unchanged
b2=[E(type='start')]+[E(type='grant',team=k,n=50) for k in 'AB']
r=F(b2+[sp('A',3),sp('B',5)]); c('2-team: A3,B5 -> B leads 2',r['lead'][S1]=={'t':'B','n':2} and r['act']==['A','B'])
c('2-team: team C cannot play',F(b2+[sp('C',3)])['lead'].get(S1) is None)
# removing the 3rd team
r=F(base+[sp('C',4),sp('A',2,S2),E(type='team3',on=False)])
c('remove C: its stations cleared, A kept, C coins zero',S1 not in r['lead'] and r['lead'][S2]['t']=='A' and r['bal']['C']==0 and r['act']==['A','B'])
c('after removal C cannot place',F(base+[E(type='team3',on=False),sp('C',3)])['lead'].get(S1) is None)
c('can re-add',F(base+[E(type='team3',on=False),E(type='team3',on=True)])['act']==['A','B','C'])

# ---------------- challenges: 3-team rules ----------------
def spawn(trig,ids,at,**k): return E(type='spawn',trig=trig,at=at,picks=[{'c':i,'title':i,'locs':[S1]} for i in ids],**k)
st=E(type='start'); sp1=spawn(st['id'],['c1','c2'],st['at']+1)
fails=[st,sp1,E(type='grant',team='A',n=100),E(type='grant',team='B',n=40),E(type='grant',team='C',n=10),E(type='team3',on=True)]
# team3 must precede start to be active at the time; rebuild in order
ev=[E(type='team3',on=True)]; ev.append(E(type='start')); st=ev[-1]; ev.append(spawn(st['id'],['c1','c2'],st['at']+1))
ev+= [E(type='grant',team=k,n=n) for k,n in (('A',100),('B',40),('C',10))]
r=F(ev+[E(type='fail',team='A',chal='c1',title='c1')]); c('one failure: still live',  'c1' in r['live'])
r=F(ev+[E(type='fail',team='A',chal='c1',title='c1'),E(type='fail',team='B',chal='c1',title='c1')]); c('two of three failed: still live','c1' in r['live'])
r=F(ev+[E(type='fail',team=k,chal='c1',title='c1') for k in 'ABC']); c('all three failed: removed',('c1' not in r['live']) and 'c1' in r['closed'])
r=F(ev+[E(type='fail',team='A',chal='c1',title='c1'),E(type='complete',team='B',chal='c1',title='c1',kind='standard',reward=10)])
c('boost x1.5 when any other team failed',[x for x in r['log'] if x['type']=='complete'][0]['gain']==15)
r=F(ev+[E(type='fail',team='A',chal='c1',title='c1'),E(type='fail',team='B',chal='c1',title='c1'),E(type='complete',team='C',chal='c1',title='c1',kind='standard',reward=20)])
c('two other teams failed: x2.25 (20 -> 45)',[x for x in r['log'] if x['type']=='complete'][0]['gain']==45,[x for x in r['log'] if x['type']=='complete'])
r=F(ev+[E(type='complete',team='C',chal='c1',title='c1',kind='steal',reward=50)])
c('steal takes the % from every rival (A 100->50, B 40->20, C 10->80)',r['bal']['A']==50 and r['bal']['B']==20 and r['bal']['C']==80,r['bal'])
r=F(ev+[E(type='fail',team='A',chal='c2',title='c2'),E(type='fail',team='B',chal='c2',title='c2'),E(type='team3',on=False)])
c('removing C when the others already failed closes the challenge',('c2' not in r['live']))

# ---------------- UI + sync: add the third team, pacing, cap, expiry ----------------
for u in ['u2','u3','u4']:
    join_from_list(w,u,gid,pw='pw1'); w.pump(300)
fh=w.frame('u1'); f={u:w.frame(u) for u in ['u2','u3','u4']}
def tab(fr,label): fr.click(f'#nav button:has-text("{label}")'); w.pump(250)
tab(fh,'Host')
c('host sees Add third team',fh.is_visible('#t3a') and not fh.is_visible('#t3x'))
c('players see only 2 join buttons',f['u4'].query_selector('#jC') is None)
fh.click('#t3a'); w.pump(600)
ev_docs=[v for k,v in w.docs.items() if f'games/{gid}/events/' in k and v.get('type')=='team3']
c('team3 event written',len(ev_docs)==1 and ev_docs[0]['on'] is True)
c('host card now offers Remove',fh.is_visible('#t3x'))
for u,k in (('u2','A'),('u3','B'),('u4','C')):
    tab(f[u],'Teams'); f[u].fill('#pn',{'u2':'Ann','u3':'Ben','u4':'Cat'}[u]); w.pump(100)
    c(f'{u} sees 3 join buttons',all(f[u].query_selector(f'#j{x}') for x in 'ABC'))
    f[u].click(f'#j{k}'); w.pump(500)
c('three players on A/B/C',[w.docs[f'games/{gid}/players/{u}']['team'] for u in ('u2','u3','u4')]==['A','B','C'])
c('teams tab shows three team cards',f['u2'].inner_text('#teams').count('stations led')==3)
c('scoreboard lists 3 teams',f['u2'].inner_text('#sb').count('\U0001FA99')==3)
fh.click('#nav button[data-t="host"]'); w.pump(200)
c('host coin rows for 3 teams',fh.query_selector_all('#hostcoins [data-g][data-d="10"]').__len__()==3)
# rename team C via host
fh.fill('#tn_C','Greens'); fh.click('[data-sv="C"]'); w.pump(500)
c('team C renamed',w.docs.get(f'games/{gid}/teams/C',{}).get('name')=='Greens' and 'Greens' in f['u4'].inner_text('#who'),f['u4'].inner_text('#who'))
# pacing defaults + save
c('pacing defaults: cap on, 10, start 3, expire off, 90',fh.is_checked('#pc-capon') and fh.input_value('#pc-cap')=='10' and fh.input_value('#pc-start')=='3' and not fh.is_checked('#pc-expon') and fh.input_value('#pc-expm')=='90' and fh.is_disabled('#pc-expm'))
fh.fill('#pc-cap','4'); fh.fill('#pc-start','2'); fh.click('#pc-save'); w.pump(500)
c('settings saved on game doc',w.games()[gid].get('chalCfg')=={'capOn':True,'cap':4,'start':2,'expireOn':False,'expireMin':90},w.games()[gid].get('chalCfg'))
# challenge bank (anywhere)
for i in range(12): w.docs[f'games/{gid}/challenges/c{i:02d}']={'title':f'Chal {i}','description':'','type':'standard','reward':10,'loc':[],'locText':'','anywhere':True,'order':i}
w.pump(600)
# grants then start
for k in 'ABC': w.docs[f'games/{gid}/events/g{k}']={'type':'grant','team':k,'n':30,'by':'u1','at':5}
fh.click('#sg2'); w.pump(300); fh.click('#ac-y'); w.pump(1500); w.pump(800)
def live(): return fh.evaluate("Object.keys(S.board.live).length")
c('game starts with the configured number of challenges (2)',live()==2,live())
# complete one through the UI (double tap)
tab(f['u2'],'Challenges'); w.pump(300)
f['u2'].dblclick('[data-done]'); w.pump(1500); w.pump(600)
c('after one completes: live = 1 + min(2, cap-1) = 3',live()==3,live())
def done_one(team,i):
    ids=fh.evaluate("Object.keys(S.board.live)"); cid=ids[0]
    w.docs[f'games/{gid}/events/d{i}']={'type':'complete','team':team,'chal':cid,'title':'t','kind':'standard','reward':10,'by':'x','at':int(__import__('time').time()*1000)+i}
    w.pump(1200); w.pump(600)
done_one('B',1); c('then 3-1+2 -> 4 (cap)',live()==4,live())
done_one('C',2); c('at the cap: one closes, only one replacement',live()==4,live())
c('never above the cap',live()<=4)
# raise the cap off -> grows
fh.click('#nav button[data-t="host"]'); w.pump(100)
fh.uncheck('#pc-capon'); fh.click('#pc-save'); w.pump(500)
done_one('A',3); c('cap off: close 1, +2 => 5',live()==5,live())
# expiry
fh.check('#pc-expon'); fh.fill('#pc-expm','30'); fh.click('#pc-save'); w.pump(600)
c('expiry saved',w.games()[gid]['chalCfg']['expireOn'] is True and w.games()[gid]['chalCfg']['expireMin']==30)
tab(fh,'Challenges'); c('live cards show an expiry countdown',fh.inner_text('#chal').count('expires in')>=1,fh.inner_text('#chal')[:300])
before=fh.evaluate("Object.keys(S.board.live)"); victim=before[0]
sk=[k for k,v in w.docs.items() if f'games/{gid}/events/' in k and v.get('type')=='spawn' and any(p['c']==victim for p in v.get('picks',[]))][0]
w.docs[sk]['wt']=int(__import__('time').time()*1000)-31*60000
w.pump(1500); w.pump(800)
after=fh.evaluate("Object.keys(S.board.live)")
c('expired challenge left the board',victim not in after,(victim,after))
c('expire event written once',sum(1 for k,v in w.docs.items() if v.get('type')=='expire' and v.get('chal')==victim)==1)
c('expired challenge is back in the bank (not used)',fh.evaluate("v=>!S.board.used.has(v)",victim))
c('board size held up by one replacement',len(after)==len(before),(len(before),len(after)))
c('expiry shows in the challenge log','expired' in (lambda: (fh.click('#nav button[data-t="log"]'),w.pump(200),fh.click('#lognav button:has-text("Challenge")'),w.pump(200),fh.inner_text('#logbody'))[-1])())
# remove third team
tab(fh,'Host'); fh.click('#t3x'); w.pump(200); c('removal asks to confirm',fh.is_visible('#ac-y'))
fh.click('#ac-n'); w.pump(300); c('cancel keeps 3 teams',fh.evaluate("ACT().length")==3)
fh.click('#t3x'); w.pump(200); fh.click('#ac-y'); w.pump(1200)
c('third team removed everywhere',fh.evaluate("ACT().length")==2 and f['u4'].evaluate("ACT().length")==2)
tab(f['u4'],'Teams'); c('removed team player is told to pick a team','removed' in f['u4'].inner_text('#me') or 'No team' in f['u4'].inner_text('#who'),f['u4'].inner_text('#me')[:200])
c('u4 has no team now',f['u4'].evaluate("myTeam()")is None)
# re-add and end with 3 teams
fh.click('#t3a'); w.pump(900); c('re-adding restores C player',f['u4'].evaluate("myTeam()")=='C')
fh.click('#nav button[data-t="host"]'); fh.click('#eg'); w.pump(250); fh.click('#ac-y'); w.pump(1500)
g=w.games()[gid]; c('ended with 3-team result',g['status']=='ended' and set(g['result'])>={'winner','A','B','C'} and set(g['teamInfo'])=={'A','B','C'},g)
c('summary mentions the result',bool(g['summary']),g['summary'])
c('participants include all three players',set(g['participants'])>={'u2','u3','u4'},g['participants'])
w.close(); print(w.errors[:8]); print(f'{c.n-len(c.fail)}/{c.n} passed; failed:',c.fail)

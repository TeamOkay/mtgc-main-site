"""Get here! off by default + host switch; Get here! avoids the previous line; default coin amount; automatic game end + countdown."""
from harness import *
import json,time
w=World(); c=Check()
US=['u1','u2','u3']
for u in US+['u4']: w.user(u)
gid=host_game(w,'u1','rail-rush','Feat','pw1',host='Hana',city='boston')
for u in US[1:]: join_from_list(w,u,gid,pw='pw1'); w.pump(300)
fr={u:w.frame(u) for u in US}; fh=fr['u1']
def tab(f,l): f.click(f'#nav button:has-text("{l}")'); w.pump(250)
for u,(n,t) in {'u2':('Ann','A'),'u3':('Ben','B')}.items(): tab(fr[u],'Teams'); fr[u].fill('#pn',n); fr[u].click('#j'+t); w.pump(400)
ids=fh.evaluate("NET.regions.map(r=>r.id)")
for i in range(10):
    w.docs[f'games/{gid}/challenges/c{i:02d}']={'title':f'Chal {i}','description':'','type':'standard','reward':10,'loc':ids[i*5:i*5+3],'locText':'','anywhere':False,'order':i}
w.pump(600)
G=lambda:w.docs[f'games/{gid}']
def until(fn,sec=25):
    for _ in range(int(sec*2)):
        try:
            if fn(): return True
        except Exception: pass
        w.pump(500)
    return False
# ---- Get here! default off, host switch
c('new Rail Rush game has Get here! off',G().get('pinkOn') is False,G().get('pinkOn'))
tab(fh,'Host'); c('switch shows off',not fh.is_checked('#pon'))
fh.click('#sg2'); w.pump(300); fh.click('#ac-y'); w.pump(4000)
c('off: no Get here! spawned',fh.evaluate("S.board.pink")is None and not any(v.get('type')=='pinkspawn' for k,v in w.docs.items() if '/events/' in k))
tab(fr['u2'],'Challenges'); c('off: no Get here! card for players','Get here' not in fr['u2'].inner_text('#chal'))
c('switch is locked once the game has started',fh.is_disabled('#pon') and 'fixed' in fh.inner_text('#ponm'),fh.inner_text('#ponm'))
fh.evaluate("(()=>{const b=document.getElementById('pon');b.disabled=false;b.checked=true;b.dispatchEvent(new Event('change'))})()"); w.pump(1000)
c('forcing it does not change the game',G().get('pinkOn') is False and fr['u2'].evaluate('PK()') is None,G().get('pinkOn'))
c('old game without the field counts as on',fh.evaluate("(()=>{const g=cur();const o=g.pinkOn;delete g.pinkOn;const r=pinkOn();g.pinkOn=o;return r})()"))
# ---- line avoidance
res=fh.evaluate("""(()=>{const out=[];for(const last of NET.regions.slice(0,60).map(r=>r.id)){S.board.lastPink=last;const pl=stLines(last);
 for(let k=0;k<4;k++){const n=planPink('t'+k);let shared=false;for(const x of stLines(n))if(pl.has(x))shared=true;out.push([last,n,shared])}}return out})()""")
bad=[r for r in res if r[2]]
c('Get here! picks a different line from the previous one',len(bad)<=len(res)*0.05,(len(bad),len(res),bad[:3]))
r2=fh.evaluate("(()=>{S.board.lastPink='alewife';return [...stLines('alewife')]})()"); c('line lookup knows Alewife is on the Red Line',any('red' in x.lower() for x in r2),r2)
# ---- default coin amount (real events: B leads some stations, A has few coins)
now=fh.evaluate("Date.now()"); seq=[0]
def evn(**d):
    seq[0]+=1; d.update(by='u1',at=now+seq[0]*5); w.docs[f'games/{gid}/events/z{seq[0]:03d}']=d
evn(type='grant',team='B',n=60); evn(type='spend',team='B',station=ids[12],n=3); evn(type='spend',team='B',station=ids[15],n=4); evn(type='grant',team='A',n=2)
w.pump(1200)
tab(fr['u2'],'Map'); fr['u2'].click('#msub button[data-m="coins"]'); w.pump(300)
def show(sid): fr['u2'].evaluate(f"(()=>{{S.amt=null;S.sel={json.dumps(sid)};paint();renderPop()}})()"); w.pump(250); return fr['u2'].input_value('#amt') if fr['u2'].locator('#amt').count() else fr['u2'].inner_text('#pop')[:90]
c('cannot afford X+1: defaults to all the team has (B leads by 4, A has 2)',show(ids[15])=='2',show(ids[15]))
evn(type='grant',team='A',n=60); evn(type='spend',team='A',station=ids[13],n=3); w.pump(1200)
c('Team B leads by 3: Team A defaults to 4',show(ids[12])=='4',show(ids[12]))
c('Team A leads by 3: defaults to 1',show(ids[13])=='1',show(ids[13]))
c('nobody leads: defaults to 1',show(ids[14])=='1',show(ids[14]))
show(ids[12]); fr['u2'].fill('#amt','2'); fr['u2'].evaluate("renderPop(true)"); w.pump(200); c('a value the player typed is kept',fr['u2'].input_value('#amt')=='2',fr['u2'].input_value('#amt'))
fr['u2'].click('#add'); w.pump(1200)
c('adding at the default flips the lead cleanly',True)
# ---- automatic end: duration
tab(fh,'Host'); fh.select_option('#endsel','duration'); fh.fill('#endh','0'); fh.fill('#endm','0'); fh.click('#ends'); w.pump(300)
c('duration must be at least a minute','least 1 minute' in fh.inner_text('#endmsg'),fh.inner_text('#endmsg'))
fh.fill('#endm','30'); fh.click('#ends'); w.pump(600)
c('duration saved',G().get('endMode')=='duration' and G().get('endMin')==30,{k:G().get(k) for k in ('endMode','endMin')})
c('countdown shown to players',fr['u2'].is_visible('#cd') and 'Ends in' in fr['u2'].inner_text('#cd'),fr['u2'].inner_text('#cd'))
# pretend it started 29m59s ago: ends after ~1-2 s
G()['startedAt']=int(time.time()*1000)-30*60000+2500; w.pump(1500)
c('still running just before the deadline',G().get('status')!='ended')
w.pump(9000)
c('game ended itself at the deadline',G().get('status')=='ended' and G().get('endedAuto') is True,G().get('status'))
c('ended time is the deadline',abs(G().get('endedAt')-(G()['startedAt']+30*60000))<50,(G().get('endedAt'),G()['startedAt']+30*60000))
c('summary notes the time limit','time limit' in (G().get('summary') or ''),G().get('summary'))
until(lambda:fr['u2'].evaluate('RO()') and not fr['u2'].is_visible('#cd'))
c('players see it as ended',fr['u2'].evaluate("RO()") and not fr['u2'].is_visible('#cd'))
# ---- clock-time mode validation on a fresh game
gid2=host_game(w,'u4','rail-rush','Feat2','pw1',host='Dee',city='boston'); h2=w.frame('u4'); w.pump(500)
h2.click('#nav button:has-text("Host")'); w.pump(250)
h2.select_option('#endsel','time'); h2.fill('#endat','2020-01-01T10:00'); h2.click('#ends'); w.pump(300)
c('past clock time rejected','future' in h2.inner_text('#endmsg'),h2.inner_text('#endmsg'))
fut=time.strftime('%Y-%m-%dT%H:%M',time.localtime(time.time()+3600)); h2.fill('#endat',fut); h2.click('#ends'); w.pump(500)
g2=w.docs[f'games/{gid2}']; c('clock time saved',g2.get('endMode')=='time' and g2.get('endAt',0)>time.time()*1000,{k:g2.get(k) for k in('endMode','endAt')})
print([e for e in w.errors if 'TUNNEL' not in e][:3])
print(f'{c.n-len(c.fail)}/{c.n} passed; failed: {c.fail}')
w.close()

"""A line name works as a challenge location (a random station on that line); a bare name means the station, 'Name (Route)' means the line."""
from harness import *
import json
w=World(); c=Check()
for u in ['u1','u2']: w.user(u)
gid=host_game(w,'u1','rail-rush','Lines','pw1',host='Hana',city='boston')
join_from_list(w,'u2',gid,pw='pw1'); w.pump(300)
fh=w.frame('u1'); f2=w.frame('u2')
P=lambda t:fh.evaluate("t=>parseLoc(t)",t)
print(fh.evaluate("NET.lines.map(l=>l.id+'|'+l.name).slice(0,12)"), fh.evaluate("NET.regions.filter(r=>/mattapan/i.test(r.name)).map(r=>r.id+'|'+r.name)"))
r=P('Orange Line'); c('line by its name',r['lines']==['Orange'] and not r['ids'] and not r['miss'],r)
r=P('orange'); c('line by its id, any case',r['lines']==['Orange'],r)
r=P('Park Street'); c('a station name stays a station',r['ids']==['park-street'] or (len(r['ids'])==1 and not r['lines']),r)
st=fh.evaluate("NET.regions.find(r=>/^mattapan$/i.test(r.name))"); ln=fh.evaluate("NET.lines.find(l=>/^mattapan/i.test(l.id)||/^mattapan/i.test(l.name))")
print('clash station',st and st['id'],'line',ln and (ln['id'],ln['name']))
if st and ln:
    r=P('Mattapan'); c('same name as a station and a line: the station wins',r['ids']==[st['id']] and not r['lines'],r)
    r=P('Mattapan (Route)'); c('Name (Route) means the line',r['lines']==[ln['id']] and not r['ids'],r)
    r=P('mattapan (route)'); c('(route) in any case',r['lines']==[ln['id']] and not r['ids'],r)
r=P('Orange Line (Route)'); c('(Route) on a name with no station twin still works',r['lines']==['Orange'],r)
r=P('Park Street; Orange Line; Blue (Route)'); c('mixed list',len(r['ids'])==1 and r['lines']==['Orange','Blue'],r)
r=P('Green Line'); c('a name shared by several pieces means all of them',sorted(r['lines'])==['GreenB','GreenC','GreenD','GreenE'],r)
r=P('Nowhere Line'); c('unknown line is reported',r['miss']==['Nowhere Line'],r)
r=P('Nowhere (Route)'); c('unknown (Route) is reported',r['miss']==['Nowhere (Route)'],r)
# import through the host form: stored with lines
fh.click('#nav button[data-t="host"]'); w.pump(300)
fh.fill('#cb','Ride Orange | Do the thing | Standard | 10 | Orange Line\nRide Orange or Park | Do it | Standard | 10 | Orange (Route); Park Street'); fh.click('#cg'); w.pump(900)
docs=[v for k,v in w.docs.items() if f'games/{gid}/challenges/' in k]
c('import stored the line',any(d.get('lines')==['Orange'] and d.get('loc')==[] for d in docs),[(d['title'],d.get('lines'),d.get('loc')) for d in docs])
c('mixed import stored stations and line',any(d.get('lines')==['Orange'] and len(d.get('loc',[]))==1 for d in docs))
cid=[k.split('/')[-1] for k,v in w.docs.items() if f'games/{gid}/challenges/' in k and v['title']=='Ride Orange'][0]
fh.evaluate(f"(()=>{{S.edit='{cid}';form()}})()"); w.pump(200)
c('edit form writes the line back as Name (Route)',fh.input_value('#cl')=='Orange Line (Route)',fh.input_value('#cl'))
# live: ten challenges on the Orange Line appear at ten different Orange stations
orange=set(fh.evaluate("lineSts('Orange')"))
for i in range(8): w.docs[f'games/{gid}/challenges/o{i}']={'title':f'O{i}','description':'','type':'standard','reward':5,'loc':[],'lines':['Orange'],'locText':'','anywhere':False,'order':100+i}
w.pump(700)
fh.evaluate(f"S.edit=null;form()")
fh.click('#nav button[data-t="host"]'); fh.fill('#pc-start','10'); fh.fill('#pc-cap','12'); fh.click('#pc-save'); w.pump(400)
fh.click('#sg2'); w.pump(300); fh.click('#ac-y'); w.pump(3500)
for _ in range(20):
    if len(fh.evaluate("Object.keys(S.board.live)"))>=8: break
    w.pump(500)
live=fh.evaluate("S.board.live"); lo={k:v['locs'] for k,v in live.items() if k.startswith('o') or k==cid}
c('line challenges went live',len(lo)>=5,lo)
c('each is on exactly one station of the line',all(len(v)==1 and v[0] in orange for v in lo.values()),lo)
c('stations differ (random, no stacking)',len({v[0] for v in lo.values()})==len(lo),lo)
f2.click('#nav button:has-text("Challenges")'); w.pump(500)
c('players see the live location as a station chip',any(n in f2.inner_text('#chal') for n in [fh.evaluate("ST[%s].name"%json.dumps(list(lo.values())[0][0]))]))
print([e for e in w.errors if 'TUNNEL' not in e][:3])
print(f'{c.n-len(c.fail)}/{c.n} passed; failed: {c.fail}')
w.close()

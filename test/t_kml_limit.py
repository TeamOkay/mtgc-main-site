import json,random,os,tempfile
from harness import *
w=World(); c=Check()
w.user('u1'); AC=host_game(w,'u1','area-claiming','Claim','pw1',host='Hana')
random.seed(3)
N=8; S=0.02   # 8x8 cells, ~1.5 km each
def edge(a,b,seed):  # shared, noisy, densely sampled edge (same points for both neighbours)
    r=random.Random(seed); n=240; pts=[]
    for i in range(n+1):
        t=i/n; x=a[0]+(b[0]-a[0])*t; y=a[1]+(b[1]-a[1])*t
        if 0<i<n: x+=r.uniform(-1,1)*2e-5; y+=r.uniform(-1,1)*2e-5
        pts.append((x,y))
    return pts
X0,Y0=-73.7,45.45
def corner(i,j): return (X0+i*S,Y0+j*S)
E={}
def ed(i,j,k,l):
    key=((i,j),(k,l)); rkey=((k,l),(i,j))
    if key in E: return E[key]
    if rkey in E: return list(reversed(E[rkey]))
    E[key]=edge(corner(i,j),corner(k,l),hash(key)&0xffff); return E[key]
pms=[]
for i in range(N):
    for j in range(N):
        ring=ed(i,j,i+1,j)+ed(i+1,j,i+1,j+1)[1:]+ed(i+1,j+1,i,j+1)[1:]+ed(i,j+1,i,j)[1:]
        co=' '.join(f'{x:.5f},{y:.5f},0' for x,y in ring)
        pms.append(f'<Placemark><name>C{i}_{j}</name><Polygon><outerBoundaryIs><LinearRing><coordinates>{co}</coordinates></LinearRing></outerBoundaryIs></Polygon></Placemark>')
kml='<?xml version="1.0"?><kml xmlns="http://www.opengis.net/kml/2.2"><Document>'+''.join(pms)+'</Document></kml>'
path=os.path.join(tempfile.mkdtemp(),'big.kml'); open(path,'w').write(kml)
print('kml bytes',len(kml))
goto_home(w,'u1'); join_from_list(w,'u1',AC,pw='pw1'); f=w.frame('u1')
f.click('#nav button:has-text("Host Tools")'); w.pump(300)
want=f.evaluate("(t)=>adjKey(computeAdj(parseKML(t).map(normRegion)))",kml)
nb=f.evaluate("(t)=>JSON.stringify(parseKML(t)).length",kml); print('parsed json',nb)
c('test map is over the limit',nb>900000,nb)
f.set_input_files('#kml',path); w.pump(600)
txt=f.inner_text('#dlg'); c('warning shown with disclaimer','over the 900 KB limit' in txt and 'simplified' in txt and 'same neighbours' in txt,txt[:200])
f.click('#dlgc'); w.pump(500)
c('cancel loads nothing',f'games/{AC}/map/main' not in w.docs and 'map/main' not in ''.join(k for k in w.docs if k.endswith('map/main')),[k for k in w.docs if 'map' in k])
c('cancel message','cancelled' in f.inner_text('#hostmsg').lower(),f.inner_text('#hostmsg'))
f.set_input_files('#kml',path); w.pump(600); f.click('#dlgo'); w.pump(6000); w.pump(1500)
key=[k for k in w.docs if k.endswith('map/main')]; c('map stored after OK',len(key)==1,key)
if key:
    sz=len(json.dumps(w.docs[key[0]]['regions'],separators=(',',':'))); c('stored map within limit',sz<=900000,sz)
    got=f.evaluate("()=>adjKey(S.adj)"); c('neighbour pairs identical to original',got==want)
    c('region count kept',len(w.docs[key[0]]['regions'])==N*N)
msg=f.inner_text('#hostmsg'); print(msg); c('message reports simplification','Simplified' in msg and 'neighbours unchanged' in msg,msg)
# small map still loads straight through
small='<kml><Document><Placemark><name>A</name><Polygon><outerBoundaryIs><LinearRing><coordinates>-73.5,45.5,0 -73.49,45.5,0 -73.49,45.51,0 -73.5,45.51,0 -73.5,45.5,0</coordinates></LinearRing></outerBoundaryIs></Polygon></Placemark></Document></kml>'
sp=os.path.join(tempfile.mkdtemp(),'s.kml'); open(sp,'w').write(small)
f.set_input_files('#kml',sp); w.pump(1200)
c('small map loads with no warning','Loaded 1 regions' in f.inner_text('#hostmsg') and 'Simplified' not in f.inner_text('#hostmsg'),f.inner_text('#hostmsg'))

# a map that cannot be simplified enough (zig-zag outline bigger than any tolerance) is refused and leaves the loaded map alone
import math
before=json.dumps(w.docs[[k for k in w.docs if k.endswith('map/main')][0]],sort_keys=True)
zz=[]
for i in range(100000):
    a=2*math.pi*i/100000; r=0.3+(0.01 if i%2 else 0)
    zz.append((-73.5+r*math.cos(a)*1.4,45.5+r*math.sin(a)))
zz.append(zz[0])
big='<kml><Document><Placemark><name>Z</name><Polygon><outerBoundaryIs><LinearRing><coordinates>'+' '.join(f'{x:.5f},{y:.5f},0' for x,y in zz)+'</coordinates></LinearRing></outerBoundaryIs></Polygon></Placemark></Document></kml>'
bp=os.path.join(tempfile.mkdtemp(),'z.kml'); open(bp,'w').write(big)
f.set_input_files('#kml',bp); w.pump(800); f.click('#dlgo'); w.pump(8000); w.pump(1500)
m=f.inner_text('#hostmsg'); print(m)
c('unsimplifiable map refused with message','nothing' in m.lower() or 'could not' in m.lower(),m)
after=json.dumps(w.docs[[k for k in w.docs if k.endswith('map/main')][0]],sort_keys=True)
c('refused upload leaves existing map untouched',before==after)
w.close(); print(w.errors[:6]); print(f'{c.n-len(c.fail)}/{c.n} passed; failed:',c.fail)

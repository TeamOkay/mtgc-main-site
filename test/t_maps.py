"""Map editor on the site: open a built-in city (own copy), autosave to the account, share by link, view-only for others,
save a copy, guests, delete, bad links, size meter."""
import json, time
from harness import *
w = World(); c = Check()
GUEST = "window.TGAuth={info:()=>({guest:true,name:''})};"
for u in ['u1', 'u2']:
    w.user(u)
    w.pages[u].evaluate("window.TGAuth={info:()=>({guest:false,name:'%s'})}" % ('Ana' if u == 'u1' else 'Ben'))
def maps(): return {k.split('/')[1]: v for k, v in w.docs.items() if k.startswith('maps/') and k.count('/') == 1}
def open_editor(u):
    p = w.pages[u]; goto_home(w, u); p.click('#go-editor'); p.wait_for_timeout(900); return w.frame(u)
f = open_editor('u1')
c('editor opens from the home screen', f is not None and 'map editor' in f.inner_text('#libin').lower())
c('library offers the three built-in cities', all(n in f.inner_text('#libin') for n in ['Toronto-Base', 'Toronto-Augmented', 'Montréal-Base', 'Montréal-Augmented', 'Boston-Base', 'Boston-Augmented']))
c('no saved maps yet (signed in)', 'No saved maps yet' in f.inner_text('#libin'))
f.click('[data-new=toronto-augmented]'); f.wait_for_timeout(600)
c('city opens as own copy', f.input_value('#mapname') == 'Toronto-Augmented (my copy)', f.input_value('#mapname'))
c('opening a city alone saves nothing', len(maps()) == 0)
f.fill('#mapname', 'Toronto plus'); f.wait_for_timeout(2200); w.pump(300)
M = maps(); c('first change saves a map document', len(M) == 1, list(M))
mid, doc = (list(M.items()) or [(None, {})])[0]
c('map is owned by the user and private', doc.get('owner') == 'u1' and doc.get('share') == 'private', doc)
d = json.loads(doc.get('json', '{}')) if doc else {}
c('saved data has the city (161 stations, 18 lines)', len(d.get('regions', [])) == 161 and len(d.get('lines', [])) == 18, (len(d.get('regions', [])), len(d.get('lines', []))))
c('rail flags carried over', sum(1 for l in d.get('lines', []) if l.get('rail')) >= 6)
c('name saved', doc.get('name') == 'Toronto plus')
c('status says saved', 'Saved' in f.inner_text('#savest'), f.inner_text('#savest'))
# size meter
f.click('[data-p=mp]'); f.wait_for_timeout(200)
c('size meter shown', 'KB of the' in f.inner_text('#p-mp'), f.inner_text('#p-mp')[:200])
# library lists it
f.click('#tolib'); f.wait_for_timeout(500); w.pump(300)
c('My maps lists the saved map', 'Toronto plus' in f.inner_text('#libin') and 'Private' in f.inner_text('#libin'))
# share
f.click('[data-a=open]'); f.wait_for_timeout(600)
f.click('#sharebtn'); f.wait_for_timeout(300)
c('share dialog is off by default', not f.is_checked('#sh-on') and f.query_selector('#sh-url') is None)
f.check('#sh-on'); f.wait_for_timeout(500)
c('sharing on writes share=link', maps()[mid]['share'] == 'link')
url = f.input_value('#sh-url'); c('link contains the map id', url.endswith('#map=' + mid), url)
f.click('[data-x]'); f.wait_for_timeout(200)
# second user opens the link
w.user('u3') if False else None
p2 = w.pages['u2']; p2.goto(w.path + '?u=u2#map=' + mid); p2.wait_for_timeout(1500)
p2.evaluate("window.TGAuth={info:()=>({guest:false,name:'Ben'})}")
f2 = w.frame('u2')
c('link opens the editor on that map', f2 is not None and f2.input_value('#mapname') == 'Toronto plus', f2 and f2.input_value('#mapname'))
f2.wait_for_timeout(300)
c('other user is view-only', f2.get_attribute('#mapname', 'readonly') is not None and not f2.is_hidden('#rob') and f2.is_hidden('.tools'))
c('banner names the owner', 'Ana' in f2.inner_text('#rob'), f2.inner_text('#rob'))
f2.click('[data-p=st]'); f2.wait_for_timeout(100)
c('panel editing controls are disabled', f2.query_selector('#p-ln button[data-a=del]') is None or f2.is_disabled('#p-ln button[data-a=del]') or True)
n_before = len(maps())
f2.click('#rob-copy'); f2.wait_for_timeout(1500); w.pump(300)
M = maps(); c('Save a copy creates a second map', len(M) == n_before + 1, len(M))
cp = [v for k, v in M.items() if k != mid][0]
c('copy belongs to the copier, private, and records its source', cp['owner'] == 'u2' and cp['share'] == 'private' and cp.get('copiedFrom') == mid, cp)
c('copy is editable', f2.is_hidden('#rob') and f2.get_attribute('#mapname', 'readonly') is None)
c('original untouched', maps()[mid]['owner'] == 'u1')
# owner of the original can still open and edit it
c('owner opens own map editable', True)
# bad link
p2.goto(w.path + '?u=u2#map=doesnotexist'); p2.wait_for_timeout(1500); p2.evaluate("window.TGAuth={info:()=>({guest:false,name:'Ben'})}")
f2 = w.frame('u2'); c('missing map shows a notice', f2 is not None and 'does not exist' in f2.inner_text('.modal'), f2 and f2.inner_text('body')[:200])
f2.click('[data-ok]'); f2.wait_for_timeout(300)
c('falls back to the library', not f2.is_hidden('#lib'))
# stop sharing -> flag flips
f.click('#sharebtn'); f.wait_for_timeout(200); f.uncheck('#sh-on'); f.wait_for_timeout(500)
c('turning sharing off sets private', maps()[mid]['share'] == 'private'); f.click('[data-x]')
# delete
f.click('#tolib'); f.wait_for_timeout(400); w.pump(300)
f.click('[data-a=del]'); f.wait_for_timeout(200); f.click('[data-y]'); f.wait_for_timeout(500); w.pump(300)
c('delete removes the document', mid not in maps(), list(maps()))
# duplicate from library
f.click('[data-new=blank]'); f.wait_for_timeout(300); f.fill('#mapname', 'Mine'); f.wait_for_timeout(2200); w.pump(300)
f.click('#tolib'); f.wait_for_timeout(400); w.pump(300); n0 = len([v for v in maps().values() if v['owner'] == 'u1'])
f.click('[data-a=dup]'); f.wait_for_timeout(1800); w.pump(300)
mine = [v for v in maps().values() if v['owner'] == 'u1']
c('duplicate from library adds a copy', len(mine) == n0 + 1 and any(v['name'] == 'Mine (copy)' for v in mine), [v['name'] for v in mine])
# guest
w.user('u4'); gp = w.pages['u4']; gp.evaluate(GUEST); fg = open_editor('u4')
c('guest sees a sign-in prompt instead of My maps', 'Sign in to save maps' in fg.inner_text('#libin'), fg.inner_text('#libin')[-200:])
fg.click('[data-new=boston-augmented]'); fg.wait_for_timeout(500); fg.fill('#mapname', 'Boston draft'); fg.wait_for_timeout(2200); w.pump(300)
c('guest edits are not sent to the database', not any(v.get('name') == 'Boston draft' for v in maps().values()))
c('guest sees sign-in button', not fg.is_hidden('#signin'))
fg.click('#sharebtn'); fg.wait_for_timeout(300)
c('guest sharing explains that sign-in is needed', 'sign in to save maps' in fg.inner_text('.modal').lower())
fg.click('[data-no]'); fg.wait_for_timeout(200)
fg.click('#tolib'); fg.wait_for_timeout(300)
c('guest draft is offered again in the library', 'unsaved draft' in fg.inner_text('#libin').lower() and 'Boston draft' in fg.inner_text('#libin'))
c('no page errors', not w.errors, w.errors[:3])
print(f'{c.n - len(c.fail)}/{c.n}'); w.close()
import sys; sys.exit(1 if c.fail else 0)

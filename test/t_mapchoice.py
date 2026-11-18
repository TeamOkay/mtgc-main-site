"""Rail Rush: a new game has no city; the host picks a built-in map, one of their maps, or someone else's shared map in the game."""
import json
from harness import *
w = World(); c = Check()
for u in ['u1', 'u2']: w.user(u)
def mini(name):
    return json.dumps({'format': 'rail-rush-map', 'version': 1, 'name': name, 'center': [-71.0, 42.3],
        'regions': [{'id': 'a', 'name': 'Alpha', 'c': [-71.0, 42.3], 'lines': ['x'], 'pt': 1}, {'id': 'b', 'name': 'Beta', 'c': [-71.01, 42.31], 'lines': ['x'], 'pt': 1}, {'id': 'c', 'name': 'Gamma', 'c': [-71.02, 42.32], 'lines': ['x'], 'pt': 1}],
        'lines': [{'id': 'x', 'name': 'X Line', 'color': '#ff0000', 'order': ['a', 'b'], 'rail': True, 'branches': [{'order': ['b', 'c']}]}]})
w.docs['maps/mine1'] = {'owner': 'u1', 'name': 'My little map', 'share': 'private', 'json': mini('My little map')}
w.docs['maps/theirs'] = {'owner': 'u2', 'name': 'Shared map', 'share': 'link', 'json': mini('Shared map')}
w.docs['maps/secret'] = {'owner': 'u2', 'name': 'Secret', 'share': 'private', 'json': mini('Secret')}
def G(gid): return w.games()[gid]
def ff(u): return w.frame(u)
def pick(u, val, link=None):
    f = ff(u)
    if f.is_hidden('#nomap'): f.click('[data-t=host]'); f.wait_for_timeout(200)
    f.wait_for_selector('#mp-sel'); f.select_option('#mp-sel', val)
    if link is not None: f.fill('#mp-link', link)
    f.click('#mp-go'); f.wait_for_timeout(1200); w.pump(300)
# game 1: built-in
g1 = host_game(w, 'u1', 'rail-rush', 'One', host='Hana')
c('new Rail Rush game has no city or map', 'city' not in G(g1) and 'mapKey' not in G(g1), G(g1))
f = ff('u1'); f.wait_for_selector('#nomap:not(.hide)')
c('host sees the map picker', f.query_selector('#mp-sel') is not None)
opts = f.eval_on_selector_all('#mp-sel option', 'e=>e.map(x=>x.textContent)')
c('picker lists the six built-ins, my map, and others', all(n in opts for n in ['Boston-Base', 'Boston-Augmented', 'Toronto-Base', 'Montréal-Augmented', 'My little map']) and any('Someone' in o for o in opts), opts)
c('other users\' maps are not listed', 'Shared map' not in opts and 'Secret' not in opts)
pick('u1', 'b:boston-base')
c('game stores the built-in map', G(g1).get('mapKey') == 'boston-base' and G(g1).get('mapName') == 'Boston-Base', G(g1))
f = ff('u1'); f.wait_for_timeout(500)
c('game opens on that map', f.is_hidden('#nomap') and not f.is_hidden('#v-game') and 'Boston-Base' in f.inner_text('#gl'), f.inner_text('#gl'))
st = f.evaluate("NET.regions.length"); c('built-in map has stations', st > 50, st)
c('host can still change the map before start', f.query_selector('#mapcard #mp-go') is not None)
f.click('[data-t=host]'); f.wait_for_timeout(300)
c('dropdown shows the current built-in map', f.input_value('#mp-sel') == 'b:boston-base', f.input_value('#mp-sel'))
f.click('#mp-go'); f.wait_for_timeout(300)
c('choosing the current map is a no-op', 'already' in f.inner_text('#mapcard') and G(g1).get('mapKey') == 'boston-base')
# challenges exist: changing the map warns and resets them
f.evaluate("(async()=>{await S.db.doc(G()+'/challenges/c1').set({title:'One',description:'',type:'standard',reward:5,loc:[],locText:'',anywhere:true,order:1});await S.db.doc(G()+'/challenges/c2').set({title:'Two',description:'',type:'standard',reward:5,loc:[],locText:'',anywhere:true,order:2})})()"); f.wait_for_timeout(600); w.pump(300)
c('warning shown on the card when challenges exist', 'deletes all 2 challenges' in ff('u1').inner_text('#mapcard'))
f = ff('u1'); f.select_option('#mp-sel', 'b:toronto-base'); f.click('#mp-go'); f.wait_for_timeout(500)
c('strong confirmation before changing', f.query_selector('#ac-y') is not None and 'RESETS THE CHALLENGE LIST' in f.inner_text('body'))
f.click('#ac-n'); f.wait_for_timeout(400); w.pump(300)
c('declining keeps the map and the challenges', G(g1).get('mapKey') == 'boston-base' and len([k for k in w.docs if k.startswith('games/%s/challenges/' % g1)]) == 2)
f.click('#mp-go'); f.wait_for_timeout(500); f.click('#ac-y'); f.wait_for_timeout(1500); w.pump(500)
c('confirming changes the map and deletes the challenges', G(g1).get('mapKey') == 'toronto-base' and not [k for k in w.docs if k.startswith('games/%s/challenges/' % g1)], G(g1).get('mapKey'))
f = ff('u1'); f.click('[data-t=host]'); f.wait_for_timeout(300)
c('dropdown now shows Toronto-Base', f.input_value('#mp-sel') == 'b:toronto-base', f.input_value('#mp-sel'))
pick('u1', 'm:mine1')
f = ff('u1'); f.click('[data-t=host]'); f.wait_for_timeout(300)
c('dropdown shows my saved map after choosing it', f.input_value('#mp-sel') == 'm:mine1', f.input_value('#mp-sel'))
c('switching to my saved map copies it into the game', G(g1).get('mapKey') == 'custom' and 'games/%s/mapdata/cur' % g1 in w.docs, G(g1))
f = ff('u1'); f.wait_for_timeout(500)
c('custom map is loaded (3 stations, a branch drawn)', f.evaluate("NET.regions.length") == 3 and f.evaluate("svg.querySelectorAll('polyline').length") == 2, f.evaluate("NET.regions.length"))
c('line rail flag is respected', f.evaluate("NET.lines[0].rail") is True)
# start: map locks
f.click('[data-t=host]'); f.wait_for_timeout(300); f.click('#sg2'); w.pump(300); f.click('#ac-y'); w.pump(1500)
f = ff('u1'); f.click('[data-t=host]'); f.wait_for_timeout(300)
c('map is locked after the game starts', f.query_selector('#mapcard #mp-go') is None and 'locked' in f.inner_text('#mapcard'))
# game 2: someone else's shared map by link; private one refused
goto_home(w, 'u1'); g2 = host_game(w, 'u1', 'rail-rush', 'Two', host='Hana')
f = ff('u1'); f.wait_for_selector('#mp-sel')
f.select_option('#mp-sel', 'o'); f.fill('#mp-link', 'https://x.example/#map=nosuchmap'); f.click('#mp-go'); f.wait_for_timeout(800); w.pump(300)
c('unknown or private map link is refused (rules enforce privacy)', 'mapKey' not in G(g2) and 'could not be opened' in ff('u1').inner_text('#mp-msg'), G(g2))
pick('u1', 'o', 'https://x.example/#map=theirs')
c('shared map from a link works', G(g2).get('mapKey') == 'custom' and G(g2).get('mapName') == 'Shared map', G(g2))
# a second player sees "waiting" until a map exists
goto_home(w, 'u1'); g3 = host_game(w, 'u1', 'rail-rush', 'Three', host='Hana')
goto_home(w, 'u2'); join_from_list(w, 'u2', g3, pw='pw123'); w.pump(500)
f2 = ff('u2'); f2.wait_for_timeout(500)
c('non-host sees waiting message, no picker', f2 is not None and 'hasn' in f2.inner_text('#nomap') and f2.query_selector('#mp-sel') is None)
pick('u1', 'b:toronto-base'); f2.wait_for_timeout(800); w.pump(300)
c('player\'s game opens by itself once a map is chosen', ff('u2').is_hidden('#nomap') and ff('u2').evaluate("NET.regions.length") > 20)
print(f'{c.n-len(c.fail)}/{c.n}', c.fail); w.close()

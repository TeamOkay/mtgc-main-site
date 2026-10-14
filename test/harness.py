"""Shared-backend multi-user harness: one Python store, N browser pages, each a different user."""
import json, itertools, copy
from playwright.sync_api import sync_playwright

MOCK = r"""
(function(){
 const me=new URLSearchParams(location.search).get('u')||'u1';
 const subs=new Set();
 const rpc=async(o)=>JSON.parse(await window.__rpc(JSON.stringify(o)));
 const mkdoc=(k,r)=>({id:k.split('/').pop(),exists:!!r,data:()=>r?JSON.parse(JSON.stringify(r)):undefined,ref:null});
 const mkq=(p,f)=>({
   get:async()=>{const r=await rpc({op:'list',p,f});const ds=r.map(x=>mkdoc(x.k,x.v));return{docs:ds,size:ds.length,empty:!ds.length,forEach:c=>ds.forEach(c)}},
   where(a,o,v){return mkq(p,(f||[]).concat([[a,o,v]]))},orderBy(){return mkq(p,f)},limit(){return mkq(p,f)},
   onSnapshot(cb,eb){const s=async()=>{try{const q=await mkq(p,f).get();cb(q)}catch(e){eb&&eb(e)}};subs.add(s);s();return()=>subs.delete(s)},
   add:async d=>{const id='a'+Math.random().toString(36).slice(2,10);await rpc({op:'set',k:p+'/'+id,v:d,me});return db.doc(p+'/'+id)}});
 const db={
  doc:k=>({id:k.split('/').pop(),path:k,
    get:async()=>{const r=await rpc({op:'get',k});return mkdoc(k,r)},
    set:async(v,o)=>{await rpc({op:o&&o.merge?'update':'set',k,v,me})},
    update:async v=>{await rpc({op:'update',k,v,me})},
    delete:async()=>{await rpc({op:'del',k,me})},
    onSnapshot(cb,eb){const s=async()=>{try{cb(mkdoc(k,await rpc({op:'get',k})))}catch(e){eb&&eb(e)}};subs.add(s);s();return()=>subs.delete(s)}}),
  collection:p=>Object.assign(mkq(p,[]),{doc:k=>db.doc(p+'/'+k)})};
 window.__notify=()=>subs.forEach(s=>s());
 window.claude={use:async n=>n==='db'?db:n==='user'?{id:async()=>me,me:async()=>({id:me}),isOwner:()=>false,canEdit:()=>true,can:()=>true,profiles:async()=>({})}:null};
})();
"""

class World:
    def __init__(self, path=None):
        self.docs = {}; self.pages = {}; self.errors = []; self.path = path or ('file://' + __import__('os').path.abspath(__import__('os').path.join(__import__('os').path.dirname(__file__), '..', 'public', 'index.html')))
        self.pw = sync_playwright().start(); self.b = self.pw.chromium.launch()
        self.ctx = self.b.new_context(viewport={'width': 900, 'height': 900})
        self.ctx.expose_function('__rpc', self._rpc)
    def _match(self, v, flt):
        for a, o, x in flt or []:
            if o == '==' and v.get(a) != x: return False
        return True
    def _rpc(self, s):
        o = json.loads(s); op = o['op']; D = self.docs; changed = False
        if op == 'get': r = copy.deepcopy(D.get(o['k']))
        elif op == 'list':
            pre = o['p'] + '/'
            r = [{'k': k, 'v': copy.deepcopy(v)} for k, v in sorted(D.items())
                 if k.startswith(pre) and '/' not in k[len(pre):] and self._match(v, o.get('f'))]
        elif op == 'set': D[o['k']] = copy.deepcopy(o['v']); r = True; changed = True
        elif op == 'update': D.setdefault(o['k'], {}).update(copy.deepcopy(o['v'])); r = True; changed = True
        elif op == 'del': D.pop(o['k'], None); r = True; changed = True
        if changed: self._notify_later = True
        return json.dumps(r)
    def pump(self, ms=300):
        for p in self.pages.values():
            try: p.evaluate('window.__notify&&window.__notify()')
            except Exception: pass
        list(self.pages.values())[0].wait_for_timeout(ms)
    def user(self, uid):
        p = self.ctx.new_page(); self.pages[uid] = p
        p.on('pageerror', lambda e: self.errors.append(f'{uid} PAGEERR {e}'))
        p.on('console', lambda m: self.errors.append(f'{uid} {m.text}') if m.type == 'error' and 'TUNNEL' not in m.text else None)
        p.add_init_script(MOCK)
        p.goto(self.path + f'?u={uid}'); p.wait_for_timeout(500)
        return p
    def frame(self, uid):
        el = self.pages[uid].query_selector('iframe:not([hidden])')
        return el.content_frame() if el else None
    def games(self):
        return {k.split('/')[1]: v for k, v in self.docs.items() if k.startswith('games/') and k.count('/') == 1}
    def close(self): self.b.close(); self.pw.stop()

def host_game(w, uid, typ, name, pw='pw123', host='Host', city=None):
    p = w.pages[uid]
    p.click('#go-start'); p.wait_for_timeout(150)
    p.click(f'button[data-t="{typ}"]'); p.wait_for_selector('#cf')
    p.fill('#cn', host); p.fill('#cg', name); p.fill('#cp', pw)
    if city and p.query_selector('#cc'): p.select_option('#cc', city)
    p.click('#cs'); p.wait_for_timeout(1200); w.pump(300)
    return [k for k, v in w.games().items() if v['name'] == name][0]

def join_from_list(w, uid, gid, pw=None, expect_prompt=None):
    p = w.pages[uid]
    p.click('#go-ongoing') if not p.is_hidden('#go-ongoing') else None
    p.wait_for_timeout(200)
    p.click(f'button[data-e="{gid}"]'); p.wait_for_timeout(500)
    prompted = p.query_selector('#pf') is not None
    if prompted and pw is not None:
        p.fill('#pw', pw); p.click('#pf button[type=submit]'); p.wait_for_timeout(1200)
    else: p.wait_for_timeout(900)
    return prompted

def goto_home(w, uid):
    p = w.pages[uid]
    for _ in range(3):
        if not p.is_hidden('#v-home'): break
        p.click('#back'); p.wait_for_timeout(150)

class Check:
    def __init__(self): self.n = 0; self.fail = []
    def __call__(self, name, cond, info=''):
        self.n += 1; print(('PASS ' if cond else 'FAIL ') + name + (f'  [{info}]' if (info and not cond) else ''))
        if not cond: self.fail.append(name)

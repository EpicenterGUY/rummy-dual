from pathlib import Path

p=Path('index.html')
s=p.read_text()
old="function expireOwnerFixedStatuses(w){const now=sideObj(w).turnStarts;for(const m of meldsOf(w)){const mb=officialStatusBag('meld',m);if(mb?.fixedOwner===w&&mb.fixedThroughStart!=null&&now>=mb.fixedThroughStart)clearOfficialStatus('meld',m,'fixed');for(const c of m.cards){const cb=officialStatusBag('card',c);if(cb?.fixedOwner===w&&cb.fixedThroughStart!=null&&now>=cb.fixedThroughStart)clearOfficialStatus('card',c,'fixed')}}for(const c of [...sideObj(w).hand,...sideObj(w).deck,...sideObj(w).spent]){const cb=officialStatusBag('card',c);if(cb?.fixedOwner===w&&cb.fixedThroughStart!=null&&now>=cb.fixedThroughStart)clearOfficialStatus('card',c,'fixed')}}"
new="function expireOwnerFixedStatuses(w){const now=sideObj(w).turnStarts;for(const side of ['player','enemy'])for(const m of meldsOf(side)){const mb=officialStatusBag('meld',m);if(side===w&&mb?.fixedOwner===w&&mb.fixedThroughStart!=null&&now>=mb.fixedThroughStart)clearOfficialStatus('meld',m,'fixed');for(const c of m.cards){const cb=officialStatusBag('card',c);if(cb?.fixedOwner===w&&cb.fixedThroughStart!=null&&now>=cb.fixedThroughStart)clearOfficialStatus('card',c,'fixed')}}for(const c of [...sideObj(w).hand,...sideObj(w).deck,...sideObj(w).spent]){const cb=officialStatusBag('card',c);if(cb?.fixedOwner===w&&cb.fixedThroughStart!=null&&now>=cb.fixedThroughStart)clearOfficialStatus('card',c,'fixed')}}"
if s.count(old)!=1: raise SystemExit(f'expiry match: {s.count(old)}')
p.write_text(s.replace(old,new,1))

p=Path('tests/status-engine.mjs')
s=p.read_text()
anchor="ok(!ctx.meldFixedActive(meld),'fixed expires at target owner next turn end');\n"
extra="""ok(!ctx.meldFixedActive(meld),'fixed expires at target owner next turn end');
const foreignCard={officialStatus:{seal:0,fixed:1,protect:0,fixedOwner:'player',fixedThroughStart:3},status:{marked:1}};
ctx.state.enemy.melds=[{cards:[foreignCard],status:ctx.blankMeldStatus()}];
ctx.expireOwnerFixedStatuses('player');
ok(!ctx.cardFixedActive(foreignCard),'card fixed expires even while that controlled card sits in opponent public meld');
"""
if s.count(anchor)!=1: raise SystemExit(f'test anchor: {s.count(anchor)}')
p.write_text(s.replace(anchor,extra,1))

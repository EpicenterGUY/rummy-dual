from pathlib import Path
p=Path('tests/rummy-grace-joker.mjs')
s=p.read_text()
old="  ctx.log = () => {};\n  const returner = { uid: 'H2', named: true, tag: 'afterRummyDraw', suppressEffectToken: null, name: '귀환자' };"
new="  ctx.log = () => {};\n  ctx.consumeOfficialStatus = () => 0;\n  const returner = { uid: 'H2', named: true, tag: 'afterRummyDraw', suppressEffectToken: null, name: '귀환자' };"
if s.count(old)!=1: raise SystemExit(f'returner seal stub: expected 1, got {s.count(old)}')
p.write_text(s.replace(old,new,1))

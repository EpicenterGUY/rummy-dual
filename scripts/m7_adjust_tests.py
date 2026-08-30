from pathlib import Path

# Keep RUMMY's existing public applyStatus wrapper so isolated RUMMY tests and cards stay behavior-compatible.
p=Path('index.html')
s=p.read_text()
old="if(lastCards.some(c=>c.tag==='rummyHeal4')){heal(w,Math.ceil(15/RECOVERY_UNIT));runEffectAction('applyStatus',{actor:w},{scope:'player',target:s,key:'regen',amount:1});if(state.switchPower>=60)addShield(w,4)}"
new="if(lastCards.some(c=>c.tag==='rummyHeal4')){heal(w,Math.ceil(15/RECOVERY_UNIT));applyStatus(w,'regen',1);if(state.switchPower>=60)addShield(w,4)}"
if s.count(old)!=1: raise SystemExit(f'rummy apply wrapper: expected 1, got {s.count(old)}')
s=s.replace(old,new,1)
p.write_text(s)

# Existing unit tests intentionally execute individual functions in VM sandboxes.
# Explicitly stub/install the new status dependencies in those isolated contexts.
p=Path('tests/core-behavior.mjs'); s=p.read_text()
old="  ctx.triggerRummy = () => {};\n  install(ctx, 'submitNewMeld');"
new="  ctx.triggerRummy = () => {};\n  ctx.blankMeldStatus = () => ({ seal: 0, fixed: 0, protect: 0, fixedOwner: null, fixedThroughStart: null });\n  install(ctx, 'submitNewMeld');"
if s.count(old)!=1: raise SystemExit(f'core new meld stub: expected 1, got {s.count(old)}')
s=s.replace(old,new,1)
old="  ctx.checkGameOver = () => {};\n  install(ctx, 'resetAllChains', 'resetBombCycle', 'coreBreak', 'damage', 'detonate');"
new="  ctx.checkGameOver = () => {};\n  ctx.officialStatusValue = (scope, target, key) => target?.status?.[key] || 0;\n  ctx.clearOfficialStatus = (scope, target, key) => { const n = target?.status?.[key] || 0; if (target?.status) target.status[key] = 0; return n; };\n  install(ctx, 'resetAllChains', 'resetBombCycle', 'coreBreak', 'damage', 'detonate');"
if s.count(old)!=1: raise SystemExit(f'core detonate status stub: expected 1, got {s.count(old)}')
s=s.replace(old,new,1)
p.write_text(s)

p=Path('tests/rummy-grace-joker.mjs'); s=p.read_text()
old="  ctx.switchName = () => 'YOU'; ctx.log = () => {}; ctx.combatBanner = () => {};\n  ctx.detonate = () => { detonations++; state.switchPower = 0; state.switchTarget = 'neutral'; return 48; };"
new="  ctx.switchName = () => 'YOU'; ctx.log = () => {}; ctx.combatBanner = () => {};\n  ctx.expireOwnerFixedStatuses = () => {};\n  ctx.detonate = () => { detonations++; state.switchPower = 0; state.switchTarget = 'neutral'; return 48; };"
if s.count(old)!=1: raise SystemExit(f'rummy turnEnd stub: expected 1, got {s.count(old)}')
s=s.replace(old,new,1)
old="  ctx.log = () => {};\n  const encore = { uid: 'HJ', named: true, tag: 'afterRummyBonus', suppressEffectToken: null, name: '앙코르' };"
new="  ctx.log = () => {};\n  ctx.consumeOfficialStatus = () => 0;\n  const encore = { uid: 'HJ', named: true, tag: 'afterRummyBonus', suppressEffectToken: null, name: '앙코르' };"
if s.count(old)!=1: raise SystemExit(f'encore seal stub: expected 1, got {s.count(old)}')
s=s.replace(old,new,1)
old="  ctx.cardText = c => c.uid;\n  install(ctx, 'freeRecoverFromMeld');"
new="  ctx.cardText = c => c.uid;\n  ctx.meldFixedActive = () => false; ctx.cardFixedActive = () => false;\n  install(ctx, 'freeRecoverFromMeld');"
if s.count(old)!=1: raise SystemExit(f'recovery fixed stub: expected 1, got {s.count(old)}')
s=s.replace(old,new,1)
p.write_text(s)

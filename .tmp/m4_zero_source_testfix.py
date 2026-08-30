from pathlib import Path

# hand-circulation isolated maintenance helper dependency
p=Path('tests/hand-circulation.mjs')
s=p.read_text()
old="install(ctx, 'combinations', 'bestNewMeld', 'bestNewMeldForTurn', 'recoveredCardCanReturn', 'recoveredCardsCanReturn', 'anyAttachOption', 'canFinishRun', 'hasAnyLegalAction', 'maintenanceLimit');"
new="install(ctx, 'combinations', 'bestNewMeld', 'bestNewMeldForTurn', 'recoveredCardCanReturn', 'recoveredCardsCanReturn', 'anyAttachOption', 'canFinishRun', 'hasAnyLegalAction', 'ownedRecycleCount', 'maintenanceLimit');"
if s.count(old)!=1:
    raise SystemExit(f'hand-circulation install contract: expected 1 match, got {s.count(old)}')
s=s.replace(old,new,1)
old_state="const state = { player, enemy, turnNo: 9, turnToken: 21, switchTarget: 'neutral', gameOver: false, turn: 'player', phase: 'action' };"
new_state="const state = { player, enemy, discard: [], turnNo: 9, turnToken: 21, switchTarget: 'neutral', gameOver: false, turn: 'player', phase: 'action' };"
if s.count(old_state)!=1:
    raise SystemExit(f'hand-circulation state contract: expected 1 match, got {s.count(old_state)}')
s=s.replace(old_state,new_state,1)
p.write_text(s)

# rummy-grace-joker isolates triggerRummy; default to a normal non-empty circulation source
p=Path('tests/rummy-grace-joker.mjs')
s=p.read_text()
old_ctx="function context(extra = {}) {\n  return vm.createContext({ console, Math, Set, Map, Array, Object, Number, String, Boolean, ...extra });\n}"
new_ctx="function context(extra = {}) {\n  const ctx = vm.createContext({ console, Math, Set, Map, Array, Object, Number, String, Boolean, ...extra });\n  ctx.ownedRecycleCount = () => 1;\n  ctx.emergencyReleaseMeld = () => false;\n  return ctx;\n}"
if s.count(old_ctx)!=1:
    raise SystemExit(f'rummy context contract: expected 1 match, got {s.count(old_ctx)}')
s=s.replace(old_ctx,new_ctx,1)
p.write_text(s)

from pathlib import Path
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

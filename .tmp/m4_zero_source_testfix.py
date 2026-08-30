from pathlib import Path
p=Path('tests/hand-circulation.mjs')
s=p.read_text()
old="install(ctx, 'combinations', 'bestNewMeld', 'bestNewMeldForTurn', 'recoveredCardCanReturn', 'recoveredCardsCanReturn', 'anyAttachOption', 'canFinishRun', 'hasAnyLegalAction', 'maintenanceLimit');"
new="install(ctx, 'combinations', 'bestNewMeld', 'bestNewMeldForTurn', 'recoveredCardCanReturn', 'recoveredCardsCanReturn', 'anyAttachOption', 'canFinishRun', 'hasAnyLegalAction', 'ownedRecycleCount', 'maintenanceLimit');"
if s.count(old)!=1:
    raise SystemExit(f'hand-circulation install contract: expected 1 match, got {s.count(old)}')
p.write_text(s.replace(old,new,1))

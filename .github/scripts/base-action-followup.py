from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
index=ROOT/'index.html'
h=index.read_text(encoding='utf-8')
old="function hasAnyLegalAction(w){const s=sideObj(w);if(s.melds.length<3&&bestNewMeldForTurn(w))return true;if(s.melds.some((m,i)=>canFinishRun(w,i)))return true;if(bestCleanupMeldAI(w))return true;return anyAttachOption(w)}"
new="function hasAnyLegalAction(w){const s=sideObj(w);if(s.melds.length<3&&bestNewMeldForTurn(w))return true;if(s.melds.some((m,i)=>canFinishRun(w,i)))return true;if(s.melds.length===3&&typeof canCleanupMeld==='function'&&s.melds.some((m,i)=>canCleanupMeld(w,i)))return true;return anyAttachOption(w)}"
if old in h:h=h.replace(old,new,1)
elif new not in h:raise SystemExit('missing hasAnyLegalAction cleanup anchor')
index.write_text(h,encoding='utf-8')

p=ROOT/'tests'/'hand-circulation.mjs'
s=p.read_text(encoding='utf-8')
fixes=[
("    newMeldCount:0, returnedSwitchThisTurn: false, maintenanceUsed: false,","    newMeldCount:0, attachCount:0, extraAttachRemaining:0, meldCleanupUsed:false, returnedSwitchThisTurn: false, maintenanceUsed: false,"),
("  install(ctx, 'combinations', 'bestNewMeld', 'bestNewMeldForTurn', 'recoveredCardCanReturn', 'recoveredCardsCanReturn', 'anyAttachOption', 'canFinishRun', 'hasAnyLegalAction', 'ownedRecycleCount', 'maintenanceLimit');","  install(ctx, 'combinations', 'bestNewMeld', 'bestNewMeldForTurn', 'recoveredCardCanReturn', 'recoveredCardsCanReturn', 'attachAccess', 'anyAttachOption', 'canFinishRun', 'canCleanupMeld', 'hasAnyLegalAction', 'ownedRecycleCount', 'maintenanceLimit');"),
("// A full three-meld board blocks a new meld, so a hand with no attach is genuinely stuck.","// A full three-meld board now exposes the conditional cleanup base action, so it is not a stuck state."),
("  ok(!ctx.hasAnyLegalAction('player'), 'new meld in hand does not count when public board is already 3/3 and no attach exists');\n  ok(ctx.maintenanceLimit('player') === 2, 'full-board dead hand receives two-card stuck maintenance');","  ok(ctx.hasAnyLegalAction('player'), 'full 3/3 board still has the conditional cleanup base action');\n  ok(ctx.maintenanceLimit('player') === 1, 'legal full-board cleanup keeps maintenance at the normal one-card limit');")
]
for old,new in fixes:
    if old in s:s=s.replace(old,new,1)
    elif new not in s:raise SystemExit(f'missing hand-circulation migration anchor: {old[:80]}')
p.write_text(s,encoding='utf-8')
print('full-board cleanup legality follow-up applied')

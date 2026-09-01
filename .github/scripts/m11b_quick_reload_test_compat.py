from pathlib import Path

paths=['tests/point-blank-quick-reload.mjs','.github/scripts/point_blank_quick_reload_regression.mjs']
old="""const playerMeld=source('playerMeld'),buttons=source('updateButtons'),ai=source('continueAITurnAfterAcquisition'),bestFinish=source('bestFinishRunAI'),legal=source('hasAnyLegalAction');
ok(playerMeld.includes(\"newMeldAccess('player',cs)\")&&playerMeld.includes('퀵 리로드가 있다면'),'player new-meld action recognizes only the explicit Quick Reload exception');"""
new="""const playerMeld=source('playerMeld'),executePlayerMeld=script.includes('function executePlayerMeld(')?source('executePlayerMeld'):'',buttons=source('updateButtons'),ai=source('continueAITurnAfterAcquisition'),bestFinish=source('bestFinishRunAI'),legal=source('hasAnyLegalAction');
const playerMeldContract=executePlayerMeld||playerMeld;
ok(playerMeldContract.includes(\"newMeldAccess('player',cs)\")&&playerMeldContract.includes('퀵 리로드가 있다면')&&(!executePlayerMeld||playerMeld.includes('executePlayerMeld(cs')),'player new-meld action recognizes only the explicit Quick Reload exception across the rank-choice UI delegation');"""
for path in paths:
    p=Path(path)
    s=p.read_text()
    if old in s:
        s=s.replace(old,new,1)
        p.write_text(s)
    elif new not in s:
        raise SystemExit(f'Quick Reload player-meld regression anchor missing: {path}')
print('Quick Reload regression aligned with split player meld UI while preserving newMeldAccess contract')

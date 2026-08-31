from pathlib import Path
p=Path('tests/deadlock-circulation.mjs')
s=p.read_text(encoding='utf-8')
old="ok(functionSource('aiTurn').includes(\"prepareAcquisitionPhase('enemy')\")&&functionSource('aiTurn').includes(\"prepareAcquisitionPhase('player')\"),'AI and following player turn both run acquisition safety');"
new="ok(functionSource('aiTurn').includes(\"prepareAcquisitionPhase('enemy')\")&&functionSource('continueAITurnAfterAcquisition').includes(\"prepareAcquisitionPhase('player')\"),'AI and following player turn both run acquisition safety across the resumable turn split');"
if old not in s: raise SystemExit('missing deadlock AI acquisition assertion')
p.write_text(s.replace(old,new,1),encoding='utf-8')

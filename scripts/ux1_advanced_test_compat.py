from pathlib import Path
p=Path('tests/practice-battle.mjs')
s=p.read_text(encoding='utf-8')
old="ok(html.includes('id=\"tutorialPracticeBtn\"')&&script.includes(\"practice.hidden=!(state.tutorialSegmentDone&&step.id==='rummy')\"),'completed tutorial can continue directly into free practice');"
new="ok(html.includes('id=\"tutorialPracticeBtn\"')&&script.includes(\"practice.hidden=!(state.tutorialSegmentDone&&segmentEnd)\"),'completed basic or advanced tutorial segment can continue directly into free practice');"
if old not in s: raise SystemExit('missing practice continuation assertion')
p.write_text(s.replace(old,new,1),encoding='utf-8')
print('updated practice continuation regression')

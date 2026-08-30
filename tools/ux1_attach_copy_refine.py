from pathlib import Path
p=Path('index.html')
s=p.read_text()
old="hint.textContent=state.tutorialSegmentDone?'기본 조작·세트·런 1차 실습을 완료했습니다. 다음 묶음에서는 붙이기와 상대 공개 조합 이용을 이어서 배웁니다.':step.hint||'';"
new="hint.textContent=state.tutorialSegmentDone?'여기까지 완료했습니다. 다음 실습은 러미입니다.':step.hint||'';"
if old not in s: raise SystemExit('missing stale tutorial completion copy')
p.write_text(s.replace(old,new,1))

t=Path('tests/tutorial-attach-switch.mjs')
x=t.read_text()
needle="ok(roadmap.includes('- [x] 붙이기 튜토리얼') && roadmap.includes('- [x] 상대 공개 조합 붙이기 체험') && roadmap.includes('- [x] 스위치 튜토리얼'), 'UX1 roadmap records attach/opponent/SWITCH lessons complete');\n"
extra=needle+"ok(script.includes('여기까지 완료했습니다. 다음 실습은 러미입니다.') && !script.includes('다음 묶음에서는 붙이기와 상대 공개 조합 이용'), 'completion coach points to RUMMY instead of stale attach work');\n"
if needle not in x: raise SystemExit('missing attach tutorial roadmap assertion')
t.write_text(x.replace(needle,extra,1))

from pathlib import Path
p=Path('tools/ux1_practice_patch.py')
s=p.read_text()
old="one('기본 조작부터 러미까지 고정 패로 직접 익힙니다.', '기본 조작부터 폭발·러미까지 고정 패로 직접 익힙니다.', 'static tutorial copy')"
new="one('<button id=\"tutorialStartBtn\" class=\"pixelBtn startMenuBtn\" type=\"button\"><span>튜토리얼<small>기본 조작부터 러미까지 고정 패로 직접 익힙니다.</small></span><span class=\"menuState\">시작</span></button>', '<button id=\"tutorialStartBtn\" class=\"pixelBtn startMenuBtn\" type=\"button\"><span>튜토리얼<small>기본 조작부터 폭발·러미까지 고정 패로 직접 익힙니다.</small></span><span class=\"menuState\">시작</span></button>', 'static tutorial copy')"
if old not in s: raise SystemExit('old broad static copy matcher missing')
p.write_text(s.replace(old,new))

t=Path('tests/start-screen.mjs')
ts=t.read_text()
repls={
"기본 조작부터 러미까지 고정 패로 직접 익힙니다.":"기본 조작부터 폭발·러미까지 고정 패로 직접 익힙니다.",
"state.sessionMode==='battle'&&state.battleId===battleId":"isLiveCombatSession()&&state.battleId===battleId",
"state.sessionMode='battle'":"newGame('battle')",
}
for a,b in repls.items():
    if a not in ts: raise SystemExit(f'start-screen expectation missing: {a}')
    ts=ts.replace(a,b)
t.write_text(ts)

f=Path('tests/tutorial-framework.mjs')
fs=f.read_text()
old_mode="ok(script.includes(\"state.sessionMode='tutorial'\"), 'tutorial has its own session mode');"
new_mode="ok(script.includes(\"newGame('tutorial')\"), 'tutorial enters through the explicit tutorial session mode');"
if old_mode not in fs: raise SystemExit('tutorial mode expectation missing')
f.write_text(fs.replace(old_mode,new_mode))

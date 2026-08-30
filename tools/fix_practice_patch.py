from pathlib import Path
p=Path('tools/ux1_practice_patch.py')
s=p.read_text()
old="one('기본 조작부터 러미까지 고정 패로 직접 익힙니다.', '기본 조작부터 폭발·러미까지 고정 패로 직접 익힙니다.', 'static tutorial copy')"
new="one('<button id=\"tutorialStartBtn\" class=\"pixelBtn startMenuBtn\" type=\"button\"><span>튜토리얼<small>기본 조작부터 러미까지 고정 패로 직접 익힙니다.</small></span><span class=\"menuState\">시작</span></button>', '<button id=\"tutorialStartBtn\" class=\"pixelBtn startMenuBtn\" type=\"button\"><span>튜토리얼<small>기본 조작부터 폭발·러미까지 고정 패로 직접 익힙니다.</small></span><span class=\"menuState\">시작</span></button>', 'static tutorial copy')"
if old not in s: raise SystemExit('old broad static copy matcher missing')
p.write_text(s.replace(old,new))

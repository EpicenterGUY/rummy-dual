from pathlib import Path

index = Path('index.html')
text = index.read_text(encoding='utf-8')
replacements = [
    ('<b>RUN MAP</b>', '<b>런 지도</b>'),
    ("const status=draft.status==='completed'?'RUN COMPLETE':progress.pending?.source==='battle'?'REWARD WAIT':progress.awaitingRegion?'ROUTE CHOICE':'IN PROGRESS';", "const status=draft.status==='completed'?'런 완료':progress.pending?.source==='battle'?'보상 대기':progress.awaitingRegion?'지역 선택':'진행 중';"),
    ('<b>RUN MAP · ${status}</b>', '<b>런 지도 · ${status}</b>'),
]
for old, new in replacements:
    if old not in text:
        raise SystemExit(f'missing route map localization target: {old}')
    text = text.replace(old, new, 1)
index.write_text(text, encoding='utf-8')

test = Path('tests/m11a-route-map.mjs')
t = test.read_text(encoding='utf-8')
old = "renderSrc.includes(\"'승리 · 보상 대기'\")&&renderSrc.includes(\"'다음 전투'\")&&renderSrc.includes('RUN COMPLETE')"
new = "renderSrc.includes(\"'승리 · 보상 대기'\")&&renderSrc.includes(\"'다음 전투'\")&&renderSrc.includes('런 완료')"
if old not in t:
    raise SystemExit('missing route map localized test target')
t = t.replace(old, new, 1)
test.write_text(t, encoding='utf-8')

doc = Path('docs/ROGUELIKE_MASTER_PLAN.md')
d = doc.read_text(encoding='utf-8').replace('헤더를 `RUN COMPLETE`로 전환한다.', '헤더를 `런 완료`로 전환한다.', 1)
doc.write_text(d, encoding='utf-8')

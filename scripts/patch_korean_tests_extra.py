from pathlib import Path

p=Path('tests/core-behavior.mjs')
s=p.read_text(encoding='utf-8')
old="ok(capture.retired[0]?.reason.includes('BURST'), '4SET retirement is explicitly caused by BURST resolution');"
new="ok(capture.retired[0]?.reason.includes('버스트'), '4SET retirement is explicitly caused by BURST resolution');"
if old not in s:
    raise SystemExit('missing core-behavior BURST reason assertion')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')

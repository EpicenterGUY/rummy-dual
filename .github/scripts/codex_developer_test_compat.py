from pathlib import Path
p=Path('tests/vsignal-encore.mjs')
s=p.read_text(encoding='utf-8')
old="ok(script.includes('n.themeId?` · 테마 ${themeDef(n.themeId)?.displayName||n.themeId}`'),'codex visibly labels themed named variants');"
new="ok(script.includes('n.themeId?` · 카드군 ${themeDef(n.themeId)?.displayName||n.themeId}`'),'codex visibly labels themed named variants with the card-group term');"
if old not in s:
    raise SystemExit('missing legacy V-SIGNAL codex terminology assertion')
p.write_text(s.replace(old,new,1),encoding='utf-8')

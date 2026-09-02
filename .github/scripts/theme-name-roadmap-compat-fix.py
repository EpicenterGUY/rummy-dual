from pathlib import Path

p = Path('ROADMAP.md')
text = p.read_text(encoding='utf-8')
changed = text.replace('MAIL-ROUTE', 'MAIL//ROUTE').replace('SCRAP-SHIFT', 'SCRAP//SHIFT')
if changed == text:
    raise SystemExit('canonical theme-name roadmap targets not found')
p.write_text(changed, encoding='utf-8')

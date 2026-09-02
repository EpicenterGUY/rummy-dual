from pathlib import Path
src=Path('.github/scripts/theme-60-integration-patch.py').read_text(encoding='utf-8')
old="anchor='## M9 — Jokers + Fields'"
new="anchor='## M9'"
if old not in src:
    raise SystemExit('missing v1 roadmap anchor')
src=src.replace(old,new,1)
exec(compile(src,'theme-60-integration-patch-v2','exec'))

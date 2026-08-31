from pathlib import Path
p=Path('.github/scripts/codex_developer_mode_patch.py')
s=p.read_text(encoding='utf-8')
old="replace_between(start,end,new_codex,end,'renderCodex')"
new="replace_between(start,end,new_codex,'renderCodex')"
if old not in s:
    raise SystemExit('missing renderCodex replace_between typo')
p.write_text(s.replace(old,new,1),encoding='utf-8')

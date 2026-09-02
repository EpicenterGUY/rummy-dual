from pathlib import Path
import runpy

runpy.run_path('.github/scripts/point-blank-full-pool-patch-v2.py', run_name='__main__')

p=Path('tests/zero-sight-full-pool.mjs')
text=p.read_text(encoding='utf-8')
old="ok(plan.includes('| ZERO-SIGHT | 18 | 18 | 0 | 18/18 |')&&plan.includes('| **합계** | **60** | **44** | **16** |'),'full-pool plan advances to 44/60 live cards');"
new="ok(plan.includes('| ZERO-SIGHT | 18 | 18 | 0 | 18/18 |')&&plan.includes('- ZERO-SIGHT: **18/18 풀 구현 완료**'),'full-pool plan keeps ZERO-SIGHT at 18/18 after later theme integration');"
if old in text:
    text=text.replace(old,new,1)
elif new not in text:
    raise SystemExit('missing ZERO-SIGHT full-pool plan assertion')
p.write_text(text,encoding='utf-8')

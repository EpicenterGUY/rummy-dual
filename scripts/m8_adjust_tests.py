from pathlib import Path

p=Path('tests/core-behavior.mjs')
s=p.read_text()
old="""  ctx.freeRecoverFromMeld = () => null;
  ctx.cutOppositeEnd = () => false;
  ctx.replaceRedundantJokers = () => {};
"""
new="""  ctx.freeRecoverFromMeld = () => null;
  ctx.cutOppositeEnd = () => false;
  ctx.recoverRedundantGapRun = () => null;
  ctx.middleManagerReturnPlaceholder = () => null;
  ctx.replaceRedundantJokers = () => {};
"""
if s.count(old)!=1:
    raise SystemExit(f'core attach helper stubs: expected 1 match, got {s.count(old)}')
p.write_text(s.replace(old,new,1))

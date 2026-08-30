from pathlib import Path
p=Path('tests/named-card-audit.mjs')
s=p.read_text()
old="ok(script.includes('recoverRedundantGapRun(targetSide,m,beforeCards,cards);middleManagerReturnPlaceholder(targetSide,m,cards);replaceRedundantJokers'),'attach resolution runs placeholder cleanup in one deterministic phase');"
new="""const gapCleanup=script.indexOf('recoverRedundantGapRun(targetSide,m,beforeCards,cards);');
const middleCleanup=script.indexOf('middleManagerReturnPlaceholder(targetSide,m,cards);',gapCleanup);
const jokerCleanup=script.indexOf('replaceRedundantJokers(targetSide,m,w);',middleCleanup);
ok(gapCleanup>=0&&middleCleanup>gapCleanup&&jokerCleanup>middleCleanup,'attach resolution runs placeholder cleanup in one deterministic phase');"""
assert s.count(old)==1, s.count(old)
p.write_text(s.replace(old,new))

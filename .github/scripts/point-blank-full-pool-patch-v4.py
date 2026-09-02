from pathlib import Path
import runpy

runpy.run_path('.github/scripts/point-blank-full-pool-patch-v3.py', run_name='__main__')

index=Path('index.html')
text=index.read_text(encoding='utf-8')
# PBH7 / PBDJ were already live before the full-pool expansion. Adding new
# tendency metadata to them changes roguelike action-tag scoring even though
# the new 16 cards are staged. Preserve their legacy reward semantics; only
# newly introduced POINT-BLANK cards receive expansion tendencies here.
for frag in [",pbCoverSwap:['interact','sustain','control']", ",pbQuickReload:['recover','combo','sustain']"]:
    if frag in text:
        text=text.replace(frag,'',1)
index.write_text(text,encoding='utf-8')

# Lock the compatibility behavior in the dedicated full-pool regression.
test=Path('tests/point-blank-full-pool.mjs')
t=test.read_text(encoding='utf-8')
needle="ok(script.includes(\"'PBH7':{slot:'H7',themeId:'point-blank',n:'엄폐 교대',t:'pbCoverSwap'\")&&script.includes(\"'PBDJ':{slot:'DJ',themeId:'point-blank',n:'퀵 리로드',t:'pbQuickReload'\"),'existing Cover Swap and Quick Reload live definitions remain unchanged');"
extra=needle+"\nok(!script.includes(\"pbCoverSwap:['interact','sustain','control']\")&&!script.includes(\"pbQuickReload:['recover','combo','sustain']\"),'full-pool expansion preserves legacy PBH7/PBDJ roguelike scoring metadata');"
if needle in t and 'preserves legacy PBH7/PBDJ roguelike scoring metadata' not in t:
    t=t.replace(needle,extra,1)
test.write_text(t,encoding='utf-8')

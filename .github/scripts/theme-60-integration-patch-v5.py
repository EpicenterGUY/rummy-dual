from pathlib import Path
src=Path('.github/scripts/theme-60-integration-patch-v4.py').read_text(encoding='utf-8')
exec(compile(src,'theme-60-integration-patch-v5-base','exec'))
p=Path('tests/ux2-menu-isolation.mjs')
s=p.read_text(encoding='utf-8')
old="""// Test the actual renderers against both pools, without adding development cards to normal views.
g.renderProgress();g.renderCodex();
assert.doesNotMatch(g.document.getElementById('themeGroupGrid').innerHTML,/point-blank/);
assert.doesNotMatch(g.document.getElementById('codexGrid').innerHTML,/codexDebug|DEV 공개/);
g.setDeveloperMode(true);g.renderProgress();g.renderCodex();
assert.match(g.document.getElementById('themeGroupGrid').innerHTML,/개발 중 · DEV 선택 가능/);
assert.match(g.document.getElementById('codexGrid').innerHTML,/codexDebug/);
"""
new="""// Test the actual renderers against both pools. Completed live themes belong in ordinary views; DEV-only card data still must not leak.
g.renderProgress();g.renderCodex();
const normalThemeGrid=g.document.getElementById('themeGroupGrid').innerHTML;
assert.match(normalThemeGrid,/v-signal/);assert.match(normalThemeGrid,/zero-sight/);assert.match(normalThemeGrid,/point-blank/,'completed POINT-BLANK is now ordinary live content');
assert.doesNotMatch(normalThemeGrid,/개발 중 · DEV 선택 가능/);
assert.doesNotMatch(g.document.getElementById('codexGrid').innerHTML,/codexDebug|DEV 공개/);
g.setDeveloperMode(true);g.renderProgress();g.renderCodex();
assert.match(g.document.getElementById('themeGroupGrid').innerHTML,/point-blank/,'DEV keeps the same completed live theme visible');
assert.match(g.document.getElementById('codexGrid').innerHTML,/codexDebug/);
"""
if new not in s:
    if old not in s: raise SystemExit('missing legacy UX2 development-theme isolation block')
    s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')
print('theme 60-card integration v5 UX isolation contract updated')

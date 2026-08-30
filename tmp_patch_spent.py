from pathlib import Path

p = Path('index.html')
s = p.read_text()

old = '''<div class="pileStation"><div class="spentPile" aria-label="내 소모패"><span class="spentMark">소모패<br><b id="playerSpentCount">0</b></span></div><div class="pileMeta"><span class="drawPath spentPath">정리 → 소모패</span><div class="pileRule">덱 0장 → 소모패 즉시 섞음</div></div></div>'''
new = '''<div class="pileStation spentStation"><div class="spentPile" aria-label="내 소모패 · 직접 조작하지 않음 · 덱이 비면 자동 재순환"><span class="spentMark">재순환 대기<br><b id="playerSpentCount">0</b><small>소모패</small></span></div><div class="pileMeta"><span class="drawPath spentPath">사용·정리 → 소모패</span><div class="pileRule"><b class="spentAutoLabel">직접 사용 불가</b> · 덱 0장 시 자동 셔플</div></div></div>'''
assert s.count(old) == 1, s.count(old)
s = s.replace(old, new)

marker = '\n/* UI2 · desktop fullscreen / Korean readability / no page scroll */'
assert s.count(marker) == 1, s.count(marker)
css = r'''

/* UI2 · spent pile clarity */
.spentMark small{display:block;margin-top:3px;font-size:7px;font-weight:700;color:#7f8c91}.spentAutoLabel{color:#d2c39d;font-weight:800}.spentStation .spentPile{cursor:default}.spentStation .pileMeta{line-height:1.35}
@media (min-width:900px){.spentStation{opacity:.86}.spentStation .spentPile{width:60px;height:86px}.spentStation .spentPile:before,.spentStation .spentPile:after{width:45px;height:66px}.spentStation .spentMark{font-size:9px}.spentStation .spentMark b{font-size:13px}.spentStation .pileMeta{max-width:150px;margin-inline:auto}}
@media (min-width:1200px){.spentStation .spentPile{width:54px;height:76px}.spentStation .spentPile:before,.spentStation .spentPile:after{width:40px;height:58px}.spentStation .spentMark{font-size:9px}.spentStation .pileMeta{font-size:9px}.spentStation .pileRule{font-size:8px}}
'''
s = s.replace(marker, css + marker)

core = ''' <div class="ruleBlock"><h3>생존 · 코어</h3><p>각 플레이어는 <b>코어 3개 × 60</b>을 가집니다. 폭발과 직접 피해는 현재 코어에 들어가며, 코어를 파괴하고 남은 <b>초과 피해는 다음 코어로 관통하지 않습니다.</b> 마지막 코어가 깨지면 패배합니다.</p></div>'''
insert = core + '''\n <div class="ruleBlock"><h3>덱 · 버림패 · 소모패</h3><p><b>공용 버림패</b>는 양쪽이 맨 위 카드를 가져올 수 있는 공용 공간입니다. <b>소모패</b>는 각자의 자동 재순환 대기 더미라서 기본적으로 직접 사용할 수 없습니다. 개인 덱의 마지막 카드를 뽑으면 그 플레이어의 소모패만 즉시 섞여 새 덱이 되며, 공용 버림패는 섞이지 않습니다.</p></div>'''
assert s.count(core) == 1, s.count(core)
s = s.replace(core, insert)
p.write_text(s)

r = Path('ROADMAP.md')
road = r.read_text()
anchor = '- [x] 선택 가능 카드·붙이기 가능 조합 강조를 발광보다 테두리/위치 변화 중심으로 통일\n'
addition = '- [x] 덱 / 공용 버림패 / 개인 소모패의 역할 위계 분리 — 소모패를 `직접 사용 불가 · 덱 0장 시 자동 셔플` 재순환 대기 영역으로 명확화하고 데스크톱에서 시각적 비중 축소\n'
assert road.count(anchor) == 1
road = road.replace(anchor, anchor + addition)
r.write_text(road)

t = Path('tests/spent-pile-ux.mjs')
t.write_text(r'''import fs from 'node:fs';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
ok(html.includes('class="pileStation spentStation"'),'spent pile has a distinct non-primary station class');
ok(html.includes('재순환 대기<br><b id="playerSpentCount">0</b><small>소모패</small>'),'spent pile identifies itself as a recycle queue while preserving the official 소모패 term');
ok(html.includes('직접 사용 불가</b> · 덱 0장 시 자동 셔플'),'spent pile permanently explains that it is not a direct action source');
ok(html.includes('aria-label="내 소모패 · 직접 조작하지 않음 · 덱이 비면 자동 재순환"'),'spent pile accessibility text explains its passive role');
ok(html.includes('/* UI2 · spent pile clarity */')&&html.includes('@media (min-width:900px){.spentStation{opacity:.86}'),'desktop visually subordinates the passive spent pile');
ok(html.includes('<h3>덱 · 버림패 · 소모패</h3>'),'rules overlay contains a dedicated pile-role explanation');
ok(html.includes('공용 버림패</b>는 양쪽이 맨 위 카드를 가져올 수 있는 공용 공간')&&html.includes('소모패</b>는 각자의 자동 재순환 대기 더미'),'rules explicitly distinguish shared discard from personal spent');
ok(html.includes('공용 버림패는 섞이지 않습니다.'),'rules state that spent recycle never absorbs shared discard');
ok(road.includes('- [x] 덱 / 공용 버림패 / 개인 소모패의 역할 위계 분리'),'roadmap records the pile hierarchy cleanup as complete');
console.log('Spent pile UX regression passed.');
''')

import fs from 'node:fs';
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

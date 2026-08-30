import fs from 'node:fs';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
ok(html.includes('class="pileStation spentStation"'),'spent pile has a distinct non-primary station class');
ok(html.includes('재순환 대기<br><b id="playerSpentCount">0</b><small>소모패</small>'),'spent pile identifies itself as a recycle queue while preserving the official 소모패 term');
ok(html.includes('직접 사용 불가</b><br>덱 0장 → 소모패 + 버림패 내 카드 자동 셔플'),'spent pile explains the complete PURE-safe recycle source');
ok(html.includes('aria-label="내 소모패 · 직접 조작하지 않음 · 덱이 비면 소모패와 공용 버림패의 내 소유 카드 자동 재순환"'),'spent pile accessibility text explains the full passive recycle rule');
ok(html.includes('/* UI2 · spent pile clarity */')&&html.includes('@media (min-width:900px){.spentStation{opacity:.86}'),'desktop visually subordinates the passive spent pile');
ok(html.includes('<h3>덱 · 버림패 · 소모패</h3>'),'rules overlay contains a dedicated pile-role explanation');
ok(html.includes('그 플레이어의 소모패 + 공용 버림패에 남아 있는 현재 그 플레이어 소유 카드')&&html.includes('상대 소유 카드와 공개 조합 카드는 그대로 남습니다.'),'rules explain owner-filtered discard recycling without touching public melds');
ok(road.includes('recycle that player’s spent pile plus cards in the shared discard currently owned by that player'),'M0 locks owner-filtered shared-discard recycling');
ok(road.includes('PURE도 기본 순환만으로 장기전이 가능하도록'),'PURE roadmap records the circulation compatibility fix');
console.log('Spent pile UX regression passed.');

import fs from 'node:fs';
const doc=fs.readFileSync(new URL('../docs/THEME_GROUPS.md',import.meta.url),'utf8');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
ok(doc.includes('# MAIL//ROUTE')&&doc.includes('후속 정식 테마 후보'),'MAIL//ROUTE is recorded as design-locked but not falsely live');
ok(doc.includes('28장, 수트별 7장'),'candidate pool is locked to 28 cards with seven per suit');
ok(doc.includes('일반/다른 테마 카드에도 붙일 수 있다'),'mail marker stays theme-agnostic for mixed decks');
ok(doc.includes('손패 ↔ 공개 조합')&&doc.includes('공개 조합 ↔ 공개 조합')&&doc.includes('공용 버림패 또는 소모패'),'mail lifecycle preserves active route zones and clears on discard/spent');
ok(doc.includes('각 플레이어는 양측 공개 조합을 통틀어 **자신의 목적지 1개**만 유지'),'destination is one public meld per player');
ok(doc.includes('새 3장 SET/RUN 생성도 손패 → 공개 조합이므로 도착'),'new meld creation counts as arrival');
ok(doc.includes('버림패에서 가져오는 것, 개인 덱에서 뽑는 것은 도착이 아니다'),'acquisition is explicitly not arrival');
ok(doc.includes('공개 조합에 있던 자신의 우편 카드를 자기 손패로 회수'),'return mail is tied to actual meld-to-hand recovery');
ok(doc.includes('반송은 우편 표식을 지우지 않는다')&&doc.includes('재배송은 추가 기본 행동이나 같은 턴 반환 예외를 자동 제공하지 않는다'),'redelivery persists mail without bypassing base action/return rules');
ok(doc.includes('동일 카드/효과의 `도착`·`지정 도착`·`반송` 유발은 각각 턴당 1회'),'arrival/target-arrival/return triggers have the once-per-turn default');
ok(doc.includes('themeTurnGates')&&!doc.includes('MAIL_POINT'),'MAIL//ROUTE reuses theme gates and creates no dedicated score resource');
ok(road.includes('- [x] MAIL//ROUTE 카드 수 / 우편 표식 수명 / 목적지 규칙 / 반송 타이밍 최종 확정'),'ROADMAP marks MAIL//ROUTE core rules complete');
console.log('MAIL//ROUTE design lock regression passed.');

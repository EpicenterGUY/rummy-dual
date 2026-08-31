import fs from 'node:fs';
const doc=fs.readFileSync(new URL('../docs/THEME_GROUPS.md',import.meta.url),'utf8');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
ok(doc.includes('# 신규 테마 발굴 원칙 — 지역에서 카드군으로'),'canonical theme doc contains the region-first origin policy');
ok(doc.includes('문화·직업 앵커 수집')&&doc.includes('최소 3개'),'new themes begin from multiple concrete cultural/occupational anchors');
ok(doc.includes('갈등 / 압력 1개 이상 정의'),'new themes require an action-producing tension rather than only aesthetics');
ok(doc.includes('동사로 변환')&&doc.includes('카드가 실제로 할 행동 4~6개'),'theme ideation converts context into gameplay verbs');
ok(doc.includes('RUMMY//DUEL 공용 행동에 매핑')&&doc.includes('최소 3개와 연결'),'theme pitch must connect to multiple shared rummy actions');
ok(doc.includes('기존 테마와 기계적 중복 검사')&&doc.includes('기존 테마 카드로 흡수'),'duplicate mechanics are absorbed before creating a redundant theme');
ok(doc.includes('전용 개념 최소화')&&doc.includes('일반/타 테마 카드도 이용할 수 있는 오픈형 개념'),'new proprietary concepts require open mixed-deck justification');
ok(doc.includes('마지막에 테마명·캐릭터·비주얼 결정'),'naming and visuals happen after the mechanical loop is justified');
ok(doc.includes('지역을 의상·음식·말투 몇 개로만 소비하지 않는다'),'policy rejects shallow regional stereotyping');
ok(doc.includes('이 조건을 못 채우면 카드 20~30장을 먼저 설계하지 않는다'),'full card-pool production is gated behind the pitch criteria');
ok(road.includes('- [x] 향후 신규 테마는 카드군부터 만들기보다 지역의 문화/직업/갈등에서 파생시키는 방식 우선 검토'),'ROADMAP marks the region-first theme policy complete');
console.log('Region-first theme origin policy regression passed.');

import fs from 'node:fs';

const doc=fs.readFileSync(new URL('../docs/TWELVE_BLOOM_DESIGN.md',import.meta.url),'utf8');
const themes=fs.readFileSync(new URL('../docs/THEME_GROUPS.md',import.meta.url),'utf8');
const plan=fs.readFileSync(new URL('../docs/THEME_FULL_POOL_PLAN.md',import.meta.url),'utf8');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}

ok(doc.includes('TWELVE-BLOOM is the renamed successor to the former HWA-TU candidate'),'TWELVE-BLOOM explicitly replaces the old HWA-TU candidate');
ok(themes.includes('CYCLE-WORKS, TWELVE-BLOOM')&&!themes.includes('CYCLE-WORKS, HWA-TU'),'canonical displayed theme-name list uses TWELVE-BLOOM');
ok(plan.includes('TWELVE-BLOOM / CYCLE-WORKS 및 이후 후보'),'full-pool plan names TWELVE-BLOOM as the next non-live candidate');
ok(!html.includes("themeId:'twelve-bloom'")&&!html.includes("'twelve-bloom':Object.freeze"),'design lock does not prematurely expose TWELVE-BLOOM as a runtime theme');

for(const row of [
 ['A','1'],['2','2'],['3','3'],['4','4'],['5','5'],['6','6'],['7','7'],['8','8'],['9','9'],['10','10'],['J','11'],['Q','12']
])ok(doc.includes(`| ${row[0]} | ${row[1]} |`),`${row[0]} maps to month ${row[1]}`);

ok(doc.includes('Each player can maintain at most one designated 윤달 card'),'leap month is limited to one owned public K per player');
ok(doc.includes('윤달 can replace at most one missing month in one 계절맞춤 check'),'leap month can replace only one missing season month');
ok(doc.includes('윤달 cannot satisfy an exact 그림맞춤'),'leap month cannot counterfeit exact picture slots');
ok(doc.includes('Jokers do not count as a month or exact picture'),'Jokers do not loosen TWELVE-BLOOM matches by default');

for(const pattern of ['| 봄맞춤 | 1 · 2 · 3 |','| 여름맞춤 | 4 · 5 · 6 |','| 가을맞춤 | 7 · 8 · 9 |','| 겨울맞춤 | 10 · 11 · 12 |'])ok(doc.includes(pattern),`season pattern locked: ${pattern}`);
for(const pattern of ['| 붉은 띠 | A♥ · 2♥ · 3♥ |','| 풀빛 띠 | 4♥ · 5♥ · 6♥ |','| 푸른 띠 | 7♥ · 8♥ · 9♥ |','| 새 셋 | 2♦ · 4♦ · 8♦ |','| 빛 셋 | A♠ · 8♠ · Q♠ |'])ok(doc.includes(pattern),`exact picture pattern locked: ${pattern}`);

ok(doc.includes("owned cards currently sitting in the opponent's public melds"),'owned cards on the opponent board are valid mixed-deck match material');
ok(doc.includes('Theme identity is never a matching requirement'),'matching never requires TWELVE-BLOOM card identity');
ok(doc.includes('hand;')&&doc.includes('personal deck;')&&doc.includes('shared discard;')&&doc.includes('personal spent;'),'non-public zones are excluded from match material');

ok(doc.includes('A continuously complete match does not repeatedly trigger'),'continuous completion cannot farm triggers');
ok(doc.includes('Breaking and rebuilding the same named match in the same turn cannot reward it twice'),'same-turn rebuild uses an anti-loop gate');
ok(doc.includes('Match completion itself adds 0 power and never moves SWITCH'),'matching itself is combat neutral');
ok(doc.includes('Match completion grants no extra basic new-meld or attach count'),'matching cannot bypass the simplified base-action budget');

const cardLines=[...doc.matchAll(/^\d+\. \*\*([^*]+)\*\* — (.+)$/gm)].map(m=>({name:m[1],effect:m[2]}));
ok(cardLines.length===24,`candidate pool has exactly 24 cards (${cardLines.length})`);
const suitCount={C:0,H:0,D:0,S:0};
for(const c of cardLines){
 const suit=c.name.includes('♣')?'C':c.name.includes('♥')?'H':c.name.includes('♦')?'D':c.name.includes('♠')?'S':null;
 if(suit)suitCount[suit]++;
}
for(const s of ['C','H','D','S'])ok(suitCount[s]===6,`candidate ${s} suit has exactly six cards`);
ok(new Set(cardLines.map(c=>c.name.split(' ')[0])).size===24,'candidate physical rank+suit slots are unique within TWELVE-BLOOM');

const direct=cardLines.filter(c=>/이번 반환 누적 위력이 \d+ 증가/.test(c.effect));
ok(direct.length===2,`candidate pool has exactly two direct return-power cards (${direct.length})`);
ok(direct.some(c=>c.name.startsWith('10♠ 낙조'))&&direct.some(c=>c.name.startsWith('Q♠ 빛 셋')),'only Sunset and Light Trio occupy the direct-power finisher lane');

ok(road.includes('- [x] `TWELVE-BLOOM` 정식 후보 정비'),'ROADMAP closes the rename/vocabulary task');
ok(road.includes('- [x] TWELVE-BLOOM 기본 판정 잠금'),'ROADMAP closes the month/leap-month rules task');
ok(road.includes('- [x] 계절맞춤 / 그림맞춤 구조 잠금'),'ROADMAP closes the matching-pattern task');
ok(road.includes('- [x] TWELVE-BLOOM 혼합덱 규칙 잠금'),'ROADMAP closes the mixed-deck material task');
ok(road.includes('- [x] TWELVE-BLOOM 24장 정식 후보 풀 재설계'),'ROADMAP closes the 24-card candidate design task');
ok(road.includes('- [ ] TWELVE-BLOOM UI/UX 구현 검증')&&road.includes('- [ ] TWELVE-BLOOM 밸런스/회귀 검증'),'implementation/UI/balance remain explicitly open');

console.log('TWELVE-BLOOM design-lock regression passed.');

import fs from 'node:fs';
import {runExperiment,DENSITIES} from '../experiments/m11b-asymmetric-density.mjs';

const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const doc=fs.readFileSync(new URL('../docs/ASYMMETRIC_RANK_PROTOTYPE.md',import.meta.url),'utf8');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}

ok(DENSITIES.zero.length===0&&DENSITIES.few.length===4&&DENSITIES.many.length===10,'density experiment keeps explicit 0 / 4 / 10 synthetic cohorts');
const results=runExperiment(700),[zero,few,many]=results;
ok(zero.basePlayableRate===zero.playableRate&&zero.choiceUpliftHandRate===0,'zero-asymmetric cohort has no choice-derived structural uplift');
ok(few.basePlayableRate===zero.basePlayableRate&&many.basePlayableRate===zero.basePlayableRate,'all cohorts preserve the exact same base-slot hand geometry');
ok(few.playableRate>zero.playableRate&&many.playableRate>few.playableRate,'structural playability rises monotonically with asymmetric density');
ok(few.choiceUpliftHandRate>0&&many.choiceUpliftHandRate>few.choiceUpliftHandRate,'choice-only rescued hands rise with density');
ok(few.avgLegalCardCombos>zero.avgLegalCardCombos&&many.avgLegalCardCombos>few.avgLegalCardCombos,'average legal 3-card combination count rises with density');
ok(few.twoMeldPotentialRate>=zero.twoMeldPotentialRate&&many.twoMeldPotentialRate>=few.twoMeldPotentialRate,'two-disjoint-meld structural potential never falls when rank choices are added');
ok(few.playableRate-zero.playableRate<=8,'4-card smoke cohort stays inside the broad pre-live structural uplift guard');
ok(many.playableRate-zero.playableRate<=12,'10-card stress cohort remains bounded rather than approaching wildcard-like behavior');
ok(many.avgLegalCardCombos<=zero.avgLegalCardCombos*1.75,'10-card stress cohort does not multiply legal hand combinations without bound');

const namedStart=html.indexOf('const NAMED={'),namedEnd=html.indexOf('const FIELDS=',namedStart),namedBlock=html.slice(namedStart,namedEnd);
ok(!/topRank\s*:|bottomRank\s*:/.test(namedBlock),'structural simulation still keeps zero live asymmetric NAMED definitions');
ok(doc.includes('## 구조적 밀도 시뮬레이션 — 라이브 승격 전 사전 게이트'),'prototype doc records the density experiment methodology and results');
ok(doc.includes('32.48%')&&doc.includes('37.60%')&&doc.includes('40.52%'),'prototype doc locks the 4,000-seed playable-rate baseline');
ok(doc.includes('세트 가능률은 +4.72%p')&&doc.includes('런은 +2.64%p'),'prototype doc records the stronger SET-side uplift warning');
ok(doc.includes('최대 4장 수준의 X/Y 노출')&&doc.includes('카드 규칙이나 덱빌더 하드캡이 아니라'),'first live density recommendation is explicitly a content-rollout gate, not a base rule');
ok(road.includes('- [x] 라이브 승격 전 구조적 밀도 시뮬레이션'),'ROADMAP marks the structural pre-live simulation complete');
ok(road.includes('- [ ] 비대칭 카드 0장 / 소수 / 다수 덱의 세트·런 성공률, 패말림, 정비, 러미 빈도 비교'),'full battle-flow density balance item remains intentionally open');
ok(road.includes('- [ ] Balance from playtest data before large content expansion'),'M12 real-playtest balance gate remains intentionally open');
console.log('M11B asymmetric-density structural simulation regression passed.');

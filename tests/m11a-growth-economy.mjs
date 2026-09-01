import assert from 'node:assert/strict';
import fs from 'node:fs';
import {runExperiment,BASE_DECK,BASE_REGULAR_SLOTS} from '../experiments/m11a-growth-economy.mjs';

const result=runExperiment(160);
assert.equal(BASE_DECK.length,30,'M11A baseline prototype must stay 29 regular slots + 1 Joker');
assert.equal(BASE_REGULAR_SLOTS.length,29,'M11A baseline regular slot count drifted');
assert.equal(result.baseline.deckSize,30);
assert.equal(result.replacement.deckSize,30);
assert.deepEqual(result.replacement,result.baseline,'same-slot named replacement must preserve structural draw/meld geometry');
assert.deepEqual(result.replacementStructuralDelta,{playableRate:0,setHandRate:0,runHandRate:0,twoMeldPotentialRate:0,avgLegalCardCombos:0});
assert.equal(result.removalCandidates,29,'single-removal sweep must exclude the Joker and cover every regular slot');
assert.equal(result.averageSingleRemoval.deckSize,29);
assert.equal(result.bestSingleRemoval.deckSize,29);
assert.equal(result.worstSingleRemoval.deckSize,29);
assert.ok(result.bestSingleRemoval.playableRate>=result.worstSingleRemoval.playableRate,'removal ordering must be deterministic');
assert.ok(!String(result.bestSingleRemoval.removedSlot).startsWith('J'),'Joker must not be part of the regular-slot removal economy sweep');
assert.ok(!String(result.worstSingleRemoval.removedSlot).startsWith('J'),'Joker must not be part of the regular-slot removal economy sweep');

const roadmap=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const plan=fs.readFileSync(new URL('../docs/ROGUELIKE_MASTER_PLAN.md',import.meta.url),'utf8');
assert.match(roadmap,/- \[x\] 카드 제거와 네임드 교체의 경제적 가치 비교/,'roadmap must close the structural removal-versus-replacement comparison');
assert.match(roadmap,/H10 제거.*\+2\.25%p.*S7 제거.*-2\.38%p/s,'roadmap must retain the measured slot-variance warning');
assert.match(plan,/동일 슬롯 교체 UI 계약 v1/,'master plan must keep the replacement contract before economy conclusions');
assert.match(plan,/성장 경제 구조 실험 v1/,'master plan must record the structural economy experiment');
assert.match(plan,/제거를 동일 슬롯 교체의 단순 상위 업그레이드로 가격 책정하지 않는다/,'removal must remain a separate scarce growth action rather than a flat stronger replacement');

console.log('M11A growth economy regression OK');

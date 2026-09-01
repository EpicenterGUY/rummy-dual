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
assert.match(roadmap,/카드 제거와 네임드 교체의 경제적 가치 비교/,'roadmap must keep the growth-economy decision');
assert.match(plan,/동일 슬롯 교체 UI 계약 v1/,'master plan must keep the replacement contract before economy conclusions');

console.log('M11A growth economy regression OK');

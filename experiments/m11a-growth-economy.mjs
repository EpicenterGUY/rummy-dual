import fs from 'node:fs';
import vm from 'node:vm';
import {fileURLToPath} from 'node:url';
import path from 'node:path';

const here=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(here,'..');
const html=fs.readFileSync(path.join(root,'index.html'),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let par=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')par++;else if(script[i]===')')par--;else if(script[i]==='{'&&par===0){brace=i;break}}if(brace<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}

export const RANK_VALUE={A:1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,J:11,Q:12,K:13};
export const BASE_REGULAR_SLOTS=['S3','S4','S5','S6','S7','S8','S9','H2','H3','H4','H7','H8','H9','D2','D3','D4','D5','D6','D7','D8','C3','C4','C5','C6','C7','C8','C9','S10','H10'];
export const BASE_DECK=[...BASE_REGULAR_SLOTS,'J1'];
const state={field:null,turnToken:1};
const ctx=vm.createContext({console,Math,Number,Object,Array,Set,RANK_VALUE,state});
for(const name of ['isJoker','isSuitFlexible','runSequenceOK','setValid','runValid','meldType'])vm.runInContext(source(name),ctx);

function makeCard(slot,uid){if(slot==='J1')return{uid,suit:'J',rank:'J1',baseRank:null,topRank:null,bottomRank:null,activeRank:null,rankOrientation:null,owner:'player'};const suit=slot[0],base=slot.slice(1);return{uid,suit,rank:base,baseRank:base,topRank:base,bottomRank:base,activeRank:null,rankOrientation:null,owner:'player'}}
function rng(seed){let x=(seed>>>0)||0x9e3779b9;return()=>{x^=x<<13;x^=x>>>17;x^=x<<5;return(x>>>0)/4294967296}}
function sampleIndices(n,k,rand){const a=Array.from({length:n},(_,i)=>i);for(let i=0;i<k;i++){const j=i+Math.floor(rand()*(n-i));[a[i],a[j]]=[a[j],a[i]]}return a.slice(0,k)}
function combos3(n){const out=[];for(let a=0;a<n-2;a++)for(let b=a+1;b<n-1;b++)for(let c=b+1;c<n;c++)out.push([a,b,c]);return out}
const HAND_COMBOS=combos3(6);
const PARTITIONS=HAND_COMBOS.filter(x=>x.includes(0)).map(left=>{const set=new Set(left),right=[];for(let i=0;i<6;i++)if(!set.has(i))right.push(i);return[left,right]});
function comboKey(idx){return idx.join(',')}
function analyzeHand(hand){let legalCombos=0,setCombos=0,runCombos=0;const legal=new Map();for(const idx of HAND_COMBOS){const type=ctx.meldType(idx.map(i=>hand[i])),key=comboKey(idx);legal.set(key,!!type);if(type){legalCombos++;if(type==='SET')setCombos++;if(type==='RUN')runCombos++}}const twoMeld=PARTITIONS.some(([a,b])=>legal.get(comboKey(a))&&legal.get(comboKey(b)));return{legalCombos,setCombos,runCombos,twoMeld}}

export function runDeck(deckSlots,seeds=Number(process.env.M11A_ECONOMY_SEEDS)||4000){if(deckSlots.length<6)throw new Error('deck needs at least 6 cards');const agg={playableHands:0,setHands:0,runHands:0,twoMeldHands:0,totalLegalCombos:0};for(let seed=1;seed<=seeds;seed++){const idx=sampleIndices(deckSlots.length,6,rng(seed)),hand=idx.map((i,n)=>makeCard(deckSlots[i],seed*100+n));const a=analyzeHand(hand);if(a.legalCombos>0)agg.playableHands++;if(a.setCombos>0)agg.setHands++;if(a.runCombos>0)agg.runHands++;if(a.twoMeld)agg.twoMeldHands++;agg.totalLegalCombos+=a.legalCombos}const pct=n=>+(n/seeds*100).toFixed(2),avg=n=>+(n/seeds).toFixed(3);return{deckSize:deckSlots.length,seeds,playableRate:pct(agg.playableHands),setHandRate:pct(agg.setHands),runHandRate:pct(agg.runHands),twoMeldPotentialRate:pct(agg.twoMeldHands),avgLegalCardCombos:avg(agg.totalLegalCombos)}}
function metricDelta(a,b){return{playableRate:+(a.playableRate-b.playableRate).toFixed(2),setHandRate:+(a.setHandRate-b.setHandRate).toFixed(2),runHandRate:+(a.runHandRate-b.runHandRate).toFixed(2),twoMeldPotentialRate:+(a.twoMeldPotentialRate-b.twoMeldPotentialRate).toFixed(2),avgLegalCardCombos:+(a.avgLegalCardCombos-b.avgLegalCardCombos).toFixed(3)}}
function meanMetrics(rows){const avg=k=>+(rows.reduce((sum,row)=>sum+row.metrics[k],0)/rows.length).toFixed(k==='avgLegalCardCombos'?3:2);return{deckSize:rows[0]?.metrics.deckSize??0,seeds:rows[0]?.metrics.seeds??0,playableRate:avg('playableRate'),setHandRate:avg('setHandRate'),runHandRate:avg('runHandRate'),twoMeldPotentialRate:avg('twoMeldPotentialRate'),avgLegalCardCombos:avg('avgLegalCardCombos')}}
function compactRemoval(row,baseline){return{removedSlot:row.removedSlot,...row.metrics,delta:metricDelta(row.metrics,baseline)}}

export function runExperiment(seeds=Number(process.env.M11A_ECONOMY_SEEDS)||4000){const baseline=runDeck(BASE_DECK,seeds);const replacement=runDeck(BASE_DECK,seeds);const removals=BASE_REGULAR_SLOTS.map(removedSlot=>({removedSlot,metrics:runDeck(BASE_DECK.filter(slot=>slot!==removedSlot),seeds)}));const averageRemoval=meanMetrics(removals);const sorted=[...removals].sort((a,b)=>b.metrics.playableRate-a.metrics.playableRate||b.metrics.avgLegalCardCombos-a.metrics.avgLegalCardCombos||a.removedSlot.localeCompare(b.removedSlot));return{seeds,baseline,replacement,replacementStructuralDelta:metricDelta(replacement,baseline),averageSingleRemoval:{...averageRemoval,delta:metricDelta(averageRemoval,baseline)},bestSingleRemoval:compactRemoval(sorted[0],baseline),worstSingleRemoval:compactRemoval(sorted.at(-1),baseline),topFive:sorted.slice(0,5).map(row=>compactRemoval(row,baseline)),bottomFive:sorted.slice(-5).reverse().map(row=>compactRemoval(row,baseline)),removalCandidates:removals.length}}

if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 const result=runExperiment();
 console.log('M11A_GROWTH_ECONOMY_RESULTS '+JSON.stringify(result));
 console.log(`baseline: deck=${result.baseline.deckSize}, playable=${result.baseline.playableRate}%, set=${result.baseline.setHandRate}%, run=${result.baseline.runHandRate}%, two-meld=${result.baseline.twoMeldPotentialRate}%, avg-combos=${result.baseline.avgLegalCardCombos}`);
 console.log(`replace-slot: structural delta playable ${result.replacementStructuralDelta.playableRate >= 0 ? '+' : ''}${result.replacementStructuralDelta.playableRate}%p, avg-combos ${result.replacementStructuralDelta.avgLegalCardCombos >= 0 ? '+' : ''}${result.replacementStructuralDelta.avgLegalCardCombos}`);
 console.log(`single-remove mean: playable=${result.averageSingleRemoval.playableRate}% (${result.averageSingleRemoval.delta.playableRate >= 0 ? '+' : ''}${result.averageSingleRemoval.delta.playableRate}%p), avg-combos=${result.averageSingleRemoval.avgLegalCardCombos} (${result.averageSingleRemoval.delta.avgLegalCardCombos >= 0 ? '+' : ''}${result.averageSingleRemoval.delta.avgLegalCardCombos})`);
 console.log(`best remove ${result.bestSingleRemoval.removedSlot}: playable=${result.bestSingleRemoval.playableRate}% (${result.bestSingleRemoval.delta.playableRate >= 0 ? '+' : ''}${result.bestSingleRemoval.delta.playableRate}%p)`);
 console.log(`worst remove ${result.worstSingleRemoval.removedSlot}: playable=${result.worstSingleRemoval.playableRate}% (${result.worstSingleRemoval.delta.playableRate >= 0 ? '+' : ''}${result.worstSingleRemoval.delta.playableRate}%p)`);
}

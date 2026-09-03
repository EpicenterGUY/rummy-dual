import {createStatusContext} from '../tests/helpers/status-fixture.mjs';
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
export const CORE_IDS=['S3','S4','S5','S6','S7','S8','S9','H2','H3','H4','H7','H8','H9','D2','D3','D4','D5','D6','D7','D8','C3','C4','C5','C6','C7','C8','C9','S10','H10'];
export const SYNTHETIC={H4:['4','6'],S5:['5','8'],D4:['4','9'],C5:['5','K'],D6:['6','8'],C3:['3','6'],H7:['7','10'],C6:['6','J'],S8:['8','K'],D3:['3','Q']};
export const DENSITIES={zero:[],few:['H4','S5','D4','C5'],many:Object.keys(SYNTHETIC)};
const state={field:null,turnToken:1};
const ctx=createStatusContext(script,{console,Math,Number,Object,Array,Set,RANK_VALUE,state});
for(const name of ['normalizePrototypeRank','ensureRankPrototype','cardPrintedRanks','isAsymmetricRankCard','isJoker','isSuitFlexible','rankChoiceOptions','rankChoicePlans','projectRankChoiceCards','rankChoicePlanLabel','runSequenceOK','setValid','runValid','meldType','legalRankChoicePlansForNewMeld'])vm.runInContext(source(name),ctx);

function makeCard(slot,asymSet,uid){if(slot==='J1')return{uid,suit:'J',rank:'J1',baseRank:null,topRank:null,bottomRank:null,activeRank:null,rankOrientation:null,owner:'player'};const suit=slot[0],base=slot.slice(1),pair=asymSet.has(slot)?SYNTHETIC[slot]:null;return{uid,suit,rank:base,baseRank:base,topRank:pair?.[0]||base,bottomRank:pair?.[1]||base,activeRank:null,rankOrientation:null,owner:'player'}}
function rng(seed){let x=(seed>>>0)||0x9e3779b9;return()=>{x^=x<<13;x^=x>>>17;x^=x<<5;return(x>>>0)/4294967296}}
function sampleIndices(n,k,rand){const a=Array.from({length:n},(_,i)=>i);for(let i=0;i<k;i++){const j=i+Math.floor(rand()*(n-i));[a[i],a[j]]=[a[j],a[i]]}return a.slice(0,k)}
function combos3(n){const out=[];for(let a=0;a<n-2;a++)for(let b=a+1;b<n-1;b++)for(let c=b+1;c<n;c++)out.push([a,b,c]);return out}
const HAND_COMBOS=combos3(6);
const PARTITIONS=HAND_COMBOS.filter(x=>x.includes(0)).map(left=>{const set=new Set(left),right=[];for(let i=0;i<6;i++)if(!set.has(i))right.push(i);return[left,right]});
function baseProjection(cards){return cards.map(c=>c.suit==='J'?{...c}:{...c,rank:c.baseRank,topRank:c.baseRank,bottomRank:c.baseRank,activeRank:null,rankOrientation:null})}
function comboKey(idx){return idx.join(',')}
function analyzeHand(hand){let baseCombos=0,flexCombos=0,setCombos=0,runCombos=0,choiceDependentCombos=0,legalPlans=0;const baseLegal=new Map(),flexLegal=new Map();for(const idx of HAND_COMBOS){const cards=idx.map(i=>hand[i]),baseType=ctx.meldType(baseProjection(cards)),plans=ctx.legalRankChoicePlansForNewMeld(cards),key=comboKey(idx);baseLegal.set(key,!!baseType);flexLegal.set(key,plans.length>0);if(baseType)baseCombos++;if(plans.length){flexCombos++;legalPlans+=plans.length;if(plans.some(p=>p.type==='SET'))setCombos++;if(plans.some(p=>p.type==='RUN'))runCombos++;if(!baseType)choiceDependentCombos++}}const baseTwoMeld=PARTITIONS.some(([a,b])=>baseLegal.get(comboKey(a))&&baseLegal.get(comboKey(b))),flexTwoMeld=PARTITIONS.some(([a,b])=>flexLegal.get(comboKey(a))&&flexLegal.get(comboKey(b)));return{baseCombos,flexCombos,setCombos,runCombos,choiceDependentCombos,legalPlans,baseTwoMeld,flexTwoMeld}}

export function runDensity(name,slots,seeds=Number(process.env.M11B_DENSITY_SEEDS)||4000){const asymSet=new Set(slots),deck=[...CORE_IDS,'J1'];const agg={playableHands:0,basePlayableHands:0,setHands:0,runHands:0,choiceUpliftHands:0,deadHands:0,handsWithAsym:0,baseTwoMeldHands:0,flexTwoMeldHands:0,twoMeldUpliftHands:0,totalFlexCombos:0,totalBaseCombos:0,totalChoiceDependentCombos:0,totalLegalPlans:0};for(let seed=1;seed<=seeds;seed++){const idx=sampleIndices(deck.length,6,rng(seed)),hand=idx.map(i=>makeCard(deck[i],asymSet,i+1)),a=analyzeHand(hand);if(hand.some(c=>c.suit!=='J'&&c.topRank!==c.bottomRank))agg.handsWithAsym++;if(a.flexCombos>0)agg.playableHands++;else agg.deadHands++;if(a.baseCombos>0)agg.basePlayableHands++;if(a.setCombos>0)agg.setHands++;if(a.runCombos>0)agg.runHands++;if(a.flexCombos>0&&a.baseCombos===0)agg.choiceUpliftHands++;if(a.baseTwoMeld)agg.baseTwoMeldHands++;if(a.flexTwoMeld)agg.flexTwoMeldHands++;if(a.flexTwoMeld&&!a.baseTwoMeld)agg.twoMeldUpliftHands++;agg.totalFlexCombos+=a.flexCombos;agg.totalBaseCombos+=a.baseCombos;agg.totalChoiceDependentCombos+=a.choiceDependentCombos;agg.totalLegalPlans+=a.legalPlans}
 const pct=n=>+(n/seeds*100).toFixed(2),avg=n=>+(n/seeds).toFixed(3);return{density:name,asymmetricCards:slots.length,seeds,handsWithAsymRate:pct(agg.handsWithAsym),playableRate:pct(agg.playableHands),basePlayableRate:pct(agg.basePlayableHands),setHandRate:pct(agg.setHands),runHandRate:pct(agg.runHands),deadHandRate:pct(agg.deadHands),choiceUpliftHandRate:pct(agg.choiceUpliftHands),choiceUpliftGivenAsymHandRate:agg.handsWithAsym?+(agg.choiceUpliftHands/agg.handsWithAsym*100).toFixed(2):0,twoMeldPotentialRate:pct(agg.flexTwoMeldHands),baseTwoMeldPotentialRate:pct(agg.baseTwoMeldHands),twoMeldUpliftRate:pct(agg.twoMeldUpliftHands),avgLegalCardCombos:avg(agg.totalFlexCombos),avgBaseCardCombos:avg(agg.totalBaseCombos),avgChoiceDependentCombos:avg(agg.totalChoiceDependentCombos),avgLegalPlans:avg(agg.totalLegalPlans)}}

export function runExperiment(seeds=Number(process.env.M11B_DENSITY_SEEDS)||4000){return Object.entries(DENSITIES).map(([name,slots])=>runDensity(name,slots,seeds))}

if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 const results=runExperiment();console.log('M11B_DENSITY_RESULTS '+JSON.stringify(results));for(const x of results)console.log(`${x.density}: asym=${x.asymmetricCards}, drawn=${x.handsWithAsymRate}%, playable=${x.playableRate}%, dead=${x.deadHandRate}%, set=${x.setHandRate}%, run=${x.runHandRate}%, choice-uplift=${x.choiceUpliftHandRate}%, two-meld=${x.twoMeldPotentialRate}%, avg-combos=${x.avgLegalCardCombos}`)
}

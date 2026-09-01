import fs from 'node:fs';
import vm from 'node:vm';

const html=fs.readFileSync('index.html','utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let par=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')par++;else if(script[i]===')')par--;else if(script[i]==='{'&&par===0){brace=i;break}}if(brace<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}

const RANK_VALUE={A:1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,J:11,Q:12,K:13};
const CORE_IDS=['S3','S4','S5','S6','S7','S8','S9','H2','H3','H4','H7','H8','H9','D2','D3','D4','D5','D6','D7','D8','C3','C4','C5','C6','C7','C8','C9','S10','H10'];
const SYNTHETIC={
  H4:['4','6'],
  S5:['5','8'],
  D4:['4','9'],
  C5:['5','K'],
  D6:['6','8'],
  C3:['3','6'],
  H7:['7','10'],
  C6:['6','J'],
  S8:['8','K'],
  D3:['3','Q']
};
const DENSITIES={zero:[],few:['H4','S5','D4','C5'],many:Object.keys(SYNTHETIC)};
const state={field:null,turnToken:1};
const ctx=vm.createContext({console,Math,Number,Object,Array,Set,RANK_VALUE,state});
for(const name of ['normalizePrototypeRank','ensureRankPrototype','cardPrintedRanks','isAsymmetricRankCard','isJoker','isSuitFlexible','rankChoiceOptions','rankChoicePlans','projectRankChoiceCards','rankChoicePlanLabel','runSequenceOK','setValid','runValid','meldType','legalRankChoicePlansForNewMeld'])vm.runInContext(source(name),ctx);

function makeCard(slot,asymSet,uid){if(slot==='J1')return{uid,suit:'J',rank:'J1',baseRank:null,topRank:null,bottomRank:null,activeRank:null,rankOrientation:null,owner:'player'};const suit=slot[0],base=slot.slice(1),pair=asymSet.has(slot)?SYNTHETIC[slot]:null;return{uid,suit,rank:base,baseRank:base,topRank:pair?.[0]||base,bottomRank:pair?.[1]||base,activeRank:null,rankOrientation:null,owner:'player'}}
function rng(seed){let x=(seed>>>0)||0x9e3779b9;return()=>{x^=x<<13;x^=x>>>17;x^=x<<5;return(x>>>0)/4294967296}}
function sampleIndices(n,k,rand){const a=Array.from({length:n},(_,i)=>i);for(let i=0;i<k;i++){const j=i+Math.floor(rand()*(n-i));[a[i],a[j]]=[a[j],a[i]]}return a.slice(0,k)}
function combos3(n){const out=[];for(let a=0;a<n-2;a++)for(let b=a+1;b<n-1;b++)for(let c=b+1;c<n;c++)out.push([a,b,c]);return out}
const HAND_COMBOS=combos3(6);
function baseProjection(cards){return cards.map(c=>c.suit==='J'?{...c}:{...c,rank:c.baseRank,topRank:c.baseRank,bottomRank:c.baseRank,activeRank:null,rankOrientation:null})}
function analyzeHand(hand){let baseCombos=0,flexCombos=0,setCombos=0,runCombos=0,choiceDependentCombos=0,legalPlans=0;for(const idx of HAND_COMBOS){const cards=idx.map(i=>hand[i]),baseType=ctx.meldType(baseProjection(cards)),plans=ctx.legalRankChoicePlansForNewMeld(cards);if(baseType)baseCombos++;if(plans.length){flexCombos++;legalPlans+=plans.length;if(plans.some(p=>p.type==='SET'))setCombos++;if(plans.some(p=>p.type==='RUN'))runCombos++;if(!baseType)choiceDependentCombos++}}return{baseCombos,flexCombos,setCombos,runCombos,choiceDependentCombos,legalPlans}}
function maintenanceRescue(deck,handIdx,asymSet,seed){const handSet=new Set(handIdx),remaining=[];for(let i=0;i<deck.length;i++)if(!handSet.has(i))remaining.push(i);if(!remaining.length)return false;const rand=rng(seed^0xa5a5a5a5);for(let bottom=0;bottom<handIdx.length;bottom++){for(let trial=0;trial<Math.min(8,remaining.length);trial++){const drawIdx=remaining[Math.floor(rand()*remaining.length)],next=[...handIdx];next[bottom]=drawIdx;const cards=next.map(i=>makeCard(deck[i],asymSet,i+1));if(analyzeHand(cards).flexCombos>0)return true}}return false}
function runDensity(name,slots,seeds=12000){const asymSet=new Set(slots),deck=[...CORE_IDS,'J1'];const agg={name,asymCards:slots.length,seeds,playableHands:0,basePlayableHands:0,setHands:0,runHands:0,choiceUpliftHands:0,deadHands:0,maintenanceRescues:0,totalFlexCombos:0,totalBaseCombos:0,totalChoiceDependentCombos:0,totalLegalPlans:0};for(let seed=1;seed<=seeds;seed++){const rand=rng(seed),idx=sampleIndices(deck.length,6,rand),hand=idx.map(i=>makeCard(deck[i],asymSet,i+1)),a=analyzeHand(hand);if(a.flexCombos>0)agg.playableHands++;else{agg.deadHands++;if(maintenanceRescue(deck,idx,asymSet,seed))agg.maintenanceRescues++}if(a.baseCombos>0)agg.basePlayableHands++;if(a.setCombos>0)agg.setHands++;if(a.runCombos>0)agg.runHands++;if(a.flexCombos>0&&a.baseCombos===0)agg.choiceUpliftHands++;agg.totalFlexCombos+=a.flexCombos;agg.totalBaseCombos+=a.baseCombos;agg.totalChoiceDependentCombos+=a.choiceDependentCombos;agg.totalLegalPlans+=a.legalPlans}
 const pct=n=>+(n/seeds*100).toFixed(2),avg=n=>+(n/seeds).toFixed(3);return{density:name,asymmetricCards:slots.length,seeds,playableRate:pct(agg.playableHands),basePlayableRate:pct(agg.basePlayableHands),setHandRate:pct(agg.setHands),runHandRate:pct(agg.runHands),deadHandRate:pct(agg.deadHands),choiceUpliftHandRate:pct(agg.choiceUpliftHands),deadHandMaintenanceRescueRate:agg.deadHands?+(agg.maintenanceRescues/agg.deadHands*100).toFixed(2):0,avgLegalCardCombos:avg(agg.totalFlexCombos),avgBaseCardCombos:avg(agg.totalBaseCombos),avgChoiceDependentCombos:avg(agg.totalChoiceDependentCombos),avgLegalPlans:avg(agg.totalLegalPlans)}}

const results=Object.entries(DENSITIES).map(([name,slots])=>runDensity(name,slots));
console.log('M11B_DENSITY_RESULTS '+JSON.stringify(results));
for(const x of results)console.log(`${x.density}: asym=${x.asymmetricCards}, playable=${x.playableRate}%, dead=${x.deadHandRate}%, set=${x.setHandRate}%, run=${x.runHandRate}%, choice-uplift=${x.choiceUpliftHandRate}%, avg-combos=${x.avgLegalCardCombos}, maintenance-rescue=${x.deadHandMaintenanceRescueRate}%`);

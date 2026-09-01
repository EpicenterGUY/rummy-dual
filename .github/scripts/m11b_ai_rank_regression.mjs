import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync('index.html','utf8');
const road=fs.readFileSync('ROADMAP.md','utf8');
const doc=fs.readFileSync('docs/ASYMMETRIC_RANK_PROTOTYPE.md','utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let par=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')par++;else if(script[i]===')')par--;else if(script[i]==='{'&&par===0){brace=i;break}}if(brace<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
function install(ctx,...names){for(const n of names)vm.runInContext(source(n),ctx)}
new Function(script);

const aiNew=source('bestNewMeld'),aiAttach=source('bestExtensionFromHand'),anyAttach=source('anyAttachOption'),aiLoop=source('continueAITurnAfterAcquisition');
ok(aiNew.includes('legalRankChoicePlansForNewMeld'),'CPU new-meld planner enumerates rank-choice plans');
ok(aiNew.includes('rankPlan:cand.plan||null'),'CPU new-meld result preserves the chosen rank plan');
ok(aiAttach.includes('legalRankChoicePlansForAttach'),'CPU attach planner enumerates top/bottom plans for single and multi-attach');
ok(aiAttach.includes('projected=cand.projected||cs'),'CPU attach scoring uses the chosen projected ranks');
ok(anyAttach.includes('legalRankChoicePlansForAttach'),'stuck-state attach legality recognizes alternate printed ranks');
ok(aiLoop.includes("attachCards('enemy',ex.cards,ex.side,ex.index,ex.rankPlan||null)"),'CPU passes selected attach rank plan into the real action');
ok(aiLoop.includes("submitNewMeld('enemy',nm.cards,nm.rankPlan||null)"),'CPU passes selected new-meld rank plan into the real action');

const RANK_VALUE={A:1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,J:11,Q:12,K:13};
let uid=1;
const card=(suit,base,top=base,bottom=base,extra={})=>({uid:uid++,suit,rank:base,baseRank:base,topRank:top,bottomRank:bottom,activeRank:null,rankOrientation:null,owner:'enemy',originOwner:'enemy',named:false,tag:null,blockedUntilTurn:null,recoveredToken:null,recoverReturnOverrideToken:null,...extra});
const rankNames=['normalizePrototypeRank','ensureRankPrototype','cardPrintedRanks','isAsymmetricRankCard','isJoker','isSuitFlexible','rankChoiceOptions','rankChoicePlans','projectRankChoiceCards','rankChoicePlanLabel','runSequenceOK','setValid','runValid','meldType','legalRankChoicePlansForNewMeld','legalRankChoicePlansForAttach'];

// New meld: base rank is illegal, top side makes the SET. CPU must preserve that exact plan without mutating the hand.
{
  const state={field:null,turnToken:1,turnNo:1,discard:[],switchTarget:'neutral',switchPower:0};
  const ctx=vm.createContext({console,Math,Number,Object,Array,Set,RANK_VALUE,state});install(ctx,'combinations',...rankNames,'bestNewMeld');
  const a=card('S','7','3','7'),b=card('H','3'),c=card('D','3'),hand=[a,b,c],before=JSON.stringify(hand);
  ctx.futureBurstRisk=(w,cards,type)=>type==='SET'&&cards[0].rank==='3'?5:0;
  const plan=ctx.bestNewMeld(hand,'enemy');
  ok(plan?.type==='SET'&&plan.rankPlan?.[0]?.rank==='3'&&plan.rankPlan?.[0]?.orientation==='top','CPU finds a SET that exists only through the asymmetric top value');
  ok(plan.score===10,'CPU applies existing new-SET score and future-BURST risk to the selected-rank projection');
  ok(JSON.stringify(hand)===before,'CPU new-meld planning never mutates unresolved real cards');
}

// Attach: CPU finds an immediate opponent SET BURST only through the alternate value.
{
  const a=card('D','3','7','3'),hand=[a];
  const enemy={hand,melds:[],returnedSwitchThisTurn:false},player={hand:[],melds:[{type:'SET',cards:[card('S','7'),card('H','7'),card('C','7')],chain:0,lastAttachToken:null,createdToken:null}],returnedSwitchThisTurn:false};
  const state={enemy,player,field:null,turnToken:2,turnNo:1,switchTarget:'neutral',switchPower:0};
  const ctx=vm.createContext({console,Math,Number,Object,Array,Set,RANK_VALUE,state});ctx.sideObj=w=>w==='enemy'?enemy:player;ctx.other=w=>w==='enemy'?'player':'enemy';ctx.meldsOf=w=>ctx.sideObj(w).melds;ctx.canSideReturn=()=>true;ctx.recoveredCardsCanReturn=()=>true;ctx.canContinueReturnedRun=()=>false;ctx.chainDamage=n=>n===1?10:n===2?15:n===3?20:25;
  install(ctx,'combinations',...rankNames,'bestExtensionFromHand');
  const plan=ctx.bestExtensionFromHand('enemy',hand);
  ok(plan?.side==='player'&&plan.score===28,'CPU values selected-rank opponent SET BURST at +24 plus existing opponent-meld fallback bias');
  ok(plan.rankPlan?.[0]?.rank==='7'&&plan.rankPlan?.[0]?.orientation==='top','CPU preserves the top-7 plan required for the BURST');
  ok(a.rank==='3'&&a.activeRank===null,'CPU BURST planning leaves the actual hand card unresolved until action commit');
}

// Multi-attach: four printed combinations collapse to one legal 7->8 RUN plan and CPU keeps both choices in order.
{
  const a=card('S','10','10','7'),b=card('S','Q','Q','8'),hand=[a,b];
  const enemy={hand,melds:[{type:'RUN',cards:[card('S','4'),card('S','5'),card('S','6')],chain:0,lastAttachToken:null,createdToken:null}],returnedSwitchThisTurn:false},player={hand:[],melds:[],returnedSwitchThisTurn:false};
  const state={enemy,player,field:null,turnToken:3,turnNo:1,switchTarget:'neutral',switchPower:0};
  const ctx=vm.createContext({console,Math,Number,Object,Array,Set,RANK_VALUE,state});ctx.sideObj=w=>w==='enemy'?enemy:player;ctx.other=w=>w==='enemy'?'player':'enemy';ctx.meldsOf=w=>ctx.sideObj(w).melds;ctx.canSideReturn=()=>true;ctx.recoveredCardsCanReturn=()=>true;ctx.canContinueReturnedRun=()=>false;ctx.chainDamage=n=>n===1?10:n===2?15:n===3?20:25;
  install(ctx,'combinations',...rankNames,'bestExtensionFromHand');
  const plan=ctx.bestExtensionFromHand('enemy',hand);
  ok(plan?.cards.length===2&&plan.score===25,'CPU scores two-card RUN extension with the existing +10 +15 chain curve');
  ok(plan.rankPlan?.map(x=>`${x.orientation}:${x.rank}`).join('|')==='bottom:7|bottom:8','CPU multi-attach preserves selected-card order and the only legal bottom/bottom plan');
}

// Equal-value legal orientations remain deterministic top-first rather than random.
{
  const a=card('S','9','4','8'),hand=[a];
  const enemy={hand,melds:[{type:'RUN',cards:[card('S','5'),card('S','6'),card('S','7')],chain:0,lastAttachToken:null,createdToken:null}],returnedSwitchThisTurn:false},player={hand:[],melds:[],returnedSwitchThisTurn:false};
  const state={enemy,player,field:null,turnToken:4,turnNo:1,switchTarget:'neutral',switchPower:0};
  const ctx=vm.createContext({console,Math,Number,Object,Array,Set,RANK_VALUE,state});ctx.sideObj=w=>w==='enemy'?enemy:player;ctx.other=w=>w==='enemy'?'player':'enemy';ctx.meldsOf=w=>ctx.sideObj(w).melds;ctx.canSideReturn=()=>true;ctx.recoveredCardsCanReturn=()=>true;ctx.canContinueReturnedRun=()=>false;ctx.chainDamage=()=>10;
  install(ctx,'combinations',...rankNames,'bestExtensionFromHand');
  const legal=ctx.legalRankChoicePlansForAttach(enemy.melds[0],[a]);
  ok(legal.length===2,'synthetic RUN exposes two equally legal orientations around the existing sequence');
  const plan=ctx.bestExtensionFromHand('enemy',hand);
  ok(plan.rankPlan?.[0]?.orientation==='top'&&plan.rankPlan?.[0]?.rank==='4','equal-score CPU rank plans use deterministic top-before-bottom enumeration');
}

// Stuck-state logic must not maintenance-cycle a card whose alternate printed value can attach.
{
  const a=card('D','3','7','3'),enemy={hand:[a],melds:[],returnedSwitchThisTurn:false},player={hand:[],melds:[{type:'SET',cards:[card('S','7'),card('H','7'),card('C','7')],chain:0,lastAttachToken:null,createdToken:null}],returnedSwitchThisTurn:false};
  const state={enemy,player,field:null,turnToken:5,turnNo:1};
  const ctx=vm.createContext({console,Math,Number,Object,Array,Set,RANK_VALUE,state});ctx.sideObj=w=>w==='enemy'?enemy:player;ctx.other=w=>w==='enemy'?'player':'enemy';ctx.meldsOf=w=>ctx.sideObj(w).melds;ctx.canSideReturn=()=>true;ctx.recoveredCardsCanReturn=()=>true;ctx.canContinueReturnedRun=()=>false;
  install(ctx,'combinations',...rankNames,'anyAttachOption');
  ok(ctx.anyAttachOption('enemy')===true,'stuck-state legality recognizes an attach that exists only through alternate printed rank');
}

const namedStart=script.indexOf('const NAMED={'),namedEnd=script.indexOf('const FIELDS=',namedStart),namedBlock=script.slice(namedStart,namedEnd);
ok(!/topRank\s*:|bottomRank\s*:/.test(namedBlock),'CPU heuristic remains dormant with zero live asymmetric card definitions');
ok(doc.includes('## 4단계 — CPU 사용값 선택'),'prototype document records CPU rank-choice phase');
ok(doc.includes('bestNewMeld')&&doc.includes('bestExtensionFromHand')&&doc.includes('anyAttachOption'),'prototype document records new-meld, attach and stuck-state CPU integration');
ok(road.includes('- [x] CPU가 두 사용값의 세트·런 가능성, 즉시 버스트/체인, 스위치 반환 가치까지 비교하는 최소 휴리스틱 설계'),'ROADMAP locks the M11B CPU rank-choice heuristic');
console.log('M11B CPU asymmetric-rank heuristic regression passed.');

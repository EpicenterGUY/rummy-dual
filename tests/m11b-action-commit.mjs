import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const doc=fs.readFileSync(new URL('../docs/ASYMMETRIC_RANK_PROTOTYPE.md',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let par=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')par++;else if(script[i]===')')par--;else if(script[i]==='{'&&par===0){brace=i;break}}if(brace<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
function install(ctx,...names){for(const n of names)vm.runInContext(source(n),ctx)}
new Function(script);

for(const name of ['normalizeRequestedRankPlan','rankChoicePlanEquivalent','rankChoiceActionPlan','applyRankChoicePlan','rankResolutionPriority'])ok(script.includes(`function ${name}(`),`M11B action helper exists: ${name}`);
ok(source('submitNewMeld').includes('rankChoiceActionPlan(cards,null,rankPlan)'),'new meld action resolves a requested rank plan before mutation');
ok(source('attachCards').includes('rankChoiceActionPlan(cards,m,rankPlan)'),'attach action resolves a requested rank plan against the target meld');
{
  const src=source('submitNewMeld');
  ok(src.indexOf('applyRankChoicePlan(cards,rankAction.plan)')<src.indexOf('removeFromHand(w,cards)'),'new meld commits active ranks before cards leave hand');
  ok(src.indexOf('removeFromHand(w,cards)')<src.indexOf('resolveEffects(w,cards,type,ctx)'),'new meld preserves existing action/effect order after rank commit');
  ok(src.includes('const willRummy=s.hand.length===0')&&src.includes('triggerRummy(w,cards,{returned:false})'),'new meld keeps RUMMY in the post-effect finish phase; runtime regression below verifies the execution order');
}
{
  const src=source('attachCards');
  ok(src.indexOf('applyRankChoicePlan(cards,rankAction.plan)')<src.indexOf('removeFromHand(w,cards)'),'attach commits active ranks before cards leave hand');
  ok(src.indexOf('removeFromHand(w,cards)')<src.indexOf('m.cards.push(...cards)'),'attach keeps hand removal before public-meld insertion');
  ok(src.indexOf('m.cards.push(...cards)')<src.indexOf("if(type==='SET'&&beforeLen===3&&m.cards.length===4)"),'BURST/CHAIN power calculation occurs only after chosen ranks are in the public meld');
}

const RANK_VALUE={A:1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,J:11,Q:12,K:13};
let uid=1;
const card=(suit,base,top=base,bottom=base,extra={})=>({uid:uid++,suit,rank:base,baseRank:base,topRank:top,bottomRank:bottom,activeRank:null,rankOrientation:null,owner:'player',originOwner:'player',named:false,tag:null,fromDiscard:false,enteredMeldToken:null,recoveredToken:null,recoverReturnOverrideToken:null,blockedUntilTurn:null,...extra});
const rankCore=['normalizePrototypeRank','ensureRankPrototype','cardPrintedRanks','isAsymmetricRankCard','cardRuleRank','chooseCardActiveRank','clearCardActiveRank','rankChoiceState','isJoker','isSuitFlexible','rankChoiceOptions','rankChoicePlans','projectRankChoiceCards','rankChoicePlanLabel','runSequenceOK','setValid','runValid','meldType','legalRankChoicePlansForNewMeld','legalRankChoicePlansForAttach','normalizeRequestedRankPlan','rankChoicePlanEquivalent','rankChoiceActionPlan','applyRankChoicePlan','rankResolutionPriority'];

// Atomic plan validation and explicit-choice requirement.
{
  const state={field:null,turnToken:1};
  const ctx=vm.createContext({console,Math,Number,Object,Array,Set,RANK_VALUE,state});install(ctx,...rankCore);
  const a=card('S','7','3','7'),b=card('H','3'),c=card('D','3'),cards=[a,b,c],before=JSON.stringify(cards);
  let action=ctx.rankChoiceActionPlan(cards);
  ok(!action.ok&&action.reason==='choice-required'&&action.legalCount===1,'unresolved asymmetric action refuses to guess a direction even when only one plan is legal');
  action=ctx.rankChoiceActionPlan(cards,null,{ranks:['3','3','3'],orientations:['top',null,null]});
  ok(action.ok&&action.type==='SET'&&action.plan[0].rank==='3','serialized UI-shaped rank choice resolves to the matching legal SET plan');
  ok(JSON.stringify(cards)===before,'planning and plan matching remain non-mutating');
  const bad={ranks:['K','3','3'],orientations:['top',null,null]};
  ok(!ctx.applyRankChoicePlan(cards,bad)&&JSON.stringify(cards)===before,'invalid plan fails atomically without partially mutating any card');
  ok(ctx.applyRankChoicePlan(cards,action.plan),'validated action plan commits successfully');
  ok(a.activeRank==='3'&&a.rank==='3'&&a.rankOrientation==='top','committed asymmetric card mirrors chosen activeRank through legacy rank');
  ok(b.activeRank===null&&c.activeRank===null,'ordinary X/X cards remain legacy-compatible and need no active rank state');
}

// Priority: Joker wildcard > printed choice > local rank modifiers.
{
  const state={field:null,turnToken:2};
  const ctx=vm.createContext({console,Math,Number,Object,Array,Set,RANK_VALUE,state});install(ctx,...rankCore);
  const joker={uid:uid++,suit:'J',rank:'J1',baseRank:null,topRank:null,bottomRank:null,activeRank:null,rankOrientation:null,tag:'jokerKing'};
  ok(ctx.rankResolutionPriority(joker,'RUN').join('>')==='joker-wild','Joker keeps independent wildcard priority and never enters activeRank selection');
  const cf=card('S','9','3','9',{tag:'counterfeiter'}),r4=card('S','4'),r5=card('S','5');
  ok(ctx.chooseCardActiveRank(cf,'3','top')&&ctx.runValid([cf,r4,r5]),'Counterfeiter RUN offset is evaluated from the chosen top activeRank');
  ok(ctx.rankResolutionPriority(cf,'RUN').join('>')==='printed-choice>run-offset','Counterfeiter priority is printed choice first, RUN offset second');
  ctx.clearCardActiveRank(cf);ctx.chooseCardActiveRank(cf,'9','bottom');
  ok(!ctx.runValid([cf,r4,r5])&&cf.activeRank==='9','Counterfeiter cannot replace the printed choice with an unrelated value; only ±1 around activeRank is explored');
  const dg=card('C','Q','3','7',{tag:'flexRankCopy'}),s5=card('S','5'),h5=card('H','5');
  ctx.chooseCardActiveRank(dg,'3','top');
  ok(ctx.setValid([dg,s5,h5])&&dg.activeRank==='3'&&dg.rank==='3','Doppelganger SET copy can override equality locally without rewriting its chosen activeRank');
  ok(ctx.rankResolutionPriority(dg,'SET').join('>')==='printed-choice>set-rank-copy','Doppelganger priority is printed choice first, SET rank copy second');
}

// Real submitNewMeld path: chosen rank is locked before effects and RUMMY.
{
  const a=card('S','7','3','7'),b=card('H','3'),c=card('D','3'),cards=[a,b,c];
  const player={hand:[...cards],melds:[],newMeldCount:0,actedThisTurn:false,turnStarts:1},enemy={hand:[],melds:[],turnStarts:1};
  const state={player,enemy,field:null,turnNo:1,turnToken:11,gameOver:false,lastPlayerMeldType:null,lastEnemyMeldType:null};
  const capture={effectRanks:null,rummyRanks:null};
  const ctx=vm.createContext({console,Math,Number,Object,Array,Set,RANK_VALUE,state});
  ctx.sideObj=w=>w==='player'?player:enemy;ctx.meldsOf=w=>ctx.sideObj(w).melds;ctx.newMeldAccess=()=>({allowed:true,extra:false,quickReloadCard:null});ctx.beforeNewMeld=()=>true;
  ctx.removeFromHand=(w,list)=>{const ids=new Set(list.map(x=>x.uid));ctx.sideObj(w).hand=ctx.sideObj(w).hand.filter(x=>!ids.has(x.uid))};
  ctx.markSetCompletion=()=>{};ctx.fieldAction=()=>{};ctx.resolveEffects=(w,list,type)=>{capture.effectRanks=list.map(x=>x.rank);return{bonus:0,flatReturn:false,forceReturn:false,pending:false}};ctx.characterActionBonus=()=>{};ctx.triggerOpponentHandTraps=()=>{};ctx.log=()=>{};ctx.blankMeldStatus=()=>({});
  ctx.triggerRummy=(w,list)=>{capture.rummyRanks=list.map(x=>x.rank);return true};
  install(ctx,...rankCore,'submitNewMeld');
  const result=ctx.submitNewMeld('player',cards,{ranks:['3','3','3'],orientations:['top',null,null]});
  ok(result==='rummy'&&player.melds.length===1&&player.melds[0].type==='SET','real new-meld path accepts the selected asymmetric SET and reaches RUMMY');
  ok(player.melds[0].cards[0].activeRank==='3'&&player.melds[0].cards[0].rank==='3','public meld stores the selected active rank, not the base slot rank');
  ok(capture.effectRanks?.[0]==='3'&&capture.rummyRanks?.[0]==='3','meld effects and RUMMY both observe the selected active rank');
}

function makeAttachContext(type,baseCards,handCards,chain=0){
  const player={hand:[...handCards,card('C','2')],melds:[],returnedSwitchThisTurn:false,actedThisTurn:false,turnStarts:1};
  const enemy={hand:[],melds:[{type,cards:[...baseCards],chain,lastAttachToken:null,createdToken:null,lastTouchedOwnerStart:0,status:{}}],returnedSwitchThisTurn:false,turnStarts:1};
  const state={player,enemy,field:null,turnNo:1,turnToken:21,gameOver:false,switchTarget:'neutral',switchPower:0,pendingTrapReduction:0,lastPlayerReturnType:null,lastEnemyReturnType:null};
  const capture={attacks:[],retired:[],effectRanks:[]};
  const ctx=vm.createContext({console,Math,Number,Object,Array,Set,RANK_VALUE,state});
  ctx.sideObj=w=>w==='player'?player:enemy;ctx.other=w=>w==='player'?'enemy':'player';ctx.meldsOf=w=>ctx.sideObj(w).melds;ctx.canSideReturn=()=>true;
  ctx.removeFromHand=(w,list)=>{const ids=new Set(list.map(x=>x.uid));ctx.sideObj(w).hand=ctx.sideObj(w).hand.filter(x=>!ids.has(x.uid))};
  ctx.markSetCompletion=m=>{if(m.type==='RUN')m.chain=Math.max(0,Math.min(4,m.chain??Math.max(0,m.cards.length-3)))};ctx.fieldAction=()=>{};
  ctx.resolveEffects=(w,list)=>{capture.effectRanks.push(list.map(x=>x.rank));return{bonus:0,flatReturn:false,forceReturn:false,pending:false}};ctx.characterActionBonus=()=>{};ctx.triggerOpponentHandTraps=()=>{};
  ctx.attackEvent=(w,hits,opts)=>{capture.attacks.push({w,hits,opts,ranks:handCards.map(x=>x.rank)});state.switchPower+=hits.reduce((n,h)=>n+h.amount,0)+(opts.bonus||0);state.switchTarget=ctx.other(w);player.returnedSwitchThisTurn=true;return{total:state.switchPower}};
  ctx.addSwitchPower=(w,n)=>{state.switchPower+=n;return n};ctx.combatBanner=()=>{};ctx.fxNode=()=>{};ctx.drawOne=()=>null;ctx.pushDiscard=()=>{};ctx.log=()=>{};ctx.freeRecoverFromMeld=()=>null;ctx.cutOppositeEnd=()=>false;ctx.recoverRedundantGapRun=()=>null;ctx.middleManagerReturnPlaceholder=()=>null;ctx.replaceRedundantJokers=()=>{};ctx.triggerRummy=()=>{};
  ctx.retireMeld=(owner,index,reason)=>{const m=ctx.meldsOf(owner)[index];capture.retired.push({owner,reason,ranks:m.cards.map(x=>x.rank),active:m.cards.map(x=>x.activeRank)});ctx.meldsOf(owner).splice(index,1)};
  install(ctx,...rankCore,'recoveredCardCanReturn','recoveredCardsCanReturn','chainDamage','canContinueReturnedRun','attachCards');
  return{ctx,state,player,enemy,capture};
}

// Real attach path: selected rank feeds BURST and CHAIN before retirement/effects.
{
  const a=card('D','3','7','3');
  const setup=makeAttachContext('SET',[card('S','7'),card('H','7'),card('C','7')],[a]);
  ok(setup.ctx.attachCards('player',[a],'enemy',0,{ranks:['7'],orientations:['top']})===true,'real attach path accepts a selected asymmetric rank that completes opponent SET');
  ok(setup.capture.attacks.length===1&&setup.capture.attacks[0].hits[0].amount===24,'selected-rank SET completion resolves normal +24 BURST');
  ok(setup.capture.retired[0]?.ranks.includes('7')&&setup.capture.retired[0]?.active.includes('7'),'BURST retirement receives the selected active rank before zone cleanup');
}
{
  const a=card('H','9','8','10');
  const setup=makeAttachContext('RUN',[card('H','5'),card('H','6'),card('H','7')],[a],0);
  ok(setup.ctx.attachCards('player',[a],'enemy',0,{ranks:['8'],orientations:['top']})===true,'real attach path accepts selected asymmetric RUN extension');
  ok(setup.capture.attacks.length===1&&setup.capture.attacks[0].hits[0].amount===10,'selected-rank RUN extension preserves normal first CHAIN +10');
  ok(setup.enemy.melds[0].cards.at(-1).rank==='8'&&setup.enemy.melds[0].cards.at(-1).activeRank==='8'&&setup.enemy.melds[0].chain===1,'public RUN stores selected active rank and existing CHAIN state advances normally');
  ok(setup.capture.effectRanks.at(-1)?.[0]==='8','attach effects observe the selected active rank');
}

// RUN finish reads the locked selected rank before retirement.
{
  const a=card('S','9','8','10');a.activeRank='8';a.rankOrientation='top';a.rank='8';
  const player={melds:[{type:'RUN',cards:[card('S','5'),card('S','6'),card('S','7'),a],chain:4,status:{}}],actedThisTurn:false},enemy={melds:[]};
  const state={player,enemy,turn:'player',phase:'action',gameOver:false,target:null,boardSelected:new Set(),selected:new Set(),selectionOrder:[]};
  const seen=[];const ctx=vm.createContext({console,Set,state});ctx.sideObj=w=>w==='player'?player:enemy;ctx.meldsOf=w=>ctx.sideObj(w).melds;ctx.meldFixedActive=()=>false;ctx.cardFixedActive=()=>false;ctx.emitEffectEvent=(name,p)=>seen.push({name,ranks:p.cards.map(x=>x.rank),active:p.cards.map(x=>x.activeRank)});ctx.retireMeld=(w,i)=>ctx.meldsOf(w).splice(i,1);ctx.combatBanner=()=>{};ctx.log=()=>{};ctx.switchName=()=> '나';
  install(ctx,'canFinishRun','finishRun');
  ok(ctx.finishRun('player',0)===true,'RUN completion executes with a locked asymmetric card');
  ok(seen[0]?.name==='onRunFinish'&&seen[0].ranks.includes('8')&&seen[0].active.includes('8'),'RUN finish event observes selected active rank before retirement reset');
}

const namedStart=script.indexOf('const NAMED={'),namedEnd=script.indexOf('const FIELDS=',namedStart),namedBlock=script.slice(namedStart,namedEnd);
ok(!/topRank\s*:|bottomRank\s*:/.test(namedBlock),'M11B action commit still enables zero live asymmetric card definitions');
ok(doc.includes('## 3단계 — 행동 확정과 숫자 우선순위'),'prototype document records action commit phase');
ok(doc.includes('조커 와일드')&&doc.includes('카운터피터')&&doc.includes('도플갱어'),'prototype document records Joker / modifier / copy priority');
ok(road.includes('- [x] 버스트·체인·런 완주·러미 판정이 선택된 사용값만 읽고 기존 처리 순서를 그대로 유지하는지 검증'),'ROADMAP locks selected-rank action/timing verification');
ok(road.includes('- [x] 조커의 와일드 판정, 기존 숫자 변경 효과, 복사 효과와 비대칭 값이 중첩될 때 우선순위 명문화'),'ROADMAP locks rank-resolution priority');
ok(/- \[[ x]\] CPU가 두 사용값의 세트·런 가능성, 즉시 버스트\/체인, 스위치 반환 가치까지 비교하는 최소 휴리스틱 설계/.test(road),'CPU asymmetric-rank planning remains tracked across later M11B phases');
console.log('M11B action commit and rank-priority regression passed.');

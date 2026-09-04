import fs from 'node:fs';
import vm from 'node:vm';

const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let par=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')par++;else if(script[i]===')')par--;else if(script[i]==='{'&&par===0){brace=i;break}}if(brace<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
function context(extra={}){return vm.createContext({console,Math,Set,Map,Array,Object,Number,String,Boolean,...extra})}
function install(ctx,...names){for(const name of names)vm.runInContext(source(name),ctx)}
let uid=0;
function card(suit,rank,extra={}){return{uid:`mix-${++uid}`,suit,rank:String(rank),owner:'player',originOwner:'player',named:false,name:'순수 카드',tag:null,themeId:null,fromDiscard:false,age:0,enteredMeldToken:null,recoveredToken:null,recoverReturnOverrideToken:null,recoverReturnTargets:null,blockedUntilTurn:null,...extra}}
const RANK_VALUE={A:1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,J:11,Q:12,K:13};

ok(script.includes("'VSH5':{slot:'H5',themeId:'v-signal',n:'앙코르',t:'vEncore'"),'Encore remains a live V-SIGNAL card');
ok(script.includes("'VSD4':{slot:'D4',themeId:'v-signal',n:'전원 집합!',t:'vGatherAll'"),'Gather All remains a live V-SIGNAL card');
ok(script.includes("'VSCK':{slot:'CK',themeId:'v-signal',n:'24시간 내구방송',t:'vEndurance'"),'Endurance Broadcast remains a live V-SIGNAL card');

// 1) Encore recovered from an ordinary RUN can legally re-enter a completely non-theme 3SET.
{
  const encore=card('H','5',{named:true,name:'앙코르',tag:'vEncore',themeId:'v-signal',recoveredToken:91,encoreGrantToken:null,encoreReturnUsedToken:null});
  const sourceRun={type:'RUN',cards:[encore,card('H','6'),card('H','7'),card('H','8')],chain:1,createdToken:null};
  const targetSet={type:'SET',cards:[card('S','5'),card('D','5'),card('C','5')],chain:0,createdToken:null};
  const player={melds:[sourceRun],returnedSwitchThisTurn:false,attachCount:0,extraAttachRemaining:0};
  const enemy={melds:[targetSet],returnedSwitchThisTurn:false,attachCount:0,extraAttachRemaining:0};
  const state={turnNo:9,turnToken:91,player,enemy,field:null};
  const ctx=context({state,RANK_VALUE});
  ctx.sideObj=w=>w==='player'?player:enemy;
  ctx.other=w=>w==='player'?'enemy':'player';
  ctx.meldsOf=w=>ctx.sideObj(w).melds;
  ctx.canSideReturn=()=>true;
  ctx.log=()=>{};
  install(ctx,'isJoker','isSuitFlexible','setValid','runSequenceOK','runValid','meldType','attachAccess','legalRecoveryReturnTargets','grantRecoveryReturnOverride','handleVSignalThemeEvent','recoveredCardCanReturn','consumeEncoreReturnPermission');
  ok(ctx.runValid(sourceRun.cards),'mixed Encore source is a real ordinary-heart RUN');
  ok(ctx.setValid(targetSet.cards),'Encore destination starts as a real non-theme 3SET');
  ok(targetSet.cards.every(c=>!c.themeId),'Encore destination requires no V-SIGNAL partner');
  ok(ctx.handleVSignalThemeEvent({event:'onRecover',actor:'player',card:encore,meld:sourceRun,turnToken:91})===true,'Encore recovery event grants a mixed-deck return window');
  ok(encore.recoverReturnTargets.length===1&&encore.recoverReturnTargets[0]===targetSet,'Encore targets the ordinary 3SET and never its source RUN');
  ok(ctx.recoveredCardCanReturn(encore,91,targetSet)===true,'same-turn Encore return is legal on the ordinary destination');
  ok(ctx.recoveredCardCanReturn(encore,91,sourceRun)===false,'same-turn Encore return stays illegal on the recovered source');
  ok(ctx.meldType(targetSet.cards.concat(encore))==='SET','Encore actually completes the ordinary rank-5 4SET');
  ok(ctx.consumeEncoreReturnPermission([encore],91,targetSet)===1&&encore.encoreReturnUsedToken===91,'mixed return consumes Encore permission exactly once');
}

// 2) Gather All can preserve a normal named card while retirement still routes every other card by current owner.
{
  const gather=card('D','4',{named:true,name:'전원 집합!',tag:'vGatherAll',themeId:'v-signal'});
  const phoenix=card('H','4',{named:true,name:'불사조',tag:'heal2'});
  const pure=card('S','4');
  const foe=card('C','4',{owner:'enemy',originOwner:'enemy'});
  const meld={type:'SET',cards:[gather,phoenix,pure,foe],chain:0};
  const player={hand:[],deck:[],spent:[],melds:[meld]};
  const enemy={hand:[],deck:[],spent:[],melds:[]};
  const state={turnNo:12,turnToken:120,player,enemy,field:null};
  const events=[];
  const ctx=context({state,RANK_VALUE});
  ctx.sideObj=w=>w==='player'?player:enemy;
  ctx.meldsOf=w=>ctx.sideObj(w).melds;
  ctx.emitEffectEvent=(event,payload)=>{events.push({event,payload});return payload};
  ctx.log=()=>{};
  ctx.cardText=c=>`${c.rank}${c.suit}`;
  install(ctx,'isJoker','isSuitFlexible','setValid','runSequenceOK','runValid','meldType','retirePreservationOffer','retireMeld');
  ok(ctx.setValid(meld.cards),'Gather All scenario is a real mixed 4SET');
  const offer=ctx.retirePreservationOffer('player',meld,'burst');
  ok(offer?.source===gather,'Gather All is recognized as the preservation source');
  ok(offer.candidates.includes(phoenix)&&offer.candidates.includes(pure),'Gather All can preserve both a normal named card and a pure card');
  ok(!offer.candidates.includes(foe),'Gather All cannot preserve an opponent-controlled card from the same public meld');
  ctx.retireMeld('player',0,'혼합 버스트',{preserveCards:[phoenix],preserveLabel:'전원 집합!'});
  ok(player.melds.length===0,'mixed 4SET still retires completely');
  ok(player.hand.includes(phoenix)&&phoenix.tag==='heal2'&&phoenix.themeId===null,'preserved ordinary named card keeps its normal identity in hand');
  ok(phoenix.blockedUntilTurn===12&&phoenix.suppressEffectToken===120,'preserved ordinary named card is locked for the rest of the turn');
  ok(player.spent.includes(gather)&&player.spent.includes(pure),'unpreserved player-controlled cards still go to player spent');
  ok(enemy.spent.includes(foe),'opponent-controlled card still returns to the opponent circulation side');
  ok(events.length===1&&events[0].event==='onRetire'&&events[0].payload.cards.length===4&&events[0].payload.preserveCards[0]===phoenix,'onRetire exposes the full mixed meld plus the chosen ordinary preservation');
}

// 3) Endurance Broadcast can preserve a normal card from a real long club RUN; no theme-only partner is required.
{
  const normalNamed=card('C','7',{named:true,name:'황금손',tag:'goldenHand'});
  const endurance=card('C','K',{named:true,name:'24시간 내구방송',tag:'vEndurance',themeId:'v-signal'});
  const run={type:'RUN',cards:[normalNamed,card('C','8'),card('C','9'),card('C','10'),card('C','J'),card('C','Q'),endurance],chain:4};
  const player={hand:[],deck:[],spent:[],melds:[run]};
  const enemy={hand:[],deck:[],spent:[],melds:[]};
  const state={turnNo:18,turnToken:180,player,enemy,field:null};
  const ctx=context({state,RANK_VALUE});
  ctx.sideObj=w=>w==='player'?player:enemy;
  ctx.meldsOf=w=>ctx.sideObj(w).melds;
  ctx.emitEffectEvent=()=>{};
  ctx.log=()=>{};
  ctx.cardText=c=>`${c.rank}${c.suit}`;
  install(ctx,'isJoker','isSuitFlexible','setValid','runSequenceOK','runValid','meldType','retirePreservationOffer','retireMeld');
  ok(ctx.runValid(run.cards),'Endurance scenario is a real C7-K club RUN');
  const offer=ctx.retirePreservationOffer('player',run,'runFinish');
  ok(offer?.source===endurance&&offer.candidates.includes(normalNamed),'Endurance can preserve an existing non-theme named card');
  run.chain=3;
  ok(ctx.retirePreservationOffer('player',run,'runFinish')===null,'Endurance does not bypass the CHAIN 4+ completion requirement');
  run.chain=4;
  ctx.retireMeld('player',0,'혼합 런 완주',{preserveCards:[normalNamed],preserveLabel:'24시간 내구방송'});
  ok(player.hand.includes(normalNamed)&&normalNamed.tag==='goldenHand','preserved normal named card remains usable as its original card on later turns');
  ok(normalNamed.blockedUntilTurn===18,'Endurance preservation also applies the same-turn lock to non-theme cards');
  const fake={...endurance,uid:'fake-endurance',themeId:null};
  const fakeRun={...run,cards:[...run.cards.slice(0,-1),fake],chain:4};
  ok(ctx.retirePreservationOffer('player',fakeRun,'runFinish')===null,'a non-theme card cannot impersonate the V-SIGNAL preservation source');
}

ok(road.includes('- [x] V-SIGNAL ↔ 일반 카드 혼합 회귀 테스트'),'ROADMAP marks V-SIGNAL mixed-card regression complete');
ok(!script.includes('hypeCount')&&!script.includes('HYPE_COUNT'),'mixed-deck support still adds no HYPE resource');
console.log('V-SIGNAL mixed-deck regression passed.');

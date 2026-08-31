import fs from 'node:fs';
import vm from 'node:vm';

const html=fs.readFileSync('index.html','utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
const road=fs.readFileSync('ROADMAP.md','utf8');
const themeDoc=fs.readFileSync('docs/THEME_GROUPS.md','utf8');

function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let par=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')par++;else if(script[i]===')')par--;else if(script[i]==='{'&&par===0){brace=i;break}}if(brace<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
function install(ctx,...names){for(const name of names)vm.runInContext(source(name),ctx)}
function context(extra={}){return vm.createContext({console,Math,Set,Map,Array,Object,Number,String,Boolean,...extra})}

const RANK_VALUE={A:1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,J:11,Q:12,K:13};
let uid=0;
function card(suit,rank,extra={}){return{uid:`zsmix-${++uid}`,suit,rank:String(rank),owner:'player',originOwner:'player',named:false,name:'순수 카드',tag:null,themeId:null,fromDiscard:false,age:0,enteredMeldToken:null,recoveredToken:null,recoverReturnOverrideToken:null,recoverReturnTargets:null,blockedUntilTurn:null,flexSuitOffSuit:false,...extra}}

new Function(script);

// 1) A ZERO-SIGHT target can be operated on by ordinary and future POINT-BLANK identity cards.
{
  const mixedMeld={type:'RUN',cards:[card('C','4'),card('C','5'),card('C','6',{themeId:'point-blank',name:'POINT-BLANK placeholder identity'})],chain:0};
  const player={melds:[mixedMeld]},enemy={melds:[]};
  const state={turnNo:14,turnToken:140,player,enemy};
  const events=[];
  const ctx=context({state});
  ctx.sideObj=w=>w==='player'?player:enemy;
  ctx.meldsOf=w=>ctx.sideObj(w).melds;
  ctx.emitEffectEvent=(event,payload={})=>{const packet={event,turnNo:state.turnNo,turnToken:state.turnToken,...payload};events.push(packet);return packet};
  ctx.log=()=>{};
  install(ctx,'meldOwnerSide','ensureMeldThemeMeta','isZeroSightTarget','zeroSightTargetActors','zeroSightTargetMeld','emitZeroSightTargetChange','clearZeroSightTarget','setZeroSightTarget');
  ok(ctx.setZeroSightTarget('player',mixedMeld),'ZERO-SIGHT can target a meld containing ordinary and POINT-BLANK identity cards');
  events.length=0;
  const pure=card('C','7');
  ctx.emitZeroSightTargetChange('attach',mixedMeld,{actionActor:'player',cards:[pure]});
  ok(events.length===1&&events[0].event==='onTargetMeldChange'&&events[0].change==='attach','ordinary-card attach uses the shared target reaction event');
  ok(events[0].cards[0]===pure&&events[0].targetedBy.includes('player'),'ordinary card identity is preserved in the targeted-meld event packet');
  events.length=0;
  const pointBlank=card('C','8',{themeId:'point-blank',name:'future POINT-BLANK card'});
  ctx.emitZeroSightTargetChange('attach',mixedMeld,{actionActor:'player',cards:[pointBlank]});
  ok(events[0].cards[0].themeId==='point-blank'&&events[0].targetedBy.includes('player'),'POINT-BLANK identity does not suppress ZERO-SIGHT target reactions before 접전 implementation');
}

// 2) V-SIGNAL Encore recovery and ZERO-SIGHT target reactions coexist on the same mixed public meld.
{
  const encore=card('H','5',{named:true,name:'앙코르',tag:'vEncore',themeId:'v-signal',recoveredToken:210,encoreGrantToken:null,encoreReturnUsedToken:null});
  const sourceRun={type:'RUN',cards:[encore,card('H','6'),card('H','7'),card('H','8')],chain:1,createdToken:null,lastAttachToken:null};
  const targetSet={type:'SET',cards:[card('S','5'),card('D','5'),card('C','5')],chain:0,createdToken:null,lastAttachToken:null};
  const player={melds:[sourceRun],returnedSwitchThisTurn:false};
  const enemy={melds:[targetSet],returnedSwitchThisTurn:false};
  const state={turnNo:21,turnToken:210,player,enemy};
  const events=[];
  const ctx=context({state,RANK_VALUE});
  ctx.sideObj=w=>w==='player'?player:enemy;
  ctx.other=w=>w==='player'?'enemy':'player';
  ctx.meldsOf=w=>ctx.sideObj(w).melds;
  ctx.canSideReturn=()=>true;
  ctx.log=()=>{};
  ctx.emitEffectEvent=(event,payload={})=>{const packet={event,turnNo:state.turnNo,turnToken:state.turnToken,...payload};events.push(packet);return packet};
  install(ctx,'isJoker','isSuitFlexible','setValid','runSequenceOK','runValid','meldType','meldOwnerSide','ensureMeldThemeMeta','isZeroSightTarget','zeroSightTargetActors','zeroSightTargetMeld','emitZeroSightTargetChange','clearZeroSightTarget','setZeroSightTarget','emitRecoveryEvent','legalRecoveryReturnTargets','grantRecoveryReturnOverride','handleVSignalThemeEvent','recoveredCardCanReturn');
  ok(ctx.runValid(sourceRun.cards)&&ctx.setValid(targetSet.cards),'mixed Encore scenario uses legal ordinary RUN/SET geometry');
  ctx.setZeroSightTarget('player',sourceRun);
  events.length=0;
  const recoveryPacket=ctx.emitRecoveryEvent('player',encore,sourceRun,'player',{free:false,reason:'mixed-test'});
  ok(recoveryPacket.event==='onRecover'&&recoveryPacket.targetedBy.includes('player'),'recovery packet snapshots the ZERO-SIGHT target before any theme-specific reaction');
  ok(events.some(e=>e.event==='onTargetMeldChange'&&e.change==='recover'&&e.targetedBy.includes('player')),'the same V-SIGNAL recovery also emits the ZERO-SIGHT target-meld change');
  ok(ctx.handleVSignalThemeEvent(recoveryPacket)===true,'V-SIGNAL Encore still receives its return permission from the shared recovery packet');
  ok(encore.recoverReturnTargets.length===1&&encore.recoverReturnTargets[0]===targetSet,'Encore permission points to the ordinary non-target 3SET, not its ZERO-SIGHT source meld');
  ok(ctx.recoveredCardCanReturn(encore,210,targetSet)===true,'cross-theme target state does not break the same-turn Encore exception');
}

// 3) Retiring a targeted mixed SET preserves target snapshots while V-SIGNAL preservation can keep a POINT-BLANK identity card.
{
  const gather=card('D','4',{named:true,name:'전원 집합!',tag:'vGatherAll',themeId:'v-signal'});
  const ordinary=card('H','4',{named:true,name:'일반 네임드',tag:'heal2'});
  const pure=card('S','4');
  const pointBlank=card('C','4',{named:true,name:'POINT-BLANK 정체성 카드',tag:'pbFuture',themeId:'point-blank'});
  const meld={type:'SET',cards:[gather,ordinary,pure,pointBlank],chain:0};
  const player={hand:[],deck:[],spent:[],melds:[meld]};
  const enemy={hand:[],deck:[],spent:[],melds:[]};
  const state={turnNo:27,turnToken:270,player,enemy};
  const events=[];
  const ctx=context({state,RANK_VALUE});
  ctx.sideObj=w=>w==='player'?player:enemy;
  ctx.meldsOf=w=>ctx.sideObj(w).melds;
  ctx.emitEffectEvent=(event,payload={})=>{const packet={event,turnNo:state.turnNo,turnToken:state.turnToken,...payload};events.push(packet);return packet};
  ctx.log=()=>{};
  ctx.cardText=c=>`${c.rank}${c.suit}`;
  install(ctx,'isJoker','isSuitFlexible','setValid','runSequenceOK','runValid','meldType','meldOwnerSide','ensureMeldThemeMeta','isZeroSightTarget','zeroSightTargetActors','zeroSightTargetMeld','emitZeroSightTargetChange','clearZeroSightTarget','clearZeroSightTargetsOnMeld','setZeroSightTarget','retirePreservationOffer','retireMeld');
  ok(ctx.setValid(meld.cards),'targeted mixed retirement scenario is a legal 4SET');
  ctx.setZeroSightTarget('player',meld);
  const offer=ctx.retirePreservationOffer('player',meld,'burst');
  ok(offer?.source===gather&&offer.candidates.includes(pointBlank),'V-SIGNAL Gather All may preserve a POINT-BLANK identity card from the targeted SET');
  events.length=0;
  ctx.retireMeld('player',0,'ZERO-SIGHT 혼합 회귀',{preserveCards:[pointBlank],preserveLabel:'전원 집합!'});
  const retireEvent=events.find(e=>e.event==='onRetire');
  const targetChange=events.find(e=>e.event==='onTargetMeldChange'&&e.change==='retire');
  const clearEvent=events.find(e=>e.event==='onTargetClear');
  ok(retireEvent?.targetedBy?.includes('player'),'onRetire keeps the ZERO-SIGHT target-owner snapshot on a mixed-theme meld');
  ok(targetChange?.targetedBy?.includes('player')&&clearEvent?.actor==='player','target retirement reaction and clear both occur before the mixed meld disappears');
  ok(player.melds.length===0,'mixed targeted SET is physically removed after target events resolve');
  ok(player.hand.includes(pointBlank)&&pointBlank.themeId==='point-blank','V-SIGNAL preservation keeps the POINT-BLANK card identity intact in hand');
  ok(pointBlank.blockedUntilTurn===27,'cross-theme preserved card keeps the normal same-turn reuse lock');
  ok(player.spent.includes(gather)&&player.spent.includes(ordinary)&&player.spent.includes(pure),'all unpreserved mixed cards follow normal owner circulation');
  ok(ctx.zeroSightTargetActors(meld).length===0,'retired meld retains no stale ZERO-SIGHT target metadata');
}

const targetChangeSource=source('emitZeroSightTargetChange');
ok(!targetChangeSource.includes('themeId')&&!targetChangeSource.includes("'zero-sight'"),'shared target reactions remain card-theme agnostic');
const attachSource=source('attachCards');
ok(attachSource.includes("emitZeroSightTargetChange('attach',m,{actionActor:w,cards:[...cards]"),'real attach resolution routes every card group through the target-change event');

ok(road.includes('- [x] ZERO-SIGHT ↔ 일반/V-SIGNAL/POINT-BLANK 혼합 회귀 테스트'),'ROADMAP marks ZERO-SIGHT mixed regression complete');
ok(themeDoc.includes('- [x] ZERO-SIGHT ↔ 일반/V-SIGNAL/POINT-BLANK 혼합 회귀 테스트'),'canonical theme doc marks ZERO-SIGHT mixed regression complete');
ok(themeDoc.includes('- [x] V-SIGNAL ↔ 일반 카드 혼합 회귀 테스트'),'canonical theme doc is synchronized with the existing V-SIGNAL mixed regression');
ok(themeDoc.includes('- [x] 표적 조합 회수/이동/새 조합 생성 반응 이벤트 정리'),'canonical theme doc is synchronized with the existing ZERO-SIGHT target-event implementation');

console.log('ZERO-SIGHT mixed-theme interoperability regression passed.');

import {createStatusContext} from './helpers/status-fixture.mjs';
import fs from 'node:fs';
import vm from 'node:vm';

const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const themeDoc=fs.readFileSync(new URL('../docs/THEME_GROUPS.md',import.meta.url),'utf8');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let par=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')par++;else if(script[i]===')')par--;else if(script[i]==='{'&&par===0){brace=i;break}}if(brace<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
function install(ctx,...names){for(const name of names)vm.runInContext(source(name),ctx)}

new Function(script);
ok(script.includes("'PBH7':{slot:'H7',themeId:'point-blank',n:'엄폐 교대',t:'pbCoverSwap'"),'Cover Swap is a live POINT-BLANK H7 variant');
ok(script.includes('대체 대상이 없으면 보호막 12')&&script.includes('원래 효과는 계속 해결'),'Cover Swap text defines non-blocking shield fallback');

// onMeldMove explicitly declares that movement itself is combat-neutral while still forwarding target/clash metadata refresh.
{
  const state={turnNo:4,turnToken:44};
  const events=[],targetChanges=[],clashChanges=[];
  const sourceMeld={type:'RUN',cards:[],themeMeta:{zeroSight:{targetedBy:{player:true,enemy:false}},pointBlank:{clashBy:{player:true,enemy:false}}}};
  const targetMeld={type:'RUN',cards:[],themeMeta:{zeroSight:{targetedBy:{player:false,enemy:false}},pointBlank:{clashBy:{player:false,enemy:false}}}};
  const ctx=createStatusContext(script,{console,Object,Array,state});
  ctx.emitEffectEvent=(event,payload)=>{const p={event,...payload};events.push(p);return p};
  ctx.zeroSightTargetActors=m=>['player','enemy'].filter(w=>m?.themeMeta?.zeroSight?.targetedBy?.[w]);
  ctx.meldOwnerSide=m=>m===sourceMeld?'enemy':'player';
  ctx.emitZeroSightTargetChange=(change,m,payload)=>{targetChanges.push({change,m,...payload});return true};
  ctx.refreshPointBlankClashMeld=(m,payload)=>{clashChanges.push({m,...payload});return true};
  install(ctx,'emitMeldMoveEvent');
  const card={uid:'v1',owner:'player',themeId:'v-signal'};
  const packet=ctx.emitMeldMoveEvent('player',card,sourceMeld,targetMeld,{reason:'mixedMove'});
  ok(packet?.combatNeutral===true&&packet.powerDelta===0&&packet.returnsSwitch===false,'onMeldMove exposes explicit combat-neutral movement contract');
  ok(packet.sourceTargetedBy?.includes('player'),'movement packet preserves ZERO-SIGHT source-target snapshot');
  ok(targetChanges.some(x=>x.change==='moveOut'),'movement still notifies ZERO-SIGHT target metadata');
  ok(clashChanges.length===2,'movement refreshes POINT-BLANK clash state on both source and destination');
  ok(sourceMeld.themeMeta.zeroSight.targetedBy.player===true&&sourceMeld.themeMeta.pointBlank.clashBy.player===true,'ZERO-SIGHT target and POINT-BLANK clash metadata coexist through movement notification');
}

// Shared movement primitive changes meld contents/CHAIN only; SWITCH combat state stays untouched.
{
  const state={turnNo:9,turnToken:91,switchPower:47,switchTarget:'enemy',player:{returnedSwitchThisTurn:true},enemy:{returnedSwitchThisTurn:false}};
  const mk=(uid)=>({uid,owner:'player',group:'r',meldType:'RUN'});
  const moving=mk('move'),sourceMeld={type:'RUN',cards:[moving,mk('s2'),mk('s3'),mk('s4')],chain:3},targetMeld={type:'RUN',cards:[mk('t1'),mk('t2'),mk('t3')],chain:1};
  const movedEvents=[];
  const ctx=createStatusContext(script,{console,Object,Array,state});
  ctx.meldOwnerSide=m=>m===sourceMeld?'enemy':'player';ctx.sideObj=()=>({turnStarts:5});
  ctx.meldType=cards=>cards.length>=3&&cards.every(c=>c.group==='r')?'RUN':null;
  ctx.markSetCompletion=()=>{};ctx.emitMeldMoveEvent=(actor,card,src,dst,opts)=>{const p={actor,card,src,dst,...opts,combatNeutral:true,powerDelta:0,returnsSwitch:false};movedEvents.push(p);return p};
  install(ctx,'moveCardBetweenMelds');
  const before={power:state.switchPower,target:state.switchTarget,returned:state.player.returnedSwitchThisTurn,targetChain:targetMeld.chain};
  const result=ctx.moveCardBetweenMelds('player',moving,sourceMeld,targetMeld,{reason:'test'});
  ok(!!result&&sourceMeld.cards.length===3&&targetMeld.cards.length===4,'shared movement primitive moves exactly one card while preserving valid melds');
  ok(sourceMeld.chain===2&&targetMeld.chain===before.targetChain,'movement decrements source RUN CHAIN but never awards destination CHAIN progress');
  ok(state.switchPower===before.power&&state.switchTarget===before.target&&state.player.returnedSwitchThisTurn===before.returned,'movement primitive cannot alter SWITCH power, direction, or physical-return usage');
  ok(result.combatNeutral===true&&result.powerDelta===0&&result.returnsSwitch===false&&movedEvents.length===1,'movement result/event both remain combat-neutral');
}

const moveSrc=source('moveCardBetweenMelds'),emitMoveSrc=source('emitMeldMoveEvent'),extMove=source('moveExtortedCard');
ok(!moveSrc.includes('addSwitchPower')&&!moveSrc.includes('returnSwitch')&&!moveSrc.includes('chainDamage')&&!moveSrc.includes('retireMeld'),'shared movement helper contains no BURST/CHAIN-power/SWITCH/retire combat path');
ok(emitMoveSrc.includes('combatNeutral:true')&&emitMoveSrc.includes('powerDelta:0')&&emitMoveSrc.includes('returnsSwitch:false'),'movement event source locks the neutral contract');
ok(!extMove.includes('addSwitchPower')&&!extMove.includes('returnSwitch')&&!extMove.includes('chainDamage')&&!extMove.includes('retireMeld'),'existing Extortion movement also remains combat-neutral');

// Cover Swap can redirect a hostile direct target to another legal own card regardless of that card's theme.
{
  const state={turnToken:12};
  const cover={uid:'cover',owner:'player',themeId:'point-blank',tag:'pbCoverSwap',name:'엄폐 교대',coverSwapUsedToken:null};
  const target={uid:'plain',owner:'player',name:'일반 카드'};
  const alt={uid:'encore',owner:'player',themeId:'v-signal',name:'앙코르'};
  const meld={cards:[target,cover,alt],themeMeta:{pointBlank:{clashBy:{player:true,enemy:false}}}};
  const shields=[];
  const ctx=createStatusContext(script,{console,Object,Array,state});ctx.log=()=>{};ctx.cardText=c=>c.name||c.uid;ctx.addShield=(w,n)=>shields.push({w,n});
  install(ctx,'isPointBlankClash','pointBlankCoverSwapSource','pointBlankCoverSwapTarget');
  const r=ctx.pointBlankCoverSwapTarget('enemy',meld,target,[alt]);
  ok(r.redirected===true&&r.card===alt&&r.source===cover,'Cover Swap redirects hostile targeting to another legal own card');
  ok(alt.themeId==='v-signal','Cover Swap replacement is theme-agnostic and can use a V-SIGNAL card');
  ok(cover.coverSwapUsedToken===12,'Cover Swap records its once-per-turn use on the source card');
  const second=ctx.pointBlankCoverSwapTarget('enemy',meld,target,[alt]);
  ok(second.redirected===false&&second.fallback===false&&second.card===target,'Cover Swap cannot trigger twice in the same turn');
  state.turnToken=13;cover.coverSwapUsedToken=null;
  const fallback=ctx.pointBlankCoverSwapTarget('enemy',meld,target,[]);
  ok(fallback.fallback===true&&fallback.card===target,'no legal replacement keeps the original hostile target');
  ok(shields.some(x=>x.w==='player'&&x.n===3),'failed Cover Swap grants exactly 3 shield units = 12 shield');
  state.turnToken=14;cover.coverSwapUsedToken=null;
  const friendly=ctx.pointBlankCoverSwapTarget('player',meld,target,[alt]);
  ok(friendly.redirected===false&&friendly.fallback===false,'Cover Swap ignores non-hostile effects from the card owner');
}

const cutSrc=source('cutOppositeEnd');
ok(extMove.includes('insuranceBlocks(w,foe,om,c)')&&extMove.indexOf('insuranceBlocks(w,foe,om,c)')<extMove.indexOf('om.cards.splice'),'existing Insurance Agent/protect resolution still happens before Extortion movement');
ok(extMove.includes('pointBlankCoverSwapTarget')&&extMove.includes('extortionCandidates(w,m).filter'),'Extortion supplies only same-effect legal alternatives to Cover Swap');
ok(cutSrc.includes('insuranceBlocks(w,targetSide,m,cand)')&&cutSrc.includes('pointBlankCoverSwapTarget(w,m,cand,[])'),'Cut Line preserves protection first and uses shield fallback because its opposite-end target has no alternate legal target');

ok(road.includes('- [x] 이동 효과 전투 중립 원칙 잠금'),'ROADMAP marks movement combat-neutral rule complete');
ok(road.includes('- [x] 7♥ `엄폐 교대` 적대 대상 교체/fallback 구현'),'ROADMAP marks Cover Swap complete');
ok(road.includes('- [x] POINT-BLANK ↔ 일반/V-SIGNAL/ZERO-SIGHT 혼합 회귀 테스트'),'ROADMAP marks POINT-BLANK mixed regression complete');
ok(themeDoc.includes('- [x] 이동 효과는 이동 자체로 버스트/체인/스위치 반환을 발생시키지 않는 기본 원칙 검증'),'canonical POINT-BLANK checklist locks movement neutrality');
ok(themeDoc.includes('- [x] 접전에서 적대적 대상 교체/보호막 fallback 처리'),'canonical POINT-BLANK checklist locks hostile target replacement');
ok(themeDoc.includes('- [x] POINT-BLANK ↔ 일반/V-SIGNAL/ZERO-SIGHT 혼합 회귀 테스트'),'canonical POINT-BLANK checklist locks mixed-theme regression');

console.log('POINT-BLANK movement neutrality, Cover Swap, and mixed-theme regression passed.');

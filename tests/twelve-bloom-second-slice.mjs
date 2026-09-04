import fs from 'node:fs';
import vm from 'node:vm';

const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){
 const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);
 let p=0,b=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')p++;else if(script[i]===')')p--;else if(script[i]==='{'&&p===0){b=i;break}}
 if(b<0)throw new Error(`missing body ${name}`);let d=0;for(let i=b;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}
 throw new Error(`unterminated ${name}`);
}

new Function(script);
ok(script.includes("'onBloomActionEnd'"),'final bloom action event is part of shared vocabulary');

const cards=[
 ['TBCA','CA','달력 펼치기','tbCalendarSpread'],
 ['TBC3','C3','빈달 찾기','tbEmptyMonth'],
 ['TBC7','C7','윤달 표식','tbLeapMark'],
 ['TBH7','H7','푸른 띠','tbBlueRibbon'],
 ['TBD4','D4','건너는 새','tbCrossBird'],
 ['TBD8','D8','돌아오는 새','tbReturningBird']
];
for(const[id,slot,name,tag]of cards)ok(script.includes(`'${id}':{slot:'${slot}',themeId:'twelve-bloom',n:'${name}',t:'${tag}'`),`${id} definition is locked`);

const resolver=source('resolveEffects');
ok(resolver.includes("case'tbCalendarSpread'")&&resolver.includes('requestTwelveBloomCalendarSpread(w,c,cards,resume)'),'달력 펼치기 is resumable');
ok(resolver.includes("case'tbLeapMark'")&&resolver.includes('requestTwelveBloomLeapMarkChoice(w,c,cards,resume)'),'윤달 표식 is resumable');
ok(resolver.includes("case'tbCrossBird'")&&resolver.includes("reason:'twelveBloomCrossBird'"),'건너는 새 uses named combat-neutral move reason');
ok(source('requestTwelveBloomLeapMarkChoice').includes('shieldOnSeason:false'),'윤달 표식 does not inherit 윤달 매듭 shield');
ok(source('requestTwelveBloomLeapMarkChoice').includes('return requestZeroSightCycle'),'윤달 표식 falls back to free maintenance when no public K exists');

const end=source('endTwelveBloomAction');
ok(end.includes("emitEffectEvent('onBloomActionEnd'")&&end.includes('summary.choicePending'),'action end emits once and reports pending reactions');
ok(source('submitNewMeld').includes('whenEffectChoicesDrained'),'new meld waits for queued bloom reactions before RUMMY');
ok(source('attachCards').includes('whenEffectChoicesDrained'),'attach waits for queued bloom reactions before RUMMY');

{
 const state={pendingEffectChoice:{id:1},effectChoiceQueue:[],effectChoiceDrainCallbacks:[]};
 let fired=0;
 const ctx=vm.createContext({state,console});
 for(const name of ['effectChoiceWorkPending','whenEffectChoicesDrained','flushEffectChoiceDrainCallbacks'])vm.runInContext(source(name),ctx);
 ok(ctx.whenEffectChoicesDrained(()=>fired++)===true&&fired===0,'drain continuation queues while a choice is pending');
 state.pendingEffectChoice=null;
 ok(ctx.flushEffectChoiceDrainCallbacks()===true&&fired===1,'drain continuation fires only after all choices are gone');
}

{
 const events={draw:0,recover:0};
 const cross={uid:40,name:'건너는 새',tag:'tbCrossBird'};
 const blue={uid:70,name:'푸른 띠',tag:'tbBlueRibbon'};
 const ctx=vm.createContext({
  console,
  twelveBloomThemePublicCards:(w,tag)=>tag==='tbBlueRibbon'?[blue]:[],
  themeTurnGateUsed:()=>false,
  claimThemeTurnGate:()=>true,
  drawOne:()=>{events.draw++;return{}},
  addShield:()=>0,
  other:w=>w==='player'?'enemy':'player',
  sideObj:w=>({id:w}),
  applyOfficialStatus:()=>1,
  log:()=>{},
  twelveBloomActionMovedCardTo:()=>false,
  twelveBloomActionCardByTag:(packet,w,tag)=>tag==='tbCrossBird'?cross:null,
  twelveBloomActionHasMoveReason:(packet,reason,uid)=>reason==='twelveBloomCrossBird'&&uid===cross.uid,
  requestTwelveBloomFreeRecoverChoice:()=>{events.recover++;return true}
 });
 vm.runInContext(source('handleTwelveBloomThemeEvent'),ctx);
 ctx.handleTwelveBloomThemeEvent({event:'onBloomMatchChange',actor:'player',owner:'player',turnToken:12,newlyCompleted:['season:summer'],steps:[]});
 ok(events.draw===1,'건너는 새 draws once when its nested move completes a season');
 ctx.handleTwelveBloomThemeEvent({event:'onBloomMatchChange',actor:'player',owner:'player',turnToken:12,newlyCompleted:['picture:blueRibbon'],steps:[]});
 ok(events.recover===1,'푸른 띠 opens one optional free-recovery reaction');
}

{
 const events={bottom:0,move:0};
 const empty={uid:3,name:'빈달 찾기',tag:'tbEmptyMonth'};
 const returning={uid:8,name:'돌아오는 새',tag:'tbReturningBird'};
 const ctx=vm.createContext({
  console,
  twelveBloomActionCardByTag:(packet,w,tag)=>tag==='tbEmptyMonth'?packet.empty?empty:null:tag==='tbReturningBird'?packet.returning?returning:null:null,
  twelveBloomHasExactlyTwoMonthSeason:()=>true,
  themeTurnGateUsed:()=>false,
  claimThemeTurnGate:()=>true,
  requestScrapShiftDrawBottom:()=>{events.bottom++;return false},
  requestTwelveBloomMoveChoice:()=>{events.move++;return true},
  other:w=>w==='player'?'enemy':'player'
 });
 vm.runInContext(source('handleTwelveBloomThemeEvent'),ctx);
 ctx.handleTwelveBloomThemeEvent({event:'onBloomActionEnd',actor:'player',turnToken:20,action:'meldCreate',actionMeta:{},after:{player:{seasons:{}}},empty:true});
 ok(events.bottom===1,'빈달 찾기 resolves from the final action snapshot');
 ctx.handleTwelveBloomThemeEvent({event:'onBloomActionEnd',actor:'player',turnToken:21,action:'recover',actionMeta:{sourceSide:'enemy'},after:{player:{seasons:{}}},returning:true});
 ok(events.move===1,'돌아오는 새 reacts only after recovery from the opponent board');
}

const move=source('twelveBloomMoveCandidates');
ok(move.includes("target.type==='SET'&&(target.cards||[]).length>=3"),'combat-neutral move never leaves a four-card SET on board');
ok(source('moveCardBetweenMelds').includes('effectSourceUid:opts.effectSourceUid||null'),'nested move retains effect-source identity');
ok(source('recoverSpecificFromMeld').includes('sourceSide,targetSide:sourceSide'),'effect recovery retains source board side');

console.log('TWELVE-BLOOM second effect slice regression passed.');

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
const cards=[
 ['TBC10','C10','겨울 채집','tbWinterGather'],
 ['TBCQ','CQ','한 해 넘기기','tbYearTurn'],
 ['TBH3','H3','봄매듭','tbSpringKnot'],
 ['TBH5','H5','풀빛 띠','tbGreenRibbon'],
 ['TBH10','H10','계절 되감기','tbSeasonRewind'],
 ['TBD10','D10','새 셋','tbBirdTrio']
];
for(const[id,slot,name,tag]of cards)ok(script.includes(`'${id}':{slot:'${slot}',themeId:'twelve-bloom',n:'${name}',t:'${tag}'`),`${id} definition is locked`);

const resolver=source('resolveEffects');
ok(resolver.includes("case'tbSeasonRewind'")&&resolver.includes('requestTwelveBloomSeasonRewind(w,c,resume)'),'계절 되감기 is a resumable active effect');
ok(source('requestTwelveBloomSeasonRewind').includes('claimTwelveBloomMatchGate(w,key,state.turnToken)'),'breaking a season with rewind burns its same-turn completion gate');
ok(source('requestTwelveBloomSeasonRewind').includes('const key=`season:${group.key}`'),'rewind gate is scoped to the selected season only');

{
 const stats={drawBottom:[],protect:0,heal:0};
 const cardsByTag={tbWinterGather:[{uid:10,name:'겨울 채집'}],tbSpringKnot:[{uid:3,name:'봄매듭'}],tbGreenRibbon:[{uid:5,name:'풀빛 띠'}],tbBirdTrio:[{uid:100,name:'새 셋'}]};
 const ctx=vm.createContext({
  console,
  twelveBloomThemePublicCards:(w,tag)=>cardsByTag[tag]||[],
  themeTurnGateUsed:()=>false,
  claimThemeTurnGate:()=>true,
  drawOne:()=>null,
  addShield:()=>0,
  other:w=>w==='player'?'enemy':'player',
  sideObj:w=>({id:w}),
  applyOfficialStatus:()=>1,
  log:()=>{},
  twelveBloomActionMovedCardTo:()=>false,
  twelveBloomActionCardByTag:()=>null,
  twelveBloomActionHasMoveReason:()=>false,
  twelveBloomQueueReaction:fn=>{fn();return false},
  requestTwelveBloomDrawBottom:(w,source,n)=>{stats.drawBottom.push([source.name,n]);return false},
  requestTwelveBloomActionProtectChoice:()=>{stats.protect++;return false},
  heal:(w,n)=>{stats.heal+=n;return n},
  requestTwelveBloomFreeRecoverChoice:()=>false
 });
 vm.runInContext(source('handleTwelveBloomThemeEvent'),ctx);
 ctx.handleTwelveBloomThemeEvent({event:'onBloomMatchChange',actor:'player',owner:'player',turnToken:8,newlyCompleted:['season:winter','season:spring','picture:greenRibbon','picture:birdTrio'],actionMeta:{cards:[1]},steps:[]});
 ok(stats.drawBottom.some(x=>x[0]==='겨울 채집'&&x[1]===1),'겨울 채집 resolves draw 1 / bottom 1');
 ok(stats.drawBottom.some(x=>x[0]==='새 셋'&&x[1]===2),'새 셋 resolves draw 2 / bottom 1');
 ok(stats.protect===1,'봄매듭 opens one action-card protection reaction');
 ok(stats.heal===2,'풀빛 띠 heals 8 through recovery-unit scaling');
}

{
 const state={turn:'player',turnToken:12};
 const year={uid:12,name:'한 해 넘기기',tag:'tbYearTurn'};
 let cycle=0,queued=0;
 const ctx=vm.createContext({
  console,state,
  twelveBloomThemePublicCards:(w,tag)=>tag==='tbYearTurn'?[year]:[],
  themeTurnGateUsed:()=>false,
  claimThemeTurnGate:()=>true,
  twelveBloomMatchSnapshot:()=>({seasons:{spring:{complete:true},summer:{complete:false}}}),
  twelveBloomQueueReaction:fn=>{queued++;fn();return true},
  requestZeroSightCycle:()=>{cycle++;return true},
  log:()=>{}
 });
 vm.runInContext(source('handleTwelveBloomThemeEvent'),ctx);
 ok(ctx.handleTwelveBloomThemeEvent({event:'onRummy',actor:'player',turnToken:12})===true,'한 해 넘기기 reacts after RUMMY when a season is complete');
 ok(queued===1&&cycle===1,'한 해 넘기기 schedules exactly one free maintenance');
}

{
 const trigger=source('triggerRummy');
 ok(trigger.includes("effectChoiceWorkPending==='function'")&&trigger.includes('whenEffectChoicesDrained'),'RUMMY finalization waits for event-created choices');
 ok(trigger.indexOf("emitEffectEvent('onRummy'")<trigger.indexOf('effectChoiceWorkPending()'),'RUMMY emits post-refill reactions before checking choice drain');
}

{
 let claimed=null,recovered=0;
 const group={key:'spring',name:'봄맞춤',candidates:[{m:{},card:{uid:1},side:'player',month:1}]};
 const snapshots=[{seasons:{spring:{complete:true}}},{seasons:{spring:{complete:false}}}];
 const ctx=vm.createContext({
  console,
  state:{turn:'enemy',turnToken:30},
  twelveBloomSeasonRecoverGroups:()=>[group],
  twelveBloomMatchSnapshot:()=>snapshots.shift()||{seasons:{spring:{complete:false}}},
  recoverSpecificFromMeld:()=>{recovered++;return{uid:1}},
  claimTwelveBloomMatchGate:(w,key,token)=>{claimed=[w,key,token];return true},
  requestEffectChoice:()=>false,
  cardText:()=>'',log:()=>{}
 });
 vm.runInContext(source('requestTwelveBloomSeasonRewind'),ctx);
 const result=ctx.requestTwelveBloomSeasonRewind('enemy',{name:'계절 되감기'});
 ok(result===false&&recovered===1,'AI rewind resolves one legal recovery synchronously');
 ok(claimed?.[1]==='season:spring'&&claimed?.[2]===30,'rewind-broken spring is suppressed for the rest of the same turn');
}

{
 const fn=source('requestTwelveBloomActionProtectChoice');
 ok(!fn.includes('cardFixedActive'),'봄매듭 may protect an action card even if it is fixed');
 ok(fn.includes("applyOfficialStatus('card',c,'protect',1"),'봄매듭 applies official card protect 1');
}

console.log('TWELVE-BLOOM third effect slice regression passed.');

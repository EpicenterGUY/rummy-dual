import fs from 'node:fs';
import vm from 'node:vm';

const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let p=0,b=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')p++;else if(script[i]===')')p--;else if(script[i]==='{'&&p===0){b=i;break}}if(b<0)throw new Error(`missing body ${name}`);let d=0;for(let i=b;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
function declaration(name,next){const a=script.indexOf(`const ${name}=`),b=script.indexOf(next,a);if(a<0||b<0)throw new Error(`missing declaration ${name}`);return script.slice(a,b)}
const card=(uid,suit,rank,owner='player')=>({uid,suit,rank,slot:suit+rank,owner,twelveBloomLeapMonth:null,twelveBloomLeapOwner:null});
const meld=cards=>({type:'RUN',cards:[...cards],chain:0,status:{},themeMeta:{}});

function makeCtx(){
 const state={turnNo:1,turnToken:10,twelveBloomActionTx:null,player:{hand:[],deck:[],spent:[],melds:[],twelveBloomMatchGates:{}},enemy:{hand:[],deck:[],spent:[],melds:[],twelveBloomMatchGates:{}},discard:[]};
 const events=[];
 const ctx=vm.createContext({console,Object,Array,Set,Map,Number,String,Boolean,Math,state});
 vm.runInContext(declaration('EFFECT_EVENTS','\nconst EFFECT_ACTIONS='),ctx);
 vm.runInContext(declaration('TWELVE_BLOOM_MONTH_BY_RANK','\nconst TWELVE_BLOOM_SEASON_DEFS='),ctx);
 vm.runInContext(declaration('TWELVE_BLOOM_SEASON_DEFS','\nconst TWELVE_BLOOM_PICTURE_DEFS='),ctx);
 vm.runInContext(declaration('TWELVE_BLOOM_PICTURE_DEFS','\nconst THEME_GROUPS='),ctx);
 ctx.effectEventSubscribers=new Set([packet=>events.push(packet)]);
 for(const name of [
  'sideObj','other','meldsOf','subscribeEffectEvent','emitEffectEvent',
  'twelveBloomAllKnownCards','twelveBloomPublicEntries','twelveBloomPublicCards','twelveBloomIsPublicCard',
  'twelveBloomCardMonth','twelveBloomExactSlot','twelveBloomMatchSnapshotFromCards','twelveBloomMatchSnapshot',
  'twelveBloomMatchDiff','captureTwelveBloomSnapshots','diffTwelveBloomSnapshots',
  'twelveBloomMatchGateState','twelveBloomMatchGateUsed','claimTwelveBloomMatchGate',
  'beginTwelveBloomAction','endTwelveBloomAction','cancelTwelveBloomAction'
 ])vm.runInContext(source(name),ctx);
 const matchEvents=()=>events.filter(e=>e.event==='onBloomMatchChange');
 const actionEvents=()=>events.filter(e=>e.event==='onBloomActionEnd');
 return{ctx,state,events,matchEvents,actionEvents}
}

new Function(script);
ok(script.includes("'onBloomMatchChange'"),'shared effect-event vocabulary contains onBloomMatchChange');
ok(source('endTwelveBloomAction').includes("claimTwelveBloomMatchGate(owner,key,tx.turnToken)"),'final event filters repeated newly-completed matches through the owner+match turn gate');
ok(source('endTwelveBloomAction').includes("combatNeutral:true,powerDelta:0,returnsSwitch:false"),'match-change event is explicitly combat neutral');

{
 const {ctx,state,events,matchEvents,actionEvents}=makeCtx();
 const a=card(1,'C','A'),two=card(2,'D','2'),three=card(3,'S','3');
 state.player.melds=[meld([a,two])];
 const tx=ctx.beginTwelveBloomAction('player','attach',{test:'normal'});
 state.player.melds[0].cards.push(three);
 const result=ctx.endTwelveBloomAction(tx,{done:true});
 ok(matchEvents().length===1,'normal final completion emits exactly one derived match event');
 ok(actionEvents().length===1,'normal public action also emits exactly one final action-settled event');
 ok(matchEvents()[0].owner==='player','derived event identifies match owner independently from board controller');
 ok(matchEvents()[0].newlyCompleted.includes('season:spring'),'normal A/2/3 completion reports spring newly completed');
 ok(result.changes.find(x=>x.owner==='player').newlyCompleted.includes('season:spring'),'transaction summary preserves eligible completion');
 ok(matchEvents()[0].powerDelta===0&&matchEvents()[0].returnsSwitch===false,'normal completion cannot add power or move SWITCH by itself');
}

{
 const {ctx,state,events,matchEvents,actionEvents}=makeCtx();
 const a=card(10,'C','A'),two=card(11,'D','2'),three=card(12,'S','3');
 state.player.melds=[meld([a,two])];
 const outer=ctx.beginTwelveBloomAction('player','attach',{test:'transient'});
 state.player.melds[0].cards.push(three); // transiently complete
 const nested=ctx.beginTwelveBloomAction('player','retireMeld',{reason:'burst'});
 state.player.melds=[]; // BURST retirement leaves final board incomplete
 const pending=ctx.endTwelveBloomAction(nested,{retired:true});
 ok(pending.pending===true&&events.length===0,'nested retirement cannot emit before the outer action finishes');
 const final=ctx.endTwelveBloomAction(outer,{done:true});
 ok(matchEvents().length===0,'transient completion that disappears before final action state emits no completion event');
 ok(actionEvents().length===1,'transient action still emits one final action-settled event');
 ok(final.changes.every(x=>!x.newlyCompleted.length),'final diff contains no false completion after transient BURST state');
}

{
 const {ctx,state,events,matchEvents,actionEvents}=makeCtx();
 const a=card(20,'C','A'),two=card(21,'D','2'),three=card(22,'S','3');
 state.player.melds=[meld([a,two])];
 const outer=ctx.beginTwelveBloomAction('player','attach');
 const nested=ctx.beginTwelveBloomAction('player','meldMove');
 state.player.melds[0].cards.push(three);
 ctx.endTwelveBloomAction(nested);
 ok(events.length===0,'nested public movement defers matching until outer action completion');
 ctx.endTwelveBloomAction(outer);
 ok(matchEvents().length===1&&matchEvents()[0].newlyCompleted.includes('season:spring'),'outer action emits one consolidated completion after nested movement');
 ok(actionEvents().length===1,'outer action emits one consolidated action-settled event after nested movement');
}

{
 const {ctx,state,events,matchEvents,actionEvents}=makeCtx();
 const a=card(30,'C','A'),two=card(31,'D','2'),three=card(32,'S','3');
 state.player.melds=[meld([a,two])];
 let tx=ctx.beginTwelveBloomAction('player','attach');
 state.player.melds[0].cards.push(three);
 ctx.endTwelveBloomAction(tx);
 ok(matchEvents().length===1,'first completion of the turn emits');

 tx=ctx.beginTwelveBloomAction('player','recover');
 state.player.melds[0].cards=state.player.melds[0].cards.filter(c=>c.uid!==three.uid);
 ctx.endTwelveBloomAction(tx);
 ok(matchEvents().length===2&&matchEvents().at(-1).broken.includes('season:spring'),'breaking the completed match is still observable');

 tx=ctx.beginTwelveBloomAction('player','attach');
 state.player.melds[0].cards.push(three);
 const suppressed=ctx.endTwelveBloomAction(tx);
 ok(matchEvents().length===2,'same-turn rebuild does not emit a second completion reward event');
 const playerChange=suppressed.changes.find(x=>x.owner==='player');
 ok(playerChange.rawNewlyCompleted.includes('season:spring')&&playerChange.suppressedNewlyCompleted.includes('season:spring'),'same-turn rebuild remains visible in diagnostics while reward completion is suppressed');

 state.turnToken=11;
 tx=ctx.beginTwelveBloomAction('player','recover');
 state.player.melds[0].cards=state.player.melds[0].cards.filter(c=>c.uid!==three.uid);
 ctx.endTwelveBloomAction(tx);
 tx=ctx.beginTwelveBloomAction('player','attach');
 state.player.melds[0].cards.push(three);
 ctx.endTwelveBloomAction(tx);
 ok(matchEvents().at(-1).newlyCompleted.includes('season:spring'),'the same match becomes eligible again on a later turn token');
}

for(const [fnName,needle] of [
 ['submitNewMeld',"beginTwelveBloomAction(w,'meldCreate'"],
 ['attachCards',"beginTwelveBloomAction(w,'attach'"],
 ['moveCardBetweenMelds',"beginTwelveBloomAction(actor,'meldMove'"],
 ['dismantleScrapShiftPart',"beginTwelveBloomAction(owner,'dismantle'"],
 ['recoverSpecificFromMeld',"beginTwelveBloomAction(w,'recover'"],
 ['playerRecover',"beginTwelveBloomAction('player','recover'"],
 ['executeRecoverAI',"beginTwelveBloomAction(w,'recover'"],
 ['retireMeld',"beginTwelveBloomAction(owner,'retireMeld'"]
])ok(source(fnName).includes(needle),`${fnName} participates in the final-state TWELVE-BLOOM transaction`);

const attach=source('attachCards');
ok(attach.indexOf('endTwelveBloomAction(bloomTx')>attach.indexOf("retireMeld(targetSide,currentIndex,'버스트 후 4장 세트 자동 정리"),'BURST attach finalizes bloom matching only after automatic SET retirement');

console.log('TWELVE-BLOOM final match-change event regression passed.');

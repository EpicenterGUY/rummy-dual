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
 ['TBD6','D6','날갯짓','tbWingbeat'],
 ['TBDQ','DQ','철새 길','tbMigratoryPath'],
 ['TBSA','SA','첫빛','tbFirstLight'],
 ['TBS3','S3','비치는 틈','tbGleamingGap'],
 ['TBS8','S8','큰빛','tbGreatLight'],
 ['TBSQ','SQ','빛 셋','tbLightTrio']
];
for(const[id,slot,name,tag]of cards)ok(script.includes(`'${id}':{slot:'${slot}',themeId:'twelve-bloom',n:'${name}',t:'${tag}'`),`${id} definition is locked`);

{
 const ctx=vm.createContext({console});
 vm.runInContext(source('twelveBloomCrossBoardMoveMeta'),ctx);
 ok(ctx.twelveBloomCrossBoardMoveMeta({actionMeta:{sourceSide:'player',targetSide:'enemy'}})?.targetSide==='enemy','날갯짓 detects own/opponent meld crossing');
 ok(ctx.twelveBloomCrossBoardMoveMeta({actionMeta:{sourceSide:'player',targetSide:'player'}})===null,'same-board movement does not count for 날갯짓');
}

{
 const own={uid:1,owner:'player'},foeCard={uid:2,owner:'enemy'},foeMeld={type:'RUN',cards:[own,foeCard]};
 const ctx=vm.createContext({console,other:w=>w==='player'?'enemy':'player',twelveBloomPublicEntries:()=>[{card:own,meld:foeMeld,side:'enemy'}],meldsOf:()=>[foeMeld]});
 vm.runInContext(source('twelveBloomActionEnteredOpponentCards'),ctx);
 vm.runInContext(source('twelveBloomOpponentMeldUsedByAction'),ctx);
 const packet={action:'attach',actionMeta:{targetSide:'enemy',targetIndex:0,cards:[1]},steps:[]};
 ok(ctx.twelveBloomActionEnteredOpponentCards(packet,'player')[0]===own,'철새 길 identifies the owned card that entered the opponent meld');
 ok(ctx.twelveBloomOpponentMeldUsedByAction(packet,'player')===foeMeld,'비치는 틈 identifies the opponent meld used by the action');
}

{
 const stats={cycle:0,pathProtect:0,sealChoice:0,gap:0,shield:0,greatProtect:0};
 const cardsByTag={
  tbWingbeat:[{uid:6,name:'날갯짓'}],
  tbMigratoryPath:[{uid:12,name:'철새 길'}],
  tbFirstLight:[{uid:1,name:'첫빛'}],
  tbGleamingGap:[{uid:3,name:'비치는 틈'}],
  tbGreatLight:[{uid:8,name:'큰빛'}]
 };
 const foeMeld={type:'RUN',cards:[{uid:91}]};
 const entered={uid:44,owner:'player'};
 const ctx=vm.createContext({
  console,state:{turn:'enemy'},
  twelveBloomThemePublicCards:(w,tag)=>cardsByTag[tag]||[],
  themeTurnGateUsed:()=>false,claimThemeTurnGate:()=>true,
  twelveBloomActionEnteredOpponentCards:()=>[entered],
  twelveBloomOpponentMeldUsedByAction:()=>foeMeld,
  twelveBloomCrossBoardMoveMeta:()=>({sourceSide:'player',targetSide:'enemy'}),
  requestTwelveBloomProtectChoice:()=>{stats.pathProtect++;return false},
  requestTwelveBloomOpponentSealChoice:()=>{stats.sealChoice++;return false},
  requestTwelveBloomGleamingGap:()=>{stats.gap++;return false},
  requestTwelveBloomPublicProtectChoice:()=>{stats.greatProtect++;return false},
  requestZeroSightCycle:()=>{stats.cycle++;return false},
  twelveBloomQueueReaction:fn=>{fn();return false},
  meldsOf:w=>w==='enemy'?[foeMeld]:[],
  other:w=>w==='player'?'enemy':'player',
  addShield:(w,n)=>{stats.shield+=n;return n},
  drawOne:()=>null,heal:()=>0,applyOfficialStatus:()=>1,sideObj:w=>({id:w}),log:()=>{},
  twelveBloomActionMovedCardTo:()=>false,twelveBloomActionCardByTag:()=>null,twelveBloomActionHasMoveReason:()=>false,
  requestTwelveBloomDrawBottom:()=>false,requestTwelveBloomActionProtectChoice:()=>false,requestTwelveBloomFreeRecoverChoice:()=>false,
  twelveBloomHasExactlyTwoMonthSeason:()=>false,requestScrapShiftDrawBottom:()=>false
 });
 vm.runInContext(source('handleTwelveBloomThemeEvent'),ctx);
 ctx.handleTwelveBloomThemeEvent({event:'onBloomMatchChange',actor:'player',owner:'player',turnToken:7,newlyCompleted:['season:spring','picture:lightTrio'],actionMeta:{},steps:[]});
 ok(stats.pathProtect===1,'철새 길 protects one entered card on the first qualifying season completion');
 ok(stats.sealChoice===1,'첫빛 opens one optional opponent-meld seal choice');
 ok(stats.gap===1,'비치는 틈 reacts to the opponent meld used by the completing action');
 ok(stats.shield===2&&stats.greatProtect===1,'큰빛 grants shield 8 and one public-card protect choice');
 ctx.handleTwelveBloomThemeEvent({event:'onBloomActionEnd',actor:'player',turnToken:7,action:'meldMove',actionMeta:{sourceSide:'player',targetSide:'enemy'},steps:[]});
 ok(stats.cycle===1,'날갯짓 grants exactly one free hand maintenance on first cross-board move');
}

{
 const foeMeld={type:'SET',cards:[{uid:9}],status:{seal:1}};
 let protectedCount=0;
 const ctx=vm.createContext({
  console,officialStatusValue:()=>1,twelveBloomOpponentMeldUsedByAction:()=>foeMeld,
  requestTwelveBloomPublicProtectChoice:()=>{protectedCount++;return false},
  applyOfficialStatus:()=>1,log:()=>{}
 });
 vm.runInContext(source('requestTwelveBloomGleamingGap'),ctx);
 ctx.requestTwelveBloomGleamingGap('player',{name:'비치는 틈'},{});
 ok(protectedCount===1,'비치는 틈 uses card protect instead when the used opponent meld is already sealed');
}

{
 const first=source('requestTwelveBloomOpponentSealChoice');
 ok(first.includes('allowSkip:true')&&first.includes("applyOfficialStatus('meld',m,'seal',1"),'첫빛 seal is optional for the human and uses official meld seal 1');
 const big=source('handleTwelveBloomThemeEvent');
 ok(big.includes("keys.includes('picture:lightTrio')")&&big.includes('addShield(w,2)'),'큰빛 is tied to exact light-trio completion and shield 8');
}

{
 const helper=source('twelveBloomLightTrioCompleteBeforeAction');
 ok(helper.includes("tx.before?.[w]?.pictures?.lightTrio?.complete"),'빛 셋 checks the pre-action snapshot rather than same-action completion');
 const resolver=source('resolveEffects');
 ok(resolver.includes("tbLightTrioChecked")&&resolver.includes("twelveBloomThemePublicCards(w,'tbLightTrio')"),'빛 셋 scans the returning meld for the staged Q♠ passive');
 ok(resolver.includes("claimThemeTurnGate(light,'tbLightTrio'")&&resolver.includes('fx.bonus+=14'),'빛 셋 adds +14 at most once per turn');
 ok(!resolver.slice(resolver.indexOf('tbLightTrioChecked'),resolver.indexOf('if(!fx.effectCards)')).includes('returnSwitch('),'빛 셋 modifies return power only and creates no extra SWITCH return');
}

console.log('TWELVE-BLOOM fourth/final effect slice regression passed.');

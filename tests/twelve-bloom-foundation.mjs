import fs from 'node:fs';
import vm from 'node:vm';

const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let p=0,b=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')p++;else if(script[i]===')')p--;else if(script[i]==='{'&&p===0){b=i;break}}if(b<0)throw new Error(`missing body ${name}`);let d=0;for(let i=b;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
function declaration(name,next){const a=script.indexOf(`const ${name}=`);if(a<0)throw new Error(`missing ${name}`);const b=script.indexOf(next,a);if(b<0)throw new Error(`missing end ${name}`);return script.slice(a,b)}
function card(uid,suit,rank,owner='player',extra={}){return{uid,suit,rank,slot:suit==='J'?'J':suit+rank,owner,name:extra.name||'테스트 카드',themeId:extra.themeId||null,twelveBloomLeapMonth:null,twelveBloomLeapOwner:null,handPrep:{turns:0,exitTurns:0,exitTurnToken:null,exitOwner:null},...extra}}
function meld(cards,type='RUN'){return{type,cards:[...cards],chain:0,status:{},themeMeta:{}}}
function makeCtx(){
 const state={turnToken:10,turnNo:3,player:{hand:[],deck:[],spent:[],melds:[]},enemy:{hand:[],deck:[],spent:[],melds:[]},discard:[]};
 const logs=[];
 const ctx=vm.createContext({console,Object,Array,Set,Map,Number,String,Boolean,Math,state,log:(msg)=>logs.push(msg)});
 vm.runInContext(declaration('TWELVE_BLOOM_MONTH_BY_RANK','\nconst TWELVE_BLOOM_SEASON_DEFS='),ctx);
 vm.runInContext(declaration('TWELVE_BLOOM_SEASON_DEFS','\nconst TWELVE_BLOOM_PICTURE_DEFS='),ctx);
 vm.runInContext(declaration('TWELVE_BLOOM_PICTURE_DEFS','\nconst THEME_GROUPS='),ctx);
 for(const name of ['sideObj','other','meldsOf','twelveBloomAllKnownCards','twelveBloomPublicEntries','twelveBloomPublicCards','twelveBloomIsPublicCard','twelveBloomCardMonth','twelveBloomExactSlot','twelveBloomMatchSnapshot','twelveBloomMatchDiff','captureTwelveBloomSnapshots','diffTwelveBloomSnapshots','twelveBloomMatchGateState','twelveBloomMatchGateUsed','claimTwelveBloomMatchGate','clearTwelveBloomLeapMonth','setTwelveBloomLeapMonth','ensureHandPreparation','resetHandPreparation','enterHand'])vm.runInContext(source(name),ctx);
 return{ctx,state,logs}
}

new Function(script);
ok(script.includes('twelveBloomLeapMonth:null,twelveBloomLeapOwner:null'),'new card state initializes leap-month metadata');
ok(!script.includes("themeId:'twelve-bloom'")&&!script.includes("'twelve-bloom':Object.freeze"),'foundation remains non-live and absent from runtime theme registries');

{
 const {ctx,state}=makeCtx();
 const a=card(1,'C','A'),two=card(2,'D','2', 'player',{themeId:'zero-sight'}),three=card(3,'H','3');
 state.player.melds=[meld([a,two])];
 state.enemy.melds=[meld([three], 'SET')];
 const snap=ctx.twelveBloomMatchSnapshot('player');
 ok(snap.seasons.spring.complete===true,'owned public cards across both boards can complete spring');
 ok(snap.months.join(',')==='1,2,3','A/2/3 map to months 1/2/3 regardless of theme identity or board controller');
 ok(snap.cardUids.length===3,'only owned public cards are included as material');
 const enemySnap=ctx.twelveBloomMatchSnapshot('enemy');
 ok(enemySnap.cardUids.length===0,'opponent-owned material is evaluated independently');
}

{
 const {ctx,state}=makeCtx();
 const ha=card(10,'H','A'),h2=card(11,'H','2'),h3=card(12,'H','3'),joker=card(13,'J','J1');
 state.player.melds=[meld([ha,h2,h3,joker],'SET')];
 const snap=ctx.twelveBloomMatchSnapshot('player');
 ok(snap.pictures.redRibbon.complete===true,'exact A♥/2♥/3♥ completes red ribbon');
 ok(!snap.months.includes(undefined)&&snap.months.length===3,'Joker contributes no month');
 ok(!snap.cardUids.includes('missing'),'snapshot remains ordinary-card based rather than theme-name based');
}

{
 const {ctx,state}=makeCtx();
 const a=card(20,'C','A'),two=card(21,'S','2'),k1=card(22,'C','K'),k2=card(23,'H','K');
 state.player.melds=[meld([a,two,k1,k2])];
 let before=ctx.twelveBloomMatchSnapshot('player');
 ok(before.seasons.spring.complete===false,'public K has no month before explicit leap designation');
 const result=ctx.setTwelveBloomLeapMonth('player',k1,3,{silent:true});
 ok(!!result&&result.diff.newlyCompleted.includes('season:spring'),'assigning K to missing month can newly complete a season');
 ok(k1.twelveBloomLeapMonth===3&&k1.twelveBloomLeapOwner==='player','designated K stores owner and chosen month');
 const second=ctx.setTwelveBloomLeapMonth('player',k2,6,{silent:true});
 ok(!!second&&k1.twelveBloomLeapMonth===null&&k1.twelveBloomLeapOwner===null,'designating a second K atomically clears the old leap card');
 ok(k2.twelveBloomLeapMonth===6,'new leap designation replaces old owner designation');
 ok(ctx.setTwelveBloomLeapMonth('player',card(24,'C','Q'),4,{silent:true})===null,'non-K cards cannot become leap month');
 ok(ctx.setTwelveBloomLeapMonth('player',k2,13,{silent:true})===null,'leap month is limited to months 1-12');
}

{
 const {ctx,state}=makeCtx();
 const ha=card(30,'H','A'),h2=card(31,'H','2'),kh=card(32,'H','K');
 state.player.melds=[meld([ha,h2,kh])];
 ctx.setTwelveBloomLeapMonth('player',kh,3,{silent:true});
 const snap=ctx.twelveBloomMatchSnapshot('player');
 ok(snap.seasons.spring.complete===true,'leap month may fill a missing season month');
 ok(snap.pictures.redRibbon.complete===false,'leap K cannot counterfeit exact H3 picture slot');
}

{
 const {ctx,state}=makeCtx();
 const a=card(40,'C','A'),two=card(41,'D','2'),three=card(42,'S','3');
 state.player.melds=[meld([a,two])];
 const before=ctx.captureTwelveBloomSnapshots();
 state.enemy.melds=[meld([three])];
 const completed=ctx.diffTwelveBloomSnapshots(before);
 ok(completed.player.newlyCompleted.includes('season:spring'),'before/after snapshot diff reports newly completed matches');
 const beforeBreak=ctx.captureTwelveBloomSnapshots();
 state.enemy.melds=[];
 const broken=ctx.diffTwelveBloomSnapshots(beforeBreak);
 ok(broken.player.broken.includes('season:spring'),'before/after snapshot diff reports broken matches');
 ok(!broken.enemy.newlyCompleted.length&&!broken.enemy.broken.length,'unaffected owner diff stays empty');
}

{
 const {ctx,state}=makeCtx();
 ok(ctx.claimTwelveBloomMatchGate('player','season:spring',10)===true,'first owner+match reward gate claim succeeds');
 ok(ctx.twelveBloomMatchGateUsed('player','season:spring',10)===true,'claimed match is visible for current turn token');
 ok(ctx.claimTwelveBloomMatchGate('player','season:spring',10)===false,'same match cannot be rewarded twice in one turn');
 state.turnToken=11;
 ok(ctx.claimTwelveBloomMatchGate('player','season:spring',11)===true,'same match becomes rewardable on a later turn token');
}

{
 const {ctx,state}=makeCtx();
 const k=card(50,'S','K');
 state.player.melds=[meld([k])];
 ctx.setTwelveBloomLeapMonth('player',k,8,{silent:true});
 state.player.melds[0].cards=[];
 ctx.enterHand('player',k);
 ok(k.twelveBloomLeapMonth===null&&k.twelveBloomLeapOwner===null,'entering hand clears leap-month designation defensively');
}

for(const [name,needle] of [
 ['pushDiscard',"clearTwelveBloomLeapMonth(c,'공용 버림패'"],
 ['bottomSpecificHandCard',"clearTwelveBloomLeapMonth(chosen,'개인 덱'"],
 ['performMaintenance',"clearTwelveBloomLeapMonth(c,'정비·개인 덱'"],
 ['recycleIfNeeded',"clearTwelveBloomLeapMonth(c,'개인 덱 재순환'"],
 ['fullRecirculation',"clearTwelveBloomLeapMonth(c,'전체 재순환'"],
 ['retireMeld',"clearTwelveBloomLeapMonth(c,'조합 정리'"],
 ['dismantleScrapShiftPart',"clearTwelveBloomLeapMonth(c,'해체·소모패'"],
 ['spendPointBlankMeldCard',"clearTwelveBloomLeapMonth(c,'효과 소모'"],
 ['insuranceBlocks',"clearTwelveBloomLeapMonth(ins,'간섭 대체 소모'"],
 ['cutOppositeEnd',"clearTwelveBloomLeapMonth(cand,'효과 소모'"]
])ok(source(name).includes(needle),`${name} clears leap designation on public/active zone exit`);

console.log('TWELVE-BLOOM match/leap-month foundation regression passed.');

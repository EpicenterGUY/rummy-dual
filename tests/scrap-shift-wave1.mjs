import fs from 'node:fs';
import vm from 'node:vm';

const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const themeDoc=fs.readFileSync(new URL('../docs/THEME_GROUPS.md',import.meta.url),'utf8');
const poolDoc=fs.readFileSync(new URL('../docs/THEME_FULL_POOL_PLAN.md',import.meta.url),'utf8');

function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let par=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')par++;else if(script[i]===')')par--;else if(script[i]==='{'&&par===0){brace=i;break}}if(brace<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
function context(extra={}){return vm.createContext({console,Set,Map,Array,Object,Number,String,Boolean,Math,...extra})}
function install(ctx,...names){for(const n of names)vm.runInContext(source(n),ctx)}

new Function(script);

const wave1=[
 ['SSDA','DA','부품 라벨','ssPartLabel'],
 ['SSC2','C2','컨베이어','ssConveyor'],
 ['SSH4','H4','수리 키트','ssRepairKit'],
 ['SSSA','SA','분해 드라이버','ssDismantleDriver']
];
for(const [id,slot,name,tag] of wave1){
 ok(script.includes(`'${id}':{slot:'${slot}',themeId:'scrap-shift',n:'${name}',t:'${tag}'`),`${name} is defined as a SCRAP-SHIFT development card`);
}
ok(script.includes("'scrap-shift':Object.freeze({id:'scrap-shift',displayName:'SCRAP-SHIFT',short:'부품 순환'")&&script.includes("themeId:'scrap-shift',live:true"),'SCRAP-SHIFT has a live build profile');
ok(html.includes('data-codex-filter="theme:scrap-shift">SCRAP-SHIFT</button>'),'SCRAP-SHIFT codex tab exists for DEV visibility');
const resolver=source('resolveEffects');
for(const tag of wave1.map(x=>x[3]))ok(resolver.includes(`case'${tag}'`),`${tag} has a live resolver branch`);

{
 const chosen=[];let cycled=0;
 const sourceCard={uid:1,owner:'enemy',name:'부품 라벨',tag:'ssPartLabel'};
 const a={uid:2,owner:'enemy',name:'일반 A',scrapShiftPart:false};
 const b={uid:3,owner:'enemy',name:'다른 테마 B',themeId:'v-signal',scrapShiftPart:false};
 const meld={type:'SET',cards:[sourceCard,a,b]};
 const state={turn:'enemy',turnToken:1};
 const ctx=context({state,isScrapShiftPart:c=>!!c.scrapShiftPart,setScrapShiftPart:(w,c)=>{c.scrapShiftPart=true;chosen.push(c);return true},requestZeroSightCycle:()=>{cycled++;return false},zeroSightCycleCandidates:()=>[],cardText:c=>c.name});
 install(ctx,'requestScrapShiftPartLabelChoice');
 ok(ctx.requestScrapShiftPartLabelChoice('enemy',sourceCard,meld,[sourceCard,a,b])===false,'part label resolves synchronously for AI');
 ok(chosen.length===1&&chosen[0]===a&&a.scrapShiftPart===true,'part label can designate an ordinary card instead of requiring its own theme');
 ok(cycled===1,'part label follows designation with one free maintenance cycle');
}

{
 const part={uid:9,owner:'enemy',name:'일반 부품',scrapShiftPart:true};
 const x={uid:10,owner:'enemy'},y={uid:11,owner:'enemy'},z={uid:12,owner:'enemy'};
 const sourceMeld={type:'RUN',cards:[x,y,z,part]},targetMeld={type:'RUN',cards:[{uid:20},{uid:21},{uid:22}]};
 const enemy={melds:[sourceMeld]},player={melds:[targetMeld]};
 const state={turn:'enemy',turnToken:2};let moved=null;
 const ctx=context({state,other:w=>w==='enemy'?'player':'enemy',meldsOf:w=>w==='enemy'?enemy.melds:player.melds,meldType:cards=>cards.length>=3?'RUN':null,meldFixedActive:()=>false,cardFixedActive:()=>false,isScrapShiftPart:(c,o)=>!!c.scrapShiftPart&&(!o||c.owner===o),moveCardBetweenMelds:(w,c,s,t,opts)=>{moved={w,c,s,t,opts};return moved},cardText:c=>c.name||String(c.uid)});
 install(ctx,'scrapShiftTransplantCandidates','requestScrapShiftTransplantChoice');
 const list=ctx.scrapShiftTransplantCandidates('enemy');
 ok(list.length===1&&list[0].card===part&&list[0].source===sourceMeld&&list[0].target===targetMeld,'conveyor finds only legal owned-part transplant paths');
 ctx.requestScrapShiftTransplantChoice('enemy',{name:'컨베이어'});
 ok(moved?.c===part&&moved?.opts?.reason==='scrapShiftTransplant','conveyor routes the part through shared meld movement');
 ok(part.scrapShiftPart===true,'transplant preserves the part marker');
}

{
 const part={uid:30,owner:'enemy',name:'재조립 부품',scrapShiftPart:true,scrapShiftPartSetToken:1,scrapShiftReassembledToken:null,blockedUntilTurn:null};
 const enemy={spent:[part],hand:[],deck:[]},player={spent:[],hand:[],deck:[]};
 const state={turn:'enemy',turnToken:3,turnNo:5};let shield=0;
 const ctx=context({state,sideObj:w=>w==='enemy'?enemy:player,isScrapShiftPart:(c,o)=>!!c.scrapShiftPart&&(!o||c.owner===o),enterHand:(w,c)=>(w==='enemy'?enemy:player).hand.push(c),emitEffectEvent:()=>({}),log:()=>{},cardText:c=>c.name,addShield:(w,n)=>{shield+=n}});
 install(ctx,'clearScrapShiftPart','reassembleScrapShiftPart','scrapShiftReassembleCandidates','requestScrapShiftReassembleChoice');
 ctx.requestScrapShiftReassembleChoice('enemy',{name:'수리 키트',tag:'ssRepairKit'},{shield:2});
 ok(enemy.spent.length===0&&enemy.hand[0]===part&&!part.scrapShiftPart,'repair kit reassembles a spent part and consumes its marker');
 ok(part.scrapShiftReassembledToken===3&&part.blockedUntilTurn===5,'repair kit inherits the same-turn reassembly lock');
 ok(shield===2,'repair kit grants shield 8 through the engine shield scale');
}

{
 const part={uid:40,owner:'enemy',name:'해체 부품',scrapShiftPart:true,age:0};
 const a={uid:41,owner:'enemy'},b={uid:42,owner:'enemy'},c={uid:43,owner:'enemy'};
 const meld={type:'RUN',cards:[a,b,c,part],chain:2};
 const drawn={uid:50,owner:'enemy',name:'교체 카드',age:5,scrapShiftPart:false};
 const enemy={melds:[meld],spent:[],hand:[],deck:[]},player={melds:[],spent:[],hand:[],deck:[]};
 const state={turn:'enemy',turnToken:4,turnNo:8};let draws=0,bottomed=null;
 const ctx=context({state,sideObj:w=>w==='enemy'?enemy:player,other:w=>w==='enemy'?'player':'enemy',meldsOf:w=>w==='enemy'?enemy.melds:player.melds,meldOwnerSide:m=>enemy.melds.includes(m)?'enemy':player.melds.includes(m)?'player':null,meldType:cards=>cards.length>=3?'RUN':null,meldFixedActive:()=>false,cardFixedActive:()=>false,isScrapShiftPart:(x,o=null)=>!!x?.scrapShiftPart&&(!o||x.owner===o),clearCardActiveRank:()=>{},clearMailRouteCard:()=>{},markSetCompletion:()=>{},zeroSightTargetActors:()=>[],emitEffectEvent:()=>({}),refreshPointBlankClashMeld:()=>{},log:()=>{},cardText:x=>x.name||String(x.uid),drawOne:()=>{draws++;enemy.hand.push(drawn);return drawn},scrapShiftCardTurnLocked:()=>false,bottomSpecificHandCard:(w,x)=>{bottomed=x;enemy.hand=enemy.hand.filter(c=>c!==x);enemy.deck.unshift(x);return true}});
 install(ctx,'scrapShiftDismantleAccess','dismantleScrapShiftPart','scrapShiftDismantleCandidates','requestScrapShiftDismantleChoice');
 const list=ctx.scrapShiftDismantleCandidates('enemy',{runOnly:true,minLength:4});
 ok(list.length===1&&list[0].card===part,'dismantle driver only offers legal parts from 4+ card RUNs');
 ctx.requestScrapShiftDismantleChoice('enemy',{name:'분해 드라이버',tag:'ssDismantleDriver'},{runOnly:true,minLength:4});
 ok(enemy.spent[0]===part&&meld.cards.length===3&&meld.chain===1,'dismantle driver performs real dismantle and RUN chain decrement');
 ok(draws===1&&bottomed===drawn&&enemy.deck[0]===drawn,'dismantle driver completes draw-one then bottom-one cycling');
}

ok(road.includes('1차 수직 슬라이스 4장 — A♦ 부품 라벨 / 2♣ 컨베이어 / 4♥ 수리 키트 / A♠ 분해 드라이버'),'ROADMAP records the four-card vertical slice');
ok(/- \[[ x]\] 24장 \/ 수트별 6장 정의 및 실제 효과 구현/.test(road),'full 24-card implementation remains tracked as later waves advance the checkbox');
ok(themeDoc.includes('1차 수직 슬라이스 — A♦ `부품 라벨` / 2♣ `컨베이어` / 4♥ `수리 키트` / A♠ `분해 드라이버`'),'canonical theme doc records wave1 without declaring full live');
ok(poolDoc.includes('24/24 라이브 구현 완료'),'full-pool policy records SCRAP-SHIFT live promotion after all waves');

console.log('SCRAP-SHIFT wave1 vertical-slice regression passed.');

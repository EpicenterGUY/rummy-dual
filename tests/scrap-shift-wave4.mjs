import fs from 'node:fs';
import vm from 'node:vm';

const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const themeDoc=fs.readFileSync(new URL('../docs/THEME_GROUPS.md',import.meta.url),'utf8');
const poolDoc=fs.readFileSync(new URL('../docs/THEME_FULL_POOL_PLAN.md',import.meta.url),'utf8');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let par=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')par++;else if(script[i]===')')par--;else if(script[i]==='{'&&par===0){brace=i;break}}if(brace<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
function context(extra={}){return vm.createContext({console,Set,Map,Array,Object,Number,String,Boolean,Math,applyScrapShiftModuleBus:()=>false,...extra})}
function install(ctx,...names){for(const n of names)vm.runInContext(source(n),ctx)}

new Function(script);
const wave4=[
 ['SSD7','D7','예비 나사','ssSpareScrew'],
 ['SSC8','C8','분기 레일','ssBranchRail'],
 ['SSH8','H8','예비 섀시','ssSpareChassis'],
 ['SSS7','S7','파쇄기','ssShredder']
];
const resolver=source('resolveEffects');
for(const [id,slot,name,tag] of wave4){
 ok(script.includes(`'${id}':{slot:'${slot}',themeId:'scrap-shift',n:'${name}',t:'${tag}'`),`${name} is defined in SCRAP-SHIFT wave4`);
 ok(resolver.includes(`case'${tag}'`),`${tag} is registered in the live resolver surface`);
}
ok(script.includes("themeId:'scrap-shift',live:false"),'wave4 remains DEV-only and does not prematurely release SCRAP-SHIFT');
ok(script.includes('scrapShiftOpponentSpentStart:null'),'new cards initialize delayed opponent-spent bookkeeping');
ok(source('clearScrapShiftPart').includes('c.scrapShiftOpponentSpentStart=null'),'clearing a part also clears stale delayed chassis bookkeeping');

{
 const target={uid:1,owner:'enemy',name:'대체 카드',age:4,scrapShiftPart:false};
 const side={hand:[target]};let designated=null,shield=0;
 const state={turn:'enemy',turnToken:10};
 const ctx=context({state,sideObj:()=>side,isScrapShiftPart:c=>!!c.scrapShiftPart,scrapShiftCardTurnLocked:()=>false,setScrapShiftPart:(w,c)=>{c.scrapShiftPart=true;designated=c;return true},addShield:(w,n)=>{shield+=n},cardText:c=>c.name});
 install(ctx,'scrapShiftHandPartCandidates','requestScrapShiftHandPartChoice');
 ok(ctx.requestScrapShiftHandPartChoice('enemy',{name:'예비 나사',tag:'ssSpareScrew'},{shield:2,allowSkip:true})===false,'spare screw part selection resolves synchronously for AI');
 ok(designated===target&&shield===2,'spare screw can designate an ordinary mixed-deck hand card and grant shield 8');
}
ok(resolver.includes("case'ssSpareScrew':if(c.fromDiscard)")&&resolver.includes("reason:'spareScrew',shield:2"),'spare screw only opens its designation after being acquired from discard');

{
 const part={uid:20,owner:'enemy',scrapShiftPart:true};
 const rail={uid:21,owner:'enemy',themeId:'scrap-shift',tag:'ssBranchRail',name:'분기 레일'};
 const state={turnToken:22};let cycles=0;
 const ctx=context({state,sideObj:()=>({}),other:w=>w==='enemy'?'player':'enemy',isScrapShiftPart:(c,o)=>!!c.scrapShiftPart&&c.owner===o,scrapShiftPublicCards:(w,tag)=>tag==='ssBranchRail'?[rail]:[],themeTurnGateUsed:()=>false,claimThemeTurnGate:()=>true,scrapShiftPassiveCycle:()=>false,scrapShiftPassiveDrawBottom:()=>{cycles++;return true},heal:()=>{},scrapShiftSealTarget:()=>null});
 install(ctx,'handleScrapShiftThemeEvent');
 ok(ctx.handleScrapShiftThemeEvent({event:'onMeldMove',actor:'enemy',card:part,reason:'scrapShiftTransplant',sourceMeld:{type:'SET'},targetMeld:{type:'RUN'},turnToken:22})===true,'branch rail reacts to a real part transplant between different meld types');
 ok(cycles===1,'branch rail performs exactly one draw-then-bottom circulation per qualifying transplant');
 ctx.handleScrapShiftThemeEvent({event:'onMeldMove',actor:'enemy',card:part,reason:'scrapShiftTransplant',sourceMeld:{type:'RUN'},targetMeld:{type:'RUN'},turnToken:22});
 ok(cycles===1,'branch rail ignores same-type transplant movement');
}

{
 const part={uid:30,owner:'player',name:'파손 부품',scrapShiftPart:true,scrapShiftOpponentSpentStart:null};
 const replacement={uid:31,owner:'player',name:'교체 후보',scrapShiftPart:false};
 const shredder={uid:32,owner:'player',themeId:'scrap-shift',tag:'ssShredder',name:'파쇄기'};
 const gates=new Set();let offered=0;
 const state={turnToken:40};
 const side={turnStarts:4,hand:[replacement],spent:[part]};
 const key=(c,k,t)=>`${c.uid}:${k}:${t}`;
 const ctx=context({state,sideObj:()=>side,isScrapShiftPart:(c,o)=>!!c.scrapShiftPart&&(!o||c.owner===o),scrapShiftPublicCards:(w,tag)=>tag==='ssShredder'?[shredder]:[],scrapShiftHandPartCandidates:()=>[replacement],themeTurnGateUsed:(c,k,t)=>gates.has(key(c,k,t)),claimThemeTurnGate:(c,k,t)=>{const x=key(c,k,t);if(gates.has(x))return false;gates.add(x);return true},requestScrapShiftHandPartChoice:()=>{offered++;return true},log:()=>{}});
 install(ctx,'noteScrapShiftPartSpent');
 ok(ctx.noteScrapShiftPartSpent('player',part,'enemy','hostileTest')===true,'common spent lifecycle recognizes an owned part');
 ok(part.scrapShiftOpponentSpentStart===5,'opponent-caused part spend is scheduled for the next owner turn start');
 ok(offered===1,'shredder offers one replacement-part designation when a part enters spent');
 ctx.noteScrapShiftPartSpent('player',part,'enemy','hostileAgain');
 ok(offered===1,'shredder shared turn gate prevents a second use in the same turn');
}

{
 const part={uid:40,owner:'player',scrapShiftPart:true,scrapShiftOpponentSpentStart:5};
 const chassis={uid:41,owner:'player',themeId:'scrap-shift',tag:'ssSpareChassis',name:'예비 섀시'};
 const side={turnStarts:5,spent:[part]};const gates=new Set();let shield=0;
 const state={turnToken:51};
 const key=(c,k,t)=>`${c.uid}:${k}:${t}`;
 const ctx=context({state,sideObj:()=>side,isScrapShiftPart:(c,o)=>!!c.scrapShiftPart&&(!o||c.owner===o),scrapShiftPublicCards:(w,tag)=>tag==='ssSpareChassis'?[chassis]:[],themeTurnGateUsed:(c,k,t)=>gates.has(key(c,k,t)),claimThemeTurnGate:(c,k,t)=>{const x=key(c,k,t);if(gates.has(x))return false;gates.add(x);return true},addShield:(w,n)=>{shield+=n},log:()=>{}});
 install(ctx,'resolveScrapShiftTurnStart');
 ok(ctx.resolveScrapShiftTurnStart('player')===true,'spare chassis resolves a pending hostile part spend on the next owner start');
 ok(shield===3&&part.scrapShiftOpponentSpentStart===null,'spare chassis grants shield 12 and consumes the delayed marker');
}
ok(source('turnStart').includes("resolveScrapShiftTurnStart(w)"),'normal turn start invokes the delayed SCRAP-SHIFT lifecycle resolver');

{
 const part={uid:50,owner:'enemy',scrapShiftPart:true};
 const sourceCard={uid:51,owner:'enemy',name:'과열 부품'};
 const meld={type:'SET',cards:[part]};const gates=new Set();let vulnerable=0;
 const state={turnToken:61};
 const key=(c,k,t)=>`${c.uid}:${k}:${t}`;
 const ctx=context({state,isScrapShiftPart:(c,o)=>!!c.scrapShiftPart&&(!o||c.owner===o),other:w=>w==='enemy'?'player':'enemy',sideObj:w=>({side:w}),themeTurnGateUsed:(c,k,t)=>gates.has(key(c,k,t)),claimThemeTurnGate:(c,k,t)=>{const x=key(c,k,t);if(gates.has(x))return false;gates.add(x);return true},applyOfficialStatus:()=>{vulnerable++;return vulnerable},log:()=>{}});
 install(ctx,'scrapShiftMeldHasOwnedPart','applyScrapShiftOverheat');
 ok(ctx.applyScrapShiftOverheat('enemy',meld,sourceCard)===true,'overheated part applies on its first qualifying return');
 ok(ctx.applyScrapShiftOverheat('enemy',meld,sourceCard)===false&&vulnerable===1,'overheated part cannot stack vulnerable twice in the same turn');
}

for(const [name,needle] of [
 ['dismantleScrapShiftPart','noteScrapShiftPartSpent(owner,c,owner'],
 ['pointBlankConvertSidearm','noteScrapShiftPartSpent(c.owner,c,w'],
 ['spendPointBlankMeldCard','noteScrapShiftPartSpent(c.owner,c,w'],
 ['insuranceBlocks','noteScrapShiftPartSpent(ins.owner,ins,actor'],
 ['cutOppositeEnd','noteScrapShiftPartSpent(cand.owner,cand,w'],
 ['retireMeld','noteScrapShiftPartSpent(c.owner,c,null']
])ok(source(name).includes(needle),`${name} routes part-to-spent movement through the shared SCRAP-SHIFT lifecycle hook`);

ok(road.includes('4차 수명주기 슬라이스 4장 — 7♦ 예비 나사 / 8♣ 분기 레일 / 8♥ 예비 섀시 / 7♠ 파쇄기'),'ROADMAP records SCRAP-SHIFT wave4');
ok(road.includes('과열 부품의 같은 턴 취약 중복 적용'),'ROADMAP records the overheated-part duplicate gate fix');
ok(themeDoc.includes('4차 수명주기 슬라이스 — 7♦ `예비 나사` / 8♣ `분기 레일` / 8♥ `예비 섀시` / 7♠ `파쇄기`'),'canonical theme doc records wave4');
const devCountMatch=poolDoc.match(/24장 미라이브 · (\d+)장 DEV 구현 완료/);
ok(!!devCountMatch&&Number(devCountMatch[1])>=16,'full-pool policy keeps at least the wave4 sixteen DEV cards while later waves may increase the count');
ok(road.includes('- [ ] 24장 / 수트별 6장 정의 및 실제 효과 구현'),'full 24-card implementation remains open after wave4');
console.log('SCRAP-SHIFT wave4 lifecycle regression passed.');

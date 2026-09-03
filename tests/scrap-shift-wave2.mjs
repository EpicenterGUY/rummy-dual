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
const wave2=[
 ['SSD3','D3','분류대','ssSortingBench'],
 ['SSC6','C6','호환 포트','ssCompatPort'],
 ['SSH6','H6','재생 공방','ssRegenWorkshop'],
 ['SSS5','S5','폐기 명령','ssDisposalOrder']
];
for(const [id,slot,name,tag] of wave2){
 ok(script.includes(`'${id}':{slot:'${slot}',themeId:'scrap-shift',n:'${name}',t:'${tag}'`),`${name} is defined in SCRAP-SHIFT wave2`);
 ok(source('resolveEffects').includes(`case'${tag}'`),`${tag} has a resolver/passive registration branch`);
}
ok(script.includes("themeId:'scrap-shift',live:false"),'wave2 remains DEV-only and does not prematurely release SCRAP-SHIFT');
ok(script.includes("clearScrapShiftPart(chosen,'패순환·개인 덱',true)"),'free cycle now clears the part marker before personal-deck entry');

{
 let cleared=0,draws=0;
 const part={uid:1,owner:'player',name:'부품',scrapShiftPart:true,age:3,fromDiscard:false,contractActive:false};
 const replacement={uid:2,owner:'player',name:'교체'};
 const side={hand:[part],deck:[replacement]};
 const ctx=context({sideObj:()=>side,clearMailRouteCard:()=>{},clearScrapShiftPart:c=>{c.scrapShiftPart=false;cleared++},drawOne:()=>{draws++;return replacement},log:()=>{},cardText:c=>c.name});
 install(ctx,'cycleSpecificHandCard');
 ctx.cycleSpecificHandCard('player',part,'수명주기 검사');
 ok(cleared===1&&!part.scrapShiftPart,'free cycle actually clears an existing part marker');
 ok(side.deck[0]===part&&draws===1,'free cycle still performs bottom-one then draw-one behavior');
}

{
 const gates=new Map();let shield=0,cycle=null,healed=0,sealed=null;
 const bench={uid:10,owner:'player',themeId:'scrap-shift',tag:'ssSortingBench',name:'분류대'};
 const port={uid:11,owner:'player',themeId:'scrap-shift',tag:'ssCompatPort',name:'호환 포트'};
 const shop={uid:12,owner:'player',themeId:'scrap-shift',tag:'ssRegenWorkshop',name:'재생 공방'};
 const order={uid:13,owner:'player',themeId:'scrap-shift',tag:'ssDisposalOrder',name:'폐기 명령'};
 const ownMeld={type:'SET',cards:[bench,port,shop,order]};
 const foeMeld={type:'RUN',chain:2,cards:[{uid:20},{uid:21},{uid:22},{uid:23}]};
 const hand=[{uid:30,owner:'player',name:'새 카드',age:1},{uid:31,owner:'player',name:'묵은 카드',age:5}];
 const state={turnToken:50};
 const gateKey=(c,k,t)=>`${c.uid}:${k}:${t}`;
 const ctx=context({state,sideObj:w=>w==='player'?{hand}:{hand:[]},other:w=>w==='player'?'enemy':'player',meldsOf:w=>w==='player'?[ownMeld]:[foeMeld],themeTurnGateUsed:(c,k,t)=>gates.has(gateKey(c,k,t)),claimThemeTurnGate:(c,k,t)=>{const key=gateKey(c,k,t);if(gates.has(key))return false;gates.set(key,true);return true},addShield:(w,n)=>{shield+=n},heal:(w,n)=>{healed+=n},zeroSightCycleCandidates:()=>hand,scrapShiftCardTurnLocked:()=>false,cycleSpecificHandCard:(w,c)=>{cycle=c;return {uid:99}},isScrapShiftPart:(c,o)=>!!c?.scrapShiftPart&&(!o||c.owner===o),applyOfficialStatus:(scope,target,key,n)=>{sealed={scope,target,key,n}},log:()=>{}});
 install(ctx,'scrapShiftPublicCards','scrapShiftPassiveCycle','scrapShiftSealTarget','handleScrapShiftThemeEvent');
 const part={uid:40,owner:'player',scrapShiftPart:true};
 ok(ctx.handleScrapShiftThemeEvent({event:'onPartSet',actor:'player',owner:'player',card:part,turnToken:50})===true,'sorting bench reacts to the first part designation');
 ctx.handleScrapShiftThemeEvent({event:'onPartSet',actor:'player',owner:'player',card:part,turnToken:50});
 ok(shield===2,'sorting bench grants shield 8 exactly once per turn token');
 ok(ctx.handleScrapShiftThemeEvent({event:'onMeldMove',actor:'player',card:part,reason:'scrapShiftTransplant',turnToken:50})===true,'compat port reacts to a real part transplant');
 ok(cycle===hand[1],'compat port uses the free-cycle path on the oldest eligible remaining hand card');
 ctx.handleScrapShiftThemeEvent({event:'onMeldMove',actor:'player',card:part,reason:'ordinaryMove',turnToken:51});
 ok(cycle===hand[1],'compat port ignores non-transplant movement');
 ok(ctx.handleScrapShiftThemeEvent({event:'onReassemble',actor:'player',owner:'player',card:part,turnToken:50})===true,'regen workshop reacts to reassembly');
 ctx.handleScrapShiftThemeEvent({event:'onReassemble',actor:'player',owner:'player',card:part,turnToken:50});
 ok(healed===2,'regen workshop heals current core 8 exactly once per turn token');
 ok(ctx.handleScrapShiftThemeEvent({event:'onDismantle',actor:'player',owner:'player',card:part,meld:foeMeld,sourceSide:'enemy',turnToken:50})===true,'disposal order reacts to dismantle');
 ok(sealed?.scope==='meld'&&sealed?.target===foeMeld&&sealed?.key==='seal'&&sealed?.n===1,'disposal order seals the dismantled enemy meld when it is a valid opponent target');
}

const handler=source('handleScrapShiftThemeEvent');
ok(handler.includes("packet.event==='onPartSet'")&&handler.includes("packet.event==='onMeldMove'")&&handler.includes("packet.event==='onReassemble'")&&handler.includes("packet.event==='onDismantle'"),'wave2 passive handler consumes all four shared action events');
ok(handler.includes("packet.reason==='scrapShiftTransplant'"),'compat port only treats SCRAP-SHIFT transplant as its trigger');
ok(handler.includes("claimThemeTurnGate"),'wave2 reactions use the shared once-per-turn gate');
ok(road.includes('2차 반응 슬라이스 4장 — 3♦ 분류대 / 6♣ 호환 포트 / 6♥ 재생 공방 / 5♠ 폐기 명령'),'ROADMAP records SCRAP-SHIFT wave2');
ok(themeDoc.includes('2차 반응 슬라이스 — 3♦ `분류대` / 6♣ `호환 포트` / 6♥ `재생 공방` / 5♠ `폐기 명령`'),'canonical theme doc records wave2');
const devCountMatch=poolDoc.match(/24장 미라이브 · (\d+)장 DEV 구현 완료/);
ok(!!devCountMatch&&Number(devCountMatch[1])>=8,'full-pool policy keeps at least the wave2 eight DEV cards while later waves may increase the count');
ok(road.includes('- [ ] 24장 / 수트별 6장 정의 및 실제 효과 구현'),'full 24-card implementation remains open');
console.log('SCRAP-SHIFT wave2 reaction regression passed.');

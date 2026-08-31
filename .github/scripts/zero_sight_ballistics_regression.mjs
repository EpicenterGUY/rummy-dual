import fs from 'node:fs';
import vm from 'node:vm';

const html=fs.readFileSync('index.html','utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
const road=fs.readFileSync('ROADMAP.md','utf8');
const themeDoc=fs.readFileSync('docs/THEME_GROUPS.md','utf8');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let par=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')par++;else if(script[i]===')')par--;else if(script[i]==='{'&&par===0){brace=i;break}}if(brace<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
function context(extra={}){return vm.createContext({console,Set,Map,Array,Object,Number,String,Boolean,Math,Infinity,...extra})}
function install(ctx,...names){for(const n of names)vm.runInContext(source(n),ctx)}

ok(script.includes("'ZSD6':{slot:'D6',themeId:'zero-sight',n:'탄도 계산',t:'zsBallistics'"),'Ballistics is a live ZERO-SIGHT 6-diamond variant');
ok(script.includes("{id:'zs3',label:'전체 3클리어 · ZERO-SIGHT',kind:'theme',when:p=>p.totalClears>=3,items:['ZSD6'],fields:[]}"),'Ballistics unlocks at three clears without mutating existing progression groups');
ok(script.includes("zsBallistics:['pressure','control']"),'Ballistics uses ordinary open-deck tendencies');
ok(!script.includes("coreShieldDeficit:['")&&!script.includes("'coreShieldDeficit'"),'core+shield deficit stays a pure helper rather than a new effect action');

// Pure calculator: requirement includes current core and shield, never overfills, and obeys cap.
{
  const enemy={hp:60,shield:12},player={hp:40,shield:0};
  const state={switchPower:0};
  const ctx=context({state,sideObj:w=>w==='enemy'?enemy:player});
  install(ctx,'coreShieldRequirement','coreShieldDeficit');
  ok(ctx.coreShieldRequirement('enemy')===72,'core+shield requirement sums current core and shield');
  ok(ctx.coreShieldDeficit('enemy',61,12)===11,'deficit returns the exact missing lethal amount below the cap');
  ok(ctx.coreShieldDeficit('enemy',30,12)===12,'deficit is capped by the card allowance');
  ok(ctx.coreShieldDeficit('enemy',72,12)===0,'deficit gives zero when already core-break capable');
  ok(ctx.coreShieldDeficit('enemy',90,12)===0,'deficit never grants negative/overkill correction');
}

// Resolver only reserves the assist when this action is actually a target return.
{
  const resolve=source('resolveEffects');
  const state={turnToken:3};
  const side={hand:[]};
  const target={type:'RUN',cards:[]};
  const ctx=context({state,sideObj:()=>side,other:()=> 'enemy',consumeOfficialStatus:()=>0,isZeroSightTarget:(w,m)=>w==='player'&&m===target});
  vm.runInContext(`${resolve};globalThis.__r=resolveEffects`,ctx);
  const card={uid:1,named:true,tag:'zsBallistics',name:'탄도 계산'};
  const action={isNew:false,isAttach:true,meld:target,totalLength:4,effectSeen:new Set(),willReturn:true};
  const out=ctx.__r('player',[card],'RUN',action);
  ok(action.fxState?.coreShieldDeficitCap===12,'target return reserves a +12 maximum lethal assist');
  ok(action.fxState?.coreShieldDeficitSource==='탄도 계산','reserved assist remembers its source for feedback');
  ok(!out.pending,'Ballistics reservation is synchronous');
}
{
  const resolve=source('resolveEffects');
  const state={turnToken:4};
  const side={hand:[]};
  const target={type:'RUN',cards:[]};
  const ctx=context({state,sideObj:()=>side,other:()=> 'enemy',consumeOfficialStatus:()=>0,isZeroSightTarget:()=>false});
  vm.runInContext(`${resolve};globalThis.__r=resolveEffects`,ctx);
  const card={uid:2,named:true,tag:'zsBallistics',name:'탄도 계산'};
  const action={isNew:false,isAttach:true,meld:target,totalLength:4,effectSeen:new Set(),willReturn:true};
  ctx.__r('player',[card],'RUN',action);
  ok(!action.fxState?.coreShieldDeficitCap,'non-target return gets no Ballistics correction');
}

// Final return pipeline must calculate after trap/base reduction and before attackEvent.
{
  const attach=source('attachCards');
  const trap=attach.indexOf('pendingTrapReduction');
  const deficit=attach.indexOf('coreShieldDeficit(other(w),projected,deficitCap)');
  const attack=attach.indexOf('attackEvent(w,finalBase?');
  ok(trap>=0&&deficit>trap,'Ballistics deficit is calculated after pending trap reduction');
  ok(attack>deficit,'Ballistics correction is folded into the same return before attackEvent');
  ok(attach.includes('projected=state.switchPower+finalBase+bonus'),'projected lethal math includes existing bomb, reduced base return, and prior named bonus');
  ok(attach.includes('if(deficitCap&&!fx.flatReturn)'),'flat-return effects cannot accidentally gain lethal correction');
}

ok(road.includes('코어+보호막 부족분 공용 계산 + 6♦ `탄도 계산` 라이브 구현'),'ROADMAP records the shared lethal-deficit helper and Ballistics');
ok(themeDoc.includes('코어+보호막 부족분 계산 공용화'),'canonical theme doc locks the pure helper decision');
ok(themeDoc.includes('6♦ `탄도 계산` 라이브 구현'),'canonical theme doc records live Ballistics');
console.log('ZERO-SIGHT core+shield deficit and Ballistics regression passed.');

import fs from 'node:fs';
import vm from 'node:vm';

const html=fs.readFileSync('index.html','utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
const road=fs.readFileSync('ROADMAP.md','utf8');
const themeDoc=fs.readFileSync('docs/THEME_GROUPS.md','utf8');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let par=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')par++;else if(script[i]===')')par--;else if(script[i]==='{'&&par===0){brace=i;break}}if(brace<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
function install(ctx,...names){for(const name of names)vm.runInContext(source(name),ctx)}

new Function(script);

// recoveryAccess is the single explicit contract for basic vs free recovery.
{
  const ctx=vm.createContext({console,Object});
  ctx.recoveryFreeReason=()=>null;
  install(ctx,'recoveryAccess');
  let a=ctx.recoveryAccess('player','player',{},{});
  ok(a.free===false&&a.reason==='basic'&&a.consumesBasic===true,'basic recovery explicitly consumes the base recovery allowance');
  ctx.recoveryFreeReason=()=> 'roundabout';
  a=ctx.recoveryAccess('player','player',{},{});
  ok(a.free===true&&a.reason==='roundabout'&&a.consumesBasic===false,'conditional free recovery explicitly preserves the base recovery allowance');
}

// Legality distinguishes an already-spent basic recovery from a still-available free recovery.
{
  const c={uid:'recover-card',owner:'player',enteredMeldToken:null};
  const m={type:'RUN',cards:[c,{uid:'2',owner:'player'},{uid:'3',owner:'player'},{uid:'4',owner:'player'}]};
  const player={recoveredThisTurn:true};
  const ctx=vm.createContext({console,Object,Array,state:{turnToken:8}});
  ctx.sideObj=()=>player;ctx.meldsOf=()=>[m];ctx.meldFixedActive=()=>false;ctx.cardFixedActive=()=>false;ctx.meldType=cards=>cards.length>=3?'RUN':null;
  ctx.recoveryFreeReason=()=>null;
  install(ctx,'recoveryAccess','canRecoverCard');
  ok(ctx.canRecoverCard('player','player',0,0)===false,'after basic recovery is spent, another basic recovery is illegal');
  ctx.recoveryFreeReason=()=> 'rummy';
  ok(ctx.canRecoverCard('player','player',0,0)===true,'after basic recovery is spent, a qualified free recovery remains legal');
  player.recoveredThisTurn=false;ctx.recoveryFreeReason=()=>null;
  ok(ctx.canRecoverCard('player','player',0,0)===true,'unused basic recovery remains legal normally');
}

// Shared recovery event exposes exactly the same distinction to themes.
{
  const packets=[];
  const meld={type:'SET',cards:[]};
  const ctx=vm.createContext({console,Object,Array});
  ctx.zeroSightTargetActors=()=>[];ctx.meldOwnerSide=()=> 'player';
  ctx.emitEffectEvent=(event,payload)=>{const p={event,...payload};packets.push(p);return p};
  install(ctx,'emitRecoveryEvent');
  let p=ctx.emitRecoveryEvent('player',{uid:'a'},meld,'player',{free:true,reason:'roundabout',consumesBasic:false});
  ok(p.free===true&&p.consumesBasic===false&&p.reason==='roundabout','free onRecover packet carries non-consuming recovery semantics');
  p=ctx.emitRecoveryEvent('player',{uid:'b'},meld,'player',{free:false,reason:'basic',consumesBasic:true});
  ok(p.free===false&&p.consumesBasic===true&&p.reason==='basic','basic onRecover packet carries consuming recovery semantics');
  p=ctx.emitRecoveryEvent('player',{uid:'c'},meld,'player',{free:false,reason:'basic'});
  ok(p.consumesBasic===true,'event helper safely derives basic consumption for legacy callers');
}

const playerRecover=source('playerRecover'),aiRecover=source('executeRecoverAI'),canRecover=source('canRecoverCard'),ui=source('updateButtons');
ok(playerRecover.includes("recovery=recoveryAccess('player'")&&playerRecover.includes('recovery.consumesBasic')&&playerRecover.includes('consumesBasic:recovery.consumesBasic'),'player recovery uses the shared recoveryAccess contract end-to-end');
ok(aiRecover.includes('recovery=recoveryAccess(w')&&aiRecover.includes('recovery.consumesBasic')&&aiRecover.includes('consumesBasic:recovery.consumesBasic'),'AI recovery uses the same recoveryAccess contract end-to-end');
ok(canRecover.includes('access.consumesBasic'),'recovery legality consumes only the basic allowance when required');
ok(ui.includes("recoverAccess?.free?'무료 회수':'회수'")&&ui.includes("'기본 회수 사용함'"),'player UI visibly distinguishes free recovery from an already-used basic recovery');

ok(road.includes('- [x] 무료 회수와 기본 회수 횟수를 명확히 구분'),'ROADMAP marks recovery distinction complete');
ok(themeDoc.includes('- [x] 무료 회수와 기본 회수 횟수의 구분을 데이터로 명확화'),'canonical POINT-BLANK document marks the recovery data contract complete');
console.log('POINT-BLANK basic/free recovery distinction regression passed.');

import fs from 'node:fs';
import vm from 'node:vm';

const html = fs.readFileSync(new URL('../index.html', import.meta.url), 'utf8');
const road = fs.readFileSync(new URL('../ROADMAP.md', import.meta.url), 'utf8');
const script = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).join('\n');

function ok(v,m){ if(!v) throw new Error(m); console.log(`PASS: ${m}`); }
function functionSource(name){
  const marker=`function ${name}(`, start=script.indexOf(marker);
  if(start<0) throw new Error(`missing function ${name}`);
  const bodyMarker=script.indexOf('){',start), brace=bodyMarker+1;
  let depth=0,end=-1;
  for(let i=brace;i<script.length;i++){
    if(script[i]==='{')depth++;
    else if(script[i]==='}'){depth--;if(depth===0){end=i+1;break}}
  }
  if(end<0)throw new Error(`unterminated ${name}`);
  return script.slice(start,end);
}
function install(ctx,...names){for(const n of names)vm.runInContext(functionSource(n),ctx)}
function makeState(){
  const player={hand:[],deck:[],spent:[],melds:[],blockOpponentDiscardNext:false,maintenanceUsed:false};
  const enemy={hand:[],deck:[],spent:[],melds:[],blockOpponentDiscardNext:false,maintenanceUsed:false};
  const state={player,enemy,discard:[],turn:'player',phase:'draw',turnNo:2,turnToken:7,battleId:10,gameOver:false,target:null,selected:new Set(),selectionOrder:[],boardSelected:new Set()};
  const logs=[],scheduled=[];
  const ctx=vm.createContext({console,Math,Set,Map,Array,Object,state,logs,scheduled,setTimeout:(fn)=>{scheduled.push(fn);return scheduled.length}});
  ctx.sideObj=w=>w==='player'?player:enemy;
  ctx.other=w=>w==='player'?'enemy':'player';
  ctx.meldsOf=w=>ctx.sideObj(w).melds;
  ctx.shuffle=a=>a;
  ctx.log=(msg)=>logs.push(msg);
  ctx.isLiveCombatSession=()=>true;
  ctx.endPlayerTurn=()=>{ctx.endCalls=(ctx.endCalls||0)+1};
  ctx.cardFixedActive=()=>false;
  ctx.meldFixedActive=()=>false;
  ctx.canRecoverCard=()=>false;
  ctx.retireMeld=(side,index)=>{
    const [m]=ctx.meldsOf(side).splice(index,1);
    if(!m)return;
    for(const c of m.cards)ctx.sideObj(c.owner).spent.push(c);
  };
  install(ctx,'ownedRecycleCount','hasAcquisitionSource','anyRecoveryOption','circulationReleasePlan','recycleIfNeeded','emergencyReleaseMeld','prepareAcquisitionPhase');
  return{ctx,state,player,enemy,logs,scheduled};
}

{
  const {ctx,state,player}=makeState();
  player.hand=[{uid:'hold',owner:'player'}];
  ok(ctx.prepareAcquisitionPhase('player')==='action','zero-source turn with a hand skips acquisition instead of locking');
  ok(state.phase==='action','player advances to action phase when acquisition is impossible');
}

{
  const {ctx,state,player}=makeState();
  player.melds=[{type:'SET',cards:[{owner:'player'},{owner:'player'},{owner:'player'}]}];
  ok(ctx.prepareAcquisitionPhase('player')==='draw','fully empty player releases a public meld and restores a draw source');
  ok(player.melds.length===0,'emergency circulation removes exactly one blocking public meld');
  ok(player.deck.length===3&&player.spent.length===0,'released owned cards recycle into the personal deck without duplication');
  ok(state.phase==='draw','restored source keeps the normal acquisition step available');
}

{
  const {ctx,state,player}=makeState();
  player.melds=[{type:'RUN',cards:[{owner:'player'},{owner:'player'},{owner:'player'},{owner:'player'}]}];
  ctx.canRecoverCard=()=>true;
  ok(ctx.prepareAcquisitionPhase('player')==='action','legal public-meld recovery is preferred over destructive emergency retirement');
  ok(player.melds.length===1,'recoverable meld stays on the board');
  ok(state.phase==='action','recovery escape opens the action phase');
}

{
  const {ctx,state,scheduled}=makeState();
  ok(ctx.prepareAcquisitionPhase('player')==='pass','cardless player with no owned board card falls back to automatic pass');
  ok(state.phase==='wait'&&scheduled.length===1,'automatic pass is scheduled instead of leaving an unusable action screen');
  scheduled[0]();
  ok(ctx.endCalls===1,'automatic pass advances the turn exactly once');
}

{
  const player={hand:[{uid:'h'}],deck:[],spent:[],melds:[],maintenanceUsed:false};
  const enemy={hand:[],deck:[],spent:[],melds:[]};
  const state={player,enemy,discard:[{owner:'player'}]};
  const ctx=vm.createContext({console,Math,Set,Map,Array,Object,state});
  ctx.sideObj=w=>w==='player'?player:enemy;
  ctx.hasAnyLegalAction=()=>false;
  install(ctx,'ownedRecycleCount','maintenanceLimit');
  ok(ctx.maintenanceLimit('player')===2,'maintenance recognizes an owned shared-discard card as recyclable personal supply');
}

const rummy=functionSource('triggerRummy');
ok(rummy.includes("ownedRecycleCount(w)<=0")&&rummy.includes("emergencyReleaseMeld(w,'러미 재충전원 0 · 순환 정체')"),'RUMMY has a zero-supply emergency circulation hook');
ok(functionSource('confirmMulligan').includes("prepareAcquisitionPhase('player')"),'first player turn prepares zero-source acquisition safely');
ok(functionSource('aiTurn').includes("prepareAcquisitionPhase('enemy')")&&functionSource('aiTurn').includes("prepareAcquisitionPhase('player')"),'AI and following player turn both run acquisition safety');
ok(functionSource('playerDraw').includes("prepareAcquisitionPhase('player')"),'failed manual draw falls back through the same acquisition safety');
ok(html.includes('완전 정체에서는 <b>내 카드가 포함된 공개 조합 1개를 긴급 정리</b>'),'rules explain the last-resort no-duplication circulation release');
ok(road.includes('Zero-source circulation safety')&&road.includes('Close zero-source deadlocks for player/AI/RUMMY'),'roadmap locks the deadlock safety rule and implementation');

console.log('Deadlock circulation regression passed.');

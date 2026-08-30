from pathlib import Path


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly 1 match, got {count}')
    return text.replace(old, new, 1)

index = Path('index.html')
html = index.read_text()

old_recycle = "function recycleIfNeeded(w){const s=sideObj(w);if(s.deck.length)return 0;const spent=s.spent.splice(0),ownedDiscard=[];for(let i=state.discard.length-1;i>=0;i--){const c=state.discard[i];if(c.owner!==w)continue;ownedDiscard.push(c);state.discard.splice(i,1)}const pool=spent.concat(ownedDiscard);if(!pool.length)return 0;s.deck=shuffle(pool);log(`${w==='player'?'내':'상대'} 재순환 · 소모패 ${spent.length}장${ownedDiscard.length?` + 공용 버림패의 내 카드 ${ownedDiscard.length}장`:''} → 새 덱 ${pool.length}장.`,'important');return pool.length}"
new_recycle = "function ownedRecycleCount(w){const s=sideObj(w);let n=s.deck.length+s.spent.length;for(const c of state.discard)if(c.owner===w)n++;return n}\nfunction hasAcquisitionSource(w){const s=sideObj(w);return ownedRecycleCount(w)>0||(!s.blockOpponentDiscardNext&&state.discard.length>0)}\nfunction anyRecoveryOption(w){for(const targetSide of [w,other(w)])for(let mi=0;mi<meldsOf(targetSide).length;mi++){const m=meldsOf(targetSide)[mi];for(let ci=0;ci<m.cards.length;ci++)if(canRecoverCard(w,targetSide,mi,ci))return true}return false}\nfunction circulationReleasePlan(w){for(const targetSide of [w,other(w)]){const list=meldsOf(targetSide);for(let i=0;i<list.length;i++){const owned=list[i].cards.filter(c=>c.owner===w).length;if(owned)return{side:targetSide,index:i,owned,count:list[i].cards.length}}}return null}\nfunction emergencyReleaseMeld(w,reason='순환 정체'){const plan=circulationReleasePlan(w);if(!plan)return false;retireMeld(plan.side,plan.index,reason);if(w==='player'){state.target=null;state.boardSelected.clear();state.selected.clear();state.selectionOrder=[]}recycleIfNeeded(w);log(`${w==='player'?'내':'상대'} 순환 안전장치 · ${plan.side===w?'내':'상대'} 공개 조합 1개를 긴급 정리해 카드 흐름을 복구했습니다.`,'important');return true}\nfunction prepareAcquisitionPhase(w){const s=sideObj(w);if(hasAcquisitionSource(w))return'draw';if(!s.hand.length&&anyRecoveryOption(w)){if(s.blockOpponentDiscardNext)s.blockOpponentDiscardNext=false;if(w==='player'&&state.turn==='player'&&state.phase==='draw')state.phase='action';log(`${w==='player'?'내':'상대'} 획득원 0 · 공개 조합의 내 카드를 회수해 순환을 이어갑니다.`,'important');return'action'}if(!s.hand.length){emergencyReleaseMeld(w,'획득원 0 · 순환 정체');if(hasAcquisitionSource(w))return'draw'}if(s.blockOpponentDiscardNext)s.blockOpponentDiscardNext=false;if(w==='player'&&state.turn==='player'&&state.phase==='draw')state.phase='action';if(!s.hand.length&&!anyRecoveryOption(w)){if(w==='player'){state.phase='wait';const battleId=state.battleId,turnToken=state.turnToken;log('순환 가능한 카드가 한 장도 없어 이번 턴을 자동 통과합니다.','important');setTimeout(()=>{if(isLiveCombatSession()&&state.battleId===battleId&&state.turnToken===turnToken&&state.turn==='player'&&!state.gameOver)endPlayerTurn()},360)}else log('상대는 순환 가능한 카드가 없어 획득을 생략합니다.','important');return'pass'}log(`${w==='player'?'내':'상대'} 획득 가능한 카드가 없어 획득 단계를 생략합니다.`,'important');return'action'}\n" + old_recycle
html = replace_once(html, old_recycle, new_recycle, 'recycle helpers')

old_maintenance = "function maintenanceLimit(w){const s=sideObj(w);if(s.maintenanceUsed||!s.hand.length||(!s.deck.length&&!s.spent.length))return 0;return hasAnyLegalAction(w)?1:2}"
new_maintenance = "function maintenanceLimit(w){const s=sideObj(w);if(s.maintenanceUsed||!s.hand.length||ownedRecycleCount(w)<=0)return 0;return hasAnyLegalAction(w)?1:2}"
html = replace_once(html, old_maintenance, new_maintenance, 'maintenance recycle source')

old_rummy = "if(w==='player')state.rummy++;const beforeReloadHand=s.hand.length;drawMany(w,reload,false);"
new_rummy = "if(w==='player')state.rummy++;if(!s.hand.length&&ownedRecycleCount(w)<=0)emergencyReleaseMeld(w,'러미 재충전원 0 · 순환 정체');const beforeReloadHand=s.hand.length;drawMany(w,Math.max(0,reload-beforeReloadHand),false);"
html = replace_once(html, old_rummy, new_rummy, 'rummy zero-source safety')

old_mulligan = "state.selected.clear();state.selectionOrder=[];state.boardSelected.clear();state.phase='draw';turnStart('player');log('전투 시작. 개인 덱 또는 공용 버림패에서 1장을 획득합니다.','important');render()}"
new_mulligan = "state.selected.clear();state.selectionOrder=[];state.boardSelected.clear();state.phase='draw';turnStart('player');prepareAcquisitionPhase('player');log('전투 시작. 개인 덱 또는 공용 버림패에서 1장을 획득합니다.','important');render()}"
html = replace_once(html, old_mulligan, new_mulligan, 'first player draw preparation')

old_player_draw = "else c=drawOne('player',fromDiscard);if(!c){log('가져올 카드가 없습니다.','hit');return}"
new_player_draw = "else c=drawOne('player',fromDiscard);if(!c){const fallback=prepareAcquisitionPhase('player');if(fallback==='action'||fallback==='pass'){render();return}log('가져올 카드가 없습니다. 순환이 복구되었으면 덱에서 다시 뽑으세요.','hit');render();return}"
html = replace_once(html, old_player_draw, new_player_draw, 'player draw fallback')

old_ai_start = "function aiTurn(){if(state.gameOver)return;turnStart('enemy');state.turn='enemy';state.phase='wait';state.lastEnemyUsedDiscard=false;"
new_ai_start = "function aiTurn(){if(state.gameOver)return;turnStart('enemy');state.turn='enemy';state.phase='wait';state.lastEnemyUsedDiscard=false;prepareAcquisitionPhase('enemy');"
html = replace_once(html, old_ai_start, new_ai_start, 'AI acquisition preparation')

old_player_turn = "state.turn='player';state.phase='draw';state.turnNo++;state.lastPlayerUsedDiscard=false;turnStart('player');render()}"
new_player_turn = "state.turn='player';state.phase='draw';state.turnNo++;state.lastPlayerUsedDiscard=false;turnStart('player');prepareAcquisitionPhase('player');render()}"
html = replace_once(html, old_player_turn, new_player_turn, 'next player acquisition preparation')

old_rules = "<div class=\"ruleBlock\"><h3>덱 · 버림패 · 소모패</h3><p><b>공용 버림패</b>는 양쪽이 맨 위 카드를 가져올 수 있는 공용 공간입니다. <b>소모패</b>는 각자의 자동 재순환 대기 더미라서 기본적으로 직접 사용할 수 없습니다. 개인 덱의 마지막 카드를 뽑으면 <b>그 플레이어의 소모패 + 공용 버림패에 남아 있는 현재 그 플레이어 소유 카드</b>만 회수해 함께 섞어 새 덱을 만듭니다. 상대 소유 카드와 공개 조합 카드는 그대로 남습니다.</p></div>"
new_rules = "<div class=\"ruleBlock\"><h3>덱 · 버림패 · 소모패</h3><p><b>공용 버림패</b>는 양쪽이 맨 위 카드를 가져올 수 있는 공용 공간입니다. <b>소모패</b>는 각자의 자동 재순환 대기 더미라서 기본적으로 직접 사용할 수 없습니다. 개인 덱의 마지막 카드를 뽑으면 <b>그 플레이어의 소모패 + 공용 버림패에 남아 있는 현재 그 플레이어 소유 카드</b>만 회수해 함께 섞어 새 덱을 만듭니다. 상대 소유 카드와 공개 조합 카드는 그대로 남습니다. <b>덱·소모패·사용 가능한 공용 버림패가 모두 0장</b>이면 획득을 생략하고 행동을 계속합니다. 손패도 0장이고 합법적인 회수로도 풀 수 없는 완전 정체에서는 <b>내 카드가 포함된 공개 조합 1개를 긴급 정리</b>해 순환을 복구합니다.</p></div>"
html = replace_once(html, old_rules, new_rules, 'rules deadlock safety')
index.write_text(html)

road_path = Path('ROADMAP.md')
road = road_path.read_text()
old_m0 = "- [x] When a personal deck empties, recycle that player’s spent pile plus cards in the shared discard currently owned by that player; opponent-owned discard and public meld cards stay in place\n"
new_m0 = old_m0 + "- [x] Zero-source circulation safety: if deck/spent/usable shared discard are all empty, skip acquisition; if the player also has no hand and no legal recovery, retire one public meld containing their card as a last-resort circulation release, without duplicating cards\n"
road = replace_once(road, old_m0, new_m0, 'roadmap M0 safety')
old_m4 = "- [x] Verify deck exhaustion/recycling under long games; recycle personal spent + currently-owned cards from shared discard, while preserving opponent-owned discard and all public meld cards\n"
new_m4 = old_m4 + "- [x] Close zero-source deadlocks for player/AI/RUMMY and make maintenance recognize currently-owned shared-discard cards as a valid personal recycle source\n"
road = replace_once(road, old_m4, new_m4, 'roadmap M4 safety')
road_path.write_text(road)

Path('tests/deadlock-circulation.mjs').write_text(r'''import fs from 'node:fs';
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
''')

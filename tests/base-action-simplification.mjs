import assert from 'node:assert/strict';
import fs from 'node:fs';
import {makeGame,html} from './helpers/live-game.mjs';

function fresh(w='enemy'){
  const g=makeGame();g.state.turn=w;g.state.phase=w==='player'?'action':'wait';
  for(const side of ['player','enemy']){
    const s=g.state[side];s.hand=[];s.melds=[];s.spent=[];s.newMeldCount=0;s.attachCount=0;s.extraAttachRemaining=0;s.meldCleanupUsed=false;s.recoveredThisTurn=false;s.returnedSwitchThisTurn=false;
  }
  g.state.switchTarget='neutral';g.state.switchPower=0;return g;
}
const cards=(g,w,slots,named=false)=>slots.map(slot=>g.makeCard(slot[0],slot.slice(1),named,w));
function run(g,w,suit,start=2,count=3,chain=0){
  const rank=v=>v===1?'A':v===11?'J':v===12?'Q':v===13?'K':String(v);
  return {type:'RUN',cards:Array.from({length:count},(_,i)=>g.makeCard(suit,rank(start+i),false,w)),chain,createdToken:0,createdTurn:0,lastTouchedOwnerStart:0,status:g.blankMeldStatus(),themeMeta:{}};
}
function set3(g,w,rank='7'){
  return {type:'SET',cards:['S','H','D'].map(s=>g.makeCard(s,rank,false,w)),chain:0,createdToken:0,createdTurn:0,lastTouchedOwnerStart:0,status:g.blankMeldStatus(),themeMeta:{}};
}

// Public slots + two exact-three creates are still the M0R base contract.
{
  const g=fresh(),s=g.state.enemy;
  const a=cards(g,'enemy',['S3','H3','D3']),b=cards(g,'enemy',['C4','C5','C6']),c=cards(g,'enemy',['S8','H8','D8']);s.hand=[...a,...b,...c];
  assert.equal(g.submitNewMeld('enemy',a),true);assert.equal(g.submitNewMeld('enemy',b),true);assert.equal(s.melds.length,2);assert.equal(s.newMeldCount,2);
  assert.equal(g.submitNewMeld('enemy',c),false,'third new meld in one turn is rejected');
  g.turnStart('enemy');s.hand.push(...c);assert.equal(g.submitNewMeld('enemy',c),true);assert.equal(s.melds.length,3);
  const d=cards(g,'enemy',['S9','H9','D9']);s.hand.push(...d);assert.equal(g.submitNewMeld('enemy',d),'full','fourth own public meld is rejected');
}
console.log('PASS public meld cap 3 and new exact-three meld cap 2');

// New own meld is protected from same-turn extension; older own and opponent melds are legal targets.
{
  const g=fresh(),s=g.state.enemy,base=cards(g,'enemy',['S2','S3','S4']),s5=cards(g,'enemy',['S5'])[0];s.hand=[...base,s5];
  assert.equal(g.submitNewMeld('enemy',base),true);assert.equal(g.attachCards('enemy',[s5],'enemy',0),false,'same-turn new own meld cannot be attached');
  g.turnStart('enemy');assert.equal(g.attachCards('enemy',[s5],'enemy',0),true,'older own meld can be attached');
}
{
  const g=fresh(),s=g.state.enemy;s.melds=[];g.state.player.melds=[run(g,'player','H',2,3,0)];const h5=g.makeCard('H','5',false,'enemy');s.hand=[h5];
  assert.equal(g.attachCards('enemy',[h5],'player',0),true,'opponent public meld can be used by attach');
}
console.log('PASS new-own-meld protection and existing own/opponent attach targets');

// One attach action may contain multiple cards, sums each CHAIN step, and moves SWITCH once.
{
  const g=fresh(),s=g.state.enemy;s.melds=[run(g,'enemy','S',2,3,0)];const more=cards(g,'enemy',['S5','S6','S7']);s.hand=[...more];
  let returns=0;g.subscribeEffectEvent(e=>{if(e.event==='onSwitchReturn'&&e.actor==='enemy')returns++});
  assert.equal(g.attachCards('enemy',more,'enemy',0),true);
  assert.equal(g.state.switchPower,45,'10+15+20 are accumulated in the one multi-attach');
  assert.equal(s.attachCount,1);assert.equal(g.state.switchTarget,'player');
  assert.ok(returns<=1,'multi-attach never emits more than one physical SWITCH return');
  const second=run(g,'enemy','H',2,3,0);s.melds.push(second);const h5=g.makeCard('H','5',false,'enemy');s.hand.push(h5);
  assert.equal(g.attachCards('enemy',[h5],'enemy',1),false,'base second attach action is rejected');
}
console.log('PASS base attach is one action; multi-card CHAIN sums while SWITCH moves once');

// Connection Link is the explicit named exception: one extra attach, power adds, SWITCH does not move again.
{
  const g=fresh(),s=g.state.enemy;
  s.melds=[run(g,'enemy','C',2,3,0),run(g,'enemy','H',2,3,0)];
  const link=g.makeCard('C','5',true,'enemy','C5'),h5=g.makeCard('H','5',false,'enemy');s.hand=[link,h5];
  assert.equal(g.attachCards('enemy',[link],'enemy',0),true,'Connection Link first attach');
  assert.equal(s.attachCount,1);assert.equal(s.extraAttachRemaining,1,'Connection Link grants explicit extra attach');
  const targetAfterFirst=g.state.switchTarget,powerAfterFirst=g.state.switchPower;
  assert.equal(g.attachCards('enemy',[h5],'enemy',1),true,'named extra attach is allowed');
  assert.equal(s.attachCount,2);assert.equal(s.extraAttachRemaining,0);assert.equal(g.state.switchTarget,targetAfterFirst,'extra attach does not move SWITCH a second time');assert.ok(g.state.switchPower>powerAfterFirst,'extra attach still adds CHAIN power');
  const third=run(g,'enemy','D',2,3,0);s.melds.push(third);const d5=g.makeCard('D','5',false,'enemy');s.hand.push(d5);assert.equal(g.attachCards('enemy',[d5],'enemy',2),false,'extra allowance is consumed');
}
console.log('PASS Connection Link is a clear named extra-attach exception');

// SET fourth suit is still +24, one return, immediate retire to current card owners' spent piles.
{
  const g=fresh(),s=g.state.enemy;s.melds=[set3(g,'enemy','7')];const c7=g.makeCard('C','7',false,'enemy');s.hand=[c7];const before=s.spent.length;
  assert.equal(g.attachCards('enemy',[c7],'enemy',0),true);assert.equal(g.state.switchPower,24);assert.equal(g.state.switchTarget,'player');assert.equal(s.melds.length,0);assert.equal(s.spent.length,before+4);
}
console.log('PASS SET fourth suit BURST +24 returns and retires immediately');

// RUN completion remains distinct: CHAIN 4+, +0, no SWITCH movement, slot opens.
{
  const g=fresh(),s=g.state.enemy;s.melds=[run(g,'enemy','S',2,7,4)];g.state.switchPower=57;g.state.switchTarget='player';
  assert.equal(g.canFinishRun('enemy',0),true);assert.equal(g.finishRun('enemy',0),true);assert.equal(s.melds.length,0);assert.equal(g.state.switchPower,57);assert.equal(g.state.switchTarget,'player');
}
console.log('PASS RUN finish remains CHAIN4+ slot release with +0 and no SWITCH movement');

// Full-board cleanup: only at 3 slots, once, not same-turn-created/fixed; protect does not block.
{
  const g=fresh(),s=g.state.enemy;s.melds=[run(g,'enemy','S'),run(g,'enemy','H')];assert.equal(g.canCleanupMeld('enemy',0),false,'1-2 slots cannot use cleanup');
  s.melds.push(set3(g,'enemy','8'));g.state.switchPower=33;g.state.switchTarget='player';const retired=[];g.subscribeEffectEvent(e=>{if(e.event==='onRetire')retired.push(e)});
  assert.equal(g.canCleanupMeld('enemy',0),true);assert.equal(g.cleanupMeld('enemy',0),true);assert.equal(s.melds.length,2);assert.equal(s.meldCleanupUsed,true);assert.equal(g.state.switchPower,33);assert.equal(g.state.switchTarget,'player');assert.ok(retired.some(e=>e.reason==='자발적 조합 정리'));
  s.melds.push(run(g,'enemy','C'));assert.equal(g.cleanupMeld('enemy',0),false,'second basic cleanup in same turn is rejected');
}
{
  const g=fresh(),s=g.state.enemy;s.melds=[run(g,'enemy','S'),run(g,'enemy','H'),set3(g,'enemy','8')];s.melds[0].createdToken=g.state.turnToken;assert.equal(g.canCleanupMeld('enemy',0),false,'same-turn-created own meld cannot be cleaned');
  g.applyOfficialStatus('meld',s.melds[1],'fixed',1,{actor:'player',silent:true});assert.equal(g.canCleanupMeld('enemy',1),false,'fixed meld cannot be cleaned');
  g.applyOfficialStatus('meld',s.melds[2],'protect',1,{actor:'enemy',silent:true});assert.equal(g.canCleanupMeld('enemy',2),true,'protect does not block voluntary own cleanup');
}
console.log('PASS conditional full-board cleanup safeguards');

// Recovery remains legal only when the meld survives and base recovery is once per turn.
{
  const g=fresh(),s=g.state.enemy;s.melds=[run(g,'enemy','S',2,3,0)];assert.equal(g.canRecoverCard('enemy','enemy',0,0),false,'cannot break a 3-card meld');
  s.melds=[run(g,'enemy','H',2,4,1)];const end=s.melds[0].cards.at(-1);assert.equal(g.canRecoverCard('enemy','enemy',0,3),true);g.executeRecoverAI('enemy',{side:'enemy',mi:0,ci:3,card:end});assert.equal(s.melds[0].cards.length,3);assert.equal(s.recoveredThisTurn,true);
}
console.log('PASS recovery still requires a legal remaining meld');

// AI cleanup values dead RUNs over burst-ready SETs and grown RUNs when a real new meld is waiting.
{
  const g=fresh(),s=g.state.enemy;s.melds=[set3(g,'enemy','9'),run(g,'enemy','C',2,3,0),run(g,'enemy','H',2,5,2)];s.hand=cards(g,'enemy',['S4','S5','S6','DK']);
  const plan=g.bestCleanupMeldAI('enemy');assert.ok(plan,'AI sees a cleanup plan on a full board with a new meld candidate');assert.equal(plan.index,1,'AI chooses the CHAIN 0 dead RUN over ready SET / grown RUN');
}
console.log('PASS AI cleanup heuristic preserves higher-value public melds');

// RUMMY behavior remains six cards and does not create power by itself.
{
  const g=fresh(),s=g.state.enemy;s.hand=[];s.deck=cards(g,'enemy',['S2','H3','D4','C5','S6','H7']);g.state.switchPower=19;g.state.switchTarget='player';
  assert.equal(g.triggerRummy('enemy',[],{returned:false}),'rummy');assert.equal(s.hand.length,6);assert.equal(g.state.switchPower,19);assert.equal(g.state.switchTarget,'player');
}
console.log('PASS RUMMY refill remains six with no inherent power/SWITCH change');

// Source-level guard: old target-specific repeat-attach state must not creep back in.
assert.ok(html.includes('function attachAccess('));
for(const legacy of ['function canContinueReturnedRun(','returnAttachToken','extraAttachGrantedToken'])assert.ok(!html.includes(legacy),`legacy attach exception removed: ${legacy}`);
assert.ok(!html.includes('같은 런 연속 연장'));
assert.ok(html.includes("C5':{n:'연결고리'")&&html.includes('추가 붙이기 1회를 얻는다'));
assert.ok(html.includes("J5':{n:'반역자 조커'")&&html.includes('추가 붙이기 허용을 잃는다'));
assert.ok(html.includes('id="cleanupBtn"')&&html.includes('function playerCleanupMeld('));
assert.ok(html.includes('새 조합은 두 번, 붙이기는 한 번, 내 필드는 세 칸.'));

const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const readme=fs.readFileSync(new URL('../README.md',import.meta.url),'utf8');
const m0r=fs.readFileSync(new URL('../docs/M0R_MELD_EXPANSION.md',import.meta.url),'utf8');
assert.ok(road.includes('## M0S — 기본 행동 단순화 / 3슬롯 필드 정리'));
assert.ok(!readme.includes('same RUN may still be extended again during the same turn'));
assert.ok(m0r.includes('플레이어 전역 턴당 1회'));
console.log('PASS source/docs expose the simplified base-action contract');

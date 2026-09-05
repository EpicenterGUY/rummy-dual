import assert from 'node:assert/strict';
import {makeGame,html} from './helpers/live-game.mjs';

function fresh(){
  const g=makeGame();
  g.state.turn='enemy';
  g.state.phase='wait';
  g.state.switchTarget='neutral';
  g.state.switchPower=0;
  g.state.turnToken=11;
  for(const w of ['player','enemy']){
    const s=g.state[w];
    s.hand=[];s.deck=[];s.spent=[];s.melds=[];
    s.newMeldCount=0;s.attachCount=0;s.extraAttachRemaining=0;
    s.recoveredThisTurn=false;s.returnedSwitchThisTurn=false;s.meldCleanupUsed=false;
  }
  g.state.discard=[];
  return g;
}
function run(g,w,suit='H',start=2,count=3){
  const rank=v=>v===1?'A':v===11?'J':v===12?'Q':v===13?'K':String(v);
  return {type:'RUN',cards:Array.from({length:count},(_,i)=>g.makeCard(suit,rank(start+i),false,w)),chain:0,createdTurn:0,createdToken:0,lastTouchedOwnerStart:0,status:g.blankMeldStatus(),themeMeta:{}};
}

// DA Fence: discard acquisition now performs an actual self-contained cycle.
{
  const g=fresh(),s=g.state.enemy;
  const hold=g.makeCard('S','2',false,'enemy');hold.age=5;
  const fence=g.makeCard('D','A',true,'enemy','DA');
  const drawn=g.makeCard('H','3',false,'enemy');
  s.hand=[hold];s.deck=[drawn];g.state.discard=[fence];
  const got=g.acquireDiscardCard('enemy',0);
  assert.equal(got.uid,fence.uid);
  assert.equal(g.onDiscardDraw('enemy',got),false);
  assert.ok(s.hand.some(c=>c.uid===fence.uid),'Fence stays in hand');
  assert.ok(s.hand.some(c=>c.uid===drawn.uid),'Fence draws one replacement candidate');
  assert.ok(!s.hand.some(c=>c.uid===hold.uid),'oldest other hand card is cycled for CPU');
  assert.ok(s.deck.some(c=>c.uid===hold.uid),'cycled card goes to deck bottom');
}
console.log('PASS common DA Fence has a real discard-acquisition cycle');

// SQ Death Sentence: exact tracked discard card creates a same-turn +6 BURST payoff.
{
  const g=fresh(),s=g.state.enemy;
  const sentence=g.makeCard('S','Q',true,'enemy','SQ');
  const hq=g.makeCard('H','Q',false,'enemy'),dq=g.makeCard('D','Q',false,'enemy');
  s.melds=[{type:'SET',cards:[sentence,hq,dq],chain:0,createdTurn:0,createdToken:0,lastTouchedOwnerStart:0,status:g.blankMeldStatus(),themeMeta:{}}];
  const cq=g.makeCard('C','Q',false,'player');
  g.state.discard=[cq];
  const got=g.acquireDiscardCard('enemy',0);
  g.onDiscardDraw('enemy',got);
  assert.equal(got.deathSentenceClaimToken,g.state.turnToken,'exact tracked discard card is marked for this turn');
  assert.equal(got.deathSentenceSourceUid,sentence.uid,'mark is bound to the exact Death Sentence card');
  assert.equal(g.attachCards('enemy',[got],'enemy',0),true);
  assert.equal(g.state.switchPower,30,'BURST 24 + Death Sentence 6');
  assert.equal(s.melds.length,0,'completed SET still retires normally');
}
console.log('PASS common SQ Death Sentence turns tracking into +6 same-turn BURST value');

// S9 Sleeper: one held owner-turn is enough preparation after the faster board rules.
{
  const g=fresh(),s=g.state.enemy,target=run(g,'player','H',2,3);
  g.state.player.melds=[target];
  const sleeper=g.makeCard('S','9',true,'enemy','S9');sleeper.age=1;
  const h9=g.makeCard('H','9',false,'enemy'),d9=g.makeCard('D','9',false,'enemy');
  s.hand=[sleeper,h9,d9];
  assert.equal(g.submitNewMeld('enemy',[sleeper,h9,d9]),true);
  assert.equal(g.meldFixedActive(target),true,'one-turn prepared Sleeper fixes a chosen opponent meld');
}
console.log('PASS common S9 Sleeper uses one-turn preparation');

// Structural anchors for later same-slot theme comparisons.
for(const sig of [
  "'S7':{n:'검은 탄환',t:'blackBullet',d:'상대 공개 조합에 붙여 스위치를 반환할 때 누적 위력이 10 증가한다.'}",
  "'H7':{n:'행운의 일곱',t:'setHeal3',d:'세트에 들어가면 보호막 12를 얻는다. 직접 버스트를 완성하면 보호막 24를 얻는다.'}",
  "'H8':{n:'응급 보호구',t:'emergencyGear',d:'조합에 들어갈 때 보호막 20을 얻는다. 스위치가 나를 향하면 보호막 32를 얻는다.'}",
  "'C5':{n:'연결고리',t:'connectionLink'",
  "'CJ':{n:'갈아끼우기',t:'freeSwapRecover'",
  "'CK':{n:'조율자',t:'alternateBonus'"
])assert.ok(html.includes(sig),`missing common-card benchmark: ${sig}`);

console.log('COMMON CARD BALANCE PASS 1 OK');

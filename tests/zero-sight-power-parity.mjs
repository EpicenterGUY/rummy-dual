import assert from 'node:assert/strict';
import {makeGame,html} from './helpers/live-game.mjs';

function fresh(){
  const g=makeGame();
  g.state.turn='enemy';
  g.state.phase='action';
  g.state.switchTarget='neutral';
  g.state.switchPower=0;
  g.state.turnToken=31;
  g.state.turnNo=9;
  for(const w of ['player','enemy']){
    const s=g.state[w];
    s.hand=[];s.deck=[];s.spent=[];s.melds=[];
    s.hp=60;s.maxHp=60;s.shield=0;
    s.newMeldCount=0;s.attachCount=0;s.extraAttachRemaining=0;
    s.recoveredThisTurn=false;s.returnedSwitchThisTurn=false;s.meldCleanupUsed=false;
  }
  g.state.discard=[];
  return g;
}
function run(g,owner,suit,start,end){
  const ranks=[];
  for(let v=start;v<=end;v++)ranks.push(v===1?'A':v===11?'J':v===12?'Q':v===13?'K':String(v));
  return {type:'RUN',cards:ranks.map(r=>g.makeCard(suit,r,false,owner)),chain:0,createdTurn:0,createdToken:0,lastTouchedOwnerStart:0,status:g.blankMeldStatus(),themeMeta:{zeroSight:{targetedBy:{player:false,enemy:false},targetedTurn:{player:null,enemy:null}}}};
}

// S7 철갑탄: target setup must beat the common S7 +10 floor.
{
  const g=fresh(),s=g.state.enemy,target=run(g,'player','S',4,6);
  g.state.player.melds=[target];
  g.setZeroSightTarget('enemy',target,{silent:true});
  const armor=g.makeCard('S','7',true,'enemy','ZSS7');
  s.hand=[armor,g.makeCard('H','K',false,'enemy')];
  assert.equal(g.attachCards('enemy',[armor],'player',0),true);
  assert.equal(g.state.switchPower,22,'first RUN extension 10 + ZERO-SIGHT target bonus 12');
}
{
  const g=fresh(),s=g.state.enemy,target=run(g,'player','S',4,6);
  g.state.player.melds=[target];
  g.setZeroSightTarget('enemy',target,{silent:true});
  g.applyOfficialStatus('meld',target,'protect',1,{actor:'player',silent:true});
  const armor=g.makeCard('S','7',true,'enemy','ZSS7');
  s.hand=[armor,g.makeCard('H','K',false,'enemy')];
  assert.equal(g.attachCards('enemy',[armor],'player',0),true);
  assert.equal(g.state.switchPower,26,'protected target gives 10 base + 16 armor-piercing bonus');
  assert.equal(g.officialStatusValue('meld',target,'protect'),0,'armor-piercing consumes protection');
}
console.log('PASS ZERO-SIGHT S7 rewards target setup above common S7');

// S10 장거리 사격: two completed owner turns of preparation deserve a finisher-sized +20.
{
  const g=fresh(),s=g.state.enemy,target=run(g,'player','S',7,9);
  g.state.player.melds=[target];
  g.setZeroSightTarget('enemy',target,{silent:true});
  const long=g.makeCard('S','10',true,'enemy','ZSS10');
  g.ensureHandPreparation(long).turns=2;
  s.hand=[long,g.makeCard('H','K',false,'enemy')];
  assert.equal(g.attachCards('enemy',[long],'player',0),true);
  assert.equal(g.state.switchPower,30,'first RUN extension 10 + prepared Long Shot 20');
}
console.log('PASS ZERO-SIGHT S10 pays off its two-turn preparation');

// H3 호흡 조절: one-turn prep + a live target gives 16 shield and still cycles one card.
{
  const g=fresh(),s=g.state.enemy;
  const target=run(g,'player','C',4,6);
  g.state.player.melds=[target];
  g.setZeroSightTarget('enemy',target,{silent:true});
  const breath=g.makeCard('H','3',true,'enemy','ZSH3');
  const s3=g.makeCard('S','3',false,'enemy'),d3=g.makeCard('D','3',false,'enemy');
  const spare=g.makeCard('C','9',false,'enemy');spare.age=8;
  const draw=g.makeCard('D','K',false,'enemy');
  g.ensureHandPreparation(breath).turns=1;
  s.hand=[breath,s3,d3,spare];
  s.deck=[draw];
  assert.equal(g.submitNewMeld('enemy',[breath,s3,d3]),true);
  assert.equal(s.shield,16,'Breath Control grants shield 16');
  assert.equal(s.hand.length,1,'free cycle preserves hand size after using the 3-card meld');
}
console.log('PASS ZERO-SIGHT H3 is a real prepared defense + cycle package');

// D8 예비 탄창: target attach now looks three cards deep, not only two.
{
  const g=fresh(),s=g.state.enemy,target=run(g,'player','D',5,7);
  g.state.player.melds=[target];
  g.setZeroSightTarget('enemy',target,{silent:true});
  const reserve=g.makeCard('D','8',true,'enemy','ZSD8');
  s.hand=[reserve,g.makeCard('H','K',false,'enemy')];
  s.deck=[
    g.makeCard('C','2',false,'enemy'),
    g.makeCard('C','3',false,'enemy'),
    g.makeCard('C','4',false,'enemy')
  ];
  let seen=0;
  g.requestZeroSightTopOrder=(w,source,count)=>{seen=count;return false};
  assert.equal(g.attachCards('enemy',[reserve],'player',0),true);
  assert.equal(seen,3,'Reserve Magazine inspects the next three acquisitions');
}
console.log('PASS ZERO-SIGHT D8 uses a three-card acquisition window');

for(const text of [
  "'ZSS7':{slot:'S7',themeId:'zero-sight',n:'철갑탄',t:'zsArmorPiercing',d:'내 상대 표적 조합에 붙여 스위치를 반환하면 누적 위력이 12 증가한다. 그 조합의 보호 1을 제거할 수 있었다면 대신 누적 위력이 16 증가한다.'}",
  "'ZSS10':{slot:'S10',themeId:'zero-sight',prepRequired:2,n:'장거리 사격',t:'zsLongShot',d:'손에서 내 턴 종료 2회를 준비한 뒤 내 표적 조합을 이용해 스위치를 반환하면 누적 위력이 20 증가한다.'}",
  "'ZSH3':{slot:'H3',themeId:'zero-sight',prepRequired:1,n:'호흡 조절',t:'zsBreathControl',d:'손에서 내 턴 종료 1회를 준비하고 내 표적이 있는 상태로 사용하면 보호막 16을 얻고 남은 손패 1장을 무료 정비한다.'}",
  "'ZSD8':{slot:'D8',themeId:'zero-sight',n:'예비 탄창',t:'zsReserveMag',d:'내 표적 조합에 이 카드를 붙이면 덱 위 3장의 다음 획득 순서를 정한다.'}"
])assert.ok(html.includes(text),'live text matches ZERO-SIGHT parity contract');

console.log('ZERO-SIGHT POWER PARITY PASS OK');

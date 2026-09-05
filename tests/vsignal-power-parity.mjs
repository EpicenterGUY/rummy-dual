import assert from 'node:assert/strict';
import {makeGame,html} from './helpers/live-game.mjs';

function fresh(){
  const g=makeGame();
  g.state.turn='enemy';
  g.state.phase='action';
  g.state.switchTarget='neutral';
  g.state.switchPower=0;
  g.state.turnToken=21;
  g.state.turnNo=7;
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
function meld(g,type,cards,chain=0){
  return {type,cards,chain,createdTurn:0,createdToken:0,lastTouchedOwnerStart:0,status:g.blankMeldStatus(),themeMeta:{zeroSight:{targetedBy:{player:false,enemy:false},targetedTurn:{player:null,enemy:null}}}};
}

// H10 기념 방송: same-slot common H10 is a meaningful sustain benchmark,
// so the themed RUMMY payoff must no longer be the weaker regen1 + shield12 package.
{
  const g=fresh(),s=g.state.enemy;
  s.hp=40;
  const milestone=g.makeCard('H','10',true,'enemy','VSH10');
  assert.equal(g.handleVSignalFullThemeEvent({event:'onRummy',actor:'enemy',lastCards:[milestone],turnToken:g.state.turnToken}),true);
  assert.equal(s.hp,48,'Milestone Broadcast heals 8');
  assert.equal(s.shield,16,'Milestone Broadcast grants shield 16');
  assert.equal(g.officialStatusValue('player',s,'regen'),1,'Milestone Broadcast keeps regen 1');
}
console.log('PASS V-SIGNAL H10 reaches a real sustain sidegrade');

// HK 100만 구독: RUMMY arms the next public card, then that card gains protect1 + shield16.
{
  const g=fresh(),s=g.state.enemy;
  const million=g.makeCard('H','K',true,'enemy','VSHK');
  assert.equal(g.handleVSignalFullThemeEvent({event:'onRummy',actor:'enemy',lastCards:[million],turnToken:g.state.turnToken}),true);
  assert.equal(s.vMillionSubReady,true,'Million Subs arms after RUMMY');
  const played=g.makeCard('C','4',false,'enemy');
  assert.equal(g.handleVSignalFullThemeEvent({event:'onMeldCreate',actor:'enemy',cards:[played],meld:null,turnToken:g.state.turnToken}),true);
  assert.equal(s.vMillionSubReady,false,'Million Subs is consumed by the next public card');
  assert.equal(s.shield,16,'Million Subs grants shield 16 on the protected public card');
  assert.equal(g.officialStatusValue('card',played,'protect'),1,'Million Subs grants protect 1');
}
console.log('PASS V-SIGNAL HK has delayed protection plus a meaningful shield floor');

// D2 신인 2기생: the faster two-new-meld core rule should become a real themed payoff.
// First new SET only cycles; second new meld this turn additionally draws one.
{
  const g=fresh(),s=g.state.enemy;
  s.newMeldCount=1;
  const rookie=g.makeCard('D','2',true,'enemy','VSD2');
  const s2=g.makeCard('S','2',false,'enemy');
  const h2=g.makeCard('H','2',false,'enemy');
  const spare=g.makeCard('C','9',false,'enemy');spare.age=6;
  const drawA=g.makeCard('S','K',false,'enemy');
  const drawB=g.makeCard('D','8',false,'enemy');
  s.hand=[rookie,s2,h2,spare];
  s.deck=[drawB,drawA];
  assert.equal(g.submitNewMeld('enemy',[rookie,s2,h2]),true);
  assert.equal(s.newMeldCount,2,'Rookie SET is the second new meld');
  assert.equal(s.hand.length,2,'second-new-meld bonus leaves one net extra card after the free cycle');
  assert.ok(s.melds.some(m=>m.type==='SET'&&m.cards.some(c=>c.uid===rookie.uid)),'Rookie still creates an ordinary legal 3SET');
}
console.log('PASS V-SIGNAL D2 converts the second-new-meld window into +1 plus cycle');

// H7 팬 서비스: mixed-ownership board play is more conditional than ordinary H7,
// so its base shield is 16 while a returning action still heals 4.
{
  const g=fresh(),s=g.state.enemy,p=g.state.player;
  s.hp=50;
  const fan=g.makeCard('H','7',true,'enemy','VSH7');
  const spare=g.makeCard('D','K',false,'enemy');
  s.hand=[fan,spare];
  p.melds=[meld(g,'RUN',[
    g.makeCard('H','4',false,'player'),
    g.makeCard('H','5',false,'player'),
    g.makeCard('H','6',false,'player')
  ])];
  assert.equal(g.attachCards('enemy',[fan],'player',0),true);
  assert.equal(s.shield,16,'Fan Service mixed-ownership entry grants shield 16');
  assert.equal(s.hp,54,'Fan Service returning action heals 4');
  assert.equal(g.state.switchPower,10,'the ordinary first RUN extension power remains unchanged');
}
console.log('PASS V-SIGNAL H7 is a conditional mixed-board sidegrade, not a raw H7 downgrade');

for(const text of [
  "'VSH7':{slot:'H7',themeId:'v-signal',n:'팬 서비스',t:'vFanService',d:'이 카드가 들어간 공개 조합에 양쪽 소유 카드가 모두 있으면 보호막 16을 얻는다.",
  "'VSH10':{slot:'H10',themeId:'v-signal',n:'기념 방송',t:'vMilestoneBroadcast',d:'이 카드 사용으로 러미하면 체력 8을 회복하고 재생 1과 보호막 16을 얻는다.'}",
  "'VSHK':{slot:'HK',themeId:'v-signal',n:'100만 구독',t:'vMillionSubs',d:'이 카드 사용으로 러미하면 다음에 공개 조합에 내는 내 카드 1장에 보호 1을 부여하고 보호막 16을 얻는다.'}",
  "'VSD2':{slot:'D2',themeId:'v-signal',n:'신인 2기생',t:'vRookieSet',d:'이 카드로 새 3장 세트를 만들면 남은 손패 1장을 덱 아래로 보내고 1장 뽑는 무료 정비를 할 수 있다. 이번 턴 두 번째 새 조합이라면 정비 전에 카드 1장을 추가로 뽑는다.'}"
]) assert.ok(html.includes(text),'live text matches V-SIGNAL parity contract');

console.log('V-SIGNAL POWER PARITY PASS OK');

import assert from 'node:assert/strict';
import {fresh,plain,named,meld,run} from './helpers/v3-fixture.mjs';
const value=(g,c)=>g.officialStatusValue('card',c,'unstable');
const grant=(g,c,n=1,actor=c.owner)=>g.applyOfficialStatus('card',c,'unstable',n,{actor,silent:true});
const start=(g,w)=>{g.state.turn=w;g.turnStart(w)};

// Only positive, finite integer countdowns on active cards are legal.
{
 const g=fresh(),c=named(g,'H9');g.state.player.hand=[c];
 for(const n of [-1,0,0.5,NaN,Infinity,'1',Number.MAX_SAFE_INTEGER+1])assert.equal(grant(g,c,n),0);
 assert.equal(g.applyOfficialStatus('player',g.state.player,'unstable',1,{actor:'player'}),0);
 assert.equal(grant(g,g.state.player.deck[0]),0);
 assert.equal(grant(g,c,4),4);assert.equal(grant(g,c,7),4);assert.equal(grant(g,c,2),2);
 assert.match(g.cardHTML(c),/unstableCardMark/);g.renderDetail(c);assert.match(g.document.getElementById('detail').innerHTML,/불안정 2.*내 턴 종료/);
}
// Own-turn grants expire now; off-turn grants wait for the recorded owner's end.
for(const owner of ['player','enemy']){
 const g=fresh(),c=plain(g,'S','8',owner);g.state.switchPower=0;g.state[owner].hand=[c];assert.equal(grant(g,c),1);
 g.turnEnd('player');assert.equal(value(g,c),owner==='player'?0:1);assert.equal(g.state[owner].spent.includes(c),owner==='player');
 if(owner==='enemy'){start(g,'enemy');g.turnEnd('enemy');assert.equal(value(g,c),0);assert.ok(g.state.enemy.spent.includes(c))}
}
{
 const g=fresh(),c=plain(g,'S','8');g.state.switchPower=0;g.state.player.hand=[c];grant(g,c,3);
 g.turnEnd('player');g.turnEnd('player');assert.equal(value(g,c),2,'the same turn end cannot decrement twice');
 start(g,'enemy');g.turnEnd('enemy');assert.equal(value(g,c),2);
 start(g,'player');g.turnEnd('player');assert.equal(value(g,c),1);
 start(g,'enemy');g.turnEnd('enemy');start(g,'player');g.turnEnd('player');assert.ok(g.state.player.spent.includes(c));assert.equal(value(g,c),0);
}
// Recovery, public relocation, and ownership changes keep the original deadline.
{
 const g=fresh(),m=run(g,'player','S',['5','6','7','8']),c=m.cards.at(-1);g.state.switchPower=0;grant(g,c,3);
 assert.equal(g.recoverSpecificFromMeld('player',m,c),c);assert.equal(value(g,c),3);
 g.state.player.hand=g.state.player.hand.filter(x=>x!==c);c.owner='enemy';g.enterHand('enemy',c);
 assert.equal(grant(g,c,2,'enemy'),2);assert.equal(c.officialStatus.unstableOwner,'player');
 g.turnEnd('player');assert.equal(value(g,c),1);
 start(g,'enemy');g.turnEnd('enemy');assert.equal(value(g,c),1,'new controller does not tick the old timer');
 start(g,'player');g.turnEnd('player');assert.ok(g.state.enemy.spent.includes(c));assert.equal(value(g,c),0);
}
{
 const g=fresh(),m=run(g,'player','S',['5','6','7','8']),dst=run(g,'enemy','S',['9','10','J']),c=m.cards.at(-1);g.state.switchPower=0;grant(g,c,2);
 assert.ok(g.moveCardBetweenMelds('player',c,m,dst));g.turnEnd('player');assert.equal(value(g,c),1);assert.equal(c.officialStatus.unstableOwner,'player');
}
// Entering discard, deck, or spent clears the countdown before immediate reacquisition.
for(const route of ['discard','bottom','maintenance','retire','cut','cost','recirculate']){
 const g=fresh(),c=plain(g,'H','6');g.state.switchPower=0;g.state.player.hand=[c,plain(g,'C','K')];grant(g,c,3);
 if(route==='discard'){g.discardSpecificHandCard('player',c);assert.equal(g.acquireDiscardCard('player',0),c)}
 if(route==='bottom'){g.state.player.deck=[];assert.equal(g.bottomSpecificHandCard('player',c),true);assert.equal(g.drawOne('player'),c)}
 if(route==='maintenance'){assert.equal(g.performMaintenance('player',[c]).length,1);assert.ok(g.state.player.deck.includes(c))}
 if(['retire','cut','cost'].includes(route)){
  g.state.player.hand=g.state.player.hand.filter(x=>x!==c);const m=meld(g,'player',[c,...['7','8','9'].map(r=>plain(g,'H',r))]);
  if(route==='retire')g.retireMeld('player',0);
  if(route==='cut')assert.equal(g.cutOppositeEnd('enemy','player',m,m.cards.at(-1)),true);
  if(route==='cost')assert.equal(g.spendPointBlankMeldCard('player',m),c);
 }
 if(route==='recirculate')g.fullRecirculation('test');
 assert.equal(value(g,c),0,`${route}: inactive entry ends the timer`);
 assert.equal(c.officialStatus.unstableOwner,null);
}
// Hostile status grants use protection and exact cover redirection, never insurance.
for(const scope of ['card','meld']){
 const g=fresh(),m=run(g,'enemy','H',['7','8','9']),c=m.cards[0];g.applyOfficialStatus(scope,scope==='card'?c:m,'protect',1,{silent:true});
 assert.equal(grant(g,c,0,'player'),0);assert.equal(g.officialStatusValue(scope,scope==='card'?c:m,'protect'),1,'invalid input cannot spend protection');
 assert.equal(grant(g,c,2,'player'),0);assert.equal(value(g,c),0);assert.equal(g.officialStatusValue(scope,scope==='card'?c:m,'protect'),0);
}
{
 const g=fresh(),cover=named(g,'PBH7','enemy'),target=plain(g,'H','8','enemy'),m=meld(g,'player',[cover,target,plain(g,'H','9')]);g.setPointBlankClash('enemy',m);
 assert.equal(grant(g,target,2,'player'),2);assert.equal(value(g,target),0);assert.equal(value(g,cover),2);assert.equal(cover.officialStatus.unstableOwner,'enemy');
}
for(const ending of ['win','loss','draw']){
 const g=fresh(),c=g.state.player.hand[0];grant(g,c,3);
 if(ending==='draw')g.resolveCirculationStalemate();else{g.state[ending==='win'?'enemy':'player'].cores=0;g.checkGameOver()}
 assert.equal(g.state.gameOver,true);assert.equal(value(g,c),0);assert.equal(grant(g,c,1),0);assert.equal(g.expireOwnerUnstableCards('player'),0);
}
console.log('Unstable lifecycle: strict grants, owner deadlines, transfer, inactive zones, protection and battle cleanup');

import assert from 'node:assert/strict';
import {fresh,plain,named,meld,run} from './helpers/v3-fixture.mjs';
const grant=(g,c,n=1)=>g.applyOfficialStatus('card',c,'unstable',n,{actor:c.owner,silent:true});
const value=(g,c)=>g.officialStatusValue('card',c,'unstable');

for(const type of ['RUN','SET']){
 const g=fresh(),cards=type==='RUN'?['5','6','7','8'].map(r=>plain(g,'S',r)):['S','H','D','C'].map(s=>plain(g,s,'5'));
 const m=meld(g,'player',cards,type,{chain:3}),c=cards.at(-1);g.state.switchPower=0;grant(g,c);
 g.applyOfficialStatus('card',c,'fixed',1,{silent:true});g.applyOfficialStatus('card',c,'protect',1,{silent:true});g.applyOfficialStatus('meld',m,'fracture',1,{actor:'enemy'});
 let spent=0,recovery=0;g.subscribeEffectEvent(p=>{if(p.event==='onRecover')recovery++;if(p.event==='onMeldSpend'){spent++;assert.equal(value(g,c),0);assert.ok(g.state.player.spent.includes(c));assert.equal(g.meldType(m.cards),type)}});
 g.turnEnd('player');assert.equal(m.cards.length,3);assert.equal(m.chain,type==='RUN'?2:3);assert.equal(g.state.player.hp,34);assert.equal(spent,1);assert.equal(recovery,0);
 assert.equal(g.state.player.newMeldCount,0);assert.equal(g.state.player.returnedSwitchThisTurn,false);assert.equal(g.state.player.recoveredThisTurn,false);
 assert.equal(c.officialStatus.protect,1,'expiry is not hostile interference and cannot spend protection');
}
// Missing interiors and three-card melds retire once; whole retirement does not fire fracture.
for(const length of [3,4,5]){
 const g=fresh(),m=run(g,'player','S',['4','5','6','7','8'].slice(0,length)),c=m.cards[1],survivor=m.cards[0];g.state.switchPower=0;grant(g,c);
 g.applyOfficialStatus('card',survivor,'comeback',1,{silent:true});g.applyOfficialStatus('meld',m,'fracture',1,{actor:'enemy'});
 let retires=0,spends=0;g.subscribeEffectEvent(p=>{if(p.event==='onRetire')retires++;if(p.event==='onMeldSpend')spends++});
 g.turnEnd('player');assert.equal(g.state.player.melds.length,0);assert.equal(retires,1);assert.equal(spends,0);assert.equal(g.state.player.hp,40);assert.ok(g.state.player.hand.includes(survivor));
 assert.equal(g.state.player.spent.filter(x=>x===c).length,1);assert.equal(m.status.fracture,0);
}
// Resolve multiple expiries atomically, preserving returns without a second consumption.
for(const remainValid of [false,true]){
 const g=fresh(),m=run(g,'player','S',remainValid?['4','5','6','7','8']:['4','5','6','7']),a=m.cards[0],b=m.cards.at(-1);g.state.switchPower=0;
 grant(g,a);grant(g,b);g.applyOfficialStatus('card',a,'comeback',1,{silent:true});g.applyOfficialStatus('card',b,'comeback',1,{silent:true});
 let retires=0,spends=0;g.subscribeEffectEvent(p=>{if(p.event==='onRetire')retires++;if(p.event==='onMeldSpend'){spends++;assert.equal(m.cards.length,3,'all due cards leave before reactions')}});
 g.turnEnd('player');assert.equal(retires,remainValid?0:1);assert.equal(spends,remainValid?2:0);assert.equal(value(g,a)+value(g,b),0);
 for(const c of [a,b])assert.equal(g.state.player.hand.includes(c),!remainValid);
 g.turnEnd('player');assert.equal(retires,remainValid?0:1);assert.equal(spends,remainValid?2:0);
}
{
 const g=fresh(),m=run(g,'player','H',['4','5','6']),expired=m.cards[0],returning=m.cards[1];g.state.switchPower=0;grant(g,expired);grant(g,returning,3);
 g.applyOfficialStatus('card',returning,'comeback',1,{silent:true});g.turnEnd('player');assert.ok(g.state.player.hand.includes(returning));assert.equal(value(g,returning),2,'another returning card keeps its decremented live timer');
}
// Silence, fixed and passive roles cannot stop expiry; invalid material roles are rechecked.
{
 const g=fresh(),structural=named(g,'C4'),m=meld(g,'player',[plain(g,'C','A'),structural,plain(g,'C','3'),plain(g,'C','5')]);g.state.switchPower=0;
 assert.equal(g.meldType(m.cards),'RUN');grant(g,structural);g.turnEnd('player');assert.equal(g.state.player.melds.length,0);
}
{
 const g=fresh(),c=named(g,'HK');g.state.player.hand=[c];c.healCharge=3;g.state.switchTarget='player';g.state.switchPower=20;grant(g,c);
 g.applyOfficialStatus('card',c,'silence',1,{actor:'player',silent:true});g.turnEnd('player');assert.ok(g.state.player.spent.includes(c));assert.equal(g.state.player.hp,20,'expiry precedes end-turn explosion');
}
// A lethal departure is already atomic and cannot continue into the pending bomb.
{
 const g=fresh(),m=run(g,'player','S',['4','5','6','7']),c=m.cards.at(-1),waiting=plain(g,'H','8');g.state.player.hand=[waiting];
 g.state.player.hp=2;g.state.player.cores=1;g.state.switchPower=30;g.state.switchTarget='player';grant(g,c);grant(g,waiting,3);g.applyOfficialStatus('meld',m,'fracture',1,{actor:'enemy'});
 let detonate=0;g.subscribeEffectEvent(p=>{if(p.event==='onDetonate')detonate++});g.endPlayerTurn();assert.equal(g.state.gameOver,true);assert.equal(g.state.phase,'over');assert.equal(g.state.turn,'player');assert.equal(m.cards.length,3);assert.ok(g.state.player.spent.includes(c));assert.equal(value(g,waiting),0);assert.equal(detonate,0);assert.equal(g.state.switchPower,0,'core break still clears the bomb');
}
// A reaction cannot run this end twice or consume a newly granted countdown immediately.
{
 const g=fresh(),m=run(g,'player','S',['4','5','6','7']),c=m.cards.at(-1),waiting=g.state.player.hand[0];g.state.switchPower=0;grant(g,c);
 let spends=0;g.subscribeEffectEvent(p=>{if(p.event==='onMeldSpend'){spends++;assert.equal(g.expireOwnerUnstableCards('player'),0);grant(g,waiting)}});
 g.turnEnd('player');g.turnEnd('player');assert.equal(spends,1);assert.equal(value(g,waiting),1);
 g.state.turn='enemy';g.turnStart('enemy');g.turnEnd('enemy');g.state.turn='player';g.turnStart('player');g.turnEnd('player');assert.ok(g.state.player.spent.includes(waiting));assert.equal(value(g,waiting),0);
}
// Emptying a hand through expiry is cleanup, not an action or a recursive Rummy turn end.
{
 const g=fresh(),c=plain(g,'H','8');g.state.player.hand=[c];g.state.switchPower=0;grant(g,c);let rummy=0;g.subscribeEffectEvent(p=>{if(p.event==='onRummy')rummy++});
 g.endPlayerTurn();assert.equal(g.state.turn,'enemy');assert.equal(g.state.player.hand.length,0);assert.equal(rummy,0);assert.ok(g.state.player.spent.includes(c));
}
console.log('Unstable expiry: valid removal, whole retirement, simultaneous timers, return, fracture and turn-end ordering');

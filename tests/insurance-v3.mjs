import assert from 'node:assert/strict';
import {fresh,plain,named,meld,run} from './helpers/v3-fixture.mjs';
const value=(g,c)=>g.officialStatusValue('card',c,'unstable');
function fixture(owner='enemy'){
 const g=fresh(),ins=named(g,'H9',owner),m=meld(g,owner,[plain(g,'H','7',owner),plain(g,'H','8',owner),ins,plain(g,'H','10',owner)]);
 g.state.switchPower=0;return{g,ins,m,actor:g.other(owner)};
}
// Both player and CPU use the same real cut path. Nothing leaves on interception.
for(const owner of ['player','enemy']){
 const {g,ins,m,actor}=fixture(owner);g.state.turn=actor;const c=m.cards[0],last=m.cards.at(-1),power=g.state.switchPower;
 let spent=0;g.subscribeEffectEvent(p=>{if(p.event==='onMeldSpend')spent++});
 assert.equal(g.cutOppositeEnd(actor,owner,m,last),false);assert.equal(m.cards.length,4);assert.equal(spent,0);assert.equal(value(g,ins),1);assert.equal(ins.insuranceUsedBattleId,g.state.battleId);
 assert.equal(g.cutOppositeEnd(actor,owner,m,last),true,'second interference is not blocked');assert.ok(g.state[owner].spent.includes(c));assert.equal(value(g,ins),1);
 g.turnEnd(actor);assert.equal(value(g,ins),1);g.state.turn=owner;g.turnStart(owner);g.turnEnd(owner);assert.equal(g.state[owner].melds.length,0);assert.equal(value(g,ins),0);assert.equal(g.state.switchPower,power);
}
// Insurance may protect itself, and delaying its cost does not require a legal removal now.
{
 const g=fresh(),ins=named(g,'H9','enemy'),m=meld(g,'enemy',[ins,...['10','J','Q'].map(r=>plain(g,'H',r,'enemy'))]);
 assert.equal(g.cutOppositeEnd('player','enemy',m,m.cards.at(-1)),false);assert.ok(m.cards.includes(ins));assert.equal(value(g,ins),1);
}
{
 const {g,ins,m}=fixture();const destination=run(g,'player','H',['4','5','6']),target=m.cards[0],choice={meld:m,card:target};
 assert.ok(g.extortionCandidates('player',destination).some(x=>x.card===target));
 assert.equal(g.moveExtortedCard('player',destination,choice),false);assert.ok(m.cards.includes(target));assert.equal(destination.cards.length,3);assert.equal(value(g,ins),1);
 assert.equal(g.moveExtortedCard('player',destination,choice),true);assert.ok(destination.cards.includes(target));
}
for(const gate of ['comeback','silence','used','ownTarget','wrongOwner']){
 const {g,ins,m}=fixture(),target=m.cards[0];
 if(gate==='comeback')g.applyOfficialStatus('card',ins,'comeback',1,{silent:true});
 if(gate==='silence')g.applyOfficialStatus('card',ins,'silence',1,{actor:'enemy',silent:true});
 if(gate==='used')ins.insuranceUsedBattleId=g.state.battleId;
 if(gate==='ownTarget')target.owner='player';
 if(gate==='wrongOwner')ins.owner='player';
 assert.equal(g.cutOppositeEnd('player','enemy',m,m.cards.at(-1)),true,gate);assert.equal(value(g,ins),0);assert.ok(g.state[target.owner].spent.includes(target));
}
for(const scope of ['card','meld']){
 const {g,ins,m}=fixture(),target=m.cards[0];g.applyOfficialStatus(scope,scope==='card'?target:m,'protect',1,{silent:true});
 assert.equal(g.cutOppositeEnd('player','enemy',m,m.cards.at(-1)),false);assert.equal(value(g,ins),0);assert.equal(ins.insuranceUsedBattleId,null);
 assert.equal(g.cutOppositeEnd('player','enemy',m,m.cards.at(-1)),false);assert.equal(value(g,ins),1,'insurance follows spent protection');
}
for(const status of ['silence','unstable']){
 const {g,ins,m}=fixture();assert.equal(g.applyOfficialStatus('card',m.cards[0],status,1,{actor:'player',silent:true}),1);
 assert.equal(ins.insuranceUsedBattleId,null);assert.equal(value(g,ins),0);assert.ok(m.cards.includes(ins),'status interference cannot invoke cut/theft insurance');
}
// Use is bound to the physical card for the battle, through hand, discard and transfer.
{
 const {g,ins,m}=fixture();assert.equal(g.cutOppositeEnd('player','enemy',m,m.cards.at(-1)),false);
 g.retireMeld('enemy',0,'test',{preserveCards:[ins]});assert.ok(g.state.enemy.hand.includes(ins));assert.equal(value(g,ins),1);
 g.discardSpecificHandCard('enemy',ins);assert.equal(value(g,ins),0);assert.equal(g.acquireDiscardCard('player',0),ins);assert.equal(ins.owner,'player');
 g.state.player.hand=g.state.player.hand.filter(x=>x!==ins);const rebuilt=meld(g,'player',[plain(g,'H','7'),plain(g,'H','8'),ins,plain(g,'H','10')]);
 assert.equal(g.cutOppositeEnd('enemy','player',rebuilt,rebuilt.cards.at(-1)),true);assert.equal(value(g,ins),0);
 g.renderDetail(ins);assert.match(g.document.getElementById('detail').innerHTML,/보험 사용 완료/);
}
// A card on an opponent's board is still protected according to its controller.
{
 const {g,ins,m}=fixture();g.state.enemy.melds=[];g.state.player.melds=[m];
 assert.equal(g.insuranceBlocks('player','player',m,m.cards[0],'cut'),true);assert.equal(value(g,ins),1);
}
console.log('Insurance: actual cut/theft, self target, controller, comeback/silence/protection, delayed cost and battle-only use');

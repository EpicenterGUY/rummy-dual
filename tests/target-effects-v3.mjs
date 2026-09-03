import assert from 'node:assert/strict';
import {fresh,plain,named,meld,run,nextTurn} from './helpers/v3-fixture.mjs';

{
 const g=fresh(),c=named(g,'ZSCA'),cards=[c,plain(g,'C',2),plain(g,'C',3)],kept=g.state.player.hand[0];g.state.player.hand.push(...cards);
 assert.equal(g.submitNewMeld('player',cards),'choice');const m=g.state.player.melds[0];assert.equal(g.zeroSightTargetMeld('player'),m);assert.equal(g.meldMarkValue(m,'player'),1);
 assert.equal(g.state.pendingEffectChoice.allowSkip,true,'Observer cycle is optional, including with just one remaining card');g.resolveEffectChoice('__skip__');assert.equal(g.state.player.hand[0],kept);
}
{
 const g=fresh(),old=run(g,'player','H',[4,5,6]),next=run(g,'enemy','D',[4,5,6]);g.setZeroSightTarget('player',old);g.applyOfficialStatus('meld',old,'mark',1,{actor:'player'});
 const c=named(g,'ZSC2'),cards=[plain(g,'C','A'),c,plain(g,'C',3)];g.state.player.hand.push(...cards);
 assert.equal(g.submitNewMeld('player',cards),'choice');const option=g.state.pendingEffectChoice.options.find(o=>o.entry.m===next);g.resolveEffectChoice(option.key);
 assert.equal(g.zeroSightTargetMeld('player'),next);assert.equal(g.meldMarkValue(next,'player'),1);assert.equal(g.meldMarkValue(old,'player'),1,'relocating the unique target does not erase its old mark');
}
{
 const g=fresh(),m=run(g,'enemy','C',[2,3,4]);m.cards[1].owner='player';const recovery=run(g,'player','H',[8,9,10,'J']);g.recoverSpecificFromMeld('player',recovery,recovery.cards.at(-1));
 const c=named(g,'ZSC5');g.state.player.hand.push(c);assert.equal(g.attachCards('player',[c],'enemy',0),true);assert.equal(g.zeroSightTargetMeld('player'),m);assert.equal(g.meldMarkValue(m,'player'),1);
}
{
 const g=fresh(),m=run(g,'enemy','C',[2,3,4]),cards=[named(g,'ZSC5'),plain(g,'C',6)];g.state.player.hand.push(...cards);
 assert.equal(g.attachCards('player',cards,'enemy',0),true);assert.equal(g.zeroSightTargetMeld('player'),null,'another card from the same action is not an already-present ally');
}
{
 const g=fresh(),record=named(g,'ZSC6'),m=meld(g,'player',[plain(g,'C',4),plain(g,'C',5),record]);g.setZeroSightTarget('player',m);
 const first=plain(g,'C',7);g.state.player.hand.push(first);g.attachCards('player',[first],'player',0);assert.equal(g.state.player.status.loaded||0,0,'the observation must survive to the next owner turn');
 nextTurn(g);g.state.switchTarget='player';const second=plain(g,'C',8);g.state.player.hand.push(second);g.attachCards('player',[second],'player',0);assert.equal(g.state.player.status.loaded,8);
 const third=plain(g,'C',9);g.state.player.hand.push(third);g.attachCards('player',[third],'player',0);assert.equal(g.state.player.status.loaded,8,'continuation does not pay a second observation or consume loading');
}
{
 const g=fresh(),drone=named(g,'ZSCJ');meld(g,'player',[plain(g,'C',10),drone,plain(g,'C','Q')]);g.state.turn='enemy';const hand=g.state.player.hand.length,deck=g.state.player.deck.length;
 for(const rank of [4,5]){const cards=['S','H','D'].map(s=>plain(g,s,rank,'enemy'));g.state.enemy.hand.push(...cards);assert.equal(g.submitNewMeld('enemy',cards),true)}
 assert.equal(g.zeroSightTargetMeld('player'),g.state.enemy.melds[0]);assert.equal(g.meldMarkValue(g.state.enemy.melds[0],'player'),1);assert.equal(g.meldMarkValue(g.state.enemy.melds[1],'player'),0);
 assert.equal(g.state.player.hand.length,hand);assert.equal(g.state.player.deck.length,deck,'Drone no longer cycles cards');
}
{
 const g=fresh(),c=named(g,'ZSD6'),m=run(g,'enemy','D',[3,4,5]);g.state.player.hand.push(c);g.setZeroSightTarget('player',m);
 for(const actor of ['player','enemy'])g.applyOfficialStatus('meld',m,'mark',1,{actor});
 Object.assign(g.state.player.status,{loaded:10,damp:15,overheat:8});g.state.enemy.shield=7;g.state.enemy.status.endure=8;g.state.switchPower=30;
 assert.equal(g.attachCards('player',[c],'enemy',0),true);assert.equal(g.state.switchPower,55,'30 + max(0,10+10+8-15) + min(12,55-43)');assert.equal(g.state.player.hp,36);
 assert.equal(g.meldMarkValue(m,'player'),0);assert.equal(g.meldMarkValue(m,'enemy'),1);
}
for(const mode of ['blocked','flat','damped']){
 const g=fresh(),m=run(g,'enemy','D',[3,4,5]);g.setZeroSightTarget('player',m);g.applyOfficialStatus('meld',m,'mark',1,{actor:'player'});g.state.player.status.damp=100;
 const effects=[{kind:'ballistics',meld:m}];if(mode==='blocked')g.state.switchTarget='enemy';
 const result=g.returnSwitch('player',10,'test',{flat:mode==='flat',targetReturnEffects:effects});
 if(mode==='damped'){assert.equal(g.state.switchPower,32,'precision is added after damping');assert.equal(g.meldMarkValue(m,'player'),0)}
 else{assert.equal(g.state.switchPower,20);assert.equal(g.meldMarkValue(m,'player'),1);assert.equal(g.state.player.status.damp,100);if(mode==='blocked')assert.equal(result.blocked,true)}
}
{
 const g=fresh(),safe=named(g,'ZSH7');meld(g,'player',[plain(g,'H',5),plain(g,'H',6),safe]);const target=run(g,'enemy','D',[2,3,4,5,6,7]);target.cards[0].owner='player';target.cards.at(-1).owner='player';g.setZeroSightTarget('player',target);
 for(const c of [target.cards.at(-1),target.cards[0]])assert.equal(g.recoverSpecificFromMeld('player',target,c),c);
 assert.equal(g.state.player.status.endure,8);assert.equal(g.state.player.shield,0);
}
{
 const g=fresh(),trace=named(g,'ZSS9');meld(g,'player',[plain(g,'S',7),plain(g,'S',8),trace]);const target=run(g,'enemy','H',[3,4,5]);g.setZeroSightTarget('player',target);g.state.turn='enemy';g.state.switchTarget='enemy';
 const c=plain(g,'H',6,'enemy');g.state.enemy.hand.push(c);assert.equal(g.attachCards('enemy',[c],'enemy',0),true);assert.equal(g.state.player.status.loaded,12);
 g.emitEffectEvent('onAttach',{actor:'enemy',meld:target,returned:true,targetedBy:['player']});assert.equal(g.state.player.status.loaded,12);
 g.retireMeld('player',0);nextTurn(g);g.returnSwitch('player',10);assert.equal(g.state.switchPower,52,'shared loading survives the source card retiring');assert.equal(g.state.player.status.loaded,0);
}
for(const prepared of [1,2]){
 const g=fresh(),c=named(g,'ZSS10'),target=run(g,'enemy','S',[7,8,9]);g.state.player.hand.push(c);g.setZeroSightTarget('player',target);g.applyOfficialStatus('meld',target,'mark',1,{actor:'player'});g.state.player.status.damp=20;
 for(let i=0;i<prepared;i++)g.advanceHandPreparation('player');assert.equal(g.attachCards('player',[c],'enemy',0),true);
 assert.equal(g.state.switchPower,prepared===2?34:20);assert.equal(g.meldMarkValue(target,'player'),prepared===2?0:1);
}
// Conditions are read from the completed departure packet, even after fracture has been consumed.
for(const move of [false,true])for(const fractured of [false,true]){
 const g=fresh(),dead=named(g,'ZSSQ'),m=meld(g,'enemy',[plain(g,'S',9,'enemy'),plain(g,'S',10,'enemy'),plain(g,'S','J','enemy'),dead]);g.setZeroSightTarget('player',m);g.state.turn='enemy';
 if(fractured)g.applyOfficialStatus('meld',m,'fracture',1,{actor:'player'});const leaving=m.cards[0];
 if(move){const dst=run(g,'enemy','S',[6,7,8]);assert.ok(g.moveCardBetweenMelds('enemy',leaving,m,dst))}else assert.equal(g.recoverSpecificFromMeld('enemy',m,leaving),leaving);
 assert.equal(g.state.enemy.status.damp||0,fractured?0:8);assert.equal(g.state.enemy.status.vulnerable||0,fractured?1:0);assert.equal(g.state.enemy.hp,fractured?34:40);
}
// Physical return order decides which card spends the shared mark; no card can spend it twice.
{
 const g=fresh(),m=run(g,'enemy','S',[10,'J','Q']);g.setZeroSightTarget('player',m);g.applyOfficialStatus('meld',m,'mark',1,{actor:'player'});g.state.switchPower=50;
 g.returnSwitch('player',10,'test',{targetReturnEffects:[{kind:'ballistics',meld:m},{kind:'oneShot',meld:m}]});assert.equal(g.state.switchPower,70);assert.equal(g.state.player.hp,35,'ONE SHOT overheats when an earlier effect already consumed the mark');
}
// DQ: all permutations, original ownership, stale choice protection, and an actual new-meld continuation.
{
 const g=fresh(),cards=[named(g,'DQ'),plain(g,'S','Q'),plain(g,'H','Q')];g.state.player.hand.push(...cards);const top=[plain(g,'S',2),plain(g,'H',3,'enemy'),plain(g,'C',4)];g.state.discard=[plain(g,'D','A','enemy'),...top];const owners=new Map(top.map(c=>[c.uid,c.owner]));
 assert.equal(g.submitNewMeld('player',cards),'choice');assert.equal(g.state.pendingEffectChoice.options.length,6);
 const option=g.state.pendingEffectChoice.options[3],expected=Array.from(option.order,c=>c.uid);g.resolveEffectChoice(option.key);assert.deepEqual(g.state.discard.slice(-3).map(c=>c.uid),expected);
 for(const c of top)assert.equal(c.owner,owners.get(c.uid));assert.equal(g.state.player.newMeldCount,1);assert.equal(g.state.player.melds.length,1);
 const source=named(g,'DQ');g.requestDiscardOrder('player',source);const freshTop=plain(g,'H',8);g.state.discard.push(freshTop);const ids=g.state.discard.map(c=>c.uid);g.resolveEffectChoice(g.state.pendingEffectChoice.options[0].key);assert.deepEqual(g.state.discard.map(c=>c.uid),ids,'a changed pile is never overwritten by an old choice');
}
console.log('Target effects: all ZERO-SIGHT wave-three reactions, timing, shared mark spending, precision and discard order passed');

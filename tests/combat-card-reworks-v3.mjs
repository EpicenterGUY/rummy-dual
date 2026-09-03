import assert from 'node:assert/strict';
import {fresh,plain,named,run,nextTurn} from './helpers/v3-fixture.mjs';
// Transfusion reacts only to real healing while public on its controller's turn.
for(const board of ['player','enemy']){
 const g=fresh(),p=g.state.player,c=named(g,'H6'),m=run(g,board,'H',['4','5']);m.cards.push(c);
 const heals=[];g.subscribeEffectEvent(e=>{if(e.event==='onHeal')heals.push(e.amount)});
 assert.equal(g.heal('player',3),12);assert.equal(p.status.endure||0,6);assert.deepEqual(heals,[12]);
 g.heal('player',2);assert.equal(p.status.endure||0,6,'one heal reaction each own turn');
 nextTurn(g);p.hp=59;g.heal('player',9);assert.equal(p.status.endure||0,6,'overhealing counts only actual 1 HP and floors half');
 p.hp=20;g.heal('player',9);assert.equal(p.status.endure||0,14,'zero half did not consume gate; real 36 HP capped to 8');
 g.addShield('player',2);assert.equal(p.shield,8,'old hand-held shield multiplier is removed');
}
{
 const g=fresh(),p=g.state.player,c=named(g,'H6');p.hand.push(c);g.heal('player',4);assert.equal(p.status.endure||0,0,'hand cannot trigger a public reaction');
 const m=run(g,'player','H',['4','5']);m.cards.push(c);p.hand=p.hand.filter(x=>x!==c);g.state.turn='enemy';p.hp=30;g.heal('player',3);assert.equal(p.status.endure||0,0,'opponent turn cannot trigger owner-turn healing reward');
}
// Life Support keeps six-card RUMMY and uses 12 actual HP / regeneration / persistent defense.
for(const power of [59,60]){
 const g=fresh(),p=g.state.enemy;g.state.turn='enemy';g.state.switchPower=power;p.hand=[];
 assert.equal(g.triggerRummy('enemy',[named(g,'H10','enemy')]),'rummy');
 assert.equal(p.hand.length,6);assert.equal(p.hp,52);assert.equal(p.status.regen,1);assert.equal(p.status.endure||0,power>=60?12:0);assert.equal(p.shield,0);
}
// Flame Streamer trades all opposing damp for vulnerable, even below 40 power.
for(const damp of [0,5]){
 const g=fresh(),m=run(g,'enemy','S',['9','10','J']),c=named(g,'VSSQ');g.state.player.hand.push(c);g.state.enemy.status.damp=damp;
 assert.equal(g.attachCards('player',[c],'enemy',0),true);assert.equal(g.state.enemy.status.damp,0);assert.equal(g.state.enemy.status.vulnerable,damp?1:0);assert.equal(g.state.switchPower,30);
}
{
 const g=fresh(),m=run(g,'enemy','S',['9','10','J']),c=named(g,'VSSQ');g.state.player.hand.push(c);g.state.enemy.status.damp=11;g.state.switchTarget='enemy';
 assert.equal(g.attachCards('player',[c],'enemy',0),false);assert.equal(g.state.enemy.status.damp,11);assert.equal(g.state.enemy.status.vulnerable,0,'failed attach pays no status cost');
}
// Emergency Retreat resumes optional recovery once; no shield replacement leak or return override.
for(const choice of ['skip','recover']){
 const g=fresh(),p=g.state.player,m=run(g,'enemy','H',['2','3','4','5']);m.cards[0].owner='player';g.setPointBlankClash('player',m);const c=named(g,'PBH6');p.hand.push(c);
 assert.equal(g.attachCards('player',[c],'enemy',0),'choice');assert.equal(p.status.endure||0,12);assert.equal(p.shield,0);assert.ok(g.state.pendingEffectChoice);
 const selected=choice==='skip'?'__skip__':g.state.pendingEffectChoice.options[0].key;g.resolveEffectChoice(selected);
 assert.equal(g.state.pendingEffectChoice,null);assert.equal(p.status.endure||0,12);assert.equal(g.state.switchPower,30,'resumed attach returns once');
 if(choice==='recover'){const recovered=p.hand.find(x=>x.rank==='2');assert.ok(recovered);assert.equal(g.recoveredCardCanReturn(recovered,g.state.turnToken,m),false);}
}
// Mag Dump applies overheat 16 + endure 8; overheat's recoil consumes that defense.
for(const eligible of [false,true]){
 const g=fresh(),p=g.state.player,m=run(g,'enemy','S',['9','10','J','Q']);m.cards[0].owner='player';g.setPointBlankClash('player',m);const c=named(g,'PBSK');p.hand.push(c);
 if(eligible){g.notePointBlankTurnAction('player','recover');g.notePointBlankTurnAction('player','maintenance');}
 const hand=p.hand.length,deck=p.deck.length;assert.equal(g.attachCards('player',[c],'enemy',0),true);
 assert.equal(g.state.switchPower,eligible?46:30);assert.equal(p.hp,40);assert.equal(p.status.overheat||0,0);assert.equal(p.status.endure||0,0);assert.equal(p.deck.length,deck);assert.equal(p.hand.length,hand-1,'no retired draw reward');
}
// Dual Joker BURST grants persistent defense; RUN still uses legal optional free recovery.
{
 const g=fresh(),p=g.state.player,m=run(g,'enemy','S',['6']);m.type='SET';m.cards=[plain(g,'S','6','enemy'),plain(g,'H','6','enemy'),plain(g,'D','6','enemy')];const c=g.makeCard('J','J3',true,'player','J3');p.hand.push(c);
 assert.equal(g.attachCards('player',[c],'enemy',0),true);assert.equal(p.status.endure||0,16);assert.equal(p.shield,0);assert.equal(g.state.switchPower,44);assert.ok(p.spent.includes(c));
 g.turnStart('player');assert.equal(p.status.endure||0,16,'endure survives owner turn start');assert.equal(g.damage('player',20),4);assert.equal(p.status.endure||0,0);
}
{
 const g=fresh(),p=g.state.player,m=run(g,'enemy','S',['5','6','7']);m.cards[0].owner='player';const c=g.makeCard('J','J3',true,'player','J3');p.hand.push(c);
 assert.equal(g.attachCards('player',[c],'enemy',0),'choice');assert.ok(g.state.pendingEffectChoice.options.every(o=>o.card!==c));g.resolveEffectChoice('__skip__');assert.equal(p.status.endure||0,0);
}
console.log('PASS v3 combat reworks: actual healing, RUMMY, damp consumption, recovery resume, overheat defense and Joker behavior');

// Execute the real tutorial attach, including the completion condition and success message.
{
 const g=fresh();g.startTutorial('jokerDual');const c=g.state.player.hand.find(c=>c.tag==='jokerDual');
 assert.equal(g.executePlayerAttach([c],{side:'player',index:0}),true);assert.equal(g.state.player.status.endure,16);assert.equal(g.state.player.shield,0);assert.ok(g.state.tutorialSuccessText.includes('불굴 16'));assert.ok(!g.state.tutorialSuccessText.includes('보호막'));
}

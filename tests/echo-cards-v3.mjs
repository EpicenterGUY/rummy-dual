import assert from 'node:assert/strict';
import {fresh,named,plain,meld,run} from './helpers/v3-fixture.mjs';

for(const order of ['first','last','sealed','silenced']){
 const g=fresh(),c=named(g,'C8'),gear=named(g,'H8'),p=plain(g,'D','8');g.state.player.hand.push(c,gear,p);
 if(order==='sealed')g.applyOfficialStatus('card',c,'seal',1,{silent:true});
 if(order==='silenced')g.applyOfficialStatus('card',c,'silence',1,{actor:'player',silent:true});
 assert.equal(g.submitNewMeld('player',order==='last'?[gear,c,p]:[c,gear,p]),true);
 assert.equal(g.state.player.shield,order==='first'||order==='silenced'?48:32);
 assert.equal(gear.officialStatus.echo,order==='last'?1:0,'completed effects are never replayed on grant');assert.equal(g.state.player.hand.length,1);
}
{
 const g=fresh(),c=named(g,'C8'),gear=named(g,'H8'),ambush=named(g,'S8');g.state.player.hand.push(c,gear,ambush);
 assert.equal(g.submitNewMeld('player',[c,gear,ambush]),'choice');const q=g.state.pendingEffectChoice;
 assert.equal(q.options.length,2);assert.ok(q.options.every(o=>o.card!==c));assert.ok(!q.allowSkip);assert.equal(g.state.player.shield,0);
 g.resolveEffectChoice(q.options.find(o=>o.card===gear).key);assert.equal(g.state.player.shield,48);assert.equal(ambush.officialStatus.echo,0);
}
{
 const g=fresh(),c=named(g,'C8'),own=named(g,'C5'),foe=named(g,'VSC6','enemy'),p=plain(g,'C','7');meld(g,'player',[own,foe,p]);g.state.player.hand.push(c);
 assert.equal(g.attachCards('player',[c],'player',0),true);assert.equal(own.officialStatus.echo,1);assert.equal(foe.officialStatus.echo,0);assert.equal(c.officialStatus.echo,0,'same meld, other own named card only');
}
{
 const g=fresh(),cards=[named(g,'C8'),plain(g,'S','8'),plain(g,'D','8')];g.state.player.hand.push(...cards);assert.equal(g.submitNewMeld('player',cards),true);assert.equal(g.state.pendingEffectChoice,null);
}
{
 const g=fresh();g.state.turn='enemy';g.state.switchTarget='enemy';const cards=[named(g,'C8','enemy'),named(g,'S8','enemy'),named(g,'H8','enemy')];g.state.enemy.hand.push(...cards);
 assert.equal(g.submitNewMeld('enemy',cards),true);assert.equal(g.state.enemy.shield,48,'CPU grants echo to a numeric source');assert.equal(g.state.pendingEffectChoice,null);
}
// Milestone waits for the new-hand choice before ending Rummy, even with one eligible card.
for(const mode of ['choose','skip','single','none','silenced','stale']){
 const g=fresh(),source=named(g,'VSH10'),gear=named(g,'H8'),copy=named(g,'C8');
 const cards=[source,plain(g,'S','10'),plain(g,'D','10')];g.state.player.hand=cards;
 g.state.player.deck=mode==='none'?['2','3','4','5','6','7'].map(r=>plain(g,'D',r)):[...['2','3','4','5'].map(r=>plain(g,'D',r)),mode==='single'?plain(g,'D','6'):copy,gear];
 if(mode==='silenced')g.applyOfficialStatus('card',source,'silence',1,{actor:'player',silent:true});
 const result=g.submitNewMeld('player',cards);
 assert.equal(g.state.player.status.regen,mode==='silenced'?0:1);assert.equal(g.state.player.shield,0,'old shield 12 reward is removed');assert.equal(g.state.player.hand.length,6);
 if(['none','silenced'].includes(mode)){assert.equal(result,'rummy');assert.equal(g.state.turn,'enemy');assert.equal(g.state.pendingEffectChoice,null);continue}
 assert.equal(result,'choice');assert.equal(g.state.turn,'player');assert.equal(g.state.phase,'action');assert.equal(g.state.player.hp,40);
 const q=g.state.pendingEffectChoice;assert.equal(q.title,'기념 방송');assert.ok(q.allowSkip);assert.ok(q.options.every(o=>g.state.player.hand.includes(o.card)&&o.card.named));if(mode==='single')assert.equal(q.options.length,1);
 const option=q.options.find(o=>o.card===gear);if(mode==='stale')g.state.battleId++;
 g.resolveEffectChoice(mode==='skip'?'__skip__':option.key);
 assert.equal(gear.officialStatus.echo,['skip','stale'].includes(mode)?0:1);assert.equal(g.state.turn,mode==='stale'?'player':'enemy');
 const before=JSON.stringify({hp:g.state.player.hp,echo:gear.officialStatus.echo,turn:g.state.turn});q.onChoose(option);assert.equal(JSON.stringify({hp:g.state.player.hp,echo:gear.officialStatus.echo,turn:g.state.turn}),before);
}
// Last Laugh finishes its additional draw/bottom before the new-hand echo selection.
for(const bottomGear of [false,true]){
 const g=fresh(),m=run(g,'enemy','H',['7','8','9']),source=named(g,'VSH10'),joker=named(g,'J2'),gear=named(g,'H8');g.state.player.hand=[source,joker];
 g.state.player.deck=[...['2','3','4','5','6','7'].map(r=>plain(g,'D',r)),gear];
 assert.equal(g.attachCards('player',[source,joker],'enemy',0),'choice');let q=g.state.pendingEffectChoice;assert.equal(q.title,'마지막 웃음');assert.equal(g.state.player.hand.length,7);assert.equal(g.state.turn,'player');
 g.resolveEffectChoice(q.options.find(o=>bottomGear?o.card===gear:o.card!==gear).key);assert.equal(g.state.player.hand.length,6);
 if(bottomGear){assert.equal(g.state.pendingEffectChoice,null);assert.equal(g.state.turn,'enemy');assert.equal(gear.officialStatus.echo,0)}else{q=g.state.pendingEffectChoice;assert.equal(q.title,'기념 방송');assert.equal(g.state.turn,'player');g.resolveEffectChoice(q.options[0].key);assert.equal(gear.officialStatus.echo,1);assert.equal(g.state.turn,'enemy')}
 assert.ok(g.runValid(m.cards));
}
{
 const g=fresh();g.state.turn='enemy';g.state.enemy.hand=[];const source=named(g,'VSH10','enemy'),gear=named(g,'H8','enemy');g.state.enemy.deck=[...['2','3','4','5','6'].map(r=>plain(g,'D',r,'enemy')),gear];
 assert.equal(g.triggerRummy('enemy',[source]),'rummy');assert.equal(gear.officialStatus.echo,1);assert.equal(g.state.enemy.status.regen,1);assert.equal(g.state.enemy.shield,0);assert.equal(g.state.pendingEffectChoice,null);
}
console.log('Echo cards: C8 order/targets/AI, Milestone new-hand choice, silence, cancellation, and Last Laugh continuation');

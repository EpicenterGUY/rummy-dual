import assert from 'node:assert/strict';
import {fresh,plain,named,meld,run,nextTurn} from './helpers/v3-fixture.mjs';
const value=(g,c)=>g.officialStatusValue('card',c,'silence');
function preparedSleeper(g,turns=2){const c=named(g,'S9');g.state.player.hand.push(c);for(let i=0;i<turns;i++)g.advanceHandPreparation('player');return c}
function choose(g,c){assert.equal(g.resolveEffectChoice(`silence:${c.uid}`),true)}

for(const turns of [0,1,2]){
 const g=fresh(),c=preparedSleeper(g,turns),foe=run(g,'enemy','H',['2','3','4']),own=run(g,'player','S',['6','7','8']);let completed=0;
 g.subscribeEffectEvent(p=>{if(p.event==='onAttach')completed++});
 const result=g.attachCards('player',[c],'player',0);
 if(turns<2){assert.equal(result,true);assert.equal(g.state.pendingEffectChoice,null);assert.equal(completed,1);assert.ok(foe.cards.every(c=>!value(g,c)))}
 else{
  assert.equal(result,'choice');assert.equal(completed,0);assert.equal(g.state.switchPower,20);assert.equal(g.resolveEffectChoice('__skip__'),false,'mandatory targeting cannot be bypassed');
  const target=foe.cards[1];choose(g,target);assert.equal(value(g,target),1);assert.equal(completed,1);assert.equal(g.state.switchPower,30);assert.equal(g.resolveEffectChoice(`silence:${target.uid}`),false);assert.equal(completed,1);assert.ok(own.cards.includes(c));
 }
}
// Card ownership, rather than which board it occupies, controls Sleeper's candidates.
{
 const g=fresh(),c=preparedSleeper(g),m=run(g,'player','S',['6','7','8']),target=m.cards[0];target.owner='enemy';
 assert.equal(g.attachCards('player',[c],'player',0),true);assert.equal(value(g,target),1);assert.equal(g.state.pendingEffectChoice,null,'one legal card resolves synchronously');
}
{
 const g=fresh(),c=preparedSleeper(g),m=run(g,'enemy','H',['2','3','4']),target=m.cards[2];g.applyOfficialStatus('card',target,'silence',1,{actor:'enemy'});const expiry=target.officialStatus.silenceDeadlineToken;
 run(g,'player','S',['6','7','8']);g.attachCards('player',[c],'player',0);choose(g,target);assert.equal(g.state.enemy.status.damp,12);assert.equal(target.officialStatus.silenceDeadlineToken,expiry,'fallback applies damp instead of refreshing silence');
}
{
 const g=fresh(),c=preparedSleeper(g),m=run(g,'enemy','H',['2','3','4']),target=m.cards[2];run(g,'player','S',['6','7','8']);g.attachCards('player',[c],'player',0);target.owner='player';choose(g,target);
 assert.equal(value(g,target),0);assert.equal(g.state.enemy.status.damp||0,0);assert.equal(g.state.switchPower,30,'an invalidated choice resumes once without applying a status');
}
for(const already of [false,true]){
 const g=fresh(),c=named(g,'PBS3'),m=run(g,'enemy','S',['4','5','6']),target=m.cards[1];g.state.player.hand.push(c);g.setPointBlankClash('player',m);
 if(already)g.applyOfficialStatus('card',target,'silence',1,{actor:'enemy'});
 assert.equal(g.attachCards('player',[c],'enemy',0),'choice');choose(g,target);assert.equal(value(g,target),1);assert.equal(g.officialStatusValue('meld',m,'fracture'),Number(already));assert.equal(g.officialStatusValue('meld',m,'seal'),0);assert.equal(g.meldFixedActive(m),false);
}
{
 const g=fresh(),c=named(g,'PBS3'),m=run(g,'enemy','S',['4','5','6']);g.state.player.hand.push(c);g.attachCards('player',[c],'enemy',0);assert.equal(g.state.pendingEffectChoice,null);assert.ok(m.cards.every(c=>!value(g,c)),'Flashbang requires the actor’s clash');
}
for(const board of ['player','enemy']){
 const g=fresh(),c=named(g,'VSD6'),m=meld(g,board,[plain(g,'D','4',board),plain(g,'D','5',board),c]);nextTurn(g,'enemy');g.state.switchTarget='enemy';let before=g.state.player.hand.length;
 const seven=plain(g,'D','7','enemy');g.state.enemy.hand.push(seven);assert.equal(g.attachCards('enemy',[seven],board,0),true);assert.equal(g.state.player.hand.length,before+1);assert.equal(value(g,c),1,`${board}: Superchat self-mutes after its draw`);
 const eight=plain(g,'D','8','enemy');g.state.enemy.hand.push(eight);g.attachCards('enemy',[eight],board,0);assert.equal(g.state.player.hand.length,before+1,'a second attachment cannot reactivate it');
 g.state.switchPower=0;g.state.turn='player';g.turnStart('player');assert.equal(value(g,c),1);g.turnEnd('player');assert.equal(value(g,c),0);
 g.state.turn='enemy';g.turnStart('enemy');g.state.switchTarget='enemy';before=g.state.player.hand.length;const nine=plain(g,'D','9','enemy');g.state.enemy.hand.push(nine);g.attachCards('enemy',[nine],board,0);assert.equal(g.state.player.hand.length,before+1);assert.equal(value(g,c),1);
}
// Silence chosen during entry resolves before the target's onAttach reaction.
{
 const g=fresh(),source=preparedSleeper(g),chat=named(g,'VSD6','enemy');run(g,'player','S',['6','7','8']);meld(g,'enemy',[plain(g,'D','4','enemy'),plain(g,'D','5','enemy'),chat]);
 g.attachCards('player',[source],'player',0);choose(g,chat);const before=g.state.enemy.hand.length;
 g.state.player.returnedSwitchThisTurn=false;g.state.switchTarget='player';const seven=plain(g,'D','7');g.state.player.hand.push(seven);g.attachCards('player',[seven],'enemy',0);assert.equal(g.state.enemy.hand.length,before);
}
// CPU goes through the same targeting and can finish the action without a human modal.
{
 const g=fresh(),c=named(g,'PBS3','enemy'),m=run(g,'player','S',['4','5','6']);nextTurn(g,'enemy');g.state.switchTarget='enemy';g.state.enemy.hand.push(c);g.setPointBlankClash('enemy',m);
 assert.equal(g.attachCards('enemy',[c],'player',0),true);assert.equal(g.state.pendingEffectChoice,null);assert.equal(m.cards.filter(c=>value(g,c)).length,1);
}
console.log('PASS Sleeper, Flashbang and Superchat: preparation, exact selection, fallbacks, completed actions, controller scope and CPU');

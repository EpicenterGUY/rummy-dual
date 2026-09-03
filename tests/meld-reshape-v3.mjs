import assert from 'node:assert/strict';
import {fresh,plain,named,meld,run} from './helpers/v3-fixture.mjs';
const ids=cards=>Array.from(cards,c=>c.uid).sort((a,b)=>a-b);

{
 const g=fresh(),c=named(g,'C9'),m=run(g,'player','C',[4,5,6,7,8],{chain:1});g.state.player.hand.push(c);g.state.player.newMeldCount=1;
 g.applyOfficialStatus('meld',m,'mark',1,{actor:'enemy'});g.applyOfficialStatus('meld',m,'mark',1,{actor:'player'});g.applyOfficialStatus('meld',m,'fracture',1,{actor:'enemy'});g.setOfficialStatus('meld',m,'protect',2);
 g.setZeroSightTarget('enemy',m);g.setPointBlankClash('enemy',m);
 const before=ids([...m.cards,c]);let changes=0,creates=0,recoveries=0;
 g.subscribeEffectEvent(p=>{if(p.event==='onMeldReshape'){changes++;assert.equal(g.state.player.melds.length,2);assert.ok(g.state.player.melds.every(x=>g.runValid(x.cards)))}if(p.event==='onMeldCreate')creates++;if(p.event==='onRecover')recoveries++});
 assert.equal(g.attachCards('player',[c],'player',0),'choice');assert.equal(g.state.switchPower,35,'the original attach resolves once before the choice');
 const option=g.state.pendingEffectChoice.options.find(o=>o.choice.kind==='split');assert.ok(option);g.resolveEffectChoice(option.key);
 const results=g.state.player.melds;assert.equal(results.length,2);assert.deepEqual(ids(results.flatMap(x=>x.cards)),before);
 assert.ok(results.every(x=>x.chain===2));assert.equal(results.reduce((n,x)=>n+x.status.fracture,0),1);assert.equal(results.reduce((n,x)=>n+x.status.protect,0),2);
 for(const actor of ['player','enemy'])assert.equal(results.reduce((n,x)=>n+g.meldMarkValue(x,actor),0),1,'marks are transferred, not copied');
 assert.equal(g.zeroSightTargetMeld('enemy'),null);assert.equal(g.pointBlankClashMeld('enemy'),null);
 assert.equal(g.state.player.newMeldCount,1);assert.equal(g.state.player.returnedSwitchThisTurn,true);assert.equal(g.state.switchPower,35);assert.equal(g.state.player.hp,40,'a reshape does not trigger fracture');
 assert.equal(changes,1);assert.equal(creates,0);assert.equal(recoveries,0);
 const extra=plain(g,'C',10);g.state.player.hand.push(extra);
 for(let i=0;i<results.length;i++)assert.equal(g.attachCards('player',[extra],'player',i),false,'reshaping never reopens a same-turn attachment');
 assert.equal(g.resolveEffectChoice(option.key),false,'a choice cannot commit twice');
}
{
 const g=fresh(),a=run(g,'player','C',[4,5,6],{chain:3}),b=run(g,'player','C',[7,8,9],{chain:1});run(g,'player','H',[4,5,6]);
 g.setOfficialStatus('meld',a,'seal',2);g.setOfficialStatus('meld',b,'seal',3);
 for(const m of [a,b]){g.applyOfficialStatus('meld',m,'fracture',1,{actor:'enemy'});g.applyOfficialStatus('meld',m,'mark',1,{actor:'player'})}
 g.applyOfficialStatus('meld',b,'mark',1,{actor:'enemy'});g.setOfficialStatus('meld',a,'protect',1);g.setOfficialStatus('meld',b,'protect',2);
 const options=g.meldReshapeCandidates('player');assert.ok(options.length);assert.ok(options.every(x=>x.kind==='merge'),'a full board can merge but cannot split');
 const choice=options.find(x=>x.sources.includes(a)&&x.sources.includes(b)),power=g.state.switchPower,result=g.applyMeldReshape('player',choice);
 assert.ok(result);assert.equal(result[0].chain,1);assert.equal(result[0].status.seal,5);assert.equal(result[0].status.protect,3);assert.equal(result[0].status.fracture,1);assert.equal(g.officialStatusValue('meld',result[0],'mark'),2);
 assert.equal(g.state.player.melds.length,2);assert.equal(g.state.switchPower,power);assert.equal(g.state.player.newMeldCount,0);
}
{
 const g=fresh(),m=run(g,'player','C',[4,5,6,7,8,9]),before=ids(m.cards);g.applyMeldFixed(m,'player');assert.equal(g.meldReshapeCandidates('player').length,0);
 g.clearOfficialStatus('meld',m,'fixed');g.applyOfficialStatus('card',m.cards[0],'fixed',1,{owner:'player',silent:true});assert.equal(g.meldReshapeCandidates('player').length,0);
 g.clearOfficialStatus('card',m.cards[0],'fixed');const choice=g.meldReshapeCandidates('player')[0];assert.ok(choice);
 const bad={...choice,groups:[choice.groups[0],choice.groups[0]]};assert.equal(g.applyMeldReshape('player',bad),false);assert.deepEqual(ids(m.cards),before);
 m.cards.push(plain(g,'C',10));assert.equal(g.applyMeldReshape('player',choice),false,'stale choices cannot drop a newly attached card');assert.equal(m.cards.length,7);assert.equal(g.state.player.melds.length,1);
 assert.equal(g.applyMeldReshape('enemy',g.meldReshapeCandidates('player')[0]),false,'the opponent cannot reshape my board');
}
// A C9 in a new meld must finish the choice before RUMMY reload/end-turn, exactly once.
for(const skip of [false,true]){
 const g=fresh(),old=run(g,'player','C',[4,5,6]),c=named(g,'C9'),cards=[plain(g,'C',7),plain(g,'C',8),c];g.state.player.hand=cards;
 assert.equal(g.submitNewMeld('player',cards),'choice');assert.equal(g.state.player.hand.length,0);assert.equal(g.state.turn,'player');assert.equal(g.state.rummy,0);
 const key=skip?'__skip__':g.state.pendingEffectChoice.options.find(o=>o.choice.kind==='merge').key;
 g.resolveEffectChoice(key);assert.equal(g.state.rummy,1);assert.equal(g.state.player.hand.length,6);assert.equal(g.state.turn,'enemy');assert.equal(g.state.player.newMeldCount,1);
 assert.equal(g.state.player.melds.length,skip?2:1);assert.equal(g.resolveEffectChoice(key),false);assert.equal(g.state.rummy,1);
 assert.deepEqual(ids(g.state.player.melds.flatMap(m=>m.cards)),ids([...old.cards,...cards]));
}
{
 const g=fresh(),c=named(g,'C9'),m=run(g,'enemy','C',[6,7,8]);g.state.player.hand.push(c);assert.equal(g.attachCards('player',[c],'enemy',0),true);
 assert.equal(m.cards.length,4);assert.equal(g.state.enemy.spent.length,0,'the previous enemy-end cut is no longer attached to C9');
}
{
 const g=fresh();g.state.turn='enemy';run(g,'enemy','C',[4,5,6]);const cards=[plain(g,'C',7,'enemy'),plain(g,'C',8,'enemy'),named(g,'C9','enemy')];g.state.enemy.hand.push(...cards);
 assert.equal(g.submitNewMeld('enemy',cards),true);assert.equal(g.state.enemy.melds.length,1);assert.equal(g.state.enemy.melds[0].cards.length,6);assert.equal(g.state.pendingEffectChoice,null,'AI resolves a candidate from the same legal list');
}
console.log('Meld reshaping: atomic card conservation, statuses, limits, stale/locked targets, RUMMY ordering and AI passed');

import assert from 'node:assert/strict';
import {fresh,named,plain,meld,run} from './helpers/v3-fixture.mjs';

function gearRun(g){
 const cards=['2','3','4','5','6','7'].map(r=>r==='3'?named(g,'C3'):plain(g,'C',r));
 return meld(g,'player',cards);
}
// Actual multi-attach order controls which completed effects exist when CA resolves.
for(const order of ['before','after','sealed','suppressed','echo']){
 const g=fresh(),m=gearRun(g),gear=named(g,'H8'),ca=named(g,'CA');g.state.player.hand.push(gear,ca);
 if(order==='sealed')g.applyOfficialStatus('card',gear,'seal',1,{silent:true});
 if(order==='suppressed')gear.suppressEffectToken=g.state.turnToken;
 if(order==='echo')g.applyOfficialStatus('card',gear,'echo',1,{silent:true});
 const cards=order==='before'?[ca,gear]:[gear,ca];
 assert.equal(g.attachCards('player',cards,'player',0),true,order);
 assert.equal(g.state.player.shield,{before:32,after:48,sealed:0,suppressed:0,echo:64}[order],order);
 assert.equal(g.state.switchPower,45,'CA does not copy the chain or directly return the switch');
 assert.equal(g.state.activeNumericAction,undefined,'action scope is restored');assert.ok(g.runValid(m.cards));
}
// Multiple eligible originals require one explicit choice, with actual amounts shown.
for(const selected of ['heal','addShield']){
 const g=fresh(),m=run(g,'player','H',['5','6','7']),phoenix=named(g,'H4'),gear=named(g,'H8'),ca=named(g,'CA');
 g.state.player.detonateMemory=1;g.applyOfficialStatus('card',ca,'flexible',1,{silent:true});
 const cards=[phoenix,gear,ca,plain(g,'H','2'),plain(g,'H','3')];g.state.player.hand.push(...cards);
 const plan=g.legalRankChoicePlansForAttach(m,cards)[0].plan;let attaches=0;g.subscribeEffectEvent(p=>{if(p.event==='onAttach')attaches++});
 assert.equal(g.attachCards('player',cards,'player',0,plan),'choice');
 assert.equal(g.state.player.hp,52);assert.equal(g.state.player.shield,32);assert.equal(g.state.switchPower,20);assert.equal(attaches,0);
 const q=g.state.pendingEffectChoice;assert.equal(q.title,'재귀 함수');assert.equal(q.options.length,2);assert.ok(!q.allowSkip);
 const option=q.options.find(o=>o.record.kind===selected);assert.ok(option);
 g.resolveEffectChoice(option.key);
 assert.equal(g.state.player.hp,selected==='heal'?58:52);assert.equal(g.state.player.shield,selected==='addShield'?48:32);assert.equal(attaches,1);
 const before=JSON.stringify({hp:g.state.player.hp,shield:g.state.player.shield,power:g.state.switchPower});
 q.onChoose(option);assert.equal(JSON.stringify({hp:g.state.player.hp,shield:g.state.player.shield,power:g.state.switchPower}),before);assert.equal(attaches,1);
}
// A queued original is recorded only after its target choice; resuming never repeats it.
for(const stale of [false,true]){
 const g=fresh(),m=run(g,'player','H',['2','3','4']),warm=named(g,'H5'),ca=named(g,'CA');
 g.applyOfficialStatus('card',ca,'flexible',1,{silent:true});g.applyOfficialStatus('card',warm,'echo',1,{silent:true});g.state.player.hand.push(warm,ca);
 assert.equal(g.attachCards('player',[warm,ca],'player',0,g.legalRankChoicePlansForAttach(m,[warm,ca])[0].plan),'choice');
 const q=g.state.pendingEffectChoice,option=q.options[0];assert.equal(q.title,'온기');assert.equal(g.state.player.hp,40);
 if(stale)g.state.turnToken++;
 g.resolveEffectChoice(option.key);
 assert.equal(g.state.player.hp,stale?40:48,'warmth 4 + echo 2 + CA 2');
 assert.equal(warm.officialStatus.echo,stale?1:0);
 const after=JSON.stringify({hp:g.state.player.hp,power:g.state.switchPower});q.onChoose(option);assert.equal(JSON.stringify({hp:g.state.player.hp,power:g.state.switchPower}),after);
}
// Neither another action nor a later Rummy effect can be read retroactively.
{
 const g=fresh(),gear=named(g,'H8'),a=g.createNumericEffectAction('player');g.runEffectAction('addShield',{actor:'player',source:gear,action:a},{amount:8});
 const cards=[named(g,'CA'),named(g,'HA'),plain(g,'D','A')];g.state.player.hand=cards;
 g.state.player.deck=['2','3','4','5','6','7','8'].map(r=>plain(g,'D',r));
 assert.equal(g.submitNewMeld('player',cards),'rummy');assert.equal(g.state.player.shield,28,'only prior 32 + later Rummy 16 - turn-end bomb 20');
 assert.equal(g.state.player.hand.length,7);
}
// Isolated dispatcher records still use the real primitives and exclude enemy/copy records.
{
 const g=fresh(),ca=named(g,'CA'),gear=named(g,'H8'),foe=named(g,'H8','enemy'),a=g.createNumericEffectAction('player');
 g.runEffectAction('addShield',{actor:'enemy',source:foe,action:a},{amount:10});
 g.runEffectAction('addShield',{actor:'player',source:gear,action:a,copied:true},{amount:10});
 assert.equal(g.requestNumericCopy('player',ca,a),false);assert.equal(g.state.player.shield,40);assert.equal(g.state.pendingEffectChoice,null);
 const b=g.createNumericEffectAction('player');g.runEffectAction('addPower',{actor:'player',source:gear,action:b},{amount:9});
 g.applyOfficialStatus('card',ca,'echo',1,{silent:true});g.requestNumericCopy('player',ca,b);
 assert.equal(g.state.switchPower,33);assert.equal(ca.officialStatus.echo,1,'a copied number does not consume CA echo');
 assert.deepEqual(Array.from(b.records,r=>[r.kind,r.amount,r.copied]),[['addPower',9,false],['addPower',4,true]]);
}
// Recovery reactions caused by this action share its record, including across a choice.
{
 const g=fresh(),ambulance=named(g,'H4B'),home=meld(g,'player',[ambulance,...['5','6','7'].map(r=>plain(g,'H',r))]),target=run(g,'enemy','C',['2','3','4','5']),raid=named(g,'VSC6'),ca=named(g,'CA');g.state.player.hand.push(raid,ca);
 assert.equal(g.attachCards('player',[raid,ca],'enemy',0),'choice');const q=g.state.pendingEffectChoice,o=q.options.find(o=>o.entry.card===ambulance);assert.ok(o);
 g.resolveEffectChoice(o.key);assert.equal(g.state.player.hp,52,'RAID recovery heals 8 through Ambulance; CA copies its completed 4');assert.equal(home.cards.length,3);assert.ok(g.state.player.hand.includes(ambulance));assert.equal(g.state.switchPower,45);assert.ok(g.runValid(target.cards));
}
console.log('Numeric copy timing: completed own sources, order, choices, resumption, Rummy boundary, and no recursive copies');

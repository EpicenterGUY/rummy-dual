import assert from 'node:assert/strict';
import {fresh,named,plain,meld} from './helpers/v3-fixture.mjs';
const grant=(g,c)=>g.applyOfficialStatus('card',c,'echo',1,{silent:true});
{
 const g=fresh(),c=named(g,'H8');
 for(const n of [-1,0,0.5,NaN,Infinity])assert.equal(g.applyOfficialStatus('card',c,'echo',n,{silent:true}),0);
 assert.equal(grant(g,c),1);assert.equal(grant(g,c),1);assert.equal(g.applyOfficialStatus('player',g.state.player,'echo',1,{silent:true}),0);
 assert.match(g.cardHTML(c),/echoCardMark/);g.renderDetail(c);assert.match(g.document.getElementById('detail').innerHTML,/다음 실제 회복·보호막·독립 위력/);
}
for(const [kind,amount,total] of [['heal',11/4,56],['addShield',7/4,10],['addPower',9,33]]){
 const g=fresh(),source=named(g,'H8'),action=g.createNumericEffectAction('player');grant(g,source);
 const beforeTarget=g.state.switchTarget,actual=g.runEffectAction(kind,{actor:'player',source,action},{amount});
 assert.equal(actual,kind==='heal'?11:kind==='addShield'?7:9);
 assert.equal(kind==='heal'?g.state.player.hp:kind==='addShield'?g.state.player.shield:g.state.switchPower,total);
 assert.equal(source.officialStatus.echo,0);assert.equal(g.state.switchTarget,beforeTarget);
 assert.deepEqual(Array.from(action.records,r=>[r.kind,r.amount,r.copied]),[[kind,actual,false],[kind,Math.floor(actual/2),true]]);
 assert.equal(action.records[1].originRecordId,action.records[0].id);
 assert.equal(g.copyNumericEffect('player',source,action.records[1],action),0,'a copy cannot be copied');
 g.runEffectAction(kind,{actor:'player',source,action},{amount:1});assert.equal(action.records.length,3,'later originals are not repeated');
}
{
 const g=fresh(),c=named(g,'H4'),a=g.createNumericEffectAction('player');grant(g,c);g.state.player.hp=60;
 assert.equal(g.runEffectAction('heal',{actor:'player',source:c,action:a},{amount:3}),0);assert.equal(c.officialStatus.echo,1);assert.equal(a.records.length,0);
 g.state.player.hp=55;g.runEffectAction('heal',{actor:'player',source:c,action:a},{amount:3});
 assert.equal(c.officialStatus.echo,0);assert.equal(a.records[0].amount,5,'record actual heal, not requested 12');assert.equal(a.records.length,1,'zero actual copy is omitted at full HP');
 g.state.player.hp=50;g.copyNumericEffect('player',named(g,'CA'),a.records[0],a);assert.equal(g.state.player.hp,52,'half of actual 5 is 2, with unit conversion once');
}
{
 const g=fresh(),c=named(g,'H8'),a=g.createNumericEffectAction('player');grant(g,c);
 g.runEffectAction('addShield',{actor:'player',source:c,action:a},{amount:0.25});assert.equal(g.state.player.shield,1);assert.equal(c.officialStatus.echo,0);assert.equal(a.records.length,1,'a positive original of 1 consumes echo even though its half is 0');
}
// Non-numeric actions, costs, unowned/ordinary sources, and field/status healing are not sources.
{
 const g=fresh(),source=named(g,'H8'),action=g.createNumericEffectAction('player');grant(g,source);
 g.withNumericEffectAction(action,()=>{
  g.runEffectAction('draw',{actor:'player',source},{count:1});
  g.runEffectAction('applyStatus',{actor:'player',source},{scope:'player',target:g.state.player,key:'endure',amount:8});
  g.runEffectAction('heal',{actor:'player',source,cost:true},{amount:1});
  g.runEffectAction('addShield',{actor:'player',source,copyable:false},{amount:1});
  g.heal('player',1);g.addShield('player',1);
  g.runEffectAction('returnSwitch',{actor:'player',source},{amount:9});
  g.runEffectAction('addShield',{actor:'player',source:plain(g,'H','8')},{amount:1});
  g.runEffectAction('addShield',{actor:'player',source:named(g,'H8','enemy')},{amount:1});
 });
 assert.equal(action.records.length,0);assert.equal(source.officialStatus.echo,1);assert.equal(g.state.player.status.endure,8);
 const before=g.state.player.shield;g.state.turnToken++;assert.equal(g.runEffectAction('addShield',{actor:'player',source,action},{amount:8}),0);assert.equal(g.state.player.shield,before);assert.equal(source.officialStatus.echo,1);
}
// Recovery is not copied; its named healing reaction is, without duplicating its status reward.
for(const silenced of [false,true]){
 const g=fresh(),c=named(g,'H4B'),m=meld(g,'enemy',[c,...['5','6','7'].map(r=>plain(g,'H',r,'enemy'))]);grant(g,c);
 if(silenced)g.applyOfficialStatus('card',c,'silence',1,{actor:'player',silent:true});let recoveries=0;g.subscribeEffectEvent(p=>{if(p.event==='onRecover')recoveries++});
 assert.equal(g.recoverSpecificFromMeld('player',m,c),c);assert.equal(g.state.player.hp,silenced?40:52);assert.equal(c.officialStatus.echo,silenced?1:0);assert.equal(g.state.player.status.endure||0,silenced?0:8);assert.equal(recoveries,1);
}
// Rummy originals use the same numeric dispatcher. Regeneration is not duplicated.
for(const id of ['HA','H10']){
 const g=fresh(),c=named(g,id,'enemy');g.state.turn='enemy';g.state.switchTarget='enemy';g.state.enemy.hand=[];grant(g,c);
 assert.equal(g.triggerRummy('enemy',[c]),'rummy');assert.equal(c.officialStatus.echo,0);
 if(id==='HA')assert.equal(g.state.enemy.shield,24);else{assert.equal(g.state.enemy.hp,58);assert.equal(g.state.enemy.status.regen,1)}
}
// A last-played card can return to its origin owner before the actor's Rummy resolves.
{
 const g=fresh(),c=named(g,'H10');c.originOwner='enemy';grant(g,c);g.applyOfficialStatus('card',c,'comeback',1,{silent:true});
 meld(g,'enemy',['S','D','C'].map(s=>plain(g,s,'10','enemy')),'SET');g.state.player.hand=[c];
 assert.equal(g.attachCards('player',[c],'enemy',0),'rummy');assert.equal(c.owner,'enemy');assert.ok(g.state.enemy.hand.includes(c));
 assert.equal(g.state.player.hp,58,'Rummy 12 + echo 6 still belong to the actor who played the card');assert.equal(c.officialStatus.echo,0);assert.equal(g.state.player.status.regen,1);
}
{
 const g=fresh(),c=named(g,'H4'),transfusion=named(g,'H6');meld(g,'player',[transfusion,plain(g,'H','7'),plain(g,'H','8')]);grant(g,c);g.state.player.hp=20;
 g.runEffectAction('heal',{actor:'player',source:c},{amount:3});assert.equal(g.state.player.hp,38);assert.equal(g.state.player.status.endure,6,'copied healing is real, but existing reaction limits still apply');
}
console.log('Echo core: strict cap, actual units, floor, one numeric primitive, exclusions, stale actions, and named reactions');

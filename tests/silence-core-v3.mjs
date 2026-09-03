import assert from 'node:assert/strict';
import {fresh,plain,named,meld,run} from './helpers/v3-fixture.mjs';
const value=(g,c)=>g.officialStatusValue('card',c,'silence');
const start=(g,w)=>{g.state.turn=w;g.turnStart(w)};

// The recorded controller's next turn must finish before the source wakes up.
for(const owner of ['player','enemy']){
 const g=fresh(),c=named(g,'HK',owner);g.state.switchPower=0;g.state[owner].hand.push(c);
 assert.equal(g.applyOfficialStatus('card',c,'silence',8,{actor:owner}),1);
 assert.equal(value(g,c),1);assert.equal(g.canTrigger(c,'reaction'),false);assert.equal(g.canTrigger(c,'use'),true);
 g.turnEnd('player');assert.equal(value(g,c),1);
 start(g,'enemy');g.turnEnd('enemy');assert.equal(value(g,c),owner==='enemy'?0:1);
 if(owner==='player'){start(g,'player');assert.equal(value(g,c),1);g.turnEnd('player');assert.equal(value(g,c),0)}
}
for(const zone of ['hand','deck','spent','discard']){
 const g=fresh(),c=named(g,'HK');g.state.switchPower=0;g.state.player.hand.push(c);g.applyOfficialStatus('card',c,'silence',1,{actor:'player'});
 g.state.player.hand=g.state.player.hand.filter(x=>x!==c);c.owner='enemy';(zone==='discard'?g.state.discard:g.state.enemy[zone]).push(c);
 g.turnEnd('player');start(g,'enemy');g.turnEnd('enemy');assert.equal(value(g,c),1,`${zone}: transfer cannot shorten duration`);
 start(g,'player');g.turnEnd('player');assert.equal(value(g,c),0,`${zone}: original controller expires a card in every zone`);
}
{
 const g=fresh(),c=named(g,'HK');g.state.player.hand.push(c);g.applyOfficialStatus('card',c,'silence',1,{actor:'player'});
 c.owner='enemy';g.applyOfficialStatus('card',c,'silence',1,{actor:'enemy'});assert.equal(c.officialStatus.silenceOwner,'player','an earlier reapplied deadline cannot shorten the old one');
 start(g,'enemy');g.applyOfficialStatus('card',c,'silence',1,{actor:'enemy'});assert.equal(c.officialStatus.silenceOwner,'enemy');assert.equal(c.officialStatus.silenceThroughStart,5);assert.equal(value(g,c),1);
}
for(const n of [0,-1,NaN,Infinity,1.5,'1']){
 const g=fresh(),c=named(g,'H8');assert.equal(g.applyOfficialStatus('card',c,'silence',n,{actor:'player'}),0);assert.equal(value(g,c),0);
}
// A mute card can still execute its entry effect, and silence never spends seal charges.
{
 const g=fresh(),c=named(g,'H8'),target=meld(g,'enemy',['S','D','C'].map(s=>plain(g,s,'8','enemy')),'SET');g.state.player.hand.push(c);
 g.applyOfficialStatus('card',c,'silence',1,{actor:'player'});assert.equal(g.attachCards('player',[c],'enemy',0),true);assert.equal(g.state.player.shield,32);assert.equal(value(g,c),1);
}
{
 const g=fresh(),c=named(g,'H8');g.state.player.hand.push(c);c.officialStatus.seal=1;g.applyOfficialStatus('card',c,'silence',1,{actor:'player'});
 assert.equal(c.officialStatus.seal,1);g.resolveEffects('player',[c],'RUN');assert.equal(c.officialStatus.seal,0);assert.equal(g.state.player.shield,0);assert.equal(value(g,c),1);
}
for(const scope of ['card','meld']){
 const g=fresh(),m=run(g,'enemy','S',['4','5','6']),c=m.cards[1];g.applyOfficialStatus(scope,scope==='card'?c:m,'protect',1,{actor:'enemy'});
 assert.equal(g.applyOfficialStatus('card',c,'silence',1,{actor:'player',silenceFallback:'damp'}),0);assert.equal(value(g,c),0);assert.equal(g.state.enemy.status.damp||0,0);assert.equal(g.officialStatusValue(scope,scope==='card'?c:m,'protect'),0);
}
{
 const g=fresh(),m=run(g,'player','S',['4','5','6']),c=m.cards[1];c.owner='enemy';g.applyOfficialStatus('meld',m,'protect',1,{actor:'player'});
 assert.equal(g.applyOfficialStatus('card',c,'silence',1,{actor:'player'}),1);assert.equal(g.officialStatusValue('meld',m,'protect'),1,'my own meld protection does not shield a foreign card from my effect');
}
for(const muteCover of [false,true]){
 const g=fresh(),cover=named(g,'PBH7','enemy'),target=plain(g,'H','8','enemy'),m=meld(g,'player',[cover,target,plain(g,'H','9')]);g.setPointBlankClash('enemy',m);
 if(muteCover)g.applyOfficialStatus('card',cover,'silence',1,{actor:'enemy'});
 g.applyOfficialStatus('card',target,'silence',1,{actor:'player'});
 assert.equal(value(g,target),muteCover?1:0);assert.equal(value(g,cover),1);assert.equal(cover.coverSwapUsedToken===g.state.turnToken,!muteCover);
}
{
 const g=fresh(),cover=named(g,'PBH7','enemy'),target=plain(g,'H','8','enemy'),m=meld(g,'player',[cover,target,plain(g,'H','9')]);g.setPointBlankClash('enemy',m);cover.officialStatus.protect=1;
 assert.equal(g.applyOfficialStatus('card',target,'silence',1,{actor:'player'}),0);assert.equal(value(g,target)+value(g,cover),0);assert.equal(cover.officialStatus.protect,0,'redirected target protection is honored');
}
{
 const g=fresh(),source=named(g,'VSCA'),m=meld(g,'player',[source,plain(g,'C','2'),plain(g,'C','3')]);g.reserveEffect('player',source,'onAttach','loaded',8,'player',{targetMeld:m});g.applyOfficialStatus('card',source,'silence',1,{actor:'player'});
 const c=plain(g,'C','4');g.state.player.hand.push(c);assert.equal(g.attachCards('player',[c],'player',0),true);assert.equal(g.state.player.status.loaded,8);assert.equal(g.state.player.effectReservations.length,0,'already-registered reservations survive silence');
}
for(const silent of [false,true]){
 const g=fresh(),ins=named(g,'H9','enemy'),m=meld(g,'enemy',[plain(g,'H','6','enemy'),plain(g,'H','7','enemy'),plain(g,'H','8','enemy'),ins]),target=m.cards[0];
 if(silent)g.applyOfficialStatus('card',ins,'silence',1,{actor:'enemy'});
 g.applyOfficialStatus('card',target,'silence',1,{actor:'player'});assert.equal(value(g,target),1);assert.equal(g.state.enemy.spent.includes(ins),false,'insurance only intercepts cut/theft, not a status');assert.equal(ins.insuranceUsedBattleId,null);
}
for(const fallback of ['damp','fracture']){
 const g=fresh(),m=run(g,'enemy','S',['4','5','6']),c=m.cards[0];g.applyOfficialStatus('card',c,'silence',1,{actor:'enemy'});m.status.protect=1;
 assert.equal(g.applyOfficialStatus('card',c,'silence',1,{actor:'player',silenceFallback:fallback}),0);assert.equal(value(g,c),1);assert.equal(m.status.protect,0);assert.equal(m.status.fracture,0);assert.equal(g.state.enemy.status.damp||0,0,'blocked fallback grants nothing');
}
{
 const g=fresh(),c=named(g,'H8','enemy');g.state.enemy.hand.push(c);c.officialStatus.protect=1;
 assert.equal(g.applyOfficialStatus('card',c,'silence',1,{actor:'player'}),0);assert.equal(c.officialStatus.protect,1,'an illegal hidden target cannot spend protection');
}
{
 const g=fresh(),c=named(g,'HK');g.state.player.hand.push(c);g.state.switchPower=0;g.applyOfficialStatus('card',c,'silence',1,{actor:'player'});
 g.turnEnd('player');start(g,'enemy');g.turnEnd('enemy');start(g,'player');c.healCharge=3;g.state.switchTarget='player';g.state.switchPower=20;g.turnEnd('player');
 assert.equal(g.state.player.hp,20);assert.equal(c.healCharge,3);assert.equal(value(g,c),0,'expiry follows, rather than precedes, turn-end explosion reactions');
}
console.log('PASS silence lifecycle, controller transfer, exact interference, entry/seal separation and independent reservations');

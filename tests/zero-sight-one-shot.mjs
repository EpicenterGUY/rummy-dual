import assert from 'node:assert/strict';
import {fresh,named,run} from './helpers/v3-fixture.mjs';
import {html} from './helpers/live-game.mjs';

const metadata=fresh().NAMED.ZSSK;
assert.equal(metadata.slot,'SK');assert.equal(metadata.themeId,'zero-sight');assert.equal(metadata.t,'zsOneShot');
assert.match(metadata.d,/행동 전 누적 위력이 50 이상/);
assert.ok(html.includes("{id:'zs7',label:'전체 7클리어 · ZERO-SIGHT',kind:'theme',when:p=>p.totalClears>=7,items:['ZSSK'],fields:[]}"),'unlock timing is unchanged');
for(const [power,marked,expected,recoil] of [[50,true,78,0],[50,false,70,5],[49,true,59,0]]){
 const g=fresh(),m=run(g,'enemy','S',[10,'J','Q']),c=named(g,'ZSSK');g.state.player.hand.push(c);g.state.switchPower=power;g.setZeroSightTarget('player',m);
 if(marked)g.applyOfficialStatus('meld',m,'mark',1,{actor:'player'});g.applyOfficialStatus('meld',m,'mark',1,{actor:'enemy'});
 let observed=false;g.subscribeEffectEvent(p=>{if(p.event==='onAttach'){observed=true;assert.ok(p.targetedBy.includes('player'));assert.equal(g.zeroSightTargetMeld('player'),m)}});
 assert.equal(g.attachCards('player',[c],'enemy',0),true);assert.equal(g.state.switchPower,expected);assert.equal(g.state.player.hp,40-recoil);assert.equal(g.state.player.status.seal||0,0);
 assert.equal(g.meldMarkValue(m,'player'),marked&&power<50?1:0);assert.equal(g.meldMarkValue(m,'enemy'),1);assert.equal(g.zeroSightTargetMeld('player'),m);assert.equal(observed,true);
}
for(const reason of ['ownership','limit','seal','own-board']){
 const g=fresh(),owner=reason==='own-board'?'player':'enemy',m=run(g,owner,'S',[10,'J','Q']),c=named(g,'ZSSK');g.state.player.hand.push(c);g.state.switchPower=50;g.setZeroSightTarget('player',m);g.applyOfficialStatus('meld',m,'mark',1,{actor:'player'});
 if(reason==='ownership')g.state.switchTarget='enemy';if(reason==='limit')g.state.player.returnedSwitchThisTurn=true;if(reason==='seal')g.state.player.status.seal=1;
 const allowed=reason==='seal'||reason==='own-board';assert.equal(g.attachCards('player',[c],owner,0),allowed);assert.equal(g.state.switchPower,allowed?60:50);assert.equal(g.meldMarkValue(m,'player'),1);assert.equal(g.state.player.hp,40);
 if(!allowed)assert.ok(g.state.player.hand.includes(c));
}
{
 const g=fresh(),m=run(g,'enemy','S',[10,'J','Q']),c=named(g,'ZSSK');g.setZeroSightTarget('player',m);g.applyOfficialStatus('meld',m,'mark',1,{actor:'player'});g.state.switchPower=60;
 const context={isAttach:true,targetOwner:'enemy',meld:m,willReturn:true,powerBeforeAction:49};g.resolveEffects('player',[c],'RUN',context);assert.equal(context.fxState.targetReturnEffects,undefined,'same-action power cannot satisfy the pre-action threshold');
 const valid={isAttach:true,targetOwner:'enemy',meld:m,willReturn:true,powerBeforeAction:50};g.resolveEffects('player',[c],'RUN',valid);assert.equal(valid.fxState.targetReturnEffects.length,1);
 g.returnSwitch('player',10,'flat',{flat:true,targetReturnEffects:valid.fxState.targetReturnEffects});assert.equal(g.state.switchPower,60);assert.equal(g.meldMarkValue(m,'player'),1);assert.equal(g.state.player.hp,40,'flat returns never trigger ONE SHOT heat');
}
{
 const g=fresh(),m=run(g,'enemy','S',[10,'J','Q']),c=named(g,'ZSSK');g.setZeroSightTarget('player',m);g.state.player.hand.push(c);g.state.player.hp=3;g.state.player.cores=2;g.state.switchPower=50;
 assert.equal(g.attachCards('player',[c],'enemy',0),true);assert.equal(g.state.player.cores,1);assert.equal(g.state.switchPower,0);assert.equal(g.state.switchTarget,'neutral');assert.equal(g.state.player.returnedSwitchThisTurn,true,'recoil core break does not restore a return');assert.ok(m.cards.includes(c));
}
console.log('ZERO-SIGHT ONE SHOT: real returns, marks, threshold, flat/sealed/blocked cases and recoil core break passed');

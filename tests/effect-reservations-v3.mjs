import assert from 'node:assert/strict';
import {makeGame} from './helpers/live-game.mjs';
function fresh(){const g=makeGame(),s=g.state;s.turn='player';s.phase='action';s.switchPower=20;s.switchTarget='player';for(const w of ['player','enemy']){Object.assign(s[w],{status:g.blankStatus(),effectReservations:[],hand:[],melds:[],shield:0,hp:40,turnStarts:2})}return g}
function card(g,id,owner='player'){const d=g.NAMED[id],slot=d.slot||id;return g.makeCard(slot[0],slot.slice(1),true,owner,id)}
function effect(g,id,type='RUN',extra={}){const c=card(g,id),m=extra.meld||{type,cards:[c],status:g.blankMeldStatus()};g.resolveEffects('player',[c],type,{meld:m,totalLength:3,...extra});return {c,m}}
{
 const g=fresh(),p=g.state.player,source=card(g,'S6'),pure=g.makeCard('H','5',false,'player');
 assert.equal(g.reserveEffect('player',source,'onRecover','loaded',12),true);
 assert.equal(g.reserveEffect('player',source,'onRecover','loaded',12),false);
 assert.equal(g.reserveEffect('player',source,'onRecover','defer'),false);
 g.emitEffectEvent('onRecover',{actor:'enemy',card:pure});assert.equal(p.effectReservations.length,1);
 g.emitEffectEvent('onMeldMove',{actor:'player',card:pure});assert.equal(p.effectReservations.length,1);
 g.emitEffectEvent('onRecover',{actor:'player',card:pure});assert.equal(p.status.loaded,12);assert.equal(p.effectReservations.length,0);
 g.emitEffectEvent('onRecover',{actor:'player',card:pure});assert.equal(p.status.loaded,12);
}
{
 const g=fresh(),p=g.state.player,source=card(g,'SK');
 g.reserveEffect('player',source,'onRecover','endure',8);g.state.switchPower=0;
 g.turnEnd('enemy');assert.equal(p.effectReservations.length,1);g.turnEnd('player');assert.equal(p.effectReservations.length,1);
 g.turnStart('player');g.turnEnd('player');assert.equal(p.effectReservations.length,0);
 g.emitEffectEvent('onRecover',{actor:'player'});assert.equal(p.status.endure||0,0);
}
{
 const g=fresh(),p=g.state.player,source=card(g,'VSD3');g.reserveEffect('player',source,'onRecover','comeback',1,'card');
 const c=g.makeCard('H','7',false,'player'),m={type:'RUN',cards:['4','5','6'].map(r=>g.makeCard('H',r,false,'player')).concat(c),chain:1,status:g.blankMeldStatus()};p.melds=[m];
 assert.ok(g.recoverSpecificFromMeld('player',m,c,{free:true}));assert.ok(p.hand.includes(c));assert.equal(g.officialStatusValue('card',c,'comeback'),1);assert.equal(p.effectReservations.length,0);assert.equal(g.recoveredCardCanReturn(c,g.state.turnToken),false);
}
{
 const g=fresh(),p=g.state.player,source=card(g,'S6');g.reserveEffect('player',source,'onRecover','loaded',12);g.reserveEffect('player',card(g,'SK'),'onRecover','endure',8);
 let reentered=false;g.subscribeEffectEvent(packet=>{if(packet.event==='onRecover'&&!reentered){reentered=true;g.emitEffectEvent('onRecover',{actor:'player'})}});
 g.emitEffectEvent('onRecover',{actor:'player'});assert.equal(p.status.loaded,12);assert.equal(p.status.endure,8);g.newGame();assert.equal(g.state.player.effectReservations.length,0);
}
// Every wave-two card is tested through the full production resolver.
{
 const g=fresh();effect(g,'SA','SET',{willReturn:true});assert.equal(g.state.player.status.loaded,18);
}
{
 const g=fresh(),p=g.state.player;p.detonateMemory=20;const c=card(g,'S6');g.resolveEffects('player',[c],'RUN',{});assert.equal(p.status.endure,8);assert.equal(p.effectReservations[0].key,'loaded');g.state.turnToken++;g.resolveEffects('player',[c],'RUN',{});assert.equal(p.status.endure,8,'combat limit survives a later use');
}
{
 const g=fresh(),p=g.state.player;p.melds=[{type:'SET',cards:[]}];effect(g,'SK','SET',{isNew:true});assert.equal(p.shield,12);assert.equal(p.effectReservations.length,1);
}
{
 const g=fresh();effect(g,'VSSA');assert.equal(g.state.player.status.endure,8);assert.equal(g.state.player.effectReservations[0].amount,6);
}
{
 const g=fresh(),c=card(g,'VSS5'),other=card(g,'S5');g.resolveEffects('player',[c,other],'RUN',{isAttach:true,targetOwner:'enemy',meld:{cards:[c,other],status:g.blankMeldStatus()}});assert.equal(g.state.enemy.status.damp,8);
}
{
 const g=fresh(),p=g.state.player;effect(g,'VSH3');assert.equal(p.status.endure,8);effect(g,'VSH3');assert.equal(p.hp,48);assert.equal(p.status.endure,8);
}
{
 const g=fresh();effect(g,'VSH7','RUN',{willReturn:true,meld:{cards:[{owner:'player'},{owner:'enemy'}]}});assert.equal(g.state.player.status.endure,8);assert.equal(g.state.player.hp,44);
}
{
 const g=fresh(),r=effect(g,'VSD3','SET',{isNew:true});assert.equal(g.officialStatusValue('meld',r.m,'protect'),1);assert.equal(g.state.player.effectReservations[0].key,'comeback');
}
{
 const g=fresh();g.state.switchPower=60;effect(g,'VSSK','RUN',{willReturn:true});g.returnSwitch('player',10);assert.equal(g.state.switchPower,86);assert.equal(g.state.player.hp,32);
}
{
 const g=fresh(),m={type:'RUN',cards:[],status:g.blankMeldStatus()};g.state.enemy.melds=[m];g.setZeroSightTarget('player',m);effect(g,'ZSS4','RUN',{meld:m,isAttach:true,targetOwner:'enemy'});assert.equal(g.state.enemy.status.damp,12);
}
{
 const g=fresh(),c=card(g,'ZSH3'),m={type:'RUN',cards:[],status:g.blankMeldStatus()};g.state.player.melds=[m];g.setZeroSightTarget('player',m);
 g.state.player.hand=[c];g.advanceHandPreparation('player');g.resolveEffects('player',[c],'RUN',{meld:m});assert.equal(g.state.player.status.endure,12);
}
{
 const g=fresh(),m={type:'RUN',cards:[{uid:'ally',owner:'player'}],status:g.blankMeldStatus()};g.state.enemy.melds=[m];g.setPointBlankClash('player',m);g.notePointBlankTurnAction('player','recover');effect(g,'PBH10','RUN',{meld:m,willReturn:true});assert.equal(g.state.player.status.endure,12);assert.equal(g.officialStatusValue('meld',m,'protect'),1);
}
{
 const g=fresh();g.state.lastPlayerReturnType='RUN';effect(g,'C10','RUN',{willReturn:true});assert.equal(g.state.player.status.loaded,8);
}
{
 const g=fresh(),m={type:'RUN',cards:[{uid:'ally',owner:'player'}],status:g.blankMeldStatus()};g.state.enemy.melds=[m];g.setPointBlankClash('player',m);effect(g,'PBS4','RUN',{meld:m,willReturn:true});assert.equal(g.state.player.status.loaded,12);
}
{
 const g=fresh(),m={type:'RUN',cards:[],status:g.blankMeldStatus()};g.state.enemy.melds=[m];g.setZeroSightTarget('player',m);effect(g,'ZSD8','RUN',{meld:m,isAttach:true});assert.equal(g.state.player.effectReservations[0].event,'onMeldMove');g.emitEffectEvent('onMeldMove',{actor:'player'});assert.equal(g.state.player.status.endure,8);
}
{
 const g=fresh(),c=card(g,'VSDK');assert.equal(g.requestVSignalLegendChoice('player',c),true);g.resolveEffectChoice('shield');assert.equal(g.state.player.status.endure,16);
}
console.log('Reservations and all sixteen wave-two cards pass with actual engine behavior');

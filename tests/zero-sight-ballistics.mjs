import assert from 'node:assert/strict';
import {fresh,named,run} from './helpers/v3-fixture.mjs';
import {html} from './helpers/live-game.mjs';

const metadata=fresh().NAMED.ZSD6;assert.equal(metadata.slot,'D6');assert.equal(metadata.themeId,'zero-sight');assert.equal(metadata.t,'zsBallistics');
assert.ok(html.includes("items:['ZSD6']"),'the existing unlock identity remains');
for(const spec of [
 {power:0,hp:40,shield:0,endure:0,expected:22},
 {power:20,hp:40,shield:0,endure:0,expected:40},
 {power:30,hp:40,shield:0,endure:0,expected:40},
 {power:40,hp:40,shield:20,endure:10,expected:62},
 {power:20,hp:40,shield:0,endure:0,damp:100,expected:32},
 {power:30,hp:40,shield:7,endure:8,loaded:10,heat:8,damp:15,expected:55},
]){
 const g=fresh(),m=run(g,'enemy','D',[3,4,5]),c=named(g,'ZSD6');g.state.player.hand.push(c);g.setZeroSightTarget('player',m);g.applyOfficialStatus('meld',m,'mark',1,{actor:'player'});
 Object.assign(g.state.enemy,{hp:spec.hp,shield:spec.shield});g.state.enemy.status.endure=spec.endure;g.state.switchPower=spec.power;Object.assign(g.state.player.status,{loaded:spec.loaded||0,overheat:spec.heat||0,damp:spec.damp||0});
 assert.equal(g.attachCards('player',[c],'enemy',0),true);assert.equal(g.state.switchPower,spec.expected,JSON.stringify(spec));assert.equal(g.meldMarkValue(m,'player'),0);
}
for(const mode of ['unmarked','non-target','sealed','blocked','flat']){
 const g=fresh(),m=run(g,'enemy','D',[3,4,5]),c=named(g,'ZSD6');g.state.player.hand.push(c);if(mode!=='non-target')g.setZeroSightTarget('player',m);if(mode!=='unmarked')g.applyOfficialStatus('meld',m,'mark',1,{actor:'player'});
 if(mode==='sealed')g.state.player.status.seal=1;
 if(mode==='blocked')g.state.switchTarget='enemy';
 if(mode==='flat')g.returnSwitch('player',10,'flat',{flat:true,targetReturnEffects:[{kind:'ballistics',meld:m}]});
 else assert.equal(g.attachCards('player',[c],'enemy',0),mode!=='blocked');
 assert.equal(g.state.switchPower,mode==='blocked'||mode==='flat'?20:30);assert.equal(g.meldMarkValue(m,'player'),mode==='unmarked'?0:1);
}
console.log('ZERO-SIGHT Ballistics: precise capped deficit after return modifiers, endure, ownership and flat/failed guards passed');

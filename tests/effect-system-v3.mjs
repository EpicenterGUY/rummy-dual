import assert from 'node:assert/strict';
import {makeGame} from './helpers/live-game.mjs';
const g=makeGame(),s=g.state,p=s.player,e=s.enemy;
function reset(){s.gameOver=false;s.switchTarget='player';s.switchPower=20;s.fuseUsed=false;for(const x of [p,e]){x.status=g.blankStatus();x.graceArmed=false;x.returnedSwitchThisTurn=false;x.shield=0;x.hp=60;x.cores=3;x.melds=[]}}
function give(key,n=1,target=p,scope='player'){return g.applyOfficialStatus(scope,target,key,n,{silent:true})}
reset();give('loaded',10);give('damp',40);give('overheat',11);g.returnSwitch('player',10);assert.equal(s.switchPower,20);assert.equal(p.hp,54);assert.equal(s.switchTarget,'enemy');for(const k of ['loaded','damp','overheat'])assert.equal(g.officialStatusValue('player',p,k),0);
reset();give('loaded',8);s.switchTarget='enemy';assert.equal(g.returnSwitch('player',10).blocked,true);assert.equal(p.status.loaded,8);s.switchTarget='player';p.returnedSwitchThisTurn=true;g.returnSwitch('player',10);assert.equal(p.status.loaded,8);p.returnedSwitchThisTurn=false;g.returnSwitch('player',10,'flat',{flat:true});assert.equal(p.status.loaded,8);assert.equal(s.switchPower,20);
reset();give('endure',12);p.shield=10;g.damage('player',8);assert.equal(p.status.endure,12);g.damage('player',20);assert.equal(p.hp,54);assert.equal(p.status.endure,0);
reset();give('endure',100);g.turnStart('player');assert.equal(p.status.endure,100);g.damage('player',2);assert.equal(p.status.endure,0);assert.equal(p.hp,60);
reset();assert.equal(give('defer'),1);assert.equal(give('defer'),0);g.turnEnd('player');assert.equal(p.hp,60);assert.equal(s.switchPower,20);assert.equal(p.status.defer,0);assert.equal(give('defer'),0);g.turnEnd('player');assert.equal(p.hp,40);assert.equal(s.switchPower,0);
reset();s.switchPower=0;assert.equal(give('defer'),0);assert.equal(s.fuseUsed,false);
reset();give('defer');g.resetBombCycle();assert.equal(p.status.defer,0);assert.equal(p.graceArmed,false);
reset();give('overheat',120);g.returnSwitch('player',10);assert.equal(p.cores,2);assert.equal(s.switchTarget,'neutral');assert.equal(s.switchPower,0);
reset();const c=g.makeCard('C','5',true,'enemy','C5B');c.originOwner='player';give('comeback',1,c,'card');const rest=['3','4'].map(r=>g.makeCard('C',r,false,'enemy'));e.melds=[{type:'RUN',cards:[...rest,c],chain:4,status:g.blankMeldStatus()}];g.retireMeld('enemy',0);assert.ok(p.hand.includes(c));assert.equal(c.owner,'player');assert.equal(c.blockedUntilTurn,s.turnNo);assert.equal(g.officialStatusValue('card',c,'comeback'),0);assert.ok(!e.spent.includes(c));assert.equal(e.spent.filter(x=>rest.includes(x)).length,2);
reset();give('loaded',Infinity);assert.equal(p.status.loaded,0);give('loaded',-1);assert.equal(p.status.loaded,0);assert.equal(give('comeback',1,p),0);
// Card effects execute through the real resolver, including seal suppression.
function effect(id,type,ctx={}){const def=g.NAMED[id],slot=def.slot||id,c=g.makeCard(slot[0],slot.slice(1),true,'player',id);const m={type,cards:[c],status:g.blankMeldStatus()};return {c,m,result:g.resolveEffects('player',[c],type,{meld:m,totalLength:3,...ctx})}}
reset();effect('S7','RUN',{isAttach:true,targetOwner:'enemy',willReturn:false});assert.equal(p.status.loaded,10);g.returnSwitch('player',10);assert.equal(s.switchPower,40);
reset();give('seal');effect('S7','RUN',{isAttach:true,targetOwner:'enemy'});assert.equal(p.status.loaded||0,0);
reset();effect('S2','RUN',{isAttach:true,targetOwner:'enemy'});assert.equal(e.status.damp,10);
reset();effect('H7','SET');assert.equal(p.status.endure,12);
reset();effect('H7','SET',{isAttach:true,totalLength:4});assert.equal(p.status.endure,24);
reset();effect('D8','SET');assert.equal(s.switchPower,12);assert.equal(s.switchTarget,'player');assert.equal(p.status.endure,8);
reset();const branch=effect('C5B','RUN');assert.equal(g.officialStatusValue('card',branch.c,'comeback'),1);assert.equal(g.officialStatusValue('meld',branch.m,'protect'),1);
reset();s.turn='player';s.phase='action';const train=g.makeCard('S','10',true,'player'),jack=g.makeCard('S','J',false,'player');p.hand=[train,jack,g.makeCard('H','2',false,'player')];p.melds=[{type:'RUN',cards:['6','7','8','9'].map(r=>g.makeCard('S',r,false,'player')),chain:0,createdToken:s.turnToken-1,status:g.blankMeldStatus()}];assert.equal(g.attachCards('player',[train,jack],'player',0),true);assert.equal(p.status.overheat,0);assert.equal(p.hp,54);assert.equal(s.switchPower,57);assert.equal(s.switchTarget,'enemy');
give('loaded',5);const queen=g.makeCard('S','Q',false,'player');p.hand.push(queen);assert.equal(g.attachCards('player',[queen],'player',0),true);assert.equal(p.status.loaded,5);assert.equal(s.switchPower,77);
console.log('Effect system v3: return ordering, invalid/flat returns, damage, defer cycle, core break, card destinations and seven-card migration passed');

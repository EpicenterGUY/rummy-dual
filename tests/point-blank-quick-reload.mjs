import assert from 'node:assert/strict';
import {makeGame} from './helpers/live-game.mjs';
function setup(){const g=makeGame(),s=g.state.enemy;g.state.turn='enemy';g.state.phase='wait';s.hand=[];s.melds=[];const q=g.makeCard('D','J',true,'enemy','PBDJ');return{g,s,q}}
function arm(g,q){const m={type:'RUN',cards:[q],themeMeta:{}};g.ensurePointBlankMeta(m).clashBy.enemy=true;return g.handlePointBlankThemeEvent({event:'onRecover',actor:'enemy',card:q,meld:m,turnToken:g.state.turnToken})}
{
 const {g,q}=setup();assert.equal(g.handlePointBlankThemeEvent({event:'onRecover',actor:'enemy',card:q,meld:{},turnToken:1}),false);assert.equal(arm(g,q),true);assert.equal(arm(g,q),false,'one recovery arm per turn');
 q.recoveredToken=g.state.turnToken;assert.equal(g.recoveredCardCanReturn(q,g.state.turnToken,{}),false,'preparation reward never grants an attack reuse');
}
for(const used of [0,1,2]){
 const {g,s,q}=setup();arm(g,q);s.newMeldCount=used;const companions=['S','H'].map(suit=>g.makeCard(suit,'J',false,'enemy')),spare=g.makeCard('C','2',false,'enemy');s.hand=[q,...companions,spare];
 const access=g.newMeldAccess('enemy',s.hand.slice(0,3));assert.equal(access.allowed,used<2);assert.equal(access.extra,false);
 const before=s.status.endure||0,result=g.submitNewMeld('enemy',s.hand.slice(0,3));assert.equal(result,used<2);
 if(used<2){assert.equal((s.status.endure||0)-before,8);assert.equal(s.newMeldCount,used+1);assert.equal(q.quickReloadConsumedToken,g.state.turnToken)}else{assert.equal(s.status.endure||0,before);assert.notEqual(q.quickReloadConsumedToken,g.state.turnToken);assert.equal(g.bestNewMeldForTurn('enemy'),null)}
}
{
 const {g,s,q}=setup();arm(g,q);s.newMeldCount=0;s.melds=Array.from({length:3},()=>({type:'SET',cards:[]}));s.hand=[q,g.makeCard('S','J',false,'enemy'),g.makeCard('H','J',false,'enemy'),g.makeCard('C','2',false,'enemy')];
 assert.equal(g.submitNewMeld('enemy',s.hand.slice(0,3)),'full');assert.equal(s.status.endure||0,0);assert.notEqual(q.quickReloadConsumedToken,g.state.turnToken);
}
{
 const {g,s,q}=setup();arm(g,q);q.quickReloadConsumedToken=g.state.turnToken;s.hand=[q,g.makeCard('S','J',false,'enemy'),g.makeCard('H','J',false,'enemy'),g.makeCard('C','2',false,'enemy')];assert.equal(g.submitNewMeld('enemy',s.hand.slice(0,3)),true);assert.equal(s.status.endure||0,0,'consumed reward is not granted twice');
}
{
 const {g,s,q}=setup();arm(g,q);g.turnStart('enemy');s.hand=[q,g.makeCard('S','J',false,'enemy'),g.makeCard('H','J',false,'enemy'),g.makeCard('C','2',false,'enemy')];assert.equal(g.submitNewMeld('enemy',s.hand.slice(0,3)),true);assert.equal(s.status.endure||0,0,'previous turn reward expires');
}
console.log('PASS Quick Reload: clash-only arm, endure +8 once on either legal create, no third create, no fourth slot, no return exception, expiry');

import assert from 'node:assert/strict';
import {makeGame} from './helpers/live-game.mjs';
function fresh(w='enemy'){
 const g=makeGame();g.state.turn=w;g.state.phase='action';g.state.turnToken=7;g.state.switchPower=0;g.state.switchTarget=null;
 for(const side of ['player','enemy']){const s=g.state[side];s.hand=[];s.melds=[];s.newMeldCount=0;s.shield=0;s.hp=40;s.healedThisTurn=0;}
 return g;
}
const card=(g,slot,w='enemy',id=null)=>g.makeCard(slot[0],slot.slice(1),!!id,w,id);
const meld=(g,slots,w='enemy',type='RUN')=>({type,cards:slots.map(s=>card(g,s,w)),chain:slots.length-3,createdToken:0,status:g.blankMeldStatus(),themeMeta:{}});
// A synchronous one-option dispatch must finish exactly once, with 8 shield (not 16).
{
 const g=fresh(),s=g.state.enemy,c=card(g,'D6','enemy','MRD6'),spare=card(g,'HK');
 const cards=[card(g,'D4'),card(g,'D5'),c];s.hand=[...cards,spare];
 assert.equal(g.submitNewMeld('enemy',cards),true);
 assert.equal(s.shield,8);assert.equal(s.newMeldCount,1);assert.equal(s.melds.length,1);assert.equal(s.hand.length,1);assert.equal(g.isMailRouteCard(spare,'enemy'),true);
}
// The player can decline even with just one candidate; both branches resume once.
for(const skip of [true,false]){
 const g=fresh('player'),s=g.state.player,c=card(g,'D6','player','MRD6'),spare=card(g,'HK','player');
 const cards=[card(g,'D4','player'),card(g,'D5','player'),c];s.hand=[...cards,spare];
 assert.equal(g.submitNewMeld('player',cards),'choice');assert.ok(g.state.pendingEffectChoice);
 const key=skip?'__skip__':g.state.pendingEffectChoice.options[0].key;
 g.resolveEffectChoice(key);assert.equal(g.state.pendingEffectChoice,null);assert.equal(s.newMeldCount,1);assert.equal(s.melds.length,1);assert.equal(s.shield,skip?0:8);assert.equal(g.isMailRouteCard(spare),!skip);
}
// Reply shield is once per card per turn even when recovery notifications repeat.
{
 const g=fresh(),c=card(g,'HA','enemy','MRHA'),m=meld(g,['H2','H3','H4']);g.setMailRouteCard('enemy',c,{silent:true});
 g.emitMailRouteReturn('enemy',c,m);g.emitMailRouteReturn('enemy',c,m);assert.equal(g.state.enemy.shield,8);
 g.state.turnToken++;g.emitMailRouteReturn('enemy',c,m);assert.equal(g.state.enemy.shield,16);
}
// Actual combat-neutral moves trigger registered-mail protection, once each turn.
{
 const g=fresh(),s=g.state.enemy,src=meld(g,['D2','D3','D4','D5']),dst=meld(g,['S2','H2','C2'],'enemy','SET'),c=card(g,'D2','enemy','MRD2');src.cards[0]=c;s.melds=[src,dst];
 g.setMailRouteCard('enemy',c,{silent:true});g.setMailRouteDestination('enemy',dst,{silent:true});
 assert.ok(g.moveCardBetweenMelds('enemy',c,src,dst));assert.equal(g.officialStatusValue('meld',dst,'protect'),1);assert.equal(g.state.switchPower,0);assert.equal(g.state.switchTarget,null);
 g.emitMailRouteArrivals('enemy',[c],dst);assert.equal(g.officialStatusValue('meld',dst,'protect'),1);
}
// Receipt may arrive several times, but healing/shield cannot multiply on neutral moves.
{
 const g=fresh(),s=g.state.enemy,m=meld(g,['H5','H6','H7']),c=card(g,'H7','enemy','MRH7');m.cards[2]=c;s.melds=[m];g.setMailRouteCard('enemy',c,{silent:true});g.setMailRouteDestination('enemy',m,{silent:true});
 g.emitMailRouteArrivals('enemy',[c],m);g.emitMailRouteArrivals('enemy',[c],m);assert.equal(s.hp,44);assert.equal(s.shield,8);
 g.clearMailRouteCard(c,'test',true);assert.equal(g.isMailRouteCard(c),false);assert.equal(c.mailRouteLastArrivalMeld,null);
}
// The sender's destination may be on the other side, including for Postmaster.
{
 const g=fresh(),s=g.state.enemy,home=meld(g,['D9','D10','DJ']),dst=meld(g,['S4','S5','S6'],'player');home.cards[2]=card(g,'DJ','enemy','MRDJ');s.melds=[home];g.state.player.melds=[dst];const c=card(g,'S7');
 g.setMailRouteCard('enemy',c,{silent:true});g.setMailRouteDestination('enemy',dst,{silent:true});g.applyOfficialStatus('meld',dst,'seal',1,{actor:'enemy',silent:true});
 g.emitMailRouteArrivals('enemy',[c],dst,{targetSide:'player'});assert.equal(g.officialStatusValue('meld',dst,'seal'),0);
}
// Real retirement restores Joker King's original ownership and ends dispatch metadata.
{
 const g=fresh(),c=g.makeCard('J','J1',true,'player');c.owner='enemy';const m=meld(g,['S3','S4','S5']);m.cards.push(c);g.state.enemy.melds=[m];g.setMailRouteCard('enemy',c,{silent:true});
 g.retireMeld('enemy',0);assert.ok(g.state.player.deck.includes(c));assert.equal(c.owner,'player');assert.equal(g.isMailRouteCard(c),false);assert.ok(!g.state.enemy.spent.includes(c));
}
// Excluded staged cards do not alter ordinary rewards, even in a scarce pool.
{
 const g=fresh(),draft=g.createRoguelikeRunDraft('pure'),base={...g.roguelikeRunDeckProfile(draft),seed:'mail-staging'};
 const ids=Object.keys(g.NAMED),mail=ids.filter(id=>g.NAMED[id].themeId==='mail-route');assert.equal(mail.length,28);
 for(const id of ids.filter(id=>['v-signal','zero-sight','point-blank'].includes(g.NAMED[id].themeId))){const result=g.roguelikeRewardCandidates({slots:[g.namedSlot(id)],variants:{},poolIds:[id]});assert.equal(result.picks[0]?.id,id,'completed card stays reward-eligible: '+id);}
 const full=g.roguelikeRewardCandidates({...base,poolIds:ids}),old=g.roguelikeRewardCandidates({...base,poolIds:ids.filter(id=>!mail.includes(id))});
 assert.equal(JSON.stringify(full),JSON.stringify(old));assert.equal(g.roguelikeRewardCandidates({...base,poolIds:mail}).picks.length,0);
}
console.log('PASS MAIL-ROUTE live action continuation, optional choices, turn gates, movement, ownership and reward staging');

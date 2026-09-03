import assert from 'node:assert/strict';
import {fresh,plain,named,meld,run,nextTurn} from './helpers/v3-fixture.mjs';
const mute=(g,c)=>g.applyOfficialStatus('card',c,'silence',1,{actor:c.owner});
const byTag=(g,tag,owner='player')=>named(g,Object.keys(g.NAMED).find(id=>g.NAMED[id].t===tag),owner);
const ranks=['A','2','3','4','5','6','7','8','9','10','J','Q','K'];
function publicSource(g,c,board='player'){
 const r=ranks.indexOf(c.rank),lo=r<=9?r:r-3;
 return meld(g,board,ranks.slice(lo,lo+4).map(rank=>rank===c.rank?c:plain(g,c.suit,rank,board)));
}
for(const silent of [false,true]){
 {
  const g=fresh(),c=named(g,'H6');publicSource(g,c);if(silent)mute(g,c);g.heal('player',2);
  assert.equal(g.state.player.status.endure||0,silent?0:4);assert.equal(g.themeTurnGateUsed(c,'healAttack'),!silent,'a mute heal response does not spend its turn gate');
 }
 {
  const g=fresh(),c=named(g,'C7','enemy'),m=meld(g,'player',[plain(g,'C','5'),plain(g,'C','6'),c]);if(silent)mute(g,c);
  const eight=plain(g,'C','8');g.state.player.hand.push(eight);g.attachCards('player',[eight],'player',0);assert.equal(g.state.enemy.status.loaded||0,silent?0:8);
 }
 {
  const g=fresh(),c=named(g,'HK');c.healCharge=2;g.state.player.hand.push(c);if(silent)mute(g,c);g.heal('player',1);g.detonate('player');assert.equal(c.healCharge,silent?2:0);assert.equal(g.state.player.hp,silent?24:44);
 }
 {
  const g=fresh(),c=byTag(g,'ambushTrap','enemy');g.state.enemy.hand.push(c);if(silent)mute(g,c);const used=plain(g,'S','9');used.fromDiscard=true;g.triggerOpponentHandTraps('player',[used]);assert.equal(g.state.pendingTrapReduction||0,silent?0:10);
 }
 {
  const g=fresh(),c=named(g,'DA');g.state.player.hand.push(c);g.state.discard=[plain(g,'D','3'),plain(g,'C','9')];if(silent)mute(g,c);assert.equal(g.basicDiscardChoices('player').length,silent?1:2);
 }
 {
  const g=fresh(),c=named(g,'SQ'),m=meld(g,'enemy',[c,plain(g,'D','Q'),plain(g,'H','Q')],'SET');g.state.discard=[plain(g,'C','Q'),plain(g,'C','2'),plain(g,'D','9')];if(silent)mute(g,c);assert.equal(g.basicDiscardChoices('player').length,silent?1:2);
 }
 {
  const g=fresh(),c=byTag(g,'alternateBonus'),set=meld(g,'player',[plain(g,'S','5'),plain(g,'D','5'),plain(g,'H','5'),plain(g,'C','5')],'SET');publicSource(g,c);run(g,'player','H',['2','3','4']);if(silent)mute(g,c);assert.equal(g.tunerReadyForRecovery('player','player',set,set.cards[2]),!silent);
 }
 for(const tag of ['vEncore','pbQuickReload','pbSidearm','ambulance','fuseRound']){
  const g=fresh(),c=byTag(g,tag),source=publicSource(g,c,'enemy');g.setPointBlankClash('player',source);
  if(tag==='vEncore')meld(g,'player',['S','H','D','C'].filter(s=>s!==c.suit).map(s=>plain(g,s,c.rank)),'SET');
  if(tag==='fuseRound'){c.fuseArmed=true;c.fuseReadyStart=3}
  if(silent)mute(g,c);assert.ok(g.recoverSpecificFromMeld('player',source,c,{free:true}));
  if(tag==='vEncore')assert.equal(c.recoverReturnOverrideToken===g.state.turnToken,!silent);
  if(tag==='pbQuickReload')assert.equal(c.quickReloadNewMeldToken===g.state.turnToken,!silent);
  if(tag==='pbSidearm')assert.equal(!!g.state.pendingEffectChoice,!silent);
  if(tag==='ambulance'){assert.equal(g.state.player.hp,silent?40:48);assert.equal(g.state.player.status.endure||0,silent?0:8)}
  if(tag==='fuseRound'){assert.equal(g.state.player.status.loaded||0,silent?0:12);assert.equal(c.fuseArmed,silent)}
 }
 {
  const g=fresh(),c=byTag(g,'zsSafeDistance'),source=publicSource(g,c),target=run(g,'enemy','D',['2','3','4','5']);target.cards[0].owner='player';g.setZeroSightTarget('player',target);if(silent)mute(g,c);
  g.recoverSpecificFromMeld('player',target,target.cards[0],{free:true});assert.equal(g.state.player.status.endure||0,silent?0:8);assert.equal(g.state.zeroSightLastRecoverActor,'player','silence does not suppress action history');
 }
 {
  const g=fresh(),c=byTag(g,'zsObservationLog'),target=publicSource(g,c);g.setZeroSightTarget('player',target);if(silent)mute(g,c);nextTurn(g);g.emitEffectEvent('onAttach',{actor:'player',meld:target,targetSide:'player',targetedBy:['player'],cards:[],returned:true,phase:'afterResolve'});assert.equal(g.state.player.status.loaded||0,silent?0:8);
 }
 {
  const g=fresh(),c=byTag(g,'zsDrone');publicSource(g,c);if(silent)mute(g,c);nextTurn(g,'enemy');const cards=['S','H','D'].map(s=>plain(g,s,'9','enemy'));g.state.enemy.hand.push(...cards);g.submitNewMeld('enemy',cards);const target=g.state.enemy.melds[0];assert.equal(g.isZeroSightTarget('player',target),!silent);assert.equal(g.meldMarkValue(target,'player'),silent?0:1);
 }
 {
  const g=fresh(),c=byTag(g,'zsRangefinder');publicSource(g,c);if(silent)mute(g,c);const target=run(g,'enemy','D',['2','3','4']);g.setZeroSightTarget('player',target);assert.equal(!!g.state.pendingEffectChoice,!silent);
 }
 {
  const g=fresh(),c=byTag(g,'zsDeadAngle'),target=publicSource(g,c,'enemy');g.setZeroSightTarget('player',target);g.applyOfficialStatus('meld',target,'fracture',1,{actor:'player'});if(silent)mute(g,c);nextTurn(g,'enemy');const recover=target.cards[0]===c?target.cards.at(-1):target.cards[0];g.recoverSpecificFromMeld('enemy',target,recover,{free:true});assert.equal(g.state.enemy.status.vulnerable||0,silent?0:1);assert.equal(g.state.enemy.hp,34,'shared fracture damage remains independent of the mute source');
 }
 {
  const g=fresh(),c=named(g,'VSS9','enemy'),target=meld(g,'enemy',[plain(g,'S','7','enemy'),plain(g,'S','8','enemy'),c]);if(silent)mute(g,c);const ten=plain(g,'S','10');g.state.player.hand.push(ten);g.attachCards('player',[ten],'enemy',0);assert.equal(g.state.enemy.effectReservations.length,silent?0:1);
 }
 for(const id of ['HA','H10','J2','VSH10','VSHK']){
  const g=fresh(),c=named(g,id,'enemy');g.state.turn='enemy';g.state.switchTarget='enemy';g.state.enemy.hand=[];if(silent)mute(g,c);g.triggerRummy('enemy',[c]);
  assert.equal(g.state.enemy.hand.length,id==='HA'&&!silent?7:6,'core RUMMY reload survives silence');
  if(id==='H10'||id==='VSH10')assert.equal(g.state.enemy.status.regen||0,silent?0:1);
  if(id==='J2')assert.equal(g.state.enemy.jokerLastDetonateReduction||0,silent?0:15);
  if(id==='VSHK')assert.equal(g.state.enemy.effectReservations.length,silent?0:2);
 }
 for(const id of ['J1','HQ']){
  const g=fresh(),c=named(g,id),cards=id==='HQ'?[c,plain(g,'S','J'),plain(g,'S','K')]:[c,plain(g,'S','5'),plain(g,'S','6')],m=meld(g,'player',cards);g.markSetCompletion(m,'player');if(silent)mute(g,c);g.retireMeld('player',0);
  assert.equal(g.state.player.spent.includes(c),silent);assert.equal((id==='J1'?g.state.player.deck:g.state.player.hand).includes(c),!silent);
 }
 for(const id of ['J4','J5']){
  const g=fresh(),c=named(g,id),m=meld(g,'player',[c,plain(g,'S','5'),plain(g,'S','6')]);if(silent)mute(g,c);const seven=plain(g,'S','7');g.state.player.hand.push(seven);g.attachCards('player',[seven],'player',0);assert.equal(m.cards.includes(c),silent);assert.equal(g.state.player.hand.includes(c),!silent);
 }
 for(const tag of ['returnIfIgnored','heal2']){
  const g=fresh(),c=byTag(g,tag);(tag==='heal2'?g.state.player.spent:g.state.discard).push(c);g.state.player.lastDetonateTaken=8;if(silent)mute(g,c);g.turnStart('player');assert.equal(g.state.player.hand.includes(c),!silent);
 }
 {
  const g=fresh(),c=named(g,'D6');g.state.player.hand.push(c);if(silent)mute(g,c);g.state.selected=new Set([c.uid]);g.state.selectionOrder=[c.uid];g.playerDiscard();assert.equal(!!g.state.pendingEffectChoice,!silent);assert.equal(g.state.discard.includes(c),silent);
 }
}
{
 const g=fresh(),c=byTag(g,'zsObservationLog'),m=publicSource(g,c);mute(g,c);g.setZeroSightTarget('player',m);assert.equal(m.themeMeta.zeroSight.observationReadyBy.player[c.uid],undefined);
 g.clearOfficialStatus('card',c,'silence');assert.equal(m.themeMeta.zeroSight.observationReadyBy.player[c.uid],4,'unmuting starts observation immediately on the existing target');
 nextTurn(g);g.emitEffectEvent('onAttach',{actor:'player',meld:m,targetSide:'player',targetedBy:['player'],cards:[],returned:true,phase:'afterResolve'});assert.equal(g.state.player.status.loaded,8);
}
console.log('PASS silence across shared, hand, discard, spent, RUMMY, retirement, recovery, ZERO-SIGHT, V-SIGNAL and POINT-BLANK reactions');

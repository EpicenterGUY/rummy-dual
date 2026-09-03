import assert from 'node:assert/strict';
import {fresh,plain,named,run,meld,nextTurn} from './helpers/v3-fixture.mjs';

// Warmth grants another card comeback without moving it, and uses actual 4 HP healing.
for(const oneCandidate of [false,true]){
 const g=fresh(),p=g.state.player,m=run(g,oneCandidate?'enemy':'player','H',['2','3','4']),c=named(g,'H5');p.hand.push(c);
 if(oneCandidate)m.cards[1].owner='player';const target=m.cards[1],before=p.hand.length;
 const result=g.attachCards('player',[c],oneCandidate?'enemy':'player',0);
 if(!oneCandidate){assert.equal(result,'choice');assert.ok(g.state.pendingEffectChoice.options.every(o=>o.card!==c));assert.equal(g.state.switchPower,20);g.resolveEffectChoice(String(target.uid));}
 else assert.equal(result,true);
 assert.equal(g.officialStatusValue('card',target,'comeback'),1);assert.equal(g.officialStatusValue('card',c,'comeback'),0);assert.equal(p.hp,44);assert.equal(p.hand.length,before-1);assert.equal(m.cards.length,4);assert.equal(g.state.switchPower,30,'resuming the choice returns only once');
}
{
 const g=fresh(),m=run(g,'player','H',['2','3','4']),c=named(g,'H5');g.state.player.hand.push(c);g.state.player.status.seal=1;
 assert.equal(g.attachCards('player',[c],'player',0),true);assert.equal(g.state.player.hp,40);assert.ok(m.cards.every(c=>!g.officialStatusValue('card',c,'comeback')));
}
{
 const g=fresh(),m=run(g,'player','H',['2','3','4']),c=named(g,'H5');g.state.player.hand.push(c);g.attachCards('player',[c],'player',0);
 const target=g.state.pendingEffectChoice.options[0].card;target.owner='enemy';g.resolveEffectChoice(String(target.uid));
 assert.equal(g.officialStatusValue('card',target,'comeback'),0);assert.equal(g.state.player.hp,40,'a changed owner invalidates the pending grant');
}
// Crossfire selects an owned card in another own SET and keeps the BURST action / retirement intact.
{
 const g=fresh(),p=g.state.player,other=meld(g,'player',['S','H','C'].map(s=>plain(g,s,'6')),'SET'),clash=meld(g,'enemy',['S','H','C'].map(s=>plain(g,s,'4','enemy')),'SET');
 clash.cards[0].owner='player';other.cards[0].owner='enemy';g.setPointBlankClash('player',clash);
 const c=named(g,'PBD4');p.hand.push(c);const before=p.hand.length,deck=p.deck.length;
 assert.equal(g.attachCards('player',[c],'enemy',0),'choice');assert.equal(g.state.pendingEffectChoice.options.length,2);
 const chosen=g.state.pendingEffectChoice.options[0].card;g.resolveEffectChoice(String(chosen.uid));
 assert.equal(g.officialStatusValue('card',chosen,'comeback'),1);assert.equal(p.hand.length,before-1);assert.equal(p.deck.length,deck);assert.ok(!g.state.enemy.melds.includes(clash));assert.equal(g.state.switchPower,44);
}
// Collab Request also triggers after both types have already been used this turn; circulation stays 1-for-1.
{
 const g=fresh(),p=g.state.player,spare=plain(g,'D','Q'),c=named(g,'VSC8');const target=run(g,'enemy','C',['5','6','7']);
 const set=['S','H','D'].map(s=>plain(g,s,'2')),ownRun=['8','9','10'].map(r=>plain(g,'H',r));p.hand.push(...set,...ownRun,c,spare);
 assert.equal(g.submitNewMeld('player',set),true);assert.equal(g.submitNewMeld('player',ownRun),true);
 const before=p.hand.length;assert.equal(g.attachCards('player',[c],'enemy',0),'choice');assert.equal(p.status.loaded,6);assert.equal(g.state.switchPower,20);
 g.resolveEffectChoice(String(spare.uid));assert.equal(p.hand.length,before-1);assert.equal(p.deck[0],spare);assert.equal(p.maintenanceUsed,false);assert.equal(g.state.switchPower,36);assert.equal(p.status.loaded,0);
 g.resolveEffects('player',[c],'RUN',{meld:target,isAttach:true,willReturn:false});assert.equal(p.status.loaded,0,'card-turn gate survives resolver reentry');
}
// ON AIR begins at CHAIN 0. The first completed own attach rewards loading after its return.
{
 const g=fresh(),p=g.state.player,c=named(g,'VSCA'),cards=[c,plain(g,'C','2'),plain(g,'C','3')];p.hand.push(...cards);
 assert.equal(g.submitNewMeld('player',cards),true);const m=p.melds[0];assert.equal(m.chain,0);assert.equal(p.effectReservations.length,1);
 const four=plain(g,'C','4');p.hand.push(four);assert.equal(g.attachCards('player',[four],'player',0),false);assert.equal(p.effectReservations.length,1);
 nextTurn(g);assert.equal(g.attachCards('player',[four],'player',0),true);assert.equal(g.state.switchPower,30);assert.equal(p.status.loaded,8);assert.equal(p.effectReservations.length,0);
 const five=plain(g,'C','5');p.hand.push(five);assert.equal(g.attachCards('player',[five],'player',0),true);assert.equal(g.state.switchPower,45);assert.equal(p.status.loaded,8,'same-RUN continuation preserves loading');
 nextTurn(g);g.state.switchTarget='player';const six=plain(g,'C','6');p.hand.push(six);assert.equal(g.attachCards('player',[six],'player',0),true);assert.equal(g.state.switchPower,73);assert.equal(p.status.loaded,0);
}
for(const removal of ['retire','reshape','recirculate','expire']){
 const g=fresh(),p=g.state.player,source=named(g,'VSCA'),target=run(g,'player','C',['A','2','3','4','5','6']);
 assert.equal(g.reserveEffect('player',source,'onAttach','loaded',8,'player',{targetMeld:target}),true);
 if(removal==='retire')g.retireMeld('player',0);
 if(removal==='reshape')g.applyMeldReshape('player',g.meldReshapeCandidates('player').find(x=>x.kind==='split'));
 if(removal==='recirculate')g.fullRecirculation('test');
 if(removal==='expire'){g.state.switchPower=0;nextTurn(g);g.turnEnd('player');}
 assert.equal(p.effectReservations.length,0,`${removal} cancels a pending scoped reservation`);assert.equal(p.status.loaded||0,0);
}
{
 const g=fresh(),p=g.state.player,source=named(g,'VSCA'),target=run(g,'player','C',['2','3','4']);target.cards.unshift(source);
 g.reserveEffect('player',source,'onAttach','loaded',8,'player',{targetMeld:target});assert.ok(g.recoverSpecificFromMeld('player',target,source,{free:true}));
 const five=plain(g,'C','5');p.hand.push(five);assert.equal(g.attachCards('player',[five],'player',0),true);assert.equal(p.status.loaded,8,'source departure does not cancel the surviving target reservation');
}
// Reverse Viral listens on either public board and can pay on a different meld after its source retires.
for(const board of ['player','enemy']){
 const g=fresh(),p=g.state.player,c=named(g,'VSS9'),source=meld(g,board,[plain(g,'S','7',board),plain(g,'S','8',board),c]);
 nextTurn(g,'enemy');g.state.switchTarget='enemy';const ten=plain(g,'S','10','enemy');g.state.enemy.hand.push(ten);assert.equal(g.attachCards('enemy',[ten],board,0),true);
 assert.equal(p.effectReservations.length,1);const reservation=p.effectReservations[0];
 const jack=plain(g,'S','J','enemy');g.state.enemy.hand.push(jack);assert.equal(g.attachCards('enemy',[jack],board,0),true);assert.equal(p.effectReservations.length,1);assert.equal(p.effectReservations[0],reservation);
 g.retireMeld(board,g.state[board].melds.indexOf(source));assert.equal(p.effectReservations.length,1);
 nextTurn(g,'player');g.state.switchTarget='enemy';assert.equal(g.returnSwitch('player',10).blocked,true);assert.equal(p.effectReservations.length,1,'failed return cannot consume the reservation');
 g.state.switchTarget='player';const before=g.state.switchPower;run(g,'enemy','H',['2','3','4']);const five=plain(g,'H','5');p.hand.push(five);g.attachCards('player',[five],'enemy',0);
 assert.equal(g.state.switchPower,before+20);assert.equal(p.effectReservations.length,0);assert.equal(p.status.loaded,0);
}
{
 const g=fresh(),p=g.state.player,c=named(g,'VSS9');g.reserveEffect('player',c,'onReturnSwitch','loaded',10,'player',{untilReturn:true});g.state.switchPower=0;
 nextTurn(g);g.turnEnd('player');nextTurn(g);g.turnEnd('player');assert.equal(p.effectReservations.length,1,'next-return reservations have no hidden turn timeout');
 g.state.switchTarget='player';g.returnSwitch('player',0,'flat',{flat:true});assert.equal(p.effectReservations.length,0);assert.equal(p.status.loaded,10,'flat return resolves the reservation but keeps unspent loading');
}
// Million Subscribers reserves both statuses on the same first surviving published card, including pure cards.
{
 const g=fresh(),p=g.state.player,c=named(g,'VSHK','player');c.originOwner='enemy';p.hand=[c];g.applyOfficialStatus('card',c,'comeback',1,{actor:'player'});
 meld(g,'enemy',['S','D','C'].map(s=>plain(g,s,'K','enemy')),'SET');
 assert.equal(g.attachCards('player',[c],'enemy',0),'rummy');assert.equal(c.owner,'enemy');assert.ok(g.state.enemy.hand.includes(c));
 assert.equal(p.effectReservations.length,2,'the RUMMY reward follows the actor who used the card, even after comeback restores its original owner');
}
{
 const g=fresh(),e=g.state.enemy;g.state.turn='enemy';e.hand=[];assert.equal(g.triggerRummy('enemy',[named(g,'VSHK','enemy')]),'rummy');assert.equal(e.effectReservations.length,2);assert.equal(e.shield,0);
 const from=run(g,'enemy','H',['A','2','3','4']),to=run(g,'enemy','H',['5','6','7']);assert.ok(g.moveCardBetweenMelds('enemy',from.cards[3],from,to));assert.equal(e.effectReservations.length,2,'public-to-public movement is not publication');
 nextTurn(g,'enemy');const cards=['H','D','S'].map(s=>plain(g,s,'9','enemy'));e.hand.push(...cards);assert.equal(g.submitNewMeld('enemy',cards),true);
 assert.equal(e.effectReservations.length,0);assert.equal(e.shield,0);assert.equal(g.officialStatusValue('card',cards[0],'comeback'),1);assert.equal(g.officialStatusValue('card',cards[0],'protect'),1);
 for(const c of cards.slice(1)){assert.equal(g.officialStatusValue('card',c,'comeback'),0);assert.equal(g.officialStatusValue('card',c,'protect'),0);}
}
for(const finish of ['win','draw']){
 const g=fresh(),p=g.state.player,c=named(g,'VSS9');g.reserveEffect('player',c,'onReturnSwitch','loaded',10,'player',{untilReturn:true});
 if(finish==='win'){g.state.enemy.cores=0;g.checkGameOver()}else{g.state.enemy.hp=p.hp;g.resolveCirculationStalemate()}
 assert.equal(g.state.gameOver,true);assert.equal(p.effectReservations.length,0);assert.equal(g.reserveEffect('player',c,'onReturnSwitch','loaded',10,'player',{untilReturn:true}),false);
}
console.log('PASS v3 publication/return reservations and card grants: timing, choices, cancellation, mixed ownership and no duplicate payouts');

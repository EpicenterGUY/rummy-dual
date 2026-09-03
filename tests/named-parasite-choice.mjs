import assert from 'node:assert/strict';
import {fresh,named,plain,run,nextTurn} from './helpers/v3-fixture.mjs';
// Parasite now rewards its owner after a real return from the opponent's board.
for(const parasiteOwner of ['player','enemy']){
 const g=fresh(),attacker=g.other(parasiteOwner),p=g.state[parasiteOwner],foe=g.state[attacker];g.state.turn=attacker;g.state.switchTarget=attacker;
 const m=run(g,attacker,'C',['5','6']),c=named(g,'C7',parasiteOwner);m.cards.push(c);const a=plain(g,'C','8',attacker),b=plain(g,'C','9',attacker);foe.hand.push(a,b);
 const hands=[p.hand.length,foe.hand.length],decks=[p.deck.length,foe.deck.length];
 assert.equal(g.attachCards(attacker,[a],attacker,0),true);assert.equal(p.status.loaded||0,8);assert.equal(g.state.pendingEffectChoice,null);assert.deepEqual([p.deck.length,foe.deck.length],decks);assert.equal(p.hand.length,hands[0]);
 assert.equal(g.attachCards(attacker,[b],attacker,0),true);assert.equal(p.status.loaded||0,8,'same-RUN continuation cannot trigger another reaction');
 g.emitEffectEvent('onAttach',{actor:attacker,meld:m,returned:true});assert.equal(p.status.loaded||0,8,'duplicate packet cannot award twice');
 g.retireMeld(attacker,0);assert.equal(p.status.loaded||0,8,'prepared loaded survives source retirement');
 nextTurn(g,parasiteOwner);g.state.switchTarget=parasiteOwner;g.returnSwitch(parasiteOwner,10);assert.equal(p.status.loaded||0,0);
}
{
 const g=fresh(),m=run(g,'player','C',['5','6']),c=named(g,'C7');m.cards.push(c);const a=plain(g,'C','8','enemy');g.state.enemy.hand.push(a);g.state.turn='enemy';g.state.switchTarget='enemy';
 assert.equal(g.attachCards('enemy',[a],'player',0),true);assert.equal(g.state.player.status.loaded||0,0,'own board is not the opponent board');
}
{
 const g=fresh(),m=run(g,'enemy','C',['5','6']),c=named(g,'C7');m.cards.push(c);const a=plain(g,'C','8','enemy');g.state.enemy.hand.push(a);g.state.turn='enemy';g.state.switchTarget='player';
 assert.equal(g.attachCards('enemy',[a],'enemy',0),false);assert.equal(g.state.player.status.loaded||0,0,'failed return cannot react');
}
console.log('PASS Parasite: post-return loaded 8, both sides, no draw/discard choice, continuation/duplicate guard and source lifetime');

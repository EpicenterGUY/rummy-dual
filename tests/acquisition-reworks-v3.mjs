import assert from 'node:assert/strict';
import {fresh,plain,named,run,meld,nextTurn} from './helpers/v3-fixture.mjs';

function drawGame(){const g=fresh();g.state.phase='draw';return g}
function sentence(g,board='player',owner='player'){
 return meld(g,board,[named(g,'SQ',owner),plain(g,'H','Q',board),plain(g,'D','Q',board)],'SET');
}

// Fence adds a choice to the one base acquisition; it does not grant an extra card.
for(const pick of ['second','cancel']){
 const g=drawGame(),p=g.state.player,fence=named(g,'DA');p.hand.push(fence);
 const second=plain(g,'D','5','enemy'),top=plain(g,'C','K','enemy');g.state.discard=[second,top];
 const acquired=[];g.subscribeEffectEvent(e=>{if(e.event==='onAcquire')acquired.push(e)});
 const hand=p.hand.length,deck=p.deck.length;
 assert.equal(g.playerDraw(true),true);assert.equal(g.state.pendingEffectChoice.options.length,2);
 assert.equal(g.playerDraw(false),false,'another acquisition cannot run under the choice modal');
 assert.equal(p.hand.length,hand);assert.equal(p.deck.length,deck);
 g.resolveEffectChoice(pick==='cancel'?'__skip__':String(second.uid));
 if(pick==='cancel'){
  assert.equal(g.state.phase,'draw');assert.equal(p.hand.length,hand);assert.equal(acquired.length,0);assert.equal(second.owner,'enemy');
 }else{
  assert.equal(g.state.phase,'action');assert.equal(p.hand.length,hand+1);assert.ok(p.hand.includes(second));
  assert.equal(second.owner,'player');assert.equal(second.originOwner,'enemy');assert.deepEqual(Array.from(g.state.discard),[top]);
  assert.equal(acquired.length,1);assert.equal(acquired[0].source,'discard');assert.equal(acquired[0].basic,true);
  assert.equal(g.playerDraw(false),false);assert.equal(g.acquireBasicCard('player',false),null,'base acquisition token is already spent');
 }
}
{
 const g=drawGame(),fence=named(g,'DA','enemy'),second=plain(g,'C','8','enemy');g.state.discard=[second,fence];
 assert.equal(g.basicDiscardChoices('player').length,1,'taking Fence does not enable its hand effect retroactively');
 assert.equal(g.playerDraw(true),true);assert.equal(g.state.pendingEffectChoice,null);assert.deepEqual(Array.from(g.state.discard),[second]);
}
// Death Sentence can search an exact missing card only in the top three, even on the opponent's board.
for(const board of ['player','enemy']){
 const g=drawGame();sentence(g,board);const wanted=plain(g,'C','Q','enemy'),second=plain(g,'C','7','enemy'),top=plain(g,'S','2','enemy');
 g.state.discard=[wanted,second,top];assert.deepEqual(Array.from(g.basicDiscardChoices('player'),x=>x.depth),[0,2]);
 g.renderDiscard();assert.match(g.document.getElementById('discardRuleText').textContent,/세 번째 \(사형선고\)/);
 g.playerDraw(true);g.resolveEffectChoice(String(wanted.uid));
 assert.ok(g.state.player.hand.includes(wanted));assert.equal(wanted.originOwner,'enemy');assert.deepEqual(Array.from(g.state.discard),[second,top]);
}
{
 const g=drawGame(),m=sentence(g);const wanted=plain(g,'C','Q','enemy');g.state.discard=[wanted,plain(g,'S','2'),plain(g,'H','3'),plain(g,'D','4')];
 assert.equal(g.basicDiscardChoices('player').length,1,'the fourth card is outside the search window');
 g.state.discard.shift();g.state.discard.splice(0,0,plain(g,'C','K'));
 assert.equal(g.basicDiscardChoices('player').length,1,'wrong rank cannot substitute for the exact missing card');
 g.state.discard[0]=wanted;m.cards[0].owner='enemy';
 assert.equal(g.basicDiscardChoices('player').length,1,'search follows the Death Sentence card controller');
}
// Fence / Sentence / Black Market share choices without charging a free alternative's cost.
{
 const g=drawGame();sentence(g);g.state.player.hand.push(named(g,'DA'));g.state.field={tag:'blackMarket'};
 const wanted=plain(g,'C','Q','enemy'),second=plain(g,'S','5','enemy'),top=plain(g,'C','K','enemy');g.state.discard=[wanted,second,top];
 const choices=g.basicDiscardChoices('player');assert.equal(choices.length,3);assert.equal(choices[1].spendTopUid,null);
 g.playerDraw(true);g.resolveEffectChoice(String(second.uid));assert.deepEqual(Array.from(g.state.discard),[wanted,top]);assert.equal(g.state.enemy.spent.length,0);
}
for(const actor of ['player','enemy']){
 const g=drawGame();g.state.turn=actor;g.state.field={tag:'blackMarket'};
 const deep=plain(g,'H','3'),second=plain(g,'D','5','enemy'),top=plain(g,'S','8','player');g.state.discard=[deep,second,top];
 const before=g.state[actor].hand.length,choice=g.basicDiscardChoices(actor)[1],result=g.acquireBasicCard(actor,true,choice);
 assert.equal(result.card,second);assert.equal(second.owner,actor);assert.equal(second.originOwner,'enemy');assert.equal(second.fromDiscard,true);
 assert.equal(g.state[actor].hand.length,before+1);assert.deepEqual(Array.from(g.state.discard),[deep]);assert.ok(g.state.player.spent.includes(top),'only the displaced top card pays Black Market');
}
{
 const g=drawGame();g.state.field={tag:'blackMarket'};const second=plain(g,'D','5'),top=plain(g,'C','K');g.state.discard=[second,top];
 g.playerDraw(true);const hand=g.state.player.hand.length;g.state.discard.push(plain(g,'H','2'));
 g.resolveEffectChoice(String(second.uid));assert.equal(g.state.player.hand.length,hand);assert.equal(g.state.discard.length,3);assert.equal(g.state.player.spent.length,0);assert.equal(g.state.phase,'draw','stale choices cannot spend a different top card');
}

// Appraiser counts playable destinations, including ownership, turn locks and the return budget.
for(const invalid of [null,'direction','new','used','blocked']){
 const g=drawGame(),p=g.state.player,c=named(g,'D7B','enemy');g.state.discard=[c];
 const own=run(g,'player','D',['3','4','5','6']);meld(g,'enemy',['S','H','C'].map(s=>plain(g,s,'7','enemy')),'SET');
 if(invalid==='direction')g.state.switchTarget='enemy';
 if(invalid==='new')own.createdToken=g.state.turnToken;
 if(invalid==='used')own.lastAttachToken=g.state.turnToken;
 if(invalid==='blocked')c.blockedUntilTurn=g.state.turnNo;
 g.playerDraw(true);const rewarded=invalid===null;
 assert.equal(p.status.endure||0,rewarded?8:0);assert.equal(g.officialStatusValue('card',c,'comeback'),rewarded?1:0);assert.equal(p.shield,0);
 g.onDiscardDraw('player',c);assert.equal(p.status.endure||0,rewarded?8:0,'the same acquired card cannot pay twice in one turn');
}
// Monopolist is armed by an actual BURST; the blocked player's deck draw offers one optional cycle.
for(const useCycle of [false,true]){
 const g=fresh(),p=g.state.player,e=g.state.enemy;g.state.turn='enemy';g.state.switchTarget='enemy';
 const m=meld(g,'player',['S','H','C'].map(s=>plain(g,s,'K')),'SET'),c=named(g,'DK','enemy');e.hand.push(c);
 assert.equal(g.attachCards('enemy',[c],'player',0),true);assert.equal(p.blockOpponentDiscardNext,true);
 nextTurn(g,'player');g.state.phase='draw';const hand=p.hand.length,deck=p.deck.length;
 assert.equal(g.playerDraw(true),false);assert.equal(p.hand.length,hand);
 assert.equal(g.playerDraw(false),true);assert.equal(p.hand.length,hand+1);assert.equal(p.blockOpponentDiscardNext,false);assert.ok(g.state.pendingEffectChoice.allowSkip);
 const card=g.state.pendingEffectChoice.options[0].card;
 g.resolveEffectChoice(useCycle?String(card.uid):'__skip__');
 assert.equal(p.hand.length,hand+1);assert.equal(p.deck.length,deck-1);assert.equal(p.maintenanceUsed,false);
 if(useCycle)assert.equal(p.deck[0],card);
 assert.equal(g.state.pendingEffectChoice,null);assert.equal(g.playerDraw(false),false);
}
{
 const g=drawGame(),p=g.state.player;p.blockOpponentDiscardNext=true;g.drawOne('player',false);
 assert.equal(p.blockOpponentDiscardNext,true);assert.equal(g.state.pendingEffectChoice,null,'effect draws cannot consume or receive the base-acquisition compensation');
}
{
 const g=drawGame(),p=g.state.player;p.blockOpponentDiscardNext=true;p.deck=[];p.spent=[];g.state.discard=[plain(g,'C','Q','enemy')];
 const before=p.hand.length;assert.equal(g.playerDraw(false),false);assert.equal(p.hand.length,before);assert.equal(g.state.phase,'action');assert.equal(g.state.pendingEffectChoice,null,'no successful deck acquisition means no free compensation draw');
}
// CPU sees deeper legal cards, and still pauses for the original owner's Bait choice.
for(const bait of [false,true]){
 const g=fresh(),e=g.state.enemy;e.hand=[named(g,'DA','enemy'),plain(g,'S',bait?'3':'5','enemy'),plain(g,'D',bait?'3':'5','enemy')];
 const second=bait?named(g,'H3'):plain(g,'H','5'),top=plain(g,'C','K');g.state.discard=[second,top];
 const acquired=[];g.subscribeEffectEvent(event=>{if(event.event==='onAcquire')acquired.push(event)});
 g.aiTurn();assert.equal(acquired.length,1);assert.equal(acquired[0].card,second);assert.equal(acquired[0].actor,'enemy');assert.equal(second.owner,'enemy');assert.equal(second.originOwner,'player');
 if(bait){assert.ok(g.state.pendingEffectChoice);assert.equal(g.state.turn,'enemy');g.resolveEffectChoice(g.state.pendingEffectChoice.options[0].key);assert.equal(acquired.length,1,'resuming Bait does not repeat acquisition');}
 assert.equal(g.state.turn,'player');assert.ok(g.state.discard.includes(top));
}
{
 const g=drawGame();g.startTutorial('basic');const p=g.state.player,top=plain(g,'D','5','enemy');g.state.discard=[top];
 const hand=p.hand.length,deck=p.deck.length;assert.equal(g.playerDraw(true),false);assert.equal(p.hand.length,hand);assert.equal(p.deck.length,deck);assert.equal(g.state.discard[0],top);
 assert.equal(g.playerDraw(false),true);assert.equal(p.hand.length,hand+1);assert.equal(g.state.phase,'action','the allowed tutorial acquisition still reaches the action phase');
}
console.log('PASS v3 acquisition reworks: exact top-three search, shared choices/costs, legal appraisal, compensation and CPU continuations');

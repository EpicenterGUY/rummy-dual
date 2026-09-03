import assert from 'node:assert/strict';
import {fresh,plain,named,meld,run,nextTurn} from './helpers/v3-fixture.mjs';
const charge=(g,c)=>g.officialStatusValue('card',c,'flexible');
const choose=(g,c)=>assert.equal(g.resolveEffectChoice(`flexible:${c.uid}`),true);
{const g=fresh();for(const id of ['D7','VSD2','VSC4']){assert.ok(g.namedTendencies(id).includes('상태'));assert.ok(!g.namedTendencies(id).includes('순환'))}}

for(const acquired of ['companion','self','none']){
 const g=fresh(),gold=named(g,'D7'),companion=plain(g,'S','7'),cards=[gold,companion,plain(g,'H','7')],left=plain(g,'C','K');g.state.player.hand=[...cards,left];
 if(acquired==='companion')companion.fromDiscard=true;if(acquired==='self')gold.fromDiscard=true;
 const deck=g.state.player.deck.length;assert.equal(g.submitNewMeld('player',cards),true);assert.equal(g.state.pendingEffectChoice,null);
 assert.equal(charge(g,companion),Number(acquired==='companion'));assert.equal(charge(g,gold),Number(acquired==='self'));assert.equal(charge(g,left),0);
 assert.equal(g.state.player.deck.length,deck);assert.deepEqual(Array.from(g.state.player.hand),[left],'Golden Hand no longer draws or cycles');
 assert.ok(cards.every(c=>!c.flexibleRole),'granting to a published card never changes its current material');
}
for(const invalidate of [false,true]){
 const g=fresh(),gold=named(g,'D7'),a=plain(g,'S','7'),b=plain(g,'H','7'),cards=[gold,a,b];a.fromDiscard=b.fromDiscard=true;g.state.player.hand=[...cards,plain(g,'C','K')];let completed=0;
 g.subscribeEffectEvent(p=>{if(p.event==='onMeldCreate')completed++});
 assert.equal(g.submitNewMeld('player',cards),'choice');assert.equal(completed,0);assert.equal(g.state.pendingEffectChoice.options.length,2);assert.equal(g.resolveEffectChoice('__skip__'),false);
 const callback=g.state.pendingEffectChoice.onChoose,option=g.state.pendingEffectChoice.options.find(x=>x.card===b);if(invalidate)b.owner='enemy';choose(g,b);callback(option);
 assert.equal(charge(g,b),Number(!invalidate));assert.equal(charge(g,a),0);assert.equal(completed,1,'a resumed effect and its action finish exactly once');
}
// The preserved Buyout King alias resolves before Golden Hand, even in reversed play order.
{
 const g=fresh(),gold=named(g,'D7'),buyer=named(g,'D10'),cards=[gold,plain(g,'D','8'),plain(g,'D','9'),buyer];run(g,'enemy','D',['4','5','6']);g.state.player.hand.push(...cards);g.state.lastEnemyDiscardRank='10';
 assert.equal(g.attachCards('player',cards,'enemy',0),true);assert.equal(charge(g,buyer),1);assert.equal(charge(g,gold),0);assert.equal(buyer.flexibleRole??null,null);assert.equal(g.state.pendingEffectChoice,null);
}

{
 const g=fresh(),source=named(g,'VSD2'),cards=[source,plain(g,'S','2'),plain(g,'H','2')],a=plain(g,'S','8'),b=plain(g,'H','4');g.state.player.hand=[...cards,a,b];let completed=0;g.subscribeEffectEvent(p=>{if(p.event==='onMeldCreate')completed++});
 const deck=g.state.player.deck.length;assert.equal(g.submitNewMeld('player',cards),'choice');assert.equal(completed,0);assert.deepEqual(Array.from(g.state.pendingEffectChoice.options,x=>x.card),[a,b]);choose(g,b);
 assert.equal(charge(g,b),1);assert.equal(charge(g,a),0);assert.equal(charge(g,source),0);assert.equal(g.state.player.deck.length,deck);assert.deepEqual(Array.from(g.state.player.hand),[a,b]);assert.equal(completed,1);
}
for(const kind of ['new-run','attach-set','empty-hand']){
 const g=fresh(),source=named(g,'VSD2'),left=plain(g,'S','K');
 if(kind==='attach-set'){meld(g,'enemy',['S','H','C'].map(s=>plain(g,s,'2','enemy')),'SET');g.state.player.hand=[source,left];assert.equal(g.attachCards('player',[source],'enemy',0),true)}
 else{const cards=kind==='new-run'?[plain(g,'D','A'),source,plain(g,'D','3')]:[source,plain(g,'S','2'),plain(g,'H','2')];g.state.player.hand=kind==='empty-hand'?cards:[...cards,left];assert.equal(g.submitNewMeld('player',cards),kind==='empty-hand'?'rummy':true)}
 assert.equal(g.state.pendingEffectChoice,null);assert.ok(g.state.player.hand.every(c=>!charge(g,c)),`${kind}: no grant outside new SET's remaining hand, including RUMMY redraw`);
}

for(const beforeChain of [0,1,2]){
 const g=fresh(),source=named(g,'VSC4'),ranks=beforeChain===0?['5','6','7']:beforeChain===1?['5','6','7','8']:['5','6','7','8','9'],m=run(g,'enemy','C',ranks,{chain:beforeChain}),left=plain(g,'H','2');g.state.player.hand=[source,left];
 g.applyOfficialStatus('card',source,'flexible',1,{silent:true});const plan=g.legalRankChoicePlansForAttach(m,[source]).find(x=>x.plan[0].flexibleChoice==='keep');
 assert.equal(g.attachCards('player',[source],'enemy',0,plan.plan),true);assert.equal(charge(g,left),Number(beforeChain<=1));assert.equal(charge(g,source),0);assert.equal(source.flexibleRole.rank,'4');assert.equal(source.flexibleRole.choice,'keep','entry grant cannot rewrite the value already used in this action');
}
{
 const g=fresh(),source=named(g,'VSC4'),cards=[source,plain(g,'C','5'),plain(g,'C','6')],left=plain(g,'H','2');g.state.player.hand=[...cards,left];g.submitNewMeld('player',cards);assert.equal(charge(g,left),0,'Game Broadcast requires attachment');
}
for(const status of ['seal','silence']){
 const g=fresh(),source=named(g,'VSD2'),cards=[source,plain(g,'S','2'),plain(g,'H','2')],left=plain(g,'C','K');g.state.player.hand=[...cards,left];g.applyOfficialStatus('card',source,status,1,{actor:'player',silent:true});
 g.submitNewMeld('player',cards);assert.equal(charge(g,left),Number(status==='silence'),'seal cancels entry; silence preserves entry');
}
{
 const g=fresh(),source=named(g,'VSD2'),cards=[source,plain(g,'S','2'),plain(g,'H','2')],left=[plain(g,'C','K'),plain(g,'C','Q')];g.state.player.hand=[...cards,...left];g.submitNewMeld('player',cards);const q=g.state.pendingEffectChoice;nextTurn(g);q.onChoose(q.options[0]);assert.ok(left.every(c=>!charge(g,c)),'stale targeting cannot grant into a later turn');
}

// CPU chooses a useful pure-card target and executes the resulting flexible extension.
{
 const g=fresh();nextTurn(g,'enemy');g.state.switchTarget='enemy';const source=named(g,'VSD2','enemy'),cards=[source,plain(g,'S','2','enemy'),plain(g,'C','2','enemy')],useful=plain(g,'H','2','enemy'),other=plain(g,'S','9','enemy');g.state.enemy.hand=[...cards,useful,other];run(g,'player','H',['4','5','6']);
 assert.equal(g.submitNewMeld('enemy',cards),true);assert.equal(charge(g,useful),1);assert.equal(charge(g,other),0);assert.equal(g.state.pendingEffectChoice,null);
 const plan=g.bestExtensionFromHand('enemy',g.state.enemy.hand);assert.ok(plan);assert.ok(plan.cards.includes(useful));assert.equal(plan.rankPlan.find(x=>x.uid===useful.uid).rank,'3');
 assert.equal(g.attachCards('enemy',plan.cards,plan.side,plan.index,plan.rankPlan),true);assert.equal(charge(g,useful),0);assert.equal(g.cardText(useful),'3♥');
}
console.log('PASS Golden Hand, Rookie Set and Game Broadcast: exact targets, existing discard alias, timing, seal/silence, empty hand, resumption and CPU');

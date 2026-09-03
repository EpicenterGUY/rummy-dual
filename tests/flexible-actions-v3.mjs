import assert from 'node:assert/strict';
import {fresh,plain,named,meld,run,nextTurn} from './helpers/v3-fixture.mjs';
const grant=(g,c)=>g.applyOfficialStatus('card',c,'flexible',1,{silent:true});

for(const denial of ['returned','switch-away','recovered','blocked','duplicate','foreign-hand','stale-charge']){
 const g=fresh(),m=run(g,'enemy','H',['4','5','6']),c=plain(g,'H','2');g.state.player.hand.push(c);grant(g,c);
 const plan=g.legalRankChoicePlansForAttach(m,[c])[0].plan;
 if(denial==='returned')g.state.player.returnedSwitchThisTurn=true;
 if(denial==='switch-away')g.state.switchTarget='enemy';
 if(denial==='recovered')c.recoveredToken=g.state.turnToken;
 if(denial==='blocked')c.blockedUntilTurn=g.state.turnNo;
 if(denial==='foreign-hand'){g.state.player.hand.splice(g.state.player.hand.indexOf(c),1);g.state.enemy.hand.push(c)}
 if(denial==='stale-charge')g.clearOfficialStatus('card',c,'flexible');
 const before=JSON.stringify({c,hand:g.state.player.hand,m,power:g.state.switchPower});
 assert.equal(g.attachCards('player',denial==='duplicate'?[c,c]:[c],'enemy',0,plan),false,denial);
 assert.equal(JSON.stringify({c,hand:g.state.player.hand,m,power:g.state.switchPower}),before,`${denial}: no partial status spend or placement`);
}
for(const denial of ['slots','generation','game-over']){
 const g=fresh(),c=plain(g,'H','2'),cards=[c,plain(g,'H','4'),plain(g,'H','5')];grant(g,c);g.state.player.hand=[...cards,plain(g,'D','K')];
 if(denial==='slots')for(const suit of ['S','D','C'])run(g,'player',suit,['7','8','9']);
 if(denial==='generation')g.state.player.newMeldCount=2;
 if(denial==='game-over')g.state.gameOver=true;
 const plan=g.legalRankChoicePlansForNewMeld(cards)[0].plan,before=JSON.stringify(cards);
 assert.equal(g.submitNewMeld('player',cards,plan),denial==='slots'?'full':false);assert.equal(JSON.stringify(cards),before);
}

{
 const g=fresh(),m=run(g,'enemy','S',['4','5','6']),a=plain(g,'H','3'),b=plain(g,'S','8');g.state.player.hand.push(a,b);grant(g,a);grant(g,b);
 const plan=g.legalRankChoicePlansForAttach(m,[a,b]).find(x=>x.plan[0].suit==='S'&&x.plan[1].rank==='7');assert.ok(plan);
 assert.equal(g.attachCards('player',[a,b],'enemy',0,plan.plan),true);assert.ok(g.runValid(m.cards));assert.equal(m.chain,2);assert.equal(g.state.switchPower,45);assert.equal(a.suit,'H');assert.equal(b.rank,'8');
 assert.equal(a.officialStatus.flexible,0);assert.equal(b.officialStatus.flexible,0);
 const eight=plain(g,'S','8');g.state.player.hand.push(eight);assert.equal(g.attachCards('player',[eight],'enemy',0),true,'later continuation reads committed 7 rather than printed 8');assert.ok(g.runValid(m.cards));
}

{
 const g=fresh(),m=meld(g,'enemy',['S','H','D'].map(s=>plain(g,s,'5','enemy')),'SET'),c=plain(g,'C','4');g.state.player.hand.push(c);grant(g,c);let observed=null;
 g.subscribeEffectEvent(p=>{if(p.event==='onAttach')observed=g.cardRuleRank(c)});
 const plan=g.legalRankChoicePlansForAttach(m,[c])[0].plan;assert.equal(g.attachCards('player',[c],'enemy',0,plan),true);
 assert.equal(observed,'5');assert.equal(g.state.switchPower,44);assert.equal(g.state.enemy.melds.length,0);assert.ok(g.state.player.spent.includes(c));assert.equal(c.rank,'4');assert.equal(c.flexibleRole,null);assert.equal(c.officialStatus.flexible,0);
}

// Public-to-public movement preserves a committed role and does not spend a future charge.
{
 const g=fresh(),source=run(g,'enemy','H',['4','5','6']),c=plain(g,'H','2');g.state.player.hand.push(c);grant(g,c);
 assert.equal(g.attachCards('player',[c],'enemy',0,g.legalRankChoicePlansForAttach(source,[c])[0].plan),true);grant(g,c);
 const target=meld(g,'player',['S','D','C'].map(s=>plain(g,s,'3')),'SET'),role=JSON.stringify(c.flexibleRole),power=g.state.switchPower;
 assert.equal(g.moveExtortedCard('player',target,{meld:source,card:c}),true);assert.ok(g.runValid(source.cards));assert.ok(g.setValid(target.cards));
 assert.equal(JSON.stringify(c.flexibleRole),role);assert.equal(c.officialStatus.flexible,1);assert.equal(g.state.switchPower,power);
}

// Recovery planning projects the post-hand-reset card, then applies only destination-bound permission.
{
 const g=fresh(),source=run(g,'player','H',['4','5','6']),c=plain(g,'H','2');g.state.player.hand.push(c);grant(g,c);
 g.attachCards('player',[c],'player',0,g.legalRankChoicePlansForAttach(source,[c])[0].plan);nextTurn(g);g.state.switchTarget='player';
 const target=meld(g,'player',['S','D','C'].map(s=>plain(g,s,'3')),'SET');meld(g,'player',[plain(g,'C','Q'),named(g,'CK'),plain(g,'C','A')]);
 assert.ok(!g.legalRecoveryReturnTargets('player',c,source,{ownOnly:true}).includes(target),'old public 3 is reset to printed 2 during recovery');assert.equal(g.tunerReadyForRecovery('player','player',source,c),false);
 grant(g,c);assert.ok(g.legalRecoveryReturnTargets('player',c,source,{ownOnly:true}).includes(target));assert.equal(g.tunerReadyForRecovery('player','player',source,c),true);
 assert.equal(g.recoverSpecificFromMeld('player',source,c,{allowReturnReuse:true,requiredType:'SET',ownOnly:true}),c);assert.equal(c.flexibleRole,null);assert.equal(c.rank,'2');assert.equal(c.officialStatus.flexible,1);assert.ok(c.recoverReturnTargets.includes(target));
 assert.equal(g.attachCards('player',[c],'player',1,g.legalRankChoicePlansForAttach(target,[c])[0].plan),true);assert.equal(c.officialStatus.flexible,0);assert.equal(c.flexibleRole,null,'burst retirement clears the newly committed role');
}

{
 const g=fresh(),c=plain(g,'D','7'),cards=[c,plain(g,'S','7'),plain(g,'C','7')];g.state.field={tag:'heartHeal'};g.state.player.hand=[...cards,plain(g,'D','K')];grant(g,c);
 const plan=g.legalRankChoicePlansForNewMeld(cards).find(x=>x.plan[0].suit==='H');assert.equal(g.submitNewMeld('player',cards,plan.plan),true);assert.equal(g.state.player.hp,44,'Heart field reads the effective played suit');assert.equal(c.suit,'D');
 assert.match(g.cardHTML(c),/7♥ 사용/);assert.match(g.cardHTML(c),/>♦</);g.renderDetail(c);const detail=g.document.getElementById('detail').innerHTML;
 assert.match(detail,/슬롯|가변 사용값/);assert.match(detail,/가변 사용값 7♥/);assert.match(detail,/공개 중 고정/);
}
{
 const g=fresh(),gap=named(g,'C4'),source=meld(g,'player',[plain(g,'C','A'),plain(g,'C','3'),gap]),c=plain(g,'C','3');g.state.player.hand.push(c);grant(g,c);
 const plan=g.legalRankChoicePlansForAttach(source,[c]).find(x=>x.plan[0].rank==='2');assert.ok(plan);assert.equal(g.attachCards('player',[c],'player',0,plan.plan),true);
 assert.ok(g.state.player.hand.includes(gap),'the committed 2 fills the actual gap and recovers Gap Run');assert.ok(!source.cards.includes(gap));assert.ok(g.runValid(source.cards));assert.equal(c.rank,'3');assert.equal(g.materialRank(c),'2');
}
{
 const g=fresh();nextTurn(g,'enemy');g.state.switchTarget='enemy';const source=run(g,'enemy','H',['4','5','6']),c=plain(g,'H','2','enemy');g.state.enemy.hand.push(c);grant(g,c);
 g.attachCards('enemy',[c],'enemy',0,g.legalRankChoicePlansForAttach(source,[c])[0].plan);nextTurn(g,'enemy');g.state.enemy.hand=[plain(g,'S','2','enemy'),plain(g,'D','2','enemy'),plain(g,'S','K','enemy')];
 const recovery=g.bestRecoverAI('enemy');assert.equal(recovery?.card,c,'CPU plans a new SET using printed 2 after public 3 is cleared');g.executeRecoverAI('enemy',recovery);
 const plan=g.bestNewMeldForTurn('enemy');assert.ok(plan?.cards.includes(c));assert.equal(g.submitNewMeld('enemy',plan.cards,plan.rankPlan),true);assert.equal(g.materialRank(c),'2');assert.equal(c.flexibleRole,null);
}
console.log('PASS flexible actions: denial gates, multi-attach, burst, continuation, movement, recovery destinations and effective-suit feedback');

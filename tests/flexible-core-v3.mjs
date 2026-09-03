import assert from 'node:assert/strict';
import {fresh,plain,named} from './helpers/v3-fixture.mjs';
const charge=(g,c)=>g.officialStatusValue('card',c,'flexible');
const grant=(g,c)=>g.applyOfficialStatus('card',c,'flexible',1,{silent:true});

{
 const g=fresh(),c=plain(g,'S','7');g.state.player.hand.push(c);
 assert.equal(g.officialStatusAllowed('card','flexible'),true);assert.equal(g.officialStatusAllowed('meld','flexible'),false);
 grant(g,c);grant(g,c);assert.equal(charge(g,c),1,'a second grant does not stack');
 for(const amount of [0,-1,0.5,Infinity,NaN]){assert.equal(g.applyOfficialStatus('card',c,'flexible',amount,{silent:true}),0);assert.equal(charge(g,c),1,'invalid grants cannot erase an existing charge')}
 const options=g.rankChoiceOptions(c);assert.equal(options.length,6);
 assert.deepEqual(Array.from(options,x=>x.flexibleChoice),['keep','rank:-1','rank:+1','suit:H','suit:D','suit:C']);
 assert.ok(options.every(x=>x.usesFlexible&&x.choiceRequired&&(x.rank==='7'||x.suit==='S')),'one spend cannot change rank and suit together');
 for(const [rank,forbidden,allowed] of [['A','K','2'],['K','A','Q']]){const edge=plain(g,'S',rank);grant(g,edge);const choices=g.rankChoiceOptions(edge);assert.ok(!choices.some(x=>x.rank===forbidden));assert.ok(choices.some(x=>x.rank===allowed))}
 const joker=named(g,'J1');grant(g,joker);const choices=g.rankChoiceOptions(joker);assert.equal(choices.length,1);assert.equal(choices[0].flexibleChoice,'keep');assert.equal(choices[0].suit,'J');
}

{
 const g=fresh(),c=plain(g,'H','2'),cards=[c,plain(g,'H','4'),plain(g,'H','5')];g.state.player.hand=[...cards,plain(g,'D','K')];grant(g,c);
 const before=JSON.stringify(cards),legal=g.legalRankChoicePlansForNewMeld(cards);
 assert.equal(legal.length,1);assert.equal(legal[0].plan[0].rank,'3');assert.equal(legal[0].plan[0].flexibleChoice,'rank:+1');
 assert.equal(JSON.stringify(cards),before,'preview never commits a role or spends flexible');
 assert.equal(g.submitNewMeld('player',cards),false,'even a single legal flexible value requires an explicit plan');
 const forged=legal[0].plan.map(x=>({...x}));forged[0].suit='S';assert.equal(g.submitNewMeld('player',cards,forged),false);assert.equal(JSON.stringify(cards),before);
 assert.equal(g.submitNewMeld('player',cards,legal[0].plan),true);
 assert.equal(c.rank,'2');assert.equal(c.baseRank,'2');assert.equal(c.suit,'H');assert.equal(g.cardRuleRank(c),'3');assert.equal(g.cardText(c),'3♥');assert.equal(charge(g,c),0);assert.ok(g.runValid(cards));
 grant(g,c);const role=JSON.stringify(c.flexibleRole);assert.equal(g.rankChoiceOptions(c).length,1);assert.equal(g.playerRankChoiceRequired([c]),false,'public re-grant is for the next hand placement');
 assert.equal(JSON.stringify(c.flexibleRole),role);g.retireMeld('player',0,'test');
 assert.equal(c.flexibleRole,null);assert.equal(c.rank,'2');assert.equal(charge(g,c),1,'unspent future charge survives retirement');assert.ok(g.state.player.spent.includes(c));
 g.state.player.spent.splice(g.state.player.spent.indexOf(c),1);g.enterHand('player',c);assert.equal(g.rankChoiceOptions(c).length,6);
}

{
 const g=fresh(),c=plain(g,'H','2'),others=[plain(g,'S','4'),plain(g,'S','5')];grant(g,c);
 assert.equal(g.legalRankChoicePlansForNewMeld([c,...others]).length,0,'H2 cannot become S3 in one use');
 const a=plain(g,'C','5'),cards=[a,plain(g,'C','5'),plain(g,'H','5')];grant(g,a);
 const legal=g.legalRankChoicePlansForNewMeld(cards);assert.deepEqual(Array.from(legal,x=>x.plan[0].suit),['S','D']);
 g.state.player.hand=[...cards,plain(g,'D','K')];assert.equal(g.submitNewMeld('player',cards,legal[0].plan),true);assert.equal(a.suit,'C');assert.equal(g.cardRuleSuit(a),'S');assert.ok(g.setValid(cards));
 const waiting=plain(g,'D','7');grant(g,waiting);g.state.player.hand.push(waiting);g.state.player.hand.splice(g.state.player.hand.indexOf(waiting),1);g.pushDiscard(waiting);assert.equal(charge(g,waiting),1,'discard is not a public placement');
}

// Flexible is a granted status, independent of intrinsic abilities stopped by silence.
{
 const g=fresh(),c=named(g,'D5'),cards=[plain(g,'D','A'),plain(g,'D','2'),c];g.state.player.hand=[...cards,plain(g,'S','K')];grant(g,c);
 const legal=g.legalRankChoicePlansForNewMeld(cards),plan=legal.find(x=>x.plan[2].rank==='4');assert.ok(plan,'flexible -1 then Counterfeiter -1 yields the missing 3');
 assert.equal(g.submitNewMeld('player',cards,plan.plan),true);assert.equal(c.rank,'5');assert.equal(c.flexibleRole.rank,'4');
 g.applyOfficialStatus('card',c,'silence',1,{actor:'player'});assert.ok(g.runValid(cards));assert.equal(g.materialRank(c),'3','silence freezes the already-established intrinsic role');assert.equal(c.flexibleRole.rank,'4');
 g.clearOfficialStatus('card',c,'silence');assert.ok(g.runValid(cards));assert.equal(c.flexibleRole.rank,'4');
 const pure=plain(g,'H','2');g.state.player.hand.push(pure);grant(g,pure);g.applyOfficialStatus('card',pure,'silence',1,{actor:'player'});
 assert.ok(g.legalRankChoicePlansForNewMeld([pure,plain(g,'H','4'),plain(g,'H','5')]).length,'silence does not disable a pending flexible charge');
}

{
 const g=fresh(),c=plain(g,'S','7');c.topRank='2';c.bottomRank='7';const cards=[c,plain(g,'H','3'),plain(g,'D','3')];grant(g,c);g.state.player.hand=[...cards,plain(g,'D','K')];
 const plan=g.legalRankChoicePlansForNewMeld(cards)[0];assert.equal(plan.plan[0].orientation,'top');assert.equal(plan.plan[0].printedRank,'2');assert.equal(plan.plan[0].rank,'3');
 assert.equal(g.submitNewMeld('player',cards,plan.plan),true);assert.equal(c.rank,'2');assert.equal(c.activeRank,'2');assert.equal(c.baseRank,'7');assert.equal(g.cardRuleRank(c),'3');
 assert.equal(g.rankResolutionPriority(c,'SET').join('>'),'printed-choice>flexible-choice');g.retireMeld('player',0,'test');assert.equal(c.rank,'7');assert.equal(c.activeRank,null);assert.equal(c.flexibleRole,null);
}
{
 const g=fresh(),c=named(g,'HQ'),cards=[plain(g,'C','10'),plain(g,'C','J'),c];g.state.player.hand=[...cards,plain(g,'D','K')];grant(g,c);
 const plan=g.legalRankChoicePlansForNewMeld(cards).find(x=>x.plan[2].suit==='C');assert.ok(plan);g.submitNewMeld('player',cards,plan.plan);
 assert.equal(c.flexSuitOffSuit,true,'Understudy compares its actual RUN role to its printed heart');g.retireMeld('player',0,'test');assert.ok(g.state.player.hand.includes(c));assert.equal(c.suit,'H');assert.equal(c.flexibleRole,null);
}
console.log('PASS flexible contract: bounded choices, atomic commitment, printed identity, zone lifetime, silence and intrinsic modifier priority');

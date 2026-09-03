import assert from 'node:assert/strict';
import {fresh,plain,named,meld} from './helpers/v3-fixture.mjs';
const mute=(g,c)=>g.applyOfficialStatus('card',c,'silence',1,{actor:c.owner});
// Silence removes unused flexibility in hand without changing printed rank/suit or Joker identity.
for(const [id,others,type] of [
 ['HQ',[['S','J'],['S','K']],'RUN'],['D4',[['S','3'],['S','5']],'RUN'],
 ['C3',[['S','4'],['H','5']],'RUN'],['D5',[['D','7'],['D','8']],'RUN'],
 ['C4',[['C','6'],['C','7']],'RUN'],['CQ',[['S','7'],['H','7']],'SET']
]){
 const g=fresh(),c=named(g,id),cards=[c,...others.map(([s,r])=>plain(g,s,r))];if(id==='D4')c.smuggledTurnToken=g.state.turnToken;
 assert.equal(g.meldType(cards),type,id);const printed=[c.rank,c.suit];mute(g,c);assert.equal(g.meldType(cards),null,`${id}: new passive material role is unavailable`);assert.deepEqual([c.rank,c.suit],printed);
}
for(const [id,others,type,extension] of [
 ['HQ',[['S','J'],['S','K']],'RUN',['S','10']],['D4',[['S','3'],['S','5']],'RUN',['S','6']],
 ['C3',[['S','4'],['H','5']],'RUN',['S','6']],['D5',[['D','7'],['D','8']],'RUN',['D','9']],
 ['C4',[['C','6'],['C','7']],'RUN',['C','8']],['CQ',[['S','7'],['H','7']],'SET',['D','7']]
]){
 const g=fresh(),c=named(g,id),cards=[c,...others.map(([s,r])=>plain(g,s,r))];if(id==='D4')c.smuggledActive=true;
 const m=meld(g,'player',cards,type);assert.equal(g.meldType(cards),type);const printed=[c.rank,c.suit];mute(g,c);
 assert.equal(g.meldType(m.cards),type,`${id}: existing public material remains valid`);assert.equal(g.meldType(m.cards.concat(plain(g,...extension))),type,`${id}: ordinary extension preserves the committed role`);assert.deepEqual([c.rank,c.suit],printed);
 g.clearOfficialStatus('card',c,'silence');assert.equal(g.meldType(m.cards),type);assert.equal(c.silenceRole,null);
}
{
 const g=fresh(),c=named(g,'C4'),m=meld(g,'player',[c,plain(g,'C','6'),plain(g,'C','7')]);mute(g,c);
 assert.equal(g.runValid([c,plain(g,'C','5'),plain(g,'C','7')]),false,'a frozen gap at 5 cannot become a new gap at 6');
 const five=plain(g,'C','5');g.state.player.hand.push(five);g.attachCards('player',[five],'player',0);assert.ok(m.cards.includes(c),'filling the gap does not trigger muted automatic recovery');
}
{
 const g=fresh(),c=named(g,'C3'),four=plain(g,'S','4'),five=plain(g,'H','5'),m=meld(g,'player',[c,four,five]);mute(g,c);
 assert.equal(g.runValid([c,four,plain(g,'H','5')]),false,'the muted bridge cannot grant its old exception to a different card');
}
{
 const g=fresh(),c=named(g,'CQ'),m=meld(g,'player',[c,plain(g,'S','7'),plain(g,'H','7')],'SET');mute(g,c);
 assert.equal(g.setValid([c,plain(g,'S','8'),plain(g,'H','8')]),false,'a committed borrowed 7 does not copy a new rank while muted');
 g.retireMeld('player',0);g.state.player.spent=g.state.player.spent.filter(x=>x!==c);g.state.player.deck.push(c);g.drawOne('player');assert.equal(c.silenceRole,null);assert.equal(g.setValid([c,plain(g,'S','7'),plain(g,'H','7')]),false,'leaving public play clears the frozen role');
}
{
 const g=fresh(),c=named(g,'J1');mute(g,c);assert.equal(g.isJoker(c),true);assert.equal(g.setValid([c,plain(g,'S','7'),plain(g,'H','7')]),true);
 const a=plain(g,'S','7');a.topRank='3';a.bottomRank='7';mute(g,a);const plans=g.legalRankChoicePlansForNewMeld([a,plain(g,'H','3'),plain(g,'D','3')]);assert.equal(plans.length,1);assert.equal(plans[0].plan[0].rank,'3','printed asymmetric rank choice is not a passive card ability');
}
console.log('PASS silence keeps exact public material roles without permitting new rank/suit/gap grants');

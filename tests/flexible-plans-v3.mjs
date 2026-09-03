import assert from 'node:assert/strict';
import {fresh,plain,named,run,nextTurn} from './helpers/v3-fixture.mjs';
const grant=(g,c)=>g.applyOfficialStatus('card',c,'flexible',1,{silent:true});
const key=plan=>JSON.stringify(Array.from(plan,p=>[p.uid,p.rank,p.suit,p.orientation,p.printedRank,p.flexibleChoice]));

// Independent exhaustive oracle: filter the entire Cartesian product, without prefix pruning.
function exhaustive(g,cards,m=null){
 const options=cards.map(c=>g.rankChoiceOptions(c)),out=[];
 function enumerate(i,plan){
  if(i===cards.length){const projected=g.projectRankChoiceCards(cards,plan),type=g.meldType((m?.cards||[]).concat(projected));if(type&&(!m||type===m.type))out.push(key(plan));return}
  for(const pick of options[i])enumerate(i+1,[...plan,pick]);
 }
 enumerate(0,[]);return out.sort();
}
for(const field of [null,'crossLane','tangled'])for(let specimen=0;specimen<8;specimen++){
 const g=fresh();g.state.field=field?{tag:field}:null;
 const cards=specimen===0?[plain(g,'S','3'),plain(g,'S','4'),plain(g,'S','5')]
  :specimen===1?[named(g,'D5'),plain(g,'D','2'),plain(g,'D','3')]
  :specimen===2?[named(g,'C4'),plain(g,'C','2'),plain(g,'C','6')]
  :specimen===3?[named(g,'C3'),plain(g,'H','4'),plain(g,'S','5')]
  :specimen===4?[named(g,'CQ'),plain(g,'S','3'),plain(g,'H','3')]
  :specimen===5?[plain(g,'S','A'),plain(g,'S','K'),plain(g,'S','2')]
  :specimen===6?[plain(g,'S','5'),plain(g,'H','5'),plain(g,'D','5')]
  :[named(g,'J1'),plain(g,'S','2'),plain(g,'H','4')];
 if(specimen===5)cards[0].bottomRank='Q';
 cards.forEach(c=>grant(g,c));g.state.player.hand=cards;const before=JSON.stringify(cards);
 const actual=Array.from(g.legalRankChoicePlansForNewMeld(cards),x=>key(x.plan)).sort();assert.deepEqual(actual,exhaustive(g,cards),`${field}/${specimen}: pruning must preserve every legal plan`);assert.equal(JSON.stringify(cards),before);
}

{
 const g=fresh(),m=run(g,'enemy','C',['4','5','6']),cards=[plain(g,'S','7'),plain(g,'H','8'),plain(g,'D','9')];cards.forEach(c=>grant(g,c));g.state.player.hand=[...cards,plain(g,'D','K')];
 const truncated=g.rankChoicePlans(cards);assert.equal(truncated.length,64);assert.ok(truncated.every(p=>!g.runValid(m.cards.concat(g.projectRankChoiceCards(cards,p)))),'the former 64-plan prefix misses the entire valid region');
 const legal=g.legalRankChoicePlansForAttach(m,cards);assert.equal(legal.length,1);assert.ok(legal[0].plan.every(p=>p.suit==='C'));
 assert.deepEqual(Array.from(legal,x=>key(x.plan)).sort(),exhaustive(g,cards,m));assert.equal(g.attachCards('player',cards,'enemy',0,legal[0].plan),true);assert.ok(g.runValid(m.cards));
}
{
 const g=fresh(),gap=named(g,'C4'),m=run(g,'player','C',['A','3']);m.cards.push(gap);g.applyOfficialStatus('card',gap,'silence',1,{actor:'player'});
 const c=plain(g,'C','6');grant(g,c);g.state.player.hand.push(c);const plans=g.legalRankChoicePlansForAttach(m,[c]);assert.ok(plans.length);assert.deepEqual(Array.from(plans,x=>key(x.plan)).sort(),exhaustive(g,[c],m),'frozen gap allowance participates in flexible planning');
}

function manyPlans(){const g=fresh(),cards=['S','H','D'].map(s=>plain(g,s,'5'));cards.forEach(c=>grant(g,c));g.state.player.hand=[...cards,plain(g,'C','K')];return{g,cards}}
// Long choice lists narrow by one card first; no values are silently truncated.
{
 const {g,cards}=manyPlans();let completed=0;assert.ok(g.legalRankChoicePlansForNewMeld(cards).length>16);const before=JSON.stringify(cards);
 assert.equal(g.requestPlayerRankChoice(cards,null,{onChoose:plan=>{completed++;assert.equal(g.submitNewMeld('player',cards,plan),true)}}),true);
 assert.equal(g.state.pendingEffectChoice.options[0].kind,'rankGroup');let steps=0;
 while(g.state.pendingEffectChoice){const q=g.state.pendingEffectChoice;assert.ok(q.options.length<=16);assert.equal(JSON.stringify(cards),before);g.resolveEffectChoice(q.options[0].key);assert.ok(++steps<=4)}
 assert.equal(completed,1);assert.ok(cards.every(c=>c.officialStatus.flexible===0&&c.flexibleRole));assert.ok(g.setValid(cards));
}
for(const narrowFirst of [false,true]){
 const {g,cards}=manyPlans(),before=JSON.stringify(cards);let completed=0;g.requestPlayerRankChoice(cards,null,{onChoose:()=>completed++});if(narrowFirst)g.resolveEffectChoice(g.state.pendingEffectChoice.options[0].key);
 assert.equal(g.resolveEffectChoice('__skip__'),true);assert.equal(g.state.pendingEffectChoice,null);assert.equal(completed,0);assert.equal(JSON.stringify(cards),before,'cancel before commitment keeps all charges and printed values');
}
for(const invalidate of ['status','turn','hand','target']){
 const g=fresh(),m=run(g,'enemy','H',['4','5','6']),c=plain(g,'H','2');grant(g,c);g.state.player.hand.push(c);let completed=0;
 g.requestPlayerRankChoice([c],m,{onChoose:plan=>{completed++;g.attachCards('player',[c],'enemy',0,plan)}});const q=g.state.pendingEffectChoice;
 if(invalidate==='status')g.clearOfficialStatus('card',c,'flexible');if(invalidate==='turn')nextTurn(g);if(invalidate==='hand')g.state.player.hand.splice(g.state.player.hand.indexOf(c),1);if(invalidate==='target')m.cards.push(plain(g,'H','3','enemy'));
 q.onChoose(q.options[0]);assert.equal(completed,0,`${invalidate}: stale UI plan rejected`);assert.ok(!c.flexibleRole);
}
{
 const g=fresh(),c=plain(g,'S','5'),cards=[c,plain(g,'H','5'),plain(g,'D','5')];g.state.player.hand=[...cards,plain(g,'C','K')];const old=g.rankChoiceActionPlan(cards).plan;grant(g,c);
 assert.equal(g.submitNewMeld('player',cards,old),false,'a newly granted charge requires a refreshed explicit choice, even for unchanged values');assert.equal(c.officialStatus.flexible,1);
 const preview=g.rankChoicePreview(cards);assert.ok(preview.plans[0].usesFlexible[0]);assert.equal(g.submitNewMeld('player',cards,preview.plans[0]),true,'serialized choices include suit, mode and printed face');
}
{
 const g=fresh();nextTurn(g,'enemy');const c=plain(g,'S','2','enemy'),cards=[c,plain(g,'H','3','enemy'),plain(g,'D','3','enemy')];grant(g,c);g.state.enemy.hand=[...cards,plain(g,'C','K','enemy')];const before=JSON.stringify(cards),choice=g.bestNewMeld(g.state.enemy.hand,'enemy');
 assert.ok(choice);assert.equal(choice.rankPlan.find(x=>x.uid===c.uid).rank,'3');assert.equal(JSON.stringify(cards),before);assert.equal(g.submitNewMeld('enemy',choice.cards,choice.rankPlan),true);assert.equal(c.officialStatus.flexible,0);assert.equal(g.state.pendingEffectChoice,null);
}
{
 const g=fresh(),c=plain(g,'H','2');g.state.enemy.hand=[plain(g,'H','4','enemy'),plain(g,'H','5','enemy'),plain(g,'S','K','enemy')];g.state.discard=[c];
 assert.equal(g.discardHelpsAI(c),false);grant(g,c);assert.equal(g.discardHelpsAI(c),true,'CPU acquisition sees the same flexible values as placement');assert.equal(c.officialStatus.flexible,1);
 const m=run(g,'player','H',['4','5','6']),withCharge=g.aiCardChoiceScore(c);g.clearOfficialStatus('card',c,'flexible');assert.ok(withCharge>=g.aiCardChoiceScore(c)+8,'deck-order scoring counts flexible-only attachment');assert.ok(g.runValid(m.cards));
}
console.log('PASS flexible planning: exhaustive parity, beyond-64 search, frozen roles, bounded UI, cancellation, stale validation, serialization and CPU');

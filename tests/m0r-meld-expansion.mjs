import assert from 'node:assert/strict';
import {makeGame,html} from './helpers/live-game.mjs';
function fresh(w='enemy'){
 const g=makeGame();g.state.turn=w;g.state.phase=w==='player'?'action':'wait';
 for(const side of ['player','enemy']){g.state[side].hand=[];g.state[side].melds=[];g.state[side].newMeldCount=0}
 return g;
}
const cards=(g,w,slots)=>slots.map(slot=>g.makeCard(slot[0],slot.slice(1),false,w));
const run=(g,w,suit='S',n=3)=>({type:'RUN',cards:cards(g,w,Array.from({length:n},(_,i)=>suit+(i+1===1?'A':i+1))),chain:n-3,createdToken:0,createdTurn:0,lastAttachToken:null,status:g.blankMeldStatus(),themeMeta:{}});
for(const w of ['player','enemy'])for(const [a,b] of [
 [['S3','H3','D3'],['S7','H7','D7']],
 [['S3','H3','D3'],['C4','C5','C6']],
 [['S3','S4','S5'],['H7','H8','H9']]
]){
 const g=fresh(w),s=g.state[w],first=cards(g,w,a),second=cards(g,w,b),third=cards(g,w,['CJ','CQ','CK']);s.hand=[...first,...second,...third];
 assert.equal(g.submitNewMeld(w,first),true);
 assert.equal(s.newMeldCount,1);
 assert.equal(g.submitNewMeld(w,second),true);
 assert.equal(s.newMeldCount,2);
 assert.equal(s.hand.length,3);assert.equal(s.melds.length,2);assert.equal(g.state.rummy,0);
 const before=JSON.stringify(s);assert.equal(g.submitNewMeld(w,third),false);assert.equal(JSON.stringify(s),before,'third base action is atomic');
 g.turnStart(w);assert.equal(s.newMeldCount,0);
 s.hand.push(...cards(g,w,['D8','D9','D10']));assert.equal(g.submitNewMeld(w,third),true);assert.equal(s.melds.length,3);
 const spare=[...s.hand],full=JSON.stringify(s);assert.equal(g.submitNewMeld(w,spare),'full');assert.equal(JSON.stringify(s),full,'fourth public slot rejected without consuming a use');
}
console.log('PASS two SETs, mixed SET/RUN, two RUNs; both sides; third base use and fourth slot rejected');
{
 const g=fresh(),s=g.state.enemy,a=cards(g,'enemy',['SA','S2','S3']),next=cards(g,'enemy',['S4','S5','S6']);s.hand=[...a,...next,...cards(g,'enemy',['DK'])];
 assert.equal(g.submitNewMeld('enemy',a),true);
 assert.equal(g.attachCards('enemy',[next[0]],'enemy',0),false);
 assert.equal(g.attachCards('enemy',next,'enemy',0),false);
 assert.equal(g.bestExtension('enemy'),null);
 assert.equal(g.anyAttachOption('enemy'),false);
 assert.equal(g.state.switchPower,0);
 g.turnStart('enemy');assert.equal(g.attachCards('enemy',next,'enemy',0),true);
 assert.equal(g.state.switchPower,45);assert.equal(g.state.switchTarget,'player');assert.equal(s.attachCount,1);
 assert.equal(s.returnedSwitchThisTurn,true);
 const otherRun=run(g,'enemy','H');s.melds.push(otherRun);const h4=cards(g,'enemy',['H4']);s.hand.push(...h4);
 assert.equal(g.attachCards('enemy',h4,'enemy',1),false,'base second attach blocked after the one attach action');
}
console.log('PASS same-turn own extension denied; next-turn multi-attach sums CHAIN and base second attach is rejected');
for(const exhausted of [false,true]){
 const g=fresh(),s=g.state.enemy;s.melds=[run(g,'enemy','S',7),run(g,'enemy','H'),run(g,'enemy','C')];
 const hand=cards(g,'enemy',['D8','D9','D10','DK']);s.hand=hand;s.newMeldCount=exhausted?2:0;g.state.switchPower=85;g.state.switchTarget='player';
 assert.equal(g.finishRun('enemy',0),true);assert.equal(s.melds.length,2);assert.equal(g.state.switchPower,85);assert.equal(s.newMeldCount,exhausted?2:0);
 assert.equal(g.submitNewMeld('enemy',hand.slice(0,3)),!exhausted,'retirement frees a slot but never refunds a turn use');
}
{
 const g=fresh(),s=g.state.enemy;s.melds=[{...run(g,'enemy'),type:'SET',cards:cards(g,'enemy',['S7','H7','D7'])},run(g,'enemy','H'),run(g,'enemy','C')];
 const fourth=cards(g,'enemy',['C7'])[0],newCards=cards(g,'enemy',['D8','D9','D10']);s.hand=[fourth,...newCards,...cards(g,'enemy',['DK'])];
 assert.equal(g.attachCards('enemy',[fourth],'enemy',0),true);assert.equal(s.melds.length,2);assert.equal(g.state.switchPower,24);
 assert.equal(g.submitNewMeld('enemy',newCards),true);assert.equal(s.melds.length,3);
}
console.log('PASS RUN completion and BURST retire/open/reuse slots without resetting action counts or power');
{
 const g=fresh(),s=g.state.enemy,m=run(g,'enemy','S',7);s.melds=[m];s.hand=cards(g,'enemy',['H7','D7','CK']);const c=m.cards.at(-1);
 assert.equal(g.canRecoverCard('enemy','enemy',0,6),true);
 g.executeRecoverAI('enemy',{side:'enemy',mi:0,ci:6,card:c});assert.equal(c.recoveredToken,g.state.turnToken);
 assert.equal(g.attachCards('enemy',[c],'enemy',0),false);
 assert.equal(g.submitNewMeld('enemy',[c,...s.hand.filter(x=>x.rank==='7'&&x!==c)]),true);
}
{
 const g=fresh(),s=g.state.enemy,all=cards(g,'enemy',['S3','H3','D3','C4','C5','C6']);s.hand=all;
 assert.equal(g.submitNewMeld('enemy',all.slice(0,3)),true);assert.equal(g.submitNewMeld('enemy',all.slice(3)),'rummy');
 assert.equal(s.hand.length,6);assert.equal(s.newMeldCount,2);assert.equal(g.state.switchPower,0);
}
console.log('PASS recovered card may prepare but cannot return; two-meld RUMMY refills six and keeps count');
{
 const g=fresh(),s=g.state.enemy,first=cards(g,'enemy',['SK','HK','DK']),second=cards(g,'enemy',['C4','C5','C6']);first[0]=g.makeCard('S','K',true,'enemy');s.hand=[...first,...second,...cards(g,'enemy',['H9'])];
 const events=[];g.subscribeEffectEvent(e=>{if(e.event==='onMeldCreate')events.push(e)});
 g.submitNewMeld('enemy',first);const shield=s.shield;assert.equal(shield,20);
 g.submitNewMeld('enemy',second);assert.equal(s.shield,shield,'first-meld named card does not react to the second action');assert.equal(events.length,2);assert.equal(events[1].extraNewMeld,false);
}
{
 const g=fresh(),s=g.state.enemy;g.state.field={tag:'casino'};const first=cards(g,'enemy',['S3','H3','D3']),second=cards(g,'enemy',['C4','C5','C6']);
 s.hand=[...cards(g,'enemy',['DK']),...first,...second,...cards(g,'enemy',['H9'])];
 g.submitNewMeld('enemy',first);assert.equal(s.flags.casinoCycle,true);const deck=s.deck.map(c=>c.uid).join(',');
 g.submitNewMeld('enemy',second);assert.equal(s.deck.map(c=>c.uid).join(','),deck,'casino does not cycle twice');
}
console.log('PASS named first-meld and field once-per-turn reactions do not double-trigger');
{
 const g=fresh(),s=g.state.enemy;s.hand=cards(g,'enemy',['S3','H3','D3','S4','S5','C4','C5','C6','DK']);
 const first=g.bestNewMeldForTurn('enemy');assert.ok(first);g.submitNewMeld('enemy',first.cards,first.rankPlan);
 const second=g.bestNewMeldForTurn('enemy');assert.ok(second,'AI preserves a disjoint second action');g.submitNewMeld('enemy',second.cards,second.rankPlan);
 assert.equal(s.newMeldCount,2);assert.equal(g.bestNewMeldForTurn('enemy'),null);
}
assert.ok(!html.includes('newMeldUsed'));assert.ok(!html.includes('기본 턴당 1회'));
console.log('PASS turn-aware AI and live wording; M0R executable expansion regression complete');
// Audit every live named definition: a following ordinary new meld must not
// replay a previously placed card's use effect or silently return the SWITCH.
let audited=0;
for(const [id,def] of Object.entries(makeGame().NAMED)){
 if(def.themeId==='twelve-bloom')continue; // staged NON-LIVE pool has dedicated effect regressions
 const g=fresh(),w='enemy',s=g.state[w],slot=def.slot||id;
 const c=slot[0]==='J'?g.makeCard('J',id,true,w,id):g.makeCard(slot[0],slot.slice(1),true,w,id);
 const companions=c.suit==='J'?cards(g,w,['S8','S9']):cards(g,w,['S','H','D','C'].filter(suit=>suit!==c.suit).slice(0,2).map(suit=>suit+c.rank));
 const first=[c,...companions],second=cards(g,w,['C2','C3','C4']);s.hand=[...first,...second,...cards(g,w,['DK'])];
 assert.equal(g.submitNewMeld(w,first),true,id+' first create');
 const values=()=>JSON.stringify({hp:s.hp,shield:s.shield,deck:s.deck.map(c=>c.uid),spent:s.spent.map(c=>c.uid),switch:g.state.switchPower,target:g.state.switchTarget});
 const after=values();assert.equal(g.submitNewMeld(w,second),true,id+' second create');assert.equal(values(),after,id+' does not trigger again from the next ordinary new meld');audited++;
}
console.log(`PASS all ${audited} live named definitions audited against a second ordinary new-meld event`);
{
 const g=fresh(),s=g.state.enemy;s.hand=cards(g,'enemy',['S3','H3','D3','C4','C5','C6','DK','SQ','H10']);
 const events=[];g.subscribeEffectEvent(e=>{if(e.event==='onMeldCreate'&&e.actor==='enemy')events.push(e)});
 g.continueAITurnAfterAcquisition({skipMaintenance:true});assert.equal(events.length,2,'actual CPU loop executes both creates');assert.equal(events[0].newMeldIndex,1);assert.equal(events[1].newMeldIndex,2);assert.equal(s.newMeldCount,2);
}
console.log('PASS actual CPU loop performs two creates with first/second event indices');
{
 const g=makeGame();assert.equal(g.state.player.hand.length,8);g.drawOne('player',false);assert.equal(g.state.player.hand.length,9,'real starting hand and acquisition');
}

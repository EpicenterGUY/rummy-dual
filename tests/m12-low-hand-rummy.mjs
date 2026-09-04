import fs from 'node:fs';
import {makeGame,html} from './helpers/live-game.mjs';

const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let p=0,b=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')p++;else if(script[i]===')')p--;else if(script[i]==='{'&&p===0){b=i;break}}let d=0;for(let i=b;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}

new Function(script);
ok(source('canSkipBaseDiscard').includes('s.hand.length<=3'),'existing low-hand discard-skip rule remains intact');
ok(source('aiShouldSkipLowHandDiscard').includes('if(aiCanDiscardToRummy(w))return false'),'AI treats low-hand skip as optional when last-card discard reaches RUMMY');
ok(source('continueAITurnAfterAcquisition').includes("urgent&&!bestExtension('enemy')"),'urgent SWITCH-return maintenance search still precedes low-hand RUMMY preference');
ok(source('continueAITurnAfterAcquisition').includes('!lowRummy&&!hasAnyLegalAction'),'nonurgent meaningless maintenance is suppressed only when a low-hand RUMMY line exists');
ok(source('bestExtensionFromHand').includes('aiLowHandRummyActionBonus(w,hand,cs)'),'attach scoring receives additive low-hand RUMMY value');
ok(source('bestNewMeld').includes('aiLowHandRummyActionBonus(w,hand,cs)'),'new-meld scoring receives additive low-hand RUMMY value');
ok(!source('aiLowHandRummyActionBonus').includes('newMeldCount=')&&!source('aiLowHandRummyActionBonus').includes('attachCount='),'RUMMY scoring creates no new action rights');
ok(source('updateButtons').includes('버리기 → 러미')&&source('playerLowHandRummyHint').includes('버리기 생략 선택이지 금지가 아님'),'HUD explains last-card RUMMY and optional low-hand protection');

function fresh(seed=1){const g=makeGame(html,seed,{developer:false});g.state.field=null;g.state.turn='enemy';g.state.phase='action';g.state.turnNo=2;g.state.turnToken=10;g.progress.totalClears=100;return g}
function clearSide(g,w){const s=g.state[w];s.hand=[];s.deck=[];s.spent=[];s.melds=[];s.newMeldCount=0;s.attachCount=0;s.extraAttachRemaining=0;s.returnedSwitchThisTurn=false;s.discardsRemaining=1;s.maintenanceUsed=false;return s}
function card(g,suit,rank,w='enemy'){return g.makeCard(suit,rank,false,w)}

{
 const g=fresh(11),s=clearSide(g,'enemy');const c=card(g,'C','5');s.hand=[c];s.deck=[card(g,'D','9')];
 ok(g.canSkipBaseDiscard('enemy'),'one-card hand may still skip the basic discard');
 ok(g.canBasicDiscardCard('enemy',c),'the same one-card hand may legally discard');
 ok(g.aiCanDiscardToRummy('enemy'),'AI recognizes legal last-card discard as a RUMMY line');
 ok(!g.aiShouldSkipLowHandDiscard('enemy'),'AI no longer auto-skips the discard that reaches RUMMY');
}

{
 const g=fresh(12),s=clearSide(g,'enemy');s.hand=[card(g,'S','7'),card(g,'H','7'),card(g,'D','7')];
 const nm=g.bestNewMeldForTurn('enemy');
 ok(nm&&nm.cards.length===3&&g.aiLowHandRummyActionBonus('enemy',s.hand,nm.cards)===8,'three-card SET/RUN that empties hand gets immediate-RUMMY score');
 const result=g.submitNewMeld('enemy',nm.cards,nm.rankPlan||null);
 ok(result==='rummy'||result==='choice','using all three cards enters the real RUMMY path');
}

{
 const g=fresh(13),s=clearSide(g,'enemy'),p=clearSide(g,'player');
 p.melds=[{type:'RUN',cards:[card(g,'H','5','player'),card(g,'H','6','player'),card(g,'H','7','player')],chain:0,createdToken:null,status:{},themeMeta:{}}];
 s.hand=[card(g,'H','8'),card(g,'H','9')];g.state.switchTarget='neutral';
 const ex=g.bestExtension('enemy');
 ok(ex&&ex.cards.length===2&&g.aiLowHandRummyActionBonus('enemy',s.hand,ex.cards)===8,'two-card multi-attach that empties hand is scored as immediate RUMMY');
 const result=g.attachCards('enemy',ex.cards,ex.side,ex.index,ex.rankPlan||null);
 ok(result==='rummy'||result==='choice','two-card multi-attach uses the existing attach permission and real RUMMY trigger');
}

{
 const g=fresh(14),s=clearSide(g,'enemy'),p=clearSide(g,'player');
 p.melds=[{type:'RUN',cards:[card(g,'S','4','player'),card(g,'S','5','player'),card(g,'S','6','player')],chain:0,createdToken:null,status:{},themeMeta:{}}];
 s.hand=[card(g,'S','7'),card(g,'C','2'),card(g,'D','9')];g.state.switchTarget='enemy';g.state.switchPower=25;
 const ex=g.bestExtension('enemy');
 ok(ex&&ex.cards.some(c=>c.rank==='7'),'urgent returning extension remains discoverable with low hand');
 const src=source('continueAITurnAfterAcquisition');
 ok(src.indexOf('switchUrgent||!nm||ex.score>=nm.score')<src.indexOf("if(rc&&(!nm||rc.score>nm.score))"),'urgent extension branch remains before recovery/new-meld fallback');
}

console.log('M12 low-hand RUMMY AI/UX regression passed.');

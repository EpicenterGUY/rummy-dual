import fs from 'node:fs';
import {createHash} from 'node:crypto';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {makeGame,html} from '../tests/helpers/live-game.mjs';
// Same seeded deck construction and bounded policy for both rules. All legal actions,
// effects, circulation, RUMMY and damage are executed by the real engine.
const baseRef='ab8578b';

// Design probe only: A..Q months, distinct rank values across all currently-owned
// public cards; K and Jokers have no assumed replacement power.
export function hwaTuSeasonMatches(state,w){const rank=c=>c.rank==='A'?1:c.rank==='J'?11:c.rank==='Q'?12:/^\d+$/.test(c.rank)?Number(c.rank):0;const months=new Set(['player','enemy'].flatMap(side=>state[side].melds.flatMap(m=>m.cards)).filter(c=>c.owner===w&&c.suit!=='J').map(rank));return [1,4,7,10].filter(start=>[start,start+1,start+2].every(n=>months.has(n))).length}
function choices(g){for(let i=0;g.state.pendingEffectChoice;i++){if(i>=40)throw Error('choice loop');const q=g.state.pendingEffectChoice;g.resolveEffectChoice(q.allowSkip?'__skip__':q.options[0].key)}}
function play(g,w,cap,stats){
 const st=g.state,s=st[w];st.turn=w;st.phase=w==='player'?'action':'wait';st.turnNo++;g.turnStart(w);const ownTurn=s.turnStarts;
 g.drawOne(w,false);let rummied=false;const unsub=g.subscribeEffectEvent(e=>{if(e.event==='onRummy'){rummied=true;stats.rummys++;if(ownTurn===1){stats.firstRummys++;stats[w==='player'?'firstPlayerRummys':'firstEnemyRummys']++}}if(e.event==='onMeldCreate'){stats.creates++;if(ownTurn===1)stats.firstCreates++}});
 const beforeCreates=stats.creates;
 for(let i=0;i<6&&!st.gameOver&&!rummied;i++){
  const ex=g.bestExtension(w),nm=s.melds.length<cap?g.bestNewMeldForTurn(w):null,rc=g.bestRecoverAI(w),fr=g.bestFinishRunAI(w),urgent=st.switchTarget===w&&st.switchPower>0;
  let result;
  if(ex&&(urgent||!nm||ex.score>=nm.score)&&(urgent||!rc||ex.score>=rc.score))result=g.attachCards(w,ex.cards,ex.side,ex.index,ex.rankPlan);
  else if(rc&&(!nm||rc.score>nm.score))result=g.executeRecoverAI(w,rc);
  else if(fr)result=g.finishRun(w,fr.index);
  else if(nm)result=g.submitNewMeld(w,nm.cards,nm.rankPlan);
  else if(!s.maintenanceUsed&&g.maintenanceLimit(w)){const limit=g.maintenanceLimit(w);result=g.performMaintenance(w,s.hand.slice(0,limit));stats.maintenance++}
  else break;
  choices(g);if(result===false||result==='full')throw Error('AI chose illegal action');
 }
 if(ownTurn===1){stats.firstTurns++;if(stats.creates-beforeCreates>=2)stats.doubleOpen++;stats.firstHand+=s.hand.length;stats.firstPublicCards+=s.melds.reduce((n,m)=>n+m.cards.length,0);if(hwaTuSeasonMatches(st,w))stats.firstSeasonHands++}
 if(!rummied&&!st.gameOver){while(s.hand.length&&s.discardsRemaining>0&&!g.canSkipBaseDiscard(w)){const card=s.hand.at(-1);g.removeFromHand(w,[card]);g.pushDiscard(card);s.discardsRemaining--;g.armSafetyPin(w,card);choices(g)}if(!s.hand.length&&!st.gameOver){g.triggerRummy(w,[],{returned:false});choices(g)}if(!rummied||w==='enemy'){g.settleContracts(w);g.turnEnd(w)}}
 else if(rummied&&w==='enemy'&&!st.gameOver)g.turnEnd(w);
 unsub();if(cap===3&&s.newMeldCount>2)throw Error('new-meld allowance exceeded');if(s.melds.length>cap)throw Error('public cap exceeded');if(hwaTuSeasonMatches(st,w))stats.seasonTurnHands++;s.hand.forEach(c=>c.age++);stats.turns++;if(s.hand.length<=3)stats.lowHand++;stats.maxSlots=Math.max(stats.maxSlots,s.melds.length);
}
function runCohort(source,cohort,seeds,cap){
 const stats={games:seeds,turns:0,firstTurns:0,creates:0,firstCreates:0,doubleOpen:0,firstHand:0,firstPublicCards:0,firstSeasonHands:0,seasonTurnHands:0,rummys:0,firstRummys:0,firstPlayerRummys:0,firstEnemyRummys:0,maintenance:0,lowHand:0,maxSlots:0,earlyEnds:0};
 for(let seed=1;seed<=seeds;seed++){
  const g=makeGame(source,seed*97,{developer:true}),st=g.state;g.progress.totalClears=100;
  for(const w of ['player','enemy']){const s=st[w];s.hand=[];s.spent=[];s.melds=[];s.deck=cohort==='pure'?g.makeM11BExperimentDeck(w,'zero',seed):g.makeDeck(w,'wanderer',cohort);g.drawMany(w,8,false)}
  // First six own turns, no mulligan; optional effect choices consistently skip.
  for(let turn=0;turn<12&&!st.gameOver;turn++)play(g,turn%2?'enemy':'player',cap,stats);
  if(st.gameOver)stats.earlyEnds++;
 }
 const rate=(n,d)=>+(100*n/d).toFixed(2),avg=(n,d)=>+(n/d).toFixed(3);
 return {...stats,doubleOpenPct:rate(stats.doubleOpen,stats.firstTurns),avgFirstCreates:avg(stats.firstCreates,stats.firstTurns),avgFirstHand:avg(stats.firstHand,stats.firstTurns),avgFirstPublicCards:avg(stats.firstPublicCards,stats.firstTurns),firstSeasonPct:rate(stats.firstSeasonHands,stats.firstTurns),seasonTurnPct:rate(stats.seasonTurnHands,stats.turns),firstRummyPct:rate(stats.firstRummys,stats.firstTurns),rummysPer100Turns:rate(stats.rummys,stats.turns),lowHandPct:rate(stats.lowHand,stats.turns)};
}
export function runExperiment(seeds=64){const oldHtml=execFileSync('git',['show',`${baseRef}:index.html`],{cwd:new URL('..',import.meta.url),encoding:'utf8',maxBuffer:8e6});return{baseRef,seeds,sourceSha256:createHash('sha256').update(html).digest('hex'),policy:'paired seeds; all defined cards available through DEV; actual deck/effect/AI helpers; six own turns; no mulligan; optional choices skipped; up to six actions per turn in both cohorts',cohorts:['pure','mixed','v-signal','zero-sight','point-blank'].map(cohort=>({cohort,before:runCohort(oldHtml,cohort,seeds,2),after:runCohort(html,cohort,seeds,3)}))}}
if(process.argv[1]===fileURLToPath(import.meta.url)){const result=runExperiment(Number(process.env.M0R_SEEDS)||64);console.log(JSON.stringify(result,null,2));if(process.env.M0R_OUTPUT)fs.writeFileSync(path.resolve(process.env.M0R_OUTPUT),JSON.stringify(result,null,2)+'\n')}

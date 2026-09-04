import fs from 'node:fs';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {makeGame,html} from '../tests/helpers/live-game.mjs';

export const BASE_REF='002bc9bcfdce86b4690ff71782cadd8fe86e510d';
export const COHORTS=['set','run','mixed','v-signal','zero-sight','point-blank','mail-route','scrap-shift'];

function instrumentSource(source){
 return source
  .replace("s.deck=shuffle(pool);log(\`${w==='player'?'내':'상대'} 재순환","s.deck=shuffle(pool);if(typeof getCirculationStats==='function'){const __st=getCirculationStats();__st.recycles=(__st.recycles||0)+1}log(\`${w==='player'?'내':'상대'} 재순환")
  .replace("function emergencyReleaseMeld(w,reason='순환 정체'){const plan=circulationReleasePlan(w);if(!plan)return false;","function emergencyReleaseMeld(w,reason='순환 정체'){const plan=circulationReleasePlan(w);if(!plan)return false;if(typeof getCirculationStats==='function'){const __st=getCirculationStats();__st.emergencyReleases=(__st.emergencyReleases||0)+1}");
}
function seeded(seed){let v=seed>>>0;return()=>{v=(Math.imul(v,1103515245)+12345)>>>0;return v/4294967296}}
function setup(g,cohort,seed){
 const rr=seeded(seed*811+17);
 g.progress.totalClears=100;
 g.progress.selectedStructure='mixed';
 for(const w of ['player','enemy']){
  const s=g.state[w];s.hand=[];s.deck=[];s.spent=[];s.melds=[];
  if(['set','run','mixed'].includes(cohort)){
   const slots=g.deckStructureSlots(cohort,rr);
   s.deck=slots.map(slot=>{const x=g.parseRegularId(slot);return g.makeCard(x.suit,x.rank,false,w)});
   s.deck.push(g.makeCard('J','J1',true,w,'J1'));
   s.deck=g.shuffle(s.deck);
  }else s.deck=g.makeDeck(w,'wanderer',cohort);
  g.drawMany(w,8,false);
 }
 Object.assign(g.state,{turnNo:1,turnToken:1,switchTarget:'neutral',switchPower:0,gameOver:false});
}
function choices(g){
 for(let i=0;g.state.pendingEffectChoice;i++){
  if(i>80)throw Error('effect choice loop');
  const q=g.state.pendingEffectChoice;
  g.resolveEffectChoice(q.allowSkip?'__skip__':q.options[0].key);
 }
}
function maintenanceCards(g,w,limit){
 const s=g.state[w];
 return s.hand.filter(c=>!g.scrapShiftCardTurnLocked||!g.scrapShiftCardTurnLocked(c))
  .map(c=>({c,score:g.aiKeepScore(c,s.hand)})).sort((a,b)=>a.score-b.score)
  .slice(0,Math.min(limit,s.hand.length)).map(x=>x.c);
}
function discardChoice(g,w){
 const s=g.state[w];
 return s.hand.filter(c=>!g.scrapShiftCardTurnLocked||!g.scrapShiftCardTurnLocked(c))
  .map(c=>({c,score:g.aiKeepScore(c,s.hand)})).sort((a,b)=>a.score-b.score)[0]?.c||null;
}
function playSide(g,w,acc,turnIndex){
 const st=g.state,s=st[w];st.turn=w;st.phase=w==='player'?'action':'wait';g.turnStart(w);
 const acq=g.prepareAcquisitionPhase(w);
 if(acq!=='draw'){acc.acqSkips++;if(acq==='pass')acc.acqPasses++}
 if(acq==='draw'){
  const top=st.discard.at(-1),fromDiscard=!s.blockOpponentDiscardNext&&top&&g.discardHelpsAI(top);
  const c=g.drawOne(w,!!fromDiscard);
  if(s.blockOpponentDiscardNext)s.blockOpponentDiscardNext=false;
  if(fromDiscard&&c){g.onDiscardDraw(w,c);choices(g)}
 }
 let rummied=false;
 const unsub=g.subscribeEffectEvent(e=>{if(e.event==='onRummy'){rummied=true;acc.rummys++;acc.handZeroEvents++;if(acc.firstRummyTurn==null)acc.firstRummyTurn=turnIndex+1}});
 const urgent=st.switchTarget===w&&st.switchPower>0;
 const lowRummy=typeof g.aiLowHandRummyOpportunity==='function'&&g.aiLowHandRummyOpportunity(w);
 if(urgent&&!g.bestExtension(w)&&g.maintenanceLimit(w)>0){
  const cards=maintenanceCards(g,w,g.maintenanceLimit(w));if(cards.length)g.performMaintenance(w,cards);
 }else if(!lowRummy&&!g.hasAnyLegalAction(w)&&g.maintenanceLimit(w)>0){
  const cards=maintenanceCards(g,w,g.maintenanceLimit(w));if(cards.length)g.performMaintenance(w,cards);
 }
 for(let i=0;i<6&&!st.gameOver&&!rummied;i++){
  const ex=g.bestExtension(w),nm=s.melds.length<3?g.bestNewMeldForTurn(w):null,rc=g.bestRecoverAI(w),fr=g.bestFinishRunAI(w),cl=g.bestCleanupMeldAI(w);
  const switchUrgent=st.switchTarget===w&&st.switchPower>0,acceptSmall=g.aiShouldAcceptSmallBomb?g.aiShouldAcceptSmallBomb(w,ex):false;
  let result=null;
  if(ex&&(!acceptSmall&&(switchUrgent||!nm||ex.score>=nm.score))&&(switchUrgent||!rc||ex.score>=rc.score))result=g.attachCards(w,ex.cards,ex.side,ex.index,ex.rankPlan||null);
  else if(rc&&(!nm||rc.score>nm.score))result=g.executeRecoverAI(w,rc);
  else if(fr)result=g.finishRun(w,fr.index);
  else if(cl)result=g.cleanupMeld(w,cl.index);
  else if(nm&&s.melds.length<3)result=g.submitNewMeld(w,nm.cards,nm.rankPlan||null);
  else break;
  choices(g);
  if(result===false||result==='full')throw Error('policy chose illegal action');
 }
 let last=null;
 while(!st.gameOver&&!rummied&&s.hand.length&&s.discardsRemaining>0){
  const skip=typeof g.aiShouldSkipLowHandDiscard==='function'?g.aiShouldSkipLowHandDiscard(w):g.canSkipBaseDiscard(w);
  if(skip){const cs=g.getCirculationStats();cs.lowSkips=(cs.lowSkips||0)+1;s.discardsRemaining=0;break}
  const d=discardChoice(g,w);if(!d)break;last=d;g.removeFromHand(w,[d]);g.pushDiscard(d);g.armSafetyPin(w,d);s.discardsRemaining=Math.max(0,s.discardsRemaining-1);
 }
 if(!st.gameOver&&!rummied&&s.hand.length===0){g.triggerRummy(w,last?[last]:[],{returned:false});choices(g);rummied=true}
 if(!rummied||w==='enemy'){g.settleContracts(w);g.turnEnd(w)}
 unsub();s.hand.forEach(c=>c.age++);if(w==='enemy')st.turnNo++;
 acc.hands.push(s.hand.length);
 if(s.hand.length>=1&&s.hand.length<=3){acc.streak[w]++;acc.maxLow=Math.max(acc.maxLow,acc.streak[w])}else acc.streak[w]=0;
}
const mean=a=>a.reduce((x,y)=>x+y,0)/(a.length||1);
const median=a=>{const x=[...a].sort((a,b)=>a-b),n=x.length;return n?(n%2?x[(n-1)/2]:(x[n/2-1]+x[n/2])/2):0};
const rate=(n,d)=>100*n/(d||1);
function runCohort(source,cohort,seeds=1000,maxTurns=120){
 const total={battles:seeds,hands:[],rummys:0,handZeroEvents:0,firstRummyTurns:[],noRummy:0,acqSkips:0,acqPasses:0,recycles:0,full:0,emergency:0,maintenance:0,maintenanceCards:0,bursts:0,chains:0,detonates:0,maxPowers:[],battleTurns:[],maxLow:0,capped:0};
 for(let seed=1;seed<=seeds;seed++){
  const g=makeGame(instrumentSource(source),seed*97,{developer:false}),st=g.state;setup(g,cohort,seed);
  const acc={hands:[],rummys:0,handZeroEvents:0,firstRummyTurn:null,acqSkips:0,acqPasses:0,streak:{player:0,enemy:0},maxLow:0};
  let t=0;for(;t<maxTurns&&!st.gameOver;t++)playSide(g,t%2?'enemy':'player',acc,t);
  if(!st.gameOver&&t>=maxTurns)total.capped++;
  const bm=g.getBattleMetrics(),cs=g.getCirculationStats();
  total.hands.push(...acc.hands);total.rummys+=acc.rummys;total.handZeroEvents+=acc.handZeroEvents;
  if(acc.firstRummyTurn==null)total.noRummy++;else total.firstRummyTurns.push(acc.firstRummyTurn);
  total.acqSkips+=acc.acqSkips;total.acqPasses+=acc.acqPasses;total.recycles+=cs.recycles||0;total.full+=cs.fullRecirculations||0;total.emergency+=cs.emergencyReleases||0;
  total.maintenance+=bm.maintenance.length;total.maintenanceCards+=bm.maintenance.reduce((n,x)=>n+(x.cards||0),0);
  total.bursts+=bm.bursts.length;total.chains+=bm.chains.length;total.detonates+=bm.detonates.length;total.maxPowers.push(bm.maxPower||0);total.battleTurns.push(t);total.maxLow=Math.max(total.maxLow,acc.maxLow);
 }
 const turns=total.battleTurns.reduce((a,b)=>a+b,0),c=[0,1,2,3].map(k=>total.hands.filter(x=>x===k).length);
 return {battles:seeds,sideTurns:turns,avgHand:+mean(total.hands).toFixed(3),medianHand:median(total.hands),hand0Events:total.handZeroEvents,hand1Pct:+rate(c[1],total.hands.length).toFixed(2),hand2Pct:+rate(c[2],total.hands.length).toFixed(2),hand3Pct:+rate(c[3],total.hands.length).toFixed(2),low13Pct:+rate(c[1]+c[2]+c[3],total.hands.length).toFixed(2),maxLowStreak:total.maxLow,rummyPer100:+rate(total.rummys,turns).toFixed(2),avgRummyPerBattle:+(total.rummys/seeds).toFixed(3),avgFirstRummyTurn:total.firstRummyTurns.length?+mean(total.firstRummyTurns).toFixed(2):null,noRummyPct:+rate(total.noRummy,seeds).toFixed(2),maintenancePer100:+rate(total.maintenance,turns).toFixed(2),avgMaintenanceCards:total.maintenance?+(total.maintenanceCards/total.maintenance).toFixed(3):0,recycles:total.recycles,fullRecirculations:total.full,emergencyReleases:total.emergency,acquisitionSkips:total.acqSkips,acquisitionPasses:total.acqPasses,avgBattleTurns:+mean(total.battleTurns).toFixed(2),medianBattleTurns:median(total.battleTurns),burstPer100:+rate(total.bursts,turns).toFixed(2),chainPer100:+rate(total.chains,turns).toFixed(2),detonatePer100:+rate(total.detonates,turns).toFixed(2),avgMaxSwitch:+mean(total.maxPowers).toFixed(2),cappedBattles:total.capped};
}
export function runExperiment(seeds=1000,maxTurns=120){
 const baseline=execFileSync('git',['show',`${BASE_REF}:index.html`],{cwd:new URL('..',import.meta.url),encoding:'utf8',maxBuffer:12e6});
 return {baseRef:BASE_REF,seeds,maxTurns,policy:'paired seeds; complete shipped engine via tests/helpers/live-game; no mulligan; real acquisition/discard/maintenance/meld/attach/recover/RUMMY/recycle/SWITCH/DETONATE paths; optional effect choices skipped consistently',cohorts:COHORTS.map(cohort=>({cohort,baseline:runCohort(baseline,cohort,seeds,maxTurns),candidateA:runCohort(html,cohort,seeds,maxTurns)}))};
}
if(process.argv[1]===fileURLToPath(import.meta.url)){
 const result=runExperiment(Number(process.env.M12_SEEDS)||1000,Number(process.env.M12_MAX_TURNS)||120);
 console.log(JSON.stringify(result,null,2));
 if(process.env.M12_OUTPUT)fs.writeFileSync(path.resolve(process.env.M12_OUTPUT),JSON.stringify(result,null,2)+'\n');
}

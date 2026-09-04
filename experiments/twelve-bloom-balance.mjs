import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {makeGameFactory,html} from '../tests/helpers/live-game.mjs';

export const COHORTS=['baseline-mixed','baseline-set','baseline-run','tb-set','tb-run','tb-mixed','tb-v-signal','tb-zero-sight','tb-point-blank','tb-mail-route','tb-scrap-shift'];
const PARTNER={'tb-v-signal':'v-signal','tb-zero-sight':'zero-sight','tb-point-blank':'point-blank','tb-mail-route':'mail-route','tb-scrap-shift':'scrap-shift'};

function instrumentSource(source){
 return source
  .replace("function claimThemeTurnGate(c,key,turnToken=state.turnToken){const bag=ensureThemeTurnGates(c);if(!bag||bag[key]===turnToken)return false;bag[key]=turnToken;return true}",
   "function claimThemeTurnGate(c,key,turnToken=state.turnToken){const bag=ensureThemeTurnGates(c);if(!bag||bag[key]===turnToken)return false;bag[key]=turnToken;if(state.tbBalanceStats&&(key==='tbSunset'||key==='tbLightTrio'))state.tbBalanceStats[key]=(state.tbBalanceStats[key]||0)+1;return true}")
  .replace("s.deck=shuffle(pool);log(", "s.deck=shuffle(pool);if(state.tbBalanceStats)state.tbBalanceStats.recycles=(state.tbBalanceStats.recycles||0)+1;log(")
  .replace("function emergencyReleaseMeld(w,reason='순환 정체'){const plan=circulationReleasePlan(w);if(!plan)return false;",
   "function emergencyReleaseMeld(w,reason='순환 정체'){const plan=circulationReleasePlan(w);if(!plan)return false;if(state.tbBalanceStats)state.tbBalanceStats.emergency=(state.tbBalanceStats.emergency||0)+1;")
  .replace("sw.returnedSwitchThisTurn=true;sw.rummyReturnPending=false;", "sw.returnedSwitchThisTurn=true;if(state.tbBalanceStats)state.tbBalanceStats.returns=(state.tbBalanceStats.returns||0)+1;sw.rummyReturnPending=false;");
}
function seeded(seed){let v=seed>>>0||1;return()=>{v=(Math.imul(v,1664525)+1013904223)>>>0;return v/4294967296}}
function sampleUnique(g,pool,n,rr,used=new Set()){
 const src=pool.filter(id=>!used.has(g.namedSlot(id))),out=[];
 while(src.length&&out.length<n){const i=Math.floor(rr()*src.length),id=src.splice(i,1)[0],slot=g.namedSlot(id);if(used.has(slot))continue;used.add(slot);out.push(id)}
 return out;
}
function cohortNamed(g,cohort,seed){
 const rr=seeded(seed*613+29),ids=Object.keys(g.NAMED).filter(id=>id[0]!=='J'),used=new Set(),out=[];
 const ordinary=ids.filter(id=>!g.NAMED[id]?.themeId);
 if(cohort.startsWith('baseline-'))return sampleUnique(g,ordinary,9,rr,used);
 const tb=ids.filter(id=>g.NAMED[id]?.themeId==='twelve-bloom');
 out.push(...sampleUnique(g,tb,4,rr,used));
 const partner=PARTNER[cohort];
 if(partner)out.push(...sampleUnique(g,ids.filter(id=>g.NAMED[id]?.themeId===partner),4,rr,used));
 out.push(...sampleUnique(g,ordinary,9-out.length,rr,used));
 return out;
}
function makeCohortDeck(g,w,cohort,seed){
 const rr=seeded(seed*997+(w==='player'?17:53));
 const structure=(cohort==='tb-set'||cohort==='baseline-set')?'set':(cohort==='tb-run'||cohort==='baseline-run')?'run':'mixed';
 const chosen=cohortNamed(g,cohort,seed+(w==='player'?0:100000));
 const variants=new Map(chosen.map(id=>[g.namedSlot(id),id]));
 const slots=new Set(chosen.map(id=>g.namedSlot(id)));
 for(const slot of g.deckStructureSlots(structure,rr)){if(slots.size>=29)break;slots.add(slot)}
 for(const slot of g.CORE_IDS){if(slots.size>=29)break;slots.add(slot)}
 for(const suit of['S','H','D','C'])for(const rank of['A','2','3','4','5','6','7','8','9','10','J','Q','K']){if(slots.size>=29)break;slots.add(suit+rank)}
 const cards=[...slots].slice(0,29).map(slot=>{const def=variants.get(slot),p=g.parseRegularId(slot);return g.makeCard(p.suit,p.rank,!!def,w,def||null)});
 cards.push(g.makeCard('J','J1',true,w,'J1'));
 return g.shuffle(cards);
}
function setup(g,cohort,seed){
 g.state.tbBalanceStats={tbSunset:0,tbLightTrio:0,recycles:0,emergency:0,returns:0};
 g.progress.totalClears=100;g.progress.selectedStructure=(cohort==='tb-set'||cohort==='baseline-set')?'set':(cohort==='tb-run'||cohort==='baseline-run')?'run':'mixed';
 for(const w of['player','enemy']){const s=g.state[w];s.hand=[];s.deck=makeCohortDeck(g,w,cohort,seed);s.spent=[];s.melds=[];g.drawMany(w,8,false)}
 Object.assign(g.state,{turnNo:1,turnToken:1,switchTarget:'neutral',switchPower:0,gameOver:false,field:null});
}
function choices(g){
 for(let i=0;g.state.pendingEffectChoice;i++){
  if(i>100)throw Error('effect choice loop');
  const q=g.state.pendingEffectChoice,key=q.options?.[0]?.key??(q.allowSkip?'__skip__':null);
  if(key==null)throw Error('choice has no resolvable option');
  g.resolveEffectChoice(key);
 }
}
function maintenanceCards(g,w,limit){const s=g.state[w];return s.hand.filter(c=>!g.scrapShiftCardTurnLocked||!g.scrapShiftCardTurnLocked(c)).map(c=>({c,score:g.aiKeepScore(c,s.hand)})).sort((a,b)=>a.score-b.score).slice(0,Math.min(limit,s.hand.length)).map(x=>x.c)}
function discardChoice(g,w){const s=g.state[w];return s.hand.filter(c=>!g.scrapShiftCardTurnLocked||!g.scrapShiftCardTurnLocked(c)).map(c=>({c,score:g.aiKeepScore(c,s.hand)})).sort((a,b)=>a.score-b.score)[0]?.c||null}
function playSide(g,w,acc,turnIndex){
 const st=g.state,s=st[w];st.turn=w;st.phase=w==='player'?'action':'wait';g.turnStart(w);
 const acq=g.prepareAcquisitionPhase(w);if(acq!=='draw'){acc.acqSkips++;if(acq==='pass')acc.acqPasses++}
 if(acq==='draw'){const top=st.discard.at(-1),fromDiscard=!s.blockOpponentDiscardNext&&top&&g.discardHelpsAI(top),c=g.drawOne(w,!!fromDiscard);if(s.blockOpponentDiscardNext)s.blockOpponentDiscardNext=false;if(fromDiscard&&c){g.onDiscardDraw(w,c);choices(g)}}
 let rummied=false;
 const unsub=g.subscribeEffectEvent(e=>{
  if(e.event==='onRummy'){rummied=true;acc.rummys++;if(acc.firstRummyTurn==null)acc.firstRummyTurn=turnIndex+1}
  if(e.event==='onBloomMatchChange'){const keys=e.newlyCompleted||[];if(keys.length){acc.bloomActions++;acc.seasons+=keys.filter(k=>k.startsWith('season:')).length;acc.pictures+=keys.filter(k=>k.startsWith('picture:')).length;if(keys.length>=2)acc.multiBloom++}acc.broken+=e.broken?.length||0}
 });
 const urgent=st.switchTarget===w&&st.switchPower>0,lowRummy=typeof g.aiLowHandRummyOpportunity==='function'&&g.aiLowHandRummyOpportunity(w);
 if(urgent&&!g.bestExtension(w)&&g.maintenanceLimit(w)>0){const cs=maintenanceCards(g,w,g.maintenanceLimit(w));if(cs.length)g.performMaintenance(w,cs)}
 else if(!lowRummy&&!g.hasAnyLegalAction(w)&&g.maintenanceLimit(w)>0){const cs=maintenanceCards(g,w,g.maintenanceLimit(w));if(cs.length)g.performMaintenance(w,cs)}
 choices(g);
 for(let i=0;i<8&&!st.gameOver&&!rummied;i++){
  const ex=g.bestExtension(w),nm=s.melds.length<3?g.bestNewMeldForTurn(w):null,rc=g.bestRecoverAI(w),fr=g.bestFinishRunAI(w),cl=g.bestCleanupMeldAI(w);
  const switchUrgent=st.switchTarget===w&&st.switchPower>0,acceptSmall=g.aiShouldAcceptSmallBomb?g.aiShouldAcceptSmallBomb(w,ex):false;let result=null;
  if(ex&&(!acceptSmall&&(switchUrgent||!nm||ex.score>=nm.score))&&(switchUrgent||!rc||ex.score>=rc.score))result=g.attachCards(w,ex.cards,ex.side,ex.index,ex.rankPlan||null);
  else if(rc&&(!nm||rc.score>nm.score))result=g.executeRecoverAI(w,rc);
  else if(fr)result=g.finishRun(w,fr.index);
  else if(cl)result=g.cleanupMeld(w,cl.index);
  else if(nm&&s.melds.length<3)result=g.submitNewMeld(w,nm.cards,nm.rankPlan||null);
  else break;
  choices(g);if(result===false||result==='full')throw Error('policy chose illegal action');
 }
 let last=null;
 while(!st.gameOver&&!rummied&&s.hand.length&&s.discardsRemaining>0){const skip=typeof g.aiShouldSkipLowHandDiscard==='function'?g.aiShouldSkipLowHandDiscard(w):g.canSkipBaseDiscard(w);if(skip){s.discardsRemaining=0;break}const d=discardChoice(g,w);if(!d)break;last=d;g.removeFromHand(w,[d]);g.pushDiscard(d);g.armSafetyPin(w,d);s.discardsRemaining=Math.max(0,s.discardsRemaining-1)}
 if(!st.gameOver&&!rummied&&s.hand.length===0){g.triggerRummy(w,last?[last]:[],{returned:false});choices(g);rummied=true}
 if(!rummied||w==='enemy'){g.settleContracts(w);g.turnEnd(w)}unsub();s.hand.forEach(c=>c.age++);if(w==='enemy')st.turnNo++;acc.hands.push(s.hand.length);
}
const mean=a=>a.reduce((x,y)=>x+y,0)/(a.length||1),rate=(n,d)=>100*n/(d||1),round=(x,n=2)=>+Number(x||0).toFixed(n);
function runCohort(factory,cohort,seeds=500,maxTurns=120){
 const total={battles:seeds,turns:0,hands:[],rummys:0,noRummy:0,firstRummy:[],bloomActions:0,seasons:0,pictures:0,multiBloom:0,broken:0,returns:0,sunset:0,light:0,recycles:0,emergency:0,full:0,maintenance:0,bursts:0,chains:0,detonates:0,maxPower:[],battleTurns:[],capped:0,acqSkips:0,acqPasses:0};
 for(let seed=1;seed<=seeds;seed++){
  const g=factory(seed*101+cohort.length),st=g.state;setup(g,cohort,seed);
  const acc={rummys:0,firstRummyTurn:null,bloomActions:0,seasons:0,pictures:0,multiBloom:0,broken:0,hands:[],acqSkips:0,acqPasses:0};
  let t=0;for(;t<maxTurns&&!st.gameOver;t++)playSide(g,t%2?'enemy':'player',acc,t);
  if(!st.gameOver&&t>=maxTurns)total.capped++;
  const bm=g.getBattleMetrics(),cs=g.getCirculationStats(),tb=st.tbBalanceStats;
  total.turns+=t;total.hands.push(...acc.hands);total.rummys+=acc.rummys;if(acc.firstRummyTurn==null)total.noRummy++;else total.firstRummy.push(acc.firstRummyTurn);
  total.bloomActions+=acc.bloomActions;total.seasons+=acc.seasons;total.pictures+=acc.pictures;total.multiBloom+=acc.multiBloom;total.broken+=acc.broken;total.returns+=tb.returns||0;
  total.sunset+=tb.tbSunset||0;total.light+=tb.tbLightTrio||0;total.recycles+=tb.recycles||0;total.emergency+=tb.emergency||0;total.full+=cs.fullRecirculations||0;
  total.maintenance+=bm.maintenance.length;total.bursts+=bm.bursts.length;total.chains+=bm.chains.length;total.detonates+=bm.detonates.length;total.maxPower.push(bm.maxPower||0);total.battleTurns.push(t);total.acqSkips+=acc.acqSkips;total.acqPasses+=acc.acqPasses;
 }
 const low=total.hands.filter(x=>x>=1&&x<=3).length,direct=total.sunset+total.light;
 return{cohort,battles:seeds,sideTurns:total.turns,avgBattleTurns:round(mean(total.battleTurns)),cappedBattles:total.capped,avgHand:round(mean(total.hands),3),low13Pct:round(rate(low,total.hands.length)),rummyPer100:round(rate(total.rummys,total.turns)),noRummyPct:round(rate(total.noRummy,seeds)),avgFirstRummyTurn:total.firstRummy.length?round(mean(total.firstRummy)):null,maintenancePer100:round(rate(total.maintenance,total.turns)),bloomActionsPer100:round(rate(total.bloomActions,total.turns)),seasonCompletionsPer100:round(rate(total.seasons,total.turns)),pictureCompletionsPer100:round(rate(total.pictures,total.turns)),multiBloomPer100:round(rate(total.multiBloom,total.turns)),brokenMatchesPer100:round(rate(total.broken,total.turns)),returnsPer100:round(rate(total.returns,total.turns)),sunsetTriggers:total.sunset,lightTrioTriggers:total.light,directTriggersPer100Returns:round(rate(direct,total.returns)),directBonusPowerPer100Turns:round(100*(total.sunset*10+total.light*14)/(total.turns||1)),recycles:total.recycles,fullRecirculations:total.full,emergencyReleases:total.emergency,burstPer100:round(rate(total.bursts,total.turns)),chainPer100:round(rate(total.chains,total.turns)),detonatePer100:round(rate(total.detonates,total.turns)),avgMaxSwitch:round(mean(total.maxPower)),acquisitionSkips:total.acqSkips,acquisitionPasses:total.acqPasses};
}
export function runExperiment(seeds=500,maxTurns=120,cohorts=COHORTS){
 const factory=makeGameFactory(instrumentSource(html),{developer:true}),selected=(cohorts||COHORTS).filter(x=>COHORTS.includes(x));
 return{head:'current-main',seeds,maxTurns,policy:'actual shipped engine; symmetric deterministic cohort decks; 8-card hands; real acquisition/meld/attach/recover/maintenance/RUMMY/recycle/SWITCH/DETONATE; effect choices deterministically take first legal option to stress theme effects; normal rules unchanged',cohorts:selected.map(c=>runCohort(factory,c,seeds,maxTurns))};
}
if(process.argv[1]===fileURLToPath(import.meta.url)){
 const selected=(process.env.TB_COHORTS||'').split(',').map(x=>x.trim()).filter(Boolean);
 const result=runExperiment(Number(process.env.TB_SEEDS)||500,Number(process.env.TB_MAX_TURNS)||120,selected.length?selected:COHORTS);
 console.log('TWELVE_BLOOM_BALANCE_RESULT='+JSON.stringify(result));
 if(process.env.TB_OUTPUT)fs.writeFileSync(path.resolve(process.env.TB_OUTPUT),JSON.stringify(result,null,2)+'\n');
}

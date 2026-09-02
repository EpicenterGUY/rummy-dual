import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';

const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(value,message){assert.ok(value,message);console.log('PASS: '+message)}
function source(name){
 const marker=`function ${name}(`,start=script.indexOf(marker);assert.ok(start>=0,`missing ${name}`);
 let par=0,brace=-1;
 for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')par++;else if(script[i]===')')par--;else if(script[i]==='{'&&par===0){brace=i;break}}
 let depth=0;
 for(let i=brace;i<script.length;i++){if(script[i]==='{')depth++;else if(script[i]==='}'&&--depth===0)return script.slice(start,i+1)}
 throw new Error('unterminated '+name)
}
function declaration(name){
 const marker=`const ${name}=`,start=script.indexOf(marker);assert.ok(start>=0,`missing ${name}`);
 let quote=null,esc=false,depth=0,started=false;
 for(let i=start+marker.length;i<script.length;i++){
  const ch=script[i];
  if(quote){if(esc)esc=false;else if(ch==='\\')esc=true;else if(ch===quote)quote=null;continue}
  if(ch==="'"||ch==='"'||ch==='`'){quote=ch;continue}
  if(ch==='{'||ch==='['||ch==='('){depth++;started=true}
  else if(ch==='}'||ch===']'||ch===')')depth--;
  else if(ch===';'&&started&&depth===0)return script.slice(start,i+1)
 }
 throw new Error('unterminated declaration '+name)
}
new Function(script);
const KEY='rummyDuelRoguelikeRunDraftV1',storage=new Map([['normal-progress','untouched'],['m12-history','untouched']]);
let failWrites=false,writeCount=0;
const localStorage={getItem:key=>storage.get(key)||null,setItem:(key,value)=>{if(failWrites)throw Error('quota');writeCount++;storage.set(key,String(value))},removeItem:key=>storage.delete(key)};
const progress={roguelikeStarter:'pure',selectedChar:'collector',selectedTheme:'v-signal',totalClears:9,deckBuild:{slots:['C2'],variants:{C2:'C2'}}};
const state={sessionMode:'roguelike',player:{hand:['test-hand'],deck:['test-deck']},rewarded:false};
const progressBefore=JSON.stringify(progress);
const ctx=vm.createContext({console,localStorage,progress,state,charUnlocked:()=>true,SUIT_SYMBOL:{S:'♠',H:'♥',D:'♦',C:'♣'},THEME_BUILD_PROFILES:{}});
for(const name of ['ROGUELIKE_ROUTE_LIMITS','ROGUELIKE_ENDGAME','FIELDS','ROGUELIKE_ENCOUNTER_PROFILES','ROGUELIKE_REGIONS','ROGUELIKE_COMMON_START_ROUTE','NAMED','CHARACTERS','TENDENCY_BY_TAG','ROGUELIKE_STARTER_IDS','ROGUELIKE_STARTER_REGULAR_SLOTS','ROGUELIKE_STARTER_LOADOUTS','ROGUELIKE_REWARD_ROLES','ROGUELIKE_THEME_ENTRY_TAGS'])vm.runInContext(declaration(name),ctx);
vm.runInContext("const ROGUELIKE_STARTER_DECK_SIZE=30;const ROGUELIKE_RUN_DRAFT_KEY='rummyDuelRoguelikeRunDraftV1';const ROGUELIKE_COMMON_START_ZONE='common-start';const ROGUELIKE_REWARD_ALGORITHM='action-tags-v1';",ctx);
for(const name of [...script.matchAll(/function (\w+)\(/g)].map(m=>m[1]).filter(name=>/roguelike/i.test(name)).concat('namedSlot'))vm.runInContext(source(name),ctx);
const allIds=vm.runInContext('Object.keys(NAMED)',ctx);let pool=[...allIds];
ctx.unlockedNamed=()=>new Set(pool);
const current=()=>ctx.loadRoguelikeRunDraft(),saved=()=>storage.get(KEY),clone=x=>JSON.parse(JSON.stringify(x));
const nextRequest=()=>ctx.roguelikeNextRewardNodeRequest(current());
const issue=()=>ctx.roguelikeIssueRewardNode(nextRequest());
const token=node=>({runId:current().runId,nodeId:node.id,revision:node.revision,deckSignature:node.deckSignature});
const planFor=(node,index=0)=>{const pick=node.picks[index];return ctx.roguelikeCurrentReplacementPlan(pick.id,pick.role,'reward',node.id)};
const fresh=()=>{pool=[...allIds];return ctx.prepareRoguelikeRunDraft('pure')};



vm.runInContext("let uidSeq=1; const RANK_VALUE={A:1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,J:11,Q:12,K:13}; let randomSeed=7; Math.random=()=>{randomSeed=(randomSeed*1664525+1013904223)>>>0;return randomSeed/4294967296};",ctx);
for(const name of ['makeCard','parseRegularId','shuffle','blankStatus','setupRoguelikeBattle','showResult','showCirculationDraw','renderPracticeCoach'])vm.runInContext(source(name),ctx);
const regions=vm.runInContext('ROGUELIKE_REGIONS',ctx);
const win=()=>ctx.roguelikeCompleteBattleNode(ctx.roguelikeCurrentBattleNodeRequest());
const skip=n=>ctx.roguelikeSkipRewardNode(token(n));
const fakeElement=()=>({textContent:'',innerHTML:'',style:{},classList:{add(){},remove(){}}});
const ui=Object.fromEntries(['resultTitle','resultText','resultUnlocks','againBtn','overlay','practiceCoachText'].map(id=>[id,fakeElement()]));
const badge=fakeElement(),meta=fakeElement();ui.practiceCoach={hidden:true,querySelector:q=>q==='.badge'?badge:meta};
ctx.document={getElementById:id=>ui[id]||null};ctx.render=()=>{};ctx.renderProgress=()=>{};ctx.clearEffectChoices=()=>{};
ctx.log=(msg,cls)=>state.logs.push({msg,cls});
ctx.drawMany=(w,n)=>{for(let i=0;i<n;i++)state[w].hand.push(state[w].deck.pop());};
function resetRuntime(){const side=()=>({hp:60,maxHp:60,cores:3,shield:0,status:ctx.blankStatus(),deck:[{id:'old-random-deck'}],hand:[{id:'old-random-hand'}],spent:[],melds:[]});Object.assign(state,{player:side(),enemy:side(),selected:new Set(),selectionOrder:[],boardSelected:new Set(),target:null,logs:[],turnNo:1,turnToken:0,turn:'player',switchTarget:'neutral',switchPower:0,field:null,phase:'mulligan',gameOver:false,rewarded:false});}
resetRuntime();

// Render real progression controls; only the newGame browser boundary is replaced.
for(const id of ['roguelikeRunDraftStatus','roguelikePrepareBtn','roguelikeClearDraftBtn','roguelikeBattleBtn','roguelikeNodeBattleBtn'])ui[id]=fakeElement();
ui.roguelikeStarterGrid={...fakeElement(),closest:()=>null,querySelectorAll:()=>[]};
let pickerHTML='',regionButtons=[];
ui.roguelikeRegionPicker={...fakeElement(),get innerHTML(){return pickerHTML},set innerHTML(value){pickerHTML=value;regionButtons=[...value.matchAll(/data-run-region="([^"]+)"/g)].map(m=>({dataset:{runRegion:m[1]}}));},querySelectorAll:()=>regionButtons};
ctx.renderProgress=()=>ctx.renderRoguelikeStarterPicker();
ctx.startRoguelikeNodeBattle=()=>{resetRuntime();const d=current();return ctx.setupRoguelikeBattle(d,{progression:true,nodeRequest:ctx.roguelikeCurrentBattleNodeRequest(d)});};
const render=()=>ctx.renderRoguelikeStarterPicker();
const choose=id=>ctx.roguelikeChooseRegion({...nextRequest(),regionId:id});
const claim=node=>ctx.roguelikeApplyRunReplacement(planFor(node));
const settle=(node,take=false)=>{assert.ok(take?claim(node):skip(node));render();};

const endgame=vm.runInContext('ROGUELIKE_ENDGAME',ctx),endRoute=ctx.roguelikeEndgameRoute();
assert.equal(endRoute.length,3);assert.equal(endRoute.at(-1).kind,'final-boss');
assert.ok(regions.every(r=>r.id!==endgame.id),'endgame is not an ordinary region choice');
for(const id of ['roguelikeRewardSkipBtn','roguelikeRewardPreviewBtn','roguelikeRewardNodeNotice','roguelikeReplacementPreview','roguelikeReplacementApplyBtn','roguelikeReplacementCancelBtn'])ui[id]=fakeElement();
ui.roguelikeRewardPreview={...fakeElement(),querySelectorAll:()=>[]};
for(const name of ['isJoker','isSuitFlexible','setValid','runSequenceOK','runValid','meldType','combinations','bestNewMeld'])vm.runInContext(source(name),ctx);
let planningSamples=0;
for(const [stage,node] of endRoute.entries()){
 const encounter=ctx.roguelikeEncounterForNode(node);assert.ok(encounter);
 assert.equal(encounter.namedIds.length,[12,14,16][stage]);assert.equal(encounter.field.id,stage===2?'F9':'F5');
 const deck=ctx.makeRoguelikeEncounterDeck(encounter);assert.equal(deck.length,30);assert.equal(deck.filter(c=>c.named).length,[13,15,17][stage]);
 assert.equal(new Set(deck.map(c=>c.slot)).size,30);assert.ok(deck.every(c=>c.owner==='enemy'&&c.originOwner==='enemy'));
 const copy=ctx.roguelikeEncounterForNode(node);encounter.slots.pop();encounter.field.desc='mutated';
 assert.equal(copy.slots.length,29);assert.notEqual(copy.field.desc,'mutated');
 state.field=copy.field;
 for(let seed=0;seed<32;seed++){
  const hand=ctx.makeRoguelikeEncounterDeck(copy).slice(0,8),plan=ctx.bestNewMeld(hand);
  if(plan){assert.ok(plan.cards.every(c=>hand.includes(c)));assert.ok(ctx.meldType(plan.cards));}
  planningSamples++;
 }
 assert.equal(ctx.roguelikeEncounterForNode({...node,kind:stage===2?'boss':'final-boss'}),null);
}
assert.equal(planningSamples,96);
const starters=['pure','wanderer','collector','salvager','jester'];
const requestFor=(draft,index,id,zone=endgame.id)=>({runId:draft.runId,sequence:draft.rewardNodes.entries.length+1,revision:draft.runDeck.revision,deckSignature:ctx.roguelikeRunDeckSignature(draft.runDeck),battleIndex:index,battleNodeId:id,zone});
let paths=0,endgameBattles=0,completedRuns=0;
for(const first of regions)for(const second of regions.filter(r=>r.id!==first.id)){
 pool=[...allIds];const starter=starters[paths%starters.length],pure=starter==='pure';
 ctx.prepareRoguelikeRunDraft(starter);const created=current();
 assert.equal(created.status,'prepared');assert.equal(created.completedAt,null);
 assert.equal(choose(endgame.id),false,'Null Ward cannot skip the two-region route');
 assert.equal(ctx.roguelikeCompleteBattleNode(requestFor(created,11,endRoute[0].id)),null);
 const forged=clone(created);forged.status='completed';forged.completedAt=new Date().toISOString();
 assert.equal(ctx.normalizeRoguelikeRunDraft(forged),null,'completion flag alone cannot complete a run');
 for(let i=0;i<3;i++)settle(win(),!pure&&i===0);
 assert.ok(choose(first.id));for(let i=0;i<4;i++)settle(win(),!pure&&i%2===0);
 assert.ok(choose(second.id));for(let i=0;i<3;i++)settle(win(),!pure&&i===0);
 const secondBoss=win(),legacyPending=current();legacyPending.version=7;delete legacyPending.completedAt;legacyPending.nodeIndex=900;legacyPending.currentZone='wrong';
 storage.set(KEY,JSON.stringify(legacyPending));const legacyJSON=saved(),loaded=current();
 assert.equal(loaded.version,8);assert.equal(loaded.nodeIndex,11);assert.equal(loaded.currentZone,second.id);
 assert.equal(loaded.status,'prepared');assert.equal(loaded.completedAt,null);assert.equal(saved(),legacyJSON);
 assert.equal(ctx.roguelikeCurrentBattleNodeRequest(),null,'old pending boss reward still gates endgame entry');
 assert.equal(ctx.roguelikeCompleteBattleNode(requestFor(loaded,11,endRoute[0].id)),null);
 settle(secondBoss,!pure);
 const legacyCleared=current(),beforeDeck=JSON.stringify(legacyCleared.runDeck),beforeLedger=JSON.stringify(legacyCleared.rewardNodes);
 legacyCleared.version=7;delete legacyCleared.completedAt;storage.set(KEY,JSON.stringify(legacyCleared));
 assert.equal(current().version,8);assert.equal(current().currentZone,endgame.id);assert.equal(current().runId,created.runId);
 assert.equal(JSON.stringify(current().runDeck),beforeDeck);assert.equal(JSON.stringify(current().rewardNodes),beforeLedger);
 assert.equal(ctx.roguelikeCurrentBattleNodeRequest().battleNodeId,endRoute[0].id);
 assert.equal(ctx.roguelikeBattleProgress().total,14);assert.equal(current().status,'prepared');
 settle(issue());assert.equal(current().nodeIndex,11,'prototype rewards do not advance the endgame route');
 if(paths===0)pool=[]; // An empty eligible pool still permits each reward gate to be skipped.
 let finalRequest,finalReward,finalPlan;
 for(const [stage,node] of endRoute.entries()){
  const request=ctx.roguelikeCurrentBattleNodeRequest(),shown=ctx.roguelikeBattleNodeForRequest(request),before=saved();
  assert.equal(request.battleIndex,11+stage);assert.equal(request.battleNodeId,node.id);assert.equal(request.zone,endgame.id);
  assert.equal(shown.kind,node.kind);assert.equal(shown.label,node.label);
  assert.equal(ctx.roguelikeCompleteBattleNode({...request,battleIndex:request.battleIndex+1}),null);
  assert.equal(ctx.roguelikeCompleteBattleNode({...request,zone:first.id}),null);
  render();assert.ok(ui.roguelikeRunDraftStatus.innerHTML.includes(node.label));assert.equal(ui.roguelikeNodeBattleBtn.disabled,false);
  ui.roguelikeNodeBattleBtn.onclick();const encounter=ctx.roguelikeEncounterForNode(node);
  assert.equal(state.roguelikeEncounter.nodeId,node.id);assert.equal(state.roguelikeEncounter.name,encounter.name);
  assert.equal(state.field.id,encounter.field.id);assert.equal(state.player.cores,3);assert.equal(state.enemy.cores,3);
  assert.equal(state.player.hp,60);assert.equal(state.enemy.hp,60);assert.equal(state.player.hand.length,8);assert.equal(state.enemy.hand.length,8);
  assert.equal(state.roguelikeDeckFingerprint,ctx.roguelikeBattleDeckFingerprint(current()));assert.equal(saved(),before);
  ctx.renderPracticeCoach();assert.equal(meta.textContent,encounter.name);assert.equal(badge.textContent,stage===2?'최종 보스':'지역 교전');
  state.gameOver=true;ctx.showResult(false);assert.equal(state.roguelikeNodeResult,'loss');assert.equal(saved(),before);
  if(stage===2)assert.equal(ui.resultTitle.textContent,'최종 보스 패배');
  ctx.showCirculationDraw();assert.equal(state.roguelikeNodeResult,'draw');assert.equal(saved(),before);
  failWrites=true;ctx.showResult(true);failWrites=false;assert.equal(state.roguelikeNodeResult,'stale');assert.equal(saved(),before);
  ctx.showResult(true);const receipt=current().rewardNodes.entries.at(-1),issued=saved();
  assert.equal(receipt.regionId,endgame.id);assert.equal(receipt.algorithm,'action-tags-region-v1');assert.equal(receipt.status,'pending');
  assert.equal(ctx.roguelikeCurrentBattleNodeRequest(),null);assert.equal(current().status,'prepared');assert.equal(current().completedAt,null);
  assert.equal(ui.roguelikeNodeBattleBtn.disabled,true);assert.equal(regionButtons.length,0);
  assert.ok(ctx.roguelikeRewardPreviewText().includes('널워드 성향 반영'));
  ctx.showResult(true);assert.equal(saved(),issued,'repeated victory cannot reroll or complete the run early');
  const invalidLegacy=current();invalidLegacy.version=7;assert.equal(ctx.normalizeRoguelikeRunDraft(invalidLegacy),null,'legacy schema cannot contain new endgame receipts');
  const wrongRegion=current();wrongRegion.rewardNodes.entries.at(-1).regionId=second.id;assert.equal(ctx.normalizeRoguelikeRunDraft(wrongRegion),null);
  const unweighted=current();unweighted.rewardNodes.entries.at(-1).algorithm='action-tags-v1';delete unweighted.rewardNodes.entries.at(-1).regionId;assert.equal(ctx.normalizeRoguelikeRunDraft(unweighted),null);
  if(stage<2)settle(receipt,!pure&&stage===0);
  else{
   finalRequest=request;finalReward=receipt;finalPlan=receipt.picks.length?planFor(receipt):null;
   assert.equal(ui.resultTitle.textContent,'최종 보스 격파');assert.equal(ui.againBtn.textContent,'마지막 보상 보기');
   assert.ok(ui.roguelikeRunDraftStatus.innerHTML.includes('마지막 보상 수령 또는 건너뛰기 후 런 완료'));
   assert.equal(ui.roguelikeNodeBattleBtn.textContent,'마지막 보상 처리 후 런 완료');
  }
  endgameBattles++;
 }
 // Completing the last reward, deck change, and timestamp is one atomic persistence operation.
 const pendingJSON=saved(),pending=current(),beforeRevision=pending.runDeck.revision,claimFinal=!pure&&paths%2===1&&!!finalPlan;
 const finishFromUI=()=>{if(claimFinal){ctx.renderRoguelikeReplacementPreview(finalPlan);ui.roguelikeReplacementApplyBtn.onclick();}else{render();ui.roguelikeRewardSkipBtn.onclick();}};
 const ranker=ctx.roguelikeRewardCandidates,unlocked=ctx.unlockedNamed;
 ctx.roguelikeRewardCandidates=()=>{throw Error('frozen final reward must not rerank')};ctx.unlockedNamed=()=>{throw Error('completion must not reread unlocks')};
 failWrites=true;finishFromUI();failWrites=false;
 assert.equal(saved(),pendingJSON);assert.equal(current().status,'prepared');assert.equal(current().completedAt,null);
 const beforeCompletionWrites=writeCount;finishFromUI();
 const completed=current(),completedJSON=saved(),timestamp=completed.completedAt;
 assert.equal(writeCount,beforeCompletionWrites+2,'completion saves run state and one archive record');
 assert.equal(completed.status,'completed');assert.equal(completed.version,8);assert.equal(completed.runId,created.runId);
 const archive=JSON.parse(storage.get('rummyDuelRoguelikeRunHistoryV1'));const archived=archive.entries.find(x=>x.runId===completed.runId);
 assert.ok(archived,'completed run is archived');assert.equal(archived.finalDeckSignature,ctx.roguelikeRunDeckSignature(completed.runDeck));assert.equal(archived.rewards.filter(x=>x.source==='battle').length,14);assert.equal(JSON.stringify(archived.regionPath),JSON.stringify(completed.regionPath));
 const archiveWrites=writeCount;render();assert.equal(writeCount,archiveWrites,'rerender does not duplicate an archived run');
 assert.equal(new Date(timestamp).toISOString(),timestamp);assert.equal(completed.currentZone,endgame.id);assert.equal(completed.nodeIndex,14);
 assert.equal(completed.rewardNodes.entries.filter(n=>n.source==='battle').length,14);assert.equal(completed.rewardNodes.entries.length,15);
 assert.equal(completed.rewardNodes.entries.at(-1).status,claimFinal?'claimed':'skipped');assert.equal(completed.runDeck.revision,beforeRevision+(claimFinal?1:0));
 if(pure)assert.equal(completed.runDeck.cards.filter(c=>c.variantId).length,0,'PURE may finish by skipping every named reward');
 assert.equal(ui.roguelikeNodeBattleBtn.disabled,true);assert.equal(ui.roguelikeNodeBattleBtn.textContent,'런 완료');
 assert.equal(ui.roguelikeRewardPreviewBtn.disabled,true);assert.equal(ui.roguelikeRewardSkipBtn.disabled,true);assert.equal(ui.roguelikePrepareBtn.textContent,'새 런 시작');
 assert.equal(ui.roguelikeBattleBtn.disabled,false);assert.equal(ui.roguelikeBattleBtn.textContent,'최종 덱 실험전 시작');
 assert.ok(ui.roguelikeRunDraftStatus.innerHTML.includes('런 완료 · 널워드 돌파'));assert.ok(ui.roguelikeRunDraftStatus.innerHTML.includes('14전투 승리'));
 assert.ok(ui.roguelikeRunDraftStatus.innerHTML.includes(first.name+' → '+second.name+' → 널워드'));assert.ok(ui.roguelikeRunDraftStatus.innerHTML.includes('최종 덱 · 30장'));
 assert.equal(ctx.roguelikeNextRewardNodeRequest(completed),null);assert.equal(ctx.roguelikeCurrentBattleNodeRequest(completed),null);
 assert.equal(ctx.roguelikeCompleteBattleNode(finalRequest).id,finalReward.id);assert.equal(ctx.roguelikeCompleteBattleNode({...finalRequest,zone:second.id}),null);
 assert.equal(ctx.roguelikeSkipRewardNode(token(finalReward)),false);assert.equal(ctx.roguelikeApplyRunReplacement(finalPlan),false);
 assert.equal(ctx.roguelikeIssueRewardNode(requestFor(completed,14,'unused')),null);assert.equal(choose(first.id),false);
 ctx.showResult(true);assert.equal(ui.resultTitle.textContent,'런 완료');assert.equal(saved(),completedJSON);assert.equal(current().completedAt,timestamp);
 const corruptions=[
  d=>d.status='prepared',d=>d.completedAt=null,d=>d.completedAt='invalid',d=>d.completedAt='2026-09-02',
  d=>d.rewardNodes.entries.pop(),d=>d.rewardNodes.entries.at(-1).battleNodeId='null-ward-2',
  d=>d.rewardNodes.entries.at(-1).status='pending',d=>d.regionPath.reverse(),d=>d.regionPath.push(endgame.id),
  d=>{d.version=7;d.status='prepared';delete d.completedAt;},d=>d.version=9,
  d=>{const extra=clone(d.rewardNodes.entries.find(n=>n.source==='prototype'));extra.sequence=d.rewardNodes.entries.length+1;extra.id=d.runId+':reward:'+extra.sequence;extra.revision=d.runDeck.revision;extra.deckSignature=ctx.roguelikeRunDeckSignature(d.runDeck);extra.picks=[];extra.status='skipped';extra.selectedId=null;d.rewardNodes.entries.push(extra);}
 ];
 for(const mutate of corruptions){const bad=clone(completed);mutate(bad);assert.equal(ctx.normalizeRoguelikeRunDraft(bad),null,'invalid completion cannot silently reopen or duplicate the run');}
 assert.equal(saved(),completedJSON);
 ctx.roguelikeRewardCandidates=ranker;ctx.unlockedNamed=unlocked;
 resetRuntime();assert.ok(ctx.setupRoguelikeBattle(completed));assert.equal(state.roguelikeProgressionBattle,false);assert.equal(state.roguelikeEncounter,null);
 ctx.showResult(true);assert.equal(saved(),completedJSON,'completed final deck remains usable in isolated RUN TEST');
 render();ui.roguelikePrepareBtn.onclick();const next=current();
 assert.notEqual(next.runId,completed.runId);assert.equal(next.status,'prepared');assert.equal(next.completedAt,null);assert.equal(next.nodeIndex,0);assert.equal(next.regionPath.length,0);
 assert.equal(ctx.roguelikeCompleteBattleNode(finalRequest),null,'a finished run callback cannot affect the next run');
 completedRuns++;paths++;ok(true,first.name+' → '+second.name+' → 널워드 completion persists once');
}
assert.equal(paths,12);assert.equal(endgameBattles,36);assert.equal(completedRuns,12);
assert.equal(JSON.stringify(progress),progressBefore);assert.equal(storage.get('normal-progress'),'untouched');assert.equal(storage.get('m12-history'),'untouched');
console.log('M11A endgame completion passed: 12 ordered routes, 36 endgame setups/results, 96 AI planning samples.');

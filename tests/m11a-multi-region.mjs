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
for(const name of ['ROGUELIKE_ROUTE_LIMITS','FIELDS','ROGUELIKE_ENCOUNTER_PROFILES','ROGUELIKE_REGIONS','ROGUELIKE_COMMON_START_ROUTE','NAMED','CHARACTERS','TENDENCY_BY_TAG','ROGUELIKE_STARTER_IDS','ROGUELIKE_STARTER_REGULAR_SLOTS','ROGUELIKE_STARTER_LOADOUTS','ROGUELIKE_REWARD_ROLES','ROGUELIKE_THEME_ENTRY_TAGS'])vm.runInContext(declaration(name),ctx);
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
const migrateV6=()=>{
 const before=current(),legacy=clone(before);legacy.version=6;legacy.nodeIndex=999;legacy.currentZone='wrong';
 storage.set(KEY,JSON.stringify(legacy));const raw=saved(),loaded=current();
 assert.equal(loaded.version,7);assert.equal(loaded.runId,before.runId);assert.equal(loaded.createdAt,before.createdAt);
 assert.deepEqual(clone(loaded.runDeck),clone(before.runDeck));assert.deepEqual(clone(loaded.rewardNodes),clone(before.rewardNodes));
 assert.deepEqual(clone(loaded.regionPath),clone(before.regionPath));assert.equal(loaded.nodeIndex,before.nodeIndex);assert.equal(loaded.currentZone,before.currentZone);
 assert.equal(saved(),raw,'loading a legacy run never rewrites the stored file');
};
let paths=0,secondRegionBattles=0;
for(const first of regions)for(const second of regions.filter(r=>r.id!==first.id)){
 fresh();migrateV6();
 for(let i=0;i<3;i++){const receipt=win();migrateV6();settle(receipt,i===0);}
 assert.ok(choose(first.id));
 for(let i=0;i<3;i++){
  const receipt=win();migrateV6();
  assert.equal(choose(second.id),false,'cannot enter another region before the first boss');
  settle(receipt,i===0);
 }
 const firstBossTicket=ctx.roguelikeCurrentBattleNodeRequest(),firstBoss=win();
 assert.equal(firstBoss.battleNodeId,first.id+'-boss');migrateV6();render();
 assert.equal(regionButtons.length,0,'pending first boss reward hides the route choice');
 assert.equal(ctx.roguelikeBattleProgress().awaitingRegion,false);
 assert.equal(choose(second.id),false);
 const injected=current();injected.regionPath.push(second.id);
 assert.equal(ctx.normalizeRoguelikeRunDraft(injected),null,'pending boss cannot authorize a saved second visit');
 settle(firstBoss,paths%2===0);migrateV6();render();
 assert.ok(ctx.roguelikeBattleProgress().awaitingRegion);
 assert.equal(ctx.roguelikeCurrentBattleNodeRequest(),null);
 assert.equal(ui.roguelikeNodeBattleBtn.disabled,true);
 assert.ok(ui.roguelikeRunDraftStatus.innerHTML.includes('다음 지역을 선택하세요'));
 assert.equal(regionButtons.length,3);assert.ok(regionButtons.every(b=>b.dataset.runRegion!==first.id));
 assert.ok(pickerHTML.includes('지역 2/2'));
 // A prototype reward changes only the save token, never the combat or region index.
 const staleButton=regionButtons.find(b=>b.dataset.runRegion===second.id),testReward=issue();settle(testReward);
 const beforeStale=saved();staleButton.onclick();assert.equal(saved(),beforeStale,'old region buttons reject a changed reward sequence');
 render();failWrites=true;const beforeFailure=saved();regionButtons.find(b=>b.dataset.runRegion===second.id).onclick();failWrites=false;
 assert.equal(saved(),beforeFailure);assert.equal(current().regionPath.length,1,'failed route persistence keeps the previous region');
 const carry=current(),carryDeck=JSON.stringify(carry.runDeck),carryLedger=JSON.stringify(carry.rewardNodes),carryTime=carry.createdAt;
 assert.equal(choose(first.id),false,'a visited region cannot be selected again');
 render();regionButtons.find(b=>b.dataset.runRegion===second.id).onclick();
 assert.deepEqual(clone(current().regionPath),[first.id,second.id]);assert.equal(current().version,7);
 assert.equal(current().runId,carry.runId);assert.equal(current().createdAt,carryTime);
 assert.equal(JSON.stringify(current().runDeck),carryDeck);assert.equal(JSON.stringify(current().rewardNodes),carryLedger);
 assert.equal(current().currentZone,second.id);assert.equal(current().nodeIndex,7);
 assert.equal(ctx.roguelikeBattleProgress().total,11);assert.equal(ctx.roguelikeBattleProgress().current.visit,2);
 assert.equal(regionButtons.length,0);assert.equal(ui.roguelikeNodeBattleBtn.disabled,false);
 assert.ok(ui.roguelikeRunDraftStatus.innerHTML.includes('공통 시작 → '+first.name+' → '+second.name));
 assert.equal(choose(regions.find(r=>r.id!==first.id&&r.id!==second.id).id),false);
 const afterChoice=saved();assert.equal(ctx.roguelikeCompleteBattleNode(firstBossTicket).id,firstBoss.id);
 assert.equal(ctx.roguelikeCompleteBattleNode({...firstBossTicket,zone:second.id}),null);
 assert.equal(saved(),afterChoice,'an old boss result cannot issue a reward on the new route');
 const ticket=ctx.roguelikeCurrentBattleNodeRequest();assert.equal(ticket.battleIndex,7);assert.equal(ticket.battleNodeId,second.id+'-1');
 assert.equal(ctx.roguelikeCompleteBattleNode({...ticket,zone:first.id,battleNodeId:first.id+'-1'}),null);
 assert.equal(ctx.roguelikeCompleteBattleNode({...ticket,battleNodeId:second.id+'-boss'}),null);
 const valid=current();
 for(const mutate of [
  d=>d.regionPath.reverse(),d=>d.regionPath.shift(),d=>d.regionPath[1]=d.regionPath[0],
  d=>d.regionPath[1]='missing',d=>d.regionPath.push(regions.find(r=>!d.regionPath.includes(r.id)).id),
  d=>d.version=6,d=>d.version=8,
  d=>{d.rewardNodes.entries.find(n=>n.battleNodeId===first.id+'-boss').battleNodeId=second.id+'-boss';}
 ]){const bad=clone(valid);mutate(bad);assert.equal(ctx.normalizeRoguelikeRunDraft(bad),null,'invalid or reordered route is rejected without resetting growth');}
 assert.equal(saved(),afterChoice);
 for(let stage=0;stage<4;stage++){
  const request=ctx.roguelikeCurrentBattleNodeRequest(),node=ctx.roguelikeBattleProgress().current,encounter=ctx.roguelikeEncounterForNode(node);
  assert.equal(request.battleIndex,7+stage);assert.equal(request.zone,second.id);
  assert.equal(request.battleNodeId,second.id+(stage===3?'-boss':'-'+(stage+1)));
  const shownNode=ctx.roguelikeBattleNodeForRequest(request);
  assert.equal(shownNode.id,node.id);assert.equal(shownNode.visit,2);assert.equal(shownNode.kind,node.kind);
  assert.equal(ctx.roguelikeBattleNodeForRequest({...request,battleIndex:request.battleIndex+1}),null);
  const beforeBattle=saved(),beforeRevision=current().runDeck.revision;
  render();ui.roguelikeNodeBattleBtn.onclick();
  assert.equal(state.roguelikeEncounter.nodeId,node.id);assert.equal(state.roguelikeEncounter.name,encounter.name);
  assert.equal(state.field.id,encounter.field.id);assert.equal(state.player.hand.length,8);assert.equal(state.enemy.hand.length,8);
  assert.equal(state.player.hand.length+state.player.deck.length,30);assert.equal(state.enemy.hand.length+state.enemy.deck.length,30);
  assert.equal(state.roguelikeDeckFingerprint,ctx.roguelikeBattleDeckFingerprint(current()));
  assert.equal(state.roguelikeBattleNodeRequest.battleIndex,7+stage);assert.equal(saved(),beforeBattle);
  state.gameOver=true;ctx.showResult(false);assert.equal(saved(),beforeBattle);assert.equal(state.roguelikeNodeResult,'loss');
  if(stage===3)assert.equal(ui.resultTitle.textContent,'중간 보스 패배');
  ctx.showCirculationDraw();assert.equal(saved(),beforeBattle);assert.equal(state.roguelikeNodeResult,'draw');
  failWrites=true;ctx.showResult(true);failWrites=false;assert.equal(saved(),beforeBattle);assert.equal(state.roguelikeNodeResult,'stale');
  ctx.showResult(true);const reward=current().rewardNodes.entries.at(-1),issued=saved();
  assert.equal(reward.battleIndex,7+stage);assert.equal(reward.battleNodeId,node.id);assert.equal(reward.regionId,second.id);
  assert.equal(reward.algorithm,'action-tags-region-v1');assert.equal(reward.status,'pending');
  assert.equal(current().runDeck.revision,beforeRevision);assert.equal(ctx.roguelikeCurrentBattleNodeRequest(),null);
  assert.equal(regionButtons.length,0);assert.equal(ui.roguelikeNodeBattleBtn.disabled,true);
  assert.ok(ui.resultText.textContent.includes(second.name));
  if(stage===3){assert.equal(ui.resultTitle.textContent,'중간 보스 격파');assert.ok(ui.resultText.textContent.includes('후반 특수구역은 준비 중'));}
  ctx.showResult(true);assert.equal(saved(),issued,'repeated second-region result preserves its frozen reward');
  const badProvenance=current();badProvenance.rewardNodes.entries.at(-1).regionId=first.id;
  assert.equal(ctx.normalizeRoguelikeRunDraft(badProvenance),null,'second-region rewards cannot retain the old region bias');
  settle(reward,(paths+stage)%2===0);secondRegionBattles++;
 }
 const end=current(),allReceipts=end.rewardNodes.entries;
 assert.equal(end.nodeIndex,11);assert.equal(allReceipts.filter(n=>n.source==='battle').length,11);
 assert.equal(allReceipts.filter(n=>n.source==='prototype').length,1);assert.equal(end.currentZone,second.id);
 assert.deepEqual(clone(allReceipts.slice(0,carry.rewardNodes.entries.length)),clone(carry.rewardNodes.entries));
 assert.equal(ctx.roguelikeBattleProgress().finished,true);assert.equal(ctx.roguelikeBattleProgress().awaitingRegion,false);
 assert.equal(ctx.roguelikeCurrentBattleNodeRequest(),null);assert.equal(regionButtons.length,0);assert.equal(ui.roguelikeNodeBattleBtn.disabled,true);
 assert.ok(ui.roguelikeRunDraftStatus.innerHTML.includes('두 지역 완료 · 런 실전 11/11 · 후반 특수구역 준비 중'));
 assert.ok(ui.roguelikeNodeBattleBtn.textContent.includes('후반 구역 준비 중'));
 const finalJSON=saved();assert.equal(choose(regions.find(r=>!end.regionPath.includes(r.id)).id),false);assert.equal(saved(),finalJSON);
 const caches=clone(end);caches.nodeIndex=123;caches.currentZone=first.id;storage.set(KEY,JSON.stringify(caches));
 assert.equal(current().nodeIndex,11);assert.equal(current().currentZone,second.id);
 paths++;ok(true,first.name+' → '+second.name+' carries growth through the second boss');
}
assert.equal(paths,12);assert.equal(secondRegionBattles,48);
assert.equal(ctx.roguelikeRegionRoute(['neon-arc','neon-arc']).length,0);
assert.equal(ctx.roguelikeRegionRoute(['neon-arc','red-zone','iron-grave']).length,0);
assert.equal(ctx.roguelikeBattleNodeForRequest({zone:'red-zone',battleNodeId:'red-zone-1',battleIndex:11}),null);
assert.equal(ctx.roguelikeBattleNodeForRequest({zone:'common-start',battleNodeId:'common-1',battleIndex:0}).id,'common-1');
assert.equal(JSON.stringify(progress),progressBefore);assert.equal(storage.get('normal-progress'),'untouched');assert.equal(storage.get('m12-history'),'untouched');
console.log('M11A two-region progression passed: 12 ordered routes, 48 second-region battle setups/results.');

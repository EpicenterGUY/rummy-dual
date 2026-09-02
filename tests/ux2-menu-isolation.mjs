import assert from 'node:assert/strict';
import {html,makeGame} from './helpers/live-game.mjs';

const NORMAL='rummyDuelProgressV25',RUN='rummyDuelRoguelikeRunDraftV1',HISTORY='rummyDuelRoguelikeRunHistoryV1';
const DEV='rummyDuelDeveloperProgressV1',DEV_RUN='rummyDuelDeveloperRunDraftV1',DEV_HISTORY='rummyDuelDeveloperRunHistoryV1';
const store=new Map(),g=makeGame(html,93,{storage:store});
const copy=value=>JSON.parse(JSON.stringify(value));
const nodeToken=()=>g.roguelikeCurrentBattleNodeRequest(g.loadRoguelikeRunDraft());
function skipPending(){const d=g.loadRoguelikeRunDraft(),n=g.roguelikePendingRewardNode(d);assert.ok(n);assert.ok(g.roguelikeSkipRewardNode({runId:d.runId,nodeId:n.id,revision:n.revision,deckSignature:n.deckSignature}));}
function finishRun(){
  for(let guard=0;guard<40;guard++){
    const d=g.loadRoguelikeRunDraft(),stage=g.roguelikeMenuStage(d);
    if(stage==='completed')return d;
    if(stage==='reward'){skipPending();continue;}
    if(stage==='region'){
      const region=['neon-arc','red-zone'].find(id=>!d.regionPath.includes(id));
      assert.ok(g.roguelikeChooseRegion({...g.roguelikeNextRewardNodeRequest(d),regionId:region}));continue;
    }
    assert.equal(stage,'battle');assert.ok(g.roguelikeCompleteBattleNode(nodeToken()));
  }
  assert.fail('run did not reach completion');
}

g.showStartScreen();g.saveProgress();
const ordinary=g.getProgress(),normalBefore=store.get(NORMAL);
assert.equal(g.roguelikeMenuStage(null),'empty');
const initial=g.commitNormalRunStart('wanderer',null);
assert.ok(initial);assert.equal(g.roguelikeMenuStage(initial),'battle');
assert.equal(g.commitNormalRunStart('pure',initial.runId),false,'replacing a live run requires explicit in-UI consent');
assert.equal(g.commitNormalRunStart('pure','stale-run',true),false,'a stale confirmation cannot replace a newer run');
const originalRun=store.get(RUN),normalRequest=nodeToken();

g.setDeveloperMode(true);
assert.notEqual(g.getProgress(),ordinary,'DEV edits a separate object');
assert.equal(g.loadRoguelikeRunDraft(),null,'DEV cannot consume the normal run');
assert.equal(g.commitNormalRunStart('pure',null),false,'normal creation is closed in a DEV session');
assert.ok(!g.roguelikeCompleteBattleNode(normalRequest),'normal battle tickets cannot advance a DEV run');
g.getProgress().selectedChar='jester';g.getProgress().selectedTheme='point-blank';
g.getProgress().deckBuild.enabled=true;g.getProgress().deckBuild.variants.S3='S3';g.getProgress().totalClears=99;g.saveProgress();
assert.equal(store.get(NORMAL),normalBefore);assert.equal(store.get(RUN),originalRun);
assert.equal(JSON.parse(store.get(DEV)).selectedChar,'jester');
g.testSetDeveloperField('F9');g.newGame('battle');
assert.equal(g.state.developerBattle,true);assert.equal(g.state.field.id,'F9');
const devProgressBefore=copy(g.getProgress());g.grantVictoryProgress();
assert.deepEqual(copy(g.getProgress()),devProgressBefore,'DEV battle victories do not grant clear/level rewards');
assert.equal(g.saveBattleMetrics('win'),false,'DEV battles never enter ordinary M12 samples');
g.prepareRoguelikeRunDraft('pure');
assert.ok(store.has(DEV_RUN));assert.equal(store.get(RUN),originalRun);
const request=g.roguelikeNextRewardNodeRequest(g.loadRoguelikeRunDraft());
assert.ok(g.roguelikeIssueRewardNode(request),'DEV manual reward tools remain usable');
skipPending();
assert.ok(g.startRoguelikeNodeBattle());assert.equal(g.state.developerBattle,true,'DEV run nodes retain the DEV battle snapshot');
const devTicket=copy(g.state.roguelikeBattleNodeRequest);
g.showResult(true);assert.equal(g.roguelikeMenuStage(g.loadRoguelikeRunDraft()),'reward');
g.restartCurrentCombat();assert.equal(g.developerModeActive(),true,'DEV result navigation returns to the same sandbox');
assert.equal(g.roguelikeMenuStage(g.loadRoguelikeRunDraft()),'reward');
assert.equal(g.document.getElementById('developerRunTools').open,true);
const devCompleted=finishRun();assert.equal(devCompleted.status,'completed');
assert.equal(g.loadRoguelikeRunHistory().entries.length,1);assert.ok(store.has(DEV_HISTORY));
assert.equal(store.has(HISTORY),false);assert.equal(store.get(RUN),originalRun);assert.equal(store.get(NORMAL),normalBefore);

g.showStartScreen();
assert.equal(g.developerModeActive(),false);assert.equal(g.state.sessionMode,'menu');
assert.equal(g.getProgress(),ordinary,'normal selections are restored without copying DEV choices');
assert.equal(g.getProgress().selectedChar,'wanderer');assert.equal(g.getProgress().selectedTheme,'mixed');
assert.equal(g.getProgress().deckBuild.enabled,false);assert.equal(g.getProgress().totalClears,0);
assert.equal(g.loadRoguelikeRunDraft().runId,initial.runId);
assert.ok(!g.roguelikeCompleteBattleNode(devTicket),'a stale DEV win cannot advance ordinary progress');
g.newGame('battle');assert.equal(g.state.developerBattle,false);assert.equal(g.state.field,null,'DEV field force does not leak to an ordinary battle');
g.grantVictoryProgress();assert.equal(g.getProgress().totalClears,1,'ordinary victories still award progress');
assert.equal(g.getProgress().chars.wanderer,1);
g.showStartScreen();
assert.ok(g.startRoguelikeNodeBattle());assert.equal(g.state.developerBattle,false);
g.showResult(true);g.restartCurrentCombat();
assert.equal(g.developerModeActive(),false);assert.equal(g.state.sessionMode,'menu');
assert.match(g.document.getElementById('runCurrentContent').innerHTML,/보상 선택/,'normal results lead to the reward stage');
const pending=g.loadRoguelikeRunDraft(),reward=g.roguelikePendingRewardNode(pending);
if(reward.picks.length){const pick=reward.picks[0],plan=g.roguelikeCurrentReplacementPlan(pick.id,pick.role,'reward',reward.id);assert.ok(g.roguelikeApplyRunReplacement(plan));assert.equal(g.roguelikeApplyRunReplacement(plan),false,'replaying a claimed reward remains rejected');}
else skipPending();
const normalCompleted=finishRun();assert.equal(normalCompleted.status,'completed');
assert.equal(g.loadRoguelikeRunHistory().entries.length,1);assert.ok(store.has(HISTORY));
assert.equal(g.getProgress().totalClears,1,'run rewards and completion do not grant normal clears');
const completedNormal=store.get(RUN),normalArchive=store.get(HISTORY);
g.setDeveloperMode(true);assert.equal(g.loadRoguelikeRunDraft().runId,devCompleted.runId);
assert.ok(g.clearRoguelikeRunDraft());assert.equal(store.has(DEV_RUN),false);assert.equal(store.get(RUN),completedNormal);assert.equal(store.get(HISTORY),normalArchive);
g.setDeveloperMode(false);
const replacement=g.commitNormalRunStart('pure',normalCompleted.runId);
assert.ok(replacement);assert.equal(g.loadRoguelikeRunHistory().entries.length,1,'new runs preserve completion records');

// Test the actual renderers against both pools, without adding development cards to normal views.
g.renderProgress();g.renderCodex();
assert.doesNotMatch(g.document.getElementById('themeGroupGrid').innerHTML,/point-blank/);
assert.doesNotMatch(g.document.getElementById('codexGrid').innerHTML,/codexDebug|DEV 공개/);
g.setDeveloperMode(true);g.renderProgress();g.renderCodex();
assert.match(g.document.getElementById('themeGroupGrid').innerHTML,/개발 중 · DEV 선택 가능/);
assert.match(g.document.getElementById('codexGrid').innerHTML,/codexDebug/);
g.setDeveloperMode(false);
assert.equal(g.document.getElementById('codexDevFilters').hidden,true);

const beforeSettings=store.get(NORMAL);assert.ok(g.updatePlayerSetting('reducedMotion',true));assert.ok(g.updatePlayerSetting('largeText',true));
assert.equal(g.document.documentElement.dataset.reducedMotion,'true');assert.equal(g.document.documentElement.dataset.largeText,'true');
assert.equal(store.get(NORMAL),beforeSettings,'display preferences use a separate settings key');
assert.deepEqual(copy(g.loadPlayerSettings()),{reducedMotion:true,largeText:true});
assert.equal(g.updatePlayerSetting('totalClears',100),false);
const blocked=makeGame(html,3,{localStorage:{getItem(){return null},setItem(){throw new Error('storage full')},removeItem(){throw new Error('storage full')}}});
assert.equal(blocked.commitNormalRunStart('wanderer',null),false,'failed persistence cannot report a started run');
assert.equal(blocked.updatePlayerSetting('largeText',true),false);assert.equal(blocked.getPlayerSettings().largeText,true,'settings still apply to the current session if persistence fails');
const partialStore=new Map(),archiveBlocked=makeGame(html,4,{localStorage:{getItem:k=>partialStore.get(k)||null,setItem(k,v){if(k===HISTORY)throw new Error('archive full');partialStore.set(k,String(v))},removeItem:k=>partialStore.delete(k)}});
assert.ok(archiveBlocked.saveRoguelikeRunDraft(normalCompleted),'archive failure never rolls back a completed run');
assert.equal(archiveBlocked.loadRoguelikeRunDraft().status,'completed');assert.equal(partialStore.has(HISTORY),false);
store.set('rummyDuelDeveloperV1','1');
const reloaded=makeGame(html,5,{storage:store});assert.equal(reloaded.developerModeActive(),false,'reloading always starts in ordinary mode');
assert.equal(reloaded.getProgress().selectedTheme,'mixed');assert.equal(reloaded.getProgress().totalClears,1);

const menu=html.match(/<nav class="startMenu"[\s\S]*?<\/nav>/)[0];
assert.deepEqual([...menu.matchAll(/<button id="([^"]+)"/g)].map(m=>m[1]),['battleStartBtn','roguelikeStartBtn','tutorialStartBtn','startCodexBtn','settingsBtn']);
assert.doesNotMatch(menu,/developer|practice|advanced|region|resetProgress/);
assert.ok(html.indexOf('id="developerBtn"')>html.indexOf('id="settingsOverlay"'));
assert.ok(html.indexOf('id="roguelikeRewardPreviewBtn"')>html.indexOf('id="developerWorkspace"'));
console.log('UX2 menu, full-run progression, DEV storage isolation and settings regression passed.');

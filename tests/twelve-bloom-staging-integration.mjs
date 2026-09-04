import assert from 'node:assert/strict';
import {makeGame,html} from './helpers/live-game.mjs';

const normal=makeGame(html,41);
const tbIds=Object.keys(normal.NAMED).filter(id=>normal.NAMED[id]?.themeId==='twelve-bloom');
assert.equal(tbIds.length,24,'TWELVE-BLOOM staging pool stays 24 cards');
assert.equal(normal.THEME_GROUPS['twelve-bloom'].live,false,'theme registry remains explicitly non-live');
assert.equal(normal.THEME_BUILD_PROFILES['twelve-bloom'].live,false,'build profile is staged, not live');
assert.equal(normal.themeBuildUnlocked('twelve-bloom'),false,'normal mode cannot select the staged build');
assert.equal(normal.themeTutorialAvailable('twelve-bloom'),false,'normal mode cannot enter the staged tutorial');
const normalOpen=normal.baseUnlockedNamed();
assert.equal(tbIds.filter(id=>normalOpen.has(id)).length,0,'normal unlock pool contains zero TWELVE-BLOOM cards');
for(const id of tbIds){
 assert.deepEqual([...normal.unlockLabelsForNamed(id)],['미정'],id+' has no live unlock group');
 assert.equal(normal.stagingUnlockLabelsForNamed(id).length,1,id+' has exactly one staging unlock tier');
 assert.ok(Array.isArray(normal.TENDENCY_BY_TAG[normal.NAMED[id].t])&&normal.TENDENCY_BY_TAG[normal.NAMED[id].t].length,id+' has AI/reward tendency metadata');
 assert.ok(normal.roguelikeNamedActionTags(id).length,id+' exposes shared roguelike action tags');
}
const staged=normal.TWELVE_BLOOM_STAGING_UNLOCKS.flatMap(g=>[...g.items]);
assert.equal(normal.TWELVE_BLOOM_STAGING_UNLOCKS.length,6,'staging unlock plan has six tiers');
assert.equal(staged.length,24,'staging unlock tiers contain 24 entries');
assert.equal(new Set(staged).size,24,'staging unlock tiers contain every physical card once');
assert.deepEqual(new Set(staged),new Set(tbIds),'staging unlock plan covers the exact TWELVE-BLOOM pool');
assert.ok(html.includes('data-codex-filter="theme:twelve-bloom"'),'DEV codex has a TWELVE-BLOOM filter tab');
assert.ok(html.includes("THEME_BUILD_PROFILES[NAMED[id].themeId]?.live!==false"),'normal codex filters staged live:false theme cards');

const dev=makeGame(html,42,{developer:true});
assert.equal(dev.themeBuildUnlocked('twelve-bloom'),true,'DEV may select the staged build profile');
assert.equal(dev.themeTutorialAvailable('twelve-bloom'),true,'DEV may enter the staged theme tutorial');
const devOpen=[...dev.unlockedNamed()].filter(id=>id[0]!=='J'&&dev.NAMED[id]);
const chosen=dev.chooseNamedForBuild(devOpen,'wanderer','twelve-bloom');
assert.equal(chosen.length,9,'automatic build still selects the standard nine named variants');
assert.equal(chosen.filter(id=>dev.NAMED[id]?.themeId==='twelve-bloom').length,4,'staged auto-build obeys the shared four-card theme cap');

const slots=[...new Set(tbIds.map(id=>dev.namedSlot(id)))];
const reward=dev.roguelikeRewardCandidates({slots,variants:{},poolIds:tbIds,seed:'tb-staging',starterId:'wanderer'});
assert.equal(reward.poolSize,24,'DEV reward pool can ingest all staged TWELVE-BLOOM variants');
assert.equal(reward.picks.length,3,'shared roguelike reward roles produce three staged candidates');
assert.ok(reward.picks.every(p=>p.themeId==='twelve-bloom'),'staged reward picks stay inside the supplied theme pool');
assert.ok(reward.picks.every(p=>p.entryStatus==='entry'||p.entryStatus==='payoff'),'TWELVE-BLOOM rewards are classified instead of unknown');
for(const tag of dev.ROGUELIKE_THEME_ENTRY_TAGS['twelve-bloom'])assert.ok(tbIds.some(id=>dev.NAMED[id].t===tag),'every TWELVE-BLOOM entry tag maps to a real card');

dev.replaceProgress({...dev.getProgress(),tutorialCompleted:true,selectedTheme:'twelve-bloom'});
assert.equal(dev.startThemeTutorial('twelve-bloom'),true,'DEV starts the staged TWELVE-BLOOM tutorial');
assert.equal(dev.state.tutorialStep,'tbSeasonMatch','staged tutorial enters the season-match scenario');
assert.equal(dev.state.player.melds.length,2,'season tutorial starts with two legal public melds');
const springRun=dev.state.player.hand.filter(c=>c.tutorialRole==='tbSpringRun');
assert.equal(springRun.length,3,'season tutorial supplies the 2-3-4 run');
const beforeHand=dev.state.player.hand.length;
assert.equal(dev.submitNewMeld('player',springRun),true,'tutorial action creates the legal 2-3-4 run');
assert.equal(dev.state.tutorialSegmentDone,true,'real onBloomMatchChange completes the staged tutorial');
assert.ok(dev.state.tutorialSuccessText.includes('봄맞춤 1·2·3'),'tutorial success confirms the real spring match');
assert.ok(dev.state.player.hand.length>=beforeHand-2,'계절 표본 draw resolves through the live match event');

console.log('TWELVE-BLOOM pre-live integration regression passed.');

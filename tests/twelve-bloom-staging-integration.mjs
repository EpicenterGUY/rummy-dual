import assert from 'node:assert/strict';
import {makeGame,html} from './helpers/live-game.mjs';

const normal=makeGame(html,41);
const tbIds=Object.keys(normal.NAMED).filter(id=>normal.NAMED[id]?.themeId==='twelve-bloom');
assert.equal(tbIds.length,24,'TWELVE-BLOOM live pool stays 24 cards');
assert.equal(normal.THEME_GROUPS['twelve-bloom'].live,true,'theme registry is live');
assert.equal(normal.THEME_BUILD_PROFILES['twelve-bloom'].live,true,'build profile is live');
assert.equal(normal.THEME_TUTORIALS['twelve-bloom'].live,true,'theme tutorial is live');
assert.equal(normal.themeTutorialAvailable('twelve-bloom'),true,'live theme tutorial is registered');

normal.replaceProgress({...normal.getProgress(),totalClears:0});
assert.equal(tbIds.filter(id=>normal.baseUnlockedNamed(normal.getProgress()).has(id)).length,0,'fresh progress starts with zero TWELVE-BLOOM cards');
assert.equal(normal.themeBuildUnlocked('twelve-bloom'),false,'theme build waits for the first live unlock tier');

const schedule=normal.TWELVE_BLOOM_STAGING_UNLOCKS;
assert.equal(schedule.length,6,'compatibility unlock schedule keeps six tiers');
const scheduled=schedule.flatMap(g=>[...g.items]);
assert.equal(scheduled.length,24,'compatibility schedule contains all 24 cards');
assert.equal(new Set(scheduled).size,24,'compatibility schedule has no duplicate cards');
assert.deepEqual(new Set(scheduled),new Set(tbIds),'compatibility schedule mirrors the live pool');

for(let tier=1;tier<=6;tier++){
 normal.replaceProgress({...normal.getProgress(),totalClears:tier});
 const open=normal.baseUnlockedNamed(normal.getProgress());
 const liveTb=tbIds.filter(id=>open.has(id));
 assert.equal(liveTb.length,tier*4,`clear tier ${tier} exposes exactly ${tier*4} TWELVE-BLOOM cards`);
 for(const id of schedule[tier-1].items)assert.deepEqual([...normal.unlockLabelsForNamed(id)],[`전체 ${tier}클리어 · TWELVE-BLOOM`],id+' uses the normal live unlock label');
}
assert.equal(normal.themeBuildUnlocked('twelve-bloom'),true,'theme build opens after live cards are unlocked');
const normalOpen=[...normal.unlockedNamed()].filter(id=>id[0]!=='J'&&normal.NAMED[id]);
const chosen=normal.chooseNamedForBuild(normalOpen,'wanderer','twelve-bloom');
assert.equal(chosen.length,9,'live automatic build keeps the standard nine named variants');
assert.equal(chosen.filter(id=>normal.NAMED[id]?.themeId==='twelve-bloom').length,4,'live automatic build obeys the shared four-card theme cap');

const openTb=tbIds.filter(id=>normal.baseUnlockedNamed(normal.getProgress()).has(id));
assert.equal(openTb.length,24,'all 24 live cards are in the ordinary unlocked pool by six clears');
const slots=[...new Set(openTb.map(id=>normal.namedSlot(id)))];
const reward=normal.roguelikeRewardCandidates({slots,variants:{},poolIds:openTb,seed:'tb-live',starterId:'wanderer'});
assert.equal(reward.poolSize,24,'ordinary unlocked TWELVE-BLOOM cards are accepted by the shared reward pool');
assert.equal(reward.picks.length,3,'shared roguelike reward roles produce three live candidates');
assert.ok(reward.picks.every(p=>p.themeId==='twelve-bloom'),'live reward picks stay inside the supplied TWELVE-BLOOM pool');
assert.ok(reward.picks.every(p=>p.entryStatus==='entry'||p.entryStatus==='payoff'),'live rewards keep entry/payoff classification');
for(const tag of normal.ROGUELIKE_THEME_ENTRY_TAGS['twelve-bloom'])assert.ok(tbIds.some(id=>normal.NAMED[id].t===tag),'every TWELVE-BLOOM entry tag maps to a real card');

assert.ok(html.includes('data-codex-filter="theme:twelve-bloom"'),'normal codex keeps the TWELVE-BLOOM filter tab');
assert.ok(html.includes("THEME_BUILD_PROFILES[NAMED[id].themeId]?.live!==false"),'codex uses the shared live-theme visibility gate');

normal.replaceProgress({...normal.getProgress(),totalClears:1,tutorialCompleted:true,selectedTheme:'twelve-bloom'});
assert.equal(normal.startThemeTutorial('twelve-bloom'),true,'normal mode starts the live TWELVE-BLOOM tutorial');
assert.equal(normal.state.tutorialStep,'tbSeasonMatch','live tutorial enters the season-match scenario');
assert.equal(normal.state.player.melds.length,2,'season tutorial starts with two legal public melds');
const springRun=normal.state.player.hand.filter(c=>c.tutorialRole==='tbSpringRun');
assert.equal(springRun.length,3,'season tutorial supplies the 2-3-4 run');
const beforeHand=normal.state.player.hand.length;
assert.equal(normal.submitNewMeld('player',springRun),true,'tutorial action creates the legal 2-3-4 run');
assert.equal(normal.state.tutorialSegmentDone,true,'real onBloomMatchChange completes the live tutorial');
assert.ok(normal.state.tutorialSuccessText.includes('봄맞춤 1·2·3'),'tutorial success confirms the real spring match');
assert.ok(normal.state.player.hand.length>=beforeHand-2,'계절 표본 draw resolves through the live match event');

console.log('TWELVE-BLOOM live integration regression passed.');

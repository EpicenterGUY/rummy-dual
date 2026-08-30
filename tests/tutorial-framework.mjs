import fs from 'node:fs';

const html = fs.readFileSync(new URL('../index.html', import.meta.url), 'utf8');
const script = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).join('\n');

function ok(condition, message) {
  if (!condition) throw new Error(message);
  console.log(`PASS: ${message}`);
}

new Function(script);

ok(html.includes('id="firstRunPrompt"'), 'first-run tutorial prompt exists');
ok(html.includes('id="firstRunTutorialBtn"') && html.includes('id="firstRunBattleBtn"'), 'first-run prompt offers tutorial or direct battle');
ok(/id="tutorialStartBtn"[^>]*type="button"(?![^>]*disabled)/.test(html), 'tutorial menu entry is enabled for the onboarding beta');
ok(html.includes('id="tutorialCoach"'), 'tutorial coach exists in the real battle layout');
ok(html.includes('id="tutorialHintBtn"') && html.includes('id="tutorialRestartBtn"') && html.includes('id="tutorialExitBtn"'), 'coach exposes hint, restart, and exit controls');

ok(script.includes('const TUTORIAL_STEPS=Object.freeze(['), 'tutorial steps are data-driven');
for (const id of ['intro','board','basic','set','run','attachOwn','attachEnemy','switch','rummy']) {
  ok(script.includes(`id:'${id}'`), `tutorial step ${id} is registered`);
}
ok(script.includes('function currentTutorialStep()'), 'shared current-step resolver exists');
ok(script.includes('function tutorialAllows('), 'shared action gate exists');
ok(script.includes('function applyTutorialScenario('), 'shared scenario hook exists');
ok(script.includes('function tutorialCheckProgress('), 'shared progress hook exists');
ok(script.includes('function renderTutorialCoach()'), 'shared coach renderer exists');
ok(script.includes("function startTutorial(stepId='intro')"), 'tutorial entry helper exists');
ok(script.includes('function restartTutorialStep()'), 'tutorial step restart helper exists');
ok(script.includes('function exitTutorial()'), 'tutorial exit helper exists');

ok(script.includes('progress.tutorialPromptSeen=true;saveProgress()'), 'entering tutorial records that the first-run prompt was handled');
ok(script.includes("document.getElementById('firstRunBattleBtn').onclick=()=>{progress.tutorialPromptSeen=true;saveProgress();"), 'direct battle dismisses only the prompt');
ok(!/startTutorial[\s\S]{0,500}tutorialCompleted\s*=\s*true/.test(script), 'intro framework does not falsely mark the full tutorial complete');
ok(script.includes("newGame('tutorial')"), 'tutorial enters through the explicit tutorial session mode');
ok(script.includes("state.phase='tutorial'"), 'onboarding intro blocks normal battle actions until a scenario is active');
ok(html.includes('.tutorialCoach') && !html.includes('.tutorialCoach{position:fixed'), 'coach stays in document flow instead of covering cards');
ok(html.includes('@media(max-width:390px)') && html.includes('.tutorialCoachActions'), 'tutorial controls have mobile layout handling');

console.log('RUMMY//DUEL tutorial framework regressions passed.');

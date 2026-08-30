import fs from 'node:fs';

const html = fs.readFileSync(new URL('../index.html', import.meta.url), 'utf8');
const roadmap = fs.readFileSync(new URL('../ROADMAP.md', import.meta.url), 'utf8');
const script = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).join('\n');

function ok(condition, message) {
  if (!condition) throw new Error(message);
  console.log(`PASS: ${message}`);
}

new Function(script);

ok(script.includes('tutorialStepToken:0') && script.includes('tutorialExitArmed:false'), 'tutorial state tracks step revision and exit confirmation');
ok(script.includes('state.tutorialStepToken++;state.tutorialStep=id'), 'every tutorial step setup invalidates stale step callbacks');
ok(script.includes('stepToken=state.tutorialStepToken') && script.includes('state.tutorialStepToken===stepToken'), 'auto advance requires the same tutorial step revision');
ok(script.includes("function restartTutorialStep(){if(state.sessionMode!=='tutorial'||!state.tutorialStep)return false") && script.includes('단계 재시작 · 고정 상태를 처음부터 다시 구성했습니다.'), 'manual step restart rebuilds deterministic state explicitly');
ok(script.includes("if(!state.tutorialExitArmed){state.tutorialExitArmed=true") && script.includes("},2400);return false}progress.tutorialPromptSeen=true;saveProgress();showStartScreen();return true}"), 'tutorial exit requires a second confirmation tap and preserves progress state');
ok(script.includes("state.sessionMode='menu';state.tutorialStep=null;state.tutorialExitArmed=false"), 'returning to menu clears tutorial exit state and invalidates session work');
ok(script.includes("exit.textContent=state.tutorialExitArmed?'한 번 더 눌러 종료':'튜토리얼 종료'"), 'coach gives explicit Korean exit confirmation feedback');

const drawStart=script.indexOf('function playerDraw('), drawGuard=script.indexOf("if(!tutorialAllows(tutorialAction",drawStart), drawMutation=script.indexOf("c=drawOne('player'",drawStart);
ok(drawStart>=0 && drawGuard>drawStart && drawMutation>drawGuard, 'tutorial draw rejection occurs before draw mutation');
const meldStart=script.indexOf('function playerMeld('), meldGuard=script.indexOf("if(!tutorialAllows('meld'",meldStart), meldMutation=script.indexOf("submitNewMeld('player'",meldStart);
ok(meldStart>=0 && meldGuard>meldStart && meldMutation>meldGuard, 'tutorial meld rejection occurs before meld mutation');
const attachStart=script.indexOf('function playerAttach(){'), attachGuard=script.indexOf("if(!tutorialAllows('attach'",attachStart), attachMutation=script.indexOf("attachCards('player'",attachStart);
ok(attachStart>=0 && attachGuard>attachStart && attachMutation>attachGuard, 'tutorial attach rejection occurs before attach mutation');
const discardStart=script.indexOf('function playerDiscard('), discardGuard=script.indexOf("if(!tutorialAllows('discard'",discardStart), discardMutation=script.indexOf("removeFromHand('player'",discardStart);
ok(discardStart>=0 && discardGuard>discardStart && discardMutation>discardGuard, 'tutorial discard rejection occurs before hand mutation');
ok(roadmap.includes('- [x] 튜토리얼 종료 / 재시작 처리') && roadmap.includes('- [x] 행동 성공 시 자동 진행'), 'UX1 P2 roadmap records stable exit/restart and wrong-action handling');

console.log('RUMMY//DUEL tutorial flow safety regressions passed.');

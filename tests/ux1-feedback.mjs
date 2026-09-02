import fs from 'node:fs';

const html = fs.readFileSync(new URL('../index.html', import.meta.url), 'utf8');
const roadmap = fs.readFileSync(new URL('../ROADMAP.md', import.meta.url), 'utf8');
const script = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).join('\n');

function ok(condition, message) {
  if (!condition) throw new Error(message);
  console.log(`PASS: ${message}`);
}

new Function(script);

ok(script.includes('function animateSwitchMove(from,target,power=state.switchPower') && script.includes("switchAnchorElement('neutral')") === false, 'switch movement uses board anchors without inventing a neutral side element');
ok(script.includes("function setSwitchTarget(target,reason='반환'){const from=state.switchTarget") && script.includes("typeof animateSwitchMove==='function'") && script.includes('animateSwitchMove(from,target,state.switchPower,reason)'), 'switch return captures the previous owner and animates to the new target');
ok(script.includes("const oldTarget=state.switchTarget;if(oldTarget!=='neutral'&&typeof animateSwitchMove==='function')animateSwitchMove(oldTarget,'neutral',0,reason)"), 'bomb-cycle reset visibly returns the switch to neutral');
ok(html.includes('.switchFlight{position:fixed') && html.includes('.initiativeSide.switchCatch') && html.includes('@keyframes switchBoardKick'), 'switch flight and catch feedback styles exist');
ok(script.includes('function animateRummyFeedback(w,reload)') && script.includes('combatBanner(`러미 · ${reload}장 리필`') && script.includes("zone.querySelectorAll(w==='player'?'.cardBtn':'.cardBack')"), 'RUMMY feedback announces reload and animates the refreshed hand');
ok(html.includes('.handZone.rummyFlash,.enemyZone.rummyFlash') && html.includes('.cardBtn.rummyDeal,.cardBack.rummyDeal'), 'RUMMY zone flash and staggered deal-in styles exist for both sides');
ok(script.includes("typeof animateRummyFeedback==='function'") && script.includes("else combatBanner('러미!','rummy',40)"), 'triggerRummy uses the richer feedback hook with a non-visual isolation fallback');
ok(script.includes('function pulseTutorialSuccess()') && script.includes("renderTutorialCoach();if(typeof pulseTutorialSuccess==='function')pulseTutorialSuccess();const battleId=state.battleId") && script.includes('},850);return true}'), 'tutorial success visibly pulses before the guarded 850ms auto-advance');
ok(html.includes('.tutorialCoach.tutorialSuccessPulse') && html.includes('@keyframes tutorialSuccessPulse'), 'tutorial coach has a dedicated success transition animation');
ok(script.includes("playerSettings.reducedMotion)||matchMedia('(prefers-reduced-motion: reduce)').matches") && html.includes('@media (prefers-reduced-motion:reduce)'), 'new feedback respects reduced-motion preferences');
ok(roadmap.includes('- [x] 세부 애니메이션 / 스위치 이동 / 러미 피드백 보강'), 'UX1 P2 roadmap marks detailed feedback polish complete');

console.log('RUMMY//DUEL UX1 feedback regressions passed.');

import fs from 'node:fs';

const html = fs.readFileSync(new URL('../index.html', import.meta.url), 'utf8');
const script = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).join('\n');

function ok(condition, message) {
  if (!condition) throw new Error(message);
  console.log(`PASS: ${message}`);
}

new Function(script);

ok(html.includes('id="startScreen"'), 'dedicated start screen shell exists');
ok(html.includes('세트와 런으로 폭탄을 키워 스위치를 넘기는 1:1 러미 배틀'), 'start screen uses the locked Korean one-line pitch');
ok(html.includes('id="battleStartBtn"'), 'start screen exposes battle start');
ok(html.includes('id="tutorialStartBtn"') && html.includes('기본 조작부터 폭발·러미까지 고정 패로 직접 익힙니다.') && !html.includes('고정 패 실습은 순차 추가 중입니다.'), 'tutorial entry advertises the completed core hands-on flow');
ok(html.includes('id="startCodexBtn"'), 'start screen reuses the card codex entry');
ok(html.includes('id="settingsBtn"') && html.includes('id="reducedMotionInput"'), 'settings entry provides real display preferences');
ok(html.includes('id="setupNextBtn"') && html.includes('id="startRulesBtn"'), 'character setup and tutorial rules remain available through focused submenus');
ok(html.includes('id="homeBtn"'), 'battle HUD can return to the start screen');
ok(html.includes('id="resultHomeBtn"'), 'result screen can return to the start screen');
ok(html.includes('<span class="menuState">시작</span>') && html.includes('<span class="menuState">열기</span>'), 'active start-menu states are Korean');

ok(script.includes("sessionMode:'menu'"), 'global state starts in menu session mode');
ok(script.includes('battleId:0'), 'global state tracks a monotonic battle session id');
ok(script.includes('state.battleId++'), 'each new battle invalidates delayed work from older battles');
ok(script.includes("isLiveCombatSession()&&state.battleId===battleId"), 'delayed battle callbacks are guarded by mode and battle id');
ok(script.includes('tutorialPromptSeen:false') && script.includes('tutorialCompleted:false'), 'progress schema carries tutorial flags');
ok(script.includes("tutorialPromptSeen:typeof x.tutorialPromptSeen==='boolean'?x.tutorialPromptSeen:false"), 'legacy progress normalizes missing tutorial prompt flag');
ok(script.includes("tutorialCompleted:typeof x.tutorialCompleted==='boolean'?x.tutorialCompleted:false"), 'legacy progress normalizes missing tutorial completion flag');
ok(script.includes("function showStartScreen()"), 'shared menu routing helper exists');
ok(script.includes("function startBattle()"), 'battle entry is routed through an explicit helper');
ok(script.includes("newGame('battle')"), 'battle entry switches session mode');
ok(!script.includes('renderProgress();newGame();'), 'page load no longer jumps directly into a random battle');
ok(script.includes('renderProgress();showStartScreen();'), 'page load lands on the start screen');

ok(html.includes('.startMenuBtn'), 'start menu has dedicated touch-target styling');
ok(html.includes('@media(max-width:390px)') && html.includes('.startScreen'), 'start screen has mobile-specific layout rules');

console.log('RUMMY//DUEL start-screen regressions passed.');

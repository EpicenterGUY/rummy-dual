from pathlib import Path

root=Path('.')
idx=root/'index.html'
s=idx.read_text()

def one(old,new,label):
    global s
    n=s.count(old)
    if n!=1:
        raise SystemExit(f'{label}: expected 1 match, got {n}')
    s=s.replace(old,new)

one("const state={sessionMode:'menu',battleId:0,tutorialStep:null,tutorialHintOpen:false,tutorialSegmentDone:false,tutorialSuccessText:'',player:null,enemy:null,discard:[],field:null,phase:'mulligan',turn:'player',turnNo:1,turnToken:0,selected:new Set(),selectionOrder:[],boardSelected:new Set(),target:null,logs:[],rummy:0,lastDamageTaken:0,lastEnemyUsedDiscard:false,lastPlayerUsedDiscard:false,lastEnemyDiscardRank:null,lastPlayerDiscardRank:null,lastPlayerMeldType:null,lastEnemyMeldType:null,lastPlayerReturnType:null,lastEnemyReturnType:null,switchTarget:'neutral',switchPower:0,lastSwitchAdd:0,lastSwitchActor:null,fuseUsed:false,gameOver:false,rewarded:false};",
    "const state={sessionMode:'menu',battleId:0,tutorialStep:null,tutorialStepToken:0,tutorialExitArmed:false,tutorialHintOpen:false,tutorialSegmentDone:false,tutorialSuccessText:'',player:null,enemy:null,discard:[],field:null,phase:'mulligan',turn:'player',turnNo:1,turnToken:0,selected:new Set(),selectionOrder:[],boardSelected:new Set(),target:null,logs:[],rummy:0,lastDamageTaken:0,lastEnemyUsedDiscard:false,lastPlayerUsedDiscard:false,lastEnemyDiscardRank:null,lastPlayerDiscardRank:null,lastPlayerMeldType:null,lastEnemyMeldType:null,lastPlayerReturnType:null,lastEnemyReturnType:null,switchTarget:'neutral',switchPower:0,lastSwitchAdd:0,lastSwitchActor:null,fuseUsed:false,gameOver:false,rewarded:false};",
    'tutorial flow state')

one("function showStartScreen(){state.battleId++;state.sessionMode='menu';state.tutorialStep=null;state.tutorialHintOpen=false;hideTutorialCoach();",
    "function showStartScreen(){state.battleId++;state.sessionMode='menu';state.tutorialStep=null;state.tutorialExitArmed=false;state.tutorialHintOpen=false;hideTutorialCoach();",
    'menu clears exit confirmation')

one("function tutorialReject(action){if(state.sessionMode!=='tutorial')return false;state.tutorialHintOpen=true;renderTutorialCoach();log(`튜토리얼 목표와 다른 행동입니다. 안내된 ${currentTutorialStep()?.title||'실습'} 행동을 먼저 해보세요.`,'hit');return true}",
    "function tutorialReject(action){if(state.sessionMode!=='tutorial')return false;state.tutorialExitArmed=false;state.tutorialHintOpen=true;renderTutorialCoach();log(`튜토리얼 목표와 다른 행동입니다. 안내된 ${currentTutorialStep()?.title||'실습'} 행동을 먼저 해보세요.`,'hit');return true}",
    'wrong action disarms exit')

old_render="function renderTutorialCoach(){const coach=document.getElementById('tutorialCoach'),step=currentTutorialStep();if(!coach)return;if(state.sessionMode!=='tutorial'||!step){coach.hidden=true;return}coach.hidden=false;document.getElementById('tutorialStepBadge').textContent=`튜토리얼 ${Math.max(1,tutorialStepIndex()+1)} / ${TUTORIAL_STEPS.length}`;document.getElementById('tutorialCoachTitle').textContent=state.tutorialSegmentDone?`${step.title} · 성공`:step.title;document.getElementById('tutorialCoachGoal').textContent=state.tutorialSuccessText||step.goal;const hint=document.getElementById('tutorialCoachHint');hint.textContent=state.tutorialSegmentDone?(step.id==='rummy'?'기본 튜토리얼 완료! 자유 연습전으로 이어가거나 메인으로 돌아갈 수 있습니다.':'다음 실습은 러미입니다.'):step.hint||'';hint.hidden=state.tutorialSegmentDone?false:!state.tutorialHintOpen;const next=document.getElementById('tutorialNextBtn'),practice=document.getElementById('tutorialPracticeBtn');if(practice)practice.hidden=!(state.tutorialSegmentDone&&step.id==='rummy');if(state.tutorialSegmentDone){next.hidden=false;next.disabled=step.id!=='rummy';next.textContent=step.id==='rummy'?'튜토리얼 완료 · 메인으로':'다음 실습 준비 중'}else{next.hidden=!step.manualNext;next.disabled=false;next.textContent=step.id==='intro'?'화면 보기':step.id==='board'?'실습 시작':'다음'}}"
new_render="function renderTutorialCoach(){const coach=document.getElementById('tutorialCoach'),step=currentTutorialStep();if(!coach)return;if(state.sessionMode!=='tutorial'||!step){coach.hidden=true;return}coach.hidden=false;document.getElementById('tutorialStepBadge').textContent=`튜토리얼 ${Math.max(1,tutorialStepIndex()+1)} / ${TUTORIAL_STEPS.length}`;document.getElementById('tutorialCoachTitle').textContent=state.tutorialSegmentDone?`${step.title} · 성공`:step.title;document.getElementById('tutorialCoachGoal').textContent=state.tutorialSuccessText||step.goal;const hint=document.getElementById('tutorialCoachHint'),exit=document.getElementById('tutorialExitBtn');if(state.tutorialExitArmed){hint.textContent='현재 단계는 처음 상태로 되돌아갑니다. 완료한 튜토리얼 기록은 유지됩니다. 종료 버튼을 한 번 더 누르면 메인으로 돌아갑니다.';hint.hidden=false}else{hint.textContent=state.tutorialSegmentDone?(step.id==='rummy'?'기본 튜토리얼 완료! 자유 연습전으로 이어가거나 메인으로 돌아갈 수 있습니다.':'다음 실습은 잠시 후 자동으로 시작됩니다.'):step.hint||'';hint.hidden=state.tutorialSegmentDone?false:!state.tutorialHintOpen}if(exit){exit.textContent=state.tutorialExitArmed?'한 번 더 눌러 종료':'튜토리얼 종료';exit.classList.toggle('armed',!!state.tutorialExitArmed)}const next=document.getElementById('tutorialNextBtn'),practice=document.getElementById('tutorialPracticeBtn');if(practice)practice.hidden=!(state.tutorialSegmentDone&&step.id==='rummy');if(state.tutorialSegmentDone){next.hidden=false;next.disabled=step.id!=='rummy';next.textContent=step.id==='rummy'?'튜토리얼 완료 · 메인으로':'자동 진행 중'}else{next.hidden=!step.manualNext;next.disabled=false;next.textContent=step.id==='intro'?'화면 보기':step.id==='board'?'실습 시작':'다음'}}"
one(old_render,new_render,'tutorial coach exit/auto copy')

one("function setTutorialStep(id){const step=TUTORIAL_STEPS.find(x=>x.id===id);if(!step)return false;state.tutorialStep=id;state.tutorialHintOpen=false;state.tutorialSegmentDone=false;state.tutorialSuccessText='';applyTutorialScenario(step);render();renderTutorialCoach();return true}",
    "function setTutorialStep(id){const step=TUTORIAL_STEPS.find(x=>x.id===id);if(!step)return false;state.tutorialStepToken++;state.tutorialStep=id;state.tutorialExitArmed=false;state.tutorialHintOpen=false;state.tutorialSegmentDone=false;state.tutorialSuccessText='';applyTutorialScenario(step);render();renderTutorialCoach();return true}",
    'step token invalidates stale auto advance')

old_auto="const battleId=state.battleId,stepId=step.id;setTimeout(()=>{if(state.sessionMode==='tutorial'&&state.battleId===battleId&&state.tutorialStep===stepId)setTutorialStep(next.id)},650);"
new_auto="const battleId=state.battleId,stepId=step.id,stepToken=state.tutorialStepToken;setTimeout(()=>{if(state.sessionMode==='tutorial'&&state.battleId===battleId&&state.tutorialStep===stepId&&state.tutorialStepToken===stepToken)setTutorialStep(next.id)},650);"
one(old_auto,new_auto,'token guarded auto advance')

one("function restartTutorialStep(){if(state.sessionMode==='tutorial'&&state.tutorialStep)setTutorialStep(state.tutorialStep)}\nfunction exitTutorial(){showStartScreen()}",
    "function restartTutorialStep(){if(state.sessionMode!=='tutorial'||!state.tutorialStep)return false;const id=state.tutorialStep,title=currentTutorialStep()?.title||'현재';const ok=setTutorialStep(id);if(ok){state.tutorialHintOpen=true;log(`튜토리얼 ${title} 단계 재시작 · 고정 상태를 처음부터 다시 구성했습니다.`,'important');render();renderTutorialCoach()}return ok}\nfunction exitTutorial(){if(state.sessionMode!=='tutorial'){showStartScreen();return true}if(!state.tutorialExitArmed){state.tutorialExitArmed=true;state.tutorialHintOpen=true;const battleId=state.battleId,stepToken=state.tutorialStepToken;renderTutorialCoach();setTimeout(()=>{if(state.sessionMode==='tutorial'&&state.battleId===battleId&&state.tutorialStepToken===stepToken&&state.tutorialExitArmed){state.tutorialExitArmed=false;renderTutorialCoach()}},2400);return false}progress.tutorialPromptSeen=true;saveProgress();showStartScreen();return true}",
    'restart and safe exit flow')

one("document.getElementById('tutorialHintBtn').onclick=()=>{state.tutorialHintOpen=!state.tutorialHintOpen;renderTutorialCoach()};",
    "document.getElementById('tutorialHintBtn').onclick=()=>{state.tutorialExitArmed=false;state.tutorialHintOpen=!state.tutorialHintOpen;renderTutorialCoach()};",
    'hint disarms exit')

css_marker="@media(max-width:390px){.tutorialTarget{outline-width:2px!important;outline-offset:1px!important}}\n\n</style>"
css_add="""@media(max-width:390px){.tutorialTarget{outline-width:2px!important;outline-offset:1px!important}}

/* UX1 P2 · tutorial mobile flow safety */
.tutorialCoachGoal,.tutorialCoachHint{overflow-wrap:anywhere;word-break:keep-all}.tutorialCoachActions .pixelBtn{min-height:38px;white-space:normal;line-height:1.25}.tutorialCoachActions .redBtn.armed{border-color:#9b6865;background:#553535}.startAux .pixelBtn{min-height:38px}
@media(max-width:390px){.tutorialCoach{padding:8px}.tutorialCoachHead{align-items:flex-start}.tutorialCoachHead b{min-width:0;overflow-wrap:anywhere}.tutorialCoachActions{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:6px}.tutorialCoachActions .pixelBtn{min-width:0;min-height:42px;padding:7px 6px;overflow-wrap:anywhere}.tutorialCoachGoal,.tutorialCoachHint{font-size:8px;line-height:1.55}.startAux .pixelBtn{min-height:40px}}
@media(max-width:370px){.tutorialCoachActions{grid-template-columns:1fr}.tutorialCoachActions .pixelBtn{min-height:42px}.tutorialCoachHead{flex-wrap:wrap}.tutorialCoachHead b{flex:1 1 180px}}

</style>"""
one(css_marker,css_add,'tutorial mobile css')

idx.write_text(s)

road=root/'ROADMAP.md'
r=road.read_text()
repls={
"- [ ] 튜토리얼 종료 / 재시작 처리":"- [x] 튜토리얼 종료 / 재시작 처리 — 단계 토큰으로 성공 직후 자동 진행과 수동 재시작 레이스를 차단하고, 종료는 2회 확인 후 메인으로 복귀. 완료 기록은 유지",
"- [ ] 행동 성공 시 자동 진행, 잘못된 행동은 상태를 망가뜨리지 않고 힌트 제공":"- [x] 행동 성공 시 자동 진행, 잘못된 행동은 상태를 망가뜨리지 않고 힌트 제공 — 실제 mutation 전에 `tutorialAllows`로 차단하며 자동 진행은 battle/step token으로 stale callback 방지",
"- [ ] 모바일 가독성 및 터치 테스트":"- [x] 모바일 가독성 및 터치 정적 회귀 — 480px 앱 상한, 390px 2열 / 370px 1열 튜토리얼 액션, 최소 42px 터치 높이와 긴 한국어 줄바꿈 계약 추가",
"- [ ] 390px 이하 한국어 버튼/가이드 잘림 회귀 테스트":"- [x] 390px 이하 한국어 버튼/가이드 잘림 회귀 테스트 — coach 목표/힌트 `overflow-wrap`, 버튼 `white-space:normal`, 370px 단일 열 fallback 검사"
}
for old,new in repls.items():
    if r.count(old)!=1: raise SystemExit(f'roadmap matcher failed: {old}')
    r=r.replace(old,new)
road.write_text(r)

# Update the older tutorial regression to the stronger step-token contract.
test=root/'tests/tutorial-basic-set-run.mjs'
t=test.read_text()
old="ok(script.includes(\"setTimeout(()=>{if(state.sessionMode==='tutorial'&&state.battleId===battleId&&state.tutorialStep===stepId)setTutorialStep(next.id)},650)\"), 'successful lessons auto-advance with stale-session protection');"
new="ok(script.includes(\"stepToken=state.tutorialStepToken\") && script.includes(\"state.tutorialStepToken===stepToken\"), 'successful lessons auto-advance with stale-session and stale-step protection');"
if t.count(old)!=1: raise SystemExit('tutorial-basic-set-run matcher failed')
test.write_text(t.replace(old,new))

flow_test=r'''import fs from 'node:fs';

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
'''
(root/'tests/tutorial-flow-safety.mjs').write_text(flow_test)

mobile_test=r'''import fs from 'node:fs';

const html = fs.readFileSync(new URL('../index.html', import.meta.url), 'utf8');
const roadmap = fs.readFileSync(new URL('../ROADMAP.md', import.meta.url), 'utf8');

function ok(condition, message) {
  if (!condition) throw new Error(message);
  console.log(`PASS: ${message}`);
}

ok(html.includes('width:min(100vw,480px)') && html.includes('viewport-fit=cover'), 'mobile shell is bounded at 480px and respects safe-area viewport fitting');
ok(html.includes('button,.cardBtn,.pileVisual,.attachHereBtn,.meldMiniCard{touch-action:manipulation}'), 'primary battle and tutorial interactive surfaces use manipulation touch behavior');
ok(html.includes('/* UX1 P2 · tutorial mobile flow safety */'), 'dedicated onboarding mobile fallback block exists');
ok(/@media\(max-width:390px\)\{\.tutorialCoach\{padding:8px\}[\s\S]*?\.tutorialCoachActions\{display:grid;grid-template-columns:minmax\(0,1fr\) minmax\(0,1fr\);gap:6px\}/.test(html), '390px tutorial actions use a bounded two-column grid');
ok(/@media\(max-width:370px\)\{\.tutorialCoachActions\{grid-template-columns:1fr\}/.test(html), '370px tutorial actions fall back to one column');
ok(html.includes('.tutorialCoachActions .pixelBtn{min-width:0;min-height:42px') && html.includes('.startAux .pixelBtn{min-height:40px}'), 'small-screen onboarding buttons preserve practical touch heights');
ok(html.includes('.tutorialCoachGoal,.tutorialCoachHint{overflow-wrap:anywhere;word-break:keep-all}') && html.includes('white-space:normal') && html.includes('overflow-wrap:anywhere'), 'long Korean coach/button copy can wrap instead of clipping');
ok(roadmap.includes('- [x] 모바일 가독성 및 터치 정적 회귀') && roadmap.includes('- [x] 390px 이하 한국어 버튼/가이드 잘림 회귀 테스트'), 'UX1 P2 roadmap records automated mobile text/touch coverage');

console.log('RUMMY//DUEL onboarding mobile regressions passed.');
'''
(root/'tests/tutorial-mobile.mjs').write_text(mobile_test)

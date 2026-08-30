from pathlib import Path

root = Path(__file__).resolve().parents[1]
index_path = root / 'index.html'
roadmap_path = root / 'ROADMAP.md'
html = index_path.read_text(encoding='utf-8')
roadmap = roadmap_path.read_text(encoding='utf-8')

def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    return text.replace(old, new, 1)

# 1) Turn the first three hands-on lessons into deterministic real-engine scenarios.
html = replace_once(html,
" {id:'basic',title:'기본 조작',goal:'카드 획득·선택·버리기를 실제 고정 상태로 연습합니다.',hint:'고정 실습 준비 중',implemented:false},\n {id:'set',title:'세트',goal:'같은 값의 서로 다른 무늬 3장으로 세트를 만듭니다.',hint:'3♠ · 3♥ · 3♦ 고정 손패 예정',implemented:false},\n {id:'run',title:'런',goal:'같은 무늬의 연속 카드 3장으로 런을 만듭니다.',hint:'4♣ · 5♣ · 6♣ 고정 손패 예정',implemented:false},",
" {id:'basic',title:'기본 조작',goal:'덱에서 지정 카드를 뽑고, 손패에서 선택한 뒤 버려 기본 행동 흐름을 익힙니다.',hint:'덱을 눌러 Q♦를 뽑은 뒤 Q♦만 선택해 버리세요.',implemented:true,scenario:'basic',allow:['drawDeck','select','discard','clear'],selectRoles:['basicDraw'],discardRole:'basicDraw',completeOn:'discard'},\n {id:'set',title:'세트',goal:'같은 값의 서로 다른 무늬 3장으로 세트를 직접 만듭니다.',hint:'강조된 3♠ · 3♥ · 3♦를 선택해 세트를 만드세요.',implemented:true,scenario:'set',allow:['select','meld','clear'],selectRoles:['setCard'],expectMeld:'SET',completeOn:'meld'},\n {id:'run',title:'런',goal:'같은 무늬의 연속 카드 3장으로 런을 직접 만듭니다.',hint:'강조된 4♣ · 5♣ · 6♣를 선택해 런을 만드세요.',implemented:true,scenario:'run',allow:['select','meld','clear'],selectRoles:['runCard'],expectMeld:'RUN',completeOn:'meld'},",
'TUTORIAL_STEPS basic/set/run')

# 2) Replace the placeholder controller with deterministic scenario setup, action constraints and auto progression.
old_controller = """function tutorialAllows(action,context={}){if(state.sessionMode!=='tutorial')return true;const step=currentTutorialStep();if(!step||!step.implemented)return false;return Array.isArray(step.allow)&&step.allow.includes(action)}
function applyTutorialScenario(step){if(!step)return false;state.phase='tutorial';state.turn='player';state.selected.clear();state.selectionOrder=[];state.boardSelected.clear();state.target=null;return true}
function renderTutorialCoach(){const coach=document.getElementById('tutorialCoach'),step=currentTutorialStep();if(!coach)return;if(state.sessionMode!=='tutorial'||!step){coach.hidden=true;return}coach.hidden=false;document.getElementById('tutorialStepBadge').textContent=`튜토리얼 ${Math.max(1,tutorialStepIndex()+1)} / ${TUTORIAL_STEPS.length}`;document.getElementById('tutorialCoachTitle').textContent=step.title;document.getElementById('tutorialCoachGoal').textContent=step.goal;const hint=document.getElementById('tutorialCoachHint');hint.textContent=step.hint||'';hint.hidden=!state.tutorialHintOpen;const next=document.getElementById('tutorialNextBtn');next.hidden=false;next.disabled=false;next.textContent=step.id==='intro'?'화면 보기':'실습 준비 상태 확인'}
function setTutorialStep(id){const step=TUTORIAL_STEPS.find(x=>x.id===id);if(!step)return false;state.tutorialStep=id;state.tutorialHintOpen=false;applyTutorialScenario(step);render();renderTutorialCoach();return true}
function startTutorial(stepId='intro'){progress.tutorialPromptSeen=true;saveProgress();hideStartScreen();document.getElementById('overlay')?.classList.remove('show');newGame();state.sessionMode='tutorial';setTutorialStep(stepId);renderStartScreen()}
function tutorialCheckProgress(event,context={}){if(state.sessionMode!=='tutorial')return false;const step=currentTutorialStep();if(!step?.completeOn||step.completeOn!==event)return false;const next=TUTORIAL_STEPS[tutorialStepIndex()+1];return next?setTutorialStep(next.id):false}
function advanceTutorial(){const step=currentTutorialStep();if(!step)return;if(step.id==='intro'){setTutorialStep('board');return}if(step.id==='board'){state.tutorialHintOpen=true;renderTutorialCoach();const hint=document.getElementById('tutorialCoachHint');hint.textContent='고정 손패 기반 기본 조작·세트·런·붙이기 실습은 다음 작업에서 이 컨트롤러에 연결됩니다.';hint.hidden=false;document.getElementById('tutorialNextBtn').hidden=true}}"""
new_controller = """function tutorialAllows(action,context={}){if(state.sessionMode!=='tutorial')return true;const step=currentTutorialStep();if(!step||!step.implemented||!Array.isArray(step.allow)||!step.allow.includes(action))return false;if(action==='select'&&step.selectRoles?.length&&!step.selectRoles.includes(context.card?.tutorialRole))return false;if(action==='discard'&&step.discardRole&&context.card?.tutorialRole!==step.discardRole)return false;if(action==='meld'&&step.expectMeld&&context.type!==step.expectMeld)return false;return true}
function tutorialReject(action){if(state.sessionMode!=='tutorial')return false;state.tutorialHintOpen=true;renderTutorialCoach();log(`튜토리얼 목표와 다른 행동입니다. 안내된 ${currentTutorialStep()?.title||'실습'} 행동을 먼저 해보세요.`,'hit');return true}
function makeTutorialCard(suit,rank,role){const c=makeCard(suit,rank,false,'player');c.tutorialRole=role;return c}
function resetTutorialSide(s){s.hp=CORE_HP;s.maxHp=CORE_HP;s.cores=CORE_COUNT;s.shield=0;s.status=blankStatus();s.lastDamageTaken=0;s.lastDetonateTaken=0;s.actedThisTurn=false;s.newMeldUsed=false;s.recoveredThisTurn=false;s.maintenanceUsed=false;s.returnedSwitchThisTurn=false;s.discardsRemaining=1;s.graceArmed=false;s.rummyReturnPending=false;s.rummyRecoveryPending=false;s.freeRecoverAfterRummy=false;s.deck=[];s.hand=[];s.spent=[];s.melds=[]}
function applyTutorialScenario(step){if(!step)return false;state.phase='tutorial';state.turn='player';state.selected.clear();state.selectionOrder=[];state.boardSelected.clear();state.target=null;state.tutorialSegmentDone=false;state.tutorialSuccessText='';if(!step.scenario)return true;const p=state.player,e=state.enemy;if(!p||!e)return false;resetTutorialSide(p);resetTutorialSide(e);state.turnNo=1;state.turnToken++;state.discard=[];state.field=null;state.logs=[];state.rummy=0;state.switchTarget='neutral';state.switchPower=0;state.lastSwitchAdd=0;state.lastSwitchActor=null;state.fuseUsed=false;state.gameOver=false;state.rewarded=false;if(step.scenario==='basic'){p.hand=[makeTutorialCard('S','2','hold')];p.deck=[makeTutorialCard('D','Q','basicDraw')];state.phase='draw';log('기본 조작 실습 · 덱에서 Q♦를 뽑아 선택한 뒤 버리세요.','important')}else if(step.scenario==='set'){p.hand=[makeTutorialCard('S','3','setCard'),makeTutorialCard('H','3','setCard'),makeTutorialCard('D','3','setCard'),makeTutorialCard('C','9','hold')];state.phase='action';log('세트 실습 · 3♠ · 3♥ · 3♦를 골라 새 세트를 만드세요.','important')}else if(step.scenario==='run'){p.hand=[makeTutorialCard('C','4','runCard'),makeTutorialCard('C','5','runCard'),makeTutorialCard('C','6','runCard'),makeTutorialCard('D','9','hold')];state.phase='action';log('런 실습 · 4♣ · 5♣ · 6♣를 골라 새 런을 만드세요.','important')}return true}
function renderTutorialCoach(){const coach=document.getElementById('tutorialCoach'),step=currentTutorialStep();if(!coach)return;if(state.sessionMode!=='tutorial'||!step){coach.hidden=true;return}coach.hidden=false;document.getElementById('tutorialStepBadge').textContent=`튜토리얼 ${Math.max(1,tutorialStepIndex()+1)} / ${TUTORIAL_STEPS.length}`;document.getElementById('tutorialCoachTitle').textContent=state.tutorialSegmentDone?`${step.title} · 성공`:step.title;document.getElementById('tutorialCoachGoal').textContent=state.tutorialSuccessText||step.goal;const hint=document.getElementById('tutorialCoachHint');hint.textContent=state.tutorialSegmentDone?'기본 조작·세트·런 1차 실습을 완료했습니다. 다음 묶음에서는 붙이기와 상대 공개 조합 이용을 이어서 배웁니다.':step.hint||'';hint.hidden=state.tutorialSegmentDone?false:!state.tutorialHintOpen;const next=document.getElementById('tutorialNextBtn');if(state.tutorialSegmentDone){next.hidden=false;next.disabled=true;next.textContent='다음 실습 준비 중'}else{next.hidden=!step.manualNext;next.disabled=false;next.textContent=step.id==='intro'?'화면 보기':step.id==='board'?'실습 시작':'다음'}}
function setTutorialStep(id){const step=TUTORIAL_STEPS.find(x=>x.id===id);if(!step)return false;state.tutorialStep=id;state.tutorialHintOpen=false;state.tutorialSegmentDone=false;state.tutorialSuccessText='';applyTutorialScenario(step);render();renderTutorialCoach();return true}
function startTutorial(stepId='intro'){progress.tutorialPromptSeen=true;saveProgress();hideStartScreen();document.getElementById('overlay')?.classList.remove('show');newGame();state.sessionMode='tutorial';setTutorialStep(stepId);renderStartScreen()}
function tutorialCheckProgress(event,context={}){if(state.sessionMode!=='tutorial')return false;const step=currentTutorialStep();if(!step?.completeOn||step.completeOn!==event)return false;if(step.expectMeld&&context.type!==step.expectMeld)return false;if(step.discardRole&&context.card?.tutorialRole!==step.discardRole)return false;const next=TUTORIAL_STEPS[tutorialStepIndex()+1];state.tutorialHintOpen=true;state.tutorialSuccessText=event==='discard'?'좋아요. 카드를 뽑고 선택해 버리는 기본 흐름을 익혔습니다.':`${step.title} 완성! 실제 조합 판정 엔진이 성공을 확인했습니다.`;log(`튜토리얼 ${step.title} 성공.`,'good');if(next?.implemented){render();renderTutorialCoach();const battleId=state.battleId,stepId=step.id;setTimeout(()=>{if(state.sessionMode==='tutorial'&&state.battleId===battleId&&state.tutorialStep===stepId)setTutorialStep(next.id)},650);return true}state.tutorialSegmentDone=true;render();renderTutorialCoach();return true}
function renderTutorialHighlights(){for(const el of document.querySelectorAll('.tutorialTarget,.tutorialLocked'))el.classList.remove('tutorialTarget','tutorialLocked');if(state.sessionMode!=='tutorial')return;const step=currentTutorialStep();if(!step?.implemented)return;if(step.id==='basic'&&state.phase==='draw')document.getElementById('deckPile')?.classList.add('tutorialTarget');for(const c of state.player.hand){const el=document.querySelector(`.cardBtn[data-uid="${c.uid}"]`);if(!el)continue;if(tutorialAllows('select',{card:c}))el.classList.add('tutorialTarget');else el.classList.add('tutorialLocked')}const cs=selectedCards(),t=cs.length===3?meldType(cs):null;if(tutorialAllows('meld',{cards:cs,type:t})&&cs.length===3)document.getElementById('meldBtn')?.classList.add('tutorialTarget');if(cs.length===1&&tutorialAllows('discard',{card:cs[0]}))document.getElementById('discardBtn')?.classList.add('tutorialTarget')}
function advanceTutorial(){const step=currentTutorialStep();if(!step)return;if(step.id==='intro'){setTutorialStep('board');return}if(step.id==='board'){setTutorialStep('basic');return}}"""
html = replace_once(html, old_controller, new_controller, 'tutorial controller')

# 3) Add tutorial-only state fields.
html = replace_once(html,
"const state={sessionMode:'menu',battleId:0,tutorialStep:null,tutorialHintOpen:false,player:null,enemy:null,",
"const state={sessionMode:'menu',battleId:0,tutorialStep:null,tutorialHintOpen:false,tutorialSegmentDone:false,tutorialSuccessText:'',player:null,enemy:null,",
'state tutorial fields')

# 4) Lock hand selection to the instructed cards during deterministic lessons.
html = replace_once(html,
"else if(state.phase==='action'){if(state.target&&!picked&&!canContinueTargetSelection(c)){log('선택한 타겟에는 이 카드를 다음 순서로 붙일 수 없습니다.','hit');return}toggleHandSelection(c.uid)}else return;",
"else if(state.phase==='action'){if(!tutorialAllows('select',{card:c})){tutorialReject('select');return}if(state.target&&!picked&&!canContinueTargetSelection(c)){log('선택한 타겟에는 이 카드를 다음 순서로 붙일 수 없습니다.','hit');return}toggleHandSelection(c.uid)}else return;",
'renderHand tutorial selection gate')

# 5) Gate draw, meld and discard mutation paths, and progress only after real engine success.
html = replace_once(html,
"function playerDraw(fromDiscard){if(state.gameOver||state.turn!=='player'||state.phase!=='draw')return;const source=",
"function playerDraw(fromDiscard){if(state.gameOver||state.turn!=='player'||state.phase!=='draw')return;const tutorialAction=fromDiscard?'drawDiscard':'drawDeck';if(!tutorialAllows(tutorialAction,{fromDiscard})){tutorialReject(tutorialAction);return}const source=",
'playerDraw tutorial gate')

html = replace_once(html,
"function playerMeld(){if(state.turn!=='player'||state.phase!=='action')return;const cs=selectedCards(),t=meldType(cs);if(state.player.newMeldUsed)",
"function playerMeld(){if(state.turn!=='player'||state.phase!=='action')return;const cs=selectedCards(),t=meldType(cs);if(!tutorialAllows('meld',{cards:cs,type:t})){tutorialReject('meld');return}if(state.player.newMeldUsed)",
'playerMeld tutorial gate')

html = replace_once(html,
"state.selected.clear();state.selectionOrder=[];state.boardSelected.clear();state.target=null;submitNewMeld('player',cs);render()}",
"state.selected.clear();state.selectionOrder=[];state.boardSelected.clear();state.target=null;const result=submitNewMeld('player',cs);if(result&&tutorialCheckProgress('meld',{type:t,cards:cs}))return;render()}",
'playerMeld tutorial progress')

html = replace_once(html,
"function playerDiscard(){if(state.turn!=='player'||state.phase!=='action')return;const cs=selectedCards();if(cs.length!==1){log('버릴 카드는 정확히 1장 선택하세요.','hit');return}const c=cs[0],r=",
"function playerDiscard(){if(state.turn!=='player'||state.phase!=='action')return;const cs=selectedCards();if(cs.length!==1){log('버릴 카드는 정확히 1장 선택하세요.','hit');return}const c=cs[0];if(!tutorialAllows('discard',{card:c})){tutorialReject('discard');return}const r=",
'playerDiscard tutorial gate')

html = replace_once(html,
"state.player.discardsRemaining=Math.max(0,(state.player.discardsRemaining||1)-1);if(state.player.hand.length===0)",
"state.player.discardsRemaining=Math.max(0,(state.player.discardsRemaining||1)-1);if(tutorialCheckProgress('discard',{card:c}))return;if(state.player.hand.length===0)",
'playerDiscard tutorial progress')

# 6) Make button enabled state and highlights agree with the action gate.
html = replace_once(html,
"document.getElementById('mulliganBtn').textContent=`선택 ${Math.min(cs.length,3)}장 교체`;renderTargetHint()}",
"document.getElementById('mulliganBtn').textContent=`선택 ${Math.min(cs.length,3)}장 교체`;if(state.sessionMode==='tutorial'){const drawDeck=tutorialAllows('drawDeck'),drawDiscard=tutorialAllows('drawDiscard'),meldAllowed=tutorialAllows('meld',{cards:cs,type:t}),discardAllowed=cs.length===1&&tutorialAllows('discard',{card:cs[0]});document.getElementById('drawDeckBtn').disabled=!draw||!drawDeck;document.getElementById('drawDiscardBtn').disabled=!draw||!state.discard.length||!drawDiscard;document.getElementById('deckPile').classList.toggle('disabled',!draw||!drawDeck);document.getElementById('discardPile').classList.toggle('disabled',!draw||!state.discard.length||!drawDiscard);meldBtn.disabled=meldBtn.disabled||!meldAllowed;attachBtn.disabled=true;recoverBtn.disabled=true;mb.disabled=true;document.getElementById('discardBtn').disabled=document.getElementById('discardBtn').disabled||!discardAllowed;document.getElementById('resetBtn').hidden=true}else document.getElementById('resetBtn').hidden=false;renderTargetHint();renderTutorialHighlights()}",
'updateButtons tutorial state')

# 7) Visually distinguish instructed and locked tutorial controls without neon glow.
html = replace_once(html,
"</style>\n</head>",
"""/* UX1 · deterministic tutorial targets */
.tutorialTarget{outline:2px solid #a9c9a1!important;outline-offset:2px!important;box-shadow:0 0 0 1px #263b32!important}
.cardBtn.tutorialTarget{transform:translateY(-3px)}
.cardBtn.tutorialLocked{opacity:.36;filter:saturate(.55)}
.pileVisual.tutorialTarget{border-radius:9px;background:#ffffff08}
.pixelBtn.tutorialTarget{background:#405b50!important;border-color:#769582!important}
@media(max-width:390px){.tutorialTarget{outline-width:2px!important;outline-offset:1px!important}}

</style>
</head>""",
'UX1 tutorial target CSS')

# 8) Roadmap: the deterministic state + basic/set/run tranche is now live.
replacements = {
"- [ ] 튜토리얼 전용 고정 게임 상태/손패/드로우 설계":"- [x] 튜토리얼 전용 고정 게임 상태/손패/드로우 설계 — 실제 카드 객체/조합 판정 엔진을 재사용하고 단계마다 상태만 결정론적으로 재구성",
"- [ ] 카드 기본 조작 튜토리얼 — 획득/선택/버리기 및 실제 행동 UI 이해":"- [x] 카드 기본 조작 튜토리얼 — 고정 Q♦ 덱 드로우 → 지정 카드 선택 → 버리기 성공 시 자동 진행",
"- [ ] 세트 튜토리얼":"- [x] 세트 튜토리얼 — 3♠ / 3♥ / 3♦ 고정 손패 + 실제 `meldType` / `submitNewMeld` 경로",
"- [ ] 런 튜토리얼":"- [x] 런 튜토리얼 — 4♣ / 5♣ / 6♣ 고정 손패 + 실제 `meldType` / `submitNewMeld` 경로",
"1. UI2 P2: hierarchy/density pass is live; finish the 360–480px real-device visual check, then defer P3 art/brand polish until gameplay/tutorial UX is steadier.\n2. UX1 P1: connect deterministic basic controls → 세트 → 런 → 붙이기 → 상대 조합 → 스위치 → 러미 scenarios to the real engine.\n3. L10N1 + M8: continue remaining text cleanup and named-card choice/copy/timing audit in parallel; do not begin large M9/content expansion until the first ~50 named-card behaviors and UX1 P1 are both stable.":
"1. UX1 P1: deterministic 기본 조작 → 세트 → 런 lessons are live; next connect 붙이기 → 상대 공개 조합 → 스위치 → 러미 to the same real-engine tutorial controller.\n2. UI2 P2: finish the 360–480px real-device visual check, then defer P3 art/brand polish until gameplay/tutorial UX is steadier.\n3. L10N1 + M8: continue remaining text cleanup and named-card choice/copy/timing audit in parallel; do not begin large M9/content expansion until the first ~50 named-card behaviors and UX1 P1 are both stable."
}
for old, new in replacements.items():
    roadmap = replace_once(roadmap, old, new, f'roadmap {old[:24]}')

# 9) Add regression coverage for the deterministic lesson contract.
test = r'''import fs from 'node:fs';

const html = fs.readFileSync(new URL('../index.html', import.meta.url), 'utf8');
const roadmap = fs.readFileSync(new URL('../ROADMAP.md', import.meta.url), 'utf8');
const script = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).join('\n');

function ok(condition, message) {
  if (!condition) throw new Error(message);
  console.log(`PASS: ${message}`);
}

new Function(script);

ok(script.includes("id:'basic'") && script.includes("scenario:'basic'") && script.includes("discardRole:'basicDraw'") && script.includes("implemented:true"), 'basic lesson is a deterministic implemented scenario');
ok(script.includes("id:'set'") && script.includes("scenario:'set'") && script.includes("expectMeld:'SET'"), 'SET lesson requires the real SET result');
ok(script.includes("id:'run'") && script.includes("scenario:'run'") && script.includes("expectMeld:'RUN'"), 'RUN lesson requires the real RUN result');
ok(script.includes("makeTutorialCard('D','Q','basicDraw')") && script.includes("makeTutorialCard('S','2','hold')"), 'basic lesson fixes one draw target while retaining a hold card to avoid accidental RUMMY');
ok(script.includes("makeTutorialCard('S','3','setCard')") && script.includes("makeTutorialCard('H','3','setCard')") && script.includes("makeTutorialCard('D','3','setCard')"), 'SET lesson uses the planned 3-suit fixed hand');
ok(script.includes("makeTutorialCard('C','4','runCard')") && script.includes("makeTutorialCard('C','5','runCard')") && script.includes("makeTutorialCard('C','6','runCard')"), 'RUN lesson uses the planned club sequence');
ok(script.includes("function resetTutorialSide") && script.includes("state.switchTarget='neutral';state.switchPower=0"), 'tutorial scenario rebuilds combat state deterministically instead of creating a separate rules engine');
ok(script.includes("if(!tutorialAllows(tutorialAction,{fromDiscard}))") && script.includes("if(!tutorialAllows('select',{card:c}))") && script.includes("if(!tutorialAllows('discard',{card:c}))"), 'draw, selection and discard mutation paths obey the tutorial action gate');
ok(script.includes("const result=submitNewMeld('player',cs);if(result&&tutorialCheckProgress('meld',{type:t,cards:cs}))"), 'SET/RUN success is confirmed only after submitNewMeld succeeds');
ok(script.includes("setTimeout(()=>{if(state.sessionMode==='tutorial'&&state.battleId===battleId&&state.tutorialStep===stepId)setTutorialStep(next.id)},650)"), 'successful lessons auto-advance with stale-session protection');
ok(script.includes("function renderTutorialHighlights") && html.includes('.cardBtn.tutorialLocked') && html.includes('.pixelBtn.tutorialTarget'), 'tutorial target and locked affordances are visible without a separate game screen');
ok(script.includes("document.getElementById('resetBtn').hidden=true"), 'random new-game reset is hidden during deterministic tutorial lessons');
ok(roadmap.includes('- [x] 카드 기본 조작 튜토리얼') && roadmap.includes('- [x] 세트 튜토리얼') && roadmap.includes('- [x] 런 튜토리얼'), 'UX1 roadmap records the completed first hands-on tranche');

console.log('RUMMY//DUEL deterministic basic/SET/RUN tutorial regressions passed.');
'''

index_path.write_text(html, encoding='utf-8')
roadmap_path.write_text(roadmap, encoding='utf-8')
(root / 'tests' / 'tutorial-basic-set-run.mjs').write_text(test, encoding='utf-8')
print('Applied UX1 deterministic basic/SET/RUN tutorial patch.')

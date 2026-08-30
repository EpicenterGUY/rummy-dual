from pathlib import Path

p=Path('index.html')
s=p.read_text()

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit(f'missing pattern: {label}')
    s=s.replace(old,new,1)

def replace_func(name,next_name,new_body):
    global s
    start=s.find(f'function {name}')
    if start<0: raise SystemExit(f'missing function: {name}')
    end=s.find(f'\nfunction {next_name}',start)
    if end<0: raise SystemExit(f'missing next function after {name}: {next_name}')
    s=s[:start]+new_body+s[end:]

rep(" {id:'rummy',title:'러미',goal:'손패를 모두 사용해 러미 6장 리필을 직접 발생시킵니다.',hint:'실제 triggerRummy 경로를 사용합니다.',implemented:false}",
" {id:'rummy',title:'러미',goal:'마지막 손패를 사용해 손패를 0장으로 만들고 러미 6장 리필을 직접 발생시킵니다.',hint:'강조된 K♠를 선택해 버리세요. 손패가 0장이 되는 순간 실제 러미 처리로 새 손패 6장을 받습니다.',implemented:true,scenario:'rummy',allow:['select','discard','clear'],selectRoles:['rummyLast'],discardRole:'rummyLast',expectReload:6,completeOn:'rummy'}",
'RUMMY step')

rep("else if(step.scenario==='switch'){p.hand=[makeTutorialCard('C','8','switchCard'),makeTutorialCard('D','2','hold')];p.melds=[makeTutorialMeld('player','SET',[makeTutorialCard('S','8','board','player'),makeTutorialCard('H','8','board','player'),makeTutorialCard('D','8','board','player')])];state.switchTarget='player';state.switchPower=36;state.phase='action';log('스위치 실습 · 8♣를 세트에 붙여 버스트 +24로 누적 위력을 키우고 상대에게 넘기세요.','important')}return true}",
"else if(step.scenario==='switch'){p.hand=[makeTutorialCard('C','8','switchCard'),makeTutorialCard('D','2','hold')];p.melds=[makeTutorialMeld('player','SET',[makeTutorialCard('S','8','board','player'),makeTutorialCard('H','8','board','player'),makeTutorialCard('D','8','board','player')])];state.switchTarget='player';state.switchPower=36;state.phase='action';log('스위치 실습 · 8♣를 세트에 붙여 버스트 +24로 누적 위력을 키우고 상대에게 넘기세요.','important')}else if(step.scenario==='rummy'){p.hand=[makeTutorialCard('S','K','rummyLast')];p.deck=[makeTutorialCard('C','2','rummyReload'),makeTutorialCard('D','4','rummyReload'),makeTutorialCard('H','6','rummyReload'),makeTutorialCard('S','8','rummyReload'),makeTutorialCard('C','10','rummyReload'),makeTutorialCard('D','Q','rummyReload')];state.phase='action';log('러미 실습 · 마지막 K♠를 버려 손패를 0장으로 만들고 새 손패 6장을 받으세요.','important')}return true}",
'RUMMY scenario')

replace_func('renderTutorialCoach','setTutorialStep',"""function renderTutorialCoach(){const coach=document.getElementById('tutorialCoach'),step=currentTutorialStep();if(!coach)return;if(state.sessionMode!=='tutorial'||!step){coach.hidden=true;return}coach.hidden=false;document.getElementById('tutorialStepBadge').textContent=`튜토리얼 ${Math.max(1,tutorialStepIndex()+1)} / ${TUTORIAL_STEPS.length}`;document.getElementById('tutorialCoachTitle').textContent=state.tutorialSegmentDone?`${step.title} · 성공`:step.title;document.getElementById('tutorialCoachGoal').textContent=state.tutorialSuccessText||step.goal;const hint=document.getElementById('tutorialCoachHint');hint.textContent=state.tutorialSegmentDone?(step.id==='rummy'?'기본 튜토리얼 완료! 메인으로 돌아가거나 이 단계를 다시 연습할 수 있습니다.':'다음 실습은 러미입니다.'):step.hint||'';hint.hidden=state.tutorialSegmentDone?false:!state.tutorialHintOpen;const next=document.getElementById('tutorialNextBtn');if(state.tutorialSegmentDone){next.hidden=false;next.disabled=step.id!=='rummy';next.textContent=step.id==='rummy'?'튜토리얼 완료 · 메인으로':'다음 실습 준비 중'}else{next.hidden=!step.manualNext;next.disabled=false;next.textContent=step.id==='intro'?'화면 보기':step.id==='board'?'실습 시작':'다음'}}""")

replace_func('tutorialCheckProgress','renderTutorialHighlights',"""function tutorialCheckProgress(event,context={}){if(state.sessionMode!=='tutorial')return false;const step=currentTutorialStep();if(!step?.completeOn||step.completeOn!==event)return false;if(step.expectMeld&&context.type!==step.expectMeld)return false;if(step.discardRole&&context.card?.tutorialRole!==step.discardRole)return false;if(step.attachSide&&context.targetSide!==step.attachSide)return false;if(step.expectAttach&&context.type!==step.expectAttach)return false;if(step.expectSwitchTarget&&context.afterTarget!==step.expectSwitchTarget)return false;if(step.minPowerGain&&((context.afterPower||0)-(context.beforePower||0)<step.minPowerGain))return false;if(step.expectReload&&context.afterHand!==step.expectReload)return false;const next=TUTORIAL_STEPS[tutorialStepIndex()+1];state.tutorialHintOpen=true;state.tutorialSuccessText=event==='discard'?'좋아요. 카드를 뽑고 선택해 버리는 기본 흐름을 익혔습니다.':event==='rummy'?`러미 성공! 손패 ${context.beforeHand}장에서 새 손패 ${context.afterHand}장으로 즉시 리필되었습니다. 기본 튜토리얼을 완료했습니다.`:event==='attach'?step.id==='attachEnemy'?'상대 공개 조합도 내 공격 경로로 사용할 수 있습니다.':step.id==='switch'?`버스트 성공! 누적 위력 ${context.beforePower} → ${context.afterPower}, 스위치가 상대에게 넘어갔습니다.`:`붙이기 성공! 실제 체인 처리로 누적 위력 ${context.afterPower}이 만들어졌습니다.`:`${step.title} 완성! 실제 조합 판정 엔진이 성공을 확인했습니다.`;log(`튜토리얼 ${step.title} 성공.`,'good');if(step.id==='rummy'){progress.tutorialPromptSeen=true;progress.tutorialCompleted=true;saveProgress()}if(next?.implemented){render();renderTutorialCoach();const battleId=state.battleId,stepId=step.id;setTimeout(()=>{if(state.sessionMode==='tutorial'&&state.battleId===battleId&&state.tutorialStep===stepId)setTutorialStep(next.id)},650);return true}state.tutorialSegmentDone=true;render();renderTutorialCoach();return true}""")

replace_func('advanceTutorial','restartTutorialStep',"""function advanceTutorial(){const step=currentTutorialStep();if(!step)return;if(step.id==='intro'){setTutorialStep('board');return}if(step.id==='board'){setTutorialStep('basic');return}if(step.id==='rummy'&&state.tutorialSegmentDone){showStartScreen();return}}""")

rep("if(w==='player')state.rummy++;drawMany(w,reload,false);", "if(w==='player')state.rummy++;const beforeReloadHand=s.hand.length;drawMany(w,reload,false);", 'RUMMY before-hand capture')
rep("if(w==='player'){state.selected.clear();state.selectionOrder=[];state.boardSelected.clear();state.target=null;endPlayerTurn()}}", "if(w==='player'){tutorialCheckProgress('rummy',{beforeHand:beforeReloadHand,reload,afterHand:s.hand.length});state.selected.clear();state.selectionOrder=[];state.boardSelected.clear();state.target=null;endPlayerTurn()}}", 'RUMMY tutorial hook')

replace_func('renderStartScreen','hideTutorialCoach',"""function renderStartScreen(){const el=document.getElementById('startMeta');if(!el)return;const id=charUnlocked(progress.selectedChar)?progress.selectedChar:'wanderer',ch=CHARACTERS[id]||CHARACTERS.wanderer;el.textContent=`${ch.name} Lv.${charLevel(progress,id)} · 전체 ${progress.totalClears}클리어`;const prompt=document.getElementById('firstRunPrompt'),note=document.getElementById('startResumeNote'),tutorialBtn=document.getElementById('tutorialStartBtn'),tutorialState=tutorialBtn?.querySelector('.menuState'),tutorialSmall=tutorialBtn?.querySelector('small');if(prompt)prompt.hidden=!!progress.tutorialPromptSeen;if(note)note.textContent=progress.tutorialCompleted?'기본 튜토리얼 완료 · 필요할 때 언제든 다시 볼 수 있습니다.':progress.tutorialPromptSeen?'기본 조작부터 러미까지 고정 패 튜토리얼을 시작할 수 있습니다.':'처음이라면 짧은 튜토리얼을 권장합니다. 강제 진행은 없습니다.';if(tutorialState)tutorialState.textContent=progress.tutorialCompleted?'다시 보기':'시작';if(tutorialSmall)tutorialSmall.textContent=progress.tutorialCompleted?'기본 튜토리얼을 처음부터 다시 플레이합니다.':'기본 조작부터 러미까지 고정 패로 직접 익힙니다.'}""")

p.write_text(s)

rp=Path('ROADMAP.md')
r=rp.read_text()
for old,new in [
('- [ ] 러미 튜토리얼','- [x] 러미 튜토리얼 — 마지막 손패를 실제로 사용해 `triggerRummy()` → 기본 6장 리필 확인'),
('- [ ] 튜토리얼 완료 상태 저장','- [x] 튜토리얼 완료 상태 저장 — 러미 실습 성공 시 `tutorialCompleted=true` 저장'),
('- [ ] 튜토리얼 다시 보기','- [x] 튜토리얼 다시 보기 — 완료 후 시작 메뉴를 `다시 보기` 상태로 전환하고 처음부터 재진입')]:
    if old not in r: raise SystemExit(f'missing roadmap item: {old}')
    r=r.replace(old,new,1)
old_next='1. UX1 P1: deterministic 기본 조작 → 세트 → 런 lessons are live; next connect 붙이기 → 상대 공개 조합 → 스위치 → 러미 to the same real-engine tutorial controller.'
if old_next in r:
    r=r.replace(old_next,'1. UX1 P1: 기본 조작 → 세트 → 런 → 붙이기 → 상대 공개 조합 → 스위치 → 러미의 실제 엔진 튜토리얼이 연결됨. 다음은 UX1 P2의 누적 위력/폭발 결과 강조와 자유 연습전.',1)
rp.write_text(r)

Path('tests/tutorial-rummy.mjs').write_text("""import fs from 'node:fs';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const roadmap=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\\s\\S]*?)<\\/script>/g)].map(m=>m[1]).join('\\n');
function ok(c,m){if(!c)throw new Error(m);console.log(`PASS: ${m}`)}
new Function(script);
ok(script.includes("id:'rummy'")&&script.includes("scenario:'rummy'")&&script.includes("expectReload:6")&&script.includes("completeOn:'rummy'"),'RUMMY lesson is deterministic and requires six-card reload');
ok(script.includes("makeTutorialCard('S','K','rummyLast')")&&script.includes("p.deck=[makeTutorialCard('C','2','rummyReload')"),'RUMMY scenario has one last card and a fixed six-card deck');
ok(script.includes("tutorialCheckProgress('rummy',{beforeHand:beforeReloadHand,reload,afterHand:s.hand.length})"),'real triggerRummy reports actual reload result');
ok(script.includes("if(step.expectReload&&context.afterHand!==step.expectReload)return false"),'tutorial only completes on actual six-card reload');
ok(script.includes("progress.tutorialCompleted=true;saveProgress()"),'final RUMMY lesson persists tutorial completion');
ok(script.includes("tutorialState.textContent=progress.tutorialCompleted?'다시 보기':'시작'"),'completed tutorial becomes replayable in start menu');
ok(script.includes("if(step.id==='rummy'&&state.tutorialSegmentDone){showStartScreen();return}"),'final completion can return to main menu');
ok(!html.includes('고정 패 실습은 순차 추가 중입니다.'),'start screen no longer says core tutorial is still being added');
ok(roadmap.includes('- [x] 러미 튜토리얼')&&roadmap.includes('- [x] 튜토리얼 완료 상태 저장')&&roadmap.includes('- [x] 튜토리얼 다시 보기'),'roadmap records RUMMY completion and replay state');
console.log('RUMMY//DUEL deterministic RUMMY tutorial regressions passed.');
""")

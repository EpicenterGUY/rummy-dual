from pathlib import Path
index=Path('index.html')
road=Path('ROADMAP.md')
s=index.read_text()
r=road.read_text()

old='<div class="startAux"><button id="startProgressBtn" class="pixelBtn" type="button">캐릭터·해금</button><button id="startRulesBtn" class="pixelBtn" type="button">규칙·용어</button><button id="developerBtn" class="pixelBtn" type="button">개발자 모드 · OFF</button><button id="advancedTutorialBtn" class="pixelBtn" type="button" disabled aria-disabled="true">고급 튜토리얼 · 기본 완료 후</button><button id="practiceStartBtn" class="pixelBtn practiceStartBtn" type="button">자유 연습전 · 진행도 영향 없음</button></div>'
new='<div class="startAux"><button id="startProgressBtn" class="pixelBtn" type="button">캐릭터·해금</button><button id="startRulesBtn" class="pixelBtn" type="button">규칙·용어</button><button id="developerBtn" class="pixelBtn" type="button">개발자 모드 · OFF</button><button id="advancedTutorialBtn" class="pixelBtn" type="button" disabled aria-disabled="true">고급 튜토리얼 · 기본 완료 후</button><button id="themeTutorialBtn" class="pixelBtn" type="button" disabled aria-disabled="true">테마 체험전 · 준비 중</button><button id="practiceStartBtn" class="pixelBtn practiceStartBtn" type="button">자유 연습전 · 진행도 영향 없음</button></div>'
if old not in s: raise SystemExit('start aux anchor not found')
s=s.replace(old,new,1)

old="const THEME_BUILD_PROFILES=Object.freeze({mixed:Object.freeze({id:'mixed',displayName:'혼합',short:'자유 혼합',desc:'해금된 모든 네임드가 캐릭터 경향에 따라 섞입니다.',themeId:null,live:true}),"
new="const THEME_TUTORIALS=Object.freeze({'v-signal':Object.freeze({themeId:'v-signal',startStep:null,live:false}),'zero-sight':Object.freeze({themeId:'zero-sight',startStep:null,live:false}),'point-blank':Object.freeze({themeId:'point-blank',startStep:null,live:false})});\nconst THEME_BUILD_PROFILES=Object.freeze({mixed:Object.freeze({id:'mixed',displayName:'혼합',short:'자유 혼합',desc:'해금된 모든 네임드가 캐릭터 경향에 따라 섞입니다.',themeId:null,live:true}),"
if old not in s: raise SystemExit('theme registry anchor not found')
s=s.replace(old,new,1)

old="rewarded:false,pendingEffectChoice:null,effectChoiceQueue:[],aiChoiceResume:null,aiAsyncActionResult:null,developerBattle:false};"
new="rewarded:false,pendingEffectChoice:null,effectChoiceQueue:[],aiChoiceResume:null,aiAsyncActionResult:null,developerBattle:false,tutorialThemeId:null};"
if old not in s: raise SystemExit('state anchor not found')
s=s.replace(old,new,1)

old="function renderStartScreen(){const el=document.getElementById('startMeta');if(!el)return;const id=charUnlocked(progress.selectedChar)?progress.selectedChar:'wanderer',ch=CHARACTERS[id]||CHARACTERS.wanderer,themeId=themeBuildUnlocked(progress.selectedTheme)?progress.selectedTheme:'mixed',theme=THEME_BUILD_PROFILES[themeId]||THEME_BUILD_PROFILES.mixed;el.textContent=`${ch.name} Lv.${charLevel(progress,id)} · ${theme.displayName}${progress.deckBuild?.enabled?' · 커스텀 덱':''} · 전체 ${progress.totalClears}클리어${typeof developerModeActive==='function'&&developerModeActive()?' · DEV':''}`;if(typeof renderDeveloperPanel==='function')renderDeveloperPanel();const prompt=document.getElementById('firstRunPrompt'),note=document.getElementById('startResumeNote'),tutorialBtn=document.getElementById('tutorialStartBtn'),tutorialState=tutorialBtn?.querySelector('.menuState'),tutorialSmall=tutorialBtn?.querySelector('small'),advanced=document.getElementById('advancedTutorialBtn');"
new="function renderStartScreen(){const el=document.getElementById('startMeta');if(!el)return;const id=charUnlocked(progress.selectedChar)?progress.selectedChar:'wanderer',ch=CHARACTERS[id]||CHARACTERS.wanderer,themeId=themeBuildUnlocked(progress.selectedTheme)?progress.selectedTheme:'mixed',theme=THEME_BUILD_PROFILES[themeId]||THEME_BUILD_PROFILES.mixed;el.textContent=`${ch.name} Lv.${charLevel(progress,id)} · ${theme.displayName}${progress.deckBuild?.enabled?' · 커스텀 덱':''} · 전체 ${progress.totalClears}클리어${typeof developerModeActive==='function'&&developerModeActive()?' · DEV':''}`;if(typeof renderDeveloperPanel==='function')renderDeveloperPanel();const prompt=document.getElementById('firstRunPrompt'),note=document.getElementById('startResumeNote'),tutorialBtn=document.getElementById('tutorialStartBtn'),tutorialState=tutorialBtn?.querySelector('.menuState'),tutorialSmall=tutorialBtn?.querySelector('small'),advanced=document.getElementById('advancedTutorialBtn'),themeTutorial=document.getElementById('themeTutorialBtn');"
if old not in s: raise SystemExit('render start variables anchor not found')
s=s.replace(old,new,1)

old="if(advanced){advanced.disabled=!progress.tutorialCompleted;advanced.setAttribute('aria-disabled',String(!progress.tutorialCompleted));advanced.textContent=progress.tutorialCompleted?'고급 튜토리얼 · 회수/정비/상태/조커/네임드':'고급 튜토리얼 · 기본 완료 후'}}"
new="if(advanced){advanced.disabled=!progress.tutorialCompleted;advanced.setAttribute('aria-disabled',String(!progress.tutorialCompleted));advanced.textContent=progress.tutorialCompleted?'고급 튜토리얼 · 회수/정비/상태/조커/네임드':'고급 튜토리얼 · 기본 완료 후'}if(themeTutorial){const available=typeof availableThemeTutorials==='function'?availableThemeTutorials():[];const ready=progress.tutorialCompleted&&available.length>0;themeTutorial.disabled=!ready;themeTutorial.setAttribute('aria-disabled',String(!ready));themeTutorial.textContent=ready?`테마 체험전 · ${available.map(x=>themeDef(x.themeId)?.displayName||x.themeId).join(' / ')}`:progress.tutorialCompleted?'테마 체험전 · 준비 중':'테마 체험전 · 기본 완료 후'}}"
if old not in s: raise SystemExit('render start advanced anchor not found')
s=s.replace(old,new,1)

old="function showStartScreen(){state.battleId++;state.sessionMode='menu';state.tutorialStep=null;state.tutorialExitArmed=false;state.tutorialHintOpen=false;"
new="function showStartScreen(){state.battleId++;state.sessionMode='menu';state.tutorialStep=null;state.tutorialExitArmed=false;state.tutorialHintOpen=false;state.tutorialThemeId=null;"
if old not in s: raise SystemExit('show start anchor not found')
s=s.replace(old,new,1)

old="function tutorialSegmentInfo(id=state.tutorialStep){const idx=tutorialStepIndex(id),advanced=TUTORIAL_STEPS.findIndex(x=>x.id==='recover'),basicEnd=TUTORIAL_STEPS.findIndex(x=>x.id==='rummy');if(idx>=advanced&&advanced>=0)return{label:'고급 튜토리얼',position:idx-advanced+1,total:TUTORIAL_STEPS.length-advanced};return{label:'튜토리얼',position:Math.max(1,idx+1),total:basicEnd>=0?basicEnd+1:TUTORIAL_STEPS.length}}"
new="function tutorialSegmentInfo(id=state.tutorialStep){const idx=tutorialStepIndex(id),step=TUTORIAL_STEPS[idx];if(step?.themeId){const themeSteps=TUTORIAL_STEPS.filter(x=>x.implemented&&x.themeId===step.themeId),pos=Math.max(0,themeSteps.findIndex(x=>x.id===id));return{label:`${themeDef(step.themeId)?.displayName||step.themeId} 체험`,position:pos+1,total:Math.max(1,themeSteps.length)}}const advanced=TUTORIAL_STEPS.findIndex(x=>x.id==='recover'),basicEnd=TUTORIAL_STEPS.findIndex(x=>x.id==='rummy');if(idx>=advanced&&advanced>=0)return{label:'고급 튜토리얼',position:idx-advanced+1,total:TUTORIAL_STEPS.filter(x=>x.implemented&&!x.themeId).length-advanced};return{label:'튜토리얼',position:Math.max(1,idx+1),total:basicEnd>=0?basicEnd+1:TUTORIAL_STEPS.length}}"
if old not in s: raise SystemExit('segment info anchor not found')
s=s.replace(old,new,1)

old="function setTutorialStep(id){const step=TUTORIAL_STEPS.find(x=>x.id===id);if(!step)return false;state.tutorialStepToken++;state.tutorialStep=id;state.tutorialExitArmed=false;"
new="function setTutorialStep(id){const step=TUTORIAL_STEPS.find(x=>x.id===id);if(!step)return false;state.tutorialStepToken++;state.tutorialStep=id;if(step.themeId)state.tutorialThemeId=step.themeId;state.tutorialExitArmed=false;"
if old not in s: raise SystemExit('set tutorial step anchor not found')
s=s.replace(old,new,1)

old="function startTutorial(stepId='intro'){progress.tutorialPromptSeen=true;saveProgress();hideStartScreen();document.getElementById('overlay')?.classList.remove('show');newGame('tutorial');setTutorialStep(stepId);renderStartScreen()}\nfunction startAdvancedTutorial()"
new="function themeTutorialDef(id){return id?THEME_TUTORIALS[id]||null:null}\nfunction themeTutorialAvailable(id){const def=themeTutorialDef(id);return !!def?.live&&!!def.startStep&&TUTORIAL_STEPS.some(x=>x.id===def.startStep&&x.implemented&&x.themeId===id)}\nfunction availableThemeTutorials(){return Object.values(THEME_TUTORIALS).filter(x=>themeTutorialAvailable(x.themeId))}\nfunction startTutorial(stepId='intro'){progress.tutorialPromptSeen=true;saveProgress();hideStartScreen();document.getElementById('overlay')?.classList.remove('show');newGame('tutorial');state.tutorialThemeId=null;setTutorialStep(stepId);renderStartScreen()}\nfunction startThemeTutorial(themeId=null){if(!progress.tutorialCompleted){log('테마 체험전은 기본 튜토리얼 완료 후 열립니다.','hit');renderStartScreen();return false}const def=themeId?themeTutorialDef(themeId):availableThemeTutorials()[0];if(!def||!themeTutorialAvailable(def.themeId)){log('현재 플레이 가능한 테마 체험전이 아직 없습니다.','hit');renderStartScreen();return false}startTutorial(def.startStep);return true}\nfunction startAdvancedTutorial()"
if old not in s: raise SystemExit('tutorial launcher anchor not found')
s=s.replace(old,new,1)

old="next.textContent=segmentEnd?(step.id==='rummy'?'기본 튜토리얼 완료 · 메인으로':'고급 튜토리얼 완료 · 메인으로'):'자동 진행 중'"
new="next.textContent=segmentEnd?(step.id==='rummy'?'기본 튜토리얼 완료 · 메인으로':step.themeId?`${themeDef(step.themeId)?.displayName||step.themeId} 체험 완료 · 메인으로`:'고급 튜토리얼 완료 · 메인으로'):'자동 진행 중'"
if old not in s: raise SystemExit('theme completion button anchor not found')
s=s.replace(old,new,1)

old="document.getElementById('advancedTutorialBtn').onclick=startAdvancedTutorial;document.getElementById('startCodexBtn')"
new="document.getElementById('advancedTutorialBtn').onclick=startAdvancedTutorial;document.getElementById('themeTutorialBtn').onclick=()=>startThemeTutorial();document.getElementById('startCodexBtn')"
if old not in s: raise SystemExit('theme button binding anchor not found')
s=s.replace(old,new,1)

old='- [ ] 테마군 튜토리얼 기반'
new='- [x] 테마군 튜토리얼 기반 — `THEME_TUTORIALS` 레지스트리(`themeId/startStep/live`)와 `startThemeTutorial()` 진입, 테마별 가용성 판정, `state.tutorialThemeId`, 테마 전용 단계 배지/완료 문구를 추가. 시작 화면의 `테마 체험전` 버튼은 기본 튜토리얼 완료 + 실제 live 테마 단계 등록 시에만 자동 활성화되어 미구현 체험전을 가장하지 않음'
if old not in r: raise SystemExit('roadmap foundation anchor not found')
r=r.replace(old,new,1)
index.write_text(s)
road.write_text(r)

from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

def rep(old,new,label,count=1):
    global s
    n=s.count(old)
    if n<count:
        raise SystemExit(f'missing {label}: {n}/{count}')
    s=s.replace(old,new,count)

def replace_between(start_marker,end_marker,new_text,label):
    global s
    a=s.find(start_marker)
    if a<0: raise SystemExit(f'missing start {label}')
    b=s.find(end_marker,a)
    if b<0: raise SystemExit(f'missing end {label}')
    s=s[:a]+new_text+s[b:]

# Developer-mode styling and clearer theme-codex locked entries.
old=".codexFieldIcon{width:46px;height:69px;border:2px solid #050609;background:#19152b;box-shadow:0 0 0 2px #5a4c83 inset;display:grid;place-items:center;text-align:center;font-size:7px;color:#d5c9ff;padding:4px}.staleBtn"
new=".codexFieldIcon{width:46px;height:69px;border:2px solid #050609;background:#19152b;box-shadow:0 0 0 2px #5a4c83 inset;display:grid;place-items:center;text-align:center;font-size:7px;color:#d5c9ff;padding:4px}.codexEntry.themeLocked{border-color:#6b5f3b;background:#171713}.codexEntry.devRevealed{border-color:#6b4d7b;background:#17131e}.codexThemeEmpty{grid-column:1/-1;padding:12px;border:1px dashed #53617a;background:#0d131d;color:#99a8bf;font-size:8px;line-height:1.55;text-align:center}.codexThemeEmpty b{color:var(--cyan);font-size:10px}.developerModal{width:min(430px,100%);padding:10px}.developerStatus{padding:9px;border:1px solid #3d485d;background:#111722;font-size:9px;font-weight:900;color:#9aa8be;margin-bottom:7px}.developerStatus.on{border-color:#7c6530;background:#292313;color:#f2d78f}.developerInfo{padding:8px;border:1px solid #31415a;background:#101722;color:#cbd4e4;font-size:8px;line-height:1.5;margin-bottom:7px}.developerActions{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-top:7px}.developerActions .pixelBtn{font-size:7px}.developerActions .wide{grid-column:1/-1}.devModeActive{box-shadow:0 0 0 2px var(--gold) inset!important;color:#f2d78f}.staleBtn"
rep(old,new,'developer CSS')

# Main and HUD access points.
old='<div class="startAux"><button id="startProgressBtn" class="pixelBtn" type="button">캐릭터·해금</button><button id="startRulesBtn" class="pixelBtn" type="button">규칙·용어</button><button id="advancedTutorialBtn" class="pixelBtn" type="button" disabled aria-disabled="true">고급 튜토리얼 · 기본 완료 후</button><button id="practiceStartBtn" class="pixelBtn practiceStartBtn" type="button">자유 연습전 · 진행도 영향 없음</button></div>'
new='<div class="startAux"><button id="startProgressBtn" class="pixelBtn" type="button">캐릭터·해금</button><button id="startRulesBtn" class="pixelBtn" type="button">규칙·용어</button><button id="developerBtn" class="pixelBtn" type="button">개발자 모드 · OFF</button><button id="advancedTutorialBtn" class="pixelBtn" type="button" disabled aria-disabled="true">고급 튜토리얼 · 기본 완료 후</button><button id="practiceStartBtn" class="pixelBtn practiceStartBtn" type="button">자유 연습전 · 진행도 영향 없음</button></div>'
rep(old,new,'start developer button')
old='<div class="hudMenuPanel"><button id="progressBtn" class="pixelBtn">캐릭터</button><button id="codexBtn" class="pixelBtn">도감</button><button id="rulesBtn" class="pixelBtn">규칙</button><button id="homeBtn" class="pixelBtn">메인</button></div>'
new='<div class="hudMenuPanel"><button id="progressBtn" class="pixelBtn">캐릭터</button><button id="codexBtn" class="pixelBtn">도감</button><button id="developerHudBtn" class="pixelBtn">개발</button><button id="rulesBtn" class="pixelBtn">규칙</button><button id="homeBtn" class="pixelBtn">메인</button></div>'
rep(old,new,'HUD developer button')

# Developer overlay before progression/codex overlays.
marker='<div id="progressOverlay" class="overlay">'
dev_overlay='''<div id="developerOverlay" class="overlay"><div class="modal developerModal pixel"><div class="rulesHead"><h2>개발자 모드</h2><button id="closeDeveloperBtn" class="pixelBtn closeBtn">닫기</button></div><div id="developerStatus" class="developerStatus">DEV · OFF</div><div class="developerInfo">현재 코드에 실제 구현된 카드·필드·캐릭터·카드군의 해금 제한을 무시합니다. 개발 중 카드군도 선택할 수 있지만 아직 구현되지 않은 설계 카드가 새로 생기는 것은 아닙니다.<br><br><b>중요:</b> DEV 상태에서 시작한 대전은 승리해도 클리어·캐릭터 레벨·해금 진행도에 반영되지 않습니다. 일반 진행도 데이터 자체는 변경하지 않습니다.</div><button id="developerToggleBtn" class="pixelBtn goldBtn" type="button">개발자 모드 켜기</button><div class="developerActions"><button id="developerCodexBtn" class="pixelBtn" type="button">전체 도감</button><button id="developerProgressBtn" class="pixelBtn" type="button">캐릭터·카드군</button><button id="developerBattleBtn" class="pixelBtn primary wide" type="button" disabled>DEV 새 대전</button></div></div></div>\n'''
if marker not in s: raise SystemExit('missing progress overlay marker')
s=s.replace(marker,dev_overlay+marker,1)

# Codex description and dedicated theme tabs.
old='<div id="codexOverlay" class="overlay"><div class="modal codexModal pixel"><div class="rulesHead"><h2>카드 도감</h2><button id="closeCodexBtn" class="pixelBtn closeBtn">닫기</button></div><div class="codexSummary"><span>해금된 네임드·조커·필드를 확인합니다.<br><span class="sub">미해금 항목은 이름/효과 대신 해금 조건만 표시.</span></span><span><b id="codexUnlockedCount">0</b> / <span id="codexTotalCount">0</span></span></div><div id="codexTabs" class="codexTabs"><button class="pixelBtn active" data-codex-filter="all">전체</button><button class="pixelBtn" data-codex-filter="S">♠</button><button class="pixelBtn" data-codex-filter="H">♥</button><button class="pixelBtn" data-codex-filter="D">♦</button><button class="pixelBtn" data-codex-filter="C">♣</button><button class="pixelBtn" data-codex-filter="J">조커</button><button class="pixelBtn" data-codex-filter="F">필드</button></div><div id="codexGrid" class="codexGrid"></div></div></div>'
new='<div id="codexOverlay" class="overlay"><div class="modal codexModal pixel"><div class="rulesHead"><h2>카드 도감</h2><button id="closeCodexBtn" class="pixelBtn closeBtn">닫기</button></div><div class="codexSummary"><span>네임드·조커·필드와 카드군별 라이브 카드를 확인합니다.<br><span class="sub">일반 탭의 미해금 카드는 숨기지만, 카드군 탭에서는 카드군 정체성과 효과를 미리 확인할 수 있습니다.</span></span><span><b id="codexUnlockedCount">0</b> / <span id="codexTotalCount">0</span></span></div><div id="codexTabs" class="codexTabs"><button class="pixelBtn active" data-codex-filter="all">전체</button><button class="pixelBtn" data-codex-filter="S">♠</button><button class="pixelBtn" data-codex-filter="H">♥</button><button class="pixelBtn" data-codex-filter="D">♦</button><button class="pixelBtn" data-codex-filter="C">♣</button><button class="pixelBtn" data-codex-filter="J">조커</button><button class="pixelBtn" data-codex-filter="F">필드</button><button class="pixelBtn" data-codex-filter="theme:v-signal">V-SIGNAL</button><button class="pixelBtn" data-codex-filter="theme:zero-sight">ZERO//SIGHT</button><button class="pixelBtn" data-codex-filter="theme:point-blank">POINT//BLANK</button></div><div id="codexGrid" class="codexGrid"></div></div></div>'
rep(old,new,'codex theme tabs')

# Battle state snapshots whether progression rewards are disabled for this battle.
old='pendingEffectChoice:null,effectChoiceQueue:[],aiChoiceResume:null,aiAsyncActionResult:null};'
new='pendingEffectChoice:null,effectChoiceQueue:[],aiChoiceResume:null,aiAsyncActionResult:null,developerBattle:false};'
rep(old,new,'developer battle state')

# Developer state is persisted separately from player progression.
old="function saveProgress(){try{localStorage.setItem('rummyDuelProgressV25',JSON.stringify(progress))}catch(e){console.warn('RUMMY//DUEL progress save failed; continuing without persistence.',e)}}\nfunction charLevel"
new="""function saveProgress(){try{localStorage.setItem('rummyDuelProgressV25',JSON.stringify(progress))}catch(e){console.warn('RUMMY//DUEL progress save failed; continuing without persistence.',e)}}
const DEV_STORAGE_KEY='rummyDuelDeveloperV1';
function loadDeveloperMode(){try{return localStorage.getItem(DEV_STORAGE_KEY)==='1'}catch(e){return false}}
let developerMode=loadDeveloperMode();
function developerModeActive(){return !!developerMode}
function saveDeveloperMode(){try{localStorage.setItem(DEV_STORAGE_KEY,developerMode?'1':'0')}catch(e){console.warn('RUMMY//DUEL developer mode save failed; continuing without persistence.',e)}}
function renderDeveloperPanel(){const on=developerModeActive(),status=document.getElementById('developerStatus'),toggle=document.getElementById('developerToggleBtn'),battle=document.getElementById('developerBattleBtn'),main=document.getElementById('developerBtn'),hud=document.getElementById('developerHudBtn');if(status){status.textContent=on?'DEV · ON · 해금 제한 우회':'DEV · OFF · 일반 진행';status.classList.toggle('on',on)}if(toggle){toggle.textContent=on?'개발자 모드 끄기':'개발자 모드 켜기';toggle.classList.toggle('redBtn',on);toggle.classList.toggle('goldBtn',!on)}if(battle)battle.disabled=!on;if(main){main.textContent=on?'개발자 모드 · ON':'개발자 모드 · OFF';main.classList.toggle('devModeActive',on)}if(hud){hud.textContent=on?'개발 · ON':'개발';hud.classList.toggle('devModeActive',on)}}
function setDeveloperMode(on){developerMode=!!on;saveDeveloperMode();if(!developerMode&&typeof progress!=='undefined'){if(!charUnlocked(progress.selectedChar))progress.selectedChar='wanderer';if(!themeBuildUnlocked(progress.selectedTheme))progress.selectedTheme='mixed';saveProgress()}if(typeof renderDeveloperPanel==='function')renderDeveloperPanel();if(typeof renderProgress==='function')renderProgress();if(typeof renderCodex==='function')renderCodex();if(typeof renderStartScreen==='function')renderStartScreen();if(typeof render==='function')render();return developerMode}
function openDeveloperPanel(){renderDeveloperPanel();document.getElementById('developerOverlay')?.classList.add('show')}
function charLevel"""
rep(old,new,'developer persistence')

# All unlock queries gain an optional DEV bypass while keeping legacy extracted-function tests valid.
old="function charUnlocked(id,p=progress){const unlock=CHARACTER_UNLOCK[id];return typeof unlock==='function'&&!!unlock(p)}"
new="function charUnlocked(id,p=progress){if(typeof developerModeActive==='function'&&developerModeActive())return Object.prototype.hasOwnProperty.call(CHARACTERS,id);const unlock=CHARACTER_UNLOCK[id];return typeof unlock==='function'&&!!unlock(p)}"
rep(old,new,'char dev unlock')
old="function themeBuildUnlocked(id,p=progress){const profile=THEME_BUILD_PROFILES[id];if(!profile)return false;if(id==='mixed')return true;if(!profile.live)return false;const open=unlockedNamed(p);for(const cardId of open)if(NAMED[cardId]?.themeId===profile.themeId)return true;return false}"
new="function themeBuildUnlocked(id,p=progress){const profile=THEME_BUILD_PROFILES[id];if(!profile)return false;if(typeof developerModeActive==='function'&&developerModeActive())return true;if(id==='mixed')return true;if(!profile.live)return false;const open=unlockedNamed(p);for(const cardId of open)if(NAMED[cardId]?.themeId===profile.themeId)return true;return false}"
rep(old,new,'theme dev unlock')
old="function unlockedNamed(p=progress){const a=new Set(STARTER_NAMED.concat(['J1']));for(const g of UNLOCK_GROUPS)if(g.when(p))for(const id of g.items||[])a.add(id);return a}\nfunction unlockedFields(p=progress){const a=[];for(const g of UNLOCK_GROUPS)if(g.when(p))for(const id of g.fields||[])a.push(id);return [...new Set(a)]}"
new="function baseUnlockedNamed(p=progress){const a=new Set(STARTER_NAMED.concat(['J1']));for(const g of UNLOCK_GROUPS)if(g.when(p))for(const id of g.items||[])a.add(id);return a}\nfunction unlockedNamed(p=progress){if(typeof developerModeActive==='function'&&developerModeActive())return new Set(Object.keys(NAMED));return baseUnlockedNamed(p)}\nfunction baseUnlockedFields(p=progress){const a=[];for(const g of UNLOCK_GROUPS)if(g.when(p))for(const id of g.fields||[])a.push(id);return [...new Set(a)]}\nfunction unlockedFields(p=progress){if(typeof developerModeActive==='function'&&developerModeActive())return Object.keys(FIELDS);return baseUnlockedFields(p)}"
rep(old,new,'base and dev unlock pools')

# Start screen visibly signals DEV and refreshes its controls.
old="el.textContent=`${ch.name} Lv.${charLevel(progress,id)} · ${theme.displayName} · 전체 ${progress.totalClears}클리어`;const prompt="
new="el.textContent=`${ch.name} Lv.${charLevel(progress,id)} · ${theme.displayName} · 전체 ${progress.totalClears}클리어${typeof developerModeActive==='function'&&developerModeActive()?' · DEV':''}`;if(typeof renderDeveloperPanel==='function')renderDeveloperPanel();const prompt="
rep(old,new,'start DEV badge')
old="for(const id of['overlay','rulesOverlay','progressOverlay','codexOverlay'])document.getElementById(id)?.classList.remove('show');"
new="for(const id of['overlay','rulesOverlay','progressOverlay','codexOverlay','developerOverlay'])document.getElementById(id)?.classList.remove('show');"
rep(old,new,'close dev overlay on home')

# Snapshot dev status at battle start; later toggling cannot turn a DEV battle into a rewarded battle.
old="function newGame(mode='battle'){state.sessionMode=mode;state.battleId++;uidSeq=1;"
new="function newGame(mode='battle'){state.sessionMode=mode;state.battleId++;state.developerBattle=mode==='battle'&&typeof developerModeActive==='function'&&developerModeActive();uidSeq=1;"
rep(old,new,'developer battle snapshot')

# Never reward a DEV battle, even if another result path accidentally calls the grant helper.
old="function grantVictoryProgress(){if(state.rewarded)return[];state.rewarded=true;const before=snapshotUnlocks();"
new="function grantVictoryProgress(){if(state.rewarded)return[];if(state.developerBattle){state.rewarded=true;return[]}state.rewarded=true;const before=snapshotUnlocks();"
rep(old,new,'dev reward guard')

# Dev result branch explicitly explains that progress is not modified.
old="const practice=state.sessionMode==='practice',title=document.getElementById('resultTitle'),text=document.getElementById('resultText'),box=document.getElementById('resultUnlocks'),again=document.getElementById('againBtn');"
new="const practice=state.sessionMode==='practice',devBattle=!!state.developerBattle,title=document.getElementById('resultTitle'),text=document.getElementById('resultText'),box=document.getElementById('resultUnlocks'),again=document.getElementById('againBtn');"
rep(old,new,'showResult dev var')
old="again.textContent=practice?'연습전 다시 하기':'다시 하기';if(practice){"
new="again.textContent=practice?'연습전 다시 하기':devBattle?'DEV 다시 하기':'다시 하기';if(practice){"
rep(old,new,'showResult dev retry')
old="renderProgress();document.getElementById('overlay').classList.add('show');return}title.textContent=win?'승리':'패배';"
new="renderProgress();document.getElementById('overlay').classList.add('show');return}if(devBattle){state.rewarded=true;title.textContent=win?'DEV 승리':'DEV 패배';title.className=win?'gold':'red';text.textContent=win?'개발자 모드 전투 승리. 이 판은 클리어·캐릭터 레벨·카드/필드 해금 진행도에 반영되지 않습니다.':'개발자 모드 전투 종료. 이 판은 진행도에 영향을 주지 않습니다.';renderProgress();document.getElementById('overlay').classList.add('show');return}title.textContent=win?'승리':'패배';"
rep(old,new,'showResult dev branch')

# Combat badge shows that the current battle itself is non-rewarding DEV, independent of current toggle.
old="document.getElementById('charBadge').innerHTML=`<span class=\"gold\">◆</span> ${ch.name} Lv.${charLevel(progress,p.charId)} <span class=\"sub\">· ${buildTheme.displayName}</span>`;"
new="document.getElementById('charBadge').innerHTML=`<span class=\"gold\">◆</span> ${ch.name} Lv.${charLevel(progress,p.charId)} <span class=\"sub\">· ${buildTheme.displayName}</span>${state.developerBattle?'<span class=\"gold\"> · DEV</span>':''}`;"
rep(old,new,'combat DEV badge')

# Render development themes accurately when DEV makes them selectable.
old="const ok=themeBuildUnlocked(id),selected=progress.selectedTheme===id,lock=themeBuildLockText(id);return`<div class=\"charCard ${selected?'selected':''} ${ok?'':'locked'}\"><div class=\"charName\">${t.displayName} ${ok?'':'🔒'}</div><div class=\"charMeta\">카드군 · ${t.short}${ok?' · 오픈형 혼합':` · ${lock}`}</div>"
new="const ok=themeBuildUnlocked(id),selected=progress.selectedTheme===id,lock=themeBuildLockText(id),dev=typeof developerModeActive==='function'&&developerModeActive(),development=!t.live;return`<div class=\"charCard ${selected?'selected':''} ${ok?'':'locked'}\"><div class=\"charName\">${t.displayName} ${ok?'':'🔒'}</div><div class=\"charMeta\">카드군 · ${t.short}${development?(dev?' · 개발 중 · DEV 선택 가능':' · 개발 중'):(ok?' · 오픈형 혼합':` · ${lock}`)}</div>"
rep(old,new,'development theme label')

# Replace codex renderer with suit + theme-aware implementation.
start='function renderCodex(){'
end='function renderProgress(){'
new_codex="""function codexThemeFilterId(){return typeof codexFilter==='string'&&codexFilter.startsWith('theme:')?codexFilter.slice(6):null}
function renderCodex(){const dev=typeof developerModeActive==='function'&&developerModeActive(),unlocked=unlockedNamed(),normalUnlocked=typeof baseUnlockedNamed==='function'?baseUnlockedNamed(progress):unlocked,uf=new Set(unlockedFields()),normalFields=new Set(typeof baseUnlockedFields==='function'?baseUnlockedFields(progress):[...uf]),allNamed=Object.keys(NAMED).sort((a,b)=>codexSortKey(a).localeCompare(codexSortKey(b))),allFields=Object.keys(FIELDS),themeFilter=codexThemeFilterId();const total=allNamed.length+allFields.length,open=[...unlocked].filter(id=>NAMED[id]).length+uf.size;document.getElementById('codexUnlockedCount').textContent=open;document.getElementById('codexTotalCount').textContent=total;document.querySelectorAll('#codexTabs [data-codex-filter]').forEach(b=>b.classList.toggle('active',b.dataset.codexFilter===codexFilter));const rows=[];for(const id of allNamed){const n=NAMED[id],slot=namedSlot(id),isJ=id[0]==='J',suit=isJ?'J':slot[0];if(themeFilter){if(n.themeId!==themeFilter)continue}else if(codexFilter!=='all'&&codexFilter!==suit)continue;const access=unlocked.has(id),normallyOpen=normalUnlocked.has(id),labels=unlockLabelsForNamed(id),reveal=access||!!themeFilter;if(reveal){const c=codexCardObj(id),slotText=isJ?'JOKER':`${parseRegularId(slot).rank}${SUIT_SYMBOL[parseRegularId(slot).suit]}`,cls=!normallyOpen?(dev?' devRevealed':' themeLocked'):'',unlockText=normallyOpen?labels.join(' 또는 '):dev?`DEV 공개 · 실제 해금: ${labels.join(' 또는 ')}`:`🔒 미해금 · 해금: ${labels.join(' 또는 ')}`;rows.push(`<div class=\"codexEntry${cls}\"><div class=\"codexMini\">${cardHTML(c)}</div><div><div class=\"codexName\">${n.n}</div><div class=\"codexMeta\">${slotText} · ${isJ?'조커':'네임드'}${n.themeId?` · 카드군 ${themeDef(n.themeId)?.displayName||n.themeId}`:''}${!isJ?` · 경향 ${namedTendencies(id).join(' / ')}`:''}</div><div class=\"codexEffect\">${n.d}</div><div class=\"codexUnlock\">${unlockText}</div></div></div>`)}else{const slotText=isJ?'조커':`${parseRegularId(slot).rank}${SUIT_SYMBOL[parseRegularId(slot).suit]}`;rows.push(`<div class=\"codexEntry locked\"><div class=\"codexLockVisual\">?</div><div><div class=\"codexName\">???</div><div class=\"codexMeta\">미해금 · ${slotText}</div><div class=\"codexUnlock\">해금: ${labels.join(' 또는 ')}</div></div></div>`)}}
if(!themeFilter&&(codexFilter==='all'||codexFilter==='F'))for(const id of allFields){const f=FIELDS[id],access=uf.has(id),normallyOpen=normalFields.has(id),labels=unlockLabelsForField(id),unlockText=normallyOpen?labels.join(' 또는 '):dev?`DEV 공개 · 실제 해금: ${labels.join(' 또는 ')}`:labels.join(' 또는 ');rows.push(access?`<div class=\"codexEntry${!normallyOpen&&dev?' devRevealed':''}\"><div class=\"codexFieldIcon\">필드</div><div><div class=\"codexName violet\">${f.name}</div><div class=\"codexMeta\">공용 필드</div><div class=\"codexEffect\">${f.desc}</div><div class=\"codexUnlock\">${unlockText}</div></div></div>`:`<div class=\"codexEntry locked\"><div class=\"codexLockVisual\">?</div><div><div class=\"codexName\">???</div><div class=\"codexMeta\">미해금</div><div class=\"codexUnlock\">해금: ${labels.join(' 또는 ')}</div></div></div>`)}if(!rows.length&&themeFilter){const t=themeDef(themeFilter);rows.push(`<div class=\"codexThemeEmpty\"><b>${t?.displayName||themeFilter}</b><br>현재 코드에 라이브 구현된 카드가 없습니다.<br>카드군 기반 시스템과 후보 설계는 개발 중이며, 구현된 카드부터 이 탭에 자동으로 나타납니다.</div>`)}document.getElementById('codexGrid').innerHTML=rows.join('')||'<div class=\"meldEmpty\">이 분류에 항목이 없습니다.</div>'}
"""
replace_between(start,end,new_codex,end,'renderCodex')

# Developer overlay event wiring.
binding_marker="document.getElementById('drawDeckBtn').onclick=()=>playerDraw(false);"
if binding_marker not in s: raise SystemExit('missing binding marker')
dev_bindings="""document.getElementById('developerBtn').onclick=openDeveloperPanel;document.getElementById('developerHudBtn').onclick=openDeveloperPanel;document.getElementById('closeDeveloperBtn').onclick=()=>document.getElementById('developerOverlay').classList.remove('show');document.getElementById('developerOverlay').onclick=e=>{if(e.target.id==='developerOverlay')e.currentTarget.classList.remove('show')};document.getElementById('developerToggleBtn').onclick=()=>setDeveloperMode(!developerModeActive());document.getElementById('developerCodexBtn').onclick=()=>{document.getElementById('developerOverlay').classList.remove('show');codexFilter='all';renderCodex();document.getElementById('codexOverlay').classList.add('show')};document.getElementById('developerProgressBtn').onclick=()=>{document.getElementById('developerOverlay').classList.remove('show');renderProgress();document.getElementById('progressOverlay').classList.add('show')};document.getElementById('developerBattleBtn').onclick=()=>{if(!developerModeActive())return;document.getElementById('developerOverlay').classList.remove('show');startBattle()};
"""
s=s.replace(binding_marker,dev_bindings+binding_marker,1)

p.write_text(s,encoding='utf-8')

# Roadmap documents UX/debug infrastructure explicitly.
road=Path('ROADMAP.md')
r=road.read_text(encoding='utf-8')
anchor='### 공통 설계 잠금\n'
if anchor not in r: raise SystemExit('missing roadmap common anchor')
insert=("- [x] 카드 도감에 카드군 전용 필터 추가 — V-SIGNAL / ZERO//SIGHT / POINT//BLANK 탭에서 현재 라이브 구현 카드를 분리해 보고, 카드군 탭에서는 미해금 카드도 카드군·이름·효과를 확인하되 실제 해금 조건은 잠금으로 표시\n"
        "- [x] 별도 개발자 모드 추가 — 현재 구현 콘텐츠의 해금 제한 우회, 개발 중 카드군 선택, 전체 도감 확인을 지원하며 DEV로 시작한 대전은 실제 클리어·레벨·해금 진행도에 반영하지 않음\n")
if '별도 개발자 모드 추가' not in r:
    r=r.replace(anchor,anchor+insert,1)
road.write_text(r,encoding='utf-8')

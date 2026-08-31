from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
def rep(old,new,label,count=1):
    global s
    if s.count(old)<count:
        raise SystemExit(f'missing {label}: {s.count(old)}/{count}')
    s=s.replace(old,new,count)

# Progress picker labels / theme grid.
rep(".progressModal{width:min(460px,100%);padding:10px}.progressSummary{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:8px}",
    ".progressModal{width:min(460px,100%);padding:10px}.progressSummary{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:8px}.pickerLabel{margin:7px 0 5px;font-size:8px;font-weight:900;color:var(--gold)}.themePickerNote{font-size:7px;color:var(--soft);line-height:1.4;margin:5px 0 2px}",
    'theme picker CSS')
old='<div id="progressOverlay" class="overlay"><div class="modal progressModal pixel"><div class="rulesHead"><h2>캐릭터 · 해금</h2><button id="closeProgressBtn" class="pixelBtn closeBtn">닫기</button></div><div class="progressSummary"><div class="progressBox">전체 클리어<br><b id="totalClears">0</b></div><div class="progressBox">공용 해금<br><b id="unlockCount">0</b><span class="sub">개</span></div></div><div id="characterGrid" class="charGrid"></div><div class="unlockGroup">'
new='<div id="progressOverlay" class="overlay"><div class="modal progressModal pixel"><div class="rulesHead"><h2>캐릭터 · 캐릭터군 · 해금</h2><button id="closeProgressBtn" class="pixelBtn closeBtn">닫기</button></div><div class="progressSummary"><div class="progressBox">전체 클리어<br><b id="totalClears">0</b></div><div class="progressBox">공용 해금<br><b id="unlockCount">0</b><span class="sub">개</span></div></div><div class="pickerLabel">캐릭터 경향</div><div id="characterGrid" class="charGrid"></div><div class="pickerLabel">캐릭터군 / 테마</div><div id="themeGroupGrid" class="charGrid"></div><div class="themePickerNote">캐릭터는 덱의 행동 경향을, 캐릭터군은 테마 카드의 출현 우선도를 정합니다. 테마를 골라도 일반·다른 카드와 섞이는 오픈형 덱입니다.</div><div class="unlockGroup">'
rep(old,new,'progress theme picker HTML')
rep('선택 캐릭터로 새 게임','선택 캐릭터/테마로 새 게임','start button label')

# Expose all planned theme identities and build-picker profiles.
old="const THEME_GROUPS=Object.freeze({'v-signal':Object.freeze({id:'v-signal',name:'V-SIGNAL',displayName:'V-SIGNAL',concept:'방송 · 합방 · RAID · 회수 · 러미'})});"
new="const THEME_GROUPS=Object.freeze({'v-signal':Object.freeze({id:'v-signal',name:'V-SIGNAL',displayName:'V-SIGNAL',concept:'방송 · 합방 · RAID · 회수 · 러미'}),'zero-sight':Object.freeze({id:'zero-sight',name:'ZERO//SIGHT',displayName:'ZERO//SIGHT',concept:'표적 · 관측 · 준비 · 정밀 타격'}),'point-blank':Object.freeze({id:'point-blank',name:'POINT//BLANK',displayName:'POINT//BLANK',concept:'접전 · 돌입 · 회수 · 교대'})});\nconst THEME_BUILD_PROFILES=Object.freeze({mixed:Object.freeze({id:'mixed',displayName:'혼합',short:'자유 혼합',desc:'해금된 모든 네임드가 캐릭터 경향에 따라 섞입니다.',themeId:null,live:true}),\n 'v-signal':Object.freeze({id:'v-signal',displayName:'V-SIGNAL',short:'방송 콤보',desc:'방송·회수·세트/런 연결 카드를 우선 편성합니다. 일반 카드도 함께 섞입니다.',themeId:'v-signal',live:true}),\n 'zero-sight':Object.freeze({id:'zero-sight',displayName:'ZERO//SIGHT',short:'정밀 표적',desc:'표적·관측·준비형 카드군. 기반 시스템 구현 중입니다.',themeId:'zero-sight',live:false}),\n 'point-blank':Object.freeze({id:'point-blank',displayName:'POINT//BLANK',short:'근접 교대',desc:'접전·돌입·회수·교대 카드군. 기반 시스템 구현 예정입니다.',themeId:'point-blank',live:false})});"
rep(old,new,'theme build profiles')

# Persist theme picker, backwards compatible with old saves.
old="function defaultProgress(){return{totalClears:0,selectedChar:'wanderer',tutorialPromptSeen:false,tutorialCompleted:false,chars:{wanderer:0,collector:0,salvager:0,jester:0}}}"
new="function defaultProgress(){return{totalClears:0,selectedChar:'wanderer',selectedTheme:'mixed',tutorialPromptSeen:false,tutorialCompleted:false,chars:{wanderer:0,collector:0,salvager:0,jester:0}}}"
rep(old,new,'default selected theme')
old="return{totalClears:Number.isFinite(tc)&&tc>=0?Math.floor(tc):0,selectedChar:Object.prototype.hasOwnProperty.call(CHARACTERS,x.selectedChar)?x.selectedChar:'wanderer',tutorialPromptSeen:typeof x.tutorialPromptSeen==='boolean'?x.tutorialPromptSeen:false,tutorialCompleted:typeof x.tutorialCompleted==='boolean'?x.tutorialCompleted:false,chars}}"
new="return{totalClears:Number.isFinite(tc)&&tc>=0?Math.floor(tc):0,selectedChar:Object.prototype.hasOwnProperty.call(CHARACTERS,x.selectedChar)?x.selectedChar:'wanderer',selectedTheme:Object.prototype.hasOwnProperty.call(THEME_BUILD_PROFILES,x.selectedTheme)?x.selectedTheme:'mixed',tutorialPromptSeen:typeof x.tutorialPromptSeen==='boolean'?x.tutorialPromptSeen:false,tutorialCompleted:typeof x.tutorialCompleted==='boolean'?x.tutorialCompleted:false,chars}}"
rep(old,new,'normalize selected theme')

# Theme availability and deck composition helpers. V-SIGNAL becomes selectable once at least one live card is unlocked.
anchor="function charUnlocked(id,p=progress){const unlock=CHARACTER_UNLOCK[id];return typeof unlock==='function'&&!!unlock(p)}\n"
insert=anchor+"function themeBuildUnlocked(id,p=progress){const profile=THEME_BUILD_PROFILES[id];if(!profile)return false;if(id==='mixed')return true;if(!profile.live)return false;const open=unlockedNamed(p);for(const cardId of open)if(NAMED[cardId]?.themeId===profile.themeId)return true;return false}\nfunction themeBuildLockText(id){if(id==='v-signal')return'테마 카드 해금 필요 · 전체 2클리어부터';return'개발 중'}\n"
rep(anchor,insert,'theme build availability')
old="function cardWeightForChar(id,charId){const ws=CHARACTERS[charId]?.weights||{},t=TENDENCY_BY_TAG[NAMED[id]?.t]||['mix'];return 1+t.reduce((a,k)=>a+(ws[k]||0),0)}"
new="function cardWeightForChar(id,charId,themeId='mixed'){const ws=CHARACTERS[charId]?.weights||{},t=TENDENCY_BY_TAG[NAMED[id]?.t]||['mix'],themeBonus=themeId!=='mixed'&&NAMED[id]?.themeId===themeId?4:0;return 1+t.reduce((a,k)=>a+(ws[k]||0),0)+themeBonus}\nfunction chooseNamedForBuild(unlocked,charId,themeId='mixed'){const preferred=themeId==='mixed'?[]:unlocked.filter(id=>NAMED[id]?.themeId===themeId),themeChosen=weightedVariantSample(preferred,Math.min(4,preferred.length),id=>cardWeightForChar(id,charId,themeId)),used=new Set(themeChosen.map(namedSlot)),rest=unlocked.filter(id=>!used.has(namedSlot(id))),fill=weightedVariantSample(rest,Math.max(0,9-themeChosen.length),id=>cardWeightForChar(id,charId,themeId));return themeChosen.concat(fill)}"
rep(old,new,'theme-aware named build')
old="function makeDeck(owner,charId=progress.selectedChar){\n const unlocked=[...unlockedNamed()].filter(id=>id[0]!=='J'&&NAMED[id]);\n const namedChosen=weightedVariantSample(unlocked,9,id=>cardWeightForChar(id,charId));"
new="function makeDeck(owner,charId=progress.selectedChar,themeId=owner==='player'?(progress.selectedTheme||'mixed'):'mixed'){\n const unlocked=[...unlockedNamed()].filter(id=>id[0]!=='J'&&NAMED[id]);\n const buildTheme=themeBuildUnlocked(themeId)?themeId:'mixed';\n const namedChosen=chooseNamedForBuild(unlocked,charId,buildTheme);"
rep(old,new,'theme-aware makeDeck')
old="const jokers=[...unlockedNamed()].filter(id=>id[0]==='J'&&NAMED[id]);const jid=weightedPick(jokers,id=>cardWeightForChar(id,charId))||'J1';"
new="const jokers=[...unlockedNamed()].filter(id=>id[0]==='J'&&NAMED[id]);const jid=weightedPick(jokers,id=>cardWeightForChar(id,charId,buildTheme))||'J1';"
rep(old,new,'theme-aware joker weight')

# Surface selected theme on start screen and combat badge; pass it into the actual player deck build.
old="function renderStartScreen(){const el=document.getElementById('startMeta');if(!el)return;const id=charUnlocked(progress.selectedChar)?progress.selectedChar:'wanderer',ch=CHARACTERS[id]||CHARACTERS.wanderer;el.textContent=`${ch.name} Lv.${charLevel(progress,id)} · 전체 ${progress.totalClears}클리어`;"
new="function renderStartScreen(){const el=document.getElementById('startMeta');if(!el)return;const id=charUnlocked(progress.selectedChar)?progress.selectedChar:'wanderer',ch=CHARACTERS[id]||CHARACTERS.wanderer,themeId=themeBuildUnlocked(progress.selectedTheme)?progress.selectedTheme:'mixed',theme=THEME_BUILD_PROFILES[themeId]||THEME_BUILD_PROFILES.mixed;el.textContent=`${ch.name} Lv.${charLevel(progress,id)} · ${theme.displayName} · 전체 ${progress.totalClears}클리어`;"
rep(old,new,'start screen theme')
old="function newGame(mode='battle'){state.sessionMode=mode;state.battleId++;uidSeq=1;if(!charUnlocked(progress.selectedChar))progress.selectedChar='wanderer';const enemyChars=Object.keys(CHARACTERS).filter(k=>charUnlocked(k));const enemyChar=enemyChars[Math.floor(Math.random()*enemyChars.length)]||'wanderer';const makeSide=(owner,charId)=>({hp:CORE_HP,maxHp:CORE_HP,cores:CORE_COUNT,shield:0,status:blankStatus(),lastDamageTaken:0,lastDetonateTaken:0,detonateMemory:0,charId,flags:"
new="function newGame(mode='battle'){state.sessionMode=mode;state.battleId++;uidSeq=1;if(!charUnlocked(progress.selectedChar))progress.selectedChar='wanderer';if(!themeBuildUnlocked(progress.selectedTheme))progress.selectedTheme='mixed';const enemyChars=Object.keys(CHARACTERS).filter(k=>charUnlocked(k));const enemyChar=enemyChars[Math.floor(Math.random()*enemyChars.length)]||'wanderer';const makeSide=(owner,charId,themeId='mixed')=>({hp:CORE_HP,maxHp:CORE_HP,cores:CORE_COUNT,shield:0,status:blankStatus(),lastDamageTaken:0,lastDetonateTaken:0,detonateMemory:0,charId,themeId,flags:"
rep(old,new,'newGame side theme')
old="deck:makeDeck(owner,charId),hand:[],spent:[],melds:[]});state.player=makeSide('player',progress.selectedChar);state.enemy=makeSide('enemy',enemyChar);"
new="deck:makeDeck(owner,charId,themeId),hand:[],spent:[],melds:[]});state.player=makeSide('player',progress.selectedChar,progress.selectedTheme);state.enemy=makeSide('enemy',enemyChar,'mixed');"
rep(old,new,'newGame deck theme')
old="log(`${CHARACTERS[state.player.charId].name} 경향의 혼합 시작덱. 개인 덱은 서로 공유하지 않습니다.`,'important');"
new="log(`${CHARACTERS[state.player.charId].name} 경향 · ${THEME_BUILD_PROFILES[state.player.themeId]?.displayName||'혼합'} 카드군의 오픈형 시작덱. 개인 덱은 서로 공유하지 않습니다.`,'important');"
rep(old,new,'battle theme log')
old="document.getElementById('charBadge').innerHTML=`<span class=\"gold\">◆</span> ${ch.name} Lv.${charLevel(progress,p.charId)}`;"
new="const buildTheme=THEME_BUILD_PROFILES[p.themeId]||THEME_BUILD_PROFILES.mixed;document.getElementById('charBadge').innerHTML=`<span class=\"gold\">◆</span> ${ch.name} Lv.${charLevel(progress,p.charId)} <span class=\"sub\">· ${buildTheme.displayName}</span>`;"
rep(old,new,'HUD theme badge')

# Render and select the theme group below character tendencies.
old="function renderProgress(){document.getElementById('totalClears').textContent=progress.totalClears;const unlocked=unlockedNamed(),fields=unlockedFields();document.getElementById('unlockCount').textContent=unlocked.size+fields.length;const cg=document.getElementById('characterGrid');cg.innerHTML=Object.entries(CHARACTERS).map(([id,c])=>{"
new="function renderProgress(){document.getElementById('totalClears').textContent=progress.totalClears;const unlocked=unlockedNamed(),fields=unlockedFields();document.getElementById('unlockCount').textContent=unlocked.size+fields.length;const cg=document.getElementById('characterGrid');cg.innerHTML=Object.entries(CHARACTERS).map(([id,c])=>{"
# Deliberately keep prefix unchanged; theme insertion is after the character button handler.
if old not in s: raise SystemExit('missing renderProgress prefix')
old2="cg.querySelectorAll('[data-char]').forEach(b=>b.onclick=()=>{progress.selectedChar=b.dataset.char;saveProgress();renderProgress();renderStartScreen();render()});const chips=[];"
new2="cg.querySelectorAll('[data-char]').forEach(b=>b.onclick=()=>{progress.selectedChar=b.dataset.char;saveProgress();renderProgress();renderStartScreen();render()});const tg=document.getElementById('themeGroupGrid');if(tg){tg.innerHTML=Object.entries(THEME_BUILD_PROFILES).map(([id,t])=>{const ok=themeBuildUnlocked(id),selected=progress.selectedTheme===id,lock=themeBuildLockText(id);return`<div class=\"charCard ${selected?'selected':''} ${ok?'':'locked'}\"><div class=\"charName\">${t.displayName} ${ok?'':'🔒'}</div><div class=\"charMeta\">카드군 · ${t.short}${ok?' · 오픈형 혼합':` · ${lock}`}</div><div class=\"charPassive\">${t.desc}</div><button class=\"pixelBtn ${selected?'primary':''}\" data-theme-build=\"${id}\" ${ok?'':'disabled'}>${selected?'선택됨':'선택'}</button></div>`}).join('');tg.querySelectorAll('[data-theme-build]').forEach(b=>b.onclick=()=>{if(!themeBuildUnlocked(b.dataset.themeBuild))return;progress.selectedTheme=b.dataset.themeBuild;saveProgress();renderProgress();renderStartScreen();render()})}const chips=[];"
rep(old2,new2,'render theme group picker')

p.write_text(s,encoding='utf-8')

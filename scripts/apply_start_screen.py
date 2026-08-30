from pathlib import Path


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly 1 match, got {count}")
    return text.replace(old, new, 1)

p = Path('index.html')
s = p.read_text(encoding='utf-8')

css = r'''
/* UX1 P1 · start screen shell */
.startScreen{position:fixed;z-index:1500;inset:0;width:min(100vw,480px);margin:auto;background:radial-gradient(circle at 50% 0%,#224750 0,transparent 36%),linear-gradient(180deg,#151b28,#090c12 70%);overflow:auto;padding:max(18px,env(safe-area-inset-top)) 14px max(18px,env(safe-area-inset-bottom));display:flex;align-items:center;justify-content:center}.startScreen.hidden{display:none}.startShell{width:min(100%,420px);display:flex;flex-direction:column;gap:12px}.startHero{text-align:center;padding:22px 14px 18px;background:#111925;border:2px solid #000;box-shadow:0 0 0 2px #40516f inset,5px 5px 0 #0007}.startLogo{font-size:30px;font-weight:900;letter-spacing:-2px}.startLogo b{color:var(--cyan)}.startPitch{margin:10px auto 0;max-width:320px;font-size:10px;line-height:1.55;color:#d8e1ef}.startMeta{margin-top:12px;font-size:8px;color:var(--soft)}.startMenu{display:grid;gap:8px}.startMenuBtn{width:100%;min-height:58px;padding:10px 12px;text-align:left;display:flex;align-items:center;justify-content:space-between;gap:12px}.startMenuBtn>span:first-child{font-size:13px;font-weight:900}.startMenuBtn small{display:block;margin-top:3px;font-size:7px;line-height:1.35;color:var(--soft);font-weight:400}.startMenuBtn .menuState{font-size:8px;color:var(--gold);white-space:nowrap}.startMenuBtn:disabled .menuState{color:#7e899c}.startAux{display:grid;grid-template-columns:1fr 1fr;gap:7px}.startAux .pixelBtn{font-size:8px;padding:8px}.startFoot{text-align:center;font-size:7px;line-height:1.5;color:#71809a}.startResumeNote{padding:7px 8px;border:1px solid #31415a;background:#0e1520;font-size:7px;line-height:1.45;color:#aebbd0;text-align:center}
@media(max-width:390px){.startScreen{padding:12px 10px}.startShell{gap:9px}.startHero{padding:18px 10px 14px}.startLogo{font-size:25px}.startPitch{font-size:9px}.startMenuBtn{min-height:52px;padding:8px 10px}.startMenuBtn>span:first-child{font-size:11px}.startAux .pixelBtn{font-size:7px;padding:7px 5px}}
'''
s = replace_once(s, '\n</style>', css + '\n</style>', 'insert start screen styles')

start_html = r'''<div id="startScreen" class="startScreen" aria-label="RUMMY//DUEL 시작 메뉴">
 <div class="startShell">
  <section class="startHero" aria-labelledby="startTitle">
   <div id="startTitle" class="startLogo">RUMMY<b>//DUEL</b></div>
   <div class="startPitch">세트와 런으로 폭탄을 키워 스위치를 넘기는 1:1 러미 배틀</div>
   <div id="startMeta" class="startMeta">유랑자 Lv.1 · 전체 0클리어</div>
  </section>
  <nav class="startMenu" aria-label="주 메뉴">
   <button id="battleStartBtn" class="pixelBtn primary startMenuBtn" type="button"><span>대전 시작<small>현재 캐릭터로 새 대전을 시작합니다.</small></span><span class="menuState">PLAY</span></button>
   <button id="tutorialStartBtn" class="pixelBtn startMenuBtn" type="button" disabled aria-disabled="true"><span>튜토리얼<small>기본 조작부터 스위치와 러미까지 연습합니다.</small></span><span class="menuState">준비 중</span></button>
   <button id="startCodexBtn" class="pixelBtn startMenuBtn" type="button"><span>카드 도감<small>해금한 네임드·조커·필드를 확인합니다.</small></span><span class="menuState">OPEN</span></button>
   <button id="settingsBtn" class="pixelBtn startMenuBtn" type="button" disabled aria-disabled="true"><span>설정<small>게임 표시와 편의 옵션을 정리할 예정입니다.</small></span><span class="menuState">준비 중</span></button>
  </nav>
  <div class="startAux"><button id="startProgressBtn" class="pixelBtn" type="button">캐릭터·해금</button><button id="startRulesBtn" class="pixelBtn" type="button">규칙·용어</button></div>
  <div id="startResumeNote" class="startResumeNote">튜토리얼은 제작 중입니다. 현재는 대전·도감·규칙을 이용할 수 있습니다.</div>
  <div class="startFoot">RUMMY//DUEL · 모바일 우선 프로토타입</div>
 </div>
</div>
'''
s = replace_once(s, '<div id="app">\n', '<div id="app">\n' + start_html, 'insert start screen markup')

s = replace_once(
    s,
    '<button id="rulesBtn" class="pixelBtn">규칙·용어</button></div></header>',
    '<button id="rulesBtn" class="pixelBtn">규칙·용어</button><button id="homeBtn" class="pixelBtn">메인</button></div></header>',
    'add battle home button',
)

s = replace_once(
    s,
    '<div class="modalBtns"><button id="againBtn" class="pixelBtn primary">다시 하기</button></div>',
    '<div class="modalBtns"><button id="againBtn" class="pixelBtn primary">다시 하기</button><button id="resultHomeBtn" class="pixelBtn">메인으로</button></div>',
    'add result home button',
)

s = replace_once(
    s,
    "function defaultProgress(){return{totalClears:0,selectedChar:'wanderer',chars:{wanderer:0,collector:0,salvager:0,jester:0}}}",
    "function defaultProgress(){return{totalClears:0,selectedChar:'wanderer',tutorialPromptSeen:false,tutorialCompleted:false,chars:{wanderer:0,collector:0,salvager:0,jester:0}}}",
    'extend progress defaults',
)

s = replace_once(
    s,
    "function normalizeProgress(x){const base=defaultProgress();if(!x||typeof x!=='object')return base;const chars={...base.chars};for(const id of Object.keys(chars)){const n=Number(x.chars?.[id]);if(Number.isFinite(n)&&n>=0)chars[id]=Math.floor(n)}const tc=Number(x.totalClears);return{totalClears:Number.isFinite(tc)&&tc>=0?Math.floor(tc):0,selectedChar:Object.prototype.hasOwnProperty.call(CHARACTERS,x.selectedChar)?x.selectedChar:'wanderer',chars}}",
    "function normalizeProgress(x){const base=defaultProgress();if(!x||typeof x!=='object')return base;const chars={...base.chars};for(const id of Object.keys(chars)){const n=Number(x.chars?.[id]);if(Number.isFinite(n)&&n>=0)chars[id]=Math.floor(n)}const tc=Number(x.totalClears);return{totalClears:Number.isFinite(tc)&&tc>=0?Math.floor(tc):0,selectedChar:Object.prototype.hasOwnProperty.call(CHARACTERS,x.selectedChar)?x.selectedChar:'wanderer',tutorialPromptSeen:typeof x.tutorialPromptSeen==='boolean'?x.tutorialPromptSeen:false,tutorialCompleted:typeof x.tutorialCompleted==='boolean'?x.tutorialCompleted:false,chars}}",
    'normalize tutorial progress flags',
)

s = replace_once(s, 'const state={player:null,enemy:null,', "const state={sessionMode:'menu',player:null,enemy:null,", 'add session mode')

routing = r'''function renderStartScreen(){const el=document.getElementById('startMeta');if(!el)return;const id=charUnlocked(progress.selectedChar)?progress.selectedChar:'wanderer',ch=CHARACTERS[id]||CHARACTERS.wanderer;el.textContent=`${ch.name} Lv.${charLevel(progress,id)} · 전체 ${progress.totalClears}클리어`}
function showStartScreen(){state.sessionMode='menu';for(const id of['overlay','rulesOverlay','progressOverlay','codexOverlay'])document.getElementById(id)?.classList.remove('show');document.getElementById('startScreen')?.classList.remove('hidden');document.body.classList.add('menu-open');renderStartScreen()}
function hideStartScreen(){document.getElementById('startScreen')?.classList.add('hidden');document.body.classList.remove('menu-open')}
function startBattle(){state.sessionMode='battle';hideStartScreen();document.getElementById('overlay')?.classList.remove('show');newGame()}
'''
s = replace_once(s, 'function newGame(){uidSeq=1;', routing + "function newGame(){state.sessionMode='battle';uidSeq=1;", 'insert menu routing')

s = replace_once(
    s,
    "cg.querySelectorAll('[data-char]').forEach(b=>b.onclick=()=>{progress.selectedChar=b.dataset.char;saveProgress();renderProgress();render()});",
    "cg.querySelectorAll('[data-char]').forEach(b=>b.onclick=()=>{progress.selectedChar=b.dataset.char;saveProgress();renderProgress();renderStartScreen();render()});",
    'refresh start metadata after character selection',
)

s = replace_once(
    s,
    "document.getElementById('startWithCharBtn').onclick=()=>{document.getElementById('progressOverlay').classList.remove('show');document.getElementById('overlay').classList.remove('show');newGame()};",
    "document.getElementById('startWithCharBtn').onclick=()=>{document.getElementById('progressOverlay').classList.remove('show');startBattle()};",
    'route character start through battle entry',
)

s = replace_once(
    s,
    "document.getElementById('resetProgressBtn').onclick=()=>{if(confirm('캐릭터 레벨과 모든 해금 진행을 초기화할까요?')){progress=defaultProgress();saveProgress();renderProgress();newGame()}};renderProgress();newGame();",
    "document.getElementById('resetProgressBtn').onclick=()=>{if(confirm('캐릭터 레벨과 모든 해금 진행을 초기화할까요?')){progress=defaultProgress();saveProgress();renderProgress();renderStartScreen();if(state.sessionMode==='battle')newGame()}};document.getElementById('battleStartBtn').onclick=startBattle;document.getElementById('startCodexBtn').onclick=()=>{renderCodex();document.getElementById('codexOverlay').classList.add('show')};document.getElementById('startProgressBtn').onclick=()=>{renderProgress();document.getElementById('progressOverlay').classList.add('show')};document.getElementById('startRulesBtn').onclick=()=>document.getElementById('rulesOverlay').classList.add('show');document.getElementById('homeBtn').onclick=showStartScreen;document.getElementById('resultHomeBtn').onclick=showStartScreen;renderProgress();showStartScreen();",
    'wire start screen and stop auto battle',
)

p.write_text(s, encoding='utf-8')

rp = Path('ROADMAP.md')
r = rp.read_text(encoding='utf-8')
updates = {
    '- [ ] 신규 시작창 UI 설계': '- [x] 신규 시작창 UI 설계',
    '- [ ] `대전 시작 / 튜토리얼 / 카드 도감 / 설정` 구조 정리': '- [x] `대전 시작 / 튜토리얼 / 카드 도감 / 설정` 구조 정리',
    '- [ ] 미구현 메뉴를 비활성/`준비 중` 상태로 구분': '- [x] 미구현 메뉴를 비활성/`준비 중` 상태로 구분',
    '- [ ] 모바일 시작창 대응': '- [x] 모바일 시작창 대응',
    '- [ ] 기존 progress 저장 스키마에 튜토리얼 상태 저장': '- [x] 기존 progress 저장 스키마에 튜토리얼 상태 저장',
    '- [ ] 시작창 메뉴 한국어화': '- [x] 시작창 메뉴 한국어화',
}
for old, new in updates.items():
    if old not in r:
        raise SystemExit(f'roadmap marker missing: {old}')
    r = r.replace(old, new, 1)
r = r.replace(
    '2. UX1 P1: build the start-screen shell, first-run prompt, tutorial save flags and shared tutorial controller, then implement basic controls → 세트 → 런 → 붙이기 → 스위치 → 러미 with fixed states.',
    '2. UX1 P1: start-screen shell/menu/tutorial save flags are live; next build the first-run prompt + shared tutorial controller, then basic controls → 세트 → 런 → 붙이기 → 스위치 → 러미 with fixed states.',
    1,
)
rp.write_text(r, encoding='utf-8')

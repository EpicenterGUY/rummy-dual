from pathlib import Path

index=Path('index.html')
road=Path('ROADMAP.md')
s=index.read_text()
r=road.read_text()

# Expose presentation-only theme hooks. Keep gameplay/data semantics unchanged.
old="function renderStartScreen(){const el=document.getElementById('startMeta');if(!el)return;const id=charUnlocked(progress.selectedChar)?progress.selectedChar:'wanderer',ch=CHARACTERS[id]||CHARACTERS.wanderer,themeId=themeBuildUnlocked(progress.selectedTheme)?progress.selectedTheme:'mixed',theme=THEME_BUILD_PROFILES[themeId]||THEME_BUILD_PROFILES.mixed;el.textContent="
new="function renderStartScreen(){const el=document.getElementById('startMeta');if(!el)return;const id=charUnlocked(progress.selectedChar)?progress.selectedChar:'wanderer',ch=CHARACTERS[id]||CHARACTERS.wanderer,themeId=themeBuildUnlocked(progress.selectedTheme)?progress.selectedTheme:'mixed',theme=THEME_BUILD_PROFILES[themeId]||THEME_BUILD_PROFILES.mixed,startScreen=document.getElementById('startScreen');if(startScreen)startScreen.dataset.theme=themeId;el.textContent="
if s.count(old)!=1:
    raise SystemExit(f'renderStartScreen hook mismatch: {s.count(old)}')
s=s.replace(old,new,1)

old="return`<div class=\"charCard ${selected?'selected':''} ${ok?'':'locked'}\"><div class=\"charName\">${t.displayName} ${ok?'':'🔒'}</div>"
new="return`<div class=\"charCard ${selected?'selected':''} ${ok?'':'locked'}\" data-theme-card=\"${id}\"><div class=\"charName\">${t.displayName} ${ok?'':'🔒'}</div>"
if s.count(old)!=1:
    raise SystemExit(f'theme picker card hook mismatch: {s.count(old)}')
s=s.replace(old,new,1)

old="function cardHTML(c){const suit=SUIT_SYMBOL[c.suit],red=(c.suit==='H'||c.suit==='D')?'suitRed':'',rank=c.suit==='J'?'J':c.rank;return`<div class=\"card ${c.named?'named':''} ${c.suit==='J'?'joker':''}\">"
new="function cardHTML(c){const suit=SUIT_SYMBOL[c.suit],red=(c.suit==='H'||c.suit==='D')?'suitRed':'',rank=c.suit==='J'?'J':c.rank,themeClass=c.themeId?`theme-${c.themeId}`:'';return`<div class=\"card ${c.named?'named':''} ${c.suit==='J'?'joker':''} ${themeClass}\">"
if s.count(old)!=1:
    raise SystemExit(f'cardHTML theme class hook mismatch: {s.count(old)}')
s=s.replace(old,new,1)

old="function render(){const p=state.player,e=state.enemy;if(!p||!e)return;const ch=CHARACTERS[p.charId]||CHARACTERS.wanderer;const buildTheme=THEME_BUILD_PROFILES[p.themeId]||THEME_BUILD_PROFILES.mixed;document.getElementById('charBadge').innerHTML="
new="function render(){const p=state.player,e=state.enemy;if(!p||!e)return;const ch=CHARACTERS[p.charId]||CHARACTERS.wanderer;const buildTheme=THEME_BUILD_PROFILES[p.themeId]||THEME_BUILD_PROFILES.mixed,app=document.getElementById('app');if(app)app.dataset.theme=p.themeId||'mixed';document.getElementById('charBadge').innerHTML="
if s.count(old)!=1:
    raise SystemExit(f'render app theme hook mismatch: {s.count(old)}')
s=s.replace(old,new,1)

marker='/* UI3 P3 · restrained theme accent layer */'
if marker in s:
    raise SystemExit('theme accent block already exists')
anchor='</style>'
block=r'''

/* UI3 P3 · restrained theme accent layer */
:root{--theme-vsignal:#8b7788;--theme-zero:#718892;--theme-pointblank:#927565}
/* Theme identity is an accent only: no theme-specific page background, glow, animation, or panel replacement. */
.startScreen[data-theme="v-signal"] .startHero:after{background:linear-gradient(90deg,transparent,#9f875f 20%,var(--theme-vsignal) 72%,transparent)}
.startScreen[data-theme="zero-sight"] .startHero:after{background:linear-gradient(90deg,transparent,#9f875f 20%,var(--theme-zero) 72%,transparent)}
.startScreen[data-theme="point-blank"] .startHero:after{background:linear-gradient(90deg,transparent,#9f875f 20%,var(--theme-pointblank) 72%,transparent)}
#app[data-theme="v-signal"] #charBadge{border-color:#746777}#app[data-theme="zero-sight"] #charBadge{border-color:#60747c}#app[data-theme="point-blank"] #charBadge{border-color:#786357}
#themeGroupGrid .charCard[data-theme-card]{border-left-width:3px}#themeGroupGrid .charCard[data-theme-card="mixed"]{border-left-color:#566267}#themeGroupGrid .charCard[data-theme-card="v-signal"]{border-left-color:var(--theme-vsignal)}#themeGroupGrid .charCard[data-theme-card="zero-sight"]{border-left-color:var(--theme-zero)}#themeGroupGrid .charCard[data-theme-card="point-blank"]{border-left-color:var(--theme-pointblank)}
#themeGroupGrid .charCard.selected[data-theme-card="v-signal"]{background:#342f35}#themeGroupGrid .charCard.selected[data-theme-card="zero-sight"]{background:#29363b}#themeGroupGrid .charCard.selected[data-theme-card="point-blank"]{background:#37312d}
.codexTabs [data-codex-filter="theme:v-signal"]{border-bottom-color:var(--theme-vsignal)}.codexTabs [data-codex-filter="theme:zero-sight"]{border-bottom-color:var(--theme-zero)}.codexTabs [data-codex-filter="theme:point-blank"]{border-bottom-color:var(--theme-pointblank)}
.card.theme-v-signal.named:after{background:var(--theme-vsignal);border-color:#6e606c;color:#f1e7ed}.card.theme-zero-sight.named:after{background:var(--theme-zero);border-color:#596d75;color:#e4eef0}.card.theme-point-blank.named:after{background:var(--theme-pointblank);border-color:#725d52;color:#f1e6df}
'''
s=s.replace(anchor,block+'\n'+anchor,1)

old='- [ ] V-SIGNAL 등 테마군은 기본 UI 위에 테마 포인트만 얹고 카지노형 네온 남발 금지'
new='- [x] V-SIGNAL 등 테마군은 기본 UI 위에 테마 포인트만 얹고 카지노형 네온 남발 금지 — 공통 전술 보드/카드 표면은 유지하고 V-SIGNAL 자주·ZERO-SIGHT 청회·POINT-BLANK 황동 포인트를 시작 밑줄, HUD 배지, 테마 선택 카드, 네임드 ◆ 표식에만 제한. 테마별 배경 교체·광원·애니메이션은 사용하지 않음'
if r.count(old)!=1:
    raise SystemExit(f'ROADMAP theme accent anchor mismatch: {r.count(old)}')
r=r.replace(old,new,1)
index.write_text(s)
road.write_text(r)
print('restrained theme accent layer installed')

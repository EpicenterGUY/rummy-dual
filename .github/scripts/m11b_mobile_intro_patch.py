from pathlib import Path

p=Path('index.html')
s=p.read_text()

css='''

/* M11B UI3 · asymmetric-rank first exposure / mobile clarity */
.asymRankIntro{display:grid;grid-template-columns:auto minmax(0,1fr) auto;align-items:center;gap:7px;margin-top:7px;padding:7px 8px;border:1px solid #806b43;border-left:3px solid #b28a4c;border-radius:7px;background:#25261f;color:#e8dfc9;font-size:7px;line-height:1.45}
.asymRankIntro[hidden]{display:none}.asymRankIntroIcon{width:28px;height:28px;display:grid;place-items:center;border:1px solid #806b43;border-radius:50%;background:#eee3c8;color:#604d2d;font-size:13px;font-weight:900}.asymRankIntroCopy{min-width:0;overflow-wrap:anywhere}.asymRankIntroCopy b{display:block;color:#f0d395;font-size:8px;margin-bottom:1px}.asymRankIntroCopy span{display:block;color:#c8c4b8}.asymRankIntro .pixelBtn{padding:5px 7px;font-size:7px;white-space:nowrap}
@media(max-width:390px){.asymRankIntro{grid-template-columns:28px minmax(0,1fr);gap:6px;padding:7px}.asymRankIntro .pixelBtn{grid-column:1/-1;width:100%;min-height:34px;white-space:normal}.asymRankIntroCopy b{font-size:7.5px}.asymRankIntroCopy span{font-size:6.5px;line-height:1.5}}
'''
if '/* M11B UI3 · asymmetric-rank first exposure / mobile clarity */' not in s:
    s=s.replace('\n</style>',css+'\n</style>',1)

hand_anchor='''<section class="handZone pixel"><div class="handTop"><div><div class="handTitle">내 손패 <span id="playerHandCount" class="cyan">8</span></div><div class="handSub">세트·런을 만들거나 공개 조합에 붙여 스위치를 넘기세요.</div></div><div class="badge">러미 <b id="rummyCount" class="gold">0</b></div></div><div id="hand" class="hand"></div>'''
hand_new='''<section class="handZone pixel"><div class="handTop"><div><div class="handTitle">내 손패 <span id="playerHandCount" class="cyan">8</span></div><div class="handSub">세트·런을 만들거나 공개 조합에 붙여 스위치를 넘기세요.</div></div><div class="badge">러미 <b id="rummyCount" class="gold">0</b></div></div><div id="asymRankIntro" class="asymRankIntro" hidden aria-live="polite"><div class="asymRankIntroIcon" aria-hidden="true">↕</div><div class="asymRankIntroCopy"><b id="asymRankIntroTitle">두 숫자 카드</b><span id="asymRankIntroText">위·아래 숫자는 오타가 아닙니다. 조합에 사용할 때 둘 중 하나를 고릅니다.</span></div><button id="asymRankIntroClose" class="pixelBtn" type="button">확인</button></div><div id="hand" class="hand"></div>'''
if hand_anchor in s:
    s=s.replace(hand_anchor,hand_new,1)
elif 'id="asymRankIntro"' not in s:
    raise SystemExit('hand intro insertion anchor missing')

old="function defaultProgress(){return{totalClears:0,selectedChar:'wanderer',selectedTheme:'mixed',tutorialPromptSeen:false,tutorialCompleted:false,deckBuild:defaultDeckBuild(),chars:{wanderer:0,collector:0,salvager:0,jester:0}}}"
new="function defaultProgress(){return{totalClears:0,selectedChar:'wanderer',selectedTheme:'mixed',tutorialPromptSeen:false,tutorialCompleted:false,asymmetricRankIntroSeen:false,deckBuild:defaultDeckBuild(),chars:{wanderer:0,collector:0,salvager:0,jester:0}}}"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('defaultProgress anchor missing')

old="tutorialCompleted:typeof x.tutorialCompleted==='boolean'?x.tutorialCompleted:false,deckBuild:normalizeDeckBuild(x.deckBuild),chars}"
new="tutorialCompleted:typeof x.tutorialCompleted==='boolean'?x.tutorialCompleted:false,asymmetricRankIntroSeen:typeof x.asymmetricRankIntroSeen==='boolean'?x.asymmetricRankIntroSeen:false,deckBuild:normalizeDeckBuild(x.deckBuild),chars}"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('normalizeProgress anchor missing')

anchor="function rankPrototypeDetailText(c){const p=cardRankPresentation(c);if(!p.asymmetric)return'';const suit=SUIT_SYMBOL[c.suit]||'',use=p.locked?`${p.activeRank}${p.orientation==='bottom'?' ↓ 아래':' ↑ 위'}`:'미확정';return` · 원본 슬롯 ${p.baseRank}${suit} · 인쇄 ${p.topRank}/${p.bottomRank} · 사용값 ${use}`}\n"
helpers='''function asymmetricRankIntroCard(){return state.player?.hand?.find(c=>isAsymmetricRankCard(c))||null}
function asymmetricRankRuleCopy(c=null){const p=c?cardRankPresentation(c):null,ranks=p?.asymmetric?`${p.topRank}/${p.bottomRank}`:'X/Y';return`위·아래 숫자 ${ranks}는 오타가 아닙니다. 세트·런을 만들거나 붙일 때 두 인쇄값 중 하나를 사용값으로 직접 고릅니다. 선택한 값은 공개 조합에 있는 동안 고정되고, 손으로 돌아오면 다시 선택할 수 있습니다.`}
function shouldShowAsymmetricRankIntro(){return !!(state.player&&!progress.asymmetricRankIntroSeen&&asymmetricRankIntroCard())}
function renderAsymmetricRankIntro(){const el=document.getElementById('asymRankIntro');if(!el)return;const c=asymmetricRankIntroCard(),show=!!c&&!progress.asymmetricRankIntroSeen;el.hidden=!show;if(!show)return;const p=cardRankPresentation(c),title=document.getElementById('asymRankIntroTitle'),text=document.getElementById('asymRankIntroText');if(title)title.textContent=`두 숫자 카드 · ${p.topRank}/${p.bottomRank}`;if(text)text.textContent=asymmetricRankRuleCopy(c)}
function dismissAsymmetricRankIntro(){if(progress.asymmetricRankIntroSeen)return false;progress.asymmetricRankIntroSeen=true;saveProgress();renderAsymmetricRankIntro();return true}
'''
if helpers.strip() not in s:
    if anchor not in s:raise SystemExit('intro helper insertion anchor missing')
    s=s.replace(anchor,anchor+helpers,1)

old="p.locked?`${p.orientation==='bottom'?'↓':'↑'} ${p.activeRank} 사용`:`↕ ${p.topRank}/${p.bottomRank}`"
new="p.locked?`${p.orientation==='bottom'?'↓':'↑'} ${p.activeRank} 사용`:'↕ 선택'"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('rank marker anchor missing')

old="renderInitiative();renderHand();renderEnemyHand();"
new="renderInitiative();renderHand();if(typeof renderAsymmetricRankIntro==='function')renderAsymmetricRankIntro();renderEnemyHand();"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('render integration anchor missing')

old="document.querySelectorAll('#hudMenu button').forEach(b=>b.addEventListener('click',()=>document.getElementById('hudMenu')?.removeAttribute('open')));renderProgress();showStartScreen();"
new="document.querySelectorAll('#hudMenu button').forEach(b=>b.addEventListener('click',()=>document.getElementById('hudMenu')?.removeAttribute('open')));document.getElementById('asymRankIntroClose').onclick=dismissAsymmetricRankIntro;renderProgress();showStartScreen();"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('intro button binding anchor missing')

p.write_text(s)

road=Path('ROADMAP.md')
r=road.read_text()
old='- [ ] 모바일에서 상·하단 숫자가 다른 카드가 단순 오타처럼 보이지 않도록 최초 획득/튜토리얼 설명 설계'
new='- [x] 모바일에서 상·하단 숫자가 다른 카드가 단순 오타처럼 보이지 않도록 최초 획득/튜토리얼 설명 설계 — 미확정 카드 중앙에 `↕ 선택` 표식을 상시 표시하고, 플레이어 손에 비대칭 카드가 처음 들어온 순간 손패 위에 비차단 설명 패널을 1회 노출한다. 확인 후 진행도에 저장하며 실제 라이브 비대칭 카드가 생기기 전까지 가짜 튜토리얼 카드는 추가하지 않음'
if old in r:r=r.replace(old,new,1)
elif new not in r:raise SystemExit('roadmap M11B mobile item missing')
road.write_text(r)

doc=Path('docs/ASYMMETRIC_RANK_PROTOTYPE.md')
d=doc.read_text()
section='''\n\n## 모바일 / 최초 노출 안내\n\n- 미확정 `X/Y` 카드는 카드 중앙에 `↕ 선택`을 상시 표시한다. 숫자가 서로 다른 것 자체가 오류가 아니라 선택 가능한 인쇄값이라는 뜻이다.\n- 플레이어 손에 비대칭 카드가 처음 존재하는 프레임에서 손패 바로 위에 작은 설명 패널을 1회 노출한다. 모달로 전투를 막지 않는다.\n- 안내 문구는 `두 숫자는 오타가 아님 → 세트/런/붙이기 시 둘 중 하나를 직접 선택 → 공개 조합에 있는 동안 고정 → 손으로 돌아오면 다시 선택`의 네 문장 의미를 유지한다.\n- `asymmetricRankIntroSeen`은 기존 진행도 저장에 마이그레이션되며, 사용자가 `확인`한 뒤에만 true가 된다. 단순히 카드를 잠깐 렌더링했다는 이유로 안내를 소비하지 않는다.\n- 현재 라이브 비대칭 카드 정의는 계속 0장이다. 실제 카드 승격 전에는 가짜 튜토리얼 카드를 기본/고급 튜토리얼에 넣지 않고, 최초 획득 안내와 개발자 시각 프로토타입으로 UI 계약만 검증한다.\n'''
if '## 모바일 / 최초 노출 안내' not in d:d+=section
doc.write_text(d)
print('M11B mobile first-exposure guidance installed')

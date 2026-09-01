from pathlib import Path

html=Path('index.html')
s=html.read_text()

css='''

/* M11B UI1 · asymmetric top/bottom rank frame prototype */
.cardFace{position:absolute;inset:0;z-index:1;transform-origin:center;transition:transform .16s ease}
.card .namedMark{z-index:3}.card.named:after{z-index:5}
.card.asymmetricRank{box-shadow:0 0 0 2px #b88642 inset,3px 5px 0 #0008}
.card.asymmetricRank:before{border-style:dashed;opacity:.9}
.card.asymmetricRank .topRankCorner,.card.asymmetricRank .bottomRankCorner{padding:1px 2px;border-radius:3px;background:#f5ecd9d9;box-shadow:0 0 0 1px #9c7440 inset}
.card.rankLockedTop .bottomRankCorner{opacity:.34}.card.rankLockedBottom .topRankCorner{opacity:.34}
.card.rankLockedBottom .cardFace{transform:rotate(180deg)}
.rankStateMark{position:absolute;z-index:4;left:50%;top:5px;transform:translateX(-50%);max-width:62%;padding:2px 4px;border:1px solid #51462f;border-radius:999px;background:#efe3c7e8;color:#54462d;font-size:6px;font-weight:900;line-height:1;white-space:nowrap;pointer-events:none}
.rankStateMark.unresolved{border-color:#6e6758;background:#e6decced;color:#655f54}.rankStateMark.locked{border-color:#4d7069;background:#dce9e3ed;color:#315b53}
.meldMiniCard .rankStateMark{top:2px;padding:1px 2px;font-size:4.5px}.cardBtn .rankStateMark{font-size:5.5px}.codexMini .rankStateMark,.discardFace .rankStateMark{font-size:4.5px;padding:1px 2px}
.rankPrototypePanel{margin-top:8px;padding:8px;border:1px solid #4b5860;border-left:3px solid #927d58;border-radius:8px;background:#202a2f}
.rankPrototypeHead{display:flex;justify-content:space-between;gap:8px;align-items:center;font-size:8px;font-weight:900;color:#e3d4b4}.rankPrototypeHead span:last-child{font-size:6px;color:#9eaaa7;font-weight:400}
.rankPrototypeNote{margin:5px 0 7px;font-size:7px;line-height:1.45;color:#aebbb7}
.rankPrototypeCards{display:flex;justify-content:center;gap:8px;flex-wrap:wrap}.rankPrototypeItem{width:82px;text-align:center}.rankPrototypeCard{width:68px;height:102px;margin:0 auto}.rankPrototypeLabel{margin-top:4px;font-size:6px;line-height:1.3;color:#c7d1ce}.rankPrototypeLabel b{color:#e1c991}
@media(max-width:390px){.rankPrototypeCards{gap:5px}.rankPrototypeItem{width:72px}.rankPrototypeCard{width:61px;height:92px}.rankStateMark{max-width:68%;font-size:5px}}
'''
if '/* M11B UI1 · asymmetric top/bottom rank frame prototype */' not in s:
    s=s.replace('\n</style>',css+'\n</style>',1)

old='''<div class="developerActions"><button id="developerCodexBtn" class="pixelBtn" type="button">전체 도감</button><button id="developerProgressBtn" class="pixelBtn" type="button">캐릭터·카드군</button><button id="developerBattleBtn" class="pixelBtn primary wide" type="button" disabled>DEV 새 대전</button></div><div class="metricsPanel">'''
new='''<div class="developerActions"><button id="developerCodexBtn" class="pixelBtn" type="button">전체 도감</button><button id="developerProgressBtn" class="pixelBtn" type="button">캐릭터·카드군</button><button id="developerBattleBtn" class="pixelBtn primary wide" type="button" disabled>DEV 새 대전</button></div><div class="rankPrototypePanel" aria-label="M11B 비대칭 숫자 카드 시각 프로토타입"><div class="rankPrototypeHead"><span>M11B · 상/하단 숫자 프레임</span><span>시각 검증용 · 라이브 0장</span></div><div class="rankPrototypeNote">같은 합성 3/7 카드를 미확정, 위쪽 3 선택, 아래쪽 7 선택 상태로 표시합니다. 아래쪽을 사용하면 카드 면만 180° 돌아 선택 숫자가 좌상단으로 올라옵니다.</div><div id="rankPrototypeCards" class="rankPrototypeCards"></div></div><div class="metricsPanel">'''
if old in s:
    s=s.replace(old,new,1)
elif 'id="rankPrototypeCards"' not in s:
    raise SystemExit('developer prototype insertion anchor missing')

old_render="if(typeof renderBattleMetricsHistory==='function')renderBattleMetricsHistory()}"
new_render="if(typeof renderBattleMetricsHistory==='function')renderBattleMetricsHistory();if(typeof renderAsymmetricRankPrototype==='function')renderAsymmetricRankPrototype()}"
if old_render in s:
    s=s.replace(old_render,new_render,1)
elif new_render not in s:
    raise SystemExit('renderDeveloperPanel anchor missing')

old_card="""function cardHTML(c){const suit=SUIT_SYMBOL[c.suit],red=(c.suit==='H'||c.suit==='D')?'suitRed':'',rank=c.suit==='J'?'J':c.rank,themeClass=c.themeId?`theme-${c.themeId}`:'';return`<div class=\"card ${c.named?'named':''} ${c.suit==='J'?'joker':''} ${themeClass}\"><div class=\"corner ${red}\">${rank}<br>${suit}</div><div class=\"centerSuit ${red}\">${suit}</div>${c.named?`<div class=\"namedMark\">${c.name}</div>`:''}<div class=\"corner bottom ${red}\">${rank}<br>${suit}</div></div>`}\n"""
new_card="""function cardRankPresentation(c){
 if(!c)return{topRank:'?',bottomRank:'?',baseRank:null,activeRank:null,orientation:null,asymmetric:false,locked:false};
 if(c.suit==='J')return{topRank:'J',bottomRank:'J',baseRank:null,activeRank:null,orientation:null,asymmetric:false,locked:false};
 ensureRankPrototype(c);const asymmetric=isAsymmetricRankCard(c),orientation=asymmetric&&c.activeRank&&(c.rankOrientation==='top'||c.rankOrientation==='bottom')?c.rankOrientation:null;
 return{topRank:asymmetric?c.topRank:(c.rank||c.baseRank),bottomRank:asymmetric?c.bottomRank:(c.rank||c.baseRank),baseRank:c.baseRank||c.rank||null,activeRank:orientation?c.activeRank:null,orientation,asymmetric,locked:!!orientation}
}
function rankPrototypeDetailText(c){const p=cardRankPresentation(c);if(!p.asymmetric)return'';const suit=SUIT_SYMBOL[c.suit]||'',use=p.locked?`${p.activeRank}${p.orientation==='bottom'?' ↓ 아래':' ↑ 위'}`:'미확정';return` · 원본 슬롯 ${p.baseRank}${suit} · 인쇄 ${p.topRank}/${p.bottomRank} · 사용값 ${use}`}
function rankPrototypeDemoCards(){const base={uid:-1,id:'M11B-DEMO',suit:'S',rank:'7',baseRank:'7',topRank:'3',bottomRank:'7',activeRank:null,rankOrientation:null,named:true,name:'회전 프로토타입',themeId:null};return[{label:'손패 · 미확정',card:{...base,uid:-11}},{label:'조합 · 위 3 사용',card:{...base,uid:-12,rank:'3',activeRank:'3',rankOrientation:'top'}},{label:'조합 · 아래 7 사용',card:{...base,uid:-13,rank:'7',activeRank:'7',rankOrientation:'bottom'}}]}
function renderAsymmetricRankPrototype(){const el=document.getElementById('rankPrototypeCards');if(!el)return;el.innerHTML=rankPrototypeDemoCards().map(x=>`<div class=\"rankPrototypeItem\"><div class=\"rankPrototypeCard\">${cardHTML(x.card)}</div><div class=\"rankPrototypeLabel\"><b>${x.label}</b><br>${rankPrototypeDetailText(x.card).replace(/^ · /,'')}</div></div>`).join('')}
function cardHTML(c){const suit=SUIT_SYMBOL[c.suit],red=(c.suit==='H'||c.suit==='D')?'suitRed':'',p=cardRankPresentation(c),themeClass=c.themeId?`theme-${c.themeId}`:'',rankClass=p.asymmetric?`asymmetricRank ${p.locked?(p.orientation==='bottom'?'rankLocked rankLockedBottom':'rankLocked rankLockedTop'):'rankUnresolved'}`:'',rankMark=p.asymmetric?`<div class=\"rankStateMark ${p.locked?'locked':'unresolved'}\">${p.locked?`${p.orientation==='bottom'?'↓':'↑'} ${p.activeRank} 사용`:`↕ ${p.topRank}/${p.bottomRank}`}</div>`:'';return`<div class=\"card ${c.named?'named':''} ${c.suit==='J'?'joker':''} ${themeClass} ${rankClass}\"><div class=\"cardFace\"><div class=\"corner topRankCorner ${red}\">${p.topRank}<br>${suit}</div><div class=\"centerSuit ${red}\">${suit}</div><div class=\"corner bottom bottomRankCorner ${red}\">${p.bottomRank}<br>${suit}</div></div>${rankMark}${c.named?`<div class=\"namedMark\">${c.name}</div>`:''}</div>`}
"""
if old_card in s:
    s=s.replace(old_card,new_card,1)
elif 'function cardRankPresentation(c)' not in s:
    raise SystemExit('cardHTML anchor missing')

old_meta="${c.named?'네임드 카드':'순수 카드'}${c.named&&c.suit!=='J'?` · 슬롯 ${cardText(c)}`:''}${c.fromDiscard?"
new_meta="${c.named?'네임드 카드':'순수 카드'}${c.named&&c.suit!=='J'?` · 슬롯 ${cardText(c)}`:''}${typeof rankPrototypeDetailText==='function'?rankPrototypeDetailText(c):''}${c.fromDiscard?"
if old_meta in s:
    s=s.replace(old_meta,new_meta,1)
elif new_meta not in s:
    raise SystemExit('renderDetail rank meta anchor missing')

html.write_text(s)

road=Path('ROADMAP.md')
r=road.read_text()
updates={
'- [ ] 실제 카드 좌상단·우하단 랭크를 서로 다르게 표시하고 180° 회전 선택이 즉시 읽히는 카드 프레임 프로토타입 제작':'- [x] 실제 카드 좌상단·우하단 랭크를 서로 다르게 표시하고 180° 회전 선택이 즉시 읽히는 카드 프레임 프로토타입 제작 — 공용 `cardHTML()`이 `topRank/bottomRank`를 분리 렌더링하고, 아래값 선택 시 카드 면만 180° 회전해 선택값이 좌상단으로 올라오도록 구현. 개발자 패널에 라이브 카드와 분리된 합성 3/7 미확정·위 선택·아래 선택 3상태 미리보기 추가',
'- [ ] 조합에 들어간 뒤에는 선택된 사용값이 어느 쪽인지 회전 상태 또는 작은 방향 마커로 명확히 고정 표시':'- [x] 조합에 들어간 뒤에는 선택된 사용값이 어느 쪽인지 회전 상태 또는 작은 방향 마커로 명확히 고정 표시 — `rankLockedTop/rankLockedBottom` 상태와 `↑/↓ 사용` 마커를 공용 카드 렌더러가 표시하고, 선택하지 않은 반대 코너는 약하게 처리. 아래값 선택은 카드 면 180° 회전과 함께 고정',
'- [ ] 카드 상세에는 `원본 슬롯`, `두 인쇄값`, 현재 조합에 있을 때의 `사용값`을 구분해 표시':'- [x] 카드 상세에는 `원본 슬롯`, `두 인쇄값`, 현재 조합에 있을 때의 `사용값`을 구분해 표시 — 비대칭 카드만 `원본 슬롯 / 인쇄 X/Y / 사용값 미확정 또는 ↑·↓ 값` 메타를 추가하고 일반 X/X 카드 상세는 기존 표시를 유지'
}
for old,new in updates.items():
    if old in r:r=r.replace(old,new,1)
    elif new not in r:raise SystemExit(f'ROADMAP anchor missing: {old}')
road.write_text(r)

doc=Path('docs/ASYMMETRIC_RANK_PROTOTYPE.md')
d=doc.read_text()
section='''

## UI 프로토타입 단계 1 — 공용 카드 프레임

- 라이브 비대칭 카드 수는 계속 **0장**이다. 개발자 패널의 `3/7` 카드는 게임 카드 정의가 아니라 공용 렌더러를 검증하기 위한 합성 시각 샘플이다.
- `cardHTML()`은 정규 카드의 `topRank`와 `bottomRank`를 각각 좌상단/우하단에 인쇄한다. 일반 `X/X` 카드는 기존과 같은 값이 양쪽에 보여 시각 호환을 유지한다.
- 미확정 `X/Y`는 두 코너를 모두 정상 표시하고 `↕ X/Y` 마커를 둔다.
- 조합에서 위값을 선택하면 `↑ X 사용`, 아래값을 선택하면 `↓ Y 사용`으로 고정한다. 아래값 선택은 카드 면(`cardFace`)만 180° 회전시켜 선택한 아래 숫자가 실제 좌상단으로 올라오게 하며 카드 이름/테마 표식은 읽기 쉽게 정방향을 유지한다.
- 선택하지 않은 반대편 코너는 약하게 표시하지만 값 자체는 숨기지 않는다. 효과가 `사용하지 않은 값`을 참조할 수 있기 때문이다.
- 카드 상세는 비대칭 카드에 한해 `원본 슬롯`, `인쇄 X/Y`, 현재 `사용값`을 별도 표시한다.
- 다음 UI 단계는 손패에서 실제 행동 후보를 고를 때 `rankChoicePreview()`의 합법 plan을 선택 UI로 연결하는 것이다.
'''
if '## UI 프로토타입 단계 1 — 공용 카드 프레임' not in d:
    d+=section
doc.write_text(d)
print('M11B asymmetric-rank card frame UI prototype installed')

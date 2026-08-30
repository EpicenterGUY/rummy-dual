from pathlib import Path

index_path = Path('index.html')
roadmap_path = Path('ROADMAP.md')
text = index_path.read_text()
roadmap = roadmap_path.read_text()


def replace_once(src, old, new, label):
    count = src.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, got {count}')
    return src.replace(old, new, 1)

old_header = '<header class="topbar between"><div><div class="logo">RUMMY<b>//DUEL</b></div><div class="sub">세트와 런으로 폭탄을 키워 스위치를 넘기는 1:1 러미 배틀</div></div><div class="topActions"><span id="charBadge" class="badge"><span class="gold">◆</span> 유랑자 Lv.1</span><button id="progressBtn" class="pixelBtn">캐릭터·해금</button><button id="codexBtn" class="pixelBtn">도감</button><button id="rulesBtn" class="pixelBtn">규칙·용어</button><button id="homeBtn" class="pixelBtn">메인</button></div></header>'
new_header = '<header class="topbar between"><div class="topBrand"><div class="logo">RUMMY<b>//DUEL</b></div><div class="sub">전술 러미 대전</div></div><div class="topActions"><span id="charBadge" class="badge"><span class="gold">◆</span> 유랑자 Lv.1</span><details id="hudMenu" class="hudMenu"><summary class="pixelBtn hudMenuBtn">메뉴</summary><div class="hudMenuPanel"><button id="progressBtn" class="pixelBtn">캐릭터</button><button id="codexBtn" class="pixelBtn">도감</button><button id="rulesBtn" class="pixelBtn">규칙</button><button id="homeBtn" class="pixelBtn">메인</button></div></details></div></header>'
text = replace_once(text, old_header, new_header, 'battle header')

old_hand = '<div class="handSub">조합은 폭탄을 바로 때리는 카드가 아니라 <b>SWITCH를 받아칠 길</b>입니다. 상대 공개 조합도 역이용하고, 회수·버림패·상태로 다음 반환을 준비하세요.</div></div><div class="badge">RUMMY <b id="rummyCount" class="gold">0</b></div>'
new_hand = '<div class="handSub">세트·런을 만들거나 공개 조합에 붙여 스위치를 넘기세요.</div></div><div class="badge">러미 <b id="rummyCount" class="gold">0</b></div>'
text = replace_once(text, old_hand, new_hand, 'hand helper')

old_log = '<section class="detail pixel" id="detail"></section><details class="log pixel"><summary>전투 기록</summary><div id="log"></div></details>'
new_log = '<section class="detail pixel" id="detail"></section><details class="log pixel"><summary><span>전투 기록</span><small>필요할 때 펼치기</small></summary><div id="log"></div></details>'
text = replace_once(text, old_log, new_log, 'combat log disclosure')

marker = '/* UI2 P2 · HUD hierarchy and density */'
if marker in text:
    raise SystemExit('UI2 P2 marker already exists')

css = r'''

/* UI2 P2 · HUD hierarchy and density */
.topbar{gap:8px}.topBrand{min-width:0;flex:1}.topBrand .sub{font-size:7px;letter-spacing:.2px}.topActions{flex:0 0 auto;gap:5px}#charBadge{max-width:142px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.hudMenu{position:relative}.hudMenu>summary{list-style:none;cursor:pointer}.hudMenu>summary::-webkit-details-marker{display:none}.hudMenuBtn{padding:5px 8px!important;font-size:8px!important}.hudMenu[open] .hudMenuBtn{background:#3b484d}.hudMenuPanel{position:absolute;z-index:80;right:0;top:calc(100% + 6px);width:148px;padding:6px;display:grid;gap:5px;background:#263137;border:1px solid #536168;border-radius:9px;box-shadow:0 8px 22px #0006}.hudMenuPanel .pixelBtn{width:100%;padding:7px 8px!important;text-align:left;font-size:8px!important}
.main{gap:5px;padding:0 7px 10px}.status{grid-template-columns:1fr 54px 1fr;gap:5px}.hpPanel{padding:6px}.mid{padding:5px 3px}.mid b{font-size:13px;margin-top:1px}.combatMeta{margin-top:3px}.coreBreakNote{display:none}
.initiativeBoard{grid-template-columns:44px minmax(0,1fr) 44px;gap:5px;padding:6px}.initiativeSide{height:30px}.initiativeLabel{display:none}.strongAttackBtn{display:none!important}.initiativeRule{margin-top:4px;padding-top:4px;border-top:1px solid #3f4d52;font-size:6px;line-height:1.3}.switchAlert{margin-top:3px}
.meldZone,.handZone{padding:7px}.meldRows{gap:5px}.meldSide{min-height:82px;padding:5px}.meldEntry{margin-bottom:4px}.meldCardRow{min-height:60px;padding-bottom:3px}.meldZone .zoneTitle .gold{display:none}.targetHint{margin-top:4px}
.handTop{align-items:center}.handSub{font-size:7px;line-height:1.35;max-width:330px}.hand{min-height:138px;padding:9px 3px 6px;gap:4px}.cardBtn.selected{transform:translateY(-5px)}.cardBtn.selected .card{outline:2px solid #79aaa4;outline-offset:1px;box-shadow:0 3px 7px #0003}.cardBtn.attachable:not(.selected) .card{outline:2px solid #7f9a82;outline-offset:1px;box-shadow:0 3px 7px #0003}.meldEntry.target{outline:2px solid #9a8c70;outline-offset:1px;box-shadow:none}.meldMiniCard.boardPick .card{outline:2px solid #8e89a3;outline-offset:1px;box-shadow:0 2px 5px #0002}.quickAttachHint{background:#35443f;color:#c7ddd2;border-color:#52645e}
.detail{padding:6px;grid-template-columns:58px 1fr;gap:7px}.detailCard{width:52px;height:78px}.detailText{margin-top:3px}.detailTip{margin-top:3px}
.log{padding:0;max-height:none;overflow:visible}.log>summary{cursor:pointer;list-style:none;display:flex;align-items:center;justify-content:space-between;gap:8px;padding:7px 8px;font-size:8px;font-weight:900;color:#cfd8d5}.log>summary::-webkit-details-marker{display:none}.log>summary:after{content:'＋';font-size:11px;color:#8fa09d}.log[open]>summary:after{content:'－'}.log>summary small{margin-left:auto;font-size:6px;font-weight:400;color:#8d9a99}.log[open]>summary{border-bottom:1px solid #435157}.log>div{max-height:128px;overflow:auto;padding:0 7px 7px}.logLine{font-size:6.5px}
@media(max-width:390px){.main{padding-left:6px;padding-right:6px}.topBrand .sub{font-size:6.5px}.status{grid-template-columns:1fr 50px 1fr}.initiativeBoard{grid-template-columns:40px minmax(0,1fr) 40px}.handSub{max-width:240px}.hudMenuPanel{width:144px}.detailTip{display:none}}
@media(max-width:370px){.topbar{padding:7px 7px 6px}.topBrand .sub{display:none}.logo{font-size:17px}#charBadge{max-width:112px;font-size:7px}.hudMenuBtn{padding:5px 7px!important;font-size:7px!important}.status{grid-template-columns:1fr 48px 1fr}.hpHead{font-size:9px}.coreHpText{font-size:7px}.initiativeBoard{grid-template-columns:38px minmax(0,1fr) 38px}.initiativeSide{font-size:7px}.initiativeState{font-size:12px}.handSub{display:none}}
'''
text = replace_once(text, '\n</style>', css + '\n</style>', 'style close')

needle = 'renderProgress();showStartScreen();\n})();'
pos = text.rfind(needle)
if pos < 0:
    raise SystemExit('final bootstrap marker not found')
listener = "document.querySelectorAll('#hudMenu button').forEach(b=>b.addEventListener('click',()=>document.getElementById('hudMenu')?.removeAttribute('open')));"
text = text[:pos] + listener + text[pos:]

roadmap_replacements = [
    ('- [ ] 상단 상태/캐릭터/메뉴 밀도 축소 및 모바일 우선 재배치', '- [x] 상단 상태/캐릭터/메뉴 밀도 축소 및 모바일 우선 재배치 — 캐릭터 배지 + 단일 `메뉴` 드롭다운'),
    ('- [ ] 스위치 핵심 정보와 보조 문구를 1차/2차 정보로 분리', '- [x] 스위치 핵심 정보와 보조 문구를 1차/2차 정보로 분리 — 상태/경고/코어 여유만 상시 노출, 중복 라벨/비활성 버튼 제거'),
    ('- [ ] 공개 조합과 손패 사이 여백·높이·스크롤 밀도 재조정', '- [x] 공개 조합과 손패 사이 여백·높이·스크롤 밀도 재조정'),
    ('- [ ] 전투 기록 기본 접힘/요약 방식 검토', '- [x] 전투 기록 기본 접힘/요약 방식 적용 — 기본 접힘 + 짧은 disclosure 헤더 + 펼쳤을 때만 제한 높이 스크롤'),
    ('- [ ] 선택 가능 카드·붙이기 가능 조합 강조를 발광보다 테두리/위치 변화 중심으로 통일', '- [x] 선택 가능 카드·붙이기 가능 조합 강조를 발광보다 테두리/위치 변화 중심으로 통일'),
    ('- [ ] 360~480px 실제 모바일 폭에서 버튼/상태 문구 잘림 회귀 점검', '- [ ] 360~480px 실제 모바일 폭에서 버튼/상태 문구 잘림 회귀 점검 — 370/390px 정적 fallback과 회귀 테스트 추가, 실기기 시각 검수 남음'),
    ('1. UI2 P2: after the first casino-tone reset, reduce HUD density and clarify information hierarchy without weakening combat readability.', '1. UI2 P2: hierarchy/density pass is live; finish the 360–480px real-device visual check, then defer P3 art/brand polish until gameplay/tutorial UX is steadier.'),
]
for old, new in roadmap_replacements:
    roadmap = replace_once(roadmap, old, new, f'roadmap: {old[:34]}')

index_path.write_text(text)
roadmap_path.write_text(roadmap)

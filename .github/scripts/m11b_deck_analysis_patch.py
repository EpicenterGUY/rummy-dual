from pathlib import Path


def replace_once(text, old, new, label):
    if old in text:
        return text.replace(old, new, 1)
    if new in text:
        return text
    raise SystemExit(f'missing anchor: {label}')

index = Path('index.html')
s = index.read_text()

old_css = ".deckWarn{grid-column:1/-1;padding:5px;border:1px solid #594b2d;background:#201c12;color:#e5ca87;font-size:7px;line-height:1.4}.deckOk{border-color:#2e5948;background:#102219;color:#aee5c2}"
new_css = ".deckWarn{grid-column:1/-1;padding:5px;border:1px solid #594b2d;background:#201c12;color:#e5ca87;font-size:7px;line-height:1.4}.deckWarn small{display:block;margin-top:2px;color:#9eaaad;font-size:6px;line-height:1.35}.deckOk{border-color:#2e5948;background:#102219;color:#aee5c2}.deckFlexNote{grid-column:1/-1;padding:5px;border:1px solid #48586b;background:#111922;color:#b9c9d8;font-size:7px;line-height:1.4}"
s = replace_once(s, old_css, new_css, 'deck analysis CSS')

old_func = "function deckBuildAnalysis(slots=progress.deckBuild?.slots||[]){const suits={S:0,H:0,D:0,C:0},ranks=Object.fromEntries(Object.keys(RANK_VALUE).map(r=>[r,0]));for(const slot of slots){const{suit,rank}=parseRegularId(slot);if(suit in suits)suits[suit]++;if(rank in ranks)ranks[rank]++}const setPairs=Object.values(ranks).filter(n=>n>=2).length,setReady=Object.values(ranks).filter(n=>n>=3).length;let runWindows=0,longestRun=0;for(const suit of['S','H','D','C']){const vals=new Set(slots.filter(x=>x[0]===suit).map(x=>RANK_VALUE[parseRegularId(x).rank]));for(let v=1;v<=11;v++)if(vals.has(v)&&vals.has(v+1)&&vals.has(v+2))runWindows++;let streak=0;for(let v=1;v<=13;v++){streak=vals.has(v)?streak+1:0;longestRun=Math.max(longestRun,streak)}}return{suits,ranks,setPairs,setReady,runWindows,longestRun}}"
new_func = """function deckBuildAsymmetricFlexAnalysis(build=progress.deckBuild||{}){const ranks=Object.fromEntries(Object.keys(RANK_VALUE).map(r=>[r,0])),details=[];for(const slot of Array.isArray(build?.slots)?build.slots:[]){const id=typeof effectiveDeckVariant==='function'?effectiveDeckVariant(slot):build?.variants?.[slot],def=id&&typeof NAMED==='object'&&NAMED?NAMED[id]:null;if(!def)continue;if(typeof namedSlot==='function'&&namedSlot(id)!==slot)continue;const base=parseRegularId(slot).rank,norm=v=>{const k=String(v??'').toUpperCase();return Object.prototype.hasOwnProperty.call(RANK_VALUE,k)?k:null},top=norm(def.topRank??base)||base,bottom=norm(def.bottomRank??base)||base;if(top===bottom)continue;for(const r of new Set([top,bottom]))ranks[r]=(ranks[r]||0)+1;details.push({slot,id,baseRank:base,topRank:top,bottomRank:bottom,alternateRanks:[...new Set([top,bottom].filter(r=>r!==base))]})}return{cards:details.length,alternateRankSlots:details.reduce((n,x)=>n+x.alternateRanks.length,0),printedRanks:ranks,details}}
function deckBuildAnalysis(slots=progress.deckBuild?.slots||[]){const suits={S:0,H:0,D:0,C:0},ranks=Object.fromEntries(Object.keys(RANK_VALUE).map(r=>[r,0]));for(const slot of slots){const{suit,rank}=parseRegularId(slot);if(suit in suits)suits[suit]++;if(rank in ranks)ranks[rank]++}const setPairs=Object.values(ranks).filter(n=>n>=2).length,setReady=Object.values(ranks).filter(n=>n>=3).length;let runWindows=0,longestRun=0;for(const suit of['S','H','D','C']){const vals=new Set(slots.filter(x=>x[0]===suit).map(x=>RANK_VALUE[parseRegularId(x).rank]));for(let v=1;v<=11;v++)if(vals.has(v)&&vals.has(v+1)&&vals.has(v+2))runWindows++;let streak=0;for(let v=1;v<=13;v++){streak=vals.has(v)?streak+1:0;longestRun=Math.max(longestRun,streak)}}return{suits,ranks,setPairs,setReady,runWindows,longestRun,basis:'base-slot'}}"""
s = replace_once(s, old_func, new_func, 'deckBuildAnalysis')

old_render_head = "const build=progress.deckBuild,selected=new Set(build.slots),analysis=deckBuildAnalysis(build.slots),valid=build.slots.length===29"
new_render_head = "const build=progress.deckBuild,selected=new Set(build.slots),analysis=deckBuildAnalysis(build.slots),flex=typeof deckBuildAsymmetricFlexAnalysis==='function'?deckBuildAsymmetricFlexAnalysis(build):{cards:0,alternateRankSlots:0},valid=build.slots.length===29"
s = replace_once(s, old_render_head, new_render_head, 'renderDeckBuilder flex analysis')

old_warn = "<div class=\"deckWarn ${valid?'deckOk':''}\">${valid?'구성 완료 · 정규 29 + 조커 1 = 30장.':'커스텀 적용 전 정규 슬롯을 정확히 29개 선택하세요.'}</div>"
new_warn = "<div class=\"deckWarn ${valid?'deckOk':''}\">${valid?'구성 완료 · 정규 29 + 조커 1 = 30장.':'커스텀 적용 전 정규 슬롯을 정확히 29개 선택하세요.'}<br><small>숫자·무늬·세트·런은 원본 52슬롯 기준 · 비대칭 사용값은 중복 집계하지 않음.</small></div>${flex.cards?`<div class=\"deckFlexNote\">비대칭 선택값 ${flex.cards}장 · 잠재 추가 랭크 ${flex.alternateRankSlots}개 · 기초 분포와 분리</div>`:''}"
s = replace_once(s, old_warn, new_warn, 'deckbuilder basis note')

index.write_text(s)

road = Path('ROADMAP.md')
r = road.read_text()
anchor = "- [x] CPU가 두 사용값의 세트·런 가능성, 즉시 버스트/체인, 스위치 반환 가치까지 비교하는 최소 휴리스틱 설계 — `bestNewMeld`와 최대 6장 `bestExtensionFromHand`가 각 카드 조합의 모든 합법 top/bottom plan을 projection으로 비교하고, 새 조합은 기존 SET/RUN 점수·미래 버스트 노출 위험을 선택값 기준으로 계산하며, 붙이기는 실제 버스트 +24 / 체인 10·15·20·25… / 상대 공개 조합·테마 보정을 선택 plan의 projection에 적용한다. 선택된 `rankPlan`을 실제 `submitNewMeld/attachCards`에 전달하며, 막힘 판정 `anyAttachOption`도 비대칭 plan을 인식한다. 점수가 같으면 기존 위→아래 열거 순서를 유지해 결정적으로 선택하고 현재 라이브 비대칭 카드는 0장\n"
item = "- [x] 덱빌더 숫자·무늬·세트·런 분포는 원본 52슬롯(`baseRank+suit`) 기준으로 고정하고 비대칭 `X/Y`의 선택 유연성은 별도 분석으로 분리 — `deckBuildAnalysis()`는 변형 인쇄값을 절대 중복 집계하지 않고 `basis:'base-slot'`을 반환한다. `deckBuildAsymmetricFlexAnalysis()`는 향후 실제 비대칭 변형이 선택된 경우에만 잠재 선택 랭크를 별도 표시하며 기초 세트/런 통계를 바꾸지 않는다. 현재 라이브 비대칭 카드는 0장\n"
if item not in r:
    if anchor not in r:
        raise SystemExit('roadmap M11B engine anchor missing')
    r = r.replace(anchor, anchor + item, 1)
road.write_text(r)

doc = Path('docs/ASYMMETRIC_RANK_PROTOTYPE.md')
d = doc.read_text()
section = """

## 덱빌더 분포 기준 — 원본 슬롯과 선택 유연성 분리

M11의 52슬롯 덱빌더는 비대칭 카드가 생겨도 **원본 슬롯 기준 분포**를 유지한다. `3/7`이 `7♠` 슬롯의 변형이라면 덱 구성의 숫자 카운트에는 `7♠` 한 장으로만 들어가며, 3과 7 두 장처럼 중복 집계하지 않는다.

- `deckBuildAnalysis(slots)`는 `baseRank+suit`에 해당하는 정규 슬롯 문자열만 사용한다. 반환값의 `basis`는 `base-slot`이다.
- 무늬 수, 랭크 수, 같은 숫자 2장+/3장+ 재료, 3연속 런 창, 최장 연속은 모두 원본 52슬롯 기준이다.
- `topRank/bottomRank`는 실전에서 한 번에 하나만 고르는 **행동 유연성**이므로 기초 분포를 직접 늘리지 않는다.
- `deckBuildAsymmetricFlexAnalysis(build)`는 선택된 변형 중 실제 `X/Y`만 찾아 잠재 선택 랭크와 원본과 다른 추가 랭크 수를 별도로 계산한다. 이 값은 기초 세트/런 통계와 합산하지 않는다.
- 덱빌더 UI도 이 구분을 명시하며, 실제 비대칭 변형이 선택된 경우에만 별도 유연성 줄을 표시한다.
- 현재 라이브 `NAMED`에는 비대칭 정의가 계속 0장이므로 일반 플레이의 기존 덱 분포 숫자는 변하지 않는다.

이 분리는 향후 밸런스 실험에서 `원래 슬롯 구조가 좋은 덱`과 `비대칭 선택값 때문에 실전 성공률이 오른 덱`을 혼동하지 않기 위한 기준이다. 실제 세트/런 성공률 증가는 M11B 밸런스 표본에서 별도로 측정한다.
"""
if '## 덱빌더 분포 기준 — 원본 슬롯과 선택 유연성 분리' not in d:
    d += section
doc.write_text(d)

print('M11B deckbuilder base-slot analysis contract installed')

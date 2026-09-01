from pathlib import Path
import re

root=Path(__file__).resolve().parents[2]
index_path=root/'index.html'
road_path=root/'ROADMAP.md'
master_path=root/'docs'/'ROGUELIKE_MASTER_PLAN.md'
starters_path=root/'docs'/'ROGUELIKE_DECK_STARTERS.md'
run_test_path=root/'tests'/'m11a-roguelike-run-init.mjs'
reward_test_path=root/'tests'/'m11a-reward-tags.mjs'


def replace_once(text, old, new, label):
    if old not in text:
        raise SystemExit(f'missing anchor: {label}')
    return text.replace(old,new,1)


def function_span(script,name):
    marker=f'function {name}('
    start=script.find(marker)
    if start<0:
        raise SystemExit(f'missing function {name}')
    par=0; brace=-1
    for i in range(start+len(marker)-1,len(script)):
        ch=script[i]
        if ch=='(': par+=1
        elif ch==')': par-=1
        elif ch=='{' and par==0:
            brace=i; break
    if brace<0: raise SystemExit(f'missing body {name}')
    depth=0
    for i in range(brace,len(script)):
        ch=script[i]
        if ch=='{': depth+=1
        elif ch=='}':
            depth-=1
            if depth==0: return start,i+1
    raise SystemExit(f'unterminated function {name}')


def replace_function(script,name,new_source):
    a,b=function_span(script,name)
    return script[:a]+new_source+script[b:]

# ---------- index.html ----------
html=index_path.read_text(encoding='utf-8')
if 'const ROGUELIKE_STARTER_REGULAR_SLOTS=Object.freeze(CORE_IDS.slice(0,29));' not in html:
    _,profile_end=function_span(html,'roguelikeStarterProfile')
    insert="""
const ROGUELIKE_STARTER_REGULAR_SLOTS=Object.freeze(CORE_IDS.slice(0,29));
const ROGUELIKE_STARTER_DECK_SIZE=30;
const ROGUELIKE_STARTER_NAMED_REGULAR_COUNT=6;
function roguelikeStarterDeckPlan(id){const key=normalizeRoguelikeStarterId(id),pure=key==='pure',namedRegular=pure?0:ROGUELIKE_STARTER_NAMED_REGULAR_COUNT,namedJoker=pure?0:1,pureRegular=ROGUELIKE_STARTER_REGULAR_SLOTS.length-namedRegular,pureJoker=pure?1:0;return{status:'locked-v1',exactDeckSize:ROGUELIKE_STARTER_DECK_SIZE,regularSlotCount:ROGUELIKE_STARTER_REGULAR_SLOTS.length,jokerCount:1,regularSlots:[...ROGUELIKE_STARTER_REGULAR_SLOTS],pureCardCount:pureRegular+pureJoker,namedCardCount:namedRegular+namedJoker,pureRegularCount:pureRegular,namedRegularCount:namedRegular,pureJokerCount:pureJoker,namedJokerCount:namedJoker,jokerPolicy:pure?'base-wild-no-effect':'named-joker',mixPolicy:pure?'pure-only-at-start':'pure-majority-plus-few-named',slotIdentity:'base-rank-suit'}}
"""
    html=html[:profile_end]+insert+html[profile_end:]

html=replace_function(html,'createRoguelikeRunDraft',"""function createRoguelikeRunDraft(starterId=progress?.roguelikeStarter||'wanderer'){let id=normalizeRoguelikeStarterId(starterId);if(!roguelikeStarterUnlocked(id))id='wanderer';const profile=roguelikeStarterProfile(id);return{version:2,mode:'roguelike-prototype',status:'prepared',runId:`rg-${Date.now().toString(36)}`,starterId:id,characterId:id==='pure'?null:id,pureStart:id==='pure',startZone:ROGUELIKE_COMMON_START_ZONE,currentZone:ROGUELIKE_COMMON_START_ZONE,regionPath:[],nodeIndex:0,themeLocks:[],allowCrossThemeRewards:true,deckPlan:roguelikeStarterDeckPlan(id),passivePlan:{status:'locked-v1',id:'none',directCombat:false},rewardPlan:{status:'ranking-weights-v1',probabilityStatus:'unresolved',candidateAlgorithm:ROGUELIKE_REWARD_ALGORITHM,roles:ROGUELIKE_REWARD_ROLES.map(x=>x.id),weightingMode:'character-tendency-score-v1',hardLock:false,tendencyHints:{...profile.tendencyHints}},createdAt:new Date().toISOString()}}""")
html=replace_function(html,'roguelikeRunDraftText',"""function roguelikeRunDraftText(draft=loadRoguelikeRunDraft()){if(!draft)return'런 초안 없음 · 스타터를 고른 뒤 구조 초안을 만들 수 있습니다.';const profile=roguelikeStarterProfile(draft.starterId),deck=draft.pureStart?'30장 · 순수 정규 29 + 기본 와일드 조커 1 · 효과 0':'30장 · 순수 23 + 네임드 정규 6 + 네임드 조커 1';return`<b>${profile.name}</b> · 공통 시작 구역 · ${deck}<br>카드군 하드 잠금 없음 · 직접 전투 패시브 없음 · 보상 후보 소프트 가중치 · 실제 보상 확률 미확정 · 현재 전투에는 아직 연결하지 않음`}""")
html=replace_once(html,
'<div class="themePickerNote">일반 대전의 캐릭터/테마 선택과 분리된 런 출발점입니다. 캐릭터는 방향만 제시하며 카드군을 잠그지 않습니다. 시작 덱 장수·패시브·정확한 보상 확률은 아직 확정하지 않습니다.</div>',
'<div class="themePickerNote">일반 대전의 캐릭터/테마 선택과 분리된 런 출발점입니다. 스타터는 30장 기준입니다. 유랑자·수집가·회수꾼·광대는 순수 23 + 네임드 정규 6 + 네임드 조커 1, PURE는 순수 정규 29 + 고유효과 없는 기본 와일드 조커 1로 시작합니다. 직접 전투 패시브는 v1에서 사용하지 않으며 실제 보상 등장 확률은 후속 밸런스에서 정합니다.</div>',
'roguelike starter UI note')
index_path.write_text(html,encoding='utf-8')

# ---------- ROADMAP ----------
road=road_path.read_text(encoding='utf-8')
road=replace_once(road,
'- [ ] 캐릭터별 시작 카드 수 / 순수카드 비율 / 보상 가중치 / 패시브 확정',
'''- [x] 캐릭터별 시작 카드 수 / 순수카드 비율 / 보상 가중치 / 패시브 확정
  - 모든 스타터는 v1에서 30장(정규 슬롯 29 + 조커 1)으로 시작한다. 일반 4스타터는 순수 23 + 네임드 정규 6 + 네임드 조커 1, PURE는 효과카드 0장을 유지한다.
  - 유랑자/수집가/회수꾼/광대의 기존 `weights`를 `character-tendency-score-v1` 보상 후보 랭킹 가중치로 잠근다. 이는 확률표나 카드군 잠금이 아니며 다른 테마 후보를 제외하지 않는다.
  - v1 스타터 직접 전투 패시브는 전원 `none`으로 잠근다. 캐릭터 차이는 시작 네임드 구성과 소프트 보상 랭킹에서 만들고 실제 등장 확률/희귀도는 후속 경제 데이터에서 정한다.''',
'road starter numbers')
road=replace_once(road,
'- [ ] PURE 시작 덱의 숫자/무늬 분포 확정',
'''- [x] PURE 시작 덱의 숫자/무늬 분포 확정
  - 정규 29슬롯은 현재 기준 구조 `CORE_IDS.slice(0,29)`를 그대로 사용한다: S3–S9 + S10, H2–H4/H7–H10, D2–D8, C3–C9.
  - 30번째 카드는 조합 판정에서만 와일드인 `기본 와일드 조커`로 두며 네임드/고유 효과/광대왕의 정리 후 즉시 덱 복귀 효과를 갖지 않는다. 따라서 PURE는 30장 모두 효과카드 0장이다.''',
'road pure distribution')
road_path.write_text(road,encoding='utf-8')

# ---------- Master plan ----------
master=master_path.read_text(encoding='utf-8')
master=replace_once(master,
'중요: 아래 내용은 구현 확정 수치가 아니다. `FINAL CORE 2.0`의 전투 규칙을 바꾸는 문서도 아니다. 향후 플레이테스트와 추가 기획을 거쳐 지역 수, 시작 덱 장수, 보상 확률, 캐릭터 패시브, 카드 희귀도 등을 다시 설계한다.',
'중요: `FINAL CORE 2.0`의 전투 규칙을 바꾸는 문서는 아니다. 아래에서 **v1 잠금**으로 명시한 스타터 30장 구조, 순수/네임드 비율, 직접 전투 패시브 없음, 캐릭터 보상 후보 랭킹 가중치는 현재 구현 기준으로 고정한다. 실제 보상 등장 확률, 카드 희귀도, 지역 수, 런 경제와 PURE 전용 특전은 플레이테스트 이후 조정한다.',
'master disclaimer')
old_block='''미확정 항목:

- 캐릭터별 시작 덱 장수
- 순수카드/효과카드 비율
- 고유 패시브의 강도
- 보상 가중치 방식
- 캐릭터와 지역의 관계'''
new_block='''v1 잠금 항목:

- 모든 스타터 시작 덱은 30장 = 정규 슬롯 29 + 조커 1.
- 유랑자/수집가/회수꾼/광대는 순수 23 + 네임드 정규 6 + 네임드 조커 1.
- PURE는 순수 정규 29 + 기본 와일드 조커 1이며 네임드/효과카드 0장.
- 직접 전투 패시브는 전원 없음. 스타터 차이는 시작 네임드 구성과 보상 후보 랭킹으로 만든다.
- 보상 후보 랭킹은 현재 `CHARACTERS.weights`를 그대로 쓰는 `character-tendency-score-v1` 소프트 가중치다. 가중치는 후보 점수에만 관여하고 다른 카드군을 금지하지 않는다.

계속 미확정인 항목:

- 6개의 시작 네임드 정규 슬롯에 들어갈 실제 카드 ID와 네임드 조커의 스타터별 세부 선택 규칙
- 실제 보상 등장 확률 / 희귀도 / 전투 등급별 경제
- 캐릭터와 지역의 관계
- PURE 전용 외부 특전/유물'''
master=replace_once(master,old_block,new_block,'master starter section')
if '## 15. 스타터 수치 기준 v1 — 30장 / PURE 기준 구조' not in master:
    master=master.rstrip()+'''\n\n## 15. 스타터 수치 기준 v1 — 30장 / PURE 기준 구조\n\nM11A 런 초안의 `deckPlan`을 미확정 자리표시자에서 실제 수치 계약으로 승격한다. 아직 이 덱을 로그라이크 전투에 직접 연결하지는 않지만, 이후 런 덱 구현은 아래 기준을 Source of Truth로 사용한다.\n\n### 공통 30장 골격\n\n- 모든 스타터는 **30장**으로 시작한다.\n- 정규 카드 슬롯은 **29개**, 조커 슬롯은 **1개**다.\n- 정규 29슬롯은 `CORE_IDS.slice(0,29)`를 공통 기준으로 사용한다: `S3,S4,S5,S6,S7,S8,S9,H2,H3,H4,H7,H8,H9,D2,D3,D4,D5,D6,D7,D8,C3,C4,C5,C6,C7,C8,C9,S10,H10`.\n- 네임드 정규 카드는 이 29개 원본 rank+suit 슬롯을 **교체**할 뿐 슬롯을 추가하지 않는다. 따라서 스타터마다 SET/RUN 기본 기하를 다르게 주지 않고 카드 효과/보상 성향으로 정체성을 만든다.\n\n### 유랑자 / 수집가 / 회수꾼 / 광대\n\n- 순수 카드: **23장**.\n- 네임드 정규: **6장**.\n- 네임드 조커: **1장**.\n- 총 네임드/효과카드: **7장 = 23.3%**, 순수카드: **23장 = 76.7%**.\n- 6개의 네임드 정규는 서로 다른 원본 슬롯을 사용해야 한다. 시작부터 하나의 테마 완성 콤보를 고정 지급하지 않으며 실제 카드 ID 선정은 후속 스타터 조립 단계에서 한다.\n\n### PURE\n\n- 순수 정규: **29장**.\n- 기본 와일드 조커: **1장**.\n- 네임드/고유 효과카드: **0장**.\n- 기본 와일드 조커는 `suit === 'J'`가 제공하는 조합용 와일드 판정만 가진다. `광대왕 조커(J1)`의 고유 효과인 조합 정리 후 즉시 원주인 덱 아래 복귀를 포함해 어떤 네임드 효과도 갖지 않는다. 일반 카드처럼 소모/재순환 흐름을 따른다.\n- 이 때문에 PURE도 다른 스타터와 같은 30장/조커 1장 구조를 유지하면서 `효과카드 0장` 정의를 지킨다. 초기 6장 손패의 순수한 SET/RUN 구조 비교에서는 기존 M11A 30장 기준 골격을 그대로 사용할 수 있다.\n\n### 캐릭터 가중치 / 패시브\n\n- 유랑자: `combo 1.7 / cycle 0.9 / extend 0.6 / pressure 0.3`.\n- 수집가: `hold 1.8 / sustain 0.8 / pressure 0.4 / status 0.3`.\n- 회수꾼: `discard 2.0 / cycle 1.1 / interact 0.7 / control 0.4`.\n- 광대: `trick 2.2 / combo 1.0 / interact 0.6 / status 0.4`.\n- PURE: 가중치 없음.\n- 이 값들은 **보상 후보 랭킹 점수**에만 사용하는 `character-tendency-score-v1`이다. 실제 드롭 확률표가 아니며 0가중치 테마/행동도 후보에서 제외하지 않는다.\n- 스타터 직접 전투 패시브는 v1에서 전원 `none`이다. M12 실전 데이터 전에 카드 수치 + 캐릭터 전투 패시브 + 보상 확률을 동시에 조정하는 다중 밸런스 축을 만들지 않는다. 향후 유물/패시브 시스템을 추가하더라도 이 결정과 별도 단계에서 검증한다.\n'''
master_path.write_text(master,encoding='utf-8')

# ---------- Starters doc ----------
starters=starters_path.read_text(encoding='utf-8')
starters=starters.replace('Updated: 2026-08-30','Updated: 2026-09-01',1)
starters=replace_once(starters,
'이 문서는 RUMMY//DUEL을 로그라이크/런 기반 구조로 확장할 때의 **캐릭터, 테마 카드군, 순수 트럼프 스타터**에 대한 현재 설계 결정을 보존한다. 실제 시작 덱 장수와 보상 확률은 플레이테스트로 조정할 수 있지만 아래 방향은 현재 잠금된 설계 기준이다.',
'이 문서는 RUMMY//DUEL을 로그라이크/런 기반 구조로 확장할 때의 **캐릭터, 테마 카드군, 순수 트럼프 스타터**에 대한 현재 설계 결정을 보존한다. 시작 덱 30장 구조와 스타터별 순수/네임드 비율은 v1 기준으로 잠그며, 실제 보상 등장 확률·희귀도·런 경제는 플레이테스트로 조정한다.',
'starters intro')
old='''## 3. 테마 스타터 덱

테마 캐릭터의 시작 덱은 순수카드와 소수의 효과카드를 혼합한다.

잠정 예시(정확한 장수는 미확정):

- 순수 트럼프 약 18~22장
- 해당 캐릭터/테마의 효과카드 약 6~10장
- 소수 범용 네임드 또는 캐릭터 고유 카드

목표는 시작부터 테마 콤보가 완성되어 있는 것이 아니라 **테마 방향의 씨앗만 가진 덱**이다.'''
new='''## 3. 일반 캐릭터 스타터 덱 — v1 잠금

유랑자, 수집가, 회수꾼, 광대의 시작 덱은 동일한 30장 골격을 사용한다.

- 정규 슬롯 29 + 조커 1 = **30장**.
- 순수 정규 카드 **23장**.
- 네임드 정규 카드 **6장**.
- 네임드 조커 **1장**.
- 총 네임드/효과카드 **7장(23.3%)**, 순수카드 **23장(76.7%)**.
- 네임드 정규 6장은 서로 다른 rank+suit 슬롯을 교체하며 원본 29슬롯 기하를 보존한다.

목표는 시작부터 테마 콤보가 완성되어 있는 것이 아니라 **테마 방향의 씨앗만 가진 덱**이다. 정확히 어떤 6장의 네임드와 어떤 네임드 조커를 받는지는 후속 스타터 조립 단계에서 정하되, 하나의 테마 완성 콤보를 고정 지급하지 않는다.'''
starters=replace_once(starters,old,new,'starters general counts')
old_pure='''### PURE 시작 특징

- 시작 덱의 모든 카드는 효과 없는 순수 트럼프 카드.
- 숫자/무늬 분포는 테마 스타터보다 안정적으로 설계할 수 있다.
- 초반 전투의 카드 효과 파워는 낮지만 세트/런의 기본 구조를 가장 순수하게 활용한다.
- 런 도중 어떤 카드군의 네임드도 획득 가능하다.
- 특정 카드군으로 갈아타거나 여러 카드군을 섞는 데 가장 자유롭다.'''
new_pure='''### PURE 시작 특징 — v1 잠금

- 시작 덱은 **순수 정규 29 + 기본 와일드 조커 1 = 30장**이다.
- 정규 29슬롯은 `CORE_IDS.slice(0,29)`를 사용한다: S3–S9 + S10, H2–H4/H7–H10, D2–D8, C3–C9.
- 기본 와일드 조커는 조합용 와일드 판정만 있고 네임드가 아니다. 광대왕 조커의 정리 후 즉시 덱 복귀 같은 고유 효과도 없다.
- 따라서 PURE의 시작 네임드/효과카드는 정확히 **0장**이다.
- 초반 전투의 카드 효과 파워는 낮지만 세트/런의 기본 구조를 가장 순수하게 활용한다.
- 런 도중 어떤 카드군의 네임드도 획득 가능하다.
- 특정 카드군으로 갈아타거나 여러 카드군을 섞는 데 가장 자유롭다.'''
starters=replace_once(starters,old_pure,new_pure,'starters pure')
starters=replace_once(starters,
'''- [ ] 로그라이크 모드의 시작 덱 최소/권장 장수 확정
- [ ] 캐릭터별 시작 효과카드 수와 순수카드 비율 확정
- [ ] PURE 시작 덱의 숫자/무늬 분포 설계
- [ ] 캐릭터별 카드 보상 가중치 시스템 설계''',
'''- [x] 로그라이크 모드의 시작 덱 v1 장수 30장 확정
- [x] 캐릭터별 시작 효과카드 수와 순수카드 비율 확정 — 일반 4스타터 순수 23 / 네임드 7
- [x] PURE 시작 덱 숫자/무늬 분포 확정 — 공통 정규 29슬롯 + 기본 와일드 조커
- [x] 캐릭터별 카드 보상 가중치 시스템 설계 — 기존 `CHARACTERS.weights` 기반 소프트 후보 랭킹, 하드 잠금 없음''',
'starters checklist counts')
starters=replace_once(starters,
'''초안은 공통 시작 구역과 빈 지역 경로, 카드군 하드 잠금 없음만 확정한다. PURE의 `시작 네임드 0장`만 실제 수치로 잠그고, 다른 스타터의 시작 덱 총 장수·순수 비율·효과카드 수·패시브·보상 확률은 플레이테스트 전까지 미확정으로 둔다. 따라서 이 UI는 현재 일반전 덱을 복사하거나 즉시 로그라이크 전투를 시작하지 않는다.''',
'''초안은 공통 시작 구역과 빈 지역 경로, 카드군 하드 잠금 없음에 더해 v1 스타터 수치를 기록한다. 일반 4스타터는 30장 중 순수 23 + 네임드 정규 6 + 네임드 조커 1, PURE는 순수 정규 29 + 기본 와일드 조커 1이다. 직접 전투 패시브는 전원 없음으로 잠그고 기존 캐릭터 `weights`는 보상 후보 랭킹에만 사용한다. 실제 보상 등장 확률은 계속 미확정이며, 이 UI는 현재 일반전 덱을 복사하거나 즉시 로그라이크 전투를 시작하지 않는다.''',
'starters section 9')
starters_path.write_text(starters,encoding='utf-8')

# ---------- Run-init regression ----------
t=run_test_path.read_text(encoding='utf-8')
t=replace_once(t,
"ok(source('createRoguelikeRunDraft').includes(\"namedCardCount:id==='pure'?0:null\"),'only PURE locks the concrete starting named-card count to zero');\nok(source('createRoguelikeRunDraft').includes('exactDeckSize:null')&&source('createRoguelikeRunDraft').includes(\"passivePlan:{status:'unresolved'\"),'unsettled deck size and passive values remain explicitly unresolved');",
"ok(script.includes('const ROGUELIKE_STARTER_REGULAR_SLOTS=Object.freeze(CORE_IDS.slice(0,29));'),'starter baseline reuses the canonical 29-slot structure');\nok(source('createRoguelikeRunDraft').includes('deckPlan:roguelikeStarterDeckPlan(id)'),'run draft materializes the locked starter deck-plan contract');\nok(source('createRoguelikeRunDraft').includes(\"passivePlan:{status:'locked-v1',id:'none',directCombat:false}\"),'v1 starters explicitly have no direct combat passive');",
'run test static counts')
t=replace_once(t,
"vm.runInContext(\"const ROGUELIKE_RUN_DRAFT_KEY='rummyDuelRoguelikeRunDraftV1'; const ROGUELIKE_COMMON_START_ZONE='common-start'; const ROGUELIKE_STARTER_IDS=Object.freeze(['wanderer','collector','salvager','jester','pure']);\",ctx);",
"vm.runInContext(\"const ROGUELIKE_RUN_DRAFT_KEY='rummyDuelRoguelikeRunDraftV1'; const ROGUELIKE_COMMON_START_ZONE='common-start'; const ROGUELIKE_STARTER_IDS=Object.freeze(['wanderer','collector','salvager','jester','pure']); const CORE_IDS=['S3','S4','S5','S6','S7','S8','S9','H2','H3','H4','H7','H8','H9','D2','D3','D4','D5','D6','D7','D8','C3','C4','C5','C6','C7','C8','C9','S10','H10','D10','C10']; const ROGUELIKE_STARTER_REGULAR_SLOTS=Object.freeze(CORE_IDS.slice(0,29)); const ROGUELIKE_STARTER_DECK_SIZE=30; const ROGUELIKE_STARTER_NAMED_REGULAR_COUNT=6;\",ctx);",
'run test constants')
t=replace_once(t,
"install(ctx,'normalizeRoguelikeStarterId','roguelikeStarterUnlocked','roguelikeStarterProfile','createRoguelikeRunDraft','normalizeRoguelikeRunDraft','loadRoguelikeRunDraft','saveRoguelikeRunDraft','clearRoguelikeRunDraft','prepareRoguelikeRunDraft');",
"install(ctx,'normalizeRoguelikeStarterId','roguelikeStarterUnlocked','roguelikeStarterProfile','roguelikeStarterDeckPlan','createRoguelikeRunDraft','normalizeRoguelikeRunDraft','loadRoguelikeRunDraft','saveRoguelikeRunDraft','clearRoguelikeRunDraft','prepareRoguelikeRunDraft');",
'run test install helper')
t=replace_once(t,
"ok(pure.pureStart===true&&pure.characterId===null&&pure.deckPlan.namedCardCount===0,'PURE draft starts with zero named cards but no fake character id');",
"ok(pure.pureStart===true&&pure.characterId===null&&pure.deckPlan.exactDeckSize===30&&pure.deckPlan.namedCardCount===0,'PURE draft is a 30-card zero-named starter with no fake character id');\n  ok(pure.deckPlan.pureRegularCount===29&&pure.deckPlan.pureJokerCount===1&&pure.deckPlan.jokerPolicy==='base-wild-no-effect','PURE uses 29 pure regular slots plus one effectless base wild Joker');\n  ok(pure.deckPlan.regularSlots.join(',')==='S3,S4,S5,S6,S7,S8,S9,H2,H3,H4,H7,H8,H9,D2,D3,D4,D5,D6,D7,D8,C3,C4,C5,C6,C7,C8,C9,S10,H10','PURE regular-slot distribution is locked to the canonical 29-slot baseline');",
'run test pure runtime')
t=replace_once(t,
"ok(wanderer.deckPlan.exactDeckSize===null&&wanderer.deckPlan.namedCardCount===null&&wanderer.passivePlan.status==='unresolved','character starter does not invent unresolved deck/passive numbers');\n  ok(wanderer.rewardPlan.status==='unresolved'&&wanderer.rewardPlan.tendencyHints.combo===1.7,'existing character weights are retained only as prototype tendency hints');",
"ok(wanderer.deckPlan.exactDeckSize===30&&wanderer.deckPlan.pureCardCount===23&&wanderer.deckPlan.namedRegularCount===6&&wanderer.deckPlan.namedJokerCount===1&&wanderer.deckPlan.namedCardCount===7,'character starter locks 23 pure + 6 named regular + 1 named Joker');\n  ok(wanderer.passivePlan.status==='locked-v1'&&wanderer.passivePlan.id==='none'&&wanderer.passivePlan.directCombat===false,'character starter v1 adds no direct combat passive');\n  ok(wanderer.rewardPlan.status==='ranking-weights-v1'&&wanderer.rewardPlan.probabilityStatus==='unresolved'&&wanderer.rewardPlan.hardLock===false&&wanderer.rewardPlan.tendencyHints.combo===1.7,'existing character weights are locked as soft candidate-ranking weights while drop probabilities remain unresolved');",
'run test wanderer runtime')
t=replace_once(t,
"ok(road.includes('- [ ] 캐릭터별 시작 카드 수 / 순수카드 비율 / 보상 가중치 / 패시브 확정'),'quantitative character starter balance remains open');\nok(road.includes('- [ ] PURE 시작 덱의 숫자/무늬 분포 확정'),'PURE distribution remains open');\nok(master.includes('## 11. 런 초기화 구조 프로토타입')&&master.includes('기존 일반전 덱 생성 가중치를 로그라이크 확률로 오인해 재사용하지 않는다'),'master plan records the architectural separation and unresolved reward probabilities');\nok(starters.includes('## 9. 캐릭터 선택 UI / 런 초안 초기화')&&starters.includes('즉시 로그라이크 전투를 시작하지 않는다'),'starter doc records that the draft is not yet a combat mode');",
"ok(road.includes('- [x] 캐릭터별 시작 카드 수 / 순수카드 비율 / 보상 가중치 / 패시브 확정'),'quantitative character starter baseline is closed');\nok(road.includes('- [x] PURE 시작 덱의 숫자/무늬 분포 확정'),'PURE distribution baseline is closed');\nok(master.includes('## 15. 스타터 수치 기준 v1 — 30장 / PURE 기준 구조')&&master.includes('character-tendency-score-v1'),'master plan records the locked starter counts and soft reward-ranking weights');\nok(starters.includes('## 3. 일반 캐릭터 스타터 덱 — v1 잠금')&&starters.includes('순수 정규 29 + 기본 와일드 조커 1'),'starter doc records both general and PURE 30-card baselines');",
'run test docs')
run_test_path.write_text(t,encoding='utf-8')

# ---------- Reward regression ----------
r=reward_test_path.read_text(encoding='utf-8')
r=replace_once(r,
"ok(source('createRoguelikeRunDraft').includes(\"status:'unresolved',candidateAlgorithm:ROGUELIKE_REWARD_ALGORITHM\"),'run draft records ranking algorithm while exact reward probabilities remain unresolved');",
"ok(source('createRoguelikeRunDraft').includes(\"status:'ranking-weights-v1',probabilityStatus:'unresolved',candidateAlgorithm:ROGUELIKE_REWARD_ALGORITHM\")&&source('createRoguelikeRunDraft').includes(\"weightingMode:'character-tendency-score-v1',hardLock:false\"),'run draft locks soft ranking weights while exact reward probabilities remain unresolved');",
'reward test draft plan')
r=replace_once(r,
"ok(road.includes('- [ ] 캐릭터별 시작 카드 수 / 순수카드 비율 / 보상 가중치 / 패시브 확정'),'starter quantitative reward weights remain open');",
"ok(road.includes('- [x] 캐릭터별 시작 카드 수 / 순수카드 비율 / 보상 가중치 / 패시브 확정'),'starter candidate-ranking weights are locked without pretending to lock drop probabilities');",
'reward test road')
r=replace_once(r,
"ok(master.includes('## 12. 행동 태그 기반 카드 보상 후보 알고리즘 v1')&&master.includes('실제 보상 확률표가 아니라 **후보 랭킹 계층**'),'master plan distinguishes candidate ranking from actual drop probabilities');",
"ok(master.includes('## 12. 행동 태그 기반 카드 보상 후보 알고리즘 v1')&&master.includes('실제 보상 확률표가 아니라 **후보 랭킹 계층**')&&master.includes('character-tendency-score-v1'),'master plan distinguishes locked candidate-ranking weights from actual drop probabilities');",
'reward test master')
reward_test_path.write_text(r,encoding='utf-8')

print('patched M11A starter baseline v1 across code, docs, and regressions')

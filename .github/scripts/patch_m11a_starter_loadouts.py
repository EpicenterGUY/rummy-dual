from pathlib import Path

root=Path(__file__).resolve().parents[2]
index_path=root/'index.html'
road_path=root/'ROADMAP.md'
master_path=root/'docs'/'ROGUELIKE_MASTER_PLAN.md'
starters_path=root/'docs'/'ROGUELIKE_DECK_STARTERS.md'
test_path=root/'tests'/'m11a-starter-loadouts.mjs'


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
anchor="const ROGUELIKE_STARTER_NAMED_REGULAR_COUNT=6;"
insert="""const ROGUELIKE_STARTER_NAMED_REGULAR_COUNT=6;
const ROGUELIKE_STARTER_LOADOUTS=Object.freeze({
 wanderer:Object.freeze({regular:Object.freeze({H2:'H2',C5:'C5',S10:'S10',D2:'D2',C6:'C6',H10:'H10'}),joker:'J1'}),
 collector:Object.freeze({regular:Object.freeze({S9:'S9',H7:'H7',H8:'H8',H9:'H9',D7:'D7B',D8:'D8'}),joker:'J3'}),
 salvager:Object.freeze({regular:Object.freeze({S3:'S3',S4:'S4',D3:'D3',D7:'D7',C7:'C7',H3:'H3'}),joker:'J4'}),
 jester:Object.freeze({regular:Object.freeze({C8:'C8',D6:'D6',D5:'D5',D4:'D4',C4:'C4',C3:'C3'}),joker:'J5'}),
 pure:Object.freeze({regular:Object.freeze({}),joker:null})
});
function roguelikeStarterLoadout(id){const key=normalizeRoguelikeStarterId(id),base=ROGUELIKE_STARTER_LOADOUTS[key]||ROGUELIKE_STARTER_LOADOUTS.wanderer;return{regular:{...(base.regular||{})},joker:base.joker||null}}
function roguelikeStarterLoadoutSummary(id){const key=normalizeRoguelikeStarterId(id);if(key==='pure')return'순수 정규 29 + 기본 와일드 조커';const loadout=roguelikeStarterLoadout(key),regular=Object.values(loadout.regular).map(cardId=>NAMED[cardId]?.n||cardId),joker=NAMED[loadout.joker]?.n||loadout.joker;return`${regular.join(' · ')} · ${joker}`}
"""
if 'const ROGUELIKE_STARTER_LOADOUTS=Object.freeze({' not in html:
    html=replace_once(html,anchor,insert,'starter loadout constants')

html=replace_function(html,'roguelikeStarterDeckPlan',"""function roguelikeStarterDeckPlan(id){const key=normalizeRoguelikeStarterId(id),pure=key==='pure',loadout=roguelikeStarterLoadout(key),variantBySlot=pure?{}:{...loadout.regular},namedRegularIds=Object.values(variantBySlot),jokerVariantId=pure?null:loadout.joker,namedRegular=namedRegularIds.length,namedJoker=jokerVariantId?1:0,pureRegular=ROGUELIKE_STARTER_REGULAR_SLOTS.length-namedRegular,pureJoker=pure?1:0,cardBlueprints=ROGUELIKE_STARTER_REGULAR_SLOTS.map(slot=>({slot,variantId:variantBySlot[slot]||null,pure:!variantBySlot[slot]}));cardBlueprints.push({slot:'J',variantId:jokerVariantId,pure:!jokerVariantId,baseWild:pure});return{status:'locked-v1',exactDeckSize:ROGUELIKE_STARTER_DECK_SIZE,regularSlotCount:ROGUELIKE_STARTER_REGULAR_SLOTS.length,jokerCount:1,regularSlots:[...ROGUELIKE_STARTER_REGULAR_SLOTS],pureCardCount:pureRegular+pureJoker,namedCardCount:namedRegular+namedJoker,pureRegularCount:pureRegular,namedRegularCount:namedRegular,pureJokerCount:pureJoker,namedJokerCount:namedJoker,variantBySlot,namedRegularIds,jokerVariantId,cardBlueprints,jokerPolicy:pure?'base-wild-no-effect':'named-joker',mixPolicy:pure?'pure-only-at-start':'pure-majority-plus-few-named',slotIdentity:'base-rank-suit'}}""")
html=replace_function(html,'createRoguelikeRunDraft',"""function createRoguelikeRunDraft(starterId=progress?.roguelikeStarter||'wanderer'){let id=normalizeRoguelikeStarterId(starterId);if(!roguelikeStarterUnlocked(id))id='wanderer';const profile=roguelikeStarterProfile(id);return{version:3,mode:'roguelike-prototype',status:'prepared',runId:`rg-${Date.now().toString(36)}`,starterId:id,characterId:id==='pure'?null:id,pureStart:id==='pure',startZone:ROGUELIKE_COMMON_START_ZONE,currentZone:ROGUELIKE_COMMON_START_ZONE,regionPath:[],nodeIndex:0,themeLocks:[],allowCrossThemeRewards:true,deckPlan:roguelikeStarterDeckPlan(id),passivePlan:{status:'locked-v1',id:'none',directCombat:false},rewardPlan:{status:'ranking-weights-v1',probabilityStatus:'unresolved',candidateAlgorithm:ROGUELIKE_REWARD_ALGORITHM,roles:ROGUELIKE_REWARD_ROLES.map(x=>x.id),weightingMode:'character-tendency-score-v1',hardLock:false,tendencyHints:{...profile.tendencyHints}},createdAt:new Date().toISOString()}}""")
html=replace_function(html,'roguelikeRunDraftText',"""function roguelikeRunDraftText(draft=loadRoguelikeRunDraft()){if(!draft)return'런 초안 없음 · 스타터를 고른 뒤 구조 초안을 만들 수 있습니다.';const profile=roguelikeStarterProfile(draft.starterId),deck=draft.pureStart?'30장 · 순수 정규 29 + 기본 와일드 조커 1 · 효과 0':'30장 · 순수 23 + 네임드 정규 6 + 네임드 조커 1',loadout=roguelikeStarterLoadoutSummary(draft.starterId);return`<b>${profile.name}</b> · 공통 시작 구역 · ${deck}<br>시작 구성 · ${loadout}<br>카드군 하드 잠금 없음 · 직접 전투 패시브 없음 · 보상 후보 소프트 가중치 · 실제 보상 확률 미확정 · 현재 전투에는 아직 연결하지 않음`}""")
index_path.write_text(html,encoding='utf-8')

# ---------- ROADMAP ----------
road=road_path.read_text(encoding='utf-8')
road_anchor="""  - v1 스타터 직접 전투 패시브는 전원 `none`으로 잠근다. 캐릭터 차이는 시작 네임드 구성과 소프트 보상 랭킹에서 만들고 실제 등장 확률/희귀도는 후속 경제 데이터에서 정한다.
- [x] 캐릭터 선택 UI와 로그라이크 런 초기화 구조 설계"""
road_insert="""  - v1 스타터 직접 전투 패시브는 전원 `none`으로 잠근다. 캐릭터 차이는 시작 네임드 구성과 소프트 보상 랭킹에서 만들고 실제 등장 확률/희귀도는 후속 경제 데이터에서 정한다.
- [x] 캐릭터별 실제 시작 네임드 6 + 조커 1 조합 확정
  - 유랑자: `H2 귀환자 / C5 연결고리 / S10 폭주기관차 / D2 외상 거래 / C6 중간관리자 / H10 연명 + J1 광대왕 조커`.
  - 수집가: `S9 잠복자 / H7 행운의 일곱 / H8 응급 보호구 / H9 보험설계사 / D7B 감정사(D7 슬롯) / D8 환전상 + J3 쌍면 조커`.
  - 회수꾼: `S3 쥐구멍 / S4 미끼 사냥꾼 / D3 사기 계약서 / D7 황금손 / C7 기생충 / H3 미끼 + J4 빈자리 조커`.
  - 광대: `C8 복사기 / D6 예약 발송 / D5 위조범 / D4 밀수품 / C4 샛길 / C3 밀수업자 + J5 반역자 조커`.
  - 네 스타터의 v1 시작 네임드는 서로 정확한 카드 ID를 공유하지 않고, 테마 전용 `themeId` 카드도 넣지 않는다. 현재 캐릭터 성향 점수에서 각 구성은 자기 캐릭터 점수가 다른 캐릭터보다 가장 높도록 회귀로 검증한다.
- [x] 캐릭터 선택 UI와 로그라이크 런 초기화 구조 설계"""
if '캐릭터별 실제 시작 네임드 6 + 조커 1 조합 확정' not in road:
    road=replace_once(road,road_anchor,road_insert,'road loadout item')
road_path.write_text(road,encoding='utf-8')

# ---------- starter doc ----------
starters=starters_path.read_text(encoding='utf-8')
starters=replace_once(starters,
"목표는 시작부터 테마 콤보가 완성되어 있는 것이 아니라 **테마 방향의 씨앗만 가진 덱**이다. 정확히 어떤 6장의 네임드와 어떤 네임드 조커를 받는지는 후속 스타터 조립 단계에서 정하되, 하나의 테마 완성 콤보를 고정 지급하지 않는다.",
"""목표는 시작부터 테마 콤보가 완성되어 있는 것이 아니라 **행동 방향의 씨앗만 가진 덱**이다. v1 실제 시작 네임드는 다음으로 잠근다.

| 스타터 | 네임드 정규 6장 | 네임드 조커 | 출발 행동 |
| --- | --- | --- | --- |
| 유랑자 | H2 귀환자, C5 연결고리, S10 폭주기관차, D2 외상 거래, C6 중간관리자, H10 연명 | J1 광대왕 조커 | 조합 연결 / 런 확장 / 패순환 |
| 수집가 | S9 잠복자, H7 행운의 일곱, H8 응급 보호구, H9 보험설계사, D7B 감정사(D7 슬롯), D8 환전상 | J3 쌍면 조커 | 보유 / 보호 / 지속 가치 |
| 회수꾼 | S3 쥐구멍, S4 미끼 사냥꾼, D3 사기 계약서, D7 황금손, C7 기생충, H3 미끼 | J4 빈자리 조커 | 버림패 / 회수 / 순환 / 상대 조합 상호작용 |
| 광대 | C8 복사기, D6 예약 발송, D5 위조범, D4 밀수품, C4 샛길, C3 밀수업자 | J5 반역자 조커 | 규칙 변형 / 런 판정 비틀기 / 변칙 붙이기 |

네 구성은 시작 시 **테마 전용 카드 0장**이며 서로 같은 정확한 네임드 ID도 공유하지 않는다. 따라서 캐릭터 정체성은 보이되 V-SIGNAL, ZERO-SIGHT, POINT-BLANK 같은 특정 카드군의 초동-엔진을 공짜로 완성하지 않는다. 현재 `CHARACTERS.weights`와 `TENDENCY_BY_TAG` 기준으로 각 7장 구성의 성향 점수는 자기 캐릭터에서 가장 높아야 하며 이를 회귀 테스트로 고정한다.""",
'starter exact loadouts')
starters=replace_once(starters,'- [ ] 다른 카드군 선택을 막는 하드 클래스 제한은 두지 않기','- [x] 다른 카드군 선택을 막는 하드 클래스 제한은 두지 않기','starter checklist hard lock')
starters=replace_once(starters,'- [ ] 동일 랭크+무늬 순수카드 → 네임드 변형 교체 UI/데이터 구조 검토','- [x] 동일 랭크+무늬 순수카드 → 네임드 변형 교체 UI/데이터 구조 검토','starter checklist replacement')
starters=replace_once(starters,'- [ ] 카드 제거와 네임드 교체의 경제적 가치 비교','- [x] 카드 제거와 네임드 교체의 경제적 가치 비교','starter checklist removal')
starters=replace_once(starters,
"초안은 공통 시작 구역과 빈 지역 경로, 카드군 하드 잠금 없음에 더해 v1 스타터 수치를 기록한다. 일반 4스타터는 30장 중 순수 23 + 네임드 정규 6 + 네임드 조커 1, PURE는 순수 정규 29 + 기본 와일드 조커 1이다. 직접 전투 패시브는 전원 없음으로 잠그고 기존 캐릭터 `weights`는 보상 후보 랭킹에만 사용한다. 실제 보상 등장 확률은 계속 미확정이며, 이 UI는 현재 일반전 덱을 복사하거나 즉시 로그라이크 전투를 시작하지 않는다.",
"초안은 공통 시작 구역과 빈 지역 경로, 카드군 하드 잠금 없음에 더해 v1 스타터 수치와 실제 네임드 ID를 기록한다. 일반 4스타터는 30장 중 순수 23 + 위 표의 네임드 정규 6 + 네임드 조커 1, PURE는 순수 정규 29 + 기본 와일드 조커 1이다. `deckPlan.cardBlueprints`는 29개 정규 슬롯의 `variantId`와 조커 변형을 포함하는 30장 조립 계약을 제공한다. 직접 전투 패시브는 전원 없음으로 잠그고 기존 캐릭터 `weights`는 보상 후보 랭킹에만 사용한다. 실제 보상 등장 확률은 계속 미확정이며, 이 UI는 현재 일반전 덱을 복사하거나 즉시 로그라이크 전투를 시작하지 않는다.",
'starter draft paragraph')
starters_path.write_text(starters,encoding='utf-8')

# ---------- master plan ----------
master=master_path.read_text(encoding='utf-8')
master=replace_once(master,
'- [ ] 캐릭터 수와 캐릭터별 시작 덱/패시브 확정\n- [ ] PURE 시작 덱 분포와 카드 외부 지원 확정\n- [ ] 카드 보상 3슬롯 생성 알고리즘 설계\n- [ ] 행동 태그 기반 보상 추천 규칙 설계',
'- [x] v1 캐릭터 수와 캐릭터별 시작 덱/패시브 확정 — 유랑자/수집가/회수꾼/광대 + PURE, 일반 4스타터 실제 네임드 6+1, 직접 전투 패시브 없음\n- [x] PURE 시작 덱 분포 확정 — 정규 29 + 기본 와일드 조커 1\n- [ ] PURE 카드 외부 지원 유물/특전 확정\n- [x] 카드 보상 3슬롯 생성 알고리즘 설계\n- [x] 행동 태그 기반 보상 추천 규칙 설계',
'master followup status')
master=replace_once(master,
'- PURE는 시작 시 네임드 0장을 확정한다. 그러나 런 중 네임드 획득은 허용한다.\n- 다른 캐릭터는 `순수 다수 + 효과카드 소수` 방향만 보존하며 정확한 시작 덱 장수와 비율은 아직 넣지 않는다.\n- 캐릭터 패시브와 실제 카드 보상 확률/가중치 수치는 `unresolved`로 둔다. 기존 일반전 덱 생성 가중치를 로그라이크 확률로 오인해 재사용하지 않는다.',
'- 모든 스타터는 30장이다. 일반 4스타터는 순수 23 + 네임드 정규 6 + 네임드 조커 1이며, PURE는 순수 정규 29 + 기본 와일드 조커 1로 네임드 0장을 유지한다.\n- 일반 4스타터의 실제 네임드 ID는 `ROGUELIKE_STARTER_LOADOUTS`로 고정하고 `deckPlan.cardBlueprints`에 30장 조립 청사진을 저장한다.\n- 직접 전투 패시브는 v1에서 전원 `none`이다. 캐릭터 `weights`는 `character-tendency-score-v1` 보상 후보 랭킹에만 쓰며 실제 보상 등장 확률은 계속 `unresolved`로 둔다.',
'master stale run-init bullets')
master=replace_once(master,
'현재 UI 프로토타입에서는 행동 태그 보상 후보를 누르면 `현재 → 교체 후` 확인 패널이 열리며 취소할 수 있다. 실제 적용 버튼은 비활성 상태다. 이유는 로그라이크 시작 덱 장수와 추가/제거 경제가 아직 확정되지 않았기 때문이다. 따라서 이 단계는 **교체 의미와 사용자 확인 흐름만 잠그며 일반 1대1 덱빌더나 진행도 데이터를 수정하지 않는다.**',
'현재 UI 프로토타입에서는 행동 태그 보상 후보를 누르면 `현재 → 교체 후` 확인 패널이 열리며 취소할 수 있다. 실제 적용 버튼은 비활성 상태다. 시작 덱 장수와 스타터 청사진은 이제 확정됐지만, 실제 run session 덱 상태와 보상/상점/이벤트 공통 commit 계층이 아직 연결되지 않았기 때문이다. 따라서 이 단계는 **교체 의미와 사용자 확인 흐름만 잠그며 일반 1대1 덱빌더나 진행도 데이터를 수정하지 않는다.**',
'master replacement stale reason')
master=replace_once(master,
'- 6개의 네임드 정규는 서로 다른 원본 슬롯을 사용해야 한다. 시작부터 하나의 테마 완성 콤보를 고정 지급하지 않으며 실제 카드 ID 선정은 후속 스타터 조립 단계에서 한다.',
'''- 6개의 네임드 정규는 서로 다른 원본 슬롯을 사용한다. 시작부터 하나의 테마 완성 콤보를 고정 지급하지 않는다.
- 유랑자: `H2 / C5 / S10 / D2 / C6 / H10 + J1`.
- 수집가: `S9 / H7 / H8 / H9 / D7B(D7) / D8 + J3`.
- 회수꾼: `S3 / S4 / D3 / D7 / C7 / H3 + J4`.
- 광대: `C8 / D6 / D5 / D4 / C4 / C3 + J5`.
- 네 스타터는 정확한 네임드 ID를 서로 공유하지 않으며 테마 전용 카드를 시작 덱에 넣지 않는다. 성향은 범용 카드의 행동 태그로만 제시한다.''',
'master exact ids')
master=master.rstrip()+'''\n\n## 16. 실제 스타터 네임드 조립 v1\n\n`ROGUELIKE_STARTER_LOADOUTS`는 일반 4스타터의 네임드 정규 6장과 네임드 조커 1장을 실제 카드 ID로 고정한다. `roguelikeStarterDeckPlan()`은 이 프리셋을 공통 29슬롯에 덮어써 `variantBySlot`, `namedRegularIds`, `jokerVariantId`, 30개의 `cardBlueprints`를 만든다. 아직 일반 전투 `makeDeck()`에 연결하지는 않으며 이후 실제 run session이 이 청사진을 소비한다.\n\n선정 원칙:\n\n- 테마 전용 `themeId` 카드는 스타터에서 제외한다. 캐릭터 선택이 특정 지역/테마의 완성 초동을 공짜로 지급하지 않게 한다.\n- 네 캐릭터 사이에서 정확한 시작 네임드 ID를 공유하지 않는다. 첫 런부터 캐릭터 인상이 겹치는 것을 줄인다.\n- 정규 네임드는 모두 공통 29슬롯 안에 있고 캐릭터당 원본 슬롯 중복이 없다. 따라서 30장 SET/RUN 구조는 모든 스타터에서 동일하다.\n- 현재 `CHARACTERS.weights × TENDENCY_BY_TAG` 단순 성향 합계로 각 7장 프리셋을 평가했을 때 자기 캐릭터 점수가 다른 캐릭터보다 가장 높아야 한다. 이는 승률 보정이 아니라 **출발 행동 정체성 검증**이다.\n- 실제 카드 파워와 승률은 M12 실전 표본으로 다시 본다. 성향 점수만으로 강약 밸런스를 확정하지 않는다.\n'''
master_path.write_text(master,encoding='utf-8')

# ---------- new regression ----------
test_path.write_text(r'''import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const master=fs.readFileSync(new URL('../docs/ROGUELIKE_MASTER_PLAN.md',import.meta.url),'utf8');
const starters=fs.readFileSync(new URL('../docs/ROGUELIKE_DECK_STARTERS.md',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let par=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')par++;else if(script[i]===')')par--;else if(script[i]==='{'&&par===0){brace=i;break}}let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
function declaration(name){const marker=`const ${name}=`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let quote=null,esc=false,depth=0,started=false;for(let i=start+marker.length;i<script.length;i++){const ch=script[i];if(quote){if(esc)esc=false;else if(ch==='\\')esc=true;else if(ch===quote)quote=null;continue}if(ch==='\''||ch==='"'||ch==='`'){quote=ch;continue}if(ch==='{'||ch==='['||ch==='('){depth++;started=true}else if(ch==='}'||ch===']'||ch===')')depth--;else if(ch===';'&&started&&depth===0)return script.slice(start,i+1)}throw new Error(`unterminated declaration ${name}`)}
new Function(script);
const ctx=vm.createContext({console,Date,Math,Object,Array,String,JSON,Map,Set});
for(const name of ['NAMED','CHARACTERS','TENDENCY_BY_TAG','ROGUELIKE_STARTER_IDS','ROGUELIKE_STARTER_REGULAR_SLOTS','ROGUELIKE_STARTER_DECK_SIZE','ROGUELIKE_STARTER_NAMED_REGULAR_COUNT','ROGUELIKE_STARTER_LOADOUTS'])vm.runInContext(declaration(name),ctx);
vm.runInContext(source('normalizeRoguelikeStarterId'),ctx);
vm.runInContext(source('roguelikeStarterLoadout'),ctx);
vm.runInContext(source('roguelikeStarterDeckPlan'),ctx);
const starters4=['wanderer','collector','salvager','jester'];
const baseline=new Set(vm.runInContext('[...ROGUELIKE_STARTER_REGULAR_SLOTS]',ctx));
const seen=new Set();
for(const starter of starters4){
  const load=vm.runInContext(`roguelikeStarterLoadout('${starter}')`,ctx);
  const ids=Object.values(load.regular);
  ok(ids.length===6,`${starter} has exactly six regular named starters`);
  ok(new Set(Object.keys(load.regular)).size===6,`${starter} uses six distinct canonical regular slots`);
  for(const [slot,id] of Object.entries(load.regular)){
    const def=vm.runInContext(`NAMED[${JSON.stringify(id)}]`,ctx);
    ok(!!def,`${starter} regular ${id} exists in live NAMED data`);
    ok((def.slot||id)===slot&&baseline.has(slot),`${starter} ${id} preserves a canonical starter slot`);
    ok(!def.themeId,`${starter} ${id} is generic rather than theme-locked`);
    ok(!seen.has(id),`${starter} ${id} is not shared by another v1 starter`);seen.add(id);
  }
  const jdef=vm.runInContext(`NAMED[${JSON.stringify(load.joker)}]`,ctx);
  ok(!!jdef&&String(load.joker).startsWith('J'),`${starter} has a live named Joker`);
  ok(!seen.has(load.joker),`${starter} Joker ${load.joker} is not shared by another v1 starter`);seen.add(load.joker);
  const plan=vm.runInContext(`roguelikeStarterDeckPlan('${starter}')`,ctx);
  ok(plan.cardBlueprints.length===30&&plan.namedRegularIds.length===6&&plan.jokerVariantId===load.joker,`${starter} materializes a 30-card blueprint with its 6+1 named ids`);
  ok(plan.cardBlueprints.filter(x=>x.slot!=='J'&&x.variantId).length===6&&plan.cardBlueprints.filter(x=>x.slot==='J'&&x.variantId).length===1,`${starter} blueprint has exactly six named regulars and one named Joker`);
  const affinity={};
  for(const target of starters4){
    const weights=vm.runInContext(`CHARACTERS[${JSON.stringify(target)}].weights`,ctx);
    affinity[target]=[...ids,load.joker].reduce((sum,id)=>{const tag=vm.runInContext(`NAMED[${JSON.stringify(id)}].t`,ctx);const tendencies=vm.runInContext(`TENDENCY_BY_TAG[${JSON.stringify(tag)}]||[]`,ctx);return sum+tendencies.reduce((n,t)=>n+(weights[t]||0),0)},0);
  }
  const best=Math.max(...Object.values(affinity));
  ok(affinity[starter]===best&&Object.entries(affinity).filter(([,v])=>v===best).length===1,`${starter} loadout has uniquely highest affinity for its own character weights`);
}
const pure=vm.runInContext("roguelikeStarterDeckPlan('pure')",ctx);
ok(pure.cardBlueprints.length===30&&pure.namedRegularIds.length===0&&pure.jokerVariantId===null,'PURE blueprint stays 30 cards with zero named variants');
ok(pure.cardBlueprints.slice(0,29).every(x=>x.variantId===null&&x.pure)&&pure.cardBlueprints[29].slot==='J'&&pure.cardBlueprints[29].baseWild===true,'PURE blueprint is 29 pure regulars plus the effectless base wild Joker');
ok(road.includes('- [x] 캐릭터별 실제 시작 네임드 6 + 조커 1 조합 확정'),'ROADMAP closes actual v1 starter named composition');
ok(master.includes('## 16. 실제 스타터 네임드 조립 v1')&&master.includes('ROGUELIKE_STARTER_LOADOUTS'),'master plan records the actual starter loadout contract');
ok(starters.includes('H2 귀환자, C5 연결고리')&&starters.includes('C8 복사기, D6 예약 발송'),'starter doc exposes the locked character loadouts');
console.log('M11A starter loadout regression passed.');
''',encoding='utf-8')

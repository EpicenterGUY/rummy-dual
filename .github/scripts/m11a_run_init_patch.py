from pathlib import Path

p=Path('index.html'); s=p.read_text()
road=Path('ROADMAP.md'); r=road.read_text()
master=Path('docs/ROGUELIKE_MASTER_PLAN.md'); m=master.read_text()
starters=Path('docs/ROGUELIKE_DECK_STARTERS.md'); d=starters.read_text()

def span(text,name):
    marker=f'function {name}('; start=text.find(marker)
    if start<0: raise SystemExit(f'missing {name}')
    brace=text.find('{',start); depth=0
    for i in range(brace,len(text)):
        if text[i]=='{': depth+=1
        elif text[i]=='}':
            depth-=1
            if depth==0:return start,i+1
    raise SystemExit(f'unterminated {name}')

def replace_fn(text,name,new):
    a,b=span(text,name); return text[:a]+new+text[b:]

# Separate roguelike starter UI from the current battle character/theme/deck builder.
html_anchor='<div class="themePickerNote">캐릭터는 덱의 행동 경향을, 캐릭터군은 테마 카드의 출현 우선도를 정합니다. 테마를 골라도 일반·다른 카드와 섞이는 오픈형 덱입니다.</div><div class="unlockGroup deckBuilderGroup">'
html_insert='<div class="themePickerNote">캐릭터는 덱의 행동 경향을, 캐릭터군은 테마 카드의 출현 우선도를 정합니다. 테마를 골라도 일반·다른 카드와 섞이는 오픈형 덱입니다.</div><div class="unlockGroup roguelikeStarterGroup"><h4>로그라이크 런 스타터 · 구조 프로토타입</h4><div class="themePickerNote">일반 대전의 캐릭터/테마 선택과 분리된 런 출발점입니다. 캐릭터는 방향만 제시하며 카드군을 잠그지 않습니다. 시작 덱 장수·패시브·정확한 보상 확률은 아직 확정하지 않습니다.</div><div id="roguelikeStarterGrid" class="charGrid"></div><div id="roguelikeRunDraftStatus" class="deckWarn">런 초안 없음 · 스타터를 고른 뒤 구조 초안을 만들 수 있습니다.</div><div class="deckBuilderHead"><button id="roguelikePrepareBtn" class="pixelBtn primary" type="button">런 구조 초안 만들기</button><button id="roguelikeClearDraftBtn" class="pixelBtn" type="button">초안 지우기</button></div></div><div class="unlockGroup deckBuilderGroup">'
if html_insert not in s:
    if html_anchor not in s: raise SystemExit('roguelike UI anchor missing')
    s=s.replace(html_anchor,html_insert,1)

# Run-init data lives beside character definitions, but does not feed current battle deck generation.
char_anchor="};\nconst TENDENCY_BY_TAG={"
run_block="""};
const ROGUELIKE_RUN_DRAFT_KEY='rummyDuelRoguelikeRunDraftV1';
const ROGUELIKE_COMMON_START_ZONE='common-start';
const ROGUELIKE_STARTER_IDS=Object.freeze(['wanderer','collector','salvager','jester','pure']);
function normalizeRoguelikeStarterId(id){return ROGUELIKE_STARTER_IDS.includes(id)?id:'wanderer'}
function roguelikeStarterUnlocked(id){const key=normalizeRoguelikeStarterId(id);return key==='pure'||(typeof charUnlocked==='function'&&charUnlocked(key))}
function roguelikeStarterProfile(id){const key=normalizeRoguelikeStarterId(id);if(key==='pure')return{id:'pure',name:'PURE',short:'백지형',desc:'효과카드 0장으로 시작하는 순수 트럼프 스타터. 런 중 어떤 네임드도 획득할 수 있다.',pure:true,tendencyHints:{}};const c=CHARACTERS[key]||CHARACTERS.wanderer;return{id:key,name:c.name,short:c.short,desc:c.desc,pure:false,tendencyHints:{...(c.weights||{})}}}
function createRoguelikeRunDraft(starterId=progress?.roguelikeStarter||'wanderer'){let id=normalizeRoguelikeStarterId(starterId);if(!roguelikeStarterUnlocked(id))id='wanderer';const profile=roguelikeStarterProfile(id);return{version:1,mode:'roguelike-prototype',status:'prepared',runId:`rg-${Date.now().toString(36)}`,starterId:id,characterId:id==='pure'?null:id,pureStart:id==='pure',startZone:ROGUELIKE_COMMON_START_ZONE,currentZone:ROGUELIKE_COMMON_START_ZONE,regionPath:[],nodeIndex:0,themeLocks:[],allowCrossThemeRewards:true,deckPlan:{status:'unresolved',exactDeckSize:null,pureCardCount:null,namedCardCount:id==='pure'?0:null,mixPolicy:id==='pure'?'pure-only-at-start':'pure-majority-plus-few-named',slotIdentity:'base-rank-suit'},passivePlan:{status:'unresolved',id:null},rewardPlan:{status:'unresolved',tendencyHints:{...profile.tendencyHints}},createdAt:new Date().toISOString()}}
function normalizeRoguelikeRunDraft(x){if(!x||typeof x!=='object'||x.mode!=='roguelike-prototype'||x.status!=='prepared')return null;const base=createRoguelikeRunDraft(x.starterId),runId=typeof x.runId==='string'&&x.runId?x.runId:base.runId,createdAt=typeof x.createdAt==='string'&&x.createdAt?x.createdAt:base.createdAt;return{...base,runId,createdAt,themeLocks:[],regionPath:[],nodeIndex:0,currentZone:ROGUELIKE_COMMON_START_ZONE}}
function loadRoguelikeRunDraft(){if(typeof localStorage==='undefined')return null;try{return normalizeRoguelikeRunDraft(JSON.parse(localStorage.getItem(ROGUELIKE_RUN_DRAFT_KEY)||'null'))}catch{return null}}
function saveRoguelikeRunDraft(draft){if(typeof localStorage==='undefined')return false;const clean=normalizeRoguelikeRunDraft(draft);if(!clean)return false;try{localStorage.setItem(ROGUELIKE_RUN_DRAFT_KEY,JSON.stringify(clean));return true}catch{return false}}
function clearRoguelikeRunDraft(){if(typeof localStorage==='undefined')return false;try{localStorage.removeItem(ROGUELIKE_RUN_DRAFT_KEY);return true}catch{return false}}
function prepareRoguelikeRunDraft(starterId=progress?.roguelikeStarter||'wanderer'){const draft=createRoguelikeRunDraft(starterId);saveRoguelikeRunDraft(draft);return draft}
function roguelikeRunDraftText(draft=loadRoguelikeRunDraft()){if(!draft)return'런 초안 없음 · 스타터를 고른 뒤 구조 초안을 만들 수 있습니다.';const profile=roguelikeStarterProfile(draft.starterId),deck=draft.pureStart?'PURE 시작 · 네임드 0장':'순수 다수 + 효과카드 소수 · 정확한 장수 미확정';return`<b>${profile.name}</b> · 공통 시작 구역 · ${deck}<br>카드군 하드 잠금 없음 · 패시브/보상 확률 미확정 · 현재 전투에는 아직 연결하지 않음`}
function renderRoguelikeStarterPicker(){const grid=document.getElementById('roguelikeStarterGrid'),status=document.getElementById('roguelikeRunDraftStatus'),prepare=document.getElementById('roguelikePrepareBtn'),clear=document.getElementById('roguelikeClearDraftBtn');if(!grid)return;let selected=normalizeRoguelikeStarterId(progress.roguelikeStarter);if(!roguelikeStarterUnlocked(selected))selected='wanderer';progress.roguelikeStarter=selected;grid.innerHTML=ROGUELIKE_STARTER_IDS.map(id=>{const p=roguelikeStarterProfile(id),open=roguelikeStarterUnlocked(id),on=id===selected,meta=p.pure?'효과카드 0장 시작 · 이후 네임드 획득 가능':`출발 성향 · ${p.short}`;return`<div class="charCard ${on?'selected':''} ${open?'':'locked'}"><div class="charName">${p.name} ${open?'':'🔒'}</div><div class="charMeta">${meta}${open?'':' · 현재 진행도에서 잠김'}</div><div class="charPassive">${p.desc}<br><b>런 원칙:</b> 다른 카드군 획득을 막지 않음</div><button class="pixelBtn ${on?'primary':''}" data-roguelike-starter="${id}" ${open?'':'disabled'}>${on?'선택됨':'선택'}</button></div>`}).join('');grid.querySelectorAll('[data-roguelike-starter]').forEach(b=>b.onclick=()=>{const id=b.dataset.roguelikeStarter;if(!roguelikeStarterUnlocked(id))return;progress.roguelikeStarter=id;saveProgress();renderRoguelikeStarterPicker()});if(status)status.innerHTML=roguelikeRunDraftText();if(prepare)prepare.onclick=()=>{prepareRoguelikeRunDraft(progress.roguelikeStarter);renderRoguelikeStarterPicker()};if(clear)clear.onclick=()=>{clearRoguelikeRunDraft();renderRoguelikeStarterPicker()}}
const TENDENCY_BY_TAG={"""
if 'const ROGUELIKE_RUN_DRAFT_KEY=' not in s:
    if char_anchor not in s: raise SystemExit('character block anchor missing')
    s=s.replace(char_anchor,run_block,1)

# Persist only the selected roguelike starter in normal progress. The actual draft has its own storage key.
default_progress="""function defaultProgress(){return{totalClears:0,selectedChar:'wanderer',selectedTheme:'mixed',roguelikeStarter:'wanderer',tutorialPromptSeen:false,tutorialCompleted:false,asymmetricRankIntroSeen:false,deckBuild:defaultDeckBuild(),chars:{wanderer:0,collector:0,salvager:0,jester:0}}}"""
s=replace_fn(s,'defaultProgress',default_progress)
normalize_progress="""function normalizeProgress(x){const base=defaultProgress();if(!x||typeof x!=='object')return base;const chars={...base.chars};for(const id of Object.keys(chars)){const n=Number(x.chars?.[id]);if(Number.isFinite(n)&&n>=0)chars[id]=Math.floor(n)}const tc=Number(x.totalClears);return{totalClears:Number.isFinite(tc)&&tc>=0?Math.floor(tc):0,selectedChar:Object.prototype.hasOwnProperty.call(CHARACTERS,x.selectedChar)?x.selectedChar:'wanderer',selectedTheme:Object.prototype.hasOwnProperty.call(THEME_BUILD_PROFILES,x.selectedTheme)?x.selectedTheme:'mixed',roguelikeStarter:normalizeRoguelikeStarterId(x.roguelikeStarter),tutorialPromptSeen:typeof x.tutorialPromptSeen==='boolean'?x.tutorialPromptSeen:false,tutorialCompleted:typeof x.tutorialCompleted==='boolean'?x.tutorialCompleted:false,asymmetricRankIntroSeen:typeof x.asymmetricRankIntroSeen==='boolean'?x.asymmetricRankIntroSeen:false,deckBuild:normalizeDeckBuild(x.deckBuild),chars}}"""
s=replace_fn(s,'normalizeProgress',normalize_progress)

# Hook the independent picker into the existing progress modal render.
a,b=span(s,'renderProgress'); fn=s[a:b]
if 'renderRoguelikeStarterPicker();renderDeckBuilder()' not in fn:
    if 'renderDeckBuilder()' not in fn: raise SystemExit('renderProgress deck builder anchor missing')
    pos=fn.rfind('renderDeckBuilder()')
    fn=fn[:pos]+'renderRoguelikeStarterPicker();'+fn[pos:]
s=s[:a]+fn+s[b:]

# Roadmap: this item is architecture/UI only; quantitative starter balance remains open.
old='- [ ] 캐릭터 선택 UI와 로그라이크 런 초기화 구조 설계'
new='- [x] 캐릭터 선택 UI와 로그라이크 런 초기화 구조 설계 — 일반 1대1의 캐릭터/테마/30장 덱 선택과 로그라이크 스타터를 분리하고 `유랑자 / 수집가 / 회수꾼 / 광대 / PURE` 전용 선택 UI를 추가. `rummyDuelRoguelikeRunDraftV1` 초안은 공통 시작 구역, 지역 경로, 노드 위치, 카드군 하드잠금 없음, 원본 랭크+무늬 슬롯 정체성을 명시하며 PURE만 시작 네임드 0장을 확정값으로 기록. 시작 덱 총 장수·순수/효과 비율·패시브·정확한 보상 확률은 미확정 상태로 보존하고 현재 일반 전투에는 아직 연결하지 않음'
if old in r:r=r.replace(old,new,1)
elif new not in r:raise SystemExit('roadmap M11A run-init item missing')

master_append="""

## 11. 런 초기화 구조 프로토타입

일반 1대1 전투의 `캐릭터 경향 + 테마 + 30장 덱빌더`와 로그라이크 시작 선택을 분리한다. 로그라이크 스타터는 `유랑자 / 수집가 / 회수꾼 / 광대 / PURE` 다섯 출발점을 별도 UI에서 고르며, 캐릭터 선택은 **보상·행동 방향의 힌트**이지 특정 테마 카드군 잠금이 아니다.

현재 `rummyDuelRoguelikeRunDraftV1` 초안 구조는 다음 원칙만 확정한다.

- 모든 런은 `common-start` 공통 시작 구역에서 출발한다.
- `themeLocks`는 항상 빈 배열이며 타 테마 카드 보상을 허용한다.
- 지역 경로와 노드 위치는 빈 경로/0에서 시작한다.
- 카드 슬롯 정체성은 기존 `base rank + suit`를 유지한다.
- PURE는 시작 시 네임드 0장을 확정한다. 그러나 런 중 네임드 획득은 허용한다.
- 다른 캐릭터는 `순수 다수 + 효과카드 소수` 방향만 보존하며 정확한 시작 덱 장수와 비율은 아직 넣지 않는다.
- 캐릭터 패시브와 실제 카드 보상 확률/가중치 수치는 `unresolved`로 둔다. 기존 일반전 덱 생성 가중치를 로그라이크 확률로 오인해 재사용하지 않는다.
- 현재 단계의 `prepared` 초안은 전투에 자동 연결하지 않는다. 지역/보상/스타터 수치가 확정된 뒤 실제 run session으로 승격한다.
"""
if '## 11. 런 초기화 구조 프로토타입' not in m:m=m.rstrip()+master_append+'\n'

starter_append="""

## 9. 캐릭터 선택 UI / 런 초안 초기화

로그라이크 스타터 선택은 기존 일반전의 `캐릭터 + 테마` 선택과 분리한다. 현재 프로토타입은 유랑자, 수집가, 회수꾼, 광대와 PURE를 출발점으로 보여 주며, 선택 결과는 별도 런 초안에 저장한다.

초안은 공통 시작 구역과 빈 지역 경로, 카드군 하드 잠금 없음만 확정한다. PURE의 `시작 네임드 0장`만 실제 수치로 잠그고, 다른 스타터의 시작 덱 총 장수·순수 비율·효과카드 수·패시브·보상 확률은 플레이테스트 전까지 미확정으로 둔다. 따라서 이 UI는 현재 일반전 덱을 복사하거나 즉시 로그라이크 전투를 시작하지 않는다.
"""
if '## 9. 캐릭터 선택 UI / 런 초안 초기화' not in d:d=d.rstrip()+starter_append+'\n'

p.write_text(s);road.write_text(r);master.write_text(m);starters.write_text(d)
print('M11A roguelike starter picker and run-draft initialization installed')

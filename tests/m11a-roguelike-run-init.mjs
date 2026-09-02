import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const master=fs.readFileSync(new URL('../docs/ROGUELIKE_MASTER_PLAN.md',import.meta.url),'utf8');
const starters=fs.readFileSync(new URL('../docs/ROGUELIKE_DECK_STARTERS.md',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let par=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')par++;else if(script[i]===')')par--;else if(script[i]==='{'&&par===0){brace=i;break}}let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
function install(ctx,...names){for(const n of names)vm.runInContext(source(n),ctx)}
new Function(script);

ok(html.includes('id="roguelikeStarterGrid"')&&html.includes('id="roguelikeRunDraftStatus"'),'progress modal exposes a separate roguelike starter picker and draft status');
ok(html.includes('id="roguelikePrepareBtn"')&&html.includes('id="roguelikeClearDraftBtn"'),'run draft can be prepared or cleared without starting normal battle');
ok(script.includes("const ROGUELIKE_STARTER_IDS=Object.freeze(['wanderer','collector','salvager','jester','pure'])"),'four existing characters plus PURE are registered as run starters');
ok(script.includes("const ROGUELIKE_COMMON_START_ZONE='common-start'"),'run draft has an explicit common starting zone');
ok(source('defaultProgress').includes("roguelikeStarter:'wanderer'"),'progress safely defaults the independent run starter');
ok(source('normalizeProgress').includes('roguelikeStarter:normalizeRoguelikeStarterId'),'old saves migrate the run starter independently');
ok(source('renderProgress').includes('renderRoguelikeStarterPicker();renderDeckBuilder()'),'run starter picker renders alongside but before the existing battle deck builder');
ok(source('newGame').includes("makeSide('player',progress.selectedChar,progress.selectedTheme)"),'normal battle still uses its existing character/theme selection path');
ok(!source('createRoguelikeRunDraft').includes('selectedTheme'),'roguelike initialization never inherits the normal-battle selected theme');
ok(source('createRoguelikeRunDraft').includes('themeLocks:[]')&&source('createRoguelikeRunDraft').includes('allowCrossThemeRewards:true'),'run draft encodes no hard theme lock and keeps cross-theme rewards open');
ok(script.includes("const ROGUELIKE_STARTER_REGULAR_SLOTS=Object.freeze(['S3','S4','S5'"),'starter baseline keeps an isolated canonical 29-slot structure');
ok(source('createRoguelikeRunDraft').includes('deckPlan:roguelikeStarterDeckPlan(id)'),'run draft materializes the locked starter deck-plan contract');
ok(source('createRoguelikeRunDraft').includes("passivePlan:{status:'locked-v1',id:'none',directCombat:false}"),'v1 starters explicitly have no direct combat passive');
ok(source('roguelikeRunDraftText').includes('별도 런 덱 실험전 사용 가능'),'UI exposes the prepared run deck as an isolated experiment battle source');

{
  const store=new Map();
  const localStorage={getItem:k=>store.has(k)?store.get(k):null,setItem:(k,v)=>store.set(k,String(v)),removeItem:k=>store.delete(k)};
  const CHARACTERS={wanderer:{name:'유랑자',short:'연계',desc:'x',weights:{combo:1.7}},collector:{name:'수집가',short:'축적',desc:'x',weights:{hold:1.8}},salvager:{name:'회수꾼',short:'순환',desc:'x',weights:{cycle:1.1}},jester:{name:'광대',short:'변칙',desc:'x',weights:{trick:2.2}}};
  const progress={roguelikeStarter:'wanderer'};
  const ctx=vm.createContext({console,Date,Math,Object,Array,String,JSON,Map,localStorage,CHARACTERS,progress,charUnlocked:id=>id!=='jester'});
  vm.runInContext("const ROGUELIKE_RUN_DRAFT_KEY='rummyDuelRoguelikeRunDraftV1'; const ROGUELIKE_COMMON_START_ZONE='common-start'; const ROGUELIKE_STARTER_IDS=Object.freeze(['wanderer','collector','salvager','jester','pure']); const CORE_IDS=['S3','S4','S5','S6','S7','S8','S9','H2','H3','H4','H7','H8','H9','D2','D3','D4','D5','D6','D7','D8','C3','C4','C5','C6','C7','C8','C9','S10','H10','D10','C10']; const ROGUELIKE_STARTER_REGULAR_SLOTS=Object.freeze(CORE_IDS.slice(0,29)); const ROGUELIKE_STARTER_DECK_SIZE=30; const ROGUELIKE_STARTER_NAMED_REGULAR_COUNT=6; const ROGUELIKE_STARTER_LOADOUTS=Object.freeze({wanderer:Object.freeze({regular:Object.freeze({H2:'H2',C5:'C5',S10:'S10',D2:'D2',C6:'C6',H10:'H10'}),joker:'J1'}),collector:Object.freeze({regular:Object.freeze({S9:'S9',H7:'H7',H8:'H8',H9:'H9',D7:'D7B',D8:'D8'}),joker:'J3'}),salvager:Object.freeze({regular:Object.freeze({S3:'S3',S4:'S4',D3:'D3',D7:'D7',C7:'C7',H3:'H3'}),joker:'J4'}),jester:Object.freeze({regular:Object.freeze({C8:'C8',D6:'D6',D5:'D5',D4:'D4',C4:'C4',C3:'C3'}),joker:'J5'}),pure:Object.freeze({regular:Object.freeze({}),joker:null})});",ctx);
  vm.runInContext("const ROGUELIKE_REWARD_ALGORITHM='action-tags-v1'; const ROGUELIKE_REWARD_ROLES=Object.freeze([{id:'reinforce',label:'현재 강화'},{id:'branch',label:'새 방향'},{id:'foundation',label:'기반 보강'}]);",ctx);
  install(ctx,'normalizeRoguelikeStarterId','roguelikeStarterUnlocked','roguelikeStarterProfile','roguelikeStarterLoadout','roguelikeStarterDeckPlan','createRoguelikeRunDeck','normalizeRoguelikeRunDeck','createRoguelikeRewardNodes','normalizeRoguelikeRewardNodes','roguelikeRunDeckSignature','roguelikeRewardNodeId','createRoguelikeRunDraft','normalizeRoguelikeRunDraft','loadRoguelikeRunDraft','saveRoguelikeRunDraft','clearRoguelikeRunDraft','prepareRoguelikeRunDraft');
  const pure=ctx.createRoguelikeRunDraft('pure');
  ok(pure.pureStart===true&&pure.characterId===null&&pure.deckPlan.exactDeckSize===30&&pure.deckPlan.namedCardCount===0,'PURE draft is a 30-card zero-named starter with no fake character id');
  ok(pure.deckPlan.pureRegularCount===29&&pure.deckPlan.pureJokerCount===1&&pure.deckPlan.jokerPolicy==='base-wild-no-effect','PURE uses 29 pure regular slots plus one effectless base wild Joker');
  ok(pure.deckPlan.regularSlots.join(',')==='S3,S4,S5,S6,S7,S8,S9,H2,H3,H4,H7,H8,H9,D2,D3,D4,D5,D6,D7,D8,C3,C4,C5,C6,C7,C8,C9,S10,H10','PURE regular-slot distribution is locked to the canonical 29-slot baseline');
  ok(pure.startZone==='common-start'&&pure.currentZone==='common-start'&&pure.regionPath.length===0&&pure.nodeIndex===0,'new run draft begins at the common zone with an empty route');
  ok(Array.isArray(pure.themeLocks)&&pure.themeLocks.length===0&&pure.allowCrossThemeRewards===true,'PURE remains free to acquire any theme after starting');
  const wanderer=ctx.createRoguelikeRunDraft('wanderer');
  ok(wanderer.deckPlan.exactDeckSize===30&&wanderer.deckPlan.pureCardCount===23&&wanderer.deckPlan.namedRegularCount===6&&wanderer.deckPlan.namedJokerCount===1&&wanderer.deckPlan.namedCardCount===7,'character starter locks 23 pure + 6 named regular + 1 named Joker');
  ok(wanderer.passivePlan.status==='locked-v1'&&wanderer.passivePlan.id==='none'&&wanderer.passivePlan.directCombat===false,'character starter v1 adds no direct combat passive');
  ok(wanderer.rewardPlan.status==='ranking-weights-v1'&&wanderer.rewardPlan.probabilityStatus==='unresolved'&&wanderer.rewardPlan.hardLock===false&&wanderer.rewardPlan.tendencyHints.combo===1.7,'existing character weights are locked as soft candidate-ranking weights while drop probabilities remain unresolved');
  const locked=ctx.createRoguelikeRunDraft('jester');
  ok(locked.starterId==='wanderer','locked character starter safely falls back instead of bypassing progression');
  const saved=ctx.prepareRoguelikeRunDraft('pure');
  ok(store.has('rummyDuelRoguelikeRunDraftV1')&&ctx.loadRoguelikeRunDraft().runId===saved.runId,'prepared run draft persists under an isolated storage key');
  store.set('rummyDuelRoguelikeRunDraftV1',JSON.stringify({...saved,version:5,themeLocks:['v-signal'],regionPath:['NEON//ARC'],nodeIndex:9,currentZone:'NEON//ARC'}));
  const normalized=ctx.loadRoguelikeRunDraft();
  ok(normalized.themeLocks.length===0&&normalized.regionPath.length===0&&normalized.nodeIndex===0&&normalized.currentZone==='common-start','draft normalization strips premature theme locks and route progress');
  ok(ctx.clearRoguelikeRunDraft()===true&&!store.has('rummyDuelRoguelikeRunDraftV1'),'run draft can be cleared without touching normal progress');
}

ok(road.includes('- [x] 캐릭터 선택 UI와 로그라이크 런 초기화 구조 설계'),'ROADMAP marks only the run-init architecture/UI item complete');
ok(!road.includes('PURE만 시작 네임드 0장을 확정값으로 기록')&&!road.includes('시작 덱 총 장수·순수/효과 비율·패시브·정확한 보상 확률은 미확정 상태'),'ROADMAP contains no stale pre-baseline run-init wording');
ok(road.includes('- [x] 캐릭터별 시작 카드 수 / 순수카드 비율 / 보상 가중치 / 패시브 확정'),'quantitative character starter baseline is closed');
ok(road.includes('- [x] PURE 시작 덱의 숫자/무늬 분포 확정'),'PURE distribution baseline is closed');
ok(master.includes('## 15. 스타터 수치 기준 v1 — 30장 / PURE 기준 구조')&&master.includes('character-tendency-score-v1'),'master plan records the locked starter counts and soft reward-ranking weights');
ok(starters.includes('## 3. 일반 캐릭터 스타터 덱 — v1 잠금')&&starters.includes('순수 정규 29 + 기본 와일드 조커 1'),'starter doc records both general and PURE 30-card baselines');
console.log('M11A roguelike run initialization regression passed.');

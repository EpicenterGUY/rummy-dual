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
ok(source('createRoguelikeRunDraft').includes("namedCardCount:id==='pure'?0:null"),'only PURE locks the concrete starting named-card count to zero');
ok(source('createRoguelikeRunDraft').includes('exactDeckSize:null')&&source('createRoguelikeRunDraft').includes("passivePlan:{status:'unresolved'"),'unsettled deck size and passive values remain explicitly unresolved');
ok(source('roguelikeRunDraftText').includes('현재 전투에는 아직 연결하지 않음'),'UI clearly labels the run draft as non-combat prototype state');

{
  const store=new Map();
  const localStorage={getItem:k=>store.has(k)?store.get(k):null,setItem:(k,v)=>store.set(k,String(v)),removeItem:k=>store.delete(k)};
  const CHARACTERS={wanderer:{name:'유랑자',short:'연계',desc:'x',weights:{combo:1.7}},collector:{name:'수집가',short:'축적',desc:'x',weights:{hold:1.8}},salvager:{name:'회수꾼',short:'순환',desc:'x',weights:{cycle:1.1}},jester:{name:'광대',short:'변칙',desc:'x',weights:{trick:2.2}}};
  const progress={roguelikeStarter:'wanderer'};
  const ctx=vm.createContext({console,Date,Math,Object,Array,String,JSON,Map,localStorage,CHARACTERS,progress,charUnlocked:id=>id!=='jester'});
  vm.runInContext("const ROGUELIKE_RUN_DRAFT_KEY='rummyDuelRoguelikeRunDraftV1'; const ROGUELIKE_COMMON_START_ZONE='common-start'; const ROGUELIKE_STARTER_IDS=Object.freeze(['wanderer','collector','salvager','jester','pure']);",ctx);
  install(ctx,'normalizeRoguelikeStarterId','roguelikeStarterUnlocked','roguelikeStarterProfile','createRoguelikeRunDraft','normalizeRoguelikeRunDraft','loadRoguelikeRunDraft','saveRoguelikeRunDraft','clearRoguelikeRunDraft','prepareRoguelikeRunDraft');
  const pure=ctx.createRoguelikeRunDraft('pure');
  ok(pure.pureStart===true&&pure.characterId===null&&pure.deckPlan.namedCardCount===0,'PURE draft starts with zero named cards but no fake character id');
  ok(pure.startZone==='common-start'&&pure.currentZone==='common-start'&&pure.regionPath.length===0&&pure.nodeIndex===0,'new run draft begins at the common zone with an empty route');
  ok(Array.isArray(pure.themeLocks)&&pure.themeLocks.length===0&&pure.allowCrossThemeRewards===true,'PURE remains free to acquire any theme after starting');
  const wanderer=ctx.createRoguelikeRunDraft('wanderer');
  ok(wanderer.deckPlan.exactDeckSize===null&&wanderer.deckPlan.namedCardCount===null&&wanderer.passivePlan.status==='unresolved','character starter does not invent unresolved deck/passive numbers');
  ok(wanderer.rewardPlan.status==='unresolved'&&wanderer.rewardPlan.tendencyHints.combo===1.7,'existing character weights are retained only as prototype tendency hints');
  const locked=ctx.createRoguelikeRunDraft('jester');
  ok(locked.starterId==='wanderer','locked character starter safely falls back instead of bypassing progression');
  const saved=ctx.prepareRoguelikeRunDraft('pure');
  ok(store.has('rummyDuelRoguelikeRunDraftV1')&&ctx.loadRoguelikeRunDraft().runId===saved.runId,'prepared run draft persists under an isolated storage key');
  store.set('rummyDuelRoguelikeRunDraftV1',JSON.stringify({...saved,themeLocks:['v-signal'],regionPath:['NEON//ARC'],nodeIndex:9,currentZone:'NEON//ARC'}));
  const normalized=ctx.loadRoguelikeRunDraft();
  ok(normalized.themeLocks.length===0&&normalized.regionPath.length===0&&normalized.nodeIndex===0&&normalized.currentZone==='common-start','draft normalization strips premature theme locks and route progress');
  ok(ctx.clearRoguelikeRunDraft()===true&&!store.has('rummyDuelRoguelikeRunDraftV1'),'run draft can be cleared without touching normal progress');
}

ok(road.includes('- [x] 캐릭터 선택 UI와 로그라이크 런 초기화 구조 설계'),'ROADMAP marks only the run-init architecture/UI item complete');
ok(road.includes('- [ ] 캐릭터별 시작 카드 수 / 순수카드 비율 / 보상 가중치 / 패시브 확정'),'quantitative character starter balance remains open');
ok(road.includes('- [ ] PURE 시작 덱의 숫자/무늬 분포 확정'),'PURE distribution remains open');
ok(master.includes('## 11. 런 초기화 구조 프로토타입')&&master.includes('기존 일반전 덱 생성 가중치를 로그라이크 확률로 오인해 재사용하지 않는다'),'master plan records the architectural separation and unresolved reward probabilities');
ok(starters.includes('## 9. 캐릭터 선택 UI / 런 초안 초기화')&&starters.includes('즉시 로그라이크 전투를 시작하지 않는다'),'starter doc records that the draft is not yet a combat mode');
console.log('M11A roguelike run initialization regression passed.');

import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const master=fs.readFileSync(new URL('../docs/ROGUELIKE_MASTER_PLAN.md',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let par=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')par++;else if(script[i]===')')par--;else if(script[i]==='{'&&par===0){brace=i;break}}let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
function install(ctx,...names){for(const n of names)vm.runInContext(source(n),ctx)}
new Function(script);

ok(html.includes('id="roguelikeRewardPreview"')&&html.includes('id="roguelikeRewardPreviewBtn"'),'roguelike starter UI exposes manual reward-candidate preview');
ok(script.includes("const ROGUELIKE_REWARD_ALGORITHM='action-tags-v1'"),'reward candidate algorithm has a stable version id');
ok(script.includes("{id:'reinforce',label:'현재 강화'}")&&script.includes("{id:'branch',label:'새 방향'}")&&script.includes("{id:'foundation',label:'기반 보강'}"),'three reward roles are explicit');
for(const n of ['roguelikeEffectActionTags','roguelikeNamedActionTags','roguelikeRewardDeckProfile','roguelikeRewardCandidateScore','roguelikeRewardCandidates'])ok(script.includes(`function ${n}(`),`reward helper exists: ${n}`);
ok(source('createRoguelikeRunDraft').includes("status:'ranking-weights-v1',probabilityStatus:'unresolved',candidateAlgorithm:ROGUELIKE_REWARD_ALGORITHM")&&source('createRoguelikeRunDraft').includes("weightingMode:'character-tendency-score-v1',hardLock:false"),'run draft locks soft ranking weights while exact reward probabilities remain unresolved');
ok(source('roguelikeRewardCandidates').includes("mode:'same-slot-replacement'"),'v1 candidate generation is explicitly same-slot replacement only');
ok(source('roguelikeRewardCandidates').includes("String(id).startsWith('J')")&&source('roguelikeRewardCandidates').includes('profile.slots.includes(slot)')&&source('roguelikeRewardCandidates').includes('profile.variants[slot]!==id'),'candidate pool excludes jokers, out-of-deck slots, and already equipped exact variants');
ok(source('roguelikeRewardPreviewText').includes('roguelikeRunDeckProfile(draft)')&&!source('roguelikeRewardPreviewText').includes('progress.deckBuild'),'developer preview uses persistent run deck rather than normal battle deck');

{
  const NAMED={
    CUR:{slot:'S3',n:'현재 런',t:'run5Bonus',themeId:null},
    REIN:{slot:'H3',n:'런 보강',t:'run4Draw',themeId:null},
    ENTRY:{slot:'D3',n:'관측수',t:'zsObserver',themeId:'zero-sight'},
    PAYOFF:{slot:'C3',n:'ONE SHOT',t:'zsOneShot',themeId:'zero-sight'},
    FOUNDATION:{slot:'S4',n:'재활용',t:'recycler',themeId:null},
    OUTSIDE:{slot:'H9',n:'덱 밖',t:'run4Draw',themeId:null},
    J1:{slot:'J',n:'조커',t:'jokerKing',themeId:null}
  };
  const TENDENCY_BY_TAG={run5Bonus:['extend','pressure'],run4Draw:['extend','cycle'],zsObserver:['control','cycle','combo'],zsOneShot:['pressure','control','status'],recycler:['cycle','discard'],jokerKing:['trick','cycle']};
  const CHARACTERS={wanderer:{name:'유랑자',short:'연계',desc:'x',weights:{combo:1.7,cycle:.9,extend:.6,pressure:.3}},collector:{name:'수집가',short:'축적',desc:'x',weights:{}},salvager:{name:'회수꾼',short:'순환',desc:'x',weights:{}},jester:{name:'광대',short:'변칙',desc:'x',weights:{}}};
  const ctx=vm.createContext({console,Set,Array,Object,String,Number,Math,NAMED,TENDENCY_BY_TAG,CHARACTERS,namedSlot:id=>NAMED[id]?.slot||id,normalizeRoguelikeStarterId:id=>['wanderer','collector','salvager','jester','pure'].includes(id)?id:'wanderer',roguelikeStarterProfile:id=>id==='pure'?{tendencyHints:{}}:{tendencyHints:{...(CHARACTERS[id]||CHARACTERS.wanderer).weights}}});
  vm.runInContext("const ROGUELIKE_REWARD_ROLES=Object.freeze([{id:'reinforce',label:'현재 강화'},{id:'branch',label:'새 방향'},{id:'foundation',label:'기반 보강'}]); const ROGUELIKE_REWARD_ALGORITHM='action-tags-v1'; const ROGUELIKE_THEME_ENTRY_TAGS=Object.freeze({'v-signal':Object.freeze(['vEncore']),'zero-sight':Object.freeze(['zsObserver','zsScopeAdjust'])});",ctx);
  install(ctx,'roguelikeEffectActionTags','roguelikeNamedActionTags','roguelikeRewardDeckProfile','roguelikeRewardStableHash','roguelikeThemeEntryStatus','roguelikeRewardCandidateScore','roguelikeRewardCandidates');
  const input={slots:['S3','H3','D3','C3','S4'],variants:{S3:'CUR'},starterId:'wanderer',poolIds:['CUR','REIN','ENTRY','PAYOFF','FOUNDATION','OUTSIDE','J1'],seed:'fixed-seed'};
  const result=ctx.roguelikeRewardCandidates(input);
  ok(result.picks.length===3&&new Set(result.picks.map(x=>x.id)).size===3,'three reward roles choose distinct cards when the pool allows it');
  const byRole=Object.fromEntries(result.picks.map(x=>[x.role,x]));
  ok(byRole.reinforce.id==='REIN','reinforce role favors existing run/attach behavior overlap');
  ok(byRole.branch.id==='ENTRY','new-direction role favors ZERO-SIGHT entry card over payoff-only ONE SHOT');
  ok(byRole.foundation.id==='FOUNDATION','foundation role favors generic maintenance/discard circulation support');
  ok(!result.picks.some(x=>x.id==='CUR'||x.id==='OUTSIDE'||x.id==='J1'),'equipped variant, out-of-slot candidate, and Joker never enter the replacement reward set');
  ok(result.skipAllowed===true&&result.mode==='same-slot-replacement','skip remains available and addition/removal is not silently mixed into v1');
  const again=ctx.roguelikeRewardCandidates(input);
  ok(JSON.stringify(result.picks)===JSON.stringify(again.picks),'same input and seed produce deterministic candidate ranking');
  const entry=ctx.roguelikeRewardCandidateScore('ENTRY',ctx.roguelikeRewardDeckProfile(input),'branch');
  const payoff=ctx.roguelikeRewardCandidateScore('PAYOFF',ctx.roguelikeRewardDeckProfile(input),'branch');
  ok(entry.entryStatus==='entry'&&payoff.entryStatus==='payoff'&&entry.score>payoff.score,'known new-theme opener metadata suppresses premature finisher offers without hard locking the theme');
  const pure=ctx.roguelikeRewardCandidates({...input,starterId:'pure',variants:{},poolIds:['ENTRY','FOUNDATION','REIN'],seed:'pure'});
  ok(pure.picks.some(x=>x.id==='ENTRY'),'PURE has no class/theme hard lock and may receive a cross-theme entry candidate');
}

ok(road.includes('- [x] 행동 태그 기반 후보 생성 알고리즘 설계'),'ROADMAP closes the action-tag candidate algorithm item');
ok(road.includes('- [ ] 일반전 / 엘리트 / 보스별 카드 보상 등급과 유물 보상 확정'),'reward rarity and encounter-tier economy remain open');
ok(road.includes('- [x] 캐릭터별 시작 카드 수 / 순수카드 비율 / 보상 가중치 / 패시브 확정'),'starter candidate-ranking weights are locked without pretending to lock drop probabilities');
ok(master.includes('## 12. 행동 태그 기반 카드 보상 후보 알고리즘 v1')&&master.includes('실제 보상 확률표가 아니라 **후보 랭킹 계층**')&&master.includes('character-tendency-score-v1'),'master plan distinguishes locked candidate-ranking weights from actual drop probabilities');
ok(master.includes('현재 장착 중인 동일 변형, 조커, 덱에 없는 슬롯은 제외'),'master plan locks same-slot replacement candidate safety');
ok(master.includes('건너뛰기')&&master.includes('하드 잠금은 만들지 않으므로'),'master plan retains skip and cross-theme openness');
console.log('M11A action-tag reward algorithm regression passed.');


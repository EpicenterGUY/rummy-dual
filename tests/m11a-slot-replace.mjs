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

ok(html.includes('id="roguelikeReplacementPreview"')&&html.includes('id="roguelikeReplacementApplyBtn"')&&html.includes('id="roguelikeReplacementCancelBtn"'),'roguelike prototype exposes replacement confirm/cancel surface');
ok(html.includes('roguelikeReplacementApplyBtn" class="pixelBtn primary" type="button" disabled'),'replacement apply is visibly disabled until a real run deck exists');
for(const n of ['normalizeRoguelikeReplacementSource','roguelikeBuildReplacementPlan','roguelikeReplacementPlanText','roguelikeCurrentReplacementPlan','renderRoguelikeReplacementPreview','bindRoguelikeRewardPreviewActions'])ok(script.includes(`function ${n}(`),`slot replacement helper exists: ${n}`);
ok(source('roguelikeBuildReplacementPlan').includes("operation:'replace-slot-variant'"),'replacement plan has a shared operation id');
ok(source('roguelikeBuildReplacementPlan').includes('preservesSlot:true')&&source('roguelikeBuildReplacementPlan').includes('changesDeckSize:false'),'replacement contract explicitly preserves the base slot and deck size');
ok(source('roguelikeBuildReplacementPlan').includes("String(candidateId).startsWith('J')")&&source('roguelikeBuildReplacementPlan').includes('!slots.includes(slot)')&&source('roguelikeBuildReplacementPlan').includes('fromVariant===candidateId'),'invalid Joker, out-of-deck, and no-op replacement plans are rejected');
ok(source('roguelikeRewardPreviewText').includes('data-roguelike-reward-pick'),'reward candidate UI exposes a selectable candidate id');
ok(source('bindRoguelikeRewardPreviewActions').includes("'reward'"),'reward candidate click feeds the common replacement plan as reward source');

{
  const NAMED={N7:{slot:'S7',n:'검은 탄환'},ALT7:{slot:'S7',n:'다른 7♠'},N5:{slot:'H5',n:'회수 카드'},OUT:{slot:'D9',n:'덱 밖'},J1:{slot:'J',n:'조커'}};
  const SUIT_SYMBOL={S:'♠',H:'♥',D:'♦',C:'♣'};
  const ctx=vm.createContext({console,Set,Array,Object,String,NAMED,SUIT_SYMBOL,namedSlot:id=>NAMED[id]?.slot||id});
  install(ctx,'normalizeRoguelikeReplacementSource','roguelikeBuildReplacementPlan','roguelikeReplacementPlanText');
  const slots=['S7','H5'];
  const variants={};
  const pure=ctx.roguelikeBuildReplacementPlan({slots,variants,candidateId:'N7',source:'reward',role:'reinforce'});
  ok(pure&&pure.slot==='S7'&&pure.baseRank==='7'&&pure.suit==='S','pure slot can preview a same-slot named replacement');
  ok(pure.fromVariant===null&&pure.fromKind==='pure'&&pure.toVariant==='N7'&&pure.toKind==='named','replacement plan distinguishes PURE -> NAMED');
  ok(pure.preservesSlot===true&&pure.changesDeckSize===false&&pure.cancelAllowed===true&&pure.applyEnabled===false,'preview contract is non-mutating, cancelable, and not live-applicable');
  const before=JSON.stringify(variants);ctx.roguelikeBuildReplacementPlan({slots,variants,candidateId:'N7',source:'shop'});ok(JSON.stringify(variants)===before,'building a plan never mutates the deck snapshot');
  const named=ctx.roguelikeBuildReplacementPlan({slots,variants:{S7:'ALT7'},candidateId:'N7',source:'event'});
  ok(named.fromVariant==='ALT7'&&named.fromKind==='named'&&named.source==='event','existing named variant can preview a named-to-named same-slot swap');
  ok(ctx.roguelikeBuildReplacementPlan({slots,variants:{S7:'N7'},candidateId:'N7'})===null,'already equipped exact variant is a no-op and rejected');
  ok(ctx.roguelikeBuildReplacementPlan({slots,variants,candidateId:'OUT'})===null,'candidate outside current deck slots is rejected');
  ok(ctx.roguelikeBuildReplacementPlan({slots,variants,candidateId:'J1'})===null,'Joker cannot enter regular same-slot replacement contract');
  ok(ctx.roguelikeBuildReplacementPlan({slots,variants,candidateId:'N5',source:'mystery'}).source==='reward','unknown source safely normalizes to reward');
  const text=ctx.roguelikeReplacementPlanText(named);
  ok(text.includes('이벤트')&&text.includes('다른 7♠ → 검은 탄환')&&text.includes('덱 장수 변화 없음'),'confirmation text exposes source, before/after identity, and size invariance');
}

ok(road.includes('- [x] 카드 보상/상점/이벤트에서 슬롯 교체 UI 설계'),'ROADMAP closes shared same-slot replacement UI design');
ok(road.includes('- [x] 카드 제거와 네임드 교체의 경제적 가치 비교'),'ROADMAP closes the structural removal-versus-replacement economy comparison');
ok(master.includes('## 14. 성장 경제 구조 실험 v1 — 제거 vs 동일 슬롯 교체'),'master plan records the structural economy decision after the replacement contract');
ok(master.includes('## 13. 동일 슬롯 교체 UI 계약 v1')&&master.includes('`reward / shop / event`'),'master plan documents shared reward/shop/event replacement source contract');
ok(master.includes('실제 적용 버튼은 비활성 상태'),'master plan explicitly keeps live deck mutation disabled at this stage');
console.log('M11A same-slot replacement UI regression passed.');

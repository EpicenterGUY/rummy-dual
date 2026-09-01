import fs from 'node:fs';
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
const storage=new Map();let failWrites=false;
const localStorage={getItem:k=>storage.get(k)||null,setItem:(k,v)=>{if(failWrites)throw Error('quota');storage.set(k,v)},removeItem:k=>storage.delete(k)};
const progress={roguelikeStarter:'pure',deckBuild:{slots:['C2'],variants:{C2:'C2'}},totalClears:9};
const before=JSON.stringify(progress);
const ctx=vm.createContext({console,localStorage,progress,charUnlocked:()=>true});
for(const n of ['NAMED','CHARACTERS','TENDENCY_BY_TAG','ROGUELIKE_STARTER_IDS','ROGUELIKE_STARTER_REGULAR_SLOTS','ROGUELIKE_STARTER_LOADOUTS','ROGUELIKE_REWARD_ROLES','ROGUELIKE_THEME_ENTRY_TAGS'])vm.runInContext(declaration(n),ctx);
vm.runInContext("const ROGUELIKE_STARTER_DECK_SIZE=30;const ROGUELIKE_RUN_DRAFT_KEY='rummyDuelRoguelikeRunDraftV1';const ROGUELIKE_COMMON_START_ZONE='common-start';const ROGUELIKE_REWARD_ALGORITHM='action-tags-v1';function unlockedNamed(){return new Set(Object.keys(NAMED))}",ctx);
for(const n of [...script.matchAll(/function (\w+)\(/g)].map(m=>m[1]).filter(n=>/roguelike/i.test(n)).concat('namedSlot'))vm.runInContext(source(n),ctx);
for(const starter of ['wanderer','collector','salvager','jester','pure']){
 const d=ctx.prepareRoguelikeRunDraft(starter);ok(d.version===4&&d.runDeck.cards.length===30,starter+' creates persistent 30-card deck');
 ok(ctx.loadRoguelikeRunDraft().runDeck.cards.filter(c=>c.variantId).length===(starter==='pure'?0:7),starter+' retains correct identities on reload');
}
const draft=ctx.prepareRoguelikeRunDraft('pure');
function candidate(){const d=ctx.loadRoguelikeRunDraft();return ctx.roguelikeRewardCandidates({...ctx.roguelikeRunDeckProfile(d),poolIds:vm.runInContext('Object.keys(NAMED)',ctx),seed:d.runId+':'+d.runDeck.revision}).picks[0]}
let pick=candidate(),plan=ctx.roguelikeCurrentReplacementPlan(pick.id,pick.role);
ok(plan.applyEnabled&&plan.fromVariant===null,'PURE reward uses its own deck, not normal custom deck');
const savedBefore=storage.get('rummyDuelRoguelikeRunDraftV1');
ok(ctx.roguelikeApplyRunReplacement({...plan,runId:'old'})===false,'different run selection rejected');
ok(storage.get('rummyDuelRoguelikeRunDraftV1')===savedBefore,'rejected apply leaves storage unchanged');
failWrites=true;ok(ctx.roguelikeApplyRunReplacement(plan)===false,'storage failure reported');failWrites=false;
ok(storage.get('rummyDuelRoguelikeRunDraftV1')===savedBefore,'failed persistence leaves deck unchanged');
ok(ctx.roguelikeApplyRunReplacement(plan),'valid reward applies');
const changed=ctx.loadRoguelikeRunDraft();
ok(changed.runDeck.cards.length===30&&changed.runDeck.revision===1&&changed.runDeck.cards.find(c=>c.slot===plan.slot).variantId===pick.id,'reload preserves replacement and exact slot count');
ok(changed.deckPlan.namedCardCount===0&&changed.runDeck.cards.filter(c=>c.variantId).length===1,'start blueprint stays PURE while current deck grows');
ok(!ctx.roguelikeApplyRunReplacement(plan),'double click/stale revision rejected');
ok(ctx.roguelikeCurrentReplacementPlan('J1','reinforce')===null,'joker cannot replace a regular slot');
ok(ctx.roguelikeCurrentReplacementPlan(pick.id,pick.role,'shop')===null,'unimplemented shop payment cannot be bypassed');
const invalid=JSON.parse(JSON.stringify(changed));invalid.runDeck.cards[0].slot=invalid.runDeck.cards[1].slot;
ok(ctx.normalizeRoguelikeRunDraft(invalid)===null,'duplicate/corrupt slot rejected rather than silently resetting growth');
const wrong=JSON.parse(JSON.stringify(changed));wrong.runDeck.cards[0].variantId='J1';ok(ctx.normalizeRoguelikeRunDraft(wrong)===null,'joker in regular slot rejected');
const legacy={...draft,version:3};delete legacy.runDeck;ok(ctx.normalizeRoguelikeRunDraft(legacy).runDeck.cards.length===30,'v3 blueprint migrates into real run deck');
ctx.charUnlocked=()=>false;const locked={...changed,starterId:'collector'};ok(ctx.normalizeRoguelikeRunDraft(locked).starterId==='collector','existing run identity survives unlock changes');
ok(JSON.stringify(progress)===before,'normal battle deck and progression remain unchanged');
ctx.clearRoguelikeRunDraft();ok(!ctx.roguelikeApplyRunReplacement(plan),'deleted run rejects old selection');
ctx.charUnlocked=()=>true;ctx.prepareRoguelikeRunDraft('pure');pick=candidate();plan=ctx.roguelikeCurrentReplacementPlan(pick.id,pick.role);
const nodes=Object.fromEntries(['roguelikeReplacementPreview','roguelikeReplacementApplyBtn','roguelikeReplacementCancelBtn'].map(id=>[id,{}]));
ctx.document={getElementById:id=>nodes[id]};ctx.SUIT_SYMBOL={S:'♠',H:'♥',D:'♦',C:'♣'};
let renders=0;ctx.renderRoguelikeStarterPicker=()=>{renders++};
ctx.renderRoguelikeReplacementPreview(plan);ok(!nodes.roguelikeReplacementApplyBtn.disabled,'selected live reward enables apply button');
nodes.roguelikeReplacementCancelBtn.onclick();ok(nodes.roguelikeReplacementApplyBtn.disabled&&ctx.loadRoguelikeRunDraft().runDeck.revision===0,'cancel clears selection without mutation');
ctx.renderRoguelikeReplacementPreview(plan);nodes.roguelikeReplacementApplyBtn.onclick();ok(renders===1&&ctx.loadRoguelikeRunDraft().runDeck.revision===1,'UI apply persists and refreshes run display');
console.log('M11A run deck persistence and replacement passed');

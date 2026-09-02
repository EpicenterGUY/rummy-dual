import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';

const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const master=fs.readFileSync(new URL('../docs/ROGUELIKE_MASTER_PLAN.md',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(value,message){assert.ok(value,message);console.log('PASS: '+message)}
function source(name){
 const marker=`function ${name}(`,start=script.indexOf(marker);assert.ok(start>=0,`missing ${name}`);
 let par=0,brace=-1;
 for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')par++;else if(script[i]===')')par--;else if(script[i]==='{'&&par===0){brace=i;break}}
 let depth=0;
 for(let i=brace;i<script.length;i++){if(script[i]==='{')depth++;else if(script[i]==='}'&&--depth===0)return script.slice(start,i+1)}
 throw new Error('unterminated '+name)
}
function declaration(name){
 const marker=`const ${name}=`,start=script.indexOf(marker);assert.ok(start>=0,`missing ${name}`);
 let quote=null,esc=false,depth=0,started=false;
 for(let i=start+marker.length;i<script.length;i++){
  const ch=script[i];
  if(quote){if(esc)esc=false;else if(ch==='\\')esc=true;else if(ch===quote)quote=null;continue}
  if(ch==="'"||ch==='"'||ch==='`'){quote=ch;continue}
  if(ch==='{'||ch==='['||ch==='('){depth++;started=true}
  else if(ch==='}'||ch===']'||ch===')')depth--;
  else if(ch===';'&&started&&depth===0)return script.slice(start,i+1)
 }
 throw new Error('unterminated declaration '+name)
}
new Function(script);
const KEY='rummyDuelRoguelikeRunDraftV1',storage=new Map([['normal-progress','untouched'],['m12-history','untouched']]);
let failWrites=false,writeCount=0;
const localStorage={getItem:key=>storage.get(key)||null,setItem:(key,value)=>{if(failWrites)throw Error('quota');writeCount++;storage.set(key,String(value))},removeItem:key=>storage.delete(key)};
const progress={roguelikeStarter:'pure',selectedChar:'collector',selectedTheme:'v-signal',totalClears:9,deckBuild:{slots:['C2'],variants:{C2:'C2'}}};
const state={sessionMode:'roguelike',player:{hand:['test-hand'],deck:['test-deck']},rewarded:false};
const progressBefore=JSON.stringify(progress),battleBefore=JSON.stringify(state);
const ctx=vm.createContext({console,localStorage,progress,state,charUnlocked:()=>true,SUIT_SYMBOL:{S:'♠',H:'♥',D:'♦',C:'♣'},THEME_BUILD_PROFILES:{}});
for(const name of ['NAMED','CHARACTERS','TENDENCY_BY_TAG','ROGUELIKE_STARTER_IDS','ROGUELIKE_STARTER_REGULAR_SLOTS','ROGUELIKE_STARTER_LOADOUTS','ROGUELIKE_REWARD_ROLES','ROGUELIKE_THEME_ENTRY_TAGS'])vm.runInContext(declaration(name),ctx);
vm.runInContext("const ROGUELIKE_STARTER_DECK_SIZE=30;const ROGUELIKE_RUN_DRAFT_KEY='rummyDuelRoguelikeRunDraftV1';const ROGUELIKE_COMMON_START_ZONE='common-start';const ROGUELIKE_REWARD_ALGORITHM='action-tags-v1';",ctx);
for(const name of [...script.matchAll(/function (\w+)\(/g)].map(m=>m[1]).filter(name=>/roguelike/i.test(name)).concat('namedSlot'))vm.runInContext(source(name),ctx);
const allIds=vm.runInContext('Object.keys(NAMED)',ctx);let pool=[...allIds];
ctx.unlockedNamed=()=>new Set(pool);
const current=()=>ctx.loadRoguelikeRunDraft(),saved=()=>storage.get(KEY),clone=x=>JSON.parse(JSON.stringify(x));
const nextRequest=()=>ctx.roguelikeNextRewardNodeRequest(current());
const issue=()=>ctx.roguelikeIssueRewardNode(nextRequest());
const token=node=>({runId:current().runId,nodeId:node.id,revision:node.revision,deckSignature:node.deckSignature});
const planFor=(node,index=0)=>{const pick=node.picks[index];return ctx.roguelikeCurrentReplacementPlan(pick.id,pick.role,'reward',node.id)};
const fresh=()=>{pool=[...allIds];return ctx.prepareRoguelikeRunDraft('pure')};

ok(ctx.roguelikeIssueRewardNode(null)===null&&!ctx.roguelikeSkipRewardNode(null)&&!ctx.roguelikeApplyRunReplacement(null),'no run cannot issue, skip, or receive a reward');
for(const starter of ['wanderer','collector','salvager','jester','pure']){
 const draft=ctx.prepareRoguelikeRunDraft(starter);
 ok(draft.version===6&&draft.rewardNodes.version===1&&draft.rewardNodes.baseRevision===0&&draft.rewardNodes.entries.length===0,starter+' starts with a separate empty node ledger');
}

// A v4 player may already have many sandbox replacements: do not reset that deck or invent receipts.
const legacy=fresh();legacy.version=4;delete legacy.rewardNodes;
legacy.runDeck.cards.find(c=>c.slot==='S3').variantId='S3';legacy.runDeck.revision=7;
storage.set(KEY,JSON.stringify(legacy));
const migrated=current();
ok(migrated.version===6&&migrated.runId===legacy.runId&&migrated.createdAt===legacy.createdAt&&migrated.runDeck.revision===7&&migrated.runDeck.cards.find(c=>c.slot==='S3').variantId==='S3','v4 migration preserves run identity, existing variants, and revision');
ok(migrated.rewardNodes.baseRevision===7&&migrated.rewardNodes.entries.length===0,'migration records the old deck revision without fabricating reward nodes');
let node=issue();ok(ctx.roguelikeApplyRunReplacement(planFor(node))&&current().runDeck.revision===8,'migrated decks can receive new node-bound rewards');
for(const version of [1,2,3]){
 const old={...legacy,version};delete old.runDeck;
 const clean=ctx.normalizeRoguelikeRunDraft(old);
 ok(clean.version===6&&clean.runDeck.cards.length===30&&clean.runDeck.revision===0&&clean.rewardNodes.entries.length===0,`v${version} blueprints still migrate to a fresh 30-card run deck`);
}

// Issuance is idempotent; a pending node blocks a second issue.
fresh();
let request=nextRequest(),before=saved(),writes=writeCount;
failWrites=true;ok(ctx.roguelikeIssueRewardNode(request)===null,'issue reports storage failure');failWrites=false;
ok(saved()===before&&writeCount===writes,'failed issue leaves no pending or partially issued node');
node=ctx.roguelikeIssueRewardNode(request);
ok(node.picks.length===3&&new Set(node.picks.map(p=>p.id)).size===3&&node.picks.map(p=>p.role).join(',')==='reinforce,branch,foundation','issue freezes three unique role candidates from the live deck');
ok(node.picks.every(p=>!p.id.startsWith('J')&&p.fromVariant===null),'PURE offer uses regular pure slots, not a Joker or normal custom deck');
before=saved();writes=writeCount;
ok(ctx.roguelikeIssueRewardNode(request).id===node.id&&saved()===before&&writeCount===writes,'repeated issue of the same request returns its original node without a write');
ok(nextRequest()===null&&ctx.roguelikeIssueRewardNode({...request,sequence:2})===null&&saved()===before,'pending reward cannot be rerolled by issuing the next node');

// Once issued, later unlock changes and ranking changes cannot rewrite the offer or revoke its cards.
const ranker=ctx.roguelikeRewardCandidates;
ctx.unlockedNamed=()=>{throw Error('issued reward must not query live unlocks')};
ctx.roguelikeRewardCandidates=()=>{throw Error('issued reward must not rerank')};
ok(JSON.stringify(current().rewardNodes.entries[0].picks)===JSON.stringify(node.picks),'reload restores the issued candidate snapshot');
ok(ctx.roguelikeRewardPreviewText().includes('발급 당시 후보 고정')&&node.picks.every(p=>ctx.roguelikeRewardPreviewText().includes(`data-roguelike-reward-pick="${p.id}"`)),'preview reads frozen candidates without reranking or unlock lookups');
ok(ctx.roguelikeIssueRewardNode(request).id===node.id,'idempotent reissue also ignores the changed live pool');
let plan=planFor(node),otherPlan=planFor(node,1),skipToken=token(node);
ok(plan&&plan.applyEnabled&&plan.nodeId===node.id,'replacement plan is tied to a saved pending node');
ok(ctx.roguelikeCurrentReplacementPlan(node.picks[0].id,node.picks[0].role)===null,'a candidate ID without node identity is not a live reward plan');
for(const changes of [{runId:'other-run'},{nodeId:'other-node'},{revision:1},{deckSignature:'other-deck'},{source:'shop'},{source:'event'},{operation:'add-card'},{applyEnabled:false},{toVariant:'J1'},{fromVariant:'S3'},{slot:'C2'},{role:'invalid'}]){
 ok(ctx.roguelikeApplyRunReplacement({...plan,...changes})===false,'rejects a stale or forged plan: '+Object.keys(changes)[0]);
}
for(const changes of [{runId:'other-run'},{nodeId:'other-node'},{revision:1},{deckSignature:'other-deck'}])ok(!ctx.roguelikeSkipRewardNode({...skipToken,...changes}),'skip verifies '+Object.keys(changes)[0]);
ok(saved()===before&&writeCount===writes,'invalid plans and skip requests leave the entire saved run unchanged');
ok(ctx.roguelikeCurrentReplacementPlan(node.picks[0].id,node.picks[0].role,'shop',node.id)===null&&ctx.roguelikeCurrentReplacementPlan('J1','reinforce','reward',node.id)===null,'pending reward cannot bypass shop payment or insert a Joker');

// One key, one successful write: receipt and replacement cannot partially commit.
failWrites=true;ok(!ctx.roguelikeApplyRunReplacement(plan),'claim reports storage failure');failWrites=false;
ok(saved()===before&&current().rewardNodes.entries[0].status==='pending','failed claim retains the original deck and pending offer');
ok(ctx.roguelikeApplyRunReplacement(plan),'one issued reward is received successfully');
const claimed=current();
ok(writeCount===writes+1&&claimed.rewardNodes.entries[0].status==='claimed'&&claimed.rewardNodes.entries[0].selectedId===plan.toVariant,'receipt and deck change are persisted in exactly one write');
ok(claimed.runDeck.revision===1&&claimed.runDeck.cards.length===30&&claimed.runDeck.cards.find(c=>c.slot===plan.slot).variantId===plan.toVariant&&claimed.deckPlan.namedCardCount===0,'claim changes one run slot while preserving deck size and original PURE blueprint');
before=saved();writes=writeCount;
ok(!ctx.roguelikeApplyRunReplacement(plan)&&!ctx.roguelikeApplyRunReplacement(otherPlan)&&!ctx.roguelikeSkipRewardNode(skipToken),'claim closes all other candidates and skip for the same node');
ok(ctx.roguelikeIssueRewardNode(request).status==='claimed'&&current().rewardNodes.entries.length===1&&saved()===before&&writeCount===writes,'reissuing a completed node never reopens it');
ctx.roguelikeRewardCandidates=ranker;ctx.unlockedNamed=()=>new Set(pool);

// Skipping consumes only this node. The same deck revision still needs a NEW node identity.
node=issue();plan=planFor(node);skipToken=token(node);request={runId:current().runId,sequence:node.sequence,revision:node.revision,deckSignature:node.deckSignature};
const deckBeforeSkip=JSON.stringify(current().runDeck);
before=saved();writes=writeCount;failWrites=true;
ok(!ctx.roguelikeSkipRewardNode(skipToken),'skip reports storage failure');failWrites=false;
ok(saved()===before,'failed skip does not consume the node');
ok(ctx.roguelikeSkipRewardNode(skipToken)&&writeCount===writes+1,'skip saves a one-time outcome');
ok(JSON.stringify(current().runDeck)===deckBeforeSkip&&current().rewardNodes.entries[1].status==='skipped'&&current().rewardNodes.entries[1].selectedId===null,'skip leaves every card and the deck revision unchanged');
ok(!ctx.roguelikeApplyRunReplacement(plan)&&!ctx.roguelikeSkipRewardNode(skipToken),'skipped node rejects an old claim or another skip');
const nextNode=issue();before=saved();
ok(nextNode.sequence===3&&nextNode.revision===node.revision,'next node remains available at the same deck revision after skip');
ok(!ctx.roguelikeApplyRunReplacement(plan)&&!ctx.roguelikeSkipRewardNode(skipToken)&&ctx.roguelikeCurrentReplacementPlan(plan.toVariant,plan.role,'reward',node.id)===null,'old node callbacks cannot act on the next pending node');
ok(ctx.roguelikeIssueRewardNode(request).status==='skipped'&&saved()===before,'old issuance request cannot replace the current pending node');

// Repeated upgrades of one slot can be replay-validated without losing older receipts.
fresh();
for(let i=0;i<9;i++){
 pool=[i%2?'S7B':'S7'];node=issue();
 const p=planFor(node);ok(p.fromVariant===(i?i%2?'S7':'S7B':null)&&ctx.roguelikeApplyRunReplacement(p),`same-slot named swap ${i+1} preserves its before/after history`);
}
ok(current().runDeck.revision===9&&current().rewardNodes.entries.length===9,'all nine receipts survive reload and reverse-snapshot validation');
ok(ctx.roguelikeRewardPreviewText().includes('#9 수령')&&!ctx.roguelikeRewardPreviewText().includes('#1 수령'),'UI keeps full history in storage but displays only the latest five results');

// Tiny and empty pools do not invent duplicate candidates; empty nodes are still skippable.
for(const ids of [[],['S3'],['S3','S4']]){
 fresh();pool=ids;node=issue();
 ok(node.picks.length===ids.length,`pool of ${ids.length} yields only ${ids.length} valid candidates`);
 if(!ids.length)ok(ctx.roguelikeRewardPreviewText().includes('교체 후보가 없습니다')&&nextRequest()===null,'empty offer explains skip and cannot be silently rerolled');
 ok(ctx.roguelikeSkipRewardNode(token(node)),'small-pool node can be skipped normally');
}

// Fail closed on malformed v5 state, rather than quietly clearing a consumed ledger.
fresh();node=issue();ctx.roguelikeApplyRunReplacement(planFor(node));
node=issue();ctx.roguelikeSkipRewardNode(token(node));node=issue();
const valid=current(),validJSON=JSON.stringify(valid);
const corruptions=[
 ['missing ledger',d=>delete d.rewardNodes],
 ['future schema',d=>d.version=7],
 ['future ledger schema',d=>d.rewardNodes.version=2],
 ['negative base revision',d=>d.rewardNodes.baseRevision=-1],
 ['invalid entries',d=>d.rewardNodes.entries={}],
 ['node from another run',d=>d.rewardNodes.entries[0].id='other-run:reward:1'],
 ['out-of-order node',d=>d.rewardNodes.entries[1].sequence=3],
 ['unimplemented source',d=>d.rewardNodes.entries[0].source='event'],
 ['unknown algorithm',d=>d.rewardNodes.entries[0].algorithm='unknown'],
 ['duplicate candidates',d=>d.rewardNodes.entries[2].picks[1].id=d.rewardNodes.entries[2].picks[0].id],
 ['duplicate roles',d=>d.rewardNodes.entries[2].picks[1].role='reinforce'],
 ['unknown card',d=>d.rewardNodes.entries[2].picks[0].id='MISSING'],
 ['Joker candidate',d=>d.rewardNodes.entries[2].picks[0].id='J1'],
 ['wrong slot',d=>d.rewardNodes.entries[2].picks[0].slot='C2'],
 ['Joker before variant',d=>d.rewardNodes.entries[2].picks[0].fromVariant='J1'],
 ['missing selected receipt',d=>d.rewardNodes.entries[0].selectedId=null],
 ['selection on skipped node',d=>d.rewardNodes.entries[1].selectedId=d.rewardNodes.entries[1].picks[0].id],
 ['pending node before history end',d=>{d.rewardNodes.entries[0].status='pending';d.rewardNodes.entries[0].selectedId=null}],
 ['wrong issued revision',d=>d.rewardNodes.entries[2].revision++],
 ['wrong snapshot',d=>d.rewardNodes.entries[2].deckSignature='wrong'],
 ['wrong final revision',d=>d.runDeck.revision++],
 ['unrecorded valid deck mutation',d=>{const c=d.runDeck.cards.find(c=>c.slot==='S7');c.variantId=c.variantId==='S7'?'S7B':'S7'}]
];
for(const [name,mutate] of corruptions){
 const bad=clone(valid);mutate(bad);
 ok(ctx.normalizeRoguelikeRunDraft(bad)===null,'corrupted saved state is rejected: '+name);
}
ok(JSON.stringify(valid)===validJSON&&saved()===validJSON,'validation never mutates the input or resets the saved run');
const extra=clone(valid);extra.rewardNodes.entries[0].debug='ignored';extra.rewardNodes.entries[2].picks[0].score=Infinity;
const clean=ctx.normalizeRoguelikeRunDraft(extra);
ok(clean&&!('debug' in clean.rewardNodes.entries[0])&&!('score' in clean.rewardNodes.entries[2].picks[0]),'only the persisted node schema is retained');

// Old UI objects are also rejected after creating a new run or deleting the saved one.
plan=planFor(node);skipToken=token(node);request={runId:current().runId,sequence:node.sequence,revision:node.revision,deckSignature:node.deckSignature};
fresh();before=saved();
ok(!ctx.roguelikeApplyRunReplacement(plan)&&!ctx.roguelikeSkipRewardNode(skipToken)&&ctx.roguelikeIssueRewardNode(request)===null&&saved()===before,'new run rejects old claim, skip, and issue tokens');
ctx.clearRoguelikeRunDraft();
ok(!ctx.roguelikeApplyRunReplacement(plan)&&!ctx.roguelikeSkipRewardNode(skipToken)&&ctx.roguelikeIssueRewardNode(request)===null,'deleted run cannot be resurrected by stale reward controls');

// Exercise real reward-panel callbacks with a minimal DOM, including reload, cancel, and quota errors.
class Element{
 constructor(){this._html='';this.textContent='';this.disabled=false;this.buttons=[]}
 set innerHTML(value){
  this._html=value;
  this.buttons=[...value.matchAll(/data-roguelike-reward-pick="([^"]+)" data-reward-role="([^"]+)" data-reward-node="([^"]+)"/g)].map(m=>({dataset:{roguelikeRewardPick:m[1],rewardRole:m[2],rewardNode:m[3]}}))
 }
 get innerHTML(){return this._html}
 querySelectorAll(){return this.buttons}
}
const elements=Object.fromEntries(['roguelikeRewardPreview','roguelikeRewardPreviewBtn','roguelikeRewardSkipBtn','roguelikeRewardNodeNotice','roguelikeReplacementPreview','roguelikeReplacementApplyBtn','roguelikeReplacementCancelBtn'].map(id=>[id,new Element()]));
ctx.document={getElementById:id=>elements[id]||null};
ctx.renderRoguelikeStarterPicker=()=>ctx.renderRoguelikeRewardPanel();
const panel=elements.roguelikeRewardPreview,issueButton=elements.roguelikeRewardPreviewBtn,skipButton=elements.roguelikeRewardSkipBtn,applyButton=elements.roguelikeReplacementApplyBtn,notice=elements.roguelikeRewardNodeNotice;
ctx.renderRoguelikeRewardPanel();
ok(issueButton.disabled&&skipButton.disabled&&applyButton.disabled,'reward UI stays disabled without a saved run');
fresh();ctx.renderRoguelikeRewardPanel();
ok(!issueButton.disabled&&skipButton.disabled,'prepared run enables issuance but not premature skip');
before=saved();failWrites=true;issueButton.onclick();failWrites=false;
ok(saved()===before&&notice.textContent.includes('저장하지 못했습니다')&&!issueButton.disabled,'failed UI issuance shows an error and remains retryable');
const oldIssue=issueButton.onclick;issueButton.onclick();
ok(issueButton.disabled&&!skipButton.disabled&&panel.buttons.length===3,'issued offer shows three selectable cards and requires resolving this node first');
const frozenButtons=panel.buttons.map(b=>b.dataset.roguelikeRewardPick).join(',');
ctx.renderRoguelikeRewardPanel();
ok(panel.buttons.map(b=>b.dataset.roguelikeRewardPick).join(',')===frozenButtons,'reopening the panel restores the same saved offer');
before=saved();panel.buttons[0].onclick();
ok(!applyButton.disabled&&saved()===before,'candidate click only prepares a confirmation, not a receipt');
elements.roguelikeReplacementCancelBtn.onclick();
ok(applyButton.disabled&&saved()===before&&current().rewardNodes.entries[0].status==='pending','selection cancel does not consume or reroll the node');
const staleCandidate=panel.buttons[0].onclick,staleSkip=skipButton.onclick;
failWrites=true;skipButton.onclick();failWrites=false;
ok(saved()===before&&notice.textContent.includes('건너뛰기를 저장하지 못했습니다')&&!skipButton.disabled&&panel.buttons.length===3,'failed UI skip keeps candidates available for retry');
skipButton.onclick();
ok(!issueButton.disabled&&skipButton.disabled&&applyButton.disabled&&panel.innerHTML.includes('#1 건너뜀'),'successful skip displays its receipt and enables a new test node');
oldIssue();ok(current().rewardNodes.entries.length===1,'stale issue callback does not issue a fresh reward after skip');
issueButton.onclick();before=saved();
staleCandidate();ok(applyButton.disabled&&saved()===before,'old candidate click cannot target a newly issued node');
staleSkip();ok(saved()===before&&current().rewardNodes.entries[1].status==='pending','old skip callback cannot consume the new node');
panel.buttons[0].onclick();failWrites=true;applyButton.onclick();failWrites=false;
ok(saved()===before&&elements.roguelikeReplacementPreview.textContent.includes('보상을 저장하지 못했습니다')&&panel.buttons.length===3,'failed UI claim preserves the offer and reports its save failure');
panel.buttons[0].onclick();const staleApply=applyButton.onclick;applyButton.onclick();
ok(current().rewardNodes.entries[1].status==='claimed'&&applyButton.disabled&&skipButton.disabled&&!issueButton.disabled&&panel.innerHTML.includes('#2 수령'),'UI claim records its result, clears selection, and enables only the next node');
before=saved();staleApply();ok(saved()===before,'double-fired UI claim cannot receive a second card');
ok(JSON.stringify(progress)===progressBefore&&JSON.stringify(state)===battleBefore&&storage.get('normal-progress')==='untouched'&&storage.get('m12-history')==='untouched','node lifecycle never mutates normal progress, battle cards, or M12 history');
ok([...storage.keys()].every(k=>[KEY,'normal-progress','m12-history'].includes(k)),'reward issuance and receipts use only the existing isolated run storage key');
for(const name of ['startRoguelikeBattle','setupRoguelikeBattle','showResult','showCirculationDraw'])ok(!source(name).includes('roguelikeIssueRewardNode'),'sandbox battle flow does not automatically issue rewards: '+name);
ok(html.includes('id="roguelikeRewardSkipBtn"')&&html.includes('테스트 노드는 수동 발급')&&html.includes('aria-live="polite"'),'UI explicitly labels prototype issuance, skip, and save errors');
ok(road.includes('- [x] 테스트 보상 노드 발급·고정 후보·1회 수령/건너뛰기')&&road.includes('- [ ] 실제 맵/전투 노드와 보상 발급 연결')&&road.includes('- [ ] 상점·이벤트 결제/조건 연결'),'ROADMAP closes node persistence only, leaving real progression and payments open');
ok(master.includes('## 19. 보상 노드 발급과 1회 처리 v1')&&master.includes('v4')&&master.includes('v5'),'master plan records node-state migration and the next integration boundary');
console.log('M11A reward-node lifecycle regression passed.');

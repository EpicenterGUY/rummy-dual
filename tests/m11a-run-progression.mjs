import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';

const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const master=fs.readFileSync(new URL('../docs/ROGUELIKE_MASTER_PLAN.md',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){assert.ok(v,m);console.log('PASS: '+m)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);assert.ok(start>=0,`missing ${name}`);let par=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')par++;else if(script[i]===')')par--;else if(script[i]==='{'&&par===0){brace=i;break}}let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw Error('unterminated '+name)}
new Function(script);

ok(script.includes("const ROGUELIKE_COMMON_START_ROUTE=Object.freeze([")&&script.includes("id:'common-1'")&&script.includes("id:'common-3'"),'common-start progression exposes a locked three-battle route');
ok(source('normalizeRoguelikeRewardNodes').includes("['prototype','battle'].includes(source)")&&source('normalizeRoguelikeRewardNodes').includes('battleNodeId'),'reward ledger accepts and validates battle-issued receipts without changing the v5 draft schema');
ok(source('roguelikeIssueRewardNode').includes("existing.source==='prototype'"),'manual test issuance cannot impersonate an existing battle reward');
ok(source('showResult').includes('roguelikeCompleteBattleNode(state.roguelikeBattleNodeRequest)'),'only the progression result route commits a battle reward after victory');
ok(source('showCirculationDraw').includes("state.roguelikeNodeResult='draw'")&&source('showCirculationDraw').includes('보상도 발급되지 않았습니다'),'progression draw remains retryable and reward-free');
ok(source('setupRoguelikeBattle').includes("log('전투는 런 덱의 독립 복제본")&&source('setupRoguelikeBattle').includes('승리하면 이 전투 자격'),'sandbox isolation and real-node persistence copy remain explicitly separate');
ok(html.includes("state.roguelikeProgressionBattle?'RUN NODE':'RUN TEST'"),'combat HUD visibly distinguishes real run nodes from RUN TEST');
ok(source('renderRoguelikeStarterPicker').includes("nodeBattle.id='roguelikeNodeBattleBtn'")&&source('renderRoguelikeStarterPicker').includes('startRoguelikeNodeBattle()'),'progress UI exposes a separate guarded real-node battle control');

const route=[{id:'common-1',label:'1'},{id:'common-2',label:'2'},{id:'common-3',label:'3'}];
let saved={runId:'run-a',runDeck:{revision:0,cards:[{slot:'S3',variantId:null},{slot:'H2',variantId:null},{slot:'D2',variantId:null}]},rewardNodes:{version:1,baseRevision:0,entries:[]}},writes=0,fail=false;
const clone=x=>JSON.parse(JSON.stringify(x));
const ctx=vm.createContext({console,ROGUELIKE_ROUTE_LIMITS:{regionVisits:2},ROGUELIKE_COMMON_START_ROUTE:route,ROGUELIKE_COMMON_START_ZONE:'common-start',ROGUELIKE_REWARD_ALGORITHM:'action-tags-v1'});
ctx.loadRoguelikeRunDraft=()=>clone(saved);
ctx.saveRoguelikeRunDraft=d=>{if(fail)return false;saved=clone(d);writes++;return true};
ctx.roguelikeRunDeckSignature=deck=>deck.cards.map(c=>`${c.slot}:${c.variantId||'-'}`).join('|');
ctx.roguelikeRewardNodeId=(runId,sequence)=>`${runId}:reward:${sequence}`;
ctx.roguelikeRunDeckProfile=d=>({slots:d.runDeck.cards.map(c=>c.slot),variants:Object.fromEntries(d.runDeck.cards.filter(c=>c.variantId).map(c=>[c.slot,c.variantId]))});
ctx.unlockedNamed=()=>new Set(['A','B','C']);
ctx.roguelikeRewardCandidates=()=>({picks:[{id:'A',role:'reinforce',slot:'S3'},{id:'B',role:'branch',slot:'H2'},{id:'C',role:'foundation',slot:'D2'}]});
for(const name of ['roguelikePendingRewardNode','roguelikeNextRewardNodeRequest','roguelikeBattleProgress','roguelikeCurrentBattleNodeRequest','roguelikeCompleteBattleNode'])vm.runInContext(source(name),ctx);

let req=ctx.roguelikeCurrentBattleNodeRequest(saved);
ok(req.battleIndex===0&&req.battleNodeId==='common-1'&&req.sequence===1,'fresh run receives an identity-bound first common-start combat ticket');
fail=true;ok(ctx.roguelikeCompleteBattleNode(req)===null&&writes===0&&saved.rewardNodes.entries.length===0,'failed atomic save does not consume the battle or create a partial reward');fail=false;
let node=ctx.roguelikeCompleteBattleNode(req);
ok(node?.source==='battle'&&node.battleIndex===0&&node.battleNodeId==='common-1'&&writes===1,'victory commits one battle receipt and frozen reward in one save');
ok(ctx.roguelikeCompleteBattleNode(req)?.id===node.id&&writes===1,'duplicate victory callback is idempotent and cannot issue a second reward');
ok(ctx.roguelikeCurrentBattleNodeRequest(saved)===null,'pending battle reward blocks the next combat node');
saved.rewardNodes.entries.at(-1).status='skipped';
saved.rewardNodes.entries.push({id:'run-a:reward:2',sequence:2,source:'prototype',status:'skipped',revision:0,deckSignature:ctx.roguelikeRunDeckSignature(saved.runDeck),picks:[],selectedId:null});
req=ctx.roguelikeCurrentBattleNodeRequest(saved);
ok(req.battleIndex===1&&req.battleNodeId==='common-2'&&req.sequence===3,'completed test rewards do not advance the real combat route');
ok(ctx.roguelikeCompleteBattleNode({...req,battleNodeId:'common-3'})===null&&saved.rewardNodes.entries.length===2,'forged or stale route identity cannot consume a node');
node=ctx.roguelikeCompleteBattleNode(req);saved.rewardNodes.entries.at(-1).status='skipped';
req=ctx.roguelikeCurrentBattleNodeRequest(saved);node=ctx.roguelikeCompleteBattleNode(req);saved.rewardNodes.entries.at(-1).status='skipped';
const progress=ctx.roguelikeBattleProgress(saved);
ok(progress.completed===3&&progress.finished&&ctx.roguelikeCurrentBattleNodeRequest(saved)===null,'three verified wins finish only the common-start slice and expose no phantom fourth battle');

ok(road.includes('공통 시작 구역 3연전 실전 슬라이스'),'ROADMAP records the completed first real-node slice');
ok(road.includes('- [ ] 실제 맵/전투 노드와 보상 발급 연결'),'full map/reward milestone stays open after the linear common-start slice');
ok(master.includes('## 20. 공통 시작 실전 노드 v1')&&master.includes('battle 출처'),'master plan documents the atomic combat-reward receipt contract');
console.log('M11A common-start progression regression passed.');

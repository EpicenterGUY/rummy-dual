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
for(const name of ['ROGUELIKE_ROUTE_LIMITS','ROGUELIKE_ENDGAME','ROGUELIKE_REGIONS','ROGUELIKE_COMMON_START_ROUTE','NAMED','CHARACTERS','TENDENCY_BY_TAG','ROGUELIKE_STARTER_IDS','ROGUELIKE_STARTER_REGULAR_SLOTS','ROGUELIKE_STARTER_LOADOUTS','ROGUELIKE_REWARD_ROLES','ROGUELIKE_THEME_ENTRY_TAGS'])vm.runInContext(declaration(name),ctx);
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


const regions=vm.runInContext('ROGUELIKE_REGIONS',ctx);
const starters=['pure','wanderer','collector','salvager','jester'];
// Wave 7 classifies Game Broadcast as status rather than cycling; the same
// deterministic starter ranking now favors PBD6 in the wanderer reinforce slot.
const baselinePicks={pure:['PBH7','PBD4','H3'],wanderer:['PBD6','S4','H3'],collector:['ZSH3','PBD4','H3'],salvager:['ZSC5','PBD4','D7B'],jester:['D3','H9','H3']};
const ids=r=>Array.from(r.picks,p=>p.id);
let offers=0,changed=0;
const changedByRegion=Object.fromEntries(regions.map(r=>[r.id,0]));
for(const starterId of starters){
 const draft=ctx.createRoguelikeRunDraft(starterId),input={...ctx.roguelikeRunDeckProfile(draft),poolIds:allIds,seed:'region-baseline'};
 const baseline=ctx.roguelikeRewardCandidates(input);
 assert.deepEqual(ids(baseline),baselinePicks[starterId],starterId+' integrated 60-card common-start ranking stays deterministic');
 assert.equal(JSON.stringify(ctx.roguelikeRewardCandidates({...input,regionId:'not-a-region'})),JSON.stringify(baseline),'unknown region cannot invent a bias');
 for(const region of regions){
  for(let seed=0;seed<64;seed++){
   const args={...input,seed:'region-paired-'+seed},neutral=ctx.roguelikeRewardCandidates(args),result=ctx.roguelikeRewardCandidates({...args,regionId:region.id});
   offers++;
   if(ids(neutral).join(',')!==ids(result).join(',')){changed++;changedByRegion[region.id]++;}
   assert.equal(result.poolSize,neutral.poolSize,'region changes ranking, never eligibility');
   assert.equal(result.algorithm,'action-tags-region-v1');assert.equal(result.regionId,region.id);
   assert.equal(result.skipAllowed,true);assert.equal(result.picks.length,3);
   assert.equal(new Set(ids(result)).size,3,'role candidates stay distinct');
   assert.equal(JSON.stringify(result),JSON.stringify(ctx.roguelikeRewardCandidates({...args,regionId:region.id})),'same regional request is deterministic');
   for(const pick of result.picks){
    assert.ok(input.slots.includes(pick.slot)&&input.variants[pick.slot]!==pick.id&&!pick.id.startsWith('J'));
    assert.ok(pick.regionBonus>=0&&pick.regionBonus<=6,'regional bonus is bounded');
    if(pick.role==='foundation'||pick.entryStatus==='payoff')assert.equal(pick.regionBonus,0,'foundation and unsupported new-theme payoffs stay unboosted');
   }
  }
 }
}
ok(Object.values(changedByRegion).every(n=>n>0),'every region changes some real starter offers');
console.log('REGION_RANKING_COMPARISON '+JSON.stringify({offers,changed,changedByRegion}));

// Ordinary and off-region cards remain eligible even when all local-affinity cards are absent.
const input={...ctx.roguelikeRunDeckProfile(ctx.createRoguelikeRunDraft('pure')),poolIds:allIds,seed:'off-region'};
const profile=ctx.roguelikeRewardDeckProfile(input);
for(const region of regions){
 const outside=allIds.filter(id=>input.slots.includes(ctx.namedSlot(id))&&ctx.roguelikeRegionRewardScore(ctx.roguelikeRewardCandidateScore(id,profile,'reinforce'),region).regionBonus===0);
 assert.ok(outside.length>=3);
 const picks=ctx.roguelikeRewardCandidates({...input,poolIds:outside,regionId:region.id});
 assert.equal(picks.picks.length,3);assert.ok(picks.picks.every(p=>outside.includes(p.id)));
 for(let count=0;count<3;count++)assert.equal(ctx.roguelikeRewardCandidates({...input,poolIds:outside.slice(0,count),regionId:region.id}).picks.length,count);
}
ok(true,'off-region-only and scarce pools remain usable without invented candidates');

// A known payoff receives the preference only after its theme has entered the deck.
const red=regions.find(r=>r.id==='red-zone');
const empty=ctx.roguelikeRewardDeckProfile({slots:['CA','D6'],variants:{},starterId:'pure'});
const entered=ctx.roguelikeRewardDeckProfile({slots:['CA','D6'],variants:{CA:'ZSCA'},starterId:'pure'});
assert.equal(ctx.roguelikeRegionRewardScore(ctx.roguelikeRewardCandidateScore('ZSD6',empty,'reinforce'),red).regionBonus,0);
assert.ok(ctx.roguelikeRegionRewardScore(ctx.roguelikeRewardCandidateScore('ZSD6',entered,'reinforce'),red).regionBonus>0);
ok(true,'new-theme prerequisite preference survives region weighting');

const win=()=>ctx.roguelikeCompleteBattleNode(ctx.roguelikeCurrentBattleNodeRequest());
const skip=n=>ctx.roguelikeSkipRewardNode(token(n));
const prepareRegion=id=>{fresh();for(let i=0;i<3;i++)assert.ok(skip(win()));assert.ok(ctx.roguelikeChooseRegion({...nextRequest(),regionId:id}));};
for(const region of regions){
 prepareRegion(region.id);
 // A caller-supplied region on a manual test request never becomes a regional battle reward.
 let test=ctx.roguelikeIssueRewardNode({...nextRequest(),regionId:region.id});
 assert.equal(test.algorithm,'action-tags-v1');assert.equal(test.regionId,undefined);assert.ok(skip(test));
 const request=ctx.roguelikeCurrentBattleNodeRequest(),before=saved();
 failWrites=true;assert.equal(ctx.roguelikeCompleteBattleNode(request),null);failWrites=false;
 assert.equal(saved(),before,'failed regional issuance keeps the node available');
 const node=ctx.roguelikeCompleteBattleNode(request),issuedJSON=saved();
 assert.equal(node.algorithm,'action-tags-region-v1');assert.equal(node.regionId,region.id);
 assert.ok(ctx.roguelikeRewardPreviewText().includes(region.name+' 성향 반영'));
 const ranker=ctx.roguelikeRewardCandidates,bonus=ctx.roguelikeRegionRewardScore;
 ctx.roguelikeRewardCandidates=()=>{throw Error('issued offer must not rerank')};
 ctx.roguelikeRegionRewardScore=()=>{throw Error('issued offer must not recalculate region bonus')};
 assert.equal(JSON.stringify(current().rewardNodes.entries.at(-1)),JSON.stringify(node));
 assert.ok(ctx.roguelikeRewardPreviewText().includes(region.name+' 성향 반영'));
 assert.equal(ctx.roguelikeCompleteBattleNode(request).id,node.id);assert.equal(saved(),issuedJSON);
 const plan=planFor(node);assert.ok(ctx.roguelikeApplyRunReplacement(plan));assert.ok(!ctx.roguelikeApplyRunReplacement(plan));
 ctx.roguelikeRewardCandidates=ranker;ctx.roguelikeRegionRewardScore=bonus;
 assert.equal(current().rewardNodes.entries.at(-1).regionId,region.id,'claim preserves regional provenance');
 // The previous release may have already frozen an unweighted region offer.
 const legacyNode=win(),legacy=current();legacy.rewardNodes.entries.at(-1).algorithm='action-tags-v1';delete legacy.rewardNodes.entries.at(-1).regionId;
 storage.set(KEY,JSON.stringify(legacy));
 assert.deepEqual(clone(current().rewardNodes.entries.at(-1).picks),clone(legacyNode.picks));
 assert.ok(!ctx.roguelikeRewardPreviewText().includes('성향 반영'),'legacy offer is not relabeled as weighted');
 assert.ok(skip(current().rewardNodes.entries.at(-1)));
 const finalNode=win();assert.equal(finalNode.regionId,region.id);
 const valid=current(),validJSON=saved();
 for(const mutate of [
  d=>d.rewardNodes.entries.at(-1).regionId='unknown',
  d=>d.rewardNodes.entries.at(-1).regionId=regions.find(r=>r.id!==region.id).id,
  d=>delete d.rewardNodes.entries.at(-1).regionId,
  d=>d.rewardNodes.entries.at(-1).algorithm='action-tags-region-v99',
  d=>{d.rewardNodes.entries[0].algorithm='action-tags-region-v1';d.rewardNodes.entries[0].regionId=region.id;},
  d=>{d.rewardNodes.entries[3].algorithm='action-tags-region-v1';d.rewardNodes.entries[3].regionId=region.id;}
 ]){const invalid=clone(valid);mutate(invalid);assert.equal(ctx.normalizeRoguelikeRunDraft(invalid),null,'region provenance must match a real regional battle');}
 assert.equal(saved(),validJSON,'invalid records never rewrite the stored run');
 assert.ok(skip(finalNode));assert.equal(ctx.roguelikeCurrentBattleNodeRequest().battleNodeId,region.id+'-boss');
 const bossReward=win();assert.equal(bossReward.regionId,region.id);assert.ok(skip(bossReward));assert.ok(ctx.roguelikeBattleProgress().finished);
}
ok(true,'all regions preserve issuance, migration, claim, skip, and corruption safeguards');
assert.equal(JSON.stringify(progress),progressBefore);assert.equal(JSON.stringify(state),battleBefore);
ok(storage.get('normal-progress')==='untouched'&&storage.get('m12-history')==='untouched','region rewards remain isolated from normal progress and battle metrics');
console.log('M11A regional reward regression passed.');

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
for(const name of ['ROGUELIKE_ROUTE_LIMITS','FIELDS','ROGUELIKE_ENCOUNTER_PROFILES','ROGUELIKE_REGIONS','ROGUELIKE_COMMON_START_ROUTE','NAMED','CHARACTERS','TENDENCY_BY_TAG','ROGUELIKE_STARTER_IDS','ROGUELIKE_STARTER_REGULAR_SLOTS','ROGUELIKE_STARTER_LOADOUTS','ROGUELIKE_REWARD_ROLES','ROGUELIKE_THEME_ENTRY_TAGS'])vm.runInContext(declaration(name),ctx);
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



vm.runInContext("let uidSeq=1; const RANK_VALUE={A:1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,J:11,Q:12,K:13}; let randomSeed=7; Math.random=()=>{randomSeed=(randomSeed*1664525+1013904223)>>>0;return randomSeed/4294967296};",ctx);
for(const name of ['makeCard','parseRegularId','shuffle','blankStatus','isJoker','isSuitFlexible','setValid','runSequenceOK','runValid','meldType','combinations','bestNewMeld','setupRoguelikeBattle','showResult','showCirculationDraw','renderPracticeCoach'])vm.runInContext(source(name),ctx);
const regions=vm.runInContext('ROGUELIKE_REGIONS',ctx),names=new Set();
const win=()=>ctx.roguelikeCompleteBattleNode(ctx.roguelikeCurrentBattleNodeRequest());
const skip=n=>ctx.roguelikeSkipRewardNode(token(n));
const reachRegion=id=>{fresh();for(let i=0;i<3;i++)assert.ok(skip(win()));assert.ok(ctx.roguelikeChooseRegion({...nextRequest(),regionId:id}));};
const fakeElement=()=>({textContent:'',innerHTML:'',style:{},classList:{add(){},remove(){}}});
const ui=Object.fromEntries(['resultTitle','resultText','resultUnlocks','againBtn','overlay','practiceCoachText'].map(id=>[id,fakeElement()]));
const badge=fakeElement(),meta=fakeElement();ui.practiceCoach={hidden:true,querySelector:q=>q==='.badge'?badge:meta};
ctx.document={getElementById:id=>ui[id]||null};ctx.render=()=>{};ctx.renderProgress=()=>{};ctx.clearEffectChoices=()=>{};
ctx.log=(msg,cls)=>state.logs.push({msg,cls});
ctx.drawMany=(w,n)=>{for(let i=0;i<n;i++)state[w].hand.push(state[w].deck.pop());};
function resetRuntime(){const side=()=>({hp:60,maxHp:60,cores:3,shield:0,status:ctx.blankStatus(),deck:[{id:'old-random-deck'}],hand:[{id:'old-random-hand'}],spent:[],melds:[]});Object.assign(state,{player:side(),enemy:side(),selected:new Set(),selectionOrder:[],boardSelected:new Set(),target:null,logs:[],turnNo:1,turnToken:0,turn:'player',switchTarget:'neutral',switchPower:0,field:null,phase:'mulligan',gameOver:false,rewarded:false});}
resetRuntime();
let planningChecks=0;
for(const region of regions){
 const route=ctx.roguelikeRegionRoute([region.id]);assert.equal(route.length,4);assert.equal(route[3].kind,'boss');
 reachRegion(region.id);
 for(let i=0;i<route.length;i++){
  const node=route[i],encounter=ctx.roguelikeEncounterForNode(node);assert.ok(encounter);
  assert.equal(encounter.namedIds.length,[6,8,10,12][i]);assert.ok(!names.has(encounter.name));names.add(encounter.name);
  const deck=ctx.makeRoguelikeEncounterDeck(encounter);assert.ok(deck);assert.equal(deck.length,30);
  assert.equal(deck.filter(c=>c.named).length,[7,9,11,13][i]);assert.equal(new Set(deck.map(c=>c.slot)).size,30);
  assert.equal(deck.filter(c=>c.suit==='J').length,1);assert.ok(deck.every(c=>c.owner==='enemy'&&c.originOwner==='enemy'));
  assert.ok(deck.filter(c=>c.named&&c.suit!=='J').every(c=>encounter.namedIds.includes(c.id)));
  const copy=ctx.roguelikeEncounterForNode(node);encounter.slots.pop();encounter.field.name='mutated';deck[0].status.cursed=3;
  assert.equal(copy.slots.length,29);assert.notEqual(copy.field.name,'mutated');assert.ok(ctx.makeRoguelikeEncounterDeck(copy).every(c=>c.status.cursed===0));
  for(let seed=0;seed<32;seed++){
   const hand=ctx.makeRoguelikeEncounterDeck(copy).slice(0,8);state.field=copy.field;
   const chosen=ctx.bestNewMeld(hand,'enemy');if(chosen){assert.equal(chosen.cards.length,3);assert.equal(ctx.meldType(chosen.cards),chosen.type);assert.ok(chosen.cards.every(c=>hand.includes(c)));}planningChecks++;
  }
  resetRuntime();const before=saved(),normalBefore=JSON.stringify(progress),request=ctx.roguelikeCurrentBattleNodeRequest();
  assert.equal(request.battleNodeId,node.id);
  assert.equal(ctx.setupRoguelikeBattle(current(),{progression:true,nodeRequest:{...request,battleNodeId:'other-boss'}}),false);
  assert.equal(ctx.setupRoguelikeBattle(current(),{progression:true,nodeRequest:request}),true);
  assert.equal(state.roguelikeEncounter.name,copy.name);assert.equal(state.field.id,copy.field.id);
  assert.equal(state.enemy.hand.length,8);assert.equal(state.enemy.deck.length,22);
  assert.deepEqual(state.enemy.hand.concat(state.enemy.deck).map(c=>c.id).sort(),ctx.makeRoguelikeEncounterDeck(copy).map(c=>c.id).sort());
  assert.equal(state.player.hand.length,8);assert.equal(state.player.deck.length,22);
  assert.equal(new Set([...state.enemy.hand,...state.enemy.deck,...state.player.hand,...state.player.deck].map(c=>c.uid)).size,60);
  assert.equal(state.enemy.cores,3);assert.equal(state.enemy.hp,60);assert.equal(state.enemy.shield,0);
  assert.equal(saved(),before);assert.equal(JSON.stringify(progress),normalBefore);
  assert.ok(ctx.roguelikeRunDraftText().includes(copy.name));assert.ok(ctx.roguelikeRunDraftText().includes(copy.field.desc));
  ctx.renderPracticeCoach();assert.equal(meta.textContent,copy.name);assert.equal(badge.textContent,i===3?'중간 보스':'지역 교전');
  state.gameOver=true;ctx.showResult(false);assert.equal(saved(),before);assert.equal(state.roguelikeNodeResult,'loss');
  ctx.showCirculationDraw();assert.equal(saved(),before);assert.equal(state.roguelikeNodeResult,'draw');
  failWrites=true;ctx.showResult(true);failWrites=false;assert.equal(saved(),before);assert.equal(state.roguelikeNodeResult,'stale');
  ctx.showResult(true);const receipt=current().rewardNodes.entries.at(-1);assert.equal(receipt.battleNodeId,node.id);
  assert.equal(receipt.regionId,region.id);assert.equal(receipt.status,'pending');assert.equal(ctx.roguelikeCurrentBattleNodeRequest(),null);
  if(i===3){assert.equal(ui.resultTitle.textContent,'중간 보스 격파');assert.ok(ui.resultText.textContent.includes('다음 지역을 선택할 수 있습니다'));}
  const issued=saved();ctx.showResult(true);assert.equal(saved(),issued,'replayed result cannot double-grant boss rewards');
  assert.ok(skip(receipt));
 }
 assert.equal(current().nodeIndex,7);assert.equal(ctx.roguelikeCurrentBattleNodeRequest(),null);assert.ok(ctx.roguelikeBattleProgress().finished);
 ok(true,region.name+' roster, live setup, outcome, and boss completion pass');
}
ok(names.size===16&&planningChecks===512,'16 distinct encounters pass 512 real AI meld-planning samples');
const redBoss=ctx.roguelikeEncounterForNode(ctx.roguelikeRegionRoute(['red-zone'])[3]);
assert.ok(['ZSCA','ZSC2','ZSD6','ZSSK','PBDJ'].every(id=>redBoss.namedIds.includes(id)),'red boss carries real target starters with its payoffs');
const valid=ctx.roguelikeEncounterForNode(ctx.roguelikeRegionRoute(['neon-arc'])[0]);
for(const mutate of [e=>e.slots.push('SA'),e=>e.slots[0]=e.slots[1],e=>e.slots[0]='S14',e=>e.namedIds.push('MISSING'),e=>e.namedIds.push(e.namedIds[0]),e=>e.namedIds.push('ZSCA'),e=>e.namedIds.push(null),e=>e.jokerId='H2']){const bad=clone(valid);mutate(bad);assert.equal(ctx.makeRoguelikeEncounterDeck(bad),null);}
assert.equal(ctx.roguelikeEncounterForNode({zone:'red-zone',id:'red-zone-boss',kind:'battle'}),null);
assert.equal(ctx.roguelikeEncounterForNode({zone:'unknown',id:'unknown-boss',kind:'boss'}),null);
ok(true,'invalid encounter composition and forged boss identity fail closed');

// Reloading the previous six-win slice exposes only the new boss; a pending sixth reward still gates it.
reachRegion('red-zone');for(let i=0;i<2;i++)assert.ok(skip(win()));const lastRegular=win();
assert.equal(ctx.roguelikeCurrentBattleNodeRequest(),null);assert.ok(skip(lastRegular));
const oldSix=clone(current()),oldReceipts=JSON.stringify(oldSix.rewardNodes.entries);storage.set(KEY,JSON.stringify(oldSix));
assert.equal(ctx.roguelikeCurrentBattleNodeRequest().battleNodeId,'red-zone-boss');assert.equal(JSON.stringify(current().rewardNodes.entries),oldReceipts);
resetRuntime();const ordinaryEnemy=state.enemy.deck,ordinaryField=state.field;
assert.ok(ctx.setupRoguelikeBattle(current()));assert.equal(state.roguelikeEncounter,null);assert.equal(state.enemy.deck,ordinaryEnemy);assert.equal(state.field,ordinaryField);
ok(true,'old six-win saves retain receipts and RUN TEST keeps ordinary opponent setup');
assert.ok(source('showStartScreen').includes('state.roguelikeEncounter=null')&&source('newGame').includes('state.roguelikeEncounter=null'),'leaving a regional battle clears encounter metadata');
assert.equal(storage.get('normal-progress'),'untouched');assert.equal(storage.get('m12-history'),'untouched');
console.log('M11A regional encounter and boss regression passed.');

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


const regions=vm.runInContext('ROGUELIKE_REGIONS.map(r=>r.id)',ctx);
const choose=id=>ctx.roguelikeChooseRegion({...nextRequest(),regionId:id});
const win=()=>ctx.roguelikeCompleteBattleNode(ctx.roguelikeCurrentBattleNodeRequest());
const skip=n=>ctx.roguelikeSkipRewardNode(token(n));
for(const id of regions){
 fresh();
 ok(!choose(id),'cannot enter '+id+' before common battles');
 for(let i=0;i<3;i++){
  const n=win();assert.ok(n);ok(!choose(id),'pending common reward blocks region choice');assert.ok(skip(n));
 }
 const before=current(),legacy=clone(before);legacy.version=5;
 storage.set(KEY,JSON.stringify(legacy));
 ok(current().version===8&&current().rewardNodes.entries.length===3,'v5 common victories survive migration');
 const oldRequest={...nextRequest(),regionId:id};
 const extra=issue();skip(extra);
 ok(!ctx.roguelikeChooseRegion(oldRequest),'stale region UI cannot bypass changed reward sequence');
 failWrites=true;ok(!choose(id)&&current().regionPath.length===0,'failed save leaves region unselected');failWrites=false;
 ok(choose(id),'select '+id);
 ok(!choose(regions.find(x=>x!==id)),'selected region cannot change');
 ok(current().currentZone===id&&current().nodeIndex===3,'reload retains region and derives position from receipts');
 const n=win();
 ok(n.battleIndex===3&&n.battleNodeId===id+'-1','first region victory has global index and region identity');
 ok(ctx.roguelikeCurrentBattleNodeRequest()===null,'region reward blocks next battle');
 ok(ctx.roguelikeApplyRunReplacement(planFor(n)),'regional replacement commits with receipt');
 for(let i=2;i<=3;i++){
  const req=ctx.roguelikeCurrentBattleNodeRequest();
  ok(req.zone===id&&req.battleNodeId===id+'-'+i,'next regional ticket stays on chosen route');
  ok(ctx.roguelikeCompleteBattleNode({...req,zone:'wrong'})===null,'wrong region callback rejected');
  const n=ctx.roguelikeCompleteBattleNode(req);assert.ok(n);assert.ok(skip(n));
 }
 ok(current().nodeIndex===6&&ctx.roguelikeCurrentBattleNodeRequest().battleNodeId===id+'-boss','existing six-win save continues at its new boss');
 assert.ok(skip(win()));
 ok(current().nodeIndex===7&&ctx.roguelikeBattleProgress().finished&&ctx.roguelikeBattleProgress().awaitingRegion,'first region finishes after the boss reward and opens the next region choice');
 ok(ctx.roguelikeCurrentBattleNodeRequest()===null,'region choice does not invent the next battle before selection');
 const good=saved(),bad=current();bad.regionPath=[regions.find(x=>x!==id)];
 storage.set(KEY,JSON.stringify(bad));ok(current()===null,'receipts from another region are rejected');storage.set(KEY,good);
 const position=current();position.nodeIndex=999;position.currentZone='wrong';storage.set(KEY,JSON.stringify(position));
 ok(current().nodeIndex===7&&current().currentZone===id,'position cannot override validated receipts');
}
fresh();const bad=current();bad.regionPath=['red-zone'];storage.set(KEY,JSON.stringify(bad));
ok(current()===null,'route cannot be injected before common completion');
ok(storage.get('normal-progress')==='untouched'&&storage.get('m12-history')==='untouched','regional progression keeps normal progress and metrics isolated');
console.log('M11A region progression regression passed.');

// Exercise the displayed region buttons and their captured save token.
fresh();for(let i=0;i<3;i++)skip(win());
const buttons=regions.map(id=>({dataset:{runRegion:id}}));
const host={innerHTML:'',textContent:'',querySelectorAll:()=>buttons};
ctx.document={getElementById:id=>id==='roguelikeRegionPicker'?host:null};
ctx.renderRoguelikeStarterPicker=()=>{};
ctx.renderRoguelikeRegionPicker(current());
ok(buttons.every(b=>typeof b.onclick==='function')&&host.innerHTML.includes('네온아크'),'ready route renders all four region actions');
buttons[0].onclick();ok(current().regionPath[0]===regions[0],'visible region action persists its selected route');
ctx.renderRoguelikeRegionPicker(current());ok(host.innerHTML==='','region choices disappear after selection');

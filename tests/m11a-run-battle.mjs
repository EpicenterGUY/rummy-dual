import fs from 'node:fs';
import vm from 'node:vm';

const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const master=fs.readFileSync(new URL('../docs/ROGUELIKE_MASTER_PLAN.md',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let par=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')par++;else if(script[i]===')')par--;else if(script[i]==='{'&&par===0){brace=i;break}}let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
function declaration(name){const marker=`const ${name}=`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let quote=null,esc=false,depth=0,started=false;for(let i=start+marker.length;i<script.length;i++){const ch=script[i];if(quote){if(esc)esc=false;else if(ch==='\\')esc=true;else if(ch===quote)quote=null;continue}if(ch==='\''||ch==='"'||ch==='`'){quote=ch;continue}if(ch==='{'||ch==='['||ch==='('){depth++;started=true}else if(ch==='}'||ch===']'||ch===')')depth--;else if(ch===';'&&started&&depth===0)return script.slice(start,i+1)}throw new Error(`unterminated declaration ${name}`)}
function install(ctx,...names){for(const n of names)vm.runInContext(source(n),ctx)}

new Function(script);
for(const n of ['roguelikeBattleCardFromBlueprint','makeRoguelikeBattleDeck','roguelikeBattleDeckFingerprint','setupRoguelikeBattle','startRoguelikeBattle'])ok(script.includes(`function ${n}(`),`run battle helper exists: ${n}`);
ok(source('isLiveCombatSession').includes("state.sessionMode==='roguelike'"),'roguelike test participates in race-safe combat callbacks');
ok(source('restartCurrentCombat').includes('startRoguelikeBattle()'),'result replay rebuilds from the currently saved run deck');
ok(source('saveBattleMetrics').includes("state.sessionMode==='roguelike'"),'run battle is excluded from M12 history');
ok(source('grantVictoryProgress').includes("state.sessionMode!=='battle'"),'non-standard sessions cannot grant clear, level, or unlock progress');
ok(source('showResult').includes("const practice=state.sessionMode==='practice',roguelike=state.sessionMode==='roguelike'")&&source('showResult').includes('런 덱·클리어·레벨·해금·M12 전투 표본'),'result UI explicitly reports run/progress/metrics isolation');
ok(html.includes('id="roguelikeBattleBtn"')&&source('renderRoguelikeStarterPicker').includes("battle.id='roguelikeBattleBtn'")&&source('renderRoguelikeStarterPicker').includes('battle.disabled=!draft')&&source('renderRoguelikeStarterPicker').includes('startRoguelikeBattle()'),'saved run deck exposes a guarded experiment-battle button with a runtime fallback');

{
 let draft=null,starts=0;const heading={},parent={},elements={};
 const grid={innerHTML:'',closest:()=>({querySelector:()=>heading}),querySelectorAll:()=>[]};
 const clear={parentElement:parent,insertAdjacentElement:(_where,node)=>{elements[node.id]=node}};
 Object.assign(elements,{roguelikeStarterGrid:grid,roguelikeRunDraftStatus:{},roguelikePrepareBtn:{},roguelikeClearDraftBtn:clear,roguelikeRewardPreview:{},roguelikeRewardPreviewBtn:{}});
 const document={getElementById:id=>elements[id]||null,createElement:()=>({})};
 const uiProgress={roguelikeStarter:'pure'};
 const uiCtx=vm.createContext({document,progress:uiProgress,ROGUELIKE_STARTER_IDS:['pure'],normalizeRoguelikeStarterId:id=>id,roguelikeStarterUnlocked:()=>true,roguelikeStarterProfile:()=>({name:'PURE',pure:true,short:'백지형',desc:'순수'}),loadRoguelikeRunDraft:()=>draft,roguelikeRunDraftText:()=>draft?'ready':'empty',prepareRoguelikeRunDraft:()=>null,clearRoguelikeRunDraft:()=>true,saveProgress:()=>true,renderRoguelikeRewardPanel:()=>null,renderRoguelikeReplacementPreview:()=>null,roguelikeRewardPreviewText:()=>'',bindRoguelikeRewardPreviewActions:()=>0,startRoguelikeBattle:()=>{starts++;return true}});
 vm.runInContext(source('renderRoguelikeStarterPicker'),uiCtx);
 uiCtx.renderRoguelikeStarterPicker();
 ok(elements.roguelikeBattleBtn?.disabled===true&&clear.disabled===true,'run battle and clear controls stay disabled without a valid saved deck');
 draft={runId:'run-ui'};uiCtx.renderRoguelikeStarterPicker();elements.roguelikeBattleBtn.onclick();
 ok(elements.roguelikeBattleBtn.disabled===false&&clear.disabled===false&&starts===1&&heading.textContent.includes('전투 프로토타입'),'valid run enables the dynamically mounted battle control and starts the isolated route');
}

const progress={roguelikeStarter:'pure',selectedChar:'collector',selectedTheme:'v-signal',totalClears:3,chars:{wanderer:2,collector:1,salvager:0,jester:0}};
const ctx=vm.createContext({console,Date,Math,Object,Array,String,JSON,Map,Set,progress,charUnlocked:()=>true});
for(const n of ['ROGUELIKE_ROUTE_LIMITS','NAMED','CHARACTERS','ROGUELIKE_STARTER_IDS','ROGUELIKE_STARTER_REGULAR_SLOTS','ROGUELIKE_STARTER_LOADOUTS','ROGUELIKE_REWARD_ROLES'])vm.runInContext(declaration(n),ctx);
vm.runInContext("const ROGUELIKE_STARTER_DECK_SIZE=30;const ROGUELIKE_COMMON_START_ZONE='common-start';const ROGUELIKE_REWARD_ALGORITHM='action-tags-v1';let uidSeq=1;",ctx);
install(ctx,'normalizeRoguelikeStarterId','roguelikeStarterUnlocked','roguelikeStarterProfile','roguelikeStarterLoadout','roguelikeStarterDeckPlan','createRoguelikeRunDeck','normalizeRoguelikeRunDeck','createRoguelikeRewardNodes','normalizeRoguelikeRewardNodes','roguelikeRunDeckSignature','roguelikeRewardNodeId','createRoguelikeRunDraft','normalizeRoguelikeRunDraft','parseRegularId','namedSlot','makeCard','shuffle','roguelikeBattleCardFromBlueprint','makeRoguelikeBattleDeck','roguelikeBattleDeckFingerprint');

const pure=ctx.createRoguelikeRunDraft('pure'),pureBefore=JSON.stringify(pure),pureDeck=ctx.makeRoguelikeBattleDeck(pure);
ok(pureDeck.length===30&&new Set(pureDeck.map(c=>c.runBlueprintSlot||c.slot)).size===30,'PURE materializes exactly one fresh combat card for every run slot');
const pureJoker=pureDeck.find(c=>c.suit==='J');
ok(pureJoker&&!pureJoker.named&&pureJoker.baseWild===true&&pureJoker.tag===null&&pureJoker.name==='기본 와일드 조커','PURE base Joker is a fully wild, effectless, non-named combat card');
pureDeck[0].age=99;pureDeck[0].status.marked=8;pureDeck.splice(1,4);
ok(JSON.stringify(pure)===pureBefore,'combat object mutation cannot flow back into the run draft blueprint');

const collector=ctx.createRoguelikeRunDraft('collector'),collectorDeck=ctx.makeRoguelikeBattleDeck(collector),expected=new Map(collector.runDeck.cards.map(c=>[c.slot,c.variantId]));
ok(collectorDeck.length===30&&collectorDeck.filter(c=>c.named).length===7,'named starter materializes its 6 regular named cards and named Joker');
ok(collectorDeck.every(c=>expected.get(c.runBlueprintSlot||c.slot)===(c.named?c.id:null)),'combat cards preserve every saved slot-to-variant identity');
ok(ctx.roguelikeBattleDeckFingerprint(collector).includes(`${collector.runId}@0:`),'battle source fingerprint binds run id, revision, and slot identities');

vm.runInContext("const state={sessionMode:'menu',player:{deck:[],hand:[],spent:[],melds:[]},enemy:{deck:[],hand:[],spent:[],melds:[]},selected:new Set(),selectionOrder:[],boardSelected:new Set(),target:null,phase:'mulligan',logs:[],developerBattle:false,battleMetrics:{x:1}};function clearEffectChoices(){}function drawMany(w,n){for(let i=0;i<n;i++)state.player.hand.push(state.player.deck.pop())}function log(msg,cls){state.logs.unshift({msg,cls})}function render(){}",ctx);
install(ctx,'setupRoguelikeBattle');
const progressBefore=JSON.stringify(progress),storedBefore=JSON.stringify(collector);
ok(ctx.setupRoguelikeBattle(collector)===true,'valid saved run deck starts the isolated setup');
const setup=vm.runInContext("({mode:state.sessionMode,run:state.roguelikeBattle,runId:state.roguelikeRunId,revision:state.roguelikeRunRevision,starter:state.roguelikeStarterId,fingerprint:state.roguelikeDeckFingerprint,developer:state.developerBattle,metrics:state.battleMetrics,hand:state.player.hand,deck:state.player.deck,logs:state.logs})",ctx);
ok(setup.mode==='roguelike'&&setup.run&&setup.runId===collector.runId&&setup.revision===0&&setup.starter==='collector','battle state snapshots the exact run identity and revision');
ok(setup.hand.length===8&&setup.deck.length===22&&setup.hand.concat(setup.deck).length===30,'run battle deals eight from its 30-card isolated combat deck');
ok(setup.developer===false&&setup.metrics===null,'run battle is distinct from DEV and normal M12 sampling');
setup.hand[0].status.cursed=7;setup.hand.length=0;
ok(JSON.stringify(collector)===storedBefore&&JSON.stringify(progress)===progressBefore,'setup and combat mutation leave run draft and normal progress untouched');
ok(setup.logs.some(x=>x.msg.includes('독립 복제본')),'combat log announces non-persistence at battle start');

{
 const metrics={saved:false},writes=[];
 const metricCtx=vm.createContext({state:{sessionMode:'roguelike',m11bExperimentBattle:false,developerBattle:false},getBattleMetrics:()=>metrics,localStorage:{getItem:()=>null,setItem:(...x)=>writes.push(x)}});
 vm.runInContext(source('saveBattleMetrics'),metricCtx);
 ok(metricCtx.saveBattleMetrics('win')===false&&metrics.saved===true&&writes.length===0,'run result is marked handled without writing normal or experiment metrics');
}
{
 const isolatedProgress={totalClears:9,chars:{wanderer:4}},rewardState={rewarded:false,developerBattle:false,sessionMode:'roguelike'};
 const rewardCtx=vm.createContext({state:rewardState,progress:isolatedProgress});
 vm.runInContext(source('grantVictoryProgress'),rewardCtx);
 ok(rewardCtx.grantVictoryProgress().length===0&&rewardState.rewarded&&isolatedProgress.totalClears===9,'run victory exits before any progression dependency or mutation');
}

ok(road.includes('- [x] 런 덱 기반 별도 실험 전투 시작과 전투 상태 격리'),'ROADMAP closes run-deck experiment battle isolation');
ok(master.includes('## 18. 런 덱 실험 전투 v1')&&master.includes('독립 복제본'),'master plan records the isolated battle contract');
console.log('M11A isolated run-deck battle regression passed.');

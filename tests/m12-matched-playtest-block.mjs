import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let p=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')p++;else if(script[i]===')')p--;else if(script[i]==='{'&&p===0){brace=i;break}}let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
new Function(script);

ok(html.includes("const M12_PLAYTEST_BLOCK_KEY='rummyDuelM12PlaytestBlockV1'"),'M12 matched block has isolated persistent state');
for(const id of ['battleMetricsPlaytestBlock','battleMetricsPlaytestBlockBtn','battleMetricsPlaytestBlockCancelBtn','m12PlaytestBlockResult','m12PlaytestBlockNextBtn'])ok(html.includes(`id="${id}"`),`matched block UI exposes ${id}`);
for(const name of ['m12PlaytestBlockLoad','m12PlaytestBlockSave','m12PlaytestBlockNext','m12PlaytestBlockPlan','startM12PlaytestBlock','cancelM12PlaytestBlock','m12PlaytestBlockSnapshotMeta','recordM12PlaytestBlockSample','m12PlaytestBlockText','applyM12PlaytestBlockNext','renderM12PlaytestBlockResult'])ok(script.includes(`function ${name}(`),`matched block helper exists: ${name}`);

{
 const store=new Map(),localStorage={getItem:k=>store.has(k)?store.get(k):null,setItem:(k,v)=>store.set(k,String(v)),removeItem:k=>store.delete(k)};
 const ctx=vm.createContext({console,Math,Number,Array,Object,JSON,Date,localStorage});
 vm.runInContext("const M12_PLAYTEST_BLOCK_KEY='rummyDuelM12PlaytestBlockV1';const M12_STRUCTURE_IDS=Object.freeze(['set','run','mixed']);",ctx);
 for(const name of ['m12PlaytestBlockLoad','m12PlaytestBlockSave','m12PlaytestBlockNext','m12PlaytestBlockPlan','recordM12PlaytestBlockSample'])vm.runInContext(source(name),ctx);
 const row=(structure,extra={})=>({mode:'battle',playerChar:'wanderer',playerTheme:'v-signal',playerStructure:structure,customDeck:false,circulation:{player:{turns:1}},...extra});
 let plan=ctx.m12PlaytestBlockPlan([row('set'),row('set'),row('run')],'wanderer','v-signal');
 ok(plan.sequence[0]==='mixed','block starts with the least-sampled structure inside the locked context');
 const block={version:1,id:'b1',charId:'wanderer',themeId:'v-signal',sequence:['mixed','set','run'],completed:[],startedAt:1,finishedAt:null};
 ctx.m12PlaytestBlockSave(block);
 ok(ctx.m12PlaytestBlockNext()==='mixed','new block exposes its first scheduled structure');
 ok(!ctx.recordM12PlaytestBlockSample(row('set',{playtestBlockId:'b1'})),'wrong scheduled structure does not advance the block');
 ok(!ctx.recordM12PlaytestBlockSample(row('mixed',{playtestBlockId:'other'})),'wrong block id does not advance the block');
 ok(!ctx.recordM12PlaytestBlockSample(row('mixed',{playtestBlockId:'b1',playerTheme:'mixed'})),'wrong locked context does not advance the block');
 ok(ctx.recordM12PlaytestBlockSample(row('mixed',{playtestBlockId:'b1'}))&&ctx.m12PlaytestBlockNext()==='set','exact first matched result advances to SET');
 ok(ctx.recordM12PlaytestBlockSample(row('set',{playtestBlockId:'b1'}))&&ctx.m12PlaytestBlockNext()==='run','exact second matched result advances to RUN');
 ok(ctx.recordM12PlaytestBlockSample(row('run',{playtestBlockId:'b1'}))&&ctx.m12PlaytestBlockLoad().finishedAt,'third matched result completes the block');
}
const snap=source('battleMetricsSnapshot'),save=source('saveBattleMetrics'),apply=source('applyM12PlaytestBlockNext');
ok(snap.includes('playtestBlockId:block?.playtestBlockId||null')&&snap.includes('playtestBlockStep:block?.playtestBlockStep||null'),'normal M12 rows carry optional block identity without a second metric record');
ok(save.includes('recordM12PlaytestBlockSample(row)'),'saved M12 row is the single source that advances matched block progress');
ok(apply.includes('progress.selectedChar=block.charId')&&apply.includes('progress.selectedTheme=block.themeId')&&apply.includes('progress.selectedStructure=next'),'next-block action restores the locked context and scheduled structure');
ok(apply.includes('progress.deckBuild.enabled=false'),'matched block forces the automatic structure deck instead of custom');
ok(source('showResult').includes('renderM12PlaytestBlockResult()')&&source('showCirculationDraw').includes('renderM12PlaytestBlockResult()'),'win/loss/draw result paths refresh block continuation UI');
ok(script.includes("document.getElementById('m12PlaytestBlockNextBtn').onclick=()=>applyM12PlaytestBlockNext()"),'result next-block button is wired');
ok(road.includes('- [x] M12 matched 3-battle structure block collector'),'ROADMAP records matched 3-battle collector complete');
console.log('M12 matched 3-battle playtest block regression passed.');

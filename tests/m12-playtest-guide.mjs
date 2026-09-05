import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let p=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')p++;else if(script[i]===')')p--;else if(script[i]==='{'&&p===0){brace=i;break}}let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
new Function(script);

for(const id of ['battleMetricsPlaytestGuide','battleMetricsPlaytestApplyBtn','battleMetricsPlaytestRefreshBtn'])ok(html.includes(`id="${id}"`),`M12 playtest collector exposes ${id}`);
for(const name of ['battleMetricsPlaytestRecommendation','battleMetricsPlaytestGuideText','applyBattleMetricsPlaytestRecommendation'])ok(script.includes(`function ${name}(`),`M12 playtest collector helper exists: ${name}`);

{
 const progress={selectedChar:'wanderer',selectedTheme:'mixed'};
 const ctx=vm.createContext({console,Math,Number,Array,Object,progress});
 vm.runInContext("const M12_STRUCTURE_MIN_SAMPLES=10;const M12_STRUCTURE_STABLE_SAMPLES=20;const M12_STRUCTURE_IDS=Object.freeze(['set','run','mixed']);",ctx);
 vm.runInContext(source('battleMetricsPlaytestRecommendation'),ctx);
 const row=(id,extra={})=>({mode:'battle',playerStructure:id,customDeck:false,circulation:{player:{turns:1}},...extra});
 let r=ctx.battleMetricsPlaytestRecommendation([]);
 ok(r.id==='set'&&r.target===10&&r.remaining===10,'empty history starts the first 10-battle gate with SET');
 r=ctx.battleMetricsPlaytestRecommendation([row('set')]);
 ok(r.id==='run','after one SET sample the least-sampled RUN structure is recommended');
 r=ctx.battleMetricsPlaytestRecommendation([row('set'),row('run')]);
 ok(r.id==='mixed','balanced round-robin reaches MIXED after SET and RUN');
 const contextBiased=[
  row('set',{playerChar:'wanderer',playerTheme:'mixed'}),
  row('run',{playerChar:'wanderer',playerTheme:'mixed'}),
  row('mixed',{playerChar:'wanderer',playerTheme:'mixed'}),
  row('set',{playerChar:'collector',playerTheme:'mixed'}),
  row('run',{playerChar:'collector',playerTheme:'mixed'})
 ];
 r=ctx.battleMetricsPlaytestRecommendation(contextBiased);
 ok(r.id==='mixed'&&r.contextCounts.mixed===1,'global least-sampled tie is broken toward the structure least represented in the current character+theme context');
 const nine=id=>Array.from({length:9},()=>row(id));
 r=ctx.battleMetricsPlaytestRecommendation([...nine('set'),...nine('run'),...nine('mixed')]);
 ok(r.target===10&&r.remaining===1,'first comparison phase guides each structure to 10 regular battles');
 const ten=id=>Array.from({length:10},()=>row(id));
 r=ctx.battleMetricsPlaytestRecommendation([...ten('set'),...ten('run'),...ten('mixed')]);
 ok(r.target===20&&r.phase==='stable'&&r.remaining===10,'after 10/10/10 the collector advances to the 20-battle stability tier');
 const twenty=id=>Array.from({length:20},()=>row(id));
 r=ctx.battleMetricsPlaytestRecommendation([...twenty('set'),...twenty('run'),...twenty('mixed')]);
 ok(r.complete&&r.id===null,'20/20/20 marks guided core-structure collection stable');
 const ignored=[...ten('set'),...ten('run'),...nine('mixed'),row('mixed',{mode:'practice'}),row('mixed',{customDeck:true}),{mode:'battle',playerStructure:'mixed'}];
 r=ctx.battleMetricsPlaytestRecommendation(ignored);
 ok(r.id==='mixed'&&r.counts.mixed===9,'practice, custom, and circulation-less rows do not satisfy guided regular-v2 counts');
}

const apply=source('applyBattleMetricsPlaytestRecommendation');
ok(apply.includes('setDeveloperMode(false)'),'guided collector leaves DEV before launching a counted battle');
ok(apply.includes('progress.selectedStructure=r.id'),'guided collector applies the recommended structure');
ok(apply.includes('progress.deckBuild.enabled=false'),'guided collector disables custom deck mode so the core structure cohort is counted');
ok(apply.includes("showBattleSetupStep('deck')"),'guided collector lands on the normal deck setup step for review');
ok(!apply.includes('progress.selectedTheme=')&&!apply.includes('progress.selectedChar='),'guided collector preserves the selected theme and character');
ok(script.includes("document.getElementById('battleMetricsPlaytestApplyBtn').onclick"),'guided collector apply button is wired');
ok(source('renderBattleMetricsHistory').includes('battleMetricsPlaytestGuideText(history)')&&source('renderBattleMetricsHistory').includes('battleMetricsPlaytestRecommendation(history)'),'M12 viewer refreshes guide copy and recommendation from saved results');
ok(road.includes('- [x] Guided M12 structure playtest collector'),'ROADMAP records the guided M12 collector complete');
console.log('M12 guided playtest collector regression passed.');

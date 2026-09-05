import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let p=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')p++;else if(script[i]===')')p--;else if(script[i]==='{'&&p===0){brace=i;break}}let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
new Function(script);
ok(html.includes("const BATTLE_METRICS_HISTORY_LIMIT=240"),'M12 history retains enough samples for 20/20/20 and cross-tabs');
ok(html.includes('id="battleMetricsThemeMatrix"'),'developer metrics panel exposes theme-by-structure matrix');
for(const name of ['battleMetricsThemeIds','battleMetricsThemeLabel','battleMetricsThemeStructureMatrix','battleMetricsThemeStructureText'])ok(script.includes(`function ${name}(`),`theme matrix helper exists: ${name}`);

{
 const ctx=vm.createContext({console,Math,Number,Array,Object});
 vm.runInContext("const M12_STRUCTURE_IDS=Object.freeze(['set','run','mixed']);const M12_THEME_STRUCTURE_MIN_SAMPLES=3;const THEME_BUILD_PROFILES=Object.freeze({mixed:Object.freeze({displayName:'혼합',live:true}),'v-signal':Object.freeze({displayName:'V-SIGNAL',live:true}),future:Object.freeze({displayName:'FUTURE',live:false})});",ctx);
 for(const name of ['battleMetricCirculationAggregate','battleMetricsAggregate','metricAvg','metricPct','battleMetricStructureLabel','battleMetricsStructureRange','battleMetricsThemeIds','battleMetricsThemeLabel','battleMetricsThemeStructureMatrix','battleMetricsThemeStructureText'])vm.runInContext(source(name),ctx);
 const circ=(low2,rummy)=>({player:{turns:10,handTotal:40,handSamples:10,low2,low3:low2,lowSkips:0,rummys:rummy,maintenance:0},enemy:{turns:10,handTotal:40,handSamples:10,low2:0,low3:0,lowSkips:0,rummys:0,maintenance:0},fullRecirculations:0});
 const row=(theme,structure,outcome='win',extra={})=>({mode:'battle',playerTheme:theme,playerStructure:structure,customDeck:false,outcome,turns:12,maxPower:30,bursts:[],chains:[],detonates:[],opponentMeldUses:0,multiAttachMax:1,rummys:[],maintenance:[],intentionalBombAccepts:[],circulation:circ(structure==='run'?5:1,structure==='set'?2:0),...extra});
 const rows=[
  ...Array.from({length:3},()=>row('v-signal','set','win')),
  ...Array.from({length:3},()=>row('v-signal','run','loss')),
  ...Array.from({length:3},(_,i)=>row('v-signal','mixed',i?'win':'loss')),
  row('mixed','set','win'),
  row('v-signal','set','win',{mode:'practice'}),
  row('v-signal','run','win',{customDeck:true}),
  {...row('v-signal','mixed'),circulation:null}
 ];
 const matrix=ctx.battleMetricsThemeStructureMatrix(rows),vs=matrix.find(x=>x.themeId==='v-signal'),mix=matrix.find(x=>x.themeId==='mixed');
 ok(vs.cells.set.samples===3&&vs.cells.run.samples===3&&vs.cells.mixed.samples===3,'matrix separates the three core structures within one theme');
 ok(vs.ready&&vs.spreads.winRate.spread>0&&vs.spreads.low2Rate.spread>0,'three samples per cell unlock within-theme observational spreads');
 ok(mix.cells.set.samples===1&&!mix.ready,'incomplete themes remain visible without claiming within-theme comparison readiness');
 ok(!matrix.some(x=>x.themeId==='future'),'non-live themes are excluded from the live M12 matrix');
 ok(ctx.battleMetricsThemeStructureText(rows).includes('V-SIGNAL')&&ctx.battleMetricsThemeStructureText(rows).includes('테마 내부 구조 관찰 가능'),'matrix text exposes live theme cells and observational readiness');
}
ok(source('saveBattleMetrics').includes('history.slice(-BATTLE_METRICS_HISTORY_LIMIT)'),'save path enforces the expanded shared history limit');
ok(source('renderBattleMetricsHistory').includes('battleMetricsThemeStructureText(history)'),'viewer refreshes the theme matrix with the rest of M12 metrics');
ok(road.includes('- [x] M12 retention fix + theme×structure matrix'),'ROADMAP records retention fix and theme cross-tab complete');
console.log('M12 theme-by-structure matrix regression passed.');

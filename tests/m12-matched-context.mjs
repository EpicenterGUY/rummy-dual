import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let p=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')p++;else if(script[i]===')')p--;else if(script[i]==='{'&&p===0){brace=i;break}}let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
new Function(script);
ok(html.includes('id="battleMetricsMatchedContexts"'),'developer metrics panel exposes character+theme matched correction');
for(const name of ['battleMetricsMatchedContextBalance','battleMetricsMatchedContextText'])ok(script.includes(`function ${name}(`),`matched-context helper exists: ${name}`);

{
 const ctx=vm.createContext({console,Math,Number,Array,Object,Map,Set});
 vm.runInContext("const M12_STRUCTURE_IDS=Object.freeze(['set','run','mixed']);const M12_MATCHED_CONTEXT_MIN_BLOCKS=3;const CHARACTERS=Object.freeze({wanderer:Object.freeze({name:'유랑자'}),collector:Object.freeze({name:'수집가'})});const THEME_BUILD_PROFILES=Object.freeze({mixed:Object.freeze({displayName:'혼합',live:true}),'v-signal':Object.freeze({displayName:'V-SIGNAL',live:true}),future:Object.freeze({displayName:'FUTURE',live:false})});",ctx);
 for(const name of ['battleMetricCirculationAggregate','battleMetricsAggregate','metricAvg','metricPct','battleMetricStructureLabel','battleMetricsStructureRange','battleMetricsThemeIds','battleMetricsThemeLabel','battleMetricsCharacterIds','battleMetricsCharacterLabel','battleMetricsMatchedContextBalance','battleMetricsMatchedContextText'])vm.runInContext(source(name),ctx);
 const circ=(low2,rummy)=>({player:{turns:10,handTotal:40,handSamples:10,low2,low3:low2,lowSkips:0,rummys:rummy,maintenance:0},enemy:{turns:10,handTotal:40,handSamples:10,low2:0,low3:0,lowSkips:0,rummys:0,maintenance:0},fullRecirculations:0});
 let seq=0;
 const row=(char,theme,structure,outcome='win',extra={})=>({savedAt:++seq,mode:'battle',playerChar:char,playerTheme:theme,playerStructure:structure,customDeck:false,outcome,turns:structure==='run'?18:12,maxPower:30,bursts:[],chains:[],detonates:[],opponentMeldUses:0,multiAttachMax:1,rummys:[],maintenance:[],intentionalBombAccepts:[],circulation:circ(structure==='run'?5:1,structure==='set'?2:0),...extra});
 const rows=[
  ...Array.from({length:5},()=>row('wanderer','mixed','set','win')),
  ...Array.from({length:2},()=>row('wanderer','mixed','run','loss')),
  ...Array.from({length:4},(_,i)=>row('wanderer','mixed','mixed',i%2?'win':'loss')),
  row('collector','v-signal','set','loss'),row('collector','v-signal','run','win'),row('collector','v-signal','mixed','win'),
  row('wanderer','future','set','win'),row('wanderer','mixed','run','win',{customDeck:true}),row('wanderer','mixed','mixed','win',{mode:'practice'})
 ];
 const m=ctx.battleMetricsMatchedContextBalance(rows);
 ok(m.completeContexts===2&&m.blocks===3,'matched correction counts two complete char+theme contexts and three balanced blocks');
 ok(m.groups.every(x=>x.stats.samples===3),'each structure contributes the same number of matched samples');
 ok(m.contexts.find(x=>x.charId==='wanderer'&&x.themeId==='mixed').matched===2,'a 5/2/4 context contributes only its minimum cell count');
 ok(m.ready&&m.spreads.winRate.spread>=0,'three matched blocks unlock observational corrected structure spreads');
 ok(!m.contexts.some(x=>x.themeId==='future'),'non-live themes are excluded from matched correction');
 const txt=ctx.battleMetricsMatchedContextText(rows);
 ok(txt.includes('균형 매칭 관찰 가능')&&txt.includes('원시 전체 승률 대비 보정 이동')&&txt.includes('유랑자+혼합 ×2'),'matched text exposes readiness, correction movement, and context contributions');
}
ok(source('renderBattleMetricsHistory').includes('battleMetricsMatchedContextText(history)'),'viewer refreshes matched correction with M12 history');
ok(road.includes('- [x] M12 character+theme matched-context correction'),'ROADMAP records combined character/theme correction complete');
console.log('M12 matched-context correction regression passed.');

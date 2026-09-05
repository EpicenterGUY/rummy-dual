import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let p=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')p++;else if(script[i]===')')p--;else if(script[i]==='{'&&p===0){brace=i;break}}let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
new Function(script);
ok(html.includes('id="battleMetricsCharacterMatrix"'),'developer metrics panel exposes character-by-structure matrix');
for(const name of ['battleMetricsCharacterIds','battleMetricsCharacterLabel','battleMetricsCharacterStructureMatrix','battleMetricsCharacterStructureText'])ok(script.includes(`function ${name}(`),`character matrix helper exists: ${name}`);

{
 const ctx=vm.createContext({console,Math,Number,Array,Object});
 vm.runInContext("const M12_STRUCTURE_IDS=Object.freeze(['set','run','mixed']);const M12_CHARACTER_STRUCTURE_MIN_SAMPLES=3;const CHARACTERS=Object.freeze({wanderer:Object.freeze({name:'유랑자'}),collector:Object.freeze({name:'수집가'}),salvager:Object.freeze({name:'회수꾼'}),jester:Object.freeze({name:'광대'})});",ctx);
 for(const name of ['battleMetricCirculationAggregate','battleMetricsAggregate','metricAvg','metricPct','battleMetricStructureLabel','battleMetricsStructureRange','battleMetricsCharacterIds','battleMetricsCharacterLabel','battleMetricsCharacterStructureMatrix','battleMetricsCharacterStructureText'])vm.runInContext(source(name),ctx);
 const circ=(low2,rummy)=>({player:{turns:10,handTotal:40,handSamples:10,low2,low3:low2,lowSkips:0,rummys:rummy,maintenance:0},enemy:{turns:10,handTotal:40,handSamples:10,low2:0,low3:0,lowSkips:0,rummys:0,maintenance:0},fullRecirculations:0});
 const row=(char,structure,outcome='win',extra={})=>({mode:'battle',playerChar:char,playerTheme:'mixed',playerStructure:structure,customDeck:false,outcome,turns:structure==='run'?20:12,maxPower:30,bursts:[],chains:[],detonates:[],opponentMeldUses:0,multiAttachMax:1,rummys:[],maintenance:[],intentionalBombAccepts:[],circulation:circ(structure==='run'?6:1,structure==='set'?2:0),...extra});
 const rows=[
  ...Array.from({length:3},()=>row('wanderer','set','win')),
  ...Array.from({length:3},()=>row('wanderer','run','loss')),
  ...Array.from({length:3},(_,i)=>row('wanderer','mixed',i?'win':'loss')),
  row('collector','set','win'),
  row('wanderer','set','win',{mode:'practice'}),
  row('wanderer','run','win',{customDeck:true}),
  {...row('wanderer','mixed'),circulation:null},
  row('unknown','set','win')
 ];
 const matrix=ctx.battleMetricsCharacterStructureMatrix(rows),wanderer=matrix.find(x=>x.charId==='wanderer'),collector=matrix.find(x=>x.charId==='collector');
 ok(wanderer.cells.set.samples===3&&wanderer.cells.run.samples===3&&wanderer.cells.mixed.samples===3,'matrix separates core structures within one character');
 ok(wanderer.ready&&wanderer.spreads.winRate.spread>0&&wanderer.spreads.low2Rate.spread>0&&wanderer.spreads.avgTurns.spread>0,'three samples per cell unlock within-character observational spreads');
 ok(collector.cells.set.samples===1&&!collector.ready,'incomplete character cells remain visible without comparison readiness');
 ok(!matrix.some(x=>x.charId==='unknown'),'unknown/deprecated character ids are excluded from the current character matrix');
 const text=ctx.battleMetricsCharacterStructureText(rows);
 ok(text.includes('유랑자')&&text.includes('캐릭터 내부 구조 관찰 가능')&&text.includes('전투 패시브 없이'),'matrix copy explains both readiness and character correction role');
}
ok(source('renderBattleMetricsHistory').includes('battleMetricsCharacterStructureText(history)'),'viewer refreshes character matrix with M12 history');
ok(road.includes('- [x] M12 character×structure correction matrix'),'ROADMAP records character correction matrix complete');
console.log('M12 character-by-structure matrix regression passed.');

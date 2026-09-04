import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let p=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')p++;else if(script[i]===')')p--;else if(script[i]==='{'&&p===0){brace=i;break}}let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
new Function(script);

ok(html.includes('/* M12 · battle metrics review panel */'),'M12 metrics review panel styling exists');
for(const id of ['battleMetricsCount','battleMetricsOverview','battleMetricsCohorts','battleMetricsList','battleMetricsCopyBtn','battleMetricsClearBtn'])ok(html.includes(`id="${id}"`),`developer panel exposes ${id}`);
ok(html.includes('.metricsList{display:flex;flex-direction:column')&&html.includes('max-height:150px;overflow:auto'),'recent sample list is bounded and scrollable');
for(const name of ['battleMetricCirculationAggregate','battleMetricsAggregate','metricAvg','metricPct','battleMetricStructureLabel','battleMetricsStructureCohorts','battleMetricsStructureText','battleMetricsAggregateText','battleMetricRowText','renderBattleMetricsHistory','copyBattleMetricsHistory','clearBattleMetricsHistory'])ok(script.includes(`function ${name}(`),`viewer helper exists: ${name}`);

{
  const ctx=vm.createContext({console,Math,Number,Array,Object});
  for(const name of ['battleMetricCirculationAggregate','battleMetricsAggregate','metricAvg','metricPct','battleMetricStructureLabel','battleMetricsStructureCohorts','battleMetricsStructureText','battleMetricsAggregateText','battleMetricRowText'])vm.runInContext(source(name),ctx);
  const circ=(turns,handTotal,low2,rummys,maintenance)=>({player:{turns,handTotal,handSamples:turns,low2,low3:low2+1,lowSkips:1,rummys,maintenance},enemy:{turns,handTotal,handSamples:turns,low2:0,low3:0,lowSkips:0,rummys:0,maintenance:0},fullRecirculations:0});
  const rows=[
    {mode:'battle',outcome:'win',playerStructure:'set',turns:10,maxPower:50,bursts:[{}],chains:[{},{}],detonates:[{}],opponentMeldUses:2,multiAttachMax:2,rummys:[{}],maintenance:[{}],intentionalBombAccepts:[{}],circulation:circ(5,20,1,1,1)},
    {mode:'battle',outcome:'loss',playerStructure:'run',turns:20,maxPower:80,bursts:[{},{}],chains:[{}],detonates:[{},{}],opponentMeldUses:0,multiAttachMax:3,rummys:[],maintenance:[{},{}],intentionalBombAccepts:[],circulation:circ(10,25,5,0,2)},
    {mode:'practice',outcome:'win',playerStructure:'set',turns:6,maxPower:30,bursts:[],chains:[{}],detonates:[],opponentMeldUses:1,multiAttachMax:1,rummys:[{}],maintenance:[],intentionalBombAccepts:[{},{}],circulation:circ(3,15,0,1,0)}
  ];
  const a=ctx.battleMetricsAggregate(rows);
  ok(a.samples===3&&a.battle===2&&a.practice===1,'aggregate separates regular battle and practice samples');
  ok(a.wins===1&&a.losses===1&&a.winRate===50,'regular-battle win rate ignores practice outcomes');
  ok(Math.abs(a.avgTurns-12)<1e-9&&a.peakPower===80,'aggregate computes average turns and peak power');
  ok(a.multiAttachPeak===3&&a.bombAccepts===3,'aggregate preserves multi-attach peak and intentional bomb-accept count');
  ok(a.circulation.samples===3&&Math.abs(a.circulation.avgPlayerHand-60/18)<1e-9,'aggregate weights player hand average by recorded player turns');
  ok(Math.abs(a.circulation.low2Rate-6/18*100)<1e-9&&Math.abs(a.circulation.rummyPer100-2/18*100)<1e-9,'aggregate derives low-hand and RUMMY rates from raw player-side counts');
  const cohorts=ctx.battleMetricsStructureCohorts(rows),set=cohorts.find(x=>x.id==='set'),run=cohorts.find(x=>x.id==='run');
  ok(set.stats.samples===2&&set.stats.battle===1&&set.stats.winRate===100,'structure cohort groups regular and practice SET samples while keeping battle win rate scoped');
  ok(run.stats.samples===1&&run.stats.winRate===0,'RUN cohort keeps its independent battle result');
  ok(ctx.battleMetricsStructureText(rows).includes('세트형')&&ctx.battleMetricsStructureText(rows).includes('런형'),'cohort text exposes structure comparison rows');
  ok(ctx.battleMetricsAggregateText(rows).includes('승률 50%')&&ctx.battleMetricsAggregateText(rows).includes('최고 80'),'aggregate text exposes balance-facing headline metrics');
  const row=ctx.battleMetricRowText(rows[0]);
  ok(row.includes('일반')&&row.includes('턴 10')&&row.includes('최대 50'),'recent-row formatter exposes concise per-battle details');
}

const snap=source('battleMetricsSnapshot');
ok(snap.includes('savedAt:Date.now()'),'saved samples receive a timestamp');
ok(snap.includes('playerChar:state.player?.charId||null')&&snap.includes('playerTheme:state.player?.themeId||null'),'saved samples retain player character/theme context');
ok(snap.includes('playerStructure:structure')&&snap.includes('customDeck:custom'),'saved samples retain structure/custom-deck cohort context');
ok(snap.includes("circulation:typeof circulationStatsSnapshot==='function'?circulationStatsSnapshot():null"),'saved samples embed per-battle circulation telemetry');
ok(snap.includes('fieldTag:state.field?.tag||null')&&snap.includes('fieldName:state.field?.name||null'),'saved samples retain field context');
ok(source('renderDeveloperPanel').includes("typeof renderBattleMetricsHistory==='function'"),'opening/refreshing developer panel refreshes metrics history');
ok(source('renderBattleMetricsHistory').includes("document.getElementById('battleMetricsCohorts')")&&source('renderBattleMetricsHistory').includes('battleMetricsStructureText(history)'),'viewer renders structure cohort comparison from saved history');
ok(script.includes("document.getElementById('battleMetricsCopyBtn').onclick"),'JSON copy action is wired');
ok(script.includes("document.getElementById('battleMetricsClearBtn').onclick"),'history clear action is wired');
ok(source('copyBattleMetricsHistory').includes('JSON.stringify(history,null,2)'),'copy action exports structured readable JSON');
ok(source('clearBattleMetricsHistory').includes('localStorage.removeItem(BATTLE_METRICS_KEY)'),'clear action removes only the battle-metrics history key');
ok(road.includes('- [x] Review/export local playtest metrics'),'ROADMAP records M12 local metrics review/export completion');
ok(road.includes('- [x] Structure / circulation cohort telemetry'),'ROADMAP records M12 structure/circulation cohort readiness');
ok(road.includes('- [ ] Balance from playtest data before large content expansion'),'actual balance verdict remains open until real samples exist');
console.log('M12 metrics viewer regression passed.');

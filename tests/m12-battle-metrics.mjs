import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const circulationExperiment=fs.readFileSync(new URL('../experiments/m12-hand-circulation.mjs',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function functionSource(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);const body=script.indexOf('){',start);let depth=0,end=-1;for(let i=body+1;i<script.length;i++){if(script[i]==='{')depth++;else if(script[i]==='}'){depth--;if(depth===0){end=i+1;break}}}if(end<0)throw new Error(`unterminated ${name}`);return script.slice(start,end)}
new Function(script);

ok(html.includes("const BATTLE_METRICS_KEY='rummyDuelBattleMetricsV1'"),'M12 uses a versioned local battle-metrics history key');
for(const name of ['blankCirculationSide','blankCirculationStats','getCirculationStats','circulationSideStats','recordCirculationCounter','recordCirculationTurn','circulationStatsSnapshot','getBattleMetrics','battleMetricTurn','recordBattleTurn','recordMeldActionMetric','recordDetonateMetric','recordRummyMetric','recordMaintenanceMetric','recordIntentionalBombAcceptance','battleMetricsSummaryText','battleMetricsSnapshot','battleMetricsHistory','saveBattleMetrics'])ok(script.includes(`function ${name}(`),`M12 helper exists: ${name}`);

{
  const state={switchPower:12,turnToken:7,sessionMode:'battle',player:{charId:'wanderer',themeId:'mixed',hand:[{},{},{}]},enemy:{charId:'wanderer',themeId:'mixed',hand:[{},{}]}};
  const progress={selectedStructure:'run',deckBuild:{enabled:false}};
  const ctx=vm.createContext({console,Math,JSON,Array,Object,Number,state,progress,other:w=>w==='player'?'enemy':'player',sideObj:w=>state[w]});
  for(const name of ['blankCirculationSide','blankCirculationStats','getCirculationStats','circulationSideStats','recordCirculationCounter','recordCirculationTurn','circulationStatsSnapshot','getBattleMetrics','battleMetricTurn','recordBattleTurn','recordMeldActionMetric','recordDetonateMetric','recordRummyMetric','recordMaintenanceMetric','recordIntentionalBombAcceptance','battleMetricTurns','battleMetricsSummaryText','battleMetricsSnapshot'])vm.runInContext(functionSource(name),ctx);
  ctx.recordCirculationTurn('player');ctx.recordCirculationTurn('enemy');ctx.recordCirculationCounter('player','lowSkips');ctx.recordCirculationCounter('player','rummys');ctx.recordCirculationCounter('enemy','maintenance');
  ok(ctx.getCirculationStats().turns===2&&ctx.circulationSideStats('player').turns===1,'circulation telemetry keeps total and per-side turn samples');
  ok(ctx.circulationSideStats('player').lowSkips===1&&ctx.circulationSideStats('player').rummys===1&&ctx.circulationSideStats('enemy').maintenance===1,'circulation counters retain actor identity');
  let st=ctx.getBattleMetrics();
  ok(st.maxPower===12&&st.turns===0,'metric state starts from the live switch power and zero completed turns');
  ctx.recordMeldActionMetric('player','RUN',3,'enemy',{extraAttach:false});
  ok(st.chains.length===1&&st.chains[0].turn===1,'CHAIN action records the current side-turn timing');
  ok(st.opponentMeldUses===1&&st.opponentMeldCards===3,'opponent public-meld use records action and card volume');
  ok(st.multiAttachActions===1&&st.multiAttachMax===3,'multi-attach tracks action count and maximum size');
  ctx.recordMeldActionMetric('enemy','SET',1,'enemy');
  ok(st.bursts.length===1&&st.bursts[0].turn===1,'BURST timing is recorded independently');
  ctx.recordDetonateMetric('enemy',42,38);
  ok(st.detonates.length===1&&st.detonates[0].power===42&&st.detonates[0].dealt===38,'DETONATE records incoming power and actual core damage');
  ctx.recordRummyMetric('player');ctx.recordMaintenanceMetric('enemy',2);
  ok(st.rummys.length===1&&st.maintenance[0].cards===2,'RUMMY and maintenance events are tracked');
  const a=ctx.recordIntentionalBombAcceptance('enemy',14,10),b=ctx.recordIntentionalBombAcceptance('enemy',14,10);
  ok(!!a&&b===null&&st.intentionalBombAccepts.length===1,'intentional small-bomb acceptance is deduplicated per turn token');
  ctx.recordBattleTurn('player');state.turnToken=8;ctx.recordIntentionalBombAcceptance('enemy',16,8);
  ok(st.turns===1&&st.intentionalBombAccepts[1].turn===2,'completed turn count advances later event timing');
  const snap=ctx.battleMetricsSnapshot('win');
  ok(snap.outcome==='win'&&snap.mode==='battle'&&snap.chains.length===1&&snap.maxPower===12,'snapshot is structured and tagged with mode/outcome');
  ok(snap.version===2&&snap.playerStructure==='run'&&snap.customDeck===false,'snapshot v2 retains the selected deck-structure cohort');
  ok(snap.circulation?.player?.turns===1&&snap.circulation.player.lowSkips===1&&snap.circulation.enemy.maintenance===1,'snapshot persists per-side circulation counters');
  ok(ctx.battleMetricsSummaryText().includes('버스트 1회@1')&&ctx.battleMetricsSummaryText().includes('체인 1회@1')&&ctx.battleMetricsSummaryText().includes('폭발 1회@1'),'result summary exposes action timing compactly');
}

ok(html.includes("state.switchPower+=amount;if(typeof getBattleMetrics==='function'){const bm=getBattleMetrics();bm.maxPower=Math.max(bm.maxPower,state.switchPower)}"),'max accumulated SWITCH power is sampled at the central power mutation');
ok(html.includes("recordMeldActionMetric(w,type,cards.length,targetSide,{extraAttach:access.extra})"),'successful attach path records BURST/CHAIN, opponent-meld use, multi-attach size and named extra-attach metadata');
ok(html.includes("recordDetonateMetric(w,total,dealt)"),'DETONATE path records timing and damage');
ok(html.includes("recordRummyMetric(w)"),'RUMMY path records event timing');
ok(html.includes("recordMaintenanceMetric(w,valid.length)"),'maintenance path records exchanged-card count');
ok(html.includes("if(acceptSmall&&typeof recordIntentionalBombAcceptance==='function')recordIntentionalBombAcceptance('enemy',state.switchPower,ex?.score||0)"),'AI strategic small-bomb acceptance is recorded from the live decision point');
ok(html.includes("if(typeof recordBattleTurn==='function')recordBattleTurn(w)"),'turn-end path records completed side turns');
ok(html.includes("showResult(win){if(typeof renderCirculationSummary==='function')renderCirculationSummary();if(typeof saveBattleMetrics==='function')saveBattleMetrics(win?'win':'loss');"),'normal battle results persist the sample');
ok(html.includes("showCirculationDraw(){if(typeof renderCirculationSummary==='function')renderCirculationSummary();if(typeof saveBattleMetrics==='function')saveBattleMetrics('draw');"),'circulation draws persist the sample');
const saveSource=functionSource('saveBattleMetrics');
ok(saveSource.includes("state.sessionMode==='tutorial'")&&saveSource.includes('if(state.developerBattle)return false'),'tutorial and ordinary DEV sessions remain excluded from normal balance history');
ok(saveSource.includes('if(state.m11bExperimentBattle)')&&saveSource.includes('saveM11BExperimentMetrics(outcome)')&&saveSource.indexOf('if(state.m11bExperimentBattle)')<saveSource.indexOf('if(state.developerBattle)return false'),'M11B DEV sandbox may route to its isolated history before generic DEV suppression');
ok(functionSource('newGame').includes('state.battleMetrics=null'),'each new combat resets the per-battle M12 metrics object');
ok(html.includes("const BATTLE_METRICS_HISTORY_LIMIT=240"),'M12 history limit is large enough for the 60-battle 20/20/20 structure stability gate and theme cross-tabs');
ok(saveSource.includes('history.slice(-BATTLE_METRICS_HISTORY_LIMIT)'),'local metric history uses the shared expanded retention limit');
ok(circulationExperiment.includes("'twelve-bloom'")&&circulationExperiment.includes("export const COHORTS="),'M12 circulation matrix includes newly live TWELVE-BLOOM');
ok(road.includes('- [x] Track turn count, BURST/CHAIN/DETONATE timing'),'ROADMAP marks M12 tracking complete');
ok(road.includes('- [x] Structure / circulation cohort telemetry'),'ROADMAP marks structure-aware M12 sampling ready');
ok(road.includes('M12: collect real playtest samples from the new per-battle metrics history'),'Current next work now points to real metric-driven balance instead of completed UX/L10N work');
console.log('M12 battle metrics regression passed.');

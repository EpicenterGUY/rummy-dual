import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync('index.html','utf8');
const road=fs.readFileSync('ROADMAP.md','utf8');
const doc=fs.readFileSync('docs/ASYMMETRIC_RANK_PROTOTYPE.md','utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let par=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')par++;else if(script[i]===')')par--;else if(script[i]==='{'&&par===0){brace=i;break}}let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
function install(ctx,...names){for(const n of names)vm.runInContext(source(n),ctx)}
new Function(script);

ok(html.includes('id="m11bExperimentReadiness"')&&html.includes('id="m11bExperimentCompare"'),'developer experiment panel exposes readiness and comparison surfaces');
ok(html.includes('/* M11B · experiment sample readiness / cohort comparison */'),'readiness panel has a dedicated responsive visual layer');
ok(script.includes('const M11B_EXPERIMENT_MIN_SAMPLES=10')&&script.includes('const M11B_EXPERIMENT_STABLE_SAMPLES=20'),'sample readiness thresholds are explicit 10 / 20 games');
for(const n of ['m11bExperimentReadiness','m11bExperimentReadinessText','m11bExperimentComparison','m11bSigned','m11bExperimentComparisonText'])ok(script.includes(`function ${n}(`),`readiness helper exists: ${n}`);
ok(source('renderM11BExperimentHistory').includes("readiness.dataset.state=gate.allStable?'stable':gate.allReady?'ready':'collecting'"),'renderer exposes collecting / ready / stable state without changing balance rules');
ok(source('renderM11BExperimentHistory').includes('m11bExperimentComparisonText(history)'),'developer renderer refreshes 0-card-relative comparison text');

const cohorts={zero:{id:'zero',label:'기준 0장'},few:{id:'few',label:'소수 4장'},many:{id:'many',label:'스트레스 10장'}};
function row(cohort,outcome,turns,maintenance=0,rummys=0,opponentMeldUses=0,multiAttachMax=1){return{cohort,outcome,turns,maintenance:Array.from({length:maintenance},()=>({actor:'player'})),rummys:Array.from({length:rummys},()=>({actor:'player'})),opponentMeldUses,multiAttachMax}}
const history=[];
for(let i=0;i<10;i++)history.push(row('zero',i<5?'win':'loss',10,1,0,1,2));
for(let i=0;i<10;i++)history.push(row('few',i<7?'win':'loss',9,0,1,2,3));
for(let i=0;i<20;i++)history.push(row('many',i<8?'win':'loss',8,0,1,3,4));
{
  const ctx=vm.createContext({console,Object,Array,Math,Number,M11B_EXPERIMENT_MIN_SAMPLES:10,M11B_EXPERIMENT_STABLE_SAMPLES:20,M11B_EXPERIMENT_COHORTS:cohorts,m11bExperimentCohort:id=>cohorts[id],m11bExperimentHistory:()=>history});
  install(ctx,'m11bExperimentAggregate','m11bExperimentReadiness','m11bExperimentReadinessText','m11bExperimentComparison','m11bSigned','m11bExperimentComparisonText');
  const gate=ctx.m11bExperimentReadiness(history);
  ok(gate.allReady===true&&gate.allStable===false,'10/10/20 samples unlock first comparison but not full stable state');
  ok(gate.cohorts.zero.status==='ready'&&gate.cohorts.few.status==='ready'&&gate.cohorts.many.status==='stable','per-cohort readiness distinguishes ready versus stable');
  const cmp=ctx.m11bExperimentComparison(history);
  ok(cmp.few.winRate===20&&cmp.many.winRate===-10,'comparison reports percentage-point win-rate differences from zero-card control');
  ok(cmp.few.avgTurns===-1&&cmp.many.avgTurns===-2,'comparison reports average turn deltas from control');
  ok(cmp.few.avgMaintenance===-1&&cmp.few.avgRummys===1&&cmp.few.avgOpponentMeldUses===1,'comparison reports maintenance, RUMMY and opponent-meld deltas');
  ok(cmp.few.multiAttachPeak===1&&cmp.many.multiAttachPeak===2,'comparison reports multi-attach peak deltas');
  ok(ctx.m11bExperimentReadinessText(history).includes('1차 비교 가능'),'readiness copy distinguishes first-comparison readiness');
  ok(ctx.m11bExperimentComparisonText(history).includes('1차 비교 표본 충족'),'comparison copy only announces the sample gate, not balance success');
  const short=history.filter((_,i)=>i<9);
  ok(ctx.m11bExperimentReadiness(short).allReady===false&&ctx.m11bExperimentReadiness(short).cohorts.zero.remaining===1,'under-sampled cohort reports exact remaining games');
}

ok(road.includes('- [x] M11B 실험 표본 준비도 / 0장 대비 코호트 차이 패널'),'ROADMAP locks the sample-readiness comparison panel');
ok(road.includes('- [ ] 비대칭 카드 0장 / 소수 / 다수 덱의 세트·런 성공률, 패말림, 정비, 러미 빈도 비교'),'final M11B battle-flow balance comparison remains open');
ok(road.includes('- [ ] Balance from playtest data before large content expansion'),'M12 real playtest balance remains open');
ok(doc.includes('### 표본 준비도 / 0장 대비 비교 패널')&&doc.includes('코호트당 10판')&&doc.includes('20판'),'prototype doc records readiness thresholds');
ok(doc.includes('통계적 유의성이나 밸런스 합격선이 아니라'),'prototype doc explicitly prevents treating readiness as a balance verdict');
const namedStart=script.indexOf('const NAMED={'),namedEnd=script.indexOf('const FIELDS=',namedStart),namedBlock=script.slice(namedStart,namedEnd);
ok(!/topRank\s*:|bottomRank\s*:/.test(namedBlock),'readiness UI still promotes zero live asymmetric NAMED cards');
console.log('M11B experiment readiness/comparison regression passed.');

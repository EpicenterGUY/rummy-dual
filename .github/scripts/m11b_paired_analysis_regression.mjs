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

ok(html.includes('id="m11bExperimentPairedCompare"'),'developer experiment panel exposes a complete-pair-only comparison surface');
for(const n of ['m11bExperimentPairedGroups','m11bExperimentPairedAnalysis','m11bExperimentPairedComparisonText'])ok(script.includes(`function ${n}(`),`paired-analysis helper exists: ${n}`);
ok(source('renderM11BExperimentHistory').includes("paired=document.getElementById('m11bExperimentPairedCompare')")&&source('renderM11BExperimentHistory').includes('m11bExperimentPairedComparisonText(history)'),'experiment history renderer refreshes the paired comparison independently of raw cohort comparison');

const cohorts={zero:{id:'zero',label:'기준 0장'},few:{id:'few',label:'소수 4장'},many:{id:'many',label:'스트레스 10장'}};
function row(pairSeed,cohort,outcome,turns,maintenance,rummys,opponentMeldUses,multiAttachMax,rescuedActions=0,savedAt=0){return{pairSeed,cohort,outcome,turns,maintenance:Array.from({length:maintenance},()=>({actor:'player'})),rummys:Array.from({length:rummys},()=>({actor:'player'})),opponentMeldUses,multiAttachMax,rescuedActions,savedAt}}
const history=[
  row(11,'zero','win',10,2,0,1,1,0,100),
  row(11,'few','loss',20,5,0,0,1,0,50),
  row(11,'few','win',8,1,1,2,2,2,200),
  row(11,'many','loss',7,0,1,3,4,3,150),
  row(22,'zero','loss',12,1,0,0,2,0,100),
  row(22,'few','win',11,1,0,1,3,1,100),
  row(22,'many','win',10,0,1,2,3,4,100),
  row(33,'zero','win',9,0,0,1,1,0,100),
  row(33,'few','win',8,0,0,1,2,1,100)
];
{
  const ctx=vm.createContext({console,Map,Object,Array,Math,Number,M11B_EXPERIMENT_COHORTS:cohorts,m11bExperimentHistory:()=>history});
  install(ctx,'m11bExperimentPairedGroups','m11bExperimentPairedAnalysis');
  const groups=ctx.m11bExperimentPairedGroups(history);
  ok(groups.length===2&&groups.every(g=>g.rows.zero&&g.rows.few&&g.rows.many),'only seeds with all three cohorts enter paired analysis');
  ok(groups.find(g=>g.pairSeed===11).rows.few.turns===8,'duplicate seed/cohort runs use the most recent savedAt record only');
  const p=ctx.m11bExperimentPairedAnalysis(history);
  ok(p.pairs===2&&p.seeds.join(',')==='11,22','paired analysis reports exact complete-pair count and deterministic seed list');
  ok(p.few.winRate===50&&p.many.winRate===0,'paired win-rate deltas are computed within seed before averaging');
  ok(p.few.avgTurns===-1.5&&p.many.avgTurns===-2.5,'paired turn deltas average the two within-seed differences');
  ok(p.few.avgMaintenance===-0.5&&p.many.avgMaintenance===-1.5,'paired maintenance deltas use player-only maintenance counts');
  ok(p.few.avgRummys===0.5&&p.many.avgRummys===1,'paired RUMMY deltas use player-only events');
  ok(p.few.avgOpponentMeldUses===1&&p.many.avgOpponentMeldUses===2,'paired opponent-meld deltas are seed-controlled');
  ok(p.few.avgMultiAttachMax===1&&p.many.avgMultiAttachMax===2,'paired multi-attach metric compares per-battle maxima instead of global cohort peaks');
  ok(p.few.avgRescuedActions===1.5&&p.many.avgRescuedActions===3.5,'paired view carries counterfactual rescued-actions-per-battle context');
}
{
  const ctx=vm.createContext({console,Map,Object,Array,Math,Number,M11B_EXPERIMENT_COHORTS:cohorts,m11bExperimentHistory:()=>history});
  install(ctx,'m11bSigned','m11bExperimentPairedGroups','m11bExperimentPairedAnalysis','m11bExperimentPairedComparisonText');
  const text=ctx.m11bExperimentPairedComparisonText(history);
  ok(text.includes('완성 페어 2세트만 사용')&&text.includes('승률 +50%p')&&text.includes('턴 -1.5'),'paired comparison text exposes pair count and controlled deltas');
  ok(text.includes('표본 수가 작으면 참고용'),'paired comparison explicitly avoids declaring statistical or balance success');
  const incomplete=history.filter(x=>x.pairSeed===33);
  ok(ctx.m11bExperimentPairedComparisonText(incomplete).includes('완성 페어 필요'),'incomplete seeds never produce paired deltas');
}

ok(road.includes('- [x] 완성 페어 전용 0/4/10장 차이 분석'),'ROADMAP locks the complete-pair-only comparison tool');
ok(road.includes('- [ ] 비대칭 카드 0장 / 소수 / 다수 덱의 세트·런 성공률, 패말림, 정비, 러미 빈도 비교'),'paired tooling does not falsely close the real M11B battle-flow balance result');
ok(road.includes('- [ ] Balance from playtest data before large content expansion'),'paired tooling does not falsely close M12 playtest balance');
ok(doc.includes('### 완성 페어 전용 비교')&&doc.includes('가장 최근인 판 하나만 사용한다'),'prototype doc records duplicate-run selection and complete-pair methodology');
ok(doc.includes('통계적 유의성이나 밸런스 합격 판정이 아니며'),'prototype doc limits interpretation of paired results');
const ns=script.indexOf('const NAMED={'),ne=script.indexOf('const FIELDS=',ns),named=script.slice(ns,ne);ok(!/topRank\s*:|bottomRank\s*:/.test(named),'paired analysis still promotes zero live asymmetric NAMED cards');
console.log('M11B complete-pair analysis regression passed.');

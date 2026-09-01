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

ok(html.includes('id="m11bExperimentGapCompare"'),'developer panel exposes a gap-tier action analysis surface');
for(const n of ['m11bRankGap','m11bGapTier','m11bExperimentGapAnalysis','m11bExperimentGapAnalysisText'])ok(script.includes(`function ${n}(`),`gap-analysis helper exists: ${n}`);
ok(source('recordM11BActionCounterfactual').includes('gaps=synthetic.map(gapOf)')&&source('recordM11BActionCounterfactual').includes('maxGap')&&source('recordM11BActionCounterfactual').includes('gapTier:tierOf(maxGap)'),'successful asymmetric actions persist per-card gaps, maximum gap and tier');
ok(source('m11bExperimentSnapshot').includes("gaps:[...(x.gaps||[])]"),'experiment snapshot clones nested gap arrays instead of sharing telemetry references');
ok(source('renderM11BExperimentHistory').includes("gap=document.getElementById('m11bExperimentGapCompare')")&&source('renderM11BExperimentHistory').includes('m11bExperimentGapAnalysisText(history)'),'experiment renderer refreshes the gap-tier surface');

{
  const RANK_VALUE={A:1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,J:11,Q:12,K:13};
  const ctx=vm.createContext({console,Math,Number,RANK_VALUE});
  install(ctx,'m11bRankGap','m11bGapTier');
  const card=(topRank,bottomRank)=>({m11bSynthetic:true,topRank,bottomRank});
  ok(ctx.m11bRankGap(card('4','6'))===2&&ctx.m11bRankGap(card('5','K'))===8,'printed-rank gap uses canonical rank distance');
  ok(ctx.m11bGapTier(1)==='small'&&ctx.m11bGapTier(2)==='small','Δ1~2 maps to small tier');
  ok(ctx.m11bGapTier(3)==='medium'&&ctx.m11bGapTier(4)==='medium','Δ3~4 maps to medium tier');
  ok(ctx.m11bGapTier(5)==='large'&&ctx.m11bGapTier(6)==='large','Δ5~6 maps to large tier');
  ok(ctx.m11bGapTier(7)==='extreme'&&ctx.m11bGapTier(12)==='extreme','Δ7+ maps to extreme tier');
}

const history=[{actionCounterfactuals:[
  {gapTier:'small',maxGap:2,rescued:true,type:'SET',opponent:false,multi:false},
  {gapTier:'small',maxGap:1,rescued:false,type:'RUN',opponent:false,multi:false},
  {gapTier:'medium',maxGap:4,rescued:true,type:'RUN',opponent:true,multi:false},
  {gapTier:'large',maxGap:5,rescued:true,type:'SET',opponent:true,multi:true},
  {maxGap:6,rescued:true,type:'RUN',opponent:true,multi:false},
  {gapTier:'extreme',maxGap:8,rescued:true,type:'RUN',opponent:false,multi:true},
  {rescued:true,type:'SET',opponent:true,multi:true}
]}];
{
  const ctx=vm.createContext({console,Object,Array,Math,Number,m11bExperimentHistory:()=>history});
  install(ctx,'m11bGapTier','m11bExperimentGapAnalysis');
  const a=ctx.m11bExperimentGapAnalysis(history);
  ok(a.observed===6&&a.skipped===1,'gap analysis counts only events with real gap telemetry and reports legacy exclusions');
  ok(a.tiers.small.observed===2&&a.tiers.small.rescued===1&&a.tiers.small.rescueRate===50,'small tier rescue rate is calculated from observed successful actions');
  ok(a.tiers.medium.observed===1&&a.tiers.medium.rescuedRun===1&&a.tiers.medium.opponentRescued===1,'medium tier preserves RUN and opponent-meld rescue context');
  ok(a.tiers.large.observed===2&&a.tiers.large.rescued===2&&a.tiers.large.rescueRate===100,'maxGap fallback classifies Δ5~6 events into large tier');
  ok(a.tiers.large.opponentRescued===2&&a.tiers.large.multiRescued===1,'large tier separately tracks opponent-board and multi-attach rescues');
  ok(a.tiers.extreme.observed===1&&a.tiers.extreme.multiRescued===1,'extreme tier tracks Δ7+ multi-attach rescue');
}
{
  const ctx=vm.createContext({console,Object,Array,Math,Number,m11bExperimentHistory:()=>history});
  install(ctx,'m11bGapTier','m11bExperimentGapAnalysis','m11bExperimentGapAnalysisText');
  const text=ctx.m11bExperimentGapAnalysisText(history);
  ok(text.includes('Δ1~2')&&text.includes('Δ3~4')&&text.includes('Δ5~6')&&text.includes('Δ7+'),'developer text exposes all four design-budget gap tiers');
  ok(text.includes('한 행동에 X/Y가 여러 장이면 가장 큰 Δ 등급으로 분류'),'developer copy states maximum-gap attribution rule');
  ok(text.includes('구형 기록 1행동은 Δ정보가 없어 제외'),'developer copy reports old telemetry excluded from gap analysis');
}

ok(road.includes('- [x] 인쇄값 차이 Δ등급 행동 텔레메트리'),'ROADMAP locks gap-tier instrumentation and analysis');
ok(road.includes('- [ ] 큰 숫자 차이 자체가 덱 안정성을 지나치게 높이는지, 특히 다중 붙이기와 상대 공개 조합 이용에서 성공률 상승폭 측정'),'gap tooling does not falsely close the large-gap balance conclusion');
ok(road.includes('- [ ] 비대칭 카드 0장 / 소수 / 다수 덱의 세트·런 성공률, 패말림, 정비, 러미 빈도 비교'),'gap tooling does not falsely close overall cohort balance');
ok(doc.includes('### 인쇄값 차이 Δ등급 행동 분석')&&doc.includes('가장 큰 Δ'),'prototype doc records conservative maximum-gap action attribution');
ok(doc.includes('Δ정보 없음')&&doc.includes('최종 결론'),'prototype doc separates legacy exclusion and final-balance interpretation');
const ns=script.indexOf('const NAMED={'),ne=script.indexOf('const FIELDS=',ns),named=script.slice(ns,ne);ok(!/topRank\s*:|bottomRank\s*:/.test(named),'gap analysis still promotes zero live asymmetric NAMED cards');
console.log('M11B printed-gap action analysis regression passed.');

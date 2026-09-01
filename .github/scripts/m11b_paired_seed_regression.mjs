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

ok(html.includes('id="m11bPairSeedLabel"')&&html.includes('id="m11bNewPairSeedBtn"'),'developer panel exposes paired-seed status and refresh control');
ok(script.includes("const M11B_EXPERIMENT_SEED_KEY='rummyDuelM11BExperimentSeedV1'"),'paired experiment seed persists under its own key');
for(const n of ['m11bNormalizeSeed','m11bGenerateSeed','m11bExperimentSeedState','saveM11BExperimentSeedState','currentM11BExperimentSeed','newM11BExperimentSeed','markM11BExperimentSeedComplete','m11bExperimentSeedStatusText','renderM11BExperimentSeedStatus','m11bSeedMix','m11bSeededShuffle','m11bExperimentDeckSeed','m11bExperimentCompletePairs'])ok(script.includes(`function ${n}(`),`paired-seed helper exists: ${n}`);
ok(source('renderDeveloperPanel').includes("renderM11BExperimentSeedStatus"),'developer panel refreshes paired-seed status');
ok(script.includes("document.getElementById('m11bNewPairSeedBtn').onclick=()=>newM11BExperimentSeed()"),'new paired-seed button is wired');
ok((script.match(/document\.querySelectorAll\('\[data-m11b-experiment\]'\)\.forEach\(b=>b\.onclick=/g)||[]).length===1,'legacy duplicate cohort event wiring is normalized to one assignment');
ok((script.match(/document\.getElementById\('m11bExperimentClearBtn'\)\.onclick=/g)||[]).length===1,'legacy duplicate M11B clear event wiring is normalized to one assignment');
ok(source('newGame').includes('state.m11bExperimentSeed=null'),'ordinary new games clear the active battle seed snapshot');
ok(source('restartCurrentCombat').includes("state.m11bExperimentSeed||currentM11BExperimentSeed()"),'result replay preserves the active paired seed');
ok(source('setupM11BExperimentBattle').includes("p.deck=makeM11BExperimentDeck('player',cohort.id,pairSeed)")&&source('setupM11BExperimentBattle').includes("e.deck=makeM11BExperimentDeck('enemy','zero',pairSeed)"),'player and control opponent are both built from the same comparison seed');
ok(source('m11bExperimentSnapshot').includes('pairSeed:state.m11bExperimentSeed||null'),'experiment snapshot records the paired seed');
ok(source('saveM11BExperimentMetrics').includes('markM11BExperimentSeedComplete(snapshot.cohort,snapshot.pairSeed)'),'completed cohort is recorded against the active seed');

{
  const slots=['S3','S4','S5','S6','S7','S8','S9','H2','H3','H4','H7','H8','H9','D2','D3','D4','D5','D6','D7','D8','C3','C4','C5','C6','C7','C8','C9','S10','H10'];
  const specs={H4:['4','6'],S5:['5','8'],D4:['4','9'],C5:['5','K'],D6:['6','8'],C3:['3','6'],H7:['7','10'],C6:['6','J'],S8:['8','K'],D3:['3','Q']};
  const cohorts={zero:{id:'zero',label:'기준 0장',slots:[]},few:{id:'few',label:'소수 4장',slots:['H4','S5','D4','C5']},many:{id:'many',label:'스트레스 10장',slots:Object.keys(specs)}};
  let uid=1;
  const ctx=vm.createContext({console,Math,Number,Object,Array,Set,CORE_IDS:slots,M11B_EXPERIMENT_SPECS:specs,m11bExperimentCohort:id=>cohorts[id],makeCard:(suit,rank,named,owner,id=null)=>({uid:uid++,id:id||suit+rank,slot:suit==='J'?'J':suit+rank,suit,rank,baseRank:suit==='J'?null:rank,topRank:suit==='J'?null:rank,bottomRank:suit==='J'?null:rank,activeRank:null,rankOrientation:null,owner,named}),shuffle:x=>x});
  install(ctx,'m11bNormalizeSeed','m11bSeedMix','m11bSeededShuffle','m11bExperimentDeckSeed','makeM11BExperimentDeck');
  const seed=314159;
  const zero=ctx.makeM11BExperimentDeck('player','zero',seed),few=ctx.makeM11BExperimentDeck('player','few',seed),many=ctx.makeM11BExperimentDeck('player','many',seed);
  const order=x=>x.map(c=>c.slot).join(',');
  ok(order(zero)===order(few)&&order(few)===order(many),'same paired seed preserves identical player base-slot order across 0 / 4 / 10 cohorts');
  ok(zero.filter(c=>c.m11bSynthetic).length===0&&few.filter(c=>c.m11bSynthetic).length===4&&many.filter(c=>c.m11bSynthetic).length===10,'paired order changes only X/Y metadata density, not canonical slot membership');
  const enemyA=ctx.makeM11BExperimentDeck('enemy','zero',seed),enemyB=ctx.makeM11BExperimentDeck('enemy','zero',seed);
  ok(order(enemyA)===order(enemyB),'control opponent order is deterministic for the same paired seed');
  ok(order(enemyA)!==order(zero),'player and opponent use different seed salts instead of mirrored deck order');
  const other=ctx.makeM11BExperimentDeck('player','zero',271828);
  ok(order(other)!==order(zero),'changing comparison seed changes the deterministic deck order');
}

{
  const cohorts={zero:{id:'zero'},few:{id:'few'},many:{id:'many'}};
  const history=[{pairSeed:11,cohort:'zero'},{pairSeed:11,cohort:'few'},{pairSeed:11,cohort:'many'},{pairSeed:22,cohort:'zero'},{pairSeed:22,cohort:'few'},{pairSeed:33,cohort:'many'}];
  const ctx=vm.createContext({console,Map,Set,Array,M11B_EXPERIMENT_COHORTS:cohorts,m11bExperimentHistory:()=>history});
  install(ctx,'m11bExperimentCompletePairs');
  ok(ctx.m11bExperimentCompletePairs(history)===1,'only seeds with all three cohorts count as complete paired sets');
}

ok(source('m11bExperimentAggregateText').includes('완성 페어'),'developer aggregate reports complete paired-set count');
ok(road.includes('- [x] 0/4/10장 페어 시드 실험'),'ROADMAP locks paired-seed deck-order control');
ok(road.includes('- [ ] 비대칭 카드 0장 / 소수 / 다수 덱의 세트·런 성공률, 패말림, 정비, 러미 빈도 비교'),'final battle-flow comparison remains open until samples exist');
ok(doc.includes('### 페어 시드 — 초기 덱 순서 변수 통제')&&doc.includes('완전 리플레이가 아니다'),'prototype doc explicitly limits paired seed to deck-order control');
const namedStart=script.indexOf('const NAMED={'),namedEnd=script.indexOf('const FIELDS=',namedStart),namedBlock=script.slice(namedStart,namedEnd);
ok(!/topRank\s*:|bottomRank\s*:/.test(namedBlock),'paired-seed tooling still leaves live asymmetric NAMED count at zero');
console.log('M11B paired-seed experiment regression passed.');

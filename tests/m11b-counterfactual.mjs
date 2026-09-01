import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const doc=fs.readFileSync(new URL('../docs/ASYMMETRIC_RANK_PROTOTYPE.md',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let par=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')par++;else if(script[i]===')')par--;else if(script[i]==='{'&&par===0){brace=i;break}}let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
function install(ctx,...names){for(const n of names)vm.runInContext(source(n),ctx)}
new Function(script);
for(const n of ['m11bBaseRankProjection','m11bBaseActionType','recordM11BActionCounterfactual'])ok(script.includes(`function ${n}(`),`counterfactual helper exists: ${n}`);
ok(source('submitNewMeld').includes("recordM11BActionCounterfactual(w,cards,type,w,null)"),'new meld records a base-rank counterfactual only on the committed action path');
ok(source('attachCards').includes("recordM11BActionCounterfactual(w,cards,type,targetSide,m)"),'attach records a target-aware base-rank counterfactual on the committed action path');
ok(source('submitNewMeld').indexOf('recordM11BActionCounterfactual')>source('submitNewMeld').indexOf('applyRankChoicePlan'),'new-meld observation happens after selected rank commit validation');
ok(source('attachCards').indexOf('recordM11BActionCounterfactual')>source('attachCards').indexOf('applyRankChoicePlan'),'attach observation happens after selected rank commit validation');
ok(source('m11bExperimentSnapshot').includes('rescuedActions:st.rescuedActions')&&source('m11bExperimentSnapshot').includes('actionCounterfactuals:st.actionCounterfactuals'),'experiment snapshot persists counterfactual summary and event detail');
ok(source('recordM11BRankChoices').includes('gap=Math.abs'),'rank-choice telemetry also records printed-rank distance for later gap analysis');
ok(source('m11bExperimentAggregateText').includes('base 불가 구제'),'developer summary exposes base-rank-rescued actions');
ok(source('m11bExperimentRowText').includes('구제 ${row.rescuedActions||0}/${row.asymActions}'),'recent experiment rows expose rescued/observed asymmetric action counts');

function meldType(cards){const real=cards.filter(c=>c.suit!=='J');if(cards.length>=3){const ranks=real.map(c=>c.rank),suits=real.map(c=>c.suit);if(new Set(ranks).size===1&&new Set(suits).size===suits.length&&cards.length<=4)return'SET';if(new Set(suits).size===1){const v={A:1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,J:11,Q:12,K:13},vals=[...new Set(ranks.map(r=>v[r]))].sort((a,b)=>a-b);if(vals.length===cards.length&&vals.every((x,i)=>i===0||x===vals[i-1]+1))return'RUN'}}return null}
const RANK_VALUE={A:1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,J:11,Q:12,K:13};
function synth(slot,base,rank,top,bottom,suit=slot[0]){return{slot,m11bSyntheticSlot:slot,m11bSynthetic:true,baseRank:base,rank,activeRank:rank,rankOrientation:rank===bottom?'bottom':'top',topRank:top,bottomRank:bottom,suit}}
function plain(suit,rank){return{suit,rank,baseRank:rank,topRank:rank,bottomRank:rank}}
{
  const state={m11bExperimentBattle:true,m11bExperimentStats:null,turnNo:3},ctx=vm.createContext({console,Math,Array,Object,Set,RANK_VALUE,state,isJoker:c=>c?.suit==='J',meldType,other:w=>w==='player'?'enemy':'player',battleMetricTurn:()=>4});
  install(ctx,'getM11BExperimentStats','m11bBaseRankProjection','m11bBaseActionType','recordM11BActionCounterfactual');
  const setCards=[synth('S7','7','3','3','7','S'),plain('H','3'),plain('D','3')];
  const evt=ctx.recordM11BActionCounterfactual('player',setCards,'SET','player',null),st=ctx.getM11BExperimentStats();
  ok(evt.rescued===true&&evt.baseType===null,'X/Y-created SET is marked rescued when base ranks make no meld');
  ok(st.asymActions===1&&st.rescuedActions===1&&st.rescuedSet===1&&st.rescuedRun===0,'rescued SET counters update exactly once');
  ok(evt.multi===false&&st.rescuedMultiAttach===0,'new three-card meld is never counted as multi-attach telemetry');
  const baseSet=[synth('S3','3','3','5','3','S'),plain('H','3'),plain('D','3')];
  const evt2=ctx.recordM11BActionCounterfactual('player',baseSet,'SET','player',null);
  ok(evt2.baseLegal===true&&evt2.rescued===false&&st.asymActions===2&&st.rescuedActions===1,'choosing a flexible card does not count as rescue when base rank was already legal');
  const meld={type:'RUN',cards:[plain('C','4'),plain('C','5'),plain('C','6')]};
  const attach=[synth('C10','10','7','7','10','C')];
  const evt3=ctx.recordM11BActionCounterfactual('player',attach,'RUN','enemy',meld);
  ok(evt3.rescued&&evt3.opponent&&st.rescuedRun===1&&st.rescuedOpponentMeld===1,'opponent RUN extension rescued only by X/Y is isolated');
  const multi=[synth('CQ','Q','7','7','Q','C'),synth('CK','K','8','8','K','C')];
  const evt4=ctx.recordM11BActionCounterfactual('player',multi,'RUN','enemy',meld);
  ok(evt4.rescued&&evt4.multi&&st.rescuedMultiAttach===1&&st.rescuedOpponentMeld===2,'multi-attach and opponent-board rescue counters stack on the same rescued action');
  ok(st.actionCounterfactuals.length===4,'successful asymmetric actions retain event-level counterfactual detail');
  const before=JSON.stringify(setCards);ctx.m11bBaseActionType(setCards,null);ok(JSON.stringify(setCards)===before,'base-rank projection never mutates actual selected cards');
  ok(ctx.recordM11BActionCounterfactual('enemy',attach,'RUN','player',meld)===null,'zero-asymmetric control CPU never contributes player flexibility telemetry');
}

{
  const cohorts={zero:{id:'zero',label:'기준 0장'},few:{id:'few',label:'소수 4장'},many:{id:'many',label:'스트레스 10장'}},history=[{cohort:'few',outcome:'win',turns:8,maintenance:[],rummys:[],opponentMeldUses:2,multiAttachMax:3,rankChoiceTop:2,rankChoiceBottom:1,asymActions:4,rescuedActions:2,rescuedSet:1,rescuedRun:1,rescuedOpponentMeld:1,rescuedMultiAttach:1,typeShiftActions:1}];
  const ctx=vm.createContext({console,Object,Array,Math,Number,M11B_EXPERIMENT_COHORTS:cohorts,m11bExperimentHistory:()=>history,m11bExperimentCohort:id=>cohorts[id],m11bExperimentCompletePairs:()=>0});
  install(ctx,'m11bExperimentAggregate','m11bExperimentAggregateText');
  const a=ctx.m11bExperimentAggregate(history).few;
  ok(a.asymActions===4&&a.rescuedActions===2&&a.rescueRate===50,'aggregate calculates action-level rescue rate within observed asymmetric actions');
  ok(a.rescuedSet===1&&a.rescuedRun===1&&a.rescuedOpponentMeld===1&&a.rescuedMultiAttach===1&&a.typeShiftActions===1,'aggregate preserves rescue breakdowns and type shifts');
  ok(ctx.m11bExperimentAggregateText(history).includes('base 불가 구제 2 (50%)'),'developer aggregate prints the counterfactual rescue rate without declaring balance success');
}

ok(road.includes('- [x] 실제 행동 baseRank 반사실 텔레메트리'),'ROADMAP locks successful-action counterfactual instrumentation');
ok(road.includes('- [ ] 큰 숫자 차이 자체가 덱 안정성을 지나치게 높이는지, 특히 다중 붙이기와 상대 공개 조합 이용에서 성공률 상승폭 측정'),'large-gap real battle conclusion remains open');
ok(road.includes('- [ ] 비대칭 카드 0장 / 소수 / 다수 덱의 세트·런 성공률, 패말림, 정비, 러미 빈도 비교'),'full M11B battle-flow balance result remains open');
ok(doc.includes('### baseRank 반사실 행동 텔레메트리')&&doc.includes('관측 전용'),'prototype doc records non-mutating counterfactual methodology');
ok(doc.includes('모든 가능한 행동의 성공 확률이 아니다'),'prototype doc explicitly limits interpretation to chosen successful actions');
const ns=script.indexOf('const NAMED={'),ne=script.indexOf('const FIELDS=',ns),named=script.slice(ns,ne);ok(!/topRank\s*:|bottomRank\s*:/.test(named),'counterfactual telemetry still promotes zero live asymmetric NAMED cards');
console.log('M11B base-rank counterfactual telemetry regression passed.');

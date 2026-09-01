import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync('index.html','utf8');
const road=fs.readFileSync('ROADMAP.md','utf8');
const doc=fs.readFileSync('docs/ASYMMETRIC_RANK_PROTOTYPE.md','utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let par=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')par++;else if(script[i]===')')par--;else if(script[i]==='{'&&par===0){brace=i;break}}if(brace<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
new Function(script);
for(const name of ['rankChoiceOptions','rankChoicePlans','projectRankChoiceCards','rankChoicePlanLabel','legalRankChoicePlansForNewMeld','legalRankChoicePlansForAttach','rankChoicePreview'])ok(script.includes(`function ${name}(`),`rank-choice planning helper exists: ${name}`);

const RANK_VALUE={A:1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,J:11,Q:12,K:13};
const state={field:null,turnToken:1};
const ctx=vm.createContext({console,Math,Number,Object,Array,Set,RANK_VALUE,state});
for(const name of ['normalizePrototypeRank','ensureRankPrototype','cardPrintedRanks','isAsymmetricRankCard','isJoker','isSuitFlexible','rankChoiceOptions','rankChoicePlans','projectRankChoiceCards','rankChoicePlanLabel','runSequenceOK','setValid','runValid','meldType','legalRankChoicePlansForNewMeld','legalRankChoicePlansForAttach','rankChoicePreview'])vm.runInContext(source(name),ctx);
let uid=1;
const card=(suit,base,top=base,bottom=base,tag=null)=>({uid:uid++,suit,rank:base,baseRank:base,topRank:top,bottomRank:bottom,activeRank:null,rankOrientation:null,tag,owner:'player'});

{
  const a=card('S','7','3','7'),b=card('H','3'),c=card('D','3');
  const before=JSON.stringify(a),plans=ctx.rankChoicePlans([a,b,c]),legal=ctx.legalRankChoicePlansForNewMeld([a,b,c]);
  ok(plans.length===2,'one unresolved asymmetric card creates exactly top/bottom plan branches');
  ok(plans[0][0].orientation==='top'&&plans[0][0].rank==='3'&&plans[1][0].orientation==='bottom'&&plans[1][0].rank==='7','rank branches are deterministic top then bottom in selected-card order');
  ok(legal.length===1&&legal[0].type==='SET','only the printed 3 side makes the synthetic 3-set legal');
  ok(legal[0].plan[0].orientation==='top'&&legal[0].label.includes('1번 위 3'),'legal SET preview retains exact card position, orientation and rank label');
  ok(JSON.stringify(a)===before,'rank-plan enumeration and legality projection do not mutate the real card');
}

{
  const a=card('S','9','A','8'),b=card('S','2'),c=card('S','3');
  const legal=ctx.legalRankChoicePlansForNewMeld([a,b,c]);
  ok(legal.length===1&&legal[0].type==='RUN'&&legal[0].plan[0].rank==='A','asymmetric active Ace preserves legal A-2-3 RUN');
}
{
  const a=card('S','9','A','10'),b=card('S','Q'),c=card('S','K');
  const legal=ctx.legalRankChoicePlansForNewMeld([a,b,c]);
  ok(legal.length===1&&legal[0].type==='RUN'&&legal[0].plan[0].rank==='A','asymmetric active Ace preserves legal Q-K-A RUN');
}
{
  const a=card('S','9','A','Q'),b=card('S','K'),c=card('S','2');
  ok(ctx.legalRankChoicePlansForNewMeld([a,b,c]).length===0,'asymmetric rank choice does not introduce illegal K-A-2 RUN');
}
{
  const a=card('S','9','3','8'),b=card('S','4'),c=card('S','5');
  const legal=ctx.legalRankChoicePlansForNewMeld([a,b,c]);
  ok(legal.length===1&&legal[0].plan[0].rank==='3','ordinary 3-4-5 boundary remains legal only on the matching printed side');
}

{
  const meld={type:'SET',cards:[card('H','3'),card('D','3'),card('C','3')]},a=card('S','7','3','7');
  const legal=ctx.legalRankChoicePlansForAttach(meld,[a]);
  ok(legal.length===1&&legal[0].plan[0].rank==='3'&&legal[0].totalLength===4,'single attach preview finds only the printed value that completes the 4-card SET');
}
{
  const meld={type:'RUN',cards:[card('S','4'),card('S','5'),card('S','6')]};
  const a=card('S','9','10','7'),b=card('S','Q','Q','8'),beforeA=JSON.stringify(a),beforeB=JSON.stringify(b);
  const legal=ctx.legalRankChoicePlansForAttach(meld,[a,b]);
  ok(legal.length===1,'multi-attach rank planner filters four top/bottom combinations down to the one legal RUN plan');
  ok(legal[0].plan[0].orientation==='bottom'&&legal[0].plan[0].rank==='7'&&legal[0].plan[1].orientation==='bottom'&&legal[0].plan[1].rank==='8','multi-attach preview preserves selected card order and exact bottom/bottom choices');
  ok(legal[0].totalLength===5&&legal[0].type==='RUN','multi-attach projection preserves target RUN type and resulting length');
  ok(JSON.stringify(a)===beforeA&&JSON.stringify(b)===beforeB,'multi-attach legality preview leaves both real cards unresolved');
  const preview=ctx.rankChoicePreview([a,b],meld);
  ok(preview.requiresChoice&&preview.legal&&preview.count===1,'serialized preview reports that direction choice is required and exactly one legal plan exists');
  ok(preview.plans[0].ranks.join(',')==='7,8'&&preview.plans[0].orientations.join(',')==='bottom,bottom','serialized preview exposes ranks and orientations for future UI');
}

{
  const a=card('S','7','3','7'),b=card('H','8','4','8');
  const plans=ctx.rankChoicePlans([a,b]);
  ok(plans.length===4,'two unresolved asymmetric cards enumerate a four-plan Cartesian product');
  ok(plans.map(p=>p.map(x=>x.orientation).join('/')).join('|')==='top/top|top/bottom|bottom/top|bottom/bottom','Cartesian product order is stable for UI preview and deterministic tests');
  a.activeRank='7';a.rankOrientation='bottom';a.rank='7';
  const locked=ctx.rankChoicePlans([a,b]);
  ok(locked.length===2&&locked.every(p=>p[0].orientation==='bottom'&&p[0].locked),'already active rank stays locked while unresolved partner still branches');
}

const namedStart=script.indexOf('const NAMED={'),namedEnd=script.indexOf('const FIELDS=',namedStart),namedBlock=script.slice(namedStart,namedEnd);
ok(!/topRank\s*:|bottomRank\s*:/.test(namedBlock),'rank-choice planner still enables zero live asymmetric card definitions');
ok(doc.includes('## 2단계 — 사용값 plan 열거와 합법성 미리보기'),'prototype doc records rank-plan preview architecture');
ok(doc.includes('원본 카드 상태를 바꾸지 않고'),'prototype doc locks non-mutating legality exploration');
ok(road.includes('- [x] 새 조합 생성·붙이기·다중 붙이기에서 각 비대칭 카드의 사용값 선택 순서와 합법성 미리보기 구조 설계'),'ROADMAP locks M11B rank-choice legality preview');
ok(road.includes('- [x] A/Q/K 경계와 A-2-3 / Q-K-A / K-A-2 런 특수 규칙에서 비대칭 값 회귀 테스트 추가'),'ROADMAP locks asymmetric A/Q/K boundary regression');
ok(road.includes('- [ ] 버스트·체인·런 완주·러미 판정이 선택된 사용값만 읽고 기존 처리 순서를 그대로 유지하는지 검증'),'full live action/timing verification remains open');
ok(road.includes('- [ ] 조커의 와일드 판정, 기존 숫자 변경 효과, 복사 효과와 비대칭 값이 중첩될 때 우선순위 명문화'),'Joker/rank-modifier priority remains explicitly open');
console.log('M11B rank-choice planning and boundary regression passed.');

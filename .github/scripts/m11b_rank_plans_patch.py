from pathlib import Path

index=Path('index.html')
road=Path('ROADMAP.md')
doc=Path('docs/ASYMMETRIC_RANK_PROTOTYPE.md')
s=index.read_text()
r=road.read_text()
d=doc.read_text()

if 'function rankChoicePlans(' in s:
    raise SystemExit('M11B rank-choice planning already installed')

anchor='function makeCard(suit,rank,named,owner,variantId=null)'
if s.count(anchor)!=1:
    raise SystemExit(f'makeCard anchor mismatch: {s.count(anchor)}')
helpers=r'''function rankChoiceOptions(c){
  if(!c)return[];
  if(isJoker(c))return[{uid:c.uid,orientation:null,rank:c.rank||null,locked:true,choiceRequired:false}];
  ensureRankPrototype(c);
  if(c.activeRank){
    const orientation=c.rankOrientation||(c.activeRank===c.bottomRank&&c.activeRank!==c.topRank?'bottom':'top');
    return[{uid:c.uid,orientation,rank:c.activeRank,locked:true,choiceRequired:false}];
  }
  if(!isAsymmetricRankCard(c))return[{uid:c.uid,orientation:null,rank:c.baseRank||c.rank,locked:true,choiceRequired:false}];
  return cardPrintedRanks(c).map(x=>({uid:c.uid,orientation:x.orientation,rank:x.rank,locked:false,choiceRequired:true}));
}
function rankChoicePlans(cards,limit=64){
  const list=Array.isArray(cards)?cards:[],cap=Math.max(1,Math.min(256,Math.floor(Number(limit)||64))),out=[],options=list.map(rankChoiceOptions);
  if(options.some(x=>!x.length))return out;
  function rec(i,plan){
    if(out.length>=cap)return;
    if(i>=options.length){out.push(plan.map((x,index)=>({...x,index})));return}
    for(const opt of options[i]){plan.push(opt);rec(i+1,plan);plan.pop();if(out.length>=cap)break}
  }
  rec(0,[]);return out
}
function projectRankChoiceCards(cards,plan){
  const list=Array.isArray(cards)?cards:[],p=Array.isArray(plan)?plan:[];
  return list.map((c,i)=>{const pick=p[i];if(!pick||isJoker(c))return{...c};const projected={...c,rank:pick.rank};if(pick.orientation==='top'||pick.orientation==='bottom'){projected.activeRank=pick.rank;projected.rankOrientation=pick.orientation}else if(!c.activeRank){projected.activeRank=null;projected.rankOrientation=null}return projected})
}
function rankChoicePlanLabel(plan){const chosen=(Array.isArray(plan)?plan:[]).filter(x=>x.choiceRequired);return chosen.length?chosen.map(x=>`${x.index+1}번 ${x.orientation==='bottom'?'아래':'위'} ${x.rank}`).join(' · '):'기본 랭크'}
function legalRankChoicePlansForNewMeld(cards){
  if(!Array.isArray(cards)||cards.length!==3)return[];
  const out=[];for(const plan of rankChoicePlans(cards)){const projected=projectRankChoiceCards(cards,plan),type=meldType(projected);if(type)out.push({plan,type,projected,label:rankChoicePlanLabel(plan)})}return out
}
function legalRankChoicePlansForAttach(m,cards){
  if(!m||!Array.isArray(m.cards)||!Array.isArray(cards)||!cards.length)return[];
  const out=[];for(const plan of rankChoicePlans(cards)){const projected=projectRankChoiceCards(cards,plan),combined=m.cards.concat(projected),type=meldType(combined);if(type===m.type)out.push({plan,type,projected,totalLength:combined.length,label:rankChoicePlanLabel(plan)})}return out
}
function rankChoicePreview(cards,m=null){const plans=m?legalRankChoicePlansForAttach(m,cards):legalRankChoicePlansForNewMeld(cards);return{requiresChoice:(cards||[]).some(c=>isAsymmetricRankCard(c)&&!c.activeRank),legal:plans.length>0,count:plans.length,plans:plans.map(x=>({type:x.type,label:x.label,ranks:x.plan.map(p=>p.rank),orientations:x.plan.map(p=>p.orientation)}))}}
'''
s=s.replace(anchor,helpers+'\n'+anchor,1)

road_repls={
"- [ ] 새 조합 생성·붙이기·다중 붙이기에서 각 비대칭 카드의 사용값 선택 순서와 합법성 미리보기 구조 설계":"- [x] 새 조합 생성·붙이기·다중 붙이기에서 각 비대칭 카드의 사용값 선택 순서와 합법성 미리보기 구조 설계 — 선택한 카드 순서를 그대로 유지한 채 각 미확정 `X/Y`의 위→아래 후보를 최대 64개 조합으로 열거하고, 원본 카드를 변형하지 않는 projection에 기존 `meldType`을 적용해 새 3장 조합/단일·다중 붙이기의 합법 plan과 방향 라벨을 반환. 아직 실제 버튼/행동에는 연결하지 않은 dormant preview 계층",
"- [ ] A/Q/K 경계와 A-2-3 / Q-K-A / K-A-2 런 특수 규칙에서 비대칭 값 회귀 테스트 추가":"- [x] A/Q/K 경계와 A-2-3 / Q-K-A / K-A-2 런 특수 규칙에서 비대칭 값 회귀 테스트 추가 — 합성 비대칭 카드의 선택값으로 A-2-3 및 Q-K-A는 기존 런 규칙 그대로 허용하고 K-A-2는 거부하며, 일반 3-4-5와 세트/다중 붙이기 방향 조합도 실행 회귀로 고정"
}
for old,new in road_repls.items():
    if r.count(old)!=1:
        raise SystemExit(f'ROADMAP anchor mismatch: {old} -> {r.count(old)}')
    r=r.replace(old,new,1)

section='''\n## 2단계 — 사용값 plan 열거와 합법성 미리보기\n\n이 단계도 라이브 카드/행동에는 연결하지 않는다. 합성 비대칭 카드로 가능한 `top/bottom` 선택을 **원본 카드 상태를 바꾸지 않고** 탐색한다.\n\n- `rankChoiceOptions(card)`: 이미 `activeRank`가 고정된 카드는 1개 고정 후보, 일반 `X/X`도 1개 기본 후보, 미확정 `X/Y`만 `top → bottom` 두 후보를 낸다.\n- `rankChoicePlans(cards)`: 사용자가 고른 카드 배열 순서를 유지하며 후보의 데카르트 곱을 만든다. 현재 다중 붙이기 탐색 상한과 맞춰 기본 최대 64개 plan으로 제한한다.\n- `projectRankChoiceCards(cards, plan)`: 실제 카드 객체는 건드리지 않고 얕은 복제본의 `rank/activeRank/rankOrientation`만 plan대로 투영한다.\n- `legalRankChoicePlansForNewMeld(cards)`: 정확히 3장의 projection을 기존 `meldType()`에 통과시켜 합법 세트/런 plan만 반환한다.\n- `legalRankChoicePlansForAttach(meld, cards)`: 대상 공개 조합 + projection이 원래 조합 종류를 유지하는 plan만 반환한다. 단일/다중 붙이기에 같은 함수를 쓴다.\n- `rankChoicePreview(cards, meld?)`: 향후 UI가 사용할 수 있도록 선택 필요 여부, 합법 plan 수, 각 카드의 선택 랭크/방향을 직렬화한다.\n\n### 경계 규칙\n\n`activeRank`는 기존 엔진의 `rank` 미러로 투영되므로 새 런 규칙을 만들지 않는다. 따라서 기존과 동일하게 `A-2-3`, `Q-K-A`는 허용하고 `K-A-2`는 허용하지 않는다. 비대칭 카드는 이 판정을 우회하지 않고, 두 인쇄값 중 선택된 하나가 기존 `setValid/runValid`에 들어갈 뿐이다.\n\n### 아직 하지 않는 것\n\n- 실제 네임드 정의에 `topRank != bottomRank`를 넣지 않는다.\n- 손패 클릭/붙이기 버튼에서 방향 선택 모달을 열지 않는다.\n- AI가 방향을 선택하지 않는다.\n- 조커·카운터피터·랭크 복사와의 최종 우선순위를 아직 확정하지 않는다.\n'''
if '## 2단계 — 사용값 plan 열거와 합법성 미리보기' not in d:
    d=d.rstrip()+section+'\n'

index.write_text(s)
road.write_text(r)
doc.write_text(d)
print('M11B rank-choice planning layer installed')

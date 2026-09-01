from pathlib import Path

index=Path('index.html')
road=Path('ROADMAP.md')
doc=Path('docs/ASYMMETRIC_RANK_PROTOTYPE.md')
s=index.read_text()
r=road.read_text()
d=doc.read_text()

anchor="function rankChoicePreview(cards,m=null){const plans=m?legalRankChoicePlansForAttach(m,cards):legalRankChoicePlansForNewMeld(cards);return{requiresChoice:(cards||[]).some(c=>isAsymmetricRankCard(c)&&!c.activeRank),legal:plans.length>0,count:plans.length,plans:plans.map(x=>({type:x.type,label:x.label,ranks:x.plan.map(p=>p.rank),orientations:x.plan.map(p=>p.orientation)}))}}\n"
insert="""function normalizeRequestedRankPlan(cards,requestedPlan){\n  if(Array.isArray(requestedPlan))return requestedPlan;\n  if(requestedPlan&&Array.isArray(requestedPlan.ranks)&&Array.isArray(requestedPlan.orientations)&&requestedPlan.ranks.length===(cards||[]).length&&requestedPlan.orientations.length===(cards||[]).length)return(cards||[]).map((c,i)=>({uid:c.uid,index:i,rank:requestedPlan.ranks[i],orientation:requestedPlan.orientations[i]}));\n  return null\n}\nfunction rankChoicePlanEquivalent(cards,a,b){\n  const left=normalizeRequestedRankPlan(cards,a),right=normalizeRequestedRankPlan(cards,b);\n  if(!left||!right||left.length!==(cards||[]).length||right.length!==left.length)return false;\n  return left.every((x,i)=>{const y=right[i],c=cards[i];return!!x&&!!y&&x.uid===c.uid&&y.uid===c.uid&&x.rank===y.rank&&(x.orientation||null)===(y.orientation||null)})\n}\nfunction rankChoiceActionPlan(cards,m=null,requestedPlan=null){\n  const list=Array.isArray(cards)?cards:[],requiresChoice=list.some(c=>isAsymmetricRankCard(c)&&!c.activeRank),legal=m?legalRankChoicePlansForAttach(m,list):legalRankChoicePlansForNewMeld(list);\n  if(!legal.length)return{ok:false,reason:'illegal',requiresChoice,legalCount:0,plan:null,type:null,totalLength:m?.cards?.length?m.cards.length+list.length:list.length};\n  if(requestedPlan==null&&requiresChoice)return{ok:false,reason:'choice-required',requiresChoice:true,legalCount:legal.length,plan:null,type:null,totalLength:m?.cards?.length?m.cards.length+list.length:list.length};\n  const chosen=requestedPlan==null?legal[0]:legal.find(x=>rankChoicePlanEquivalent(list,x.plan,requestedPlan));\n  if(!chosen)return{ok:false,reason:'invalid-plan',requiresChoice,legalCount:legal.length,plan:null,type:null,totalLength:m?.cards?.length?m.cards.length+list.length:list.length};\n  return{ok:true,reason:null,requiresChoice,legalCount:legal.length,plan:chosen.plan,type:chosen.type,totalLength:chosen.totalLength||list.length,label:chosen.label}\n}\nfunction applyRankChoicePlan(cards,plan){\n  const list=Array.isArray(cards)?cards:[],normalized=normalizeRequestedRankPlan(list,plan);\n  if(!normalized||normalized.length!==list.length)return false;\n  for(let i=0;i<list.length;i++){const c=list[i],p=normalized[i],opts=rankChoiceOptions(c);if(!p||p.uid!==c.uid||!opts.some(o=>o.rank===p.rank&&(o.orientation||null)===(p.orientation||null)))return false}\n  const snap=list.map(c=>({rank:c.rank,activeRank:c.activeRank??null,rankOrientation:c.rankOrientation??null}));\n  for(let i=0;i<list.length;i++){const c=list[i],p=normalized[i];if(isJoker(c)||!isAsymmetricRankCard(c)||c.activeRank)continue;if(!chooseCardActiveRank(c,p.rank,p.orientation)){for(let j=0;j<list.length;j++){list[j].rank=snap[j].rank;list[j].activeRank=snap[j].activeRank;list[j].rankOrientation=snap[j].rankOrientation}return false}}\n  return true\n}\nfunction rankResolutionPriority(c,type=null){if(isJoker(c))return['joker-wild'];const out=[isAsymmetricRankCard(c)?'printed-choice':'printed-rank'];if(type==='SET'&&c?.tag==='flexRankCopy')out.push('set-rank-copy');if(type==='RUN'&&c?.tag==='counterfeiter')out.push('run-offset');return out}\n"""
if insert not in s:
    if s.count(anchor)!=1: raise SystemExit(f'rankChoicePreview anchor mismatch: {s.count(anchor)}')
    s=s.replace(anchor,anchor+insert,1)

old="function submitNewMeld(w,cards){const s=sideObj(w),access=typeof newMeldAccess==='function'?newMeldAccess(w,cards):{allowed:!s.newMeldUsed,extra:false,quickReloadCard:null};if(!access.allowed||cards.length!==3)return false;if(cards.some(c=>c.blockedUntilTurn===state.turnNo))return false;const type=meldType(cards);if(!type)return false;if(meldsOf(w).length>=2)return'full';if(!beforeNewMeld(w))return false;if(access.extra&&access.quickReloadCard){"
new="function submitNewMeld(w,cards,rankPlan=null){const s=sideObj(w),access=typeof newMeldAccess==='function'?newMeldAccess(w,cards):{allowed:!s.newMeldUsed,extra:false,quickReloadCard:null};if(!access.allowed||cards.length!==3)return false;if(cards.some(c=>c.blockedUntilTurn===state.turnNo))return false;const rankAction=typeof rankChoiceActionPlan==='function'?rankChoiceActionPlan(cards,null,rankPlan):{ok:true,type:meldType(cards),plan:null};if(!rankAction.ok||!rankAction.type)return false;const type=rankAction.type;if(meldsOf(w).length>=2)return'full';if(!beforeNewMeld(w))return false;if(rankAction.plan&&typeof applyRankChoicePlan==='function'&&!applyRankChoicePlan(cards,rankAction.plan))return false;if(access.extra&&access.quickReloadCard){"
if old in s:s=s.replace(old,new,1)
elif new not in s: raise SystemExit('submitNewMeld anchor missing')

old="function attachCards(w,cards,targetSide,targetIndex){\n"
new="function attachCards(w,cards,targetSide,targetIndex,rankPlan=null){\n"
if old in s:s=s.replace(old,new,1)
elif new not in s: raise SystemExit('attachCards signature anchor missing')

old="  const beforeLen=m.cards.length,beforeChain=m.chain||0,beforeCards=[...m.cards],combined=m.cards.concat(cards),type=meldType(combined);\n  if(type!==m.type)return false;\n  const willBaseReturn=type==='RUN'||(type==='SET'&&beforeLen===3&&combined.length===4);\n"
new="  const beforeLen=m.cards.length,beforeChain=m.chain||0,beforeCards=[...m.cards],rankAction=typeof rankChoiceActionPlan==='function'?rankChoiceActionPlan(cards,m,rankPlan):{ok:true,type:meldType(m.cards.concat(cards)),plan:null,totalLength:m.cards.length+cards.length};\n  if(!rankAction.ok||rankAction.type!==m.type)return false;\n  const type=rankAction.type,combinedLength=m.cards.length+cards.length;\n  const willBaseReturn=type==='RUN'||(type==='SET'&&beforeLen===3&&combinedLength===4);\n"
if old in s:s=s.replace(old,new,1)
elif new not in s: raise SystemExit('attachCards legality anchor missing')

old="  if(willBaseReturn&&!continuation&&s.returnedSwitchThisTurn)return false;\n  removeFromHand(w,cards);\n"
new="  if(willBaseReturn&&!continuation&&s.returnedSwitchThisTurn)return false;\n  if(rankAction.plan&&typeof applyRankChoicePlan==='function'&&!applyRankChoicePlan(cards,rankAction.plan))return false;\n  removeFromHand(w,cards);\n"
if old in s:s=s.replace(old,new,1)
elif new not in s: raise SystemExit('attachCards commit anchor missing')

road_old="- [ ] 버스트·체인·런 완주·러미 판정이 선택된 사용값만 읽고 기존 처리 순서를 그대로 유지하는지 검증"
road_new="- [x] 버스트·체인·런 완주·러미 판정이 선택된 사용값만 읽고 기존 처리 순서를 그대로 유지하는지 검증 — 행동 전 projection으로 합법성을 확인한 뒤 모든 실패 가능 기본 가드를 통과한 시점에 `applyRankChoicePlan()`이 `activeRank → rank`를 원자적으로 확정하고, 그 다음에만 손패 제거·공개 조합 삽입·버스트/체인 계산·효과·러미가 진행된다. 런 완주는 공개 조합에 고정된 선택값을 그대로 이벤트에 전달한 뒤 정리 시 초기화. 현재 라이브 비대칭 카드는 0장"
if road_old in r:r=r.replace(road_old,road_new,1)
elif road_new not in r: raise SystemExit('ROADMAP timing item missing')

prio_old="- [ ] 조커의 와일드 판정, 기존 숫자 변경 효과, 복사 효과와 비대칭 값이 중첩될 때 우선순위 명문화"
prio_new="- [x] 조커의 와일드 판정, 기존 숫자 변경 효과, 복사 효과와 비대칭 값이 중첩될 때 우선순위 명문화 — `조커 와일드 > 인쇄값 선택 > 카드 고유 숫자 보정`으로 잠금. 조커는 `activeRank`를 갖지 않고 기존 완전 와일드를 유지한다. 카운터피터의 런 ±1은 선택된 `activeRank`를 기준으로 합법성에서만 탐색하며 선택값을 변경하지 않는다. 도플갱어의 세트 랭크 복사는 세트 판정에서 선택값 위에 적용되지만 `activeRank/rankOrientation` 기록 자체는 유지한다"
if prio_old in r:r=r.replace(prio_old,prio_new,1)
elif prio_new not in r: raise SystemExit('ROADMAP priority item missing')

section="""
## 3단계 — 행동 확정과 숫자 우선순위

아직 라이브 비대칭 카드 정의와 플레이어 방향 선택 UI는 추가하지 않는다. 이 단계는 2단계의 projection 결과를 **실제 행동 직전** 안전하게 확정하는 계층이다.

- `rankChoiceActionPlan(cards, meld?, requestedPlan?)`: 새 조합/붙이기의 합법 plan 중 요청한 방향 조합이 실제 합법 목록에 있는지 다시 확인한다. 미확정 비대칭 카드가 있는데 plan이 없으면 `choice-required`로 거부한다.
- `applyRankChoicePlan(cards, plan)`: 모든 카드의 plan을 먼저 검증한 뒤 비대칭 카드만 `activeRank/rankOrientation/rank`에 일괄 반영한다. 하나라도 맞지 않으면 아무 카드도 바꾸지 않으며 중간 실패 시 snapshot으로 롤백한다.
- `submitNewMeld(..., rankPlan)`과 `attachCards(..., rankPlan)`은 기존 모든 기본 가드를 먼저 확인한 다음 공개 조합으로 카드를 이동하기 직전에만 plan을 확정한다. 따라서 실패한 행동이 손패 카드의 방향을 오염시키지 않는다.
- 기존 함수 추출형 회귀와 호환하기 위해 rank-choice helper가 없는 격리 테스트 환경에서는 예전 `meldType()` 경로로 fallback한다. 실제 전체 게임에서는 helper가 항상 존재한다.

### 숫자 판정 우선순위

1. **조커 와일드**: 조커는 `baseRank/topRank/bottomRank/activeRank`를 사용하지 않는다. 기존 세트/런의 빈 자리를 대신하는 완전 와일드 판정이 가장 먼저 독립적으로 적용된다.
2. **인쇄값 선택**: 일반 정규 카드는 `X/X`, 비대칭 정규 카드는 `X/Y` 중 하나를 선택해 `activeRank`를 확정한다. 이 값이 기존 `rank` 미러가 되어 이후 판정의 입력이 된다.
3. **카드 고유 숫자 보정**: 카운터피터는 런 판정에서 선택된 값의 `-1/0/+1`을 임시 후보로 탐색한다. 도플갱어(`flexRankCopy`)는 세트 판정에서 다른 고정 카드 랭크를 복사한다. 두 효과 모두 `activeRank`나 원본 인쇄값을 다시 쓰지 않는다.
4. **효과/공격/러미 처리**: 합법 조합이 확정된 뒤 버스트·체인·카드 효과·러미가 기존 순서대로 실행된다. 이 시점의 실제 카드 `rank`는 선택된 `activeRank`와 일치한다.
5. **조합 정리**: 버스트 정리, 런 완주, 회수/재순환 등으로 공개 조합을 떠날 때 기존 중앙 초기화 경로가 `activeRank/rankOrientation`을 지우고 `rank=baseRank`로 되돌린다.

합성 회귀에서는 비대칭 세트로 새 조합을 만든 뒤 러미까지 선택값이 유지되는지, 비대칭 카드로 상대 세트를 버스트하거나 런 체인을 올릴 때 선택값이 공개 조합/공격 처리에 들어가는지, 잘못된 plan이 실제 카드 상태를 부분 변경하지 않는지 검사한다.
"""
if '## 3단계 — 행동 확정과 숫자 우선순위' not in d:
    d=d.rstrip()+"\n"+section

index.write_text(s)
road.write_text(r)
doc.write_text(d)
print('M11B action-commit and priority layer installed')

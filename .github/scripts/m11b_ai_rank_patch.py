from pathlib import Path

index=Path('index.html')
road=Path('ROADMAP.md')
doc=Path('docs/ASYMMETRIC_RANK_PROTOTYPE.md')
s=index.read_text(); r=road.read_text(); d=doc.read_text()

old="function bestNewMeld(hand,w=null){let best=null;if(hand.length<3)return null;for(const cs of combinations(hand,3)){const t=meldType(cs);if(t){const risk=typeof futureBurstRisk==='function'?futureBurstRisk(w,cs,t):0;let sc=12+cs.filter(c=>c.named).length*2+(t==='SET'?3:2)-risk;if(!best||sc>best.score)best={cards:cs,type:t,score:sc}}}return best}"
new="function bestNewMeld(hand,w=null){let best=null;if(hand.length<3)return null;for(const cs of combinations(hand,3)){const planned=typeof legalRankChoicePlansForNewMeld==='function'?legalRankChoicePlansForNewMeld(cs):null,candidates=planned??[];if(planned===null){const t=meldType(cs);if(t)candidates.push({plan:null,type:t,projected:cs,label:'legacy'})}for(const cand of candidates){const t=cand.type,projected=cand.projected||cs,risk=typeof futureBurstRisk==='function'?futureBurstRisk(w,projected,t):0;let sc=12+cs.filter(c=>c.named).length*2+(t==='SET'?3:2)-risk;if(!best||sc>best.score)best={cards:cs,type:t,score:sc,rankPlan:cand.plan||null,rankPlanLabel:cand.label||null}}}return best}"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('bestNewMeld anchor missing')

old="function anyAttachOption(w){const s=sideObj(w),hand=s.hand.filter(c=>c.blockedUntilTurn!==state.turnNo);for(let k=1;k<=Math.min(6,hand.length);k++)for(const cs of combinations(hand,k))for(const targetSide of[w,other(w)])for(const m of meldsOf(targetSide)){const continuation=typeof canContinueReturnedRun==='function'&&canContinueReturnedRun(w,m);if(m.lastAttachToken===state.turnToken&&!continuation)continue;if(m.createdToken===state.turnToken&&targetSide===w)continue;const combined=m.cards.concat(cs),type=meldType(combined);if(type!==m.type)continue;const wouldReturn=m.type==='RUN'||(m.type==='SET'&&m.cards.length===3&&combined.length===4);if(wouldReturn&&!recoveredCardsCanReturn(cs,state.turnToken,m))continue;if(wouldReturn&&!continuation&&(!canSideReturn(w)||s.returnedSwitchThisTurn))continue;return true}return false}"
new="function anyAttachOption(w){const s=sideObj(w),hand=s.hand.filter(c=>c.blockedUntilTurn!==state.turnNo);for(let k=1;k<=Math.min(6,hand.length);k++)for(const cs of combinations(hand,k))for(const targetSide of[w,other(w)])for(const m of meldsOf(targetSide)){const continuation=typeof canContinueReturnedRun==='function'&&canContinueReturnedRun(w,m);if(m.lastAttachToken===state.turnToken&&!continuation)continue;if(m.createdToken===state.turnToken&&targetSide===w)continue;const planned=typeof legalRankChoicePlansForAttach==='function'?legalRankChoicePlansForAttach(m,cs):null,candidates=planned??[];if(planned===null){const combined=m.cards.concat(cs),type=meldType(combined);if(type===m.type)candidates.push({plan:null,type,projected:cs,totalLength:combined.length})}for(const cand of candidates){if(cand.type!==m.type)continue;const combinedLength=cand.totalLength||m.cards.length+cs.length,wouldReturn=m.type==='RUN'||(m.type==='SET'&&m.cards.length===3&&combinedLength===4);if(wouldReturn&&!recoveredCardsCanReturn(cs,state.turnToken,m))continue;if(wouldReturn&&!continuation&&(!canSideReturn(w)||s.returnedSwitchThisTurn))continue;return true}}return false}"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('anyAttachOption anchor missing')

old="function bestExtensionFromHand(w,hand,mustUid=null){const s=sideObj(w);let best=null;for(const targetSide of[w,other(w)])for(let i=0;i<meldsOf(targetSide).length;i++){const m=meldsOf(targetSide)[i],continuation=typeof canContinueReturnedRun==='function'&&canContinueReturnedRun(w,m);if(m.lastAttachToken===state.turnToken&&!continuation)continue;if(m.createdToken===state.turnToken&&targetSide===w)continue;for(let k=1;k<=Math.min(6,hand.length);k++)for(const cs of combinations(hand,k)){if(mustUid!=null&&!cs.some(c=>c.uid===mustUid))continue;if(cs.some(c=>c.blockedUntilTurn===state.turnNo))continue;const combined=m.cards.concat(cs);if(meldType(combined)!==m.type)continue;const wouldReturn=m.type==='RUN'||(m.type==='SET'&&m.cards.length===3&&combined.length===4);if(wouldReturn&&!recoveredCardsCanReturn(cs,state.turnToken,m))continue;if(wouldReturn&&!continuation&&(!canSideReturn(w)||s.returnedSwitchThisTurn))continue;let sc=0;if(m.type==='SET')sc=m.cards.length===3&&m.cards.length+k===4?24:0;else for(let z=1;z<=k;z++)sc+=chainDamage((m.chain||0)+z);const powerGain=sc;if(typeof opponentMeldAttachBias==='function')sc+=opponentMeldAttachBias(w,targetSide,m,combined,k);else if(targetSide===other(w))sc+=4;if(targetSide===other(w)&&cs.some(c=>c.tag==='enemyAttachBonus'))sc+=15;if(typeof themeAIAttachBias==='function')sc+=themeAIAttachBias(w,targetSide,m,cs,powerGain);if(!best||sc>best.score)best={cards:cs,side:targetSide,index:i,score:sc}}}return best}"
new="function bestExtensionFromHand(w,hand,mustUid=null){const s=sideObj(w);let best=null;for(const targetSide of[w,other(w)])for(let i=0;i<meldsOf(targetSide).length;i++){const m=meldsOf(targetSide)[i],continuation=typeof canContinueReturnedRun==='function'&&canContinueReturnedRun(w,m);if(m.lastAttachToken===state.turnToken&&!continuation)continue;if(m.createdToken===state.turnToken&&targetSide===w)continue;for(let k=1;k<=Math.min(6,hand.length);k++)for(const cs of combinations(hand,k)){if(mustUid!=null&&!cs.some(c=>c.uid===mustUid))continue;if(cs.some(c=>c.blockedUntilTurn===state.turnNo))continue;const planned=typeof legalRankChoicePlansForAttach==='function'?legalRankChoicePlansForAttach(m,cs):null,candidates=planned??[];if(planned===null){const combined=m.cards.concat(cs),type=meldType(combined);if(type===m.type)candidates.push({plan:null,type,projected:cs,totalLength:combined.length,label:'legacy'})}for(const cand of candidates){if(cand.type!==m.type)continue;const projected=cand.projected||cs,combined=m.cards.concat(projected),combinedLength=cand.totalLength||combined.length,wouldReturn=m.type==='RUN'||(m.type==='SET'&&m.cards.length===3&&combinedLength===4);if(wouldReturn&&!recoveredCardsCanReturn(cs,state.turnToken,m))continue;if(wouldReturn&&!continuation&&(!canSideReturn(w)||s.returnedSwitchThisTurn))continue;let sc=0;if(m.type==='SET')sc=m.cards.length===3&&combinedLength===4?24:0;else for(let z=1;z<=k;z++)sc+=chainDamage((m.chain||0)+z);const powerGain=sc;if(typeof opponentMeldAttachBias==='function')sc+=opponentMeldAttachBias(w,targetSide,m,combined,k);else if(targetSide===other(w))sc+=4;if(targetSide===other(w)&&cs.some(c=>c.tag==='enemyAttachBonus'))sc+=15;if(typeof themeAIAttachBias==='function')sc+=themeAIAttachBias(w,targetSide,m,projected,powerGain);if(!best||sc>best.score)best={cards:cs,side:targetSide,index:i,score:sc,rankPlan:cand.plan||null,rankPlanLabel:cand.label||null,projectedCards:projected}}}}return best}"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('bestExtensionFromHand anchor missing')

old="const r=attachCards('enemy',ex.cards,ex.side,ex.index);"
new="const r=attachCards('enemy',ex.cards,ex.side,ex.index,ex.rankPlan||null);"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('AI attach execution anchor missing')
old="const r=submitNewMeld('enemy',nm.cards);"
new="const r=submitNewMeld('enemy',nm.cards,nm.rankPlan||null);"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('AI new-meld execution anchor missing')

road_old="- [ ] CPU가 두 사용값의 세트·런 가능성, 즉시 버스트/체인, 스위치 반환 가치까지 비교하는 최소 휴리스틱 설계"
road_new="- [x] CPU가 두 사용값의 세트·런 가능성, 즉시 버스트/체인, 스위치 반환 가치까지 비교하는 최소 휴리스틱 설계 — `bestNewMeld`와 최대 6장 `bestExtensionFromHand`가 각 카드 조합의 모든 합법 top/bottom plan을 projection으로 비교하고, 새 조합은 기존 SET/RUN 점수·미래 버스트 노출 위험을 선택값 기준으로 계산하며, 붙이기는 실제 버스트 +24 / 체인 10·15·20·25… / 상대 공개 조합·테마 보정을 선택 plan의 projection에 적용한다. 선택된 `rankPlan`을 실제 `submitNewMeld/attachCards`에 전달하며, 막힘 판정 `anyAttachOption`도 비대칭 plan을 인식한다. 점수가 같으면 기존 위→아래 열거 순서를 유지해 결정적으로 선택하고 현재 라이브 비대칭 카드는 0장"
if road_old in r:r=r.replace(road_old,road_new,1)
elif road_new not in r:raise SystemExit('ROADMAP CPU item missing')

section="""
## 4단계 — CPU 사용값 선택

라이브 비대칭 카드를 추가하지 않은 채 CPU가 미래의 `X/Y` 카드를 정상적으로 사용할 수 있는 최소 계획 계층을 연결한다.

- 새 3장 조합: `bestNewMeld`가 손패 조합마다 `legalRankChoicePlansForNewMeld()`의 합법 방향을 모두 검사한다. 각 projection에 기존 새 조합 점수와 `futureBurstRisk()`를 그대로 적용하고 최고 점수의 `rankPlan`을 보존한다.
- 단일/다중 붙이기: `bestExtensionFromHand`가 최대 6장 조합의 모든 `legalRankChoicePlansForAttach()`를 검사한다. 선택된 projection으로 버스트 +24, 런 체인 단계 합계, 상대 공개 조합 보정, 테마 AI 보정을 계산한다.
- 스위치 반환 가치는 기존 AI 구조를 유지한다. 붙이기 후보의 점수 자체가 버스트/체인 위력을 포함하고, 현재 스위치가 CPU를 향하면 `continueAITurnAfterAcquisition()`이 새 조합보다 반환 가능한 붙이기를 우선한다. 따라서 비대칭 plan도 동일한 반환 판단에 들어간다.
- 실행 시 `bestNewMeld` / `bestExtensionFromHand`가 선택한 `rankPlan`을 각각 `submitNewMeld(..., rankPlan)` / `attachCards(..., rankPlan)`에 전달한다. CPU도 플레이어와 같은 원자적 plan 검증을 통과해야 실제 카드 방향이 확정된다.
- 완전 막힘 판정 `anyAttachOption`도 baseRank만 보지 않고 합법 top/bottom plan 존재 여부를 검사하므로, 다른 면으로는 붙일 수 있는 카드를 정비 대상으로 잘못 판정하지 않는다.
- 동점 plan은 기존 plan 열거 순서(카드 선택 순서, 위→아래)를 유지해 랜덤 노이즈 없이 결정적으로 선택한다.

이 단계도 현재 라이브 카드풀에는 `topRank/bottomRank` 비대칭 정의를 추가하지 않는다. 합성 회귀로만 CPU 선택과 실제 plan 전달을 검증한다.
"""
if '## 4단계 — CPU 사용값 선택' not in d:d=d.rstrip()+"\n"+section

index.write_text(s);road.write_text(r);doc.write_text(d)
print('M11B CPU rank-plan heuristic installed')

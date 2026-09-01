from pathlib import Path

p=Path('index.html'); s=p.read_text()
road=Path('ROADMAP.md'); r=road.read_text()
doc=Path('docs/ASYMMETRIC_RANK_PROTOTYPE.md'); d=doc.read_text()

def span(text,name):
    marker=f'function {name}('; start=text.find(marker)
    if start<0: raise SystemExit(f'missing {name}')
    brace=text.find('{',start); depth=0
    for i in range(brace,len(text)):
        if text[i]=='{': depth+=1
        elif text[i]=='}':
            depth-=1
            if depth==0:return start,i+1
    raise SystemExit(f'unterminated {name}')

def replace_fn(text,name,new):
    a,b=span(text,name); return text[:a]+new+text[b:]

helpers='''
function m11bBaseRankProjection(cards){return(Array.isArray(cards)?cards:[]).map(c=>{if(isJoker(c))return{...c};const base=c.baseRank||c.rank;return{...c,rank:base,activeRank:null,rankOrientation:null}})}
function m11bBaseActionType(cards,m=null){const projected=m11bBaseRankProjection(cards);if(!projected.length)return null;if(m){const type=meldType((m.cards||[]).concat(projected));return type===m.type?type:null}return meldType(projected)}
function recordM11BActionCounterfactual(w,cards,type,targetSide,m=null){if(!state.m11bExperimentBattle||w!=='player')return null;const list=Array.isArray(cards)?cards:[];if(!list.some(c=>c?.m11bSynthetic))return null;const st=getM11BExperimentStats(),baseType=m11bBaseActionType(list,m),baseLegal=!!baseType,rescued=!baseLegal,typeShift=!!baseType&&baseType!==type,evt={turn:typeof battleMetricTurn==='function'?battleMetricTurn():state.turnNo,type,targetSide,count:list.length,baseType,baseLegal,rescued,typeShift,opponent:targetSide===other(w),multi:list.length>1,slots:list.filter(c=>c?.m11bSynthetic).map(c=>c.m11bSyntheticSlot||c.slot)};st.asymActions++;if(typeShift)st.typeShiftActions++;if(rescued){st.rescuedActions++;if(type==='SET')st.rescuedSet++;if(type==='RUN')st.rescuedRun++;if(evt.opponent)st.rescuedOpponentMeld++;if(evt.multi)st.rescuedMultiAttach++}st.actionCounterfactuals.push(evt);return evt}
'''
if 'function m11bBaseRankProjection(' not in s:
    a,b=span(s,'recordM11BRankChoices'); s=s[:b]+helpers+s[b:]

stats='''function getM11BExperimentStats(){return state.m11bExperimentStats||(state.m11bExperimentStats={top:0,bottom:0,choices:[],asymActions:0,rescuedActions:0,rescuedSet:0,rescuedRun:0,rescuedOpponentMeld:0,rescuedMultiAttach:0,typeShiftActions:0,actionCounterfactuals:[]})}'''
s=replace_fn(s,'getM11BExperimentStats',stats)

choices='''function recordM11BRankChoices(cards,plan){if(!state.m11bExperimentBattle)return 0;const list=Array.isArray(cards)?cards:[],normalized=typeof normalizeRequestedRankPlan==='function'?normalizeRequestedRankPlan(list,plan):plan;if(!Array.isArray(normalized))return 0;const st=getM11BExperimentStats();let n=0;for(let i=0;i<list.length;i++){const c=list[i],x=normalized[i];if(!c?.m11bSynthetic||!isAsymmetricRankCard(c)||!x?.orientation)continue;const orientation=x.orientation==='bottom'?'bottom':'top',gap=Math.abs((RANK_VALUE[c.topRank]||0)-(RANK_VALUE[c.bottomRank]||0));st[orientation]++;st.choices.push({turn:typeof battleMetricTurn==='function'?battleMetricTurn():state.turnNo,slot:c.m11bSyntheticSlot||c.slot,topRank:c.topRank,bottomRank:c.bottomRank,rank:x.rank,orientation,gap});n++}return n}'''
s=replace_fn(s,'recordM11BRankChoices',choices)

# Setup explicitly initializes the expanded experiment telemetry.
a,b=span(s,'setupM11BExperimentBattle'); fn=s[a:b]
old="state.m11bExperimentStats={top:0,bottom:0,choices:[]};"
new="state.m11bExperimentStats={top:0,bottom:0,choices:[],asymActions:0,rescuedActions:0,rescuedSet:0,rescuedRun:0,rescuedOpponentMeld:0,rescuedMultiAttach:0,typeShiftActions:0,actionCounterfactuals:[]};"
if old in fn: fn=fn.replace(old,new,1)
elif new not in fn: raise SystemExit('setup stats anchor missing')
s=s[:a]+fn+s[b:]

snapshot='''function m11bExperimentSnapshot(outcome='result'){const base=battleMetricsSnapshot(outcome),cohort=m11bExperimentCohort(state.m11bExperimentCohort),st=getM11BExperimentStats();return{...base,version:2,mode:'m11b-experiment',cohort:cohort.id,cohortLabel:cohort.label,asymmetricCards:cohort.slots.length,syntheticSlots:[...cohort.slots],pairSeed:state.m11bExperimentSeed||null,rankChoiceTop:st.top,rankChoiceBottom:st.bottom,rankChoices:st.choices.map(x=>({...x})),asymActions:st.asymActions,rescuedActions:st.rescuedActions,rescuedSet:st.rescuedSet,rescuedRun:st.rescuedRun,rescuedOpponentMeld:st.rescuedOpponentMeld,rescuedMultiAttach:st.rescuedMultiAttach,typeShiftActions:st.typeShiftActions,actionCounterfactuals:st.actionCounterfactuals.map(x=>({...x,slots:[...x.slots]}))}}'''
s=replace_fn(s,'m11bExperimentSnapshot',snapshot)

# Successful new meld: rank plan is committed first; base-rank counterfactual then runs before hand mutation.
a,b=span(s,'submitNewMeld'); fn=s[a:b]
anchor="if(rankAction.plan&&typeof applyRankChoicePlan==='function'&&!applyRankChoicePlan(cards,rankAction.plan))return false;"
insert=anchor+"if(typeof recordM11BActionCounterfactual==='function')recordM11BActionCounterfactual(w,cards,type,w,null);"
if insert not in fn:
    if anchor not in fn: raise SystemExit('submit rank commit anchor missing')
    fn=fn.replace(anchor,insert,1)
s=s[:a]+fn+s[b:]

# Successful attach: same principle, target meld is still unmutated at measurement time.
a,b=span(s,'attachCards'); fn=s[a:b]
anchor="if(rankAction.plan&&typeof applyRankChoicePlan==='function'&&!applyRankChoicePlan(cards,rankAction.plan))return false;"
insert=anchor+"\n  if(typeof recordM11BActionCounterfactual==='function')recordM11BActionCounterfactual(w,cards,type,targetSide,m);"
if insert not in fn:
    if anchor not in fn: raise SystemExit('attach rank commit anchor missing')
    fn=fn.replace(anchor,insert,1)
s=s[:a]+fn+s[b:]

aggregate='''function m11bExperimentAggregate(history=m11bExperimentHistory()){const rows=(Array.isArray(history)?history:[]).filter(Boolean),avg=(list,fn)=>list.length?list.reduce((a,x)=>a+(Number(fn(x))||0),0)/list.length:0,sum=(list,fn)=>list.reduce((a,x)=>a+(Number(fn(x))||0),0);return Object.fromEntries(Object.keys(M11B_EXPERIMENT_COHORTS).map(id=>{const list=rows.filter(x=>x.cohort===id),wins=list.filter(x=>x.outcome==='win').length,asymActions=sum(list,x=>x.asymActions),rescuedActions=sum(list,x=>x.rescuedActions);return[id,{samples:list.length,winRate:list.length?Math.round(wins/list.length*100):0,avgTurns:avg(list,x=>x.turns),avgMaintenance:avg(list,x=>x.maintenance?.filter(e=>e.actor==='player').length||0),avgRummys:avg(list,x=>x.rummys?.filter(e=>e.actor==='player').length||0),avgOpponentMeldUses:avg(list,x=>x.opponentMeldUses),multiAttachPeak:list.reduce((m,x)=>Math.max(m,Number(x.multiAttachMax)||0),0),top:sum(list,x=>x.rankChoiceTop),bottom:sum(list,x=>x.rankChoiceBottom),asymActions,rescuedActions,rescueRate:asymActions?Math.round(rescuedActions/asymActions*100):0,rescuedSet:sum(list,x=>x.rescuedSet),rescuedRun:sum(list,x=>x.rescuedRun),rescuedOpponentMeld:sum(list,x=>x.rescuedOpponentMeld),rescuedMultiAttach:sum(list,x=>x.rescuedMultiAttach),typeShiftActions:sum(list,x=>x.typeShiftActions)}]}))}'''
s=replace_fn(s,'m11bExperimentAggregate',aggregate)

aggtext='''function m11bExperimentAggregateText(history=m11bExperimentHistory()){const a=m11bExperimentAggregate(history),fmt=n=>Number(n||0).toFixed(1),line=id=>{const x=a[id],c=m11bExperimentCohort(id),counter=x.asymActions?` · 비대칭 행동 ${x.asymActions} · base 불가 구제 ${x.rescuedActions} (${x.rescueRate}%) [세트 ${x.rescuedSet}/런 ${x.rescuedRun}/상대 ${x.rescuedOpponentMeld}/다중 ${x.rescuedMultiAttach}]${x.typeShiftActions?` · 타입 전환 ${x.typeShiftActions}`:''}`:'';return`${c.label} ${x.samples}판 · 승률 ${x.winRate}% · 턴 ${fmt(x.avgTurns)} · 정비 ${fmt(x.avgMaintenance)} · 러미 ${fmt(x.avgRummys)} · 상대 조합 ${fmt(x.avgOpponentMeldUses)} · 다중 최고 ${x.multiAttachPeak||1}장 · 선택 ↑${x.top}/↓${x.bottom}${counter}`};const total=Object.values(a).reduce((n,x)=>n+x.samples,0),pairs=typeof m11bExperimentCompletePairs==='function'?m11bExperimentCompletePairs(history):0;return total?[line('zero'),line('few'),line('many'),`완성 페어 ${pairs}세트`].join('<br>'):'아직 저장된 M11B 실험 표본이 없습니다.'}'''
s=replace_fn(s,'m11bExperimentAggregateText',aggtext)

row='''function m11bExperimentRowText(row){const result=row.outcome==='win'?'승':row.outcome==='loss'?'패':'무',stamp=row.savedAt?new Date(row.savedAt).toLocaleString('ko-KR',{month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit'}):'이전 기록',seed=row.pairSeed?` · 시드 ${row.pairSeed}`:'',counter=row.asymActions?` · 구제 ${row.rescuedActions||0}/${row.asymActions}`:'';return`<b>${row.cohortLabel||row.cohort} · ${result}</b> · ${stamp}${seed}<br>턴 ${row.turns||0} · 정비 ${row.maintenance?.filter(e=>e.actor==='player').length||0} · 러미 ${row.rummys?.filter(e=>e.actor==='player').length||0} · 상대 조합 ${row.opponentMeldUses||0} · 다중 ${row.multiAttachMax||1} · 사용값 ↑${row.rankChoiceTop||0}/↓${row.rankChoiceBottom||0}${counter}` }'''
s=replace_fn(s,'m11bExperimentRowText',row)

road_anchor='- [x] 0/4/10장 페어 시드 실험 — 동일 비교 시드에서는 플레이어 0/4/10장 코호트의 원본 29슬롯 카드 순서가 같고 상대 0장 기준덱 순서도 동일하도록 개발자 실험 덱만 결정론적으로 셔플. 완료한 코호트를 시드별로 추적하고 3종을 모두 끝낸 `완성 페어` 수를 표시하며, 시드는 덱 순서만 통제하고 인간/AI 행동까지 고정하는 완전 리플레이로 취급하지 않음'
road_item='- [x] 실제 행동 baseRank 반사실 텔레메트리 — M11B 실험전에서 합성 X/Y가 들어간 성공 행동마다 해당 손패 카드만 `baseRank`로 되돌린 projection을 기존 `meldType`으로 재판정해, 선택권이 없으면 불가능했던 `구제 행동`과 세트/런·상대 공개 조합·다중붙이기 구제 횟수, base에서도 합법하지만 조합 타입만 바뀐 횟수를 별도 기록. 실제 행동을 막거나 수정하지 않는 관측 전용 계층이며 최종 성공률/밸런스 판정은 표본 수집 전까지 미완료 유지'
if road_item not in r:
    if road_anchor not in r: raise SystemExit('paired-seed roadmap anchor missing')
    r=r.replace(road_anchor,road_anchor+'\n'+road_item,1)

append='''

### baseRank 반사실 행동 텔레메트리

실험전에서 X/Y를 실제로 사용한 **성공 행동**마다, 그 행동에 사용한 손패 카드만 원본 `baseRank`로 되돌린 복제본을 만들어 같은 공개 조합 상태에 다시 판정한다.

- 새 3장 조합은 base projection도 어떤 세트/런이든 합법이면 `base에서도 가능`으로 본다. 실제 X/Y 선택으로 세트↔런 타입만 달라졌다면 별도 `타입 전환`으로 센다.
- 붙이기는 목적지의 기존 공개 조합을 그대로 두고, 이번에 붙인 카드만 baseRank로 되돌렸을 때 **같은 조합 타입을 유지할 수 있는지** 판정한다.
- base projection이 불법인데 실제 선택값 행동은 성공했다면 `구제 행동`이다. 세트 / 런 / 상대 공개 조합 사용 / 2장 이상 다중붙이기 구제를 각각 별도 누적한다.
- 이 판정은 성공 행동 뒤의 효과나 위력에 관여하지 않는 **관측 전용**이다. 실제 카드·공개 조합을 되돌리거나 선택 결과를 수정하지 않는다.
- 개발자 패널은 코호트별 `비대칭 행동 N · base 불가 구제 M (비율)`과 세트/런/상대/다중 구제 내역을 보여준다.
- 이 값은 플레이어가 실제로 선택한 행동만 대상으로 하므로 모든 가능한 행동의 성공 확률이 아니다. M11B 최종 밸런스 체크는 코호트 표본과 M12 실플레이 데이터를 함께 본 뒤 결정한다.
'''
if '### baseRank 반사실 행동 텔레메트리' not in d:d=d.rstrip()+append+'\n'

p.write_text(s);road.write_text(r);doc.write_text(d)
print('M11B base-rank counterfactual telemetry patch installed')

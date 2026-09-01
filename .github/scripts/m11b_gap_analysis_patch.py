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

# Add a dedicated gap-tier surface after the paired comparison.
old_ui='<div id="m11bExperimentPairedCompare" class="m11bCompare m11bPairedCompare">같은 비교 시드의 0/4/10장을 모두 끝내면 완성 페어 차이를 표시합니다.</div><div id="m11bExperimentList"'
new_ui='<div id="m11bExperimentPairedCompare" class="m11bCompare m11bPairedCompare">같은 비교 시드의 0/4/10장을 모두 끝내면 완성 페어 차이를 표시합니다.</div><div id="m11bExperimentGapCompare" class="m11bCompare m11bGapCompare">비대칭 성공 행동이 쌓이면 인쇄값 차이 Δ1~2 / 3~4 / 5~6 / 7+별 구제율을 표시합니다.</div><div id="m11bExperimentList"'
if old_ui in s:s=s.replace(old_ui,new_ui,1)
elif 'id="m11bExperimentGapCompare"' not in s:raise SystemExit('gap comparison UI anchor missing')

helpers='''
function m11bRankGap(c){if(!c||!c.m11bSynthetic)return 0;const rv=typeof RANK_VALUE==='object'&&RANK_VALUE?RANK_VALUE:{A:1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,J:11,Q:12,K:13};return Math.abs((rv[c.topRank]||0)-(rv[c.bottomRank]||0))}
function m11bGapTier(gap){const n=Math.max(0,Math.round(Number(gap)||0));return n<=0?null:n<=2?'small':n<=4?'medium':n<=6?'large':'extreme'}
function m11bExperimentGapAnalysis(history=m11bExperimentHistory()){const tiers={small:{label:'Δ1~2',observed:0,rescued:0,rescuedSet:0,rescuedRun:0,opponentRescued:0,multiRescued:0},medium:{label:'Δ3~4',observed:0,rescued:0,rescuedSet:0,rescuedRun:0,opponentRescued:0,multiRescued:0},large:{label:'Δ5~6',observed:0,rescued:0,rescuedSet:0,rescuedRun:0,opponentRescued:0,multiRescued:0},extreme:{label:'Δ7+',observed:0,rescued:0,rescuedSet:0,rescuedRun:0,opponentRescued:0,multiRescued:0}};let skipped=0;for(const row of Array.isArray(history)?history:[])for(const evt of Array.isArray(row?.actionCounterfactuals)?row.actionCounterfactuals:[]){const tier=evt.gapTier||m11bGapTier(evt.maxGap);if(!tier||!tiers[tier]){skipped++;continue}const x=tiers[tier];x.observed++;if(evt.rescued){x.rescued++;if(evt.type==='SET')x.rescuedSet++;if(evt.type==='RUN')x.rescuedRun++;if(evt.opponent)x.opponentRescued++;if(evt.multi)x.multiRescued++}}for(const x of Object.values(tiers))x.rescueRate=x.observed?Math.round(x.rescued/x.observed*100):0;return{tiers,observed:Object.values(tiers).reduce((n,x)=>n+x.observed,0),skipped}}
function m11bExperimentGapAnalysisText(history=m11bExperimentHistory()){const a=m11bExperimentGapAnalysis(history);if(!a.observed)return'<b>Δ등급 행동 표본 필요</b> · 새 반사실 텔레메트리 이후 비대칭 성공 행동이 기록되면 숫자 차이별 구제율을 표시합니다.';const order=['small','medium','large','extreme'],line=id=>{const x=a.tiers[id];return`<b>${x.label}</b> · 행동 ${x.observed} · 구제 ${x.rescued} (${x.rescueRate}%) · 세트 ${x.rescuedSet} / 런 ${x.rescuedRun} · 상대 ${x.opponentRescued} · 다중 ${x.multiRescued}`};return`<b>인쇄값 차이별 성공 행동 반사실</b> · 한 행동에 X/Y가 여러 장이면 가장 큰 Δ 등급으로 분류 · 표본 전 결론 금지<br>${order.map(line).join('<br>')}${a.skipped?`<br>구형 기록 ${a.skipped}행동은 Δ정보가 없어 제외`:''}`}
'''
if 'function m11bRankGap(' not in s:
    a,b=span(s,'m11bBaseActionType'); s=s[:b]+helpers+s[b:]

# Enrich successful-action counterfactual events with gap values. Keep fallbacks so isolated regressions can extract this function alone.
record="""function recordM11BActionCounterfactual(w,cards,type,targetSide,m=null){if(!state.m11bExperimentBattle||w!=='player')return null;const list=Array.isArray(cards)?cards:[];if(!list.some(c=>c?.m11bSynthetic))return null;const synthetic=list.filter(c=>c?.m11bSynthetic),gapOf=typeof m11bRankGap==='function'?m11bRankGap:c=>{const rv=typeof RANK_VALUE==='object'&&RANK_VALUE?RANK_VALUE:{A:1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,J:11,Q:12,K:13};return Math.abs((rv[c?.topRank]||0)-(rv[c?.bottomRank]||0))},gaps=synthetic.map(gapOf),maxGap=gaps.length?Math.max(...gaps):0,tierOf=typeof m11bGapTier==='function'?m11bGapTier:n=>n<=0?null:n<=2?'small':n<=4?'medium':n<=6?'large':'extreme',st=getM11BExperimentStats(),baseType=m11bBaseActionType(list,m),baseLegal=!!baseType,rescued=!baseLegal,typeShift=!!baseType&&baseType!==type,evt={turn:typeof battleMetricTurn==='function'?battleMetricTurn():state.turnNo,type,targetSide,count:list.length,baseType,baseLegal,rescued,typeShift,opponent:targetSide===other(w),multi:!!m&&list.length>1,slots:synthetic.map(c=>c.m11bSyntheticSlot||c.slot),gaps,maxGap,gapTier:tierOf(maxGap)};st.asymActions++;if(typeShift)st.typeShiftActions++;if(rescued){st.rescuedActions++;if(type==='SET')st.rescuedSet++;if(type==='RUN')st.rescuedRun++;if(evt.opponent)st.rescuedOpponentMeld++;if(evt.multi)st.rescuedMultiAttach++}st.actionCounterfactuals.push(evt);return evt}"""
a,b=span(s,'recordM11BActionCounterfactual'); s=s[:a]+record+s[b:]

# Snapshot nested arrays independently.
a,b=span(s,'m11bExperimentSnapshot'); fn=s[a:b]
old="actionCounterfactuals:st.actionCounterfactuals.map(x=>({...x,slots:[...x.slots]}))"
new="actionCounterfactuals:st.actionCounterfactuals.map(x=>({...x,slots:[...x.slots],gaps:[...(x.gaps||[])]}))"
if old in fn:fn=fn.replace(old,new,1)
elif new not in fn:raise SystemExit('snapshot counterfactual copy anchor missing')
s=s[:a]+fn+s[b:]

render="""function renderM11BExperimentHistory(){const history=m11bExperimentHistory(),count=document.getElementById('m11bExperimentCount'),readiness=document.getElementById('m11bExperimentReadiness'),overview=document.getElementById('m11bExperimentOverview'),compare=document.getElementById('m11bExperimentCompare'),paired=document.getElementById('m11bExperimentPairedCompare'),gap=document.getElementById('m11bExperimentGapCompare'),list=document.getElementById('m11bExperimentList');if(count)count.textContent=`${history.length}판`;if(readiness){const gate=m11bExperimentReadiness(history);readiness.textContent=m11bExperimentReadinessText(history);readiness.dataset.state=gate.allStable?'stable':gate.allReady?'ready':'collecting'}if(overview)overview.innerHTML=m11bExperimentAggregateText(history);if(compare)compare.innerHTML=m11bExperimentComparisonText(history);if(paired)paired.innerHTML=m11bExperimentPairedComparisonText(history);if(gap)gap.innerHTML=m11bExperimentGapAnalysisText(history);if(list)list.innerHTML=history.length?history.slice(-8).reverse().map(x=>`<div class=\"metricsRow\">${m11bExperimentRowText(x)}</div>`).join(''):'<div class=\"metricsEmpty\">위의 0/4/10장 실험전을 끝내면 별도 기록이 쌓입니다.</div>';return history}"""
a,b=span(s,'renderM11BExperimentHistory'); s=s[:a]+render+s[b:]

road_anchor='- [x] 완성 페어 전용 0/4/10장 차이 분석 — 같은 `pairSeed`에서 세 코호트를 모두 완료한 기록만 묶고, 같은 시드·같은 코호트 재실험은 가장 최근 판만 사용. 승률·턴·정비·러미·상대 공개 조합 사용·판별 최대 다중붙이기를 시드 안에서 먼저 0장 기준으로 차감한 뒤 완성 페어 전체 평균을 개발자 패널에 별도 표시하며, 구제 행동/판도 함께 보여준다. 전체 코호트 평균은 그대로 남기고 페어 분석 역시 표본 수가 작을 때 밸런스 결론으로 취급하지 않음'
road_item='- [x] 인쇄값 차이 Δ등급 행동 텔레메트리 — 비대칭 성공 행동에 사용된 합성 X/Y의 인쇄값 차이를 기록하고, 한 행동에 여러 X/Y가 있으면 최대 Δ를 기준으로 `Δ1~2 / Δ3~4 / Δ5~6 / Δ7+`에 분류. 등급별 관측 행동·baseRank 구제율·세트/런·상대 공개 조합·다중붙이기 구제 횟수를 개발자 패널에 표시하며, Δ정보가 없는 기존 기록은 별도 제외 수로 표시. 큰 숫자 차이의 실제 밸런스 결론은 표본 전까지 미완료 유지'
if road_item not in r:
    if road_anchor not in r:raise SystemExit('paired analysis roadmap anchor missing')
    r=r.replace(road_anchor,road_anchor+'\n'+road_item,1)

append='''

### 인쇄값 차이 Δ등급 행동 분석

비대칭의 숫자 간격 자체가 안정성을 얼마나 올리는지 보기 위해, 성공 행동 반사실 이벤트에 그 행동에서 사용한 합성 X/Y 카드들의 인쇄값 차이 `gap`을 함께 저장한다.

- 등급은 설계 예산과 동일하게 `Δ1~2 = 소`, `Δ3~4 = 중`, `Δ5~6 = 대`, `Δ7+ = 극단`으로 나눈다.
- 한 행동에 X/Y가 여러 장 들어가면 **가장 큰 Δ**를 그 행동의 등급으로 사용한다. 큰 간격 카드가 포함된 행동의 위험을 작은 간격으로 희석하지 않기 위한 보수적 분류다.
- 등급별로 관측된 비대칭 성공 행동 수, baseRank로는 불가능했던 구제 행동 수/비율, 세트·런 구제, 상대 공개 조합 구제, 다중붙이기 구제를 표시한다.
- `gapTier/maxGap`이 저장되기 전의 구형 반사실 이벤트는 추정해서 섞지 않고 `Δ정보 없음`으로 제외한다.
- 이 분석은 이미 선택되어 성공한 행동의 조건부 통계다. 큰 Δ가 덱 전체 승률이나 패말림을 얼마나 바꾸는지에 대한 최종 결론은 0/4/10장 코호트와 완성 페어 표본을 함께 본 뒤 내린다.
'''
if '### 인쇄값 차이 Δ등급 행동 분석' not in d:d=d.rstrip()+append+'\n'

p.write_text(s);road.write_text(r);doc.write_text(d)
print('M11B gap-tier action telemetry patch installed')

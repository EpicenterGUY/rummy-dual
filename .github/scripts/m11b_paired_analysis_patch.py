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

# Developer surface: keep raw cohort comparison and add complete-pair-only comparison below it.
old_ui='<div id="m11bExperimentCompare" class="m11bCompare">0장 기준 표본이 쌓이면 4장/10장 차이를 표시합니다.</div><div id="m11bExperimentList"'
new_ui='<div id="m11bExperimentCompare" class="m11bCompare">0장 기준 표본이 쌓이면 4장/10장 차이를 표시합니다.</div><div id="m11bExperimentPairedCompare" class="m11bCompare m11bPairedCompare">같은 비교 시드의 0/4/10장을 모두 끝내면 완성 페어 차이를 표시합니다.</div><div id="m11bExperimentList"'
if old_ui in s:
    s=s.replace(old_ui,new_ui,1)
elif 'id="m11bExperimentPairedCompare"' not in s:
    raise SystemExit('M11B paired comparison UI anchor missing')

# Add complete-pair analysis helpers after the existing complete-pair counter.
helpers='''
function m11bExperimentPairedGroups(history=m11bExperimentHistory()){const groups=new Map();for(const row of Array.isArray(history)?history:[]){if(!row?.pairSeed||!M11B_EXPERIMENT_COHORTS[row.cohort])continue;const key=String(row.pairSeed),g=groups.get(key)||{pairSeed:row.pairSeed,rows:{}};const prev=g.rows[row.cohort],prevTime=Number(prev?.savedAt)||0,nextTime=Number(row.savedAt)||0;if(!prev||nextTime>=prevTime)g.rows[row.cohort]=row;groups.set(key,g)}return[...groups.values()].filter(g=>g.rows.zero&&g.rows.few&&g.rows.many).sort((a,b)=>(Number(a.pairSeed)||0)-(Number(b.pairSeed)||0))}
function m11bExperimentPairedAnalysis(history=m11bExperimentHistory()){const pairs=m11bExperimentPairedGroups(history),avg=(id,fn)=>pairs.length?pairs.reduce((sum,g)=>sum+(Number(fn(g.rows[id]))||0)-(Number(fn(g.rows.zero))||0),0)/pairs.length:0,win=x=>x?.outcome==='win'?1:0,maintenance=x=>x?.maintenance?.filter(e=>e.actor==='player').length||0,rummy=x=>x?.rummys?.filter(e=>e.actor==='player').length||0,rescue=x=>Number(x?.rescuedActions)||0,line=id=>({winRate:avg(id,win)*100,avgTurns:avg(id,x=>x?.turns),avgMaintenance:avg(id,maintenance),avgRummys:avg(id,rummy),avgOpponentMeldUses:avg(id,x=>x?.opponentMeldUses),avgMultiAttachMax:avg(id,x=>x?.multiAttachMax||1),avgRescuedActions:pairs.length?pairs.reduce((sum,g)=>sum+rescue(g.rows[id]),0)/pairs.length:0});return{pairs:pairs.length,few:line('few'),many:line('many'),seeds:pairs.map(g=>g.pairSeed)}}
function m11bExperimentPairedComparisonText(history=m11bExperimentHistory()){const p=m11bExperimentPairedAnalysis(history);if(!p.pairs)return'<b>완성 페어 필요</b> · 같은 비교 시드에서 0장·4장·10장을 모두 끝내면 시드 내 차이를 계산합니다.';const line=(x,label)=>`<b>${label} vs 0장</b> · 승률 ${m11bSigned(x.winRate,0,'%p')} · 턴 ${m11bSigned(x.avgTurns,1)} · 정비 ${m11bSigned(x.avgMaintenance,1)} · 러미 ${m11bSigned(x.avgRummys,1)} · 상대 조합 ${m11bSigned(x.avgOpponentMeldUses,1)} · 다중 최대/판 ${m11bSigned(x.avgMultiAttachMax,1)}장 · 구제/판 ${x.avgRescuedActions.toFixed(1)}`;return`<b>완성 페어 ${p.pairs}세트만 사용</b> · 동일 seed 안에서 먼저 0장 값을 뺀 뒤 평균 · 표본 수가 작으면 참고용<br>${line(p.few,'소수 4장')}<br>${line(p.many,'스트레스 10장')}`}
'''
if 'function m11bExperimentPairedGroups(' not in s:
    a,b=span(s,'m11bExperimentCompletePairs'); s=s[:b]+helpers+s[b:]

# Refresh paired surface whenever experiment history changes.
render='''function renderM11BExperimentHistory(){const history=m11bExperimentHistory(),count=document.getElementById('m11bExperimentCount'),readiness=document.getElementById('m11bExperimentReadiness'),overview=document.getElementById('m11bExperimentOverview'),compare=document.getElementById('m11bExperimentCompare'),paired=document.getElementById('m11bExperimentPairedCompare'),list=document.getElementById('m11bExperimentList');if(count)count.textContent=`${history.length}판`;if(readiness){const gate=m11bExperimentReadiness(history);readiness.textContent=m11bExperimentReadinessText(history);readiness.dataset.state=gate.allStable?'stable':gate.allReady?'ready':'collecting'}if(overview)overview.innerHTML=m11bExperimentAggregateText(history);if(compare)compare.innerHTML=m11bExperimentComparisonText(history);if(paired)paired.innerHTML=m11bExperimentPairedComparisonText(history);if(list)list.innerHTML=history.length?history.slice(-8).reverse().map(x=>`<div class="metricsRow">${m11bExperimentRowText(x)}</div>`).join(''):'<div class="metricsEmpty">위의 0/4/10장 실험전을 끝내면 별도 기록이 쌓입니다.</div>';return history}'''
a,b=span(s,'renderM11BExperimentHistory'); s=s[:a]+render+s[b:]

road_anchor='- [x] 실제 행동 baseRank 반사실 텔레메트리 — M11B 실험전에서 합성 X/Y가 들어간 성공 행동마다 해당 손패 카드만 `baseRank`로 되돌린 projection을 기존 `meldType`으로 재판정해, 선택권이 없으면 불가능했던 `구제 행동`과 세트/런·상대 공개 조합·다중붙이기 구제 횟수, base에서도 합법하지만 조합 타입만 바뀐 횟수를 별도 기록. 실제 행동을 막거나 수정하지 않는 관측 전용 계층이며 최종 성공률/밸런스 판정은 표본 수집 전까지 미완료 유지'
road_item='- [x] 완성 페어 전용 0/4/10장 차이 분석 — 같은 `pairSeed`에서 세 코호트를 모두 완료한 기록만 묶고, 같은 시드·같은 코호트 재실험은 가장 최근 판만 사용. 승률·턴·정비·러미·상대 공개 조합 사용·판별 최대 다중붙이기를 시드 안에서 먼저 0장 기준으로 차감한 뒤 완성 페어 전체 평균을 개발자 패널에 별도 표시하며, 구제 행동/판도 함께 보여준다. 전체 코호트 평균은 그대로 남기고 페어 분석 역시 표본 수가 작을 때 밸런스 결론으로 취급하지 않음'
if road_item not in r:
    if road_anchor not in r: raise SystemExit('counterfactual roadmap anchor missing')
    r=r.replace(road_anchor,road_anchor+'\n'+road_item,1)

append='''

### 완성 페어 전용 비교

전체 0/4/10장 코호트 평균은 수집량을 빠르게 보는 용도지만 서로 다른 비교 시드가 섞일 수 있다. 그래서 별도로 **같은 `pairSeed`에서 0장·4장·10장을 모두 끝낸 완성 페어만** 사용한 비교를 제공한다.

- 같은 시드에서 같은 코호트를 여러 번 끝냈다면 `savedAt`이 가장 최근인 판 하나만 사용한다. 오래된 재시도와 최신 재시도를 동시에 한 페어로 중복 계산하지 않는다.
- 세 코호트 중 하나라도 빠진 시드는 페어 분석에서 제외한다. 전체 코호트 요약에는 기존처럼 남는다.
- 각 완성 페어 안에서 먼저 `4장 - 0장`, `10장 - 0장` 차이를 계산한 뒤 그 차이를 모든 완성 페어에 걸쳐 평균한다.
- 표시 항목은 승률 차이, 평균 턴, 플레이어 정비, 플레이어 러미, 상대 공개 조합 사용, 한 판의 최대 다중붙이기와 비대칭 baseRank 구제 행동/판이다.
- 페어 시드는 초기 덱 순서만 통제한다. 인간 선택과 AI 행동을 고정하지 않으므로 페어 분석도 통계적 유의성이나 밸런스 합격 판정이 아니며, 완성 페어 수가 적을 때는 참고용이다.
'''
if '### 완성 페어 전용 비교' not in d:d=d.rstrip()+append+'\n'

p.write_text(s); road.write_text(r); doc.write_text(d)
print('M11B complete-pair comparison patch installed')

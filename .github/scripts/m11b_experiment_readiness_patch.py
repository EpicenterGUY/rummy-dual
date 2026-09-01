from pathlib import Path

p=Path('index.html')
s=p.read_text()
road=Path('ROADMAP.md')
doc=Path('docs/ASYMMETRIC_RANK_PROTOTYPE.md')
r=road.read_text()
d=doc.read_text()

def function_span(text,name):
    marker=f'function {name}('
    start=text.find(marker)
    if start<0: raise SystemExit(f'missing function {name}')
    brace=text.find('{',start)
    if brace<0: raise SystemExit(f'missing body {name}')
    depth=0
    for i in range(brace,len(text)):
        if text[i]=='{': depth+=1
        elif text[i]=='}':
            depth-=1
            if depth==0: return start,i+1
    raise SystemExit(f'unterminated function {name}')

def replace_function(text,name,new_source):
    a,b=function_span(text,name)
    return text[:a]+new_source+text[b:]

css='''
/* M11B · experiment sample readiness / cohort comparison */
.m11bReadiness,.m11bCompare{margin-top:6px;padding:6px 7px;border:1px solid #46524f;background:#151b1d;color:#aeb9b4;font-size:6.5px;line-height:1.5;overflow-wrap:anywhere}.m11bReadiness{border-left:3px solid #777f7b}.m11bReadiness[data-state="ready"]{border-left-color:#6a9c91;color:#bfd9d2}.m11bReadiness[data-state="stable"]{border-left-color:#b39761;color:#e5d6b6}.m11bCompare b{color:#ead7ac}.m11bCompare .positive{color:#9fc9bd}.m11bCompare .negative{color:#d8aaa5}.m11bCompare .neutral{color:#aeb9b4}
@media(max-width:390px){.m11bReadiness,.m11bCompare{font-size:6.8px;line-height:1.55}}
'''
if '/* M11B · experiment sample readiness / cohort comparison */' not in s:
    if '</style>' not in s: raise SystemExit('style end missing')
    s=s.replace('</style>',css+'\n</style>',1)

old_html='<div id="m11bExperimentOverview" class="metricsOverview">기록 없음</div><div id="m11bExperimentList" class="metricsList">'
new_html='<div id="m11bExperimentReadiness" class="m11bReadiness" data-state="collecting">표본 준비도 · 코호트당 10판부터 1차 비교</div><div id="m11bExperimentOverview" class="metricsOverview">기록 없음</div><div id="m11bExperimentCompare" class="m11bCompare">0장 기준 표본이 쌓이면 4장/10장 차이를 표시합니다.</div><div id="m11bExperimentList" class="metricsList">'
if old_html in s:
    s=s.replace(old_html,new_html,1)
elif 'id="m11bExperimentReadiness"' not in s:
    raise SystemExit('experiment metrics HTML anchor missing')

key="const M11B_EXPERIMENT_KEY='rummyDuelM11BExperimentV1';"
constants="const M11B_EXPERIMENT_KEY='rummyDuelM11BExperimentV1';\nconst M11B_EXPERIMENT_MIN_SAMPLES=10;\nconst M11B_EXPERIMENT_STABLE_SAMPLES=20;"
if constants not in s:
    if key not in s: raise SystemExit('experiment storage key missing')
    s=s.replace(key,constants,1)

helpers='''
function m11bExperimentReadiness(history=m11bExperimentHistory()){const a=m11bExperimentAggregate(history),minimum=M11B_EXPERIMENT_MIN_SAMPLES,stable=M11B_EXPERIMENT_STABLE_SAMPLES,cohorts=Object.fromEntries(Object.keys(M11B_EXPERIMENT_COHORTS).map(id=>{const samples=a[id]?.samples||0,status=samples>=stable?'stable':samples>=minimum?'ready':'collecting';return[id,{samples,status,remaining:Math.max(0,minimum-samples),stableRemaining:Math.max(0,stable-samples)}]})),allReady=Object.values(cohorts).every(x=>x.samples>=minimum),allStable=Object.values(cohorts).every(x=>x.samples>=stable);return{minimum,stable,cohorts,allReady,allStable}}
function m11bExperimentReadinessText(history=m11bExperimentHistory()){const g=m11bExperimentReadiness(history),label=id=>{const c=m11bExperimentCohort(id),x=g.cohorts[id],stateLabel=x.status==='stable'?'안정권':x.status==='ready'?'비교 가능':`수집 중 · ${x.remaining}판 남음`;return`${c.label} ${x.samples}판 (${stateLabel})`},overall=g.allStable?'세 코호트 안정권':g.allReady?'1차 비교 가능':'표본 수집 중';return`표본 준비도 · ${label('zero')} · ${label('few')} · ${label('many')} · ${overall} · 기준 ${g.minimum}판 / 안정권 ${g.stable}판`}
function m11bExperimentComparison(history=m11bExperimentHistory()){const a=m11bExperimentAggregate(history),base=a.zero,delta=id=>{const x=a[id];if(!base?.samples||!x?.samples)return null;return{samples:x.samples,winRate:x.winRate-base.winRate,avgTurns:x.avgTurns-base.avgTurns,avgMaintenance:x.avgMaintenance-base.avgMaintenance,avgRummys:x.avgRummys-base.avgRummys,avgOpponentMeldUses:x.avgOpponentMeldUses-base.avgOpponentMeldUses,multiAttachPeak:x.multiAttachPeak-base.multiAttachPeak}};return{baseSamples:base?.samples||0,few:delta('few'),many:delta('many')}}
function m11bSigned(value,digits=1,suffix=''){const n=Number(value)||0,rounded=Math.abs(n)<Math.pow(10,-digits)/2?0:n;return`${rounded>0?'+':''}${rounded.toFixed(digits)}${suffix}`}
function m11bExperimentComparisonText(history=m11bExperimentHistory()){const cmp=m11bExperimentComparison(history),ready=m11bExperimentReadiness(history);if(!cmp.baseSamples)return'<b>0장 기준 표본 필요</b> · 기준 코호트가 1판 이상 있어야 차이를 계산합니다.';const line=(id,label)=>{const x=cmp[id];if(!x)return`<b>${label}</b> · 해당 코호트 표본 필요`;return`<b>${label} vs 0장</b> · 승률 ${m11bSigned(x.winRate,0,'%p')} · 턴 ${m11bSigned(x.avgTurns,1)} · 정비 ${m11bSigned(x.avgMaintenance,1)} · 러미 ${m11bSigned(x.avgRummys,1)} · 상대 조합 ${m11bSigned(x.avgOpponentMeldUses,1)} · 다중 최고 ${m11bSigned(x.multiAttachPeak,0)}장`};const gate=ready.allReady?' · <span class="positive">1차 비교 표본 충족</span>':' · <span class="neutral">아직 서술형 참고만</span>';return`${line('few','소수 4장')}<br>${line('many','스트레스 10장')}${gate}`}
'''
if 'function m11bExperimentReadiness(' not in s:
    a,b=function_span(s,'m11bExperimentAggregate')
    s=s[:b]+helpers+s[b:]

render='''function renderM11BExperimentHistory(){const history=m11bExperimentHistory(),count=document.getElementById('m11bExperimentCount'),readiness=document.getElementById('m11bExperimentReadiness'),overview=document.getElementById('m11bExperimentOverview'),compare=document.getElementById('m11bExperimentCompare'),list=document.getElementById('m11bExperimentList');if(count)count.textContent=`${history.length}판`;if(readiness){const gate=m11bExperimentReadiness(history);readiness.textContent=m11bExperimentReadinessText(history);readiness.dataset.state=gate.allStable?'stable':gate.allReady?'ready':'collecting'}if(overview)overview.innerHTML=m11bExperimentAggregateText(history);if(compare)compare.innerHTML=m11bExperimentComparisonText(history);if(list)list.innerHTML=history.length?history.slice(-8).reverse().map(x=>`<div class="metricsRow">${m11bExperimentRowText(x)}</div>`).join(''):'<div class="metricsEmpty">위의 0/4/10장 실험전을 끝내면 별도 기록이 쌓입니다.</div>';return history}'''
s=replace_function(s,'renderM11BExperimentHistory',render)

road_anchor='- [x] 개발자 전용 0/4/10장 실제 전투 샌드박스 + 분리 지표 기록 — 개발자 패널에서 동일 원본 29슬롯+광대왕 조커의 기준 0장 / 소수 4장 / 스트레스 10장 코호트를 시작하며 상대는 항상 0장 X/X 기준덱. 합성 X/Y는 `NAMED`/해금/자동 덱에 등록하지 않고 별도 `rummyDuelM11BExperimentV1` 기록에 턴·정비·러미·상대 조합·다중 붙이기·↑/↓ 사용값을 최대 60판 보존. DEV/실험전은 진행도와 M12 일반/연습 `rummyDuelBattleMetricsV1` 표본에서 제외하며 `newGame()` 전투 지표 초기화도 회귀 잠금'
road_item='- [x] M11B 실험 표본 준비도 / 0장 대비 코호트 차이 패널 — 개발자 패널에서 0/4/10장 각각 10판을 `1차 비교 가능`, 20판을 `안정권`으로 표시하고, 0장 기준 대비 4장/10장의 승률·평균 턴·정비·러미·상대 공개 조합 사용·최대 다중붙이기 차이를 자동 요약. 이 기준은 데이터 수집 준비도일 뿐 통계적 유의성·밸런스 합격 판정이 아니며 최종 M11B/M12 밸런스 항목은 계속 미완료로 유지'
if road_item not in r:
    if road_anchor not in r: raise SystemExit('roadmap sandbox anchor missing')
    r=r.replace(road_anchor,road_anchor+'\n'+road_item,1)

append='''

### 표본 준비도 / 0장 대비 비교 패널

- 개발자 패널은 각 코호트의 누적 표본을 `기준 0장 / 소수 4장 / 스트레스 10장`으로 따로 센다.
- **코호트당 10판**은 `1차 비교 가능`, **20판**은 `안정권`으로 표시한다. 이 숫자는 통계적 유의성이나 밸런스 합격선이 아니라, 너무 적은 표본으로 성급하게 결론내리지 않기 위한 작업 준비도다.
- 0장 기준 표본이 1판 이상 있으면 4장/10장 코호트의 `승률(%p) / 평균 턴 / 플레이어 정비 / 플레이어 러미 / 상대 공개 조합 이용 / 최대 다중붙이기` 차이를 자동 계산한다.
- 세 코호트 모두 10판 미만이면 비교값은 **서술형 참고**로만 표시한다. 세 코호트 모두 10판 이상일 때만 UI가 `1차 비교 표본 충족`을 표시한다.
- 20판 안정권도 자동 승격 조건이 아니다. 비대칭 정식 승격은 아래의 실제 밸런스 항목과 M12 일반 플레이 표본을 함께 본 뒤 별도로 결정한다.
'''
if '### 표본 준비도 / 0장 대비 비교 패널' not in d:
    d=d.rstrip()+append+'\n'

p.write_text(s)
road.write_text(r)
doc.write_text(d)
print('M11B experiment readiness patch installed')

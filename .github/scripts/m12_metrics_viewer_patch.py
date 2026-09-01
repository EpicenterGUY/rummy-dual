from pathlib import Path

index=Path('index.html')
road=Path('ROADMAP.md')
s=index.read_text()
r=road.read_text()

marker='/* M12 · battle metrics review panel */'
if marker in s:
    raise SystemExit('M12 metrics viewer already installed')

css_anchor='.developerActions .wide{grid-column:1/-1}.devModeActive{box-shadow:0 0 0 2px var(--gold) inset!important;color:#f2d78f}'
css_new='''.developerActions .wide{grid-column:1/-1}
/* M12 · battle metrics review panel */
.metricsPanel{margin-top:8px;padding:8px;border:1px solid #415159;background:#121a1e}.metricsHead{display:flex;align-items:center;justify-content:space-between;gap:7px;font-size:8px;font-weight:900;color:#dce6e2}.metricsHead span:last-child{color:#c6aa70}.metricsOverview{margin-top:6px;padding:6px;border:1px solid #334249;background:#0e1519;color:#cbd6d2;font-size:7px;line-height:1.5}.metricsList{display:flex;flex-direction:column;gap:4px;margin-top:6px;max-height:150px;overflow:auto}.metricsRow{padding:5px 6px;border:1px solid #2d3a40;background:#10171b;font-size:7px;line-height:1.45;color:#bfcac7}.metricsRow b{color:#e6e9e4}.metricsRow .win{color:#93c8b2}.metricsRow .loss{color:#d89b9b}.metricsRow .draw{color:#c8b37a}.metricsEmpty{padding:7px;border:1px dashed #46545a;color:#879792;font-size:7px;text-align:center}.metricsActions{display:grid;grid-template-columns:1fr 1fr;gap:5px;margin-top:6px}.metricsActions .pixelBtn{font-size:7px;padding:5px}.devModeActive{box-shadow:0 0 0 2px var(--gold) inset!important;color:#f2d78f}'''
if s.count(css_anchor)!=1:
    raise SystemExit(f'CSS anchor mismatch: {s.count(css_anchor)}')
s=s.replace(css_anchor,css_new,1)

html_anchor='<button id="developerBattleBtn" class="pixelBtn primary wide" type="button" disabled>DEV 새 대전</button></div></div></div>'
html_new='''<button id="developerBattleBtn" class="pixelBtn primary wide" type="button" disabled>DEV 새 대전</button></div><div class="metricsPanel"><div class="metricsHead"><span>밸런스 전투 기록</span><span id="battleMetricsCount">0판</span></div><div id="battleMetricsOverview" class="metricsOverview">기록 없음</div><div id="battleMetricsList" class="metricsList"><div class="metricsEmpty">일반전/연습전을 끝내면 최근 50판이 여기에 쌓입니다.</div></div><div class="metricsActions"><button id="battleMetricsCopyBtn" class="pixelBtn" type="button">JSON 복사</button><button id="battleMetricsClearBtn" class="pixelBtn redBtn" type="button">기록 지우기</button></div></div></div></div>'''
if s.count(html_anchor)!=1:
    raise SystemExit(f'HTML anchor mismatch: {s.count(html_anchor)}')
s=s.replace(html_anchor,html_new,1)

old_snapshot="function battleMetricsSnapshot(outcome='result'){const st=getBattleMetrics();return{version:1,mode:state.sessionMode||'battle',outcome,turns:st.turns,bursts:st.bursts.map(x=>({...x})),chains:st.chains.map(x=>({...x})),detonates:st.detonates.map(x=>({...x})),rummys:st.rummys.map(x=>({...x})),maintenance:st.maintenance.map(x=>({...x})),maxPower:st.maxPower,opponentMeldUses:st.opponentMeldUses,opponentMeldCards:st.opponentMeldCards,multiAttachActions:st.multiAttachActions,multiAttachMax:st.multiAttachMax,intentionalBombAccepts:st.intentionalBombAccepts.map(x=>({...x}))}}"
new_snapshot="function battleMetricsSnapshot(outcome='result'){const st=getBattleMetrics();return{version:1,savedAt:Date.now(),mode:state.sessionMode||'battle',outcome,playerChar:state.player?.charId||null,playerTheme:state.player?.themeId||null,fieldTag:state.field?.tag||null,fieldName:state.field?.name||null,turns:st.turns,bursts:st.bursts.map(x=>({...x})),chains:st.chains.map(x=>({...x})),detonates:st.detonates.map(x=>({...x})),rummys:st.rummys.map(x=>({...x})),maintenance:st.maintenance.map(x=>({...x})),maxPower:st.maxPower,opponentMeldUses:st.opponentMeldUses,opponentMeldCards:st.opponentMeldCards,multiAttachActions:st.multiAttachActions,multiAttachMax:st.multiAttachMax,intentionalBombAccepts:st.intentionalBombAccepts.map(x=>({...x}))}}"
if s.count(old_snapshot)!=1:
    raise SystemExit(f'snapshot anchor mismatch: {s.count(old_snapshot)}')
s=s.replace(old_snapshot,new_snapshot,1)

history_anchor="function battleMetricsHistory(){if(typeof localStorage==='undefined')return[];try{const v=JSON.parse(localStorage.getItem(BATTLE_METRICS_KEY)||'[]');return Array.isArray(v)?v:[]}catch{return[]}}\nfunction saveBattleMetrics"
viewer_funcs="""function battleMetricsHistory(){if(typeof localStorage==='undefined')return[];try{const v=JSON.parse(localStorage.getItem(BATTLE_METRICS_KEY)||'[]');return Array.isArray(v)?v:[]}catch{return[]}}
function battleMetricsAggregate(history=battleMetricsHistory()){const rows=(Array.isArray(history)?history:[]).filter(Boolean),battle=rows.filter(x=>x.mode==='battle'),practice=rows.filter(x=>x.mode==='practice'),avg=(fn,list=rows)=>list.length?list.reduce((a,x)=>a+(Number(fn(x))||0),0)/list.length:0,sum=(fn,list=rows)=>list.reduce((a,x)=>a+(Number(fn(x))||0),0),peak=(fn,list=rows)=>list.reduce((m,x)=>Math.max(m,Number(fn(x))||0),0),wins=battle.filter(x=>x.outcome==='win').length,losses=battle.filter(x=>x.outcome==='loss').length,draws=battle.filter(x=>x.outcome==='draw').length;return{samples:rows.length,battle:battle.length,practice:practice.length,wins,losses,draws,winRate:battle.length?Math.round(wins/battle.length*100):0,avgTurns:avg(x=>x.turns),avgMaxPower:avg(x=>x.maxPower),peakPower:peak(x=>x.maxPower),avgBursts:avg(x=>x.bursts?.length||0),avgChains:avg(x=>x.chains?.length||0),avgDetonates:avg(x=>x.detonates?.length||0),avgOpponentMeldUses:avg(x=>x.opponentMeldUses),multiAttachPeak:peak(x=>x.multiAttachMax),avgRummys:avg(x=>x.rummys?.length||0),avgMaintenance:avg(x=>x.maintenance?.length||0),bombAccepts:sum(x=>x.intentionalBombAccepts?.length||0)}}
function metricAvg(n){return Number.isFinite(n)?n.toFixed(1):'0.0'}
function battleMetricsAggregateText(history=battleMetricsHistory()){const a=battleMetricsAggregate(history);if(!a.samples)return'아직 저장된 전투 표본이 없습니다.';return `표본 ${a.samples}판 · 일반 ${a.battle} / 연습 ${a.practice} · 일반전 승 ${a.wins} 패 ${a.losses} 무 ${a.draws} · 승률 ${a.winRate}%<br>평균 턴 ${metricAvg(a.avgTurns)} · 평균 최대 위력 ${metricAvg(a.avgMaxPower)} / 최고 ${a.peakPower} · 버스트 ${metricAvg(a.avgBursts)} · 체인 ${metricAvg(a.avgChains)} · 폭발 ${metricAvg(a.avgDetonates)}<br>상대 조합 사용 ${metricAvg(a.avgOpponentMeldUses)}회 · 다중붙이기 최고 ${a.multiAttachPeak||1}장 · 러미 ${metricAvg(a.avgRummys)} · 정비 ${metricAvg(a.avgMaintenance)} · 소폭탄 수용 총 ${a.bombAccepts}회`}
function battleMetricRowText(row){const result=row.outcome==='win'?'승':row.outcome==='loss'?'패':'무',mode=row.mode==='practice'?'연습':'일반',stamp=row.savedAt?new Date(row.savedAt).toLocaleString('ko-KR',{month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit'}):'이전 기록',theme=row.playerTheme&&row.playerTheme!=='mixed'?` · ${row.playerTheme}`:'',field=row.fieldName?` · ${row.fieldName}`:'';return`<b>${mode} · <span class="${row.outcome==='win'?'win':row.outcome==='loss'?'loss':'draw'}">${result}</span></b> · ${stamp}${theme}${field}<br>턴 ${row.turns||0} · 최대 ${row.maxPower||0} · 버스트 ${row.bursts?.length||0} · 체인 ${row.chains?.length||0} · 폭발 ${row.detonates?.length||0} · 상대 조합 ${row.opponentMeldUses||0} · 다중 ${row.multiAttachMax||1} · 러미 ${row.rummys?.length||0} · 정비 ${row.maintenance?.length||0}`}
function renderBattleMetricsHistory(){const history=battleMetricsHistory(),count=document.getElementById('battleMetricsCount'),overview=document.getElementById('battleMetricsOverview'),list=document.getElementById('battleMetricsList');if(count)count.textContent=`${history.length}판`;if(overview)overview.innerHTML=battleMetricsAggregateText(history);if(list)list.innerHTML=history.length?history.slice(-8).reverse().map(x=>`<div class="metricsRow">${battleMetricRowText(x)}</div>`).join(''):'<div class="metricsEmpty">일반전/연습전을 끝내면 최근 50판이 여기에 쌓입니다.</div>';return history}
async function copyBattleMetricsHistory(){const history=battleMetricsHistory(),text=JSON.stringify(history,null,2);if(typeof navigator!=='undefined'&&navigator.clipboard?.writeText){try{await navigator.clipboard.writeText(text);return true}catch{}}return false}
function clearBattleMetricsHistory(){if(typeof localStorage==='undefined')return false;try{localStorage.removeItem(BATTLE_METRICS_KEY);if(typeof renderBattleMetricsHistory==='function')renderBattleMetricsHistory();return true}catch{return false}}
function saveBattleMetrics"""
if s.count(history_anchor)!=1:
    raise SystemExit(f'history anchor mismatch: {s.count(history_anchor)}')
s=s.replace(history_anchor,viewer_funcs,1)

old_render="function renderDeveloperPanel(){const on=developerModeActive(),status=document.getElementById('developerStatus'),toggle=document.getElementById('developerToggleBtn'),battle=document.getElementById('developerBattleBtn'),main=document.getElementById('developerBtn'),hud=document.getElementById('developerHudBtn');if(status){status.textContent=on?'DEV · ON · 해금 제한 우회':'DEV · OFF · 일반 진행';status.classList.toggle('on',on)}if(toggle){toggle.textContent=on?'개발자 모드 끄기':'개발자 모드 켜기';toggle.classList.toggle('redBtn',on);toggle.classList.toggle('goldBtn',!on)}if(battle)battle.disabled=!on;if(main){main.textContent=on?'개발자 모드 · ON':'개발자 모드 · OFF';main.classList.toggle('devModeActive',on)}if(hud){hud.textContent=on?'개발 · ON':'개발';hud.classList.toggle('devModeActive',on)}}"
new_render="function renderDeveloperPanel(){const on=developerModeActive(),status=document.getElementById('developerStatus'),toggle=document.getElementById('developerToggleBtn'),battle=document.getElementById('developerBattleBtn'),main=document.getElementById('developerBtn'),hud=document.getElementById('developerHudBtn');if(status){status.textContent=on?'DEV · ON · 해금 제한 우회':'DEV · OFF · 일반 진행';status.classList.toggle('on',on)}if(toggle){toggle.textContent=on?'개발자 모드 끄기':'개발자 모드 켜기';toggle.classList.toggle('redBtn',on);toggle.classList.toggle('goldBtn',!on)}if(battle)battle.disabled=!on;if(main){main.textContent=on?'개발자 모드 · ON':'개발자 모드 · OFF';main.classList.toggle('devModeActive',on)}if(hud){hud.textContent=on?'개발 · ON':'개발';hud.classList.toggle('devModeActive',on)}if(typeof renderBattleMetricsHistory==='function')renderBattleMetricsHistory()}"
if s.count(old_render)!=1:
    raise SystemExit(f'developer render anchor mismatch: {s.count(old_render)}')
s=s.replace(old_render,new_render,1)

event_anchor="document.getElementById('developerBattleBtn').onclick=()=>{if(!developerModeActive())return;document.getElementById('developerOverlay').classList.remove('show');startBattle()};"
event_new=event_anchor+"document.getElementById('battleMetricsCopyBtn').onclick=async()=>{const ok=typeof copyBattleMetricsHistory==='function'&&await copyBattleMetricsHistory();const b=document.getElementById('battleMetricsCopyBtn');if(b){const old=b.textContent;b.textContent=ok?'복사 완료':'복사 실패';setTimeout(()=>b.textContent=old,900)}};document.getElementById('battleMetricsClearBtn').onclick=()=>{if(confirm('저장된 전투 지표 기록을 모두 지울까요?'))clearBattleMetricsHistory()};"
if s.count(event_anchor)!=1:
    raise SystemExit(f'event anchor mismatch: {s.count(event_anchor)}')
s=s.replace(event_anchor,event_new,1)

road_anchor="- [x] Track turn count, BURST/CHAIN/DETONATE timing, max power, opponent-meld use, multi-attach size, RUMMY, maintenance and intentional bomb acceptance — 전투별 구조화 이벤트를 수집해 결과 요약에 표시하고 일반/연습 전투 최근 50판을 `rummyDuelBattleMetricsV1` 로컬 기록으로 보존. 튜토리얼/DEV 전투는 밸런스 표본에서 제외\n- [ ] Balance from playtest data before large content expansion"
road_new=road_anchor.split('\n')[0]+"\n- [x] Review/export local playtest metrics — 개발자 패널에서 최근 50판의 일반/연습 표본 수, 일반전 승률, 평균 턴·최대 위력·버스트·체인·폭발·상대 조합 사용·러미·정비와 다중붙이기/소폭탄 수용을 즉시 요약하고 최근 8판 상세·JSON 복사·기록 초기화를 지원\n- [ ] Balance from playtest data before large content expansion"
if r.count(road_anchor)!=1:
    raise SystemExit(f'ROADMAP metrics anchor mismatch: {r.count(road_anchor)}')
r=r.replace(road_anchor,road_new,1)

index.write_text(s)
road.write_text(r)
print('M12 metrics viewer installed')

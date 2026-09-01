from pathlib import Path

index=Path('index.html')
road=Path('ROADMAP.md')
s=index.read_text()
r=road.read_text()

marker='const BATTLE_METRICS_KEY=' 
if marker in s:
    raise SystemExit('M12 battle metrics already installed')

old="function circulationSummaryText(){const st=getCirculationStats(),avg=st.handSamples?(st.handTotal/st.handSamples).toFixed(1):'-',low2=st.turns?Math.round(st.low2/st.turns*100):0;return `패순환 · 평균 손패 ${avg}장 · 2장 이하 ${low2}% · 저손패 보호 ${st.lowSkips}회 · 러미 ${st.rummys}회 · 정비 ${st.maintenance}회 · 전체 재순환 ${st.fullRecirculations}회`}\nfunction renderCirculationSummary(){const el=document.getElementById('circulationSummary');if(el)el.textContent=circulationSummaryText()}"
new="""function circulationSummaryText(){const st=getCirculationStats(),avg=st.handSamples?(st.handTotal/st.handSamples).toFixed(1):'-',low2=st.turns?Math.round(st.low2/st.turns*100):0;return `패순환 · 평균 손패 ${avg}장 · 2장 이하 ${low2}% · 저손패 보호 ${st.lowSkips}회 · 러미 ${st.rummys}회 · 정비 ${st.maintenance}회 · 전체 재순환 ${st.fullRecirculations}회`}
const BATTLE_METRICS_KEY='rummyDuelBattleMetricsV1';
function getBattleMetrics(){return state.battleMetrics||(state.battleMetrics={turns:0,bursts:[],chains:[],detonates:[],rummys:[],maintenance:[],maxPower:Math.max(0,state.switchPower||0),opponentMeldUses:0,opponentMeldCards:0,multiAttachActions:0,multiAttachMax:0,intentionalBombAccepts:[],lastAcceptTurnToken:null,saved:false})}
function battleMetricTurn(){return getBattleMetrics().turns+1}
function recordBattleTurn(w){const st=getBattleMetrics();st.turns++;return st.turns}
function recordMeldActionMetric(w,type,count,targetSide,opts={}){const st=getBattleMetrics(),n=Math.max(1,Math.round(count||1)),evt={turn:battleMetricTurn(),actor:w,cards:n,targetSide,continuation:!!opts.continuation};if(type==='SET')st.bursts.push(evt);else if(type==='RUN')st.chains.push(evt);if(targetSide===other(w)){st.opponentMeldUses++;st.opponentMeldCards+=n}if(n>1){st.multiAttachActions++;st.multiAttachMax=Math.max(st.multiAttachMax,n)}return evt}
function recordDetonateMetric(w,power,dealt){const st=getBattleMetrics(),evt={turn:battleMetricTurn(),target:w,power:Math.max(0,Math.round(power||0)),dealt:Math.max(0,Math.round(dealt||0))};st.detonates.push(evt);return evt}
function recordRummyMetric(w){const st=getBattleMetrics(),evt={turn:battleMetricTurn(),actor:w};st.rummys.push(evt);return evt}
function recordMaintenanceMetric(w,count){const st=getBattleMetrics(),evt={turn:battleMetricTurn(),actor:w,cards:Math.max(1,Math.round(count||1))};st.maintenance.push(evt);return evt}
function recordIntentionalBombAcceptance(w,power,returnGain=0){const st=getBattleMetrics();if(st.lastAcceptTurnToken===state.turnToken)return null;st.lastAcceptTurnToken=state.turnToken;const evt={turn:battleMetricTurn(),actor:w,power:Math.max(0,Math.round(power||0)),declinedReturnGain:Math.max(0,Math.round(returnGain||0))};st.intentionalBombAccepts.push(evt);return evt}
function battleMetricTurns(list){return list.length?list.map(x=>x.turn).join('/'):'-'}
function battleMetricsSummaryText(){const st=getBattleMetrics();return `전투지표 · 턴 ${st.turns} · 버스트 ${st.bursts.length}회@${battleMetricTurns(st.bursts)} · 체인 ${st.chains.length}회@${battleMetricTurns(st.chains)} · 폭발 ${st.detonates.length}회@${battleMetricTurns(st.detonates)} · 최대 위력 ${st.maxPower} · 상대 조합 ${st.opponentMeldUses}회 · 최대 다중붙이기 ${st.multiAttachMax||1}장 · 소폭탄 수용 ${st.intentionalBombAccepts.length}회`}
function battleMetricsSnapshot(outcome='result'){const st=getBattleMetrics();return{version:1,mode:state.sessionMode||'battle',outcome,turns:st.turns,bursts:st.bursts.map(x=>({...x})),chains:st.chains.map(x=>({...x})),detonates:st.detonates.map(x=>({...x})),rummys:st.rummys.map(x=>({...x})),maintenance:st.maintenance.map(x=>({...x})),maxPower:st.maxPower,opponentMeldUses:st.opponentMeldUses,opponentMeldCards:st.opponentMeldCards,multiAttachActions:st.multiAttachActions,multiAttachMax:st.multiAttachMax,intentionalBombAccepts:st.intentionalBombAccepts.map(x=>({...x}))}}
function battleMetricsHistory(){if(typeof localStorage==='undefined')return[];try{const v=JSON.parse(localStorage.getItem(BATTLE_METRICS_KEY)||'[]');return Array.isArray(v)?v:[]}catch{return[]}}
function saveBattleMetrics(outcome='result'){const st=getBattleMetrics();if(st.saved||state.sessionMode==='tutorial'||state.developerBattle)return false;st.saved=true;if(typeof localStorage==='undefined')return false;try{const history=battleMetricsHistory();history.push(battleMetricsSnapshot(outcome));localStorage.setItem(BATTLE_METRICS_KEY,JSON.stringify(history.slice(-50)));return true}catch{return false}}
function renderCirculationSummary(){const el=document.getElementById('circulationSummary');if(el)el.textContent=circulationSummaryText()+(typeof battleMetricsSummaryText==='function'?` · ${battleMetricsSummaryText()}`:'')}"""
if s.count(old)!=1:
    raise SystemExit(f'circulation summary anchor mismatch: {s.count(old)}')
s=s.replace(old,new,1)

repls=[
("state.switchPower+=amount;state.lastSwitchAdd=amount;","state.switchPower+=amount;if(typeof getBattleMetrics==='function'){const bm=getBattleMetrics();bm.maxPower=Math.max(bm.maxPower,state.switchPower)}state.lastSwitchAdd=amount;"),
("m.cards.push(...cards);\n  if(willBaseReturn", "m.cards.push(...cards);\n  if(typeof recordMeldActionMetric==='function')recordMeldActionMetric(w,type,cards.length,targetSide,{continuation});\n  if(willBaseReturn"),
("if(typeof getCirculationStats==='function')getCirculationStats().rummys++;if(lastCards.some", "if(typeof getCirculationStats==='function')getCirculationStats().rummys++;if(typeof recordRummyMetric==='function')recordRummyMetric(w);if(lastCards.some"),
("if(typeof getCirculationStats==='function')getCirculationStats().maintenance++;log(`", "if(typeof getCirculationStats==='function')getCirculationStats().maintenance++;if(typeof recordMaintenanceMetric==='function')recordMaintenanceMetric(w,valid.length);log(`"),
("const total=state.switchPower;combatBanner(`폭발 ${total}`,'break',0);const dealt=damage(w,raw,{label:'폭발',detonate:true});s.lastDetonateTaken=dealt;", "const total=state.switchPower;combatBanner(`폭발 ${total}`,'break',0);const dealt=damage(w,raw,{label:'폭발',detonate:true});if(typeof recordDetonateMetric==='function')recordDetonateMetric(w,total,dealt);s.lastDetonateTaken=dealt;"),
("const actionCap=state.sessionMode==='practice'?2:4;let actions=Math.max(0,resumeState.actionsUsed||0),rummied=!!resumeState.rummied;while(actions++<actionCap&&!state.gameOver&&!rummied){const ex=bestExtension('enemy'),nm=state.enemy.melds.length<2?bestNewMeldForTurn('enemy'):null,rc=bestRecoverAI('enemy'),fr=bestFinishRunAI('enemy');const switchUrgent=state.switchTarget==='enemy'&&state.switchPower>0,acceptSmall=typeof aiShouldAcceptSmallBomb==='function'?aiShouldAcceptSmallBomb('enemy',ex):false;", "const actionCap=state.sessionMode==='practice'?2:4;let actions=Math.max(0,resumeState.actionsUsed||0),rummied=!!resumeState.rummied;while(actions++<actionCap&&!state.gameOver&&!rummied){const ex=bestExtension('enemy'),nm=state.enemy.melds.length<2?bestNewMeldForTurn('enemy'):null,rc=bestRecoverAI('enemy'),fr=bestFinishRunAI('enemy');const switchUrgent=state.switchTarget==='enemy'&&state.switchPower>0,acceptSmall=typeof aiShouldAcceptSmallBomb==='function'?aiShouldAcceptSmallBomb('enemy',ex):false;if(acceptSmall&&typeof recordIntentionalBombAcceptance==='function')recordIntentionalBombAcceptance('enemy',state.switchPower,ex?.score||0);"),
("function turnEnd(w){if(typeof advanceHandPreparation==='function')advanceHandPreparation(w);if(typeof expirePointBlankClashAtTurnEnd==='function')expirePointBlankClashAtTurnEnd(w);if(typeof recordCirculationTurn==='function')recordCirculationTurn(w);const s=sideObj(w);", "function turnEnd(w){if(typeof advanceHandPreparation==='function')advanceHandPreparation(w);if(typeof expirePointBlankClashAtTurnEnd==='function')expirePointBlankClashAtTurnEnd(w);if(typeof recordCirculationTurn==='function')recordCirculationTurn(w);const s=sideObj(w);"),
("s.jokerLastDetonateReduction=0;s.lastDamageTaken=0}\nfunction rectSnapshot", "s.jokerLastDetonateReduction=0;s.lastDamageTaken=0;if(typeof recordBattleTurn==='function')recordBattleTurn(w)}\nfunction rectSnapshot"),
("function showCirculationDraw(){if(typeof renderCirculationSummary==='function')renderCirculationSummary();const title=", "function showCirculationDraw(){if(typeof renderCirculationSummary==='function')renderCirculationSummary();if(typeof saveBattleMetrics==='function')saveBattleMetrics('draw');const title="),
("function showResult(win){if(typeof renderCirculationSummary==='function')renderCirculationSummary();const practice=", "function showResult(win){if(typeof renderCirculationSummary==='function')renderCirculationSummary();if(typeof saveBattleMetrics==='function')saveBattleMetrics(win?'win':'loss');const practice=")
]
for old_s,new_s in repls:
    if old_s==new_s:
        continue
    if s.count(old_s)!=1:
        raise SystemExit(f'hook mismatch ({old_s[:70]!r}): {s.count(old_s)}')
    s=s.replace(old_s,new_s,1)

old_road='- [ ] Track turn count, BURST/CHAIN/DETONATE timing, max power, opponent-meld use, multi-attach size, RUMMY, maintenance and intentional bomb acceptance'
new_road='- [x] Track turn count, BURST/CHAIN/DETONATE timing, max power, opponent-meld use, multi-attach size, RUMMY, maintenance and intentional bomb acceptance — 전투별 구조화 이벤트를 수집해 결과 요약에 표시하고 일반/연습 전투 최근 50판을 `rummyDuelBattleMetricsV1` 로컬 기록으로 보존. 튜토리얼/DEV 전투는 밸런스 표본에서 제외'
if r.count(old_road)!=1:
    raise SystemExit(f'M12 roadmap anchor mismatch: {r.count(old_road)}')
r=r.replace(old_road,new_road,1)

old_next="""## Current next work
1. UX1 P1: deterministic 기본 조작 → 세트 → 런 → 붙이기 → 상대 공개 조합 → 스위치 lessons are live; next connect 러미, then move into P2 누적 위력 / 폭발 tutorial.
2. UI2 P2: finish the 360–480px real-device visual check, then defer P3 art/brand polish until gameplay/tutorial UX is steadier.
3. L10N1 + M8: continue remaining text cleanup and named-card choice/copy/timing audit in parallel; do not begin large M9/content expansion until the first ~50 named-card behaviors and UX1 P1 are both stable."""
new_next="""## Current next work
1. UI2 P2: finish the remaining 360–480px live-browser / real-device visual check; static fallbacks and desktop/tablet/P3 visual audits are already locked.
2. M12: collect real playtest samples from the new per-battle metrics history and balance from data before large content expansion.
3. M11A/M11B: keep roguelike progression and asymmetric top/bottom-rank cards in prototype/design validation until M12 evidence supports promotion; defer M13 file splitting until rules/tests remain stable through those experiments."""
if old_next in r:
    r=r.replace(old_next,new_next,1)

index.write_text(s)
road.write_text(r)
print('M12 battle metrics tracking installed')

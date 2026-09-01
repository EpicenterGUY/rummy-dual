from pathlib import Path

p=Path('index.html')
s=p.read_text()
road=Path('ROADMAP.md')
doc=Path('docs/ASYMMETRIC_RANK_PROTOTYPE.md')

def replace_once(text,old,new,label):
    if old in text:return text.replace(old,new,1)
    if new in text:return text
    raise SystemExit(f'missing anchor: {label}')

def function_span(text,name):
    marker=f'function {name}('
    start=text.find(marker)
    if start<0:raise SystemExit(f'missing function {name}')
    brace=text.find('{',start)
    if brace<0:raise SystemExit(f'missing body {name}')
    depth=0
    i=brace
    while i<len(text):
        if text[i]=='{':depth+=1
        elif text[i]=='}':
            depth-=1
            if depth==0:return start,i+1
        i+=1
    raise SystemExit(f'unterminated function {name}')

def edit_function(text,name,editor):
    a,b=function_span(text,name)
    old=text[a:b]
    new=editor(old)
    if new==old:return text
    return text[:a]+new+text[b:]

css='''
/* M11B · developer-only asymmetric battle sandbox */
.rankExperimentActions{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:5px;margin-top:7px}.rankExperimentActions .pixelBtn{min-width:0;padding:5px 4px;font-size:6px;line-height:1.3;white-space:normal}.rankExperimentNote{margin-top:5px;padding-top:5px;border-top:1px solid #46524f;color:#9faaa6;font-size:6px;line-height:1.45}.m11bMetricsPanel{border-left:3px solid #9b8051}.m11bMetricsPanel .metricsHead span:first-child{color:#ead7ac}
@media(max-width:390px){.rankExperimentActions{grid-template-columns:1fr}.rankExperimentActions .pixelBtn{min-height:34px;font-size:6.5px}}
'''
if '/* M11B · developer-only asymmetric battle sandbox */' not in s:
    s=s.replace('</style>',css+'\n</style>',1)

old_html='''<div id="rankPrototypeCards" class="rankPrototypeCards"></div></div><div class="metricsPanel"><div class="metricsHead"><span>밸런스 전투 기록</span>'''
new_html='''<div id="rankPrototypeCards" class="rankPrototypeCards"></div><div class="rankExperimentActions" aria-label="M11B 비대칭 실험전 코호트"><button class="pixelBtn" data-m11b-experiment="zero" type="button" disabled>기준전 · 0장</button><button class="pixelBtn primary" data-m11b-experiment="few" type="button" disabled>소수 · 4장</button><button class="pixelBtn" data-m11b-experiment="many" type="button" disabled>스트레스 · 10장</button></div><div class="rankExperimentNote">DEV 전용 · 동일한 원본 29슬롯 + 광대왕 조커를 쓰고 플레이어 쪽 비대칭 밀도만 바꿉니다. 상대는 항상 0장 기준덱입니다. 결과는 일반 진행도와 M12 일반/연습 기록에 섞이지 않습니다.</div></div><div class="metricsPanel m11bMetricsPanel"><div class="metricsHead"><span>M11B 비대칭 실험 기록</span><span id="m11bExperimentCount">0판</span></div><div id="m11bExperimentOverview" class="metricsOverview">기록 없음</div><div id="m11bExperimentList" class="metricsList"><div class="metricsEmpty">위의 0/4/10장 실험전을 끝내면 별도 기록이 쌓입니다.</div></div><div class="metricsActions"><button id="m11bExperimentCopyBtn" class="pixelBtn" type="button">실험 JSON 복사</button><button id="m11bExperimentClearBtn" class="pixelBtn redBtn" type="button">실험 기록 지우기</button></div></div><div class="metricsPanel"><div class="metricsHead"><span>밸런스 전투 기록</span>'''
s=replace_once(s,old_html,new_html,'developer experiment HTML')

old_state="developerBattle:false,tutorialThemeId:null"
new_state="developerBattle:false,m11bExperimentBattle:false,m11bExperimentCohort:null,m11bExperimentStats:null,battleMetrics:null,tutorialThemeId:null"
s=replace_once(s,old_state,new_state,'state experiment fields')

constants="""const M11B_EXPERIMENT_KEY='rummyDuelM11BExperimentV1';
const M11B_EXPERIMENT_SPECS=Object.freeze({H4:Object.freeze(['4','6']),S5:Object.freeze(['5','8']),D4:Object.freeze(['4','9']),C5:Object.freeze(['5','K']),D6:Object.freeze(['6','8']),C3:Object.freeze(['3','6']),H7:Object.freeze(['7','10']),C6:Object.freeze(['6','J']),S8:Object.freeze(['8','K']),D3:Object.freeze(['3','Q'])});
const M11B_EXPERIMENT_COHORTS=Object.freeze({zero:Object.freeze({id:'zero',label:'기준 0장',slots:Object.freeze([])}),few:Object.freeze({id:'few',label:'소수 4장',slots:Object.freeze(['H4','S5','D4','C5'])}),many:Object.freeze({id:'many',label:'스트레스 10장',slots:Object.freeze(Object.keys(M11B_EXPERIMENT_SPECS))})});
function m11bExperimentCohort(id){return M11B_EXPERIMENT_COHORTS[id]||M11B_EXPERIMENT_COHORTS.few}
function getM11BExperimentStats(){return state.m11bExperimentStats||(state.m11bExperimentStats={top:0,bottom:0,choices:[]})}
function recordM11BRankChoices(cards,plan){if(!state.m11bExperimentBattle)return 0;const list=Array.isArray(cards)?cards:[],normalized=typeof normalizeRequestedRankPlan==='function'?normalizeRequestedRankPlan(list,plan):plan;if(!Array.isArray(normalized))return 0;const st=getM11BExperimentStats();let n=0;for(let i=0;i<list.length;i++){const c=list[i],x=normalized[i];if(!c?.m11bSynthetic||!isAsymmetricRankCard(c)||!x?.orientation)continue;const orientation=x.orientation==='bottom'?'bottom':'top';st[orientation]++;st.choices.push({turn:typeof battleMetricTurn==='function'?battleMetricTurn():state.turnNo,slot:c.m11bSyntheticSlot||c.slot,topRank:c.topRank,bottomRank:c.bottomRank,rank:x.rank,orientation});n++}return n}
function makeM11BExperimentDeck(owner,cohortId='few'){const cohort=m11bExperimentCohort(cohortId),active=new Set(cohort.slots),cards=CORE_IDS.slice(0,29).map(slot=>{const suit=slot[0],rank=slot.slice(1),c=makeCard(suit,rank,false,owner),pair=active.has(slot)?M11B_EXPERIMENT_SPECS[slot]:null;if(pair){c.topRank=pair[0];c.bottomRank=pair[1];c.baseRank=rank;c.rank=rank;c.activeRank=null;c.rankOrientation=null;c.m11bSynthetic=true;c.m11bSyntheticSlot=slot;c.name=`M11B ${pair[0]}/${pair[1]}`;c.effect='개발자 비대칭 실험용 합성 카드. 별도 고유 효과 없이 사용값 유연성만 측정한다.'}return c});cards.push(makeCard('J','J1',true,owner,'J1'));return shuffle(cards)}
function m11bExperimentHistory(){if(typeof localStorage==='undefined')return[];try{const v=JSON.parse(localStorage.getItem(M11B_EXPERIMENT_KEY)||'[]');return Array.isArray(v)?v:[]}catch{return[]}}
function m11bExperimentSnapshot(outcome='result'){const base=battleMetricsSnapshot(outcome),cohort=m11bExperimentCohort(state.m11bExperimentCohort),st=getM11BExperimentStats();return{...base,version:1,mode:'m11b-experiment',cohort:cohort.id,cohortLabel:cohort.label,asymmetricCards:cohort.slots.length,syntheticSlots:[...cohort.slots],rankChoiceTop:st.top,rankChoiceBottom:st.bottom,rankChoices:st.choices.map(x=>({...x}))}}
function saveM11BExperimentMetrics(outcome='result'){if(!state.m11bExperimentBattle||typeof localStorage==='undefined')return false;try{const history=m11bExperimentHistory();history.push(m11bExperimentSnapshot(outcome));localStorage.setItem(M11B_EXPERIMENT_KEY,JSON.stringify(history.slice(-60)));if(typeof renderM11BExperimentHistory==='function')renderM11BExperimentHistory();return true}catch{return false}}
function m11bExperimentAggregate(history=m11bExperimentHistory()){const rows=(Array.isArray(history)?history:[]).filter(Boolean),avg=(list,fn)=>list.length?list.reduce((a,x)=>a+(Number(fn(x))||0),0)/list.length:0;return Object.fromEntries(Object.keys(M11B_EXPERIMENT_COHORTS).map(id=>{const list=rows.filter(x=>x.cohort===id),wins=list.filter(x=>x.outcome==='win').length;return[id,{samples:list.length,winRate:list.length?Math.round(wins/list.length*100):0,avgTurns:avg(list,x=>x.turns),avgMaintenance:avg(list,x=>x.maintenance?.filter(e=>e.actor==='player').length||0),avgRummys:avg(list,x=>x.rummys?.filter(e=>e.actor==='player').length||0),avgOpponentMeldUses:avg(list,x=>x.opponentMeldUses),multiAttachPeak:list.reduce((m,x)=>Math.max(m,Number(x.multiAttachMax)||0),0),top:list.reduce((n,x)=>n+(Number(x.rankChoiceTop)||0),0),bottom:list.reduce((n,x)=>n+(Number(x.rankChoiceBottom)||0),0)}]}))}
function m11bExperimentAggregateText(history=m11bExperimentHistory()){const a=m11bExperimentAggregate(history),fmt=n=>Number(n||0).toFixed(1),line=id=>{const x=a[id],c=m11bExperimentCohort(id);return`${c.label} ${x.samples}판 · 승률 ${x.winRate}% · 턴 ${fmt(x.avgTurns)} · 정비 ${fmt(x.avgMaintenance)} · 러미 ${fmt(x.avgRummys)} · 상대 조합 ${fmt(x.avgOpponentMeldUses)} · 다중 최고 ${x.multiAttachPeak||1}장 · 선택 ↑${x.top}/↓${x.bottom}`};const total=Object.values(a).reduce((n,x)=>n+x.samples,0);return total?[line('zero'),line('few'),line('many')].join('<br>'):'아직 저장된 M11B 실험 표본이 없습니다.'}
function m11bExperimentRowText(row){const result=row.outcome==='win'?'승':row.outcome==='loss'?'패':'무',stamp=row.savedAt?new Date(row.savedAt).toLocaleString('ko-KR',{month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit'}):'이전 기록';return`<b>${row.cohortLabel||row.cohort} · ${result}</b> · ${stamp}<br>턴 ${row.turns||0} · 정비 ${row.maintenance?.filter(e=>e.actor==='player').length||0} · 러미 ${row.rummys?.filter(e=>e.actor==='player').length||0} · 상대 조합 ${row.opponentMeldUses||0} · 다중 ${row.multiAttachMax||1} · 사용값 ↑${row.rankChoiceTop||0}/↓${row.rankChoiceBottom||0}`}
function renderM11BExperimentHistory(){const history=m11bExperimentHistory(),count=document.getElementById('m11bExperimentCount'),overview=document.getElementById('m11bExperimentOverview'),list=document.getElementById('m11bExperimentList');if(count)count.textContent=`${history.length}판`;if(overview)overview.innerHTML=m11bExperimentAggregateText(history);if(list)list.innerHTML=history.length?history.slice(-8).reverse().map(x=>`<div class=\"metricsRow\">${m11bExperimentRowText(x)}</div>`).join(''):'<div class=\"metricsEmpty\">위의 0/4/10장 실험전을 끝내면 별도 기록이 쌓입니다.</div>';return history}
async function copyM11BExperimentHistory(){const text=JSON.stringify(m11bExperimentHistory(),null,2);if(typeof navigator!=='undefined'&&navigator.clipboard?.writeText){try{await navigator.clipboard.writeText(text);return true}catch{}}return false}
function clearM11BExperimentHistory(){if(typeof localStorage==='undefined')return false;try{localStorage.removeItem(M11B_EXPERIMENT_KEY);renderM11BExperimentHistory();return true}catch{return false}}
"""
if "const M11B_EXPERIMENT_KEY='rummyDuelM11BExperimentV1';" not in s:
    s=s.replace("const BATTLE_METRICS_KEY='rummyDuelBattleMetricsV1';",constants+"\nconst BATTLE_METRICS_KEY='rummyDuelBattleMetricsV1';",1)

# Render developer controls and experiment history.
def edit_dev(fn):
    fn=replace_once(fn,"if(battle)battle.disabled=!on;","if(battle)battle.disabled=!on;document.querySelectorAll('[data-m11b-experiment]').forEach(b=>b.disabled=!on);",'developer cohort disabled state')
    fn=replace_once(fn,"if(typeof renderAsymmetricRankPrototype==='function')renderAsymmetricRankPrototype()","if(typeof renderAsymmetricRankPrototype==='function')renderAsymmetricRankPrototype();if(typeof renderM11BExperimentHistory==='function')renderM11BExperimentHistory()",'developer experiment history render')
    return fn
s=edit_function(s,'renderDeveloperPanel',edit_dev)

# Every battle must get fresh metrics and experiment flags.
def edit_newgame(fn):
    old="state.sessionMode=mode;state.battleId++;"
    new="state.sessionMode=mode;state.battleId++;state.m11bExperimentBattle=false;state.m11bExperimentCohort=null;state.m11bExperimentStats=null;state.battleMetrics=null;"
    return replace_once(fn,old,new,'newGame metric reset')
s=edit_function(s,'newGame',edit_newgame)

# Record a choice only after an atomic rank plan succeeds.
def edit_apply(fn):
    if "recordM11BRankChoices(list,normalized)" in fn:return fn
    pos=fn.rfind('return true')
    if pos<0:raise SystemExit('applyRankChoicePlan final return missing')
    return fn[:pos]+"if(typeof recordM11BRankChoices==='function')recordM11BRankChoices(list,normalized);"+fn[pos:]
s=edit_function(s,'applyRankChoicePlan',edit_apply)

# Dedicated setup/start path. Player varies 0/4/10; CPU always base 0.
start_funcs="""
function setupM11BExperimentBattle(cohortId='few'){const cohort=m11bExperimentCohort(cohortId),p=state.player,e=state.enemy;if(!p||!e)return false;state.m11bExperimentBattle=true;state.m11bExperimentCohort=cohort.id;state.m11bExperimentStats={top:0,bottom:0,choices:[]};state.developerBattle=true;state.battleMetrics=null;p.charId='wanderer';p.themeId='mixed';e.charId='wanderer';e.themeId='mixed';p.deck=makeM11BExperimentDeck('player',cohort.id);e.deck=makeM11BExperimentDeck('enemy','zero');p.hand=[];e.hand=[];p.spent=[];e.spent=[];p.melds=[];e.melds=[];state.discard=[];state.field=null;state.phase='mulligan';state.turn='player';state.turnNo=1;state.turnToken=0;state.selected.clear();state.selectionOrder=[];state.boardSelected.clear();state.target=null;state.logs=[];state.rummy=0;state.switchTarget='neutral';state.switchPower=0;state.lastSwitchAdd=0;state.lastSwitchActor=null;state.fuseUsed=false;state.gameOver=false;state.rewarded=false;clearEffectChoices();drawMany('player',8,false);drawMany('enemy',8,false);log(`M11B 비대칭 실험전 · ${cohort.label}. 플레이어 원본 29슬롯 중 X/Y ${cohort.slots.length}장, 상대는 동일 슬롯 X/X 0장 기준덱입니다.`,'important');log('DEV 전용 표본 · 진행도와 일반 M12 전투 기록에는 반영되지 않습니다. 정비·러미·상대 조합·다중 붙이기·위/아래 사용값만 별도 기록합니다.','good');render();return true}
function startM11BExperimentBattle(cohortId='few'){if(!developerModeActive()){openDeveloperPanel();return false}state.tutorialStep=null;state.tutorialHintOpen=false;hideTutorialCoach();hideStartScreen();document.getElementById('developerOverlay')?.classList.remove('show');document.getElementById('overlay')?.classList.remove('show');newGame('battle');return setupM11BExperimentBattle(cohortId)}
"""
if 'function setupM11BExperimentBattle(' not in s:
    marker="function restartCurrentCombat()"
    idx=s.find(marker)
    if idx<0:raise SystemExit('restartCurrentCombat anchor missing')
    s=s[:idx]+start_funcs+s[idx:]

def edit_restart(fn):
    old="if(state.sessionMode==='practice')startPracticeBattle();else newGame('battle')"
    new="if(state.m11bExperimentBattle)startM11BExperimentBattle(state.m11bExperimentCohort||'few');else if(state.sessionMode==='practice')startPracticeBattle();else newGame('battle')"
    return replace_once(fn,old,new,'experiment replay path')
s=edit_function(s,'restartCurrentCombat',edit_restart)

# Route experiment results to a separate localStorage history; ordinary DEV battles remain unsaved.
def edit_save(fn):
    old="if(st.saved||state.sessionMode==='tutorial'||state.developerBattle)return false;st.saved=true;"
    new="if(st.saved||state.sessionMode==='tutorial')return false;if(state.m11bExperimentBattle){st.saved=true;return saveM11BExperimentMetrics(outcome)}if(state.developerBattle)return false;st.saved=true;"
    return replace_once(fn,old,new,'saveBattleMetrics experiment route')
s=edit_function(s,'saveBattleMetrics',edit_save)

# Wire developer controls.
old_events="document.getElementById('developerBattleBtn').onclick=()=>{if(!developerModeActive())return;document.getElementById('developerOverlay').classList.remove('show');startBattle()};"
new_events=old_events+"document.querySelectorAll('[data-m11b-experiment]').forEach(b=>b.onclick=()=>startM11BExperimentBattle(b.dataset.m11bExperiment));document.getElementById('m11bExperimentCopyBtn').onclick=async()=>{const ok=await copyM11BExperimentHistory(),b=document.getElementById('m11bExperimentCopyBtn');if(b){const old=b.textContent;b.textContent=ok?'복사 완료':'복사 실패';setTimeout(()=>b.textContent=old,900)}};document.getElementById('m11bExperimentClearBtn').onclick=()=>{if(confirm('저장된 M11B 비대칭 실험 기록을 모두 지울까요?'))clearM11BExperimentHistory()};"
s=replace_once(s,old_events,new_events,'developer experiment events')

p.write_text(s)

r=road.read_text()
anchor='''### 밸런스 판정 기준
- [x] 라이브 승격 전 구조적 밀도 시뮬레이션'''
item='''### 밸런스 판정 기준
- [x] 개발자 전용 0/4/10장 실제 전투 샌드박스 + 분리 지표 기록 — 개발자 패널에서 동일 원본 29슬롯+광대왕 조커의 기준 0장 / 소수 4장 / 스트레스 10장 코호트를 시작하며 상대는 항상 0장 X/X 기준덱. 합성 X/Y는 `NAMED`/해금/자동 덱에 등록하지 않고 별도 `rummyDuelM11BExperimentV1` 기록에 턴·정비·러미·상대 조합·다중 붙이기·↑/↓ 사용값을 최대 60판 보존. DEV/실험전은 진행도와 M12 일반/연습 `rummyDuelBattleMetricsV1` 표본에서 제외하며 `newGame()` 전투 지표 초기화도 회귀 잠금
- [x] 라이브 승격 전 구조적 밀도 시뮬레이션'''
if '개발자 전용 0/4/10장 실제 전투 샌드박스' not in r:
    if anchor not in r:raise SystemExit('ROADMAP M11B balance anchor missing')
    r=r.replace(anchor,item,1)
road.write_text(r)

d=doc.read_text()
section='''

## 개발자 전용 실제 전투 샌드박스

구조적 6장 손패 시뮬레이션 다음 단계로 **실제 턴 흐름을 사용하는 DEV 전용 0/4/10장 전투**를 둔다. 아직 비대칭 네임드를 라이브 `NAMED`에 올리는 단계가 아니다.

- 개발자 패널의 `기준전 · 0장 / 소수 · 4장 / 스트레스 · 10장` 버튼에서만 시작한다. DEV가 꺼져 있으면 버튼도 비활성이다.
- 세 코호트 모두 현재 기본 정규 29슬롯 + 광대왕 조커 1장을 사용한다. 플레이어 정규 카드의 `topRank/bottomRank`만 합성으로 바꾸며, 상대는 항상 같은 29슬롯의 `X/X` 0장 기준덱이다.
- `소수 4장`과 `스트레스 10장`의 슬롯/인쇄값은 `experiments/m11b-asymmetric-density.mjs`와 동일하다. 합성 카드는 네임드가 아니고 고유 효과도 없다. 따라서 **사용값 유연성 자체의 실제 전투 영향**만 본다.
- 실험전은 `state.developerBattle=true`이며 승패가 클리어·캐릭터 레벨·해금에 반영되지 않는다. 일반 DEV 대전과 마찬가지로 공개 콘텐츠 표본이 아니다.
- M12의 일반/연습 기록 키 `rummyDuelBattleMetricsV1`에도 넣지 않는다. 대신 `rummyDuelM11BExperimentV1`에 최근 60판을 별도로 저장한다.
- 실험 기록은 코호트/승패/턴 수/플레이어 정비/플레이어 러미/상대 공개 조합 이용/최대 다중 붙이기와, 합성 X/Y가 실제 조합에 들어갈 때 선택한 `↑ top / ↓ bottom` 횟수 및 개별 슬롯·선택값을 기록한다.
- 결과창의 다시 하기는 직전 0/4/10 코호트를 그대로 다시 시작한다.
- `newGame()`은 매 전투 `state.battleMetrics=null`로 초기화한다. 이전 전투의 `saved:true`가 다음 전투 저장을 막지 못하도록 M12 전투 지표 생명주기를 함께 수정한다.

### 이 샌드박스로 확인할 것

1. 0/4/10장에서 실제 정비 빈도가 구조 시뮬레이션의 막힘 감소 방향과 일치하는가.
2. 4장 수준에서 실제 러미가 과도하게 늘어나는가.
3. 비대칭 카드가 상대 공개 조합 붙이기와 다중 붙이기의 성공 경로를 지나치게 늘리는가.
4. top/bottom 선택이 한쪽에 지나치게 쏠린다면 두 인쇄값 중 하나가 사실상 장식인지 확인한다.
5. 위 데이터는 **개발자 조작 표본**이므로 최종 승률/콘텐츠 밸런스 결론으로 쓰지 않는다. 정식 승격 전에는 M12 실제 플레이 표본이 여전히 필요하다.
'''
if '## 개발자 전용 실제 전투 샌드박스' not in d:d+=section
doc.write_text(d)
print('M11B developer sandbox patch installed')

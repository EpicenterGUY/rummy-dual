from pathlib import Path

p=Path('index.html')
s=p.read_text()
road=Path('ROADMAP.md')
doc=Path('docs/ASYMMETRIC_RANK_PROTOTYPE.md')
r=road.read_text(); d=doc.read_text()

def function_span(text,name):
    marker=f'function {name}('
    start=text.find(marker)
    if start<0: raise SystemExit(f'missing function {name}')
    brace=text.find('{',start); depth=0
    for i in range(brace,len(text)):
        if text[i]=='{': depth+=1
        elif text[i]=='}':
            depth-=1
            if depth==0:return start,i+1
    raise SystemExit(f'unterminated function {name}')

def replace_function(text,name,new):
    a,b=function_span(text,name);return text[:a]+new+text[b:]

css='''
/* M11B · paired deck-seed experiment control */
.rankExperimentSeedRow{display:flex;align-items:center;justify-content:space-between;gap:6px;margin-top:6px;padding-top:6px;border-top:1px solid #46524f}.rankExperimentSeedLabel{min-width:0;color:#d6c8a8;font-size:6px;line-height:1.4;overflow-wrap:anywhere}.rankExperimentSeedRow .pixelBtn{flex:0 0 auto;padding:5px 7px;font-size:6px}
@media(max-width:390px){.rankExperimentSeedRow{align-items:stretch;flex-direction:column}.rankExperimentSeedRow .pixelBtn{width:100%;min-height:34px}}
'''
if '/* M11B · paired deck-seed experiment control */' not in s:
    s=s.replace('</style>',css+'\n</style>',1)

old='결과는 일반 진행도와 M12 일반/연습 기록에 섞이지 않습니다.</div></div><div class="metricsPanel m11bMetricsPanel">'
new='결과는 일반 진행도와 M12 일반/연습 기록에 섞이지 않습니다.<div class="rankExperimentSeedRow"><span id="m11bPairSeedLabel" class="rankExperimentSeedLabel">비교 시드 준비 중</span><button id="m11bNewPairSeedBtn" class="pixelBtn" type="button" disabled>새 비교 시드</button></div></div></div><div class="metricsPanel m11bMetricsPanel">'
if old in s:s=s.replace(old,new,1)
elif 'id="m11bPairSeedLabel"' not in s:raise SystemExit('seed control HTML anchor missing')

old_state='m11bExperimentCohort:null,m11bExperimentStats:null,battleMetrics:null'
new_state='m11bExperimentCohort:null,m11bExperimentStats:null,m11bExperimentSeed:null,battleMetrics:null'
if old_state in s:s=s.replace(old_state,new_state,1)
elif 'm11bExperimentSeed:null' not in s:raise SystemExit('state seed anchor missing')

const_anchor="const M11B_EXPERIMENT_STABLE_SAMPLES=20;"
consts="""const M11B_EXPERIMENT_STABLE_SAMPLES=20;
const M11B_EXPERIMENT_SEED_KEY='rummyDuelM11BExperimentSeedV1';
let m11bExperimentFallbackSeed=1731;"""
if "const M11B_EXPERIMENT_SEED_KEY='rummyDuelM11BExperimentSeedV1';" not in s:
    if const_anchor not in s:raise SystemExit('readiness constant anchor missing')
    s=s.replace(const_anchor,consts,1)

seed_helpers='''
function m11bNormalizeSeed(value){const n=Number(value);if(!Number.isFinite(n))return 1;const v=(Math.floor(n)>>>0);return v||1}
function m11bGenerateSeed(){const now=typeof Date!=='undefined'?Date.now():1,noise=Math.floor(Math.random()*0xffffffff);return m11bNormalizeSeed(now^noise)}
function m11bExperimentSeedState(){if(typeof localStorage==='undefined')return{seed:m11bExperimentFallbackSeed,completed:[]};try{const raw=JSON.parse(localStorage.getItem(M11B_EXPERIMENT_SEED_KEY)||'null');if(raw&&Number.isFinite(Number(raw.seed))){return{seed:m11bNormalizeSeed(raw.seed),completed:Array.isArray(raw.completed)?raw.completed.filter(id=>M11B_EXPERIMENT_COHORTS[id]):[]}}const fresh={seed:m11bGenerateSeed(),completed:[]};localStorage.setItem(M11B_EXPERIMENT_SEED_KEY,JSON.stringify(fresh));return fresh}catch{return{seed:m11bExperimentFallbackSeed,completed:[]}}}
function saveM11BExperimentSeedState(value){const next={seed:m11bNormalizeSeed(value?.seed),completed:Array.isArray(value?.completed)?[...new Set(value.completed.filter(id=>M11B_EXPERIMENT_COHORTS[id]))]:[]};m11bExperimentFallbackSeed=next.seed;if(typeof localStorage!=='undefined')try{localStorage.setItem(M11B_EXPERIMENT_SEED_KEY,JSON.stringify(next))}catch{}return next}
function currentM11BExperimentSeed(){return m11bExperimentSeedState().seed}
function newM11BExperimentSeed(){const current=m11bExperimentSeedState().seed;let seed=m11bGenerateSeed();if(seed===current)seed=m11bNormalizeSeed(seed+1);const next=saveM11BExperimentSeedState({seed,completed:[]});if(typeof renderM11BExperimentSeedStatus==='function')renderM11BExperimentSeedStatus();return next.seed}
function markM11BExperimentSeedComplete(cohortId,seed){const cur=m11bExperimentSeedState();if(m11bNormalizeSeed(seed)!==cur.seed||!M11B_EXPERIMENT_COHORTS[cohortId])return cur;return saveM11BExperimentSeedState({seed:cur.seed,completed:[...cur.completed,cohortId]})}
function m11bExperimentSeedStatusText(){const cur=m11bExperimentSeedState(),done=['zero','few','many'].filter(id=>cur.completed.includes(id)),left=['zero','few','many'].filter(id=>!cur.completed.includes(id));return`비교 시드 ${cur.seed} · 완료 ${done.length}/3${left.length?` · 남음 ${left.map(id=>m11bExperimentCohort(id).label).join(' / ')}`:' · 0/4/10장 한 세트 완료'}`}
function renderM11BExperimentSeedStatus(){const label=document.getElementById('m11bPairSeedLabel'),button=document.getElementById('m11bNewPairSeedBtn');if(label)label.textContent=m11bExperimentSeedStatusText();if(button)button.disabled=!developerModeActive()||(state.m11bExperimentBattle&&!state.gameOver);return m11bExperimentSeedState()}
function m11bSeedMix(seed,salt){let x=m11bNormalizeSeed(seed)^(salt>>>0);x=Math.imul(x^(x>>>16),0x7feb352d);x=Math.imul(x^(x>>>15),0x846ca68b);return m11bNormalizeSeed(x^(x>>>16))}
function m11bSeededShuffle(list,seed){const a=list,randSeed=m11bNormalizeSeed(seed);let x=randSeed;const random=()=>{x=(x+0x6D2B79F5)>>>0;let t=x;t=Math.imul(t^(t>>>15),t|1);t^=t+Math.imul(t^(t>>>7),t|61);return((t^(t>>>14))>>>0)/4294967296};for(let i=a.length-1;i>0;i--){const j=Math.floor(random()*(i+1));[a[i],a[j]]=[a[j],a[i]]}return a}
function m11bExperimentDeckSeed(seed,owner){return m11bSeedMix(seed,owner==='player'?0x13579bdf:0x2468ace0)}
function m11bExperimentCompletePairs(history=m11bExperimentHistory()){const groups=new Map();for(const row of Array.isArray(history)?history:[]){if(!row?.pairSeed||!M11B_EXPERIMENT_COHORTS[row.cohort])continue;const key=String(row.pairSeed),set=groups.get(key)||new Set();set.add(row.cohort);groups.set(key,set)}return[...groups.values()].filter(set=>set.has('zero')&&set.has('few')&&set.has('many')).length}
'''
if 'function m11bNormalizeSeed(' not in s:
    a,b=function_span(s,'m11bExperimentCohort');s=s[:b]+seed_helpers+s[b:]

make='''function makeM11BExperimentDeck(owner,cohortId='few',seed=null){const cohort=m11bExperimentCohort(cohortId),active=new Set(cohort.slots),cards=CORE_IDS.slice(0,29).map(slot=>{const suit=slot[0],rank=slot.slice(1),c=makeCard(suit,rank,false,owner),pair=active.has(slot)?M11B_EXPERIMENT_SPECS[slot]:null;if(pair){c.topRank=pair[0];c.bottomRank=pair[1];c.baseRank=rank;c.rank=rank;c.activeRank=null;c.rankOrientation=null;c.m11bSynthetic=true;c.m11bSyntheticSlot=slot;c.name=`M11B ${pair[0]}/${pair[1]}`;c.effect='개발자 비대칭 실험용 합성 카드. 별도 고유 효과 없이 사용값 유연성만 측정한다.'}return c});cards.push(makeCard('J','J1',true,owner,'J1'));return seed==null?shuffle(cards):m11bSeededShuffle(cards,m11bExperimentDeckSeed(seed,owner))}'''
s=replace_function(s,'makeM11BExperimentDeck',make)

snap='''function m11bExperimentSnapshot(outcome='result'){const base=battleMetricsSnapshot(outcome),cohort=m11bExperimentCohort(state.m11bExperimentCohort),st=getM11BExperimentStats();return{...base,version:1,mode:'m11b-experiment',cohort:cohort.id,cohortLabel:cohort.label,asymmetricCards:cohort.slots.length,syntheticSlots:[...cohort.slots],pairSeed:state.m11bExperimentSeed||null,rankChoiceTop:st.top,rankChoiceBottom:st.bottom,rankChoices:st.choices.map(x=>({...x}))}}'''
s=replace_function(s,'m11bExperimentSnapshot',snap)

save='''function saveM11BExperimentMetrics(outcome='result'){if(!state.m11bExperimentBattle||typeof localStorage==='undefined')return false;try{const history=m11bExperimentHistory(),snapshot=m11bExperimentSnapshot(outcome);history.push(snapshot);localStorage.setItem(M11B_EXPERIMENT_KEY,JSON.stringify(history.slice(-60)));markM11BExperimentSeedComplete(snapshot.cohort,snapshot.pairSeed);if(typeof renderM11BExperimentHistory==='function')renderM11BExperimentHistory();if(typeof renderM11BExperimentSeedStatus==='function')renderM11BExperimentSeedStatus();return true}catch{return false}}'''
s=replace_function(s,'saveM11BExperimentMetrics',save)

row='''function m11bExperimentRowText(row){const result=row.outcome==='win'?'승':row.outcome==='loss'?'패':'무',stamp=row.savedAt?new Date(row.savedAt).toLocaleString('ko-KR',{month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit'}):'이전 기록',seed=row.pairSeed?` · 시드 ${row.pairSeed}`:'';return`<b>${row.cohortLabel||row.cohort} · ${result}</b> · ${stamp}${seed}<br>턴 ${row.turns||0} · 정비 ${row.maintenance?.filter(e=>e.actor==='player').length||0} · 러미 ${row.rummys?.filter(e=>e.actor==='player').length||0} · 상대 조합 ${row.opponentMeldUses||0} · 다중 ${row.multiAttachMax||1} · 사용값 ↑${row.rankChoiceTop||0}/↓${row.rankChoiceBottom||0}` }'''
s=replace_function(s,'m11bExperimentRowText',row)

# Add complete paired-set count to aggregate text without changing existing cohort metrics.
a,b=function_span(s,'m11bExperimentAggregateText');fn=s[a:b]
if '완성 페어' not in fn:
    fn=fn.replace("const total=Object.values(a).reduce((n,x)=>n+x.samples,0);return total?", "const total=Object.values(a).reduce((n,x)=>n+x.samples,0),pairs=m11bExperimentCompletePairs(history);return total?")
    fn=fn.replace("[line('zero'),line('few'),line('many')].join('<br>')", "[line('zero'),line('few'),line('many'),`완성 페어 ${pairs}세트`].join('<br>')")
    s=s[:a]+fn+s[b:]

setup='''function setupM11BExperimentBattle(cohortId='few',seed=currentM11BExperimentSeed()){const cohort=m11bExperimentCohort(cohortId),pairSeed=m11bNormalizeSeed(seed),p=state.player,e=state.enemy;if(!p||!e)return false;state.m11bExperimentBattle=true;state.m11bExperimentCohort=cohort.id;state.m11bExperimentStats={top:0,bottom:0,choices:[]};state.m11bExperimentSeed=pairSeed;state.developerBattle=true;state.battleMetrics=null;p.charId='wanderer';p.themeId='mixed';e.charId='wanderer';e.themeId='mixed';p.deck=makeM11BExperimentDeck('player',cohort.id,pairSeed);e.deck=makeM11BExperimentDeck('enemy','zero',pairSeed);p.hand=[];e.hand=[];p.spent=[];e.spent=[];p.melds=[];e.melds=[];state.discard=[];state.field=null;state.phase='mulligan';state.turn='player';state.turnNo=1;state.turnToken=0;state.selected.clear();state.selectionOrder=[];state.boardSelected.clear();state.target=null;state.logs=[];state.rummy=0;state.switchTarget='neutral';state.switchPower=0;state.lastSwitchAdd=0;state.lastSwitchActor=null;state.fuseUsed=false;state.gameOver=false;state.rewarded=false;clearEffectChoices();drawMany('player',8,false);drawMany('enemy',8,false);log(`M11B 비대칭 실험전 · ${cohort.label} · 비교 시드 ${pairSeed}. 플레이어 X/Y ${cohort.slots.length}장, 상대 0장. 같은 시드는 원본 슬롯 덱 순서만 맞추며 플레이 선택/AI 행동까지 고정하는 완전 리플레이는 아닙니다.`,'important');render();return true}'''
s=replace_function(s,'setupM11BExperimentBattle',setup)
start='''function startM11BExperimentBattle(cohortId='few',seed=currentM11BExperimentSeed()){if(!developerModeActive())return false;state.tutorialStep=null;state.tutorialHintOpen=false;hideTutorialCoach();hideStartScreen();document.getElementById('developerOverlay')?.classList.remove('show');document.getElementById('overlay')?.classList.remove('show');newGame('battle');return setupM11BExperimentBattle(cohortId,seed)}'''
s=replace_function(s,'startM11BExperimentBattle',start)

# newGame clears active battle seed; persistent seed state lives separately.
a,b=function_span(s,'newGame');fn=s[a:b]
if 'state.m11bExperimentSeed=null' not in fn:
    fn=fn.replace('state.m11bExperimentStats=null;state.battleMetrics=null;','state.m11bExperimentStats=null;state.m11bExperimentSeed=null;state.battleMetrics=null;',1)
    s=s[:a]+fn+s[b:]

restart='''function restartCurrentCombat(){document.getElementById('overlay')?.classList.remove('show');if(state.m11bExperimentBattle)return startM11BExperimentBattle(state.m11bExperimentCohort||'few',state.m11bExperimentSeed||currentM11BExperimentSeed());if(state.sessionMode==='practice')startPracticeBattle();else newGame('battle')}'''
s=replace_function(s,'restartCurrentCombat',restart)

# Developer panel also refreshes seed status and locks new-seed button during a live experiment.
a,b=function_span(s,'renderDeveloperPanel');fn=s[a:b]
if "renderM11BExperimentSeedStatus" not in fn:
    fn=fn.replace("if(typeof renderM11BExperimentHistory==='function')renderM11BExperimentHistory()","if(typeof renderM11BExperimentHistory==='function')renderM11BExperimentHistory();if(typeof renderM11BExperimentSeedStatus==='function')renderM11BExperimentSeedStatus()")
    s=s[:a]+fn+s[b:]

# Wire new seed button.
wire="document.getElementById('m11bNewPairSeedBtn')?.addEventListener('click',()=>newM11BExperimentSeed());"
if wire not in s:
    anchor="document.getElementById('m11bExperimentClearBtn')?.addEventListener('click',()=>{if(confirm('M11B 실험 기록을 모두 지울까요?'))clearM11BExperimentHistory()});"
    if anchor not in s:raise SystemExit('M11B event wiring anchor missing')
    s=s.replace(anchor,anchor+'\n'+wire,1)

road_anchor='- [x] M11B 실험 표본 준비도 / 0장 대비 코호트 차이 패널 — 개발자 패널에서 0/4/10장 각각 10판을 `1차 비교 가능`, 20판을 `안정권`으로 표시하고, 0장 기준 대비 4장/10장의 승률·평균 턴·정비·러미·상대 공개 조합 사용·최대 다중붙이기 차이를 자동 요약. 이 기준은 데이터 수집 준비도일 뿐 통계적 유의성·밸런스 합격 판정이 아니며 최종 M11B/M12 밸런스 항목은 계속 미완료로 유지'
road_item='- [x] 0/4/10장 페어 시드 실험 — 동일 비교 시드에서는 플레이어 0/4/10장 코호트의 원본 29슬롯 카드 순서가 같고 상대 0장 기준덱 순서도 동일하도록 개발자 실험 덱만 결정론적으로 셔플. 완료한 코호트를 시드별로 추적하고 3종을 모두 끝낸 `완성 페어` 수를 표시하며, 시드는 덱 순서만 통제하고 인간/AI 행동까지 고정하는 완전 리플레이로 취급하지 않음'
if road_item not in r:
    if road_anchor not in r:raise SystemExit('roadmap readiness anchor missing')
    r=r.replace(road_anchor,road_anchor+'\n'+road_item,1)

append='''

### 페어 시드 — 초기 덱 순서 변수 통제

- 개발자 패널은 현재 비교 시드를 별도 `rummyDuelM11BExperimentSeedV1`에 저장한다. `새 비교 시드`를 누르기 전까지 0/4/10장 버튼은 같은 시드를 사용한다.
- 같은 시드에서는 플레이어의 **원본 29슬롯 + 조커 순서가 세 코호트에서 동일**하다. 4장/10장 코호트는 같은 슬롯 위치에 X/Y 인쇄값만 얹는다.
- 상대는 항상 0장 X/X 기준덱이며 같은 비교 시드에서 상대 덱 순서도 동일하다. 플레이어와 상대는 서로 다른 salt를 사용해 양쪽 덱이 거울처럼 같은 순서가 되지는 않는다.
- 전투 결과에는 `pairSeed`를 기록하고, 현재 시드에서 완료한 0/4/10장 코호트를 추적한다. 세 종류를 모두 끝내면 `완성 페어 1세트`로 집계한다.
- **페어 시드는 완전 리플레이가 아니다.** 초기 덱 순서 변수만 통제한다. 플레이어 선택, 효과 선택, AI 판단에서 발생하는 이후 분기는 동일하다고 가정하지 않는다.
- 따라서 페어 결과는 같은 초기 카드 공급에서 밀도 차이를 보기 위한 보조 증거이며, 최종 밸런스 판정은 여전히 다수 표본과 M12 실제 플레이 데이터를 요구한다.
'''
if '### 페어 시드 — 초기 덱 순서 변수 통제' not in d:d=d.rstrip()+append+'\n'

p.write_text(s);road.write_text(r);doc.write_text(d)
print('M11B paired-seed experiment patch installed')

from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

def once(old,new,label):
    global s
    if old not in s:
        raise SystemExit(f'missing {label}')
    s=s.replace(old,new,1)

once('<p id="resultText"></p><div id="resultUnlocks" class="resultUnlocks" style="display:none"></div>',
     '<p id="resultText"></p><p id="circulationSummary" class="circulationSummary"></p><div id="resultUnlocks" class="resultUnlocks" style="display:none"></div>',
     'result summary slot')

once("state.rewarded=false;state.fullRecirculationCount=0;drawMany('player',8,false);",
     "state.rewarded=false;state.fullRecirculationCount=0;state.circulationStats={turns:0,handTotal:0,handSamples:0,low2:0,low3:0,lowSkips:0,rummys:0,maintenance:0,fullRecirculations:0};drawMany('player',8,false);",
     'newGame circulation reset')

marker='function circulationStalled(w)'
helper="""function getCirculationStats(){return state.circulationStats||(state.circulationStats={turns:0,handTotal:0,handSamples:0,low2:0,low3:0,lowSkips:0,rummys:0,maintenance:0,fullRecirculations:0})}
function recordCirculationTurn(w){const st=getCirculationStats(),n=sideObj(w)?.hand?.length||0;st.turns++;st.handTotal+=n;st.handSamples++;if(n<=2)st.low2++;if(n<=3)st.low3++;return n}
function circulationSummaryText(){const st=getCirculationStats(),avg=st.handSamples?(st.handTotal/st.handSamples).toFixed(1):'-',low2=st.turns?Math.round(st.low2/st.turns*100):0;return `패순환 · 평균 손패 ${avg}장 · 2장 이하 ${low2}% · 저손패 보호 ${st.lowSkips}회 · 러미 ${st.rummys}회 · 정비 ${st.maintenance}회 · 전체 재순환 ${st.fullRecirculations}회`}
function renderCirculationSummary(){const el=document.getElementById('circulationSummary');if(el)el.textContent=circulationSummaryText()}
"""
if 'function getCirculationStats()' not in s:
    if marker not in s:
        raise SystemExit('missing circulation helper marker')
    s=s.replace(marker,helper+marker,1)

once("state.fullRecirculationCount=(state.fullRecirculationCount||0)+1;state.target=null;",
     "state.fullRecirculationCount=(state.fullRecirculationCount||0)+1;getCirculationStats().fullRecirculations++;state.target=null;",
     'full recirculation metric')

once("s.maintenanceUsed=true;s.actedThisTurn=true;log(`${w==='player'?'YOU':'CPU'} 정비",
     "s.maintenanceUsed=true;s.actedThisTurn=true;getCirculationStats().maintenance++;log(`${w==='player'?'YOU':'CPU'} 정비",
     'maintenance metric')

once("s.rummyReturnPending=true;s.rummyRecoveryPending=true;if(lastCards.some(c=>c.tag==='rummyPlus1'))",
     "s.rummyReturnPending=true;s.rummyRecoveryPending=true;getCirculationStats().rummys++;if(lastCards.some(c=>c.tag==='rummyPlus1'))",
     'rummy metric')

once("if(!cs.length&&typeof canSkipBaseDiscard==='function'&&canSkipBaseDiscard('player')){state.player.discardsRemaining=0;",
     "if(!cs.length&&typeof canSkipBaseDiscard==='function'&&canSkipBaseDiscard('player')){getCirculationStats().lowSkips++;state.player.discardsRemaining=0;",
     'player low hand metric')

once("if(typeof canSkipBaseDiscard==='function'&&canSkipBaseDiscard('enemy')){state.enemy.discardsRemaining=0;",
     "if(typeof canSkipBaseDiscard==='function'&&canSkipBaseDiscard('enemy')){getCirculationStats().lowSkips++;state.enemy.discardsRemaining=0;",
     'enemy low hand metric')

once("function turnEnd(w){const s=sideObj(w);",
     "function turnEnd(w){recordCirculationTurn(w);const s=sideObj(w);",
     'turn end hand sample')

once("function showCirculationDraw(){const title=",
     "function showCirculationDraw(){renderCirculationSummary();const title=",
     'circulation draw summary')

once("function showResult(win){const practice=",
     "function showResult(win){renderCirculationSummary();const practice=",
     'normal result summary')

p.write_text(s,encoding='utf-8')

road=Path('ROADMAP.md')
r=road.read_text(encoding='utf-8')
anchor='- [x] Reset transient discard-contract state whenever a card is freshly acquired from deck/discard before source-specific effects are applied\n'
line='- [x] Add per-battle circulation telemetry at result time: average hand, low-hand rate/skips, RUMMY, maintenance, and full-recirculation counts\n'
if line not in r:
    if anchor not in r:
        raise SystemExit('missing M4 roadmap anchor')
    r=r.replace(anchor,anchor+line,1)
road.write_text(r,encoding='utf-8')

test=Path('tests/circulation-telemetry.mjs')
test.write_text("""import fs from 'node:fs';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
ok(html.includes('id=\"circulationSummary\"'),'result overlay exposes circulation summary');
ok(html.includes('function getCirculationStats()')&&html.includes('function circulationSummaryText()'),'circulation telemetry helpers exist');
ok(html.includes('recordCirculationTurn(w);const s=sideObj(w);'),'both turn-end paths sample final hand size');
ok(html.includes('getCirculationStats().lowSkips++'),'low-hand protection usage is counted');
ok(html.includes('getCirculationStats().rummys++'),'RUMMY usage is counted for either side');
ok(html.includes('getCirculationStats().maintenance++'),'maintenance usage is counted');
ok(html.includes('getCirculationStats().fullRecirculations++'),'full recirculation usage is counted');
ok(html.includes('renderCirculationSummary();const practice=')&&html.includes('showCirculationDraw(){renderCirculationSummary();'),'normal and deadlock results render the metrics');
ok(road.includes('per-battle circulation telemetry'),'M4 records live circulation telemetry complete');
console.log('Circulation telemetry regression passed.');
""",encoding='utf-8')

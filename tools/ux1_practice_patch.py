from pathlib import Path

p=Path('index.html')
s=p.read_text()

def one(old,new,label):
    global s
    n=s.count(old)
    if n!=1:
        raise SystemExit(f'{label}: expected 1 match, got {n}')
    s=s.replace(old,new)

one('.startAux{display:grid;grid-template-columns:1fr 1fr;gap:7px}.startAux .pixelBtn{font-size:8px;padding:8px}',
    '.startAux{display:grid;grid-template-columns:1fr 1fr;gap:7px}.startAux .pixelBtn{font-size:8px;padding:8px}.startAux .practiceStartBtn{grid-column:1/-1}',
    'practice start aux css')
one('.tutorialCoachActions{display:flex;gap:5px;flex-wrap:wrap;margin-top:7px}.tutorialCoachActions .pixelBtn{font-size:7px;padding:6px;flex:1 1 auto}',
    '.tutorialCoachActions{display:flex;gap:5px;flex-wrap:wrap;margin-top:7px}.tutorialCoachActions .pixelBtn{font-size:7px;padding:6px;flex:1 1 auto}.practiceCoach{padding:8px 10px;border:1px solid #4d615e;border-radius:9px;background:#243330;box-shadow:none}.practiceCoach[hidden]{display:none}.practiceCoachHead{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:5px}.practiceCoachHead b{font-size:9px;color:#b9d7d1}.practiceCoachText{font-size:7px;line-height:1.5;color:#cbd7d3}',
    'practice coach css')
one('<div class="startAux"><button id="startProgressBtn" class="pixelBtn" type="button">캐릭터·해금</button><button id="startRulesBtn" class="pixelBtn" type="button">규칙·용어</button></div>',
    '<div class="startAux"><button id="startProgressBtn" class="pixelBtn" type="button">캐릭터·해금</button><button id="startRulesBtn" class="pixelBtn" type="button">규칙·용어</button><button id="practiceStartBtn" class="pixelBtn practiceStartBtn" type="button">자유 연습전 · 진행도 영향 없음</button></div>',
    'practice start button')
one('<button id="tutorialRestartBtn" class="pixelBtn" type="button">이 단계 다시 보기</button><button id="tutorialExitBtn" class="pixelBtn redBtn" type="button">튜토리얼 종료</button>',
    '<button id="tutorialRestartBtn" class="pixelBtn" type="button">이 단계 다시 보기</button><button id="tutorialPracticeBtn" class="pixelBtn primary" type="button" hidden>자유 연습전</button><button id="tutorialExitBtn" class="pixelBtn redBtn" type="button">튜토리얼 종료</button>',
    'tutorial practice button')
one('</section>\n<section class="status">',
    '</section>\n<section id="practiceCoach" class="practiceCoach" hidden aria-live="polite"><div class="practiceCoachHead"><span class="badge">자유 연습전</span><b>승패·해금 기록 없음</b></div><div id="practiceCoachText" class="practiceCoachText"></div></section>\n<section class="status">',
    'practice coach html')
one('기본 조작부터 러미까지 고정 패로 직접 익힙니다.', '기본 조작부터 폭발·러미까지 고정 패로 직접 익힙니다.', 'static tutorial copy')
one("function startBattle(){state.tutorialStep=null;state.tutorialHintOpen=false;hideTutorialCoach();state.sessionMode='battle';hideStartScreen();document.getElementById('overlay')?.classList.remove('show');newGame()}",
    "function startBattle(){state.tutorialStep=null;state.tutorialHintOpen=false;hideTutorialCoach();hideStartScreen();document.getElementById('overlay')?.classList.remove('show');newGame('battle')}\nfunction isLiveCombatSession(){return state.sessionMode==='battle'||state.sessionMode==='practice'}\nfunction makePracticeCards(owner,specs){return specs.map(([suit,rank])=>makeCard(suit,rank,false,owner))}\nfunction makePracticeDeck(owner,specs){return makePracticeCards(owner,[...specs].reverse())}\nfunction setupPracticeBattle(){const p=state.player,e=state.enemy;if(!p||!e)return false;p.charId='wanderer';e.charId='wanderer';p.hp=p.maxHp=CORE_HP;e.hp=e.maxHp=CORE_HP;p.cores=e.cores=CORE_COUNT;p.shield=0;e.shield=0;p.status=blankStatus();e.status=blankStatus();p.hand=makePracticeCards('player',[['S','3'],['H','3'],['D','3'],['C','3'],['C','4'],['C','5'],['C','6'],['C','7']]);p.deck=makePracticeDeck('player',[['C','8'],['H','9'],['D','2'],['S','Q'],['C','10'],['C','J'],['C','Q'],['C','K'],['C','A'],['D','6'],['S','6'],['H','6'],['D','8'],['S','8'],['H','8'],['D','10'],['S','10'],['H','10'],['D','K'],['S','K'],['H','K'],['D','A']]);e.hand=makePracticeCards('enemy',[['S','2'],['H','4'],['D','6'],['C','8'],['S','10'],['H','Q'],['D','A'],['C','K']]);e.deck=makePracticeDeck('enemy',[['H','5'],['H','6'],['H','7'],['S','3'],['S','4'],['S','5'],['D','7'],['D','8'],['D','9'],['C','9'],['C','10'],['C','J'],['S','7'],['S','8'],['S','9'],['D','3'],['H','3'],['C','3'],['D','Q'],['S','Q'],['C','Q'],['H','K']]);p.spent=[];e.spent=[];p.melds=[];e.melds=[];state.discard=[];state.field=null;state.phase='action';state.turn='player';state.turnNo=1;state.turnToken=0;state.selected.clear();state.selectionOrder=[];state.boardSelected.clear();state.target=null;state.logs=[];state.rummy=0;state.switchTarget='neutral';state.switchPower=0;state.lastSwitchAdd=0;state.lastSwitchActor=null;state.fuseUsed=false;state.gameOver=false;state.rewarded=false;turnStart('player');p.shield=12;log('자유 연습전 · 순수 카드와 고정 손패로 기본 규칙을 반복합니다. 승패는 클리어·레벨·해금에 반영되지 않습니다.','important');log('첫 손패에는 3 세트와 4♣-5♣-6♣ 런 재료가 모두 있습니다. 새 조합은 한 턴에 1개만 만들 수 있습니다.','good');render();return true}\nfunction startPracticeBattle(){state.tutorialStep=null;state.tutorialHintOpen=false;hideTutorialCoach();hideStartScreen();document.getElementById('overlay')?.classList.remove('show');newGame('practice');setupPracticeBattle()}\nfunction restartCurrentCombat(){document.getElementById('overlay')?.classList.remove('show');if(state.sessionMode==='practice')startPracticeBattle();else newGame('battle')}\nfunction renderPracticeCoach(){const box=document.getElementById('practiceCoach'),txt=document.getElementById('practiceCoachText');if(!box||!txt)return;if(state.sessionMode!=='practice'){box.hidden=true;return}box.hidden=false;if(state.gameOver)txt.textContent='연습전 종료 · 결과는 진행도에 반영되지 않습니다.';else if(state.turnNo===1&&state.turn==='player')txt.textContent='첫 손패에는 3♠·3♥·3♦ 세트와 4♣·5♣·6♣ 런 재료가 있습니다. 원하는 쪽부터 만들어 보세요.';else if(state.switchTarget==='player'&&state.switchPower>0)txt.textContent=`스위치가 나를 가리킵니다. 턴 종료 전 버스트/체인으로 반환하지 못하면 ${state.switchPower}이 폭발합니다.`;else if(state.switchTarget==='enemy'&&state.switchPower>0)txt.textContent=`스위치가 상대를 가리킵니다. 지금은 새 조합·회수·정비로 다음 반환을 준비해도 좋습니다.`;else if(state.phase==='draw')txt.textContent='내 턴 시작 · 개인 덱 또는 공용 버림패에서 1장을 가져온 뒤 자유롭게 조합을 만들어 보세요.';else txt.textContent='세트·런·상대 공개 조합 붙이기·회수·정비를 자유롭게 시험할 수 있습니다. CPU는 연습전에서 행동 수가 줄어듭니다.'}",
    'practice functions')
one("function startTutorial(stepId='intro'){progress.tutorialPromptSeen=true;saveProgress();hideStartScreen();document.getElementById('overlay')?.classList.remove('show');newGame();state.sessionMode='tutorial';setTutorialStep(stepId);renderStartScreen()}",
    "function startTutorial(stepId='intro'){progress.tutorialPromptSeen=true;saveProgress();hideStartScreen();document.getElementById('overlay')?.classList.remove('show');newGame('tutorial');setTutorialStep(stepId);renderStartScreen()}",
    'tutorial new game mode')
one("function newGame(){state.sessionMode='battle';", "function newGame(mode='battle'){state.sessionMode=mode;", 'newGame mode')
one("function endPlayerTurn(){settleContracts('player');turnEnd('player');state.phase='wait';state.turn='enemy';state.player.hand.forEach(c=>c.age++);render();if(!state.gameOver){const battleId=state.battleId;setTimeout(()=>{if(state.sessionMode==='battle'&&state.battleId===battleId&&!state.gameOver)aiTurn()},430)}}",
    "function endPlayerTurn(){settleContracts('player');turnEnd('player');state.phase='wait';state.turn='enemy';state.player.hand.forEach(c=>c.age++);render();if(!state.gameOver){const battleId=state.battleId;setTimeout(()=>{if(isLiveCombatSession()&&state.battleId===battleId&&!state.gameOver)aiTurn()},430)}}",
    'live combat ai guard')
one('let actions=0,rummied=false;while(actions++<4&&!state.gameOver){', "const actionCap=state.sessionMode==='practice'?2:4;let actions=0,rummied=false;while(actions++<actionCap&&!state.gameOver){", 'practice ai cap')
one("function checkGameOver(){if(state.gameOver)return;if((state.player?.cores||0)<=0||(state.enemy?.cores||0)<=0){state.gameOver=true;state.phase='over';const win=(state.enemy?.cores||0)<=0,battleId=state.battleId;setTimeout(()=>{if(state.sessionMode==='battle'&&state.battleId===battleId&&state.gameOver)showResult(win)},1400)}}",
    "function checkGameOver(){if(state.gameOver)return;if((state.player?.cores||0)<=0||(state.enemy?.cores||0)<=0){state.gameOver=true;state.phase='over';const win=(state.enemy?.cores||0)<=0,battleId=state.battleId;setTimeout(()=>{if(isLiveCombatSession()&&state.battleId===battleId&&state.gameOver)showResult(win)},1400)}}",
    'practice result guard')
old_show="function showResult(win){document.getElementById('resultTitle').textContent=win?'승리':'패배';document.getElementById('resultTitle').className=win?'cyan':'red';const box=document.getElementById('resultUnlocks');box.style.display='none';box.innerHTML='';if(win){const news=grantVictoryProgress(),lv=charLevel(progress,state.player.charId);document.getElementById('resultText').textContent=`상대의 마지막 코어를 파괴했습니다. ${CHARACTERS[state.player.charId].name} Lv.${lv} · 전체 ${progress.totalClears}클리어 · 러미 ${state.rummy}회.`;if(news.length){box.style.display='block';box.innerHTML=`<b>새 해금</b><br>${news.map(x=>'• '+x).join('<br>')}`}}else document.getElementById('resultText').textContent='상대가 내 마지막 코어를 먼저 파괴했습니다. 패배해도 해금 진행은 감소하지 않습니다.';renderProgress();document.getElementById('overlay').classList.add('show')}"
new_show="function showResult(win){const practice=state.sessionMode==='practice',title=document.getElementById('resultTitle'),text=document.getElementById('resultText'),box=document.getElementById('resultUnlocks'),again=document.getElementById('againBtn');box.style.display='none';box.innerHTML='';again.textContent=practice?'연습전 다시 하기':'다시 하기';if(practice){title.textContent=win?'연습전 승리':'연습전 패배';title.className=win?'cyan':'red';text.textContent=win?'연습 상대의 마지막 코어를 파괴했습니다. 이 결과는 클리어·레벨·해금에 반영되지 않습니다.':'연습전에서 내 마지막 코어가 파괴되었습니다. 진행도 변화 없이 바로 다시 연습할 수 있습니다.';renderProgress();document.getElementById('overlay').classList.add('show');return}title.textContent=win?'승리':'패배';title.className=win?'cyan':'red';if(win){const news=grantVictoryProgress(),lv=charLevel(progress,state.player.charId);text.textContent=`상대의 마지막 코어를 파괴했습니다. ${CHARACTERS[state.player.charId].name} Lv.${lv} · 전체 ${progress.totalClears}클리어 · 러미 ${state.rummy}회.`;if(news.length){box.style.display='block';box.innerHTML=`<b>새 해금</b><br>${news.map(x=>'• '+x).join('<br>')}`}}else text.textContent='상대가 내 마지막 코어를 먼저 파괴했습니다. 패배해도 해금 진행은 감소하지 않습니다.';renderProgress();document.getElementById('overlay').classList.add('show')}"
one(old_show,new_show,'practice result no progress')
one("const next=document.getElementById('tutorialNextBtn');if(state.tutorialSegmentDone){", "const next=document.getElementById('tutorialNextBtn'),practice=document.getElementById('tutorialPracticeBtn');if(practice)practice.hidden=!(state.tutorialSegmentDone&&step.id==='rummy');if(state.tutorialSegmentDone){", 'tutorial practice visibility')
one("step.id==='rummy'?'기본 튜토리얼 완료! 메인으로 돌아가거나 이 단계를 다시 연습할 수 있습니다.'", "step.id==='rummy'?'기본 튜토리얼 완료! 자유 연습전으로 이어가거나 메인으로 돌아갈 수 있습니다.'", 'rummy coach copy')
one("if(note)note.textContent=progress.tutorialCompleted?'기본 튜토리얼 완료 · 필요할 때 언제든 다시 볼 수 있습니다.':progress.tutorialPromptSeen?'기본 조작부터 러미까지 고정 패 튜토리얼을 시작할 수 있습니다.'", "if(note)note.textContent=progress.tutorialCompleted?'기본 튜토리얼 완료 · 자유 연습전에서 반복하거나 언제든 다시 볼 수 있습니다.':progress.tutorialPromptSeen?'기본 조작부터 폭발·러미까지 고정 패 튜토리얼을 시작할 수 있습니다.'", 'start note practice')
one("if(tutorialSmall)tutorialSmall.textContent=progress.tutorialCompleted?'기본 튜토리얼을 처음부터 다시 플레이합니다.':'기본 조작부터 러미까지 고정 패로 직접 익힙니다.'", "if(tutorialSmall)tutorialSmall.textContent=progress.tutorialCompleted?'기본 튜토리얼을 처음부터 다시 플레이합니다.':'기본 조작부터 폭발·러미까지 고정 패로 직접 익힙니다.'", 'tutorial small copy')
one("renderInitiative();renderHand();renderEnemyHand();renderDiscard();renderMelds();updateButtons();", "renderInitiative();renderHand();renderEnemyHand();renderDiscard();renderMelds();updateButtons();renderPracticeCoach();", 'render practice coach')
one("document.getElementById('resetBtn').onclick=()=>{document.getElementById('overlay').classList.remove('show');newGame()};document.getElementById('againBtn').onclick=()=>{document.getElementById('overlay').classList.remove('show');newGame()};", "document.getElementById('resetBtn').onclick=restartCurrentCombat;document.getElementById('againBtn').onclick=restartCurrentCombat;", 'practice-aware restart')
one("document.getElementById('tutorialExitBtn').onclick=exitTutorial;document.getElementById('startCodexBtn').onclick", "document.getElementById('tutorialExitBtn').onclick=exitTutorial;document.getElementById('tutorialPracticeBtn').onclick=startPracticeBattle;document.getElementById('practiceStartBtn').onclick=startPracticeBattle;document.getElementById('startCodexBtn').onclick", 'practice button handlers')
one("function showStartScreen(){state.battleId++;state.sessionMode='menu';state.tutorialStep=null;state.tutorialHintOpen=false;hideTutorialCoach();", "function showStartScreen(){state.battleId++;state.sessionMode='menu';state.tutorialStep=null;state.tutorialHintOpen=false;hideTutorialCoach();const practice=document.getElementById('practiceCoach');if(practice)practice.hidden=true;", 'hide practice on menu')
p.write_text(s)

r=Path('ROADMAP.md')
rs=r.read_text()
old='- [ ] 자유 연습전'
if rs.count(old)!=1: raise SystemExit(f'roadmap practice match {rs.count(old)}')
rs=rs.replace(old,'- [x] 자유 연습전 — 순수 카드·필드 없음·유리한 고정 시작 손패·첫 사이클 보호막 12·CPU 행동 축소. 일반 대전과 분리된 `practice` 세션이며 승패/클리어/레벨/해금 진행도에는 영향 없음')
r.write_text(rs)

Path('tests/practice-battle.mjs').write_text(r'''import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const roadmap=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(c,m){if(!c)throw new Error(m);console.log(`PASS: ${m}`)}
function functionSource(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);const body=script.indexOf('){',start),brace=body+1;let depth=0,end=-1;for(let i=brace;i<script.length;i++){if(script[i]==='{')depth++;else if(script[i]==='}'){depth--;if(depth===0){end=i+1;break}}}if(end<0)throw new Error(`unterminated ${name}`);return script.slice(start,end)}
function install(ctx,...names){for(const n of names)vm.runInContext(functionSource(n),ctx)}
new Function(script);
ok(html.includes('id="practiceStartBtn"')&&html.includes('자유 연습전 · 진행도 영향 없음'),'start screen exposes free practice battle without changing the four primary menu items');
ok(html.includes('id="tutorialPracticeBtn"')&&script.includes("practice.hidden=!(state.tutorialSegmentDone&&step.id==='rummy')"),'completed tutorial can continue directly into free practice');
ok(script.includes("function newGame(mode='battle'){state.sessionMode=mode;")&&script.includes("function isLiveCombatSession(){return state.sessionMode==='battle'||state.sessionMode==='practice'}"),'battle engine has an explicit practice session mode');
ok(script.includes("const actionCap=state.sessionMode==='practice'?2:4"),'practice CPU uses a reduced action cap');
ok(script.includes("if(practice){title.textContent=win?'연습전 승리':'연습전 패배'")&&script.includes("이 결과는 클리어·레벨·해금에 반영되지 않습니다."),'practice result path explicitly avoids progression rewards');
ok(script.includes("if(state.sessionMode==='practice')startPracticeBattle();else newGame('battle')"),'reset and result replay preserve practice mode');
ok(script.includes("setTimeout(()=>{if(isLiveCombatSession()&&state.battleId===battleId&&!state.gameOver)aiTurn()},430)")&&script.includes("if(isLiveCombatSession()&&state.battleId===battleId&&state.gameOver)showResult(win)"),'practice shares race-safe AI/result scheduling with battle mode');
{
 const state={sessionMode:'practice',player:{},enemy:{},selected:new Set(),selectionOrder:[],boardSelected:new Set(),target:null};
 let uid=1,logs=[],rendered=0;
 const ctx=vm.createContext({console,Math,state,CORE_HP:60,CORE_COUNT:3});
 ctx.blankStatus=()=>({vulnerable:0,seal:0,regen:0});
 ctx.makeCard=(suit,rank,named,owner)=>({uid:uid++,suit,rank,owner,named});
 ctx.turnStart=w=>{state.turnToken++;const s=w==='player'?state.player:state.enemy;s.turnStarts=(s.turnStarts||0)+1;s.newMeldUsed=false;s.returnedSwitchThisTurn=false};
 ctx.log=(msg)=>logs.push(msg);ctx.render=()=>rendered++;
 install(ctx,'makePracticeCards','makePracticeDeck','setupPracticeBattle');
 ok(ctx.setupPracticeBattle()===true,'practice setup applies successfully to a live state');
 ok(state.field===null&&state.phase==='action'&&state.turn==='player','practice skips field and mulligan to start immediately in action phase');
 ok(state.player.hand.map(c=>`${c.rank}${c.suit}`).join(',')==='3S,3H,3D,3C,4C,5C,6C,7C','practice opening hand deterministically contains both SET and RUN lessons');
 ok(state.player.shield===12&&state.player.cores===3&&state.enemy.cores===3,'practice keeps normal CORE rules and only adds first-cycle shield forgiveness');
 ok(state.player.hand.every(c=>!c.named)&&state.enemy.hand.every(c=>!c.named),'practice battle uses pure cards only');
 ok(state.player.deck.at(-1).rank==='8'&&state.player.deck.at(-1).suit==='C','practice personal deck has deterministic first draw 8 club');
 ok(logs.some(x=>x.includes('진행되지 않습니다')||x.includes('반영되지 않습니다'))&&rendered===1,'practice clearly states no progression and renders the prepared board once');
}
ok(roadmap.includes('- [x] 자유 연습전 — 순수 카드'),'UX1 P2 roadmap records free practice battle complete');
console.log('RUMMY//DUEL free practice battle regressions passed.');
''')

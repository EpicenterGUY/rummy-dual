from pathlib import Path

INDEX = Path('index.html')
text = INDEX.read_text(encoding='utf-8')


def replace_once(old: str, new: str, label: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly 1 match, found {count}')
    text = text.replace(old, new, 1)


# Battlefield/discard rules shown to the player.
replace_once(
    '공용 버림패 <b id="discardCount">0</b>/5<div class="pileRule">최근 5장 · 맨 위만 가져오기</div>',
    '공용 버림패 <b id="discardCount">0</b><div class="pileRule">장수 제한 없음 · 맨 위만 가져오기</div>',
    'discard pile UI cap',
)
replace_once(
    '획득은 내 덱 맨 위 또는 공용 버림패 맨 위 중 하나입니다.</p>',
    '획득은 내 덱 맨 위 또는 공용 버림패 맨 위 중 하나입니다. <b>공용 버림패에는 장수 제한이 없고</b>, 기본 획득은 맨 위 카드만 가져옵니다.</p>',
    'turn rules discard text',
)
replace_once(
    '이번 턴 자신이 새로 만든 조합에는 같은 턴 다시 붙일 수 없습니다.</p>',
    '이번 턴 자신이 새로 만든 조합에는 같은 턴 다시 붙일 수 없습니다. 각 플레이어의 공개 조합은 <b>최대 2개</b>이며, 기본 행동으로 기존 조합이나 RUN을 자유롭게 정리해 자리를 만들 수 없습니다.</p>',
    'shared battlefield rules text',
)

# Progress hardening: corrupted/old localStorage must not prevent boot.
replace_once(
    "function loadProgress(){try{const x=JSON.parse(localStorage.getItem('rummyDuelProgressV25')||'null');if(x&&x.chars)return Object.assign(defaultProgress(),x,{chars:Object.assign(defaultProgress().chars,x.chars)})}catch(e){}return defaultProgress()}",
    "function normalizeProgress(x){const base=defaultProgress();if(!x||typeof x!=='object')return base;const chars={...base.chars};for(const id of Object.keys(chars)){const n=Number(x.chars?.[id]);if(Number.isFinite(n)&&n>=0)chars[id]=Math.floor(n)}const tc=Number(x.totalClears);return{totalClears:Number.isFinite(tc)&&tc>=0?Math.floor(tc):0,selectedChar:Object.prototype.hasOwnProperty.call(CHARACTERS,x.selectedChar)?x.selectedChar:'wanderer',chars}}\nfunction loadProgress(){try{const x=JSON.parse(localStorage.getItem('rummyDuelProgressV25')||'null');return normalizeProgress(x)}catch(e){console.warn('RUMMY//DUEL progress load failed; defaults restored.',e);return defaultProgress()}}",
    'loadProgress hardening',
)
replace_once(
    "function saveProgress(){try{localStorage.setItem('rummyDuelProgressV25',JSON.stringify(progress))}catch(e){}}",
    "function saveProgress(){try{localStorage.setItem('rummyDuelProgressV25',JSON.stringify(progress))}catch(e){console.warn('RUMMY//DUEL progress save failed; continuing without persistence.',e)}}",
    'saveProgress warning',
)
replace_once(
    "function charUnlocked(id,p=progress){return !!CHARACTER_UNLOCK[id](p)}",
    "function charUnlocked(id,p=progress){const unlock=CHARACTER_UNLOCK[id];return typeof unlock==='function'&&!!unlock(p)}",
    'safe charUnlocked',
)

# Shared discard acquisition path. Both normal top-card takes and Black Market second-card takes use it.
replace_once(
    "function drawOne(w,fromDiscard=false){const s=sideObj(w);let c=null;if(fromDiscard&&state.discard.length)c=state.discard.pop();else{recycleIfNeeded(w);c=s.deck.pop()}if(!c)return null;if(fromDiscard){const oldOwner=c.owner;c.owner=w;if(c.tag==='returnIfIgnored'&&oldOwner!==w)c.blockedUntilTurn=state.turnNo}c.fromDiscard=fromDiscard;c.age=0;s.hand.push(c);return c}",
    "function acquireDiscardCard(w,indexFromTop=0){const s=sideObj(w),idx=state.discard.length-1-indexFromTop;if(idx<0)return null;const[c]=state.discard.splice(idx,1),oldOwner=c.owner;c.owner=w;if(c.tag==='returnIfIgnored'&&oldOwner!==w)c.blockedUntilTurn=state.turnNo;c.fromDiscard=true;c.age=0;s.hand.push(c);return c}\nfunction drawOne(w,fromDiscard=false){const s=sideObj(w);if(fromDiscard)return acquireDiscardCard(w,0);recycleIfNeeded(w);const c=s.deck.pop();if(!c)return null;c.fromDiscard=false;c.age=0;s.hand.push(c);return c}",
    'common discard acquisition',
)
replace_once(
    "function pushDiscard(c){c.fromDiscard=false;c.contractActive=false;state.discard.push(c);while(state.discard.length>5){const old=state.discard.shift();sideObj(old.owner).spent.push(old);log(`버림패 5장 제한 · ${cardText(old)} → ${old.owner==='player'?'내':'상대'} 소모패.`,'important')}}",
    "function pushDiscard(c){c.fromDiscard=false;c.contractActive=false;state.discard.push(c)}",
    'remove discard cap',
)
replace_once(
    "const removed=state.discard.pop();sideObj(removed.owner).spent.push(removed);c=state.discard.pop();c.owner='player';c.fromDiscard=true;c.age=0;state.player.hand.push(c)",
    "const removed=state.discard.pop();sideObj(removed.owner).spent.push(removed);c=acquireDiscardCard('player',0)",
    'player Black Market path',
)
replace_once(
    "const rm=state.discard.pop();sideObj(rm.owner).spent.push(rm);c=drawOne('enemy',true)",
    "const rm=state.discard.pop();sideObj(rm.owner).spent.push(rm);c=acquireDiscardCard('enemy',0)",
    'AI Black Market path',
)

# No free base board cleanup. Full boards must be managed through attach/recover/card effects.
replace_once(
    "function canRetireStaleRun(owner,index){const s=sideObj(owner),m=meldsOf(owner)[index];return !!m&&m.type==='RUN'&&s.runRetireAvailable&&!s.actedThisTurn}",
    "function canRetireStaleRun(){return false}",
    'disable free RUN retirement check',
)
replace_once(
    "function playerRetireStaleRun(index){if(state.turn!=='player'||state.phase!=='action'||!canRetireStaleRun('player',index))return;retireMeld('player',index,'턴 초반 RUN 자율 정리');state.player.runRetireAvailable=false;render()}",
    "function playerRetireStaleRun(){return false}",
    'disable player free RUN retirement',
)
replace_once(
    "function retireStaleRunAI(w){const s=sideObj(w);if(!s.runRetireAvailable||s.actedThisTurn)return false;const pick=meldsOf(w).findIndex(m=>m.type==='RUN');if(pick>=0){retireMeld(w,pick,'턴 초반 RUN 자율 정리');s.runRetireAvailable=false;return true}return false}",
    "function retireStaleRunAI(){return false}",
    'disable AI free RUN retirement',
)
replace_once(
    "if(meldsOf(w).length>=2){if(w==='enemy')retireMeld(w,0,'새 조합 자리 확보');else return'needRetire'}",
    "if(meldsOf(w).length>=2)return'full'",
    'block new meld on full board',
)
replace_once(
    "function playerRetireMeld(index){if(state.turn!=='player'||state.phase!=='action'||state.player.melds.length<2)return;const cs=selectedCards();if(state.player.newMeldUsed||!meldType(cs)){log('새 조합으로 낼 손패를 먼저 선택해야 정리할 자리를 고를 수 있습니다.','hit');return}retireMeld('player',index,'새 조합 자리 확보');render()}",
    "function playerRetireMeld(){return false}",
    'disable free player meld retirement',
)
replace_once(
    "if(state.player.melds.length>=2){log('공개 조합이 2개입니다. 아래의 “이 조합 정리”로 자리를 먼저 만드세요.','hit');return}",
    "if(state.player.melds.length>=2){log('공개 조합이 2개입니다. 기존 조합에 붙이거나 회수·카드 효과로 전장을 정리해야 새 조합을 만들 수 있습니다.','hit');return}",
    'full board player message',
)
replace_once(
    "const cs=selectedCards(),t=cs.length===3?meldType(cs):null,canRetireForNew=state.turn==='player'&&state.phase==='action'&&!state.player.newMeldUsed&&state.player.melds.length>=2&&!!t;",
    "const cs=selectedCards(),t=cs.length===3?meldType(cs):null,canRetireForNew=false;",
    'hide free meld-retire button',
)
replace_once(
    "else if(state.player.melds.length>=2&&t)meldText='조합 1개 정리 필요';",
    "else if(state.player.melds.length>=2&&t)meldText='공개 조합 2/2 · 새 조합 불가';",
    'full board button text',
)
replace_once(
    "if(!s.newMeldUsed&&bestNewMeld(s.hand))return true;",
    "if(!s.newMeldUsed&&s.melds.length<2&&bestNewMeld(s.hand))return true;",
    'legal action full board check',
)
replace_once(
    "if(!hasAnyLegalAction('enemy'))retireStaleRunAI('enemy');",
    "",
    'remove AI free RUN retirement call',
)
replace_once(
    "nm=!state.enemy.newMeldUsed?bestNewMeld(state.enemy.hand):null",
    "nm=!state.enemy.newMeldUsed&&state.enemy.melds.length<2?bestNewMeld(state.enemy.hand):null",
    'AI full board new meld scoring',
)
replace_once(
    "if(nm&&!state.enemy.newMeldUsed){const r=submitNewMeld('enemy',nm.cards);",
    "if(nm&&!state.enemy.newMeldUsed&&state.enemy.melds.length<2){const r=submitNewMeld('enemy',nm.cards);",
    'AI full board execution',
)

# CORE LETHAL feedback must use the actual target, while returnSwitch can preview the post-return target.
replace_once(
    "function addSwitchPower(w,amount,label='POWER'){amount=Math.max(0,Math.round(amount||0));if(!amount)return 0;const before=state.switchPower;state.switchPower+=amount;state.lastSwitchAdd=amount;state.lastSwitchActor=w;log(`${switchName(w)} ${label} · 누적 위력 +${amount} → ${state.switchPower}.`,'important');fxNode(`POWER +${amount}`,'damage',other(w),20);const target=other(w),need=sideObj(target).hp+sideObj(target).shield;if(before<OVERLOAD&&state.switchPower>=OVERLOAD)combatBanner(`OVERLOAD ${state.switchPower}`,'break',70);else if(before<need&&state.switchPower>=need)combatBanner(`CORE LETHAL ${state.switchPower}`,'burst',70);return amount}",
    "function addSwitchPower(w,amount,label='POWER',targetOverride=null){amount=Math.max(0,Math.round(amount||0));if(!amount)return 0;const before=state.switchPower;state.switchPower+=amount;state.lastSwitchAdd=amount;state.lastSwitchActor=w;log(`${switchName(w)} ${label} · 누적 위력 +${amount} → ${state.switchPower}.`,'important');fxNode(`POWER +${amount}`,'damage',other(w),20);const target=targetOverride||(state.switchTarget!=='neutral'?state.switchTarget:null),need=target?sideObj(target).hp+sideObj(target).shield:Infinity;if(before<OVERLOAD&&state.switchPower>=OVERLOAD)combatBanner(`OVERLOAD ${state.switchPower}`,'break',70);else if(target&&before<need&&state.switchPower>=need)combatBanner(`CORE LETHAL ${state.switchPower}`,'burst',70);return amount}",
    'CORE LETHAL target',
)
replace_once(
    "if(!opts.flat)addSwitchPower(w,amount,label);",
    "if(!opts.flat)addSwitchPower(w,amount,label,other(w));",
    'return target preview',
)

# Card text/logic synchronization.
replace_once(
    "'C10':{n:'연쇄반응',t:'sameMeldBonus',d:'직전 반환과 다른 종류의 조합으로 반환하면 1장 뽑기. 같은 종류면 보호막 10.'}",
    "'C10':{n:'연쇄반응',t:'sameMeldBonus',d:'직전 반환과 다른 종류의 조합으로 반환하면 1장 뽑기. 같은 종류면 보호막 12.'}",
    'C10 shield text',
)
replace_once(
    "function detonate(w,reason='턴 종료'){if(state.gameOver||state.switchTarget!==w||state.switchPower<=0)return 0;const s=sideObj(w);let raw=state.switchPower;if(s.status.vulnerable>0){raw=Math.round(raw*1.25);log(`${switchName(w)} 취약 · 다음 DETONATE +25%.`,'hit');s.status.vulnerable=0}",
    "function detonate(w,reason='턴 종료'){if(state.gameOver||state.switchTarget!==w||state.switchPower<=0)return 0;const s=sideObj(w);let raw=state.switchPower;if(s.status.vulnerable>0){raw=Math.round(raw*1.25);log(`${switchName(w)} 취약 · 다음 DETONATE +25%.`,'hit');s.status.vulnerable=0}if(s.jokerLastDetonateReduction){const cut=Math.min(raw,s.jokerLastDetonateReduction);raw-=cut;s.jokerLastDetonateReduction=0;log(`${switchName(w)} 마지막 웃음 · DETONATE 피해 -${cut}.`,'good');fxNode(`DETONATE -${cut}`,'shield',w,20)}",
    'J2 detonate reduction',
)
replace_once(
    "function triggerRummy(w,lastCards){let reload=6;if(lastCards.some(c=>c.tag==='rummyPlus1')){reload=7;if(state.switchTarget===w)addShield(w,4)}if(lastCards.some(c=>c.tag==='rummyHeal4')){heal(w,Math.ceil(15/RECOVERY_UNIT));applyStatus(w,'regen',1);if(state.switchPower>=60)addShield(w,4)}if(lastCards.some(c=>c.tag==='jokerLast')){drawMany(w,1,false);const s=sideObj(w),cand=s.hand.sort((a,b)=>b.age-a.age)[0];if(cand){removeFromHand(w,[cand]);s.deck.unshift(cand)}}if(w==='player')state.rummy++;drawMany(w,reload,false);if(w==='player')state.playerJustRummied=true;else state.enemyJustRummied=true;combatBanner('RUMMY!','rummy',40);log(`${w==='player'?'YOU':'CPU'} RUMMY! 새 손패 ${reload}장.`,'good');if(w==='player'){state.selected.clear();state.boardSelected.clear();state.target=null;endPlayerTurn()}}",
    "function triggerRummy(w,lastCards,opts={}){let reload=6;const s=sideObj(w),jokerLast=lastCards.some(c=>c.tag==='jokerLast');if(lastCards.some(c=>c.tag==='rummyPlus1')){reload=7;if(state.switchTarget===w)addShield(w,4)}if(lastCards.some(c=>c.tag==='rummyHeal4')){heal(w,Math.ceil(15/RECOVERY_UNIT));applyStatus(w,'regen',1);if(state.switchPower>=60)addShield(w,4)}if(w==='player')state.rummy++;drawMany(w,reload,false);if(jokerLast&&opts.returned){drawMany(w,1,false);const cand=[...s.hand].sort((a,b)=>b.age-a.age)[0];if(cand){removeFromHand(w,[cand]);cand.fromDiscard=false;cand.age=0;s.deck.unshift(cand)}log(`${switchName(w)} 마지막 웃음 · 반환 RUMMY 후 1장 추가 순환.`,'good')}else if(jokerLast&&state.switchTarget===w&&state.switchPower>0){s.jokerLastDetonateReduction=15;log(`${switchName(w)} 마지막 웃음 · 이번 턴 DETONATE 피해 15 감소 준비.`,'good')}if(w==='player')state.playerJustRummied=true;else state.enemyJustRummied=true;combatBanner('RUMMY!','rummy',40);log(`${w==='player'?'YOU':'CPU'} RUMMY! 새 손패 ${reload}장.`,'good');if(w==='player'){state.selected.clear();state.boardSelected.clear();state.target=null;endPlayerTurn()}}",
    'J2 RUMMY behavior',
)
replace_once("triggerRummy(w,cards);return'rummy'", "triggerRummy(w,cards,{returned:false});return'rummy'", 'new meld RUMMY context')
replace_once("triggerRummy(w,cards);return'rummy'", "triggerRummy(w,cards,{returned:returning||fx.forceReturn});return'rummy'", 'attach RUMMY context')
replace_once("triggerRummy('player',[c]);render();", "triggerRummy('player',[c],{returned:false});render();", 'player discard RUMMY context')
replace_once(
    "function turnEnd(w){const s=sideObj(w);s.creditDebt=false;if(state.switchTarget===w&&state.switchPower>0){if(s.graceArmed){s.graceArmed=false;combatBanner('DETONATE DELAY','rummy',30);log(`${switchName(w)} 유예 · 누적 ${state.switchPower}과 SWITCH를 유지하고 다음 자기 턴 종료까지 버팁니다.`,'good')}else detonate(w,'턴 종료')}s.lastDamageTaken=0}",
    "function turnEnd(w){const s=sideObj(w);s.creditDebt=false;if(state.switchTarget===w&&state.switchPower>0){if(s.graceArmed){s.graceArmed=false;combatBanner('DETONATE DELAY','rummy',30);log(`${switchName(w)} 유예 · 누적 ${state.switchPower}과 SWITCH를 유지하고 다음 자기 턴 종료까지 버팁니다.`,'good')}else detonate(w,'턴 종료')}s.jokerLastDetonateReduction=0;s.lastDamageTaken=0}",
    'clear J2 one-turn reduction',
)
replace_once("while(!state.gameOver&&!rummied&&state.enemy.hand.length&&state.enemy.discardsRemaining>0){", "let lastDiscarded=null;while(!state.gameOver&&!rummied&&state.enemy.hand.length&&state.enemy.discardsRemaining>0){", 'AI last discard tracking declaration')
replace_once("removeFromHand('enemy',[d]);if(d.tag==='topDeckChoice'", "lastDiscarded=d;removeFromHand('enemy',[d]);if(d.tag==='topDeckChoice'", 'AI last discard tracking')
replace_once("triggerRummy('enemy',[]);rummied=true", "triggerRummy('enemy',lastDiscarded?[lastDiscarded]:[],{returned:false});rummied=true", 'AI discard RUMMY context')

INDEX.write_text(text, encoding='utf-8')

# Persistent, buildless smoke test: syntax + critical rule invariants.
tests = Path('tests')
tests.mkdir(exist_ok=True)
Path('tests/rules-smoke.mjs').write_text(r'''import fs from 'node:fs';

const html = fs.readFileSync(new URL('../index.html', import.meta.url), 'utf8');
const script = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).join('\n');

function ok(condition, message) {
  if (!condition) throw new Error(message);
  console.log(`PASS: ${message}`);
}

new Function(script);
ok(!html.includes('버림패 5장 제한'), 'discard pile has no five-card cap logic');
ok(!html.includes('공용 버림패 <b id="discardCount">0</b>/5'), 'discard UI has no /5 cap');
ok(html.includes('function canRetireStaleRun(){return false}'), 'free RUN retirement is disabled');
ok(html.includes("if(meldsOf(w).length>=2)return'full'"), 'full public board blocks new meld creation');
ok(html.includes("s.melds.length<2&&bestNewMeld(s.hand)"), 'maintenance/legal-action check respects the two-meld cap');
ok(html.includes('function acquireDiscardCard(w,indexFromTop=0)'), 'discard acquisition uses a shared helper');
ok(html.includes("c=acquireDiscardCard('player',0)"), 'player Black Market second-card path uses shared acquisition');
ok(html.includes("c=acquireDiscardCard('enemy',0)"), 'AI Black Market second-card path uses shared acquisition');
ok(html.includes("typeof unlock==='function'&&!!unlock(p)"), 'invalid saved character IDs cannot crash char unlock checks');
ok(html.includes('같은 종류면 보호막 12.'), 'Chain Reaction text matches its 12-shield implementation');
ok(html.includes('jokerLastDetonateReduction=15'), 'Last Laugh DETONATE reduction is implemented');
ok(html.includes('if(jokerLast&&opts.returned)'), 'Last Laugh bonus cycle requires a returning RUMMY');
ok(html.includes("addSwitchPower(w,amount,label,other(w))"), 'SWITCH returns evaluate CORE LETHAL against the post-return target');
console.log('RUMMY//DUEL rules smoke tests passed.');
''', encoding='utf-8')

print('rules sync patch applied')

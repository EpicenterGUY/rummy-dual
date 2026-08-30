from pathlib import Path

index = Path('index.html')
html = index.read_text(encoding='utf-8')


def bounds(src, name):
    marker = f'function {name}('
    start = src.find(marker)
    if start < 0:
        raise RuntimeError(f'missing function {name}')
    brace = src.find('{', start)
    if brace < 0:
        raise RuntimeError(f'missing body {name}')
    depth = 0
    for i in range(brace, len(src)):
        ch = src[i]
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return start, i + 1
    raise RuntimeError(f'unterminated function {name}')


def get_func(name):
    a, b = bounds(html, name)
    return html[a:b]


def set_func(name, new):
    global html
    a, b = bounds(html, name)
    html = html[:a] + new + html[b:]


def edit_func(name, old, new):
    src = get_func(name)
    if old not in src:
        raise RuntimeError(f'{name}: expected fragment not found: {old[:100]}')
    set_func(name, src.replace(old, new, 1))


# Per-battle full recirculation counter.
edit_func(
    'newGame',
    "state.rewarded=false;drawMany('player',8,false);",
    "state.rewarded=false;state.fullRecirculationCount=0;drawMany('player',8,false);",
)

# Two-sided circulation deadlock safety.
marker = 'function prepareAcquisitionPhase(w)'
if 'function fullRecirculation(' not in html:
    safety = r'''function circulationStalled(w){const s=sideObj(w);return !hasAcquisitionSource(w)&&!s.hand.length&&!anyRecoveryOption(w)}
function circulationCardCount(){let n=state.discard.length;for(const w of['player','enemy']){const s=sideObj(w);n+=s.hand.length+s.deck.length+s.spent.length;for(const m of s.melds)n+=m.cards.length}return n}
function bothCirculationStalled(){return circulationCardCount()>0&&circulationStalled('player')&&circulationStalled('enemy')}
function showCirculationDraw(){const title=document.getElementById('resultTitle'),text=document.getElementById('resultText'),box=document.getElementById('resultUnlocks'),again=document.getElementById('againBtn');if(box){box.style.display='none';box.innerHTML=''}if(again)again.textContent=state.sessionMode==='practice'?'연습전 다시 하기':'다시 하기';if(title){title.textContent=state.sessionMode==='practice'?'연습전 무승부':'무승부';title.className='gold'}if(text)text.textContent='두 번째 완전 순환 정체가 발생했고 남은 코어 수와 현재 코어 체력도 같아 무승부로 종료되었습니다.';if(typeof renderProgress==='function')renderProgress();document.getElementById('overlay')?.classList.add('show')}
function resolveCirculationStalemate(){const p=state.player,e=state.enemy,pc=p.cores||0,ec=e.cores||0;if(pc!==ec){const win=pc>ec;log(`순환 교착 판정 · 남은 코어 ${pc}:${ec} → ${win?'나':'상대'} 승리.`,'important');if(win){e.cores=0;e.hp=0}else{p.cores=0;p.hp=0}checkGameOver();return win?'player':'enemy'}if(p.hp!==e.hp){const win=p.hp>e.hp;log(`순환 교착 판정 · 코어 수 동률, 현재 코어 ${p.hp}:${e.hp} → ${win?'나':'상대'} 승리.`,'important');if(win){e.cores=0;e.hp=0}else{p.cores=0;p.hp=0}checkGameOver();return win?'player':'enemy'}state.gameOver=true;state.phase='over';log('순환 교착 판정 · 남은 코어와 현재 체력까지 동률 → 무승부.','important');const battleId=state.battleId;setTimeout(()=>{if(state.battleId===battleId&&state.gameOver)showCirculationDraw()},500);return'draw'}
function fullRecirculation(reason='양쪽 완전 순환 정체'){if((state.fullRecirculationCount||0)>=1)return resolveCirculationStalemate();const all=[],seen=new Set(),take=c=>{if(!c||seen.has(c.uid))return;seen.add(c.uid);all.push(c)};for(const w of['player','enemy']){const s=sideObj(w);s.hand.forEach(take);s.deck.forEach(take);s.spent.forEach(take);for(const m of s.melds)m.cards.forEach(take);s.hand=[];s.deck=[];s.spent=[];s.melds=[]}state.discard.forEach(take);state.discard=[];for(const c of all){c.fromDiscard=false;c.contractActive=false;c.enteredMeldToken=null;c.recoveredToken=null;c.recoverReturnOverrideToken=null;c.recoverReturnTargets=null;c.blockedUntilTurn=null;c.outlawFreeRecoverAt=null;c.smuggledActive=false;c.age=0;if(c.flexSuitOffSuit)c.flexSuitOffSuit=false;if(c.status)c.status=blankStatus();sideObj(c.owner).deck.push(c)}for(const w of['player','enemy']){const s=sideObj(w);s.deck=shuffle(s.deck);drawMany(w,Math.min(6,s.deck.length),false)}state.fullRecirculationCount=(state.fullRecirculationCount||0)+1;state.target=null;state.selected?.clear?.();state.selectionOrder=[];state.boardSelected?.clear?.();log(`전체 재순환 · ${reason}. 모든 손패·덱·소모패·버림패·공개 조합을 현재 소유자 덱으로 회수해 섞고 각자 최대 6장을 다시 받았습니다. 코어와 스위치는 유지됩니다.`,'important');combatBanner('전체 재순환','rummy',40);return'recycled'}
'''
    html = html.replace(marker, safety + marker, 1)

set_func(
    'prepareAcquisitionPhase',
    r'''function prepareAcquisitionPhase(w){const s=sideObj(w);if(hasAcquisitionSource(w))return'draw';if(!s.hand.length&&anyRecoveryOption(w)){if(s.blockOpponentDiscardNext)s.blockOpponentDiscardNext=false;if(w==='player'&&state.turn==='player'&&state.phase==='draw')state.phase='action';log(`${w==='player'?'내':'상대'} 획득원 0 · 공개 조합의 내 카드를 회수해 순환을 이어갑니다.`,'important');return'action'}if(typeof bothCirculationStalled==='function'&&bothCirculationStalled()&&typeof fullRecirculation==='function'){fullRecirculation('양쪽 모두 획득·회수 불가');if(state.gameOver)return'pass';if(hasAcquisitionSource(w))return'draw';if(s.hand.length){if(w==='player'&&state.turn==='player'&&state.phase==='draw')state.phase='action';return'action'}}if(!s.hand.length){emergencyReleaseMeld(w,'획득원 0 · 순환 정체');if(hasAcquisitionSource(w))return'draw'}if(s.blockOpponentDiscardNext)s.blockOpponentDiscardNext=false;if(w==='player'&&state.turn==='player'&&state.phase==='draw')state.phase='action';if(!s.hand.length&&!anyRecoveryOption(w)){if(w==='player'){state.phase='wait';const battleId=state.battleId,turnToken=state.turnToken;log('순환 가능한 카드가 한 장도 없어 이번 턴을 자동 통과합니다.','important');setTimeout(()=>{if(isLiveCombatSession()&&state.battleId===battleId&&state.turnToken===turnToken&&state.turn==='player'&&!state.gameOver)endPlayerTurn()},360)}else log('상대는 순환 가능한 카드가 없어 획득을 생략합니다.','important');return'pass'}log(`${w==='player'?'내':'상대'} 획득 가능한 카드가 없어 획득 단계를 생략합니다.`,'important');return'action'}''',
)

# J4/J5: current attach may not auto-recover itself. Later valid replacement is marked recovered.
set_func(
    'replaceRedundantJokers',
    r'''function replaceRedundantJokers(targetSide,m,attacher,newCards=[]){if(!newCards.some(c=>!isJoker(c)))return;const added=new Set(newCards.map(c=>c.uid));for(let i=m.cards.length-1;i>=0;i--){const j=m.cards[i];if(!['vacancyJoker','rebelJoker'].includes(j.tag)||added.has(j.uid))continue;const remain=m.cards.filter((_,k)=>k!==i);if(remain.length<3||meldType(remain)!==m.type)continue;m.cards.splice(i,1);if(m.type==='RUN')m.chain=Math.max(0,(m.chain||0)-1);sideObj(j.owner).hand.push(j);j.suppressEffectToken=state.turnToken;j.recoveredToken=state.turnToken;j.recoverReturnOverrideToken=null;j.recoverReturnTargets=null;j.age=0;log(`${j.name}: 실제 카드가 채워져 원주인 손패로 복귀${m.type==='RUN'?' · 체인 -1':''}.`,'good');if(j.tag==='rebelJoker'&&attacher!==j.owner){m.lastAttachToken=state.turnToken;log(`${j.name}: 반역 · 이 조합은 이번 턴 다시 반환에 사용할 수 없습니다.`,'important')}}markSetCompletion(m,targetSide)}''',
)
edit_func('attachCards', 'if(willBaseReturn&&!recoveredCardsCanReturn(cards,state.turnToken)){', 'if(willBaseReturn&&!recoveredCardsCanReturn(cards,state.turnToken,m)){')
edit_func('attachCards', 'replaceRedundantJokers(targetSide,m,w);', 'replaceRedundantJokers(targetSide,m,w,cards);')

# Destination-bound same-turn recovery-return exceptions.
set_func(
    'recoveredCardCanReturn',
    "function recoveredCardCanReturn(c,turnToken,targetMeld=null){if(c.recoveredToken!==turnToken)return true;if(c.recoverReturnOverrideToken!==turnToken)return false;if(Array.isArray(c.recoverReturnTargets))return c.recoverReturnTargets.includes(targetMeld);return true}",
)
set_func(
    'recoveredCardsCanReturn',
    "function recoveredCardsCanReturn(cards,turnToken,targetMeld=null){return cards.every(c=>recoveredCardCanReturn(c,turnToken,targetMeld))}",
)
if 'function legalRecoveryReturnTargets(' not in html:
    after = get_func('recoveredCardsCanReturn')
    helpers = r'''
function legalRecoveryReturnTargets(w,c,sourceMeld,opts={}){const out=[],s=sideObj(w),sides=opts.ownOnly?[w]:[w,other(w)],requiredType=opts.requiredType||null;for(const targetSide of sides)for(const m of meldsOf(targetSide)){if(m===sourceMeld||requiredType&&m.type!==requiredType)continue;if(m.createdToken===state.turnToken&&targetSide===w)continue;const continuation=typeof canContinueReturnedRun==='function'&&canContinueReturnedRun(w,m);if(m.lastAttachToken===state.turnToken&&!continuation)continue;if(meldType(m.cards.concat(c))!==m.type)continue;const wouldReturn=m.type==='RUN'||(m.type==='SET'&&m.cards.length===3);if(wouldReturn&&!continuation&&(!canSideReturn(w)||s.returnedSwitchThisTurn))continue;out.push(m)}return out}
function grantRecoveryReturnOverride(w,c,sourceMeld,opts={}){const targets=legalRecoveryReturnTargets(w,c,sourceMeld,opts);c.recoverReturnTargets=targets;c.recoverReturnOverrideToken=targets.length?state.turnToken:null;return targets.length}
'''
    html = html.replace(after, after + helpers, 1)

set_func(
    'freeRecoverFromMeld',
    r'''function freeRecoverFromMeld(w,m,exclude=[],opts={}){if(meldFixedActive(m))return null;const ex=new Set(exclude.map(c=>c.uid));for(let i=0;i<m.cards.length;i++){const c=m.cards[i];if(ex.has(c.uid)||c.owner!==w||c.enteredMeldToken===state.turnToken||cardFixedActive(c))continue;const remain=m.cards.filter((_,j)=>j!==i);if(remain.length<3||meldType(remain)!==m.type)continue;m.cards.splice(i,1);if(m.type==='RUN')m.chain=Math.max(0,(m.chain||0)-1);sideObj(w).hand.push(c);sideObj(w).rummyRecoveryPending=false;c.suppressEffectToken=state.turnToken;c.recoveredToken=state.turnToken;c.recoverReturnOverrideToken=null;c.recoverReturnTargets=null;c.age=0;markSetCompletion(m,w);if(opts.allowReturnReuse&&typeof grantRecoveryReturnOverride==='function')grantRecoveryReturnOverride(w,c,m,{requiredType:opts.requiredType||null,ownOnly:!!opts.ownOnly});log(`무료 회수: ${cardText(c)}${m.type==='RUN'?' · 체인 -1':''}.`,'good');return c}return null}''',
)
edit_func('playerRecover', "c.recoverReturnOverrideToken=freeReason==='tuner'?state.turnToken:null;c.age=0;", "c.recoverReturnOverrideToken=null;c.recoverReturnTargets=null;c.age=0;")
edit_func('playerRecover', 'markSetCompletion(m,plan.side);', "markSetCompletion(m,plan.side);if(freeReason==='tuner'&&typeof grantRecoveryReturnOverride==='function')grantRecoveryReturnOverride('player',c,m,{requiredType:m.type==='SET'?'RUN':'SET',ownOnly:true});")
edit_func('executeRecoverAI', "c.recoverReturnOverrideToken=freeReason==='tuner'?state.turnToken:null;c.age=0;", "c.recoverReturnOverrideToken=null;c.recoverReturnTargets=null;c.age=0;")
edit_func('executeRecoverAI', 'markSetCompletion(m,plan.side);', "markSetCompletion(m,plan.side);if(freeReason==='tuner'&&typeof grantRecoveryReturnOverride==='function')grantRecoveryReturnOverride(w,c,m,{requiredType:m.type==='SET'?'RUN':'SET',ownOnly:true});")
edit_func('canAttachTo', 'if(wouldReturn&&!recoveredCardsCanReturn(cards,state.turnToken))return false;', 'if(wouldReturn&&!recoveredCardsCanReturn(cards,state.turnToken,m))return false;')
edit_func('attachReason', "if(wouldReturn&&!recoveredCardsCanReturn(cards,state.turnToken))return'이번 턴 회수한 카드는 버스트/체인 반환에 재사용 불가';", "if(wouldReturn&&!recoveredCardsCanReturn(cards,state.turnToken,m))return'회수 효과가 허용한 다른 조합에만 같은 턴 반환 재사용 가능';")

# Legal-action audit: same returned RUN continuation remains legal.
set_func(
    'anyAttachOption',
    r'''function anyAttachOption(w){const s=sideObj(w),hand=s.hand.filter(c=>c.blockedUntilTurn!==state.turnNo);for(let k=1;k<=Math.min(4,hand.length);k++)for(const cs of combinations(hand,k))for(const targetSide of[w,other(w)])for(const m of meldsOf(targetSide)){const continuation=typeof canContinueReturnedRun==='function'&&canContinueReturnedRun(w,m);if(m.lastAttachToken===state.turnToken&&!continuation)continue;if(m.createdToken===state.turnToken&&targetSide===w)continue;const combined=m.cards.concat(cs),type=meldType(combined);if(type!==m.type)continue;const wouldReturn=m.type==='RUN'||(m.type==='SET'&&m.cards.length===3&&combined.length===4);if(wouldReturn&&!recoveredCardsCanReturn(cs,state.turnToken,m))continue;if(wouldReturn&&!continuation&&(!canSideReturn(w)||s.returnedSwitchThisTurn))continue;return true}return false}''',
)
set_func(
    'bestExtensionFromHand',
    r'''function bestExtensionFromHand(w,hand,mustUid=null){const s=sideObj(w);let best=null;for(const targetSide of[w,other(w)])for(let i=0;i<meldsOf(targetSide).length;i++){const m=meldsOf(targetSide)[i],continuation=typeof canContinueReturnedRun==='function'&&canContinueReturnedRun(w,m);if(m.lastAttachToken===state.turnToken&&!continuation)continue;if(m.createdToken===state.turnToken&&targetSide===w)continue;for(let k=1;k<=Math.min(4,hand.length);k++)for(const cs of combinations(hand,k)){if(mustUid!=null&&!cs.some(c=>c.uid===mustUid))continue;if(cs.some(c=>c.blockedUntilTurn===state.turnNo))continue;const combined=m.cards.concat(cs);if(meldType(combined)!==m.type)continue;const wouldReturn=m.type==='RUN'||(m.type==='SET'&&m.cards.length===3&&combined.length===4);if(wouldReturn&&!recoveredCardsCanReturn(cs,state.turnToken,m))continue;if(wouldReturn&&!continuation&&(!canSideReturn(w)||s.returnedSwitchThisTurn))continue;let sc=0;if(m.type==='SET')sc=m.cards.length===3&&m.cards.length+k===4?24:0;else for(let z=1;z<=k;z++)sc+=chainDamage((m.chain||0)+z);if(targetSide===other(w))sc+=4;if(targetSide===other(w)&&cs.some(c=>c.tag==='enemyAttachBonus'))sc+=15;if(!best||sc>best.score)best={cards:cs,side:targetSide,index:i,score:sc}}}return best}''',
)

# Low-hand protection: only the final/base mandatory discard may be waived.
if 'function canSkipBaseDiscard(' not in html:
    pos = html.find('function playerDiscard()')
    if pos < 0:
        raise RuntimeError('missing playerDiscard insertion point')
    html = html[:pos] + "function canSkipBaseDiscard(w){const s=sideObj(w);return state.sessionMode!=='tutorial'&&s.hand.length>0&&s.hand.length<=3&&(s.discardsRemaining||1)===1}\n" + html[pos:]

set_func(
    'playerDiscard',
    r'''function playerDiscard(){if(state.turn!=='player'||state.phase!=='action')return;const cs=selectedCards();if(!cs.length&&typeof canSkipBaseDiscard==='function'&&canSkipBaseDiscard('player')){state.player.discardsRemaining=0;state.selected.clear();state.selectionOrder=[];state.boardSelected.clear();state.target=null;log(`저손패 보호 · 손패 ${state.player.hand.length}장이라 기본 버리기 1회를 생략하고 턴을 종료합니다.`,'important');endPlayerTurn();render();return}if(cs.length!==1){log('버릴 카드는 정확히 1장 선택하세요. 저손패 보호가 켜졌다면 선택을 해제하고 턴 종료를 누르세요.','hit');return}const c=cs[0];if(!tutorialAllows('discard',{card:c})){tutorialReject('discard');return}const r=rectSnapshot(document.querySelector(`.cardBtn[data-uid="${c.uid}"]`));removeFromHand('player',[c]);state.selected.clear();state.selectionOrder=[];state.boardSelected.clear();let discard=true;if(c.tag==='topDeckChoice'&&confirm('예약 발송: 버림패 대신 이 카드를 내 덱 위에 놓을까요?')){c.fromDiscard=false;c.contractActive=false;state.player.deck.push(c);discard=false;log(`${c.name}: 버림패 대신 내 덱 위로 예약 발송.`,'important');flashPile('deckPile')}else{const pawn=state.field?.tag==='pawnshop'&&c.fromDiscard;pushDiscard(c);state.lastPlayerDiscardRank=c.rank;log(`YOU 버리기: ${cardText(c)}${c.named?' ['+c.name+']':''}`);armSafetyPin('player',c);if(pawn)addShield('player',3)}state.player.discardsRemaining=Math.max(0,(state.player.discardsRemaining||1)-1);if(tutorialCheckProgress('discard',{card:c}))return;if(state.player.hand.length===0){triggerRummy('player',[c],{returned:false});render();if(discard)animateDiscardMove(c,r);return}if(state.player.discardsRemaining>0){if(typeof canSkipBaseDiscard==='function'&&canSkipBaseDiscard('player'))log(`저손패 보호 · 추가 버리기 해결 완료. 남은 기본 버리기는 선택 없이 생략할 수 있습니다.`,'good');else log(`외상 거래 · 추가로 ${state.player.discardsRemaining}장 더 버리세요.`,'hit');render();if(discard)animateDiscardMove(c,r);return}endPlayerTurn();render();if(discard)animateDiscardMove(c,r)}''',
)

edit_func(
    'updateButtons',
    "document.getElementById('discardBtn').disabled=!(action&&cs.length===1);",
    "const discardBtn=document.getElementById('discardBtn'),lowHandSkip=action&&typeof canSkipBaseDiscard==='function'&&canSkipBaseDiscard('player')&&cs.length===0;discardBtn.disabled=!(action&&(cs.length===1||lowHandSkip));discardBtn.textContent=lowHandSkip?'턴 종료 · 버리기 면제':'선택 1장 버리기';",
)

# AI acquisition and low-hand discard handling.
edit_func('aiTurn', "state.lastEnemyUsedDiscard=false;prepareAcquisitionPhase('enemy');let fromDiscard=false", "state.lastEnemyUsedDiscard=false;const acquisition=prepareAcquisitionPhase('enemy');if(state.gameOver){render();return}let fromDiscard=false")
edit_func('aiTurn', "let c=null;if(fromDiscard&&state.field?.tag==='blackMarket'", "let c=null;if(acquisition==='draw'){if(fromDiscard&&state.field?.tag==='blackMarket'")
edit_func('aiTurn', "else c=fromDiscard?drawOne('enemy',true):drawOne('enemy',false);if(state.enemy.blockOpponentDiscardNext)", "else c=fromDiscard?drawOne('enemy',true):drawOne('enemy',false)}if(state.enemy.blockOpponentDiscardNext)")
edit_func('aiTurn', "while(!state.gameOver&&!rummied&&state.enemy.hand.length&&state.enemy.discardsRemaining>0){let d=null;", "while(!state.gameOver&&!rummied&&state.enemy.hand.length&&state.enemy.discardsRemaining>0){if(typeof canSkipBaseDiscard==='function'&&canSkipBaseDiscard('enemy')){state.enemy.discardsRemaining=0;log(`상대 저손패 보호 · 손패 ${state.enemy.hand.length}장이라 기본 버리기 1회를 생략합니다.`,'important');break}let d=null;")

# Rules / UX wording.
old_turn = '<div class="ruleBlock"><h3>기본 턴</h3><p><b>개인 덱 약 30장 · 시작 손패 8장 · 최대 3장 멀리건.</b> 턴은 <b>1장 획득 → 행동 → 1장 버리기</b>. 획득은 내 덱 맨 위 또는 공용 버림패 맨 위 중 하나입니다. <b>공용 버림패에는 장수 제한이 없고</b>, 기본 획득은 맨 위 카드만 가져옵니다.</p></div>'
new_turn = '<div class="ruleBlock"><h3>기본 턴</h3><p><b>개인 덱 약 30장 · 시작 손패 8장 · 최대 3장 멀리건.</b> 기본 턴은 <b>1장 획득 → 행동 → 1장 버리기</b>입니다. 단, 행동을 마쳤을 때 손패가 <b>1~3장</b>이고 기본 버리기 1회만 남았다면 <b>저손패 보호</b>로 그 기본 버리기를 생략하고 턴을 끝낼 수 있습니다. 카드 효과가 만든 추가 버리기는 먼저 해결해야 합니다.</p></div>'
if old_turn not in html:
    raise RuntimeError('rules: base turn text not found')
html = html.replace(old_turn, new_turn, 1)

old_cycle = '<div class="ruleBlock"><h3>덱 · 버림패 · 소모패</h3><p><b>공용 버림패</b>는 양쪽이 맨 위 카드를 가져올 수 있는 공용 공간입니다. <b>소모패</b>는 각자의 자동 재순환 대기 더미라서 기본적으로 직접 사용할 수 없습니다. 개인 덱의 마지막 카드를 뽑으면 <b>그 플레이어의 소모패 + 공용 버림패에 남아 있는 현재 그 플레이어 소유 카드</b>만 회수해 함께 섞어 새 덱을 만듭니다. 상대 소유 카드와 공개 조합 카드는 그대로 남습니다. <b>덱·소모패·사용 가능한 공용 버림패가 모두 0장</b>이면 획득을 생략하고 행동을 계속합니다. 손패도 0장이고 합법적인 회수로도 풀 수 없는 완전 정체에서는 <b>내 카드가 포함된 공개 조합 1개를 긴급 정리</b>해 순환을 복구합니다.</p></div>'
new_cycle = '<div class="ruleBlock"><h3>덱 · 버림패 · 소모패</h3><p><b>공용 버림패</b>는 양쪽이 맨 위 카드를 가져올 수 있는 공용 공간입니다. <b>소모패</b>는 각자의 자동 재순환 대기 더미입니다. 개인 덱이 비면 <b>그 플레이어의 소모패 + 공용 버림패의 현재 그 플레이어 소유 카드</b>를 회수해 새 덱을 만듭니다. 한쪽만 완전히 막히면 기존처럼 회수 또는 내 카드가 포함된 공개 조합 1개 긴급 정리로 순환을 복구합니다. <b>양쪽 모두 획득·회수로 순환을 이어갈 수 없는 완전 정체</b>라면 <b>전체 재순환</b>: 손패·덱·소모패·공용 버림패·모든 공개 조합을 현재 소유자별 덱으로 되돌려 섞고 각자 최대 6장을 다시 받습니다. 공개 조합/체인은 사라지지만 <b>코어·현재 체력·보호막·스위치 대상·누적 위력은 유지</b>됩니다. 같은 전투에서 두 번째 전체 정체가 오면 남은 코어 → 현재 코어 체력 순으로 승부를 판정하고 모두 같으면 무승부입니다.</p></div>'
if old_cycle not in html:
    raise RuntimeError('rules: circulation text not found')
html = html.replace(old_cycle, new_cycle, 1)

old_recover = '<li><b>회수:</b> 턴당 1회, 공개 조합의 내가 제어하는 카드 1장을 손으로. 빼도 조합이 유지되어야 하며 이번 턴 공개한 카드는 회수 불가. <b>회수한 카드는 같은 턴 버스트/체인 반환 재료로 다시 사용할 수 없습니다.</b> 단, 카드 효과가 명시적으로 허용하면 예외입니다.</li>'
new_recover = '<li><b>회수:</b> 턴당 1회, 공개 조합의 내가 제어하는 카드 1장을 손으로. 빼도 조합이 유지되어야 하며 이번 턴 공개한 카드는 회수 불가. <b>회수한 카드는 같은 턴 버스트/체인 반환 재료로 다시 사용할 수 없습니다.</b> 카드 효과가 예외를 주더라도 그 효과가 허용한 <b>다른 목적지 조합</b>에만 같은 턴 반환 재사용할 수 있습니다.</li>'
if old_recover not in html:
    raise RuntimeError('rules: recovery text not found')
html = html.replace(old_recover, new_recover, 1)
html = html.replace(
    '<div class="handSub">세트·런을 만들거나 공개 조합에 붙여 스위치를 넘기세요.</div>',
    '<div class="handSub">세트·런을 만들거나 공개 조합에 붙이세요. 손패 3장 이하는 기본 버리기 면제 가능.</div>',
    1,
)

index.write_text(html, encoding='utf-8')

# README sync.
readme_path = Path('README.md')
readme = readme_path.read_text(encoding='utf-8')
readme = readme.replace(
    "- When a personal deck is empty, only that player's spent pile is shuffled into a new deck. The shared discard pile stays public.",
    "- When a personal deck is empty, recycle that player's spent pile plus cards in the shared discard currently owned by that player; opponent-owned discard and public meld cards stay in place.",
)
anchor = '- Normal maintenance cycles 1 card; when completely stuck, up to 2 cards.\n'
if '- Low-hand protection:' not in readme:
    readme = readme.replace(
        anchor,
        anchor
        + '- Low-hand protection: when only the base discard remains and the hand is 1–3 cards, that base discard may be skipped; extra discards created by card effects must be paid first.\n'
        + '- If both players are simultaneously unable to acquire or recover cards, perform one full recirculation: return all cards from hands/decks/spent/shared discard/public melds to their current owners, shuffle, and deal up to 6 each. CORE/HP/shield/SWITCH power and target remain. A second full stall is resolved by remaining CORE, then current CORE HP, then draw.\n',
    )
readme = readme.replace(
    'unless a named effect explicitly allows it.',
    'unless a named effect explicitly allows it, and that exception is bound to the destination meld(s) allowed by that effect.',
)
readme_path.write_text(readme, encoding='utf-8')

# ROADMAP sync.
road_path = Path('ROADMAP.md')
road = road_path.read_text(encoding='utf-8')
road = road.replace(
    '- [x] Zero-source circulation safety: if deck/spent/usable shared discard are all empty, skip acquisition; if the player also has no hand and no legal recovery, retire one public meld containing their card as a last-resort circulation release, without duplicating cards',
    '- [x] Zero-source circulation safety: one-sided stalls skip acquisition / use legal recovery / release one owned public meld as needed; simultaneous two-sided stalls perform one full current-owner recirculation while preserving CORE and SWITCH state, with a second stall resolved by CORE → current HP → draw',
)
if '- [x] Low-hand protection:' not in road:
    road = road.replace(
        '- [x] RUMMY refills 6\n',
        '- [x] RUMMY refills 6\n- [x] Low-hand protection: with 1–3 cards and only the base discard remaining, the base discard may be skipped; card-effect extra discards are still paid first\n',
    )
if 'Close Vacancy/Rebel Joker self-recovery' not in road:
    road = road.replace(
        '## M2 — Confirmed bug fixes\n',
        '## M2 — Confirmed bug fixes\n- [x] Close Vacancy/Rebel Joker self-recovery loops: a Joker added by the current attach cannot auto-replace itself, and any later auto-return is marked recovered for the turn\n- [x] Make stuck-state legality include same-RUN continuation after the one physical SWITCH return\n- [x] Bind same-turn recovered-card return exceptions to the destination melds authorized by the granting effect\n',
    )
if 'Full-recirculation / low-hand / Joker-loop' not in road:
    road = road.replace(
        '## M3 — Regression tests\n',
        '## M3 — Regression tests\n- [x] Full-recirculation / low-hand / Joker-loop / continuation-legality / destination-bound recovery safety regressions\n',
    )
road_path.write_text(road, encoding='utf-8')

# Focused regression suite.
test = r'''import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);const brace=script.indexOf('{',start);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
function install(ctx,...names){for(const n of names)vm.runInContext(source(n),ctx)}
function c(uid,owner='player',extra={}){return{uid,owner,suit:'C',rank:'4',age:0,...extra}}

{
 const player={hand:[]},enemy={hand:[]},state={player,enemy,turnToken:5};
 const ctx=vm.createContext({console,Set,Math,state});ctx.sideObj=w=>w==='player'?player:enemy;ctx.isJoker=x=>x.suit==='J';ctx.meldType=cards=>cards.filter(x=>x.suit!=='J').length>=3?'RUN':null;ctx.markSetCompletion=()=>{};ctx.log=()=>{};install(ctx,'replaceRedundantJokers');
 const j=c('j','player',{suit:'J',tag:'vacancyJoker',name:'빈자리 조커'}),m={type:'RUN',chain:1,cards:[c('4'),c('5'),c('6'),j]};
 ctx.replaceRedundantJokers('player',m,'player',[j]);
 ok(m.cards.includes(j)&&player.hand.length===0,'newly attached vacancy Joker does not auto-recover itself');
 const real=c('7','player',{suit:'C',rank:'7'});m.cards.push(real);ctx.replaceRedundantJokers('player',m,'player',[real]);
 ok(!m.cards.includes(j)&&player.hand.includes(j),'pre-existing vacancy Joker can be replaced by a newly attached real card');
 ok(j.recoveredToken===state.turnToken&&j.recoverReturnOverrideToken==null,'auto-returned Joker is marked recovered and has no same-turn return override');
}

{
 const card={uid:'8',suit:'H',rank:'8',owner:'player',blockedUntilTurn:null,recoveredToken:null,recoverReturnOverrideToken:null};
 const player={hand:[card],deck:[c('d')],spent:[],melds:[],newMeldUsed:false,returnedSwitchThisTurn:true,maintenanceUsed:false};
 const enemy={hand:[],deck:[],spent:[],melds:[],newMeldUsed:false,returnedSwitchThisTurn:false};
 const m={type:'RUN',cards:[{suit:'H',rank:'5'},{suit:'H',rank:'6'},{suit:'H',rank:'7'}],chain:1,lastAttachToken:9,returnAttachToken:9,createdToken:null};enemy.melds=[m];
 const state={player,enemy,discard:[],turnNo:2,turnToken:9,switchTarget:'enemy',gameOver:false,turn:'player',phase:'action'};
 const ctx=vm.createContext({console,Set,Map,Array,Math,state});ctx.sideObj=w=>w==='player'?player:enemy;ctx.other=w=>w==='player'?'enemy':'player';ctx.meldsOf=w=>ctx.sideObj(w).melds;ctx.canSideReturn=w=>state.switchTarget==='neutral'||state.switchTarget===w;ctx.canContinueReturnedRun=(w,x)=>w==='player'&&x===m;ctx.meldType=cards=>cards.every(x=>x.suit==='H')&&new Set(cards.map(x=>Number(x.rank))).size===cards.length?'RUN':null;ctx.meldFixedActive=()=>false;ctx.cardFixedActive=()=>false;install(ctx,'combinations','bestNewMeld','bestNewMeldForTurn','recoveredCardCanReturn','recoveredCardsCanReturn','anyAttachOption','canFinishRun','hasAnyLegalAction','ownedRecycleCount','maintenanceLimit');
 ok(ctx.anyAttachOption('player'),'same returned RUN continuation counts as a legal attach after physical SWITCH return');
 ok(ctx.maintenanceLimit('player')===1,'legal same-RUN continuation prevents false two-card stuck maintenance');
}

{
 const a={},b={},card={recoveredToken:3,recoverReturnOverrideToken:3,recoverReturnTargets:[b]};
 const ctx=vm.createContext({console,Array});install(ctx,'recoveredCardCanReturn','recoveredCardsCanReturn');
 ok(!ctx.recoveredCardCanReturn(card,3,a),'destination-bound recovered card cannot return through an unauthorized meld');
 ok(ctx.recoveredCardCanReturn(card,3,b),'destination-bound recovered card may return through its authorized meld');
}

{
 const player={hand:[1,2,3],discardsRemaining:1},enemy={hand:[],discardsRemaining:1},state={player,enemy,sessionMode:'battle'};
 const ctx=vm.createContext({console,state});ctx.sideObj=w=>w==='player'?player:enemy;install(ctx,'canSkipBaseDiscard');
 ok(ctx.canSkipBaseDiscard('player'),'1–3 card hand may waive the base discard');
 player.discardsRemaining=2;ok(!ctx.canSkipBaseDiscard('player'),'extra discard debt prevents low-hand waiver until paid');
 player.discardsRemaining=1;player.hand.push(4);ok(!ctx.canSkipBaseDiscard('player'),'four-card hand still owes the normal discard');
 player.hand=[1,2,3];state.sessionMode='tutorial';ok(!ctx.canSkipBaseDiscard('player'),'tutorial keeps its scripted discard step deterministic');
}

{
 const pCards=Array.from({length:7},(_,i)=>c(`p${i}`,'player'));
 const eCards=Array.from({length:7},(_,i)=>c(`e${i}`,'enemy'));
 const player={hand:[],deck:[],spent:[],melds:[{type:'RUN',cards:pCards}],cores:2,hp:37,shield:5};
 const enemy={hand:[],deck:[],spent:[],melds:[{type:'SET',cards:eCards}],cores:1,hp:44,shield:2};
 const state={player,enemy,discard:[],fullRecirculationCount:0,switchTarget:'player',switchPower:73,selected:new Set(),selectionOrder:[],boardSelected:new Set(),target:null,gameOver:false};
 const ctx=vm.createContext({console,Set,Math,state});ctx.sideObj=w=>w==='player'?player:enemy;ctx.shuffle=x=>x;ctx.blankStatus=()=>({});ctx.drawMany=(w,n)=>{const s=ctx.sideObj(w);let k=0;while(k<n&&s.deck.length){s.hand.push(s.deck.pop());k++}return k};ctx.log=()=>{};ctx.combatBanner=()=>{};ctx.resolveCirculationStalemate=()=>{throw new Error('unexpected second stall')};install(ctx,'fullRecirculation');
 ctx.fullRecirculation('test');
 ok(player.hand.length===6&&enemy.hand.length===6&&player.deck.length===1&&enemy.deck.length===1,'full recirculation redeals up to six and leaves the remainder in each current owner deck');
 ok(player.melds.length===0&&enemy.melds.length===0&&state.discard.length===0,'full recirculation clears public melds and shared discard');
 ok(state.switchTarget==='player'&&state.switchPower===73&&player.cores===2&&player.hp===37&&player.shield===5,'full recirculation preserves SWITCH, CORE, HP and shield state');
 ok(state.fullRecirculationCount===1,'full recirculation is counted for second-stall protection');
}

ok(source('attachCards').includes('replaceRedundantJokers(targetSide,m,w,cards)'),'attach resolution passes current new cards into Joker replacement guard');
ok(source('freeRecoverFromMeld').includes('grantRecoveryReturnOverride'),'free swap recovery records authorized return destinations');
ok(source('playerRecover').includes('ownOnly:true')&&source('executeRecoverAI').includes('ownOnly:true'),'Tuner recovery binds its exception to own opposite-type destination melds for player and AI');
ok(html.includes('저손패 보호')&&html.includes('전체 재순환'),'rules UI documents low-hand protection and full recirculation');
console.log('Safety hardening regression passed.');
'''
Path('tests/safety-hardening.mjs').write_text(test, encoding='utf-8')

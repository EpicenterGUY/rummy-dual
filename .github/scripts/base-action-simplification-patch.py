from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
INDEX=ROOT/'index.html'
README=ROOT/'README.md'
ROAD=ROOT/'ROADMAP.md'
M0R=ROOT/'docs'/'M0R_MELD_EXPANSION.md'
UX=ROOT/'docs'/'NEW_USER_UX_TERMS.md'
M0R_TEST=ROOT/'tests'/'m0r-meld-expansion.mjs'
FINAL_TEST=ROOT/'tests'/'final-rule-audit.mjs'


def replace_once(text,old,new,label):
    if old not in text:
        if new in text:return text
        raise SystemExit(f'missing anchor: {label}')
    return text.replace(old,new,1)


def insert_before_once(text,anchor,block,marker,label):
    if marker in text:return text
    if anchor not in text:raise SystemExit(f'missing anchor: {label}')
    return text.replace(anchor,block+anchor,1)

h=INDEX.read_text(encoding='utf-8')

# --- player controls: short verbs + conditional cleanup ---
h=replace_once(h,
'''<div class="controls"><button id="meldBtn" class="pixelBtn primary">새 조합 내기</button><button id="attachBtn" class="pixelBtn goldBtn">선택 카드 이어붙이기</button><button id="recoverBtn" class="pixelBtn">공개 카드 회수</button><button id="maintenanceBtn" class="pixelBtn" hidden>정비</button><button id="discardBtn" class="pixelBtn redBtn">선택 1장 버리기</button><button id="clearBtn" class="pixelBtn">선택 해제</button></div>''',
'''<div class="controls"><button id="meldBtn" class="pixelBtn primary">새 조합</button><button id="attachBtn" class="pixelBtn goldBtn">붙이기</button><button id="recoverBtn" class="pixelBtn">회수</button><button id="maintenanceBtn" class="pixelBtn" hidden>정비</button><button id="cleanupBtn" class="pixelBtn" hidden>정리</button><button id="discardBtn" class="pixelBtn redBtn">버리기</button><button id="clearBtn" class="pixelBtn">선택 해제</button></div>''','action buttons')

# --- player-facing rulebook ---
h=replace_once(h,
'''<div class="ruleBlock"><h3>런 · 체인</h3><p>새 런은 같은 무늬의 연속 3장으로 시작하고 체인 0입니다. 기존 런 연장은 <b>+10 → +15 → +20 → +25</b>이며 이후에도 +25입니다. <b>체인 4 이상인 내 런은 내 턴에 선택적으로 「런 완주」해 슬롯을 비울 수 있고, 완주하지 않으면 계속 이어갈 수 있습니다.</b> 한 행동에서 여러 장을 붙이면 순서대로 모두 계산합니다. A-2-3, Q-K-A 가능 / K-A-2 불가.</p></div>''',
'''<div class="ruleBlock"><h3>런 · 체인</h3><p>새 런은 같은 무늬의 연속 3장으로 시작하고 체인 0입니다. 기존 런 연장은 <b>+10 → +15 → +20 → +25</b>이며 이후에도 +25입니다. <b>기본 붙이기는 턴당 1회</b>지만, 한 번의 붙이기에 합법적으로 이어지는 여러 장을 함께 넣으면 카드마다 체인 위력을 순서대로 모두 계산합니다. <b>체인 4 이상인 내 런은 내 턴에 선택적으로 「런 완주」해 슬롯을 비울 수 있고, 완주하지 않으면 이후 연장은 계속 +25입니다.</b> A-2-3, Q-K-A 가능 / K-A-2 불가.</p></div>''','rulebook run')
h=replace_once(h,
'''<div class="ruleBlock"><h3>공동 전장</h3><p>내 카드는 <b>상대 공개 조합에도</b> 붙일 수 있습니다. 누가 조합을 만들었는지가 아니라 <b>누가 버스트/체인을 발생시켰는지</b>가 반환자를 결정합니다. 이번 턴 자신이 새로 만든 조합에는 같은 턴 다시 붙일 수 없습니다. 각 플레이어의 공개 조합은 <b>최대 3개</b>입니다. 조합을 자유롭게 버릴 수는 없지만, 체인 4 이상인 런은 제어자가 자기 턴에 <b>런 완주</b>로 정리할 수 있습니다.</p></div>''',
'''<div class="ruleBlock"><h3>공동 전장</h3><p>내 카드는 <b>상대 공개 조합에도</b> 붙일 수 있습니다. 누가 조합을 만들었는지가 아니라 <b>누가 버스트/체인을 발생시켰는지</b>가 반환자를 결정합니다. 이번 턴 자신이 새로 만든 조합에는 같은 턴 붙일 수 없습니다. 각 플레이어의 자기 공개 조합은 <b>세트+런 합산 최대 3개</b>이며, 상대 조합에 들어간 내 카드는 내 슬롯을 차지하지 않습니다. 내 3칸이 모두 찼다면 자기 턴에 1회, 이번 턴 만든 조합과 고정된 조합을 제외한 내 조합 하나를 <b>정리</b>해 슬롯을 비울 수 있습니다. 정리는 위력과 스위치를 바꾸지 않습니다.</p></div>''','rulebook shared board')
h=replace_once(h,
'''<div class="ruleBlock"><h3>반환 제한</h3><p>한 플레이어의 한 턴에 <b>스위치가 실제로 이동하는 것은 기본 1회</b>입니다. 다만 반환에 사용한 <b>같은 런</b>은 그 턴에 계속 이어붙일 수 있으며, 추가 연장의 체인 위력은 누적되지만 스위치는 다시 이동하지 않습니다. 다른 런/세트로 새 반환을 만드는 것은 불가합니다. 회수·정비·버림패 조작·방어 등 비공격 행동은 계속 가능합니다.</p></div>''',
'''<div class="ruleBlock"><h3>기본 행동 횟수</h3><p><b>새 조합은 두 번, 붙이기는 한 번, 내 필드는 세 칸.</b> 새 조합·붙이기·회수·정비·조건부 정리·런 완주는 정해진 순서 없이 자유롭게 섞어 사용할 수 있습니다. 네임드 카드가 명시적으로 추가 행동을 주면 그 카드가 예외를 만듭니다.</p></div><div class="ruleBlock"><h3>반환 제한</h3><p>한 플레이어의 한 턴에 <b>스위치가 실제로 이동하는 것은 기본 1회</b>입니다. 기본 붙이기도 턴당 1회이며, 여러 장을 붙이고 싶다면 <b>한 번의 붙이기 행동에 함께 선택</b>합니다. 카드 효과가 「추가 붙이기 1회」를 주는 경우 추가 체인/버스트 위력은 누적되지만 스위치는 두 번째로 이동하지 않습니다. 회수·정비·정리·버림패 조작·방어 등 비공격 행동은 계속 가능합니다.</p></div>''','rulebook return limit')
h=replace_once(h,
'''<span>고정 · 조합/카드 · 다음 소유자 턴 종료까지 회수·강탈·절단 등 이동 불가</span>''',
'''<span>고정 · 조합/카드 · 다음 소유자 턴 종료까지 회수·강탈·절단·자발적 정리 등 이동 불가</span>''','fixed status wording')

# --- named redesigns whose old text depended on repeated same-RUN base attach ---
h=replace_once(h,
'''C5':{n:'연결고리',t:'connectionLink',d:'런에 붙일 때 그 런의 내 제어 카드 1장을 무료 회수할 수 있다. 빼도 런은 유효해야 하며, 그 런에는 이번 턴 한 번 더 붙일 수 있다.'}''',
'''C5':{n:'연결고리',t:'connectionLink',d:'런에 붙일 때 그 런의 내 제어 카드 1장을 무료 회수할 수 있다. 빼도 런은 유효해야 한다. 이 행동을 해결한 뒤 이번 턴 추가 붙이기 1회를 얻는다. 추가 붙이기는 스위치를 다시 이동시키지 않는다.'}''','connection link text')
h=replace_once(h,
'''J5':{n:'반역자 조커',t:'rebelJoker',d:'상대 공개 조합에도 와일드로 붙일 수 있다. 실제 카드로 교체되면 원주인 손으로 돌아오고 그 조합은 그 턴 다시 스위치를 반환할 수 없다.'}''',
'''J5':{n:'반역자 조커',t:'rebelJoker',d:'상대 공개 조합에도 와일드로 붙일 수 있다. 실제 카드로 교체되면 원주인 손으로 돌아오고, 교체한 플레이어가 이번 턴 가진 추가 붙이기 허용을 잃는다.'}''','rebel joker text')

# --- global attach action contract ---
helpers='''function attachAccess(w){const s=sideObj(w),used=Math.max(0,s.attachCount||0),extra=Math.max(0,s.extraAttachRemaining||0);if(used<1)return{allowed:true,extra:false,used,extraRemaining:extra};return{allowed:extra>0,extra:true,used,extraRemaining:extra}}\nfunction consumeAttachUse(w,access=attachAccess(w)){if(!access?.allowed)return false;const s=sideObj(w);s.attachCount=Math.max(0,s.attachCount||0)+1;if(access.extra)s.extraAttachRemaining=Math.max(0,(s.extraAttachRemaining||0)-1);return true}\nfunction grantExtraAttach(w,amount=1,source=null){const s=sideObj(w),n=Math.max(0,Math.round(amount||0));if(!n)return false;s.extraAttachRemaining=Math.max(s.extraAttachRemaining||0,n);if(typeof log==='function')log(`${source?.name||'카드 효과'}: 이번 턴 추가 붙이기 ${n}회 허용.`,'good');return true}\n'''
h=insert_before_once(h,'function bestNewMeldForTurn(w,hand=sideObj(w).hand)',helpers,'function attachAccess(w)','attach action helpers')

h=replace_once(h,
'''function canContinueReturnedRun(w,m){return !!m&&m.type==='RUN'&&m.rebelReturnBlockedToken!==state.turnToken&&m.returnAttachToken===state.turnToken&&sideObj(w).returnedSwitchThisTurn&&state.switchTarget===other(w)}\n''','', 'remove same-run continuation helper')

h=replace_once(h,
'''function canTargetAttachMeld(side,index){\n  if(state.turn!=='player'||state.phase!=='action')return false;\n  const m=meldsOf(side)[index];\n  if(!m||(m.createdToken===state.turnToken&&side==='player'))return false;\n  const continuation=canContinueReturnedRun('player',m);\n  if(m.lastAttachToken===state.turnToken&&!continuation)return false;\n  const wouldReturn=m.type==='RUN'||(m.type==='SET'&&m.cards.length===3);\n  if(!wouldReturn)return false;\n  if(!continuation&&(!canSideReturn('player')||state.player.returnedSwitchThisTurn))return false;\n  return true;\n}''',
'''function canTargetAttachMeld(side,index){\n  if(state.turn!=='player'||state.phase!=='action')return false;\n  const m=meldsOf(side)[index],access=attachAccess('player');\n  if(!access.allowed||!m||(m.createdToken===state.turnToken&&side==='player'))return false;\n  const wouldReturn=m.type==='RUN'||(m.type==='SET'&&m.cards.length===3);\n  if(!wouldReturn)return false;\n  if(!access.extra&&(!canSideReturn('player')||state.player.returnedSwitchThisTurn))return false;\n  return true;\n}''','canTargetAttachMeld')

old_can_attach='''function canAttachTo(side,index,cards=selectedCards()){\n  if(state.turn!=='player'||state.phase!=='action'||!cards.length)return false;\n  if(cards.some(c=>c.blockedUntilTurn===state.turnNo))return false;\n  const m=meldsOf(side)[index];\n  if(!m||(m.createdToken===state.turnToken&&side==='player'))return false;\n  const continuation=canContinueReturnedRun('player',m);\n  if(m.lastAttachToken===state.turnToken&&!continuation)return false;\nconst rankPlans=typeof legalRankChoicePlansForAttach==='function'?legalRankChoicePlansForAttach(m,cards):null;if(rankPlans?rankPlans.length===0:meldType(m.cards.concat(cards))!==m.type)return false;\n  const wouldReturn=m.type==='RUN'||(m.type==='SET'&&m.cards.length===3&&m.cards.length+cards.length===4);\n  if(wouldReturn&&!recoveredCardsCanReturn(cards,state.turnToken,m))return false;\n  if(wouldReturn&&!continuation&&!canSideReturn('player'))return false;\n  if(wouldReturn&&!continuation&&state.player.returnedSwitchThisTurn)return false;'''
new_can_attach='''function canAttachTo(side,index,cards=selectedCards()){\n  if(state.turn!=='player'||state.phase!=='action'||!cards.length)return false;\n  if(cards.some(c=>c.blockedUntilTurn===state.turnNo))return false;\n  const m=meldsOf(side)[index],access=attachAccess('player');\n  if(!access.allowed||!m||(m.createdToken===state.turnToken&&side==='player'))return false;\nconst rankPlans=typeof legalRankChoicePlansForAttach==='function'?legalRankChoicePlansForAttach(m,cards):null;if(rankPlans?rankPlans.length===0:meldType(m.cards.concat(cards))!==m.type)return false;\n  const wouldReturn=m.type==='RUN'||(m.type==='SET'&&m.cards.length===3&&m.cards.length+cards.length===4);\n  if(wouldReturn&&!recoveredCardsCanReturn(cards,state.turnToken,m))return false;\n  if(wouldReturn&&!access.extra&&!canSideReturn('player'))return false;\n  if(wouldReturn&&!access.extra&&state.player.returnedSwitchThisTurn)return false;'''
h=replace_once(h,old_can_attach,new_can_attach,'canAttachTo global limit')

h=replace_once(h,
'''  const continuation=canContinueReturnedRun('player',m);\n  if(m.lastAttachToken===state.turnToken&&!continuation)return'이번 턴 이 조합의 붙이기 처리가 이미 끝남';\n  const wouldReturn=m.type==='RUN'||(m.type==='SET'&&m.cards.length===3&&m.cards.length+cards.length===4);\n  if(wouldReturn&&!recoveredCardsCanReturn(cards,state.turnToken,m))return'회수 효과가 허용한 다른 조합에만 같은 턴 반환 재사용 가능';\n  if(wouldReturn&&!continuation&&!canSideReturn('player'))return'스위치가 상대에게 있음 · 다른 조합으로 추가 반환 불가';\n  if(wouldReturn&&!continuation&&state.player.returnedSwitchThisTurn)return'이번 턴 스위치 반환 사용함';''',
'''  const access=attachAccess('player');\n  if(!access.allowed)return'기본 붙이기 1회 사용 완료';\n  const wouldReturn=m.type==='RUN'||(m.type==='SET'&&m.cards.length===3&&m.cards.length+cards.length===4);\n  if(wouldReturn&&!recoveredCardsCanReturn(cards,state.turnToken,m))return'회수 효과가 허용한 목적지에만 같은 턴 반환 재사용 가능';\n  if(wouldReturn&&!access.extra&&!canSideReturn('player'))return'스위치가 상대에게 있음 · 기본 붙이기 반환 불가';\n  if(wouldReturn&&!access.extra&&state.player.returnedSwitchThisTurn)return'이번 턴 정상 스위치 반환 사용함';''','attachReason')

# legal recovery-return destination must never bypass the global attach-use gate.
h=replace_once(h,
'''function legalRecoveryReturnTargets(w,c,sourceMeld,opts={}){const out=[],s=sideObj(w),sides=opts.ownOnly?[w]:[w,other(w)],requiredType=opts.requiredType||null;for(const targetSide of sides)for(const m of meldsOf(targetSide)){if(m===sourceMeld||requiredType&&m.type!==requiredType)continue;if(m.createdToken===state.turnToken&&targetSide===w)continue;const continuation=typeof canContinueReturnedRun==='function'&&canContinueReturnedRun(w,m);if(m.lastAttachToken===state.turnToken&&!continuation)continue;if(meldType(m.cards.concat(c))!==m.type)continue;const wouldReturn=m.type==='RUN'||(m.type==='SET'&&m.cards.length===3);if(wouldReturn&&!continuation&&(!canSideReturn(w)||s.returnedSwitchThisTurn))continue;out.push(m)}return out}''',
'''function legalRecoveryReturnTargets(w,c,sourceMeld,opts={}){const out=[],s=sideObj(w),sides=opts.ownOnly?[w]:[w,other(w)],requiredType=opts.requiredType||null,access=attachAccess(w);if(!access.allowed)return out;for(const targetSide of sides)for(const m of meldsOf(targetSide)){if(m===sourceMeld||requiredType&&m.type!==requiredType)continue;if(m.createdToken===state.turnToken&&targetSide===w)continue;if(meldType(m.cards.concat(c))!==m.type)continue;const wouldReturn=m.type==='RUN'||(m.type==='SET'&&m.cards.length===3);if(wouldReturn&&!access.extra&&(!canSideReturn(w)||s.returnedSwitchThisTurn))continue;out.push(m)}return out}''','legal recovery targets')

h=replace_once(h,
'''function tunerReadyForRecovery(w,targetSide,m,c){const s=sideObj(w);if(!s||targetSide!==w||s.flags?.tuner||!m||!c)return false;const own=meldsOf(w);if(!own.some(mm=>mm.cards.some(x=>x.owner===w&&x.tag==='alternateBonus')))return false;if(!own.some(mm=>mm.type==='SET')||!own.some(mm=>mm.type==='RUN'))return false;const destType=m.type==='SET'?'RUN':m.type==='RUN'?'SET':null;if(!destType)return false;return own.some(tm=>{if(tm===m||tm.type!==destType||tm.lastAttachToken===state.turnToken||tm.createdToken===state.turnToken)return false;if(meldType(tm.cards.concat(c))!==tm.type)return false;const wouldReturn=tm.type==='RUN'||(tm.type==='SET'&&tm.cards.length===3);return !wouldReturn||(canSideReturn(w)&&!s.returnedSwitchThisTurn)})}''',
'''function tunerReadyForRecovery(w,targetSide,m,c){const s=sideObj(w),access=attachAccess(w);if(!s||!access.allowed||targetSide!==w||s.flags?.tuner||!m||!c)return false;const own=meldsOf(w);if(!own.some(mm=>mm.cards.some(x=>x.owner===w&&x.tag==='alternateBonus')))return false;if(!own.some(mm=>mm.type==='SET')||!own.some(mm=>mm.type==='RUN'))return false;const destType=m.type==='SET'?'RUN':m.type==='RUN'?'SET':null;if(!destType)return false;return own.some(tm=>{if(tm===m||tm.type!==destType||tm.createdToken===state.turnToken)return false;if(meldType(tm.cards.concat(c))!==tm.type)return false;const wouldReturn=tm.type==='RUN'||(tm.type==='SET'&&tm.cards.length===3);return !wouldReturn||access.extra||(canSideReturn(w)&&!s.returnedSwitchThisTurn)})}''','tuner recovery attach gate')

# AI/search helpers use the same global action gate and still enumerate multi-card attaches.
h=replace_once(h,
'''function anyAttachOption(w){const s=sideObj(w),hand=s.hand.filter(c=>c.blockedUntilTurn!==state.turnNo);for(let k=1;k<=Math.min(6,hand.length);k++)for(const cs of combinations(hand,k))for(const targetSide of[w,other(w)])for(const m of meldsOf(targetSide)){const continuation=typeof canContinueReturnedRun==='function'&&canContinueReturnedRun(w,m);if(m.lastAttachToken===state.turnToken&&!continuation)continue;if(m.createdToken===state.turnToken&&targetSide===w)continue;const planned=typeof legalRankChoicePlansForAttach==='function'?legalRankChoicePlansForAttach(m,cs):null,candidates=planned??[];if(planned===null){const combined=m.cards.concat(cs),type=meldType(combined);if(type===m.type)candidates.push({plan:null,type,projected:cs,totalLength:combined.length})}for(const cand of candidates){if(cand.type!==m.type)continue;const combinedLength=cand.totalLength||m.cards.length+cs.length,wouldReturn=m.type==='RUN'||(m.type==='SET'&&m.cards.length===3&&combinedLength===4);if(wouldReturn&&!recoveredCardsCanReturn(cs,state.turnToken,m))continue;if(wouldReturn&&!continuation&&(!canSideReturn(w)||s.returnedSwitchThisTurn))continue;return true}}return false}''',
'''function anyAttachOption(w){const s=sideObj(w),access=attachAccess(w),hand=s.hand.filter(c=>c.blockedUntilTurn!==state.turnNo);if(!access.allowed)return false;for(let k=1;k<=Math.min(6,hand.length);k++)for(const cs of combinations(hand,k))for(const targetSide of[w,other(w)])for(const m of meldsOf(targetSide)){if(m.createdToken===state.turnToken&&targetSide===w)continue;const planned=typeof legalRankChoicePlansForAttach==='function'?legalRankChoicePlansForAttach(m,cs):null,candidates=planned??[];if(planned===null){const combined=m.cards.concat(cs),type=meldType(combined);if(type===m.type)candidates.push({plan:null,type,projected:cs,totalLength:combined.length})}for(const cand of candidates){if(cand.type!==m.type)continue;const combinedLength=cand.totalLength||m.cards.length+cs.length,wouldReturn=m.type==='RUN'||(m.type==='SET'&&m.cards.length===3&&combinedLength===4);if(wouldReturn&&!recoveredCardsCanReturn(cs,state.turnToken,m))continue;if(wouldReturn&&!access.extra&&(!canSideReturn(w)||s.returnedSwitchThisTurn))continue;return true}}return false}''','anyAttachOption')

old_best_ext='''function bestExtensionFromHand(w,hand,mustUid=null){const s=sideObj(w);let best=null;for(const targetSide of[w,other(w)])for(let i=0;i<meldsOf(targetSide).length;i++){const m=meldsOf(targetSide)[i],continuation=typeof canContinueReturnedRun==='function'&&canContinueReturnedRun(w,m);if(m.lastAttachToken===state.turnToken&&!continuation)continue;if(m.createdToken===state.turnToken&&targetSide===w)continue;for(let k=1;k<=Math.min(6,hand.length);k++)for(const cs of combinations(hand,k)){if(mustUid!=null&&!cs.some(c=>c.uid===mustUid))continue;if(cs.some(c=>c.blockedUntilTurn===state.turnNo))continue;const planned=typeof legalRankChoicePlansForAttach==='function'?legalRankChoicePlansForAttach(m,cs):null,candidates=planned??[];if(planned===null){const combined=m.cards.concat(cs),type=meldType(combined);if(type===m.type)candidates.push({plan:null,type,projected:cs,totalLength:combined.length,label:'legacy'})}for(const cand of candidates){if(cand.type!==m.type)continue;const projected=cand.projected||cs,combined=m.cards.concat(projected),combinedLength=cand.totalLength||combined.length,wouldReturn=m.type==='RUN'||(m.type==='SET'&&m.cards.length===3&&combinedLength===4);if(wouldReturn&&!recoveredCardsCanReturn(cs,state.turnToken,m))continue;if(wouldReturn&&!continuation&&(!canSideReturn(w)||s.returnedSwitchThisTurn))continue;let sc=0;if(m.type==='SET')sc=m.cards.length===3&&combinedLength===4?24:0;else for(let z=1;z<=k;z++)sc+=chainDamage((m.chain||0)+z);const powerGain=sc;if(typeof opponentMeldAttachBias==='function')sc+=opponentMeldAttachBias(w,targetSide,m,combined,k);else if(targetSide===other(w))sc+=4;if(targetSide===other(w)&&cs.some(c=>c.tag==='enemyAttachBonus'))sc+=15;if(typeof themeAIAttachBias==='function')sc+=themeAIAttachBias(w,targetSide,m,projected,powerGain);if(!best||sc>best.score)best={cards:cs,side:targetSide,index:i,score:sc,rankPlan:cand.plan||null,rankPlanLabel:cand.label||null,projectedCards:projected}}}}return best}'''
new_best_ext='''function bestExtensionFromHand(w,hand,mustUid=null){const s=sideObj(w),access=attachAccess(w);let best=null;if(!access.allowed)return null;for(const targetSide of[w,other(w)])for(let i=0;i<meldsOf(targetSide).length;i++){const m=meldsOf(targetSide)[i];if(m.createdToken===state.turnToken&&targetSide===w)continue;for(let k=1;k<=Math.min(6,hand.length);k++)for(const cs of combinations(hand,k)){if(mustUid!=null&&!cs.some(c=>c.uid===mustUid))continue;if(cs.some(c=>c.blockedUntilTurn===state.turnNo))continue;const planned=typeof legalRankChoicePlansForAttach==='function'?legalRankChoicePlansForAttach(m,cs):null,candidates=planned??[];if(planned===null){const combined=m.cards.concat(cs),type=meldType(combined);if(type===m.type)candidates.push({plan:null,type,projected:cs,totalLength:combined.length,label:'legacy'})}for(const cand of candidates){if(cand.type!==m.type)continue;const projected=cand.projected||cs,combined=m.cards.concat(projected),combinedLength=cand.totalLength||combined.length,wouldReturn=m.type==='RUN'||(m.type==='SET'&&m.cards.length===3&&combinedLength===4);if(wouldReturn&&!recoveredCardsCanReturn(cs,state.turnToken,m))continue;if(wouldReturn&&!access.extra&&(!canSideReturn(w)||s.returnedSwitchThisTurn))continue;let sc=0;if(m.type==='SET')sc=m.cards.length===3&&combinedLength===4?24:0;else for(let z=1;z<=k;z++)sc+=chainDamage((m.chain||0)+z);const powerGain=sc;if(typeof opponentMeldAttachBias==='function')sc+=opponentMeldAttachBias(w,targetSide,m,combined,k);else if(targetSide===other(w))sc+=4;if(targetSide===other(w)&&cs.some(c=>c.tag==='enemyAttachBonus'))sc+=15;if(typeof themeAIAttachBias==='function')sc+=themeAIAttachBias(w,targetSide,m,projected,powerGain);if(access.extra)sc-=2;if(!best||sc>best.score)best={cards:cs,side:targetSide,index:i,score:sc,rankPlan:cand.plan||null,rankPlanLabel:cand.label||null,projectedCards:projected}}}}return best}'''
h=replace_once(h,old_best_ext,new_best_ext,'bestExtensionFromHand')

h=replace_once(h,
'''function discardHelpsAI(c){const h=state.enemy.hand;for(let k=2;k<=Math.min(5,h.length);k++)for(const hs of combinations(h,k))if(meldType(hs.concat(c)))return true;for(const targetSide of ['enemy','player'])for(const m of meldsOf(targetSide)){if(m.lastAttachToken===state.turnToken)continue;for(let k=0;k<=Math.min(3,h.length);k++)for(const hs of combinations(h,k))if(meldType(m.cards.concat([c,...hs]))===m.type)return true}return false}''',
'''function discardHelpsAI(c){const h=state.enemy.hand;for(let k=2;k<=Math.min(5,h.length);k++)for(const hs of combinations(h,k))if(meldType(hs.concat(c)))return true;if(!attachAccess('enemy').allowed)return false;for(const targetSide of ['enemy','player'])for(const m of meldsOf(targetSide)){if(m.createdToken===state.turnToken&&targetSide==='enemy')continue;for(let k=0;k<=Math.min(3,h.length);k++)for(const hs of combinations(h,k))if(meldType(m.cards.concat([c,...hs]))===m.type)return true}return false}''','discardHelpsAI')

# Attach resolution: one global base use; named extra uses add power without a second physical SWITCH move.
h=replace_once(h,
'''  const s=sideObj(w),m=meldsOf(targetSide)[targetIndex];\n  if(!m||(m.createdToken===state.turnToken&&targetSide===w))return false;\n  const continuation=canContinueReturnedRun(w,m);\n  if(m.lastAttachToken===state.turnToken&&!continuation)return false;''',
'''  const s=sideObj(w),m=meldsOf(targetSide)[targetIndex],access=attachAccess(w);\n  if(!access.allowed||!m||(m.createdToken===state.turnToken&&targetSide===w))return false;''','attachCards header')
h=replace_once(h,
'''  if(willBaseReturn&&!continuation&&!canSideReturn(w))return false;\n  if(willBaseReturn&&!continuation&&s.returnedSwitchThisTurn)return false;''',
'''  if(willBaseReturn&&!access.extra&&!canSideReturn(w))return false;\n  if(willBaseReturn&&!access.extra&&s.returnedSwitchThisTurn)return false;''','attachCards return gate')
h=replace_once(h,
'''  if(typeof recordM11BActionCounterfactual==='function')recordM11BActionCounterfactual(w,cards,type,targetSide,m);\n  removeFromHand(w,cards);''',
'''  if(typeof recordM11BActionCounterfactual==='function')recordM11BActionCounterfactual(w,cards,type,targetSide,m);\n  if(!consumeAttachUse(w,access))return false;\n  removeFromHand(w,cards);''','consume attach use')
h=replace_once(h,
'''  if(typeof recordMeldActionMetric==='function')recordMeldActionMetric(w,type,cards.length,targetSide,{continuation});''',
'''  if(typeof recordMeldActionMetric==='function')recordMeldActionMetric(w,type,cards.length,targetSide,{extraAttach:access.extra});''','attach metric')
h=replace_once(h,
'''  m.lastAttachToken=state.turnToken;\n  m.lastTouchedOwnerStart=sideObj(targetSide).turnStarts+(w===targetSide?0:1);''',
'''  m.lastTouchedOwnerStart=sideObj(targetSide).turnStarts+(w===targetSide?0:1);''','remove per-meld attach token')
h=replace_once(h,
'''  const returning=base>0&&!continuation;\n  const ctx={isNew:false,isAttach:true,targetOwner:targetSide,totalLength:m.cards.length,beforeLength:beforeLen,beforeChain,effectSeen:new Set(),meld:m,willReturn:returning};''',
'''  const returning=base>0&&!access.extra;\n  const ctx={isNew:false,isAttach:true,targetOwner:targetSide,totalLength:m.cards.length,beforeLength:beforeLen,beforeChain,effectSeen:new Set(),meld:m,willReturn:returning,extraAttach:access.extra};''','attach returning context')
h=replace_once(h,
'''    const forceReturn=!continuation&&!!fx.forceReturn;''',
'''    const forceReturn=!access.extra&&!!fx.forceReturn;''','force return gate')
h=replace_once(h,
'''      attackEvent(w,finalBase?[{amount:finalBase,label,kind:type==='SET'?'burst':'chain'}]:[],{bonus,label,flatReturn:fx.flatReturn,forceReturn:true});\n      m.returnAttachToken=state.turnToken;\n      \n    }else if(continuation&&finalBase>0){combatBanner(label,'chain',0);addSwitchPower(w,finalBase,`${label} · 연속 연장`,other(w));log(`${w==='player'?'나':'상대'} 같은 런 연속 연장 · 스위치 추가 이동 없이 체인 위력 +${finalBase}.`,'important')}\n    cards.forEach(c=>c.fromDiscard=false);\n    if(cards.some(c=>c.tag==='connectionLink')&&type==='RUN'&&m.extraAttachGrantedToken!==state.turnToken){m.extraAttachGrantedToken=state.turnToken;m.lastAttachToken=null}''',
'''      attackEvent(w,finalBase?[{amount:finalBase,label,kind:type==='SET'?'burst':'chain'}]:[],{bonus,label,flatReturn:fx.flatReturn,forceReturn:true});\n    }else if(access.extra&&(finalBase>0||bonus>0)){const extraPower=Math.max(0,finalBase+bonus);combatBanner(`${label} · 추가 붙이기`,'chain',0);if(extraPower)addSwitchPower(w,extraPower,`${label} · 카드 효과 추가 붙이기`,other(w));log(`${w==='player'?'나':'상대'} 카드 효과 추가 붙이기 · 누적 위력 +${extraPower} · 스위치 이동 없음.`,'important')}\n    cards.forEach(c=>c.fromDiscard=false);\n    if(cards.some(c=>c.tag==='connectionLink')&&type==='RUN')grantExtraAttach(w,1,cards.find(c=>c.tag==='connectionLink'))''','attach finish branch')

for old,new,label in [
("returned:returning||forceReturn,continuation,phase:'afterResolve'","returned:returning||forceReturn,extraAttach:access.extra,phase:'afterResolve'",'onAttach event'),
("returned:returning||forceReturn,continuation});if(typeof refreshPointBlankClashMeld","returned:returning||forceReturn,extraAttach:access.extra});if(typeof refreshPointBlankClashMeld",'zero sight event'),
("returned:returning||forceReturn,continuation});if(typeof emitMailRouteArrivals","returned:returning||forceReturn,extraAttach:access.extra});if(typeof emitMailRouteArrivals",'point blank event')]:
    h=replace_once(h,old,new,label)
h=replace_once(h,
'''    const actionNote=continuation?' · 연속 체인':returning||forceReturn?' · 스위치 반환':' · 구조 변경';''',
'''    const actionNote=access.extra?' · 추가 붙이기 · 스위치 이동 없음':returning||forceReturn?' · 스위치 반환':' · 구조 변경';''','attach action log')

# Meld objects no longer carry base-rule per-target attach continuation state.
h=h.replace(',lastAttachToken:null,extraAttachGrantedToken:null,lastTouchedOwnerStart:',',lastTouchedOwnerStart:')
h=h.replace(',lastAttachToken:null,extraAttachGrantedToken:null,lastTouchedOwnerStart:0',',lastTouchedOwnerStart:0')

# Rebel Joker now counters named extra-attach allowance instead of an obsolete base continuation.
h=replace_once(h,
'''if(j.tag==='rebelJoker'){m.lastAttachToken=state.turnToken;m.rebelReturnBlockedToken=state.turnToken;log(`${j.name}: 반역 · 이 조합은 이번 턴 다시 스위치를 반환하거나 연속 연장할 수 없습니다.`,'important')}''',
'''if(j.tag==='rebelJoker'){sideObj(attacher).extraAttachRemaining=0;log(`${j.name}: 반역 · 교체한 플레이어의 이번 턴 추가 붙이기 허용을 제거합니다.`,'important')}''','rebel joker resolution')

# Turn/session state for global attach and conditional cleanup.
h=replace_once(h,
'''s.actedThisTurn=false;s.newMeldCount=0;s.recoveredThisTurn=false;s.maintenanceUsed=false;s.returnedSwitchThisTurn=false;''',
'''s.actedThisTurn=false;s.newMeldCount=0;s.attachCount=0;s.extraAttachRemaining=0;s.meldCleanupUsed=false;s.recoveredThisTurn=false;s.maintenanceUsed=false;s.returnedSwitchThisTurn=false;''','turn start state')
h=replace_once(h,
'''s.actedThisTurn=false;s.newMeldCount=0;s.recoveredThisTurn=false;s.maintenanceUsed=false;s.returnedSwitchThisTurn=false;s.discardsRemaining=1;''',
'''s.actedThisTurn=false;s.newMeldCount=0;s.attachCount=0;s.extraAttachRemaining=0;s.meldCleanupUsed=false;s.recoveredThisTurn=false;s.maintenanceUsed=false;s.returnedSwitchThisTurn=false;s.discardsRemaining=1;''','tutorial reset state')
h=replace_once(h,
'''actedThisTurn:false,newMeldCount:0,recoveredThisTurn:false,maintenanceUsed:false,returnedSwitchThisTurn:false,discardsRemaining:1''',
'''actedThisTurn:false,newMeldCount:0,attachCount:0,extraAttachRemaining:0,meldCleanupUsed:false,recoveredThisTurn:false,maintenanceUsed:false,returnedSwitchThisTurn:false,discardsRemaining:1''','new game side state')

# --- full-board cleanup action ---
cleanup_helpers='''function canCleanupMeld(w,index){const s=sideObj(w),m=meldsOf(w)[index];if(state.gameOver||state.turn!==w||!m||s.melds.length!==3||s.meldCleanupUsed)return false;if(w==='player'&&state.phase!=='action')return false;if(m.createdToken===state.turnToken)return false;if(meldFixedActive(m)||m.cards.some(cardFixedActive))return false;return true}\nfunction cleanupMeld(w,index){if(!canCleanupMeld(w,index))return false;const s=sideObj(w),m=meldsOf(w)[index],beforePower=state.switchPower,beforeTarget=state.switchTarget;s.meldCleanupUsed=true;s.actedThisTurn=true;retireMeld(w,index,'자발적 조합 정리');if(w==='player'){state.target=null;state.boardSelected.clear();state.selected.clear();state.selectionOrder=[]}combatBanner('조합 정리 · +0 · 스위치 유지','status',20);log(`${switchName(w)} 조합 정리 · ${m.type==='SET'?'세트':'런'} 퇴장 · 위력 +0 · 스위치 이동 없음.`,'important');if(state.switchPower!==beforePower||state.switchTarget!==beforeTarget)throw new Error('cleanupMeld changed SWITCH state');if(w==='player'&&typeof render==='function')render();return true}\nfunction cleanupMeldAIScore(w,m){if(!m)return-Infinity;let score=0;if(m.type==='SET'&&m.cards.length===3)score-=22;if(m.type==='RUN'){score+=m.cards.length===3?12:3;score-=Math.max(0,m.chain||0)*7;if((m.chain||0)>=4)score-=18}if(typeof isZeroSightTarget==='function'&&(isZeroSightTarget(w,m)||isZeroSightTarget(other(w),m)))score-=6;if(typeof isPointBlankClash==='function'&&isPointBlankClash(w,m))score-=6;if(typeof isMailRouteDestination==='function'&&isMailRouteDestination(w,m))score-=6;return score}\nfunction bestCleanupMeldAI(w){const s=sideObj(w);if(!s||s.melds.length!==3||s.meldCleanupUsed||(s.newMeldCount||0)>=2)return null;const next=bestNewMeldForTurn(w);if(!next)return null;let best=null;for(let i=0;i<s.melds.length;i++){const m=s.melds[i];if(!canCleanupMeld(w,i)||canFinishRun(w,i))continue;const score=cleanupMeldAIScore(w,m)+Math.max(0,next.score||0)-14;if(score>0&&(!best||score>best.score))best={index:i,score,meld:m,next}}return best}\nfunction playerCleanupMeld(){if(state.turn!=='player'||state.phase!=='action')return false;const s=state.player;if(s.melds.length!==3){log('조합 정리는 내 공개 조합 3칸이 모두 찼을 때만 사용할 수 있습니다.','hit');return false}if(s.meldCleanupUsed){log('기본 조합 정리는 턴당 1회입니다.','hit');return false}const list=s.melds.map((m,index)=>({m,index})).filter(x=>canCleanupMeld('player',x.index));if(!list.length){log('정리 가능한 조합이 없습니다. 이번 턴 만든 조합과 고정된 조합은 정리할 수 없습니다.','hit');return false}const confirm=entry=>requestEffectChoice({kicker:'기본 행동 · 정리',title:'조합 정리 확인',text:'이 조합을 정리하면 위력은 +0이고 스위치는 이동하지 않습니다. 카드들은 일반 조합 퇴장 규칙에 따라 이동합니다.',options:[{key:'confirm',label:'정리하기',detail:`${entry.m.type==='SET'?'세트':'런'} ${entry.m.cards.length}장 · 슬롯 1개 확보`}],allowSkip:true,skipLabel:'취소',onChoose:o=>{if(o)cleanupMeld('player',meldsOf('player').indexOf(entry.m))}});return requestEffectChoice({kicker:'기본 행동 · 정리',title:'정리할 내 공개 조합을 선택하세요',text:'내 필드 3칸이 모두 찼을 때 턴당 1회 사용할 수 있습니다. 이번 턴 만든 조합과 고정된 조합은 제외됩니다.',options:list.map(x=>({key:`cleanup:${x.index}`,label:`${x.index+1} · ${x.m.type==='SET'?'세트':'런'} · ${x.m.cards.length}장`,detail:x.m.type==='RUN'?`체인 ${x.m.chain||0} · 위력 +0`:'버스트 준비 포기 · 위력 +0',entry:x})),allowSkip:true,skipLabel:'취소',onChoose:o=>{if(o?.entry)confirm(o.entry)}})}\n'''
h=insert_before_once(h,'function bestFinishRunAI(w)',cleanup_helpers,'function canCleanupMeld(w,index)','meld cleanup helpers')

h=replace_once(h,
'''function hasAnyLegalAction(w){const s=sideObj(w);if(s.melds.length<3&&bestNewMeldForTurn(w))return true;if(s.melds.some((m,i)=>canFinishRun(w,i)))return true;return anyAttachOption(w)}''',
'''function hasAnyLegalAction(w){const s=sideObj(w);if(s.melds.length<3&&bestNewMeldForTurn(w))return true;if(s.melds.some((m,i)=>canFinishRun(w,i)))return true;if(bestCleanupMeldAI(w))return true;return anyAttachOption(w)}''','hasAnyLegalAction cleanup')

# AI action loop: finish a mature RUN first; otherwise clear only a low-value full-board meld when it enables a real new meld.
h=replace_once(h,
'''const actionCap=state.sessionMode==='practice'?4:6;let actions=Math.max(0,resumeState.actionsUsed||0),rummied=!!resumeState.rummied;while(actions++<actionCap&&!state.gameOver&&!rummied){const ex=bestExtension('enemy'),nm=state.enemy.melds.length<3?bestNewMeldForTurn('enemy'):null,rc=bestRecoverAI('enemy'),fr=bestFinishRunAI('enemy');''',
'''const actionCap=state.sessionMode==='practice'?4:6;let actions=Math.max(0,resumeState.actionsUsed||0),rummied=!!resumeState.rummied;while(actions++<actionCap&&!state.gameOver&&!rummied){const ex=bestExtension('enemy'),nm=state.enemy.melds.length<3?bestNewMeldForTurn('enemy'):null,rc=bestRecoverAI('enemy'),fr=bestFinishRunAI('enemy'),cl=bestCleanupMeldAI('enemy');''','AI cleanup plan')
h=replace_once(h,
'''if(fr){finishRun('enemy',fr.index);continue}if(nm&&state.enemy.melds.length<3){''',
'''if(fr){finishRun('enemy',fr.index);continue}if(cl){cleanupMeld('enemy',cl.index);continue}if(nm&&state.enemy.melds.length<3){''','AI cleanup execution')

# Player errors, previews and HUD speak in action-count terms, not target-meld continuation terms.
h=replace_once(h,
'''function attachPreviewText(p){if(!p)return'';const seq=p.steps.map(x=>`${cardText(x.card)} +${x.amount}`).join(' → ');return`${p.type==='SET'?'버스트':'체인'} ${seq} · 합계 +${p.total} · 스위치 → 상대`}''',
'''function attachPreviewText(p){if(!p)return'';const seq=p.steps.map(x=>`${cardText(x.card)} +${x.amount}`).join(' → '),extra=typeof attachAccess==='function'&&attachAccess('player').extra;return`${p.type==='SET'?'버스트':'체인'} ${seq} · 합계 +${p.total} · ${extra?'추가 붙이기 · 스위치 이동 없음':'스위치 → 상대'}`}''','attach preview')
h=replace_once(h,
'''if(!ok){log('붙이기 불가 · 같은 조합에 이번 턴 이미 붙였거나, 붙인 뒤 조합이 유효하지 않습니다.','hit');return false}''',
'''if(!ok){log('붙이기 불가 · 기본 붙이기 1회를 이미 사용했거나, 붙인 뒤 조합이 유효하지 않습니다. 추가 붙이기는 네임드 카드가 명시적으로 허용할 때만 가능합니다.','hit');return false}''','player attach error')
h=replace_once(h,
'''else if(state.player.returnedSwitchThisTurn){e.className='targetHint idle';e.innerHTML='<b>이번 턴 스위치 반환 완료.</b> 방금 반환한 같은 런은 계속 연장해 체인 위력을 더할 수 있지만 스위치는 다시 움직이지 않습니다. 다른 버스트/체인 반환은 불가.'}''',
'''else if((state.player.attachCount||0)>=1){const aa=attachAccess('player');e.className=aa.allowed?'targetHint good':'targetHint idle';e.innerHTML=aa.allowed?'<b>카드 효과 추가 붙이기 가능.</b> 추가 체인/버스트 위력은 누적되지만 스위치는 다시 움직이지 않습니다.':'<b>기본 붙이기 1회 사용 완료.</b> 여러 장을 잇고 싶다면 한 번의 붙이기에 함께 선택합니다.'}''','target hint attach used')
h=replace_once(h,
'''const bits=[`새 조합 <b>${state.player.newMeldCount||0}/2</b>`];''',
'''const bits=[`새 조합 <b>${state.player.newMeldCount||0}/2</b>`,`붙이기 <b>${Math.min(1,state.player.attachCount||0)}/1</b>${(state.player.extraAttachRemaining||0)>0?` + 추가 ${state.player.extraAttachRemaining}`:''}`];''','selection strip attach count')

# updateButtons: short labels and cleanup visibility.
h=replace_once(h,
'''const recoverBtn=document.getElementById('recoverBtn'),recoverAccess=rp?recoveryAccess('player',rp.side,rp.meld,rp.card):null;recoverBtn.disabled=!rp;recoverBtn.textContent=rp?`${rp.side==='enemy'?'상대 조합 · ':''}${cardText(rp.card)} ${recoverAccess?.free?'무료 회수':'회수'}`:state.player.recoveredThisTurn?'기본 회수 사용함':'내 카드 회수';const mb=document.getElementById('maintenanceBtn'),limit=action?maintenanceLimit('player'):0;mb.hidden=!limit;mb.disabled=!(limit&&cs.length>=1&&cs.length<=limit);mb.textContent=limit===2?(cs.length>=1&&cs.length<=2?`정비 ${cs.length}장 · 막힘 보정`:'정비 · 최대 2장'):limit===1?(cs.length===1?'정비 1장 교환':'정비 · 1장 선택'):'정비 사용함';const discardBtn=document.getElementById('discardBtn')''',
'''const recoverBtn=document.getElementById('recoverBtn'),recoverAccess=rp?recoveryAccess('player',rp.side,rp.meld,rp.card):null;recoverBtn.disabled=!rp;recoverBtn.textContent=rp?`${rp.side==='enemy'?'상대 · ':''}${cardText(rp.card)} ${recoverAccess?.free?'무료 회수':'회수'}`:state.player.recoveredThisTurn?'회수 사용함':'회수';const mb=document.getElementById('maintenanceBtn'),limit=action?maintenanceLimit('player'):0;mb.hidden=!limit;mb.disabled=!(limit&&cs.length>=1&&cs.length<=limit);mb.textContent=limit===2?(cs.length>=1&&cs.length<=2?`정비 ${cs.length}장 · 막힘 보정`:'정비 · 최대 2장'):limit===1?(cs.length===1?'정비 1장':'정비'):'정비 사용함';const cleanupBtn=document.getElementById('cleanupBtn'),cleanupCandidates=state.player.melds.map((m,i)=>canCleanupMeld('player',i)).filter(Boolean).length;cleanupBtn.hidden=!(action&&state.player.melds.length===3);cleanupBtn.disabled=!(action&&state.player.melds.length===3&&!state.player.meldCleanupUsed&&cleanupCandidates>0);cleanupBtn.textContent=state.player.meldCleanupUsed?'정리 사용함':cleanupCandidates?`정리 · ${cleanupCandidates}곳`:'정리 불가';const discardBtn=document.getElementById('discardBtn')''','updateButtons cleanup')

# Bind cleanup button.
h=replace_once(h,
'''document.getElementById('meldBtn').onclick=playerMeld;document.getElementById('attachBtn').onclick=playerAttach;document.getElementById('recoverBtn').onclick=playerRecover;document.getElementById('maintenanceBtn').onclick=playerMaintenance;document.getElementById('discardBtn').onclick=playerDiscard;''',
'''document.getElementById('meldBtn').onclick=playerMeld;document.getElementById('attachBtn').onclick=playerAttach;document.getElementById('recoverBtn').onclick=playerRecover;document.getElementById('maintenanceBtn').onclick=playerMaintenance;document.getElementById('cleanupBtn').onclick=playerCleanupMeld;document.getElementById('discardBtn').onclick=playerDiscard;''','cleanup button binding')

# Tutorial and practice copy: three memorable limits, no old same-RUN exception.
h=replace_once(h,
'''{id:'board',title:'전투 화면 읽기',goal:'위쪽은 코어와 스위치, 가운데는 덱·버림패·공개 조합, 아래쪽은 내 손패와 행동 버튼입니다.',hint:'안내 패널은 카드나 공개 조합을 덮지 않고 화면 흐름 안에 표시됩니다.',manualNext:true,implemented:true}''',
'''{id:'board',title:'전투 화면 읽기',goal:'위쪽은 코어와 스위치, 가운데는 덱·버림패·공개 조합, 아래쪽은 내 손패와 행동 버튼입니다. 새 조합은 두 번, 붙이기는 한 번, 내 필드는 세 칸입니다.',hint:'기본은 짧게 기억하세요. 새 조합 2회 · 붙이기 1회 · 내 공개 조합 최대 3개.',manualNext:true,implemented:true}''','tutorial board memory')
h=replace_once(h,
'''{id:'attachOwn',title:'붙이기',goal:'이미 공개된 내 런에 조건이 맞는 카드를 붙여 체인을 발생시킵니다.',hint:'강조된 7♣를 선택한 뒤 내 런에 붙이세요. 런은 붙일 때마다 체인 위력이 증가합니다.',implemented:true''',
'''{id:'attachOwn',title:'붙이기',goal:'이미 공개된 내 런에 조건이 맞는 카드를 붙여 체인을 발생시킵니다. 기본 붙이기는 턴당 1회이며 여러 장을 한 번에 붙일 수 있습니다.',hint:'강조된 7♣를 선택한 뒤 내 런에 붙이세요. 여러 장을 잇는다면 한 붙이기 행동에 함께 선택합니다.',implemented:true''','tutorial attach')
h=replace_once(h,
'''log('첫 손패에는 3 세트와 4♣-5♣-6♣ 런 재료가 모두 있습니다. 새 3장 조합은 세트/런을 합쳐 한 턴에 최대 2개 만들 수 있습니다. 새 조합에 붙이기는 다음 자기 턴부터 가능합니다.','good');''',
'''log('첫 손패에는 3 세트와 4♣-5♣-6♣ 런 재료가 모두 있습니다. 새 조합은 턴당 2회, 기본 붙이기는 턴당 1회, 내 공개 조합은 최대 3개입니다. 새 조합에 붙이기는 다음 자기 턴부터 가능합니다.','good');''','practice log')

# Full board message now points to conditional cleanup.
h=replace_once(h,
'''log('공개 조합이 3개입니다. 기존 조합에 붙이거나 회수·카드 효과로 전장을 정리해야 새 조합을 만들 수 있습니다.','hit');''',
'''log('공개 조합이 3개입니다. 이번 턴 만들지 않았고 고정되지 않은 내 조합은 기본 정리 1회로 슬롯을 비울 수 있습니다.','hit');''','full board player message')

INDEX.write_text(h,encoding='utf-8')

# --- README source of truth ---
r=README.read_text(encoding='utf-8')
r=replace_once(r,
'- Each player may keep up to 3 public melds. A full board blocks creating another meld until normal play or a card effect changes the board; there is no free base meld disposal action.',
'- Each player may keep up to 3 own public melds. When all 3 are full, once per own turn the player may clean up one older, non-fixed own meld for +0 power and no SWITCH movement; a meld created that turn cannot be cleaned up. Opponent melds containing your cards do not consume your slots.','README cleanup')
r=replace_once(r,
'- SWITCH physically moves at most once per player turn. After a RUN returns SWITCH, that **same RUN may still be extended again during the same turn**; each later extension adds its next CHAIN power but does not move SWITCH a second time. A different RUN/SET cannot create another return that turn. This makes split play such as 9♠ then 10♠ equivalent in core power flow to selecting both for one multi-attach.',
'- Base attach is one action per player turn. One attach action may add multiple legal cards to a RUN, resolving CHAIN +10 / +15 / +20 / +25 in order while SWITCH moves only once. Repeating attach in the same turn requires a named card that explicitly grants an extra attach; that extra attach may add power but does not move SWITCH a second time.','README attach')
README.write_text(r,encoding='utf-8')

# --- ROADMAP: replace superseded rules, then record the completed simplification milestone ---
road=ROAD.read_text(encoding='utf-8')
road=replace_once(road,
'- [x] Public meld cap 3 per player; no free base meld/RUN disposal',
'- [x] Public meld cap 3 per player; when all 3 own slots are full, one older non-fixed own meld may be voluntarily cleaned up once per own turn for +0 power / no SWITCH movement; same-turn-created melds are excluded','ROADMAP base cleanup')
road=replace_once(road,
'- [x] Make stuck-state legality include same-RUN continuation after the one physical SWITCH return',
'- [x] Make stuck-state legality use the global base attach count; repeated attach exists only when a named effect explicitly grants an extra attach','ROADMAP continuation removal')
road=replace_once(road,
'''## M1 — Final rules ↔ live code sync''',
'''## M0S — 기본 행동 단순화 / 3슬롯 필드 정리 — 2026-09-04\n- [x] 기존 M0R의 공개 조합 3칸 / 새 조합 2회 / 신규 자기 조합 당턴 확장 금지 / 시작 손패 8장을 유지\n- [x] 기본 붙이기를 전역 턴당 1회로 단순화하고, 한 행동의 다중 카드 런 확장에 체인 위력을 순서대로 합산\n- [x] `canContinueReturnedRun` / `returnAttachToken` / 조합별 `lastAttachToken` 기반 같은 RUN 연속 붙이기 기본 예외 제거\n- [x] 5♣ `연결고리`를 명시적인 「추가 붙이기 1회」 네임드로 재설계하고, 반역자 조커는 추가 붙이기 허용을 제거하는 카운터로 재설계\n- [x] 자기 공개 조합 3칸이 모두 찼을 때만 턴당 1회 가능한 `조합 정리` 구현 — 당턴 생성/고정 조합 제외, 보호는 방해하지 않음, 일반 `onRetire`/`retireMeld` 경로 사용, 위력 +0 / SWITCH 이동 없음\n- [x] AI가 기본 붙이기 1회와 다중 붙이기를 공유하고, 만원 상태에서 새 조합 후보가 있을 때 낮은 가치의 CHAIN 0 런을 우선 정리하되 버스트 준비 세트·성장 RUN은 보존하도록 평가\n- [x] 전투 버튼/규칙·용어/튜토리얼/연습전 문구를 「새 조합 두 번 · 붙이기 한 번 · 내 필드 세 칸」으로 동기화\n- [x] V-SIGNAL / ZERO-SIGHT / POINT-BLANK / MAIL-ROUTE / SCRAP-SHIFT의 회수·이동·추가 행동 경로가 전역 붙이기 횟수를 우회하지 않도록 감사; CYCLE-WORKS / TWELVE-BLOOM 후보는 추가 기본 생성 보너스를 요구하지 않는 정책 유지\n- [ ] Android/iOS/Fold 실기기 터치·안전영역 재확인 — 소스/브라우저 회귀와 별개인 실기기 검증\n\n## M1 — Final rules ↔ live code sync''','ROADMAP M0S')
ROAD.write_text(road,encoding='utf-8')

# --- M0R canonical expansion doc: record superseding simplification and update old execution summary ---
m=M0R.read_text(encoding='utf-8')
m=replace_once(m,
'양쪽 플레이어의 세트+세트 / 세트+런 / 런+런, 생성 1·2 허용/3 거부, 슬롯 3 허용/4 거부, 실패 시 손패·횟수 불변, 당턴 단일/다중 확장 금지, 다음 턴 체인과 동일 런 연속 확장, 다른 조합의 두 번째 반환 금지, 런 완주/버스트 이후 슬롯 재사용, 정리 후 생성 횟수 보존, 회수→새 조합 허용/반환 재사용 금지, 러미 6장 재충전, 실제 CPU 두 번 생성, 초기 손패 8+1을 검사한다.',
'양쪽 플레이어의 세트+세트 / 세트+런 / 런+런, 생성 1·2 허용/3 거부, 슬롯 3 허용/4 거부, 실패 시 손패·횟수 불변, 당턴 신규 자기 조합 확장 금지, 다음 턴 한 번의 다중 붙이기 체인 합산, 기본 두 번째 붙이기 거부, 네임드 추가 붙이기, 런 완주/버스트 이후 슬롯 재사용, 조건부 조합 정리, 회수→새 조합 허용/반환 재사용 제한, 러미 6장 재충전, 실제 CPU 두 번 생성, 초기 손패 8+1을 검사한다.','M0R execution summary')
append='''\n## 2026-09-04 기본 행동 단순화 후속 잠금\n\nM0R의 3슬롯/새 조합 2회/당턴 신규 자기 조합 확장 금지는 그대로 유지한다. 후속 규칙에서는 기본 붙이기를 조합별 토큰이 아니라 **플레이어 전역 턴당 1회**로 계산한다. 한 붙이기 행동에 여러 장을 함께 넣는 것이 기본 다중 확장 수단이며, 같은 RUN을 나눠 여러 번 붙이는 기본 예외는 제거한다.\n\n공개 조합 3칸이 모두 찼을 때만 턴당 1회 `조합 정리`를 사용할 수 있다. 이번 턴 만든 조합과 고정된 조합은 대상이 아니고, 보호는 자기 정리를 막지 않는다. 정리는 기존 `retireMeld()`와 `onRetire`를 그대로 통과하며 위력과 SWITCH에는 영향을 주지 않는다. CHAIN 4+ RUN의 `런 완주`는 만원 여부와 무관한 별도 정상 종료 행동으로 유지한다.\n\n네임드 예외는 기본 규칙을 복잡하게 만들지 않는다. 5♣ 연결고리는 「그 RUN에 또 붙일 수 있음」 대신 **추가 붙이기 1회**를 명시적으로 부여한다. 반역자 조커의 낡은 동일-RUN 재반환 차단은 추가 붙이기 허용 제거로 바뀐다. V-SIGNAL 앙코르·조율자·갈아끼우기 등 회수 카드 재사용 허용은 목적지 제한을 유지하되, 전역 붙이기 횟수 자체는 우회하지 않는다.\n\n기억 문구는 **“새 조합은 두 번, 붙이기는 한 번, 내 필드는 세 칸.”** 으로 통일한다.\n'''
if '## 2026-09-04 기본 행동 단순화 후속 잠금' not in m:m+=append
M0R.write_text(m,encoding='utf-8')

# --- new-user UX terminology doc ---
ux=UX.read_text(encoding='utf-8')
ux=replace_once(ux,
'''안내:\n> 조건이 맞는 카드는 이미 공개된 조합에 **붙일 수 있습니다.** 상대 조합도 이용할 수 있습니다.''',
'''안내:\n> 조건이 맞는 카드는 이미 공개된 조합에 **붙일 수 있습니다.** 상대 조합도 이용할 수 있습니다. 기본 붙이기는 턴당 한 번이며, 여러 장을 잇고 싶다면 한 행동에 함께 선택합니다.''','UX attach guidance')
ux=replace_once(ux,
'''- 한 턴 기본 반환은 1회.''',
'''- 한 턴 기본 반환은 1회. 기본 붙이기도 1회이며, 네임드가 명시적으로 「추가 붙이기」를 줄 때만 예외가 생긴다.\n- 신규 유저 기억 문구: **“새 조합은 두 번, 붙이기는 한 번, 내 필드는 세 칸.”**\n- 자기 공개 조합 3칸이 모두 찼다면, 당턴 생성/고정 조합을 제외하고 기본 `정리` 1회로 슬롯을 비울 수 있다. 정리는 위력 +0 / SWITCH 이동 없음.','UX switch basics')
UX.write_text(ux,encoding='utf-8')

# --- existing M0R executable regression: replace old split-attach continuation expectation ---
t=M0R_TEST.read_text(encoding='utf-8')
old=''' g.turnStart('enemy');assert.equal(g.attachCards('enemy',[next[0]],'enemy',0),true);\n assert.equal(g.state.switchPower,10);assert.equal(g.state.switchTarget,'player');\n assert.equal(g.attachCards('enemy',next.slice(1),'enemy',0),true);assert.equal(g.state.switchPower,45);\n assert.equal(s.returnedSwitchThisTurn,true);\n const otherRun=run(g,'enemy','H');s.melds.push(otherRun);const h4=cards(g,'enemy',['H4']);s.hand.push(...h4);\n assert.equal(g.attachCards('enemy',h4,'enemy',1),false,'different return blocked after first return');\n}\nconsole.log('PASS same-turn own extension denied; next-turn CHAIN and same-RUN continuation preserve single return');'''
new=''' g.turnStart('enemy');assert.equal(g.attachCards('enemy',next,'enemy',0),true);\n assert.equal(g.state.switchPower,45);assert.equal(g.state.switchTarget,'player');assert.equal(s.attachCount,1);\n assert.equal(s.returnedSwitchThisTurn,true);\n const otherRun=run(g,'enemy','H');s.melds.push(otherRun);const h4=cards(g,'enemy',['H4']);s.hand.push(...h4);\n assert.equal(g.attachCards('enemy',h4,'enemy',1),false,'base second attach blocked after the one attach action');\n}\nconsole.log('PASS same-turn own extension denied; next-turn multi-attach sums CHAIN and base second attach is rejected');'''
t=replace_once(t,old,new,'M0R legacy continuation test')
M0R_TEST.write_text(t,encoding='utf-8')

# final audit should distinguish removed unrestricted disposal from new full-board cleanup.
f=FINAL_TEST.read_text(encoding='utf-8')
f=replace_once(f,
'''ok(!html.includes('function playerRetireMeld('), 'legacy free meld-retire action stub is removed');''',
'''ok(!html.includes('function playerRetireMeld('), 'legacy unrestricted free meld-retire action stub is removed');\nok(html.includes('function canCleanupMeld(') && html.includes("s.melds.length!==3") && html.includes('m.createdToken===state.turnToken'), 'new cleanup is conditional on full board and excludes same-turn melds');\nok(html.includes('function attachAccess(') && !html.includes('function canContinueReturnedRun(') && !html.includes('returnAttachToken'), 'base attach is global once-per-turn with no same-RUN continuation state');''','final audit new contract')
FINAL_TEST.write_text(f,encoding='utf-8')

print('base action simplification patch applied')

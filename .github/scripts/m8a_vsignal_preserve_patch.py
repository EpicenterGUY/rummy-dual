from pathlib import Path

index=Path('index.html')
s=index.read_text(encoding='utf-8')

def rep(old,new,label,count=1):
    global s
    found=s.count(old)
    if found<count:
        raise SystemExit(f'missing {label}: {found}/{count}')
    s=s.replace(old,new,count)

# Live V-SIGNAL variants for D4 and CK.
rep("'D4':{n:'밀수품',t:'smuggledSuit',d:'버림패에서 가져온 턴에 한해 RUN에서 원하는 무늬처럼 취급.'},",
    "'D4':{n:'밀수품',t:'smuggledSuit',d:'버림패에서 가져온 턴에 한해 RUN에서 원하는 무늬처럼 취급.'},\n'VSD4':{slot:'D4',themeId:'v-signal',n:'전원 집합!',t:'vGatherAll',d:'이 카드가 들어간 SET을 내가 BURST로 완성해 정리할 때, 그 SET에서 내가 제어하는 카드 1장을 손패로 보존할 수 있다. 보존한 카드는 이번 턴 사용할 수 없다.'},",
    'V-SIGNAL Gather All definition')
rep("'CK':{n:'조율자',t:'alternateBonus',d:'조율자가 내 공개 조합에 있고 SET과 RUN이 모두 있으면, 다른 종류 조합에 바로 붙을 수 있는 내 카드 회수를 턴당 1회 무료로 하고 그 카드는 같은 턴 즉시 이어붙일 수 있다.'},",
    "'CK':{n:'조율자',t:'alternateBonus',d:'조율자가 내 공개 조합에 있고 SET과 RUN이 모두 있으면, 다른 종류 조합에 바로 붙을 수 있는 내 카드 회수를 턴당 1회 무료로 하고 그 카드는 같은 턴 즉시 이어붙일 수 있다.'},\n'VSCK':{slot:'CK',themeId:'v-signal',n:'24시간 내구방송',t:'vEndurance',d:'이 카드가 들어간 체인 4 이상 RUN을 내가 완주할 때, 그 RUN에서 내가 제어하는 카드 1장을 손패로 보존할 수 있다. 보존한 카드는 이번 턴 사용할 수 없다.'},",
    'V-SIGNAL Endurance definition')

# Unlock live variants without unlocking the unrelated base cards.
rep("items:['S9','H10','D2','C6','SJ','H3']",
    "items:['S9','H10','D2','VSD4','C6','SJ','H3']",
    'Gather All unlock')
rep("items:['SA','S2','H9','C9','J4']",
    "items:['SA','S2','H9','C9','VSCK','J4']",
    'Endurance unlock')

rep("rebelJoker:['trick','interact','pressure'],vEncore:['cycle','combo']",
    "rebelJoker:['trick','interact','pressure'],vEncore:['cycle','combo'],vGatherAll:['hold','combo','cycle'],vEndurance:['extend','sustain','cycle']",
    'V-SIGNAL preservation tendencies')

# Common preservation planner. It is deliberately card-agnostic once an offer exists:
# candidates are any cards currently controlled by the acting player, including ordinary cards.
anchor="function consumeEncoreReturnPermission(cards,turnToken,targetMeld=null){let used=0;for(const c of cards||[]){if(c?.themeId!=='v-signal'||c.tag!=='vEncore'||c.recoveredToken!==turnToken||c.recoverReturnOverrideToken!==turnToken)continue;if(Array.isArray(c.recoverReturnTargets)&&!c.recoverReturnTargets.includes(targetMeld))continue;c.recoverReturnOverrideToken=null;c.recoverReturnTargets=null;c.encoreReturnUsedToken=turnToken;used++}return used}\n"
insert=anchor+"function retirePreservationOffer(actor,m,kind){if(!actor||!m)return null;let source=null;if(kind==='burst'&&m.type==='SET'&&m.cards.length===4)source=m.cards.find(c=>c.owner===actor&&c.themeId==='v-signal'&&c.tag==='vGatherAll')||null;else if(kind==='runFinish'&&m.type==='RUN'&&(m.chain||0)>=4)source=m.cards.find(c=>c.owner===actor&&c.themeId==='v-signal'&&c.tag==='vEndurance')||null;if(!source)return null;const candidates=m.cards.filter(c=>c.owner===actor);return candidates.length?{actor,source,kind,candidates}:null}\nfunction requestRetirePreservation(actor,m,kind,onResolved=null){const offer=retirePreservationOffer(actor,m,kind);if(!offer)return{paused:false,card:null};const done=card=>{if(typeof onResolved==='function')onResolved(card||null)};if(actor==='player'&&state.turn==='player'&&typeof requestEffectChoice==='function'){const title=offer.source.name,text=kind==='burst'?'BURST로 정리되는 SET에서 내가 제어하는 카드 1장을 손패로 보존할 수 있습니다. 보존한 카드는 이번 턴 사용할 수 없습니다.':'완주로 정리되는 RUN에서 내가 제어하는 카드 1장을 손패로 보존할 수 있습니다. 보존한 카드는 이번 턴 사용할 수 없습니다.';const opened=requestEffectChoice({title,text,options:offer.candidates.map(c=>({key:c.uid,label:`${cardText(c)}${c.named?` · ${c.name}`:''}`,detail:c.themeId?`테마 ${themeDef(c.themeId)?.displayName||c.themeId}`:'일반/비테마 카드',card:c})),allowSkip:true,skipLabel:'보존하지 않기',onChoose:o=>done(o?.card||null)});if(opened)return{paused:true,card:null}}let card=null;if(!(kind==='burst'&&sideObj(actor).hand.length===0)){card=[...offer.candidates].sort((a,b)=>(b.named?1:0)-(a.named?1:0)||b.age-a.age)[0]||null}return{paused:false,card}}\n"
rep(anchor,insert,'common retire preservation planner')

# Make passive tags explicit in normal named effect resolution.
rep("case'vacancyJoker':case'rebelJoker':break}}return{bonus:",
    "case'vGatherAll':case'vEndurance':break;case'vacancyJoker':case'rebelJoker':break}}return{bonus:",
    'passive preservation tags')

# retireMeld keeps its legacy signature for isolated-function regressions; the 4th arg is optional.
old_retire="function retireMeld(owner,index=0,reason='정리'){const arr=meldsOf(owner),m=arr[index];if(!m)return;if(typeof emitEffectEvent==='function')emitEffectEvent('onRetire',{owner,meld:m,cards:[...m.cards],reason,phase:'before'});arr.splice(index,1);for(const c of m.cards){if(c.tag==='jokerKing'){const home=c.originOwner||c.owner;c.owner=home;c.fromDiscard=false;c.age=0;c.suppressEffectToken=null;sideObj(home).deck.unshift(c);log(`${c.name}: 조합 정리 후 원주인의 덱 맨 아래로 귀환.`,'good')}else if(c.tag==='flexSuit'&&c.flexSuitOffSuit){const home=c.owner;sideObj(home).hand.push(c);c.flexSuitOffSuit=false;c.age=0;log(`${c.name}: 다른 무늬 대역 역할을 마치고 현재 제어자 손패로 귀환.`,'good')}else{if(c.tag==='smuggledSuit')c.smuggledActive=false;sideObj(c.owner).spent.push(c)}}log(`${owner==='player'?'내':'상대'} ${m.type} 정리 · ${reason}.`,'important')}"
new_retire="function retireMeld(owner,index=0,reason='정리'){const opts=arguments[3]||{},arr=meldsOf(owner),m=arr[index];if(!m)return;const preserveCards=(opts.preserveCards||[]).filter(Boolean),preserveUids=new Set(preserveCards.map(c=>c.uid));if(typeof emitEffectEvent==='function')emitEffectEvent('onRetire',{owner,meld:m,cards:[...m.cards],reason,phase:'before',preserveCards:[...preserveCards]});arr.splice(index,1);for(const c of m.cards){if(preserveUids.has(c.uid)){const home=c.owner;c.fromDiscard=false;c.contractActive=false;c.enteredMeldToken=null;c.suppressEffectToken=state.turnToken;c.recoveredToken=null;c.recoverReturnOverrideToken=null;c.recoverReturnTargets=null;c.age=0;c.blockedUntilTurn=state.turnNo;if(c.tag==='smuggledSuit')c.smuggledActive=false;if(c.flexSuitOffSuit)c.flexSuitOffSuit=false;sideObj(home).hand.push(c);log(`${opts.preserveLabel||'보존'}: ${cardText(c)}를 손패로 보존 · 이번 턴 사용 불가.`,'good');continue}if(c.tag==='jokerKing'){const home=c.originOwner||c.owner;c.owner=home;c.fromDiscard=false;c.age=0;c.suppressEffectToken=null;sideObj(home).deck.unshift(c);log(`${c.name}: 조합 정리 후 원주인의 덱 맨 아래로 귀환.`,'good')}else if(c.tag==='flexSuit'&&c.flexSuitOffSuit){const home=c.owner;sideObj(home).hand.push(c);c.flexSuitOffSuit=false;c.age=0;log(`${c.name}: 다른 무늬 대역 역할을 마치고 현재 제어자 손패로 귀환.`,'good')}else{if(c.tag==='smuggledSuit')c.smuggledActive=false;sideObj(c.owner).spent.push(c)}}log(`${owner==='player'?'내':'상대'} ${m.type} 정리 · ${reason}.`,'important')}"
rep(old_retire,new_retire,'retireMeld preservation support')

# BURST auto-retire: choose preservation before retiring; RUMMY is evaluated after preservation.
old_attach="    const willRummy=s.hand.length===0;\n    const actionNote=continuation?' · 연속 체인':returning||forceReturn?' · 스위치 반환':' · 구조 변경';\n    log(`${w==='player'?'나':'상대'} ${targetSide===w?'내':'상대'} ${type==='SET'?'세트':'런'}에 ${cards.length}장 붙이기${actionNote}.`,'important');\n    if(type==='SET'&&m.cards.length===4){const currentIndex=meldsOf(targetSide).indexOf(m);if(currentIndex>=0)retireMeld(targetSide,currentIndex,'버스트 후 4장 세트 자동 정리')}\n    if(willRummy&&!state.gameOver){const rr=triggerRummy(w,cards,{returned:returning||forceReturn});return rr==='choice'?'choice':'rummy'}\n    return true;"
new_attach="    const actionNote=continuation?' · 연속 체인':returning||forceReturn?' · 스위치 반환':' · 구조 변경';\n    log(`${w==='player'?'나':'상대'} ${targetSide===w?'내':'상대'} ${type==='SET'?'세트':'런'}에 ${cards.length}장 붙이기${actionNote}.`,'important');\n    const afterRetire=()=>{const willRummy=s.hand.length===0;if(willRummy&&!state.gameOver){const rr=triggerRummy(w,cards,{returned:returning||forceReturn});return rr==='choice'?'choice':'rummy'}return true};\n    if(type==='SET'&&m.cards.length===4){const completeRetire=preserved=>{const currentIndex=meldsOf(targetSide).indexOf(m);if(currentIndex>=0)retireMeld(targetSide,currentIndex,'버스트 후 4장 세트 자동 정리',{preserveCards:preserved?[preserved]:[],preserveLabel:'전원 집합!'});const result=afterRetire();if(w==='player'&&typeof render==='function')render();return result};if(typeof requestRetirePreservation==='function'){const req=requestRetirePreservation(w,m,'burst',completeRetire);if(req.paused)return'choice';return completeRetire(req.card)}return completeRetire(null)}\n    return afterRetire();"
rep(old_attach,new_attach,'BURST preservation continuation')

# RUN finish: preserve after onRunFinish but before onRetire/removal.
old_finish="function finishRun(w,index){if(!canFinishRun(w,index))return false;const s=sideObj(w),m=meldsOf(w)[index],count=m.cards.length;s.actedThisTurn=true;if(typeof emitEffectEvent==='function')emitEffectEvent('onRunFinish',{actor:w,meld:m,cards:[...m.cards],chain:m.chain||0,count,phase:'beforeRetire'});retireMeld(w,index,'런 완주');if(w==='player'){state.target=null;state.boardSelected.clear();state.selected.clear();state.selectionOrder=[]}combatBanner('런 완주','chain',30);log(`${switchName(w)} 런 완주 · ${count}장 조합을 정리해 공개 조합 슬롯을 비웠습니다. 누적 위력과 스위치는 변하지 않습니다.`,'good');return true}"
new_finish="function finishRun(w,index){if(!canFinishRun(w,index))return false;const s=sideObj(w),m=meldsOf(w)[index],count=m.cards.length;s.actedThisTurn=true;if(typeof emitEffectEvent==='function')emitEffectEvent('onRunFinish',{actor:w,meld:m,cards:[...m.cards],chain:m.chain||0,count,phase:'beforeRetire'});const complete=preserved=>{const currentIndex=meldsOf(w).indexOf(m);if(currentIndex>=0)retireMeld(w,currentIndex,'런 완주',{preserveCards:preserved?[preserved]:[],preserveLabel:'24시간 내구방송'});if(w==='player'){state.target=null;state.boardSelected.clear();state.selected.clear();state.selectionOrder=[]}combatBanner('런 완주','chain',30);log(`${switchName(w)} 런 완주 · ${count}장 조합을 정리해 공개 조합 슬롯을 비웠습니다. 누적 위력과 스위치는 변하지 않습니다.`,'good');if(w==='player'&&typeof render==='function')render();return true};if(typeof requestRetirePreservation==='function'){const req=requestRetirePreservation(w,m,'runFinish',complete);if(req.paused)return'choice';return complete(req.card)}return complete(null)}"
rep(old_finish,new_finish,'RUN finish preservation continuation')

index.write_text(s,encoding='utf-8')

road=Path('ROADMAP.md')
r=road.read_text(encoding='utf-8')
r=r.replace('- [ ] 버스트 정리/런 완주 직전 카드 보존 타이밍 구현','- [x] 버스트 정리/런 완주 직전 카드 보존 타이밍 구현',1)
anchor_r='- [x] `앙코르` 등 회수 후 동일 턴 반환 예외를 카드 단위로 안전하게 구현\n'
if anchor_r not in r:
    raise SystemExit('missing V-SIGNAL roadmap anchor')
if '전원 집합!' not in r.split('### ZERO//SIGHT',1)[0]:
    r=r.replace(anchor_r,anchor_r+'- [x] 4♦ `전원 집합!` / K♣ `24시간 내구방송` 라이브 구현 — 정리 직전 선택형 손패 보존, 일반 카드도 후보 가능, 보존 카드는 해당 턴 재사용 금지\n',1)
road.write_text(r,encoding='utf-8')

doc=Path('docs/THEME_GROUPS.md')
d=doc.read_text(encoding='utf-8')
d=d.replace('- 4♦ `전원 집합!` — 버스트 정리 직전 자신의 카드 1장 보존.','- 4♦ `전원 집합!` — 이 카드가 들어간 SET을 내가 BURST로 완성해 정리할 때, 그 SET에서 내가 제어하는 카드 1장을 손패로 보존할 수 있다. 보존한 카드는 이번 턴 사용할 수 없다.',1)
d=d.replace('- K♣ `24시간 내구방송` — 체인 4+ 런 완주 시 자신의 카드 1장 보존.','- K♣ `24시간 내구방송` — 이 카드가 들어간 체인 4 이상 RUN을 내가 완주할 때, 그 RUN에서 내가 제어하는 카드 1장을 손패로 보존할 수 있다. 보존한 카드는 이번 턴 사용할 수 없다.',1)
d=d.replace('- [ ] 세트 정리/런 완주 직전 카드 보존 타이밍 정의','- [x] 세트 정리/런 완주 직전 카드 보존 타이밍 정의',1)
anchor_d='- [x] 앙코르 구현 잠금: `onRecover`로 자기 자신에게만 목적지 제한 반환 허가를 부여하고, 실제 반환 재료로 쓰는 순간 허가를 소비하며 같은 턴 재회수로 재충전하지 않음\n'
if anchor_d not in d:
    raise SystemExit('missing V-SIGNAL doc anchor')
if '보존 구현 잠금' not in d:
    d=d.replace(anchor_d,anchor_d+'- [x] 보존 구현 잠금: `onRunFinish` 이후/`onRetire` 이전에 선택하고, `onRetire`는 원래 전체 카드와 `preserveCards`를 함께 관측하며 실제 정리 단계에서 보존 카드만 손패로 분리한다. 일반/타 테마 카드도 보존 가능\n',1)
doc.write_text(d,encoding='utf-8')

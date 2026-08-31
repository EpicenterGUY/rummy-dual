from pathlib import Path

index = Path('index.html')
s = index.read_text(encoding='utf-8')

def rep(old, new, label, count=1):
    global s
    found = s.count(old)
    if found < count:
        raise SystemExit(f'missing {label}: {found}/{count}')
    s = s.replace(old, new, count)

def function_bounds(name):
    marker = f'function {name}('
    start = s.find(marker)
    if start < 0:
        raise SystemExit(f'missing function {name}')
    par = 0
    brace = -1
    for i in range(start + len(marker) - 1, len(s)):
        ch = s[i]
        if ch == '(':
            par += 1
        elif ch == ')':
            par -= 1
        elif ch == '{' and par == 0:
            brace = i
            break
    if brace < 0:
        raise SystemExit(f'missing body {name}')
    depth = 0
    for i in range(brace, len(s)):
        if s[i] == '{':
            depth += 1
        elif s[i] == '}':
            depth -= 1
            if depth == 0:
                return start, i + 1
    raise SystemExit(f'unterminated function {name}')

def rep_in_function(name, old, new, label):
    global s
    start, end = function_bounds(name)
    fn = s[start:end]
    if old not in fn:
        raise SystemExit(f'missing {label} in {name}')
    fn = fn.replace(old, new, 1)
    s = s[:start] + fn + s[end:]

old_defs = "const EFFECT_EVENTS=Object.freeze(['onAcquire','onDiscard','onMeldCreate','onAttach','onBurst','onChain','onRecover','onRummy','onReturnSwitch','onDetonate','onCoreBreak','onTurnStart','onTurnEnd','onRetire']);\nconst EFFECT_ACTIONS=Object.freeze(['draw','heal','addShield','addPower','returnSwitch','applyStatus','retireMeld']);"
new_defs = "const EFFECT_EVENTS=Object.freeze(['onAcquire','onDiscard','onMeldCreate','onAttach','onBurst','onChain','onRecover','onRummy','onReturnSwitch','onDetonate','onCoreBreak','onTurnStart','onTurnEnd','onRunFinish','onRetire']);\nconst EFFECT_ACTIONS=Object.freeze(['draw','heal','addShield','addPower','returnSwitch','applyStatus','retireMeld']);\nconst THEME_GROUPS=Object.freeze({'v-signal':Object.freeze({id:'v-signal',name:'V-SIGNAL',displayName:'V-SIGNAL',concept:'방송 · 합방 · RAID · 회수 · 러미'})});\nconst effectEventSubscribers=new Set();\nfunction themeDef(id){return id?THEME_GROUPS[id]||null:null}\nfunction cardTheme(c){return themeDef(c?.themeId)}\nfunction subscribeEffectEvent(handler){if(typeof handler!=='function')return()=>false;effectEventSubscribers.add(handler);return()=>effectEventSubscribers.delete(handler)}\nfunction emitEffectEvent(event,payload={}){if(!EFFECT_EVENTS.includes(event))return null;const packet={event,turnNo:state.turnNo,turnToken:state.turnToken,...payload};for(const handler of [...effectEventSubscribers])handler(packet);return packet}\nfunction meldOwnerSide(m){if(!m)return null;if(meldsOf('player').includes(m))return'player';if(meldsOf('enemy').includes(m))return'enemy';return null}\nfunction emitRecoveryEvent(actor,card,meld,targetSide=null,opts={}){return emitEffectEvent('onRecover',{actor,card,meld,targetSide:targetSide||meldOwnerSide(meld),free:!!opts.free,automatic:!!opts.automatic,reason:opts.reason||'recover'})}"
rep(old_defs, new_defs, 'effect event/theme foundation')

rep("tag:def?.t||null,named:!!def", "tag:def?.t||null,themeId:def?.themeId||null,named:!!def", 'card themeId metadata')

rep_in_function(
    'submitNewMeld',
    "if(w==='player')state.lastPlayerMeldType=type;else state.lastEnemyMeldType=type;log(`",
    "if(w==='player')state.lastPlayerMeldType=type;else state.lastEnemyMeldType=type;emitEffectEvent('onMeldCreate',{actor:w,cards:[...cards],type,meld:m,targetSide:w});log(`",
    'onMeldCreate emission'
)

rep_in_function(
    'attachCards',
    "replaceRedundantJokers(targetSide,m,w,cards);\n    const willRummy=s.hand.length===0;",
    "replaceRedundantJokers(targetSide,m,w,cards);\n    emitEffectEvent('onAttach',{actor:w,cards:[...cards],type,meld:m,targetSide,returned:returning||forceReturn,continuation,phase:'afterResolve'});\n    const willRummy=s.hand.length===0;",
    'onAttach emission'
)

rep_in_function(
    'playerRecover',
    "log(`나 회수 · ${plan.side==='enemy'?'상대':'내'} 공개 조합의 ${cardText(c)} → 손패${m.type==='RUN'?' · 체인 -1':''}.`,'important');if(tutorialCheckProgress",
    "log(`나 회수 · ${plan.side==='enemy'?'상대':'내'} 공개 조합의 ${cardText(c)} → 손패${m.type==='RUN'?' · 체인 -1':''}.`,'important');emitRecoveryEvent('player',c,m,plan.side,{free:!!freeReason,reason:freeReason||'basic'});if(tutorialCheckProgress",
    'player onRecover emission'
)

rep_in_function(
    'executeRecoverAI',
    "log(`${w==='player'?'YOU':'CPU'} 회수 · ${cardText(c)}${freeReason==='tuner'?' · 조율자 무료 이동':''}${m.type==='RUN'?' · 체인 -1':''}.`,'important');return c",
    "log(`${w==='player'?'YOU':'CPU'} 회수 · ${cardText(c)}${freeReason==='tuner'?' · 조율자 무료 이동':''}${m.type==='RUN'?' · 체인 -1':''}.`,'important');emitRecoveryEvent(w,c,m,plan.side,{free:!!freeReason,reason:freeReason||'basic'});return c",
    'AI onRecover emission'
)

rep_in_function(
    'recoverSpecificFromMeld',
    "log(`${opts.label||'무료 회수'}: ${cardText(c)}${m.type==='RUN'?' · 체인 -1':''}.`,'good');return c",
    "log(`${opts.label||'무료 회수'}: ${cardText(c)}${m.type==='RUN'?' · 체인 -1':''}.`,'good');emitRecoveryEvent(w,c,m,null,{free:true,reason:opts.label||'effect'});return c",
    'effect onRecover emission'
)

rep_in_function(
    'recoverRedundantGapRun',
    "log(`${c.name}: 빠진 실제 카드가 채워져 무료 회수${m.type==='RUN'?' · 체인 -1':''}.`,'good');return c",
    "log(`${c.name}: 빠진 실제 카드가 채워져 무료 회수${m.type==='RUN'?' · 체인 -1':''}.`,'good');emitRecoveryEvent(c.owner,c,m,targetSide,{free:true,automatic:true,reason:'gapAuto'});return c",
    'Gap Run auto-recover emission'
)

rep_in_function(
    'middleManagerReturnPlaceholder',
    "log(`중간관리자: 대체재 ${c.name}를 원주인 손으로 반환${m.type==='RUN'?' · 체인 -1':''}.`,'good');return c",
    "log(`중간관리자: 대체재 ${c.name}를 원주인 손으로 반환${m.type==='RUN'?' · 체인 -1':''}.`,'good');emitRecoveryEvent(c.owner,c,m,targetSide,{free:true,automatic:true,reason:'middleManager'});return c",
    'Middle Manager auto-recover emission'
)

rep_in_function(
    'replaceRedundantJokers',
    "log(`${j.name}: 실제 카드가 채워져 원주인 손패로 복귀${m.type==='RUN'?' · 체인 -1':''}.`,'good');if(j.tag==='rebelJoker')",
    "log(`${j.name}: 실제 카드가 채워져 원주인 손패로 복귀${m.type==='RUN'?' · 체인 -1':''}.`,'good');emitRecoveryEvent(j.owner,j,m,targetSide,{free:true,automatic:true,reason:'jokerReplacement'});if(j.tag==='rebelJoker')",
    'Joker replacement recovery emission'
)

rep_in_function(
    'triggerRummy',
    "const beforeReloadHand=s.hand.length;drawMany(w,Math.max(0,reload-beforeReloadHand),false);let finalized=false;",
    "const beforeReloadHand=s.hand.length;drawMany(w,Math.max(0,reload-beforeReloadHand),false);emitEffectEvent('onRummy',{actor:w,lastCards:[...lastCards],reload,beforeHand:beforeReloadHand,afterHand:s.hand.length,returned:!!opts.returned});let finalized=false;",
    'onRummy emission'
)

rep_in_function(
    'finishRun',
    "const s=sideObj(w),m=meldsOf(w)[index],count=m.cards.length;s.actedThisTurn=true;retireMeld(w,index,'런 완주');",
    "const s=sideObj(w),m=meldsOf(w)[index],count=m.cards.length;s.actedThisTurn=true;emitEffectEvent('onRunFinish',{actor:w,meld:m,cards:[...m.cards],chain:m.chain||0,count,phase:'beforeRetire'});retireMeld(w,index,'런 완주');",
    'onRunFinish pre-retire emission'
)

rep_in_function(
    'retireMeld',
    "const arr=meldsOf(owner),m=arr[index];if(!m)return;arr.splice(index,1);",
    "const arr=meldsOf(owner),m=arr[index];if(!m)return;emitEffectEvent('onRetire',{owner,meld:m,cards:[...m.cards],reason,phase:'before'});arr.splice(index,1);",
    'onRetire pre-retire emission'
)

index.write_text(s, encoding='utf-8')

road = Path('ROADMAP.md')
r = road.read_text(encoding='utf-8')
r = r.replace('- [ ] Favor meld mutation, recovery, movement, discard, defense, RUMMY and timing interactions', '- [x] Favor meld mutation, recovery, movement, discard, defense, RUMMY and timing interactions', 1)
r = r.replace('- [ ] 새 조합/붙이기/회수/러미/런 완주 이벤트를 공용 효과 엔진에 필요한 만큼 노출', '- [x] 새 조합/붙이기/회수/러미/런 완주 이벤트를 공용 효과 엔진에 필요한 만큼 노출', 1)
r = r.replace('- [ ] M8 첫 ~50 네임드 선택/복사/타이밍 안정화 후 대규모 테마 구현 시작', '- [x] M8 첫 ~50 네임드 선택/복사/타이밍 안정화 후 대규모 테마 구현 시작', 1)
anchor = '- [x] 새 조합/붙이기/회수/러미/런 완주 이벤트를 공용 효과 엔진에 필요한 만큼 노출\n'
if anchor not in r:
    raise SystemExit('missing roadmap V-SIGNAL event anchor')
if 'V-SIGNAL foundation: themeId' not in r:
    r = r.replace(anchor, anchor + '- [x] V-SIGNAL foundation: `themeId`/표시명 메타데이터 + 구독형 공용 이벤트 버스 + 정리 직전 `onRunFinish`/`onRetire` 훅 추가\n', 1)
road.write_text(r, encoding='utf-8')

doc = Path('docs/THEME_GROUPS.md')
d = doc.read_text(encoding='utf-8')
d = d.replace('- [ ] 테마 ID/표시명 데이터 구조 추가', '- [x] 테마 ID/표시명 데이터 구조 추가', 1)
d = d.replace('- [ ] HYPE 관련 전용 자원은 만들지 않음', '- [x] HYPE 관련 전용 자원은 만들지 않음', 1)
d = d.replace('- [ ] 새 조합/붙이기/회수/러미/런 완주 이벤트를 테마 카드가 공용 엔진에서 읽을 수 있게 정리', '- [x] 새 조합/붙이기/회수/러미/런 완주 이벤트를 테마 카드가 공용 엔진에서 읽을 수 있게 정리', 1)
anchor2 = '- [x] 새 조합/붙이기/회수/러미/런 완주 이벤트를 테마 카드가 공용 엔진에서 읽을 수 있게 정리\n'
if anchor2 not in d:
    raise SystemExit('missing theme doc event anchor')
if '`onRunFinish`' not in d.split('# ZERO//SIGHT',1)[0]:
    d = d.replace(anchor2, anchor2 + '- [x] 공용 훅 이름 잠금: `onMeldCreate` / `onAttach` / `onRecover` / `onRummy` / `onRunFinish`; 모든 조합 정리 직전에는 `onRetire`도 발생\n', 1)
d = d.replace('Updated: 2026-08-30', 'Updated: 2026-08-31', 1)
doc.write_text(d, encoding='utf-8')

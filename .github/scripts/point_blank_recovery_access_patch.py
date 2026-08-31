from pathlib import Path

index=Path('index.html')
road=Path('ROADMAP.md')
theme=Path('docs/THEME_GROUPS.md')
text=index.read_text()

old_reason="function recoveryFreeReason(w,targetSide,m,c){const s=sideObj(w);if(tunerReadyForRecovery(w,targetSide,m,c))return'tuner';if(state.field?.tag==='roundabout'&&!s.flags.roundabout)return'roundabout';if(c.outlawFreeRecoverAt!=null&&s.turnStarts<=c.outlawFreeRecoverAt)return'outlaw';if(s.freeRecoverAfterRummy)return'rummy';return null}\nfunction chainDamage(step)"
new_reason="function recoveryFreeReason(w,targetSide,m,c){const s=sideObj(w);if(tunerReadyForRecovery(w,targetSide,m,c))return'tuner';if(state.field?.tag==='roundabout'&&!s.flags.roundabout)return'roundabout';if(c.outlawFreeRecoverAt!=null&&s.turnStarts<=c.outlawFreeRecoverAt)return'outlaw';if(s.freeRecoverAfterRummy)return'rummy';return null}\nfunction recoveryAccess(w,targetSide,m,c){const reason=recoveryFreeReason(w,targetSide,m,c);return{free:!!reason,reason:reason||'basic',consumesBasic:!reason}}\nfunction chainDamage(step)"
assert old_reason in text,'recovery reason anchor changed'
text=text.replace(old_reason,new_reason,1)

old_can="function canRecoverCard(w,targetSide,mi,ci){const s=sideObj(w),m=meldsOf(targetSide)[mi],c=m?.cards[ci];if(!m||!c||c.owner!==w||c.enteredMeldToken===state.turnToken)return false;const free=!!recoveryFreeReason(w,targetSide,m,c);if(s.recoveredThisTurn&&!free)return false;if(meldFixedActive(m)||cardFixedActive(c))return false;const remain=m.cards.filter((_,i)=>i!==ci);return remain.length>=3&&meldType(remain)===m.type}"
new_can="function canRecoverCard(w,targetSide,mi,ci){const s=sideObj(w),m=meldsOf(targetSide)[mi],c=m?.cards[ci];if(!m||!c||c.owner!==w||c.enteredMeldToken===state.turnToken)return false;const access=recoveryAccess(w,targetSide,m,c);if(s.recoveredThisTurn&&access.consumesBasic)return false;if(meldFixedActive(m)||cardFixedActive(c))return false;const remain=m.cards.filter((_,i)=>i!==ci);return remain.length>=3&&meldType(remain)===m.type}"
assert old_can in text,'canRecoverCard anchor changed'
text=text.replace(old_can,new_can,1)

old_player_prefix="beforeChain=m.chain||0,freeReason=recoveryFreeReason('player',plan.side,m,plan.card),[c]=m.cards.splice(plan.ci,1);"
new_player_prefix="beforeChain=m.chain||0,recovery=recoveryAccess('player',plan.side,m,plan.card),freeReason=recovery.free?recovery.reason:null,[c]=m.cards.splice(plan.ci,1);"
assert old_player_prefix in text,'player recovery access anchor changed'
text=text.replace(old_player_prefix,new_player_prefix,1)
old_consume="if(!freeReason)s.recoveredThisTurn=true;else{"
assert text.count(old_consume)>=2,'expected player and AI recovery consumption anchors'
text=text.replace(old_consume,"if(recovery.consumesBasic)s.recoveredThisTurn=true;else{",1)
old_player_event="emitRecoveryEvent('player',c,m,plan.side,{free:!!freeReason,reason:freeReason||'basic'})"
new_player_event="emitRecoveryEvent('player',c,m,plan.side,{free:recovery.free,reason:recovery.reason,consumesBasic:recovery.consumesBasic})"
assert old_player_event in text,'player recovery event anchor changed'
text=text.replace(old_player_event,new_player_event,1)

old_ai_prefix="freeReason=recoveryFreeReason(w,plan.side,m,plan.card),[c]=m.cards.splice(plan.ci,1);"
new_ai_prefix="recovery=recoveryAccess(w,plan.side,m,plan.card),freeReason=recovery.free?recovery.reason:null,[c]=m.cards.splice(plan.ci,1);"
assert old_ai_prefix in text,'AI recovery access anchor changed'
text=text.replace(old_ai_prefix,new_ai_prefix,1)
text=text.replace(old_consume,"if(recovery.consumesBasic)s.recoveredThisTurn=true;else{",1)
old_ai_event="emitRecoveryEvent(w,c,m,plan.side,{free:!!freeReason,reason:freeReason||'basic'})"
new_ai_event="emitRecoveryEvent(w,c,m,plan.side,{free:recovery.free,reason:recovery.reason,consumesBasic:recovery.consumesBasic})"
assert old_ai_event in text,'AI recovery event anchor changed'
text=text.replace(old_ai_event,new_ai_event,1)

old_emit="function emitRecoveryEvent(actor,card,meld,targetSide=null,opts={}){const targetedBy=typeof zeroSightTargetActors==='function'?zeroSightTargetActors(meld):[];const packet=emitEffectEvent('onRecover',{actor,card,meld,targetSide:targetSide||meldOwnerSide(meld),free:!!opts.free,automatic:!!opts.automatic,reason:opts.reason||'recover',targetedBy});if(targetedBy.length&&typeof emitZeroSightTargetChange==='function')emitZeroSightTargetChange('recover',meld,{actionActor:actor,card,free:!!opts.free,automatic:!!opts.automatic,reason:opts.reason||'recover'});if(typeof refreshPointBlankClashMeld==='function')refreshPointBlankClashMeld(meld,{change:'recover',actionActor:actor,card,free:!!opts.free,automatic:!!opts.automatic,reason:opts.reason||'recover'});return packet}"
new_emit="function emitRecoveryEvent(actor,card,meld,targetSide=null,opts={}){const targetedBy=typeof zeroSightTargetActors==='function'?zeroSightTargetActors(meld):[],consumesBasic=opts.consumesBasic!=null?!!opts.consumesBasic:!opts.free;const packet=emitEffectEvent('onRecover',{actor,card,meld,targetSide:targetSide||meldOwnerSide(meld),free:!!opts.free,consumesBasic,automatic:!!opts.automatic,reason:opts.reason||'recover',targetedBy});if(targetedBy.length&&typeof emitZeroSightTargetChange==='function')emitZeroSightTargetChange('recover',meld,{actionActor:actor,card,free:!!opts.free,consumesBasic,automatic:!!opts.automatic,reason:opts.reason||'recover'});if(typeof refreshPointBlankClashMeld==='function')refreshPointBlankClashMeld(meld,{change:'recover',actionActor:actor,card,free:!!opts.free,consumesBasic,automatic:!!opts.automatic,reason:opts.reason||'recover'});return packet}"
assert old_emit in text,'emitRecoveryEvent anchor changed'
text=text.replace(old_emit,new_emit,1)

old_ui="const recoverBtn=document.getElementById('recoverBtn');recoverBtn.disabled=!rp;recoverBtn.textContent=state.player.recoveredThisTurn?'회수 사용함':rp?`${rp.side==='enemy'?'상대 조합 · ':''}${cardText(rp.card)} 회수`:'내 카드 회수';"
new_ui="const recoverBtn=document.getElementById('recoverBtn'),recoverAccess=rp?recoveryAccess('player',rp.side,rp.meld,rp.card):null;recoverBtn.disabled=!rp;recoverBtn.textContent=rp?`${rp.side==='enemy'?'상대 조합 · ':''}${cardText(rp.card)} ${recoverAccess?.free?'무료 회수':'회수'}`:state.player.recoveredThisTurn?'기본 회수 사용함':'내 카드 회수';"
assert old_ui in text,'recovery button anchor changed'
text=text.replace(old_ui,new_ui,1)

index.write_text(text)

r=road.read_text()
old_road='- [ ] 무료 회수와 기본 회수 횟수를 명확히 구분'
new_road='- [x] 무료 회수와 기본 회수 횟수를 명확히 구분 — 공용 `recoveryAccess`가 `free / reason / consumesBasic`을 반환하고 플레이어·AI·합법성 판정·`onRecover` 이벤트가 이를 공유; 기본 회수를 이미 쓴 뒤에도 조건부 무료 회수는 가능하며 UI도 `무료 회수`와 `기본 회수 사용함`을 구분'
assert old_road in r,'ROADMAP recovery distinction anchor changed'
r=r.replace(old_road,new_road,1)
road.write_text(r)

t=theme.read_text()
old_doc='- [ ] 무료 회수와 기본 회수 횟수의 구분을 데이터로 명확화'
new_doc='- [x] 무료 회수와 기본 회수 횟수의 구분을 데이터로 명확화 — `recoveryAccess = { free, reason, consumesBasic }`을 공용 판정으로 사용하고 `onRecover` 패킷에도 같은 구분을 노출'
assert old_doc in t,'THEME_GROUPS recovery distinction anchor changed'
t=t.replace(old_doc,new_doc,1)
theme.write_text(t)

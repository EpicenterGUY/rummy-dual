from pathlib import Path

index=Path('index.html')
road=Path('ROADMAP.md')
theme=Path('docs/THEME_GROUPS.md')
text=index.read_text()

old_named="'DJ':{n:'강탈자',t:'extortion',d:'상대 공개 조합에서 빼도 유지되는 카드 1장을 내 공개 조합으로 직접 옮긴다. 이동 후 양쪽 조합 모두 유효해야 한다.'},\n'DQ':{n:'시장 조작자',t:'marketMaker',d:'새 조합으로 내면 공용 버림패 위 3장의 순서를 뒤집는다.'},"
new_named="'DJ':{n:'강탈자',t:'extortion',d:'상대 공개 조합에서 빼도 유지되는 카드 1장을 내 공개 조합으로 직접 옮긴다. 이동 후 양쪽 조합 모두 유효해야 한다.'},\n'PBDJ':{slot:'DJ',themeId:'point-blank',n:'퀵 리로드',t:'pbQuickReload',d:'접전에서 이 카드를 회수하면, 이번 턴 이미 새 조합을 만들었어도 이 카드를 포함해 새 3장 세트/런을 1회 추가로 만들 수 있다. 회수 카드의 버스트/체인 반환 제한은 그대로.'},\n'DQ':{n:'시장 조작자',t:'marketMaker',d:'새 조합으로 내면 공용 버림패 위 3장의 순서를 뒤집는다.'},"
assert old_named in text,'Quick Reload NAMED anchor changed'
text=text.replace(old_named,new_named,1)

old_sub="subscribeEffectEvent(handleVSignalThemeEvent);\nconst TUTORIAL_STEPS=Object.freeze(["
new_sub="""subscribeEffectEvent(handleVSignalThemeEvent);\nfunction handlePointBlankThemeEvent(packet){if(packet?.event!=='onRecover')return false;const c=packet.card;if(c?.themeId!=='point-blank'||c.tag!=='pbQuickReload'||c.quickReloadNewMeldToken===packet.turnToken)return false;if(typeof isPointBlankClash!=='function'||!isPointBlankClash(packet.actor,packet.meld))return false;c.quickReloadNewMeldToken=packet.turnToken;c.quickReloadConsumedToken=null;if(typeof log==='function')log(`${c.name}: 접전 회수 · 이번 턴 이 카드를 포함한 새 3장 조합을 1회 추가로 만들 수 있습니다. 반환 재사용 제한은 유지됩니다.`,'good');return true}\nsubscribeEffectEvent(handlePointBlankThemeEvent);\nconst TUTORIAL_STEPS=Object.freeze(["""
assert old_sub in text,'theme subscriber anchor changed'
text=text.replace(old_sub,new_sub,1)

old_best="function bestNewMeldForTurn(w,hand=sideObj(w).hand){return bestNewMeld(hand.filter(c=>c.blockedUntilTurn!==state.turnNo),w)}"
new_best="""function quickReloadNewMeldCard(w,cards){return(cards||[]).find(c=>c.owner===w&&c.themeId==='point-blank'&&c.tag==='pbQuickReload'&&c.quickReloadNewMeldToken===state.turnToken&&c.quickReloadConsumedToken!==state.turnToken)||null}\nfunction newMeldAccess(w,cards){const s=sideObj(w),quick=quickReloadNewMeldCard(w,cards);if(!s.newMeldUsed)return{allowed:true,extra:false,quickReloadCard:quick};return{allowed:!!quick,extra:!!quick,quickReloadCard:quick}}\nfunction bestNewMeldForTurn(w,hand=sideObj(w).hand){const usable=hand.filter(c=>c.blockedUntilTurn!==state.turnNo),s=sideObj(w);if(!s.newMeldUsed)return bestNewMeld(usable,w);if(typeof quickReloadNewMeldCard!=='function')return null;let best=null;for(const cs of combinations(usable,3)){if(!quickReloadNewMeldCard(w,cs))continue;const cand=bestNewMeld(cs,w);if(cand&&(!best||cand.score>best.score))best=cand}return best}"""
assert old_best in text,'bestNewMeldForTurn anchor changed'
text=text.replace(old_best,new_best,1)

old_submit="function submitNewMeld(w,cards){const s=sideObj(w);if(s.newMeldUsed||cards.length!==3)return false;"
new_submit="function submitNewMeld(w,cards){const s=sideObj(w),access=typeof newMeldAccess==='function'?newMeldAccess(w,cards):{allowed:!s.newMeldUsed,extra:false,quickReloadCard:null};if(!access.allowed||cards.length!==3)return false;"
assert old_submit in text,'submitNewMeld prefix changed'
text=text.replace(old_submit,new_submit,1)
old_before="if(meldsOf(w).length>=2)return'full';if(!beforeNewMeld(w))return false;removeFromHand(w,cards);"
new_before="if(meldsOf(w).length>=2)return'full';if(!beforeNewMeld(w))return false;if(access.extra&&access.quickReloadCard){access.quickReloadCard.quickReloadConsumedToken=state.turnToken;if(typeof log==='function')log(`${access.quickReloadCard.name}: 퀵 리로드 · 이번 턴 추가 새 조합 권한 사용.`,'good')}removeFromHand(w,cards);"
assert old_before in text,'submitNewMeld access-consume anchor changed'
text=text.replace(old_before,new_before,1)
old_create_event="emitEffectEvent('onMeldCreate',{actor:w,cards:[...cards],type,meld:m,targetSide:w,targetedBy:typeof zeroSightTargetActors==='function'?zeroSightTargetActors(m):[]})"
new_create_event="emitEffectEvent('onMeldCreate',{actor:w,cards:[...cards],type,meld:m,targetSide:w,targetedBy:typeof zeroSightTargetActors==='function'?zeroSightTargetActors(m):[],extraNewMeld:!!access.extra,quickReloadCard:access.quickReloadCard||null})"
assert old_create_event in text,'onMeldCreate Quick Reload anchor changed'
text=text.replace(old_create_event,new_create_event,1)

old_player_guard="if(state.player.newMeldUsed){log('새 조합은 한 턴에 1회만 낼 수 있습니다.','hit');return}"
new_player_guard="const meldAccess=typeof newMeldAccess==='function'?newMeldAccess('player',cs):{allowed:!state.player.newMeldUsed,extra:false};if(!meldAccess.allowed){log('새 조합은 한 턴에 1회만 낼 수 있습니다. 접전에서 회수한 퀵 리로드가 있다면 그 카드를 포함한 추가 새 조합만 예외입니다.','hit');return}"
assert old_player_guard in text,'playerMeld guard anchor changed'
text=text.replace(old_player_guard,new_player_guard,1)

old_button="meldBtn.disabled=!(action&&cs.length===3&&t&&!state.player.newMeldUsed&&state.player.melds.length<2);let meldText='새 3장 조합';if(state.player.newMeldUsed)meldText='새 조합 사용함';"
new_button="const newAccess=cs.length===3&&typeof newMeldAccess==='function'?newMeldAccess('player',cs):{allowed:!state.player.newMeldUsed,extra:false};meldBtn.disabled=!(action&&cs.length===3&&t&&newAccess.allowed&&state.player.melds.length<2);let meldText='새 3장 조합';if(state.player.newMeldUsed&&!newAccess.allowed)meldText='새 조합 사용함';"
assert old_button in text,'updateButtons new-meld anchor changed'
text=text.replace(old_button,new_button,1)
old_set_text="else if(t==='SET')meldText='세트 3장 구축 · 버스트 준비';else if(t==='RUN')meldText='런 3장 구축 · 체인 0';"
new_set_text="else if(t==='SET')meldText=`${newAccess.extra?'퀵 리로드 · 추가 ':''}세트 3장 구축 · 버스트 준비`;else if(t==='RUN')meldText=`${newAccess.extra?'퀵 리로드 · 추가 ':''}런 3장 구축 · 체인 0`;"
assert old_set_text in text,'updateButtons meld label anchor changed'
text=text.replace(old_set_text,new_set_text,1)

old_hint="if(t&&!state.player.newMeldUsed)bits.push(`<span class=\"ok\">${t} 3장 새 조합</span>`);"
new_hint="if(t&&(typeof newMeldAccess!=='function'?!state.player.newMeldUsed:newMeldAccess('player',cs).allowed))bits.push(`<span class=\"ok\">${state.player.newMeldUsed?'퀵 리로드 · 추가 ':''}${t} 3장 새 조합</span>`);"
assert old_hint in text,'renderTargetHint new-meld anchor changed'
text=text.replace(old_hint,new_hint,1)

old_finish="function bestFinishRunAI(w){const s=sideObj(w);if(s.newMeldUsed||s.melds.length<2||!bestNewMeldForTurn(w))return null;"
new_finish="function bestFinishRunAI(w){const s=sideObj(w);if(s.melds.length<2||!bestNewMeldForTurn(w))return null;"
assert old_finish in text,'bestFinishRunAI anchor changed'
text=text.replace(old_finish,new_finish,1)
old_legal="function hasAnyLegalAction(w){const s=sideObj(w);if(!s.newMeldUsed&&s.melds.length<2&&bestNewMeldForTurn(w))return true;"
new_legal="function hasAnyLegalAction(w){const s=sideObj(w);if(s.melds.length<2&&bestNewMeldForTurn(w))return true;"
assert old_legal in text,'hasAnyLegalAction anchor changed'
text=text.replace(old_legal,new_legal,1)

old_ai_nm="const ex=bestExtension('enemy'),nm=!state.enemy.newMeldUsed&&state.enemy.melds.length<2?bestNewMeldForTurn('enemy'):null,rc=bestRecoverAI('enemy'),fr=bestFinishRunAI('enemy');"
new_ai_nm="const ex=bestExtension('enemy'),nm=state.enemy.melds.length<2?bestNewMeldForTurn('enemy'):null,rc=bestRecoverAI('enemy'),fr=bestFinishRunAI('enemy');"
assert old_ai_nm in text,'AI new-meld selection anchor changed'
text=text.replace(old_ai_nm,new_ai_nm,1)
old_ai_submit="if(nm&&!state.enemy.newMeldUsed&&state.enemy.melds.length<2){const r=submitNewMeld('enemy',nm.cards);"
new_ai_submit="if(nm&&state.enemy.melds.length<2){const r=submitNewMeld('enemy',nm.cards);"
assert old_ai_submit in text,'AI new-meld submit anchor changed'
text=text.replace(old_ai_submit,new_ai_submit,1)

# Let AI notice that recovering Quick Reload from its clash can unlock a second new meld.
old_recover_score="const c=m.cards[ci],hyp=s.hand.concat(c);let sc=tunerReadyForRecovery(w,targetSide,m,c)?18:-1;"
new_recover_score="const c=m.cards[ci],hyp=s.hand.concat(c);let sc=tunerReadyForRecovery(w,targetSide,m,c)?18:-1;if(s.newMeldUsed&&c.themeId==='point-blank'&&c.tag==='pbQuickReload'&&typeof isPointBlankClash==='function'&&isPointBlankClash(w,m)){const canReload=combinations(hyp,3).some(cs=>cs.includes(c)&&!!meldType(cs));if(canReload)sc=Math.max(sc,16)}"
assert old_recover_score in text,'AI Quick Reload recovery score anchor changed'
text=text.replace(old_recover_score,new_recover_score,1)

index.write_text(text)

r=road.read_text()
old_road='- [ ] `퀵 리로드` 등 회수 후 새 조합 생성 전용 예외 구현'
new_road='- [x] `퀵 리로드` 회수 후 추가 새 조합 예외 구현 — 기존 기본 규칙이 이미 회수 카드를 같은 턴 첫 새 조합에 허용하므로 죽은 효과를 수정; J♦ 변형 `퀵 리로드`는 접전에서 회수했을 때 그 카드를 포함하는 새 3장 조합을 이번 턴 1회 추가로 허용하며, `recoverReturnOverrideToken`은 부여하지 않아 버스트/체인 반환 재사용 금지는 그대로 유지'
assert old_road in r,'ROADMAP Quick Reload anchor changed'
r=r.replace(old_road,new_road,1)
road.write_text(r)

t=theme.read_text()
old_card='- J♦ `퀵 리로드` — 회수 카드를 같은 턴 새 세트/런 생성 재료로 허용, 반환 재료 제한은 유지.'
new_card='- J♦ `퀵 리로드` — 접전에서 이 카드를 회수하면, 이번 턴 이미 새 조합을 만들었어도 이 카드를 포함하는 새 3장 세트/런을 1회 추가 생성. 반환 재료 제한은 유지. *(기본 규칙이 회수 카드의 첫 새 조합 사용을 이미 허용하므로 효과를 비중복 형태로 수정)*'
assert old_card in t,'THEME_GROUPS Quick Reload card anchor changed'
t=t.replace(old_card,new_card,1)
old_check='- [ ] 회수 카드를 새 조합 재료로만 허용하는 `퀵 리로드` 예외 처리'
new_check='- [x] 회수 카드를 추가 새 조합 재료로만 허용하는 `퀵 리로드` 예외 처리 — 접전 회수 시 카드 단위·현재 턴 토큰으로 추가 새 조합 1회를 허용하며 반환 재사용 예외는 부여하지 않음'
assert old_check in t,'THEME_GROUPS Quick Reload checklist anchor changed'
t=t.replace(old_check,new_check,1)
old_attach_doc='- [ ] 일반 카드가 접전 조합에 붙어도 테마 엔진이 인식하도록 이벤트 설계'
new_attach_doc='- [x] 일반 카드가 접전 조합에 붙어도 테마 엔진이 인식하도록 이벤트 설계 — 붙이기/회수/이동은 카드군 검사 없이 `refreshPointBlankClashMeld`와 `onClashMeldChange`를 거쳐 접전 유지·해제 상태를 갱신'
if old_attach_doc in t:t=t.replace(old_attach_doc,new_attach_doc,1)
theme.write_text(t)

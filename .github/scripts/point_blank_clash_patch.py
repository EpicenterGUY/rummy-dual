from pathlib import Path

index=Path('index.html')
road=Path('ROADMAP.md')
theme=Path('docs/THEME_GROUPS.md')
text=index.read_text()

old_events="const EFFECT_EVENTS=Object.freeze(['onAcquire','onDiscard','onMeldCreate','onAttach','onBurst','onChain','onRecover','onMeldMove','onTargetSet','onTargetClear','onTargetMeldChange','onRummy','onReturnSwitch','onDetonate','onCoreBreak','onTurnStart','onTurnEnd','onRunFinish','onRetire']);"
new_events="const EFFECT_EVENTS=Object.freeze(['onAcquire','onDiscard','onMeldCreate','onAttach','onBurst','onChain','onRecover','onMeldMove','onTargetSet','onTargetClear','onTargetMeldChange','onClashSet','onClashClear','onClashMeldChange','onRummy','onReturnSwitch','onDetonate','onCoreBreak','onTurnStart','onTurnEnd','onRunFinish','onRetire']);"
assert old_events in text,'effect event anchor changed'
text=text.replace(old_events,new_events,1)

anchor="function officialStatusBag(scope,target){"
helpers="""function ensurePointBlankMeta(m){if(!m)return null;m.themeMeta=m.themeMeta||{};m.themeMeta.pointBlank=m.themeMeta.pointBlank||{clashBy:{player:false,enemy:false},clashTurn:{player:null,enemy:null},releaseAtTurnEndStart:{player:null,enemy:null}};return m.themeMeta.pointBlank}\nfunction isPointBlankClash(actor,m){return !!m?.themeMeta?.pointBlank?.clashBy?.[actor]}\nfunction pointBlankClashActors(m){return['player','enemy'].filter(actor=>isPointBlankClash(actor,m))}\nfunction pointBlankClashMeld(actor){for(const side of['player','enemy'])for(const m of meldsOf(side))if(isPointBlankClash(actor,m))return m;return null}\nfunction pointBlankOwnCardCount(actor,m){return(m?.cards||[]).filter(c=>c.owner===actor).length}\nfunction emitPointBlankClashChange(change,m,payload={}){if(!m||typeof emitEffectEvent!=='function')return null;const clashBy=pointBlankClashActors(m);if(!clashBy.length&&!payload.force)return null;return emitEffectEvent('onClashMeldChange',{change,meld:m,meldSide:typeof meldOwnerSide==='function'?meldOwnerSide(m):null,clashBy,...payload})}\nfunction clearPointBlankClash(actor,opts={}){let cleared=0;for(const side of['player','enemy'])for(const m of meldsOf(side)){const meta=m?.themeMeta?.pointBlank;if(!meta?.clashBy?.[actor])continue;if(typeof emitEffectEvent==='function'&&!opts.silentEvent)emitEffectEvent('onClashClear',{actor,meld:m,meldSide:side,reason:opts.reason||'clear',nextMeld:opts.nextMeld||null});meta.clashBy[actor]=false;meta.clashTurn[actor]=null;meta.releaseAtTurnEndStart[actor]=null;cleared++}if(cleared&&!opts.silent&&typeof log==='function')log(`${actor==='player'?'내':'상대'} POINT-BLANK 접전 해제.`,'important');return cleared}\nfunction clearPointBlankClashesOnMeld(m,opts={}){const meta=m?.themeMeta?.pointBlank;if(!meta)return 0;let cleared=0;for(const actor of['player','enemy']){if(!meta.clashBy?.[actor])continue;if(typeof emitEffectEvent==='function'&&!opts.silentEvent)emitEffectEvent('onClashClear',{actor,meld:m,meldSide:typeof meldOwnerSide==='function'?meldOwnerSide(m):null,reason:opts.reason||'retire',nextMeld:null});meta.clashBy[actor]=false;meta.clashTurn[actor]=null;meta.releaseAtTurnEndStart[actor]=null;cleared++}return cleared}\nfunction refreshPointBlankClashMeld(m,opts={}){if(!m)return 0;const meta=m?.themeMeta?.pointBlank;if(!meta)return 0;let touched=0;for(const actor of['player','enemy']){if(!meta.clashBy?.[actor])continue;const ownCards=pointBlankOwnCardCount(actor,m),before=meta.releaseAtTurnEndStart[actor];if(ownCards>0)meta.releaseAtTurnEndStart[actor]=null;else if(meta.releaseAtTurnEndStart[actor]==null){const starts=sideObj(actor)?.turnStarts||0;meta.releaseAtTurnEndStart[actor]=starts+(state.turn===actor?0:1)}if(opts.change&&typeof emitPointBlankClashChange==='function')emitPointBlankClashChange(opts.change,m,{...opts,actor,ownCards,releaseAtTurnEndStart:meta.releaseAtTurnEndStart[actor],pendingChanged:before!==meta.releaseAtTurnEndStart[actor]});touched++}return touched}\nfunction setPointBlankClash(actor,m,opts={}){if(!m||!['player','enemy'].includes(actor))return false;const side=typeof meldOwnerSide==='function'?meldOwnerSide(m):null;if(side&&side!==other(actor))return false;const old=pointBlankClashMeld(actor);if(old===m){refreshPointBlankClashMeld(m);return true}if(old)clearPointBlankClash(actor,{silent:true,reason:'relocate',nextMeld:m});const meta=ensurePointBlankMeta(m);meta.clashBy[actor]=true;meta.clashTurn[actor]=state.turnNo??null;meta.releaseAtTurnEndStart[actor]=null;refreshPointBlankClashMeld(m);if(typeof emitEffectEvent==='function'&&!opts.silentEvent)emitEffectEvent('onClashSet',{actor,meld:m,meldSide:side||null,previousMeld:old||null,ownCards:pointBlankOwnCardCount(actor,m),releaseAtTurnEndStart:meta.releaseAtTurnEndStart[actor],reason:old?'relocate':opts.reason||'set'});if(!opts.silent&&typeof log==='function')log(`${actor==='player'?'내':'상대'} POINT-BLANK 접전 지정 · ${m.type} ${m.cards.length}장.`,'important');return true}\nfunction expirePointBlankClashAtTurnEnd(actor){const m=pointBlankClashMeld(actor);if(!m)return false;const meta=m.themeMeta?.pointBlank;if(!meta?.clashBy?.[actor])return false;const ownCards=pointBlankOwnCardCount(actor,m);if(ownCards>0){meta.releaseAtTurnEndStart[actor]=null;return false}const starts=sideObj(actor)?.turnStarts||0;if(meta.releaseAtTurnEndStart[actor]==null)meta.releaseAtTurnEndStart[actor]=starts;if(starts<meta.releaseAtTurnEndStart[actor])return false;return clearPointBlankClash(actor,{reason:'unmanned-turn-end'})>0}\n"""
assert anchor in text,'point blank helper insertion anchor changed'
text=text.replace(anchor,helpers+anchor,1)

old_recover="if(targetedBy.length&&typeof emitZeroSightTargetChange==='function')emitZeroSightTargetChange('recover',meld,{actionActor:actor,card,free:!!opts.free,automatic:!!opts.automatic,reason:opts.reason||'recover'});return packet}"
new_recover="if(targetedBy.length&&typeof emitZeroSightTargetChange==='function')emitZeroSightTargetChange('recover',meld,{actionActor:actor,card,free:!!opts.free,automatic:!!opts.automatic,reason:opts.reason||'recover'});if(typeof refreshPointBlankClashMeld==='function')refreshPointBlankClashMeld(meld,{change:'recover',actionActor:actor,card,free:!!opts.free,automatic:!!opts.automatic,reason:opts.reason||'recover'});return packet}"
assert old_recover in text,'recovery event anchor changed'
text=text.replace(old_recover,new_recover,1)

old_move="if(sourceTargetedBy.length&&typeof emitZeroSightTargetChange==='function')emitZeroSightTargetChange('moveOut',sourceMeld,{actionActor:actor,card,targetMeld,reason:opts.reason||'move'});if(targetTargetedBy.length&&typeof emitZeroSightTargetChange==='function')emitZeroSightTargetChange('moveIn',targetMeld,{actionActor:actor,card,sourceMeld,reason:opts.reason||'move'});return packet}"
new_move="if(sourceTargetedBy.length&&typeof emitZeroSightTargetChange==='function')emitZeroSightTargetChange('moveOut',sourceMeld,{actionActor:actor,card,targetMeld,reason:opts.reason||'move'});if(targetTargetedBy.length&&typeof emitZeroSightTargetChange==='function')emitZeroSightTargetChange('moveIn',targetMeld,{actionActor:actor,card,sourceMeld,reason:opts.reason||'move'});if(typeof refreshPointBlankClashMeld==='function'){refreshPointBlankClashMeld(sourceMeld,{change:'moveOut',actionActor:actor,card,targetMeld,reason:opts.reason||'move'});refreshPointBlankClashMeld(targetMeld,{change:'moveIn',actionActor:actor,card,sourceMeld,reason:opts.reason||'move'})}return packet}"
assert old_move in text,'meld move event anchor changed'
text=text.replace(old_move,new_move,1)

old_attach="if(typeof emitZeroSightTargetChange==='function')emitZeroSightTargetChange('attach',m,{actionActor:w,cards:[...cards],targetSide,returned:returning||forceReturn,continuation});"
new_attach=old_attach+"if(typeof refreshPointBlankClashMeld==='function')refreshPointBlankClashMeld(m,{change:'attach',actionActor:w,cards:[...cards],targetSide,returned:returning||forceReturn,continuation});"
assert old_attach in text,'attach clash refresh anchor changed'
text=text.replace(old_attach,new_attach,1)

old_retire="if(typeof clearZeroSightTargetsOnMeld==='function')clearZeroSightTargetsOnMeld(m,{reason:'retire'});arr.splice(index,1);"
new_retire="if(typeof clearZeroSightTargetsOnMeld==='function')clearZeroSightTargetsOnMeld(m,{reason:'retire'});if(typeof clearPointBlankClashesOnMeld==='function')clearPointBlankClashesOnMeld(m,{reason:'retire'});arr.splice(index,1);"
assert old_retire in text,'retire clash clear anchor changed'
text=text.replace(old_retire,new_retire,1)

old_turn="function turnEnd(w){if(typeof advanceHandPreparation==='function')advanceHandPreparation(w);if(typeof recordCirculationTurn==='function')recordCirculationTurn(w);"
new_turn="function turnEnd(w){if(typeof advanceHandPreparation==='function')advanceHandPreparation(w);if(typeof expirePointBlankClashAtTurnEnd==='function')expirePointBlankClashAtTurnEnd(w);if(typeof recordCirculationTurn==='function')recordCirculationTurn(w);"
assert old_turn in text,'turnEnd clash expiry anchor changed'
text=text.replace(old_turn,new_turn,1)

index.write_text(text)

r=road.read_text()
old_road='- [ ] 상대 공개 조합 단위 접전 메타데이터 / 1개 제한 / 지연 해제 구현'
new_road='- [x] 상대 공개 조합 단위 접전 메타데이터 / 1개 제한 / 지연 해제 구현 — 접전은 표적과 분리된 `themeMeta.pointBlank`로 관리하고 상대 공개 조합만 지정 가능; 새 접전은 기존 접전을 이전하며, 자신의 카드가 모두 빠지면 다음 자기 턴 종료를 해제 시점으로 예약하고 그 전에 재돌입하면 예약을 취소함'
assert old_road in r,'ROADMAP POINT-BLANK clash anchor changed'
r=r.replace(old_road,new_road,1)
road.write_text(r)

t=theme.read_text()
old_meta='- [ ] 상대 공개 조합 단위 `접전` 메타데이터 설계'
new_meta='- [x] 상대 공개 조합 단위 `접전` 메타데이터 설계 — 공식 상태/표적과 분리된 `themeMeta.pointBlank`에서 접전 소유자·지정 턴·지연 해제 시점을 관리'
old_limit='- [ ] 접전 1개 제한 / 이전 / 아군 카드 부재 시 지연 해제 처리'
new_limit='- [x] 접전 1개 제한 / 이전 / 아군 카드 부재 시 지연 해제 처리 — 각 플레이어는 상대 공개 조합 1개만 접전으로 유지하고, 자신의 카드가 0장이 되면 다음 자기 턴 종료 해제를 예약하되 재돌입하면 예약 취소'
assert old_meta in t and old_limit in t,'THEME_GROUPS POINT-BLANK clash anchors changed'
t=t.replace(old_meta,new_meta,1).replace(old_limit,new_limit,1)
theme.write_text(t)

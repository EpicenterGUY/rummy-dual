from pathlib import Path

root=Path('.')
index=Path('index.html')
road=Path('ROADMAP.md')
theme=Path('docs/THEME_GROUPS.md')

# 1) Canonical display naming: IDs remain zero-sight / point-blank, display names use hyphens.
for path in [index,road,theme,*Path('tests').glob('*.mjs')]:
    if not path.exists():
        continue
    text=path.read_text()
    text=text.replace('ZERO//SIGHT','ZERO-SIGHT').replace('POINT//BLANK','POINT-BLANK')
    path.write_text(text)

text=index.read_text()

old="const EFFECT_EVENTS=Object.freeze(['onAcquire','onDiscard','onMeldCreate','onAttach','onBurst','onChain','onRecover','onRummy','onReturnSwitch','onDetonate','onCoreBreak','onTurnStart','onTurnEnd','onRunFinish','onRetire']);"
new="const EFFECT_EVENTS=Object.freeze(['onAcquire','onDiscard','onMeldCreate','onAttach','onBurst','onChain','onRecover','onMeldMove','onTargetSet','onTargetClear','onTargetMeldChange','onRummy','onReturnSwitch','onDetonate','onCoreBreak','onTurnStart','onTurnEnd','onRunFinish','onRetire']);"
assert old in text, 'EFFECT_EVENTS anchor missing'
text=text.replace(old,new,1)

old="function isZeroSightTarget(actor,m){return !!ensureMeldThemeMeta(m)?.zeroSight?.targetedBy?.[actor]}\nfunction zeroSightTargetMeld(actor){for(const side of['player','enemy'])for(const m of meldsOf(side))if(isZeroSightTarget(actor,m))return m;return null}\nfunction clearZeroSightTarget(actor,opts={}){let cleared=0;for(const side of['player','enemy'])for(const m of meldsOf(side)){const meta=ensureMeldThemeMeta(m)?.zeroSight;if(!meta?.targetedBy?.[actor])continue;meta.targetedBy[actor]=false;meta.targetedTurn[actor]=null;cleared++}if(cleared&&!opts.silent)log(`${actor==='player'?'내':'상대'} ZERO-SIGHT 표적 해제.`,'important');return cleared}\nfunction setZeroSightTarget(actor,m,opts={}){if(!m||!['player','enemy'].includes(actor))return false;const old=zeroSightTargetMeld(actor);if(old===m)return true;clearZeroSightTarget(actor,{silent:true});const meta=ensureMeldThemeMeta(m).zeroSight;meta.targetedBy[actor]=true;meta.targetedTurn[actor]=state.turnNo??null;if(!opts.silent)log(`${actor==='player'?'내':'상대'} ZERO-SIGHT 표적 지정 · ${m.type} ${m.cards.length}장.`,'important');return true}"
new="function isZeroSightTarget(actor,m){return !!ensureMeldThemeMeta(m)?.zeroSight?.targetedBy?.[actor]}\nfunction zeroSightTargetActors(m){return ['player','enemy'].filter(actor=>isZeroSightTarget(actor,m))}\nfunction zeroSightTargetSnapshot(m){return{player:isZeroSightTarget('player',m),enemy:isZeroSightTarget('enemy',m)}}\nfunction zeroSightTargetMeld(actor){for(const side of['player','enemy'])for(const m of meldsOf(side))if(isZeroSightTarget(actor,m))return m;return null}\nfunction emitZeroSightTargetChange(change,m,payload={}){if(!m||typeof emitEffectEvent!=='function')return null;const targetedBy=zeroSightTargetActors(m);if(!targetedBy.length&&!payload.force)return null;return emitEffectEvent('onTargetMeldChange',{change,meld:m,meldSide:typeof meldOwnerSide==='function'?meldOwnerSide(m):null,targetedBy,...payload})}\nfunction clearZeroSightTarget(actor,opts={}){let cleared=0;for(const side of['player','enemy'])for(const m of meldsOf(side)){const meta=ensureMeldThemeMeta(m)?.zeroSight;if(!meta?.targetedBy?.[actor])continue;if(typeof emitEffectEvent==='function'&&!opts.silentEvent)emitEffectEvent('onTargetClear',{actor,meld:m,meldSide:side,reason:opts.reason||'clear',nextMeld:opts.nextMeld||null});meta.targetedBy[actor]=false;meta.targetedTurn[actor]=null;cleared++}if(cleared&&!opts.silent)log(`${actor==='player'?'내':'상대'} ZERO-SIGHT 표적 해제.`,'important');return cleared}\nfunction clearZeroSightTargetsOnMeld(m,opts={}){if(!m)return 0;const meta=ensureMeldThemeMeta(m)?.zeroSight;if(!meta)return 0;let cleared=0;for(const actor of['player','enemy']){if(!meta.targetedBy?.[actor])continue;if(typeof emitEffectEvent==='function'&&!opts.silentEvent)emitEffectEvent('onTargetClear',{actor,meld:m,meldSide:typeof meldOwnerSide==='function'?meldOwnerSide(m):null,reason:opts.reason||'retire',nextMeld:null});meta.targetedBy[actor]=false;meta.targetedTurn[actor]=null;cleared++}return cleared}\nfunction setZeroSightTarget(actor,m,opts={}){if(!m||!['player','enemy'].includes(actor))return false;const old=zeroSightTargetMeld(actor);if(old===m)return true;if(old)clearZeroSightTarget(actor,{silent:true,reason:'retarget',nextMeld:m});const meta=ensureMeldThemeMeta(m).zeroSight;meta.targetedBy[actor]=true;meta.targetedTurn[actor]=state.turnNo??null;if(typeof emitEffectEvent==='function'&&!opts.silentEvent)emitEffectEvent('onTargetSet',{actor,meld:m,meldSide:typeof meldOwnerSide==='function'?meldOwnerSide(m):null,previousMeld:old||null,reason:old?'retarget':opts.reason||'set'});if(!opts.silent)log(`${actor==='player'?'내':'상대'} ZERO-SIGHT 표적 지정 · ${m.type} ${m.cards.length}장.`,'important');return true}"
assert old in text, 'ZERO-SIGHT helper anchor missing'
text=text.replace(old,new,1)

old="function emitRecoveryEvent(actor,card,meld,targetSide=null,opts={}){return emitEffectEvent('onRecover',{actor,card,meld,targetSide:targetSide||meldOwnerSide(meld),free:!!opts.free,automatic:!!opts.automatic,reason:opts.reason||'recover'})}"
new="function emitRecoveryEvent(actor,card,meld,targetSide=null,opts={}){const targetedBy=typeof zeroSightTargetActors==='function'?zeroSightTargetActors(meld):[];const packet=emitEffectEvent('onRecover',{actor,card,meld,targetSide:targetSide||meldOwnerSide(meld),free:!!opts.free,automatic:!!opts.automatic,reason:opts.reason||'recover',targetedBy});if(targetedBy.length&&typeof emitZeroSightTargetChange==='function')emitZeroSightTargetChange('recover',meld,{actionActor:actor,card,free:!!opts.free,automatic:!!opts.automatic,reason:opts.reason||'recover'});return packet}\nfunction emitMeldMoveEvent(actor,card,sourceMeld,targetMeld,opts={}){if(typeof emitEffectEvent!=='function')return null;const sourceTargetedBy=typeof zeroSightTargetActors==='function'?zeroSightTargetActors(sourceMeld):[],targetTargetedBy=typeof zeroSightTargetActors==='function'?zeroSightTargetActors(targetMeld):[];const packet=emitEffectEvent('onMeldMove',{actor,card,sourceMeld,targetMeld,sourceSide:typeof meldOwnerSide==='function'?meldOwnerSide(sourceMeld):null,targetSide:typeof meldOwnerSide==='function'?meldOwnerSide(targetMeld):null,sourceTargetedBy,targetTargetedBy,reason:opts.reason||'move'});if(sourceTargetedBy.length&&typeof emitZeroSightTargetChange==='function')emitZeroSightTargetChange('moveOut',sourceMeld,{actionActor:actor,card,targetMeld,reason:opts.reason||'move'});if(targetTargetedBy.length&&typeof emitZeroSightTargetChange==='function')emitZeroSightTargetChange('moveIn',targetMeld,{actionActor:actor,card,sourceMeld,reason:opts.reason||'move'});return packet}"
assert old in text, 'emitRecoveryEvent anchor missing'
text=text.replace(old,new,1)

old="if(typeof emitEffectEvent==='function')emitEffectEvent('onMeldCreate',{actor:w,cards:[...cards],type,meld:m,targetSide:w});"
new="if(typeof emitEffectEvent==='function')emitEffectEvent('onMeldCreate',{actor:w,cards:[...cards],type,meld:m,targetSide:w,targetedBy:typeof zeroSightTargetActors==='function'?zeroSightTargetActors(m):[]});"
assert old in text, 'onMeldCreate anchor missing'
text=text.replace(old,new,1)

old="if(typeof emitEffectEvent==='function')emitEffectEvent('onAttach',{actor:w,cards:[...cards],type,meld:m,targetSide,returned:returning||forceReturn,continuation,phase:'afterResolve'});"
new="if(typeof emitEffectEvent==='function')emitEffectEvent('onAttach',{actor:w,cards:[...cards],type,meld:m,targetSide,returned:returning||forceReturn,continuation,phase:'afterResolve',targetedBy:typeof zeroSightTargetActors==='function'?zeroSightTargetActors(m):[]});if(typeof emitZeroSightTargetChange==='function')emitZeroSightTargetChange('attach',m,{actionActor:w,cards:[...cards],targetSide,returned:returning||forceReturn,continuation});"
assert old in text, 'onAttach anchor missing'
text=text.replace(old,new,1)

old="m.cards.push(c);m.lastTouchedOwnerStart=sideObj(w).turnStarts;markSetCompletion(om,foe);markSetCompletion(m,w);log(`강탈자: ${cardText(c)}를 상대 ${om.type}에서 새 ${m.type}으로 이동${om.type==='RUN'?' · 상대 CHAIN -1':''}.`,'important');return true}"
new="m.cards.push(c);m.lastTouchedOwnerStart=sideObj(w).turnStarts;markSetCompletion(om,foe);markSetCompletion(m,w);if(typeof emitMeldMoveEvent==='function')emitMeldMoveEvent(w,c,om,m,{reason:'extortion'});log(`강탈자: ${cardText(c)}를 상대 ${om.type}에서 새 ${m.type}으로 이동${om.type==='RUN'?' · 상대 CHAIN -1':''}.`,'important');return true}"
assert old in text, 'Extortion move anchor missing'
text=text.replace(old,new,1)

old="function retireMeld(owner,index=0,reason='정리'){const opts=arguments[3]||{},arr=meldsOf(owner),m=arr[index];if(!m)return;const preserveCards=(opts.preserveCards||[]).filter(Boolean),preserveUids=new Set(preserveCards.map(c=>c.uid));if(typeof emitEffectEvent==='function')emitEffectEvent('onRetire',{owner,meld:m,cards:[...m.cards],reason,phase:'before',preserveCards:[...preserveCards],themeMeta:m.themeMeta||null});arr.splice(index,1);if(m.themeMeta?.zeroSight){m.themeMeta.zeroSight.targetedBy={player:false,enemy:false};m.themeMeta.zeroSight.targetedTurn={player:null,enemy:null}}"
new="function retireMeld(owner,index=0,reason='정리'){const opts=arguments[3]||{},arr=meldsOf(owner),m=arr[index];if(!m)return;const preserveCards=(opts.preserveCards||[]).filter(Boolean),preserveUids=new Set(preserveCards.map(c=>c.uid)),targetedBy=typeof zeroSightTargetActors==='function'?zeroSightTargetActors(m):[];if(typeof emitEffectEvent==='function')emitEffectEvent('onRetire',{owner,meld:m,cards:[...m.cards],reason,phase:'before',preserveCards:[...preserveCards],themeMeta:m.themeMeta||null,targetedBy});if(targetedBy.length&&typeof emitZeroSightTargetChange==='function')emitZeroSightTargetChange('retire',m,{actionActor:null,reason,preserveCards:[...preserveCards]});if(typeof clearZeroSightTargetsOnMeld==='function')clearZeroSightTargetsOnMeld(m,{reason:'retire'});arr.splice(index,1);if(m.themeMeta?.zeroSight){m.themeMeta.zeroSight.targetedBy={player:false,enemy:false};m.themeMeta.zeroSight.targetedTurn={player:null,enemy:null}}"
assert old in text, 'retireMeld anchor missing'
text=text.replace(old,new,1)

index.write_text(text)

# 3) Documentation checkboxes / event contract.
rt=road.read_text()
rt=rt.replace('- [ ] 표적 조합 회수/이동/새 조합 생성 반응 이벤트 정리','- [x] 표적 조합 회수/이동/새 조합 생성 반응 이벤트 정리 — `onTargetSet` / `onTargetClear` / `onTargetMeldChange` / `onMeldMove` 추가, 기존 `onMeldCreate` / `onAttach` / `onRecover` 패킷에 표적 스냅샷 노출')
road.write_text(rt)

doc=theme.read_text()
doc=doc.replace('- [ ] 일반 카드가 표적 조합을 이용해도 테마 효과가 발동하도록 이벤트 설계','- [x] 일반 카드가 표적 조합을 이용해도 테마 효과가 발동하도록 이벤트 설계 — 카드군 검사 없이 `targetedBy` 스냅샷과 `onTargetMeldChange`를 공용 행동에서 발생')
anchor='- [x] 표적 1개 제한 / 이전 / 조합 정리 시 해제 처리\n'
if anchor in doc and 'onTargetSet` / `onTargetClear`' not in doc:
    doc=doc.replace(anchor,anchor+'- [x] 표적 반응 이벤트 잠금: `onTargetSet` / `onTargetClear` / `onTargetMeldChange` / `onMeldMove`; `onRecover` / `onAttach` / `onRetire`에는 당시 `targetedBy` 스냅샷을 포함하고 `onMeldCreate`는 새 조합 생성 반응에 그대로 사용\n',1)
theme.write_text(doc)

print('ZERO-SIGHT naming + target reaction event patch applied')

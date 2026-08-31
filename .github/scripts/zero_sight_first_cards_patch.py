from pathlib import Path

index=Path('index.html')
road=Path('ROADMAP.md')
theme=Path('docs/THEME_GROUPS.md')
text=index.read_text()

# Card definitions: three live ZERO-SIGHT variants.
text=text.replace("'S4':{n:'미끼 사냥꾼',t:'discardPursuit',d:'상대가 직전 턴 버림패를 이용했다면 상대 공개 조합에 붙일 때 그 조합의 내 카드 1장을 무료 회수할 수 있다.'},",
"'S4':{n:'미끼 사냥꾼',t:'discardPursuit',d:'상대가 직전 턴 버림패를 이용했다면 상대 공개 조합에 붙일 때 그 조합의 내 카드 1장을 무료 회수할 수 있다.'},\n'ZSS4':{slot:'S4',themeId:'zero-sight',n:'제압 사격',t:'zsSuppressingFire',d:'내가 표적으로 지정한 상대 공개 조합에 붙이면 봉인 1 또는 고정 중 하나를 선택한다.'},",1)
text=text.replace("'H3':{n:'미끼',t:'bait',d:'상대가 버림패에서 가져가면 원래 주인은 1장 뽑고 손패 1장을 덱 아래로 보낸다.'},",
"'H3':{n:'미끼',t:'bait',d:'상대가 버림패에서 가져가면 원래 주인은 1장 뽑고 손패 1장을 덱 아래로 보낸다.'},\n'ZSH3':{slot:'H3',themeId:'zero-sight',prepRequired:2,n:'호흡 조절',t:'zsBreathControl',d:'손에서 2턴 준비하고 같은 표적을 2턴 이상 유지한 뒤 이 카드를 조합에 사용하면 보호막 16을 얻고 무료 정비 1회를 얻는다.'},",1)
text=text.replace("'CA':{n:'재귀 함수',t:'repeatNumeric',d:'같은 행동의 다른 네임드 중 실제 발동 조건을 만족한 효과 하나를 복제한다. 연결자면 1장 뽑기, 응급 보호구면 보호막 12, 갈아끼우기면 무료 회수 1회. 누적 위력은 복사하지 않는다.'},",
"'CA':{n:'재귀 함수',t:'repeatNumeric',d:'같은 행동의 다른 네임드 중 실제 발동 조건을 만족한 효과 하나를 복제한다. 연결자면 1장 뽑기, 응급 보호구면 보호막 12, 갈아끼우기면 무료 회수 1회. 누적 위력은 복사하지 않는다.'},\n'ZSCA':{slot:'CA',themeId:'zero-sight',n:'관측수',t:'zsObserver',d:'이 카드가 공개 조합에 들어가면 그 조합을 내 표적으로 지정하고 무료 정비 1회를 얻는다.'},",1)

# Unlock pacing and live theme picker.
text=text.replace("items:['S8','H5','VSH5','D9','C8','D10','C3']","items:['S8','H5','VSH5','ZSCA','D9','C8','D10','C3']",1)
text=text.replace("items:['S9','H10','D2','VSD4','C6','SJ','H3']","items:['S9','H10','D2','VSD4','C6','SJ','H3','ZSH3']",1)
text=text.replace("items:['S10','SK','HK','DJ','C10','S4']","items:['S10','SK','HK','DJ','C10','S4','ZSS4']",1)
text=text.replace("'zero-sight':Object.freeze({id:'zero-sight',displayName:'ZERO-SIGHT',short:'정밀 표적',desc:'표적·관측·준비형 카드군. 기반 시스템 구현 중입니다.',themeId:'zero-sight',live:false})",
"'zero-sight':Object.freeze({id:'zero-sight',displayName:'ZERO-SIGHT',short:'정밀 표적',desc:'표적을 지정하고 손패를 준비해 정밀하게 간섭하는 카드군. 일반 카드도 표적 조합을 이용할 수 있습니다.',themeId:'zero-sight',live:true})",1)
text=text.replace("function themeBuildLockText(id){if(id==='v-signal')return'테마 카드 해금 필요 · 전체 2클리어부터';return'개발 중'}",
"function themeBuildLockText(id){if(id==='v-signal')return'테마 카드 해금 필요 · 전체 2클리어부터';if(id==='zero-sight')return'테마 카드 해금 필요 · 전체 2클리어부터';return'개발 중'}",1)

# Tendencies for deck weighting.
text=text.replace("vEncore:['cycle','combo'],vGatherAll:['hold','combo','cycle'],vEndurance:['extend','sustain','cycle']",
"vEncore:['cycle','combo'],vGatherAll:['hold','combo','cycle'],vEndurance:['extend','sustain','cycle'],zsObserver:['control','cycle','tempo'],zsBreathControl:['hold','sustain','cycle'],zsSuppressingFire:['control','status','interact']",1)

# ZERO-SIGHT target age and suppression choice helpers.
anchor="function zeroSightTargetMeld(actor){for(const side of['player','enemy'])for(const m of meldsOf(side))if(isZeroSightTarget(actor,m))return m;return null}\n"
insert="function zeroSightTargetMeld(actor){for(const side of['player','enemy'])for(const m of meldsOf(side))if(isZeroSightTarget(actor,m))return m;return null}\nfunction zeroSightTargetAge(actor,m=zeroSightTargetMeld(actor)){if(!m||!isZeroSightTarget(actor,m))return 0;const since=ensureMeldThemeMeta(m)?.zeroSight?.targetedTurn?.[actor];return since==null?0:Math.max(0,(state.turnNo||0)-since)}\nfunction requestZeroSightSuppressionChoice(w,m,onAsyncResolved=null){if(!m)return false;const apply=kind=>{if(kind==='seal'){if(typeof applyOfficialStatus==='function')applyOfficialStatus('meld',m,'seal',1,{actor:w,silent:true});if(typeof log==='function')log('제압 사격: 표적 조합에 봉인 1.','important')}else{if(typeof applyMeldFixed==='function')applyMeldFixed(m,typeof other==='function'?other(w):null);if(typeof log==='function')log('제압 사격: 표적 조합을 고정.','important')}return kind};if(w==='player'&&state.turn==='player'&&typeof requestEffectChoice==='function'){const opened=requestEffectChoice({title:'제압 사격',text:'내 표적 조합에 적용할 제압 방식을 고르세요.',options:[{key:'seal',label:'봉인 1',detail:'다음 네임드 효과 하나를 막음'},{key:'fixed',label:'고정',detail:'다음 상대 턴 종료까지 회수·이동 불가'}],onChoose:o=>{const kind=o?.key==='seal'?'seal':'fixed';apply(kind);if(typeof onAsyncResolved==='function')onAsyncResolved(kind)}});if(opened)return true}const kind=apply('fixed');if(typeof onAsyncResolved==='function')onAsyncResolved(kind);return false}\n"
assert anchor in text
text=text.replace(anchor,insert,1)

# Free maintenance charges: independent from the normal maintenance use.
old="function maintenanceLimit(w){const s=sideObj(w);if(s.maintenanceUsed||!s.hand.length||ownedRecycleCount(w)<=0)return 0;return hasAnyLegalAction(w)?1:2}\nfunction canMaintenance(w){return maintenanceLimit(w)>0}\nfunction performMaintenance(w,cards){const s=sideObj(w),limit=maintenanceLimit(w),list=(Array.isArray(cards)?cards:[cards]).filter(Boolean).slice(0,limit);if(!list.length||!limit)return[];if(!s.deck.length)recycleIfNeeded(w);if(!s.deck.length)return[];const ids=new Set(s.hand.map(c=>c.uid)),valid=list.filter(c=>ids.has(c.uid));if(!valid.length||valid.length>limit)return[];removeFromHand(w,valid);for(const c of valid){c.fromDiscard=false;c.contractActive=false;c.age=0;s.deck.unshift(c)}const got=[];for(let i=0;i<valid.length;i++){const x=drawOne(w,false);if(x)got.push(x)}s.maintenanceUsed=true;s.actedThisTurn=true;if(typeof getCirculationStats==='function')getCirculationStats().maintenance++;log(`${w==='player'?'YOU':'CPU'} 정비 · 손패 ${valid.length}장을 덱 아래로 보내고 ${got.length}장 교체${limit===2?' (완전 막힘 보정)':''}.`,'important');return got}"
new="function grantFreeMaintenance(w,n=1,label='무료 정비'){const s=sideObj(w),before=Math.max(0,s.freeMaintenanceCharges||0);s.freeMaintenanceCharges=Math.min(1,before+Math.max(0,Number(n)||0));if(s.freeMaintenanceCharges>before&&typeof log==='function')log(`${label}: 무료 정비 1회 준비.`,'good');return s.freeMaintenanceCharges}\nfunction maintenanceLimit(w){const s=sideObj(w);if(!s.hand.length||ownedRecycleCount(w)<=0)return 0;if((s.freeMaintenanceCharges||0)>0)return 1;if(s.maintenanceUsed)return 0;return hasAnyLegalAction(w)?1:2}\nfunction canMaintenance(w){return maintenanceLimit(w)>0}\nfunction performMaintenance(w,cards){const s=sideObj(w),free=(s.freeMaintenanceCharges||0)>0,limit=maintenanceLimit(w),list=(Array.isArray(cards)?cards:[cards]).filter(Boolean).slice(0,limit);if(!list.length||!limit)return[];if(!s.deck.length)recycleIfNeeded(w);if(!s.deck.length)return[];const ids=new Set(s.hand.map(c=>c.uid)),valid=list.filter(c=>ids.has(c.uid));if(!valid.length||valid.length>limit)return[];removeFromHand(w,valid);for(const c of valid){c.fromDiscard=false;c.contractActive=false;c.age=0;s.deck.unshift(c)}const got=[];for(let i=0;i<valid.length;i++){const x=drawOne(w,false);if(x)got.push(x)}if(free)s.freeMaintenanceCharges=Math.max(0,(s.freeMaintenanceCharges||0)-1);else s.maintenanceUsed=true;s.actedThisTurn=true;if(typeof getCirculationStats==='function')getCirculationStats().maintenance++;log(`${w==='player'?'YOU':'CPU'} 정비${free?' · 무료':''} · 손패 ${valid.length}장을 덱 아래로 보내고 ${got.length}장 교체${!free&&limit===2?' (완전 막힘 보정)':''}.`,'important');return got}"
assert old in text
text=text.replace(old,new,1)

# Side initialization / reset lifecycle for free maintenance.
text=text.replace("recoveredThisTurn:false,maintenanceUsed:false,returnedSwitchThisTurn:false","recoveredThisTurn:false,maintenanceUsed:false,freeMaintenanceCharges:0,returnedSwitchThisTurn:false",1)
text=text.replace("s.recoveredThisTurn=false;s.maintenanceUsed=false;s.returnedSwitchThisTurn=false","s.recoveredThisTurn=false;s.maintenanceUsed=false;s.freeMaintenanceCharges=0;s.returnedSwitchThisTurn=false",1)
text=text.replace("s.newMeldUsed=false;s.recoveredThisTurn=false;s.maintenanceUsed=false;s.returnedSwitchThisTurn=false","s.newMeldUsed=false;s.recoveredThisTurn=false;s.maintenanceUsed=false;s.freeMaintenanceCharges=0;s.returnedSwitchThisTurn=false",1)

# Effect cases. Guard helpers so isolated regression VMs remain compatible.
needle="case'jokerDual':if(type==='SET'&&ctx.isAttach&&ctx.totalLength===4)addShield(w,5);if(type==='RUN'&&ctx.isAttach){const paused=requestFreeRecoverChoice(w,ctx.meld,cards,{title:c.name,label:c.name,allowSkip:true,text:'쌍면 조커 효과로 무료 회수할 내 카드를 고르세요.',onAsyncResolved:resume});if(paused)return pause()}break;case'vGatherAll':case'vEndurance':break;"
replacement="case'jokerDual':if(type==='SET'&&ctx.isAttach&&ctx.totalLength===4)addShield(w,5);if(type==='RUN'&&ctx.isAttach){const paused=requestFreeRecoverChoice(w,ctx.meld,cards,{title:c.name,label:c.name,allowSkip:true,text:'쌍면 조커 효과로 무료 회수할 내 카드를 고르세요.',onAsyncResolved:resume});if(paused)return pause()}break;case'zsObserver':if(ctx.meld){if(typeof setZeroSightTarget==='function')setZeroSightTarget(w,ctx.meld);if(typeof grantFreeMaintenance==='function')grantFreeMaintenance(w,1,c.name)}break;case'zsBreathControl':{const prep=typeof handPreparationReady==='function'&&handPreparationReady(c,2,w),age=typeof zeroSightTargetAge==='function'?zeroSightTargetAge(w):0;if(prep&&age>=2){addShield(w,4);if(typeof grantFreeMaintenance==='function')grantFreeMaintenance(w,1,c.name)}break}case'zsSuppressingFire':if(ctx.isAttach&&ctx.targetOwner===foe&&typeof isZeroSightTarget==='function'&&isZeroSightTarget(w,ctx.meld)&&typeof requestZeroSightSuppressionChoice==='function'){const paused=requestZeroSightSuppressionChoice(w,ctx.meld,resume);if(paused)return pause()}break;case'vGatherAll':case'vEndurance':break;"
assert needle in text
text=text.replace(needle,replacement,1)

# UI wording for free maintenance.
text=text.replace("else if(limit){e.className='targetHint good';e.innerHTML=limit===2?'<b>완전 막힘 · 정비 강화</b> · 손패 1~2장을 덱 아래로 보내고 같은 수만큼 교체할 수 있습니다.':'<b>정비 가능</b> · 평소에도 손패 1장을 덱 아래로 보내고 1장 교체할 수 있습니다.'}",
"else if(limit){e.className='targetHint good';e.innerHTML=(state.player.freeMaintenanceCharges||0)>0?'<b>무료 정비 가능</b> · 손패 1장을 덱 아래로 보내고 1장 교체합니다. 일반 정비 횟수는 소모하지 않습니다.':limit===2?'<b>완전 막힘 · 정비 강화</b> · 손패 1~2장을 덱 아래로 보내고 같은 수만큼 교체할 수 있습니다.':'<b>정비 가능</b> · 평소에도 손패 1장을 덱 아래로 보내고 1장 교체할 수 있습니다.'}",1)
text=text.replace("mb.textContent=limit===2?(cs.length>=1&&cs.length<=2?`정비 ${cs.length}장 · 막힘 보정`:'정비 · 최대 2장'):limit===1?(cs.length===1?'정비 1장 교환':'정비 · 1장 선택'):'정비 사용함';",
"mb.textContent=(state.player.freeMaintenanceCharges||0)>0?(cs.length===1?'무료 정비 1장 교환':'무료 정비 · 1장 선택'):limit===2?(cs.length>=1&&cs.length<=2?`정비 ${cs.length}장 · 막힘 보정`:'정비 · 최대 2장'):limit===1?(cs.length===1?'정비 1장 교환':'정비 · 1장 선택'):'정비 사용함';",1)

index.write_text(text)

# Roadmap: live first cards and theme selection.
rt=road.read_text()
marker='- [x] 표적 조합 회수/이동/새 조합 생성 반응 이벤트 정리 — `onTargetSet` / `onTargetClear` / `onTargetMeldChange` / `onMeldMove` 추가, 기존 `onMeldCreate` / `onAttach` / `onRecover` 패킷에 표적 스냅샷 노출\n'
if marker in rt and 'A♣ `관측수` / 3♥ `호흡 조절` / 4♠ `제압 사격` 라이브 구현' not in rt:
    rt=rt.replace(marker,marker+'- [x] A♣ `관측수` / 3♥ `호흡 조절` / 4♠ `제압 사격` 라이브 구현 — 표적 초동, 2턴 준비 보상, 상대 표적 봉인/고정 선택을 첫 실카드 묶음으로 추가\n- [x] ZERO-SIGHT 캐릭터군 선택 라이브 전환 — 첫 카드 해금(전체 2클리어)부터 선택 가능, 테마 카드 최대 4장 우선 편성 후 일반 카드와 혼합\n',1)
road.write_text(rt)

# Canonical theme doc live-card notes.
doc=theme.read_text()
marker='## ZERO-SIGHT 구현 체크\n\n'
if marker in doc and '관측수` / 3♥ `호흡 조절` / 4♠ `제압 사격` 라이브 구현' not in doc:
    doc=doc.replace(marker,marker+'- [x] A♣ `관측수` / 3♥ `호흡 조절` / 4♠ `제압 사격` 라이브 구현. 관측수는 표적+무료 정비 초동, 호흡 조절은 손패 준비 2턴+동일 표적 유지 2턴 보상, 제압 사격은 자신의 상대 표적에 봉인/고정 선택을 제공한다.\n- [x] 무료 정비를 일반 정비와 분리된 턴 내 1회권으로 구현해 ZERO-SIGHT 초동/준비 보상이 기존 정비 횟수를 덮어쓰지 않게 함.\n',1)
theme.write_text(doc)

print('ZERO-SIGHT first live cards patch applied')

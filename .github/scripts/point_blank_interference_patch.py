from pathlib import Path

index=Path('index.html')
road=Path('ROADMAP.md')
theme=Path('docs/THEME_GROUPS.md')
text=index.read_text()

# 1) Live POINT-BLANK H7 variant.
old_h7="'H7':{n:'행운의 일곱',t:'setHeal3',d:'SET에 들어가면 보호막 12. 직접 BURST를 완성하면 보호막 24.'},\n'H8':{n:'응급 보호구',t:'emergencyGear',d:'조합에 들어갈 때 보호막 20. SWITCH가 나를 향하면 보호막 32.'},"
new_h7="'H7':{n:'행운의 일곱',t:'setHeal3',d:'SET에 들어가면 보호막 12. 직접 BURST를 완성하면 보호막 24.'},\n'PBH7':{slot:'H7',themeId:'point-blank',n:'엄폐 교대',t:'pbCoverSwap',d:'접전의 내 카드가 상대 효과의 직접 대상이 될 때 턴당 1회, 같은 효과의 다른 합법적인 내 카드로 대상을 교대한다. 대체 대상이 없으면 보호막 12를 얻고 원래 효과는 계속 해결한다.'},\n'H8':{n:'응급 보호구',t:'emergencyGear',d:'조합에 들어갈 때 보호막 20. SWITCH가 나를 향하면 보호막 32.'},"
assert old_h7 in text,'H7 named anchor changed'
text=text.replace(old_h7,new_h7,1)

# 2) Explicit movement-only event contract: movement never creates BURST/CHAIN/SWITCH return by itself.
old_packet="const packet=emitEffectEvent('onMeldMove',{actor,card,sourceMeld,targetMeld,sourceSide:typeof meldOwnerSide==='function'?meldOwnerSide(sourceMeld):null,targetSide:typeof meldOwnerSide==='function'?meldOwnerSide(targetMeld):null,sourceTargetedBy,targetTargetedBy,reason:opts.reason||'move'});"
new_packet="const packet=emitEffectEvent('onMeldMove',{actor,card,sourceMeld,targetMeld,sourceSide:typeof meldOwnerSide==='function'?meldOwnerSide(sourceMeld):null,targetSide:typeof meldOwnerSide==='function'?meldOwnerSide(targetMeld):null,sourceTargetedBy,targetTargetedBy,reason:opts.reason||'move',combatNeutral:true,powerDelta:0,returnsSwitch:false});"
assert old_packet in text,'onMeldMove packet anchor changed'
text=text.replace(old_packet,new_packet,1)

# 3) Shared movement primitive for current/future theme effects. It mutates melds and metadata only.
old_sub="function handleVSignalThemeEvent(packet){"
new_sub="""function moveCardBetweenMelds(actor,card,sourceMeld,targetMeld,opts={}){if(!card||!sourceMeld||!targetMeld||sourceMeld===targetMeld)return null;const sourceSide=typeof meldOwnerSide==='function'?meldOwnerSide(sourceMeld):null,targetSide=typeof meldOwnerSide==='function'?meldOwnerSide(targetMeld):null,i=sourceMeld.cards.findIndex(c=>c.uid===card.uid);if(i<0)return null;const remain=sourceMeld.cards.filter((_,j)=>j!==i),added=targetMeld.cards.concat(card);if(remain.length<3||meldType(remain)!==sourceMeld.type||meldType(added)!==targetMeld.type)return null;sourceMeld.cards.splice(i,1);if(sourceMeld.type==='RUN')sourceMeld.chain=Math.max(0,(sourceMeld.chain||0)-1);targetMeld.cards.push(card);if(actor&&typeof sideObj==='function')targetMeld.lastTouchedOwnerStart=sideObj(actor)?.turnStarts??targetMeld.lastTouchedOwnerStart;if(typeof markSetCompletion==='function'){markSetCompletion(sourceMeld,sourceSide);markSetCompletion(targetMeld,targetSide)}const event=typeof emitMeldMoveEvent==='function'?emitMeldMoveEvent(actor,card,sourceMeld,targetMeld,{...opts,reason:opts.reason||'move'}):null;return{card,sourceMeld,targetMeld,sourceSide,targetSide,event,combatNeutral:true,powerDelta:0,returnsSwitch:false}}\nfunction handleVSignalThemeEvent(packet){"""
assert old_sub in text,'movement helper insertion anchor changed'
text=text.replace(old_sub,new_sub,1)

# 4) POINT-BLANK Cover Swap: board-passive, once per turn, card-owner based (works inside opponent-owned clash melds).
old_insurance="function insuranceBlocks(actor,targetSide,m,targetCard){"
new_insurance="""function pointBlankCoverSwapSource(owner,m,targetCard=null){if(!owner||!m||typeof isPointBlankClash!=='function'||!isPointBlankClash(owner,m))return null;return(m.cards||[]).find(c=>c.owner===owner&&c.themeId==='point-blank'&&c.tag==='pbCoverSwap'&&c.coverSwapUsedToken!==state.turnToken)||null}\nfunction pointBlankCoverSwapTarget(actor,m,targetCard,replacementCandidates=[]){const owner=targetCard?.owner;if(!owner||actor===owner||!m||typeof isPointBlankClash!=='function'||!isPointBlankClash(owner,m))return{card:targetCard,redirected:false,fallback:false,source:null};const source=pointBlankCoverSwapSource(owner,m,targetCard);if(!source)return{card:targetCard,redirected:false,fallback:false,source:null};const legal=(replacementCandidates||[]).filter(c=>c&&c.uid!==targetCard.uid&&c.owner===owner&&(m.cards||[]).some(x=>x.uid===c.uid)),replacement=(m.cards||[]).find(c=>legal.some(x=>x.uid===c.uid))||null;source.coverSwapUsedToken=state.turnToken;if(replacement){if(typeof log==='function')log(`${source.name}: 엄폐 교대 · ${cardText(targetCard)} 대신 ${cardText(replacement)}이 적대 효과의 대상이 됩니다.`,'good');return{card:replacement,redirected:true,fallback:false,source}}if(typeof addShield==='function')addShield(owner,3);if(typeof log==='function')log(`${source.name}: 교대할 합법 대상이 없어 보호막 12. 원래 적대 효과는 계속 해결됩니다.`,'good');return{card:targetCard,redirected:false,fallback:true,source}}\nfunction insuranceBlocks(actor,targetSide,m,targetCard){"""
assert old_insurance in text,'insurance insertion anchor changed'
text=text.replace(old_insurance,new_insurance,1)

# 5) Extortion keeps its locked Insurance Agent ordering, then allows a legal same-effect Cover Swap redirect.
old_extort="function moveExtortedCard(w,m,choice){if(!choice?.meld||!choice?.card)return false;const current=extortionCandidates(w,m).find(x=>x.meld===choice.meld&&x.card.uid===choice.card.uid);if(!current)return false;const foe=current.targetSide,om=current.meld,c=current.card,i=om.cards.findIndex(x=>x.uid===c.uid);if(i<0)return false;if(insuranceBlocks(w,foe,om,c))return false;om.cards.splice(i,1);if(om.type==='RUN')om.chain=Math.max(0,(om.chain||0)-1);m.cards.push(c);m.lastTouchedOwnerStart=sideObj(w).turnStarts;markSetCompletion(om,foe);markSetCompletion(m,w);if(typeof emitMeldMoveEvent==='function')emitMeldMoveEvent(w,c,om,m,{reason:'extortion'});log(`강탈자: ${cardText(c)}를 상대 ${om.type}에서 새 ${m.type}으로 이동${om.type==='RUN'?' · 상대 CHAIN -1':''}.`,'important');return true}"
new_extort="function moveExtortedCard(w,m,choice){if(!choice?.meld||!choice?.card)return false;const current=extortionCandidates(w,m).find(x=>x.meld===choice.meld&&x.card.uid===choice.card.uid);if(!current)return false;const foe=current.targetSide,om=current.meld;let c=current.card,i=om.cards.findIndex(x=>x.uid===c.uid);if(i<0)return false;if(insuranceBlocks(w,foe,om,c))return false;let swap=null;if(typeof pointBlankCoverSwapTarget==='function'){const alternatives=extortionCandidates(w,m).filter(x=>x.meld===om&&x.card.uid!==c.uid).map(x=>x.card);swap=pointBlankCoverSwapTarget(w,om,c,alternatives);if(swap?.card)c=swap.card;i=om.cards.findIndex(x=>x.uid===c.uid);if(i<0)return false}om.cards.splice(i,1);if(om.type==='RUN')om.chain=Math.max(0,(om.chain||0)-1);m.cards.push(c);m.lastTouchedOwnerStart=sideObj(w).turnStarts;markSetCompletion(om,foe);markSetCompletion(m,w);if(typeof emitMeldMoveEvent==='function')emitMeldMoveEvent(w,c,om,m,{reason:'extortion',interferenceRedirected:!!swap?.redirected,coverSwapFallback:!!swap?.fallback});log(`강탈자: ${cardText(c)}를 상대 ${om.type}에서 새 ${m.type}으로 이동${om.type==='RUN'?' · 상대 CHAIN -1':''}.`,'important');return true}"
assert old_extort in text,'Extortion move anchor changed'
text=text.replace(old_extort,new_extort,1)

# 6) Cut Line has no alternate legal target under its opposite-end rule, so Cover Swap falls back to shield.
old_cut="function cutOppositeEnd(w,targetSide,m,newCard){if(m.type!=='RUN'||m.cards.length<4||meldFixedActive(m))return false;const old=m.cards.filter(c=>c.uid!==newCard.uid&&!isJoker(c));if(!old.length)return false;const nv=RANK_VALUE[newCard.rank]||0,sorted=[...old].sort((a,b)=>RANK_VALUE[a.rank]-RANK_VALUE[b.rank]);const cand=nv<=RANK_VALUE[sorted[0].rank]?sorted.at(-1):sorted[0];if(!cand||cardFixedActive(cand)||protectedByConstruction(m,cand))return false;const i=m.cards.findIndex(c=>c.uid===cand.uid),remain=m.cards.filter((_,j)=>j!==i);if(remain.length<3||meldType(remain)!==m.type)return false;if(insuranceBlocks(w,targetSide,m,cand))return false;m.cards.splice(i,1);m.chain=Math.max(0,(m.chain||0)-1);sideObj(cand.owner).spent.push(cand);markSetCompletion(m,targetSide);log(`절단선: 상대 RUN의 ${cardText(cand)} 소모 · CHAIN -1.`,'important');return true}"
new_cut="function cutOppositeEnd(w,targetSide,m,newCard){if(m.type!=='RUN'||m.cards.length<4||meldFixedActive(m))return false;const old=m.cards.filter(c=>c.uid!==newCard.uid&&!isJoker(c));if(!old.length)return false;const nv=RANK_VALUE[newCard.rank]||0,sorted=[...old].sort((a,b)=>RANK_VALUE[a.rank]-RANK_VALUE[b.rank]);let cand=nv<=RANK_VALUE[sorted[0].rank]?sorted.at(-1):sorted[0];if(!cand||cardFixedActive(cand)||protectedByConstruction(m,cand))return false;let i=m.cards.findIndex(c=>c.uid===cand.uid),remain=m.cards.filter((_,j)=>j!==i);if(remain.length<3||meldType(remain)!==m.type)return false;if(insuranceBlocks(w,targetSide,m,cand))return false;if(typeof pointBlankCoverSwapTarget==='function'){const swap=pointBlankCoverSwapTarget(w,m,cand,[]);if(swap?.card)cand=swap.card;i=m.cards.findIndex(c=>c.uid===cand.uid);remain=m.cards.filter((_,j)=>j!==i);if(i<0||remain.length<3||meldType(remain)!==m.type)return false}m.cards.splice(i,1);m.chain=Math.max(0,(m.chain||0)-1);sideObj(cand.owner).spent.push(cand);markSetCompletion(m,targetSide);log(`절단선: 상대 RUN의 ${cardText(cand)} 소모 · CHAIN -1.`,'important');return true}"
assert old_cut in text,'Cut Line anchor changed'
text=text.replace(old_cut,new_cut,1)

index.write_text(text)

# Roadmap: record both rules and the completed mixed regression gate.
r=road.read_text()
r=r.replace('Updated: 2026-08-31','Updated: 2026-09-01',1)
old_road="- [x] `퀵 리로드` 회수 후 추가 새 조합 예외 구현 — 기존 기본 규칙이 이미 회수 카드를 같은 턴 첫 새 조합에 허용하므로 죽은 효과를 수정; J♦ 변형 `퀵 리로드`는 접전에서 회수했을 때 그 카드를 포함하는 새 3장 조합을 이번 턴 1회 추가로 허용하며, `recoverReturnOverrideToken`은 부여하지 않아 버스트/체인 반환 재사용 금지는 그대로 유지\n- [ ] POINT-BLANK ↔ 일반/V-SIGNAL/ZERO-SIGHT 혼합 회귀 테스트"
new_road="- [x] `퀵 리로드` 회수 후 추가 새 조합 예외 구현 — 기존 기본 규칙이 이미 회수 카드를 같은 턴 첫 새 조합에 허용하므로 죽은 효과를 수정; J♦ 변형 `퀵 리로드`는 접전에서 회수했을 때 그 카드를 포함하는 새 3장 조합을 이번 턴 1회 추가로 허용하며, `recoverReturnOverrideToken`은 부여하지 않아 버스트/체인 반환 재사용 금지는 그대로 유지\n- [x] 이동 효과 전투 중립 원칙 잠금 — `onMeldMove`는 `combatNeutral / powerDelta:0 / returnsSwitch:false`를 명시하고 공용 `moveCardBetweenMelds`는 조합/CHAIN/메타데이터만 갱신하며 이동 자체로 BURST·CHAIN 위력·SWITCH 반환·자동 정리를 만들지 않음\n- [x] 7♥ `엄폐 교대` 적대 대상 교체/fallback 구현 — 접전의 자기 카드가 상대의 직접 간섭 대상일 때 턴당 1회 같은 효과의 다른 합법적인 자기 카드로 교대; 대체 대상이 없으면 보호막 12를 얻고 원래 간섭은 계속 해결\n- [x] POINT-BLANK ↔ 일반/V-SIGNAL/ZERO-SIGHT 혼합 회귀 테스트 — 접전/표적 동시 메타데이터, 테마 비의존 이동, V-SIGNAL·일반 카드 대상 교대, 이동 전투 중립을 실행 회귀로 잠금"
assert old_road in r,'ROADMAP POINT-BLANK tail anchor changed'
r=r.replace(old_road,new_road,1)
road.write_text(r)

# Canonical theme doc.
t=theme.read_text()
t=t.replace('Updated: 2026-08-31','Updated: 2026-09-01',1)
old_card="- 7♥ `엄폐 교대` — 접전 카드가 적대 효과 대상일 때 대상 교체, 실패 시 보호막."
new_card="- 7♥ `엄폐 교대` — 접전의 내 카드가 상대 효과의 직접 대상이 될 때 턴당 1회, 같은 효과가 합법적으로 겨냥할 수 있는 다른 내 카드로 대상을 교대. 대체 대상이 없으면 보호막 12를 얻고 원래 효과는 계속 해결."
assert old_card in t,'Cover Swap card text anchor changed'
t=t.replace(old_card,new_card,1)
t=t.replace('- [ ] 이동 효과는 이동 자체로 버스트/체인/스위치 반환을 발생시키지 않는 기본 원칙 검증','- [x] 이동 효과는 이동 자체로 버스트/체인/스위치 반환을 발생시키지 않는 기본 원칙 검증 — `onMeldMove`가 전투 중립 계약을 명시하고 공용 이동 함수는 공개 조합/CHAIN/표적·접전 메타데이터만 갱신',1)
t=t.replace('- [ ] 접전에서 적대적 대상 교체/보호막 fallback 처리','- [x] 접전에서 적대적 대상 교체/보호막 fallback 처리 — H7 변형 `엄폐 교대`는 카드 소유자 기준 접전을 확인해 턴당 1회 합법 대체 대상으로 교대하고, 대체 불가 시 보호막 12 후 원래 효과를 계속 해결',1)
t=t.replace('- [ ] POINT-BLANK ↔ 일반/V-SIGNAL/ZERO-SIGHT 혼합 회귀 테스트','- [x] POINT-BLANK ↔ 일반/V-SIGNAL/ZERO-SIGHT 혼합 회귀 테스트 — 표적+접전 공존, 일반/타 테마 카드의 접전 이동·적대 대상 교대, 이동의 전투 중립을 실행 검증',1)
theme.write_text(t)

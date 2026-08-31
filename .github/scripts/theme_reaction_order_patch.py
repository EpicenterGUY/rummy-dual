from pathlib import Path

index=Path('index.html')
road=Path('ROADMAP.md')
theme=Path('docs/THEME_GROUPS.md')
text=index.read_text()

# 1) Explicitly document the shared ordering contract next to the event vocabulary.
old="const EFFECT_ACTIONS=Object.freeze(['draw','heal','addShield','addPower','returnSwitch','applyStatus','retireMeld']);"
new=old+"\nconst THEME_REACTION_ORDER=Object.freeze({attach:Object.freeze(['onAttach','onTargetMeldChange','onClashMeldChange','postReturn']),recover:Object.freeze(['onRecover','onTargetMeldChange','onClashMeldChange']),move:Object.freeze(['onMeldMove','onTargetMeldChange:source','onTargetMeldChange:target','onClashMeldChange:source','onClashMeldChange:target'])});"
assert old in text,'effect-action anchor changed'
text=text.replace(old,new,1)

# 2) Shared per-card/per-turn gate for theme reactions. Legacy tokens remain for old saves/tests/readability.
old="function themeDef(id){return id?THEME_GROUPS[id]||null:null}"
new="""function ensureThemeTurnGates(c){if(!c)return null;c.themeTurnGates=c.themeTurnGates||{};return c.themeTurnGates}
function themeTurnGateUsed(c,key,turnToken=state.turnToken){const bag=ensureThemeTurnGates(c);return !!bag&&bag[key]===turnToken}
function claimThemeTurnGate(c,key,turnToken=state.turnToken){const bag=ensureThemeTurnGates(c);if(!bag||bag[key]===turnToken)return false;bag[key]=turnToken;return true}
function themeDef(id){return id?THEME_GROUPS[id]||null:null}"""
assert old in text,'theme helper insertion anchor changed'
text=text.replace(old,new,1)

# 3) Encore uses the generic gate while preserving encoreGrantToken compatibility.
old="function handleVSignalThemeEvent(packet){if(packet?.event!=='onRecover')return false;const c=packet.card;if(c?.themeId!=='v-signal'||c.tag!=='vEncore'||c.encoreGrantToken===packet.turnToken)return false;if(typeof grantRecoveryReturnOverride!=='function')return false;const count=grantRecoveryReturnOverride(packet.actor,c,packet.meld,{});if(!count)return false;c.encoreGrantToken=packet.turnToken;if(typeof log==='function')log(`${c.name}: 회수한 이번 턴 한 번, 다른 합법적인 조합의 버스트/체인 반환 재료로 다시 사용할 수 있습니다.`,'good');return true}"
new="function handleVSignalThemeEvent(packet){if(packet?.event!=='onRecover')return false;const c=packet.card;const gateUsed=typeof themeTurnGateUsed==='function'&&themeTurnGateUsed(c,'vEncoreGrant',packet.turnToken);if(c?.themeId!=='v-signal'||c.tag!=='vEncore'||c.encoreGrantToken===packet.turnToken||gateUsed)return false;if(typeof grantRecoveryReturnOverride!=='function')return false;const count=grantRecoveryReturnOverride(packet.actor,c,packet.meld,{});if(!count)return false;if(typeof claimThemeTurnGate==='function'&&!claimThemeTurnGate(c,'vEncoreGrant',packet.turnToken))return false;c.encoreGrantToken=packet.turnToken;if(typeof log==='function')log(`${c.name}: 회수한 이번 턴 한 번, 다른 합법적인 조합의 버스트/체인 반환 재료로 다시 사용할 수 있습니다.`,'good');return true}"
assert old in text,'V-SIGNAL handler anchor changed'
text=text.replace(old,new,1)

# 4) Quick Reload uses the same shared gate.
old="function handlePointBlankThemeEvent(packet){if(packet?.event!=='onRecover')return false;const c=packet.card;if(c?.themeId!=='point-blank'||c.tag!=='pbQuickReload'||c.quickReloadNewMeldToken===packet.turnToken)return false;if(typeof isPointBlankClash!=='function'||!isPointBlankClash(packet.actor,packet.meld))return false;c.quickReloadNewMeldToken=packet.turnToken;c.quickReloadConsumedToken=null;if(typeof log==='function')log(`${c.name}: 접전 회수 · 이번 턴 이 카드를 포함한 새 3장 조합을 1회 추가로 만들 수 있습니다. 반환 재사용 제한은 유지됩니다.`,'good');return true}"
new="function handlePointBlankThemeEvent(packet){if(packet?.event!=='onRecover')return false;const c=packet.card;const gateUsed=typeof themeTurnGateUsed==='function'&&themeTurnGateUsed(c,'pbQuickReload',packet.turnToken);if(c?.themeId!=='point-blank'||c.tag!=='pbQuickReload'||c.quickReloadNewMeldToken===packet.turnToken||gateUsed)return false;if(typeof isPointBlankClash!=='function'||!isPointBlankClash(packet.actor,packet.meld))return false;if(typeof claimThemeTurnGate==='function'&&!claimThemeTurnGate(c,'pbQuickReload',packet.turnToken))return false;c.quickReloadNewMeldToken=packet.turnToken;c.quickReloadConsumedToken=null;if(typeof log==='function')log(`${c.name}: 접전 회수 · 이번 턴 이 카드를 포함한 새 3장 조합을 1회 추가로 만들 수 있습니다. 반환 재사용 제한은 유지됩니다.`,'good');return true}"
assert old in text,'POINT-BLANK handler anchor changed'
text=text.replace(old,new,1)

# 5) Initialize explicit gate storage on cards.
old="encoreGrantToken:null,encoreReturnUsedToken:null,fuseArmed:false"
new="encoreGrantToken:null,encoreReturnUsedToken:null,themeTurnGates:{},fuseArmed:false"
assert old in text,'makeCard gate state anchor changed'
text=text.replace(old,new,1)

# 6) Cover Swap checks/claims the generic gate but keeps coverSwapUsedToken for compatibility and debug readability.
old="function pointBlankCoverSwapSource(owner,m,targetCard=null){if(!owner||!m||typeof isPointBlankClash!=='function'||!isPointBlankClash(owner,m))return null;return(m.cards||[]).find(c=>c.owner===owner&&c.themeId==='point-blank'&&c.tag==='pbCoverSwap'&&c.coverSwapUsedToken!==state.turnToken)||null}"
new="function pointBlankCoverSwapSource(owner,m,targetCard=null){if(!owner||!m||typeof isPointBlankClash!=='function'||!isPointBlankClash(owner,m))return null;return(m.cards||[]).find(c=>c.owner===owner&&c.themeId==='point-blank'&&c.tag==='pbCoverSwap'&&c.coverSwapUsedToken!==state.turnToken&&!(typeof themeTurnGateUsed==='function'&&themeTurnGateUsed(c,'pbCoverSwap',state.turnToken)))||null}"
assert old in text,'Cover Swap source anchor changed'
text=text.replace(old,new,1)
old="source.coverSwapUsedToken=state.turnToken;if(replacement){"
new="if(typeof claimThemeTurnGate==='function'&&!claimThemeTurnGate(source,'pbCoverSwap',state.turnToken))return{card:targetCard,redirected:false,fallback:false,source:null};source.coverSwapUsedToken=state.turnToken;if(replacement){"
assert old in text,'Cover Swap claim anchor changed'
text=text.replace(old,new,1)

index.write_text(text)

# 7) Roadmap closes the common ordering/gate contract.
r=road.read_text()
old='- [ ] 한 행동에서 표적/접전/RAID/회수 반응이 중첩될 때 트리거 순서와 턴당 1회 제한 명문화'
new='- [x] 한 행동의 테마 반응 순서 + 턴당 1회 게이트 명문화 — 공용 순서는 `기본 행동 이벤트 → ZERO-SIGHT 표적 변화 → POINT-BLANK 접전 변화 → 반환 후 지연 처리`로 잠금. 이동은 표적 source→target 뒤 접전 source→target 순서. 카드 단위 `themeTurnGates` / `claimThemeTurnGate`가 같은 `turnToken`의 중복 테마 반응을 차단하고 기존 앙코르/퀵 리로드/엄폐 교대 토큰은 호환용으로 유지'
assert old in r,'ROADMAP reaction-order anchor changed'
r=r.replace(old,new,1)
road.write_text(r)

# 8) Canonical theme docs close V-SIGNAL common once-per-turn item and record the cross-theme order.
t=theme.read_text()
old='- [ ] 상대 조합 사용 반응의 턴당 1회 처리 공통화'
new='- [x] 테마 반응의 턴당 1회 처리 공통화 — 카드 단위 `themeTurnGates` / `claimThemeTurnGate`를 공용 계약으로 사용. 라이브 앙코르·퀵 리로드·엄폐 교대가 같은 게이트를 공유하며 기존 카드별 토큰은 저장/회귀 호환을 위해 유지. 향후 상대 조합 사용 반응도 같은 키 기반 게이트를 사용'
assert old in t,'V-SIGNAL turn gate checklist anchor changed'
t=t.replace(old,new,1)
common='- 기본 상태인 취약·봉인·고정·보호·재생을 적극 재사용하고, 테마 전용 상태가 공용 엔진을 불필요하게 복제하지 않게 한다.'
add=common+"\n- 한 행동에서 여러 테마가 겹치면 **기본 행동 이벤트 → 표적 변화 반응 → 접전 변화 반응 → 반환 후 지연 처리** 순으로 해결한다. 이동은 표적 source→target을 먼저, 접전 source→target을 다음에 해결한다."
assert common in t,'theme common principle anchor changed'
t=t.replace(common,add,1)
theme.write_text(t)

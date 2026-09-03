from pathlib import Path

INDEX = Path('index.html')
ROAD = Path('ROADMAP.md')
THEMES = Path('docs/THEME_GROUPS.md')
POOL = Path('docs/THEME_FULL_POOL_PLAN.md')


def replace_once(text, old, new, label):
    if new in text:
        return text
    if old not in text:
        raise SystemExit(f'missing anchor: {label}')
    return text.replace(old, new, 1)


h = INDEX.read_text(encoding='utf-8')

h = replace_once(
    h,
    "const EFFECT_EVENTS=Object.freeze(['onAcquire','onDiscard','onMeldCreate','onAttach','onBurst','onChain','onRecover','onMeldMove','onTargetSet','onTargetClear','onTargetMeldChange','onClashSet','onClashClear','onClashMeldChange','onMailSet','onDestinationSet','onArrival','onReturnMail','onRummy','onReturnSwitch','onDetonate','onCoreBreak','onTurnStart','onTurnEnd','onRunFinish','onRetire']);",
    "const EFFECT_EVENTS=Object.freeze(['onAcquire','onDiscard','onMeldCreate','onAttach','onBurst','onChain','onRecover','onMeldMove','onTargetSet','onTargetClear','onTargetMeldChange','onClashSet','onClashClear','onClashMeldChange','onMailSet','onDestinationSet','onArrival','onReturnMail','onPartSet','onDismantle','onReassemble','onRummy','onReturnSwitch','onDetonate','onCoreBreak','onTurnStart','onTurnEnd','onRunFinish','onRetire']);",
    'SCRAP-SHIFT effect events',
)

h = replace_once(
    h,
    "const THEME_REACTION_ORDER=Object.freeze({attach:Object.freeze(['onAttach','onTargetMeldChange','onClashMeldChange','onArrival','postReturn']),recover:Object.freeze(['onRecover','onTargetMeldChange','onClashMeldChange','onReturnMail']),move:Object.freeze(['onMeldMove','onTargetMeldChange:source','onTargetMeldChange:target','onClashMeldChange:source','onClashMeldChange:target','onArrival'])});",
    "const THEME_REACTION_ORDER=Object.freeze({attach:Object.freeze(['onAttach','onTargetMeldChange','onClashMeldChange','onArrival','postReturn']),recover:Object.freeze(['onRecover','onTargetMeldChange','onClashMeldChange','onReturnMail']),move:Object.freeze(['onMeldMove','onTargetMeldChange:source','onTargetMeldChange:target','onClashMeldChange:source','onClashMeldChange:target','onArrival']),dismantle:Object.freeze(['onDismantle','onTargetMeldChange','onClashMeldChange'])});",
    'SCRAP-SHIFT reaction order',
)

h = replace_once(
    h,
    "'mail-route':Object.freeze({id:'mail-route',name:'MAIL-ROUTE',displayName:'MAIL-ROUTE',concept:'우편 · 목적지 · 도착 · 반송 · 재배송'})});",
    "'mail-route':Object.freeze({id:'mail-route',name:'MAIL-ROUTE',displayName:'MAIL-ROUTE',concept:'우편 · 목적지 · 도착 · 반송 · 재배송'}),'scrap-shift':Object.freeze({id:'scrap-shift',name:'SCRAP-SHIFT',displayName:'SCRAP-SHIFT',concept:'부품 · 해체 · 이식 · 재조립',live:false})});",
    'SCRAP-SHIFT theme registry',
)

h = replace_once(
    h,
    "themeTurnGates:{},zsCounterTraceCharged:false",
    "themeTurnGates:{},scrapShiftPart:false,scrapShiftPartSetToken:null,scrapShiftReassembledToken:null,zsCounterTraceCharged:false",
    'card SCRAP-SHIFT state',
)

foundation = r"""
function isScrapShiftPart(c,owner=null){return !!c?.scrapShiftPart&&(!owner||c.owner===owner)}
function scrapShiftCardTurnLocked(c){return !!c&&c.scrapShiftReassembledToken===state.turnToken}
function scrapShiftPartZone(owner,c){if(!owner||!c||c.owner!==owner)return null;const s=sideObj(owner);if(s.hand.includes(c))return'hand';for(const side of[owner,other(owner)])for(const m of meldsOf(side))if((m.cards||[]).includes(c))return'meld';if(s.spent.includes(c))return'spent';if(s.deck.includes(c))return'deck';if(state.discard.includes(c))return'discard';return null}
function clearScrapShiftPart(c,reason='zoneExit',silent=false){if(!c)return false;const had=!!c.scrapShiftPart;c.scrapShiftPart=false;c.scrapShiftPartSetToken=null;c.scrapShiftReassembledToken=null;if(had&&!silent&&typeof log==='function')log(`${c.name||cardText(c)}: 부품 표식 해제 · ${reason}.`,'important');return had}
function setScrapShiftPart(owner,c,opts={}){if(!owner||!c||c.owner!==owner)return false;const zone=scrapShiftPartZone(owner,c);if(zone!=='hand'&&zone!=='meld')return false;if(c.scrapShiftPart)return true;c.scrapShiftPart=true;c.scrapShiftPartSetToken=state.turnToken;if(typeof emitEffectEvent==='function')emitEffectEvent('onPartSet',{actor:owner,owner,card:c,zone,reason:opts.reason||'partSet'});if(!opts.silent&&typeof log==='function')log(`${opts.label||'SCRAP-SHIFT'}: ${cardText(c)}를 부품으로 지정.`,'good');return true}
function scrapShiftDismantleAccess(owner,m,c){if(!owner||!m||!c||c.owner!==owner||!isScrapShiftPart(c,owner))return{allowed:false,reason:'part'};const sourceSide=typeof meldOwnerSide==='function'?meldOwnerSide(m):null;if(!sourceSide)return{allowed:false,reason:'meld'};if((typeof meldFixedActive==='function'&&meldFixedActive(m))||(typeof cardFixedActive==='function'&&cardFixedActive(c)))return{allowed:false,reason:'fixed'};const i=(m.cards||[]).findIndex(x=>x.uid===c.uid);if(i<0)return{allowed:false,reason:'missing'};const remain=m.cards.filter((_,j)=>j!==i);if(remain.length<3||meldType(remain)!==m.type)return{allowed:false,reason:'invalid'};return{allowed:true,sourceSide,index:i,remain}}
function dismantleScrapShiftPart(owner,m,c,opts={}){const access=scrapShiftDismantleAccess(owner,m,c);if(!access.allowed)return null;const targetedBy=typeof zeroSightTargetActors==='function'?zeroSightTargetActors(m):[];m.cards.splice(access.index,1);if(typeof clearCardActiveRank==='function')clearCardActiveRank(c);if(typeof clearMailRouteCard==='function')clearMailRouteCard(c,'해체·소모패',true);c.fromDiscard=false;c.contractActive=false;c.age=0;if(m.type==='RUN')m.chain=Math.max(0,(m.chain||0)-1);sideObj(owner).spent.push(c);if(typeof markSetCompletion==='function')markSetCompletion(m,access.sourceSide);const packet=typeof emitEffectEvent==='function'?emitEffectEvent('onDismantle',{actor:owner,owner,card:c,meld:m,sourceSide:access.sourceSide,reason:opts.reason||'dismantle',combatNeutral:true,powerDelta:0,returnsSwitch:false}):null;if(targetedBy.length&&typeof emitZeroSightTargetChange==='function')emitZeroSightTargetChange('dismantle',m,{actionActor:owner,card:c,reason:opts.reason||'dismantle'});if(typeof refreshPointBlankClashMeld==='function')refreshPointBlankClashMeld(m,{change:'dismantle',actionActor:owner,card:c,reason:opts.reason||'dismantle'});if(!opts.silent&&typeof log==='function')log(`${opts.label||'SCRAP-SHIFT'}: ${cardText(c)} 해체 · 소모패로 이동${m.type==='RUN'?' · 체인 -1':''}.`,'important');return{card:c,meld:m,sourceSide:access.sourceSide,event:packet,combatNeutral:true,powerDelta:0,returnsSwitch:false}}
function reassembleScrapShiftPart(owner,c,opts={}){if(!owner||!c||c.owner!==owner||!isScrapShiftPart(c,owner))return null;const s=sideObj(owner),i=s.spent.findIndex(x=>x.uid===c.uid);if(i<0)return null;s.spent.splice(i,1);clearScrapShiftPart(c,'재조립',true);c.blockedUntilTurn=state.turnNo;c.scrapShiftReassembledToken=state.turnToken;c.fromDiscard=false;c.contractActive=false;c.age=0;if(typeof enterHand==='function')enterHand(owner,c);else s.hand.push(c);const packet=typeof emitEffectEvent==='function'?emitEffectEvent('onReassemble',{actor:owner,owner,card:c,reason:opts.reason||'reassemble',blockedTurn:state.turnNo}):null;if(!opts.silent&&typeof log==='function')log(`${opts.label||'SCRAP-SHIFT'}: ${cardText(c)} 재조립 · 손패 복귀, 이번 턴 사용 불가.`,'good');return{card:c,event:packet}}
""".strip()

h = replace_once(
    h,
    "function ensureMailRouteMeta(m){if(!m)return null;",
    foundation + "\nfunction ensureMailRouteMeta(m){if(!m)return null;",
    'SCRAP-SHIFT helper block',
)

h = replace_once(
    h,
    "function pushDiscard(c){if(typeof clearMailRouteCard==='function')clearMailRouteCard(c,'버림패',true);",
    "function pushDiscard(c){if(typeof clearMailRouteCard==='function')clearMailRouteCard(c,'버림패',true);if(typeof clearScrapShiftPart==='function')clearScrapShiftPart(c,'공용 버림패',true);",
    'discard clears part',
)

h = replace_once(
    h,
    "function recycleIfNeeded(w){const s=sideObj(w);if(s.deck.length)return 0;const spent=s.spent.splice(0),ownedDiscard=[];",
    "function recycleIfNeeded(w){const s=sideObj(w);if(s.deck.length)return 0;const spent=s.spent.splice(0),ownedDiscard=[];",
    'recycle anchor noop',
)
h = replace_once(
    h,
    "for(const c of pool)if(typeof clearMailRouteCard==='function')clearMailRouteCard(c,'개인 덱 재순환',true);s.deck=shuffle(pool);",
    "for(const c of pool){if(typeof clearMailRouteCard==='function')clearMailRouteCard(c,'개인 덱 재순환',true);if(typeof clearScrapShiftPart==='function')clearScrapShiftPart(c,'개인 덱 재순환',true)}s.deck=shuffle(pool);",
    'recycle clears part',
)

h = replace_once(
    h,
    "if(typeof clearMailRouteCard==='function')clearMailRouteCard(c,'전체 재순환',true);if(typeof clearCardActiveRank==='function')clearCardActiveRank(c);",
    "if(typeof clearMailRouteCard==='function')clearMailRouteCard(c,'전체 재순환',true);if(typeof clearScrapShiftPart==='function')clearScrapShiftPart(c,'전체 재순환',true);if(typeof clearCardActiveRank==='function')clearCardActiveRank(c);",
    'full recirculation clears part',
)

h = replace_once(
    h,
    "if(typeof clearMailRouteCard==='function')clearMailRouteCard(chosen,'덱 아래',true);side.deck.unshift(chosen);",
    "if(typeof clearMailRouteCard==='function')clearMailRouteCard(chosen,'덱 아래',true);if(typeof clearScrapShiftPart==='function')clearScrapShiftPart(chosen,'덱 아래',true);side.deck.unshift(chosen);",
    'hand bottom clears part',
)

h = replace_once(
    h,
    "function performMaintenance(w,cards){const s=sideObj(w),limit=maintenanceLimit(w),list=(Array.isArray(cards)?cards:[cards]).filter(Boolean).slice(0,limit);",
    "function performMaintenance(w,cards){const s=sideObj(w),limit=maintenanceLimit(w),list=(Array.isArray(cards)?cards:[cards]).filter(c=>c&&(!(typeof scrapShiftCardTurnLocked==='function')||!scrapShiftCardTurnLocked(c))).slice(0,limit);",
    'maintenance rejects reassembled card',
)
h = replace_once(
    h,
    "if(typeof clearMailRouteCard==='function')clearMailRouteCard(c,'정비',true);s.deck.unshift(c)",
    "if(typeof clearMailRouteCard==='function')clearMailRouteCard(c,'정비',true);if(typeof clearScrapShiftPart==='function')clearScrapShiftPart(c,'정비·개인 덱',true);s.deck.unshift(c)",
    'maintenance clears part',
)

h = replace_once(
    h,
    "function acquireDiscardCard(w,indexFromTop=0){const s=sideObj(w),idx=state.discard.length-1-indexFromTop;if(idx<0)return null;const[c]=state.discard.splice(idx,1),oldOwner=c.owner;",
    "function acquireDiscardCard(w,indexFromTop=0){const s=sideObj(w),idx=state.discard.length-1-indexFromTop;if(idx<0)return null;const[c]=state.discard.splice(idx,1),oldOwner=c.owner;if(typeof clearScrapShiftPart==='function')clearScrapShiftPart(c,'공용 버림패 획득',true);",
    'discard acquisition safety clear',
)

h = replace_once(
    h,
    "recycleIfNeeded(w);const c=s.deck.pop();if(!c)return null;c.fromDiscard=false;",
    "recycleIfNeeded(w);const c=s.deck.pop();if(!c)return null;if(typeof clearScrapShiftPart==='function')clearScrapShiftPart(c,'개인 덱 획득',true);c.fromDiscard=false;",
    'deck draw safety clear',
)

h = replace_once(
    h,
    "function chooseAIDiscard(exclude=new Set()){const h=state.enemy.hand,s=h.filter(c=>!exclude.has(c.uid)).map(c=>({c,score:aiKeepScore(c,h)}));",
    "function chooseAIDiscard(exclude=new Set()){const h=state.enemy.hand,s=h.filter(c=>!exclude.has(c.uid)&&(!(typeof scrapShiftCardTurnLocked==='function')||!scrapShiftCardTurnLocked(c))).map(c=>({c,score:aiKeepScore(c,h)}));",
    'AI discard lock',
)
h = replace_once(
    h,
    "function chooseAIMaintenanceCards(){const h=state.enemy.hand.map(c=>({c,score:aiKeepScore(c,state.enemy.hand)})).sort((a,b)=>a.score-b.score);",
    "function chooseAIMaintenanceCards(){const h=state.enemy.hand.filter(c=>(!(typeof scrapShiftCardTurnLocked==='function')||!scrapShiftCardTurnLocked(c))).map(c=>({c,score:aiKeepScore(c,state.enemy.hand)})).sort((a,b)=>a.score-b.score);",
    'AI maintenance lock',
)

h = replace_once(
    h,
    "function playerMaintenance(){if(state.turn!=='player'||state.phase!=='action')return;const limit=maintenanceLimit('player');",
    "function playerMaintenance(){if(state.turn!=='player'||state.phase!=='action')return;const limit=maintenanceLimit('player');",
    'player maintenance anchor noop',
)
h = replace_once(
    h,
    "const cs=selectedCards();if(!tutorialAllows('maintenance',{cards:cs}))",
    "const cs=selectedCards();if(cs.some(c=>typeof scrapShiftCardTurnLocked==='function'&&scrapShiftCardTurnLocked(c))){log('재조립한 카드는 이번 턴 정비할 수 없습니다.','hit');return}if(!tutorialAllows('maintenance',{cards:cs}))",
    'player maintenance lock message',
)

h = replace_once(
    h,
    "const c=cs[0];if(typeof notePointBlankTurnAction==='function')notePointBlankTurnAction('player','discard');",
    "const c=cs[0];if(typeof scrapShiftCardTurnLocked==='function'&&scrapShiftCardTurnLocked(c)){log('재조립한 카드는 이번 턴 버릴 수 없습니다.','hit');return}if(typeof notePointBlankTurnAction==='function')notePointBlankTurnAction('player','discard');",
    'player discard lock',
)

# Top-deck reservation paths are direct personal-deck transitions.
h = replace_once(
    h,
    "if(typeof clearMailRouteCard==='function')clearMailRouteCard(c,'덱 예약',true);state.player.deck.push(c);",
    "if(typeof clearMailRouteCard==='function')clearMailRouteCard(c,'덱 예약',true);if(typeof clearScrapShiftPart==='function')clearScrapShiftPart(c,'덱 예약',true);state.player.deck.push(c);",
    'player top-deck reservation clears part',
)
h = replace_once(
    h,
    "if(typeof clearMailRouteCard==='function')clearMailRouteCard(d,'덱 예약',true);state.enemy.deck.push(d);",
    "if(typeof clearMailRouteCard==='function')clearMailRouteCard(d,'덱 예약',true);if(typeof clearScrapShiftPart==='function')clearScrapShiftPart(d,'덱 예약',true);state.enemy.deck.push(d);",
    'enemy top-deck reservation clears part',
)

# Joker King returns directly to a personal deck during retirement.
h = replace_once(
    h,
    "if(c.tag==='jokerKing'){if(typeof clearMailRouteCard==='function')clearMailRouteCard(c,'조합 정리·덱 귀환',true);const home=c.originOwner||c.owner;",
    "if(c.tag==='jokerKing'){if(typeof clearMailRouteCard==='function')clearMailRouteCard(c,'조합 정리·덱 귀환',true);if(typeof clearScrapShiftPart==='function')clearScrapShiftPart(c,'조합 정리·덱 귀환',true);const home=c.originOwner||c.owner;",
    'Joker King deck return clears part',
)

# Render the physical non-stacking part marker. Keep it independent from theme identity.
h = replace_once(
    h,
    ".mailCardMark{position:absolute;z-index:7;left:5px;bottom:5px;padding:1px 3px;border:1px solid #5a4218;background:#f1d690;color:#34260d;font-size:6px;font-weight:900}",
    ".mailCardMark{position:absolute;z-index:7;left:5px;bottom:5px;padding:1px 3px;border:1px solid #5a4218;background:#f1d690;color:#34260d;font-size:6px;font-weight:900}.scrapPartMark{position:absolute;z-index:7;right:5px;bottom:5px;padding:1px 3px;border:1px solid #3c5963;background:#9ac6c8;color:#13252a;font-size:6px;font-weight:900}",
    'part mark CSS',
)
h = replace_once(
    h,
    "mailMark=typeof isMailRouteCard==='function'&&isMailRouteCard(c)?'<div class=\"mailCardMark\">우편</div>':'',rankClass=",
    "mailMark=typeof isMailRouteCard==='function'&&isMailRouteCard(c)?'<div class=\"mailCardMark\">우편</div>':'',partMark=typeof isScrapShiftPart==='function'&&isScrapShiftPart(c)?'<div class=\"scrapPartMark\">부품</div>':'',rankClass=",
    'card part marker variable',
)
h = replace_once(
    h,
    "${rankMark}${mailMark}${c.named?`<div class=\"namedMark\">${c.name}</div>`:''}</div>`}",
    "${rankMark}${mailMark}${partMark}${c.named?`<div class=\"namedMark\">${c.name}</div>`:''}</div>`}",
    'card part marker output',
)

INDEX.write_text(h, encoding='utf-8')

road = ROAD.read_text(encoding='utf-8')
road_anchor = """## M9 — Jokers and fields
"""
road_insert = """## M8SS — SCRAP-SHIFT 24/24 풀 카드군 · 개발 중
부품 표식을 일반/다른 테마의 내 소유 카드에도 붙여 해체·이식·재조립하는 순환형 오픈 테마. 24장 전체가 끝날 때까지 일반 카드군 선택/보상에는 노출하지 않는다.

- [x] `SCRAP-SHIFT` 테마 레지스트리 추가 — 아직 `live:false`
- [x] `부품` 비중첩 카드 표식 + 손패/공개 조합/소모패 유지 + 버림패/개인 덱 진입 시 정리 기반 구현
- [x] 공용 파생 이벤트 `onPartSet` / `onDismantle` / `onReassemble` 추가
- [x] 해체 공용 헬퍼 — 조합 유효성 유지, RUN 체인 -1, 회수와 분리, 전투 중립, 표적→접전 갱신
- [x] 재조립 공용 헬퍼 — 소모패 부품→손패, 표식 소비, 같은 턴 조합/버리기/정비 금지
- [x] 부품 표식 UI 추가 — 테마 카드 여부와 무관하게 실제 카드에 `부품` 표시
- [x] AI 기본 버리기/정비가 재조립 잠금 카드를 자발적으로 소비하지 않도록 공용 잠금 적용
- [ ] 24장 / 수트별 6장 정의 및 실제 효과 구현
- [ ] 이식 카드군 효과를 기존 `onMeldMove` 공용 이동과 연결
- [ ] 해금·도감·자동 테마 빌드·체험전 연결 후 일반 보상 승격
- [ ] SCRAP-SHIFT 단일/모든 2테마/일반 mixed + 전체 회귀

## M9 — Jokers and fields
"""
if '## M8SS — SCRAP-SHIFT 24/24 풀 카드군 · 개발 중' not in road:
    if road_anchor not in road:
        raise SystemExit('missing ROADMAP M9 anchor')
    road = road.replace(road_anchor, road_insert, 1)
ROAD.write_text(road, encoding='utf-8')

themes = THEMES.read_text(encoding='utf-8')
themes = themes.replace(
    "- 한 행동에서 여러 테마가 겹치면 **기본 행동 이벤트 → 표적 변화 반응 → 접전 변화 반응 → 반환 후 지연 처리** 순으로 해결한다. 이동은 표적 source→target을 먼저, 접전 source→target을 다음에 해결한다.",
    "- 한 행동에서 여러 테마가 겹치면 **기본 행동 이벤트 → 부품 파생 반응(해당 시) → 표적 변화 반응 → 접전 변화 반응 → 우편 도착/반송 → 반환 후 지연 처리** 순으로 해결한다. 이동은 표적 source→target을 먼저, 접전 source→target을 다음에 해결하고 마지막에 우편 도착을 파생한다. 해체는 `onDismantle → 표적 변화 → 접전 변화`를 따른다.",
    1,
)
themes = themes.replace(
    "후속 정식 테마 후보. **카드 풀과 부품 규칙은 설계 잠금됐지만 아직 라이브 카드군은 아니다.** 별도 고철 포인트나 부품 개수 자원을 만들지 않고, 실제 카드에 붙는 표식과 기존 손패·공개 조합·소모패 이동만 사용한다.",
    "후속 정식 테마 후보. **카드 풀과 부품 규칙은 설계 잠금됐고 공용 엔진 기반 구현을 시작했지만, 24장 카드는 아직 라이브 카드군이 아니다.** 별도 고철 포인트나 부품 개수 자원을 만들지 않고, 실제 카드에 붙는 표식과 기존 손패·공개 조합·소모패 이동만 사용한다.",
    1,
)
lock_anchor = "- [x] 전용 숫자 자원 없이 부품 존재/이동/행동 종류만 참조\n"
lock_new = lock_anchor + "- [x] 엔진 1차 기반 — `SCRAP-SHIFT` 비라이브 레지스트리, 카드별 부품 표식/수명주기, `onPartSet`/`onDismantle`/`onReassemble`, 해체·재조립 공용 헬퍼, 재조립 동일 턴 잠금, 부품 UI 표시 구현\n- [ ] 24장 전체 정의/효과/해금/도감/덱빌더/체험전 연결 뒤 카드군 라이브 승격\n"
if '- [x] 엔진 1차 기반 — `SCRAP-SHIFT` 비라이브 레지스트리' not in themes:
    if lock_anchor not in themes:
        raise SystemExit('missing SCRAP-SHIFT lock anchor')
    themes = themes.replace(lock_anchor, lock_new, 1)
THEMES.write_text(themes, encoding='utf-8')

pool = POOL.read_text(encoding='utf-8')
pool = pool.replace(
    "### MAIL-ROUTE\n\n- 정식 후보: 28장 / 수트별 7장\n- 현재 상태: 규칙·후보 풀 설계 완료, 라이브 아님\n- 정책: `우편/목적지/도착/반송` 공용 계약과 28장 효과 구현을 함께 준비한 뒤 라이브한다.",
    "### MAIL-ROUTE\n\n- 정식 후보: 28장 / 수트별 7장\n- 현재 상태: **28/28 라이브 구현 완료**\n- 정책: `우편/목적지/도착/반송` 공용 계약과 28장 효과가 일반 플레이 풀에 통합되어 있다.",
    1,
)
pool = pool.replace(
    "### SCRAP-SHIFT\n\n- 정식 후보: 24장 / 수트별 6장\n- 현재 상태: 규칙·후보 풀 설계 완료, 라이브 아님\n- 정책: `부품/해체/이식/재조립` 공용 계약과 24장 효과 구현을 함께 준비한 뒤 라이브한다.",
    "### SCRAP-SHIFT\n\n- 정식 후보: 24장 / 수트별 6장\n- 현재 상태: **규칙·후보 풀 잠금 + 공용 엔진 1차 기반 구현 중, 24장 미라이브**\n- 정책: `부품/해체/이식/재조립` 공용 계약을 먼저 회귀로 잠근 뒤 24장 전체 효과·해금·도감·빌드·체험전을 한 릴리스 단위로 완성한다. 현재는 부품 표식/수명주기, 해체·재조립 헬퍼, 파생 이벤트와 동일 턴 잠금까지 기반 구현한다.",
    1,
)
POOL.write_text(pool, encoding='utf-8')

print('SCRAP-SHIFT foundation patch applied')

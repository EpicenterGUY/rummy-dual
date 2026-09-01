from pathlib import Path

index=Path('index.html')
road=Path('ROADMAP.md')
doc=Path('docs/ASYMMETRIC_RANK_PROTOTYPE.md')
s=index.read_text()
r=road.read_text()

marker='function normalizePrototypeRank('
if marker in s:
    raise SystemExit('M11B rank scaffold already installed')

uid_anchor='let uidSeq=1;\nfunction makeCard('
helpers=r'''let uidSeq=1;
function normalizePrototypeRank(rank,fallback=null){return rank!=null&&Object.prototype.hasOwnProperty.call(RANK_VALUE,rank)?rank:fallback}
function ensureRankPrototype(c){if(!c)return null;if(c.suit==='J'){c.baseRank=null;c.topRank=null;c.bottomRank=null;c.activeRank=null;c.rankOrientation=null;return c}const base=normalizePrototypeRank(c.baseRank,normalizePrototypeRank(c.rank,null));if(!base)return c;c.baseRank=base;c.topRank=normalizePrototypeRank(c.topRank,base);c.bottomRank=normalizePrototypeRank(c.bottomRank,base);const active=normalizePrototypeRank(c.activeRank,null);if(active&&(active===c.topRank||active===c.bottomRank)){c.activeRank=active;c.rank=active;if(c.rankOrientation!=='top'&&c.rankOrientation!=='bottom')c.rankOrientation=active===c.bottomRank&&active!==c.topRank?'bottom':'top'}else{c.activeRank=null;c.rankOrientation=null;c.rank=base}return c}
function cardPrintedRanks(c){if(!c||c.suit==='J')return[];ensureRankPrototype(c);return[{orientation:'top',rank:c.topRank},{orientation:'bottom',rank:c.bottomRank}]}
function isAsymmetricRankCard(c){const p=cardPrintedRanks(c);return p.length===2&&p[0].rank!==p[1].rank}
function cardRuleRank(c){if(!c)return null;if(c.suit==='J')return c.rank||null;ensureRankPrototype(c);return c.activeRank||c.baseRank||c.rank||null}
function chooseCardActiveRank(c,rank,orientation=null){if(!c||c.suit==='J')return false;ensureRankPrototype(c);const options=cardPrintedRanks(c),pick=orientation?options.find(x=>x.orientation===orientation&&x.rank===rank):options.find(x=>x.rank===rank);if(!pick)return false;c.activeRank=pick.rank;c.rankOrientation=pick.orientation;c.rank=pick.rank;return true}
function clearCardActiveRank(c){if(!c)return null;if(c.suit==='J'){c.activeRank=null;c.rankOrientation=null;return c}ensureRankPrototype(c);c.activeRank=null;c.rankOrientation=null;c.rank=c.baseRank;return c}
function rankChoiceState(c){const printed=cardPrintedRanks(c);return{baseRank:c?.baseRank||c?.rank||null,topRank:printed[0]?.rank||null,bottomRank:printed[1]?.rank||null,activeRank:c?.activeRank||null,orientation:c?.rankOrientation||null,asymmetric:printed.length===2&&printed[0].rank!==printed[1].rank}}
function makeCard('''
if s.count(uid_anchor)!=1:
    raise SystemExit(f'uid/makeCard anchor mismatch: {s.count(uid_anchor)}')
s=s.replace(uid_anchor,helpers,1)

old_make="function makeCard(suit,rank,named,owner,variantId=null){const slot=suit==='J'?'J':suit+rank,id=variantId||(suit==='J'?rank:slot),def=named?NAMED[id]:null;return{uid:uidSeq++,id,slot,suit,rank,owner,originOwner:owner,name:def?.n||'순수 카드',effect:def?.d||'효과 없음. 기본 랭크와 무늬만 사용한다.',tag:def?.t||null,themeId:def?.themeId||null,prepRequired:Math.max(0,Number(def?.prepRequired)||0),named:!!def,age:0,handPrep:{turns:0,exitTurns:0,exitTurnToken:null,exitOwner:null},fromDiscard:false,smuggledActive:false,smuggledTurnToken:null,enteredMeldToken:null,suppressEffectToken:null,contractActive:false,healCharge:0,recoveredToken:null,recoverReturnOverrideToken:null,encoreGrantToken:null,encoreReturnUsedToken:null,themeTurnGates:{},fuseArmed:false,flexSuitOffSuit:false,officialStatus:{seal:0,fixed:0,protect:0,fixedOwner:null,fixedThroughStart:null},status:{charged:0,reserved:0,cursed:0,pledged:0,marked:0},blockedUntilTurn:null}}"
new_make="function makeCard(suit,rank,named,owner,variantId=null){const slot=suit==='J'?'J':suit+rank,id=variantId||(suit==='J'?rank:slot),def=named?NAMED[id]:null,baseRank=suit==='J'?null:rank,topRank=suit==='J'?null:(def?.topRank||baseRank),bottomRank=suit==='J'?null:(def?.bottomRank||baseRank);return{uid:uidSeq++,id,slot,suit,rank,baseRank,topRank,bottomRank,activeRank:null,rankOrientation:null,owner,originOwner:owner,name:def?.n||'순수 카드',effect:def?.d||'효과 없음. 기본 랭크와 무늬만 사용한다.',tag:def?.t||null,themeId:def?.themeId||null,prepRequired:Math.max(0,Number(def?.prepRequired)||0),named:!!def,age:0,handPrep:{turns:0,exitTurns:0,exitTurnToken:null,exitOwner:null},fromDiscard:false,smuggledActive:false,smuggledTurnToken:null,enteredMeldToken:null,suppressEffectToken:null,contractActive:false,healCharge:0,recoveredToken:null,recoverReturnOverrideToken:null,encoreGrantToken:null,encoreReturnUsedToken:null,themeTurnGates:{},fuseArmed:false,flexSuitOffSuit:false,officialStatus:{seal:0,fixed:0,protect:0,fixedOwner:null,fixedThroughStart:null},status:{charged:0,reserved:0,cursed:0,pledged:0,marked:0},blockedUntilTurn:null}}"
if s.count(old_make)!=1:
    raise SystemExit(f'makeCard anchor mismatch: {s.count(old_make)}')
s=s.replace(old_make,new_make,1)

old_enter="function enterHand(w,c){if(!c)return null;resetHandPreparation(c);sideObj(w).hand.push(c);return c}"
new_enter="function enterHand(w,c){if(!c)return null;if(typeof clearCardActiveRank==='function')clearCardActiveRank(c);resetHandPreparation(c);sideObj(w).hand.push(c);return c}"
if s.count(old_enter)!=1:
    raise SystemExit(f'enterHand anchor mismatch: {s.count(old_enter)}')
s=s.replace(old_enter,new_enter,1)

old_discard="function pushDiscard(c){c.fromDiscard=false;c.contractActive=false;state.discard.push(c)}"
new_discard="function pushDiscard(c){if(typeof clearCardActiveRank==='function')clearCardActiveRank(c);c.fromDiscard=false;c.contractActive=false;state.discard.push(c)}"
if s.count(old_discard)!=1:
    raise SystemExit(f'pushDiscard anchor mismatch: {s.count(old_discard)}')
s=s.replace(old_discard,new_discard,1)

old_retire="for(const c of m.cards){if(preserveUids.has(c.uid))"
new_retire="for(const c of m.cards){if(typeof clearCardActiveRank==='function')clearCardActiveRank(c);if(preserveUids.has(c.uid))"
if s.count(old_retire)!=1:
    raise SystemExit(f'retire loop anchor mismatch: {s.count(old_retire)}')
s=s.replace(old_retire,new_retire,1)

old_full="for(const c of all){c.fromDiscard=false;c.contractActive=false;"
new_full="for(const c of all){if(typeof clearCardActiveRank==='function')clearCardActiveRank(c);c.fromDiscard=false;c.contractActive=false;"
if s.count(old_full)!=1:
    raise SystemExit(f'full recirculation anchor mismatch: {s.count(old_full)}')
s=s.replace(old_full,new_full,1)

road_repls={
"- [ ] 기존 단일 `rank`와 호환되는 `baseRank / topRank / bottomRank / activeRank` 데이터 구조 설계":"- [x] 기존 단일 `rank`와 호환되는 `baseRank / topRank / bottomRank / activeRank` 데이터 구조 설계 — 모든 정규 카드는 원본 슬롯용 `baseRank`, 인쇄값 `topRank/bottomRank`, 조합 안 선택값 `activeRank`를 가질 수 있다. 기존 엔진 호환을 위해 `rank`는 조합 밖에서는 `baseRank`, 향후 선택이 확정된 조합 안에서는 `activeRank`를 미러링하는 전환 계층으로 잠금. 현재 라이브 비대칭 정의는 0장",
"- [ ] 손에서는 `activeRank` 미확정, 조합 투입 시 확정, 조합을 떠나 손으로 돌아오면 다시 미확정으로 초기화하는 생명주기 명문화":"- [x] 손에서는 `activeRank` 미확정, 조합 투입 시 확정, 조합을 떠나 손으로 돌아오면 다시 미확정으로 초기화하는 생명주기 명문화 — `chooseCardActiveRank` / `clearCardActiveRank`와 `rankOrientation`으로 top/bottom 방향을 분리하고 `docs/ASYMMETRIC_RANK_PROTOTYPE.md`에 영역별 생명주기를 고정",
"- [ ] 버림패·소모패·덱·재순환처럼 조합 밖 영역에서는 방향 선택 상태를 유지하지 않는 기본안 검증":"- [x] 버림패·소모패·덱·재순환처럼 조합 밖 영역에서는 방향 선택 상태를 유지하지 않는 기본안 검증 — 손 진입, 공용 버림패 진입, 공개 조합 정리, 전체 재순환 경로에서 `activeRank/rankOrientation`을 제거하고 `rank=baseRank`로 복귀. 조합→조합 이동은 공개 조합을 떠나지 않으므로 선택값 유지 후보로 잠금"
}
for old,new in road_repls.items():
    if r.count(old)!=1:
        raise SystemExit(f'ROADMAP anchor mismatch for {old}: {r.count(old)}')
    r=r.replace(old,new,1)

index.write_text(s)
road.write_text(r)
doc.write_text('''# M11B — 비대칭 상·하단 랭크 프로토타입\n\n이 문서는 비대칭 `X/Y` 카드의 **엔진 호환 계층**만 잠근다. 현재 라이브 카드 풀에는 비대칭 카드가 0장이며, 세트/런/버스트/체인/스위치 규칙은 아직 변경하지 않는다.\n\n## 데이터 모델\n\n- `baseRank`: 52슬롯의 원본 랭크. 카드 정체성, 덱빌더 슬롯, 네임드 변형 귀속은 항상 이 값 기준이다.\n- `topRank`: 카드 좌상단에 인쇄될 후보 랭크.\n- `bottomRank`: 카드 우하단에 인쇄될 후보 랭크.\n- `activeRank`: 공개 조합에 투입될 때 선택되는 실제 세트/런 판정값. 조합 밖에서는 `null`.\n- `rankOrientation`: `top` 또는 `bottom`. 같은 숫자가 양쪽에 인쇄된 일반 `X/X` 카드는 방향 의미가 없다.\n- `rank`: 기존 엔진 호환 미러. 조합 밖에서는 `baseRank`, 선택이 확정된 조합 안에서는 `activeRank`와 같게 유지한다.\n\n## 생명주기\n\n| 영역 | activeRank | rank | 비고 |\n| --- | --- | --- | --- |\n| 개인 덱 | `null` | `baseRank` | 방향 없음 |\n| 손패 | `null` | `baseRank` | 사용 직전까지 미확정 |\n| 공용 버림패 | `null` | `baseRank` | 방향 없음 |\n| 개인 소모패 | `null` | `baseRank` | 방향 없음 |\n| 공개 조합 | 선택값 | 선택값 | `top/bottom` 중 실제 인쇄값 하나만 선택 |\n| 조합 → 손/덱/버림/소모 | 즉시 `null` | `baseRank` | 다음 사용 때 다시 선택 가능 |\n| 조합 → 다른 조합 직접 이동 | 유지 후보 | 선택값 | 공개 조합을 떠나지 않으므로 1차 기본안은 유지. 실제 이동 선택 UI 단계에서 재검증 |\n\n## 호환 규칙\n\n1. 일반 카드와 기존 네임드는 기본적으로 `X/X`이며 `topRank=bottomRank=baseRank`다.\n2. 현재 엔진의 수많은 `c.rank` 판정을 즉시 전부 교체하지 않는다. `rank` 미러를 유지해 기존 회귀를 보존한다.\n3. `namedSlot()`과 52슬롯 정체성은 `baseRank+suit`에서 절대 바뀌지 않는다. `activeRank`는 슬롯 교체가 아니다.\n4. 조커는 이 스캐폴드의 랭크 인쇄값을 사용하지 않는다. `baseRank/topRank/bottomRank/activeRank=null`이며 기존 와일드 판정이 우선이다.\n5. 실제 비대칭 카드 정의, 사용값 선택 UI, 세트/런 합법성 탐색은 다음 단계 전까지 라이브에 넣지 않는다.\n\n## 현재 중앙 초기화 경로\n\n- `enterHand()` — 공개 조합에서 회수되거나 다른 효과로 손에 들어오면 선택값 제거.\n- `pushDiscard()` — 공용 버림패 진입 시 선택값 제거.\n- `retireMeld()` — 조합 정리로 손/덱/소모패 어디로 가든 먼저 선택값 제거.\n- `fullRecirculation()` — 모든 영역을 덱으로 되돌리는 긴급 재순환에서 선택값 제거.\n\n다음 구현 단계는 `새 조합 생성 / 단일 붙이기 / 다중 붙이기`에서 비대칭 카드마다 가능한 사용값 조합을 열거하고, 실제 행동을 확정하기 전에 선택값을 고르게 하는 것이다.\n''')
print('M11B asymmetric-rank compatibility scaffold installed')

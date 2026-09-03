from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INDEX = ROOT / 'index.html'
ROAD = ROOT / 'ROADMAP.md'
THEME = ROOT / 'docs' / 'THEME_GROUPS.md'
POOL = ROOT / 'docs' / 'THEME_FULL_POOL_PLAN.md'


def replace_once(text, old, new, label):
    if new in text:
        return text
    if old not in text:
        raise SystemExit(f'missing anchor: {label}')
    return text.replace(old, new, 1)


def insert_before_once(text, anchor, block, marker, label):
    if marker in text:
        return text
    if anchor not in text:
        raise SystemExit(f'missing anchor: {label}')
    return text.replace(anchor, block + anchor, 1)


h = INDEX.read_text(encoding='utf-8')

# Keep partial SCRAP-SHIFT definitions visible only in DEV until the full 24-card release.
old_profile = " 'mail-route':Object.freeze({id:'mail-route',displayName:'MAIL-ROUTE',short:'배송 경로',desc:'일반 카드에도 우편 표식을 붙이고 목적지·도착·반송·재배송으로 공개 조합 사이를 순환합니다.',themeId:'mail-route',live:true})});"
new_profile = " 'mail-route':Object.freeze({id:'mail-route',displayName:'MAIL-ROUTE',short:'배송 경로',desc:'일반 카드에도 우편 표식을 붙이고 목적지·도착·반송·재배송으로 공개 조합 사이를 순환합니다.',themeId:'mail-route',live:true}),\n 'scrap-shift':Object.freeze({id:'scrap-shift',displayName:'SCRAP-SHIFT',short:'부품 순환',desc:'일반 카드에도 부품 표식을 붙여 해체·이식·재조립으로 다시 사용합니다. 24장 전체 완성 전에는 DEV에서만 선택할 수 있습니다.',themeId:'scrap-shift',live:false})});"
h = replace_once(h, old_profile, new_profile, 'SCRAP-SHIFT build profile')

old_tab = '<button class="pixelBtn" data-codex-filter="theme:mail-route">MAIL-ROUTE</button>'
new_tab = old_tab + '<button class="pixelBtn" data-codex-filter="theme:scrap-shift">SCRAP-SHIFT</button>'
h = replace_once(h, old_tab, new_tab, 'SCRAP-SHIFT codex tab')

helpers = r'''function scrapShiftTransplantCandidates(w){const out=[];if(!w||typeof meldsOf!=='function'||typeof other!=='function')return out;for(const sourceSide of[w,other(w)])for(const source of meldsOf(sourceSide)){if(typeof meldFixedActive==='function'&&meldFixedActive(source))continue;for(const card of source.cards||[]){if(card?.owner!==w||!isScrapShiftPart(card,w)||(typeof cardFixedActive==='function'&&cardFixedActive(card)))continue;const remain=source.cards.filter(x=>x.uid!==card.uid);if(remain.length<3||meldType(remain)!==source.type)continue;for(const targetSide of[w,other(w)])for(const target of meldsOf(targetSide)){if(target===source||(typeof meldFixedActive==='function'&&meldFixedActive(target)))continue;if(meldType((target.cards||[]).concat(card))!==target.type)continue;out.push({card,source,target,sourceSide,targetSide})}}}return out}
function requestScrapShiftTransplantChoice(w,sourceCard,onAsyncResolved=null){const list=scrapShiftTransplantCandidates(w);if(!list.length){if(typeof onAsyncResolved==='function')onAsyncResolved(null);return false}const apply=x=>moveCardBetweenMelds(w,x.card,x.source,x.target,{reason:'scrapShiftTransplant'}),interactive=w==='player'&&state.turn==='player'&&typeof requestEffectChoice==='function'&&list.length>1;if(interactive)return requestEffectChoice({title:sourceCard?.name||'컨베이어',text:'이식할 내 부품과 목적 공개 조합을 고르세요. 원본과 목적지는 이동 뒤에도 유효해야 합니다.',options:list.map((x,i)=>({key:`ssmove:${i}`,label:`${cardText(x.card)}${x.card.named?` · ${x.card.name}`:''}`,detail:`${x.source.type==='SET'?'세트':'런'} → ${x.target.type==='SET'?'세트':'런'} · 전투 중립`,entry:x})),onChoose:o=>{const result=o?.entry?apply(o.entry):null;if(typeof onAsyncResolved==='function')onAsyncResolved(result)}});return apply(list[0])&&false}
function scrapShiftReassembleCandidates(w){return sideObj(w).spent.filter(c=>isScrapShiftPart(c,w))}
function requestScrapShiftReassembleChoice(w,sourceCard,opts={}){const list=scrapShiftReassembleCandidates(w);if(!list.length){if(typeof opts.onAsyncResolved==='function')opts.onAsyncResolved(null);return false}const apply=c=>{const result=reassembleScrapShiftPart(w,c,{reason:sourceCard?.tag||'repairKit',label:sourceCard?.name||'SCRAP-SHIFT'});if(result&&opts.shield)addShield(w,opts.shield);return result},interactive=w==='player'&&state.turn==='player'&&typeof requestEffectChoice==='function'&&list.length>1;if(interactive)return requestEffectChoice({title:sourceCard?.name||'수리 키트',text:'재조립할 내 소모패의 부품 1장을 고르세요. 손패로 돌아온 카드는 이번 턴 사용할 수 없습니다.',options:list.map(c=>({key:`ssre:${c.uid}`,label:`${cardText(c)}${c.named?` · ${c.name}`:''}`,detail:'부품 표식 소비 · 이번 턴 사용 불가',card:c})),onChoose:o=>{const result=o?.card?apply(o.card):null;if(typeof opts.onAsyncResolved==='function')opts.onAsyncResolved(result)}});apply(list[0]);return false}
function scrapShiftDismantleCandidates(w,opts={}){const out=[];for(const side of[w,other(w)])for(const meld of meldsOf(side)){if(opts.runOnly&&meld.type!=='RUN')continue;if(opts.minLength&&meld.cards.length<opts.minLength)continue;for(const card of meld.cards||[]){const access=scrapShiftDismantleAccess(w,meld,card);if(access.allowed)out.push({side,meld,card})}}return out}
function requestScrapShiftDismantleChoice(w,sourceCard,opts={}){const list=scrapShiftDismantleCandidates(w,opts);if(!list.length){if(typeof opts.onAsyncResolved==='function')opts.onAsyncResolved(null);return false}const finish=(entry,resumeAfter)=>{const result=dismantleScrapShiftPart(w,entry.meld,entry.card,{reason:sourceCard?.tag||'dismantleDriver',label:sourceCard?.name||'SCRAP-SHIFT'});if(!result){if(resumeAfter&&typeof opts.onAsyncResolved==='function')opts.onAsyncResolved(null);return false}drawOne(w,false);const candidates=sideObj(w).hand.filter(c=>!(typeof scrapShiftCardTurnLocked==='function'&&scrapShiftCardTurnLocked(c)));if(!candidates.length){if(resumeAfter&&typeof opts.onAsyncResolved==='function')opts.onAsyncResolved(result);return false}const bottom=c=>bottomSpecificHandCard(w,c,sourceCard?.name||'분해 드라이버'),interactive=w==='player'&&state.turn==='player'&&typeof requestEffectChoice==='function'&&candidates.length>1;if(interactive){requestEffectChoice({title:sourceCard?.name||'분해 드라이버',text:'해체 성공으로 1장을 뽑았습니다. 덱 아래로 보낼 손패 1장을 고르세요.',options:candidates.map(c=>({key:`ssbottom:${c.uid}`,label:`${cardText(c)}${c.named?` · ${c.name}`:''}`,detail:'덱 아래로 보내기',card:c})),onChoose:o=>{if(o?.card)bottom(o.card);if(typeof opts.onAsyncResolved==='function')opts.onAsyncResolved(result)}});return true}bottom([...candidates].sort((a,b)=>b.age-a.age)[0]);if(resumeAfter&&typeof opts.onAsyncResolved==='function')opts.onAsyncResolved(result);return false},interactive=w==='player'&&state.turn==='player'&&typeof requestEffectChoice==='function'&&list.length>1;if(interactive)return requestEffectChoice({title:sourceCard?.name||'분해 드라이버',text:'4장 이상 RUN에서 해체할 내 부품 1장을 고르세요.',options:list.map((x,i)=>({key:`ssdis:${i}`,label:`${cardText(x.card)}${x.card.named?` · ${x.card.name}`:''}`,detail:`${x.meld.cards.length}장 RUN · 해체 후 체인 -1`,entry:x})),allowSkip:true,skipLabel:'해체하지 않기',onChoose:o=>{if(o?.entry)finish(o.entry,true);else if(typeof opts.onAsyncResolved==='function')opts.onAsyncResolved(null)}});return finish(list[0],false)}
function requestScrapShiftPartLabelChoice(w,sourceCard,meld,actionCards=[],onAsyncResolved=null){const list=(meld?.cards||[]).filter(c=>c?.owner===w&&c.uid!==sourceCard?.uid&&!isScrapShiftPart(c,w));if(!list.length){if(typeof onAsyncResolved==='function')onAsyncResolved(null);return false}const apply=card=>setScrapShiftPart(w,card,{reason:'partLabel',label:sourceCard?.name||'부품 라벨'}),afterAsync=card=>{if(card)apply(card);if(typeof requestZeroSightCycle==='function')return requestZeroSightCycle(w,sourceCard,actionCards,onAsyncResolved);if(typeof onAsyncResolved==='function')onAsyncResolved(card||null);return false},interactive=w==='player'&&state.turn==='player'&&typeof requestEffectChoice==='function'&&list.length>1;if(interactive)return requestEffectChoice({title:sourceCard?.name||'부품 라벨',text:'새 조합의 다른 내 카드 1장을 부품으로 지정하세요. 이어서 남은 손패를 1장 무료 정비합니다.',options:list.map(c=>({key:`sspart:${c.uid}`,label:`${cardText(c)}${c.named?` · ${c.name}`:''}`,detail:'부품 표식 부여',card:c})),onChoose:o=>afterAsync(o?.card||null)});const chosen=list[0];apply(chosen);const cycleList=typeof zeroSightCycleCandidates==='function'?zeroSightCycleCandidates(w,actionCards):[];if(w==='player'&&state.turn==='player'&&cycleList.length>1&&typeof requestZeroSightCycle==='function')return requestZeroSightCycle(w,sourceCard,actionCards,onAsyncResolved);if(typeof requestZeroSightCycle==='function')requestZeroSightCycle(w,sourceCard,actionCards);return false}
'''
h = insert_before_once(h, 'function ensureMailRouteMeta(m)', helpers, 'function scrapShiftTransplantCandidates(w)', 'SCRAP-SHIFT wave1 helpers')

case_anchor = "case'mrFinalNotice':setMailRouteCard(w,c,{reason:'finalNotice',label:c.name});if(isReturning&&state.switchPower>=40&&ctx.meld&&ctx.targetOwner===foe&&isMailRouteDestination(w,ctx.meld))fx.bonus+=14;break;case'vacancyJoker':case'rebelJoker':break"
case_repl = "case'mrFinalNotice':setMailRouteCard(w,c,{reason:'finalNotice',label:c.name});if(isReturning&&state.switchPower>=40&&ctx.meld&&ctx.targetOwner===foe&&isMailRouteDestination(w,ctx.meld))fx.bonus+=14;break;case'ssPartLabel':if(ctx.isNew&&ctx.meld){const paused=requestScrapShiftPartLabelChoice(w,c,ctx.meld,cards,resume);if(paused)return pause()}break;case'ssConveyor':{const paused=requestScrapShiftTransplantChoice(w,c,resume);if(paused)return pause();break}case'ssRepairKit':{const paused=requestScrapShiftReassembleChoice(w,c,{shield:2,onAsyncResolved:resume});if(paused)return pause();break}case'ssDismantleDriver':{const paused=requestScrapShiftDismantleChoice(w,c,{runOnly:true,minLength:4,onAsyncResolved:resume});if(paused)return pause();break}case'vacancyJoker':case'rebelJoker':break"
h = replace_once(h, case_anchor, case_repl, 'resolveEffects SCRAP-SHIFT cases')

card_anchor = ",'MRSK':{slot:'SK',themeId:'mail-route',n:'최종 통지',t:'mrFinalNotice',d:'이 카드를 조합에 사용하면 자신을 우편으로 발송한다. 누적 위력 40 이상에서 상대 목적지에 지정 도착하며 스위치를 반환하면 이번 반환의 누적 위력이 14 증가한다.'}\n\n};"
card_repl = ",'MRSK':{slot:'SK',themeId:'mail-route',n:'최종 통지',t:'mrFinalNotice',d:'이 카드를 조합에 사용하면 자신을 우편으로 발송한다. 누적 위력 40 이상에서 상대 목적지에 지정 도착하며 스위치를 반환하면 이번 반환의 누적 위력이 14 증가한다.'}\n,'SSDA':{slot:'DA',themeId:'scrap-shift',n:'부품 라벨',t:'ssPartLabel',d:'새 3장 조합에 들어가면 그 조합의 다른 내 카드 1장을 부품으로 지정하고 남은 손패 1장을 무료 정비한다.'}\n,'SSC2':{slot:'C2',themeId:'scrap-shift',n:'컨베이어',t:'ssConveyor',d:'내 부품 카드 1장을 원본과 목적지가 모두 유효한 다른 공개 조합으로 이식한다. 이동 자체는 전투 중립이다.'}\n,'SSH4':{slot:'H4',themeId:'scrap-shift',n:'수리 키트',t:'ssRepairKit',d:'내 소모패의 부품 카드 1장을 재조립하고 보호막 8을 얻는다. 재조립한 카드는 이번 턴 사용할 수 없다.'}\n,'SSSA':{slot:'SA',themeId:'scrap-shift',n:'분해 드라이버',t:'ssDismantleDriver',d:'4장 이상 RUN의 내 부품 카드 1장을 해체할 수 있다. 성공하면 카드 1장을 뽑고 손패 1장을 덱 아래로 보낸다.'}\n\n};"
h = replace_once(h, card_anchor, card_repl, 'SCRAP-SHIFT wave1 card definitions')

INDEX.write_text(h, encoding='utf-8')

road = ROAD.read_text(encoding='utf-8')
road_anchor = "- [x] AI 기본 버리기/정비가 재조립 잠금 카드를 자발적으로 소비하지 않도록 공용 잠금 적용\n- [ ] 24장 / 수트별 6장 정의 및 실제 효과 구현"
road_repl = "- [x] AI 기본 버리기/정비가 재조립 잠금 카드를 자발적으로 소비하지 않도록 공용 잠금 적용\n- [x] 1차 수직 슬라이스 4장 — A♦ 부품 라벨 / 2♣ 컨베이어 / 4♥ 수리 키트 / A♠ 분해 드라이버. 부품 지정·이식·재조립·해체를 DEV 전용 카드로 실제 행동 경로에 연결\n- [ ] 24장 / 수트별 6장 정의 및 실제 효과 구현"
road = replace_once(road, road_anchor, road_repl, 'ROADMAP wave1')
ROAD.write_text(road, encoding='utf-8')

theme = THEME.read_text(encoding='utf-8')
theme_anchor = "- [x] 엔진 1차 기반 — `SCRAP-SHIFT` 비라이브 레지스트리, 카드별 부품 표식/수명주기, `onPartSet`/`onDismantle`/`onReassemble`, 해체·재조립 공용 헬퍼, 재조립 동일 턴 잠금, 부품 UI 표시 구현\n- [ ] 24장 전체 정의/효과/해금/도감/덱빌더/체험전 연결 뒤 카드군 라이브 승격"
theme_repl = "- [x] 엔진 1차 기반 — `SCRAP-SHIFT` 비라이브 레지스트리, 카드별 부품 표식/수명주기, `onPartSet`/`onDismantle`/`onReassemble`, 해체·재조립 공용 헬퍼, 재조립 동일 턴 잠금, 부품 UI 표시 구현\n- [x] 1차 수직 슬라이스 — A♦ `부품 라벨` / 2♣ `컨베이어` / 4♥ `수리 키트` / A♠ `분해 드라이버`를 DEV 전용으로 구현해 부품 지정·이식·재조립·해체의 실제 카드 행동을 검증\n- [ ] 24장 전체 정의/효과/해금/도감/덱빌더/체험전 연결 뒤 카드군 라이브 승격"
theme = replace_once(theme, theme_anchor, theme_repl, 'theme doc wave1')
THEME.write_text(theme, encoding='utf-8')

pool = POOL.read_text(encoding='utf-8')
pool = replace_once(pool, '- 현재 상태: **규칙·후보 풀 잠금 + 공용 엔진 1차 기반 구현 중, 24장 미라이브**', '- 현재 상태: **규칙·후보 풀 잠금 + 공용 엔진 1차 기반 구현 중, 24장 미라이브 · 4장 수직 슬라이스 DEV 구현 완료**', 'pool plan wave1')
POOL.write_text(pool, encoding='utf-8')

print('SCRAP-SHIFT wave1 patch applied')

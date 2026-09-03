from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
INDEX=ROOT/'index.html'
ROAD=ROOT/'ROADMAP.md'
THEME=ROOT/'docs'/'THEME_GROUPS.md'
POOL=ROOT/'docs'/'THEME_FULL_POOL_PLAN.md'

def replace_once(text,old,new,label):
    if new in text:return text
    if old not in text:raise SystemExit(f'missing anchor: {label}')
    return text.replace(old,new,1)

def insert_before_once(text,anchor,block,marker,label):
    if marker in text:return text
    if anchor not in text:raise SystemExit(f'missing anchor: {label}')
    return text.replace(anchor,block+anchor,1)

h=INDEX.read_text(encoding='utf-8')

helpers=r'''function scrapShiftMeldHasOwnedPart(w,m){return !!m&&(m.cards||[]).some(c=>isScrapShiftPart(c,w))}
function requestScrapShiftDrawBottom(w,source,onAsyncResolved=null){drawOne(w,false);const candidates=sideObj(w).hand.filter(c=>!(typeof scrapShiftCardTurnLocked==='function'&&scrapShiftCardTurnLocked(c)));if(!candidates.length){if(typeof onAsyncResolved==='function')onAsyncResolved(null);return false}const apply=c=>bottomSpecificHandCard(w,c,source?.name||'표준 규격'),interactive=w==='player'&&state.turn==='player'&&typeof requestEffectChoice==='function'&&candidates.length>1;if(interactive)return requestEffectChoice({title:source?.name||'표준 규격',text:'1장을 뽑았습니다. 덱 아래로 보낼 손패 1장을 고르세요.',options:candidates.map(c=>({key:`ssspec:${c.uid}`,label:`${cardText(c)}${c.named?` · ${c.name}`:''}`,detail:'덱 아래로 보내기',card:c})),onChoose:o=>{if(o?.card)apply(o.card);if(typeof onAsyncResolved==='function')onAsyncResolved(o?.card||null)}});const chosen=[...candidates].sort((a,b)=>(b.age||0)-(a.age||0))[0];apply(chosen);if(typeof onAsyncResolved==='function')onAsyncResolved(chosen);return false}
function scrapShiftProtectCandidates(w,m){if(!m)return[];return(m.cards||[]).filter(c=>c.owner===w)}
function requestScrapShiftProtectChoice(w,source,m,onAsyncResolved=null){const candidates=scrapShiftProtectCandidates(w,m);if(!candidates.length){if(typeof onAsyncResolved==='function')onAsyncResolved(null);return false}const apply=c=>{applyOfficialStatus('card',c,'protect',1,{actor:w,silent:true});if(typeof log==='function')log(`${source?.name||'임시 용접'}: ${cardText(c)}에 보호 1.`,'good');return c},interactive=w==='player'&&state.turn==='player'&&typeof requestEffectChoice==='function'&&candidates.length>1;if(interactive)return requestEffectChoice({title:source?.name||'임시 용접',text:'이 런의 내 카드 1장에 보호 1을 부여하세요.',options:candidates.map(c=>({key:`ssweld:${c.uid}`,label:`${cardText(c)}${c.named?` · ${c.name}`:''}`,detail:'보호 1',card:c})),onChoose:o=>{const result=o?.card?apply(o.card):null;if(typeof onAsyncResolved==='function')onAsyncResolved(result)}});const chosen=candidates[0];apply(chosen);if(typeof onAsyncResolved==='function')onAsyncResolved(chosen);return false}
function scrapShiftRecoverCandidates(w){const out=[];for(const side of[w,other(w)])for(const m of meldsOf(side))for(const c of freeRecoverCandidates(w,m,[]))if(isScrapShiftPart(c,w))out.push({side,m,card:c});return out}
function requestScrapShiftRecoverChoice(w,source,onAsyncResolved=null){const candidates=scrapShiftRecoverCandidates(w);if(!candidates.length){if(typeof onAsyncResolved==='function')onAsyncResolved(null);return false}const apply=x=>recoverSpecificFromMeld(w,x.m,x.card,{label:`${source?.name||'자석 회수기'} 무료 회수`}),interactive=w==='player'&&state.turn==='player'&&typeof requestEffectChoice==='function'&&candidates.length>1;if(interactive)return requestEffectChoice({title:source?.name||'자석 회수기',text:'공개 조합에서 무료 회수할 내 부품 1장을 고르세요. 일반 회수의 동일 턴 반환 제한은 유지됩니다.',options:candidates.map((x,i)=>({key:`ssmag:${x.card.uid}:${i}`,label:`${cardText(x.card)}${x.card.named?` · ${x.card.name}`:''}`,detail:`${x.side===w?'내':'상대'} ${x.m.type==='SET'?'세트':'런'}에서 무료 회수`,entry:x})),onChoose:o=>{const result=o?.entry?apply(o.entry):null;if(typeof onAsyncResolved==='function')onAsyncResolved(result)}});const chosen=candidates[0];const result=apply(chosen);if(typeof onAsyncResolved==='function')onAsyncResolved(result);return false}
function applyScrapShiftOverheat(w,m,source=null){if(!scrapShiftMeldHasOwnedPart(w,m))return false;applyOfficialStatus('player',sideObj(other(w)),'vulnerable',1,{actor:w});if(typeof log==='function')log(`${source?.name||'과열 부품'}: 부품 포함 반환 · 상대 취약 1.`,'important');return true}
'''
h=insert_before_once(h,'function ensureMailRouteMeta(m)',helpers,'function scrapShiftMeldHasOwnedPart(w,m)','SCRAP-SHIFT wave3 helpers')

old_cases="case'ssPartLabel':if(ctx.isNew&&ctx.meld){const paused=requestScrapShiftPartLabelChoice(w,c,ctx.meld,cards,resume);if(paused)return pause()}break;case'ssSortingBench':break;case'ssConveyor':{const paused=requestScrapShiftTransplantChoice(w,c,resume);if(paused)return pause();break}case'ssCompatPort':break;case'ssRepairKit':{const paused=requestScrapShiftReassembleChoice(w,c,{shield:2,onAsyncResolved:resume});if(paused)return pause();break}case'ssRegenWorkshop':break;case'ssDismantleDriver':{const paused=requestScrapShiftDismantleChoice(w,c,{runOnly:true,minLength:4,onAsyncResolved:resume});if(paused)return pause();break}case'ssDisposalOrder':break;case'vacancyJoker':case'rebelJoker':break"
new_cases="case'ssPartLabel':if(ctx.isNew&&ctx.meld){const paused=requestScrapShiftPartLabelChoice(w,c,ctx.meld,cards,resume);if(paused)return pause()}break;case'ssSortingBench':break;case'ssStandardSpec':if(type==='SET'&&ctx.meld&&isScrapShiftPart(c,w)){const paused=requestScrapShiftDrawBottom(w,c,resume);if(paused)return pause()}break;case'ssConveyor':{const paused=requestScrapShiftTransplantChoice(w,c,resume);if(paused)return pause();break}case'ssTempWeld':if(ctx.isAttach&&type==='RUN'&&ctx.meld&&scrapShiftMeldHasOwnedPart(w,ctx.meld)){const paused=requestScrapShiftProtectChoice(w,c,ctx.meld,resume);if(paused)return pause()}break;case'ssCompatPort':break;case'ssMagnetRetriever':{const paused=requestScrapShiftRecoverChoice(w,c,resume);if(paused)return pause();break}case'ssRepairKit':{const paused=requestScrapShiftReassembleChoice(w,c,{shield:2,onAsyncResolved:resume});if(paused)return pause();break}case'ssRegenWorkshop':break;case'ssDismantleDriver':{const paused=requestScrapShiftDismantleChoice(w,c,{runOnly:true,minLength:4,onAsyncResolved:resume});if(paused)return pause();break}case'ssDisposalOrder':break;case'ssOverheatedPart':if(isReturning&&ctx.meld)applyScrapShiftOverheat(w,ctx.meld,c);break;case'vacancyJoker':case'rebelJoker':break"
h=replace_once(h,old_cases,new_cases,'SCRAP-SHIFT wave3 resolver cases')

old_cards=",'SSS5':{slot:'S5',themeId:'scrap-shift',n:'폐기 명령',t:'ssDisposalOrder',d:'이번 턴 처음 내 부품을 해체한 뒤 상대 공개 조합 하나에 봉인 1을 부여한다.'}\n\n};"
new_cards=",'SSS5':{slot:'S5',themeId:'scrap-shift',n:'폐기 명령',t:'ssDisposalOrder',d:'이번 턴 처음 내 부품을 해체한 뒤 상대 공개 조합 하나에 봉인 1을 부여한다.'}\n,'SSD5':{slot:'D5',themeId:'scrap-shift',n:'표준 규격',t:'ssStandardSpec',d:'이 카드가 부품인 상태로 세트에 들어가면 카드 1장을 뽑고 손패 1장을 덱 아래로 보낸다.'}\n,'SSC4':{slot:'C4',themeId:'scrap-shift',n:'임시 용접',t:'ssTempWeld',d:'내 부품이 있는 런에 붙이면 그 런의 내 카드 1장에 보호 1을 부여한다.'}\n,'SSH2':{slot:'H2',themeId:'scrap-shift',n:'자석 회수기',t:'ssMagnetRetriever',d:'공개 조합에서 내 부품 카드 1장을 무료 회수한다. 일반 회수의 동일 턴 반환 제한은 유지된다.'}\n,'SSS10':{slot:'S10',themeId:'scrap-shift',n:'과열 부품',t:'ssOverheatedPart',d:'내 부품이 있는 조합으로 스위치를 반환하면 상대에게 취약 1을 부여한다.'}\n\n};"
h=replace_once(h,old_cards,new_cards,'SCRAP-SHIFT wave3 card definitions')
INDEX.write_text(h,encoding='utf-8')

road=ROAD.read_text(encoding='utf-8')
road_anchor='- [x] 무료 패순환으로 개인 덱에 들어가는 부품도 표식을 해제하도록 수명주기 누락 경로 보정\n- [ ] 24장 / 수트별 6장 정의 및 실제 효과 구현\n- [ ] 이식 카드군 효과를 기존 `onMeldMove` 공용 이동과 연결'
road_repl='- [x] 무료 패순환으로 개인 덱에 들어가는 부품도 표식을 해제하도록 수명주기 누락 경로 보정\n- [x] 3차 유틸리티 슬라이스 4장 — 5♦ 표준 규격 / 4♣ 임시 용접 / 2♥ 자석 회수기 / 10♠ 과열 부품. 부품 상태의 세트 진입·런 보호·무료 회수·반환 취약을 실제 행동 경로에 연결\n- [ ] 24장 / 수트별 6장 정의 및 실제 효과 구현\n- [x] 이식 카드군 효과를 기존 `onMeldMove` 공용 이동과 연결'
road=replace_once(road,road_anchor,road_repl,'ROADMAP wave3')
ROAD.write_text(road,encoding='utf-8')

theme=THEME.read_text(encoding='utf-8')
theme_anchor='- [x] 패순환 개인 덱 진입 시 부품 표식 해제 누락 경로 보정\n- [ ] 24장 전체 정의/효과/해금/도감/덱빌더/체험전 연결 뒤 카드군 라이브 승격'
theme_repl='- [x] 패순환 개인 덱 진입 시 부품 표식 해제 누락 경로 보정\n- [x] 3차 유틸리티 슬라이스 — 5♦ `표준 규격` / 4♣ `임시 용접` / 2♥ `자석 회수기` / 10♠ `과열 부품`을 DEV 전용 구현. 부품 세트 진입·런 보호·무료 회수·반환 취약의 기본 전투 루프 검증\n- [ ] 24장 전체 정의/효과/해금/도감/덱빌더/체험전 연결 뒤 카드군 라이브 승격'
theme=replace_once(theme,theme_anchor,theme_repl,'theme doc wave3')
THEME.write_text(theme,encoding='utf-8')

pool=POOL.read_text(encoding='utf-8')
pool=replace_once(pool,'24장 미라이브 · 8장 DEV 구현 완료(행동 4 + 반응 4)','24장 미라이브 · 12장 DEV 구현 완료(행동 4 + 반응 4 + 유틸리티 4)','pool plan wave3')
POOL.write_text(pool,encoding='utf-8')
print('SCRAP-SHIFT wave3 patch applied')

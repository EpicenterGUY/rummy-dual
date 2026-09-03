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

# Deck entry through free cycle must obey the same part lifecycle as maintenance/bottoming.
old_cycle="chosen.fromDiscard=false;chosen.contractActive=false;chosen.age=0;if(typeof clearMailRouteCard==='function')clearMailRouteCard(chosen,'패순환',true);side.deck.unshift(chosen);"
new_cycle="chosen.fromDiscard=false;chosen.contractActive=false;chosen.age=0;if(typeof clearMailRouteCard==='function')clearMailRouteCard(chosen,'패순환',true);if(typeof clearScrapShiftPart==='function')clearScrapShiftPart(chosen,'패순환·개인 덱',true);side.deck.unshift(chosen);"
h=replace_once(h,old_cycle,new_cycle,'free-cycle part lifecycle')

helpers=r'''function scrapShiftPublicCards(actor,tag=null){const out=[];if(!actor||typeof meldsOf!=='function'||typeof other!=='function')return out;for(const side of[actor,other(actor)])for(const m of meldsOf(side))for(const c of m.cards||[])if(c?.owner===actor&&c.themeId==='scrap-shift'&&(!tag||c.tag===tag))out.push(c);return out}
function scrapShiftPassiveCycle(w,source){const candidates=(typeof zeroSightCycleCandidates==='function'?zeroSightCycleCandidates(w,[]):sideObj(w).hand||[]).filter(c=>!(typeof scrapShiftCardTurnLocked==='function'&&scrapShiftCardTurnLocked(c)));if(!candidates.length)return false;const chosen=[...candidates].sort((a,b)=>(b.age||0)-(a.age||0))[0];return !!(typeof cycleSpecificHandCard==='function'&&cycleSpecificHandCard(w,chosen,source?.name||'호환 포트'))}
function scrapShiftSealTarget(w,packet,source){const foe=other(w),foeMelds=meldsOf(foe);if(!foeMelds.length)return null;let target=packet?.sourceSide===foe&&packet?.meld&&foeMelds.includes(packet.meld)?packet.meld:null;if(!target)target=[...foeMelds].sort((a,b)=>(b.cards?.length||0)-(a.cards?.length||0)||((b.chain||0)-(a.chain||0)))[0]||null;if(!target)return null;applyOfficialStatus('meld',target,'seal',1,{actor:w,silent:true});if(typeof log==='function')log(`${source?.name||'폐기 명령'}: 상대 ${target.type==='SET'?'세트':'런'}에 봉인 1.`,'important');return target}
function handleScrapShiftThemeEvent(packet){if(!packet?.event||typeof sideObj!=='function'||typeof other!=='function')return false;let changed=false;if(packet.event==='onPartSet'){const w=packet.owner||packet.actor,bench=scrapShiftPublicCards(w,'ssSortingBench').find(c=>!themeTurnGateUsed(c,'ssSortingBench',packet.turnToken));if(bench&&claimThemeTurnGate(bench,'ssSortingBench',packet.turnToken)){addShield(w,2);changed=true}}
 if(packet.event==='onMeldMove'&&packet.reason==='scrapShiftTransplant'&&isScrapShiftPart(packet.card,packet.actor)){const w=packet.actor,port=scrapShiftPublicCards(w,'ssCompatPort').find(c=>!themeTurnGateUsed(c,'ssCompatPort',packet.turnToken));if(port&&claimThemeTurnGate(port,'ssCompatPort',packet.turnToken)){scrapShiftPassiveCycle(w,port);changed=true}}
 if(packet.event==='onReassemble'){const w=packet.owner||packet.actor,shop=scrapShiftPublicCards(w,'ssRegenWorkshop').find(c=>!themeTurnGateUsed(c,'ssRegenWorkshop',packet.turnToken));if(shop&&claimThemeTurnGate(shop,'ssRegenWorkshop',packet.turnToken)){heal(w,2);changed=true}}
 if(packet.event==='onDismantle'){const w=packet.owner||packet.actor,order=scrapShiftPublicCards(w,'ssDisposalOrder').find(c=>!themeTurnGateUsed(c,'ssDisposalOrder',packet.turnToken));if(order&&claimThemeTurnGate(order,'ssDisposalOrder',packet.turnToken)){scrapShiftSealTarget(w,packet,order);changed=true}}
 return changed}
subscribeEffectEvent(handleScrapShiftThemeEvent);
'''
h=insert_before_once(h,'function ensureMailRouteMeta(m)',helpers,'function handleScrapShiftThemeEvent(packet)','SCRAP-SHIFT wave2 passive handler')

old_cases="case'ssPartLabel':if(ctx.isNew&&ctx.meld){const paused=requestScrapShiftPartLabelChoice(w,c,ctx.meld,cards,resume);if(paused)return pause()}break;case'ssConveyor':{const paused=requestScrapShiftTransplantChoice(w,c,resume);if(paused)return pause();break}case'ssRepairKit':{const paused=requestScrapShiftReassembleChoice(w,c,{shield:2,onAsyncResolved:resume});if(paused)return pause();break}case'ssDismantleDriver':{const paused=requestScrapShiftDismantleChoice(w,c,{runOnly:true,minLength:4,onAsyncResolved:resume});if(paused)return pause();break}case'vacancyJoker':case'rebelJoker':break"
new_cases="case'ssPartLabel':if(ctx.isNew&&ctx.meld){const paused=requestScrapShiftPartLabelChoice(w,c,ctx.meld,cards,resume);if(paused)return pause()}break;case'ssSortingBench':break;case'ssConveyor':{const paused=requestScrapShiftTransplantChoice(w,c,resume);if(paused)return pause();break}case'ssCompatPort':break;case'ssRepairKit':{const paused=requestScrapShiftReassembleChoice(w,c,{shield:2,onAsyncResolved:resume});if(paused)return pause();break}case'ssRegenWorkshop':break;case'ssDismantleDriver':{const paused=requestScrapShiftDismantleChoice(w,c,{runOnly:true,minLength:4,onAsyncResolved:resume});if(paused)return pause();break}case'ssDisposalOrder':break;case'vacancyJoker':case'rebelJoker':break"
h=replace_once(h,old_cases,new_cases,'SCRAP-SHIFT wave2 resolver cases')

old_cards=",'SSSA':{slot:'SA',themeId:'scrap-shift',n:'분해 드라이버',t:'ssDismantleDriver',d:'4장 이상 런의 내 부품 카드 1장을 해체할 수 있다. 성공하면 카드 1장을 뽑고 손패 1장을 덱 아래로 보낸다.'}\n\n};"
new_cards=",'SSSA':{slot:'SA',themeId:'scrap-shift',n:'분해 드라이버',t:'ssDismantleDriver',d:'4장 이상 런의 내 부품 카드 1장을 해체할 수 있다. 성공하면 카드 1장을 뽑고 손패 1장을 덱 아래로 보낸다.'}\n,'SSD3':{slot:'D3',themeId:'scrap-shift',n:'분류대',t:'ssSortingBench',d:'이번 턴 처음 내 카드가 부품이 되면 보호막 8을 얻는다.'}\n,'SSC6':{slot:'C6',themeId:'scrap-shift',n:'호환 포트',t:'ssCompatPort',d:'이번 턴 처음 내 부품 이식에 성공하면 남은 손패 1장을 무료 정비한다.'}\n,'SSH6':{slot:'H6',themeId:'scrap-shift',n:'재생 공방',t:'ssRegenWorkshop',d:'이번 턴 처음 재조립하면 현재 코어를 8 회복한다.'}\n,'SSS5':{slot:'S5',themeId:'scrap-shift',n:'폐기 명령',t:'ssDisposalOrder',d:'이번 턴 처음 내 부품을 해체한 뒤 상대 공개 조합 하나에 봉인 1을 부여한다.'}\n\n};"
h=replace_once(h,old_cards,new_cards,'SCRAP-SHIFT wave2 card definitions')
INDEX.write_text(h,encoding='utf-8')

road=ROAD.read_text(encoding='utf-8')
road_anchor='- [x] 1차 수직 슬라이스 4장 — A♦ 부품 라벨 / 2♣ 컨베이어 / 4♥ 수리 키트 / A♠ 분해 드라이버. 부품 지정·이식·재조립·해체를 DEV 전용 카드로 실제 행동 경로에 연결\n- [ ] 24장 / 수트별 6장 정의 및 실제 효과 구현'
road_repl='- [x] 1차 수직 슬라이스 4장 — A♦ 부품 라벨 / 2♣ 컨베이어 / 4♥ 수리 키트 / A♠ 분해 드라이버. 부품 지정·이식·재조립·해체를 DEV 전용 카드로 실제 행동 경로에 연결\n- [x] 2차 반응 슬라이스 4장 — 3♦ 분류대 / 6♣ 호환 포트 / 6♥ 재생 공방 / 5♠ 폐기 명령. `onPartSet`·`onMeldMove`·`onReassemble`·`onDismantle` 수동 반응과 턴당 1회 게이트 연결\n- [x] 무료 패순환으로 개인 덱에 들어가는 부품도 표식을 해제하도록 수명주기 누락 경로 보정\n- [ ] 24장 / 수트별 6장 정의 및 실제 효과 구현'
road=replace_once(road,road_anchor,road_repl,'ROADMAP wave2')
ROAD.write_text(road,encoding='utf-8')

theme=THEME.read_text(encoding='utf-8')
theme_anchor='- [x] 1차 수직 슬라이스 — A♦ `부품 라벨` / 2♣ `컨베이어` / 4♥ `수리 키트` / A♠ `분해 드라이버`를 DEV 전용으로 구현해 부품 지정·이식·재조립·해체의 실제 카드 행동을 검증\n- [ ] 24장 전체 정의/효과/해금/도감/덱빌더/체험전 연결 뒤 카드군 라이브 승격'
theme_repl='- [x] 1차 수직 슬라이스 — A♦ `부품 라벨` / 2♣ `컨베이어` / 4♥ `수리 키트` / A♠ `분해 드라이버`를 DEV 전용으로 구현해 부품 지정·이식·재조립·해체의 실제 카드 행동을 검증\n- [x] 2차 반응 슬라이스 — 3♦ `분류대` / 6♣ `호환 포트` / 6♥ `재생 공방` / 5♠ `폐기 명령`을 공용 파생 이벤트에 연결하고 카드별 턴당 1회 게이트로 잠금\n- [x] 패순환 개인 덱 진입 시 부품 표식 해제 누락 경로 보정\n- [ ] 24장 전체 정의/효과/해금/도감/덱빌더/체험전 연결 뒤 카드군 라이브 승격'
theme=replace_once(theme,theme_anchor,theme_repl,'theme doc wave2')
THEME.write_text(theme,encoding='utf-8')

pool=POOL.read_text(encoding='utf-8')
pool=replace_once(pool,'24장 미라이브 · 4장 수직 슬라이스 DEV 구현 완료','24장 미라이브 · 8장 DEV 구현 완료(행동 4 + 반응 4)','pool plan wave2')
POOL.write_text(pool,encoding='utf-8')
print('SCRAP-SHIFT wave2 patch applied')

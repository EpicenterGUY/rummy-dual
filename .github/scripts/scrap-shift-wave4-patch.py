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

# Delayed chassis bookkeeping belongs to the physical card and is cleared with the part marker.
h=replace_once(h,
    'scrapShiftPart:false,scrapShiftPartSetToken:null,scrapShiftReassembledToken:null,zsCounterTraceCharged:false',
    'scrapShiftPart:false,scrapShiftPartSetToken:null,scrapShiftReassembledToken:null,scrapShiftOpponentSpentStart:null,zsCounterTraceCharged:false',
    'SCRAP-SHIFT opponent-spent card state')
h=replace_once(h,
    "function clearScrapShiftPart(c,reason='zoneExit',silent=false){if(!c)return false;const had=!!c.scrapShiftPart;c.scrapShiftPart=false;c.scrapShiftPartSetToken=null;c.scrapShiftReassembledToken=null;if(had&&!silent&&typeof log==='function')log(`${c.name||cardText(c)}: 부품 표식 해제 · ${reason}.`,'important');return had}",
    "function clearScrapShiftPart(c,reason='zoneExit',silent=false){if(!c)return false;const had=!!c.scrapShiftPart;c.scrapShiftPart=false;c.scrapShiftPartSetToken=null;c.scrapShiftReassembledToken=null;c.scrapShiftOpponentSpentStart=null;if(had&&!silent&&typeof log==='function')log(`${c.name||cardText(c)}: 부품 표식 해제 · ${reason}.`,'important');return had}",
    'SCRAP-SHIFT pending chassis clear')

helpers=r'''function scrapShiftHandPartCandidates(w,exclude=[]){const ex=new Set((exclude||[]).map(c=>c.uid));return(sideObj(w).hand||[]).filter(c=>c?.owner===w&&!ex.has(c.uid)&&!isScrapShiftPart(c,w)&&!(typeof scrapShiftCardTurnLocked==='function'&&scrapShiftCardTurnLocked(c)))}
function requestScrapShiftHandPartChoice(w,source,opts={}){const candidates=scrapShiftHandPartCandidates(w,opts.exclude||[]);if(!candidates.length){if(typeof opts.onAsyncResolved==='function')opts.onAsyncResolved(null);return false}const apply=c=>{if(!c||!setScrapShiftPart(w,c,{reason:opts.reason||source?.tag||'scrapShiftHandPart',label:source?.name||'SCRAP-SHIFT'}))return null;if(opts.shield)addShield(w,opts.shield);return c},interactive=w==='player'&&state.turn==='player'&&typeof requestEffectChoice==='function';if(interactive)return requestEffectChoice({title:source?.name||'부품 지정',text:opts.text||'손패의 내 카드 1장을 부품으로 지정할 수 있습니다.',options:candidates.map(c=>({key:`sshandpart:${c.uid}`,label:`${cardText(c)}${c.named?` · ${c.name}`:''}`,detail:opts.shield?'부품 지정 · 보호막 8':'부품 지정',card:c})),allowSkip:opts.allowSkip!==false,skipLabel:'지정하지 않기',onChoose:o=>{const result=o?.card?apply(o.card):null;if(typeof opts.onAsyncResolved==='function')opts.onAsyncResolved(result)}});const chosen=[...candidates].sort((a,b)=>(b.age||0)-(a.age||0))[0];const result=apply(chosen);if(typeof opts.onAsyncResolved==='function')opts.onAsyncResolved(result);return false}
function scrapShiftPassiveDrawBottom(w,source){if(typeof requestScrapShiftDrawBottom!=='function')return false;requestScrapShiftDrawBottom(w,source);return true}
function noteScrapShiftPartSpent(owner,c,actor=null,reason='spent'){if(!owner||!c||!isScrapShiftPart(c,owner))return false;if(actor&&actor!==owner)c.scrapShiftOpponentSpentStart=(sideObj(owner).turnStarts||0)+1;const shredder=scrapShiftPublicCards(owner,'ssShredder').find(x=>!themeTurnGateUsed(x,'ssShredder',state.turnToken)),candidates=scrapShiftHandPartCandidates(owner,[c]);if(shredder&&candidates.length&&claimThemeTurnGate(shredder,'ssShredder',state.turnToken)){requestScrapShiftHandPartChoice(owner,shredder,{exclude:[c],reason:'shredder',allowSkip:true,text:'부품이 소모패에 들어갔습니다. 손패의 다른 내 카드 1장을 새 부품으로 지정할 수 있습니다.'});if(typeof log==='function')log(`${shredder.name}: 부품 소모 감지 · 대체 부품 지정 기회.`,'important')}return true}
function resolveScrapShiftTurnStart(w){const s=sideObj(w),pending=(s.spent||[]).filter(c=>isScrapShiftPart(c,w)&&c.scrapShiftOpponentSpentStart!=null&&c.scrapShiftOpponentSpentStart<=s.turnStarts);if(!pending.length)return false;const chassis=scrapShiftPublicCards(w,'ssSpareChassis').find(c=>!themeTurnGateUsed(c,'ssSpareChassis',state.turnToken));let changed=false;if(chassis&&claimThemeTurnGate(chassis,'ssSpareChassis',state.turnToken)){addShield(w,3);changed=true;if(typeof log==='function')log(`${chassis.name}: 상대 효과로 소모된 부품 확인 · 보호막 12.`,'good')}for(const c of pending)c.scrapShiftOpponentSpentStart=null;return changed}
'''
h=insert_before_once(h,'function ensureMailRouteMeta(m)',helpers,'function scrapShiftHandPartCandidates(w,exclude=[])','SCRAP-SHIFT wave4 helpers')

# 과열 부품은 후보 문구대로 같은 턴 중복 취약을 막는다.
h=replace_once(h,
    "function applyScrapShiftOverheat(w,m,source=null){if(!scrapShiftMeldHasOwnedPart(w,m))return false;applyOfficialStatus('player',sideObj(other(w)),'vulnerable',1,{actor:w});if(typeof log==='function')log(`${source?.name||'과열 부품'}: 부품 포함 반환 · 상대 취약 1.`,'important');return true}",
    "function applyScrapShiftOverheat(w,m,source=null){if(!scrapShiftMeldHasOwnedPart(w,m))return false;const token=typeof state!=='undefined'?state.turnToken:null;if(source&&token!=null&&typeof themeTurnGateUsed==='function'&&themeTurnGateUsed(source,'ssOverheatedPart',token))return false;if(source&&token!=null&&typeof claimThemeTurnGate==='function'&&!claimThemeTurnGate(source,'ssOverheatedPart',token))return false;applyOfficialStatus('player',sideObj(other(w)),'vulnerable',1,{actor:w});if(typeof log==='function')log(`${source?.name||'과열 부품'}: 부품 포함 반환 · 상대 취약 1.`,'important');return true}",
    'overheated part once-per-turn gate')

# Public transplant reaction: SET↔RUN change gets draw-then-bottom through the existing movement event.
old_move=" if(packet.event==='onMeldMove'&&packet.reason==='scrapShiftTransplant'&&isScrapShiftPart(packet.card,packet.actor)){const w=packet.actor,port=scrapShiftPublicCards(w,'ssCompatPort').find(c=>!themeTurnGateUsed(c,'ssCompatPort',packet.turnToken));if(port&&claimThemeTurnGate(port,'ssCompatPort',packet.turnToken)){scrapShiftPassiveCycle(w,port);changed=true}}"
new_move=" if(packet.event==='onMeldMove'&&packet.reason==='scrapShiftTransplant'&&isScrapShiftPart(packet.card,packet.actor)){const w=packet.actor,port=scrapShiftPublicCards(w,'ssCompatPort').find(c=>!themeTurnGateUsed(c,'ssCompatPort',packet.turnToken));if(port&&claimThemeTurnGate(port,'ssCompatPort',packet.turnToken)){scrapShiftPassiveCycle(w,port);changed=true}const rail=packet.sourceMeld?.type&&packet.targetMeld?.type&&packet.sourceMeld.type!==packet.targetMeld.type?scrapShiftPublicCards(w,'ssBranchRail')[0]:null;if(rail&&scrapShiftPassiveDrawBottom(w,rail))changed=true}"
h=replace_once(h,old_move,new_move,'SCRAP-SHIFT branch rail event')

# Register every currently relevant part -> spent route with the common lifecycle hook.
h=replace_once(h,
    'sideObj(owner).spent.push(c);if(typeof markSetCompletion===\'function\')markSetCompletion(m,access.sourceSide);',
    "sideObj(owner).spent.push(c);if(typeof noteScrapShiftPartSpent==='function')noteScrapShiftPartSpent(owner,c,owner,opts.reason||'dismantle');if(typeof markSetCompletion==='function')markSetCompletion(m,access.sourceSide);",
    'dismantle spent lifecycle')
h=replace_once(h,
    "side.spent.push(c);c.fromDiscard=false;c.contractActive=false;c.age=0;drawMany(w,2,false);",
    "side.spent.push(c);if(typeof noteScrapShiftPartSpent==='function')noteScrapShiftPartSpent(c.owner,c,w,'sidearmConvert');c.fromDiscard=false;c.contractActive=false;c.age=0;drawMany(w,2,false);",
    'sidearm spent lifecycle')
h=replace_once(h,
    "sideObj(c.owner).spent.push(c);markSetCompletion(m,meldOwnerSide(m));",
    "sideObj(c.owner).spent.push(c);if(typeof noteScrapShiftPartSpent==='function')noteScrapShiftPartSpent(c.owner,c,w,'pointBlankSpend');markSetCompletion(m,meldOwnerSide(m));",
    'point blank spend lifecycle')
h=replace_once(h,
    "sideObj(ins.owner).spent.push(ins);log(`${ins.name}: 조합 간섭을 대신 받아 소모됨${m.type==='RUN'?' · 체인 -1':''}.`,'good');",
    "sideObj(ins.owner).spent.push(ins);if(typeof noteScrapShiftPartSpent==='function')noteScrapShiftPartSpent(ins.owner,ins,actor,'insurance');log(`${ins.name}: 조합 간섭을 대신 받아 소모됨${m.type==='RUN'?' · 체인 -1':''}.`,'good');",
    'insurance spent lifecycle')
h=replace_once(h,
    "sideObj(cand.owner).spent.push(cand);markSetCompletion(m,targetSide);log(`절단선: 상대 런의 ${cardText(cand)} 소모 · 체인 -1.`,'important');",
    "sideObj(cand.owner).spent.push(cand);if(typeof noteScrapShiftPartSpent==='function')noteScrapShiftPartSpent(cand.owner,cand,w,'cutLine');markSetCompletion(m,targetSide);log(`절단선: 상대 런의 ${cardText(cand)} 소모 · 체인 -1.`,'important');",
    'hostile cut spent lifecycle')
h=replace_once(h,
    "sideObj(c.owner).spent.push(c)}}log(`${owner==='player'?'내':'상대'} ${m.type} 정리 · ${reason}.`,'important')",
    "sideObj(c.owner).spent.push(c);if(typeof noteScrapShiftPartSpent==='function')noteScrapShiftPartSpent(c.owner,c,null,'meldRetire')}}log(`${owner==='player'?'내':'상대'} ${m.type} 정리 · ${reason}.`,'important')",
    'meld retirement spent lifecycle')

# Next-own-turn delayed reward resolves after the normal shield reset/status start processing.
h=replace_once(h,
    "if(officialStatusValue('player',s,'regen')>0){const r=officialStatusValue('player',s,'regen');heal(w,r);consumeOfficialStatus('player',s,'regen')}}",
    "if(officialStatusValue('player',s,'regen')>0){const r=officialStatusValue('player',s,'regen');heal(w,r);consumeOfficialStatus('player',s,'regen')}if(typeof resolveScrapShiftTurnStart==='function')resolveScrapShiftTurnStart(w)}",
    'spare chassis turn start')

old_cases="case'ssPartLabel':if(ctx.isNew&&ctx.meld){const paused=requestScrapShiftPartLabelChoice(w,c,ctx.meld,cards,resume);if(paused)return pause()}break;case'ssSortingBench':break;case'ssStandardSpec':if(type==='SET'&&ctx.meld&&isScrapShiftPart(c,w)){const paused=requestScrapShiftDrawBottom(w,c,resume);if(paused)return pause()}break;case'ssConveyor':{const paused=requestScrapShiftTransplantChoice(w,c,resume);if(paused)return pause();break}case'ssTempWeld':if(ctx.isAttach&&type==='RUN'&&ctx.meld&&scrapShiftMeldHasOwnedPart(w,ctx.meld)){const paused=requestScrapShiftProtectChoice(w,c,ctx.meld,resume);if(paused)return pause()}break;case'ssCompatPort':break;case'ssMagnetRetriever':{const paused=requestScrapShiftRecoverChoice(w,c,resume);if(paused)return pause();break}case'ssRepairKit':{const paused=requestScrapShiftReassembleChoice(w,c,{shield:2,onAsyncResolved:resume});if(paused)return pause();break}case'ssRegenWorkshop':break;case'ssDismantleDriver':{const paused=requestScrapShiftDismantleChoice(w,c,{runOnly:true,minLength:4,onAsyncResolved:resume});if(paused)return pause();break}case'ssDisposalOrder':break;case'ssOverheatedPart':if(isReturning&&ctx.meld)applyScrapShiftOverheat(w,ctx.meld,c);break;case'vacancyJoker':case'rebelJoker':break"
new_cases="case'ssPartLabel':if(ctx.isNew&&ctx.meld){const paused=requestScrapShiftPartLabelChoice(w,c,ctx.meld,cards,resume);if(paused)return pause()}break;case'ssSortingBench':break;case'ssStandardSpec':if(type==='SET'&&ctx.meld&&isScrapShiftPart(c,w)){const paused=requestScrapShiftDrawBottom(w,c,resume);if(paused)return pause()}break;case'ssSpareScrew':if(c.fromDiscard){const paused=requestScrapShiftHandPartChoice(w,c,{exclude:cards,reason:'spareScrew',shield:2,allowSkip:true,text:'버림패에서 가져온 예비 나사를 사용했습니다. 남은 손패의 내 카드 1장을 부품으로 지정할 수 있습니다.',onAsyncResolved:resume});if(paused)return pause()}break;case'ssConveyor':{const paused=requestScrapShiftTransplantChoice(w,c,resume);if(paused)return pause();break}case'ssTempWeld':if(ctx.isAttach&&type==='RUN'&&ctx.meld&&scrapShiftMeldHasOwnedPart(w,ctx.meld)){const paused=requestScrapShiftProtectChoice(w,c,ctx.meld,resume);if(paused)return pause()}break;case'ssCompatPort':case'ssBranchRail':break;case'ssMagnetRetriever':{const paused=requestScrapShiftRecoverChoice(w,c,resume);if(paused)return pause();break}case'ssRepairKit':{const paused=requestScrapShiftReassembleChoice(w,c,{shield:2,onAsyncResolved:resume});if(paused)return pause();break}case'ssRegenWorkshop':case'ssSpareChassis':break;case'ssDismantleDriver':{const paused=requestScrapShiftDismantleChoice(w,c,{runOnly:true,minLength:4,onAsyncResolved:resume});if(paused)return pause();break}case'ssDisposalOrder':case'ssShredder':break;case'ssOverheatedPart':if(isReturning&&ctx.meld)applyScrapShiftOverheat(w,ctx.meld,c);break;case'vacancyJoker':case'rebelJoker':break"
h=replace_once(h,old_cases,new_cases,'SCRAP-SHIFT wave4 resolver cases')

old_cards=",'SSS10':{slot:'S10',themeId:'scrap-shift',n:'과열 부품',t:'ssOverheatedPart',d:'내 부품이 있는 조합으로 스위치를 반환하면 상대에게 취약 1을 부여한다.'}\n\n};"
new_cards=",'SSS10':{slot:'S10',themeId:'scrap-shift',n:'과열 부품',t:'ssOverheatedPart',d:'내 부품이 있는 조합으로 스위치를 반환하면 상대에게 취약 1을 부여한다. 같은 턴에는 한 번만 적용된다.'}\n,'SSD7':{slot:'D7',themeId:'scrap-shift',n:'예비 나사',t:'ssSpareScrew',d:'이 카드를 버림패에서 가져온 턴에 사용하면 남은 손패의 내 카드 1장을 부품으로 지정할 수 있다. 지정했다면 보호막 8을 얻는다.'}\n,'SSC8':{slot:'C8',themeId:'scrap-shift',n:'분기 레일',t:'ssBranchRail',d:'내 부품을 세트와 런 사이로 이식하면 카드 1장을 뽑고 손패 1장을 덱 아래로 보낸다.'}\n,'SSH8':{slot:'H8',themeId:'scrap-shift',n:'예비 섀시',t:'ssSpareChassis',d:'상대 효과로 내 부품이 소모패에 들어가면 다음 내 턴 시작에 그 카드가 여전히 부품일 경우 보호막 12를 얻는다.'}\n,'SSS7':{slot:'S7',themeId:'scrap-shift',n:'파쇄기',t:'ssShredder',d:'내 부품이 소모패에 들어간 턴에 손패의 다른 내 카드 1장을 새 부품으로 지정할 수 있다. 턴당 1회.'}\n\n};"
h=replace_once(h,old_cards,new_cards,'SCRAP-SHIFT wave4 card definitions')
INDEX.write_text(h,encoding='utf-8')

road=ROAD.read_text(encoding='utf-8')
road_anchor='- [x] 3차 유틸리티 슬라이스 4장 — 5♦ 표준 규격 / 4♣ 임시 용접 / 2♥ 자석 회수기 / 10♠ 과열 부품. 부품 상태의 세트 진입·런 보호·무료 회수·반환 취약을 실제 행동 경로에 연결\n- [ ] 24장 / 수트별 6장 정의 및 실제 효과 구현'
road_repl='- [x] 3차 유틸리티 슬라이스 4장 — 5♦ 표준 규격 / 4♣ 임시 용접 / 2♥ 자석 회수기 / 10♠ 과열 부품. 부품 상태의 세트 진입·런 보호·무료 회수·반환 취약을 실제 행동 경로에 연결\n- [x] 4차 수명주기 슬라이스 4장 — 7♦ 예비 나사 / 8♣ 분기 레일 / 8♥ 예비 섀시 / 7♠ 파쇄기. 버림패 기동·세트↔런 이식·상대 효과 소모 추적·대체 부품 지정을 공용 부품 수명주기에 연결\n- [x] 과열 부품의 같은 턴 취약 중복 적용을 공용 테마 턴 게이트로 차단\n- [ ] 24장 / 수트별 6장 정의 및 실제 효과 구현'
road=replace_once(road,road_anchor,road_repl,'ROADMAP wave4')
ROAD.write_text(road,encoding='utf-8')

theme=THEME.read_text(encoding='utf-8')
theme_anchor='- [x] 3차 유틸리티 슬라이스 — 5♦ `표준 규격` / 4♣ `임시 용접` / 2♥ `자석 회수기` / 10♠ `과열 부품`을 DEV 전용 구현. 부품 세트 진입·런 보호·무료 회수·반환 취약의 기본 전투 루프 검증\n- [ ] 24장 전체 정의/효과/해금/도감/덱빌더/체험전 연결 뒤 카드군 라이브 승격'
theme_repl='- [x] 3차 유틸리티 슬라이스 — 5♦ `표준 규격` / 4♣ `임시 용접` / 2♥ `자석 회수기` / 10♠ `과열 부품`을 DEV 전용 구현. 부품 세트 진입·런 보호·무료 회수·반환 취약의 기본 전투 루프 검증\n- [x] 4차 수명주기 슬라이스 — 7♦ `예비 나사` / 8♣ `분기 레일` / 8♥ `예비 섀시` / 7♠ `파쇄기` 구현. 버림패 획득 턴 부품 지정, 세트↔런 이식 순환, 상대 효과 소모의 다음 턴 추적, 턴당 1회 대체 부품 지정 연결\n- [x] 10♠ `과열 부품` 같은 턴 중복 취약 방지 게이트 보정\n- [ ] 24장 전체 정의/효과/해금/도감/덱빌더/체험전 연결 뒤 카드군 라이브 승격'
theme=replace_once(theme,theme_anchor,theme_repl,'theme doc wave4')
THEME.write_text(theme,encoding='utf-8')

pool=POOL.read_text(encoding='utf-8')
pool=replace_once(pool,'24장 미라이브 · 12장 DEV 구현 완료(행동 4 + 반응 4 + 유틸리티 4)','24장 미라이브 · 16장 DEV 구현 완료(행동 4 + 반응 4 + 유틸리티 4 + 수명주기 4)','pool plan wave4')
POOL.write_text(pool,encoding='utf-8')
print('SCRAP-SHIFT wave4 patch applied')

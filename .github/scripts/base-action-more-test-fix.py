from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]

p=ROOT/'tests'/'korean-terms.mjs'
s=p.read_text(encoding='utf-8')
old="ok(html.includes('합계 +${p.total} · 스위치 → 상대'), 'multi-attach preview is localized');"
new="ok(html.includes(\"extra?'추가 붙이기 · 스위치 이동 없음':'스위치 → 상대'\") && html.includes('합계 +${p.total}'), 'multi-attach preview localizes both normal return and named extra-attach no-move states');"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('missing korean-terms attach preview anchor')
p.write_text(s,encoding='utf-8')

p=ROOT/'tests'/'m10-multiattach-search.mjs'
s=p.read_text(encoding='utf-8')
fixes=[
("  const meld = {type:'RUN', cards:[{uid:'m1'},{uid:'m2'},{uid:'m3'}], chain:0, lastAttachToken:null, createdToken:null};","  const meld = {type:'RUN', cards:[{uid:'m1'},{uid:'m2'},{uid:'m3'}], chain:0, createdToken:null};"),
("  const side = {hand, returnedSwitchThisTurn:false};","  const side = {hand, returnedSwitchThisTurn:false, attachCount:0, extraAttachRemaining:0};"),
("    canSideReturn:()=>true,\n    canContinueReturnedRun:()=>false","    canSideReturn:()=>true"),
("  install(ctx, 'chainDamage', 'combinations', 'bestExtensionFromHand', 'anyAttachOption');","  install(ctx, 'chainDamage', 'combinations', 'attachAccess', 'bestExtensionFromHand', 'anyAttachOption');")
]
for old,new in fixes:
    if old in s:s=s.replace(old,new,1)
    elif new not in s:raise SystemExit(f'missing M10 migration anchor: {old[:80]}')
p.write_text(s,encoding='utf-8')
print('localized preview and M10 multi-attach harness migrated')


p=ROOT/'tests'/'m11b-action-commit.mjs'
s=p.read_text(encoding='utf-8')
fixes=[
("  const player={hand:[...handCards,card('C','2')],melds:[],returnedSwitchThisTurn:false,actedThisTurn:false,turnStarts:1};","  const player={hand:[...handCards,card('C','2')],melds:[],returnedSwitchThisTurn:false,attachCount:0,extraAttachRemaining:0,actedThisTurn:false,turnStarts:1};"),
("  const enemy={hand:[],melds:[{type,cards:[...baseCards],chain,lastAttachToken:null,createdToken:null,lastTouchedOwnerStart:0,status:{}}],returnedSwitchThisTurn:false,turnStarts:1};","  const enemy={hand:[],melds:[{type,cards:[...baseCards],chain,createdToken:null,lastTouchedOwnerStart:0,status:{}}],returnedSwitchThisTurn:false,attachCount:0,extraAttachRemaining:0,turnStarts:1};"),
("  install(ctx,...rankCore,'recoveredCardCanReturn','recoveredCardsCanReturn','chainDamage','canContinueReturnedRun','attachCards');","  install(ctx,...rankCore,'recoveredCardCanReturn','recoveredCardsCanReturn','chainDamage','attachAccess','consumeAttachUse','attachCards');")
]
for old,new in fixes:
    if old in s:s=s.replace(old,new,1)
    elif new not in s:raise SystemExit(f'missing M11B attach migration anchor: {old[:90]}')
p.write_text(s,encoding='utf-8')
print('M11B attach action harness migrated to global attach contract')


p=ROOT/'tests'/'m11b-ai-rank-plans.mjs'
s=p.read_text(encoding='utf-8')
before=s
s=s.replace(",lastAttachToken:null","")
s=s.replace("returnedSwitchThisTurn:false}","returnedSwitchThisTurn:false,attachCount:0,extraAttachRemaining:0}")
s=s.replace("ctx.canContinueReturnedRun=()=>false;","")
s=s.replace("install(ctx,'combinations',...rankNames,'bestExtensionFromHand');","install(ctx,'combinations',...rankNames,'attachAccess','bestExtensionFromHand');")
s=s.replace("install(ctx,'combinations',...rankNames,'anyAttachOption');","install(ctx,'combinations',...rankNames,'attachAccess','anyAttachOption');")
if s==before and "attachAccess','bestExtensionFromHand" not in s:
    raise SystemExit('missing M11B AI attach migration anchors')
p.write_text(s,encoding='utf-8')
print('M11B AI rank-plan harness migrated to global attach contract')


p=ROOT/'tests'/'m12-battle-metrics.mjs'
s=p.read_text(encoding='utf-8')
fixes=[
("  ctx.recordMeldActionMetric('player','RUN',3,'enemy',{continuation:false});","  ctx.recordMeldActionMetric('player','RUN',3,'enemy',{extraAttach:false});"),
("ok(html.includes(\"recordMeldActionMetric(w,type,cards.length,targetSide,{continuation})\"),'successful attach path records BURST/CHAIN, opponent-meld use and multi-attach size');","ok(html.includes(\"recordMeldActionMetric(w,type,cards.length,targetSide,{extraAttach:access.extra})\"),'successful attach path records BURST/CHAIN, opponent-meld use, multi-attach size and named extra-attach metadata');")
]
for old,new in fixes:
    if old in s:s=s.replace(old,new,1)
    elif new not in s:raise SystemExit(f'missing M12 attach metric migration anchor: {old[:100]}')
p.write_text(s,encoding='utf-8')
print('M12 attach metrics migrated from continuation to extraAttach metadata')


p=ROOT/'tests'/'named-card-audit.mjs'
s=p.read_text(encoding='utf-8')
old="ok(html.includes(\"'C5':{n:'연결고리',t:'connectionLink',d:'런에 붙일 때\" )&&html.includes('그 런에는 이번 턴 한 번 더 붙일 수 있다.'),'Connection Link documents its extra-attach behavior');"
new="ok(html.includes(\"'C5':{n:'연결고리',t:'connectionLink',d:'런에 붙일 때\" )&&html.includes('이번 턴 추가 붙이기 1회를 얻는다.')&&html.includes('추가 붙이기는 스위치를 다시 이동시키지 않는다.'),'Connection Link documents the named extra-attach exception and no second SWITCH move');"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('missing Connection Link audit migration anchor')
p.write_text(s,encoding='utf-8')
print('Connection Link named-card audit migrated to explicit extraAttach contract')


p=ROOT/'tests'/'named-card-behavior-2.mjs'
s=p.read_text(encoding='utf-8')
fixes=[
("  const source={type:'RUN',cards:[card('C',6),card('C',7),card('C',8),moving],createdToken:1,lastAttachToken:null};","  const source={type:'RUN',cards:[card('C',6),card('C',7),card('C',8),moving],createdToken:1};"),
("  const target={type:'SET',cards:[Object.assign(card('S',9),{_meldType:'SET'}),card('H',9),tuner],createdToken:1,lastAttachToken:null};","  const target={type:'SET',cards:[Object.assign(card('S',9),{_meldType:'SET'}),card('H',9),tuner],createdToken:1};"),
("  const side={flags:{tuner:false,roundabout:false},returnedSwitchThisTurn:false,turnStarts:1,freeRecoverAfterRummy:false};","  const side={flags:{tuner:false,roundabout:false},returnedSwitchThisTurn:false,attachCount:0,extraAttachRemaining:0,turnStarts:1,freeRecoverAfterRummy:false};"),
("  install(ctx,'tunerReadyForRecovery','recoveryFreeReason');","  install(ctx,'attachAccess','tunerReadyForRecovery','recoveryFreeReason');")
]
for old,new in fixes:
    if old in s:s=s.replace(old,new,1)
    elif new not in s:raise SystemExit(f'missing named behavior attach migration anchor: {old[:100]}')
p.write_text(s,encoding='utf-8')
print('named-card Tuner harness migrated to global attach contract')


p=ROOT/'tests'/'named-final-semantics.mjs'
s=p.read_text(encoding='utf-8')
fixes=[
("const insurance=source('insuranceBlocks'),detonate=source('detonate'),replace=source('replaceRedundantJokers'),continuation=source('canContinueReturnedRun');","const insurance=source('insuranceBlocks'),detonate=source('detonate'),replace=source('replaceRedundantJokers');"),
("ok(replace.includes('m.rebelReturnBlockedToken=state.turnToken')&&replace.includes('m.lastAttachToken=state.turnToken'),'Rebel replacement records both generic attach lock and explicit return-continuation lock');","ok(replace.includes('sideObj(attacher).extraAttachRemaining=0'),'Rebel replacement removes the replacing player\\'s named extra-attach allowance');"),
("ok(continuation.includes('m.rebelReturnBlockedToken!==state.turnToken'),'same-RUN continuation cannot bypass a Rebel replacement lock');","ok(!script.includes('function canContinueReturnedRun(')&&!replace.includes('rebelReturnBlockedToken')&&!replace.includes('lastAttachToken'),'Rebel semantics no longer depend on removed same-RUN continuation state');")
]
for old,new in fixes:
    if old in s:s=s.replace(old,new,1)
    elif new not in s:raise SystemExit(f'missing named-final semantics migration anchor: {old[:110]}')
p.write_text(s,encoding='utf-8')
print('Rebel Joker final semantics migrated to extraAttach suppression')


p=ROOT/'tests'/'point-blank-recovery-access.mjs'
s=p.read_text(encoding='utf-8')
old="ok(ui.includes(\"recoverAccess?.free?'무료 회수':'회수'\")&&ui.includes(\"'기본 회수 사용함'\"),'player UI visibly distinguishes free recovery from an already-used basic recovery');"
new="ok(ui.includes(\"recoverAccess?.free?'무료 회수':'회수'\")&&ui.includes(\"'회수 사용함'\")&&ui.includes(\":state.player.recoveredThisTurn?'회수 사용함':'회수'\"),'player UI visibly distinguishes free recovery from an already-used basic recovery with the compact action label');"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('missing POINT-BLANK recovery UI migration anchor')
p.write_text(s,encoding='utf-8')
print('POINT-BLANK recovery UI regression migrated to compact label')


p=ROOT/'tests'/'safety-hardening.mjs'
s=p.read_text(encoding='utf-8')
old="""{
 const card={uid:'8',suit:'H',rank:'8',owner:'player',blockedUntilTurn:null,recoveredToken:null,recoverReturnOverrideToken:null};
 const player={hand:[card],deck:[c('d')],spent:[],melds:[],newMeldCount:0,returnedSwitchThisTurn:true,maintenanceUsed:false};
 const enemy={hand:[],deck:[],spent:[],melds:[],newMeldCount:0,returnedSwitchThisTurn:false};
 const m={type:'RUN',cards:[{suit:'H',rank:'5'},{suit:'H',rank:'6'},{suit:'H',rank:'7'}],chain:1,lastAttachToken:9,returnAttachToken:9,createdToken:null};enemy.melds=[m];
 const state={player,enemy,discard:[],turnNo:2,turnToken:9,switchTarget:'enemy',gameOver:false,turn:'player',phase:'action'};
 const ctx=vm.createContext({console,Set,Map,Array,Math,state});ctx.sideObj=w=>w==='player'?player:enemy;ctx.other=w=>w==='player'?'enemy':'player';ctx.meldsOf=w=>ctx.sideObj(w).melds;ctx.canSideReturn=w=>state.switchTarget==='neutral'||state.switchTarget===w;ctx.canContinueReturnedRun=(w,x)=>w==='player'&&x===m;ctx.meldType=cards=>cards.every(x=>x.suit==='H')&&new Set(cards.map(x=>Number(x.rank))).size===cards.length?'RUN':null;ctx.meldFixedActive=()=>false;ctx.cardFixedActive=()=>false;install(ctx,'combinations','bestNewMeld','bestNewMeldForTurn','recoveredCardCanReturn','recoveredCardsCanReturn','anyAttachOption','canFinishRun','hasAnyLegalAction','ownedRecycleCount','maintenanceLimit');
 ok(ctx.anyAttachOption('player'),'same returned RUN continuation counts as a legal attach after physical SWITCH return');
 ok(ctx.maintenanceLimit('player')===1,'legal same-RUN continuation prevents false two-card stuck maintenance');
}"""
new="""{
 const card={uid:'8',suit:'H',rank:'8',owner:'player',blockedUntilTurn:null,recoveredToken:null,recoverReturnOverrideToken:null};
 const player={hand:[card],deck:[c('d')],spent:[],melds:[],newMeldCount:0,attachCount:1,extraAttachRemaining:0,returnedSwitchThisTurn:true,maintenanceUsed:false};
 const enemy={hand:[],deck:[],spent:[],melds:[],newMeldCount:0,attachCount:0,extraAttachRemaining:0,returnedSwitchThisTurn:false};
 const m={type:'RUN',cards:[{suit:'H',rank:'5'},{suit:'H',rank:'6'},{suit:'H',rank:'7'}],chain:1,createdToken:null};enemy.melds=[m];
 const state={player,enemy,discard:[],turnNo:2,turnToken:9,switchTarget:'enemy',gameOver:false,turn:'player',phase:'action'};
 const ctx=vm.createContext({console,Set,Map,Array,Math,state});ctx.sideObj=w=>w==='player'?player:enemy;ctx.other=w=>w==='player'?'enemy':'player';ctx.meldsOf=w=>ctx.sideObj(w).melds;ctx.canSideReturn=w=>state.switchTarget==='neutral'||state.switchTarget===w;ctx.meldType=cards=>cards.every(x=>x.suit==='H')&&new Set(cards.map(x=>Number(x.rank))).size===cards.length?'RUN':null;ctx.meldFixedActive=()=>false;ctx.cardFixedActive=()=>false;ctx.anyCleanupOption=()=>false;install(ctx,'combinations','bestNewMeld','bestNewMeldForTurn','recoveredCardCanReturn','recoveredCardsCanReturn','attachAccess','anyAttachOption','canFinishRun','hasAnyLegalAction','ownedRecycleCount','maintenanceLimit');
 ok(!ctx.anyAttachOption('player'),'spent base attach does not regain a hidden same-RUN continuation after SWITCH return');
 ok(ctx.maintenanceLimit('player')===2,'without a named exception, spent attach correctly qualifies for stuck maintenance');
 player.extraAttachRemaining=1;
 ok(ctx.anyAttachOption('player'),'explicit named extra-attach allowance restores a legal attach without a second SWITCH move');
 ok(ctx.maintenanceLimit('player')===1,'named extra-attach allowance prevents false stuck maintenance');
}"""
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('missing safety-hardening same-RUN migration anchor')
p.write_text(s,encoding='utf-8')
print('safety hardening migrated from same-RUN continuation to named extraAttach contract')


p=ROOT/'tests'/'status-engine.mjs'
s=p.read_text(encoding='utf-8')
old="ok(html.includes('고정 · 조합/카드 · 다음 소유자 턴 종료까지 회수·강탈·절단 등 이동 불가'),'rules modal documents fixed scope/lifecycle');"
new="ok(html.includes('고정 · 조합/카드 · 다음 소유자 턴 종료까지 회수·강탈·절단·자발적 정리 등 이동 불가'),'rules modal documents fixed scope/lifecycle including voluntary cleanup lock');"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('missing fixed-status cleanup wording migration anchor')
p.write_text(s,encoding='utf-8')
print('status-engine fixed wording migrated for voluntary cleanup')


p=ROOT/'tests'/'vsignal-mixed-regression.mjs'
s=p.read_text(encoding='utf-8')
fixes=[
("  const sourceRun={type:'RUN',cards:[encore,card('H','6'),card('H','7'),card('H','8')],chain:1,createdToken:null,lastAttachToken:null};","  const sourceRun={type:'RUN',cards:[encore,card('H','6'),card('H','7'),card('H','8')],chain:1,createdToken:null};"),
("  const targetSet={type:'SET',cards:[card('S','5'),card('D','5'),card('C','5')],chain:0,createdToken:null,lastAttachToken:null};","  const targetSet={type:'SET',cards:[card('S','5'),card('D','5'),card('C','5')],chain:0,createdToken:null};"),
("  const player={melds:[sourceRun],returnedSwitchThisTurn:false};","  const player={melds:[sourceRun],returnedSwitchThisTurn:false,attachCount:0,extraAttachRemaining:0};"),
("  const enemy={melds:[targetSet],returnedSwitchThisTurn:false};","  const enemy={melds:[targetSet],returnedSwitchThisTurn:false,attachCount:0,extraAttachRemaining:0};"),
("  install(ctx,'isJoker','isSuitFlexible','setValid','runSequenceOK','runValid','meldType','legalRecoveryReturnTargets','grantRecoveryReturnOverride','handleVSignalThemeEvent','recoveredCardCanReturn','consumeEncoreReturnPermission');","  install(ctx,'isJoker','isSuitFlexible','setValid','runSequenceOK','runValid','meldType','attachAccess','legalRecoveryReturnTargets','grantRecoveryReturnOverride','handleVSignalThemeEvent','recoveredCardCanReturn','consumeEncoreReturnPermission');")
]
for old,new in fixes:
    if old in s:s=s.replace(old,new,1)
    elif new not in s:raise SystemExit(f'missing V-SIGNAL mixed attach migration anchor: {old[:110]}')
p.write_text(s,encoding='utf-8')
print('V-SIGNAL mixed recovery-return harness migrated to global attach contract')


p=ROOT/'tests'/'vsignal-tutorial.mjs'
s=p.read_text(encoding='utf-8')
fixes=[
(" const sourceRun={type:'RUN',cards:[encore,card('H','6'),card('H','7'),card('H','8')],chain:1,createdToken:null,lastAttachToken:null};"," const sourceRun={type:'RUN',cards:[encore,card('H','6'),card('H','7'),card('H','8')],chain:1,createdToken:null};"),
(" const destSet={type:'SET',cards:[card('S','5',{owner:'enemy'}),card('D','5',{owner:'enemy'}),card('C','5',{owner:'enemy'})],chain:0,createdToken:null,lastAttachToken:null};"," const destSet={type:'SET',cards:[card('S','5',{owner:'enemy'}),card('D','5',{owner:'enemy'}),card('C','5',{owner:'enemy'})],chain:0,createdToken:null};"),
(" const player={melds:[sourceRun],returnedSwitchThisTurn:false},enemy={melds:[destSet],returnedSwitchThisTurn:false};"," const player={melds:[sourceRun],returnedSwitchThisTurn:false,attachCount:0,extraAttachRemaining:0},enemy={melds:[destSet],returnedSwitchThisTurn:false,attachCount:0,extraAttachRemaining:0};"),
(" ctx.sideObj=w=>w==='player'?player:enemy;ctx.other=w=>w==='player'?'enemy':'player';ctx.meldsOf=w=>ctx.sideObj(w).melds;ctx.canSideReturn=()=>true;ctx.canContinueReturnedRun=()=>false;ctx.log=()=>{};"," ctx.sideObj=w=>w==='player'?player:enemy;ctx.other=w=>w==='player'?'enemy':'player';ctx.meldsOf=w=>ctx.sideObj(w).melds;ctx.canSideReturn=()=>true;ctx.log=()=>{};"),
(" install(ctx,'isJoker','isSuitFlexible','setValid','runSequenceOK','runValid','meldType','legalRecoveryReturnTargets','grantRecoveryReturnOverride','handleVSignalThemeEvent','recoveredCardCanReturn');"," install(ctx,'isJoker','isSuitFlexible','setValid','runSequenceOK','runValid','meldType','attachAccess','legalRecoveryReturnTargets','grantRecoveryReturnOverride','handleVSignalThemeEvent','recoveredCardCanReturn');")
]
for old,new in fixes:
    if old in s:s=s.replace(old,new,1)
    elif new not in s:raise SystemExit(f'missing V-SIGNAL tutorial attach migration anchor: {old[:110]}')
p.write_text(s,encoding='utf-8')
print('V-SIGNAL tutorial harness migrated to global attach contract')

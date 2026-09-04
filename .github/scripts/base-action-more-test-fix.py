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

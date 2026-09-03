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

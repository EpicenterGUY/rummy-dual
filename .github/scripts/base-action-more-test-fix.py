from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
p=ROOT/'tests'/'korean-terms.mjs'
s=p.read_text(encoding='utf-8')
old="ok(html.includes('합계 +${p.total} · 스위치 → 상대'), 'multi-attach preview is localized');"
new="ok(html.includes(\"extra?'추가 붙이기 · 스위치 이동 없음':'스위치 → 상대'\") && html.includes('합계 +${p.total}'), 'multi-attach preview localizes both normal return and named extra-attach no-move states');"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('missing korean-terms attach preview anchor')
p.write_text(s,encoding='utf-8')
print('korean terms attach preview regression migrated')

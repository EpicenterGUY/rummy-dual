from pathlib import Path

p=Path('index.html')
s=p.read_text()

# Multi-attach telemetry only applies to attach actions with 2+ cards.
old="opponent:targetSide===other(w),multi:list.length>1,slots:"
new="opponent:targetSide===other(w),multi:!!m&&list.length>1,slots:"
if old not in s:
    if new not in s:
        raise SystemExit('counterfactual multi-attach anchor missing')
else:
    s=s.replace(old,new,1)

# Keep recordM11BRankChoices extractable in isolated regressions. Runtime uses
# RANK_VALUE; extracted-function tests get the same canonical fallback table.
old_gap="const orientation=x.orientation==='bottom'?'bottom':'top',gap=Math.abs((RANK_VALUE[c.topRank]||0)-(RANK_VALUE[c.bottomRank]||0));"
new_gap="const orientation=x.orientation==='bottom'?'bottom':'top',rv=typeof RANK_VALUE==='object'&&RANK_VALUE?RANK_VALUE:{A:1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,J:11,Q:12,K:13},gap=Math.abs((rv[c.topRank]||0)-(rv[c.bottomRank]||0));"
if old_gap in s:
    s=s.replace(old_gap,new_gap,1)
elif new_gap not in s:
    raise SystemExit('rank-choice gap anchor missing')

p.write_text(s)

# Lock the terminology in the prototype doc: multi-attach means attach action only.
doc=Path('docs/ASYMMETRIC_RANK_PROTOTYPE.md')
d=doc.read_text()
old_doc='- base projection이 불법인데 실제 선택값 행동은 성공했다면 `구제 행동`이다. 세트 / 런 / 상대 공개 조합 사용 / 2장 이상 다중붙이기 구제를 각각 별도 누적한다.'
new_doc='- base projection이 불법인데 실제 선택값 행동은 성공했다면 `구제 행동`이다. 세트 / 런 / 상대 공개 조합 사용을 별도 누적하고, `다중붙이기 구제`는 **붙이기 행동에서 한 번에 2장 이상 붙인 경우에만** 센다. 새 3장 조합은 카드 수가 3이어도 다중붙이기가 아니다.'
if old_doc in d:
    d=d.replace(old_doc,new_doc,1)
elif new_doc not in d:
    raise SystemExit('counterfactual doc anchor missing')
doc.write_text(d)

# Add permanent regression assertions for both semantic boundaries.
t=Path('.github/scripts/m11b_counterfactual_regression.mjs')
r=t.read_text()
anchor="ok(st.asymActions===1&&st.rescuedActions===1&&st.rescuedSet===1&&st.rescuedRun===0,'rescued SET counters update exactly once');"
insert=anchor+"\n  ok(evt.multi===false&&st.rescuedMultiAttach===0,'new three-card meld is never counted as multi-attach telemetry');"
if insert not in r:
    if anchor not in r: raise SystemExit('counterfactual regression anchor missing')
    r=r.replace(anchor,insert,1)
t.write_text(r)
print('M11B counterfactual telemetry semantics and isolated-test compatibility fixed')

from pathlib import Path
p=Path('.github/scripts/m11b_rank_choice_ui_patch.py')
s=p.read_text()
old='''old="""  const combined=m.cards.concat(cards),type=meldType(combined);\n  if(type!==m.type)return false;\n"""\nnew="""  const rankPlans=typeof legalRankChoicePlansForAttach==='function'?legalRankChoicePlansForAttach(m,cards):null;\n  const combined=m.cards.concat(cards),type=rankPlans?.[0]?.type||meldType(combined);\n  if(rankPlans?rankPlans.length===0:type!==m.type)return false;\n"""'''
new='''old="  if(meldType(m.cards.concat(cards))!==m.type)return false;"\nnew="const rankPlans=typeof legalRankChoicePlansForAttach==='function'?legalRankChoicePlansForAttach(m,cards):null;if(rankPlans?rankPlans.length===0:meldType(m.cards.concat(cards))!==m.type)return false;"'''
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('rank-choice patcher canAttach anchor block missing')
p.write_text(s)
print('M11B rank-choice patcher aligned to current canAttachTo source')

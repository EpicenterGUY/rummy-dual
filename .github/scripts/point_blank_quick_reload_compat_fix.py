from pathlib import Path

p=Path('index.html')
text=p.read_text()
old="function bestFinishRunAI(w){const s=sideObj(w);if(s.melds.length<2||!bestNewMeldForTurn(w))return null;"
new="function bestFinishRunAI(w){const s=sideObj(w),nextMeld=bestNewMeldForTurn(w),extraReady=s.newMeldUsed&&typeof newMeldAccess==='function'&&nextMeld&&newMeldAccess(w,nextMeld.cards).extra;if(s.melds.length<2||!nextMeld||(s.newMeldUsed&&!extraReady))return null;"
assert old in text,'Quick Reload bestFinishRunAI compatibility anchor changed'
text=text.replace(old,new,1)
p.write_text(text)

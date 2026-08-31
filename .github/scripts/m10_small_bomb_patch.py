from pathlib import Path

index = Path('index.html')
road = Path('ROADMAP.md')
text = index.read_text()

old_anchor = "function chooseAIMaintenanceCards(){const h=state.enemy.hand.map(c=>({c,score:aiKeepScore(c,state.enemy.hand)})).sort((a,b)=>a.score-b.score);return h.slice(0,Math.min(2,h.length)).map(x=>x.c)}\nfunction continueAITurnAfterAcquisition(resumeState={})"
new_anchor = "function chooseAIMaintenanceCards(){const h=state.enemy.hand.map(c=>({c,score:aiKeepScore(c,state.enemy.hand)})).sort((a,b)=>a.score-b.score);return h.slice(0,Math.min(2,h.length)).map(x=>x.c)}\nfunction aiShouldAcceptSmallBomb(w,ex=null){const s=sideObj(w),foe=sideObj(other(w)),incoming=Math.max(0,state.switchPower||0);if(state.switchTarget!==w||incoming<=0)return false;if(incoming>=s.hp+s.shield)return false;const coreDamage=Math.max(0,incoming-s.shield),postHp=s.hp-coreDamage,reserve=Math.max(10,Math.ceil((s.maxHp||60)*.18)),budget=Math.max(10,Math.min(18,Math.floor(s.hp*.3)));if(coreDamage>budget||postHp<reserve)return false;if(ex){const gain=Math.max(0,ex.score||0),projected=incoming+gain,foeNeed=foe.hp+foe.shield;if(gain>=20||gain>=incoming+8||projected>=foeNeed)return false}return true}\nfunction continueAITurnAfterAcquisition(resumeState={})"
assert old_anchor in text, 'AI maintenance/turn anchor changed'
text = text.replace(old_anchor, new_anchor, 1)

old_decision = "const switchUrgent=state.switchTarget==='enemy'&&state.switchPower>0,coreNeed=state.enemy.hp+state.enemy.shield,acceptThreshold=Math.max(12,Math.floor(state.enemy.hp*.35+state.enemy.shield*.5)),acceptSmall=switchUrgent&&state.switchPower<coreNeed&&state.switchPower<=acceptThreshold;"
new_decision = "const switchUrgent=state.switchTarget==='enemy'&&state.switchPower>0,acceptSmall=typeof aiShouldAcceptSmallBomb==='function'?aiShouldAcceptSmallBomb('enemy',ex):false;"
assert old_decision in text, 'legacy small-bomb decision anchor changed'
text = text.replace(old_decision, new_decision, 1)
index.write_text(text)

r = road.read_text()
old_line = '- [ ] Improve intentional small-bomb acceptance decisions'
new_line = '- [x] Improve intentional small-bomb acceptance decisions — AI accepts only survivable low-cost bombs that preserve a safe current-CORE reserve, but returns instead when the available extension is high-value or creates immediate lethal pressure on the opponent'
assert old_line in r, 'M10 small-bomb roadmap anchor changed'
r = r.replace(old_line, new_line, 1)
road.write_text(r)

from pathlib import Path

index = Path('index.html')
road = Path('ROADMAP.md')
text = index.read_text()

old_newmeld = "function bestNewMeld(hand){let best=null;if(hand.length<3)return null;for(const cs of combinations(hand,3)){const t=meldType(cs);if(t){let sc=12+cs.filter(c=>c.named).length*2+(t==='SET'?3:2);if(!best||sc>best.score)best={cards:cs,type:t,score:sc}}}return best}\nfunction bestNewMeldForTurn(w,hand=sideObj(w).hand){return bestNewMeld(hand.filter(c=>c.blockedUntilTurn!==state.turnNo))}"
new_newmeld = "function futureBurstRisk(w,cards,type){if(!w||type!=='SET'||cards.length!==3)return 0;const foe=sideObj(other(w)),handCount=foe?.hand?.length||0;let risk=4+Math.min(4,Math.max(0,handCount-3));if(state.switchTarget===other(w)&&state.switchPower>0)risk+=4;const top=state.discard?.at(-1);if(top&&meldType(cards.concat(top))==='SET')risk+=8;return risk}\nfunction opponentMeldAttachBias(w,targetSide,m,combined,attachCount=1){if(targetSide!==other(w)||!m)return 0;if(m.type==='SET'&&m.cards.length===3&&combined.length===4)return 8;if(m.type==='RUN'&&(m.chain||0)+attachCount>=4)return-4;if(m.type==='RUN')return 2;return 0}\nfunction bestNewMeld(hand,w=null){let best=null;if(hand.length<3)return null;for(const cs of combinations(hand,3)){const t=meldType(cs);if(t){const risk=typeof futureBurstRisk==='function'?futureBurstRisk(w,cs,t):0;let sc=12+cs.filter(c=>c.named).length*2+(t==='SET'?3:2)-risk;if(!best||sc>best.score)best={cards:cs,type:t,score:sc}}}return best}\nfunction bestNewMeldForTurn(w,hand=sideObj(w).hand){return bestNewMeld(hand.filter(c=>c.blockedUntilTurn!==state.turnNo),w)}"
assert old_newmeld in text, 'bestNewMeld anchor changed'
text = text.replace(old_newmeld, new_newmeld, 1)

old_bias = "if(targetSide===other(w))sc+=4;if(targetSide===other(w)&&cs.some(c=>c.tag==='enemyAttachBonus'))sc+=15;"
new_bias = "if(typeof opponentMeldAttachBias==='function')sc+=opponentMeldAttachBias(w,targetSide,m,combined,k);else if(targetSide===other(w))sc+=4;if(targetSide===other(w)&&cs.some(c=>c.tag==='enemyAttachBonus'))sc+=15;"
assert old_bias in text, 'bestExtension opponent-meld score anchor changed'
text = text.replace(old_bias, new_bias, 1)

index.write_text(text)

r = road.read_text()
old_line = '- [ ] Improve opponent-meld and future-BURST risk evaluation'
new_line = '- [x] Improve opponent-meld and future-BURST risk evaluation — AI now penalizes exposed 3-card SETs using public hand-count / current SWITCH pressure / top-discard burst access, favors immediate BURST cleanup of opponent SETs, and discounts opponent-controlled RUNs that would be pushed to CHAIN 4+ completion flexibility'
assert old_line in r, 'M10 board-risk roadmap anchor changed'
r = r.replace(old_line, new_line, 1)
road.write_text(r)

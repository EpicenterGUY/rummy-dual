from pathlib import Path

index=Path('index.html')
road=Path('ROADMAP.md')
theme=Path('docs/THEME_GROUPS.md')
text=index.read_text()

# 1) Small additive AI layer. It never changes legality; it only ranks already-legal actions.
old="function bestNewMeld(hand,w=null){"
helpers="""function themeAIAttachBias(w,targetSide,m,cards,powerGain=0){if(!w||!m)return 0;const foe=other(w);let score=0;const ownTarget=typeof isZeroSightTarget==='function'&&isZeroSightTarget(w,m),ownClash=typeof isPointBlankClash==='function'&&isPointBlankClash(w,m);if(ownTarget)score+=4;if(ownTarget&&targetSide===foe&&(cards||[]).some(c=>c?.tag==='zsBallistics')&&typeof coreShieldDeficit==='function')score+=coreShieldDeficit(foe,(state.switchPower||0)+Math.max(0,powerGain||0),12);if(ownTarget&&targetSide===foe&&(cards||[]).some(c=>c?.tag==='zsOneShot'))score+=(state.switchPower||0)>=50?18:-6;if(ownClash&&targetSide===foe)score+=4;if(targetSide===foe&&(cards||[]).some(c=>c?.themeId==='v-signal'))score+=2;return score}
function themeAIRecoveryBias(w,targetSide,m,c){if(!w||!m||!c)return 0;let score=0;if(typeof recoveryAccess==='function'&&recoveryAccess(w,targetSide,m,c)?.free)score+=5;if(c.themeId==='v-signal'&&c.tag==='vEncore'&&typeof legalRecoveryReturnTargets==='function'&&legalRecoveryReturnTargets(w,c,m,{}).length)score+=9;if(typeof isPointBlankClash==='function'&&isPointBlankClash(w,m))score+=3;return score}
function bestNewMeld(hand,w=null){"""
assert old in text,'AI helper insertion anchor changed'
text=text.replace(old,helpers,1)

# 2) Preserve M10 base scoring then add theme context as a separate small layer.
old="let sc=0;if(m.type==='SET')sc=m.cards.length===3&&m.cards.length+k===4?24:0;else for(let z=1;z<=k;z++)sc+=chainDamage((m.chain||0)+z);if(typeof opponentMeldAttachBias==='function')sc+=opponentMeldAttachBias(w,targetSide,m,combined,k);else if(targetSide===other(w))sc+=4;if(targetSide===other(w)&&cs.some(c=>c.tag==='enemyAttachBonus'))sc+=15;if(!best||sc>best.score)best={cards:cs,side:targetSide,index:i,score:sc}"
new="let sc=0;if(m.type==='SET')sc=m.cards.length===3&&m.cards.length+k===4?24:0;else for(let z=1;z<=k;z++)sc+=chainDamage((m.chain||0)+z);const powerGain=sc;if(typeof opponentMeldAttachBias==='function')sc+=opponentMeldAttachBias(w,targetSide,m,combined,k);else if(targetSide===other(w))sc+=4;if(targetSide===other(w)&&cs.some(c=>c.tag==='enemyAttachBonus'))sc+=15;if(typeof themeAIAttachBias==='function')sc+=themeAIAttachBias(w,targetSide,m,cs,powerGain);if(!best||sc>best.score)best={cards:cs,side:targetSide,index:i,score:sc}"
assert old in text,'bestExtension scoring anchor changed'
text=text.replace(old,new,1)

# 3) Recovery scoring gets the same additive theme layer; existing Tuner/Quick Reload/new-meld logic remains intact.
old="const c=m.cards[ci],hyp=s.hand.concat(c);let sc=tunerReadyForRecovery(w,targetSide,m,c)?18:-1;if(s.newMeldUsed&&c.themeId==='point-blank'&&c.tag==='pbQuickReload'&&typeof isPointBlankClash==='function'&&isPointBlankClash(w,m)){"
new="const c=m.cards[ci],hyp=s.hand.concat(c);let sc=tunerReadyForRecovery(w,targetSide,m,c)?18:-1;if(typeof themeAIRecoveryBias==='function')sc+=themeAIRecoveryBias(w,targetSide,m,c);if(s.newMeldUsed&&c.themeId==='point-blank'&&c.tag==='pbQuickReload'&&typeof isPointBlankClash==='function'&&isPointBlankClash(w,m)){"
assert old in text,'bestRecover scoring anchor changed'
text=text.replace(old,new,1)

index.write_text(text)

# 4) Roadmap closes minimum theme-aware AI gate.
r=road.read_text()
old='- [ ] AI가 표적·접전·RAID·회수 가치를 판단할 최소 휴리스틱 추가'
new='- [x] AI 표적·접전·상대 조합 사용·회수 최소 휴리스틱 추가 — 기존 M10 합법성/보드 위험 점수는 그대로 두고 `themeAIAttachBias` / `themeAIRecoveryBias`를 가산층으로 추가. 내 표적 활용, 탄도 계산의 실제 부족분, ONE SHOT 50+ 성공/실패, 내 접전 재진입, V-SIGNAL의 상대 조합 사용(RAID형 진입), 무료 회수·앙코르 재진입·접전 회수 가치를 판단하며 테마 점수가 행동 합법성을 우회하지 않음'
assert old in r,'ROADMAP theme AI anchor changed'
r=r.replace(old,new,1)
road.write_text(r)

# 5) Canonical theme design records the same conservative AI policy.
t=theme.read_text()
anchor='- 한 행동에서 여러 테마가 겹치면 **기본 행동 이벤트 → 표적 변화 반응 → 접전 변화 반응 → 반환 후 지연 처리** 순으로 해결한다. 이동은 표적 source→target을 먼저, 접전 source→target을 다음에 해결한다.'
add=anchor+"\n- AI는 테마 전용 별도 규칙을 만들지 않고 이미 합법인 행동의 점수에만 작은 테마 보정을 더한다. 표적 킬각, 접전 재진입, V-SIGNAL 상대 조합 진입, 무료/재사용 회수를 우선 보되 기존 버스트·체인·보드 위험 판단을 덮어쓰지 않는다."
assert anchor in t,'theme AI principle anchor changed'
t=t.replace(anchor,add,1)
theme.write_text(t)

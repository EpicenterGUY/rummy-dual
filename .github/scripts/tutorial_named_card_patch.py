from pathlib import Path

index=Path('index.html')
road=Path('ROADMAP.md')
s=index.read_text()
r=road.read_text()

old=" {id:'jokerDual',title:'쌍면 조커',goal:'조커는 와일드 판정 외에도 각자 고유 효과를 가질 수 있습니다. 쌍면 조커의 세트 효과를 직접 발동합니다.',hint:'쌍면 조커를 내 6♠-6♥-6♦ 세트에 붙이세요. 버스트 +24와 함께 보호막 20을 얻습니다.',implemented:true,scenario:'jokerDual',allow:['select','attach','clear'],selectRoles:['jokerDualCard'],attachSide:'player',expectAttach:'SET',expectAttachTag:'jokerDual',expectSwitchTarget:'enemy',minPowerGain:24,expectShieldGain:20,completeOn:'attach',stopAfter:true}\n]);"
new=" {id:'jokerDual',title:'쌍면 조커',goal:'조커는 와일드 판정 외에도 각자 고유 효과를 가질 수 있습니다. 쌍면 조커의 세트 효과를 직접 발동합니다.',hint:'쌍면 조커를 내 6♠-6♥-6♦ 세트에 붙이세요. 버스트 +24와 함께 보호막 20을 얻습니다.',implemented:true,scenario:'jokerDual',allow:['select','attach','clear'],selectRoles:['jokerDualCard'],attachSide:'player',expectAttach:'SET',expectAttachTag:'jokerDual',expectSwitchTarget:'enemy',minPowerGain:24,expectShieldGain:20,completeOn:'attach'},\n {id:'namedCard',title:'네임드 카드',goal:'네임드는 기존 랭크·무늬 슬롯의 조합 역할을 그대로 유지하면서 고유 효과가 추가된 변형입니다. 응급 보호구로 일반 8♥와의 차이를 확인합니다.',hint:'응급 보호구 8♥를 내 8♠-8♦-8♣ 세트에 붙이세요. 일반 8♥도 버스트를 완성하지만, 네임드 변형은 보호막 20을 추가로 얻습니다.',implemented:true,scenario:'namedCard',allow:['select','attach','clear'],selectRoles:['namedCard'],attachSide:'player',expectAttach:'SET',expectAttachTag:'emergencyGear',expectSwitchTarget:'enemy',minPowerGain:24,expectShieldGain:20,completeOn:'attach',stopAfter:true}\n]);"
if old not in s: raise SystemExit('tutorial step anchor not found')
s=s.replace(old,new,1)

old="function makeTutorialJoker(id,role,owner='player'){const c=makeCard('J',id,true,owner,id);c.tutorialRole=role;return c}\nfunction makeTutorialMeld"
new="function makeTutorialJoker(id,role,owner='player'){const c=makeCard('J',id,true,owner,id);c.tutorialRole=role;return c}\nfunction makeTutorialNamed(id,role,owner='player'){const def=NAMED[id],slot=def?.slot||id,suit=slot[0],rank=slot.slice(1),c=makeCard(suit,rank,true,owner,id);c.tutorialRole=role;return c}\nfunction makeTutorialMeld"
if old not in s: raise SystemExit('tutorial helper anchor not found')
s=s.replace(old,new,1)

old="else if(step.scenario==='jokerDual'){p.hand=[makeTutorialJoker('J3','jokerDualCard'),makeTutorialCard('D','2','hold')];p.melds=[makeTutorialMeld('player','SET',[makeTutorialCard('S','6','board','player'),makeTutorialCard('H','6','board','player'),makeTutorialCard('D','6','board','player')])];state.phase='action';log('조커 고유 효과 실습 · 쌍면 조커를 6 세트에 붙여 버스트와 보호막 20을 함께 확인하세요.','important')}return true}"
new="else if(step.scenario==='jokerDual'){p.hand=[makeTutorialJoker('J3','jokerDualCard'),makeTutorialCard('D','2','hold')];p.melds=[makeTutorialMeld('player','SET',[makeTutorialCard('S','6','board','player'),makeTutorialCard('H','6','board','player'),makeTutorialCard('D','6','board','player')])];state.phase='action';log('조커 고유 효과 실습 · 쌍면 조커를 6 세트에 붙여 버스트와 보호막 20을 함께 확인하세요.','important')}else if(step.scenario==='namedCard'){p.hand=[makeTutorialNamed('H8','namedCard'),makeTutorialCard('D','2','hold')];p.melds=[makeTutorialMeld('player','SET',[makeTutorialCard('S','8','board','player'),makeTutorialCard('D','8','board','player'),makeTutorialCard('C','8','board','player')])];state.phase='action';log('네임드 카드 실습 · 응급 보호구 8♥는 일반 8♥와 같은 세트 재료이면서, 조합에 들어가면 보호막 20을 추가로 얻습니다.','important')}return true}"
if old not in s: raise SystemExit('tutorial scenario anchor not found')
s=s.replace(old,new,1)

old="step.id==='jokerDual'?'고급 튜토리얼 완료! 조커의 와일드 판정·정리 시 귀환·조커별 고유 효과까지 확인했습니다.':'다음 실습은 잠시 후 자동으로 시작됩니다.'"
new="step.id==='namedCard'?'고급 튜토리얼 완료! 네임드는 기존 랭크·무늬 슬롯의 조합 역할을 유지하면서 고유 효과가 추가되는 변형이라는 점까지 확인했습니다.':'다음 실습은 잠시 후 자동으로 시작됩니다.'"
if old not in s: raise SystemExit('tutorial completion copy anchor not found')
s=s.replace(old,new,1)

old="step.id==='jokerDual'?`쌍면 조커 성공! 와일드 버스트 +24와 고유 효과 보호막 ${context.afterShield-context.beforeShield}을 함께 얻었습니다.`:`붙이기 성공! 실제 체인 처리로 누적 위력 ${context.afterPower}이 만들어졌습니다.`"
new="step.id==='jokerDual'?`쌍면 조커 성공! 와일드 버스트 +24와 고유 효과 보호막 ${context.afterShield-context.beforeShield}을 함께 얻었습니다.`:step.id==='namedCard'?`네임드 확인! 8♥의 기본 세트 역할로 버스트를 완성하면서 응급 보호구 고유 효과로 보호막 ${context.afterShield-context.beforeShield}을 추가로 얻었습니다.`:`붙이기 성공! 실제 체인 처리로 누적 위력 ${context.afterPower}이 만들어졌습니다.`"
if old not in s: raise SystemExit('tutorial success copy anchor not found')
s=s.replace(old,new,1)

old="advanced.textContent=progress.tutorialCompleted?'고급 튜토리얼 · 회수/정비/상태/조커':'고급 튜토리얼 · 기본 완료 후'"
new="advanced.textContent=progress.tutorialCompleted?'고급 튜토리얼 · 회수/정비/상태/조커/네임드':'고급 튜토리얼 · 기본 완료 후'"
if old not in s: raise SystemExit('advanced button anchor not found')
s=s.replace(old,new,1)

old='- [ ] 네임드 카드 설명'
new='- [x] 네임드 카드 설명 — 고급 튜토리얼 마지막에 8♥ `응급 보호구`를 실제 8 세트에 붙이는 실습 추가. 일반 8♥와 동일한 랭크·무늬/버스트 역할을 유지하면서 네임드 고유 효과 보호막 20이 실제 `resolveEffects()`에서 추가되는 구조를 체험하고, 네임드는 별도 카드 종류가 아니라 정규 슬롯의 효과 변형임을 안내'
if old not in r: raise SystemExit('roadmap anchor not found')
r=r.replace(old,new,1)

index.write_text(s)
road.write_text(r)

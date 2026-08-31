from pathlib import Path

index=Path('index.html')
road=Path('ROADMAP.md')
foundation=Path('tests/theme-tutorial-foundation.mjs')
s=index.read_text()
r=road.read_text()
f=foundation.read_text()

old="const THEME_TUTORIALS=Object.freeze({'v-signal':Object.freeze({themeId:'v-signal',startStep:null,live:false}),'zero-sight':Object.freeze({themeId:'zero-sight',startStep:null,live:false}),'point-blank':Object.freeze({themeId:'point-blank',startStep:null,live:false})});"
new="const THEME_TUTORIALS=Object.freeze({'v-signal':Object.freeze({themeId:'v-signal',startStep:'vsEncore',live:true}),'zero-sight':Object.freeze({themeId:'zero-sight',startStep:null,live:false}),'point-blank':Object.freeze({themeId:'point-blank',startStep:null,live:false})});"
if old not in s: raise SystemExit('theme tutorial registry anchor not found')
s=s.replace(old,new,1)

old=" {id:'namedCard',title:'네임드 카드',goal:'네임드는 기존 랭크·무늬 슬롯의 조합 역할을 그대로 유지하면서 고유 효과가 추가된 변형입니다. 응급 보호구로 일반 8♥와의 차이를 확인합니다.',hint:'응급 보호구 8♥를 내 8♠-8♦-8♣ 세트에 붙이세요. 일반 8♥도 버스트를 완성하지만, 네임드 변형은 보호막 20을 추가로 얻습니다.',implemented:true,scenario:'namedCard',allow:['select','attach','clear'],selectRoles:['namedCard'],attachSide:'player',expectAttach:'SET',expectAttachTag:'emergencyGear',expectSwitchTarget:'enemy',minPowerGain:24,expectShieldGain:20,completeOn:'attach',stopAfter:true}\n]);"
new=" {id:'namedCard',title:'네임드 카드',goal:'네임드는 기존 랭크·무늬 슬롯의 조합 역할을 그대로 유지하면서 고유 효과가 추가된 변형입니다. 응급 보호구로 일반 8♥와의 차이를 확인합니다.',hint:'응급 보호구 8♥를 내 8♠-8♦-8♣ 세트에 붙이세요. 일반 8♥도 버스트를 완성하지만, 네임드 변형은 보호막 20을 추가로 얻습니다.',implemented:true,scenario:'namedCard',allow:['select','attach','clear'],selectRoles:['namedCard'],attachSide:'player',expectAttach:'SET',expectAttachTag:'emergencyGear',expectSwitchTarget:'enemy',minPowerGain:24,expectShieldGain:20,completeOn:'attach',stopAfter:true},\n {id:'vsEncore',themeId:'v-signal',title:'앙코르 재입장',goal:'V-SIGNAL은 회수한 카드를 다른 공개 조합으로 다시 연결하는 콤보를 만든다. 앙코르를 회수한 뒤 같은 턴 다른 조합의 반환 재료로 재사용해 보세요.',hint:'먼저 내 ♥ RUN의 앙코르 5♥를 선택해 회수하세요. 그 다음 손으로 돌아온 앙코르를 선택해 상대 5♠·5♦·5♣ 세트에 붙이세요. 보통 회수 카드는 같은 턴 BURST/CHAIN 반환에 못 쓰지만, 앙코르는 다른 합법 조합에 한 번 재입장할 수 있습니다.',implemented:true,scenario:'vsEncore',allow:['boardSelect','recover','select','attach','clear'],boardRoles:['vsEncoreCard'],boardSide:'player',selectRoles:['vsEncoreCard'],attachSide:'enemy',expectAttach:'SET',expectAttachTag:'vEncore',expectRecoveredSameTurn:true,expectSwitchTarget:'enemy',minPowerGain:24,completeOn:'attach',stopAfter:true}\n]);"
if old not in s: raise SystemExit('tutorial step tail anchor not found')
s=s.replace(old,new,1)

old="else if(step.scenario==='namedCard'){p.hand=[makeTutorialNamed('H8','namedCard'),makeTutorialCard('D','2','hold')];p.melds=[makeTutorialMeld('player','SET',[makeTutorialCard('S','8','board','player'),makeTutorialCard('D','8','board','player'),makeTutorialCard('C','8','board','player')])];state.phase='action';log('네임드 카드 실습 · 응급 보호구 8♥는 일반 8♥와 같은 세트 재료이면서, 조합에 들어가면 보호막 20을 추가로 얻습니다.','important')}return true}"
new="else if(step.scenario==='namedCard'){p.hand=[makeTutorialNamed('H8','namedCard'),makeTutorialCard('D','2','hold')];p.melds=[makeTutorialMeld('player','SET',[makeTutorialCard('S','8','board','player'),makeTutorialCard('D','8','board','player'),makeTutorialCard('C','8','board','player')])];state.phase='action';log('네임드 카드 실습 · 응급 보호구 8♥는 일반 8♥와 같은 세트 재료이면서, 조합에 들어가면 보호막 20을 추가로 얻습니다.','important')}else if(step.scenario==='vsEncore'){const encore=makeTutorialNamed('VSH5','vsEncoreCard');p.hand=[makeTutorialCard('D','2','hold')];p.melds=[makeTutorialMeld('player','RUN',[encore,makeTutorialCard('H','6','board','player'),makeTutorialCard('H','7','board','player'),makeTutorialCard('H','8','board','player')],1)];e.melds=[makeTutorialMeld('enemy','SET',[makeTutorialCard('S','5','board','enemy'),makeTutorialCard('D','5','board','enemy'),makeTutorialCard('C','5','board','enemy')])];state.phase='action';log('V-SIGNAL 체험 · 내 ♥ RUN의 앙코르 5♥를 회수한 뒤, 같은 턴 상대 5 세트에 재입장시켜 BURST하세요. 일반 회수 카드의 반환 재사용 제한을 앙코르가 한 번 넘습니다.','important')}return true}"
if old not in s: raise SystemExit('tutorial scenario tail anchor not found')
s=s.replace(old,new,1)

old="if(step.expectAttachTag&&!context.cards?.some(c=>c.tag===step.expectAttachTag))return false;if(step.expectSwitchTarget"
new="if(step.expectAttachTag&&!context.cards?.some(c=>c.tag===step.expectAttachTag))return false;if(step.expectRecoveredSameTurn&&!context.cards?.some(c=>c.recoveredToken===state.turnToken))return false;if(step.expectSwitchTarget"
if old not in s: raise SystemExit('tutorial progress attach guard anchor not found')
s=s.replace(old,new,1)

old="step.id==='namedCard'?`네임드 확인! 8♥의 기본 세트 역할로 버스트를 완성하면서 응급 보호구 고유 효과로 보호막 ${context.afterShield-context.beforeShield}을 추가로 얻었습니다.`:`붙이기 성공! 실제 체인 처리로 누적 위력 ${context.afterPower}이 만들어졌습니다.`"
new="step.id==='namedCard'?`네임드 확인! 8♥의 기본 세트 역할로 버스트를 완성하면서 응급 보호구 고유 효과로 보호막 ${context.afterShield-context.beforeShield}을 추가로 얻었습니다.`:step.id==='vsEncore'?`앙코르 성공! 방금 회수한 V-SIGNAL 5♥를 같은 턴 다른 공개 세트에 재입장시켜 버스트하고 스위치를 상대에게 반환했습니다.`:`붙이기 성공! 실제 체인 처리로 누적 위력 ${context.afterPower}이 만들어졌습니다.`"
if old not in s: raise SystemExit('tutorial success copy anchor not found')
s=s.replace(old,new,1)

old="step.id==='namedCard'?'고급 튜토리얼 완료! 네임드는 기존 랭크·무늬 슬롯의 조합 역할을 유지하면서 고유 효과가 추가되는 변형이라는 점까지 확인했습니다.':'다음 실습은 잠시 후 자동으로 시작됩니다.'"
new="step.id==='namedCard'?'고급 튜토리얼 완료! 네임드는 기존 랭크·무늬 슬롯의 조합 역할을 유지하면서 고유 효과가 추가되는 변형이라는 점까지 확인했습니다.':step.themeId==='v-signal'?'V-SIGNAL 체험 완료! 전용 자원 없이 회수 → 다른 공개 조합 재입장 → BURST로 이어지는 테마의 핵심 연결을 확인했습니다.':'다음 실습은 잠시 후 자동으로 시작됩니다.'"
if old not in s: raise SystemExit('tutorial coach completion copy anchor not found')
s=s.replace(old,new,1)

old='- [ ] V-SIGNAL 등 실제 구현된 테마군 체험전'
new='- [x] V-SIGNAL 등 실제 구현된 테마군 체험전 — 첫 live 테마 체험으로 `앙코르 재입장` 고정 시나리오 추가. 실제 V-SIGNAL 5♥ `앙코르`를 5♥-6♥-7♥-8♥ RUN에서 회수한 뒤 같은 턴 상대의 일반 5♠-5♦-5♣ SET에 붙여 BURST +24 / SWITCH 반환까지 수행한다. `expectRecoveredSameTurn`으로 회수 직후 재사용임을 검증하며, 기본 회수 카드의 반환 재사용 금지와 앙코르의 목적지 제한 1회 예외를 실제 엔진 경로로 체험. `THEME_TUTORIALS.v-signal`을 live로 전환해 기본 튜토리얼 완료 후 시작 화면에서 V-SIGNAL 체험전이 자동 활성화됨'
if old not in r: raise SystemExit('roadmap V-SIGNAL experience anchor not found')
r=r.replace(old,new,1)

old="ok(script.includes(\"const THEME_TUTORIALS=Object.freeze({'v-signal':Object.freeze({themeId:'v-signal',startStep:null,live:false})\"),'theme tutorial registry starts explicit and non-live');"
new="ok(script.includes('const THEME_TUTORIALS=Object.freeze(')&&script.includes(\"'zero-sight':Object.freeze({themeId:'zero-sight',startStep:null,live:false})\")&&script.includes(\"'point-blank':Object.freeze({themeId:'point-blank',startStep:null,live:false})\"),'theme tutorial registry stays explicit while unimplemented themes remain non-live');"
if old not in f: raise SystemExit('foundation regression initial-state anchor not found')
f=f.replace(old,new,1)

index.write_text(s)
road.write_text(r)
foundation.write_text(f)

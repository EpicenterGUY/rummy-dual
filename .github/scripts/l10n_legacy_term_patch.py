from pathlib import Path

index=Path('index.html')
road=Path('ROADMAP.md')
s=index.read_text()
r=road.read_text()

replacements=[
("<title>RUMMY//DUEL - FINAL CORE 2.0</title>","<title>RUMMY//DUEL</title>"),
("<b>SWITCH가 실제로 이동하는 것은 기본 1회</b>","<b>스위치가 실제로 이동하는 것은 기본 1회</b>"),
("<b>같은 RUN</b>","<b>같은 런</b>"),
("추가 연장의 CHAIN 위력은 누적되지만 SWITCH는 다시 이동하지 않습니다.","추가 연장의 체인 위력은 누적되지만 스위치는 다시 이동하지 않습니다."),
("다른 RUN/SET으로 새 반환을 만드는 것은 불가합니다.","다른 런/세트로 새 반환을 만드는 것은 불가합니다."),
("<h3>OVERLOAD · CORE LETHAL</h3>","<h3>과부하 · 코어 파괴 가능</h3>"),
("<b>100+</b>는 OVERLOAD일 뿐 자동 폭발하지 않고","<b>100+</b>는 과부하 표시일 뿐 자동 폭발하지 않고"),
("현재 누적이 SWITCH 대상의 <b>현재 CORE HP + 보호막</b> 이상이면 CORE LETHAL로 표시합니다.","현재 누적이 스위치 대상의 <b>현재 코어 체력 + 보호막</b> 이상이면 코어 파괴 가능으로 표시합니다."),
("이는 전체 게임 즉사가 아니라 현재 CORE 파괴 가능성을 뜻합니다.","이는 전체 게임 즉사가 아니라 현재 코어 파괴 가능성을 뜻합니다."),
("<li>RUN에서 카드가 빠지면 CHAIN -1, 최소 0.</li>","<li>런에서 카드가 빠지면 체인 -1, 최소 0.</li>"),
("자기 턴 시작에 현재 CORE 회복 후 1 감소","자기 턴 시작에 현재 코어 회복 후 1 감소"),
("SET/RUN 전환과 조합 연결 카드가 조금 더 자주 등장하는 경향.","세트/런 전환과 조합 연결 카드가 조금 더 자주 등장하는 경향."),
("모든 RUN은 숫자 한 칸을 한 번 건너뛸 수 있음.","모든 런은 숫자 한 칸을 한 번 건너뛸 수 있음."),
("BURST/CHAIN 반환 재사용 제한은 그대로 적용.","버스트/체인 반환 재사용 제한은 그대로 적용."),
("5장 이상 RUN의 양끝 카드는 상대의 절단·탈취 효과 대상이 되지 않음.","5장 이상 런의 양끝 카드는 상대의 절단·탈취 효과 대상이 되지 않음."),
("모든 RUN은 다른 무늬 카드 1장까지 포함할 수 있다.","모든 런은 다른 무늬 카드 1장까지 포함할 수 있다."),
("CPU는 연습전에서 행동 수가 줄어듭니다.","상대는 연습전에서 행동 수가 줄어듭니다."),
("FINAL CORE 2.0 · CORE 3개 × 60. 폭발 초과 피해는 다음 CORE로 관통하지 않습니다.","코어 3개 × 60 · 폭발 초과 피해는 다음 코어로 관통하지 않습니다."),
("BURST/CHAIN으로 폭탄을 키워 SWITCH를 반환합니다. 100+도 계속 누적되며 유예는 카드 효과로만 가능합니다.","버스트/체인으로 폭탄을 키워 스위치를 반환합니다. 누적 위력은 100 이상도 계속 쌓이며 유예는 카드 효과로만 가능합니다."),
(" · 현재 CORE 실제 피해 ${dealt}."," · 현재 코어 실제 피해 ${dealt}."),
("CPU가 버림패 아래 카드를 확인했습니다.","상대가 버림패 아래 카드를 확인했습니다."),
("절단선: 상대 RUN의 ${cardText(cand)} 소모 · CHAIN -1.","절단선: 상대 런의 ${cardText(cand)} 소모 · 체인 -1."),
("상대 RUN의 내 소유 카드 중 무료 회수할 카드를 고르세요.","상대 런의 내 소유 카드 중 무료 회수할 카드를 고르세요."),
("조건을 만족한 RUN에서 무료 회수할 내 카드를 고르세요.","조건을 만족한 런에서 무료 회수할 내 카드를 고르세요."),
("RUN이 6장 이상입니다. 뽑은 뒤 남은 손패 1장을 덱 아래로 보낼 수 있습니다.","런이 6장 이상입니다. 뽑은 뒤 남은 손패 1장을 덱 아래로 보낼 수 있습니다."),
("이 RUN에서 무료 회수할 내 카드를 고르거나 건너뛸 수 있습니다.","이 런에서 무료 회수할 내 카드를 고르거나 건너뛸 수 있습니다."),
("BURST로 정리되는 SET에서 내가 제어하는 카드 1장을 손패로 보존할 수 있습니다.","버스트로 정리되는 세트에서 내가 제어하는 카드 1장을 손패로 보존할 수 있습니다."),
("완주로 정리되는 RUN에서 내가 제어하는 카드 1장을 손패로 보존할 수 있습니다.","완주로 정리되는 런에서 내가 제어하는 카드 1장을 손패로 보존할 수 있습니다."),
("${w==='player'?'YOU':'CPU'} 정비","${w==='player'?'나':'상대'} 정비"),
("${w==='player'?'YOU':'CPU'} 남은 보호막","${w==='player'?'나':'상대'} 남은 보호막"),
("combatBanner('DETONATE DELAY','rummy',30)","combatBanner('폭발 유예','rummy',30)"),
("과 SWITCH를 유지하고 다음 자기 턴 종료까지 버팁니다.","과 스위치를 유지하고 다음 자기 턴 종료까지 버팁니다."),
("log(`YOU 버리기: ${cardText(c)}${c.named?' ['+c.name+']':''}`)","log(`나 버리기: ${cardText(c)}${c.named?' ['+c.name+']':''}`)"),
("${w==='player'?'YOU':'CPU'} 회수","${w==='player'?'나':'상대'} 회수"),
("${d.name}: CPU가 덱 위로 예약 발송.","${d.name}: 상대가 덱 위로 예약 발송."),
("log(`CPU 버리기: ${cardText(d)}`)","log(`상대 버리기: ${cardText(d)}`)"),
("`CPU가 버림패에서 가져오기: ${cardText(c)}.`","`상대가 버림패에서 가져오기: ${cardText(c)}.`"),
("'CPU가 개인 덱에서 1장 뽑았습니다.'","'상대가 개인 덱에서 1장 뽑았습니다.'"),
]
for old,new in replacements:
    count=s.count(old)
    if count!=1:
        raise SystemExit(f'expected exactly 1 match ({count}): {old}')
    s=s.replace(old,new,1)

old='- [ ] 중복 / 폐기된 옛 용어 제거'
new='- [x] 중복 / 폐기된 옛 용어 제거 — 브라우저 제목·규칙 오버레이·캐릭터/필드 설명·선택창·연습전/전투 로그에서 남아 있던 `FINAL CORE / SET / RUN / BURST / CHAIN / SWITCH / DETONATE DELAY / OVERLOAD / CORE LETHAL / YOU / CPU` 표시를 공식 한국어 표기로 정리. 브랜드 `RUMMY//DUEL`, 테마 고유명과 내부 엔진 키는 유지'
if r.count(old)!=1:
    raise SystemExit(f'ROADMAP legacy terminology anchor count mismatch: {r.count(old)}')
r=r.replace(old,new,1)
index.write_text(s)
road.write_text(r)
print(f'legacy replacements: {len(replacements)}')

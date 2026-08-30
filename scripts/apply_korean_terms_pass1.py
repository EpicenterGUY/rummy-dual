from pathlib import Path


def swap(text, old, new, label, minimum=1):
    count = text.count(old)
    if count < minimum:
        raise SystemExit(f"{label}: expected at least {minimum} match(es), got {count}")
    return text.replace(old, new)

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# Static battle shell: keep brand name, localize player-facing system/UI labels.
static = {
    '<div class="sub">FINAL CORE 2.0 · 3 CORE SWITCH RALLY</div>': '<div class="sub">세트와 런으로 폭탄을 키워 스위치를 넘기는 1:1 러미 배틀</div>',
    '<span>YOU <span id="pCores"': '<span>나 <span id="pCores"',
    '<span id="pHpText" class="coreHpText">CORE 60 / 60</span>': '<span id="pHpText" class="coreHpText">코어 60 / 60</span>',
    '<div class="coreBreakNote">CORE BREAK · 초과 피해 LOST · 다음 CORE 관통 0</div>': '<div class="coreBreakNote">코어 파괴 · 초과 피해 소멸 · 다음 코어 관통 없음</div>',
    '<div class="mid pixel">TURN<b id="turnCount">1</b><span id="turnWho" class="cyan">PLAYER</span></div>': '<div class="mid pixel">턴<b id="turnCount">1</b><span id="turnWho" class="cyan">나</span></div>',
    '<span>CPU <span id="eCores"': '<span>상대 <span id="eCores"',
    '<span id="eHpText" class="coreHpText">CORE 60 / 60</span>': '<span id="eHpText" class="coreHpText">코어 60 / 60</span>',
    '<div class="initiativeSide playerSide"><span>YOU</span></div>': '<div class="initiativeSide playerSide"><span>나</span></div>',
    '<div class="initiativeLabel">SWITCH · 누적 위력</div>': '<div class="initiativeLabel">스위치 · 누적 위력</div>',
    '<div id="switchAlert" class="switchAlert safe">중립 · DETONATE 없음</div>': '<div id="switchAlert" class="switchAlert safe">중립 · 폭발 없음</div>',
    '<div id="switchRule" class="initiativeRule">BURST/CHAIN으로 위력을 더해 상대에게 넘깁니다.</div>': '<div id="switchRule" class="initiativeRule">버스트/체인으로 위력을 더해 상대에게 넘깁니다.</div>',
    '<div class="initiativeSide enemySide"><span>CPU</span></div>': '<div class="initiativeSide enemySide"><span>상대</span></div>',
    '<h2 id="resultTitle">VICTORY</h2>': '<h2 id="resultTitle">승리</h2>',
    '<div class="rulesHead"><h2>규칙 · 용어집 FINAL CORE 2.0</h2>': '<div class="rulesHead"><h2>규칙 · 용어집</h2>',
}
for old, new in static.items():
    s = swap(s, old, new, f'static {old[:32]}')

# Rules/help overlay. These are full user-facing blocks; internal rule identifiers stay unchanged.
rules = {
    '<div class="ruleBlock"><h3>생존 · CORE</h3><p>각 플레이어는 <b>CORE 3개 × 60 HP</b>를 가집니다. DETONATE와 직접 피해는 현재 CORE에 들어가며, CORE를 파괴하고 남은 <b>초과 피해는 다음 CORE로 관통하지 않습니다.</b> 마지막 CORE가 깨지면 패배합니다.</p></div>': '<div class="ruleBlock"><h3>생존 · 코어</h3><p>각 플레이어는 <b>코어 3개 × 60</b>을 가집니다. 폭발과 직접 피해는 현재 코어에 들어가며, 코어를 파괴하고 남은 <b>초과 피해는 다음 코어로 관통하지 않습니다.</b> 마지막 코어가 깨지면 패배합니다.</p></div>',
    '<div class="ruleBlock"><h3>CORE BREAK</h3><p>CORE가 깨지면 다음 CORE가 60/60으로 활성화됩니다. <b>누적 위력 0 · SWITCH 중립 · 모든 RUN CHAIN 0 · 보호막 0</b>으로 폭탄 사이클만 초기화하며 공개 SET/RUN은 그대로 남습니다.</p></div>': '<div class="ruleBlock"><h3>코어 파괴</h3><p>코어가 깨지면 다음 코어가 60/60으로 활성화됩니다. <b>누적 위력 0 · 스위치 중립 · 모든 런 체인 0 · 보호막 0</b>으로 폭탄 사이클만 초기화하며 공개 세트/런은 그대로 남습니다.</p></div>',
    '<div class="ruleBlock"><h3>SET · BURST</h3><p>새 SET은 같은 숫자·서로 다른 무늬 <b>정확히 3장</b>으로 시작해 BURST READY가 됩니다. 이미 공개된 3SET에 마지막 무늬가 들어오면 <b>BURST +24</b>, SWITCH를 상대에게 넘기고 <b>완성된 4SET은 즉시 정리</b>됩니다.</p></div>': '<div class="ruleBlock"><h3>세트 · 버스트</h3><p>새 세트는 같은 숫자·서로 다른 무늬 <b>정확히 3장</b>으로 시작해 버스트 준비 상태가 됩니다. 이미 공개된 3장 세트에 마지막 무늬가 들어오면 <b>버스트 +24</b>, 스위치를 상대에게 넘기고 <b>완성된 4장 세트는 즉시 정리</b>됩니다.</p></div>',
    '<div class="ruleBlock"><h3>RUN · CHAIN</h3><p>새 RUN은 같은 무늬의 연속 3장으로 시작하고 CHAIN 0입니다. 기존 RUN 연장은 <b>+10 → +15 → +20 → +25</b>. 한 행동에서 여러 장을 붙이면 순서대로 모두 계산합니다. A-2-3, Q-K-A 가능 / K-A-2 불가.</p></div>': '<div class="ruleBlock"><h3>런 · 체인</h3><p>새 런은 같은 무늬의 연속 3장으로 시작하고 체인 0입니다. 기존 런 연장은 <b>+10 → +15 → +20 → +25</b>이며 이후에도 +25입니다. <b>체인 4 이상인 내 런은 내 턴에 선택적으로 「런 완주」해 슬롯을 비울 수 있고, 완주하지 않으면 계속 이어갈 수 있습니다.</b> 한 행동에서 여러 장을 붙이면 순서대로 모두 계산합니다. A-2-3, Q-K-A 가능 / K-A-2 불가.</p></div>',
    '<div class="ruleBlock"><h3>공동 전장</h3><p>내 카드는 <b>상대 공개 조합에도</b> 붙일 수 있습니다. 누가 조합을 만들었는지가 아니라 <b>누가 BURST/CHAIN을 발생시켰는지</b>가 반환자를 결정합니다. 이번 턴 자신이 새로 만든 조합에는 같은 턴 다시 붙일 수 없습니다. 각 플레이어의 공개 조합은 <b>최대 2개</b>이며, 기본 행동으로 기존 조합이나 RUN을 자유롭게 정리해 자리를 만들 수 없습니다.</p></div>': '<div class="ruleBlock"><h3>공동 전장</h3><p>내 카드는 <b>상대 공개 조합에도</b> 붙일 수 있습니다. 누가 조합을 만들었는지가 아니라 <b>누가 버스트/체인을 발생시켰는지</b>가 반환자를 결정합니다. 이번 턴 자신이 새로 만든 조합에는 같은 턴 다시 붙일 수 없습니다. 각 플레이어의 공개 조합은 <b>최대 2개</b>입니다. 조합을 자유롭게 버릴 수는 없지만, 체인 4 이상인 런은 제어자가 자기 턴에 <b>런 완주</b>로 정리할 수 있습니다.</p></div>',
    '<div class="ruleBlock"><h3>SWITCH · DETONATE</h3><p>SWITCH가 중립일 때 BURST/CHAIN에 성공하면 폭탄이 시작되어 상대에게 갑니다. SWITCH가 나를 향할 때 BURST/CHAIN에 성공하면 더 키워 상대에게 반환합니다. <b>턴 종료까지 반환하지 않으면 DETONATE.</b> 중립에서 공격하지 못했다고 피해를 받지는 않습니다. 작은 폭탄은 일부러 맞고 초기화할 수도 있습니다.</p></div>': '<div class="ruleBlock"><h3>스위치 · 폭발</h3><p>스위치가 중립일 때 버스트/체인에 성공하면 폭탄이 시작되어 상대에게 갑니다. 스위치가 나를 향할 때 버스트/체인에 성공하면 더 키워 상대에게 반환합니다. <b>턴 종료까지 반환하지 않으면 폭발합니다.</b> 중립에서 공격하지 못했다고 피해를 받지는 않습니다. 작은 폭탄은 일부러 맞고 초기화할 수도 있습니다.</p></div>',
    '<div class="ruleBlock"><h3>RUMMY</h3><p>손패가 0장이 되면 현재 행동과 효과를 모두 해결한 뒤 <b>6장</b>을 새로 받고 자신의 턴이라면 종료합니다. RUMMY 자체에는 기본 피해·위력·SWITCH 이동이 없습니다.</p></div>': '<div class="ruleBlock"><h3>러미</h3><p>손패가 0장이 되면 현재 행동과 효과를 모두 해결한 뒤 <b>6장</b>을 새로 받고 자신의 턴이라면 종료합니다. 러미 자체에는 기본 피해·위력·스위치 이동이 없습니다.</p></div>',
    '<div class="ruleBlock"><h3>유예는 카드 효과</h3><p>기본적으로 SWITCH를 못 돌리면 바로 DETONATE합니다. <b>무료 기본 유예는 없습니다.</b> 대신 안전핀 같은 희귀 네임드가 DETONATE를 다음 자기 턴 종료까지 한 번 미룰 수 있습니다. 한 폭탄 사이클에서 기본적으로 유예는 최대 1회입니다.</p></div>': '<div class="ruleBlock"><h3>유예는 카드 효과</h3><p>기본적으로 스위치를 못 돌리면 바로 폭발합니다. <b>무료 기본 유예는 없습니다.</b> 대신 안전핀 같은 희귀 네임드가 폭발을 다음 자기 턴 종료까지 한 번 미룰 수 있습니다. 한 폭탄 사이클에서 기본적으로 유예는 최대 1회입니다.</p></div>',
    '<div class="ruleBlock"><h3>광대왕 조커</h3><p><b>완전 와일드.</b> SET/RUN에서 필요한 자리를 자동으로 대신합니다. 광대왕 조커가 포함된 공개 조합이 정리될 때 조커는 소모되지 않고 <b>원주인의 덱 맨 아래</b>로 돌아갑니다. 빈자리 조커의 \'실제 카드가 채워지면 즉시 회수\' 역할과 구분됩니다.</p></div>': '<div class="ruleBlock"><h3>광대왕 조커</h3><p><b>완전 와일드.</b> 세트/런에서 필요한 자리를 자동으로 대신합니다. 광대왕 조커가 포함된 공개 조합이 정리될 때 조커는 소모되지 않고 <b>원주인의 덱 맨 아래</b>로 돌아갑니다. 빈자리 조커의 \'실제 카드가 채워지면 즉시 회수\' 역할과 구분됩니다.</p></div>',
    '<div class="ruleBlock"><h3>보호막 · 공식 상태</h3><p>보호막은 현재 CORE 앞에서 피해를 먼저 막는 <b>별도 수치</b>이며 기본 하드캡이 없습니다. 남은 보호막은 자기 턴 시작 시 사라집니다. 공식 상태는 아래 5종만 공용 규칙으로 사용하며 카드 고유 표식은 별도입니다.</p><div class="statusLegend"><span>취약 · 플레이어 · 다음 DETONATE +25% 후 해제</span>': '<div class="ruleBlock"><h3>보호막 · 공식 상태</h3><p>보호막은 현재 코어 앞에서 피해를 먼저 막는 <b>별도 수치</b>이며 기본 하드캡이 없습니다. 남은 보호막은 자기 턴 시작 시 사라집니다. 공식 상태는 아래 5종만 공용 규칙으로 사용하며 카드 고유 표식은 별도입니다.</p><div class="statusLegend"><span>취약 · 플레이어 · 다음 폭발 +25% 후 해제</span>',
    '<div class="ruleBlock"><h3>카드 설계 원칙</h3><p><b>기본은 럼미, 미친 짓은 카드가 한다.</b> 카드풀 대부분은 조합 변형·회수·이동·버림패·순환·상태·RUMMY를 연결하며, 누적 위력 자체를 직접 +X/-X 하는 카드는 소수로 유지합니다.</p></div>': '<div class="ruleBlock"><h3>카드 설계 원칙</h3><p><b>기본은 러미, 미친 짓은 카드가 한다.</b> 카드풀 대부분은 조합 변형·회수·이동·버림패·순환·상태·러미를 연결하며, 누적 위력 자체를 직접 +X/-X 하는 카드는 소수로 유지합니다.</p></div>',
}
for old, new in rules.items():
    s = swap(s, old, new, f'rule block {old[24:56]}')

old_glossary = '<div class="ruleBlock"><h3>용어집</h3><div class="glossary"><div class="term">CORE</div><div>현재 피해를 받는 생명 층. 3개 × 60.</div><div class="term">CORE BREAK</div><div>현재 CORE 파괴. 초과 피해는 관통하지 않으며 폭탄 사이클을 초기화.</div><div class="term">SWITCH</div><div>현재 누적 폭탄을 받아쳐야 하는 플레이어.</div><div class="term">DETONATE</div><div>SWITCH를 가진 채 턴을 끝냈을 때 현재 CORE가 받는 폭발.</div><div class="term">OVERLOAD</div><div>누적 100+ 위험도 표시. 상한/자동 폭발이 아님.</div><div class="term">CORE LETHAL</div><div>현재 누적이 대상의 현재 CORE HP+보호막 이상인 상태.</div><div class="term">BURST</div><div>기존 3SET의 마지막 무늬 완성. 기본 +24 후 4SET 정리.</div><div class="term">CHAIN</div><div>기존 RUN을 연장할수록 10/15/20/25로 상승.</div><div class="term">정비</div><div>평소 1장 교환, 완전 막힘이면 최대 2장 교환.</div><div class="term">유예</div><div>일부 카드가 한 폭탄 사이클에 한 번 DETONATE를 한 턴 미루는 특수 효과.</div></div></div>'
new_glossary = '<div class="ruleBlock"><h3>용어집</h3><div class="glossary"><div class="term">세트</div><div>같은 숫자·서로 다른 무늬의 조합.</div><div class="term">런</div><div>같은 무늬의 연속 숫자 조합.</div><div class="term">붙이기</div><div>조건이 맞는 카드를 이미 공개된 조합에 추가하는 행동.</div><div class="term">스위치</div><div>현재 누적 위력의 폭발 위험이 누구를 향하는지 나타내는 고유 시스템.</div><div class="term">러미</div><div>손패를 모두 사용했을 때 새 손패를 받는 처리.</div><div class="term">폭발</div><div>스위치가 자신을 향한 채 턴을 끝냈을 때 누적 위력이 현재 코어에 피해로 적용되는 처리.</div><div class="term">과부하</div><div>누적 위력 100+ 위험도 표시. 상한이나 자동 폭발은 아님.</div><div class="term">코어</div><div>현재 피해를 받는 생명 층. 3개 × 60.</div><div class="term">코어 파괴</div><div>현재 코어 파괴. 초과 피해는 관통하지 않으며 폭탄 사이클을 초기화.</div><div class="term">코어 파괴 가능</div><div>현재 누적 위력이 대상의 현재 코어+보호막 이상인 상태.</div><div class="term">버스트</div><div>기존 3장 세트의 마지막 무늬 완성. 기본 +24 후 4장 세트 정리.</div><div class="term">체인</div><div>기존 런을 연장할수록 10/15/20/25로 상승하며 이후 +25.</div><div class="term">런 완주</div><div>체인 4 이상인 런을 제어자가 자기 턴에 선택적으로 정리해 슬롯을 비우는 행동.</div><div class="term">정비</div><div>평소 1장 교환, 완전 막힘이면 최대 2장 교환.</div><div class="term">유예</div><div>일부 카드가 한 폭탄 사이클에 한 번 폭발을 한 턴 미루는 특수 효과.</div></div></div>'
s = swap(s, old_glossary, new_glossary, 'official glossary')

# Dynamic feedback and battle UI.
repls = [
    ("function switchName(w){return w==='player'?'YOU':'CPU'}", "function switchName(w){return w==='player'?'나':'상대'}", 'side display labels'),
    ("log(`${reason} · 모든 공개 RUN CHAIN 0.`", "log(`${reason} · 모든 공개 런 체인 0.`", 'chain reset log'),
    ("combatBanner('CORE BREAK','break',130)", "combatBanner('코어 파괴','break',130)", 'core break banner'),
    ("`${switchName(w)} CORE BREAK · ${s.cores} CORE 남음.${overkill>0?` OVERKILL ${overkill} LOST · NO PIERCE.`:''}`", "`${switchName(w)} 코어 파괴 · ${s.cores}코어 남음.${overkill>0?` 초과 피해 ${overkill} 소멸 · 관통 없음.`:''}`", 'core break log'),
    ("`OVERKILL ${overkill} LOST · NO PIERCE`", "`초과 피해 ${overkill} 소멸 · 관통 없음`", 'overkill fx'),
    ("`${overkill} LOST · NO PIERCE`", "`${overkill} 소멸 · 관통 없음`", 'overkill banner'),
    ("resetBombCycle('CORE BREAK',true)", "resetBombCycle('코어 파괴',true)", 'core break reset reason'),
    ("`NEXT CORE ${s.hp}/${s.maxHp}`", "`다음 코어 ${s.hp}/${s.maxHp}`", 'next core fx'),
    ("combatBanner('FUSE HELD','rummy',40)", "combatBanner('유예 준비','rummy',40)", 'grace banner'),
    (" · DETONATE를 다음 자기 턴 종료까지 유예.", " · 폭발을 다음 자기 턴 종료까지 유예.", 'grace log'),
    ("function addSwitchPower(w,amount,label='POWER'", "function addSwitchPower(w,amount,label='위력'", 'power default label'),
    ("fxNode(`POWER +${amount}`", "fxNode(`위력 +${amount}`", 'power fx'),
    ("combatBanner(`OVERLOAD ${state.switchPower}`", "combatBanner(`과부하 ${state.switchPower}`", 'overload banner'),
    ("combatBanner(`CORE LETHAL ${state.switchPower}`", "combatBanner(`코어 파괴 가능 ${state.switchPower}`", 'lethal banner'),
    ("log(`SWITCH → ${switchName(target)} · ${reason}.`", "log(`스위치 → ${switchName(target)} · ${reason}.`", 'switch target log'),
    ("combatBanner(`SWITCH → ${switchName(target)}`", "combatBanner(`스위치 → ${switchName(target)}`", 'switch target banner'),
    ("function returnSwitch(w,amount,label='RETURN'", "function returnSwitch(w,amount,label='반환'", 'return default label'),
    ("는 현재 SWITCH 대상이 아니므로", "는 현재 스위치 대상이 아니므로", 'switch ownership message'),
    ("반환 제한 · 한 턴에 SWITCH는 1회만", "반환 제한 · 한 턴에 스위치는 1회만", 'switch limit message'),
    ("fxNode(`POWER -${got}`", "fxNode(`위력 -${got}`", 'power reduction fx'),
    ("다음 DETONATE +25%", "다음 폭발 +25%", 'vulnerable detonate'),
    ("DETONATE 피해 -${cut}", "폭발 피해 -${cut}", 'last laugh reduction log'),
    ("`DETONATE -${cut}`", "`폭발 -${cut}`", 'last laugh reduction fx'),
    ("combatBanner(`DETONATE ${total}`", "combatBanner(`폭발 ${total}`", 'detonate banner'),
    ("{label:'DETONATE',detonate:true}", "{label:'폭발',detonate:true}", 'detonate damage label'),
    ("resetBombCycle('DETONATE',false)", "resetBombCycle('폭발',false)", 'detonate reset label'),
    ("h.label||'CHAIN'", "h.label||'체인'", 'attack fallback label'),
    ("`NAMED +${bonus}`", "`네임드 +${bonus}`", 'named bonus fx'),
    ("`${w==='player'?'YOU':'CPU'} 현재 CORE +${got}`", "`${w==='player'?'나':'상대'} 현재 코어 +${got}`", 'heal log'),
    ("`+${got} CORE`", "`+${got} 코어`", 'heal fx'),
    ("`${w==='player'?'YOU':'CPU'} 보호막 +${got}", "`${w==='player'?'나':'상대'} 보호막 +${got}", 'shield log'),
    ("`${w==='player'?'YOU':'CPU'} 보호막이 ${blocked} 피해 흡수.`", "`${w==='player'?'나':'상대'} 보호막이 ${blocked} 피해 흡수.`", 'block log'),
    ("`BLOCK ${blocked}`", "`방어 ${blocked}`", 'block fx'),
    ("combatBanner('SHIELD BREAK'", "combatBanner('보호막 파괴'", 'shield break banner'),
    ("`${w==='player'?'YOU':'CPU'} 현재 CORE ${dealt} 피해", "`${w==='player'?'나':'상대'} 현재 코어 ${dealt} 피해", 'damage log'),
    ("`-${dealt} CORE`", "`-${dealt} 코어`", 'damage fx'),
    ("log(`${w==='player'?'YOU':'CPU'} ${type} 3장 구축 · ${type==='SET'?'BURST READY':'CHAIN 0'}.`", "log(`${w==='player'?'나':'상대'} ${type==='SET'?'세트':'런'} 3장 구축 · ${type==='SET'?'버스트 준비':'체인 0'}.`", 'new meld log'),
    ("회수한 카드는 같은 턴 BURST/CHAIN으로 SWITCH를 반환하는 데", "회수한 카드는 같은 턴 버스트/체인으로 스위치를 반환하는 데", 'recover return warning'),
    ("label='SET BURST'", "label='세트 버스트'", 'set attack label'),
    ("label=`RUN CHAIN ${m.chain}`", "label=`런 체인 ${m.chain}`", 'run attack label'),
    ("`${w==='player'?'YOU':'CPU'} ${targetSide===w?'내':'상대'} ${type}에 ${cards.length}장 붙이기${returning?' · SWITCH 반환':' · 구조 변경'}.`", "`${w==='player'?'나':'상대'} ${targetSide===w?'내':'상대'} ${type==='SET'?'세트':'런'}에 ${cards.length}장 붙이기${returning?' · 스위치 반환':' · 구조 변경'}.`", 'attach log'),
    ("'BURST 후 4SET 자동 정리'", "'버스트 후 4장 세트 자동 정리'", 'burst retire reason'),
    ("log(`YOU 회수 ·", "log(`나 회수 ·", 'recover log'),
    ("' · CHAIN -1'", "' · 체인 -1'", 'recover chain text'),
    ("반환 RUMMY 후", "반환 러미 후", 'last laugh rummy log'),
    ("이번 턴 DETONATE 피해 15 감소 준비", "이번 턴 폭발 피해 15 감소 준비", 'last laugh detonate log'),
    ("combatBanner('RUMMY!'", "combatBanner('러미!'", 'rummy banner'),
    ("`${w==='player'?'YOU':'CPU'} RUMMY! 새 손패 ${reload}장.`", "`${w==='player'?'나':'상대'} 러미! 새 손패 ${reload}장.`", 'rummy log'),
    ("return`${p.type==='SET'?'BURST':'CHAIN'} ${seq} · TOTAL +${p.total} · SWITCH → CPU`", "return`${p.type==='SET'?'버스트':'체인'} ${seq} · 합계 +${p.total} · 스위치 → 상대`", 'attach preview'),
    ("새 조합은 정확히 3장 SET/RUN으로 시작합니다.", "새 조합은 정확히 3장 세트/런으로 시작합니다.", 'new meld error'),
    ("이번 턴 회수한 카드는 BURST/CHAIN 반환에 재사용 불가", "이번 턴 회수한 카드는 버스트/체인 반환에 재사용 불가", 'attach reason recover'),
    ("SWITCH가 상대에게 있음 · 이번 턴 공격 반환 불가", "스위치가 상대에게 있음 · 이번 턴 공격 반환 불가", 'attach reason switch'),
    ("이번 턴 SWITCH 반환 사용함", "이번 턴 스위치 반환 사용함", 'attach reason spent'),
    ("return'SET 최대 4장'", "return'세트 최대 4장'", 'set max reason'),
    ("return'RUN 양끝과 이어져야 함'", "return'런 양끝과 이어져야 함'", 'run edge reason'),
    ("'<div class=\"attackReadout burst\">BURST READY · 4번째 카드 +24 · SWITCH 반환</div>'", "'<div class=\"attackReadout burst\">버스트 준비 · 4번째 카드 +24 · 스위치 반환</div>'", 'set readout'),
    ("`<div class=\"attackReadout chain\">CHAIN ${m.chain||0} · NEXT +${chainDamage((m.chain||0)+1)} · SWITCH 반환${(m.chain||0)>=4?' · 런 완주 가능':''}</div>`", "`<div class=\"attackReadout chain\">체인 ${m.chain||0} · 다음 +${chainDamage((m.chain||0)+1)} · 스위치 반환${(m.chain||0)>=4?' · 런 완주 가능':''}</div>`", 'run readout'),
    ("${side==='enemy'?'CPU':'YOU'} · ${m.type} ·", "${side==='enemy'?'상대':'나'} · ${m.type==='SET'?'세트':'런'} ·", 'meld header'),
    ("` · TOTAL +${preview.total}`", "` · 합계 +${preview.total}`", 'attach button total'),
    ("${state.target.side==='enemy'?'CPU':'YOU'} ${tm.type} 타겟", "${state.target.side==='enemy'?'상대':'나'} ${tm.type==='SET'?'세트':'런'} 타겟", 'target preview label'),
    ("${state.target.side==='enemy'?'CPU':'YOU'} ${tm.type} 타겟 선택", "${state.target.side==='enemy'?'상대':'나'} ${tm.type==='SET'?'세트':'런'} 타겟 선택", 'target selected label'),
    ("이번 턴 SWITCH 반환 완료.", "이번 턴 스위치 반환 완료.", 'target hint switch'),
    ("추가 BURST/CHAIN 반환은 불가.", "추가 버스트/체인 반환은 불가.", 'target hint burst chain'),
    ("공개 RUN을 먼저 눌러", "공개 런을 먼저 눌러", 'target hint run'),
    ("`${t} 3장 새 조합`", "`${t==='SET'?'세트':'런'} 3장 새 조합`", 'selection strip meld'),
    ("${state.target.side==='enemy'?'CPU':'YOU'} ${tm.type}</span>", "${state.target.side==='enemy'?'상대':'나'} ${tm.type==='SET'?'세트':'런'}</span>", 'selection strip target'),
    ("SET = 같은 숫자/서로 다른 무늬 · RUN = 같은 무늬 연속 3장.", "세트 = 같은 숫자/서로 다른 무늬 · 런 = 같은 무늬 연속 3장.", 'detail help'),
    ("c.owner==='player'?'YOU':'CPU'", "c.owner==='player'?'나':'상대'", 'detail controller'),
    ("c.originOwner==='player'?'YOU':'CPU'", "c.originOwner==='player'?'나':'상대'", 'detail original owner'),
    ("meldText='SET 3장 구축 · BURST READY'", "meldText='세트 3장 구축 · 버스트 준비'", 'meld button set'),
    ("meldText='RUN 3장 구축 · CHAIN 0'", "meldText='런 3장 구축 · 체인 0'", 'meld button run'),
    ("`붙이기 · TOTAL +${preview.total} · SWITCH→CPU`", "`붙이기 · 합계 +${preview.total} · 스위치→상대`", 'attach button preview'),
    ("`붙이기 · TOTAL +${p.total} · SWITCH→CPU`", "`붙이기 · 합계 +${p.total} · 스위치→상대`", 'single attach preview'),
    ("win?'VICTORY':'DEFEAT'", "win?'승리':'패배'", 'result title'),
    ("CPU의 마지막 CORE를 파괴했습니다.", "상대의 마지막 코어를 파괴했습니다.", 'victory copy'),
    (" · RUMMY ${state.rummy}회.", " · 러미 ${state.rummy}회.", 'victory rummy count'),
    ("<b>NEW UNLOCK</b>", "<b>새 해금</b>", 'unlock title'),
    ("CPU가 내 마지막 CORE를 먼저 파괴했습니다.", "상대가 내 마지막 코어를 먼저 파괴했습니다.", 'defeat copy'),
    ("hit.owner==='player'?'YOU':'CPU'", "hit.owner==='player'?'나':'상대'", 'death sentence owner'),
    ("const slotText=isJ?'JOKER':", "const slotText=isJ?'조커':", 'codex joker label'),
    ("<div class=\"codexFieldIcon\">FIELD</div>", "<div class=\"codexFieldIcon\">필드</div>", 'codex field label'),
    ("state.switchPower>=100?'OVERLOAD':'',isLethal?'CORE LETHAL':''", "state.switchPower>=100?'과부하':'',isLethal?'코어 파괴 가능':''", 'initiative tier'),
    ("state.switchPower>=70?'CRITICAL':state.switchPower>=40?'DANGER':'')", "state.switchPower>=70?'고위험':state.switchPower>=40?'주의':'')", 'initiative danger tier'),
    ("`${targetKey==='player'?'YOU':'CPU'} ← SWITCH ${state.switchPower}", "`${targetKey==='player'?'나':'상대'} ← 스위치 ${state.switchPower}", 'initiative target text'),
    ("alert.textContent='중립 · DETONATE 없음'", "alert.textContent='중립 · 폭발 없음'", 'neutral alert'),
    ("`⚠ 내 턴 종료 시 DETONATE ${state.switchPower} · 반환 필요`", "`⚠ 내 턴 종료 시 폭발 ${state.switchPower} · 반환 필요`", 'player detonate alert'),
    ("`CPU 턴 종료 시 DETONATE ${state.switchPower}`", "`상대 턴 종료 시 폭발 ${state.switchPower}`", 'enemy detonate alert'),
    ("`⚠ SWITCH → YOU · 다음 내 턴 종료 전 반환 준비`", "`⚠ 스위치 → 나 · 다음 내 턴 종료 전 반환 준비`", 'incoming alert'),
    ("`SWITCH → CPU · CPU가 다음 반환/DETONATE 대상`", "`스위치 → 상대 · 상대가 다음 반환/폭발 대상`", 'enemy target alert'),
    ("rule.textContent='BURST/CHAIN으로 폭탄을 시작하세요.'", "rule.textContent='버스트/체인으로 폭탄을 시작하세요.'", 'neutral switch rule'),
    ("`CORE LETHAL · ${over} 초과`", "`코어 파괴 가능 · ${over} 초과`", 'lethal margin'),
    ("`CORE까지 ${deficit}`", "`코어까지 ${deficit}`", 'core deficit'),
    ("` · SHIELD ${target.shield}`", "` · 보호막 ${target.shield}`", 'shield readout'),
    ("`현재 CORE ${target.hp}/${target.maxHp}", "`현재 코어 ${target.hp}/${target.maxHp}", 'current core readout'),
    ("btn.textContent=isLethal?'CORE LETHAL':targetTurn?`DETONATE ${state.switchPower}`:state.switchPower>=100?'OVERLOAD'", "btn.textContent=isLethal?'코어 파괴 가능':targetTurn?`폭발 ${state.switchPower}`:state.switchPower>=100?'과부하'", 'initiative button'),
    ("`CORE ${p.hp} / ${p.maxHp}`", "`코어 ${p.hp} / ${p.maxHp}`", 'player core hp'),
    ("`CORE ${e.hp} / ${e.maxHp}`", "`코어 ${e.hp} / ${e.maxHp}`", 'enemy core hp'),
    ("state.turn==='player'?'PLAYER':'CPU'", "state.turn==='player'?'나':'상대'", 'turn owner'),
    ("phase='CPU가 생각 중...'", "phase='상대가 생각 중...'", 'enemy thinking'),
    ("phase='내 턴 · SWITCH 반환 1회 완료.", "phase='내 턴 · 스위치 반환 1회 완료.", 'phase return done'),
    ("phase=`내 턴 · SWITCH ${state.switchPower}. 반환하지 못하면 현재 CORE에 DETONATE", "phase=`내 턴 · 스위치 ${state.switchPower}. 반환하지 못하면 현재 코어에 폭발", 'phase detonate'),
    ("phase=`내 턴 · SWITCH는 CPU가 보유 중.", "phase=`내 턴 · 스위치는 상대가 보유 중.", 'phase enemy switch'),
]
for old, new, label in repls:
    s = swap(s, old, new, label)

# Rule UI recovery line and a few high-frequency remaining copy fragments.
s = s.replace('회수한 카드는 같은 턴 BURST/CHAIN 반환 재료로 다시 사용할 수 없습니다', '회수한 카드는 같은 턴 버스트/체인 반환 재료로 다시 사용할 수 없습니다')
s = s.replace('RUMMY', '러미') if False else s  # brand/internal identifiers intentionally untouched

p.write_text(s, encoding='utf-8')

# Update tests whose contract is explicitly the player-visible wording.
p = Path('tests/combat-readability.mjs')
s = p.read_text(encoding='utf-8')
for old, new in [
    ("내 턴 종료 시 DETONATE", "내 턴 종료 시 폭발"),
    ("CPU 턴 종료 시 DETONATE", "상대 턴 종료 시 폭발"),
    ("CORE까지", "코어까지"),
    ("BURST READY · 4번째 카드 +24 · SWITCH 반환", "버스트 준비 · 4번째 카드 +24 · 스위치 반환"),
    (" · NEXT +${chainDamage((m.chain||0)+1)} · SWITCH 반환", " · 다음 +${chainDamage((m.chain||0)+1)} · 스위치 반환"),
    ("OVERKILL ${overkill} LOST · NO PIERCE", "초과 피해 ${overkill} 소멸 · 관통 없음"),
    ("초과 피해 LOST · 다음 CORE 관통 0", "초과 피해 소멸 · 다음 코어 관통 없음"),
]:
    s = swap(s, old, new, f'combat test {old}')
p.write_text(s, encoding='utf-8')

p = Path('tests/multiattach-ux.mjs')
s = p.read_text(encoding='utf-8')
s = swap(s, "ok(html.includes('SWITCH → CPU'), 'multi-attach preview explicitly shows the resulting SWITCH direction');", "ok(html.includes('스위치 → 상대'), 'multi-attach preview explicitly shows the resulting SWITCH direction');", 'multiattach switch test')
s = swap(s, "ok(html.includes('TOTAL +${p.total}'), 'multi-attach preview renders an aggregate total');", "ok(html.includes('합계 +${p.total}'), 'multi-attach preview renders an aggregate total');", 'multiattach total test')
p.write_text(s, encoding='utf-8')

p = Path('tests/rules-smoke.mjs')
s = p.read_text(encoding='utf-8')
s = swap(s, "ok(html.includes('회수한 카드는 같은 턴 BURST/CHAIN 반환 재료로 다시 사용할 수 없습니다'), 'rules UI documents the recovery return guard');", "ok(html.includes('회수한 카드는 같은 턴 버스트/체인 반환 재료로 다시 사용할 수 없습니다'), 'rules UI documents the recovery return guard');", 'rules smoke recovery copy')
p.write_text(s, encoding='utf-8')

p = Path('ROADMAP.md')
s = p.read_text(encoding='utf-8')
for old, new, label in [
    ("- [ ] 일반 UI 용어 한국어화 (`YOU/PLAYER/CPU/NEXT/TOTAL` 등)", "- [x] 일반 UI 용어 한국어화 1차 (`YOU/PLAYER/CPU/NEXT/TOTAL` 등 전투 핵심 노출 제거)", 'roadmap general UI'),
    ("- [ ] 전투 배너/경고 문구 한국어화 (`CORE BREAK`, `DETONATE`, `OVERLOAD`, `NO PIERCE` 등)", "- [x] 전투 배너/경고 문구 한국어화 1차 (`코어 파괴`, `폭발`, `과부하`, `관통 없음`)", 'roadmap combat UI'),
    ("- [ ] 도움말 / 규칙 설명 용어 반영", "- [x] 도움말 / 규칙 설명 핵심 용어 반영 + `런 완주` 규칙 동기화", 'roadmap rules help'),
    ("- [ ] 기존 규칙 오버레이의 공식 용어집 갱신", "- [x] 기존 규칙 오버레이의 공식 용어집 갱신", 'roadmap glossary'),
    ("- [ ] 사용자 노출 문자열 회귀 테스트 추가", "- [x] 사용자 노출 문자열 회귀 테스트 추가", 'roadmap string test'),
]:
    s = swap(s, old, new, label)
p.write_text(s, encoding='utf-8')

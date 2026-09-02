from pathlib import Path
import runpy

runpy.run_path('.github/scripts/zero-sight-full-pool-patch-v2.py', run_name='__main__')

index=Path('index.html')
text=index.read_text(encoding='utf-8')
repls={
"'ZSS7':{slot:'S7',themeId:'zero-sight',rewardPool:false,n:'철갑탄',t:'zsArmorPiercing',d:'내 상대 표적 조합에 붙여 스위치를 반환하면 누적 위력 +10. 그 조합의 보호 1을 제거할 수 있었다면 대신 +14.'},":"'ZSS7':{slot:'S7',themeId:'zero-sight',rewardPool:false,n:'철갑탄',t:'zsArmorPiercing',d:'내 상대 표적 조합에 붙여 스위치를 반환하면 누적 위력이 10 증가한다. 그 조합의 보호 1을 제거할 수 있었다면 대신 누적 위력이 14 증가한다.'},",
"'ZSS10':{slot:'S10',themeId:'zero-sight',rewardPool:false,prepRequired:2,n:'장거리 사격',t:'zsLongShot',d:'손에서 내 턴 종료 2회를 준비한 뒤 내 표적 조합을 이용해 스위치를 반환하면 누적 위력 +16.'},":"'ZSS10':{slot:'S10',themeId:'zero-sight',rewardPool:false,prepRequired:2,n:'장거리 사격',t:'zsLongShot',d:'손에서 내 턴 종료 2회를 준비한 뒤 내 표적 조합을 이용해 스위치를 반환하면 누적 위력이 16 증가한다.'},",
"'ZSSQ':{slot:'SQ',themeId:'zero-sight',rewardPool:false,n:'데드 앵글',t:'zsDeadAngle',d:'이 카드가 내 표적에 있는 동안 상대가 그 표적에서 카드를 회수하거나 밖으로 이동시키면 상대에게 취약 1을 주고 남은 내 카드 1장에 보호 1을 부여한다. 턴당 1회.'},":"'ZSSQ':{slot:'SQ',themeId:'zero-sight',rewardPool:false,n:'데드 앵글',t:'zsDeadAngle',d:'이 카드가 내 표적에 있는 동안 상대가 그 표적에서 카드를 회수하거나 밖으로 이동시키면 상대에게 취약 1을 주고 남은 내 카드 1장에 보호 1을 부여한다. 이 효과는 턴당 1회만 발동한다.'},",
"'ZSC6':{slot:'C6',themeId:'zero-sight',rewardPool:false,n:'관측 기록',t:'zsObservationLog',d:'이 카드가 있는 내 표적을 다음 턴까지 유지한 뒤 그 표적에 내가 처음 붙이면 남은 손패 1장을 무료 정비한다. 턴당 1회.'},":"'ZSC6':{slot:'C6',themeId:'zero-sight',rewardPool:false,n:'관측 기록',t:'zsObservationLog',d:'이 카드가 있는 내 표적을 다음 턴까지 유지한 뒤 그 표적에 내가 처음 붙이면 남은 손패 1장을 무료 정비한다. 이 효과는 턴당 1회만 발동한다.'},",
}
for old,new in repls.items():
    if old in text:
        text=text.replace(old,new,1)
    elif new not in text:
        raise SystemExit(f'missing card text anchor: {old[:40]}')
index.write_text(text,encoding='utf-8')

# Keep canonical wording aligned with the live card text.
theme=Path('docs/THEME_GROUPS.md')
t=theme.read_text(encoding='utf-8')
doc_repls={
"- 6♣ `관측 기록` — 이 카드가 있는 표적을 다음 턴까지 유지한 뒤 처음 붙이면 턴당 1회 무료 정비.":"- 6♣ `관측 기록` — 이 카드가 있는 표적을 다음 턴까지 유지한 뒤 처음 붙이면 무료 정비한다. 이 효과는 턴당 1회만 발동한다.",
"- 7♠ `철갑탄` — 상대 표적 반환 +10, 그 조합의 보호 1을 제거하면 대신 +14.":"- 7♠ `철갑탄` — 상대 표적을 이용해 반환하면 누적 위력이 10 증가한다. 그 조합의 보호 1을 제거하면 대신 14 증가한다.",
"- 10♠ `장거리 사격` — 손에서 2턴 준비 후 내 표적 반환 +16.":"- 10♠ `장거리 사격` — 손에서 2턴 준비 후 내 표적을 이용해 반환하면 누적 위력이 16 증가한다.",
"- Q♠ `데드 앵글` — 이 카드가 내 표적에 있는 동안 상대가 그 표적에서 회수/이동하면 턴당 1회 상대 취약 1 + 남은 내 카드 보호 1.":"- Q♠ `데드 앵글` — 이 카드가 내 표적에 있는 동안 상대가 그 표적에서 회수/이동하면 상대에게 취약 1을 주고 남은 내 카드 1장에 보호 1을 부여한다. 이 효과는 턴당 1회만 발동한다.",
}
for old,new in doc_repls.items():
    if old in t:
        t=t.replace(old,new,1)
theme.write_text(t,encoding='utf-8')

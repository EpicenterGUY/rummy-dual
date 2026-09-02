from pathlib import Path
import runpy

runpy.run_path('.github/scripts/zero-sight-full-pool-patch-v3.py', run_name='__main__')

index=Path('index.html')
text=index.read_text(encoding='utf-8')
old="'ZSS9':{slot:'S9',themeId:'zero-sight',rewardPool:false,n:'역추적',t:'zsCounterTrace',d:'이 카드가 공개된 동안 상대가 내 표적 조합으로 스위치를 반환하면 충전한다. 공개 상태를 유지한 채 내가 다음 스위치를 반환하면 누적 위력 +12 후 충전을 해제한다.'},"
new="'ZSS9':{slot:'S9',themeId:'zero-sight',rewardPool:false,n:'역추적',t:'zsCounterTrace',d:'이 카드가 공개된 동안 상대가 내 표적 조합으로 스위치를 반환하면 충전한다. 공개 상태를 유지한 채 내가 다음 스위치를 반환하면 누적 위력이 12 증가하고 충전을 해제한다.'},"
if old in text:
    text=text.replace(old,new,1)
elif new not in text:
    raise SystemExit('missing Counter Trace card-text anchor')
index.write_text(text,encoding='utf-8')

theme=Path('docs/THEME_GROUPS.md')
t=theme.read_text(encoding='utf-8')
old="- 9♠ `역추적` — 공개된 동안 상대가 내 표적으로 반환하면 충전, 공개 상태의 내 다음 반환 +12 후 해제."
new="- 9♠ `역추적` — 공개된 동안 상대가 내 표적으로 반환하면 충전한다. 공개 상태의 내 다음 반환에서 누적 위력이 12 증가한 뒤 충전을 해제한다."
if old in t:
    t=t.replace(old,new,1)
theme.write_text(t,encoding='utf-8')

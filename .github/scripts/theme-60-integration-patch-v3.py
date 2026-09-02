from pathlib import Path
src=Path('.github/scripts/theme-60-integration-patch-v2.py').read_text(encoding='utf-8')
exec(compile(src,'theme-60-integration-patch-v3-base','exec'))
p=Path('index.html')
s=p.read_text(encoding='utf-8')
old="step.themeId?`${themeDef(step.themeId)?.displayName||step.themeId} 체험 완료! ${step.themeId==='v-signal'?'회수 → 재입장 연결':step.themeId==='zero-sight'?'표적 지정 → 정밀 효과 연결':'접전 지정 → 돌입·회수 연결'}의 핵심을 확인했습니다.`:'다음 실습은 잠시 후 자동으로 시작됩니다.'"
new="step.themeId==='v-signal'?'V-SIGNAL 체험 완료! 전용 자원 없이 회수 → 다른 공개 조합 재입장 → 버스트로 이어지는 테마의 핵심 연결을 확인했습니다.':step.themeId==='zero-sight'?'ZERO-SIGHT 체험 완료! 표적 지정 → 정밀 효과 연결의 핵심을 확인했습니다.':step.themeId==='point-blank'?'POINT-BLANK 체험 완료! 접전 지정 → 돌입·회수 연결의 핵심을 확인했습니다.':'다음 실습은 잠시 후 자동으로 시작됩니다.'"
if new not in s:
    if old not in s: raise SystemExit('missing generic theme completion copy')
    s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')
print('theme 60-card integration v3 copy compatibility applied')

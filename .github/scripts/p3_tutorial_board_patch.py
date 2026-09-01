from pathlib import Path

index=Path('index.html')
road=Path('ROADMAP.md')
s=index.read_text()
r=road.read_text()

marker='/* UI3 P3 · tutorial tactical-board finish */'
anchor='</style>'
old_rule='.tutorialCoach{position:relative;border:1px solid #56666a!important;border-left:4px solid #6f9690!important;border-radius:10px;background:#263238!important;box-shadow:0 7px 20px #0003,0 1px 0 #ffffff08 inset!important;color:#e8ece8}'
new_rule='.tutorialCoach{border:1px solid #56666a!important;border-left:4px solid #6f9690!important;border-radius:10px;background:#263238!important;box-shadow:0 7px 20px #0003,0 1px 0 #ffffff08 inset!important;color:#e8ece8}'

if marker in s:
    if s.count(old_rule)!=1:
        raise SystemExit(f'P3 tutorial desktop-position correction mismatch: {s.count(old_rule)}')
    s=s.replace(old_rule,new_rule,1)
else:
    if s.count(anchor)!=1:
        raise SystemExit(f'style closing tag mismatch: {s.count(anchor)}')
    block=r'''

/* UI3 P3 · tutorial tactical-board finish */
.tutorialCoach{border:1px solid #56666a!important;border-left:4px solid #6f9690!important;border-radius:10px;background:#263238!important;box-shadow:0 7px 20px #0003,0 1px 0 #ffffff08 inset!important;color:#e8ece8}
.tutorialCoach:before{content:"";position:absolute;left:0;top:10px;bottom:10px;width:2px;background:#90b9b355;pointer-events:none}
.tutorialCoachHead{padding-bottom:6px;border-bottom:1px solid #445258;margin-bottom:7px}.tutorialCoachHead .badge{border:1px solid #5d7774;border-radius:999px;background:#31423f;box-shadow:none;color:#cfe1dc}.tutorialCoachHead b{color:#eef0ea!important;letter-spacing:-.02em}
.tutorialCoachGoal{color:#dce4e1!important}.tutorialCoachHint{border:1px solid #4a5c60!important;border-left:3px solid #8d8065!important;border-radius:7px;background:#202a2f!important;color:#c7d4d0!important;box-shadow:none!important}
.tutorialCoachActions{padding-top:7px;border-top:1px solid #3f4c51}.tutorialCoachActions .pixelBtn{border-color:#46555a;background:#303b40;box-shadow:none}.tutorialCoachActions .pixelBtn:hover{border-color:#657479;background:#364247}.tutorialCoachActions .pixelBtn.primary{border-color:#587a76;background:#36514e}.tutorialCoachActions .redBtn{border-color:#73565a;background:#443337}.tutorialCoachActions .redBtn:hover{border-color:#8b6267;background:#4d383d}
.tutorialCoach.tutorialSuccessPulse{border-left-color:#86aa8d!important;background:#293a35!important}.tutorialCoach.tutorialSuccessPulse .tutorialCoachHead .badge{border-color:#6d8b73;background:#35483b;color:#d5e6d9}
.practiceCoach{border:1px solid #536360!important;border-left:3px solid #76938e!important;border-radius:9px;background:#273431!important;box-shadow:0 4px 14px #0002!important}.practiceCoachHead{padding-bottom:5px;border-bottom:1px solid #465551}.practiceCoachHead .badge{border:1px solid #5f7772;border-radius:999px;background:#30403d;box-shadow:none;color:#c9ddd8}.practiceCoachHead b{color:#b9cbc7}.practiceCoachText{color:#d0dad7!important}
.tutorialTarget{outline:2px solid #7fa09a!important;outline-offset:2px!important;filter:none!important}.pixelBtn.tutorialTarget{border-color:#78958e!important;background:#3c514c!important;box-shadow:none!important}.pileVisual.tutorialTarget{background:#7fa09a0b!important}.cardBtn.tutorialTarget .card,.meldEntry.tutorialTarget{outline-color:#8a9d88!important}
@media(max-width:390px){.tutorialCoach{border-left-width:3px!important;border-radius:8px}.tutorialCoachHead{gap:6px}.tutorialCoachActions{padding-top:6px}.tutorialCoachActions .pixelBtn{box-shadow:none}.practiceCoach{border-left-width:3px!important}}
'''
    s=s.replace(anchor,block+'\n'+anchor,1)

old='- [ ] 튜토리얼 coach를 동일한 전술 보드 톤으로 최종 마감'
new='- [x] 튜토리얼 coach를 동일한 전술 보드 톤으로 최종 마감 — coach/힌트/연습 안내를 슬레이트 보드와 청록·황동의 낮은 채도 강조로 통일하고, 단계 배지·버튼·타겟 강조에서 네온/강한 픽셀 그림자를 제거'
if old in r:
    r=r.replace(old,new,1)
elif new not in r:
    raise SystemExit('ROADMAP P3 tutorial state missing')

index.write_text(s)
road.write_text(r)
print('P3 tutorial tactical-board finish installed/corrected')

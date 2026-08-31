from pathlib import Path

index=Path('index.html')
road=Path('ROADMAP.md')
s=index.read_text()
r=road.read_text()

anchor='@media (prefers-reduced-motion:reduce){*,*:before,*:after{animation-duration:.001ms!important;animation-iteration-count:1!important;transition-duration:.001ms!important;scroll-behavior:auto!important}}'
if s.count(anchor)!=1:
    raise SystemExit(f'mobile wrap CSS anchor mismatch: {s.count(anchor)}')
block=r'''

/* L10N · long Korean copy mobile wrap safety */
.combatBanner{max-width:94%;white-space:normal;text-align:center;line-height:1.25;overflow-wrap:anywhere;word-break:keep-all}
.effectChoiceTitle,.effectChoiceText,.effectChoiceBtn,.effectChoiceBtn small{min-width:0;white-space:normal;overflow-wrap:anywhere;word-break:keep-all}
.effectChoiceBtn>span,.effectChoiceBtn>small{min-width:0}
.fieldStrip>span{min-width:0}.fieldStrip>span:last-child{text-align:right;overflow-wrap:anywhere;word-break:keep-all}.fieldEffect{overflow-wrap:anywhere;word-break:keep-all}
.phaseText,.initiativeRule,.switchAlert,.practiceCoachText,.startResumeNote{overflow-wrap:anywhere;word-break:keep-all}
.startMenuBtn>span:first-child{min-width:0}.startMenuBtn small{white-space:normal;overflow-wrap:anywhere;word-break:keep-all}
.progressFooter .pixelBtn,.developerActions .pixelBtn,.modalBtns .pixelBtn{min-width:0;white-space:normal;overflow-wrap:anywhere;word-break:keep-all}
.rulesHead h2,.codexSummary>span:first-child{min-width:0;overflow-wrap:anywhere;word-break:keep-all}
@media(max-width:390px){
 .combatBanner{max-width:calc(100vw - 28px);padding:7px 9px;font-size:14px}
 .combatBanner.break{font-size:20px}
 .effectChoicePanel{width:min(94vw,430px);padding:10px}
 .effectChoiceBtn{align-items:flex-start;flex-wrap:wrap}
 .effectChoiceBtn small{flex:1 1 100%;line-height:1.35}
 .fieldStrip{align-items:flex-start}.fieldStrip>span:last-child{max-width:62%}
 .startMenuBtn{gap:8px}.startMenuBtn .menuState{flex:0 0 auto}
 .progressFooter{flex-wrap:wrap}.progressFooter .pixelBtn{flex:1 1 150px}
}
'''
s=s.replace(anchor,anchor+block,1)

old='- [ ] 모바일 UI에서 긴 한국어 표현 잘림 점검'
new='- [x] 모바일 UI에서 긴 한국어 표현 잘림 점검 — 390px 이하에서 전투 배너·효과 선택창·필드 설명·페이즈/스위치 안내·시작 메뉴·모달 버튼의 긴 한국어가 고정 한 줄/flex 최소폭 때문에 잘리지 않도록 줄바꿈·최소폭·최대폭 안전 규칙 추가. 카드명·캐릭터 배지처럼 의도적으로 축약되는 정보 표시는 유지'
if r.count(old)!=1:
    raise SystemExit(f'ROADMAP mobile Korean wrap anchor mismatch: {r.count(old)}')
r=r.replace(old,new,1)
index.write_text(s)
road.write_text(r)
print('mobile Korean wrap safety CSS installed')

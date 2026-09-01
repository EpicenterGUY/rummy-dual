from pathlib import Path

index=Path('index.html')
road=Path('ROADMAP.md')
s=index.read_text()
r=road.read_text()

marker='/* UI3 P3 · start/result/codex visual language */'
if marker in s:
    raise SystemExit('P3 shell visual block already exists')
anchor='</style>'
if s.count(anchor)!=1:
    raise SystemExit(f'style closing tag mismatch: {s.count(anchor)}')
block=r'''

/* UI3 P3 · start/result/codex visual language */
.startHero{position:relative;overflow:hidden;border-color:#b6a98f;box-shadow:0 0 0 1px #d6c8ad inset,0 10px 26px #0003}
.startHero:after{content:"";position:absolute;left:18%;right:18%;bottom:0;height:3px;background:linear-gradient(90deg,transparent,#9f875f 25%,#6f9690 75%,transparent)}
.startMenuBtn{border-color:#46555a;background:#2c373c;box-shadow:0 1px 0 #ffffff0a inset,0 4px 12px #0002;border-left:4px solid #59676b}
.startMenuBtn.primary{background:#334b49;border-left-color:#78aaa4}.startMenuBtn:hover{border-color:#637277}.startMenuBtn.primary:hover{border-color:#78aaa4}
.startMenuBtn .menuState{padding:3px 6px;border:1px solid #75684f;border-radius:999px;background:#332f27;color:#dec99f}.startMenuBtn:disabled .menuState{border-color:#50585a;background:#2a3032;color:#7e8988}
.startResumeNote,.firstRunPrompt{box-shadow:0 1px 0 #ffffff06 inset,0 3px 10px #0002}
#overlay{background:#0d1215d9}#overlay .modal{border:1px solid #59666b;border-radius:14px;background:#273238;box-shadow:0 18px 60px #0008,0 1px 0 #ffffff08 inset}
#resultTitle{margin:0 0 10px;padding:0 0 8px;border-bottom:1px solid #566267;font-size:22px;letter-spacing:-.03em}#overlay .modal p{color:#d4ddda}
#circulationSummary{margin:10px 0 0;padding:8px 9px;border:1px solid #455257;border-radius:8px;background:#20292d;color:#aeb9b7;font-size:8px;line-height:1.5}
#resultUnlocks{margin-top:9px;padding:9px;border:1px solid #75684f;border-radius:8px;background:#332f27;color:#e7d9bb;line-height:1.55}#resultUnlocks b{color:#d7bd8b}
#overlay .modalBtns{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:7px}#overlay .modalBtns .pixelBtn{min-width:0;min-height:42px}
.codexModal{border:1px solid #59666b!important;border-radius:14px;background:#242f34!important;box-shadow:0 18px 60px #0008,0 1px 0 #ffffff08 inset!important}
.codexModal .rulesHead{background:#242f34;border-bottom:1px solid #445157;margin:0 -2px 8px;padding:4px 2px 8px}.codexModal .rulesHead h2{color:#eef0ea}
.codexSummary{border-color:#4b595e;background:#2a353a;border-radius:8px;color:#d7dedb}.codexSummary b{color:#d7bd8b}
.codexTabs{padding:2px 1px 8px;margin-bottom:7px;border-bottom:1px solid #414e53}.codexTabs .pixelBtn{background:#303b40;border-color:#46555a;box-shadow:none}.codexTabs .active{background:#36524f;border-color:#6f9690;box-shadow:none;color:#e4f0ed}
.codexEntry{border-color:#445258;background:#29343a;border-radius:8px}.codexEntry.locked{background:#20282c;color:#7f8a8b}.codexName{color:#f0f2ed}.codexMeta{color:#aeb9b7}.codexEffect{color:#d4dcda}.codexUnlock{color:#d7bd8b}
.codexLockVisual{border:1px solid #4a565a;background:repeating-linear-gradient(45deg,#303a3f 0 4px,#252e32 4px 8px);box-shadow:none;color:#7f8b8c}
.codexFieldIcon{border:1px solid #75684f;background:#332f27;box-shadow:none;color:#e0cda6}.codexEntry.themeLocked{border-color:#75684f;background:#302e27}.codexEntry.devRevealed{border-color:#696378;background:#302f38}
.codexThemeEmpty{border-color:#56666a;background:#222c31;color:#aeb9b7;border-radius:8px}.codexThemeEmpty b{color:#90b9b3}
@media(max-width:390px){#resultTitle{font-size:19px}#overlay .modal{padding:11px}.codexModal{border-radius:10px}.startMenuBtn{border-left-width:3px}}
'''
s=s.replace(anchor,block+'\n'+anchor,1)

old='- [ ] 시작창/결과창/도감의 시각 언어 통일'
new='- [x] 시작창/결과창/도감의 시각 언어 통일 — 시작 히어로는 종이/황동 포인트, 메뉴·결과·도감 인터랙션은 슬레이트/청록 표면으로 통일하고 해금·필드 정보에만 절제된 황동 강조를 사용'
if r.count(old)!=1:
    raise SystemExit(f'ROADMAP P3 shell visual anchor mismatch: {r.count(old)}')
r=r.replace(old,new,1)
index.write_text(s)
road.write_text(r)
print('P3 start/result/codex visual language installed')

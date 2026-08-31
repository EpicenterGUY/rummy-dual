from pathlib import Path

index=Path('index.html')
road=Path('ROADMAP.md')
theme=Path('docs/THEME_GROUPS.md')
text=index.read_text()

# 1) Add 6♦ ZERO-SIGHT variant.
old="'D6':{n:'예약 발송',t:'topDeckChoice',d:'버릴 때 버림패 대신 자기 덱 맨 위에 놓을 수 있다.'},"
new=old+"\n'ZSD6':{slot:'D6',themeId:'zero-sight',n:'탄도 계산',t:'zsBallistics',d:'내 표적 조합을 이용해 스위치를 반환할 때, 이번 반환까지 반영한 상대 현재 코어+보호막 부족분만큼 최대 +12 보정한다.'},"
assert old in text,'D6 card anchor changed'
text=text.replace(old,new,1)

# 2) Ordinary open-deck tendency and independent unlock progression.
old="zsObserver:['control','cycle','combo'],zsScopeAdjust:['control','cycle','interact']"
new="zsObserver:['control','cycle','combo'],zsScopeAdjust:['control','cycle','interact'],zsBallistics:['pressure','control']"
assert old in text,'ZERO-SIGHT tendency anchor changed'
text=text.replace(old,new,1)
# Do not mutate existing g3 array: older theme regressions intentionally lock that progression contract.
old=" {id:'g3',label:'전체 3클리어',kind:'mixed',when:p=>p.totalClears>=3,items:['S9','H10','D2','VSD4','C6','SJ','H3'],fields:[]},"
new=old+"\n {id:'zs3',label:'전체 3클리어 · ZERO-SIGHT',kind:'theme',when:p=>p.totalClears>=3,items:['ZSD6'],fields:[]},"
assert old in text,'g3 unlock anchor changed'
text=text.replace(old,new,1)

# 3) Shared core+shield requirement/deficit calculator. This is intentionally a pure helper, not an effect action.
old="function addSwitchPower(w,amount,label='위력',targetOverride=null){"
helper="""function coreShieldRequirement(w){const s=sideObj(w);return Math.max(0,Math.round((s?.hp||0)+(s?.shield||0)))}
function coreShieldDeficit(w,projectedPower=state.switchPower,cap=Infinity){const projected=Math.max(0,Math.round(projectedPower||0)),gap=Math.max(0,coreShieldRequirement(w)-projected),limit=Number.isFinite(cap)?Math.max(0,Math.round(cap)):Infinity;return Math.min(gap,limit)}
function addSwitchPower(w,amount,label='위력',targetOverride=null){"""
assert old in text,'addSwitchPower helper anchor changed'
text=text.replace(old,helper,1)

# 4) Resolver only reserves the cap. Final amount is deliberately calculated after trap reduction.
old="case'zsObserver':if(ctx.meld){if(typeof setZeroSightTarget==='function')setZeroSightTarget(w,ctx.meld,{reason:'observer'});const paused=requestZeroSightCycle(w,c,cards,resume);if(paused)return pause()}break;case'zsScopeAdjust':{const paused=requestZeroSightRelocation(w,c,{...ctx,cards},resume);if(paused)return pause();break}case'vacancyJoker':case'rebelJoker':break"
new="case'zsObserver':if(ctx.meld){if(typeof setZeroSightTarget==='function')setZeroSightTarget(w,ctx.meld,{reason:'observer'});const paused=requestZeroSightCycle(w,c,cards,resume);if(paused)return pause()}break;case'zsScopeAdjust':{const paused=requestZeroSightRelocation(w,c,{...ctx,cards},resume);if(paused)return pause();break}case'zsBallistics':if(isReturning&&ctx.meld&&typeof isZeroSightTarget==='function'&&isZeroSightTarget(w,ctx.meld)){fx.coreShieldDeficitCap=Math.max(fx.coreShieldDeficitCap||0,12);fx.coreShieldDeficitSource=c.name}break;case'vacancyJoker':case'rebelJoker':break"
assert old in text,'resolveEffects ZERO-SIGHT tail anchor changed'
text=text.replace(old,new,1)

# 5) Apply the reserved lethal assist after base-power trap reduction and before returnSwitch.
old="""    const forceReturn=!continuation&&!!fx.forceReturn;
    if(returning||forceReturn){
      if(w==='player')state.lastPlayerReturnType=type;else state.lastEnemyReturnType=type;
      attackEvent(w,finalBase?[{amount:finalBase,label,kind:type==='SET'?'burst':'chain'}]:[],{bonus,label,flatReturn:fx.flatReturn,forceReturn:true});"""
new="""    const forceReturn=!continuation&&!!fx.forceReturn;
    if(returning||forceReturn){
      const deficitCap=Math.max(0,ctx.fxState?.coreShieldDeficitCap||0);
      if(deficitCap&&!fx.flatReturn){const projected=state.switchPower+finalBase+bonus,assist=coreShieldDeficit(other(w),projected,deficitCap);if(assist){bonus+=assist;log(`${ctx.fxState?.coreShieldDeficitSource||'탄도 계산'}: 상대 현재 코어+보호막 부족분 ${assist}만큼 반환 위력 보정.`,'important')}}
      if(w==='player')state.lastPlayerReturnType=type;else state.lastEnemyReturnType=type;
      attackEvent(w,finalBase?[{amount:finalBase,label,kind:type==='SET'?'burst':'chain'}]:[],{bonus,label,flatReturn:fx.flatReturn,forceReturn:true});"""
assert old in text,'attach final return anchor changed'
text=text.replace(old,new,1)

index.write_text(text)

# Roadmap sync.
r=road.read_text()
anchor="- [x] ZERO-SIGHT 첫 라이브 스타터 페어 — A♣ `관측수` / 2♣ `스코프 조정`을 전체 1클리어 해금으로 추가하고 ZERO-SIGHT 오픈형 테마 선택을 활성화"
assert anchor in r,'ROADMAP ZERO-SIGHT starter anchor missing'
insert=anchor+"\n- [x] 코어+보호막 부족분 공용 계산 + 6♦ `탄도 계산` 라이브 구현 — `coreShieldRequirement` / `coreShieldDeficit` 순수 헬퍼로 현재 코어+보호막 기준 킬각 부족분을 계산하며, 별도 효과 액션/자원은 만들지 않음. 탄도 계산은 표적 반환의 실제 기본 위력·기존 누적·네임드 보정·매복 감소까지 반영한 최종 반환 직전에 부족분만 최대 +12 보정"
r=r.replace(anchor,insert,1)
road.write_text(r)

# Canonical theme doc sync.
t=theme.read_text()
old="- [ ] 코어+보호막 부족분 계산 공통 액션 추가 검토"
new="- [x] 코어+보호막 부족분 계산 공용화 — 별도 효과 액션을 늘리지 않고 `coreShieldRequirement` / `coreShieldDeficit` 순수 계산 헬퍼로 잠금. 현재 코어+보호막과 예상 반환 위력의 차이를 0 이상으로 계산하고 카드별 상한을 적용"
assert old in t,'theme deficit checklist anchor changed'
t=t.replace(old,new,1)
anchor="- [x] 첫 라이브 스타터 구현 — A♣ `관측수` / 2♣ `스코프 조정`; 둘 다 전용 자원 없이 표적·공용 패순환만 사용하며 전체 1클리어부터 오픈형 ZERO-SIGHT 빌드에 편성"
assert anchor in t,'theme starter implementation anchor missing'
t=t.replace(anchor,anchor+"\n- [x] 6♦ `탄도 계산` 라이브 구현 — 전체 3클리어 해금. 표적 조합 반환에서 매복 감소까지 반영한 실제 반환 직전 예상 위력을 기준으로 코어+보호막 부족분만 최대 +12 보정하고, 이미 파괴 가능하면 +0",1)
theme.write_text(t)

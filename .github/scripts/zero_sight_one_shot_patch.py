from pathlib import Path

index=Path('index.html')
road=Path('ROADMAP.md')
theme=Path('docs/THEME_GROUPS.md')
audit=Path('tests/named-card-audit.mjs')
text=index.read_text()

# 1) Add K♠ ZERO-SIGHT finisher as an exact-slot variant.
old="'SK':{n:'겁쟁이 왕',t:'firstMeldBonus',d:'내 공개 조합이 없을 때 이 카드로 첫 조합을 만들면 보호막 20.'},"
new=old+"\n'ZSSK':{slot:'SK',themeId:'zero-sight',n:'ONE SHOT',t:'zsOneShot',d:'상대 표적 조합에 붙여 스위치를 반환할 때, 이 행동 전 기존 누적 위력이 50 이상이면 +18 후 표적을 해제한다. 50 미만이면 반환 후 자신에게 봉인 1.'},"
assert old in text,'SK card anchor changed'
text=text.replace(old,new,1)

# 2) Open-deck tendency and independent late unlock.
old="zsBallistics:['pressure','control']"
new="zsBallistics:['pressure','control'],zsOneShot:['pressure','control','status']"
assert old in text,'ZERO-SIGHT tendency anchor changed'
text=text.replace(old,new,1)
old=" {id:'g7',label:'전체 7클리어',kind:'mixed',when:p=>p.totalClears>=7,items:[],fields:['F5']},"
new=old+"\n {id:'zs7',label:'전체 7클리어 · ZERO-SIGHT',kind:'theme',when:p=>p.totalClears>=7,items:['ZSSK'],fields:[]},"
assert old in text,'g7 unlock anchor changed'
text=text.replace(old,new,1)

# 3) Shared post-return resolution keeps target-reaction timing stable and avoids same-action seal-order dependence.
old="function firstCopyEffectSource(cards,self,tags){"
helper="""function resolveZeroSightPostReturn(w,m,fxState={}){let changed=false;if(fxState.zeroSightClearTargetAfterReturn===m&&typeof isZeroSightTarget==='function'&&isZeroSightTarget(w,m)){if(typeof clearZeroSightTarget==='function')clearZeroSightTarget(w,{reason:'oneShot'});fxState.zeroSightClearTargetAfterReturn=null;changed=true}const seal=Math.max(0,Math.round(fxState.zeroSightSelfSealAfterReturn||0));if(seal){if(typeof applyOfficialStatus==='function')applyOfficialStatus('player',sideObj(w),'seal',seal,{actor:w});if(typeof log==='function')log(`ONE SHOT 실패 · ${w==='player'?'나':'상대'}에게 봉인 ${seal}.`,'hit');fxState.zeroSightSelfSealAfterReturn=0;changed=true}return changed}
function firstCopyEffectSource(cards,self,tags){"""
assert old in text,'post-return helper insertion anchor changed'
text=text.replace(old,helper,1)

# 4) Reserve success/failure state during named-effect resolution; do not clear target or self-seal yet.
old="case'zsBallistics':if(isReturning&&ctx.meld&&typeof isZeroSightTarget==='function'&&isZeroSightTarget(w,ctx.meld)){fx.coreShieldDeficitCap=Math.max(fx.coreShieldDeficitCap||0,12);fx.coreShieldDeficitSource=c.name}break;case'vacancyJoker':case'rebelJoker':break"
new="case'zsBallistics':if(isReturning&&ctx.meld&&typeof isZeroSightTarget==='function'&&isZeroSightTarget(w,ctx.meld)){fx.coreShieldDeficitCap=Math.max(fx.coreShieldDeficitCap||0,12);fx.coreShieldDeficitSource=c.name}break;case'zsOneShot':if(isReturning&&ctx.targetOwner===foe&&ctx.meld&&typeof isZeroSightTarget==='function'&&isZeroSightTarget(w,ctx.meld)){if(state.switchPower>=50){fx.bonus+=18;fx.zeroSightClearTargetAfterReturn=ctx.meld}else fx.zeroSightSelfSealAfterReturn=Math.max(fx.zeroSightSelfSealAfterReturn||0,1)}break;case'vacancyJoker':case'rebelJoker':break"
assert old in text,'resolver ZERO-SIGHT finisher anchor changed'
text=text.replace(old,new,1)

# 5) Resolve deferred ONE SHOT consequences only after attach/target/clash reaction packets observed the target state.
old="if(typeof emitEffectEvent==='function')emitEffectEvent('onAttach',{actor:w,cards:[...cards],type,meld:m,targetSide,returned:returning||forceReturn,continuation,phase:'afterResolve',targetedBy:typeof zeroSightTargetActors==='function'?zeroSightTargetActors(m):[]});if(typeof emitZeroSightTargetChange==='function')emitZeroSightTargetChange('attach',m,{actionActor:w,cards:[...cards],targetSide,returned:returning||forceReturn,continuation});if(typeof refreshPointBlankClashMeld==='function')refreshPointBlankClashMeld(m,{change:'attach',actionActor:w,cards:[...cards],targetSide,returned:returning||forceReturn,continuation});"
new=old+"if((returning||forceReturn)&&typeof resolveZeroSightPostReturn==='function')resolveZeroSightPostReturn(w,m,ctx.fxState||{});"
assert old in text,'attach reaction timing anchor changed'
text=text.replace(old,new,1)

index.write_text(text)

# 6) Keep direct-power audit honest now that Ballistics and ONE SHOT are live.
a=audit.read_text()
old="const direct=new Set(['finalUltimatum','blackBullet','fuseRound']);"
new="const direct=new Set(['finalUltimatum','blackBullet','fuseRound','zsBallistics','zsOneShot']);"
assert old in a,'named direct-power audit anchor changed'
a=a.replace(old,new,1)
audit.write_text(a)

# 7) Roadmap sync.
r=road.read_text()
anchor="- [x] 코어+보호막 부족분 공용 계산 + 6♦ `탄도 계산` 라이브 구현 — `coreShieldRequirement` / `coreShieldDeficit` 순수 헬퍼로 현재 코어+보호막 기준 킬각 부족분을 계산하며, 별도 효과 액션/자원은 만들지 않음. 탄도 계산은 표적 반환의 실제 기본 위력·기존 누적·네임드 보정·매복 감소까지 반영한 최종 반환 직전에 부족분만 최대 +12 보정"
assert anchor in r,'ROADMAP Ballistics anchor missing'
r=r.replace(anchor,anchor+"\n- [x] K♠ `ONE SHOT` 라이브 구현 — 전체 7클리어 해금. 상대 표적 조합 반환 시 행동 전 기존 누적 위력 50+면 +18, 반환 반응 이벤트가 표적 상태를 모두 관측한 뒤 표적 해제. 50 미만 시 현재 행동의 다른 네임드 순서를 방해하지 않고 반환 후 자신에게 봉인 1",1)
road.write_text(r)

# 8) Canonical theme doc sync and precise wording.
t=theme.read_text()
old="- K♠ `ONE SHOT` — 누적 50+에서 상대 표적 조합 반환 +18 후 표적 해제, 실패 시 자기 봉인 리스크."
new="- K♠ `ONE SHOT` — 상대 표적 조합 반환 시 **행동 전 기존 누적 위력**이 50+면 +18 후 표적 해제. 50 미만이면 반환 후 자신에게 봉인 1."
assert old in t,'ONE SHOT candidate wording anchor changed'
t=t.replace(old,new,1)
anchor="- [x] 6♦ `탄도 계산` 라이브 구현 — 전체 3클리어 해금. 표적 조합 반환에서 매복 감소까지 반영한 실제 반환 직전 예상 위력을 기준으로 코어+보호막 부족분만 최대 +12 보정하고, 이미 파괴 가능하면 +0"
assert anchor in t,'theme Ballistics implementation anchor missing'
t=t.replace(anchor,anchor+"\n- [x] K♠ `ONE SHOT` 라이브 구현 — 전체 7클리어 해금. 성공 +18은 상대 표적 조합의 실제 반환에만 적용하고, 성공 시 `onAttach`/표적 조합 변화 반응 뒤 표적을 해제한다. 50 미만 실패 봉인은 현재 행동 종료 뒤 적용해 카드 순서 의존을 만들지 않는다.",1)
theme.write_text(t)

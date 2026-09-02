from pathlib import Path
import re


def replace_once(text, old, new, label):
    if old not in text:
        raise SystemExit(f'missing {label}')
    return text.replace(old, new, 1)


def add_after_named(text, anchor_id, new_id, line):
    if f"'{new_id}':{{" in text:
        return text
    pat = re.compile(rf"^'{re.escape(anchor_id)}':\{{[^\n]*\}},$", re.M)
    m = pat.search(text)
    if not m:
        raise SystemExit(f'missing NAMED anchor {anchor_id} for {new_id}')
    return text[:m.end()] + '\n' + line + text[m.end():]


index = Path('index.html')
text = index.read_text(encoding='utf-8')

# ---------------------------------------------------------------------------
# 1) ZERO-SIGHT 18-card definition pool. Existing live cards stay untouched;
#    the 14 new cards are staged out of ordinary roguelike rewards until the
#    three-theme 60-card integration pass.
# ---------------------------------------------------------------------------
defs = [
 ('D2','ZSD2', "'ZSD2':{slot:'D2',themeId:'zero-sight',rewardPool:false,n:'거리측정기',t:'zsRangefinder',d:'이 카드가 공개된 동안 내 표적을 새로 지정하거나 이전하면 턴당 1회 덱 위 3장의 다음 획득 순서를 정한다.'},"),
 ('H3','ZSH3', "'ZSH3':{slot:'H3',themeId:'zero-sight',rewardPool:false,prepRequired:1,n:'호흡 조절',t:'zsBreathControl',d:'손에서 내 턴 종료 1회를 준비하고 내 표적이 있는 상태로 사용하면 보호막 12를 얻고 남은 손패 1장을 무료 정비한다.'},"),
 ('S4','ZSS4', "'ZSS4':{slot:'S4',themeId:'zero-sight',rewardPool:false,n:'제압 사격',t:'zsSuppressiveFire',d:'내 상대 표적 조합에 붙이면 봉인이 없을 때 봉인 1을 부여하고, 이미 봉인이 있으면 그 조합을 고정한다.'},"),
 ('H4','ZSH4', "'ZSH4':{slot:'H4',themeId:'zero-sight',rewardPool:false,n:'위장망',t:'zsCamouflage',d:'이 카드를 사용한 공개 조합을 내 표적으로 지정한다. 그 조합에 내가 제어하는 카드가 2장 이상이면 보호 1도 부여한다.'},"),
 ('C5','ZSC5', "'ZSC5':{slot:'C5',themeId:'zero-sight',rewardPool:false,n:'사각지대',t:'zsBlindSpot',d:'내 카드가 이미 들어간 상대 공개 조합에 붙이면 그 조합으로 표적을 이전한다. 이번 턴 먼저 회수했다면 남은 손패 1장을 무료 정비한다.'},"),
 ('C6','ZSC6', "'ZSC6':{slot:'C6',themeId:'zero-sight',rewardPool:false,n:'관측 기록',t:'zsObservationLog',d:'이 카드가 있는 내 표적을 다음 턴까지 유지한 뒤 그 표적에 내가 처음 붙이면 남은 손패 1장을 무료 정비한다. 턴당 1회.'},"),
 ('S7','ZSS7', "'ZSS7':{slot:'S7',themeId:'zero-sight',rewardPool:false,n:'철갑탄',t:'zsArmorPiercing',d:'내 상대 표적 조합에 붙여 스위치를 반환하면 누적 위력 +10. 그 조합의 보호 1을 제거할 수 있었다면 대신 +14.'},"),
 ('H7','ZSH7', "'ZSH7':{slot:'H7',themeId:'zero-sight',rewardPool:false,n:'안전거리',t:'zsSafeDistance',d:'이 카드가 공개된 동안 내 표적에서 내가 카드를 회수하면 턴당 1회 보호막 12를 얻는다.'},"),
 ('C8','ZSC8', "'ZSC8':{slot:'C8',themeId:'zero-sight',rewardPool:false,n:'관측 교대',t:'zsObserverShift',d:'이 카드를 내 표적 조합에서 회수하면 그 표적을 다른 공개 조합으로 이전할 수 있다.'},"),
 ('D8','ZSD8', "'ZSD8':{slot:'D8',themeId:'zero-sight',rewardPool:false,n:'예비 탄창',t:'zsReserveMag',d:'내 표적 조합에 이 카드를 붙이면 덱 위 2장의 다음 획득 순서를 정한다.'},"),
 ('S9','ZSS9', "'ZSS9':{slot:'S9',themeId:'zero-sight',rewardPool:false,n:'역추적',t:'zsCounterTrace',d:'이 카드가 공개된 동안 상대가 내 표적 조합으로 스위치를 반환하면 충전한다. 공개 상태를 유지한 채 내가 다음 스위치를 반환하면 누적 위력 +12 후 충전을 해제한다.'},"),
 ('S10','ZSS10', "'ZSS10':{slot:'S10',themeId:'zero-sight',rewardPool:false,prepRequired:2,n:'장거리 사격',t:'zsLongShot',d:'손에서 내 턴 종료 2회를 준비한 뒤 내 표적 조합을 이용해 스위치를 반환하면 누적 위력 +16.'},"),
 ('CJ','ZSCJ', "'ZSCJ':{slot:'CJ',themeId:'zero-sight',rewardPool:false,n:'관측 드론',t:'zsDrone',d:'이 카드가 공개된 동안 상대가 새 공개 조합을 만들면 턴당 1회 그 조합으로 내 표적을 자동 이전하고 남은 손패 1장을 무료 정비한다.'},"),
 ('SQ','ZSSQ', "'ZSSQ':{slot:'SQ',themeId:'zero-sight',rewardPool:false,n:'데드 앵글',t:'zsDeadAngle',d:'이 카드가 내 표적에 있는 동안 상대가 그 표적에서 카드를 회수하거나 밖으로 이동시키면 상대에게 취약 1을 주고 남은 내 카드 1장에 보호 1을 부여한다. 턴당 1회.'},"),
]
for anchor, cid, line in defs:
    text = add_after_named(text, anchor, cid, line)

# Explicit counter-trace state lives on card objects and is cleared by full recirculation.
old = "themeTurnGates:{},fuseArmed:false"
new = "themeTurnGates:{},zsCounterTraceCharged:false,fuseArmed:false"
if old in text:
    text = replace_once(text, old, new, 'makeCard ZERO-SIGHT state')
elif new not in text:
    raise SystemExit('unrecognized makeCard theme state')
old = "c.age=0;if(typeof resetHandPreparation==='function')resetHandPreparation(c);"
new = "c.age=0;c.zsCounterTraceCharged=false;if(typeof resetHandPreparation==='function')resetHandPreparation(c);"
if old in text:
    text = replace_once(text, old, new, 'recirculation ZERO-SIGHT state reset')
elif new not in text:
    raise SystemExit('unrecognized recirculation card reset')

# ---------------------------------------------------------------------------
# 2) Open-deck tendencies for all 18 cards.
# ---------------------------------------------------------------------------
old = "zsObserver:['control','cycle','combo'],zsScopeAdjust:['control','cycle','interact'],zsBallistics:['pressure','control'],zsOneShot:['pressure','control','status']"
new = "zsObserver:['control','cycle','combo'],zsScopeAdjust:['control','cycle','interact'],zsRangefinder:['control','cycle'],zsBreathControl:['hold','sustain','cycle'],zsSuppressiveFire:['control','status','interact'],zsCamouflage:['control','sustain'],zsBlindSpot:['interact','control','cycle'],zsObservationLog:['control','cycle','hold'],zsBallistics:['pressure','control'],zsArmorPiercing:['pressure','interact'],zsSafeDistance:['sustain','recover'],zsObserverShift:['recover','control','interact'],zsReserveMag:['cycle','control'],zsCounterTrace:['pressure','control'],zsLongShot:['hold','pressure'],zsDrone:['control','cycle','interact'],zsDeadAngle:['control','status','sustain'],zsOneShot:['pressure','control','status']"
if old in text:
    text = replace_once(text, old, new, 'ZERO-SIGHT tendencies')
elif new not in text:
    raise SystemExit('unrecognized ZERO-SIGHT tendency block')

# ---------------------------------------------------------------------------
# 3) Shared ZERO-SIGHT helpers: top-deck order, target age, public-card scan,
#    and retarget-only chooser. No numeric theme resource is introduced.
# ---------------------------------------------------------------------------
if 'function zeroSightPublicCards(' not in text:
    anchor = "function zeroSightCycleCandidates(w,exclude=[]){"
    helper = r'''function zeroSightPublicCards(actor,tag=null){const out=[];if(typeof meldsOf!=='function'||typeof other!=='function')return out;for(const side of[actor,other(actor)])for(const m of meldsOf(side))for(const c of m.cards||[])if(c?.owner===actor&&c.themeId==='zero-sight'&&(!tag||c.tag===tag))out.push(c);return out}
function zeroSightTargetAge(actor,m=null){const target=m||(typeof zeroSightTargetMeld==='function'?zeroSightTargetMeld(actor):null);if(!target)return 0;const setTurn=target?.themeMeta?.zeroSight?.targetedTurn?.[actor];if(setTurn==null)return 0;return Math.max(0,(state.turnNo??setTurn)-setTurn)}
function zeroSightPermutations(cards){const out=[];function rec(prefix,rest){if(!rest.length){out.push(prefix);return}for(let i=0;i<rest.length;i++)rec(prefix.concat(rest[i]),rest.slice(0,i).concat(rest.slice(i+1)))}rec([],cards||[]);return out}
function applyZeroSightTopOrder(w,drawOrder){const side=sideObj(w),n=drawOrder?.length||0;if(!n||side.deck.length<n)return false;const current=side.deck.slice(-n),have=new Set(current.map(c=>c.uid));if(drawOrder.some(c=>!have.has(c.uid)))return false;side.deck.splice(side.deck.length-n,n);for(let i=drawOrder.length-1;i>=0;i--)side.deck.push(drawOrder[i]);if(w==='player'&&typeof flashPile==='function')flashPile('deckPile');return true}
function requestZeroSightTopOrder(w,source,count=3,onAsyncResolved=null){const side=sideObj(w),n=Math.min(Math.max(0,count||0),side.deck.length);if(n<2){if(typeof onAsyncResolved==='function')onAsyncResolved(null);return false}const window=side.deck.slice(-n),orders=zeroSightPermutations(window),currentDraw=[...window].reverse(),apply=order=>{const ok=applyZeroSightTopOrder(w,order);if(ok&&typeof log==='function')log(`${source?.name||'ZERO-SIGHT 관측'}: 다음 획득 순서 · ${order.map(cardText).join(' → ')}.`,'good');return ok},interactive=w==='player'&&state.turn==='player'&&typeof requestEffectChoice==='function';if(interactive){return requestEffectChoice({title:source?.name||'ZERO-SIGHT 관측',text:`덱 위 ${n}장의 다음 획득 순서를 고르세요.`,options:orders.map((order,i)=>({key:`zsorder:${i}`,label:order.map(cardText).join(' → '),detail:'왼쪽부터 다음 획득',order})),onChoose:o=>{if(o?.order)apply(o.order);if(typeof onAsyncResolved==='function')onAsyncResolved(o?.order||null)}})}let chosen=currentDraw;if(w==='enemy'&&typeof aiCardChoiceScore==='function')chosen=[...orders].sort((a,b)=>(aiCardChoiceScore(b[0])||0)-(aiCardChoiceScore(a[0])||0))[0]||currentDraw;apply(chosen);if(typeof onAsyncResolved==='function')onAsyncResolved(chosen);return false}
function requestZeroSightRetargetOnly(w,source,current=null,onAsyncResolved=null){const from=current||(typeof zeroSightTargetMeld==='function'?zeroSightTargetMeld(w):null),candidates=typeof zeroSightRelocationTargets==='function'?zeroSightRelocationTargets(w,from):[];if(!from||!candidates.length){if(typeof onAsyncResolved==='function')onAsyncResolved(null);return false}const apply=entry=>entry?.m&&typeof setZeroSightTarget==='function'?setZeroSightTarget(w,entry.m,{reason:'observerShift'}):false,interactive=w==='player'&&state.turn==='player'&&typeof requestEffectChoice==='function'&&candidates.length>1;if(interactive)return requestEffectChoice({title:source?.name||'관측 교대',text:'회수한 표적을 다른 공개 조합으로 이전할 수 있습니다.',options:candidates.map((x,i)=>({key:`zsretarget:${i}`,label:`${x.side===w?'내':'상대'} ${x.m.type} · ${x.m.cards.length}장`,detail:'표적 이전',entry:x})),allowSkip:true,skipLabel:'이전하지 않기',onChoose:o=>{if(o?.entry)apply(o.entry);if(typeof onAsyncResolved==='function')onAsyncResolved(o?.entry||null)}});const chosen=candidates[0];apply(chosen);if(typeof onAsyncResolved==='function')onAsyncResolved(chosen);return false}
'''
    if anchor not in text:
        raise SystemExit('missing ZERO-SIGHT helper anchor')
    text = text.replace(anchor, helper + anchor, 1)

# ---------------------------------------------------------------------------
# 4) Passive target-event reactions. Guarded for isolated foundation tests.
# ---------------------------------------------------------------------------
if 'function handleZeroSightFullThemeEvent(' not in text:
    anchor = "function handlePointBlankThemeEvent(packet){"
    handler = r'''function handleZeroSightFullThemeEvent(packet){
 if(!packet?.event||typeof sideObj!=='function'||typeof other!=='function'||typeof meldsOf!=='function'||typeof zeroSightPublicCards!=='function')return false;
 if(packet.event==='onRecover'){state.zeroSightLastRecoverActor=packet.actor;state.zeroSightLastRecoverToken=packet.turnToken}
 if(packet.event==='onTargetSet'){
  const actor=packet.actor,range=zeroSightPublicCards(actor,'zsRangefinder')[0];if(range&&(!themeTurnGateUsed(range,'zsRangefinder',packet.turnToken))){if(typeof claimThemeTurnGate==='function')claimThemeTurnGate(range,'zsRangefinder',packet.turnToken);if(typeof requestZeroSightTopOrder==='function')requestZeroSightTopOrder(actor,range,3);return true}
 }
 if(packet.event==='onMeldCreate'){
  const owner=other(packet.actor),drone=zeroSightPublicCards(owner,'zsDrone')[0];if(drone&&packet.meld&&(!themeTurnGateUsed(drone,'zsDrone',packet.turnToken))){if(typeof claimThemeTurnGate==='function')claimThemeTurnGate(drone,'zsDrone',packet.turnToken);if(typeof setZeroSightTarget==='function')setZeroSightTarget(owner,packet.meld,{reason:'drone'});if(typeof requestZeroSightCycle==='function')requestZeroSightCycle(owner,drone,packet.cards||[]);return true}
 }
 if(packet.event==='onAttach'){
  const actor=packet.actor;
  if((packet.targetedBy||[]).includes(actor)&&typeof zeroSightTargetAge==='function'&&zeroSightTargetAge(actor,packet.meld)>=1){const record=(packet.meld?.cards||[]).find(c=>c.owner===actor&&c.themeId==='zero-sight'&&c.tag==='zsObservationLog');if(record&&!themeTurnGateUsed(record,'zsObservationLog',packet.turnToken)){if(typeof claimThemeTurnGate==='function')claimThemeTurnGate(record,'zsObservationLog',packet.turnToken);if(typeof requestZeroSightCycle==='function')requestZeroSightCycle(actor,record,packet.cards||[]);}}
  if(packet.returned)for(const owner of packet.targetedBy||[]){if(owner===actor)continue;const trace=zeroSightPublicCards(owner,'zsCounterTrace')[0];if(trace&&!trace.zsCounterTraceCharged){trace.zsCounterTraceCharged=true;if(typeof log==='function')log(`${trace.name}: 상대의 표적 반환을 역추적 · 다음 내 반환 +12 준비.`,'important')}}
 }
 if(packet.event==='onRecover'){
  const actor=packet.actor;if((packet.targetedBy||[]).includes(actor)){const safe=zeroSightPublicCards(actor,'zsSafeDistance')[0]||((packet.card?.owner===actor&&packet.card?.themeId==='zero-sight'&&packet.card?.tag==='zsSafeDistance')?packet.card:null);if(safe&&!themeTurnGateUsed(safe,'zsSafeDistance',packet.turnToken)){if(typeof claimThemeTurnGate==='function')claimThemeTurnGate(safe,'zsSafeDistance',packet.turnToken);if(typeof addShield==='function')addShield(actor,3)}}
  if(packet.card?.owner===actor&&packet.card?.themeId==='zero-sight'&&packet.card?.tag==='zsObserverShift'&&(packet.targetedBy||[]).includes(actor)&&typeof requestZeroSightRetargetOnly==='function')requestZeroSightRetargetOnly(actor,packet.card,packet.meld);
  for(const owner of packet.targetedBy||[]){if(owner===actor)continue;const dead=(packet.meld?.cards||[]).find(c=>c.owner===owner&&c.themeId==='zero-sight'&&c.tag==='zsDeadAngle');if(!dead||themeTurnGateUsed(dead,'zsDeadAngle',packet.turnToken))continue;if(typeof claimThemeTurnGate==='function')claimThemeTurnGate(dead,'zsDeadAngle',packet.turnToken);if(typeof applyOfficialStatus==='function')applyOfficialStatus('player',sideObj(actor),'vulnerable',1,{actor:owner});const ally=(packet.meld?.cards||[]).find(c=>c.owner===owner&&c.uid!==dead.uid);if(ally&&typeof applyOfficialStatus==='function')applyOfficialStatus('card',ally,'protect',1,{actor:owner,silent:true});return true}
 }
 if(packet.event==='onMeldMove'){
  const actor=packet.actor;for(const owner of packet.sourceTargetedBy||[]){if(owner===actor)continue;const dead=(packet.sourceMeld?.cards||[]).find(c=>c.owner===owner&&c.themeId==='zero-sight'&&c.tag==='zsDeadAngle');if(!dead||themeTurnGateUsed(dead,'zsDeadAngle',packet.turnToken))continue;if(typeof claimThemeTurnGate==='function')claimThemeTurnGate(dead,'zsDeadAngle',packet.turnToken);if(typeof applyOfficialStatus==='function')applyOfficialStatus('player',sideObj(actor),'vulnerable',1,{actor:owner});const ally=(packet.sourceMeld?.cards||[]).find(c=>c.owner===owner&&c.uid!==dead.uid);if(ally&&typeof applyOfficialStatus==='function')applyOfficialStatus('card',ally,'protect',1,{actor:owner,silent:true});return true}
 }
 return false
}
subscribeEffectEvent(handleZeroSightFullThemeEvent);
'''
    if anchor not in text:
        raise SystemExit('missing ZERO-SIGHT subscriber anchor')
    text = text.replace(anchor, handler + anchor, 1)

# ---------------------------------------------------------------------------
# 5) Resolver branches. Counter-trace is a public boolean charge; direct power
#    remains limited to Ballistics / Armor Piercing / Counter Trace / Long Shot /
#    ONE SHOT rather than becoming a theme-wide resource.
# ---------------------------------------------------------------------------
if 'zsCounterTraceChecked' not in text:
    anchor = "if(isReturning&&ctx.meld&&!fx.vReverseViralChecked)"
    pre = "if(isReturning&&!fx.zsCounterTraceChecked&&typeof zeroSightPublicCards==='function'){fx.zsCounterTraceChecked=true;const trace=zeroSightPublicCards(w,'zsCounterTrace').find(x=>x.zsCounterTraceCharged);if(trace){trace.zsCounterTraceCharged=false;fx.bonus+=12;if(typeof log==='function')log(`${trace.name}: 역추적 사격 · 이번 반환 누적 위력 +12.`,'good')}}"
    if anchor not in text:
        raise SystemExit('missing resolver pre-return anchor')
    text = text.replace(anchor, pre + anchor, 1)

anchor = "case'zsObserver':"
if "case'zsRangefinder':" not in text:
    cases = r'''case'zsRangefinder':case'zsObservationLog':case'zsSafeDistance':case'zsObserverShift':case'zsCounterTrace':case'zsDrone':case'zsDeadAngle':break;case'zsBreathControl':if(typeof zeroSightTargetMeld==='function'&&zeroSightTargetMeld(w)&&typeof handPreparationReady==='function'&&handPreparationReady(c,1,w)){addShield(w,3);const paused=requestZeroSightCycle(w,c,cards,resume);if(paused)return pause()}break;case'zsSuppressiveFire':if(ctx.isAttach&&ctx.targetOwner===foe&&ctx.meld&&typeof isZeroSightTarget==='function'&&isZeroSightTarget(w,ctx.meld)){const sealed=typeof officialStatusValue==='function'&&officialStatusValue('meld',ctx.meld,'seal')>0;if(sealed&&typeof lockMeldRecovery==='function')lockMeldRecovery(ctx.meld,ctx.targetOwner);else if(typeof applyOfficialStatus==='function')applyOfficialStatus('meld',ctx.meld,'seal',1,{actor:w,silent:true})}break;case'zsCamouflage':if(ctx.meld&&typeof setZeroSightTarget==='function'){setZeroSightTarget(w,ctx.meld,{reason:'camouflage'});if((ctx.meld.cards||[]).filter(x=>x.owner===w).length>=2&&typeof applyOfficialStatus==='function')applyOfficialStatus('meld',ctx.meld,'protect',1,{actor:w,silent:true})}break;case'zsBlindSpot':if(ctx.isAttach&&ctx.targetOwner===foe&&ctx.meld&&(ctx.meld.cards||[]).some(x=>x.uid!==c.uid&&x.owner===w)){if(typeof setZeroSightTarget==='function')setZeroSightTarget(w,ctx.meld,{reason:'blindSpot'});if(state.zeroSightLastRecoverActor===w&&state.zeroSightLastRecoverToken===state.turnToken){const paused=requestZeroSightCycle(w,c,cards,resume);if(paused)return pause()}}break;case'zsArmorPiercing':if(ctx.isAttach&&ctx.targetOwner===foe&&isReturning&&ctx.meld&&typeof isZeroSightTarget==='function'&&isZeroSightTarget(w,ctx.meld)){let pierced=false;if(typeof officialStatusValue==='function'&&officialStatusValue('meld',ctx.meld,'protect')>0&&typeof consumeOfficialStatus==='function'){consumeOfficialStatus('meld',ctx.meld,'protect',1);pierced=true}fx.bonus+=pierced?14:10}break;case'zsReserveMag':if(ctx.isAttach&&ctx.meld&&typeof isZeroSightTarget==='function'&&isZeroSightTarget(w,ctx.meld)&&typeof requestZeroSightTopOrder==='function'){const paused=requestZeroSightTopOrder(w,c,2,resume);if(paused)return pause()}break;case'zsLongShot':if(isReturning&&ctx.meld&&typeof isZeroSightTarget==='function'&&isZeroSightTarget(w,ctx.meld)&&typeof handPreparationReady==='function'&&handPreparationReady(c,2,w))fx.bonus+=16;break;'''
    if anchor not in text:
        raise SystemExit('missing ZERO-SIGHT resolver anchor')
    text = text.replace(anchor, cases + anchor, 1)

# ---------------------------------------------------------------------------
# 6) Unlock the new 14 cards without changing the four existing ZERO-SIGHT
#    timing contracts (starter pair / Ballistics / ONE SHOT).
# ---------------------------------------------------------------------------
unlock_inserts = [
 ("{id:'g1',label:'전체 1클리어',kind:'mixed',when:p=>p.totalClears>=1,items:['S6','H7','D8','C2','ZSCA','ZSC2','DA','D3'],fields:['F1']},", "{id:'zsf1',label:'전체 1클리어 · ZERO-SIGHT 증원',kind:'theme',when:p=>p.totalClears>=1,items:['ZSD2','ZSH3','ZSH4'],fields:[]},"),
 ("{id:'g2',label:'전체 2클리어',kind:'mixed',when:p=>p.totalClears>=2,items:['S8','H5','VSH5','D9','C8','D10','C3'],fields:['F2']},", "{id:'zsf2',label:'전체 2클리어 · ZERO-SIGHT 증원',kind:'theme',when:p=>p.totalClears>=2,items:['ZSS4','ZSC5'],fields:[]},"),
 ("{id:'zs3',label:'전체 3클리어 · ZERO-SIGHT',kind:'theme',when:p=>p.totalClears>=3,items:['ZSD6'],fields:[]},", "{id:'zsf3',label:'전체 3클리어 · ZERO-SIGHT 증원',kind:'theme',when:p=>p.totalClears>=3,items:['ZSC6','ZSH7'],fields:[]},"),
 ("{id:'g4',label:'전체 4클리어',kind:'mixed',when:p=>p.totalClears>=4,items:['SQ','HJ','CJ','CQ','H6','J2'],fields:[]},", "{id:'zsf4',label:'전체 4클리어 · ZERO-SIGHT 증원',kind:'theme',when:p=>p.totalClears>=4,items:['ZSS7','ZSC8'],fields:[]},"),
 ("{id:'g5',label:'전체 5클리어',kind:'mixed',when:p=>p.totalClears>=5,items:['S10','SK','HK','DJ','C10','S4'],fields:['F4']},", "{id:'zsf5',label:'전체 5클리어 · ZERO-SIGHT 증원',kind:'theme',when:p=>p.totalClears>=5,items:['ZSD8','ZSS9'],fields:[]},"),
 ("{id:'g6',label:'전체 6클리어',kind:'mixed',when:p=>p.totalClears>=6,items:['SA','S2','H9','C9','VSCK','J4'],fields:['F6']},", "{id:'zsf6',label:'전체 6클리어 · ZERO-SIGHT 증원',kind:'theme',when:p=>p.totalClears>=6,items:['ZSS10','ZSCJ'],fields:[]},"),
 ("{id:'zs7',label:'전체 7클리어 · ZERO-SIGHT',kind:'theme',when:p=>p.totalClears>=7,items:['ZSSK'],fields:[]},", "{id:'zsf7',label:'전체 7클리어 · ZERO-SIGHT 증원',kind:'theme',when:p=>p.totalClears>=7,items:['ZSSQ'],fields:[]},"),
]
for anchor_line, inserted in unlock_inserts:
    if inserted in text:
        continue
    if anchor_line not in text:
        raise SystemExit(f'missing unlock anchor {anchor_line[:32]}')
    text = text.replace(anchor_line, anchor_line + '\n ' + inserted, 1)

index.write_text(text, encoding='utf-8')

# ---------------------------------------------------------------------------
# 7) Canonical docs / roadmap / full-pool status.
# ---------------------------------------------------------------------------
theme = Path('docs/THEME_GROUPS.md')
t = theme.read_text(encoding='utf-8')
repls = {
"- 2♦ `거리측정기` — 표적 지정/변경 시 덱 위 3장 정렬.": "- 2♦ `거리측정기` — 공개된 동안 내 표적 지정/변경 시 턴당 1회 덱 위 3장의 다음 획득 순서를 정한다.",
"- 3♥ `호흡 조절` — 표적 유지 후 충전, 사용 시 보호막 + 정비.": "- 3♥ `호흡 조절` — 손에서 1턴 준비하고 내 표적이 있으면 사용 시 보호막 12 + 무료 정비.",
"- 4♠ `제압 사격` — 상대 표적 조합에 붙어 봉인 또는 고정.": "- 4♠ `제압 사격` — 상대 표적에 붙을 때 봉인 1, 이미 봉인이 있으면 고정.",
"- 4♥ `위장망` — 자신의 카드가 든 조합을 표적으로 만들며 보호.": "- 4♥ `위장망` — 사용한 조합을 표적으로 만들고 내 카드가 2장 이상이면 보호 1.",
"- 5♣ `사각지대` — 자신의 카드가 들어간 상대 조합으로 표적 이동 + 회수 연계 정비.": "- 5♣ `사각지대` — 내 카드가 이미 든 상대 조합으로 표적 이전. 같은 턴 먼저 회수했다면 무료 정비.",
"- 6♣ `관측 기록` — 표적 장기 유지 후 처음 붙는 자신의 카드에 패순환 보상.": "- 6♣ `관측 기록` — 이 카드가 있는 표적을 다음 턴까지 유지한 뒤 처음 붙이면 턴당 1회 무료 정비.",
"- 7♠ `철갑탄` — 상대 표적 조합 반환 +10, 보호 제거 대응.": "- 7♠ `철갑탄` — 상대 표적 반환 +10, 그 조합의 보호 1을 제거하면 대신 +14.",
"- 7♥ `안전거리` — 표적 조합에서 자신의 카드가 회수되면 보호막.": "- 7♥ `안전거리` — 공개된 동안 내 표적에서 내가 회수하면 턴당 1회 보호막 12.",
"- 8♣ `관측 교대` — 표적 조합에서 회수 후 다른 조합으로 표적 이전.": "- 8♣ `관측 교대` — 이 카드를 내 표적에서 회수하면 다른 공개 조합으로 표적 이전 가능.",
"- 8♦ `예비 탄창` — 표적 조합 확장 시 다음 획득 후보를 미리 본다.": "- 8♦ `예비 탄창` — 내 표적에 붙이면 덱 위 2장의 다음 획득 순서를 정한다.",
"- 9♠ `역추적` — 상대가 표적 조합으로 반환하면 충전, 다음 반환 +12.": "- 9♠ `역추적` — 공개된 동안 상대가 내 표적으로 반환하면 충전, 공개 상태의 내 다음 반환 +12 후 해제.",
"- 10♠ `장거리 사격` — 손에서 2턴 준비 후 표적 반환 +16.": "- 10♠ `장거리 사격` — 손에서 2턴 준비 후 내 표적 반환 +16.",
"- J♣ `관측 드론` — 상대가 새 조합을 만들면 표적 자동 이전 가능 + 정비.": "- J♣ `관측 드론` — 공개된 동안 상대가 새 조합을 만들면 턴당 1회 그 조합으로 표적 자동 이전 + 무료 정비.",
"- Q♠ `데드 앵글` — 상대가 표적 조합을 회수/이동하면 취약 및 아군 카드 보호.": "- Q♠ `데드 앵글` — 이 카드가 내 표적에 있는 동안 상대가 그 표적에서 회수/이동하면 턴당 1회 상대 취약 1 + 남은 내 카드 보호 1.",
}
for a,b in repls.items():
    if a in t: t=t.replace(a,b,1)
if '- [x] ZERO-SIGHT 18/18 풀 카드군 라이브 구현' not in t:
    marker='## ZERO-SIGHT 구현 체크\n\n'
    if marker not in t: raise SystemExit('missing ZERO-SIGHT checklist marker')
    t=t.replace(marker,marker+'- [x] ZERO-SIGHT 18/18 풀 카드군 라이브 구현 — 18개 정의·효과·해금·도감/덱빌더 연결 완료. 신규 14장은 60장 통합 전까지 기존 로그라이크 지역 적 덱과 일반 랜덤 보상 순위에서 우선 제외\n',1)
theme.write_text(t,encoding='utf-8')

plan=Path('docs/THEME_FULL_POOL_PLAN.md')
p=plan.read_text(encoding='utf-8')
p=p.replace('| ZERO-SIGHT | 18 | 4 | 14 | 18/18 |','| ZERO-SIGHT | 18 | 18 | 0 | 18/18 |',1)
p=p.replace('| **합계** | **60** | **30** | **30** | **60/60** |','| **합계** | **60** | **44** | **16** | **60/60** |',1)
p=p.replace('- ZERO-SIGHT: `관측수`, `스코프 조정`, `탄도 계산`, `ONE SHOT`','- ZERO-SIGHT: **18/18 풀 구현 완료**',1)
p=p.replace('### F2 — ZERO-SIGHT 18/18\n\n현재 4장 → 18장으로 완성한다.','### F2 — ZERO-SIGHT 18/18 · 완료\n\n18장 전체 정의·실전 효과·해금·도감/덱빌더 연결을 완료했다. 신규 14장은 60장 통합 전까지 기존 로그라이크 지역 적 덱에는 넣지 않고, 일반 랜덤 보상 순위에서도 후보가 충분할 때 우선 제외한다.',1)
if '**F2 완료 기록**' not in p:
    gate='- V-SIGNAL 회수 및 POINT-BLANK 접전과 같은 조합에서 공존\n'
    if gate in p:p=p.replace(gate,gate+'\n**F2 완료 기록** — 2026-09-03. `tests/zero-sight-full-pool.mjs`와 기존 ZERO-SIGHT 표적/준비/탄도/ONE SHOT/혼합 회귀 및 전체 `tests/*.mjs`를 릴리스 게이트로 사용한다.\n',1)
plan.write_text(p,encoding='utf-8')

road=Path('ROADMAP.md')
r=road.read_text(encoding='utf-8')
if 'ZERO-SIGHT 18/18 풀 카드군 구현' not in r:
    r += '\n\n## 2026-09-03 · ZERO-SIGHT 풀 카드군\n- [x] ZERO-SIGHT 18/18 풀 카드군 구현\n- [x] 신규 14장 실제 효과·해금·도감/덱빌더 연결\n- [x] 표적 1개 계약과 일반/V-SIGNAL 혼합 상호작용 유지\n- [x] 신규 14장 로그라이크 보상은 60장 통합 전까지 staged 처리\n'
road.write_text(r,encoding='utf-8')

# Keep the direct-power minority audit honest as the pool expands.
audit=Path('tests/named-card-audit.mjs')
a=audit.read_text(encoding='utf-8')
a=a.replace("'zsBallistics','zsOneShot'", "'zsBallistics','zsArmorPiercing','zsCounterTrace','zsLongShot','zsOneShot'", 1)
audit.write_text(a,encoding='utf-8')

# ---------------------------------------------------------------------------
# 8) Dedicated full-pool regression.
# ---------------------------------------------------------------------------
test=Path('tests/zero-sight-full-pool.mjs')
test.write_text(r'''import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
const plan=fs.readFileSync(new URL('../docs/THEME_FULL_POOL_PLAN.md',import.meta.url),'utf8');
const theme=fs.readFileSync(new URL('../docs/THEME_GROUPS.md',import.meta.url),'utf8');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const audit=fs.readFileSync(new URL('named-card-audit.mjs',import.meta.url),'utf8');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let par=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')par++;else if(script[i]===')')par--;else if(script[i]==='{'&&par===0){brace=i;break}}if(brace<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
function literal(name,next){const a=script.indexOf(`const ${name}=`);if(a<0)throw new Error(`missing ${name}`);const b=script.indexOf(next,a);if(b<0)throw new Error(`missing end ${name}`);return script.slice(a+`const ${name}=`.length,b).trim().replace(/;$/,'')}
const ctx=vm.createContext({console,Object,Array,Set,Map,Number,String,Boolean,Math});
vm.runInContext(`globalThis.NAMED=${literal('NAMED','\nconst CHARACTERS=')}`,ctx);
const expected={ZSCA:'zsObserver',ZSC2:'zsScopeAdjust',ZSD2:'zsRangefinder',ZSH3:'zsBreathControl',ZSS4:'zsSuppressiveFire',ZSH4:'zsCamouflage',ZSC5:'zsBlindSpot',ZSD6:'zsBallistics',ZSC6:'zsObservationLog',ZSS7:'zsArmorPiercing',ZSH7:'zsSafeDistance',ZSC8:'zsObserverShift',ZSD8:'zsReserveMag',ZSS9:'zsCounterTrace',ZSS10:'zsLongShot',ZSCJ:'zsDrone',ZSSQ:'zsDeadAngle',ZSSK:'zsOneShot'};
const cards=Object.entries(ctx.NAMED).filter(([,d])=>d?.themeId==='zero-sight');
ok(cards.length===18,`ZERO-SIGHT full pool has exactly 18 definitions (${cards.length})`);
ok(new Set(cards.map(([,d])=>d.slot)).size===18,'ZERO-SIGHT cards occupy 18 distinct physical slots');
for(const[id,tag]of Object.entries(expected)){const d=ctx.NAMED[id];ok(!!d,`${id} definition exists`);ok(d.themeId==='zero-sight'&&d.t===tag,`${id} keeps ZERO-SIGHT tag ${tag}`);if(!['ZSCA','ZSC2','ZSD6','ZSSK'].includes(id))ok(d.rewardPool===false,`${id} is staged out of ordinary roguelike rewards until 60-card integration`)}
ok(ctx.NAMED.ZSS10.prepRequired===2&&ctx.NAMED.ZSH3.prepRequired===1,'prepared ZERO-SIGHT cards declare shared handPrep requirements');
for(const tag of ['zsBreathControl','zsSuppressiveFire','zsCamouflage','zsBlindSpot','zsArmorPiercing','zsReserveMag','zsLongShot'])ok(script.includes(`case'${tag}'`),`${tag} has a live resolver branch`);
for(const tag of ['zsRangefinder','zsObservationLog','zsSafeDistance','zsObserverShift','zsCounterTrace','zsDrone','zsDeadAngle'])ok(script.includes(tag)&&script.includes('function handleZeroSightFullThemeEvent('),`${tag} is wired through the passive target-event handler`);
ok(script.includes('function requestZeroSightTopOrder(')&&script.includes('function requestZeroSightRetargetOnly('),'information and recovery target choices use shared resumable helpers');
ok(script.includes('subscribeEffectEvent(handleZeroSightFullThemeEvent);'),'ZERO-SIGHT passive effects subscribe to the shared event bus');
ok(script.includes("typeof zeroSightPublicCards==='function'"),'resolver/event additions remain safe for isolated legacy regression extraction');
const unlock=script.slice(script.indexOf('const UNLOCK_GROUPS='),script.indexOf('function unlockedNamed'));
for(const id of Object.keys(expected))ok(unlock.includes(`'${id}'`),`${id} is reachable through progression unlock groups`);
ok(unlock.includes("items:['S6','H7','D8','C2','ZSCA','ZSC2','DA','D3']"),'existing ZERO-SIGHT starter timing stays untouched');
ok(unlock.includes("items:['ZSD6']")&&unlock.includes("items:['ZSSK']"),'Ballistics and ONE SHOT legacy unlock timings stay untouched');

// Counter Trace: opponent target return charges a public card, next owner return consumes +12.
{
 const handler=source('handleZeroSightFullThemeEvent'),resolve=source('resolveEffects');
 const trace={uid:1,owner:'player',themeId:'zero-sight',tag:'zsCounterTrace',name:'역추적',named:true,zsCounterTraceCharged:false,themeTurnGates:{}};
 const meld={cards:[trace]},player={melds:[meld],hand:[]},enemy={melds:[],hand:[]},state={turnToken:9,turnNo:9,player,enemy};
 const box={globalThis:null,state,sideObj:w=>w==='player'?player:enemy,other:w=>w==='player'?'enemy':'player',meldsOf:w=>w==='player'?player.melds:enemy.melds,themeTurnGateUsed:()=>false,claimThemeTurnGate:()=>true,log:()=>{},consumeOfficialStatus:()=>0};box.globalThis=box;
 box.zeroSightPublicCards=(actor,tag)=>actor==='player'&&tag==='zsCounterTrace'?[trace]:[];
 vm.runInNewContext(`${handler};globalThis.__h=handleZeroSightFullThemeEvent;`,box);
 box.__h({event:'onAttach',actor:'enemy',returned:true,targetedBy:['player'],turnToken:9,meld});
 ok(trace.zsCounterTraceCharged===true,'opponent return through player target charges Counter Trace');
 vm.runInNewContext(`${resolve};globalThis.__r=resolveEffects;`,box);
 const action={meld,effectSeen:new Set(),willReturn:true,isAttach:true,targetOwner:'enemy',totalLength:4};
 const out=box.__r('player',[],'RUN',action);
 ok(out.bonus===12&&!trace.zsCounterTraceCharged,'next owner return consumes Counter Trace for exactly +12');
}

// Long Shot uses shared hand preparation rather than a theme counter.
{
 const resolve=source('resolveEffects'),state={turnToken:12,switchPower:20};
 const box={globalThis:null,state,sideObj:()=>({hand:[]}),other:()=> 'enemy',consumeOfficialStatus:()=>0,isZeroSightTarget:()=>true,handPreparationReady:(c,n)=>c.ready===n};box.globalThis=box;
 vm.runInNewContext(`${resolve};globalThis.__r=resolveEffects;`,box);
 const c={uid:2,named:true,tag:'zsLongShot',name:'장거리 사격',ready:2};
 const out=box.__r('player',[c],'RUN',{meld:{},effectSeen:new Set(),willReturn:true,isAttach:true,targetOwner:'enemy',totalLength:4});
 ok(out.bonus===16,'two-turn prepared Long Shot adds exactly +16 on a target return');
}

ok(!script.includes('zeroSightResource')&&!script.includes('ZERO_SIGHT_COUNT'),'ZERO-SIGHT adds no dedicated numeric resource');
ok(audit.includes("'zsArmorPiercing','zsCounterTrace','zsLongShot'"),'direct-power minority audit counts the new precision modifiers');
ok(theme.includes('ZERO-SIGHT 18/18 풀 카드군 라이브 구현'),'canonical theme document records full implementation');
ok(plan.includes('| ZERO-SIGHT | 18 | 18 | 0 | 18/18 |')&&plan.includes('| **합계** | **60** | **44** | **16** |'),'full-pool plan advances to 44/60 live cards');
ok(road.includes('ZERO-SIGHT 18/18 풀 카드군 구현'),'ROADMAP records ZERO-SIGHT completion');
console.log('ZERO-SIGHT 18/18 full-pool regression passed.');
''',encoding='utf-8')

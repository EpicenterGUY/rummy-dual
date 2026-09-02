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
# 1) POINT-BLANK 18-card definition pool. PBH7/PBDJ remain untouched because
#    existing Red Zone encounters and dedicated regressions already use them.
#    The 16 new cards are staged out of ordinary roguelike rewards until the
#    separate 60-card integration pass.
# ---------------------------------------------------------------------------
defs = [
 ('CA','PBCA', "'PBCA':{slot:'CA',themeId:'point-blank',rewardPool:false,n:'돌입 명령',t:'pbBreachOrder',d:'이 카드를 상대 공개 조합에 붙이면 그 조합을 내 접전으로 지정한다. 이미 같은 조합이 내 접전이면 남은 손패 1장을 무료 정비한다.'},"),
 ('HA','PBHA', "'PBHA':{slot:'HA',themeId:'point-blank',rewardPool:false,n:'브리치 실드',t:'pbBreachShield',d:'이 카드를 상대 공개 조합에 붙이면 그 조합을 내 접전으로 지정하고 보호막 12를 얻는다. 붙이기 전부터 그 조합에 내 카드가 있었다면 대신 보호막 20을 얻는다.'},"),
 ('C2','PBC2', "'PBC2':{slot:'C2',themeId:'point-blank',rewardPool:false,n:'슬라이드 스텝',t:'pbSlideStep',d:'이 카드를 상대 공개 조합에 붙이면 그 조합으로 내 접전을 이전하고 남은 손패 1장을 무료 정비한다.'},"),
 ('H2','PBH2', "'PBH2':{slot:'H2',themeId:'point-blank',rewardPool:false,n:'사이드암',t:'pbSidearm',d:'이 카드를 상대 공개 조합에서 회수하면 이 카드를 소모패로 보내는 것을 선택할 수 있다. 그렇게 하면 카드 2장을 뽑은 뒤 손패 1장을 버린다.'},"),
 ('S3','PBS3', "'PBS3':{slot:'S3',themeId:'point-blank',rewardPool:false,n:'플래시뱅',t:'pbFlashbang',d:'이 카드를 내 접전에 붙이면 그 조합에 봉인 1을 부여한다. 이미 봉인이 있다면 대신 그 조합을 고정한다.'},"),
 ('S4','PBS4', "'PBS4':{slot:'S4',themeId:'point-blank',rewardPool:false,n:'벅샷',t:'pbBuckshot',d:'이 카드로 내 접전에서 스위치를 반환하면 누적 위력이 8 증가한다. 같은 조합에 이 카드 외의 내 카드가 있으면 대신 12 증가한다.'},"),
 ('D4','PBD4', "'PBD4':{slot:'D4',themeId:'point-blank',rewardPool:false,n:'크로스파이어',t:'pbCrossfire',d:'이 카드로 내 접전 세트의 버스트를 완성할 때 내 다른 공개 세트가 있으면 카드 1장을 뽑는다.'},"),
 ('C5','PBC5', "'PBC5':{slot:'C5',themeId:'point-blank',rewardPool:false,n:'문 걷어차기',t:'pbDoorKick',d:'이 카드가 내 접전에 처음 들어가는 내 카드라면, 붙인 뒤 다른 공개 조합에서 내가 제어하는 카드 1장을 무료 회수할 수 있다. 회수 카드의 같은 턴 반환 제한은 유지한다.'},"),
 ('D6','PBD6', "'PBD6':{slot:'D6',themeId:'point-blank',rewardPool:false,n:'탄창 교체',t:'pbReload',d:'이번 턴 붙이기, 회수, 버리기, 정비 중 서로 다른 행동을 2종류 이상 수행한 뒤 이 카드를 사용하면 카드 2장을 뽑고 손패 1장을 덱 아래로 보낸다. 카드당 턴당 1회만 발동한다.'},"),
 ('H6','PBH6', "'PBH6':{slot:'H6',themeId:'point-blank',rewardPool:false,n:'응급 후퇴',t:'pbEmergencyRetreat',d:'스위치가 나를 향할 때 이 카드를 사용하면 보호막 16을 얻고 내 접전에서 내가 제어하는 카드 1장을 무료 회수할 수 있다. 회수 카드의 같은 턴 반환 제한은 유지한다.'},"),
 ('S8','PBS8', "'PBS8':{slot:'S8',themeId:'point-blank',rewardPool:false,n:'영거리 사격',t:'pbZeroRange',d:'내 접전에 내 카드가 2장 이상 있을 때 이 카드로 스위치를 반환하면 누적 위력이 14 증가한다. 런이면 반환 뒤 빼도 유지되는 내 카드 1장을 소모하고, 세트 버스트면 그 세트의 자동 정리가 비용을 대신한다.'},"),
 ('C8','PBC8', "'PBC8':{slot:'C8',themeId:'point-blank',rewardPool:false,n:'백도어',t:'pbBackdoor',d:'내 상대 런 접전과 내 다른 런 사이에서 내가 제어하는 카드 1장을 합법적으로 이동시킬 수 있다. 이동 자체는 체인 위력이나 스위치 반환을 만들지 않는다.'},"),
 ('C9','PBC9', "'PBC9':{slot:'C9',themeId:'point-blank',rewardPool:false,n:'룸 클리어',t:'pbRoomClear',d:'내 접전에서 내가 제어하는 카드 1장을 무료 회수하고, 다른 내 카드 1장을 합법적인 다른 공개 조합으로 이동시킬 수 있다. 두 행동 뒤 모든 조합은 유효해야 하며 이동은 전투 중립이다.'},"),
 ('H10','PBH10', "'PBH10':{slot:'H10',themeId:'point-blank',rewardPool:false,n:'아드레날린',t:'pbAdrenaline',d:'내 접전에서 스위치를 반환하면 보호막 12를 얻는다. 이번 턴에 회수도 했다면 그 접전에 보호 1을 추가로 부여한다.'},"),
 ('CQ','PBCQ', "'PBCQ':{slot:'CQ',themeId:'point-blank',rewardPool:false,n:'돌입대장',t:'pbBreachLeader',d:'이 카드를 사용하면 이번 턴 다음에 내 접전에 붙는 아무 내 카드 1회에 카드 보호 1, 무료 정비, 무료 회수 중 하나를 선택해 부여한다.'},"),
 ('SK','PBSK', "'PBSK':{slot:'SK',themeId:'point-blank',rewardPool:false,n:'탄창 비우기',t:'pbMagDump',d:'이번 턴 내 접전에 붙이기와 회수를 했고 버리기 또는 정비도 했다면, 이 카드로 내 접전에서 스위치를 반환할 때 누적 위력이 16 증가하고 카드 1장을 뽑는다. 카드당 턴당 1회만 발동한다.'},"),
]
for anchor, cid, line in defs:
    text = add_after_named(text, anchor, cid, line)

# ---------------------------------------------------------------------------
# 2) Tendencies. The theme remains an open action module, not a closed deck.
# ---------------------------------------------------------------------------
old = "zsDrone:['control','cycle','interact'],zsDeadAngle:['control','status','sustain'],zsOneShot:['pressure','control','status']"
new = "zsDrone:['control','cycle','interact'],zsDeadAngle:['control','status','sustain'],zsOneShot:['pressure','control','status'],pbBreachOrder:['interact','control','cycle'],pbBreachShield:['interact','sustain'],pbSlideStep:['interact','cycle','control'],pbSidearm:['recover','cycle'],pbFlashbang:['interact','status','control'],pbBuckshot:['pressure','interact'],pbCrossfire:['hold','combo','cycle'],pbDoorKick:['interact','recover','cycle'],pbReload:['cycle','combo'],pbEmergencyRetreat:['recover','sustain'],pbCoverSwap:['interact','sustain','control'],pbZeroRange:['pressure','interact'],pbBackdoor:['interact','extend','combo'],pbRoomClear:['recover','interact','combo'],pbAdrenaline:['sustain','interact'],pbQuickReload:['recover','combo','sustain'],pbBreachLeader:['combo','interact','cycle'],pbMagDump:['pressure','combo','cycle']"
if old in text:
    text = replace_once(text, old, new, 'POINT-BLANK tendencies')
elif new not in text:
    raise SystemExit('unrecognized tendency tail')

# ---------------------------------------------------------------------------
# 3) POINT-BLANK shared action history + choices/movement helpers.
#    This stores only whether common actions happened this turn; it is not a
#    numeric theme resource and all movement routes through the neutral helper.
# ---------------------------------------------------------------------------
if 'function notePointBlankTurnAction(' not in text:
    anchor = "function pointBlankCoverSwapSource(owner,m,targetCard=null){"
    helpers = r'''function pointBlankBlankActions(){return{attach:false,recover:false,discard:false,maintenance:false}}
function pointBlankTurnActions(w){const s=sideObj(w);return s.pbActionToken===state.turnToken&&s.pbActions?{...pointBlankBlankActions(),...s.pbActions}:pointBlankBlankActions()}
function notePointBlankTurnAction(w,kind){if(typeof sideObj!=='function')return pointBlankBlankActions();const s=sideObj(w);if(s.pbActionToken!==state.turnToken){s.pbActionToken=state.turnToken;s.pbActions=pointBlankBlankActions()}if(Object.prototype.hasOwnProperty.call(s.pbActions,kind))s.pbActions[kind]=true;return s.pbActions}
function pointBlankDistinctActionCount(w){return Object.values(pointBlankTurnActions(w)).filter(Boolean).length}
function pointBlankPublicCards(actor,tag=null){const out=[];if(typeof meldsOf!=='function'||typeof other!=='function')return out;for(const side of[actor,other(actor)])for(const m of meldsOf(side))for(const c of m.cards||[])if(c?.owner===actor&&c.themeId==='point-blank'&&(!tag||c.tag===tag))out.push(c);return out}
function pointBlankOtherRecoverCandidates(w,currentMeld=null,exclude=[]){const ex=new Set((exclude||[]).map(c=>c.uid)),out=[];for(const side of[w,other(w)])for(const m of meldsOf(side)){if(m===currentMeld)continue;for(const c of freeRecoverCandidates(w,m,exclude))if(!ex.has(c.uid))out.push({meld:m,card:c})}return out}
function requestPointBlankOtherRecoverChoice(w,source,currentMeld=null,exclude=[],onAsyncResolved=null){const candidates=pointBlankOtherRecoverCandidates(w,currentMeld,exclude);if(!candidates.length){if(typeof onAsyncResolved==='function')onAsyncResolved(null);return false}const apply=x=>x?.meld&&x?.card?recoverSpecificFromMeld(w,x.meld,x.card,{exclude,label:`${source?.name||'POINT-BLANK'} 무료 회수`}):null,interactive=w==='player'&&state.turn==='player'&&typeof requestEffectChoice==='function';if(interactive)return requestEffectChoice({title:source?.name||'POINT-BLANK',text:'다른 공개 조합에서 무료 회수할 내 카드 1장을 고르거나 건너뛸 수 있습니다.',options:candidates.map((x,i)=>({key:`pbrecover:${x.card.uid}:${i}`,label:`${cardText(x.card)}${x.card.named?` · ${x.card.name}`:''}`,detail:`${meldOwnerSide(x.meld)===w?'내':'상대'} ${x.meld.type}`,entry:x})),allowSkip:true,skipLabel:'회수하지 않기',onChoose:o=>{if(o?.entry)apply(o.entry);if(typeof onAsyncResolved==='function')onAsyncResolved(o?.entry||null)}});const chosen=candidates[0];apply(chosen);if(typeof onAsyncResolved==='function')onAsyncResolved(chosen);return false}
function pointBlankDiscardHandCard(w,c,label='POINT-BLANK'){const side=sideObj(w),i=side.hand.findIndex(x=>x.uid===c?.uid);if(i<0)return false;const[chosen]=side.hand.splice(i,1);pushDiscard(chosen);if(typeof notePointBlankTurnAction==='function')notePointBlankTurnAction(w,'discard');if(w==='player')state.lastPlayerDiscardRank=chosen.rank;else state.lastEnemyDiscardRank=chosen.rank;if(typeof log==='function')log(`${label}: ${cardText(chosen)}를 손패에서 버렸습니다.`,'important');return true}
function requestPointBlankHandDiscard(w,source,onAsyncResolved=null){const side=sideObj(w),candidates=[...side.hand];if(!candidates.length){if(typeof onAsyncResolved==='function')onAsyncResolved(null);return false}const apply=c=>pointBlankDiscardHandCard(w,c,source?.name||'사이드암'),interactive=w==='player'&&state.turn==='player'&&typeof requestEffectChoice==='function'&&candidates.length>1;if(interactive)return requestEffectChoice({title:source?.name||'사이드암',text:'2장을 뽑았습니다. 버릴 손패 1장을 고르세요.',options:candidates.map(c=>({key:`pbdiscard:${c.uid}`,label:`${cardText(c)}${c.named?` · ${c.name}`:''}`,detail:'공용 버림패로 이동',card:c})),onChoose:o=>{if(o?.card)apply(o.card);if(typeof onAsyncResolved==='function')onAsyncResolved(o?.card||null)}});const chosen=w==='enemy'&&typeof aiKeepScore==='function'?[...candidates].sort((a,b)=>aiKeepScore(a,side.hand)-aiKeepScore(b,side.hand))[0]:candidates[0];apply(chosen);if(typeof onAsyncResolved==='function')onAsyncResolved(chosen);return false}
function pointBlankConvertSidearm(w,c){const side=sideObj(w),i=side.hand.findIndex(x=>x.uid===c?.uid);if(i<0)return false;side.hand.splice(i,1);side.spent.push(c);c.fromDiscard=false;c.contractActive=false;c.age=0;drawMany(w,2,false);const later=typeof queueMicrotask==='function'?queueMicrotask:fn=>fn();later(()=>requestPointBlankHandDiscard(w,c));if(typeof log==='function')log(`${c.name}: 소모패 전환 · 2장 뽑은 뒤 1장을 버립니다.`,'good');return true}
function requestPointBlankSidearmChoice(w,c){if(!c||c.owner!==w)return false;if(w==='player'&&state.turn==='player'&&typeof requestEffectChoice==='function')return requestEffectChoice({title:c.name,text:'회수한 사이드암을 그대로 손에 둘지, 소모패로 전환해 2장을 뽑고 1장을 버릴지 선택하세요.',options:[{key:'keep',label:'손에 유지',detail:'추가 효과 없음'},{key:'convert',label:'소모패 전환',detail:'2장 뽑기 → 손패 1장 버리기'}],onChoose:o=>{if(o?.key==='convert')pointBlankConvertSidearm(w,c)}});return pointBlankConvertSidearm(w,c)}
function pointBlankMoveCandidateLegal(w,source,target,c){if(!source||!target||source===target||!c||c.owner!==w||meldFixedActive(source)||meldFixedActive(target)||cardFixedActive(c))return false;const remain=source.cards.filter(x=>x.uid!==c.uid),added=target.cards.concat(c);return remain.length>=3&&meldType(remain)===source.type&&meldType(added)===target.type}
function pointBlankBackdoorCandidates(w){const clash=pointBlankClashMeld(w);if(!clash||clash.type!=='RUN')return[];const ownRuns=meldsOf(w).filter(m=>m!==clash&&m.type==='RUN'),out=[];for(const own of ownRuns)for(const[source,target]of[[clash,own],[own,clash]])for(const c of source.cards||[])if(pointBlankMoveCandidateLegal(w,source,target,c))out.push({source,target,card:c});return out}
function requestPointBlankBackdoorChoice(w,sourceCard,onAsyncResolved=null){const candidates=pointBlankBackdoorCandidates(w);if(!candidates.length){if(typeof onAsyncResolved==='function')onAsyncResolved(null);return false}const apply=x=>moveCardBetweenMelds(w,x.card,x.source,x.target,{reason:'pointBlankBackdoor'}),interactive=w==='player'&&state.turn==='player'&&typeof requestEffectChoice==='function'&&candidates.length>1;if(interactive)return requestEffectChoice({title:sourceCard?.name||'백도어',text:'접전 런과 내 다른 런 사이에서 이동할 내 카드를 고르세요. 이동 자체는 전투 중립입니다.',options:candidates.map((x,i)=>({key:`pbback:${x.card.uid}:${i}`,label:`${cardText(x.card)}${x.card.named?` · ${x.card.name}`:''}`,detail:`${meldOwnerSide(x.source)===w?'내 런':'접전 런'} → ${meldOwnerSide(x.target)===w?'내 런':'접전 런'}`,entry:x})),allowSkip:true,skipLabel:'이동하지 않기',onChoose:o=>{if(o?.entry)apply(o.entry);if(typeof onAsyncResolved==='function')onAsyncResolved(o?.entry||null)}});const chosen=candidates[0];apply(chosen);if(typeof onAsyncResolved==='function')onAsyncResolved(chosen);return false}
function pointBlankRoomClearCandidates(w){const clash=pointBlankClashMeld(w);if(!clash||meldFixedActive(clash))return[];const out=[],targets=[];for(const side of[w,other(w)])for(const m of meldsOf(side))if(m!==clash&&!meldFixedActive(m))targets.push(m);for(const recover of clash.cards||[]){if(recover.owner!==w||cardFixedActive(recover)||recover.enteredMeldToken===state.turnToken)continue;const afterRecover=clash.cards.filter(c=>c.uid!==recover.uid);if(afterRecover.length<3||meldType(afterRecover)!==clash.type)continue;for(const moving of afterRecover){if(moving.owner!==w||moving.uid===recover.uid||cardFixedActive(moving)||moving.enteredMeldToken===state.turnToken)continue;const afterBoth=afterRecover.filter(c=>c.uid!==moving.uid);if(afterBoth.length<3||meldType(afterBoth)!==clash.type)continue;for(const target of targets)if(meldType(target.cards.concat(moving))===target.type)out.push({clash,recover,moving,target})}return out}
function executePointBlankRoomClear(w,x){if(!x?.clash||!x?.recover||!x?.moving||!x?.target)return false;const recovered=recoverSpecificFromMeld(w,x.clash,x.recover,{label:'룸 클리어 무료 회수'});if(!recovered)return false;const moved=moveCardBetweenMelds(w,x.moving,x.clash,x.target,{reason:'pointBlankRoomClear'});return !!moved}
function requestPointBlankRoomClearChoice(w,sourceCard,onAsyncResolved=null){const candidates=pointBlankRoomClearCandidates(w);if(!candidates.length){if(typeof onAsyncResolved==='function')onAsyncResolved(null);return false}const apply=x=>executePointBlankRoomClear(w,x),interactive=w==='player'&&state.turn==='player'&&typeof requestEffectChoice==='function';if(interactive)return requestEffectChoice({title:sourceCard?.name||'룸 클리어',text:'접전에서 회수할 카드와 다른 조합으로 이동할 카드를 한 묶음으로 고르세요.',options:candidates.map((x,i)=>({key:`pbroom:${i}`,label:`회수 ${cardText(x.recover)} · 이동 ${cardText(x.moving)}`,detail:`이동 대상 ${meldOwnerSide(x.target)===w?'내':'상대'} ${x.target.type}`,entry:x})),allowSkip:true,skipLabel:'실행하지 않기',onChoose:o=>{if(o?.entry)apply(o.entry);if(typeof onAsyncResolved==='function')onAsyncResolved(o?.entry||null)}});const chosen=candidates[0];apply(chosen);if(typeof onAsyncResolved==='function')onAsyncResolved(chosen);return false}
function pointBlankSpendCandidates(w,m){if(!m||m.type!=='RUN')return[];return(m.cards||[]).filter(c=>c.owner===w&&!cardFixedActive(c)&&(()=>{const remain=m.cards.filter(x=>x.uid!==c.uid);return remain.length>=3&&meldType(remain)===m.type})())}
function spendPointBlankMeldCard(w,m,source=null){const c=pointBlankSpendCandidates(w,m)[0];if(!c)return null;const i=m.cards.findIndex(x=>x.uid===c.uid);if(i<0)return null;m.cards.splice(i,1);m.chain=Math.max(0,(m.chain||0)-1);sideObj(c.owner).spent.push(c);markSetCompletion(m,meldOwnerSide(m));if(typeof emitZeroSightTargetChange==='function')emitZeroSightTargetChange('spend',m,{actionActor:w,card:c,reason:'zeroRange'});if(typeof refreshPointBlankClashMeld==='function')refreshPointBlankClashMeld(m,{change:'spend',actionActor:w,card:c,reason:'zeroRange'});if(typeof log==='function')log(`${source?.name||'영거리 사격'}: ${cardText(c)}를 소모패로 보내 비용을 지불했습니다.`,'important');return c}
function resolvePointBlankPostReturn(w,m,fxState={}){if(fxState.pointBlankZeroRangeSpendMeld===m&&m?.type==='RUN'){spendPointBlankMeldCard(w,m,fxState.pointBlankZeroRangeSource||null);fxState.pointBlankZeroRangeSpendMeld=null;return true}return false}
function pointBlankLeaderReady(w){const s=sideObj(w),r=s.pbLeaderReady;return r&&r.token===state.turnToken?r:null}
function armPointBlankLeader(w,c){const s=sideObj(w);s.pbLeaderReady={token:state.turnToken,sourceUid:c.uid,sourceName:c.name};if(typeof log==='function')log(`${c.name}: 이번 턴 다음 접전 붙이기에 돌입 지원을 준비했습니다.`,'good');return true}
function consumePointBlankLeaderReady(w){const s=sideObj(w),r=pointBlankLeaderReady(w);s.pbLeaderReady=null;return r}
function requestPointBlankLeaderReward(w,packet,ready){const meld=packet?.meld,attached=(packet?.cards||[]).filter(c=>c.owner===w),cycleReady=sideObj(w).hand.length>0,recoverReady=freeRecoverCandidates(w,meld,packet.cards||[]).length>0,protectReady=attached.length>0,options=[];if(protectReady)options.push({key:'protect',label:'진입 보호',detail:'이번에 붙인 내 카드 1장에 보호 1'});if(cycleReady)options.push({key:'cycle',label:'진입 정비',detail:'남은 손패 1장 무료 정비'});if(recoverReady)options.push({key:'recover',label:'돌입 회수',detail:'접전의 다른 내 카드 1장 무료 회수'});if(!options.length)return false;const apply=key=>{if(key==='protect'&&attached[0])applyOfficialStatus('card',attached[0],'protect',1,{actor:w,silent:true});else if(key==='cycle')requestZeroSightCycle(w,{name:ready?.sourceName||'돌입대장'},packet.cards||[]);else if(key==='recover')requestFreeRecoverChoice(w,meld,packet.cards||[],{title:ready?.sourceName||'돌입대장',label:'돌입대장 무료 회수',allowSkip:false})},interactive=w==='player'&&state.turn==='player'&&typeof requestEffectChoice==='function'&&options.length>1;if(interactive)return requestEffectChoice({title:ready?.sourceName||'돌입대장',text:'이번 접전 진입에 적용할 지원 하나를 선택하세요.',options,onChoose:o=>apply(o?.key)});const key=recoverReady?'recover':protectReady?'protect':'cycle';apply(key);return false}
'''
    if anchor not in text:
        raise SystemExit('missing POINT-BLANK helper anchor')
    text = text.replace(anchor, helpers + anchor, 1)

# ---------------------------------------------------------------------------
# 4) Extend passive POINT-BLANK event handling without altering the existing
#    Quick Reload subscriber that old regressions exercise in isolation.
# ---------------------------------------------------------------------------
if 'function handlePointBlankFullThemeEvent(' not in text:
    anchor = "subscribeEffectEvent(handlePointBlankThemeEvent);"
    handler = r'''
function handlePointBlankFullThemeEvent(packet){
 if(!packet?.event||typeof sideObj!=='function'||typeof other!=='function')return false;
 const actor=packet.actor;
 if(packet.event==='onRecover'){
  if(typeof notePointBlankTurnAction==='function')notePointBlankTurnAction(actor,'recover');
  const c=packet.card;if(c?.owner===actor&&c.themeId==='point-blank'&&c.tag==='pbSidearm'&&packet.targetSide===other(actor)){if(typeof requestPointBlankSidearmChoice==='function')requestPointBlankSidearmChoice(actor,c);return true}
 }
 if(packet.event==='onAttach'){
  if(typeof notePointBlankTurnAction==='function')notePointBlankTurnAction(actor,'attach');
  const ready=typeof pointBlankLeaderReady==='function'?pointBlankLeaderReady(actor):null;if(ready&&packet.meld&&typeof isPointBlankClash==='function'&&isPointBlankClash(actor,packet.meld)&&!(packet.cards||[]).some(c=>c.uid===ready.sourceUid)){if(typeof consumePointBlankLeaderReady==='function')consumePointBlankLeaderReady(actor);if(typeof requestPointBlankLeaderReward==='function')requestPointBlankLeaderReward(actor,packet,ready);return true}
 }
 return false
}
subscribeEffectEvent(handlePointBlankFullThemeEvent);'''
    text = text.replace(anchor, anchor + handler, 1)

# ---------------------------------------------------------------------------
# 5) Record common action history at the actual engine routes.
# ---------------------------------------------------------------------------
old = "s.maintenanceUsed=true;s.actedThisTurn=true;if(typeof getCirculationStats==='function')"
new = "s.maintenanceUsed=true;s.actedThisTurn=true;if(typeof notePointBlankTurnAction==='function')notePointBlankTurnAction(w,'maintenance');if(typeof getCirculationStats==='function')"
if old in text:
    text = replace_once(text, old, new, 'maintenance action tracking')
elif new not in text:
    raise SystemExit('unrecognized maintenance tracking route')

old = "const c=cs[0];if(!tutorialAllows('discard',{card:c}))"
new = "const c=cs[0];if(typeof notePointBlankTurnAction==='function')notePointBlankTurnAction('player','discard');if(!tutorialAllows('discard',{card:c}))"
if old in text:
    text = replace_once(text, old, new, 'player discard tracking')
elif new not in text:
    raise SystemExit('unrecognized player discard route')

old = "if(!d)break;lastDiscarded=d;removeFromHand('enemy',[d]);"
new = "if(!d)break;lastDiscarded=d;if(typeof notePointBlankTurnAction==='function')notePointBlankTurnAction('enemy','discard');removeFromHand('enemy',[d]);"
if old in text:
    text = replace_once(text, old, new, 'AI discard tracking')
elif new not in text:
    raise SystemExit('unrecognized AI discard route')

# ---------------------------------------------------------------------------
# 6) Resolver branches. Current attach counts before PB payoff checks so Reload
#    and Mag Dump can legally use the action that is being resolved.
# ---------------------------------------------------------------------------
old = "const effectCards=fx.effectCards,pause=()=>({bonus:fx.bonus||0,flatReturn:!!fx.flatReturn,forceReturn:!!fx.forceReturn,pending:true});"
new = "const effectCards=fx.effectCards,pause=()=>({bonus:fx.bonus||0,flatReturn:!!fx.flatReturn,forceReturn:!!fx.forceReturn,pending:true});if(ctx.isAttach&&typeof notePointBlankTurnAction==='function')notePointBlankTurnAction(w,'attach');"
if old in text:
    text = replace_once(text, old, new, 'resolver PB attach history')
elif new not in text:
    raise SystemExit('unrecognized resolver pause anchor')

anchor = "case'zsRangefinder':"
if "case'pbBreachOrder':" not in text:
    cases = r'''case'pbBreachOrder':if(ctx.isAttach&&ctx.targetOwner===foe&&ctx.meld){const already=typeof isPointBlankClash==='function'&&isPointBlankClash(w,ctx.meld);if(already){if(typeof requestZeroSightCycle==='function'){const paused=requestZeroSightCycle(w,c,cards,resume);if(paused)return pause()}}else if(typeof setPointBlankClash==='function')setPointBlankClash(w,ctx.meld,{reason:'breachOrder'})}break;case'pbBreachShield':if(ctx.isAttach&&ctx.targetOwner===foe&&ctx.meld){const hadOwn=(ctx.meld.cards||[]).some(x=>x.owner===w&&!cards.some(y=>y.uid===x.uid));if(typeof setPointBlankClash==='function')setPointBlankClash(w,ctx.meld,{reason:'breachShield'});addShield(w,hadOwn?5:3)}break;case'pbSlideStep':if(ctx.isAttach&&ctx.targetOwner===foe&&ctx.meld){if(typeof setPointBlankClash==='function')setPointBlankClash(w,ctx.meld,{reason:'slideStep'});if(typeof requestZeroSightCycle==='function'){const paused=requestZeroSightCycle(w,c,cards,resume);if(paused)return pause()}}break;case'pbSidearm':case'pbCoverSwap':case'pbQuickReload':break;case'pbFlashbang':if(ctx.isAttach&&ctx.meld&&typeof isPointBlankClash==='function'&&isPointBlankClash(w,ctx.meld)){const sealed=typeof officialStatusValue==='function'&&officialStatusValue('meld',ctx.meld,'seal')>0;if(sealed&&typeof lockMeldRecovery==='function')lockMeldRecovery(ctx.meld,ctx.targetOwner);else if(typeof applyOfficialStatus==='function')applyOfficialStatus('meld',ctx.meld,'seal',1,{actor:w,silent:true})}break;case'pbBuckshot':if(isReturning&&ctx.meld&&typeof isPointBlankClash==='function'&&isPointBlankClash(w,ctx.meld)){const otherOwn=(ctx.meld.cards||[]).some(x=>x.owner===w&&x.uid!==c.uid&&!cards.some(y=>y.uid===x.uid));fx.bonus+=otherOwn?12:8}break;case'pbCrossfire':if(ctx.isAttach&&type==='SET'&&ctx.totalLength===4&&ctx.meld&&typeof isPointBlankClash==='function'&&isPointBlankClash(w,ctx.meld)&&meldsOf(w).some(m=>m!==ctx.meld&&m.type==='SET'))drawOne(w,false);break;case'pbDoorKick':if(ctx.isAttach&&ctx.meld&&typeof isPointBlankClash==='function'&&isPointBlankClash(w,ctx.meld)){const priorOwn=(ctx.meld.cards||[]).filter(x=>x.owner===w&&!cards.some(y=>y.uid===x.uid)).length;if(priorOwn===0&&(!(typeof themeTurnGateUsed==='function')||!themeTurnGateUsed(c,'pbDoorKick',state.turnToken))){if(typeof claimThemeTurnGate==='function')claimThemeTurnGate(c,'pbDoorKick',state.turnToken);if(typeof requestPointBlankOtherRecoverChoice==='function'){const paused=requestPointBlankOtherRecoverChoice(w,c,ctx.meld,cards,resume);if(paused)return pause()}}}break;case'pbReload':if(typeof pointBlankDistinctActionCount==='function'&&pointBlankDistinctActionCount(w)>=2&&(!(typeof themeTurnGateUsed==='function')||!themeTurnGateUsed(c,'pbReload',state.turnToken))){if(typeof claimThemeTurnGate==='function')claimThemeTurnGate(c,'pbReload',state.turnToken);drawMany(w,2,false);if(typeof requestHandBottomChoice==='function'){const paused=requestHandBottomChoice(w,{title:c.name,label:c.name,text:'탄창 교체로 2장을 뽑았습니다. 덱 아래로 보낼 손패 1장을 고르세요.',onAsyncResolved:resume});if(paused)return pause()}}break;case'pbEmergencyRetreat':if(state.switchTarget===w){addShield(w,4);const clash=typeof pointBlankClashMeld==='function'?pointBlankClashMeld(w):null;if(clash&&typeof requestFreeRecoverChoice==='function'){const paused=requestFreeRecoverChoice(w,clash,cards,{title:c.name,label:c.name,allowSkip:true,text:'접전에서 무료 회수할 내 카드 1장을 고르거나 건너뛸 수 있습니다.',onAsyncResolved:resume});if(paused)return pause()}}break;case'pbZeroRange':if(isReturning&&ctx.meld&&typeof isPointBlankClash==='function'&&isPointBlankClash(w,ctx.meld)&&(ctx.meld.cards||[]).filter(x=>x.owner===w).length>=2){const canPay=ctx.meld.type==='SET'&&ctx.totalLength===4||typeof pointBlankSpendCandidates==='function'&&pointBlankSpendCandidates(w,ctx.meld).length>0;if(canPay){fx.bonus+=14;if(ctx.meld.type==='RUN'){fx.pointBlankZeroRangeSpendMeld=ctx.meld;fx.pointBlankZeroRangeSource=c}}}break;case'pbBackdoor':if(typeof requestPointBlankBackdoorChoice==='function'){const paused=requestPointBlankBackdoorChoice(w,c,resume);if(paused)return pause()}break;case'pbRoomClear':if(typeof requestPointBlankRoomClearChoice==='function'){const paused=requestPointBlankRoomClearChoice(w,c,resume);if(paused)return pause()}break;case'pbAdrenaline':if(isReturning&&ctx.meld&&typeof isPointBlankClash==='function'&&isPointBlankClash(w,ctx.meld)){addShield(w,3);const a=typeof pointBlankTurnActions==='function'?pointBlankTurnActions(w):null;if(a?.recover&&typeof applyOfficialStatus==='function')applyOfficialStatus('meld',ctx.meld,'protect',1,{actor:w,silent:true})}break;case'pbBreachLeader':if(typeof armPointBlankLeader==='function')armPointBlankLeader(w,c);break;case'pbMagDump':if(isReturning&&ctx.isAttach&&ctx.meld&&typeof isPointBlankClash==='function'&&isPointBlankClash(w,ctx.meld)){const a=typeof pointBlankTurnActions==='function'?pointBlankTurnActions(w):null;if(a?.attach&&a?.recover&&(a?.discard||a?.maintenance)&&(!(typeof themeTurnGateUsed==='function')||!themeTurnGateUsed(c,'pbMagDump',state.turnToken))){if(typeof claimThemeTurnGate==='function')claimThemeTurnGate(c,'pbMagDump',state.turnToken);fx.bonus+=16;drawOne(w,false)}}break;'''
    if anchor not in text:
        raise SystemExit('missing resolver ZERO/PB anchor')
    text = text.replace(anchor, cases + anchor, 1)

# Resolve Zero Range cost after the attack event has returned SWITCH, but before
# automatic SET retirement. A 4-card SET already pays by retiring as normal.
old = "if((returning||forceReturn)&&typeof resolveZeroSightPostReturn==='function')resolveZeroSightPostReturn(w,m,ctx.fxState||{});"
new = "if((returning||forceReturn)&&typeof resolveZeroSightPostReturn==='function')resolveZeroSightPostReturn(w,m,ctx.fxState||{});if((returning||forceReturn)&&typeof resolvePointBlankPostReturn==='function')resolvePointBlankPostReturn(w,m,ctx.fxState||{});"
if old in text:
    text = replace_once(text, old, new, 'POINT-BLANK post-return hook')
elif new not in text:
    raise SystemExit('unrecognized post-return hook')

# ---------------------------------------------------------------------------
# 7) Unlock all 18 POINT-BLANK cards in separate themed progression groups.
# ---------------------------------------------------------------------------
if "{id:'pbf1'" not in text:
    marker = "const UNLOCK_GROUPS=[\n"
    groups = """ {id:'pbf1',label:'전체 1클리어 · POINT-BLANK',kind:'theme',when:p=>p.totalClears>=1,items:['PBCA','PBHA','PBC2'],fields:[]},
 {id:'pbf2',label:'전체 2클리어 · POINT-BLANK',kind:'theme',when:p=>p.totalClears>=2,items:['PBH2','PBS3'],fields:[]},
 {id:'pbf3',label:'전체 3클리어 · POINT-BLANK',kind:'theme',when:p=>p.totalClears>=3,items:['PBS4','PBD4','PBH7'],fields:[]},
 {id:'pbf4',label:'전체 4클리어 · POINT-BLANK',kind:'theme',when:p=>p.totalClears>=4,items:['PBC5','PBD6','PBH6'],fields:[]},
 {id:'pbf5',label:'전체 5클리어 · POINT-BLANK',kind:'theme',when:p=>p.totalClears>=5,items:['PBS8','PBC8'],fields:[]},
 {id:'pbf6',label:'전체 6클리어 · POINT-BLANK',kind:'theme',when:p=>p.totalClears>=6,items:['PBC9','PBH10','PBDJ'],fields:[]},
 {id:'pbf7',label:'전체 7클리어 · POINT-BLANK',kind:'theme',when:p=>p.totalClears>=7,items:['PBCQ','PBSK'],fields:[]},
"""
    if marker not in text:
        raise SystemExit('missing unlock group array')
    text = text.replace(marker, marker + groups, 1)

index.write_text(text, encoding='utf-8')

# ---------------------------------------------------------------------------
# 8) Canonical docs / roadmap / full-pool status.
# ---------------------------------------------------------------------------
theme = Path('docs/THEME_GROUPS.md')
t = theme.read_text(encoding='utf-8')
repls = {
"- A♣ `돌입 명령` — 상대 조합 접전 지정, 이미 접전이면 무료 정비.": "- A♣ `돌입 명령` — 상대 조합에 붙이면 그 조합을 접전으로 지정한다. 이미 같은 조합이 접전이면 무료 정비한다.",
"- A♥ `브리치 실드` — 새 접전 지정 시 보호막, 이미 자신의 카드가 있으면 강화.": "- A♥ `브리치 실드` — 상대 조합에 붙이면 접전으로 지정하고 보호막 12를 얻는다. 붙이기 전부터 내 카드가 있었다면 보호막 20을 얻는다.",
"- 2♣ `슬라이드 스텝` — 자신의 카드가 상대 조합에 붙을 때 접전 이전 + 정비.": "- 2♣ `슬라이드 스텝` — 상대 조합에 붙이면 그 조합으로 접전을 이전하고 무료 정비한다.",
"- 2♥ `사이드암` — 상대 조합에서 회수 시 소모패 전환을 선택해 2장 뽑고 1장 버리기.": "- 2♥ `사이드암` — 상대 조합에서 회수하면 소모패 전환을 선택할 수 있다. 전환하면 2장을 뽑고 손패 1장을 버린다.",
"- 3♠ `플래시뱅` — 접전 조합에 봉인 또는 고정.": "- 3♠ `플래시뱅` — 접전에 붙이면 봉인 1을 부여하고, 이미 봉인이 있으면 대신 고정한다.",
"- 4♠ `벅샷` — 접전 반환 +8, 같은 조합에 자신의 다른 카드가 있으면 +12.": "- 4♠ `벅샷` — 접전에서 반환하면 누적 위력이 8 증가한다. 같은 조합에 다른 내 카드가 있으면 대신 12 증가한다.",
"- 4♦ `크로스파이어` — 접전 세트와 자신의 세트를 연결, 버스트 시 카드 획득.": "- 4♦ `크로스파이어` — 접전 세트의 버스트를 완성할 때 내 다른 공개 세트가 있으면 카드 1장을 뽑는다.",
"- 5♣ `문 걷어차기` — 처음 접전에 붙인 뒤 자신의 다른 공개 카드 무료 회수.": "- 5♣ `문 걷어차기` — 접전에 처음 들어가는 내 카드라면 다른 공개 조합의 내 카드 1장을 무료 회수할 수 있다. 같은 턴 반환 제한은 유지한다.",
"- 6♦ `탄창 교체` — 붙이기/회수/버리기/정비 중 서로 다른 2개 수행 시 2장 뽑고 1장 덱 아래.": "- 6♦ `탄창 교체` — 한 턴에 붙이기·회수·버리기·정비 중 서로 다른 행동 2종류 이상을 수행한 뒤 사용하면 2장을 뽑고 손패 1장을 덱 아래로 보낸다. 카드당 턴당 1회만 발동한다.",
"- 6♥ `응급 후퇴` — 스위치가 자신을 향할 때 접전 카드 무료 회수 + 보호막 16.": "- 6♥ `응급 후퇴` — 스위치가 자신을 향할 때 사용하면 보호막 16을 얻고 접전의 내 카드 1장을 무료 회수할 수 있다. 같은 턴 반환 제한은 유지한다.",
"- 8♠ `영거리 사격` — 접전에 자신의 카드 2장 이상이면 반환 +14 후 자신의 카드 1장 소모.": "- 8♠ `영거리 사격` — 접전에 내 카드가 2장 이상일 때 반환하면 누적 위력이 14 증가한다. 런이면 빼도 유지되는 내 카드 1장을 소모하고, 세트 버스트면 자동 정리가 비용을 대신한다.",
"- 8♣ `백도어` — 상대 런 접전과 자신의 다른 런 사이 카드 이동.": "- 8♣ `백도어` — 상대 런 접전과 내 다른 런 사이에서 내 카드 1장을 합법적으로 이동할 수 있다. 이동 자체는 전투 중립이다.",
"- 9♣ `룸 클리어` — 접전 카드 하나 회수 + 다른 하나를 합법적인 다른 조합으로 이동.": "- 9♣ `룸 클리어` — 접전의 내 카드 1장을 무료 회수하고 다른 내 카드 1장을 합법적인 다른 조합으로 이동할 수 있다. 두 행동 뒤 모든 조합은 유효해야 하며 이동은 전투 중립이다.",
"- 10♥ `아드레날린` — 접전 반환 시 보호막, 같은 턴 회수까지 했다면 후속 방어.": "- 10♥ `아드레날린` — 접전에서 반환하면 보호막 12를 얻는다. 같은 턴 회수도 했다면 접전에 보호 1을 추가로 부여한다.",
"- Q♣ `돌입대장` — 다음에 접전에 붙는 **아무 카드**에게 보호/정비/무료 회수 중 하나 부여.": "- Q♣ `돌입대장` — 사용한 턴 다음 접전 붙이기 1회에 아무 내 카드도 이용할 수 있는 카드 보호 1·무료 정비·무료 회수 중 하나를 선택해 부여한다.",
"- K♠ `탄창 비우기` — 접전 붙이기 + 회수 + 버리기/정비를 모두 수행한 턴의 반환 +16 + 카드 획득.": "- K♠ `탄창 비우기` — 같은 턴 접전 붙이기와 회수, 그리고 버리기 또는 정비까지 수행한 뒤 접전에서 반환하면 누적 위력이 16 증가하고 카드 1장을 뽑는다. 카드당 턴당 1회만 발동한다.",
}
for a,b in repls.items():
    if a in t:
        t=t.replace(a,b,1)
if '- [x] POINT-BLANK 18/18 풀 카드군 라이브 구현' not in t:
    marker='## POINT-BLANK 구현 체크\n\n'
    if marker not in t: raise SystemExit('missing POINT-BLANK checklist marker')
    t=t.replace(marker,marker+'- [x] POINT-BLANK 18/18 풀 카드군 라이브 구현 — 18개 정의·효과·해금·도감/덱빌더 연결 완료. 신규 16장은 60장 통합 전까지 기존 로그라이크 지역 적 덱과 일반 랜덤 보상 순위에서 우선 제외\n',1)
theme.write_text(t,encoding='utf-8')

plan=Path('docs/THEME_FULL_POOL_PLAN.md')
p=plan.read_text(encoding='utf-8')
p=p.replace('| POINT-BLANK | 18 | 2 | 16 | 18/18 |','| POINT-BLANK | 18 | 18 | 0 | 18/18 |',1)
p=p.replace('| **합계** | **60** | **44** | **16** | **60/60** |','| **합계** | **60** | **60** | **0** | **60/60** |',1)
p=p.replace('- POINT-BLANK: `엄폐 교대`, `퀵 리로드`','- POINT-BLANK: **18/18 풀 구현 완료**',1)
p=p.replace('### F3 — POINT-BLANK 18/18\n\n현재 2장 → 18장으로 완성한다.','### F3 — POINT-BLANK 18/18 · 완료\n\n18장 전체 정의·실전 효과·해금·도감/덱빌더 연결을 완료했다. 신규 16장은 60장 통합 전까지 기존 로그라이크 지역 적 덱에는 넣지 않고, 일반 랜덤 보상 순위에서도 후보가 충분할 때 우선 제외한다.',1)
if '**F3 완료 기록**' not in p:
    gate='- 이동 자체는 버스트/체인/스위치 반환을 만들지 않는 전투 중립 유지\n'
    if gate in p:p=p.replace(gate,gate+'\n**F3 완료 기록** — 2026-09-03. `tests/point-blank-full-pool.mjs`와 기존 접전/이동/회수/퀵 리로드 회귀 및 전체 `tests/*.mjs`를 릴리스 게이트로 사용한다. 세 카드군 정식 후보 60장은 모두 개별 구현되었으며, 보상·적 덱·튜토리얼을 다시 배치하는 60장 통합 단계는 별도로 진행한다.\n',1)
plan.write_text(p,encoding='utf-8')

road=Path('ROADMAP.md')
r=road.read_text(encoding='utf-8')
if 'POINT-BLANK 18/18 풀 카드군 구현' not in r:
    r += '\n\n## 2026-09-03 · POINT-BLANK 풀 카드군\n- [x] POINT-BLANK 18/18 풀 카드군 구현\n- [x] 신규 16장 실제 효과·해금·도감/덱빌더 연결\n- [x] 접전 1개·지연 해제·전투 중립 이동·기본/무료 회수 계약 유지\n- [x] 붙이기/회수/버리기/정비 공용 행동 이력을 전용 숫자 자원 없이 재사용\n- [x] 신규 16장 로그라이크 보상은 60장 통합 전까지 staged 처리\n'
road.write_text(r,encoding='utf-8')

# Direct SWITCH/power minority audit: preserve the contiguous ZERO strings that
# existing dedicated tests search for, then append the three PB finishers.
audit=Path('tests/named-card-audit.mjs')
a=audit.read_text(encoding='utf-8')
old="'zsArmorPiercing','zsCounterTrace','zsLongShot','zsBallistics','zsOneShot'"
new="'zsArmorPiercing','zsCounterTrace','zsLongShot','zsBallistics','zsOneShot','pbBuckshot','pbZeroRange','pbMagDump'"
if old in a:
    a=a.replace(old,new,1)
elif new not in a:
    raise SystemExit('missing direct-power audit sequence')
audit.write_text(a,encoding='utf-8')

# ---------------------------------------------------------------------------
# 9) Dedicated POINT-BLANK full-pool regression.
# ---------------------------------------------------------------------------
test=Path('tests/point-blank-full-pool.mjs')
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
const expected={PBCA:'pbBreachOrder',PBHA:'pbBreachShield',PBC2:'pbSlideStep',PBH2:'pbSidearm',PBS3:'pbFlashbang',PBS4:'pbBuckshot',PBD4:'pbCrossfire',PBC5:'pbDoorKick',PBD6:'pbReload',PBH6:'pbEmergencyRetreat',PBH7:'pbCoverSwap',PBS8:'pbZeroRange',PBC8:'pbBackdoor',PBC9:'pbRoomClear',PBH10:'pbAdrenaline',PBDJ:'pbQuickReload',PBCQ:'pbBreachLeader',PBSK:'pbMagDump'};
const cards=Object.entries(ctx.NAMED).filter(([,d])=>d?.themeId==='point-blank');
ok(cards.length===18,`POINT-BLANK full pool has exactly 18 definitions (${cards.length})`);
ok(new Set(cards.map(([,d])=>d.slot)).size===18,'POINT-BLANK cards occupy 18 distinct physical slots');
for(const[id,tag]of Object.entries(expected)){const d=ctx.NAMED[id];ok(!!d,`${id} definition exists`);ok(d.themeId==='point-blank'&&d.t===tag,`${id} keeps POINT-BLANK tag ${tag}`);if(!['PBH7','PBDJ'].includes(id))ok(d.rewardPool===false,`${id} is staged out of ordinary roguelike rewards until 60-card integration`)}
ok(script.includes("'PBH7':{slot:'H7',themeId:'point-blank',n:'엄폐 교대',t:'pbCoverSwap'")&&script.includes("'PBDJ':{slot:'DJ',themeId:'point-blank',n:'퀵 리로드',t:'pbQuickReload'"),'existing Cover Swap and Quick Reload live definitions remain unchanged');
for(const tag of ['pbBreachOrder','pbBreachShield','pbSlideStep','pbFlashbang','pbBuckshot','pbCrossfire','pbDoorKick','pbReload','pbEmergencyRetreat','pbZeroRange','pbBackdoor','pbRoomClear','pbAdrenaline','pbBreachLeader','pbMagDump'])ok(script.includes(`case'${tag}'`),`${tag} has a live resolver branch`);
ok(script.includes('function handlePointBlankFullThemeEvent(')&&script.includes('subscribeEffectEvent(handlePointBlankFullThemeEvent);'),'Sidearm/action/leader reactions use the shared event bus');
for(const fn of ['notePointBlankTurnAction','pointBlankTurnActions','requestPointBlankSidearmChoice','requestPointBlankBackdoorChoice','requestPointBlankRoomClearChoice','requestPointBlankLeaderReward','resolvePointBlankPostReturn'])ok(script.includes(`function ${fn}(`),`${fn} helper exists`);
const moveFns=source('requestPointBlankBackdoorChoice')+source('executePointBlankRoomClear');
ok(moveFns.includes('moveCardBetweenMelds')&&!moveFns.includes('addSwitchPower')&&!moveFns.includes('returnSwitch'),'Backdoor and Room Clear route through the combat-neutral movement primitive only');
const post=source('resolvePointBlankPostReturn');
ok(post.includes('spendPointBlankMeldCard')&&!post.includes('returnSwitch')&&!post.includes('addSwitchPower'),'Zero Range pays its RUN cost after return without a second combat event');
const unlock=script.slice(script.indexOf('const UNLOCK_GROUPS='),script.indexOf('function unlockedNamed'));
for(const id of Object.keys(expected))ok(unlock.includes(`'${id}'`),`${id} is reachable through progression unlock groups`);

// Common-event history is boolean and resets by turn token rather than growing a resource.
{
 const f1=source('pointBlankBlankActions'),f2=source('pointBlankTurnActions'),f3=source('notePointBlankTurnAction'),f4=source('pointBlankDistinctActionCount');
 const player={},state={turnToken:5,player,enemy:{}};const box={globalThis:null,state,sideObj:w=>w==='player'?player:state.enemy,Object};box.globalThis=box;
 vm.runInNewContext(`${f1};${f2};${f3};${f4};globalThis.note=notePointBlankTurnAction;globalThis.get=pointBlankTurnActions;globalThis.count=pointBlankDistinctActionCount;`,box);
 box.note('player','attach');box.note('player','recover');ok(box.count('player')===2&&box.get('player').attach&&box.get('player').recover,'two distinct common actions are recorded for Reload/Mag Dump');
 state.turnToken=6;ok(box.count('player')===0,'POINT-BLANK action history naturally expires on the next turn token');
}

// Buckshot differentiates solo entry from an already-established own presence.
{
 const resolve=source('resolveEffects');
 const base={turnToken:8,switchPower:20};
 function run(meld,cards){const p={hand:[]},e={hand:[]},box={globalThis:null,state:{...base},sideObj:()=>p,other:()=> 'enemy',consumeOfficialStatus:()=>0,isPointBlankClash:()=>true,notePointBlankTurnAction:()=>({attach:true,recover:false,discard:false,maintenance:false})};box.globalThis=box;vm.runInNewContext(`${resolve};globalThis.r=resolveEffects;`,box);return box.r('player',cards,'RUN',{meld,effectSeen:new Set(),willReturn:true,isAttach:true,targetOwner:'enemy',totalLength:4})}
 const buck={uid:'b',owner:'player',named:true,tag:'pbBuckshot',name:'벅샷'};
 ok(run({cards:[buck,{uid:'e1',owner:'enemy'},{uid:'e2',owner:'enemy'}]},[buck]).bonus===8,'Buckshot adds 8 when it is the only owned card in the clash action');
 const ally={uid:'a',owner:'player'};ok(run({cards:[buck,ally,{uid:'e',owner:'enemy'}]},[buck]).bonus===12,'Buckshot adds 12 when another owned card already occupies the clash');
}

ok(!script.includes('pointBlankCount')&&!script.includes('POINT_BLANK_COUNT')&&!script.includes('pointBlankResource'),'POINT-BLANK creates no dedicated numeric resource');
ok(audit.includes("'pbBuckshot','pbZeroRange','pbMagDump'"),'direct-power minority audit counts only the three new PB precision finishers');
ok(theme.includes('POINT-BLANK 18/18 풀 카드군 라이브 구현'),'canonical theme document records full implementation');
ok(plan.includes('| POINT-BLANK | 18 | 18 | 0 | 18/18 |')&&plan.includes('| **합계** | **60** | **60** | **0** |'),'full-pool plan reaches 60/60 individually implemented cards');
ok(road.includes('POINT-BLANK 18/18 풀 카드군 구현'),'ROADMAP records POINT-BLANK completion');
console.log('POINT-BLANK 18/18 full-pool regression passed.');
''',encoding='utf-8')

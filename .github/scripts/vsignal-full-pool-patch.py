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
# 1) V-SIGNAL 24-card definition pool.
#    The 21 new cards are staged out of ordinary roguelike reward ranking until
#    the three-theme 60-card integration pass, but remain live for unlocks,
#    codex, deck construction and normal battles.
# ---------------------------------------------------------------------------
defs = [
 ('SA','VSSA', "'VSSA':{slot:'SA',themeId:'v-signal',rewardPool:false,n:'초방송사고',t:'vBroadcastAccident',d:'스위치가 나를 향할 때 이 카드를 사용하면 보호막 12를 얻는다. 그 행동으로 스위치를 반환하면 이번 반환의 누적 위력이 6 증가한다.'},"),
 ('S5','VSS5', "'VSS5':{slot:'S5',themeId:'v-signal',rewardPool:false,n:'악질 클립',t:'vBadClip',d:'다른 네임드 카드와 같은 행동으로 상대 공개 조합에 붙이면, 스위치를 반환할 때 누적 위력이 6 증가한다. 반환하지 않았다면 그 조합에 봉인 1을 부여한다.'},"),
 ('S7','VSS7', "'VSS7':{slot:'S7',themeId:'v-signal',rewardPool:false,n:'실시간 논란',t:'vLiveControversy',d:'상대가 직전 턴에 카드를 회수했다면, 이 카드를 상대 공개 조합에 붙일 때 상대에게 취약 1을 부여한다.'},"),
 ('S9','VSS9', "'VSS9':{slot:'S9',themeId:'v-signal',rewardPool:false,n:'역바이럴',t:'vReverseViral',d:'이 카드가 들어간 내 공개 조합을 상대가 이용하면 반격을 준비한다. 준비된 조합으로 내가 스위치를 반환하면 누적 위력이 10 증가하고 준비를 해제한다.'},"),
 ('SQ','VSSQ', "'VSSQ':{slot:'SQ',themeId:'v-signal',rewardPool:false,n:'염상 스트리머',t:'vFlameStreamer',d:'스위치 누적 위력이 40 이상일 때 이 카드로 스위치를 반환하면 상대에게 취약 1을 부여한다.'},"),
 ('SK','VSSK', "'VSSK':{slot:'SK',themeId:'v-signal',rewardPool:false,n:'BAN 직전',t:'vBanSoon',d:'스위치 누적 위력이 60 이상일 때 이 카드로 스위치를 반환하면 이번 반환의 누적 위력이 16 증가한다.'},"),
 ('HA','VSHA', "'VSHA':{slot:'HA',themeId:'v-signal',rewardPool:false,n:'첫 방송',t:'vFirstBroadcast',d:'이 카드로 새 3장 세트 또는 런을 만들면 남은 손패 1장을 덱 아래로 보내고 1장 뽑는 무료 정비를 할 수 있다. 새 조합 생성 횟수는 늘지 않는다.'},"),
 ('H3','VSH3', "'VSH3':{slot:'H3',themeId:'v-signal',rewardPool:false,n:'ASMR',t:'vAsmr',d:'이 카드가 공개 조합에 들어갈 때 보호막 8을 얻는다. 행동 시작 시 스위치가 나를 향하고 있었다면 대신 보호막 16을 얻는다.'},"),
 ('H7','VSH7', "'VSH7':{slot:'H7',themeId:'v-signal',rewardPool:false,n:'팬 서비스',t:'vFanService',d:'이 카드가 들어간 공개 조합에 양쪽 소유 카드가 모두 있으면 보호막 12를 얻는다. 그 행동으로 스위치를 반환하면 체력 4를 회복한다.'},"),
 ('H10','VSH10', "'VSH10':{slot:'H10',themeId:'v-signal',rewardPool:false,n:'기념 방송',t:'vMilestoneBroadcast',d:'이 카드 사용으로 러미하면 재생 1과 보호막 12를 얻는다.'},"),
 ('HK','VSHK', "'VSHK':{slot:'HK',themeId:'v-signal',rewardPool:false,n:'100만 구독',t:'vMillionSubs',d:'이 카드 사용으로 러미하면 다음에 공개 조합에 내는 내 카드 1장에 보호 1을 부여하고 보호막 8을 얻는다.'},"),
 ('D2','VSD2', "'VSD2':{slot:'D2',themeId:'v-signal',rewardPool:false,n:'신인 2기생',t:'vRookieSet',d:'이 카드로 새 3장 세트를 만들면 남은 손패 1장을 덱 아래로 보내고 1장 뽑는 무료 정비를 할 수 있다.'},"),
 ('D3','VSD3', "'VSD3':{slot:'D3',themeId:'v-signal',rewardPool:false,n:'3인 합방',t:'vTrioCollab',d:'이 카드로 정확히 3장인 새 세트를 만들면 그 세트에 보호 1을 부여한다.'},"),
 ('D6','VSD6', "'VSD6':{slot:'D6',themeId:'v-signal',rewardPool:false,n:'슈퍼챗',t:'vSuperchat',d:'이 카드가 있는 공개 조합에 상대가 카드를 붙이면 턴당 1회 카드 1장을 뽑는다.'},"),
 ('DJ','VSDJ', "'VSDJ':{slot:'DJ',themeId:'v-signal',rewardPool:false,n:'매니저',t:'vManager',d:'내 공개 조합에 이 카드를 사용하면 그 조합의 봉인 1을 먼저 제거하고, 봉인이 없으면 고정 1을 제거한다. 둘 다 없으면 그 조합에 보호 1을 부여한다.'},"),
 ('DK','VSDK', "'VSDK':{slot:'DK',themeId:'v-signal',rewardPool:false,n:'전설의 아이돌',t:'vLegendIdol',d:'이 카드로 4장 세트의 버스트를 완성하면 카드 1장을 뽑거나 보호막 16을 얻을 수 있다.'},"),
 ('CA','VSCA', "'VSCA':{slot:'CA',themeId:'v-signal',rewardPool:false,n:'ON AIR',t:'vOnAir',d:'이 카드로 새 3장 런을 만들면 그 런의 체인을 1부터 시작한다.'},"),
 ('C4','VSC4', "'VSC4':{slot:'C4',themeId:'v-signal',rewardPool:false,n:'게임 방송',t:'vGameBroadcast',d:'체인 1 이하인 런에 이 카드를 붙이면 남은 손패 1장을 덱 아래로 보내고 1장 뽑는 무료 정비를 할 수 있다.'},"),
 ('C6','VSC6', "'VSC6':{slot:'C6',themeId:'v-signal',rewardPool:false,n:'RAID',t:'vRaid',d:'이 카드를 상대 공개 조합에 붙인 뒤 내 다른 공개 조합에서 내가 제어하는 카드 1장을 무료 회수할 수 있다. 회수한 카드의 같은 턴 버스트·체인 반환 재사용 제한은 유지한다.'},"),
 ('C8','VSC8', "'VSC8':{slot:'C8',themeId:'v-signal',rewardPool:false,n:'콜라보 신청',t:'vCollabRequest',d:'이번 턴에 세트와 런 양쪽에 모두 카드를 사용하게 되는 행동에 이 카드가 들어가면 카드 1장을 뽑는다. 카드당 턴당 1회만 발동한다.'},"),
 ('CJ','VSCJ', "'VSCJ':{slot:'CJ',themeId:'v-signal',rewardPool:false,n:'천재 편집자',t:'vGeniusEditor',d:'이 카드를 사용할 때 현재 행동의 조합이 아닌 공개 조합에서 내가 제어하는 카드 1장을 합법적인 다른 런으로 이동할 수 있다. 이동 자체는 버스트·체인 위력이나 스위치 반환을 만들지 않는다.'},"),
]
for anchor, cid, line in defs:
    text = add_after_named(text, anchor, cid, line)

# ---------------------------------------------------------------------------
# 2) Expansion-safe theme composition: max four cards from the chosen theme.
# ---------------------------------------------------------------------------
old = "function chooseNamedForBuild(unlocked,charId,themeId='mixed'){const preferred=themeId==='mixed'?[]:unlocked.filter(id=>NAMED[id]?.themeId===themeId),themeChosen=weightedVariantSample(preferred,Math.min(4,preferred.length),id=>cardWeightForChar(id,charId,themeId)),used=new Set(themeChosen.map(namedSlot)),rest=unlocked.filter(id=>!used.has(namedSlot(id))),fill=weightedVariantSample(rest,Math.max(0,9-themeChosen.length),id=>cardWeightForChar(id,charId,themeId));return themeChosen.concat(fill)}"
new = "function chooseNamedForBuild(unlocked,charId,themeId='mixed'){const preferred=themeId==='mixed'?[]:unlocked.filter(id=>NAMED[id]?.themeId===themeId),themeCap=Math.min(4,new Set(preferred.map(namedSlot)).size),themeChosen=weightedVariantSample(preferred,themeCap,id=>cardWeightForChar(id,charId,themeId)),used=new Set(themeChosen.map(namedSlot)),rest=unlocked.filter(id=>!used.has(namedSlot(id))&&(themeId==='mixed'||NAMED[id]?.themeId!==themeId)),fill=weightedVariantSample(rest,Math.max(0,9-themeChosen.length),id=>cardWeightForChar(id,charId,themeId));return themeChosen.concat(fill)}"
if old in text:
    text = replace_once(text, old, new, 'theme build cap')
elif new not in text:
    raise SystemExit('unrecognized chooseNamedForBuild')

# Attach context exposes pre-action length/chain for low-chain V-SIGNAL cards.
old = "const ctx={isNew:false,isAttach:true,targetOwner:targetSide,totalLength:m.cards.length,effectSeen:new Set(),meld:m,willReturn:returning};"
new = "const ctx={isNew:false,isAttach:true,targetOwner:targetSide,totalLength:m.cards.length,beforeLength:beforeLen,beforeChain,effectSeen:new Set(),meld:m,willReturn:returning};"
if old in text:
    text = replace_once(text, old, new, 'attach context snapshots')
elif new not in text:
    raise SystemExit('unrecognized attach context')

# ---------------------------------------------------------------------------
# 3) Shared V-SIGNAL helpers.
# ---------------------------------------------------------------------------
if 'function noteVSignalMeldKind(' not in text:
    anchor = "function zeroSightCycleCandidates(w,exclude=[]){"
    helper = r'''function noteVSignalMeldKind(w,type){
 const side=sideObj(w);if(side.vSignalKindToken!==state.turnToken){side.vSignalKindToken=state.turnToken;side.vSignalKinds={SET:false,RUN:false}}
 const hadSet=!!side.vSignalKinds.SET,hadRun=!!side.vSignalKinds.RUN,before=!!side.vSignalKinds[type];if(type==='SET'||type==='RUN')side.vSignalKinds[type]=true;
 const both=!!side.vSignalKinds.SET&&!!side.vSignalKinds.RUN;return{before,both,completedPair:both&&!before&&!(hadSet&&hadRun)}
}
function vSignalOpponentRecoveredLastTurn(w){return state.vSignalLastRecoverActor===other(w)&&state.vSignalLastRecoverToken===state.turnToken-1}
function vSignalRaidRecoveryCandidates(w,currentMeld=null,exclude=[]){
 const ex=new Set((exclude||[]).map(c=>c.uid)),out=[];for(const m of meldsOf(w)){if(m===currentMeld)continue;for(const c of freeRecoverCandidates(w,m,exclude))if(!ex.has(c.uid))out.push({meld:m,card:c})}return out
}
function requestVSignalRaidRecoverChoice(w,currentMeld=null,exclude=[],onAsyncResolved=null){
 const candidates=vSignalRaidRecoveryCandidates(w,currentMeld,exclude);if(!candidates.length){if(typeof onAsyncResolved==='function')onAsyncResolved(null);return false}
 const apply=x=>x?.meld&&x?.card?recoverSpecificFromMeld(w,x.meld,x.card,{exclude,label:'RAID 무료 회수'}):null,interactive=w==='player'&&state.turn==='player'&&typeof requestEffectChoice==='function';
 if(interactive)return requestEffectChoice({title:'RAID',text:'내 다른 공개 조합에서 무료 회수할 카드 1장을 고르거나 건너뛸 수 있습니다.',options:candidates.map((x,i)=>({key:`raid:${x.card.uid}:${i}`,label:`${cardText(x.card)}${x.card.named?` · ${x.card.name}`:''}`,detail:x.meld.type==='RUN'?`내 런 · 체인 ${x.meld.chain||0}`:'내 세트',entry:x})),allowSkip:true,skipLabel:'회수하지 않기',onChoose:o=>{if(o?.entry)apply(o.entry);if(typeof onAsyncResolved==='function')onAsyncResolved(o?.entry||null)}});
 const chosen=candidates[0];apply(chosen);if(typeof onAsyncResolved==='function')onAsyncResolved(chosen);return false
}
function vSignalEditorMoveCandidates(w,currentMeld=null,exclude=[]){
 const ex=new Set((exclude||[]).map(c=>c.uid)),out=[];for(const sourceSide of[w,other(w)])for(const source of meldsOf(sourceSide)){if(source===currentMeld||meldFixedActive(source))continue;for(const card of source.cards){if(card.owner!==w||ex.has(card.uid)||cardFixedActive(card))continue;for(const targetSide of[w,other(w)])for(const target of meldsOf(targetSide)){if(target===source||meldFixedActive(target)||target.type!=='RUN')continue;const remain=source.cards.filter(x=>x.uid!==card.uid),added=target.cards.concat(card);if(remain.length<3||meldType(remain)!==source.type||meldType(added)!==target.type)continue;out.push({source,target,card,sourceSide,targetSide})}}}return out
}
function requestVSignalEditorChoice(w,currentMeld=null,exclude=[],onAsyncResolved=null){
 const candidates=vSignalEditorMoveCandidates(w,currentMeld,exclude);if(!candidates.length){if(typeof onAsyncResolved==='function')onAsyncResolved(null);return false}
 const apply=x=>x?moveCardBetweenMelds(w,x.card,x.source,x.target,{reason:'vSignalEditor'}):null,interactive=w==='player'&&state.turn==='player'&&typeof requestEffectChoice==='function';
 if(interactive)return requestEffectChoice({title:'천재 편집자',text:'다른 공개 조합의 내 카드 1장을 합법적인 런으로 이동하거나 건너뛸 수 있습니다. 이동 자체는 전투 위력을 만들지 않습니다.',options:candidates.map((x,i)=>({key:`edit:${x.card.uid}:${i}`,label:`${cardText(x.card)}${x.card.named?` · ${x.card.name}`:''}`,detail:`${x.source.type==='RUN'?'런':'세트'} → 런`,entry:x})),allowSkip:true,skipLabel:'이동하지 않기',onChoose:o=>{if(o?.entry)apply(o.entry);if(typeof onAsyncResolved==='function')onAsyncResolved(o?.entry||null)}});
 const chosen=candidates[0];apply(chosen);if(typeof onAsyncResolved==='function')onAsyncResolved(chosen);return false
}
function requestVSignalLegendChoice(w,c,onAsyncResolved=null){
 const apply=key=>{if(key==='draw')drawOne(w,false);else addShield(w,4);if(typeof log==='function')log(`${c.name}: ${key==='draw'?'카드 1장을 뽑았습니다.':'보호막 16을 얻었습니다.'}`,'good');return key},interactive=w==='player'&&state.turn==='player'&&typeof requestEffectChoice==='function';
 if(interactive)return requestEffectChoice({title:c.name,text:'버스트 후 받을 보상을 고르세요.',options:[{key:'draw',label:'카드 획득',detail:'카드 1장을 뽑는다'},{key:'shield',label:'팬덤 보호',detail:'보호막 16을 얻는다'}],onChoose:o=>{const key=o?.key||'shield';apply(key);if(typeof onAsyncResolved==='function')onAsyncResolved(key)}});
 const key=sideObj(w).hand.length<=2?'draw':'shield';apply(key);if(typeof onAsyncResolved==='function')onAsyncResolved(key);return false
}
'''
    text = replace_once(text, anchor, helper + anchor, 'V-SIGNAL helper anchor')

# ---------------------------------------------------------------------------
# 4) Passive event reactions: recovery memory, Superchat, Reverse Viral,
#    milestone RUMMY and Million Subs next-card protection.
# ---------------------------------------------------------------------------
if 'function handleVSignalFullThemeEvent(' not in text:
    anchor = 'subscribeEffectEvent(handleVSignalThemeEvent);'
    handler = r'''
function handleVSignalFullThemeEvent(packet){
 if(!packet?.event)return false;
 if(packet.event==='onRecover'){state.vSignalLastRecoverActor=packet.actor;state.vSignalLastRecoverToken=packet.turnToken;return false}
 if(packet.event==='onRummy'){
  const cards=packet.lastCards||[],side=sideObj(packet.actor);if(cards.some(c=>c?.themeId==='v-signal'&&c.tag==='vMilestoneBroadcast')){applyStatus(packet.actor,'regen',1);addShield(packet.actor,3);log(`${packet.actor==='player'?'내':'상대'} 기념 방송 · 재생 1과 보호막 12.`,'good')}
  if(cards.some(c=>c?.themeId==='v-signal'&&c.tag==='vMillionSubs')){side.vMillionSubReady=true;log(`${packet.actor==='player'?'내':'상대'} 100만 구독 · 다음 공개 카드 1장을 보호합니다.`,'good')}
  return true
 }
 if(packet.event==='onAttach'){
  const actor=packet.actor,foe=other(actor),m=packet.meld;
  for(const c of m?.cards||[]){if(c.owner!==foe||packet.targetSide!==foe||actor===c.owner)continue;
   if(c.themeId==='v-signal'&&c.tag==='vReverseViral'){c.vReverseViralCharge=true;c.vReverseViralChargeOwner=foe;log(`${c.name}: 상대가 내 공개 조합을 이용해 반격 준비.`,'important')}
   if(c.themeId==='v-signal'&&c.tag==='vSuperchat'&&claimThemeTurnGate(c,'vSuperchat',packet.turnToken)){drawOne(foe,false);log(`${c.name}: 상대가 방송 조합을 이용해 카드 1장을 뽑았습니다.`,'good')}
  }
 }
 if(packet.event==='onAttach'||packet.event==='onMeldCreate'){
  const actor=packet.actor,side=sideObj(actor);if(side.vMillionSubReady){const card=(packet.cards||[]).find(c=>c.owner===actor);if(card){side.vMillionSubReady=false;applyOfficialStatus('card',card,'protect',1,{actor,silent:true});addShield(actor,2);log(`100만 구독: ${cardText(card)}에 보호 1 · 보호막 8.`,'good');return true}}
 }
 return false
}
subscribeEffectEvent(handleVSignalFullThemeEvent);'''
    text = replace_once(text, anchor, anchor + handler, 'V-SIGNAL full event handler anchor')

# ---------------------------------------------------------------------------
# 5) Live action effects in the common resolver.
# ---------------------------------------------------------------------------
old_head = "function resolveEffects(w,cards,type,ctx={}){const side=sideObj(w),seen=ctx.effectSeen||new Set(),foe=other(w),isReturning=!!ctx.willReturn,fx=ctx.fxState||(ctx.fxState={bonus:0,flatReturn:false,forceReturn:false,index:0,effectCards:null});"
new_head = "function resolveEffects(w,cards,type,ctx={}){const side=sideObj(w),seen=ctx.effectSeen||new Set(),foe=other(w),isReturning=!!ctx.willReturn,fx=ctx.fxState||(ctx.fxState={bonus:0,flatReturn:false,forceReturn:false,index:0,effectCards:null}),vSignalAction=noteVSignalMeldKind(w,type);if(isReturning&&ctx.meld&&!fx.vReverseViralChecked){fx.vReverseViralChecked=true;for(const x of ctx.meld.cards||[])if(x.owner===w&&x.themeId==='v-signal'&&x.tag==='vReverseViral'&&x.vReverseViralCharge){x.vReverseViralCharge=false;fx.bonus+=10;log(`${x.name}: 준비된 반격 · 이번 반환 누적 위력 +10.`,'good')}}"
if old_head in text:
    text = replace_once(text, old_head, new_head, 'resolveEffects V-SIGNAL action state')
elif new_head not in text:
    raise SystemExit('unrecognized resolveEffects header')

old_cases = "case'vGatherAll':case'vEndurance':break;case'zsObserver':"
new_cases = "case'vBroadcastAccident':if(state.switchTarget===w){addShield(w,3);if(isReturning)fx.bonus+=6}break;case'vBadClip':if(ctx.isAttach&&ctx.targetOwner===foe&&cards.some(x=>x.uid!==c.uid&&x.named)){if(isReturning)fx.bonus+=6;else applyOfficialStatus('meld',ctx.meld,'seal',1,{actor:w,silent:true})}break;case'vLiveControversy':if(ctx.isAttach&&ctx.targetOwner===foe&&vSignalOpponentRecoveredLastTurn(w))applyOfficialStatus('player',sideObj(foe),'vulnerable',1,{actor:w});break;case'vReverseViral':break;case'vFlameStreamer':if(isReturning&&state.switchPower>=40)applyOfficialStatus('player',sideObj(foe),'vulnerable',1,{actor:w});break;case'vBanSoon':if(isReturning&&state.switchPower>=60)fx.bonus+=16;break;case'vFirstBroadcast':if(ctx.isNew){const paused=requestZeroSightCycle(w,c,cards,resume);if(paused)return pause()}break;case'vAsmr':addShield(w,state.switchTarget===w?4:2);break;case'vFanService':if(ctx.meld&&new Set(ctx.meld.cards.map(x=>x.owner)).size>=2){addShield(w,3);if(isReturning)heal(w,1)}break;case'vMilestoneBroadcast':case'vMillionSubs':break;case'vRookieSet':if(ctx.isNew&&type==='SET'){const paused=requestZeroSightCycle(w,c,cards,resume);if(paused)return pause()}break;case'vTrioCollab':if(ctx.isNew&&type==='SET'&&ctx.totalLength===3)applyOfficialStatus('meld',ctx.meld,'protect',1,{actor:w,silent:true});break;case'vSuperchat':break;case'vManager':if(ctx.meld&&ctx.targetOwner===w){if(officialStatusValue('meld',ctx.meld,'seal')>0)consumeOfficialStatus('meld',ctx.meld,'seal',1);else if(officialStatusValue('meld',ctx.meld,'fixed')>0)clearOfficialStatus('meld',ctx.meld,'fixed');else applyOfficialStatus('meld',ctx.meld,'protect',1,{actor:w,silent:true})}break;case'vLegendIdol':if(ctx.isAttach&&type==='SET'&&ctx.totalLength===4){const paused=requestVSignalLegendChoice(w,c,resume);if(paused)return pause()}break;case'vOnAir':if(ctx.isNew&&type==='RUN'&&ctx.meld)ctx.meld.chain=Math.max(1,ctx.meld.chain||0);break;case'vGameBroadcast':if(ctx.isAttach&&type==='RUN'&&(ctx.beforeChain||0)<=1){const paused=requestZeroSightCycle(w,c,cards,resume);if(paused)return pause()}break;case'vRaid':if(ctx.isAttach&&ctx.targetOwner===foe){const paused=requestVSignalRaidRecoverChoice(w,ctx.meld,cards,resume);if(paused)return pause()}break;case'vCollabRequest':if(vSignalAction.completedPair&&claimThemeTurnGate(c,'vCollabRequest',state.turnToken))drawOne(w,false);break;case'vGeniusEditor':{const paused=requestVSignalEditorChoice(w,ctx.meld,cards,resume);if(paused)return pause();break}case'vGatherAll':case'vEndurance':break;case'zsObserver':"
if old_cases in text:
    text = replace_once(text, old_cases, new_cases, 'V-SIGNAL resolver cases')
elif "case'vBroadcastAccident'" not in text:
    raise SystemExit('unrecognized V-SIGNAL resolver case anchor')

# ---------------------------------------------------------------------------
# 6) Build tendency tags. Direct-power tags remain a minority.
# ---------------------------------------------------------------------------
old = "vEncore:['cycle','combo'],vGatherAll:['hold','combo','cycle'],vEndurance:['extend','sustain','cycle'],zsObserver:"
new = "vEncore:['cycle','combo'],vBroadcastAccident:['sustain','pressure'],vBadClip:['interact','control','pressure'],vLiveControversy:['control','status'],vReverseViral:['control','pressure'],vFlameStreamer:['status','pressure'],vBanSoon:['pressure','hold'],vFirstBroadcast:['combo','cycle'],vAsmr:['sustain','tempo'],vFanService:['interact','sustain'],vMilestoneBroadcast:['cycle','sustain'],vMillionSubs:['cycle','sustain','combo'],vRookieSet:['combo','cycle'],vTrioCollab:['hold','sustain'],vSuperchat:['interact','cycle'],vManager:['control','sustain'],vLegendIdol:['hold','cycle','sustain'],vOnAir:['extend','combo'],vGameBroadcast:['extend','cycle'],vRaid:['interact','recover','cycle'],vCollabRequest:['combo','cycle'],vGeniusEditor:['interact','combo','extend'],vGatherAll:['hold','combo','cycle'],vEndurance:['extend','sustain','cycle'],zsObserver:"
if old in text:
    text = replace_once(text, old, new, 'V-SIGNAL tendency tags')
elif "vBroadcastAccident:['sustain','pressure']" not in text:
    raise SystemExit('unrecognized tendency tail')

# ---------------------------------------------------------------------------
# 7) Unlock all 24 V-SIGNAL variants across normal clear milestones.
# ---------------------------------------------------------------------------
unlock_replacements = [
 ("items:['S6','H7','D8','C2','ZSCA','ZSC2','DA','D3']", "items:['S6','H7','D8','C2','ZSCA','ZSC2','VSHA','VSD2','VSCA','DA','D3']"),
 ("items:['S8','H5','VSH5','D9','C8','D10','C3']", "items:['S8','H5','VSH5','VSH3','VSC4','VSC6','D9','C8','D10','C3']"),
 ("items:['S9','H10','D2','VSD4','C6','SJ','H3']", "items:['S9','H10','D2','VSD4','VSH7','VSD6','VSC8','C6','SJ','H3']"),
 ("items:['SQ','HJ','CJ','CQ','H6','J2']", "items:['SQ','HJ','CJ','CQ','H6','VSSA','VSS5','VSDJ','J2']"),
 ("items:['S10','SK','HK','DJ','C10','S4']", "items:['S10','SK','HK','DJ','C10','S4','VSS7','VSH10','VSCJ']"),
 ("items:['SA','S2','H9','C9','VSCK','J4']", "items:['SA','S2','H9','C9','VSCK','VSS9','VSHK','J4']"),
 ("items:[],fields:['F5']", "items:['VSSQ','VSDK'],fields:['F5']"),
 ("items:['S7B','D7B','H4B','C5B','J5']", "items:['S7B','D7B','H4B','C5B','VSSK','J5']"),
]
for old_frag,new_frag in unlock_replacements:
    if old_frag in text:
        text = replace_once(text, old_frag, new_frag, f'unlock {old_frag[:20]}')
    elif new_frag not in text:
        raise SystemExit(f'unrecognized unlock fragment {old_frag}')

# ---------------------------------------------------------------------------
# 8) Roguelike reward staging. Do not mutate fixed encounter pools in F1.
#    Scarce legal pools still fall back to all candidates so rewards never
#    disappear simply because most candidates are staged.
# ---------------------------------------------------------------------------
old = "const pool=[...new Set(Array.isArray(input.poolIds)?input.poolIds:[])].filter(id=>{const def=NAMED?.[id];if(!def||String(id).startsWith('J'))return false;const slot=namedSlot(id);return profile.slots.includes(slot)&&profile.variants[slot]!==id}),seed=String(input.seed||'reward-v1'),used=new Set(),picks=[];"
new = "const rawPool=[...new Set(Array.isArray(input.poolIds)?input.poolIds:[])].filter(id=>{const def=NAMED?.[id];if(!def||String(id).startsWith('J'))return false;const slot=namedSlot(id);return profile.slots.includes(slot)&&profile.variants[slot]!==id}),stagedPool=rawPool.filter(id=>NAMED?.[id]?.rewardPool!==false),pool=stagedPool.length>=ROGUELIKE_REWARD_ROLES.length?stagedPool:rawPool,seed=String(input.seed||'reward-v1'),used=new Set(),picks=[];"
if old in text:
    text = replace_once(text, old, new, 'roguelike staged reward pool')
elif new not in text:
    raise SystemExit('unrecognized roguelike reward pool')

index.write_text(text, encoding='utf-8')

# ---------------------------------------------------------------------------
# 9) Scalable theme composition regression.
# ---------------------------------------------------------------------------
test = Path('tests/theme-mix-simulation.mjs')
t = test.read_text(encoding='utf-8')
old_block = """for(const[a,b]of pairs){
  const themed=[...themeCards(a),...themeCards(b)],ctx=makeCtx(a.length*100+b.length),uniqueCount=uniqueSlots(themed).size;
  const chosen=[...ctx.weightedVariantSample(themed,uniqueCount,()=>1)],used=new Set(chosen.map(id=>ctx.namedSlot(id)));
  const ordinary=regularIds.filter(id=>!ctx.NAMED[id]?.themeId&&!used.has(ctx.namedSlot(id)));
  const fill=[...ctx.weightedVariantSample(ordinary,Math.max(0,9-chosen.length),()=>1)],build=chosen.concat(fill),slots=build.map(id=>ctx.namedSlot(id));
  ok(new Set(slots).size===build.length,`${a}+${b} mix resolves all physical-slot conflicts`);
  ok(build.some(id=>ctx.NAMED[id]?.themeId===a)&&build.some(id=>ctx.NAMED[id]?.themeId===b),`${a}+${b} mix represents both themes`);
  ok(build.some(id=>!ctx.NAMED[id]?.themeId),`${a}+${b} mix still leaves ordinary-card space`);
  ok(build.length===9,`${a}+${b} mix fills the standard nine named-card module slots`);
}
"""
new_block = """for(const[a,b]of pairs){
  const ctx=makeCtx(a.length*100+b.length),aPool=themeCards(a),aCap=Math.min(4,uniqueSlots(aPool).size);
  const first=[...ctx.weightedVariantSample(aPool,aCap,()=>1)],used=new Set(first.map(id=>ctx.namedSlot(id)));
  const bPool=themeCards(b).filter(id=>!used.has(ctx.namedSlot(id))),bCap=Math.min(4,uniqueSlots(bPool).size);
  const second=[...ctx.weightedVariantSample(bPool,bCap,()=>1)];for(const id of second)used.add(ctx.namedSlot(id));
  const chosen=first.concat(second),ordinary=regularIds.filter(id=>!ctx.NAMED[id]?.themeId&&!used.has(ctx.namedSlot(id)));
  const fill=[...ctx.weightedVariantSample(ordinary,Math.max(0,9-chosen.length),()=>1)],build=chosen.concat(fill),slots=build.map(id=>ctx.namedSlot(id));
  ok(first.length>0&&second.length>0,`${a}+${b} mix represents both theme modules`);
  ok(first.length<=4&&second.length<=4,`${a}+${b} mix respects the four-card cap per theme`);
  ok(new Set(slots).size===build.length,`${a}+${b} mix resolves all physical-slot conflicts`);
  ok(build.some(id=>ctx.NAMED[id]?.themeId===a)&&build.some(id=>ctx.NAMED[id]?.themeId===b),`${a}+${b} mix represents both themes`);
  ok(build.some(id=>!ctx.NAMED[id]?.themeId),`${a}+${b} mix still leaves ordinary-card space`);
  ok(build.length===9,`${a}+${b} mix fills the standard nine named-card module slots`);
}
"""
if old_block in t:
    t = t.replace(old_block, new_block, 1)
elif 'mix respects the four-card cap per theme' not in t:
    raise SystemExit('unrecognized two-theme simulation block')
old_tags = "const directTags=new Set(['finalUltimatum','blackBullet','fuseRound','zsBallistics','zsOneShot']);"
new_tags = "const directTags=new Set(['finalUltimatum','blackBullet','fuseRound','vBroadcastAccident','vBadClip','vReverseViral','vBanSoon','zsBallistics','zsOneShot']);"
if old_tags in t:
    t = t.replace(old_tags, new_tags, 1)
elif new_tags not in t:
    raise SystemExit('unrecognized direct power tag set')
test.write_text(t, encoding='utf-8')

# ---------------------------------------------------------------------------
# 10) Dedicated full-pool structural regression.
# ---------------------------------------------------------------------------
full_test = Path('tests/vsignal-full-pool.mjs')
full_test.write_text(r'''import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const plan=fs.readFileSync(new URL('../docs/THEME_FULL_POOL_PLAN.md',import.meta.url),'utf8');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function literal(name,next){const a=script.indexOf(`const ${name}=`);if(a<0)throw new Error(`missing ${name}`);const b=script.indexOf(next,a);if(b<0)throw new Error(`missing end ${name}`);return script.slice(a+`const ${name}=`.length,b).trim().replace(/;$/,'')}
const ctx=vm.createContext({console,Object,Array,Set,Map,Number,String,Boolean,Math});
vm.runInContext(`globalThis.NAMED=${literal('NAMED','\nconst CHARACTERS=')}`,ctx);
const expected={
 VSSA:'vBroadcastAccident',VSS5:'vBadClip',VSS7:'vLiveControversy',VSS9:'vReverseViral',VSSQ:'vFlameStreamer',VSSK:'vBanSoon',
 VSHA:'vFirstBroadcast',VSH3:'vAsmr',VSH5:'vEncore',VSH7:'vFanService',VSH10:'vMilestoneBroadcast',VSHK:'vMillionSubs',
 VSD2:'vRookieSet',VSD3:'vTrioCollab',VSD4:'vGatherAll',VSD6:'vSuperchat',VSDJ:'vManager',VSDK:'vLegendIdol',
 VSCA:'vOnAir',VSC4:'vGameBroadcast',VSC6:'vRaid',VSC8:'vCollabRequest',VSCJ:'vGeniusEditor',VSCK:'vEndurance'
};
const cards=Object.entries(ctx.NAMED).filter(([,d])=>d?.themeId==='v-signal');
ok(cards.length===24,`V-SIGNAL full pool has exactly 24 definitions (${cards.length})`);
ok(new Set(cards.map(([,d])=>d.slot)).size===24,'V-SIGNAL 24 cards occupy 24 distinct physical slots');
for(const[id,tag]of Object.entries(expected)){
 const d=ctx.NAMED[id];ok(!!d,`${id} definition exists`);ok(d.themeId==='v-signal'&&d.t===tag,`${id} keeps V-SIGNAL tag ${tag}`);
 if(!['VSH5','VSD4','VSCK'].includes(id))ok(d.rewardPool===false,`${id} is staged out of ordinary roguelike rewards until 60-card integration`);
}
for(const tag of ['vBroadcastAccident','vBadClip','vLiveControversy','vFlameStreamer','vBanSoon','vFirstBroadcast','vAsmr','vFanService','vRookieSet','vTrioCollab','vManager','vLegendIdol','vOnAir','vGameBroadcast','vRaid','vCollabRequest','vGeniusEditor'])ok(script.includes(`case'${tag}'`),`${tag} has a live common-resolver branch`);
for(const tag of ['vReverseViral','vSuperchat','vMilestoneBroadcast','vMillionSubs'])ok(script.includes(tag)&&script.includes('function handleVSignalFullThemeEvent('),`${tag} is wired through the passive V-SIGNAL event handler`);
ok(script.includes('function requestVSignalRaidRecoverChoice('),'RAID uses a resumable legal free-recovery chooser');
ok(script.includes('function requestVSignalEditorChoice('),'Genius Editor uses a resumable legal movement chooser');
ok(script.includes('function requestVSignalLegendChoice('),'Legend Idol uses a resumable reward choice');
ok(script.includes('function noteVSignalMeldKind('),'SET/RUN cross-play is tracked without a new numeric resource');
ok(script.includes("themeCap=Math.min(4,new Set(preferred.map(namedSlot)).size)"),'automatic theme build caps the selected theme at four physical slots');
ok(script.includes("(themeId==='mixed'||NAMED[id]?.themeId!==themeId)"),'automatic fill cannot silently exceed the four-card theme cap');
ok(script.includes('stagedPool=rawPool.filter(id=>NAMED?.[id]?.rewardPool!==false)'),'ordinary roguelike reward ranking honors staged full-pool cards');
ok(script.includes('pool=stagedPool.length>=ROGUELIKE_REWARD_ROLES.length?stagedPool:rawPool'),'scarce roguelike reward pools preserve the legal fallback');
const unlockBlock=script.slice(script.indexOf('const UNLOCK_GROUPS='),script.indexOf('function unlockedNamed'));
for(const id of Object.keys(expected))ok(unlockBlock.includes(`'${id}'`),`${id} is reachable through progression unlock groups`);
ok(!script.includes('hypeCount')&&!script.includes('HYPE_COUNT'),'V-SIGNAL still creates no HYPE resource');
ok(road.includes('V-SIGNAL 24/24 풀 카드군 구현'),'ROADMAP records the full V-SIGNAL implementation');
ok(plan.includes('| V-SIGNAL | 24 | 24 | 0 | 24/24 |'),'full-pool plan records V-SIGNAL as 24/24');
console.log('V-SIGNAL 24/24 full-pool regression passed.');
''', encoding='utf-8')

# ---------------------------------------------------------------------------
# 11) Canonical docs and roadmap.
# ---------------------------------------------------------------------------
theme_doc = Path('docs/THEME_GROUPS.md')
d = theme_doc.read_text(encoding='utf-8')
policy = '- 테마 구성 안정성은 최대 테마 밀도 오픈형 빌드·모든 2테마 조합·일반 mixed 다중 시드 회귀로 검사한다. 같은 숫자+무늬 슬롯은 언제나 한 변형만 남기고, 직접 누적 위력 카드는 전체 풀의 소수로 유지한다.'
extra = policy + '\n- 카드 풀이 4장을 넘는 테마도 자동 빌드는 한 테마 최대 4장만 우선 편성한다. 2테마 혼합 시에도 각 테마 최대 4장으로 제한하고 최소 1장의 비테마 공간을 남긴다.'
if policy in d and '2테마 혼합 시에도 각 테마 최대 4장' not in d:
    d = d.replace(policy, extra, 1)
# Keep the canonical names/axes but document the exact implemented effects for the places where wording changed from the earlier candidate shorthand.
repls = {
"- A♠ `초방송사고` — 스위치가 자신을 향할 때 방어, 성공 반환 시 소형 추가 위력.":"- A♠ `초방송사고` — 스위치가 자신을 향할 때 사용하면 보호막 12, 같은 행동의 반환이면 누적 위력 +6.",
"- 5♠ `악질 클립` — 앞선 네임드 효과와 연계한 추가 위력 또는 상대 조합 봉인.":"- 5♠ `악질 클립` — 다른 네임드와 함께 상대 조합에 붙이면 반환 시 +6, 비반환이면 그 조합 봉인 1.",
"- 7♠ `실시간 논란` — 상대의 직전 회수 행동에 반응하는 압박.":"- 7♠ `실시간 논란` — 상대가 직전 턴에 회수했다면 상대 조합에 붙을 때 상대에게 취약 1.",
"- 9♠ `역바이럴` — 상대가 내 공개 조합을 이용한 뒤 충전되는 반격.":"- 9♠ `역바이럴` — 상대가 이 카드가 있는 내 조합을 이용하면 반격 준비, 그 조합으로 다음 반환 시 +10 후 해제.",
"- Q♠ `염상 스트리머` — 높은 누적 위력에서 취약 부여.":"- Q♠ `염상 스트리머` — 누적 위력 40+에서 이 카드로 반환하면 상대에게 취약 1.",
"- K♠ `BAN 직전` — 높은 누적 위력에서 +16급 피니시 보정.":"- K♠ `BAN 직전` — 누적 위력 60+에서 이 카드로 반환하면 이번 반환 +16.",
"- 3♥ `ASMR` — 조합 진입 시 보호막, 스위치가 자신을 향하면 강화.":"- 3♥ `ASMR` — 조합 진입 시 보호막 8, 행동 시작 시 스위치가 자신을 향하면 보호막 16.",
"- 7♥ `팬 서비스` — 양측 카드가 섞인 공개 조합 활용 시 회복/보호막.":"- 7♥ `팬 서비스` — 양측 소유 카드가 섞인 조합에 들어가면 보호막 12, 그 행동으로 반환하면 체력 4 회복.",
"- 10♥ `기념 방송` — 이 카드로 러미하면 재생 + 보호막.":"- 10♥ `기념 방송` — 이 카드로 러미하면 재생 1 + 보호막 12.",
"- K♥ `100만 구독` — 러미 후 첫 조합 카드에 보호/획득 보조.":"- K♥ `100만 구독` — 이 카드로 러미하면 다음 공개 카드 1장에 보호 1 + 보호막 8.",
"- 2♦ `신인 2기생` — 새 3장 세트 생성 시 무료 정비.":"- 2♦ `신인 2기생` — 새 3장 세트 생성 시 남은 손패 1장 무료 정비.",
"- 3♦ `3인 합방` — 정확히 3장 세트에 보호 부여.":"- 3♦ `3인 합방` — 정확히 3장인 새 세트에 보호 1.",
"- 6♦ `슈퍼챗` — 해당 조합을 상대가 이용하면 카드 획득.":"- 6♦ `슈퍼챗` — 이 카드가 있는 공개 조합에 상대가 붙이면 턴당 1회 1장 획득.",
"- J♦ `매니저` — 봉인/고정 제거 또는 보호 부여.":"- J♦ `매니저` — 내 조합의 봉인 1 → 고정 1 순으로 제거하고, 둘 다 없으면 보호 1.",
"- K♦ `전설의 아이돌` — 버스트 후 후속 자원 또는 방어를 선택.":"- K♦ `전설의 아이돌` — 이 카드로 4장 세트 버스트를 완성하면 1장 획득 또는 보호막 16 선택.",
"- A♣ `ON AIR` — 새 런의 체인을 1부터 시작시키는 장기 런 스타터.":"- A♣ `ON AIR` — 새 3장 런의 체인을 1부터 시작.",
"- 4♣ `게임 방송` — 낮은 체인의 런 연장 시 무료 정비.":"- 4♣ `게임 방송` — 체인 1 이하 런에 붙이면 남은 손패 1장 무료 정비.",
"- 6♣ `RAID` — 상대 조합에 붙은 뒤 자신의 다른 공개 카드 무료 회수.":"- 6♣ `RAID` — 상대 조합에 붙은 뒤 내 다른 공개 조합에서 내 카드 1장 무료 회수. 당턴 반환 재사용 제한은 유지.",
"- 8♣ `콜라보 신청` — 같은 턴 세트↔런 교차 플레이에 카드 획득.":"- 8♣ `콜라보 신청` — 이 카드의 행동으로 같은 턴 세트·런 양쪽 사용을 완성하면 턴당 1회 1장 획득.",
"- J♣ `천재 편집자` — 자신의 공개 카드를 합법적인 다른 조합으로 이동.":"- J♣ `천재 편집자` — 현재 행동 조합이 아닌 공개 조합의 내 카드 1장을 합법적인 다른 런으로 전투 중립 이동.",
}
for a,b in repls.items():
    if a in d:
        d=d.replace(a,b,1)
marker = '## V-SIGNAL 구현 체크\n'
if marker in d and '- [x] V-SIGNAL 24/24 풀 카드군 라이브 구현' not in d:
    d=d.replace(marker, marker+'\n- [x] V-SIGNAL 24/24 풀 카드군 라이브 구현 — 24개 정의·효과·해금·도감/덱빌더 연결 완료. 신규 21장은 60장 통합 전까지 기존 로그라이크 지역 적 덱과 일반 랜덤 보상 순위에서 우선 제외하며 희소 후보 안전망만 허용\n',1)
theme_doc.write_text(d,encoding='utf-8')

plan = Path('docs/THEME_FULL_POOL_PLAN.md')
p = plan.read_text(encoding='utf-8')
p = p.replace('| V-SIGNAL | 24 | 3 | 21 | 24/24 |','| V-SIGNAL | 24 | 24 | 0 | 24/24 |')
p = p.replace('| **합계** | **60** | **9** | **51** | **60/60** |','| **합계** | **60** | **30** | **30** | **60/60** |')
p = p.replace('- V-SIGNAL: `앙코르`, `전원 집합!`, `24시간 내구방송`','- V-SIGNAL: **24/24 풀 구현 완료**')
p = p.replace('### F1 — V-SIGNAL 24/24\n\n현재 3장 → 24장으로 완성한다.','### F1 — V-SIGNAL 24/24 · 완료\n\n24장 전체 정의·실전 효과·해금·도감/덱빌더 연결을 완료했다. 신규 21장은 60장 통합 전까지 기존 로그라이크 지역 적 덱에는 넣지 않고, 일반 랜덤 보상 순위에서도 후보가 충분할 때 우선 제외한다.')
if 'F1 완료 기록' not in p:
    key='완료 게이트:\n\n- 24개 정의 + 24개 실제 효과\n- V-SIGNAL 전용 회귀\n- 일반/다른 테마 카드가 합방·RAID·회수 루프에 참여 가능\n- HYPE 등 전용 숫자 자원 없음'
    repl=key+'\n\n**F1 완료 기록** — 2026-09-02. `tests/vsignal-full-pool.mjs`, 기존 `tests/vsignal-mixed-regression.mjs`, 확장형 `tests/theme-mix-simulation.mjs` 및 전체 회귀를 릴리스 게이트로 사용한다.'
    if key in p:p=p.replace(key,repl,1)
plan.write_text(p,encoding='utf-8')

road=Path('ROADMAP.md')
r=road.read_text(encoding='utf-8')
needle='- [x] V-SIGNAL ↔ 일반 카드 혼합 회귀 테스트'
line='- [x] V-SIGNAL 24/24 풀 카드군 구현 — 정식 후보 24장 전부를 실제 NAMED 변형·공용 효과 엔진·해금·도감/덱빌더에 연결. HYPE 같은 전용 숫자 자원 없이 세트·런·붙이기·회수·정비·이동·러미·공식 상태를 재사용하고, 자동 테마 빌드 최대 4장 및 확장형 2테마 조합 회귀를 함께 잠금'
if line not in r:
    if needle in r:r=r.replace(needle,needle+'\n'+line,1)
    else:r+='\n'+line+'\n'
road.write_text(r,encoding='utf-8')

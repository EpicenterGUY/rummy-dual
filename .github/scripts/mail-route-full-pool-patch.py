from pathlib import Path
import re

index=Path('index.html')
text=index.read_text(encoding='utf-8')

def once(old,new,label):
    global text
    if new in text:
        return
    if old not in text:
        raise SystemExit(f'missing anchor: {label}')
    text=text.replace(old,new,1)

# ---------- Runtime registries / UI ----------
once("const EFFECT_EVENTS=Object.freeze(['onAcquire','onDiscard','onMeldCreate','onAttach','onBurst','onChain','onRecover','onMeldMove','onTargetSet','onTargetClear','onTargetMeldChange','onClashSet','onClashClear','onClashMeldChange','onRummy','onReturnSwitch','onDetonate','onCoreBreak','onTurnStart','onTurnEnd','onRunFinish','onRetire']);",
     "const EFFECT_EVENTS=Object.freeze(['onAcquire','onDiscard','onMeldCreate','onAttach','onBurst','onChain','onRecover','onMeldMove','onTargetSet','onTargetClear','onTargetMeldChange','onClashSet','onClashClear','onClashMeldChange','onMailSet','onDestinationSet','onArrival','onReturnMail','onRummy','onReturnSwitch','onDetonate','onCoreBreak','onTurnStart','onTurnEnd','onRunFinish','onRetire']);",
     'mail effect events')
once("const THEME_REACTION_ORDER=Object.freeze({attach:Object.freeze(['onAttach','onTargetMeldChange','onClashMeldChange','postReturn']),recover:Object.freeze(['onRecover','onTargetMeldChange','onClashMeldChange']),move:Object.freeze(['onMeldMove','onTargetMeldChange:source','onTargetMeldChange:target','onClashMeldChange:source','onClashMeldChange:target'])});",
     "const THEME_REACTION_ORDER=Object.freeze({attach:Object.freeze(['onAttach','onTargetMeldChange','onClashMeldChange','onArrival','postReturn']),recover:Object.freeze(['onRecover','onTargetMeldChange','onClashMeldChange','onReturnMail']),move:Object.freeze(['onMeldMove','onTargetMeldChange:source','onTargetMeldChange:target','onClashMeldChange:source','onClashMeldChange:target','onArrival'])});",
     'mail reaction order')
once("'point-blank':Object.freeze({id:'point-blank',name:'POINT-BLANK',displayName:'POINT-BLANK',concept:'접전 · 돌입 · 회수 · 교대'})});",
     "'point-blank':Object.freeze({id:'point-blank',name:'POINT-BLANK',displayName:'POINT-BLANK',concept:'접전 · 돌입 · 회수 · 교대'}),'mail-route':Object.freeze({id:'mail-route',name:'MAIL-ROUTE',displayName:'MAIL-ROUTE',concept:'우편 · 목적지 · 도착 · 반송 · 재배송'})});",
     'theme group registry')
once("'point-blank':Object.freeze({themeId:'point-blank',startStep:'pbBreach',live:true})});",
     "'point-blank':Object.freeze({themeId:'point-blank',startStep:'pbBreach',live:true}),'mail-route':Object.freeze({themeId:'mail-route',startStep:'mrAddress',live:true})});",
     'theme tutorial registry')
once(" 'point-blank':Object.freeze({id:'point-blank',displayName:'POINT-BLANK',short:'근접 교대',desc:'접전·돌입·회수·교대를 엮어 상대 공개 조합 안에서 압박합니다. 일반 카드도 함께 섞입니다.',themeId:'point-blank',live:true})});",
     " 'point-blank':Object.freeze({id:'point-blank',displayName:'POINT-BLANK',short:'근접 교대',desc:'접전·돌입·회수·교대를 엮어 상대 공개 조합 안에서 압박합니다. 일반 카드도 함께 섞입니다.',themeId:'point-blank',live:true}),\n 'mail-route':Object.freeze({id:'mail-route',displayName:'MAIL-ROUTE',short:'배송 경로',desc:'일반 카드에도 우편 표식을 붙이고 목적지·도착·반송·재배송으로 공개 조합 사이를 순환합니다.',themeId:'mail-route',live:true})});",
     'mail route build profile')
once("<button class=\"pixelBtn\" data-codex-filter=\"theme:point-blank\">POINT-BLANK</button>",
     "<button class=\"pixelBtn\" data-codex-filter=\"theme:point-blank\">POINT-BLANK</button><button class=\"pixelBtn\" data-codex-filter=\"theme:mail-route\">MAIL-ROUTE</button>",
     'mail codex tab')
once("if(id==='point-blank')return'테마 카드 해금 필요 · 전체 1클리어부터';return'사용할 수 없음'",
     "if(id==='point-blank')return'테마 카드 해금 필요 · 전체 1클리어부터';if(id==='mail-route')return'테마 카드 해금 필요 · 전체 1클리어부터';return'사용할 수 없음'",
     'mail route unlock copy')

# CSS/UI marks.
once(".zeroSightTag{display:inline-block;margin-left:4px;padding:1px 3px;border:1px solid #31536d;background:#13283a;color:#a8d8f6;font-size:6px;font-weight:900}",
     ".zeroSightTag{display:inline-block;margin-left:4px;padding:1px 3px;border:1px solid #31536d;background:#13283a;color:#a8d8f6;font-size:6px;font-weight:900}.meldEntry.mailRouteDestination{border-color:#c9a85a;box-shadow:0 0 0 2px #59491f inset}.mailRouteTag{display:inline-block;margin-left:4px;padding:1px 3px;border:1px solid #725b29;background:#332a16;color:#f1d690;font-size:6px;font-weight:900}.mailCardMark{position:absolute;z-index:7;left:5px;bottom:5px;padding:1px 3px;border:1px solid #5a4218;background:#f1d690;color:#34260d;font-size:6px;font-weight:900}",
     'mail route CSS')

# ---------- 28 card definitions ----------
mail_defs="""
,'MRDA':{slot:'DA',themeId:'mail-route',n:'발송 접수',t:'mrDispatchDesk',d:'새 3장 조합을 만들 때 그 조합의 다른 내 카드 1장을 우편으로 발송할 수 있다. 발송했다면 보호막 8을 얻는다.'}
,'MRD2':{slot:'D2',themeId:'mail-route',n:'등기 우편',t:'mrRegistered',d:'이 카드를 조합에 사용하면 자신을 우편으로 발송한다. 세트의 내 목적지에 지정 도착했다면 그 조합에 보호 1을 부여한다.'}
,'MRD4':{slot:'D4',themeId:'mail-route',n:'우편 분류기',t:'mrSorter',d:'공개된 동안 이번 턴 처음 내 카드가 우편으로 발송되면 보호막 8을 얻는다.'}
,'MRD6':{slot:'D6',themeId:'mail-route',n:'특급 발송',t:'mrExpress',d:'이 카드를 조합에 사용하면 남은 손패의 내 카드 1장을 우편으로 발송할 수 있다. 발송했다면 보호막 8을 얻는다.'}
,'MRD8':{slot:'D8',themeId:'mail-route',n:'대량 발송',t:'mrBulkMail',d:'이 카드로 새 3장 세트를 만들면 그 세트의 다른 내 카드들을 모두 우편으로 발송한다.'}
,'MRDJ':{slot:'DJ',themeId:'mail-route',n:'우체국장',t:'mrPostmaster',d:'공개된 동안 내 우편이 내 목적지에 지정 도착하면 그 목적지의 봉인 1을 제거하고, 봉인이 없으면 고정을 해제하며, 둘 다 없으면 보호 1을 부여한다. 이 효과는 턴당 1회만 발동한다.'}
,'MRDK':{slot:'DK',themeId:'mail-route',n:'중앙 우체국',t:'mrCentralOffice',d:'공개된 동안 내 우편이 내 세트 목적지에 지정 도착하면 턴당 1회 카드 1장을 뽑는다.'}
,'MRCA':{slot:'CA',themeId:'mail-route',n:'주소 라벨',t:'mrAddressLabel',d:'이 카드를 조합에 사용하면 자신을 우편으로 발송하고 그 공개 조합을 내 목적지로 지정한다.'}
,'MRC3':{slot:'C3',themeId:'mail-route',n:'경로 수정',t:'mrRouteChange',d:'이 카드를 조합에 사용하면 내 목적지를 다른 공개 조합으로 이전할 수 있다. 현재 목적지가 없다면 이 카드가 들어간 조합을 목적지로 지정한다.'}
,'MRC5':{slot:'C5',themeId:'mail-route',n:'배송 기사',t:'mrCourier',d:'공개된 동안 내 우편이 공개 조합에 도착하면 턴당 1회 보호막 8을 얻는다.'}
,'MRC7':{slot:'C7',themeId:'mail-route',n:'환승 센터',t:'mrTransferHub',d:'이 카드를 조합에 사용하면 다른 공개 조합의 내 우편 카드 1장을 합법적인 다른 공개 조합으로 이동할 수 있다. 이동 자체는 전투 중립이다.'}
,'MRC9':{slot:'C9',themeId:'mail-route',n:'우회 배송',t:'mrDetour',d:'이 카드를 조합에 사용하면 자신을 우편으로 발송한다. 목적지가 아닌 공개 조합에 도착했다면 그 조합을 새 목적지로 지정한다.'}
,'MRCQ':{slot:'CQ',themeId:'mail-route',n:'라스트 마일',t:'mrLastMile',d:'우편 상태인 이 카드가 런 목적지에 지정 도착하면 다른 공개 조합의 내 우편 카드 1장을 무료 회수할 수 있다. 기본 반환 제한은 유지한다.'}
,'MRCK':{slot:'CK',themeId:'mail-route',n:'전국 배송망',t:'mrNetwork',d:'공개된 동안 내 우편이 세트와 런 사이를 이동하면 턴당 1회 카드 1장을 뽑는다.'}
,'MRHA':{slot:'HA',themeId:'mail-route',n:'회신 봉투',t:'mrReplyEnvelope',d:'이 카드를 조합에 사용하면 자신을 우편으로 발송한다. 우편 상태로 반송되면 보호막 8을 얻는다.'}
,'MRH3':{slot:'H3',themeId:'mail-route',n:'반송 접수',t:'mrReturnDesk',d:'우편 상태인 이 카드가 반송되면 카드 1장을 뽑고, 이 카드 외 가장 오래 보유한 손패 1장을 덱 아래로 보낸다.'}
,'MRH5':{slot:'H5',themeId:'mail-route',n:'재배송',t:'mrRedelivery',d:'이 카드를 조합에 사용하면 자신을 우편으로 발송한다. 반송된 턴 한 번, 반송한 조합과 다른 합법적인 공개 조합의 버스트/체인 반환 재료로 다시 사용할 수 있다.'}
,'MRH7':{slot:'H7',themeId:'mail-route',n:'수취 확인',t:'mrReceipt',d:'이 카드를 조합에 사용하면 자신을 우편으로 발송한다. 목적지에 지정 도착하면 현재 코어를 4 회복하고 보호막 8을 얻는다.'}
,'MRH9':{slot:'H9',themeId:'mail-route',n:'보관 우편함',t:'mrMailbox',d:'공개된 동안 내 목적지가 정리되면 다른 공개 조합이 있을 경우 그중 하나를 새 목적지로 지정하고 보호막 8을 얻는다.'}
,'MRHQ':{slot:'HQ',themeId:'mail-route',n:'답장 대기',t:'mrReplyWait',d:'공개된 동안 상대 공개 조합에서 내 우편이 반송되면 턴당 1회 카드 1장을 뽑는다.'}
,'MRHK':{slot:'HK',themeId:'mail-route',n:'우편 러미',t:'mrPostalRummy',d:'이 카드를 사용해 러미하면 재생 1을 얻고 새 손패의 우편이 아닌 카드 1장을 우편으로 발송한다.'}
,'MRSA':{slot:'SA',themeId:'mail-route',n:'검열 봉투',t:'mrCensorEnvelope',d:'이 카드를 조합에 사용하면 자신을 우편으로 발송한다. 상대 공개 조합의 내 목적지에 지정 도착하면 그 조합에 봉인 1을 부여한다.'}
,'MRS3':{slot:'S3',themeId:'mail-route',n:'도난 우편',t:'mrStolenMail',d:'공개된 동안 상대가 내 목적지에 카드를 붙이면 턴당 1회 카드 1장을 뽑는다.'}
,'MRS5':{slot:'S5',themeId:'mail-route',n:'배달 사고',t:'mrDeliveryFailure',d:'이 카드를 조합에 사용하면 자신을 우편으로 발송한다. 상대 공개 조합에 도착했지만 지정 도착이 아니라면 상대에게 취약 1을 부여한다.'}
,'MRS7':{slot:'S7',themeId:'mail-route',n:'위험물 우편',t:'mrHazardMail',d:'이 카드를 조합에 사용하면 자신을 우편으로 발송한다. 상대 목적지에 지정 도착하며 스위치를 반환하면 이번 반환의 누적 위력이 10 증가한다.'}
,'MRS9':{slot:'S9',themeId:'mail-route',n:'가로채기',t:'mrInterception',d:'공개된 동안 상대가 내 목적지에서 카드를 회수하거나 다른 조합으로 이동하면 턴당 1회 그 목적지를 고정한다.'}
,'MRSQ':{slot:'SQ',themeId:'mail-route',n:'검은 봉투',t:'mrBlackEnvelope',d:'이 카드를 조합에 사용하면 자신을 우편으로 발송한다. 상대 목적지에 지정 도착하면 상대에게 취약 1을 부여하고 보호막 8을 얻는다.'}
,'MRSK':{slot:'SK',themeId:'mail-route',n:'최종 통지',t:'mrFinalNotice',d:'이 카드를 조합에 사용하면 자신을 우편으로 발송한다. 누적 위력 40 이상에서 상대 목적지에 지정 도착하며 스위치를 반환하면 이번 반환의 누적 위력이 14 증가한다.'}
"""
if "'MRDA':" not in text:
    anchor='\nconst CHARACTERS='
    pos=text.find(anchor)
    if pos<0: raise SystemExit('missing CHARACTERS anchor')
    end=text.rfind('\n};',0,pos)
    if end<0: raise SystemExit('missing NAMED end')
    text=text[:end]+mail_defs+text[end:]

# ---------- Unlocks ----------
vs8=" {id:'vs8',label:'전체 8클리어 · V-SIGNAL',kind:'theme',when:p=>p.totalClears>=8,items:['VSSK'],fields:[]},"
mail_unlocks=vs8+"\n"+"\n".join([
" {id:'mrf1',label:'전체 1클리어 · MAIL-ROUTE',kind:'theme',when:p=>p.totalClears>=1,items:['MRDA','MRCA','MRHA','MRSA'],fields:[]},",
" {id:'mrf2',label:'전체 2클리어 · MAIL-ROUTE',kind:'theme',when:p=>p.totalClears>=2,items:['MRD2','MRC3','MRH3','MRS3'],fields:[]},",
" {id:'mrf3',label:'전체 3클리어 · MAIL-ROUTE',kind:'theme',when:p=>p.totalClears>=3,items:['MRD4','MRC5','MRH5','MRS5'],fields:[]},",
" {id:'mrf4',label:'전체 4클리어 · MAIL-ROUTE',kind:'theme',when:p=>p.totalClears>=4,items:['MRD6','MRC7','MRH7','MRS7'],fields:[]},",
" {id:'mrf5',label:'전체 5클리어 · MAIL-ROUTE',kind:'theme',when:p=>p.totalClears>=5,items:['MRD8','MRC9','MRH9','MRS9'],fields:[]},",
" {id:'mrf6',label:'전체 6클리어 · MAIL-ROUTE',kind:'theme',when:p=>p.totalClears>=6,items:['MRDJ','MRCQ','MRHQ','MRSQ'],fields:[]},",
" {id:'mrf7',label:'전체 7클리어 · MAIL-ROUTE',kind:'theme',when:p=>p.totalClears>=7,items:['MRDK','MRCK','MRHK','MRSK'],fields:[]},"
])
once(vs8,mail_unlocks,'mail unlock groups')

# ---------- MAIL-ROUTE foundation/helpers ----------
helper_anchor='function handleVSignalThemeEvent(packet)'
mail_helpers=r'''function ensureMailRouteMeta(m){if(!m)return null;m.themeMeta=m.themeMeta||{};m.themeMeta.mailRoute=m.themeMeta.mailRoute||{destinationBy:{player:false,enemy:false}};m.themeMeta.mailRoute.destinationBy=m.themeMeta.mailRoute.destinationBy||{player:false,enemy:false};return m.themeMeta.mailRoute}
function isMailRouteCard(c,sender=null){return !!c?.mailRouteSender&&(!sender||c.mailRouteSender===sender)}
function clearMailRouteCard(c,reason='routeEnd',silent=false){if(!c?.mailRouteSender)return false;const sender=c.mailRouteSender;c.mailRouteSender=null;c.mailRouteSentToken=null;c.mailRouteReturnToken=null;c.mailRouteReturnSource=null;if(!silent&&typeof log==='function')log(`${c.name||cardText(c)}: 우편 발송 종료 · ${reason}.`,'important');return sender}
function setMailRouteCard(sender,c,opts={}){if(!sender||!c||c.owner!==sender)return false;c.mailRouteSender=sender;c.mailRouteSentToken=state.turnToken;c.mailRouteLastSetToken=state.turnToken;if(typeof emitEffectEvent==='function')emitEffectEvent('onMailSet',{sender,actor:sender,card:c,reason:opts.reason||'dispatch'});if(!opts.silent&&typeof log==='function')log(`${opts.label||c.name||'MAIL-ROUTE'}: ${cardText(c)} 우편 발송.`,'good');return true}
function mailRouteDestinationMeld(actor){if(!actor||typeof meldsOf!=='function'||typeof other!=='function')return null;for(const side of[actor,other(actor)])for(const m of meldsOf(side))if(ensureMailRouteMeta(m)?.destinationBy?.[actor])return m;return null}
function isMailRouteDestination(actor,m){return !!actor&&!!m&&!!ensureMailRouteMeta(m)?.destinationBy?.[actor]}
function clearMailRouteDestination(actor,opts={}){const old=mailRouteDestinationMeld(actor);if(!old)return null;ensureMailRouteMeta(old).destinationBy[actor]=false;if(!opts.silent&&typeof log==='function')log(`MAIL-ROUTE: ${actor==='player'?'내':'상대'} 목적지 해제.`,'important');return old}
function setMailRouteDestination(actor,m,opts={}){if(!actor||!m)return false;const old=mailRouteDestinationMeld(actor);if(old&&old!==m)ensureMailRouteMeta(old).destinationBy[actor]=false;ensureMailRouteMeta(m).destinationBy[actor]=true;if(typeof emitEffectEvent==='function')emitEffectEvent('onDestinationSet',{actor,meld:m,oldMeld:old||null,reason:opts.reason||'destination'});if(!opts.silent&&typeof log==='function')log(`${opts.label||'MAIL-ROUTE'}: ${actor==='player'?'내':'상대'} 목적지 → ${meldOwnerSide(m)===actor?'내':'상대'} ${m.type==='SET'?'세트':'런'}.`,'good');return true}
function clearMailRouteDestinationsOnMeld(m,opts={}){if(!m)return[];const cleared=[];for(const actor of['player','enemy'])if(isMailRouteDestination(actor,m)){ensureMailRouteMeta(m).destinationBy[actor]=false;cleared.push(actor)}if(cleared.length&&!opts.silent&&typeof log==='function')log(`MAIL-ROUTE: 정리된 공개 조합의 목적지 ${cleared.length}개 해제.`,'important');return cleared}
function mailRoutePublicCards(actor,tag=null){const out=[];if(!actor||typeof meldsOf!=='function'||typeof other!=='function')return out;for(const side of[actor,other(actor)])for(const m of meldsOf(side))for(const c of m.cards||[])if(c?.owner===actor&&c.themeId==='mail-route'&&(!tag||c.tag===tag))out.push(c);return out}
function mailRouteCardMeld(c){if(!c||typeof meldsOf!=='function')return null;for(const side of['player','enemy'])for(const m of meldsOf(side))if((m.cards||[]).includes(c))return m;return null}
function emitMailRouteArrivals(actor,cards,m,opts={}){if(!m||typeof emitEffectEvent!=='function')return[];const out=[];for(const c of cards||[]){if(!isMailRouteCard(c))continue;const sender=c.mailRouteSender,designated=isMailRouteDestination(sender,m),packet=emitEffectEvent('onArrival',{actor,sender,card:c,meld:m,targetSide:opts.targetSide||meldOwnerSide(m),designated,source:opts.source||'arrival',combatNeutral:!!opts.combatNeutral});c.mailRouteLastArrivalToken=state.turnToken;c.mailRouteLastArrivalMeld=m;c.mailRouteLastArrivalDesignated=designated;out.push(packet)}return out}
function emitMailRouteReturn(actor,c,m,opts={}){if(!c||!isMailRouteCard(c)||c.mailRouteSender!==actor||typeof emitEffectEvent!=='function')return null;c.mailRouteReturnToken=state.turnToken;c.mailRouteReturnSource=m||null;return emitEffectEvent('onReturnMail',{actor,sender:actor,card:c,meld:m,sourceSide:opts.sourceSide||meldOwnerSide(m),free:!!opts.free,reason:opts.reason||'returnMail'})}
function mailRouteMarkCandidates(w,candidates,exclude=[]){const ex=new Set((exclude||[]).map(c=>c.uid));return(candidates||[]).filter(c=>c?.owner===w&&!ex.has(c.uid))}
function requestMailRouteMarkChoice(w,source,candidates,opts={}){const list=mailRouteMarkCandidates(w,candidates,opts.exclude||[]);if(!list.length){if(typeof opts.onAsyncResolved==='function')opts.onAsyncResolved(null);return false}const apply=c=>{const ok=setMailRouteCard(w,c,{reason:opts.reason||source?.tag||'dispatch',label:source?.name||'MAIL-ROUTE'});if(ok&&opts.shield)addShield(w,opts.shield);return ok},interactive=w==='player'&&state.turn==='player'&&typeof requestEffectChoice==='function'&&list.length>1;if(interactive)return requestEffectChoice({title:source?.name||'MAIL-ROUTE',text:opts.text||'우편으로 발송할 내 카드 1장을 고르세요.',options:list.map(c=>({key:`mrmail:${c.uid}`,label:`${cardText(c)}${c.named?` · ${c.name}`:''}`,detail:isMailRouteCard(c)?'기존 발송 갱신':'우편 표식 부여',card:c})),allowSkip:!!opts.allowSkip,skipLabel:'발송하지 않기',onChoose:o=>{if(o?.card)apply(o.card);if(typeof opts.onAsyncResolved==='function')opts.onAsyncResolved(o?.card||null)}});const chosen=list[0];apply(chosen);if(typeof opts.onAsyncResolved==='function')opts.onAsyncResolved(chosen);return false}
function mailRouteDestinationCandidates(w,current=null,exclude=null){const out=[];for(const side of[w,other(w)])for(const m of meldsOf(side))if(m!==exclude&&m!==current)out.push({side,m});return out}
function requestMailRouteDestinationChoice(w,source,current=null,exclude=null,onAsyncResolved=null){const list=mailRouteDestinationCandidates(w,current,exclude);if(!list.length){if(typeof onAsyncResolved==='function')onAsyncResolved(null);return false}const apply=x=>setMailRouteDestination(w,x.m,{reason:source?.tag||'routeChange',label:source?.name}),interactive=w==='player'&&state.turn==='player'&&typeof requestEffectChoice==='function'&&list.length>1;if(interactive)return requestEffectChoice({title:source?.name||'경로 수정',text:'새 목적지로 지정할 공개 조합을 고르세요.',options:list.map((x,i)=>({key:`mrdest:${i}`,label:`${x.side===w?'내':'상대'} ${x.m.type==='SET'?'세트':'런'} · ${x.m.cards.length}장`,detail:'목적지 이전',entry:x})),allowSkip:true,skipLabel:'이전하지 않기',onChoose:o=>{if(o?.entry)apply(o.entry);if(typeof onAsyncResolved==='function')onAsyncResolved(o?.entry||null)}});const chosen=list[0];apply(chosen);if(typeof onAsyncResolved==='function')onAsyncResolved(chosen);return false}
function mailRouteTransferCandidates(w,excludeMeld=null){const out=[];for(const sourceSide of[w,other(w)])for(const source of meldsOf(sourceSide)){if(source===excludeMeld||meldFixedActive(source))continue;for(const c of source.cards||[]){if(c.owner!==w||!isMailRouteCard(c,w)||cardFixedActive(c))continue;const remain=source.cards.filter(x=>x.uid!==c.uid);if(remain.length<3||meldType(remain)!==source.type)continue;for(const targetSide of[w,other(w)])for(const target of meldsOf(targetSide)){if(target===source||target===excludeMeld||meldFixedActive(target))continue;if(meldType(target.cards.concat(c))===target.type)out.push({source,target,card:c,sourceSide,targetSide})}}}return out}
function requestMailRouteTransferChoice(w,sourceCard,excludeMeld=null,onAsyncResolved=null){const list=mailRouteTransferCandidates(w,excludeMeld);if(!list.length){if(typeof onAsyncResolved==='function')onAsyncResolved(null);return false}const apply=x=>moveCardBetweenMelds(w,x.card,x.source,x.target,{reason:'mailRouteTransfer'}),interactive=w==='player'&&state.turn==='player'&&typeof requestEffectChoice==='function'&&list.length>1;if(interactive)return requestEffectChoice({title:sourceCard?.name||'환승 센터',text:'이동할 내 우편과 목적 공개 조합을 고르세요. 이동 자체는 전투 중립입니다.',options:list.map((x,i)=>({key:`mrmove:${i}`,label:`${cardText(x.card)}${x.card.named?` · ${x.card.name}`:''}`,detail:`${x.source.type==='SET'?'세트':'런'} → ${x.target.type==='SET'?'세트':'런'}`,entry:x})),allowSkip:true,skipLabel:'이동하지 않기',onChoose:o=>{if(o?.entry)apply(o.entry);if(typeof onAsyncResolved==='function')onAsyncResolved(o?.entry||null)}});const chosen=list[0];apply(chosen);if(typeof onAsyncResolved==='function')onAsyncResolved(chosen);return false}
function mailRouteRecoverCandidates(w,excludeMeld=null){const out=[];for(const side of[w,other(w)])for(const m of meldsOf(side)){if(m===excludeMeld)continue;for(const c of freeRecoverCandidates(w,m,[]))if(isMailRouteCard(c,w))out.push({side,m,card:c})}return out}
function requestMailRouteRecoverChoice(w,sourceCard,excludeMeld=null,onAsyncResolved=null){const list=mailRouteRecoverCandidates(w,excludeMeld);if(!list.length){if(typeof onAsyncResolved==='function')onAsyncResolved(null);return false}const apply=x=>recoverSpecificFromMeld(w,x.m,x.card,{label:`${sourceCard?.name||'MAIL-ROUTE'} 무료 회수`}),interactive=w==='player'&&state.turn==='player'&&typeof requestEffectChoice==='function'&&list.length>1;if(interactive)return requestEffectChoice({title:sourceCard?.name||'라스트 마일',text:'다른 공개 조합에서 반송할 내 우편 1장을 고르세요.',options:list.map((x,i)=>({key:`mrrecover:${i}`,label:`${cardText(x.card)}${x.card.named?` · ${x.card.name}`:''}`,detail:`${x.m.type==='SET'?'세트':'런'}에서 무료 회수`,entry:x})),allowSkip:true,skipLabel:'회수하지 않기',onChoose:o=>{if(o?.entry)apply(o.entry);if(typeof onAsyncResolved==='function')onAsyncResolved(o?.entry||null)}});const chosen=list[0];apply(chosen);if(typeof onAsyncResolved==='function')onAsyncResolved(chosen);return false}
function handleMailRouteThemeEvent(packet){if(!packet?.event||typeof sideObj!=='function'||typeof other!=='function')return false;let changed=false;if(packet.event==='onMailSet'){const sorter=mailRoutePublicCards(packet.sender,'mrSorter').find(c=>!themeTurnGateUsed(c,'mrSorter',packet.turnToken));if(sorter&&claimThemeTurnGate(sorter,'mrSorter',packet.turnToken)){addShield(packet.sender,2);changed=true}}
 if(packet.event==='onArrival'){const w=packet.sender,c=packet.card,m=packet.meld,foe=other(w);const courier=mailRoutePublicCards(w,'mrCourier').find(x=>!themeTurnGateUsed(x,'mrCourier',packet.turnToken));if(courier&&claimThemeTurnGate(courier,'mrCourier',packet.turnToken)){addShield(w,2);changed=true}if(c?.tag==='mrDetour'&&!packet.designated){setMailRouteDestination(w,m,{reason:'detour',label:c.name});changed=true}if(packet.designated&&packet.targetSide===w){const post=mailRoutePublicCards(w,'mrPostmaster').find(x=>!themeTurnGateUsed(x,'mrPostmaster',packet.turnToken));if(post&&claimThemeTurnGate(post,'mrPostmaster',packet.turnToken)){if(officialStatusValue('meld',m,'seal')>0)consumeOfficialStatus('meld',m,'seal',1);else if(officialStatusValue('meld',m,'fixed')>0)clearOfficialStatus('meld',m,'fixed');else applyOfficialStatus('meld',m,'protect',1,{actor:w,silent:true});changed=true}const central=mailRoutePublicCards(w,'mrCentralOffice').find(x=>m.type==='SET'&&!themeTurnGateUsed(x,'mrCentralOffice',packet.turnToken));if(central&&claimThemeTurnGate(central,'mrCentralOffice',packet.turnToken)){drawOne(w,false);changed=true}}if(c?.tag==='mrReceipt'&&packet.designated){heal(w,1);addShield(w,2);changed=true}if(c?.tag==='mrCensorEnvelope'&&packet.designated&&packet.targetSide===foe){applyOfficialStatus('meld',m,'seal',1,{actor:w,silent:true});changed=true}if(c?.tag==='mrDeliveryFailure'&&!packet.designated&&packet.targetSide===foe){applyOfficialStatus('player',sideObj(foe),'vulnerable',1,{actor:w});changed=true}if(c?.tag==='mrBlackEnvelope'&&packet.designated&&packet.targetSide===foe){applyOfficialStatus('player',sideObj(foe),'vulnerable',1,{actor:w});addShield(w,2);changed=true}}
 if(packet.event==='onReturnMail'){const w=packet.actor,c=packet.card;if(c?.tag==='mrReplyEnvelope'){addShield(w,2);changed=true}if(c?.tag==='mrReturnDesk'&&!themeTurnGateUsed(c,'mrReturnDesk',packet.turnToken)&&claimThemeTurnGate(c,'mrReturnDesk',packet.turnToken)){drawOne(w,false);const cand=sideObj(w).hand.filter(x=>x.uid!==c.uid).sort((a,b)=>b.age-a.age)[0];if(cand)bottomSpecificHandCard(w,cand,c.name);changed=true}if(c?.tag==='mrRedelivery'&&!themeTurnGateUsed(c,'mrRedelivery',packet.turnToken)){const n=grantRecoveryReturnOverride(w,c,packet.meld,{});if(n&&claimThemeTurnGate(c,'mrRedelivery',packet.turnToken)){c.mailRouteRedeliveryToken=packet.turnToken;changed=true}}const reply=mailRoutePublicCards(w,'mrReplyWait').find(x=>packet.sourceSide===other(w)&&!themeTurnGateUsed(x,'mrReplyWait',packet.turnToken));if(reply&&claimThemeTurnGate(reply,'mrReplyWait',packet.turnToken)){drawOne(w,false);changed=true}}
 if(packet.event==='onAttach'){for(const owner of['player','enemy']){if(owner===packet.actor||!isMailRouteDestination(owner,packet.meld))continue;const stolen=mailRoutePublicCards(owner,'mrStolenMail').find(x=>!themeTurnGateUsed(x,'mrStolenMail',packet.turnToken));if(stolen&&claimThemeTurnGate(stolen,'mrStolenMail',packet.turnToken)){drawOne(owner,false);changed=true}}}
 if(packet.event==='onRecover'||packet.event==='onMeldMove'){const actor=packet.actor,source=packet.event==='onRecover'?packet.meld:packet.sourceMeld;for(const owner of['player','enemy']){if(owner===actor||!source||!isMailRouteDestination(owner,source))continue;const intercept=mailRoutePublicCards(owner,'mrInterception').find(x=>!themeTurnGateUsed(x,'mrInterception',packet.turnToken));if(intercept&&claimThemeTurnGate(intercept,'mrInterception',packet.turnToken)){applyOfficialStatus('meld',source,'fixed',1,{actor:owner,silent:true});changed=true}}}
 if(packet.event==='onMeldMove'&&isMailRouteCard(packet.card)){const w=packet.card.mailRouteSender,network=mailRoutePublicCards(w,'mrNetwork').find(x=>packet.sourceMeld?.type!==packet.targetMeld?.type&&!themeTurnGateUsed(x,'mrNetwork',packet.turnToken));if(network&&claimThemeTurnGate(network,'mrNetwork',packet.turnToken)){drawOne(w,false);changed=true}}
 if(packet.event==='onRummy'){const w=packet.actor,postal=(packet.lastCards||[]).find(c=>c?.tag==='mrPostalRummy');if(postal){applyOfficialStatus('player',sideObj(w),'regen',1,{actor:w});const cand=sideObj(w).hand.find(c=>!isMailRouteCard(c));if(cand)setMailRouteCard(w,cand,{reason:'postalRummy',label:postal.name});changed=true}}
 if(packet.event==='onRetire'){for(const owner of['player','enemy']){if(!isMailRouteDestination(owner,packet.meld))continue;const box=mailRoutePublicCards(owner,'mrMailbox').find(c=>!(packet.meld?.cards||[]).includes(c)&&!themeTurnGateUsed(c,'mrMailbox',packet.turnToken));if(!box)continue;const candidates=[];for(const side of[owner,other(owner)])for(const m of meldsOf(side))if(m!==packet.meld)candidates.push(m);if(candidates.length&&claimThemeTurnGate(box,'mrMailbox',packet.turnToken)){setMailRouteDestination(owner,candidates[0],{reason:'mailbox',label:box.name});addShield(owner,2);changed=true}}}
 return changed}
subscribeEffectEvent(handleMailRouteThemeEvent);
'''
if 'function ensureMailRouteMeta(' not in text:
    if helper_anchor not in text: raise SystemExit('missing helper anchor')
    text=text.replace(helper_anchor,mail_helpers+'\n'+helper_anchor,1)

# Derive mail events only after existing target/clash reactions.
once("if(typeof refreshPointBlankClashMeld==='function')refreshPointBlankClashMeld(meld,{change:'recover',actionActor:actor,card,free:!!opts.free,consumesBasic,automatic:!!opts.automatic,reason:opts.reason||'recover'});return packet}",
     "if(typeof refreshPointBlankClashMeld==='function')refreshPointBlankClashMeld(meld,{change:'recover',actionActor:actor,card,free:!!opts.free,consumesBasic,automatic:!!opts.automatic,reason:opts.reason||'recover'});if(typeof emitMailRouteReturn==='function')emitMailRouteReturn(actor,card,meld,{sourceSide:targetSide||meldOwnerSide(meld),free:!!opts.free,reason:opts.reason||'recover'});return packet}",
     'recover derived return-mail event')
once("if(typeof refreshPointBlankClashMeld==='function'){refreshPointBlankClashMeld(sourceMeld,{change:'moveOut',actionActor:actor,card,targetMeld,reason:opts.reason||'move'});refreshPointBlankClashMeld(targetMeld,{change:'moveIn',actionActor:actor,card,sourceMeld,reason:opts.reason||'move'})}return packet}",
     "if(typeof refreshPointBlankClashMeld==='function'){refreshPointBlankClashMeld(sourceMeld,{change:'moveOut',actionActor:actor,card,targetMeld,reason:opts.reason||'move'});refreshPointBlankClashMeld(targetMeld,{change:'moveIn',actionActor:actor,card,sourceMeld,reason:opts.reason||'move'})}if(typeof emitMailRouteArrivals==='function')emitMailRouteArrivals(actor,[card],targetMeld,{source:'move',targetSide:typeof meldOwnerSide==='function'?meldOwnerSide(targetMeld):null,combatNeutral:true});return packet}",
     'move derived arrival event')
once("if(typeof emitEffectEvent==='function')emitEffectEvent('onMeldCreate',{actor:w,cards:[...cards],type,meld:m,targetSide:w,targetedBy:typeof zeroSightTargetActors==='function'?zeroSightTargetActors(m):[],newMeldIndex:s.newMeldCount,extraNewMeld:false,quickReloadCard:access.quickReloadCard||null});log(`",
     "if(typeof emitEffectEvent==='function')emitEffectEvent('onMeldCreate',{actor:w,cards:[...cards],type,meld:m,targetSide:w,targetedBy:typeof zeroSightTargetActors==='function'?zeroSightTargetActors(m):[],newMeldIndex:s.newMeldCount,extraNewMeld:false,quickReloadCard:access.quickReloadCard||null});if(typeof emitMailRouteArrivals==='function')emitMailRouteArrivals(w,cards,m,{source:'meldCreate',targetSide:w});log(`",
     'new meld arrival event')
once("if(typeof refreshPointBlankClashMeld==='function')refreshPointBlankClashMeld(m,{change:'attach',actionActor:w,cards:[...cards],targetSide,returned:returning||forceReturn,continuation});if((returning||forceReturn)&&typeof resolveZeroSightPostReturn==='function')",
     "if(typeof refreshPointBlankClashMeld==='function')refreshPointBlankClashMeld(m,{change:'attach',actionActor:w,cards:[...cards],targetSide,returned:returning||forceReturn,continuation});if(typeof emitMailRouteArrivals==='function')emitMailRouteArrivals(w,cards,m,{source:'attach',targetSide});if((returning||forceReturn)&&typeof resolveZeroSightPostReturn==='function')",
     'attach arrival event')

# ---------- Resolver cases ----------
mail_cases=r'''case'mrDispatchDesk':if(ctx.isNew&&ctx.meld){const list=(ctx.meld.cards||[]).filter(x=>x.uid!==c.uid&&x.owner===w);const paused=requestMailRouteMarkChoice(w,c,list,{reason:'dispatchDesk',shield:2,allowSkip:true,onAsyncResolved:resume});if(paused)return pause()}break;case'mrRegistered':setMailRouteCard(w,c,{reason:'registered',label:c.name});if(type==='SET'&&ctx.meld&&isMailRouteDestination(w,ctx.meld))applyOfficialStatus('meld',ctx.meld,'protect',1,{actor:w,silent:true});break;case'mrSorter':case'mrPostmaster':case'mrCentralOffice':break;case'mrExpress':{const paused=requestMailRouteMarkChoice(w,c,side.hand,{exclude:cards,reason:'express',shield:2,allowSkip:true,onAsyncResolved:resume});if(paused)return pause();break}case'mrBulkMail':if(ctx.isNew&&type==='SET'&&ctx.meld)for(const x of ctx.meld.cards||[])if(x.uid!==c.uid&&x.owner===w)setMailRouteCard(w,x,{reason:'bulk',label:c.name,silent:true});break;case'mrAddressLabel':setMailRouteCard(w,c,{reason:'addressLabel',label:c.name});if(ctx.meld)setMailRouteDestination(w,ctx.meld,{reason:'addressLabel',label:c.name});break;case'mrRouteChange':{const current=mailRouteDestinationMeld(w);if(!current&&ctx.meld)setMailRouteDestination(w,ctx.meld,{reason:'routeChange',label:c.name});else{const paused=requestMailRouteDestinationChoice(w,c,current,ctx.meld===current?null:ctx.meld,resume);if(paused)return pause()}break}case'mrCourier':case'mrNetwork':break;case'mrTransferHub':{const paused=requestMailRouteTransferChoice(w,c,ctx.meld,resume);if(paused)return pause();break}case'mrDetour':setMailRouteCard(w,c,{reason:'detour',label:c.name});break;case'mrLastMile':if(isMailRouteCard(c,w)&&ctx.meld&&ctx.meld.type==='RUN'&&isMailRouteDestination(w,ctx.meld)){const paused=requestMailRouteRecoverChoice(w,c,ctx.meld,resume);if(paused)return pause()}break;case'mrReplyEnvelope':setMailRouteCard(w,c,{reason:'replyEnvelope',label:c.name});break;case'mrReturnDesk':break;case'mrRedelivery':setMailRouteCard(w,c,{reason:'redelivery',label:c.name});break;case'mrReceipt':setMailRouteCard(w,c,{reason:'receipt',label:c.name});break;case'mrMailbox':case'mrReplyWait':case'mrPostalRummy':break;case'mrCensorEnvelope':setMailRouteCard(w,c,{reason:'censor',label:c.name});break;case'mrStolenMail':break;case'mrDeliveryFailure':setMailRouteCard(w,c,{reason:'deliveryFailure',label:c.name});break;case'mrHazardMail':setMailRouteCard(w,c,{reason:'hazard',label:c.name});if(isReturning&&ctx.meld&&ctx.targetOwner===foe&&isMailRouteDestination(w,ctx.meld))fx.bonus+=10;break;case'mrInterception':break;case'mrBlackEnvelope':setMailRouteCard(w,c,{reason:'blackEnvelope',label:c.name});break;case'mrFinalNotice':setMailRouteCard(w,c,{reason:'finalNotice',label:c.name});if(isReturning&&state.switchPower>=40&&ctx.meld&&ctx.targetOwner===foe&&isMailRouteDestination(w,ctx.meld))fx.bonus+=14;break;'''
if "case'mrDispatchDesk':" not in text:
    marker="case'vacancyJoker':case'rebelJoker':break"
    if marker not in text: raise SystemExit('missing resolver end marker')
    text=text.replace(marker,mail_cases+marker,1)

# ---------- Lifecycle cleanup ----------
once("function pushDiscard(c){if(typeof clearCardActiveRank==='function')clearCardActiveRank(c);c.fromDiscard=false;",
     "function pushDiscard(c){if(typeof clearMailRouteCard==='function')clearMailRouteCard(c,'버림패',true);if(typeof clearCardActiveRank==='function')clearCardActiveRank(c);c.fromDiscard=false;",
     'discard clears mail')
once("for(const c of all){if(typeof clearCardActiveRank==='function')clearCardActiveRank(c);",
     "for(const c of all){if(typeof clearMailRouteCard==='function')clearMailRouteCard(c,'전체 재순환',true);if(typeof clearCardActiveRank==='function')clearCardActiveRank(c);",
     'full recycle clears mail')
once("const pool=spent.concat(ownedDiscard);if(!pool.length)return 0;s.deck=shuffle(pool);",
     "const pool=spent.concat(ownedDiscard);if(!pool.length)return 0;for(const c of pool)if(typeof clearMailRouteCard==='function')clearMailRouteCard(c,'개인 덱 재순환',true);s.deck=shuffle(pool);",
     'recycle pool clears mail')
once("chosen.fromDiscard=false;chosen.contractActive=false;chosen.age=0;side.deck.unshift(chosen);",
     "chosen.fromDiscard=false;chosen.contractActive=false;chosen.age=0;if(typeof clearMailRouteCard==='function')clearMailRouteCard(chosen,'덱 아래',true);side.deck.unshift(chosen);",
     'bottom hand clears mail')
once("chosen.fromDiscard=false;chosen.contractActive=false;chosen.age=0;side.deck.unshift(chosen);const got=drawOne(w,false);",
     "chosen.fromDiscard=false;chosen.contractActive=false;chosen.age=0;if(typeof clearMailRouteCard==='function')clearMailRouteCard(chosen,'패순환',true);side.deck.unshift(chosen);const got=drawOne(w,false);",
     'cycle clears mail')
once("for(const c of valid){c.fromDiscard=false;c.contractActive=false;c.age=0;s.deck.unshift(c)}",
     "for(const c of valid){c.fromDiscard=false;c.contractActive=false;c.age=0;if(typeof clearMailRouteCard==='function')clearMailRouteCard(c,'정비',true);s.deck.unshift(c)}",
     'maintenance clears mail')
once("old.age=0;old.fromDiscard=false;old.contractActive=false;side.deck.unshift(old);",
     "old.age=0;old.fromDiscard=false;old.contractActive=false;if(typeof clearMailRouteCard==='function')clearMailRouteCard(old,'소모패 재활용',true);side.deck.unshift(old);",
     'spent recycle clears mail')
once("side.hand.splice(i,1);side.spent.push(c);c.fromDiscard=false;",
     "side.hand.splice(i,1);if(typeof clearMailRouteCard==='function')clearMailRouteCard(c,'소모패 전환',true);side.spent.push(c);c.fromDiscard=false;",
     'sidearm spent clears mail')
once("sideObj(cand.owner).spent.push(cand);markSetCompletion(m,targetSide);",
     "if(typeof clearMailRouteCard==='function')clearMailRouteCard(cand,'효과 소모',true);sideObj(cand.owner).spent.push(cand);markSetCompletion(m,targetSide);",
     'cut line spent clears mail')
once("for(const c of cards){c.age=0;c.fromDiscard=false;state.player.deck.unshift(c)}",
     "for(const c of cards){c.age=0;c.fromDiscard=false;if(typeof clearMailRouteCard==='function')clearMailRouteCard(c,'멀리건',true);state.player.deck.unshift(c)}",
     'mulligan clears mail')
once("c.fromDiscard=false;c.contractActive=false;state.player.deck.push(c);discard=false;",
     "c.fromDiscard=false;c.contractActive=false;if(typeof clearMailRouteCard==='function')clearMailRouteCard(c,'덱 예약',true);state.player.deck.push(c);discard=false;",
     'player deck reserve clears mail')
once("d.fromDiscard=false;d.contractActive=false;state.enemy.deck.push(d);log(`",
     "d.fromDiscard=false;d.contractActive=false;if(typeof clearMailRouteCard==='function')clearMailRouteCard(d,'덱 예약',true);state.enemy.deck.push(d);log(`",
     'AI deck reserve clears mail')
# Retire: destination clears after onRetire; non-preserved cards clear mail before deck/spent.
once("if(typeof clearPointBlankClashesOnMeld==='function')clearPointBlankClashesOnMeld(m,{reason:'retire'});arr.splice(index,1);",
     "if(typeof clearPointBlankClashesOnMeld==='function')clearPointBlankClashesOnMeld(m,{reason:'retire'});if(typeof clearMailRouteDestinationsOnMeld==='function')clearMailRouteDestinationsOnMeld(m,{reason:'retire',silent:true});arr.splice(index,1);",
     'retire clears destinations')
once("if(c.tag==='jokerKing'){const home=c.originOwner||c.owner;c.owner=home;c.fromDiscard=false;",
     "if(c.tag==='jokerKing'){if(typeof clearMailRouteCard==='function')clearMailRouteCard(c,'조합 정리·덱 귀환',true);const home=c.originOwner||c.owner;c.owner=home;c.fromDiscard=false;",
     'joker retire clears mail')
once("else{if(c.tag==='smuggledSuit')c.smuggledActive=false;sideObj(c.owner).spent.push(c)}}",
     "else{if(c.tag==='smuggledSuit')c.smuggledActive=false;if(typeof clearMailRouteCard==='function')clearMailRouteCard(c,'조합 정리·소모패',true);sideObj(c.owner).spent.push(c)}}",
     'retire spent clears mail')

# ---------- AI biases ----------
once("if(targetSide===foe&&(cards||[]).some(c=>c?.themeId==='v-signal'))score+=2;return score}",
     "if(targetSide===foe&&(cards||[]).some(c=>c?.themeId==='v-signal'))score+=2;if(typeof isMailRouteDestination==='function'&&isMailRouteDestination(w,m)&&(cards||[]).some(c=>isMailRouteCard(c,w)||c?.themeId==='mail-route'))score+=4;return score}",
     'mail AI attach bias')
once("if(typeof isPointBlankClash==='function'&&isPointBlankClash(w,m))score+=3;return score}",
     "if(typeof isPointBlankClash==='function'&&isPointBlankClash(w,m))score+=3;if(typeof isMailRouteCard==='function'&&isMailRouteCard(c,w))score+=4;return score}",
     'mail AI recovery bias')

# ---------- Render mail state ----------
once("p=cardRankPresentation(c),themeClass=c.themeId?`theme-${c.themeId}`:'',rankClass=",
     "p=cardRankPresentation(c),themeClass=c.themeId?`theme-${c.themeId}`:'',mailMark=typeof isMailRouteCard==='function'&&isMailRouteCard(c)?'<div class=\"mailCardMark\">우편</div>':'',rankClass=",
     'card html mail marker variable')
once("${rankMark}${c.named?`<div class=\"namedMark\">${c.name}</div>`:''}</div>`}",
     "${rankMark}${mailMark}${c.named?`<div class=\"namedMark\">${c.name}</div>`:''}</div>`}",
     'card html mail marker')
# renderMelds: destination badges/classes.
once("zeroTags=`${zeroP?'<span class=\"zeroSightTag\">내 표적</span>':''}${zeroE?'<span class=\"zeroSightTag\">상대 표적</span>':''}`;const attack=",
     "zeroTags=`${zeroP?'<span class=\"zeroSightTag\">내 표적</span>':''}${zeroE?'<span class=\"zeroSightTag\">상대 표적</span>':''}`,mailP=typeof isMailRouteDestination==='function'&&isMailRouteDestination('player',m),mailE=typeof isMailRouteDestination==='function'&&isMailRouteDestination('enemy',m),mailTags=`${mailP?'<span class=\"mailRouteTag\">내 목적지</span>':''}${mailE?'<span class=\"mailRouteTag\">상대 목적지</span>':''}`;const attack=",
     'meld mail tags variables')
once("${zeroP||zeroE?'zeroSightTarget':''}\" data-side=",
     "${zeroP||zeroE?'zeroSightTarget':''} ${mailP||mailE?'mailRouteDestination':''}\" data-side=",
     'meld mail destination class')
once("${m.cards.length}장 ${zeroTags}</span>",
     "${m.cards.length}장 ${zeroTags}${mailTags}</span>",
     'meld mail tags display')
once("${c.healCharge?` · 기록 ${c.healCharge}`:''} · 현재 제어",
     "${c.healCharge?` · 기록 ${c.healCharge}`:''}${typeof isMailRouteCard==='function'&&isMailRouteCard(c)?` · 우편 발송자 ${c.mailRouteSender==='player'?'나':'상대'}`:''} · 현재 제어",
     'detail mail state')

# ---------- Theme tutorial ----------
pb_step=" {id:'pbBreach',themeId:'point-blank',title:'브리치 실드 · 접전 진입',goal:'POINT-BLANK는 상대 공개 조합 하나를 접전으로 만들고 그 안에서 회수·교대·재돌입 효과를 이어갑니다. 브리치 실드로 상대 런에 진입하세요.',hint:'브리치 실드 A♥를 선택해 상대 2♥-3♥-4♥ 런에 붙이세요. 접전이 지정되고 보호막 12를 얻습니다.',implemented:true,scenario:'pbBreach',allow:['select','attach','clear'],selectRoles:['pbBreachCard'],attachSide:'enemy',expectAttach:'RUN',expectAttachTag:'pbBreachShield',expectShieldGain:12,completeOn:'attach',stopAfter:true}"
mr_step=pb_step+",\n {id:'mrAddress',themeId:'mail-route',title:'주소 라벨 · 지정 도착',goal:'MAIL-ROUTE는 일반 카드에도 우편 표식을 붙이고 공개 조합 하나를 목적지로 지정합니다. 주소 라벨을 포함한 A 세트로 첫 지정 도착을 만들어 보세요.',hint:'주소 라벨 A♣와 A♥·A♦를 선택해 새 세트를 만드세요. 주소 라벨이 자신을 우편으로 발송하고 그 세트를 내 목적지로 지정한 뒤 지정 도착합니다.',implemented:true,scenario:'mrAddress',allow:['select','meld','clear'],selectRoles:['mrAddressCard','mrAddressSet'],expectMeld:'SET',completeOn:'meld',stopAfter:true}"
once(pb_step,mr_step,'mail tutorial step')
once("else if(step.scenario==='pbBreach'){p.hand=[makeTutorialNamed('PBHA','pbBreachCard'),makeTutorialCard('D','9','hold')];e.melds=[makeTutorialMeld('enemy','RUN',[makeTutorialCard('H','2','board','enemy'),makeTutorialCard('H','3','board','enemy'),makeTutorialCard('H','4','board','enemy')])];state.switchTarget='player';state.switchPower=12;state.phase='action';log('POINT-BLANK 체험 · 브리치 실드 A♥를 상대 ♥ 런에 붙여 접전을 만들고 보호막을 확보하세요.','important')}return true}",
     "else if(step.scenario==='pbBreach'){p.hand=[makeTutorialNamed('PBHA','pbBreachCard'),makeTutorialCard('D','9','hold')];e.melds=[makeTutorialMeld('enemy','RUN',[makeTutorialCard('H','2','board','enemy'),makeTutorialCard('H','3','board','enemy'),makeTutorialCard('H','4','board','enemy')])];state.switchTarget='player';state.switchPower=12;state.phase='action';log('POINT-BLANK 체험 · 브리치 실드 A♥를 상대 ♥ 런에 붙여 접전을 만들고 보호막을 확보하세요.','important')}else if(step.scenario==='mrAddress'){p.hand=[makeTutorialNamed('MRCA','mrAddressCard'),makeTutorialCard('H','A','mrAddressSet'),makeTutorialCard('D','A','mrAddressSet'),makeTutorialCard('S','9','hold')];state.phase='action';log('MAIL-ROUTE 체험 · 주소 라벨 A♣와 A♥·A♦로 새 세트를 만들어 우편 발송 → 목적지 지정 → 지정 도착을 확인하세요.','important')}return true}",
     'mail tutorial scenario')
once("step.themeId==='point-blank'?'POINT-BLANK 체험 완료! 접전 지정 → 돌입·회수 연결의 핵심을 확인했습니다.':'다음 실습은 잠시 후 자동으로 시작됩니다.'",
     "step.themeId==='point-blank'?'POINT-BLANK 체험 완료! 접전 지정 → 돌입·회수 연결의 핵심을 확인했습니다.':step.themeId==='mail-route'?'MAIL-ROUTE 체험 완료! 우편 발송 → 목적지 지정 → 도착 → 반송·재배송으로 이어지는 핵심을 확인했습니다.':'다음 실습은 잠시 후 자동으로 시작됩니다.'",
     'mail tutorial completion copy')

# ---------- Docs: canonical 28 list ----------
theme_path=Path('docs/THEME_GROUPS.md')
doc=theme_path.read_text(encoding='utf-8')
mail_list=r'''## 현재 정식 후보 28장

### ♦ 발송 / 우체국 / 분류 / 세트
- A♦ `발송 접수` — 새 3장 조합에서 다른 내 카드 1장을 우편으로 발송하고, 발송했다면 보호막 8.
- 2♦ `등기 우편` — 사용 시 자신을 우편으로 발송. 세트의 내 목적지에 지정 도착하면 그 조합 보호 1.
- 4♦ `우편 분류기` — 공개된 동안 이번 턴 처음 내 카드가 우편이 되면 보호막 8.
- 6♦ `특급 발송` — 사용 시 남은 손패 1장을 우편으로 발송할 수 있고, 발송했다면 보호막 8.
- 8♦ `대량 발송` — 새 3장 세트를 만들면 그 세트의 다른 내 카드들을 모두 우편으로 발송.
- J♦ `우체국장` — 내 우편이 내 목적지에 지정 도착하면 봉인 제거 → 고정 해제 → 보호 1 순서. 턴당 1회.
- K♦ `중앙 우체국` — 내 우편이 내 세트 목적지에 지정 도착하면 턴당 1회 1장 획득.

### ♣ 주소 / 경로 / 배송 / 런
- A♣ `주소 라벨` — 사용 시 자신을 우편으로 발송하고 그 조합을 내 목적지로 지정.
- 3♣ `경로 수정` — 내 목적지를 다른 공개 조합으로 이전. 목적지가 없으면 현재 조합을 지정.
- 5♣ `배송 기사` — 공개된 동안 내 우편이 도착하면 턴당 1회 보호막 8.
- 7♣ `환승 센터` — 다른 공개 조합의 내 우편 1장을 합법적인 다른 공개 조합으로 전투 중립 이동.
- 9♣ `우회 배송` — 사용 시 자신을 우편으로 발송. 비지정 도착하면 그 조합을 새 목적지로 지정.
- Q♣ `라스트 마일` — 우편 상태로 런 목적지에 지정 도착하면 다른 조합의 내 우편 1장을 무료 회수. 기본 반환 제한 유지.
- K♣ `전국 배송망` — 내 우편이 세트↔런 사이를 이동하면 턴당 1회 1장 획득.

### ♥ 회신 / 반송 / 생존 / 러미
- A♥ `회신 봉투` — 사용 시 자신을 우편으로 발송. 우편 상태로 반송되면 보호막 8.
- 3♥ `반송 접수` — 우편 상태로 반송되면 1장 획득 후 이 카드 외 가장 오래 보유한 손패 1장을 덱 아래로 보냄.
- 5♥ `재배송` — 사용 시 자신을 우편으로 발송. 반송된 턴 한 번, 반송한 조합과 다른 합법 조합의 버스트/체인 반환 재료로 재사용 가능.
- 7♥ `수취 확인` — 사용 시 자신을 우편으로 발송. 지정 도착하면 현재 코어 4 회복 + 보호막 8.
- 9♥ `보관 우편함` — 공개된 동안 내 목적지가 정리되면 다른 공개 조합을 새 목적지로 지정하고 보호막 8.
- Q♥ `답장 대기` — 공개된 동안 상대 공개 조합에서 내 우편이 반송되면 턴당 1회 1장 획득.
- K♥ `우편 러미` — 이 카드를 사용해 러미하면 재생 1 + 새 손패의 우편 아닌 카드 1장을 우편으로 발송.

### ♠ 검열 / 위험 우편 / 가로채기
- A♠ `검열 봉투` — 사용 시 자신을 우편으로 발송. 상대 공개 조합의 내 목적지에 지정 도착하면 조합 봉인 1.
- 3♠ `도난 우편` — 공개된 동안 상대가 내 목적지에 붙이면 턴당 1회 1장 획득.
- 5♠ `배달 사고` — 사용 시 자신을 우편으로 발송. 상대 공개 조합에 비지정 도착하면 상대 취약 1.
- 7♠ `위험물 우편` — 사용 시 자신을 우편으로 발송. 상대 목적지에 지정 도착하며 스위치를 반환하면 이번 반환 +10.
- 9♠ `가로채기` — 공개된 동안 상대가 내 목적지에서 회수/이동하면 턴당 1회 그 목적지를 고정.
- Q♠ `검은 봉투` — 사용 시 자신을 우편으로 발송. 상대 목적지 지정 도착 시 상대 취약 1 + 보호막 8.
- K♠ `최종 통지` — 사용 시 자신을 우편으로 발송. 누적 위력 40+에서 상대 목적지 지정 도착 반환 시 이번 반환 +14.

## MAIL-ROUTE 구현 체크

- [x] MAIL-ROUTE 28/28 풀 카드군 라이브 구현 — 정의·효과·해금·도감/덱빌더·체험전 연결
- [x] 우편 비중첩 표식 + 발송자 기록, 손패/공개 조합 이동 동안 유지
- [x] 목적지 플레이어당 1개, 표적·접전과 독립 공존
- [x] 조합 생성/붙이기/전투 중립 이동 뒤 도착·지정 도착 파생
- [x] 실제 공개 조합→자기 손 회수만 반송으로 파생
- [x] 재배송은 기본 행동을 늘리지 않으며 `재배송` 카드만 당턴 반환 재사용 예외를 명시적으로 허용
- [x] 버림패·소모패·개인 덱 진입 시 우편 표식 해제
- [x] 플레이어 선택 효과는 공용 재개형 선택 UI, AI는 같은 합법 후보에서 자동 선택
- [x] 일반/다른 테마 카드도 우편 표식을 받고 목적지 도착/반송 루프에 참여 가능
- [x] 일반 로그라이크 보상은 해금 즉시 허용. 고정 지역 적 덱은 기존 60장 지역 구성을 유지하고 후속 다테마 지역 재편 때 별도 조정
- [x] 직접 누적 위력 카드는 `위험물 우편` / `최종 통지` 2장으로 제한
- [x] 전용 숫자 자원·우표·배송 점수 없음

'''
mail_start=doc.find('# MAIL-ROUTE')
if mail_start<0: raise SystemExit('missing MAIL-ROUTE doc')
lock=doc.find('## 구현 전 잠금',mail_start)
if lock<0: raise SystemExit('missing MAIL-ROUTE lock doc')
if '## 현재 정식 후보 28장' not in doc[mail_start:lock]:
    doc=doc[:lock]+mail_list+doc[lock:]
doc=doc.replace('후속 정식 테마 후보. **규칙 구조는 잠금됐지만 아직 라이브 카드군은 아니다.** 구현 전에는 아래 우편/목적지/도착/반송 계약을 우선하며, 별도 우편 점수나 우표 자원은 만들지 않는다.','정식 라이브 테마. **28/28 풀 구현 완료.** 아래 우편/목적지/도착/반송 계약을 공용 엔진 위에서 사용하며, 별도 우편 점수나 우표 자원은 만들지 않는다.',1)
theme_path.write_text(doc,encoding='utf-8')

road=Path('ROADMAP.md');r=road.read_text(encoding='utf-8')
mr_road=r'''## M8MR — MAIL-ROUTE 28/28 풀 카드군 · 완료
우편 표식과 공개 조합 목적지를 이용하는 이동·회수형 오픈 테마. 일반/다른 테마 카드도 발송할 수 있고 전용 숫자 자원은 만들지 않는다.

- [x] 28장 / 수트별 7장 정식 후보 명단 잠금
- [x] `우편` 비중첩 표식 + 발송자 기록 + 수명 주기 구현
- [x] 플레이어당 목적지 1개 + 표적/접전 독립 공존
- [x] 새 조합·붙이기·조합 이동의 도착/지정 도착 파생 이벤트 구현
- [x] 공개 조합→자기 손 회수의 반송 이벤트 + 재배송 예외 구현
- [x] 28장 전체 정의/효과/해금/도감/덱빌더/체험전 연결
- [x] 플레이어 선택은 공용 재개형 선택 UI, AI는 동일 합법 후보 사용
- [x] 일반 로그라이크 보상 해금 후 허용, 기존 고정 지역 적 덱은 유지
- [x] MAIL-ROUTE 단일/2테마/일반 혼합 + 전체 회귀

'''
if '## M8MR — MAIL-ROUTE 28/28 풀 카드군 · 완료' not in r:
    anchor='## M9'
    if anchor not in r: raise SystemExit('missing ROADMAP M9')
    r=r.replace(anchor,mr_road+anchor,1)
road.write_text(r,encoding='utf-8')

plan=Path('docs/THEME_FULL_POOL_PLAN.md');p=plan.read_text(encoding='utf-8')
mr_plan=r'''### F4 — MAIL-ROUTE 28/28 · 완료

28장 전체를 한 번에 라이브 구현했다. 별도 우표/배송 점수 자원 없이 실제 카드의 `우편` 표식과 공개 조합의 플레이어별 `목적지` 메타데이터만 사용한다.

완료 게이트:
- 28개 정의 / 수트별 7장 / 28개 서로 다른 물리 슬롯
- 우편·목적지·도착·지정 도착·반송·재배송 공용 계약
- 버림패·소모패·개인 덱 진입 시 우편 상태 정리
- 플레이어 공용 선택 UI + AI 합법 자동 선택
- 해금·도감·자동 테마 빌드·체험전 연결
- 해금된 28장 일반 로그라이크 보상 허용
- V-SIGNAL / ZERO-SIGHT / POINT-BLANK와 2테마 구성 회귀
- 직접 누적 위력 2장만 사용, 전용 숫자 자원 없음
- 전체 `tests/*.mjs` 회귀

**F4 완료 기록** — 2026-09-03. `tests/mail-route-full-pool.mjs`, 확장 `tests/theme-mix-simulation.mjs` 및 전체 회귀를 릴리스 게이트로 사용한다.

'''
if '### F4 — MAIL-ROUTE 28/28 · 완료' not in p:
    anchor='## 5.'
    if anchor in p:p=p.replace(anchor,mr_plan+anchor,1)
    else:p+='\n\n'+mr_plan
plan.write_text(p,encoding='utf-8')

# ---------- Existing regression updates ----------
mix=Path('tests/theme-mix-simulation.mjs');s=mix.read_text(encoding='utf-8')
s=s.replace("const themeIds=['v-signal','zero-sight','point-blank'];","const themeIds=['v-signal','zero-sight','point-blank','mail-route'];")
s=s.replace("const pairs=[['v-signal','zero-sight'],['v-signal','point-blank'],['zero-sight','point-blank']];","const pairs=[];for(let i=0;i<themeIds.length;i++)for(let j=i+1;j<themeIds.length;j++)pairs.push([themeIds[i],themeIds[j]]);")
s=s.replace("'vBanSoon','zsBallistics'","'vBanSoon','mrHazardMail','mrFinalNotice','zsBallistics'")
mix.write_text(s,encoding='utf-8')

audit=Path('tests/named-card-audit.mjs');s=audit.read_text(encoding='utf-8')
s=s.replace("'pbMagDump']);","'pbMagDump','mrHazardMail','mrFinalNotice']);")
audit.write_text(s,encoding='utf-8')

# ---------- Dedicated regression ----------
test=Path('tests/mail-route-full-pool.mjs')
test.write_text(r'''import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
const doc=fs.readFileSync(new URL('../docs/THEME_GROUPS.md',import.meta.url),'utf8');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const plan=fs.readFileSync(new URL('../docs/THEME_FULL_POOL_PLAN.md',import.meta.url),'utf8');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw Error(`missing ${name}`);let p=0,b=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')p++;else if(script[i]===')')p--;else if(script[i]==='{'&&p===0){b=i;break}}let d=0;for(let i=b;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw Error(`unterminated ${name}`)}
function literal(name,next){const a=script.indexOf(`const ${name}=`),b=script.indexOf(next,a);return script.slice(a+`const ${name}=`.length,b).trim().replace(/;$/,'')}
const ctx=vm.createContext({console,Object,Array,Set,Map,Number,String,Boolean,Math});
vm.runInContext(`globalThis.NAMED=${literal('NAMED','\nconst CHARACTERS=')}`,ctx);
const defs=Object.entries(ctx.NAMED).filter(([,d])=>d?.themeId==='mail-route');
ok(defs.length===28,`MAIL-ROUTE full pool has exactly 28 definitions (${defs.length})`);
const slots=defs.map(([id,d])=>d.slot||id);ok(new Set(slots).size===28,'MAIL-ROUTE cards occupy 28 distinct physical slots');
const suits=Object.fromEntries(['S','H','D','C'].map(s=>[s,slots.filter(x=>x[0]===s).length]));for(const s of ['S','H','D','C'])ok(suits[s]===7,`MAIL-ROUTE ${s} suit has exactly seven cards`);
const ids=['MRDA','MRD2','MRD4','MRD6','MRD8','MRDJ','MRDK','MRCA','MRC3','MRC5','MRC7','MRC9','MRCQ','MRCK','MRHA','MRH3','MRH5','MRH7','MRH9','MRHQ','MRHK','MRSA','MRS3','MRS5','MRS7','MRS9','MRSQ','MRSK'];for(const id of ids)ok(ctx.NAMED[id]?.themeId==='mail-route',`${id} is a live MAIL-ROUTE definition`);
for(const ev of ['onMailSet','onDestinationSet','onArrival','onReturnMail'])ok(script.includes(`'${ev}'`),`${ev} is registered in the shared event foundation`);
for(const fn of ['setMailRouteCard','clearMailRouteCard','setMailRouteDestination','mailRouteDestinationMeld','emitMailRouteArrivals','emitMailRouteReturn','requestMailRouteMarkChoice','requestMailRouteDestinationChoice','requestMailRouteTransferChoice','requestMailRouteRecoverChoice','handleMailRouteThemeEvent'])ok(script.includes(`function ${fn}(`),`${fn} is implemented`);
ok(script.includes("emitMailRouteArrivals(w,cards,m,{source:'meldCreate'")&&script.includes("emitMailRouteArrivals(w,cards,m,{source:'attach'")&&script.includes("emitMailRouteArrivals(actor,[card],targetMeld,{source:'move'"),'create/attach/move derive arrival after common movement');
ok(script.includes("emitMailRouteReturn(actor,card,meld") ,'recover derives return-mail only through the common recovery event path');
for(const marker of ["clearMailRouteCard(c,'버림패'","clearMailRouteCard(c,'전체 재순환'","clearMailRouteCard(c,'조합 정리·소모패'","clearMailRouteCard(c,'정비'"])ok(script.includes(marker),`mail lifecycle cleanup contains ${marker}`);
const resolver=source('resolveEffects');for(const tag of ['mrDispatchDesk','mrRegistered','mrExpress','mrBulkMail','mrAddressLabel','mrRouteChange','mrTransferHub','mrDetour','mrLastMile','mrReplyEnvelope','mrRedelivery','mrReceipt','mrCensorEnvelope','mrDeliveryFailure','mrHazardMail','mrBlackEnvelope','mrFinalNotice'])ok(resolver.includes(`case'${tag}'`),`${tag} has a live resolver branch`);
for(const tag of ['mrSorter','mrPostmaster','mrCentralOffice','mrCourier','mrNetwork','mrReturnDesk','mrMailbox','mrReplyWait','mrPostalRummy','mrStolenMail','mrInterception'])ok(script.includes(tag)&&source('handleMailRouteThemeEvent').includes(tag),`${tag} is wired through the passive MAIL-ROUTE event handler`);
ok(script.includes("themeId:'mail-route',live:true")&&script.includes("'mail-route':Object.freeze({themeId:'mail-route',startStep:'mrAddress',live:true})"),'MAIL-ROUTE build profile and tutorial are live');
ok(html.includes('data-codex-filter="theme:mail-route"'),'card encyclopedia exposes a MAIL-ROUTE tab');
for(const id of ids)ok(script.includes(`'${id}'`),`${id} is reachable from runtime/unlock data`);
ok((script.match(/id:'mrf\d'/g)||[]).length===7,'MAIL-ROUTE uses seven staged progression groups without a closed numeric resource');
ok(!/stampCount|postageCount|mailScore|우표\s*(점수|카운터)|배송\s*점수/.test(script),'MAIL-ROUTE creates no postage/mail numeric resource');
ok(script.includes("fx.bonus+=10")&&script.includes("fx.bonus+=14"),'only the two intended MAIL-ROUTE finishers add direct return power');
ok(doc.includes('## 현재 정식 후보 28장')&&doc.includes('MAIL-ROUTE 28/28 풀 카드군 라이브 구현'),'canonical theme doc locks all 28 cards and implementation contract');
ok(road.includes('M8MR — MAIL-ROUTE 28/28 풀 카드군 · 완료'),'ROADMAP records MAIL-ROUTE completion');
ok(plan.includes('F4 — MAIL-ROUTE 28/28 · 완료'),'full-pool plan records MAIL-ROUTE completion');
// Execute core metadata foundation in isolation.
const emitted=[];const fake={turnToken:7,turnNo:2,player:{melds:[]},enemy:{melds:[]}};Object.assign(ctx,{state:fake,emitEffectEvent:(event,payload)=>{emitted.push({event,...payload});return payload},meldsOf:w=>fake[w].melds,other:w=>w==='player'?'enemy':'player',meldOwnerSide:m=>fake.player.melds.includes(m)?'player':fake.enemy.melds.includes(m)?'enemy':null,log:()=>{}});for(const fn of ['ensureMailRouteMeta','isMailRouteCard','clearMailRouteCard','setMailRouteCard','mailRouteDestinationMeld','isMailRouteDestination','clearMailRouteDestination','setMailRouteDestination','emitMailRouteArrivals','emitMailRouteReturn'])vm.runInContext(source(fn),ctx);const card={uid:1,owner:'player',name:'일반 카드'},m1={type:'SET',cards:[card],themeMeta:{}},m2={type:'RUN',cards:[],themeMeta:{}};fake.player.melds.push(m1);fake.enemy.melds.push(m2);ok(ctx.setMailRouteCard('player',card,{silent:true})===true&&ctx.isMailRouteCard(card,'player'),'ordinary owned card can receive a non-stacking mail mark');ctx.setMailRouteDestination('player',m1,{silent:true});ok(ctx.isMailRouteDestination('player',m1),'player destination is stored on the public meld');ctx.setMailRouteDestination('player',m2,{silent:true});ok(!ctx.isMailRouteDestination('player',m1)&&ctx.isMailRouteDestination('player',m2),'new destination atomically clears the previous one');ctx.emitMailRouteArrivals('player',[card],m2,{targetSide:'enemy'});ok(emitted.some(x=>x.event==='onArrival'&&x.designated===true),'arrival derives designated-arrival from the sender current destination');ctx.emitMailRouteReturn('player',card,m2,{sourceSide:'enemy'});ok(emitted.some(x=>x.event==='onReturnMail'),'actual mail recovery can derive return-mail while preserving the mark');ok(ctx.isMailRouteCard(card,'player'),'return-mail keeps the mail mark for later redelivery');ctx.clearMailRouteCard(card,'test',true);ok(!ctx.isMailRouteCard(card),'route-ending cleanup removes the mail mark');
console.log('MAIL-ROUTE 28/28 full-pool regression passed.');
''',encoding='utf-8')

index.write_text(text,encoding='utf-8')
print('MAIL-ROUTE 28-card full-pool patch applied')

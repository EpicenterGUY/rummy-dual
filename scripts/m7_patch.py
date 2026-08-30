from pathlib import Path

p = Path('index.html')
s = p.read_text()

def rep(old, new, label):
    global s
    n = s.count(old)
    if n != 1:
        raise SystemExit(f'{label}: expected 1 match, got {n}')
    s = s.replace(old, new, 1)

rep(
    "const CORE_HP=60,CORE_COUNT=3,OVERLOAD=100,RECOVERY_UNIT=4;",
    """const CORE_HP=60,CORE_COUNT=3,OVERLOAD=100,RECOVERY_UNIT=4;
const OFFICIAL_STATUS=Object.freeze({
 vulnerable:{label:'취약',scopes:['player'],lifecycle:'nextDetonate'},
 seal:{label:'봉인',scopes:['player','meld','card'],lifecycle:'nextNamedEffect'},
 fixed:{label:'고정',scopes:['meld','card'],lifecycle:'throughNextOwnerTurn'},
 protect:{label:'보호',scopes:['meld','card'],lifecycle:'nextInterference'},
 regen:{label:'재생',scopes:['player'],lifecycle:'ownerTurnStartDecay'}
});
const EFFECT_EVENTS=Object.freeze(['onAcquire','onDiscard','onMeldCreate','onAttach','onBurst','onChain','onRecover','onRummy','onReturnSwitch','onDetonate','onCoreBreak','onTurnStart','onTurnEnd','onRetire']);
const EFFECT_ACTIONS=Object.freeze(['draw','heal','addShield','addPower','returnSwitch','applyStatus','retireMeld']);""",
    'status constants',
)

rep(
    "fuseArmed:false,status:{charged:0,reserved:0,cursed:0,pledged:0,marked:0},blockedUntilTurn:null",
    "fuseArmed:false,officialStatus:{seal:0,fixed:0,protect:0,fixedOwner:null,fixedThroughStart:null},status:{charged:0,reserved:0,cursed:0,pledged:0,marked:0},blockedUntilTurn:null",
    'card official status bag',
)

rep(
    "function blankStatus(){return{vulnerable:0,seal:0,regen:0}}",
    """function blankStatus(){return{vulnerable:0,seal:0,regen:0}}
function blankMeldStatus(){return{seal:0,fixed:0,protect:0,fixedOwner:null,fixedThroughStart:null}}
function officialStatusBag(scope,target){if(!target)return null;if(scope==='player'){target.status=target.status||blankStatus();return target.status}if(scope==='meld'){target.status=target.status||blankMeldStatus();if(target.status.protected!=null){target.status.protect=Math.max(target.status.protect||0,target.status.protected||0);delete target.status.protected}if(target.status.sealNamed!=null){target.status.seal=Math.max(target.status.seal||0,target.status.sealNamed||0);delete target.status.sealNamed}return target.status}if(scope==='card'){target.officialStatus=target.officialStatus||{seal:0,fixed:0,protect:0,fixedOwner:null,fixedThroughStart:null};return target.officialStatus}return null}
function officialStatusAllowed(scope,key){const def=OFFICIAL_STATUS[key];return !!def&&def.scopes.includes(scope)}
function officialStatusValue(scope,target,key){if(!officialStatusAllowed(scope,key))return 0;const bag=officialStatusBag(scope,target);return Math.max(0,Number(bag?.[key]||0))}
function setOfficialStatus(scope,target,key,n){if(!officialStatusAllowed(scope,key))return 0;const bag=officialStatusBag(scope,target);bag[key]=Math.max(0,Number(n||0));return bag[key]}
function applyOfficialStatus(scope,target,key,n=1,opts={}){if(!officialStatusAllowed(scope,key))return 0;const next=setOfficialStatus(scope,target,key,officialStatusValue(scope,target,key)+Math.max(0,Number(n||0)));const bag=officialStatusBag(scope,target);if(key==='fixed'&&opts.owner){bag.fixedOwner=opts.owner;bag.fixedThroughStart=sideObj(opts.owner).turnStarts+1}if(!opts.silent){const actor=opts.actor||null,label=OFFICIAL_STATUS[key].label,who=scope==='player'?(actor?switchName(actor):'플레이어'):scope==='meld'?'공개 조합':'카드';log(`${who} ${label} +${n}`,'important');if(actor)fxNode(`${label} +${n}`,'status',actor,40)}return next}
function consumeOfficialStatus(scope,target,key,n=1){const cur=officialStatusValue(scope,target,key);if(cur<=0)return 0;const used=Math.min(cur,Math.max(1,Number(n||1)));setOfficialStatus(scope,target,key,cur-used);return used}
function clearOfficialStatus(scope,target,key){const bag=officialStatusBag(scope,target),cur=officialStatusValue(scope,target,key);setOfficialStatus(scope,target,key,0);if(key==='fixed'&&bag){bag.fixedOwner=null;bag.fixedThroughStart=null}return cur}
function fixedStatusActive(scope,target){if(!officialStatusAllowed(scope,'fixed'))return false;const bag=officialStatusBag(scope,target);if(!bag||!(bag.fixed>0))return false;const owner=bag.fixedOwner;if(owner&&bag.fixedThroughStart!=null&&sideObj(owner).turnStarts>bag.fixedThroughStart){clearOfficialStatus(scope,target,'fixed');return false}return true}
function cardFixedActive(c){return fixedStatusActive('card',c)}
function meldFixedActive(m){return fixedStatusActive('meld',m)}
function applyMeldFixed(m,owner){if(!m)return false;applyOfficialStatus('meld',m,'fixed',1,{owner,silent:true});log(`${owner==='player'?'내':'상대'} 공개 조합 고정 · 다음 자기 턴 종료까지 회수·이동 불가.`,'important');return true}
function expireOwnerFixedStatuses(w){const now=sideObj(w).turnStarts;for(const m of meldsOf(w)){const mb=officialStatusBag('meld',m);if(mb?.fixedOwner===w&&mb.fixedThroughStart!=null&&now>=mb.fixedThroughStart)clearOfficialStatus('meld',m,'fixed');for(const c of m.cards){const cb=officialStatusBag('card',c);if(cb?.fixedOwner===w&&cb.fixedThroughStart!=null&&now>=cb.fixedThroughStart)clearOfficialStatus('card',c,'fixed')}}for(const c of [...sideObj(w).hand,...sideObj(w).deck,...sideObj(w).spent]){const cb=officialStatusBag('card',c);if(cb?.fixedOwner===w&&cb.fixedThroughStart!=null&&now>=cb.fixedThroughStart)clearOfficialStatus('card',c,'fixed')}}
function meldStatusText(m){const a=[],protect=officialStatusValue('meld',m,'protect'),seal=officialStatusValue('meld',m,'seal');if(protect)a.push(`보호 ${protect}`);if(seal)a.push(`봉인 ${seal}`);if(meldFixedActive(m))a.push('고정');return a.length?` · ${a.join(' · ')}`:''}
function runEffectAction(name,ctx={},payload={}){if(!EFFECT_ACTIONS.includes(name))return false;const actor=ctx.actor;if(name==='draw')return drawMany(actor,payload.count??1,false);if(name==='heal')return heal(actor,payload.amount??1);if(name==='addShield')return addShield(actor,payload.amount??1);if(name==='addPower')return addSwitchPower(actor,payload.amount??0,payload.label||'POWER');if(name==='returnSwitch')return returnSwitch(actor,payload.amount??0,payload.label||'RETURN',payload.opts||{});if(name==='applyStatus')return applyOfficialStatus(payload.scope,payload.target,payload.key,payload.amount??1,{actor,...(payload.opts||{})});if(name==='retireMeld')return retireMeld(payload.owner,payload.index??0,payload.reason||'효과');return false}""",
    'status helpers',
)

rep(
    "function lockMeldRecovery(m,owner){if(!m)return;m.recoverLockedOwner=owner;m.recoverLockedThroughStart=sideObj(owner).turnStarts+1;log(`${owner==='player'?'내':'상대'} 공개 조합이 다음 자기 턴 동안 회수 봉인.`,'important')}",
    "function lockMeldRecovery(m,owner){return applyMeldFixed(m,owner)}",
    'fixed wrapper',
)

rep(
    "function insuranceBlocks(actor,targetSide,m,targetCard){m.status=m.status||{};if((m.status.protected||0)>0){m.status.protected--;log(`조합 보호가 간섭을 1회 막았습니다.`,'good');return true}",
    "function insuranceBlocks(actor,targetSide,m,targetCard){if(targetCard&&consumeOfficialStatus('card',targetCard,'protect')){log(`카드 보호가 간섭을 1회 막았습니다.`,'good');return true}if(consumeOfficialStatus('meld',m,'protect')){log(`조합 보호가 간섭을 1회 막았습니다.`,'good');return true}",
    'protect consume',
)

rep(
    "function freeRecoverFromMeld(w,m,exclude=[],opts={}){const ex=new Set(exclude.map(c=>c.uid));for(let i=0;i<m.cards.length;i++){const c=m.cards[i];if(ex.has(c.uid)||c.owner!==w||c.enteredMeldToken===state.turnToken)continue;",
    "function freeRecoverFromMeld(w,m,exclude=[],opts={}){if(meldFixedActive(m))return null;const ex=new Set(exclude.map(c=>c.uid));for(let i=0;i<m.cards.length;i++){const c=m.cards[i];if(ex.has(c.uid)||c.owner!==w||c.enteredMeldToken===state.turnToken||cardFixedActive(c))continue;",
    'fixed free recovery',
)

rep(
    "function autoExtortToNewMeld(w,m){const foe=other(w),arr=meldsOf(foe);for(const om of arr){for(let i=0;i<om.cards.length;i++){const c=om.cards[i];if(protectedByConstruction(om,c))continue;",
    "function autoExtortToNewMeld(w,m){const foe=other(w),arr=meldsOf(foe);for(const om of arr){if(meldFixedActive(om))continue;for(let i=0;i<om.cards.length;i++){const c=om.cards[i];if(cardFixedActive(c)||protectedByConstruction(om,c))continue;",
    'fixed extortion',
)

rep(
    "function cutOppositeEnd(w,targetSide,m,newCard){if(m.type!=='RUN'||m.cards.length<4)return false;",
    "function cutOppositeEnd(w,targetSide,m,newCard){if(m.type!=='RUN'||m.cards.length<4||meldFixedActive(m))return false;",
    'fixed cut meld',
)
rep(
    "if(!cand||protectedByConstruction(m,cand))return false;",
    "if(!cand||cardFixedActive(cand)||protectedByConstruction(m,cand))return false;",
    'fixed cut card',
)

rep(
    "if(side.status.seal>0){side.status.seal--;log(`${c.name}: 봉인으로 효과가 무효.`,'hit');continue}if(ctx.isAttach&&ctx.meld?.status?.sealNamed>0&&c.tag!=='venomNeedle'){ctx.meld.status.sealNamed--;log(`${c.name}: 조합의 효과 봉인으로 무효.`,'hit');continue}",
    "if(consumeOfficialStatus('player',side,'seal')){log(`${c.name}: 봉인으로 효과가 무효.`,'hit');continue}if(ctx.isAttach&&c.tag!=='venomNeedle'&&consumeOfficialStatus('meld',ctx.meld,'seal')){log(`${c.name}: 조합의 봉인으로 효과가 무효.`,'hit');continue}if(consumeOfficialStatus('card',c,'seal')){log(`${c.name}: 카드 봉인으로 효과가 무효.`,'hit');continue}",
    'seal consume',
)

rep(
    "case'venomNeedle':if(ctx.isAttach&&ctx.targetOwner===foe){ctx.meld.status=ctx.meld.status||{};ctx.meld.status.sealNamed=(ctx.meld.status.sealNamed||0)+1;log(`${c.name}: 상대 조합의 다음 네임드 효과 봉인.`,'important')}break;",
    "case'venomNeedle':if(ctx.isAttach&&ctx.targetOwner===foe){runEffectAction('applyStatus',{actor:w},{scope:'meld',target:ctx.meld,key:'seal',amount:1,opts:{silent:true}});log(`${c.name}: 상대 조합의 다음 네임드 효과 봉인.`,'important')}break;",
    'venom seal apply',
)
rep(
    "case'branchLink':if(type==='RUN'){ctx.meld.status=ctx.meld.status||{};ctx.meld.status.protected=(ctx.meld.status.protected||0)+1}break;",
    "case'branchLink':if(type==='RUN')runEffectAction('applyStatus',{actor:w},{scope:'meld',target:ctx.meld,key:'protect',amount:1,opts:{silent:true}});break;",
    'branch protect apply',
)

rep(
    "const m={type,cards:[...cards],chain:0,createdTurn:state.turnNo,createdToken:state.turnToken,lastAttachToken:null,recoverLockedOwner:null,recoverLockedThroughStart:null,extraAttachGrantedToken:null,lastTouchedOwnerStart:s.turnStarts,status:{protected:0,sealNamed:0}};",
    "const m={type,cards:[...cards],chain:0,createdTurn:state.turnNo,createdToken:state.turnToken,lastAttachToken:null,extraAttachGrantedToken:null,lastTouchedOwnerStart:s.turnStarts,status:blankMeldStatus()};",
    'new meld status',
)

rep(
    "if(s.status.vulnerable>0){raw=Math.round(raw*1.25);log(`${switchName(w)} 취약 · 다음 DETONATE +25%.`,'hit');s.status.vulnerable=0}",
    "if(officialStatusValue('player',s,'vulnerable')>0){raw=Math.round(raw*1.25);log(`${switchName(w)} 취약 · 다음 DETONATE +25%.`,'hit');clearOfficialStatus('player',s,'vulnerable')}",
    'vulnerable consume',
)
rep(
    "function applyStatus(w,key,n){const s=sideObj(w);if(!(key in s.status))s.status[key]=0;s.status[key]+=n;const label={vulnerable:'취약',seal:'봉인',regen:'재생'}[key]||key;log(`${w==='player'?'YOU':'CPU'} ${label} +${n}`,'important');fxNode(`${label} +${n}`,'status',w,40)}",
    "function applyStatus(w,key,n){return applyOfficialStatus('player',sideObj(w),key,n,{actor:w})}",
    'player apply wrapper',
)

rep(
    "if(lastCards.some(c=>c.tag==='rummyHeal4')){heal(w,Math.ceil(15/RECOVERY_UNIT));applyStatus(w,'regen',1);if(state.switchPower>=60)addShield(w,4)}",
    "if(lastCards.some(c=>c.tag==='rummyHeal4')){heal(w,Math.ceil(15/RECOVERY_UNIT));runEffectAction('applyStatus',{actor:w},{scope:'player',target:s,key:'regen',amount:1});if(state.switchPower>=60)addShield(w,4)}",
    'regen action',
)
rep(
    "if(s.status.regen>0){const r=s.status.regen;heal(w,r);s.status.regen=Math.max(0,r-1)}",
    "if(officialStatusValue('player',s,'regen')>0){const r=officialStatusValue('player',s,'regen');heal(w,r);consumeOfficialStatus('player',s,'regen')}",
    'regen lifecycle',
)

rep(
    "function turnEnd(w){const s=sideObj(w);s.creditDebt=false;",
    "function turnEnd(w){const s=sideObj(w);s.creditDebt=false;expireOwnerFixedStatuses(w);",
    'fixed expiry at owner turn end',
)

rep(
    "if(s.recoveredThisTurn&&!free)return false;if(m.recoverLockedOwner===w&&s.turnStarts<=m.recoverLockedThroughStart)return false;const remain=",
    "if(s.recoveredThisTurn&&!free)return false;if(meldFixedActive(m)||cardFixedActive(c))return false;const remain=",
    'basic recovery fixed',
)

rep(
    "const ms=m.status||{};const mst=(ms.protected?` · 보호 ${ms.protected}`:'')+(ms.sealNamed?` · 효과봉인 ${ms.sealNamed}`:'');",
    "const mst=meldStatusText(m);",
    'meld status ui',
)
rep(
    "function statusHTML(w){const s=sideObj(w),a=[];if(s.shield)a.push(`<span class=\"statChip shieldChip\">🛡 <b>${s.shield}</b></span>`);if(s.graceArmed)a.push('<span class=\"statChip fuseChip\">유예 준비</span>');for(const [k,n]of Object.entries(s.status))if(n){const nm={vulnerable:'취약',seal:'봉인',regen:'재생'}[k]||k;a.push(`<span class=\"statChip statusChip\">${nm} ${n}</span>`)}return a.join('')||'<span class=\"statChip\">상태 없음</span>'}",
    "function statusHTML(w){const s=sideObj(w),a=[];if(s.shield)a.push(`<span class=\"statChip shieldChip\">🛡 <b>${s.shield}</b></span>`);if(s.graceArmed)a.push('<span class=\"statChip fuseChip\">유예 준비</span>');for(const k of['vulnerable','seal','regen']){const n=officialStatusValue('player',s,k);if(n)a.push(`<span class=\"statChip statusChip\">${OFFICIAL_STATUS[k].label} ${n}</span>`)}return a.join('')||'<span class=\"statChip\">상태 없음</span>'}",
    'status ui',
)

rep(
    '<div class="ruleBlock"><h3>보호막 · 상태</h3><p>보호막은 현재 CORE 앞에서 피해를 먼저 막는 별도 수치이며 최대 40입니다. 기본적으로 자기 턴 시작 시 남은 보호막이 사라집니다.</p><div class="statusLegend"><span>취약 · 다음 DETONATE +25%</span><span>봉인 · 다음 네임드 효과 1회 무효</span><span>고정 · 카드/조합 회수·이동 불가</span><span>보호 · 다음 조합 간섭 1회 무효</span><span>재생 X · 현재 CORE 회복</span></div></div>',
    '<div class="ruleBlock"><h3>보호막 · 공식 상태</h3><p>보호막은 현재 CORE 앞에서 피해를 먼저 막는 <b>별도 수치</b>이며 기본 하드캡이 없습니다. 남은 보호막은 자기 턴 시작 시 사라집니다. 공식 상태는 아래 5종만 공용 규칙으로 사용하며 카드 고유 표식은 별도입니다.</p><div class="statusLegend"><span>취약 · 플레이어 · 다음 DETONATE +25% 후 해제</span><span>봉인 · 플레이어/조합/카드 · 다음 네임드 효과 1회 무효</span><span>고정 · 조합/카드 · 다음 소유자 턴 종료까지 회수·강탈·절단 등 이동 불가</span><span>보호 · 조합/카드 · 다음 적대적 간섭 1회 무효</span><span>재생 X · 플레이어 · 자기 턴 시작에 현재 CORE 회복 후 1 감소</span></div></div>',
    'rules status block',
)

p.write_text(s)

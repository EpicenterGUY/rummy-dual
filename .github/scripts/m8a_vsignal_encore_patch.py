from pathlib import Path

index=Path('index.html')
s=index.read_text(encoding='utf-8')

def rep(old,new,label,count=1):
    global s
    found=s.count(old)
    if found<count:
        raise SystemExit(f'missing {label}: {found}/{count}')
    s=s.replace(old,new,count)

# 1) First live V-SIGNAL card as an alternate H5 named variant.
rep("'H5':{n:'온기',t:'runHeal2',d:'RUN에 들어갈 때 그 RUN에 ♥가 3장 이상이면 같은 RUN의 내 카드 1장을 무료 회수할 수 있다.'},",
    "'H5':{n:'온기',t:'runHeal2',d:'RUN에 들어갈 때 그 RUN에 ♥가 3장 이상이면 같은 RUN의 내 카드 1장을 무료 회수할 수 있다.'},\n'VSH5':{slot:'H5',themeId:'v-signal',n:'앙코르',t:'vEncore',d:'이 카드를 회수한 턴에도 한 번, 회수한 조합과 다른 합법적인 공개 조합의 버스트/체인 반환 재료로 다시 사용할 수 있다.'},",
    'V-SIGNAL Encore definition')

# 2) Make it a live alternate at the same unlock timing as the base H5.
rep("items:['S8','H5','D9','C8','D10','C3']",
    "items:['S8','H5','VSH5','D9','C8','D10','C3']",
    'Encore unlock group')

# 3) Tendency metadata.
rep("rebelJoker:['trick','interact','pressure']",
    "rebelJoker:['trick','interact','pressure'],vEncore:['cycle','combo']",
    'Encore tendency')

# 4) Explicit per-card once-per-turn bookkeeping.
rep("recoveredToken:null,recoverReturnOverrideToken:null,fuseArmed:false",
    "recoveredToken:null,recoverReturnOverrideToken:null,encoreGrantToken:null,encoreReturnUsedToken:null,fuseArmed:false",
    'Encore card state')

# 5) Theme event handler. It only grants a destination-bound override to Encore itself.
anchor="function emitRecoveryEvent(actor,card,meld,targetSide=null,opts={}){return emitEffectEvent('onRecover',{actor,card,meld,targetSide:targetSide||meldOwnerSide(meld),free:!!opts.free,automatic:!!opts.automatic,reason:opts.reason||'recover'})}\n"
insert=anchor+"function handleVSignalThemeEvent(packet){if(packet?.event!=='onRecover')return false;const c=packet.card;if(c?.themeId!=='v-signal'||c.tag!=='vEncore'||c.encoreGrantToken===packet.turnToken)return false;if(typeof grantRecoveryReturnOverride!=='function')return false;const count=grantRecoveryReturnOverride(packet.actor,c,packet.meld,{});if(!count)return false;c.encoreGrantToken=packet.turnToken;if(typeof log==='function')log(`${c.name}: 회수한 이번 턴 한 번, 다른 합법적인 조합의 버스트/체인 반환 재료로 다시 사용할 수 있습니다.`,'good');return true}\nsubscribeEffectEvent(handleVSignalThemeEvent);\n"
rep(anchor,insert,'V-SIGNAL event handler')

# 6) Consume only Encore's special return permission when it is actually used for a returning attach.
anchor2="function recoveredCardsCanReturn(cards,turnToken,targetMeld=null){return cards.every(c=>recoveredCardCanReturn(c,turnToken,targetMeld))}\n"
insert2=anchor2+"function consumeEncoreReturnPermission(cards,turnToken,targetMeld=null){let used=0;for(const c of cards||[]){if(c?.themeId!=='v-signal'||c.tag!=='vEncore'||c.recoveredToken!==turnToken||c.recoverReturnOverrideToken!==turnToken)continue;if(Array.isArray(c.recoverReturnTargets)&&!c.recoverReturnTargets.includes(targetMeld))continue;c.recoverReturnOverrideToken=null;c.recoverReturnTargets=null;c.encoreReturnUsedToken=turnToken;used++}return used}\n"
rep(anchor2,insert2,'Encore permission consumer')

rep("m.cards.push(...cards);\n  if(type==='RUN')",
    "m.cards.push(...cards);\n  if(willBaseReturn&&typeof consumeEncoreReturnPermission==='function')consumeEncoreReturnPermission(cards,state.turnToken,m);\n  if(type==='RUN')",
    'consume Encore on returning attach')

# 7) Theme visibility in detail + codex.
old_detail="${c.named?`<div class=\"tendencyLine\">경향: ${namedTendencies(c.id).join(' · ')} <span class=\"sub\">(전용 테마 아님)</span></div>`:''}"
new_detail="${c.named?`<div class=\"tendencyLine\">경향: ${namedTendencies(c.id).join(' · ')} ${c.themeId?`<span class=\"sub\">· 테마 ${themeDef(c.themeId)?.displayName||c.themeId}</span>`:'<span class=\"sub\">(전용 테마 아님)</span>'}</div>`:''}"
rep(old_detail,new_detail,'theme label in card detail')

old_codex="${slotText} · ${isJ?'조커':'네임드'}${!isJ?` · 경향 ${namedTendencies(id).join(' / ')}`:''}"
new_codex="${slotText} · ${isJ?'조커':'네임드'}${n.themeId?` · 테마 ${themeDef(n.themeId)?.displayName||n.themeId}`:''}${!isJ?` · 경향 ${namedTendencies(id).join(' / ')}`:''}"
rep(old_codex,new_codex,'theme label in codex')

index.write_text(s,encoding='utf-8')

road=Path('ROADMAP.md')
r=road.read_text(encoding='utf-8')
r=r.replace("- [ ] `앙코르` 등 회수 후 동일 턴 반환 예외를 카드 단위로 안전하게 구현",
            "- [x] `앙코르` 등 회수 후 동일 턴 반환 예외를 카드 단위로 안전하게 구현",1)
anchor_r="- [x] V-SIGNAL foundation: `themeId`/표시명 메타데이터 + 구독형 공용 이벤트 버스 + 정리 직전 `onRunFinish`/`onRetire` 훅 추가\n"
if anchor_r not in r:
    raise SystemExit('missing ROADMAP V-SIGNAL foundation anchor')
if '5♥ `앙코르` 라이브 구현' not in r:
    r=r.replace(anchor_r,anchor_r+"- [x] 5♥ `앙코르` 라이브 구현 — H5 대체 네임드 변형, 자기 회수 시 다른 합법 조합으로의 반환 재사용을 카드 단위·턴당 1회·목적지 제한으로 허용\n",1)
road.write_text(r,encoding='utf-8')

doc=Path('docs/THEME_GROUPS.md')
d=doc.read_text(encoding='utf-8')
d=d.replace("- 5♥ `앙코르` — 회수한 턴에도 한 번 버스트/체인 반환 재료 재사용을 허용하는 규칙 예외.",
            "- 5♥ `앙코르` — 이 카드를 회수한 턴에도 한 번, 회수한 조합과 다른 합법적인 공개 조합의 버스트/체인 반환 재료로 다시 사용할 수 있다.",1)
d=d.replace("- [ ] 회수 후 동일 턴 반환 예외를 카드 단위로 안전하게 허용",
            "- [x] 회수 후 동일 턴 반환 예외를 카드 단위로 안전하게 허용",1)
anchor_d="- [x] 공용 훅 이름 잠금: `onMeldCreate` / `onAttach` / `onRecover` / `onRummy` / `onRunFinish`; 모든 조합 정리 직전에는 `onRetire`도 발생\n"
if anchor_d not in d:
    raise SystemExit('missing theme doc event anchor')
if '앙코르 구현 잠금' not in d:
    d=d.replace(anchor_d,anchor_d+"- [x] 앙코르 구현 잠금: `onRecover`로 자기 자신에게만 목적지 제한 반환 허가를 부여하고, 실제 반환 재료로 쓰는 순간 허가를 소비하며 같은 턴 재회수로 재충전하지 않음\n",1)
doc.write_text(d,encoding='utf-8')

from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

def rep(old,new,label,count=1):
    global s
    if s.count(old)<count:
        raise SystemExit(f'missing {label}: {s.count(old)}/{count}')
    s=s.replace(old,new,count)

# Card-level hand preparation metadata. Kept separate from shared official statuses and legacy age.
old="function makeCard(suit,rank,named,owner,variantId=null){const slot=suit==='J'?'J':suit+rank,id=variantId||(suit==='J'?rank:slot),def=named?NAMED[id]:null;return{uid:uidSeq++,id,slot,suit,rank,owner,originOwner:owner,name:def?.n||'순수 카드',effect:def?.d||'효과 없음. 기본 랭크와 무늬만 사용한다.',tag:def?.t||null,themeId:def?.themeId||null,named:!!def,age:0,fromDiscard:false,smuggledActive:false,smuggledTurnToken:null,enteredMeldToken:null,suppressEffectToken:null,contractActive:false,healCharge:0,recoveredToken:null,recoverReturnOverrideToken:null,encoreGrantToken:null,encoreReturnUsedToken:null,fuseArmed:false,flexSuitOffSuit:false,officialStatus:{seal:0,fixed:0,protect:0,fixedOwner:null,fixedThroughStart:null},status:{charged:0,reserved:0,cursed:0,pledged:0,marked:0},blockedUntilTurn:null}}"
new="function makeCard(suit,rank,named,owner,variantId=null){const slot=suit==='J'?'J':suit+rank,id=variantId||(suit==='J'?rank:slot),def=named?NAMED[id]:null;return{uid:uidSeq++,id,slot,suit,rank,owner,originOwner:owner,name:def?.n||'순수 카드',effect:def?.d||'효과 없음. 기본 랭크와 무늬만 사용한다.',tag:def?.t||null,themeId:def?.themeId||null,prepRequired:Math.max(0,Number(def?.prepRequired)||0),named:!!def,age:0,handPrep:{turns:0,exitTurns:0,exitTurnToken:null,exitOwner:null},fromDiscard:false,smuggledActive:false,smuggledTurnToken:null,enteredMeldToken:null,suppressEffectToken:null,contractActive:false,healCharge:0,recoveredToken:null,recoverReturnOverrideToken:null,encoreGrantToken:null,encoreReturnUsedToken:null,fuseArmed:false,flexSuitOffSuit:false,officialStatus:{seal:0,fixed:0,protect:0,fixedOwner:null,fixedThroughStart:null},status:{charged:0,reserved:0,cursed:0,pledged:0,marked:0},blockedUntilTurn:null}}"
rep(old,new,'makeCard handPrep')

old="function sideObj(w){return w==='player'?state.player:state.enemy}function other(w){return w==='player'?'enemy':'player'}function meldsOf(w){return sideObj(w).melds}function removeFromHand(w,cards){const ids=new Set((cards||[]).map(c=>c.uid)),s=sideObj(w);s.hand=s.hand.filter(c=>!ids.has(c.uid))}function log(msg,cls=''){state.logs.unshift({msg,cls});state.logs=state.logs.slice(0,36)}"
new="function sideObj(w){return w==='player'?state.player:state.enemy}function other(w){return w==='player'?'enemy':'player'}function meldsOf(w){return sideObj(w).melds}\nfunction ensureHandPreparation(c){if(!c)return null;c.handPrep=c.handPrep||{turns:0,exitTurns:0,exitTurnToken:null,exitOwner:null};return c.handPrep}\nfunction resetHandPreparation(c){const m=ensureHandPreparation(c);if(!m)return null;m.turns=0;m.exitTurns=0;m.exitTurnToken=null;m.exitOwner=null;return m}\nfunction enterHand(w,c){if(!c)return null;resetHandPreparation(c);sideObj(w).hand.push(c);return c}\nfunction leaveHandPreparation(w,c){const m=ensureHandPreparation(c);if(!m)return 0;m.exitTurns=Math.max(0,m.turns||0);m.exitTurnToken=state.turnToken;m.exitOwner=w;m.turns=0;return m.exitTurns}\nfunction preparedTurnsAtUse(c,w=state.turn){const m=ensureHandPreparation(c);if(!m)return 0;if(m.exitTurnToken===state.turnToken&&m.exitOwner===w)return Math.max(0,m.exitTurns||0);return Math.max(0,m.turns||0)}\nfunction handPreparationReady(c,required=c?.prepRequired||0,w=state.turn){const need=Math.max(0,Number(required)||0);return need>0&&preparedTurnsAtUse(c,w)>=need}\nfunction advanceHandPreparation(w){let advanced=0;for(const c of sideObj(w).hand){const m=ensureHandPreparation(c);m.turns=Math.min(99,Math.max(0,m.turns||0)+1);m.exitTurns=0;m.exitTurnToken=null;m.exitOwner=null;advanced++}return advanced}\nfunction removeFromHand(w,cards){const list=cards||[],ids=new Set(list.map(c=>c.uid)),s=sideObj(w);for(const c of list)if(s.hand.some(x=>x.uid===c.uid))leaveHandPreparation(w,c);s.hand=s.hand.filter(c=>!ids.has(c.uid))}function log(msg,cls=''){state.logs.unshift({msg,cls});state.logs=state.logs.slice(0,36)}"
rep(old,new,'hand preparation helpers')

# Every fresh hand entry resets preparation. Effects may inspect the same-action exit snapshot after removeFromHand.
rep("c.fromDiscard=true;c.age=0;s.hand.push(c);return c}","c.fromDiscard=true;c.age=0;enterHand(w,c);return c}",'discard acquisition hand entry')
rep("c.age=0;s.hand.push(c);if(!s.deck.length)recycleIfNeeded(w);return c}","c.age=0;enterHand(w,c);if(!s.deck.length)recycleIfNeeded(w);return c}",'deck draw hand entry')
rep("sideObj(w).hand.push(c);if(c.tag==='smuggledSuit')c.smuggledActive=false;", "enterHand(w,c);if(c.tag==='smuggledSuit')c.smuggledActive=false;", 'free recovery hand entry')
rep("sideObj(c.owner).hand.push(c);c.suppressEffectToken=state.turnToken;", "enterHand(c.owner,c);c.suppressEffectToken=state.turnToken;", 'gap recovery hand entry')
rep("sideObj(c.owner).hand.push(c);c.suppressEffectToken=state.turnToken;", "enterHand(c.owner,c);c.suppressEffectToken=state.turnToken;", 'middle manager hand entry')
rep("sideObj(j.owner).hand.push(j);j.suppressEffectToken=state.turnToken;", "enterHand(j.owner,j);j.suppressEffectToken=state.turnToken;", 'joker replacement hand entry')
rep("sideObj(home).hand.push(c);log(`${opts.preserveLabel||'보존'}:", "enterHand(home,c);log(`${opts.preserveLabel||'보존'}:", 'retire preserve hand entry')
rep("sideObj(home).hand.push(c);c.flexSuitOffSuit=false;", "enterHand(home,c);c.flexSuitOffSuit=false;", 'understudy hand entry')
rep("const free=!!recoveryFreeReason(w,targetSide,m,c);", "const free=!!recoveryFreeReason(w,targetSide,m,c);", 'recovery anchor no-op')
rep("[c]=m.cards.splice(plan.ci,1);s.hand.push(c);if(c.tag==='smuggledSuit')", "[c]=m.cards.splice(plan.ci,1);enterHand('player',c);if(c.tag==='smuggledSuit')", 'player recovery hand entry')
rep("const [back]=state.discard.splice(ri,1);back.fromDiscard=false;s.hand.push(back);log", "const [back]=state.discard.splice(ri,1);back.fromDiscard=false;enterHand(w,back);log", 'return-if-ignored hand entry')
rep("const [ph]=s.spent.splice(pi,1);s.hand.push(ph);ph.phoenixReturned=true;", "const [ph]=s.spent.splice(pi,1);enterHand(w,ph);ph.phoenixReturned=true;", 'phoenix hand entry')
rep("[c]=m.cards.splice(plan.ci,1);s.hand.push(c);if(c.tag==='smuggledSuit')", "[c]=m.cards.splice(plan.ci,1);enterHand(w,c);if(c.tag==='smuggledSuit')", 'AI recovery hand entry')

# Full recirculation is a hard lifecycle reset.
old="c.outlawFreeRecoverAt=null;c.smuggledActive=false;c.smuggledTurnToken=null;c.age=0;if(c.flexSuitOffSuit)c.flexSuitOffSuit=false;"
new="c.outlawFreeRecoverAt=null;c.smuggledActive=false;c.smuggledTurnToken=null;c.age=0;resetHandPreparation(c);if(c.flexSuitOffSuit)c.flexSuitOffSuit=false;"
rep(old,new,'full recirculation prep reset')

# A full owner turn spent in hand advances preparation exactly once, before DETONATE settles.
old="function turnEnd(w){if(typeof recordCirculationTurn==='function')recordCirculationTurn(w);const s=sideObj(w);"
new="function turnEnd(w){if(typeof advanceHandPreparation==='function')advanceHandPreparation(w);if(typeof recordCirculationTurn==='function')recordCirculationTurn(w);const s=sideObj(w);"
rep(old,new,'turnEnd prep advance')

# Future prepared ZERO//SIGHT cards can surface the marker without adding a new resource bar.
old="b.innerHTML=`<span class=\"selectedTick\">${picked?`#${orderMap.get(c.uid)}`:'선택'}</span>${targetNext?`<span class=\"quickAttachHint\">다음 +${nextAmount}</span>`:attachN?`<span class=\"quickAttachHint\">붙임 ${attachN}</span>`:''}${cardHTML(c)}`;"
new="const prep=c.prepRequired>0?ensureHandPreparation(c):null,prepText=prep?`${Math.min(prep.turns,c.prepRequired)}/${c.prepRequired}`:'';b.innerHTML=`<span class=\"selectedTick\">${picked?`#${orderMap.get(c.uid)}`:'선택'}</span>${prep?`<span class=\"handPrepTag ${prep.turns>=c.prepRequired?'ready':''}\">준비 ${prepText}</span>`:''}${targetNext?`<span class=\"quickAttachHint\">다음 +${nextAmount}</span>`:attachN?`<span class=\"quickAttachHint\">붙임 ${attachN}</span>`:''}${cardHTML(c)}`;"
rep(old,new,'hand prep marker render')
old=".quickAttachHint{position:absolute;z-index:9;right:2px;bottom:-4px;padding:2px 4px;border:1px solid #000;background:#214c3f;color:#9ce5b2;font-size:6px;font-weight:900}.cardBtn.selected .quickAttachHint{display:none}"
new=".quickAttachHint{position:absolute;z-index:9;right:2px;bottom:-4px;padding:2px 4px;border:1px solid #000;background:#214c3f;color:#9ce5b2;font-size:6px;font-weight:900}.handPrepTag{position:absolute;z-index:9;left:2px;bottom:-4px;padding:2px 4px;border:1px solid #000;background:#243047;color:#a9c8e7;font-size:6px;font-weight:900}.handPrepTag.ready{background:#3b3420;color:#f2d78f}.cardBtn.selected .quickAttachHint{display:none}"
rep(old,new,'hand prep marker css')

p.write_text(s,encoding='utf-8')

# Canonical docs / roadmap.
road=Path('ROADMAP.md')
r=road.read_text(encoding='utf-8')
old='- [ ] 손에서 턴 경과 충전 상태를 카드 단위 마커로 구현'
new='- [x] 손에서 턴 경과 충전 상태를 카드 단위 `handPrep` 마커로 구현 — 손에 남긴 자기 턴 종료마다 +1, 손을 떠나는 행동에는 그 준비값을 현재 행동 동안만 스냅샷으로 남기고 즉시 초기화, 새로 손에 들어오면 0부터 다시 시작'
if old not in r: raise SystemExit('missing ROADMAP hand prep item')
r=r.replace(old,new,1)
road.write_text(r,encoding='utf-8')

theme=Path('docs/THEME_GROUPS.md')
t=theme.read_text(encoding='utf-8')
old='- [ ] 손에서 턴 경과 충전 상태를 카드 단위 마커로 구현'
new='- [x] 손에서 턴 경과 충전 상태를 카드 단위 `handPrep` 마커로 구현\n  - 손에 남긴 자신의 턴 종료마다 준비 +1. 상대 턴 경과만으로는 증가하지 않는다.\n  - 새로 뽑기/버림패 획득/회수/효과 반환/정리 보존으로 손에 들어오면 준비는 0부터 다시 시작한다.\n  - 조합 사용·붙이기·버리기·정비 등으로 손을 떠날 때 준비값은 즉시 초기화하되, 그 행동의 네임드 효과 해석 동안에는 `preparedTurnsAtUse()`가 직전 값을 읽을 수 있다.\n  - 준비는 공식 상태 5종이나 별도 전용 자원이 아니라 카드 단위 메타데이터이며, 손을 떠난 뒤 다음 행동까지 축적값을 보존하지 않는다.'
if old not in t: raise SystemExit('missing THEME_GROUPS hand prep item')
t=t.replace(old,new,1)
theme.write_text(t,encoding='utf-8')

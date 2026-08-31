from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
def rep(old,new,label,count=1):
    global s
    if s.count(old)<count: raise SystemExit(f'missing {label}: {s.count(old)}/{count}')
    s=s.replace(old,new,count)

# Add a light visual cue for target-marked public melds.
rep(".meldEntry{padding:5px;border:1px solid #29364d;background:#101824;margin-bottom:6px;cursor:pointer;transition:.12s}",
    ".meldEntry{padding:5px;border:1px solid #29364d;background:#101824;margin-bottom:6px;cursor:pointer;transition:.12s}.meldEntry.zeroSightTarget{border-color:#8fb7d9;box-shadow:0 0 0 2px #29475f inset}.zeroSightTag{display:inline-block;margin-left:4px;padding:1px 3px;border:1px solid #31536d;background:#13283a;color:#a8d8f6;font-size:6px;font-weight:900}",
    'ZERO//SIGHT target CSS')

# Common meld-level theme metadata, deliberately separate from official statuses.
anchor="function blankMeldStatus(){return{seal:0,fixed:0,protect:0,fixedOwner:null,fixedThroughStart:null}}\n"
insert=anchor+"function ensureMeldThemeMeta(m){if(!m)return null;m.themeMeta=m.themeMeta||{};m.themeMeta.zeroSight=m.themeMeta.zeroSight||{targetedBy:{player:false,enemy:false},targetedTurn:{player:null,enemy:null}};return m.themeMeta}\nfunction isZeroSightTarget(actor,m){return !!ensureMeldThemeMeta(m)?.zeroSight?.targetedBy?.[actor]}\nfunction zeroSightTargetMeld(actor){for(const side of['player','enemy'])for(const m of meldsOf(side))if(isZeroSightTarget(actor,m))return m;return null}\nfunction clearZeroSightTarget(actor,opts={}){let cleared=0;for(const side of['player','enemy'])for(const m of meldsOf(side)){const meta=ensureMeldThemeMeta(m)?.zeroSight;if(!meta?.targetedBy?.[actor])continue;meta.targetedBy[actor]=false;meta.targetedTurn[actor]=null;cleared++}if(cleared&&!opts.silent)log(`${actor==='player'?'내':'상대'} ZERO//SIGHT 표적 해제.`,'important');return cleared}\nfunction setZeroSightTarget(actor,m,opts={}){if(!m||!['player','enemy'].includes(actor))return false;const old=zeroSightTargetMeld(actor);if(old===m)return true;clearZeroSightTarget(actor,{silent:true});const meta=ensureMeldThemeMeta(m).zeroSight;meta.targetedBy[actor]=true;meta.targetedTurn[actor]=state.turnNo??null;if(!opts.silent)log(`${actor==='player'?'내':'상대'} ZERO//SIGHT 표적 지정 · ${m.type} ${m.cards.length}장.`,'important');return true}\n"
rep(anchor,insert,'ZERO//SIGHT target metadata helpers')

# Ensure newly created public melds have theme metadata immediately.
old="const m={type,cards:[...cards],chain:0,createdTurn:state.turnNo,createdToken:state.turnToken,lastAttachToken:null,extraAttachGrantedToken:null,lastTouchedOwnerStart:s.turnStarts,status:blankMeldStatus()};meldsOf(w).push(m);"
new="const m={type,cards:[...cards],chain:0,createdTurn:state.turnNo,createdToken:state.turnToken,lastAttachToken:null,extraAttachGrantedToken:null,lastTouchedOwnerStart:s.turnStarts,status:blankMeldStatus(),themeMeta:{zeroSight:{targetedBy:{player:false,enemy:false},targetedTurn:{player:null,enemy:null}}}};meldsOf(w).push(m);"
rep(old,new,'new meld target metadata')

# Retire event sees the target metadata before removal; then the removed object is explicitly cleared.
old="if(typeof emitEffectEvent==='function')emitEffectEvent('onRetire',{owner,meld:m,cards:[...m.cards],reason,phase:'before',preserveCards:[...preserveCards]});arr.splice(index,1);for(const c of m.cards){"
new="if(typeof emitEffectEvent==='function')emitEffectEvent('onRetire',{owner,meld:m,cards:[...m.cards],reason,phase:'before',preserveCards:[...preserveCards],themeMeta:m.themeMeta||null});arr.splice(index,1);if(m.themeMeta?.zeroSight){m.themeMeta.zeroSight.targetedBy={player:false,enemy:false};m.themeMeta.zeroSight.targetedTurn={player:null,enemy:null}}for(const c of m.cards){"
rep(old,new,'retire target cleanup')

# Render target ownership without changing attach legality. A target can be used by ordinary cards.
old="const mst=meldStatusText(m),finishable=side==='player'&&canFinishRun('player',i);const attack=preview?"
new="const mst=meldStatusText(m),finishable=side==='player'&&canFinishRun('player',i),zeroP=typeof isZeroSightTarget==='function'&&isZeroSightTarget('player',m),zeroE=typeof isZeroSightTarget==='function'&&isZeroSightTarget('enemy',m),zeroTags=`${zeroP?'<span class=\"zeroSightTag\">내 표적</span>':''}${zeroE?'<span class=\"zeroSightTag\">상대 표적</span>':''}`;const attack=preview?"
rep(old,new,'render target flags')
old="return`<div class=\"meldEntry ${ok?'validAttach':''} ${targeted?'target':''} ${cls}\" data-side=\"${side}\" data-index=\"${i}\"><div class=\"meldEntryHead\"><span class=\"meldType ${m.type==='SET'?'gold':'cyan'}\">${side==='enemy'?'상대':'나'} · ${m.type==='SET'?'세트':'런'} · ${m.cards.length}장</span>"
new="return`<div class=\"meldEntry ${ok?'validAttach':''} ${targeted?'target':''} ${cls} ${zeroP||zeroE?'zeroSightTarget':''}\" data-side=\"${side}\" data-index=\"${i}\"><div class=\"meldEntryHead\"><span class=\"meldType ${m.type==='SET'?'gold':'cyan'}\">${side==='enemy'?'상대':'나'} · ${m.type==='SET'?'세트':'런'} · ${m.cards.length}장 ${zeroTags}</span>"
rep(old,new,'render target badge')

p.write_text(s,encoding='utf-8')

road=Path('ROADMAP.md'); r=road.read_text(encoding='utf-8')
r=r.replace('- [ ] 공개 조합 단위 표적 메타데이터 및 1개 제한 구현','- [x] 공개 조합 단위 표적 메타데이터 및 1개 제한 구현',1)
road.write_text(r,encoding='utf-8')

doc=Path('docs/THEME_GROUPS.md'); d=doc.read_text(encoding='utf-8')
d=d.replace('- [ ] 공개 조합 단위 `표적` 메타데이터 설계','- [x] 공개 조합 단위 `표적` 메타데이터 설계',1)
d=d.replace('- [ ] 표적 1개 제한 / 이전 / 조합 정리 시 해제 처리','- [x] 표적 1개 제한 / 이전 / 조합 정리 시 해제 처리',1)
needle='## ZERO//SIGHT 구현 체크\n\n'
if needle in d and '표적 메타데이터 구현 잠금:' not in d:
    d=d.replace(needle,needle+'- [x] 표적 메타데이터 구현 잠금: 공식 상태와 분리된 조합 메타데이터로 관리하며, 각 플레이어는 독립적으로 1개만 유지한다. 새 표적 지정 시 자신의 기존 표적만 해제하고, `onRetire`는 정리 직전 표적 정보를 관측한 뒤 실제 제거 단계에서 표적을 소거한다. 일반/타 테마 카드의 붙이기 합법성은 표적 여부로 제한하지 않는다.\n',1)
doc.write_text(d,encoding='utf-8')

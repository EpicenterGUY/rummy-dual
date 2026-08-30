from pathlib import Path


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected 1 match, got {count}")
    return text.replace(old, new, 1)

p = Path('index.html')
s = p.read_text(encoding='utf-8')

s = replace_once(
    s,
    '.runRetireBtn{width:100%;margin-top:4px;padding:5px!important;font-size:7px!important}',
    '.runFinishBtn{width:100%;margin-top:5px;padding:6px!important;font-size:8px!important;background:linear-gradient(180deg,#38596c,#203544);box-shadow:0 0 0 2px #638ca0 inset,4px 4px 0 #0006}.runFinishReady{color:#b9ebff!important;font-weight:900}',
    'run finish css'
)

old = "function hasAnyLegalAction(w){const s=sideObj(w);if(!s.newMeldUsed&&s.melds.length<2&&bestNewMeldForTurn(w))return true;return anyAttachOption(w)}"
new = "function canFinishRun(w,index){const s=sideObj(w),m=meldsOf(w)[index];if(state.gameOver||state.turn!==w||!m||m.type!=='RUN'||(m.chain||0)<4)return false;if(w==='player'&&state.phase!=='action')return false;if(meldFixedActive(m)||m.cards.some(cardFixedActive))return false;return true}\nfunction finishRun(w,index){if(!canFinishRun(w,index))return false;const s=sideObj(w),m=meldsOf(w)[index],count=m.cards.length;s.actedThisTurn=true;retireMeld(w,index,'런 완주');if(w==='player'){state.target=null;state.boardSelected.clear();state.selected.clear();state.selectionOrder=[]}combatBanner('런 완주','chain',30);log(`${switchName(w)} 런 완주 · ${count}장 조합을 정리해 공개 조합 슬롯을 비웠습니다. 누적 위력과 스위치는 변하지 않습니다.`,'good');return true}\nfunction bestFinishRunAI(w){const s=sideObj(w);if(s.newMeldUsed||s.melds.length<2||!bestNewMeldForTurn(w))return null;let best=null;for(let i=0;i<s.melds.length;i++){const m=s.melds[i];if(!canFinishRun(w,i))continue;const score=(m.cards.length*10)+(m.chain||0);if(!best||score>best.score)best={index:i,score}}return best}\nfunction hasAnyLegalAction(w){const s=sideObj(w);if(!s.newMeldUsed&&s.melds.length<2&&bestNewMeldForTurn(w))return true;if(s.melds.some((m,i)=>canFinishRun(w,i)))return true;return anyAttachOption(w)}"
s = replace_once(s, old, new, 'run finish helpers')

old = "let actions=0,rummied=false;while(actions++<4&&!state.gameOver){const ex=bestExtension('enemy'),nm=!state.enemy.newMeldUsed&&state.enemy.melds.length<2?bestNewMeldForTurn('enemy'):null,rc=bestRecoverAI('enemy');const switchUrgent=state.switchTarget==='enemy'&&state.switchPower>0,coreNeed=state.enemy.hp+state.enemy.shield,acceptThreshold=Math.max(12,Math.floor(state.enemy.hp*.35+state.enemy.shield*.5)),acceptSmall=switchUrgent&&state.switchPower<coreNeed&&state.switchPower<=acceptThreshold;if(ex&&(!acceptSmall&&(switchUrgent||!nm||ex.score>=nm.score))&&(!rc||ex.score>=rc.score)){const r=attachCards('enemy',ex.cards,ex.side,ex.index);if(r==='rummy'){rummied=true;break}continue}if(rc&&(!nm||rc.score>nm.score)){executeRecoverAI('enemy',rc);continue}if(nm&&!state.enemy.newMeldUsed&&state.enemy.melds.length<2){const r=submitNewMeld('enemy',nm.cards);if(r==='rummy'){rummied=true;break}continue}break}"
new = "let actions=0,rummied=false;while(actions++<4&&!state.gameOver){const ex=bestExtension('enemy'),nm=!state.enemy.newMeldUsed&&state.enemy.melds.length<2?bestNewMeldForTurn('enemy'):null,rc=bestRecoverAI('enemy'),fr=bestFinishRunAI('enemy');const switchUrgent=state.switchTarget==='enemy'&&state.switchPower>0,coreNeed=state.enemy.hp+state.enemy.shield,acceptThreshold=Math.max(12,Math.floor(state.enemy.hp*.35+state.enemy.shield*.5)),acceptSmall=switchUrgent&&state.switchPower<coreNeed&&state.switchPower<=acceptThreshold;if(ex&&(!acceptSmall&&(switchUrgent||!nm||ex.score>=nm.score))&&(!rc||ex.score>=rc.score)){const r=attachCards('enemy',ex.cards,ex.side,ex.index);if(r==='rummy'){rummied=true;break}continue}if(rc&&(!nm||rc.score>nm.score)){executeRecoverAI('enemy',rc);continue}if(fr){finishRun('enemy',fr.index);continue}if(nm&&!state.enemy.newMeldUsed&&state.enemy.melds.length<2){const r=submitNewMeld('enemy',nm.cards);if(r==='rummy'){rummied=true;break}continue}break}"
s = replace_once(s, old, new, 'ai run finish')

s = replace_once(
    s,
    "const mst=meldStatusText(m);const attack=preview?",
    "const mst=meldStatusText(m),finishable=side==='player'&&canFinishRun('player',i);const attack=preview?",
    'render finish state'
)

s = replace_once(
    s,
    ":m.type==='SET'?'<div class=\"attackReadout burst\">BURST READY · 4번째 카드 +24 · SWITCH 반환</div>':`<div class=\"attackReadout chain\">CHAIN ${m.chain||0} · NEXT +${chainDamage((m.chain||0)+1)} · SWITCH 반환</div>`;",
    ":m.type==='SET'?'<div class=\"attackReadout burst\">BURST READY · 4번째 카드 +24 · SWITCH 반환</div>':`<div class=\"attackReadout chain\">CHAIN ${m.chain||0} · NEXT +${chainDamage((m.chain||0)+1)} · SWITCH 반환${(m.chain||0)>=4?' · 런 완주 가능':''}</div>`;",
    'run finish readout'
)

s = replace_once(
    s,
    "</div>${ok?`<button type=\"button\" class=\"attachHereBtn\" data-attach-side=\"${side}\" data-attach-index=\"${i}\">+ 선택 ${cs.length}장 붙이기${preview?` · TOTAL +${preview.total}`:''}</button>`:''}</div>`}).join('');document.querySelectorAll(`#${id} .meldMiniCard`)",
    "</div>${finishable?`<button type=\"button\" class=\"pixelBtn runFinishBtn\" data-run-finish=\"${i}\">런 완주 · 슬롯 비우기</button>`:''}${ok?`<button type=\"button\" class=\"attachHereBtn\" data-attach-side=\"${side}\" data-attach-index=\"${i}\">+ 선택 ${cs.length}장 붙이기${preview?` · TOTAL +${preview.total}`:''}</button>`:''}</div>`}).join('');document.querySelectorAll(`#${id} .meldMiniCard`)",
    'run finish button'
)

s = replace_once(
    s,
    "document.querySelectorAll(`#${id} .attachHereBtn`).forEach(b=>{b.onclick=e=>{e.stopPropagation();playerAttachTo(b.dataset.attachSide,+b.dataset.attachIndex)}});",
    "document.querySelectorAll(`#${id} .runFinishBtn`).forEach(b=>{b.onclick=e=>{e.stopPropagation();if(finishRun('player',+b.dataset.runFinish)){render();updateButtons()}}});document.querySelectorAll(`#${id} .attachHereBtn`).forEach(b=>{b.onclick=e=>{e.stopPropagation();playerAttachTo(b.dataset.attachSide,+b.dataset.attachIndex)}});",
    'run finish handler'
)

p.write_text(s, encoding='utf-8')

p = Path('README.md')
s = p.read_text(encoding='utf-8')
s = replace_once(
    s,
    "- RUN extensions use CHAIN +10 / +15 / +20 / +25; RUNs do not have a free base retirement action.\n",
    "- RUN extensions use CHAIN +10 / +15 / +20 / +25. At CHAIN 4+, the meld controller may voluntarily **complete the RUN** on their own turn to free that public-meld slot; if kept, later extensions remain +25. Completing a RUN adds no power and does not move SWITCH.\n",
    'readme run rule'
)
p.write_text(s, encoding='utf-8')

p = Path('ROADMAP.md')
s = p.read_text(encoding='utf-8')
s = replace_once(
    s,
    "- [x] RUN CHAIN +10 / +15 / +20 / +25\n",
    "- [x] RUN CHAIN +10 / +15 / +20 / +25; CHAIN 4+ RUN may be voluntarily `런 완주`ed by its controller on their own turn to free the slot, while keeping it allows continued +25 extensions\n",
    'roadmap rule lock'
)
s = replace_once(
    s,
    "- [x] Audit remaining code-only base rules: remove the hidden shield-40 cap, obsolete retire/draw-preview routes, and superseded generic RUMMY flags; clarify Roundabout against the recovery-return guard\n",
    "- [x] Audit remaining code-only base rules: remove the hidden shield-40 cap, obsolete retire/draw-preview routes, and superseded generic RUMMY flags; clarify Roundabout against the recovery-return guard\n- [x] Add conditional RUN completion: controller-only at CHAIN 4+, no bonus power/SWITCH movement, slot opens immediately, continuation remains +25 if not completed; AI and stuck-state logic respect it\n",
    'roadmap implementation'
)
p.write_text(s, encoding='utf-8')

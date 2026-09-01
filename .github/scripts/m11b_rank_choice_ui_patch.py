from pathlib import Path

p=Path('index.html')
s=p.read_text()

css='''

/* M11B UI2 · player asymmetric-rank legality and choice preview */
.rankChoiceHint{display:inline-block;margin-left:4px;padding:2px 4px;border:1px solid #756443;border-radius:999px;background:#2b271d;color:#e4cf98;font-size:6px;font-weight:900;line-height:1.2}
.selectionStrip .rankChoiceHint{margin:0;border-color:#766641;background:#292419;color:#ead39b}
.targetHint .rankChoiceHint{margin:3px 0 0;border-color:#5f725f;background:#1c2923;color:#bde0c3;white-space:normal}
.effectChoiceBtn.rankPlanChoice{align-items:flex-start}.effectChoiceBtn.rankPlanChoice strong{color:#f0d69c}.effectChoiceBtn.rankPlanChoice small{text-align:right;line-height:1.35}
@media(max-width:390px){.rankChoiceHint{font-size:5.5px;padding:2px 3px}.effectChoiceBtn.rankPlanChoice{gap:5px}.effectChoiceBtn.rankPlanChoice small{font-size:6px}}
'''
if '/* M11B UI2 · player asymmetric-rank legality and choice preview */' not in s:
    s=s.replace('\n</style>',css+'\n</style>',1)

# Shared choice modal can identify a rank-choice request without changing existing effect choices.
old="function renderEffectChoiceModal(){const root=ensureEffectChoiceModal();if(!root)return;const q=state.pendingEffectChoice;if(!q){root.hidden=true;return}root.hidden=false;const title=root.querySelector('#effectChoiceTitle'),text=root.querySelector('#effectChoiceText'),opts=root.querySelector('#effectChoiceOptions'),skip=root.querySelector('#effectChoiceSkip');title.textContent=q.title||'효과 대상 선택';text.textContent=q.text||'적용할 대상을 고르세요.';opts.innerHTML='';for(const o of q.options||[]){const b=document.createElement('button');b.type='button';b.className='pixelBtn effectChoiceBtn';b.dataset.choiceKey=String(o.key);const strong=document.createElement('strong');strong.textContent=o.label||String(o.key);b.appendChild(strong);if(o.detail){const small=document.createElement('small');small.textContent=o.detail;b.appendChild(small)}b.onclick=()=>resolveEffectChoice(String(o.key));opts.appendChild(b)}skip.hidden=!q.allowSkip;skip.textContent=q.skipLabel||'건너뛰기';skip.onclick=()=>resolveEffectChoice('__skip__')}"
new="function renderEffectChoiceModal(){const root=ensureEffectChoiceModal();if(!root)return;const q=state.pendingEffectChoice;if(!q){root.hidden=true;return}root.hidden=false;const kicker=root.querySelector('.effectChoiceKicker'),title=root.querySelector('#effectChoiceTitle'),text=root.querySelector('#effectChoiceText'),opts=root.querySelector('#effectChoiceOptions'),skip=root.querySelector('#effectChoiceSkip');if(kicker)kicker.textContent=q.kicker||'효과 선택';title.textContent=q.title||'효과 대상 선택';text.textContent=q.text||'적용할 대상을 고르세요.';opts.innerHTML='';for(const o of q.options||[]){const b=document.createElement('button');b.type='button';b.className=`pixelBtn effectChoiceBtn${o.kind==='rankPlan'?' rankPlanChoice':''}`;b.dataset.choiceKey=String(o.key);const strong=document.createElement('strong');strong.textContent=o.label||String(o.key);b.appendChild(strong);if(o.detail){const small=document.createElement('small');small.textContent=o.detail;b.appendChild(small)}b.onclick=()=>resolveEffectChoice(String(o.key));opts.appendChild(b)}skip.hidden=!q.allowSkip;skip.textContent=q.skipLabel||'건너뛰기';skip.onclick=()=>resolveEffectChoice('__skip__')}"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('effect choice renderer anchor missing')

# Player-facing rank-plan helper layer, kept dormant for ordinary X/X cards.
anchor="function rankResolutionPriority(c,type=null){if(isJoker(c))return['joker-wild'];const out=[isAsymmetricRankCard(c)?'printed-choice':'printed-rank'];if(type==='SET'&&c?.tag==='flexRankCopy')out.push('set-rank-copy');if(type==='RUN'&&c?.tag==='counterfeiter')out.push('run-offset');return out}\n"
helpers='''function playerRankChoiceRequired(cards){return(Array.isArray(cards)?cards:[]).some(c=>isAsymmetricRankCard(c)&&!c.activeRank)}
function playerLegalRankPlans(cards,m=null){if(!Array.isArray(cards)||!cards.length)return[];return m?legalRankChoicePlansForAttach(m,cards):legalRankChoicePlansForNewMeld(cards)}
function playerRankChoiceHint(cards,m=null){if(!playerRankChoiceRequired(cards))return'';const legal=playerLegalRankPlans(cards,m);if(!legal.length)return'사용값 선택 · 합법 후보 없음';const shown=legal.slice(0,3).map(x=>`${x.label} → ${x.type==='SET'?'세트':'런'}`),rest=legal.length-shown.length;return`사용값 ${legal.length}안 · ${shown.join(' / ')}${rest>0?` / +${rest}안`:''}`}
function requestPlayerRankChoice(cards,m=null,opts={}){const list=Array.isArray(cards)?cards:[];if(!playerRankChoiceRequired(list))return false;const legal=playerLegalRankPlans(list,m);if(!legal.length)return false;if(typeof requestEffectChoice!=='function')return false;const battleId=state.battleId,turnToken=state.turnToken,uids=list.map(c=>c.uid),meldRef=m||null;return requestEffectChoice({kicker:'사용값 선택',title:opts.title||'카드 방향 선택',text:opts.text||'이 행동에 사용할 위/아래 인쇄값을 고르세요. 선택한 값은 공개 조합에 있는 동안 고정됩니다.',options:legal.map((x,i)=>({key:`rank:${i}`,kind:'rankPlan',label:x.label,detail:`${x.type==='SET'?'세트':'런'} · ${x.projected.map(cardText).join(' ')}`,rankPlan:x.plan,type:x.type})),onChoose:o=>{const live=state.battleId===battleId&&state.turnToken===turnToken&&state.turn==='player'&&state.phase==='action'&&uids.every((uid,i)=>state.player.hand.some(c=>c.uid===uid&&c===list[i]))&&(!meldRef||meldsOf('player').includes(meldRef)||meldsOf('enemy').includes(meldRef));if(!live){if(typeof log==='function')log('사용값 선택이 만료되었습니다. 현재 손패와 전장을 다시 확인하세요.','hit');return}if(o?.rankPlan&&typeof opts.onChoose==='function')opts.onChoose(o.rankPlan,o.type,o)}})}
'''
if helpers.strip() not in s:
    if anchor not in s:raise SystemExit('rank helper insertion anchor missing')
    s=s.replace(anchor,anchor+helpers,1)

# Player attach legality must inspect all rank projections, not unresolved base rank.
old="""  const combined=m.cards.concat(cards),type=meldType(combined);
  if(type!==m.type)return false;
"""
new="""  const rankPlans=typeof legalRankChoicePlansForAttach==='function'?legalRankChoicePlansForAttach(m,cards):null;
  const combined=m.cards.concat(cards),type=rankPlans?.[0]?.type||meldType(combined);
  if(rankPlans?rankPlans.length===0:type!==m.type)return false;
"""
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('canAttachTo legality anchor missing')

# Preview uses first legal projection for rank labels while power remains target/count based.
old="function attachPreview(side,index,cards=selectedCards()){const m=meldsOf(side)[index];if(!m||!cards.length||!canAttachTo(side,index,cards))return null;return buildAttachPreview(m,cards)}"
new="function attachPreview(side,index,cards=selectedCards()){const m=meldsOf(side)[index];if(!m||!cards.length||!canAttachTo(side,index,cards))return null;const plans=typeof legalRankChoicePlansForAttach==='function'?legalRankChoicePlansForAttach(m,cards):[],previewCards=plans[0]?.projected||cards,p=buildAttachPreview(m,previewCards);if(p){p.rankPlanCount=plans.length;p.requiresRankChoice=typeof playerRankChoiceRequired==='function'&&playerRankChoiceRequired(cards)}return p}"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('attachPreview anchor missing')

# Split actual player action completion so pre-action rank selection can safely resume into the existing path.
old="""function playerMeld(){if(state.turn!=='player'||state.phase!=='action')return;const cs=selectedCards(),t=meldType(cs);if(!tutorialAllows('meld',{cards:cs,type:t})){tutorialReject('meld');return}const meldAccess=typeof newMeldAccess==='function'?newMeldAccess('player',cs):{allowed:!state.player.newMeldUsed,extra:false};if(!meldAccess.allowed){log('새 조합은 한 턴에 1회만 낼 수 있습니다. 접전에서 회수한 퀵 리로드가 있다면 그 카드를 포함한 추가 새 조합만 예외입니다.','hit');return}if(cs.length!==3||!t){log('새 조합은 정확히 3장 세트/런으로 시작합니다.','hit');return}if(state.player.melds.length>=2){log('공개 조합이 2개입니다. 기존 조합에 붙이거나 회수·카드 효과로 전장을 정리해야 새 조합을 만들 수 있습니다.','hit');return}state.selected.clear();state.selectionOrder=[];state.boardSelected.clear();state.target=null;const result=submitNewMeld('player',cs);if(result&&tutorialCheckProgress('meld',{type:t,cards:cs}))return;render()}
function playerAttach(){if(state.turn!=='player'||state.phase!=='action')return;const cs=selectedCards();if(!cs.length){log('붙일 손패 카드를 선택하세요.','hit');return}let target=state.target;if(!target){const cand=attachCandidates(cs);if(cand.length===1)target={side:cand[0].side,index:cand[0].index};else{log(cand.length?'붙일 곳이 여러 곳입니다. 공개 조합 아래의 붙이기 버튼을 고르세요.':'붙일 수 있는 공개 조합이 없습니다.','hit');return}}const m=meldsOf(target.side)[target.index],type=m?.type;if(!tutorialAllows('attach',{cards:cs,targetSide:target.side,targetIndex:target.index,type})){tutorialReject('attach');return}const beforePower=state.switchPower,beforeTarget=state.switchTarget,beforeShield=state.player.shield,jokerUids=new Set(cs.filter(isJoker).map(c=>c.uid));const ok=attachCards('player',cs,target.side,target.index);if(!ok){log('붙이기 불가 · 같은 조합에 이번 턴 이미 붙였거나, 붙인 뒤 조합이 유효하지 않습니다.','hit');return}state.selected.clear();state.selectionOrder=[];state.boardSelected.clear();state.target=null;if(tutorialCheckProgress('attach',{cards:cs,targetSide:target.side,targetIndex:target.index,type,beforePower,beforeTarget,beforeShield,afterShield:state.player.shield,afterPower:state.switchPower,afterTarget:state.switchTarget,jokerReturnedToDeck:state.player.deck.some(c=>jokerUids.has(c.uid)),jokerSpent:state.player.spent.some(c=>jokerUids.has(c.uid))}))return;render()}
"""
new="""function executePlayerMeld(cs,t,rankPlan=null){if(!tutorialAllows('meld',{cards:cs,type:t})){tutorialReject('meld');return false}const meldAccess=typeof newMeldAccess==='function'?newMeldAccess('player',cs):{allowed:!state.player.newMeldUsed,extra:false};if(!meldAccess.allowed){log('새 조합은 한 턴에 1회만 낼 수 있습니다. 접전에서 회수한 퀵 리로드가 있다면 그 카드를 포함한 추가 새 조합만 예외입니다.','hit');return false}if(cs.length!==3||!t){log('새 조합은 정확히 3장 세트/런으로 시작합니다.','hit');return false}if(state.player.melds.length>=2){log('공개 조합이 2개입니다. 기존 조합에 붙이거나 회수·카드 효과로 전장을 정리해야 새 조합을 만들 수 있습니다.','hit');return false}state.selected.clear();state.selectionOrder=[];state.boardSelected.clear();state.target=null;const result=submitNewMeld('player',cs,rankPlan);if(result&&tutorialCheckProgress('meld',{type:t,cards:cs}))return result;render();return result}
function playerMeld(){if(state.turn!=='player'||state.phase!=='action')return;const cs=selectedCards(),plans=cs.length===3&&typeof legalRankChoicePlansForNewMeld==='function'?legalRankChoicePlansForNewMeld(cs):[],t=plans[0]?.type||meldType(cs);if(cs.length!==3||!t){log(playerRankChoiceRequired(cs)?'선택한 비대칭 카드의 어느 사용값으로도 정확한 3장 세트/런을 만들 수 없습니다.':'새 조합은 정확히 3장 세트/런으로 시작합니다.','hit');return}if(playerRankChoiceRequired(cs)){if(requestPlayerRankChoice(cs,null,{title:'새 조합 · 사용값 선택',onChoose:(rankPlan,type)=>executePlayerMeld(cs,type,rankPlan)}))return;log('비대칭 카드의 합법적인 사용값을 선택할 수 없습니다.','hit');return}return executePlayerMeld(cs,t,null)}
function executePlayerAttach(cs,target,rankPlan=null){const m=meldsOf(target.side)[target.index],type=m?.type;if(!m)return false;if(!tutorialAllows('attach',{cards:cs,targetSide:target.side,targetIndex:target.index,type})){tutorialReject('attach');return false}const beforePower=state.switchPower,beforeTarget=state.switchTarget,beforeShield=state.player.shield,jokerUids=new Set(cs.filter(isJoker).map(c=>c.uid));const ok=attachCards('player',cs,target.side,target.index,rankPlan);if(!ok){log('붙이기 불가 · 같은 조합에 이번 턴 이미 붙였거나, 붙인 뒤 조합이 유효하지 않습니다.','hit');return false}state.selected.clear();state.selectionOrder=[];state.boardSelected.clear();state.target=null;if(tutorialCheckProgress('attach',{cards:cs,targetSide:target.side,targetIndex:target.index,type,beforePower,beforeTarget,beforeShield,afterShield:state.player.shield,afterPower:state.switchPower,afterTarget:state.switchTarget,jokerReturnedToDeck:state.player.deck.some(c=>jokerUids.has(c.uid)),jokerSpent:state.player.spent.some(c=>jokerUids.has(c.uid))}))return ok;render();return ok}
function playerAttach(){if(state.turn!=='player'||state.phase!=='action')return;const cs=selectedCards();if(!cs.length){log('붙일 손패 카드를 선택하세요.','hit');return}let target=state.target;if(!target){const cand=attachCandidates(cs);if(cand.length===1)target={side:cand[0].side,index:cand[0].index};else{log(cand.length?'붙일 곳이 여러 곳입니다. 공개 조합 아래의 붙이기 버튼을 고르세요.':'붙일 수 있는 공개 조합이 없습니다.','hit');return}}const m=meldsOf(target.side)[target.index];if(!m||!canAttachTo(target.side,target.index,cs)){log('붙이기 불가 · 현재 선택으로 유지되는 공개 조합이 없습니다.','hit');return}if(playerRankChoiceRequired(cs)){if(requestPlayerRankChoice(cs,m,{title:`${m.type==='SET'?'세트':'런'} 붙이기 · 사용값 선택`,onChoose:rankPlan=>executePlayerAttach(cs,target,rankPlan)}))return;log('비대칭 카드의 합법적인 붙이기 사용값을 선택할 수 없습니다.','hit');return}return executePlayerAttach(cs,target,null)}
"""
if old in s:s=s.replace(old,new,1)
elif 'function executePlayerMeld(' not in s:raise SystemExit('player action anchor missing')

# Plan-aware new-meld status in target/selection preview.
old="const rp=recoverPlan(),cand=attachCandidates(cs),t=cs.length===3?meldType(cs):null,limit="
new="const rp=recoverPlan(),cand=attachCandidates(cs),newRankPlans=cs.length===3&&typeof legalRankChoicePlansForNewMeld==='function'?legalRankChoicePlansForNewMeld(cs):[],t=cs.length===3?(newRankPlans[0]?.type||meldType(cs)):null,limit="
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('renderTargetHint new meld anchor missing')

old="if(preview)bits.push(`<span class=\"ok\">${attachPreviewText(preview)}</span>`);if(rp)bits.push('<span class=\"ok\">회수 가능</span>');"
new="if(preview)bits.push(`<span class=\"ok\">${attachPreviewText(preview)}</span>`);const rankHint=typeof playerRankChoiceHint==='function'&&cs.length?playerRankChoiceHint(cs,tm||null):'';if(rankHint)bits.push(`<span class=\"rankChoiceHint\">${rankHint}</span>`);if(rp)bits.push('<span class=\"ok\">회수 가능</span>');"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('selection strip rank hint anchor missing')

# Plan-aware button enablement and label.
old="function updateButtons(){const cs=selectedCards(),t=cs.length===3?meldType(cs):null,rp=recoverPlan(),action="
new="function updateButtons(){const cs=selectedCards(),newRankPlans=cs.length===3&&typeof legalRankChoicePlansForNewMeld==='function'?legalRankChoicePlansForNewMeld(cs):[],t=cs.length===3?(newRankPlans[0]?.type||meldType(cs)):null,rp=recoverPlan(),action="
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('updateButtons rank plan anchor missing')

old="else if(t==='SET')meldText=`${newAccess.extra?'퀵 리로드 · 추가 ':''}세트 3장 구축 · 버스트 준비`;else if(t==='RUN')meldText=`${newAccess.extra?'퀵 리로드 · 추가 ':''}런 3장 구축 · 체인 0`;"
new="else if(typeof playerRankChoiceRequired==='function'&&playerRankChoiceRequired(cs)&&newRankPlans.length){const types=[...new Set(newRankPlans.map(x=>x.type))].map(x=>x==='SET'?'세트':'런').join('/');meldText=`사용값 선택 · ${newRankPlans.length}안 · ${types}`}else if(t==='SET')meldText=`${newAccess.extra?'퀵 리로드 · 추가 ':''}세트 3장 구축 · 버스트 준비`;else if(t==='RUN')meldText=`${newAccess.extra?'퀵 리로드 · 추가 ':''}런 3장 구축 · 체인 0`;"
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('meld button label anchor missing')

p.write_text(s)

road=Path('ROADMAP.md')
r=road.read_text()
old='- [ ] 손패에서 비대칭 카드 선택 시 두 사용값과 각각의 합법 세트/런 후보를 미리보기로 표시'
new='- [x] 손패에서 비대칭 카드 선택 시 두 사용값과 각각의 합법 세트/런 후보를 미리보기로 표시 — `playerRankChoiceHint()`가 현재 선택/타겟 기준 모든 합법 top/bottom plan을 세트·런과 함께 selection strip에 요약하고, `canAttachTo`·붙이기 강조·새 조합 버튼도 projection 기반 합법성을 사용. 실제 새 조합/붙이기 실행 직전에는 공용 선택 모달에서 합법 plan을 명시적으로 고르게 하며 합법 plan이 1개뿐이어도 엔진이 임의 방향을 추측하지 않음'
if old in r:r=r.replace(old,new,1)
elif new not in r:raise SystemExit('ROADMAP UI2 anchor missing')
road.write_text(r)

doc=Path('docs/ASYMMETRIC_RANK_PROTOTYPE.md')
d=doc.read_text()
section='''

## UI 프로토타입 단계 2 — 손패 합법성 미리보기와 명시 선택

- 라이브 비대칭 카드는 계속 **0장**이며, 이번 단계도 엔진/UI 준비만 활성화한다.
- 손패 선택의 새 조합/붙이기 합법성은 미확정 카드의 `baseRank` 하나로 판단하지 않는다. `legalRankChoicePlansForNewMeld()` / `legalRankChoicePlansForAttach()`의 모든 top/bottom projection 중 하나라도 합법이면 UI도 합법 행동으로 표시한다.
- selection strip은 현재 선택과 붙이기 타겟을 기준으로 `사용값 N안 · 1번 위 3 → 세트 / 1번 아래 7 → 런`처럼 **합법한 방향만** 요약한다. 여러 비대칭 카드의 경우 선택 카드 순서를 보존한 조합 plan을 최대 기존 64개 한도 안에서 표시/실행한다.
- 새 조합 또는 붙이기 실행 시 미확정 비대칭 카드가 있으면 공용 선택 모달을 행동 전에 연다. 각 버튼은 방향 라벨, 결과 세트/런, projection된 카드 숫자를 보여준다.
- 합법 plan이 1개뿐이어도 자동 선택하지 않는다. 방향은 카드의 공개 상태가 되므로 플레이어가 직접 확정한다는 기존 엔진 계약을 유지한다.
- 선택 모달이 열린 동안 실제 손패/전장은 변하지 않는다. 선택 완료 시 같은 전투/턴/손패/조합인지 다시 확인한 뒤 `submitNewMeld(..., rankPlan)` 또는 `attachCards(..., rankPlan)`에 전달한다.
- 일반 `X/X`는 `playerRankChoiceRequired()`가 false이므로 모달, 추가 마커, 실행 경로 변화 없이 기존 행동을 그대로 사용한다.
'''
if '## UI 프로토타입 단계 2 — 손패 합법성 미리보기와 명시 선택' not in d:d+=section
doc.write_text(d)
print('M11B player rank-choice UI installed')

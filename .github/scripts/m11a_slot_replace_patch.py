from pathlib import Path
p=Path('index.html'); s=p.read_text()
road=Path('ROADMAP.md'); r=road.read_text()
master=Path('docs/ROGUELIKE_MASTER_PLAN.md'); m=master.read_text()

def span(text,name):
    marker=f'function {name}('; start=text.find(marker)
    if start<0: raise SystemExit(f'missing {name}')
    par=0; brace=-1
    for i in range(start+len(marker)-1,len(text)):
        if text[i]=='(': par+=1
        elif text[i]==')': par-=1
        elif text[i]=='{' and par==0: brace=i; break
    if brace<0: raise SystemExit(f'missing body {name}')
    d=0
    for i in range(brace,len(text)):
        if text[i]=='{': d+=1
        elif text[i]=='}':
            d-=1
            if d==0:return start,i+1
    raise SystemExit(f'unterminated {name}')

def replace_fn(text,name,new):
    a,b=span(text,name); return text[:a]+new+text[b:]

ui_anchor='<div class="themePickerNote">개발 단계 미리보기는 현재 29슬롯 덱빌더를 구조 대역으로 사용합니다. 실제 로그라이크 덱/보상 확률/희귀도와는 아직 연결되지 않습니다.</div></div><div class="unlockGroup deckBuilderGroup">'
ui_new='<div class="themePickerNote">개발 단계 미리보기는 현재 29슬롯 덱빌더를 구조 대역으로 사용합니다. 실제 로그라이크 덱/보상 확률/희귀도와는 아직 연결되지 않습니다.</div><div class="pickerLabel">동일 슬롯 교체 확인 · 공용 UI 계약</div><div id="roguelikeReplacementPreview" class="deckWarn">보상 후보를 누르면 원본 슬롯을 유지한 교체 계획을 표시합니다.</div><div class="deckBuilderHead"><button id="roguelikeReplacementApplyBtn" class="pixelBtn primary" type="button" disabled>적용 · 실제 런 덱 확정 후</button><button id="roguelikeReplacementCancelBtn" class="pixelBtn" type="button">교체 선택 취소</button></div><div class="themePickerNote">보상/상점/이벤트 모두 같은 `슬롯 → 변형` 교체 계획을 사용합니다. 이 프로토타입은 확인·취소 흐름만 검증하며 실제 덱은 변경하지 않습니다.</div></div><div class="unlockGroup deckBuilderGroup">'
if ui_new not in s:
    if ui_anchor not in s: raise SystemExit('slot replace UI anchor missing')
    s=s.replace(ui_anchor,ui_new,1)

# Shared transaction preview: reward/shop/event all describe the same same-slot replacement.
a,b=span(s,'roguelikeRewardPreviewText')
if 'function roguelikeBuildReplacementPlan(' not in s:
    block="""
function normalizeRoguelikeReplacementSource(source){return source==='shop'||source==='event'?'shop'===source?'shop':'event':'reward'}
function roguelikeBuildReplacementPlan(input={}){const slots=[...new Set(Array.isArray(input.slots)?input.slots:[])],variants=input.variants&&typeof input.variants==='object'?input.variants:{},candidateId=input.candidateId,def=candidateId&&NAMED?.[candidateId];if(!def||String(candidateId).startsWith('J'))return null;const slot=namedSlot(candidateId);if(!slots.includes(slot))return null;const fromVariant=variants[slot]||null;if(fromVariant===candidateId)return null;return{version:1,status:'preview',operation:'replace-slot-variant',source:normalizeRoguelikeReplacementSource(input.source),role:input.role||null,slot,suit:slot[0],baseRank:slot.slice(1),fromVariant,toVariant:candidateId,fromKind:fromVariant?'named':'pure',toKind:'named',preservesSlot:true,changesDeckSize:false,cancelAllowed:true,applyEnabled:false,blockedReason:'run-deck-unresolved'}}
function roguelikeReplacementPlanText(plan){if(!plan)return'보상 후보를 누르면 원본 슬롯을 유지한 교체 계획을 표시합니다.';const from=plan.fromVariant?(NAMED?.[plan.fromVariant]?.n||plan.fromVariant):'순수 카드',to=NAMED?.[plan.toVariant]?.n||plan.toVariant,src=plan.source==='shop'?'상점':plan.source==='event'?'이벤트':'카드 보상';return`<b>${src} · ${plan.baseRank}${SUIT_SYMBOL[plan.suit]} 슬롯</b><br>${from} → ${to}<br>원본 랭크+무늬 유지 · 덱 장수 변화 없음 · 취소 가능 · 실제 적용은 런 덱 확정 후`}
function roguelikeCurrentReplacementPlan(candidateId,role=null,source='reward'){const build=normalizeDeckBuild(progress.deckBuild),variants={};for(const slot of build.slots){const id=effectiveDeckVariant(slot);if(id)variants[slot]=id}return roguelikeBuildReplacementPlan({slots:build.slots,variants,candidateId,role,source})}
function renderRoguelikeReplacementPreview(plan=null){const box=document.getElementById('roguelikeReplacementPreview'),apply=document.getElementById('roguelikeReplacementApplyBtn'),cancel=document.getElementById('roguelikeReplacementCancelBtn');if(box)box.innerHTML=roguelikeReplacementPlanText(plan);if(apply){apply.disabled=true;apply.textContent=plan?'적용 · 실제 런 덱 확정 후':'적용 · 후보 선택 필요'}if(cancel)cancel.onclick=()=>renderRoguelikeReplacementPreview(null);return plan}
function bindRoguelikeRewardPreviewActions(container){if(!container)return 0;const buttons=[...container.querySelectorAll('[data-roguelike-reward-pick]')];for(const b of buttons)b.onclick=()=>renderRoguelikeReplacementPreview(roguelikeCurrentReplacementPlan(b.dataset.roguelikeRewardPick,b.dataset.rewardRole||null,'reward'));return buttons.length}
"""
    s=s[:b]+block+s[b:]

preview_new="""function roguelikeRewardPreviewText(){const draft=loadRoguelikeRunDraft();if(!draft)return'<span class=\"unlockChip\">런 구조 초안을 먼저 만드세요.</span>';const build=normalizeDeckBuild(progress.deckBuild),variants={};for(const slot of build.slots){const id=effectiveDeckVariant(slot);if(id)variants[slot]=id}const pool=[...unlockedNamed()].filter(id=>!String(id).startsWith('J')),result=roguelikeRewardCandidates({slots:build.slots,variants,starterId:draft.starterId,poolIds:pool,seed:draft.runId});if(!result.picks.length)return'<span class=\"unlockChip\">현재 해금 풀에서 같은 슬롯 교체 후보를 만들 수 없습니다.</span>';return result.picks.map(x=>`<button class=\"pixelBtn\" type=\"button\" data-roguelike-reward-pick=\"${x.id}\" data-reward-role=\"${x.role}\" title=\"점수 ${x.score} · ${x.tags.join(' / ')||'행동 태그 없음'}\"><b>${x.roleLabel}</b> · ${x.name} · ${x.slot.slice(1)}${SUIT_SYMBOL[x.slot[0]]}<br><small>${x.tags.join(' · ')||'기반 효과'}${x.themeId?` · ${THEME_BUILD_PROFILES[x.themeId]?.displayName||x.themeId}`:' · 범용'}</small></button>`).join('')+'<span class=\"unlockChip\">건너뛰기 가능 · 후보를 누르면 교체 확인만 표시</span>'}"""
s=replace_fn(s,'roguelikeRewardPreviewText',preview_new)

render_new="""function renderRoguelikeStarterPicker(){const grid=document.getElementById('roguelikeStarterGrid'),status=document.getElementById('roguelikeRunDraftStatus'),prepare=document.getElementById('roguelikePrepareBtn'),clear=document.getElementById('roguelikeClearDraftBtn'),reward=document.getElementById('roguelikeRewardPreview'),rewardBtn=document.getElementById('roguelikeRewardPreviewBtn');if(!grid)return;let selected=normalizeRoguelikeStarterId(progress.roguelikeStarter);if(!roguelikeStarterUnlocked(selected))selected='wanderer';progress.roguelikeStarter=selected;grid.innerHTML=ROGUELIKE_STARTER_IDS.map(id=>{const p=roguelikeStarterProfile(id),open=roguelikeStarterUnlocked(id),on=id===selected,meta=p.pure?'효과카드 0장 시작 · 이후 네임드 획득 가능':`출발 성향 · ${p.short}`;return`<div class=\"charCard ${on?'selected':''} ${open?'':'locked'}\"><div class=\"charName\">${p.name} ${open?'':'🔒'}</div><div class=\"charMeta\">${meta}${open?'':' · 현재 진행도에서 잠김'}</div><div class=\"charPassive\">${p.desc}<br><b>런 원칙:</b> 다른 카드군 획득을 막지 않음</div><button class=\"pixelBtn ${on?'primary':''}\" data-roguelike-starter=\"${id}\" ${open?'':'disabled'}>${on?'선택됨':'선택'}</button></div>`}).join('');grid.querySelectorAll('[data-roguelike-starter]').forEach(b=>b.onclick=()=>{const id=b.dataset.roguelikeStarter;if(!roguelikeStarterUnlocked(id))return;progress.roguelikeStarter=id;saveProgress();renderRoguelikeStarterPicker()});const draft=loadRoguelikeRunDraft();if(status)status.innerHTML=roguelikeRunDraftText(draft);if(prepare)prepare.onclick=()=>{prepareRoguelikeRunDraft(progress.roguelikeStarter);renderRoguelikeStarterPicker()};if(clear)clear.onclick=()=>{clearRoguelikeRunDraft();renderRoguelikeStarterPicker()};if(reward)reward.innerHTML=draft?'<span class=\"unlockChip\">초안 준비됨 · 버튼을 눌러 현재 덱 구조 대역으로 3역할 후보를 계산하세요.</span>':'<span class=\"unlockChip\">런 구조 초안을 만든 뒤 후보를 미리볼 수 있습니다.</span>';renderRoguelikeReplacementPreview(null);if(rewardBtn){rewardBtn.disabled=!draft;rewardBtn.onclick=()=>{if(reward){reward.innerHTML=roguelikeRewardPreviewText();bindRoguelikeRewardPreviewActions(reward)}renderRoguelikeReplacementPreview(null)}}}"""
s=replace_fn(s,'renderRoguelikeStarterPicker',render_new)

old='- [ ] 카드 보상/상점/이벤트에서 슬롯 교체 UI 설계'
new='- [x] 카드 보상/상점/이벤트에서 슬롯 교체 UI 설계 — 공용 `replace-slot-variant` 계획 객체가 보상/상점/이벤트 출처를 정규화하고 `현재 변형(또는 순수) → 새 네임드`, 원본 rank+suit 슬롯 보존, 덱 장수 불변, 취소 가능을 같은 계약으로 표시. 행동 태그 보상 미리보기의 후보 버튼을 이 교체 확인 UI에 연결하되 실제 로그라이크 덱 장수/경제가 미확정이므로 적용 버튼은 명시적으로 비활성화해 일반 30장 덱이나 진행도를 변경하지 않음'
if old in r:r=r.replace(old,new,1)
elif new not in r:raise SystemExit('slot replacement roadmap item missing')

append="""

## 13. 동일 슬롯 교체 UI 계약 v1

카드 보상, 상점, 이벤트에서 네임드를 얻는 기본 성장 행동은 서로 다른 덱 수정 코드를 만들지 않고 `replace-slot-variant` 공용 계획을 사용한다.

계획이 반드시 보여 주는 정보:

- 출처: `reward / shop / event`
- 원본 `rank+suit` 슬롯
- 현재 상태: 순수 카드 또는 현재 네임드 변형
- 교체 후 네임드 변형
- `preservesSlot: true`
- `changesDeckSize: false`
- 취소 가능

잘못된 후보는 계획 자체를 만들지 않는다. 조커, 현재 덱에 없는 슬롯, 이미 장착한 동일 변형은 동일 슬롯 교체 대상이 아니다.

현재 UI 프로토타입에서는 행동 태그 보상 후보를 누르면 `현재 → 교체 후` 확인 패널이 열리며 취소할 수 있다. 실제 적용 버튼은 비활성 상태다. 이유는 로그라이크 시작 덱 장수와 추가/제거 경제가 아직 확정되지 않았기 때문이다. 따라서 이 단계는 **교체 의미와 사용자 확인 흐름만 잠그며 일반 1대1 덱빌더나 진행도 데이터를 수정하지 않는다.**

향후 실제 런 덱이 생기면 같은 계획 객체의 검증 결과를 보상/상점/이벤트 공통 commit 함수가 소비하도록 확장한다.
"""
if '## 13. 동일 슬롯 교체 UI 계약 v1' not in m:m=m.rstrip()+append+'\n'

p.write_text(s); road.write_text(r); master.write_text(m)
print('patched M11A same-slot replacement UI contract')

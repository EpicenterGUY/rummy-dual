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
        elif text[i]=='{' and par==0:
            brace=i; break
    if brace<0: raise SystemExit(f'missing body {name}')
    depth=0
    for i in range(brace,len(text)):
        if text[i]=='{': depth+=1
        elif text[i]=='}':
            depth-=1
            if depth==0:return start,i+1
    raise SystemExit(f'unterminated {name}')

def replace_fn(text,name,new):
    a,b=span(text,name); return text[:a]+new+text[b:]

# Reward preview UI inside the already-separated roguelike starter prototype.
status_anchor='<div id="roguelikeRunDraftStatus" class="deckWarn">런 초안 없음 · 스타터를 고른 뒤 구조 초안을 만들 수 있습니다.</div><div class="deckBuilderHead"><button id="roguelikePrepareBtn" class="pixelBtn primary" type="button">런 구조 초안 만들기</button><button id="roguelikeClearDraftBtn" class="pixelBtn" type="button">초안 지우기</button></div>'
status_new='<div id="roguelikeRunDraftStatus" class="deckWarn">런 초안 없음 · 스타터를 고른 뒤 구조 초안을 만들 수 있습니다.</div><div class="deckBuilderHead"><button id="roguelikePrepareBtn" class="pixelBtn primary" type="button">런 구조 초안 만들기</button><button id="roguelikeClearDraftBtn" class="pixelBtn" type="button">초안 지우기</button></div><div class="pickerLabel">행동 태그 보상 후보 · v1</div><div id="roguelikeRewardPreview" class="unlockList"><span class="unlockChip">런 구조 초안을 만든 뒤 후보를 미리볼 수 있습니다.</span></div><button id="roguelikeRewardPreviewBtn" class="pixelBtn" type="button" disabled>3역할 보상 후보 미리보기</button><div class="themePickerNote">개발 단계 미리보기는 현재 29슬롯 덱빌더를 구조 대역으로 사용합니다. 실제 로그라이크 덱/보상 확률/희귀도와는 아직 연결되지 않습니다.</div>'
if status_new not in s:
    if status_anchor not in s: raise SystemExit('reward preview html anchor missing')
    s=s.replace(status_anchor,status_new,1)

# Pure ranking layer. It reads named effect tendencies as normalized player-facing action tags,
# but does not turn the old battle weights into reward probabilities.
anchor_name='roguelikeRunDraftText'
a,b=span(s,anchor_name)
if 'const ROGUELIKE_REWARD_ROLES=' not in s:
    block="""
const ROGUELIKE_REWARD_ROLES=Object.freeze([{id:'reinforce',label:'현재 강화'},{id:'branch',label:'새 방향'},{id:'foundation',label:'기반 보강'}]);
const ROGUELIKE_REWARD_ALGORITHM='action-tags-v1';
const ROGUELIKE_THEME_ENTRY_TAGS=Object.freeze({'v-signal':Object.freeze(['vEncore']),'zero-sight':Object.freeze(['zsObserver','zsScopeAdjust'])});
function roguelikeEffectActionTags(tag){const key=String(tag||''),low=key.toLowerCase(),out=new Set(),tendencies=typeof TENDENCY_BY_TAG==='object'&&TENDENCY_BY_TAG?(TENDENCY_BY_TAG[key]||[]):[];for(const t of tendencies){if(t==='combo'){out.add('set');out.add('run')}else if(t==='cycle'){out.add('maintenance');out.add('rummy')}else if(t==='extend'){out.add('run');out.add('attach')}else if(t==='pressure')out.add('switch');else if(t==='hold')out.add('hold');else if(t==='sustain')out.add('recover');else if(t==='status')out.add('status');else if(t==='discard'){out.add('discard');out.add('maintenance')}else if(t==='interact'){out.add('attach');out.add('opponent')}else if(t==='control'){out.add('status');out.add('opponent')}else if(t==='trick')out.add('rule');else if(t==='tempo')out.add('maintenance')}if(low.includes('rummy'))out.add('rummy');if(low.includes('recover')||low.includes('encore')||low.includes('recycler')||low.includes('ambulance'))out.add('recover');if(low.includes('discard')||low.includes('smuggl')||low.includes('market')||low.includes('appraiser')||low.includes('fence'))out.add('discard');if(low.includes('run')||low.includes('gap')||low.includes('connection')||low.includes('branch')||low.includes('middle'))out.add('run');if(low.includes('set'))out.add('set');if(low.includes('attach')||low.includes('parasite')||low.includes('extortion')||low.includes('cutline')||low.includes('connection')||low.includes('branch'))out.add('attach');return[...out].sort()}
function roguelikeNamedActionTags(id){const def=typeof NAMED==='object'&&NAMED?NAMED[id]:null;return def?roguelikeEffectActionTags(def.t):[]}
function roguelikeRewardDeckProfile(input={}){const slots=[...new Set(Array.isArray(input.slots)?input.slots:[])],variants=input.variants&&typeof input.variants==='object'?input.variants:{},actionCounts={},themeIds=[];for(const slot of slots){const id=variants[slot],def=id&&NAMED?.[id];if(!def)continue;for(const tag of roguelikeNamedActionTags(id))actionCounts[tag]=(actionCounts[tag]||0)+1;if(def.themeId&&!themeIds.includes(def.themeId))themeIds.push(def.themeId)}return{slots,variants:{...variants},actionCounts,themeIds,starterId:normalizeRoguelikeStarterId(input.starterId),tendencyHints:{...roguelikeStarterProfile(input.starterId).tendencyHints}}}
function roguelikeRewardStableHash(text){let h=2166136261;for(const ch of String(text)){h^=ch.charCodeAt(0);h=Math.imul(h,16777619)}return h>>>0}
function roguelikeThemeEntryStatus(id,profile){const def=NAMED?.[id];if(!def?.themeId||profile.themeIds.includes(def.themeId))return'present';const known=ROGUELIKE_THEME_ENTRY_TAGS[def.themeId];if(!known)return'unknown';return known.includes(def.t)?'entry':'payoff'}
function roguelikeRewardCandidateScore(id,profile,role){const def=NAMED?.[id];if(!def)return null;const slot=namedSlot(id),tags=roguelikeNamedActionTags(id),tendencies=TENDENCY_BY_TAG[def.t]||[],overlap=tags.reduce((n,t)=>n+Math.min(3,profile.actionCounts[t]||0),0),novelty=tags.filter(t=>!(profile.actionCounts[t]>0)).length,affinity=tendencies.reduce((n,t)=>n+(Number(profile.tendencyHints[t])||0),0),sameTheme=!!def.themeId&&profile.themeIds.includes(def.themeId),newTheme=!!def.themeId&&!sameTheme,entry=roguelikeThemeEntryStatus(id,profile),slotPure=!profile.variants[slot];let score=0;if(role==='reinforce')score=overlap*5+affinity*2+(sameTheme?2:0)+(slotPure?1:0)-novelty*.5;else if(role==='branch')score=novelty*4+overlap*.5+affinity*.5+(newTheme?3:0)+(entry==='entry'?5:entry==='payoff'?-6:0);else{const foundation=tags.filter(t=>t==='maintenance'||t==='recover'||t==='discard').length,volatile=tags.filter(t=>t==='switch'||t==='rule'||t==='status').length;score=(def.themeId?1:5)+foundation*2+(slotPure?1:0)-volatile*1.5+overlap*.25}return{id,slot,name:def.n||id,themeId:def.themeId||null,effectTag:def.t||null,tags,role,score:Math.round(score*100)/100,overlap,novelty,affinity:Math.round(affinity*100)/100,entryStatus:entry}}
function roguelikeRewardCandidates(input={}){const profile=roguelikeRewardDeckProfile(input),pool=[...new Set(Array.isArray(input.poolIds)?input.poolIds:[])].filter(id=>{const def=NAMED?.[id];if(!def||String(id).startsWith('J'))return false;const slot=namedSlot(id);return profile.slots.includes(slot)&&profile.variants[slot]!==id}),seed=String(input.seed||'reward-v1'),used=new Set(),picks=[];for(const roleDef of ROGUELIKE_REWARD_ROLES){const ranked=pool.filter(id=>!used.has(id)).map(id=>roguelikeRewardCandidateScore(id,profile,roleDef.id)).filter(Boolean).sort((a,b)=>b.score-a.score||(roguelikeRewardStableHash(`${seed}|${roleDef.id}|${a.id}`)-roguelikeRewardStableHash(`${seed}|${roleDef.id}|${b.id}`)));const pick=ranked[0];if(pick){used.add(pick.id);picks.push({...pick,roleLabel:roleDef.label})}}return{version:1,algorithm:ROGUELIKE_REWARD_ALGORITHM,mode:'same-slot-replacement',profile,picks,skipAllowed:true,poolSize:pool.length}}
function roguelikeRewardPreviewText(){const draft=loadRoguelikeRunDraft();if(!draft)return'<span class="unlockChip">런 구조 초안을 먼저 만드세요.</span>';const build=normalizeDeckBuild(progress.deckBuild),variants={};for(const slot of build.slots){const id=effectiveDeckVariant(slot);if(id)variants[slot]=id}const pool=[...unlockedNamed()].filter(id=>!String(id).startsWith('J')),result=roguelikeRewardCandidates({slots:build.slots,variants,starterId:draft.starterId,poolIds:pool,seed:draft.runId});if(!result.picks.length)return'<span class="unlockChip">현재 해금 풀에서 같은 슬롯 교체 후보를 만들 수 없습니다.</span>';return result.picks.map(x=>`<span class="unlockChip" title="점수 ${x.score} · ${x.tags.join(' / ')||'행동 태그 없음'}"><b>${x.roleLabel}</b> · ${x.name} · ${x.slot.slice(1)}${SUIT_SYMBOL[x.slot[0]]}<br>${x.tags.join(' · ')||'기반 효과'}${x.themeId?` · ${THEME_BUILD_PROFILES[x.themeId]?.displayName||x.themeId}`:' · 범용'}</span>`).join('')+'<span class="unlockChip">건너뛰기 가능 · 동일 슬롯 교체 후보 v1</span>'}
"""
    s=s[:b]+block+s[b:]

# Run draft records the candidate algorithm identity while probabilities remain unresolved.
a,b=span(s,'createRoguelikeRunDraft'); fn=s[a:b]
old="rewardPlan:{status:'unresolved',tendencyHints:{...profile.tendencyHints}}"
new="rewardPlan:{status:'unresolved',candidateAlgorithm:ROGUELIKE_REWARD_ALGORITHM,roles:ROGUELIKE_REWARD_ROLES.map(x=>x.id),tendencyHints:{...profile.tendencyHints}}"
if old in fn: fn=fn.replace(old,new,1)
elif 'candidateAlgorithm:ROGUELIKE_REWARD_ALGORITHM' not in fn: raise SystemExit('run draft rewardPlan anchor missing')
s=s[:a]+fn+s[b:]

# Keep picker independent and expose a manual prototype preview only after a draft exists.
render_new="""function renderRoguelikeStarterPicker(){const grid=document.getElementById('roguelikeStarterGrid'),status=document.getElementById('roguelikeRunDraftStatus'),prepare=document.getElementById('roguelikePrepareBtn'),clear=document.getElementById('roguelikeClearDraftBtn'),reward=document.getElementById('roguelikeRewardPreview'),rewardBtn=document.getElementById('roguelikeRewardPreviewBtn');if(!grid)return;let selected=normalizeRoguelikeStarterId(progress.roguelikeStarter);if(!roguelikeStarterUnlocked(selected))selected='wanderer';progress.roguelikeStarter=selected;grid.innerHTML=ROGUELIKE_STARTER_IDS.map(id=>{const p=roguelikeStarterProfile(id),open=roguelikeStarterUnlocked(id),on=id===selected,meta=p.pure?'효과카드 0장 시작 · 이후 네임드 획득 가능':`출발 성향 · ${p.short}`;return`<div class=\"charCard ${on?'selected':''} ${open?'':'locked'}\"><div class=\"charName\">${p.name} ${open?'':'🔒'}</div><div class=\"charMeta\">${meta}${open?'':' · 현재 진행도에서 잠김'}</div><div class=\"charPassive\">${p.desc}<br><b>런 원칙:</b> 다른 카드군 획득을 막지 않음</div><button class=\"pixelBtn ${on?'primary':''}\" data-roguelike-starter=\"${id}\" ${open?'':'disabled'}>${on?'선택됨':'선택'}</button></div>`}).join('');grid.querySelectorAll('[data-roguelike-starter]').forEach(b=>b.onclick=()=>{const id=b.dataset.roguelikeStarter;if(!roguelikeStarterUnlocked(id))return;progress.roguelikeStarter=id;saveProgress();renderRoguelikeStarterPicker()});const draft=loadRoguelikeRunDraft();if(status)status.innerHTML=roguelikeRunDraftText(draft);if(prepare)prepare.onclick=()=>{prepareRoguelikeRunDraft(progress.roguelikeStarter);renderRoguelikeStarterPicker()};if(clear)clear.onclick=()=>{clearRoguelikeRunDraft();renderRoguelikeStarterPicker()};if(reward)reward.innerHTML=draft?'<span class=\"unlockChip\">초안 준비됨 · 버튼을 눌러 현재 덱 구조 대역으로 3역할 후보를 계산하세요.</span>':'<span class=\"unlockChip\">런 구조 초안을 만든 뒤 후보를 미리볼 수 있습니다.</span>';if(rewardBtn){rewardBtn.disabled=!draft;rewardBtn.onclick=()=>{if(reward)reward.innerHTML=roguelikeRewardPreviewText()}}}"""
s=replace_fn(s,'renderRoguelikeStarterPicker',render_new)

# Roadmap: algorithm architecture can close without rarity/drop-rate balance.
old='- [ ] 행동 태그 기반 후보 생성 알고리즘 설계'
new='- [x] 행동 태그 기반 후보 생성 알고리즘 설계 — `action-tags-v1`은 네임드 효과의 기존 성향 메타를 세트/런/붙이기/회수/정비/러미/버림패/스위치/상태 등 플레이 행동 태그로 정규화하고, 현재 덱 프로필과 비교해 `현재 강화 / 새 방향 / 기반 보강` 3역할을 각각 1장씩 결정적으로 랭킹. 기본 성장축에 맞춰 현재 원본 슬롯에 존재하는 네임드 교체만 후보로 허용하고 현재 변형/조커/덱 외 슬롯은 제외. 새 테마는 알려진 초동 카드를 피니셔보다 우선하지만 하드 테마 잠금은 없으며, 정확한 드롭 확률·희귀도·일반/엘리트/보스 보상 수치는 여전히 미확정'
if old in r:r=r.replace(old,new,1)
elif new not in r:raise SystemExit('roadmap reward algorithm item missing')

append="""

## 12. 행동 태그 기반 카드 보상 후보 알고리즘 v1

`action-tags-v1`은 실제 보상 확률표가 아니라 **후보 랭킹 계층**이다. 기존 일반전 캐릭터 가중치를 그대로 드롭 확률로 재사용하지 않고, 네임드 효과 태그를 플레이어가 이해할 수 있는 행동 태그(`세트 / 런 / 붙이기 / 회수 / 정비 / 러미 / 버림패 / 스위치 / 상태 / 상대 조합 / 규칙 변형`)로 정규화한 뒤 현재 런 덱과 비교한다.

기본 3역할은 다음과 같다.

1. `현재 강화` — 현재 덱에서 이미 반복되는 행동과 겹치는 카드에 높은 점수를 준다. 스타터 성향은 작은 tie/방향 보정일 뿐 확률 잠금이 아니다.
2. `새 방향` — 현재 덱에 없는 행동과 새 테마를 우선한다. 새 테마에 이미 초동 메타가 정의되어 있으면 초동을 먼저 올리고, 초동 없이 피니셔만 제시하는 후보는 낮춘다. 현재 라이브 기준 ZERO-SIGHT는 `관측수 / 스코프 조정`이 `ONE SHOT`보다 첫 진입 우선이다.
3. `기반 보강` — 테마 의존도가 낮은 범용 카드와 정비/회수/버림패 같은 순환 기반 행동을 우선한다.

현재 v1의 후보 풀은 **덱에 이미 존재하는 원본 rank+suit 슬롯의 네임드 교체**로 제한한다. 현재 장착 중인 동일 변형, 조커, 덱에 없는 슬롯은 제외한다. 이는 `교체`를 기본 성장축으로 둔 기존 원칙을 따른 것이며 `추가 / 제거` 보상의 경제가 확정되기 전까지 서로 섞지 않기 위함이다.

세 역할은 가능한 경우 서로 다른 카드를 뽑고 `건너뛰기`는 항상 별도 선택지로 유지한다. 같은 입력과 seed에서는 결과가 결정적이라 회귀/밸런스 비교가 가능하다. 캐릭터/테마 하드 잠금은 만들지 않으므로 새 방향 역할에서 다른 테마 카드가 정상적으로 등장할 수 있다.

현재 진행도 화면의 개발 미리보기는 실제 로그라이크 덱이 아직 없기 때문에 기존 29슬롯 덱빌더를 **구조 대역**으로만 사용한다. 이 미리보기 결과는 전투, 해금, 보상 저장에 반영되지 않는다.

아직 확정하지 않는 것:

- 일반전 / 엘리트 / 보스별 희귀도와 보상 등급
- 실제 드롭 확률과 역할별 등장 확률
- 카드 추가/제거의 경제 비용
- 스타터별 정확한 보상 가중치 수치
- 지역 가중치와 타지역 출현률
"""
if '## 12. 행동 태그 기반 카드 보상 후보 알고리즘 v1' not in m:m=m.rstrip()+append+'\n'

p.write_text(s); road.write_text(r); master.write_text(m)
print('patched M11A action-tag reward algorithm')

from pathlib import Path

index=Path('index.html')
text=index.read_text(encoding='utf-8')

def replace_once(old,new,label):
    global text
    if new in text:
        return
    if old not in text:
        raise SystemExit(f'missing anchor: {label}')
    text=text.replace(old,new,1)

# 1) Battle setup UI: theme identity and meld geometry are separate axes.
old_ui='<section data-setup-step="deck" hidden><p class="menuIntro">혼합 덱으로 바로 시작하거나, 해금한 카드군을 중심으로 구성하세요.</p><div class="pickerLabel">카드군 / 테마</div><div id="themeGroupGrid" class="charGrid"></div><div class="themePickerNote">캐릭터는 행동 경향을, 카드군은 카드 출현 우선도를 정합니다. 다른 카드와도 자유롭게 섞입니다.</div>'
new_ui='<section data-setup-step="deck" hidden><p class="menuIntro">카드군과 조합 구조를 따로 고르세요. 카드군은 효과 방향을, 조합 구조는 실제 숫자·무늬 골격을 정합니다.</p><div class="pickerLabel">카드군 / 테마</div><div id="themeGroupGrid" class="charGrid"></div><div class="themePickerNote">캐릭터는 행동 경향을, 카드군은 카드 출현 우선도를 정합니다. 같은 카드군도 SET형·RUN형·혼합형으로 다르게 굴릴 수 있습니다.</div><div class="pickerLabel">조합 구조</div><div id="deckStructureGrid" class="charGrid"></div><div class="themePickerNote">SET형은 같은 숫자의 무늬 밀도를, RUN형은 같은 무늬의 연속 구간을, 혼합형은 SET/RUN 양쪽에 걸치는 교차 카드를 우선합니다.</div>'
replace_once(old_ui,new_ui,'battle setup structure picker')

# 2) Canonical structure profiles.
anchor='const effectEventSubscribers=new Set();'
profiles="""const DECK_STRUCTURE_PROFILES=Object.freeze({
 set:Object.freeze({id:'set',displayName:'SET형',short:'같은 숫자 집중',desc:'7개 중심 숫자를 여러 무늬로 겹쳐 세트 생성과 버스트 재료 순환을 우선합니다.'}),
 run:Object.freeze({id:'run',displayName:'RUN형',short:'같은 무늬 연속',desc:'두 무늬의 긴 연속 구간을 중심으로 런 생성과 체인 연장을 우선합니다.'}),
 mixed:Object.freeze({id:'mixed',displayName:'혼합형',short:'SET + RUN 교차',desc:'한 무늬의 긴 런 축과 여러 무늬의 세트 축을 겹쳐 상황에 따라 양쪽으로 전환합니다.'})
});
"""
if 'const DECK_STRUCTURE_PROFILES=' not in text:
    if anchor not in text: raise SystemExit('missing anchor: effect subscribers')
    text=text.replace(anchor,profiles+anchor,1)

# 3) Persist selected structure independently from theme.
old_default="function defaultProgress(){return{totalClears:0,selectedChar:'wanderer',selectedTheme:'mixed',roguelikeStarter:'wanderer',tutorialPromptSeen:false,tutorialCompleted:false,asymmetricRankIntroSeen:false,deckBuild:defaultDeckBuild(),chars:{wanderer:0,collector:0,salvager:0,jester:0}}}"
new_default="function defaultProgress(){return{totalClears:0,selectedChar:'wanderer',selectedTheme:'mixed',selectedStructure:'mixed',roguelikeStarter:'wanderer',tutorialPromptSeen:false,tutorialCompleted:false,asymmetricRankIntroSeen:false,deckBuild:defaultDeckBuild(),chars:{wanderer:0,collector:0,salvager:0,jester:0}}}"
replace_once(old_default,new_default,'default progress structure')
old_norm="selectedTheme:Object.prototype.hasOwnProperty.call(THEME_BUILD_PROFILES,x.selectedTheme)?x.selectedTheme:'mixed',roguelikeStarter:normalizeRoguelikeStarterId(x.roguelikeStarter)"
new_norm="selectedTheme:Object.prototype.hasOwnProperty.call(THEME_BUILD_PROFILES,x.selectedTheme)?x.selectedTheme:'mixed',selectedStructure:Object.prototype.hasOwnProperty.call(DECK_STRUCTURE_PROFILES,x.selectedStructure)?x.selectedStructure:'mixed',roguelikeStarter:normalizeRoguelikeStarterId(x.roguelikeStarter)"
replace_once(old_norm,new_norm,'normalized progress structure')

# 4) Named selection may only occupy physical slots already admitted by the geometry skeleton.
old_choose="function chooseNamedForBuild(unlocked,charId,themeId='mixed'){const preferred=themeId==='mixed'?[]:unlocked.filter(id=>NAMED[id]?.themeId===themeId),themeCap=Math.min(4,new Set(preferred.map(namedSlot)).size),themeChosen=weightedVariantSample(preferred,themeCap,id=>cardWeightForChar(id,charId,themeId)),used=new Set(themeChosen.map(namedSlot)),rest=unlocked.filter(id=>!used.has(namedSlot(id))&&(themeId==='mixed'||NAMED[id]?.themeId!==themeId)),fill=weightedVariantSample(rest,Math.max(0,9-themeChosen.length),id=>cardWeightForChar(id,charId,themeId));return themeChosen.concat(fill)}"
new_choose="function chooseNamedForBuild(unlocked,charId,themeId='mixed',allowedSlots=null){const allowed=allowedSlots?new Set(allowedSlots):null,candidates=unlocked.filter(id=>!allowed||allowed.has(namedSlot(id))),preferred=themeId==='mixed'?[]:candidates.filter(id=>NAMED[id]?.themeId===themeId),themeCap=Math.min(4,new Set(preferred.map(namedSlot)).size),themeChosen=weightedVariantSample(preferred,themeCap,id=>cardWeightForChar(id,charId,themeId)),used=new Set(themeChosen.map(namedSlot)),rest=candidates.filter(id=>!used.has(namedSlot(id))&&(themeId==='mixed'||NAMED[id]?.themeId!==themeId)),fill=weightedVariantSample(rest,Math.max(0,9-themeChosen.length),id=>cardWeightForChar(id,charId,themeId));return themeChosen.concat(fill)}"
replace_once(old_choose,new_choose,'slot-bounded named selection')

# 5) Geometry-first 29-slot skeletons. Random suit permutation and cyclic rank offset
# keep battles varied while preserving the same structural density.
old_support="function supportIds(id){const slot=namedSlot(id),{suit,rank}=parseRegularId(slot),v=RANK_VALUE[rank],out=[];for(const s of['S','H','D','C'])if(s!==suit)out.push(s+rank);for(const d of[-2,-1,1,2]){const nv=v+d;if(nv>=1&&nv<=13){const r=Object.keys(RANK_VALUE).find(k=>RANK_VALUE[k]===nv);out.push(suit+r)}}return out}"
new_support=old_support+"\n"+"""function deckStructureShuffle(values,rand=Math.random){const out=[...values];for(let i=out.length-1;i>0;i--){const raw=Number(rand()),j=Math.max(0,Math.min(i,Math.floor((Number.isFinite(raw)?raw:0)*(i+1))));[out[i],out[j]]=[out[j],out[i]]}return out}
function deckStructureSlots(structureId='mixed',rand=Math.random){const id=DECK_STRUCTURE_PROFILES[structureId]?structureId:'mixed',ranks=['A','2','3','4','5','6','7','8','9','10','J','Q','K'],suits=deckStructureShuffle(['S','H','D','C'],rand),raw=Number(rand()),offset=Math.floor(Math.max(0,Math.min(.999999,Number.isFinite(raw)?raw:0))*13),rank=i=>ranks[(offset+i+130)%13],slots=[];if(id==='set'){for(let i=0;i<7;i++){const r=rank(i*2);for(const s of suits)slots.push(s+r)}slots.push(suits[0]+rank(1))}else if(id==='run'){for(const s of suits.slice(0,2))for(const r of ranks)slots.push(s+r);for(let i=0;i<3;i++)slots.push(suits[2]+rank(i))}else{for(const r of ranks)slots.push(suits[0]+r);for(const step of[0,3,6,9])for(const s of suits.slice(1))slots.push(s+rank(step));for(const step of[1,2,4,5])slots.push(suits[1]+rank(step))}return[...new Set(slots)].slice(0,29)}
function deckStructureHandFit(slots,handSize=6,samples=512){const src=[...slots],rankIndex=Object.fromEntries(['A','2','3','4','5','6','7','8','9','10','J','Q','K'].map((r,i)=>[r,i]));let seed=0x6d2b79f5,setHands=0,runHands=0,anyHands=0;const next=()=>{seed=Math.imul(seed^seed>>>15,1|seed);seed^=seed+Math.imul(seed^seed>>>7,61|seed);return((seed^seed>>>14)>>>0)/4294967296};for(let n=0;n<samples;n++){const pool=[...src],hand=[];for(let i=0;i<Math.min(handSize,pool.length);i++){const j=i+Math.floor(next()*(pool.length-i));[pool[i],pool[j]]=[pool[j],pool[i]];hand.push(pool[i])}const counts={},bySuit={S:new Set(),H:new Set(),D:new Set(),C:new Set()};for(const slot of hand){const{suit,rank}=parseRegularId(slot);counts[rank]=(counts[rank]||0)+1;bySuit[suit]?.add(rankIndex[rank])}const hasSet=Object.values(counts).some(v=>v>=3);let hasRun=false;for(const vals of Object.values(bySuit))for(let v=0;v<13;v++)if(vals.has(v)&&vals.has((v+1)%13)&&vals.has((v+2)%13)){hasRun=true;break}if(hasSet)setHands++;if(hasRun)runHands++;if(hasSet||hasRun)anyHands++}return{samples,setRate:setHands/samples,runRate:runHands/samples,anyRate:anyHands/samples}}
"""
replace_once(old_support,new_support,'deck structure skeleton helpers')

# 6) Automatic player deck: structure first, named/theme variants second.
old_make=""" const unlocked=[...unlockedNamed()].filter(id=>id[0]!=='J'&&NAMED[id]);
 const buildTheme=themeBuildUnlocked(themeId)?themeId:'mixed';
 const namedChosen=chooseNamedForBuild(unlocked,charId,buildTheme);
 const variantBySlot=new Map(namedChosen.map(id=>[namedSlot(id),id]));
 const slots=new Set(namedChosen.map(namedSlot));
 const support=[];for(const id of namedChosen)support.push(...supportIds(id));shuffle(support);for(const id of support){if(slots.size>=22)break;slots.add(id)}
 const cores=shuffle([...CORE_IDS]);for(const id of cores){if(slots.size>=29)break;slots.add(id)}
 const rest=shuffle([...ALL_REGULAR]);for(const id of rest){if(slots.size>=29)break;slots.add(id)}
"""
new_make=""" const unlocked=[...unlockedNamed()].filter(id=>id[0]!=='J'&&NAMED[id]);
 const buildTheme=themeBuildUnlocked(themeId)?themeId:'mixed';
 const structureSlots=owner==='player'?deckStructureSlots(progress.selectedStructure||'mixed'):null;
 const namedChosen=chooseNamedForBuild(unlocked,charId,buildTheme,structureSlots);
 const variantBySlot=new Map(namedChosen.map(id=>[namedSlot(id),id]));
 const slots=structureSlots?new Set(structureSlots):new Set(namedChosen.map(namedSlot));
 if(!structureSlots){const support=[];for(const id of namedChosen)support.push(...supportIds(id));shuffle(support);for(const id of support){if(slots.size>=22)break;slots.add(id)}const cores=shuffle([...CORE_IDS]);for(const id of cores){if(slots.size>=29)break;slots.add(id)}const rest=shuffle([...ALL_REGULAR]);for(const id of rest){if(slots.size>=29)break;slots.add(id)}}
"""
replace_once(old_make,new_make,'geometry-first makeDeck')

# 7) Render structure picker, selection summary and custom reset recommendation.
old_summary="function renderProgress(){const summary=document.getElementById('setupSelectionSummary');if(summary)summary.textContent=`${CHARACTERS[progress.selectedChar]?.name||'유랑자'} · ${THEME_BUILD_PROFILES[progress.selectedTheme]?.displayName||'혼합'}${progress.deckBuild?.enabled?' · 커스텀 덱':''}`;"
new_summary="function renderProgress(){const summary=document.getElementById('setupSelectionSummary');if(summary)summary.textContent=`${CHARACTERS[progress.selectedChar]?.name||'유랑자'} · ${THEME_BUILD_PROFILES[progress.selectedTheme]?.displayName||'혼합'} · ${DECK_STRUCTURE_PROFILES[progress.selectedStructure]?.displayName||'혼합형'}${progress.deckBuild?.enabled?' · 커스텀 덱':''}`;"
replace_once(old_summary,new_summary,'setup summary structure')

old_after_theme="tg.querySelectorAll('[data-theme-build]').forEach(b=>b.onclick=()=>{if(!themeBuildUnlocked(b.dataset.themeBuild))return;progress.selectedTheme=b.dataset.themeBuild;saveProgress();renderProgress();renderStartScreen();render()})}const chips=[];"
new_after_theme="tg.querySelectorAll('[data-theme-build]').forEach(b=>b.onclick=()=>{if(!themeBuildUnlocked(b.dataset.themeBuild))return;progress.selectedTheme=b.dataset.themeBuild;saveProgress();renderProgress();renderStartScreen();render()})}const sg=document.getElementById('deckStructureGrid');if(sg){sg.innerHTML=Object.values(DECK_STRUCTURE_PROFILES).map(p=>{const selected=progress.selectedStructure===p.id;return`<div class=\"charCard ${selected?'selected':''}\" data-structure-card=\"${p.id}\"><div class=\"charName\">${p.displayName}</div><div class=\"charMeta\">조합 구조 · ${p.short}</div><div class=\"charPassive\">${p.desc}</div><button class=\"pixelBtn ${selected?'primary':''}\" data-deck-structure=\"${p.id}\" type=\"button\">${selected?'선택됨':'선택'}</button></div>`}).join('');sg.querySelectorAll('[data-deck-structure]').forEach(b=>b.onclick=()=>{progress.selectedStructure=b.dataset.deckStructure;saveProgress();renderProgress();renderStartScreen();render()})}const chips=[];"
replace_once(old_after_theme,new_after_theme,'structure picker render')

old_reset="document.getElementById('deckResetBtn').onclick=()=>{const enabled=build.enabled;progress.deckBuild={...defaultDeckBuild(),enabled};saveProgress();renderDeckBuilder();renderStartScreen()};"
new_reset="document.getElementById('deckResetBtn').onclick=()=>{const enabled=build.enabled,recommended=deckStructureSlots(progress.selectedStructure||'mixed',()=>0);progress.deckBuild={...defaultDeckBuild(),slots:recommended,enabled};saveProgress();renderDeckBuilder();renderStartScreen()};"
replace_once(old_reset,new_reset,'custom reset uses selected structure')

# 8) Show the selected structure and estimated six-card hand resilience in deck analysis.
old_analysis="const build=progress.deckBuild,selected=new Set(build.slots),analysis=deckBuildAnalysis(build.slots),flex=typeof deckBuildAsymmetricFlexAnalysis==='function'?deckBuildAsymmetricFlexAnalysis(build):{cards:0,alternateRankSlots:0},valid=build.slots.length===29"
new_analysis="const build=progress.deckBuild,selected=new Set(build.slots),analysis=deckBuildAnalysis(build.slots),fit=build.slots.length===29?deckStructureHandFit(build.slots):null,flex=typeof deckBuildAsymmetricFlexAnalysis==='function'?deckBuildAsymmetricFlexAnalysis(build):{cards:0,alternateRankSlots:0},valid=build.slots.length===29"
replace_once(old_analysis,new_analysis,'deck builder fit analysis')
old_warn="${valid?'구성 완료 · 정규 29 + 조커 1 = 30장.':'커스텀 적용 전 정규 슬롯을 정확히 29개 선택하세요.'}<br><small>숫자·무늬·세트·런은 원본 52슬롯 기준 · 비대칭 사용값은 중복 집계하지 않음.</small></div>"
new_warn="${valid?'구성 완료 · 정규 29 + 조커 1 = 30장.':'커스텀 적용 전 정규 슬롯을 정확히 29개 선택하세요.'}${fit?`<br><small>6장 표본 · SET ${(fit.setRate*100).toFixed(1)}% / RUN ${(fit.runRate*100).toFixed(1)}% / 둘 중 하나 ${(fit.anyRate*100).toFixed(1)}%</small>`:''}<br><small>숫자·무늬·세트·런은 원본 52슬롯 기준 · 비대칭 사용값은 중복 집계하지 않음.</small></div>"
replace_once(old_warn,new_warn,'deck builder hand fit output')

index.write_text(text,encoding='utf-8')

# Roadmap: make the second deck-building axis explicit and leave human balance tuning open.
road=Path('ROADMAP.md')
r=road.read_text(encoding='utf-8')
section="""
## M4B — 덱 조합 구조 축: SET / RUN / 혼합
테마 카드군은 **효과 빌드**, 조합 구조는 **숫자·무늬 골격 빌드**로 분리한다. 자동 덱은 먼저 29개 물리 슬롯의 조합 골격을 만든 뒤 그 안에 해금 네임드/테마 변형을 배치한다. 자세한 기준은 `docs/DECK_STRUCTURE_PROFILES.md`를 따른다.

- [x] 대전 준비에 `SET형 / RUN형 / 혼합형` 독립 선택 축 추가 — 카드군 선택과 별개로 저장
- [x] SET형 29슬롯 골격 — 7개 중심 랭크를 4무늬로 겹치고 1장 보조 슬롯을 더해 SET/BURST 재료 밀도 우선
- [x] RUN형 29슬롯 골격 — 2개 무늬 13연속 + 제3무늬 3연속으로 RUN/CHAIN 재료 밀도 우선
- [x] 혼합형 29슬롯 골격 — 1개 무늬 13연속 + 4개 교차 랭크의 타 무늬 + 보조 연속 구간으로 SET/RUN 전환점 확보
- [x] 골격 → 네임드/테마 변형 순서로 자동 덱 생성 변경 — 선택 테마는 최대 4장, 물리 슬롯 중복 금지 유지
- [x] 커스텀 덱 `추천 29슬롯 복원`이 현재 선택 조합 구조를 사용하도록 연결
- [x] 6장 손패 표본 기반 SET/RUN/둘 중 하나 성립률을 덱 분석에 표시
- [x] 구조별 자동 덱·테마 혼합·진행도 저장·전체 회귀 테스트 추가
- [ ] 인간 실전 및 M12 전투 기록으로 구조별 승률/러미율/저손패 정체율을 비교해 최종 골격 수치 조정

"""
if '## M4B — 덱 조합 구조 축' not in r:
    marker='## M5 — Multi-attach UX\n'
    if marker not in r: raise SystemExit('missing ROADMAP M5 anchor')
    r=r.replace(marker,section+marker,1)
road.write_text(r,encoding='utf-8')

# Canonical design note.
doc=Path('docs/DECK_STRUCTURE_PROFILES.md')
doc.write_text("""# RUMMY//DUEL — 덱 조합 구조 프로필

## 목적
카드군/테마는 효과 시너지를 고르는 축이고, 조합 구조는 실제 29개 정규 물리 슬롯의 숫자·무늬 분포를 고르는 축이다. 두 축을 분리해 카드군 효과가 맞더라도 손패가 SET/RUN 어느 쪽도 만들지 못하는 고립 분포를 줄인다.

자동 전투 덱은 항상 **조합 골격 29슬롯 → 네임드/테마 변형 배치 → 조커 1장** 순서로 만든다. 네임드 변형은 원래 물리 슬롯을 바꾸지 않는다.

## SET형
- 7개 중심 랭크를 네 무늬 모두 채워 28슬롯을 만든다.
- 인접 랭크 1장을 보조로 넣어 총 29슬롯을 맞춘다.
- 목표: 같은 숫자 3장 SET과 네 번째 무늬 BURST 재료가 덱이 줄어든 뒤에도 반복해서 남도록 한다.
- 의도적으로 RUN 창은 적게 둔다.

## RUN형
- 두 무늬를 A~K 전 구간으로 채워 26슬롯을 만든다.
- 제3무늬에 3연속 구간을 더해 총 29슬롯을 만든다.
- 목표: 긴 RUN과 반복 CHAIN 연장 재료가 덱이 줄어든 뒤에도 같은 무늬에 남도록 한다.
- 두 주력 무늬가 같은 랭크를 공유하므로 최소한의 SET 전환 가능성은 남긴다.

## 혼합형
- 한 무늬를 A~K 전 구간으로 채워 RUN 축을 만든다.
- 4개 간격 랭크를 나머지 세 무늬에도 채워 SET 축을 만든다.
- 두 번째 무늬에 4장의 보조 연속 슬롯을 더한다.
- 목표: RUN 축 위의 카드가 동시에 SET의 한 장으로도 쓰이는 `교차 카드`를 확보해 손패 상황에 따라 양쪽으로 전환한다.

## 자동 덱 규칙
1. 플레이어 자동 덱에만 선택한 조합 구조를 적용한다. CPU 자동 덱은 기존 생성 방식을 유지해 난이도 회귀를 피한다.
2. 조합 구조가 29개 물리 슬롯을 먼저 확정한다.
3. 네임드/테마 카드는 그 29슬롯 안에서만 변형으로 들어간다.
4. 한 카드군 자동 편성은 물리 슬롯 기준 최대 4장이다.
5. 나머지 네임드는 캐릭터 행동 경향으로 채우며 자동 네임드 모듈은 기존 9장 규모를 유지한다.
6. 랭크 시작점과 무늬 역할은 매 전투 회전/섞기되어 같은 구조라도 특정 숫자·무늬만 고정되지 않는다.
7. 커스텀 덱은 사용자가 직접 29슬롯을 바꿀 수 있으며, 추천 복원은 현재 선택 구조의 대표 골격을 사용한다.

## 검증 기준
- 모든 프로필은 정확히 29개의 서로 다른 정규 슬롯을 만든다.
- SET형 6장 표본의 SET 성립률은 RUN형보다 유의하게 높아야 한다.
- RUN형 6장 표본의 RUN 성립률은 SET형보다 유의하게 높아야 한다.
- 혼합형은 SET/RUN 어느 한쪽으로 과도하게 치우치지 않고, `둘 중 하나` 성립률이 두 전용 구조와 경쟁 가능한 수준이어야 한다.
- 테마를 선택해도 최대 4장 제한과 물리 슬롯 유일성은 유지한다.

최종 승률·러미율·저손패 정체율 수치는 인간 실전/M12 데이터가 쌓인 뒤 조정한다.
""",encoding='utf-8')

# Dedicated executable regression.
test=Path('tests/deck-structure-profiles.mjs')
test.write_text(r"""import fs from 'node:fs';
import vm from 'node:vm';

const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const doc=fs.readFileSync(new URL('../docs/DECK_STRUCTURE_PROFILES.md',import.meta.url),'utf8');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw Error(`missing ${name}`);let par=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')par++;else if(script[i]===')')par--;else if(script[i]==='{'&&par===0){brace=i;break}}let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw Error(`unterminated ${name}`)}
function declaration(name){const marker=`const ${name}=`,start=script.indexOf(marker);if(start<0)throw Error(`missing ${name}`);let q=null,e=false,d=0,seen=false;for(let i=start+marker.length;i<script.length;i++){const ch=script[i];if(q){if(e)e=false;else if(ch==='\\')e=true;else if(ch===q)q=null;continue}if(ch==="'"||ch==='"'||ch==='`'){q=ch;continue}if(ch==='{'||ch==='['||ch==='('){d++;seen=true}else if(ch==='}'||ch===']'||ch===')')d--;else if(ch===';'&&seen&&d===0)return script.slice(start,i+1)}throw Error(`unterminated ${name}`)}
new Function(script);
const ctx=vm.createContext({console,Math,Object,Array,Set,Map});
vm.runInContext("const RANK_VALUE={A:1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,J:11,Q:12,K:13};",ctx);
vm.runInContext(declaration('DECK_STRUCTURE_PROFILES'),ctx);
for(const n of ['parseRegularId','deckStructureShuffle','deckStructureSlots','deckStructureHandFit'])vm.runInContext(source(n),ctx);
const all=new Set(['S','H','D','C'].flatMap(s=>['A','2','3','4','5','6','7','8','9','10','J','Q','K'].map(r=>s+r)));
for(const id of ['set','run','mixed'])for(const value of [0,.17,.49,.83]){let i=0,seq=[value,.31,.67,.11,.91];const slots=ctx.deckStructureSlots(id,()=>seq[(i++)%seq.length]);ok(slots.length===29,`${id} produces exactly 29 regular slots`);ok(new Set(slots).size===29,`${id} has no duplicate physical slots`);ok(slots.every(x=>all.has(x)),`${id} uses only legal rank+suit slots`)}
const zero=()=>0,setSlots=ctx.deckStructureSlots('set',zero),runSlots=ctx.deckStructureSlots('run',zero),mixSlots=ctx.deckStructureSlots('mixed',zero),setFit=ctx.deckStructureHandFit(setSlots,6,4096),runFit=ctx.deckStructureHandFit(runSlots,6,4096),mixFit=ctx.deckStructureHandFit(mixSlots,6,4096);
ok(setFit.setRate>runFit.setRate*3,'SET profile materially favors SET-ready six-card hands');
ok(runFit.runRate>setFit.runRate*3,'RUN profile materially favors RUN-ready six-card hands');
ok(Math.abs(mixFit.setRate-mixFit.runRate)<.05,'mixed profile keeps SET/RUN six-card rates near each other');
ok(mixFit.anyRate>=Math.min(setFit.anyRate,runFit.anyRate),'mixed profile keeps competitive any-meld hand resilience');
ok(script.includes("selectedStructure:'mixed'")&&script.includes('DECK_STRUCTURE_PROFILES,x.selectedStructure'),'selected structure persists independently in progress');
ok(script.includes('id="deckStructureGrid"')&&script.includes('[data-deck-structure]'),'battle setup exposes an independent structure picker');
ok(script.includes("const structureSlots=owner==='player'?deckStructureSlots(progress.selectedStructure||'mixed'):null"),'automatic player deck fixes geometry before named variants');
ok(script.includes('chooseNamedForBuild(unlocked,charId,buildTheme,structureSlots)'),'theme/named selection is bounded by admitted structure slots');
ok(script.includes("if(!structureSlots){const support=[]"),'CPU keeps the legacy support-based deck generation path');
ok(script.includes("deckStructureSlots(progress.selectedStructure||'mixed',()=>0)"),'custom recommended reset follows the selected structure');
ok(road.includes('## M4B — 덱 조합 구조 축: SET / RUN / 혼합'),'ROADMAP contains the new deck-structure milestone');
ok(doc.includes('조합 골격 29슬롯 → 네임드/테마 변형 배치 → 조커 1장'),'canonical structure doc locks geometry-before-theme order');
console.log('Deck structure SET/RUN/mixed regression passed.',{setFit,runFit,mixFit});
""",encoding='utf-8')

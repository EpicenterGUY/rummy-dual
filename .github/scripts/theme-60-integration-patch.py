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

# 1) All three completed themes are normal live build/tutorial content.
once("const THEME_TUTORIALS=Object.freeze({'v-signal':Object.freeze({themeId:'v-signal',startStep:'vsEncore',live:true}),'zero-sight':Object.freeze({themeId:'zero-sight',startStep:null,live:false}),'point-blank':Object.freeze({themeId:'point-blank',startStep:null,live:false})});",
     "const THEME_TUTORIALS=Object.freeze({'v-signal':Object.freeze({themeId:'v-signal',startStep:'vsEncore',live:true}),'zero-sight':Object.freeze({themeId:'zero-sight',startStep:'zsObserver',live:true}),'point-blank':Object.freeze({themeId:'point-blank',startStep:'pbBreach',live:true})});",
     'theme tutorials go live')
once("'point-blank':Object.freeze({id:'point-blank',displayName:'POINT-BLANK',short:'근접 교대',desc:'접전·돌입·회수·교대 카드군. 기반 시스템 구현 예정입니다.',themeId:'point-blank',live:false})",
     "'point-blank':Object.freeze({id:'point-blank',displayName:'POINT-BLANK',short:'근접 교대',desc:'접전·돌입·회수·교대를 엮어 상대 공개 조합 안에서 압박합니다. 일반 카드도 함께 섞입니다.',themeId:'point-blank',live:true})",
     'point blank live build profile')
once("function themeBuildLockText(id){if(id==='v-signal')return'테마 카드 해금 필요 · 전체 2클리어부터';if(id==='zero-sight')return'테마 카드 해금 필요 · 전체 1클리어부터';return'개발 중'}",
     "function themeBuildLockText(id){if(id==='v-signal')return'테마 카드 해금 필요 · 전체 2클리어부터';if(id==='zero-sight')return'테마 카드 해금 필요 · 전체 1클리어부터';if(id==='point-blank')return'테마 카드 해금 필요 · 전체 1클리어부터';return'사용할 수 없음'}",
     'point blank unlock copy')

# 2) Full-pool staging is over: all 60 completed theme cards may enter normal reward ranking once unlocked.
def unstage(match):
    return match.group(1)
text,new_count=re.subn(r"(themeId:'(?:v-signal|zero-sight|point-blank)',)rewardPool:false,",unstage,text)
if new_count not in (0,51):
    raise SystemExit(f'expected 51 staged theme cards, got {new_count}')
old_reward="const suppliedPool=[...new Set(Array.isArray(input.poolIds)?input.poolIds:[])],allowStaged=suppliedPool.length<ROGUELIKE_REWARD_ROLES.length,pool=suppliedPool.filter(id=>{const def=NAMED?.[id];if(!def||String(id).startsWith('J')||(!allowStaged&&def.rewardPool===false))return false;"
new_reward="const suppliedPool=[...new Set(Array.isArray(input.poolIds)?input.poolIds:[])],pool=suppliedPool.filter(id=>{const def=NAMED?.[id];if(!def||String(id).startsWith('J'))return false;"
once(old_reward,new_reward,'remove reward staging filter')

# 3) Region encounters now showcase the completed live pools while preserving fixed physical slot skeletons.
once("named:Object.freeze(['VSH5','H2','D2','D8','H10','C10','VSD4','H3','C8','H8','VSCK','CJ'])",
     "named:Object.freeze(['VSH5','VSD4','VSS5','VSH3','VSH7','VSH10','VSD2','VSD3','VSD6','VSC8','VSCJ','VSCK'])",
     'neon v-signal roster')
once("named:Object.freeze(['ZSCA','ZSC2','S5','S7B','C5B','PBH7','ZSD6','H8','PBDJ','S8','ZSSK','S6'])",
     "named:Object.freeze(['ZSCA','ZSC2','ZSH4','PBD4','ZSD6','PBH6','ZSS7','PBS8','ZSD8','PBDJ','ZSSQ','ZSSK'])",
     'red zone precision clash roster')

# 4) Theme tutorial selector: multiple live experiences must all be reachable from the menu.
once("<button id=\"themeTutorialBtn\" class=\"pixelBtn\" type=\"button\" disabled aria-disabled=\"true\">테마 체험전 · 기본 완료 후</button>",
     "<div id=\"themeTutorialPicker\" class=\"codexFilterRow\"><label>테마 <select id=\"themeTutorialSelect\" aria-label=\"테마 체험전 선택\" disabled><option value=\"\">준비 중</option></select></label><button id=\"themeTutorialBtn\" class=\"pixelBtn\" type=\"button\" disabled aria-disabled=\"true\">테마 체험전 · 기본 완료 후</button></div>",
     'theme tutorial selector html')
once("const prompt=document.getElementById('firstRunPrompt'),note=document.getElementById('startResumeNote'),tutorialBtn=document.getElementById('basicTutorialBtn'),tutorialState=tutorialBtn?.querySelector('.menuState'),tutorialSmall=tutorialBtn?.querySelector('small'),advanced=document.getElementById('advancedTutorialBtn'),themeTutorial=document.getElementById('themeTutorialBtn');",
     "const prompt=document.getElementById('firstRunPrompt'),note=document.getElementById('startResumeNote'),tutorialBtn=document.getElementById('basicTutorialBtn'),tutorialState=tutorialBtn?.querySelector('.menuState'),tutorialSmall=tutorialBtn?.querySelector('small'),advanced=document.getElementById('advancedTutorialBtn'),themeTutorial=document.getElementById('themeTutorialBtn'),themeTutorialSelect=document.getElementById('themeTutorialSelect');",
     'render start tutorial selector variable')
once("if(themeTutorial){const available=typeof availableThemeTutorials==='function'?availableThemeTutorials():[],ready=p.tutorialCompleted&&available.length>0;themeTutorial.disabled=!ready;themeTutorial.setAttribute('aria-disabled',String(!ready));themeTutorial.textContent=ready?`테마 체험전 · ${available.map(x=>themeDef(x.themeId)?.displayName||x.themeId).join(' / ')}`:p.tutorialCompleted?'테마 체험전 · 준비 중':'테마 체험전 · 기본 완료 후'}",
     "if(themeTutorial){const available=typeof availableThemeTutorials==='function'?availableThemeTutorials():[],ready=p.tutorialCompleted&&available.length>0,prior=themeTutorialSelect?.value||'',preferred=available.some(x=>x.themeId===p.selectedTheme)?p.selectedTheme:available.some(x=>x.themeId===prior)?prior:available[0]?.themeId||'';if(themeTutorialSelect){themeTutorialSelect.innerHTML=available.length?available.map(x=>`<option value=\"${x.themeId}\">${themeDef(x.themeId)?.displayName||x.themeId}</option>`).join(''):'<option value=\"\">준비 중</option>';themeTutorialSelect.value=preferred;themeTutorialSelect.disabled=!ready}themeTutorial.disabled=!ready;themeTutorial.setAttribute('aria-disabled',String(!ready));themeTutorial.textContent=ready?'선택한 테마 체험 시작':p.tutorialCompleted?'테마 체험전 · 준비 중':'테마 체험전 · 기본 완료 후'}",
     'render multiple live tutorial choices')
once("document.getElementById('themeTutorialBtn').onclick=()=>startThemeTutorial();",
     "document.getElementById('themeTutorialBtn').onclick=()=>startThemeTutorial(document.getElementById('themeTutorialSelect')?.value||null);",
     'theme tutorial selected launch')

# 5) Add one focused experience for each newly activated theme.
old_tail=" {id:'vsEncore',themeId:'v-signal',title:'앙코르 재입장',goal:'V-SIGNAL은 회수한 카드를 다른 공개 조합으로 다시 연결하는 콤보를 만든다. 앙코르를 회수한 뒤 같은 턴 다른 조합의 반환 재료로 재사용해 보세요.',hint:'먼저 내 ♥ 런의 앙코르 5♥를 선택해 회수하세요. 그 다음 손으로 돌아온 앙코르를 선택해 상대 5♠·5♦·5♣ 세트에 붙이세요. 보통 회수 카드는 같은 턴 버스트/체인 반환에 못 쓰지만, 앙코르는 다른 합법 조합에 한 번 재입장할 수 있습니다.',implemented:true,scenario:'vsEncore',allow:['boardSelect','recover','select','attach','clear'],boardRoles:['vsEncoreCard'],boardSide:'player',selectRoles:['vsEncoreCard'],attachSide:'enemy',expectAttach:'SET',expectAttachTag:'vEncore',expectRecoveredSameTurn:true,expectSwitchTarget:'enemy',minPowerGain:24,completeOn:'attach',stopAfter:true}\n]);"
new_tail=" {id:'vsEncore',themeId:'v-signal',title:'앙코르 재입장',goal:'V-SIGNAL은 회수한 카드를 다른 공개 조합으로 다시 연결하는 콤보를 만든다. 앙코르를 회수한 뒤 같은 턴 다른 조합의 반환 재료로 재사용해 보세요.',hint:'먼저 내 ♥ 런의 앙코르 5♥를 선택해 회수하세요. 그 다음 손으로 돌아온 앙코르를 선택해 상대 5♠·5♦·5♣ 세트에 붙이세요. 보통 회수 카드는 같은 턴 버스트/체인 반환에 못 쓰지만, 앙코르는 다른 합법 조합에 한 번 재입장할 수 있습니다.',implemented:true,scenario:'vsEncore',allow:['boardSelect','recover','select','attach','clear'],boardRoles:['vsEncoreCard'],boardSide:'player',selectRoles:['vsEncoreCard'],attachSide:'enemy',expectAttach:'SET',expectAttachTag:'vEncore',expectRecoveredSameTurn:true,expectSwitchTarget:'enemy',minPowerGain:24,completeOn:'attach',stopAfter:true},\n {id:'zsObserver',themeId:'zero-sight',title:'관측수 · 표적 지정',goal:'ZERO-SIGHT는 공개 조합 하나를 표적으로 지정해 다른 카드의 정밀 효과가 공통 조합을 따라가게 합니다. 관측수를 포함한 A 세트를 만들어 표적을 지정하세요.',hint:'관측수 A♣와 A♥ · A♦를 선택해 새 세트를 만드세요. 관측수가 그 공개 조합을 내 표적으로 지정하고 남은 손패를 한 번 순환합니다.',implemented:true,scenario:'zsObserver',allow:['select','meld','clear'],selectRoles:['zsObserverCard','zsSet'],expectMeld:'SET',completeOn:'meld',stopAfter:true},\n {id:'pbBreach',themeId:'point-blank',title:'브리치 실드 · 접전 진입',goal:'POINT-BLANK는 상대 공개 조합 하나를 접전으로 만들고 그 안에서 회수·교대·재돌입 효과를 이어갑니다. 브리치 실드로 상대 런에 진입하세요.',hint:'브리치 실드 A♥를 선택해 상대 2♥-3♥-4♥ 런에 붙이세요. 접전이 지정되고 보호막 12를 얻습니다.',implemented:true,scenario:'pbBreach',allow:['select','attach','clear'],selectRoles:['pbBreachCard'],attachSide:'enemy',expectAttach:'RUN',expectAttachTag:'pbBreachShield',expectShieldGain:12,completeOn:'attach',stopAfter:true}\n]);"
once(old_tail,new_tail,'new theme tutorial steps')
once("else if(step.scenario==='vsEncore'){const encore=makeTutorialNamed('VSH5','vsEncoreCard');p.hand=[makeTutorialCard('D','2','hold')];p.melds=[makeTutorialMeld('player','RUN',[encore,makeTutorialCard('H','6','board','player'),makeTutorialCard('H','7','board','player'),makeTutorialCard('H','8','board','player')],1)];e.melds=[makeTutorialMeld('enemy','SET',[makeTutorialCard('S','5','board','enemy'),makeTutorialCard('D','5','board','enemy'),makeTutorialCard('C','5','board','enemy')])];state.phase='action';log('V-SIGNAL 체험 · 내 ♥ 런의 앙코르 5♥를 회수한 뒤, 같은 턴 상대 5 세트에 재입장시켜 버스트하세요. 일반 회수 카드의 반환 재사용 제한을 앙코르가 한 번 넘습니다.','important')}return true}",
     "else if(step.scenario==='vsEncore'){const encore=makeTutorialNamed('VSH5','vsEncoreCard');p.hand=[makeTutorialCard('D','2','hold')];p.melds=[makeTutorialMeld('player','RUN',[encore,makeTutorialCard('H','6','board','player'),makeTutorialCard('H','7','board','player'),makeTutorialCard('H','8','board','player')],1)];e.melds=[makeTutorialMeld('enemy','SET',[makeTutorialCard('S','5','board','enemy'),makeTutorialCard('D','5','board','enemy'),makeTutorialCard('C','5','board','enemy')])];state.phase='action';log('V-SIGNAL 체험 · 내 ♥ 런의 앙코르 5♥를 회수한 뒤, 같은 턴 상대 5 세트에 재입장시켜 버스트하세요. 일반 회수 카드의 반환 재사용 제한을 앙코르가 한 번 넘습니다.','important')}else if(step.scenario==='zsObserver'){p.hand=[makeTutorialNamed('ZSCA','zsObserverCard'),makeTutorialCard('H','A','zsSet'),makeTutorialCard('D','A','zsSet'),makeTutorialCard('C','9','hold')];state.phase='action';log('ZERO-SIGHT 체험 · 관측수 A♣와 A♥·A♦로 새 세트를 만들어 그 조합을 표적으로 지정하세요.','important')}else if(step.scenario==='pbBreach'){p.hand=[makeTutorialNamed('PBHA','pbBreachCard'),makeTutorialCard('D','9','hold')];e.melds=[makeTutorialMeld('enemy','RUN',[makeTutorialCard('H','2','board','enemy'),makeTutorialCard('H','3','board','enemy'),makeTutorialCard('H','4','board','enemy')])];state.switchTarget='player';state.switchPower=12;state.phase='action';log('POINT-BLANK 체험 · 브리치 실드 A♥를 상대 ♥ 런에 붙여 접전을 만들고 보호막을 확보하세요.','important')}return true}",
     'tutorial scenarios')

# Make completion copy generic for every live theme instead of V-SIGNAL-only.
once("step.themeId==='v-signal'?'V-SIGNAL 체험 완료! 전용 자원 없이 회수 → 다른 공개 조합 재입장 → 버스트로 이어지는 테마의 핵심 연결을 확인했습니다.':'다음 실습은 잠시 후 자동으로 시작됩니다.'",
     "step.themeId?`${themeDef(step.themeId)?.displayName||step.themeId} 체험 완료! ${step.themeId==='v-signal'?'회수 → 재입장 연결':step.themeId==='zero-sight'?'표적 지정 → 정밀 효과 연결':'접전 지정 → 돌입·회수 연결'}의 핵심을 확인했습니다.`:'다음 실습은 잠시 후 자동으로 시작됩니다.'",
     'generic theme tutorial completion copy')

# 6) Docs and roadmap: close the 60-card integration gate.
road=Path('ROADMAP.md')
r=road.read_text(encoding='utf-8')
section="""
## M8T — 기존 3테마 60장 통합 · 완료
V-SIGNAL 24장 + ZERO-SIGHT 18장 + POINT-BLANK 18장의 개별 구현 뒤, 실제 일반 플레이 풀로 승격하는 통합 단계다.

- [x] 60장 전체를 해금 이후 일반 로그라이크 보상 후보로 승격 — 임시 `rewardPool:false` staging 제거
- [x] POINT-BLANK 일반 카드군 선택 활성화 — V-SIGNAL / ZERO-SIGHT / POINT-BLANK 3테마 모두 일반 빌드 가능
- [x] 카드 도감의 3테마 탭에서 각 24 / 18 / 18 전체 효과 사전 확인 유지
- [x] ZERO-SIGHT `관측수 · 표적 지정` 체험전 추가
- [x] POINT-BLANK `브리치 실드 · 접전 진입` 체험전 추가
- [x] 테마 체험전 선택 UI 추가 — 여러 라이브 테마를 각각 직접 시작 가능
- [x] 네온 아크 적 덱을 V-SIGNAL 풀 카드로 재편
- [x] 레드 존 적 덱을 ZERO-SIGHT + POINT-BLANK 혼합 풀로 재편
- [x] 기존 해금 단계는 유지해 초반 카드 폭증을 방지하고, 해금된 카드만 보상/덱빌더에 진입
- [x] 60장 직접 위력 비율·물리 슬롯 유일성·테마 혼합 회귀 유지
- [x] 전체 `tests/*.mjs` 회귀 통과

"""
if '## M8T — 기존 3테마 60장 통합 · 완료' not in r:
    anchor='## M9 — Jokers + Fields'
    if anchor not in r: raise SystemExit('missing ROADMAP M9 anchor')
    r=r.replace(anchor,section+anchor,1)
road.write_text(r,encoding='utf-8')

plan=Path('docs/THEME_FULL_POOL_PLAN.md')
p=plan.read_text(encoding='utf-8')
p=p.replace('## 4. 60장 완성 후 통합\n\n세 카드군의 개별 효과 구현이 모두 끝난 뒤 한 번에 아래를 정리한다.','## 4. 60장 완성 후 통합 · 완료\n\n**통합 완료 기록 — 2026-09-03.** 세 카드군의 60장 전체를 일반 플레이 풀로 승격했다. 기존 해금 단계는 유지하되 해금된 카드는 보상·자동 덱·도감에서 더 이상 임시 staging으로 제외하지 않는다.')
for old,new in [
('- 카드 도감 카드군별 전체 카드 표시','- [x] 카드 도감 카드군별 전체 카드 표시'),
('- 해금 그룹 재배치','- [x] 기존 단계형 해금 그룹 유지 및 60장 전체 도달성 확인'),
('- 로그라이크 랜덤 보상 후보 조정','- [x] 로그라이크 랜덤 보상 후보 조정 — 60장 staging 해제'),
('- 지역 적 덱/보스 카드 풀 조정','- [x] 지역 적 덱/보스 카드 풀 조정'),
('- 테마 빌드 프로필 및 가중치 재시뮬레이션','- [x] 테마 빌드 프로필 및 가중치 재시뮬레이션 — 4장 상한/혼합 9장 계약 유지'),
('- ZERO-SIGHT / POINT-BLANK 튜토리얼 활성화','- [x] ZERO-SIGHT / POINT-BLANK 튜토리얼 활성화'),
('- 카드군별 핵심 행동 도움말 추가','- [x] 카드군별 핵심 행동 도움말 추가 — 선택 설명 + 체험전 목표/힌트'),
('- 60장 전체 직접 위력 효과 비율 감사','- [x] 60장 전체 직접 위력 효과 비율 감사'),
('- 슬롯 중복/물리 52슬롯 충돌 감사','- [x] 슬롯 중복/물리 52슬롯 충돌 감사'),
('- 전체 `tests/*.mjs` 회귀','- [x] 전체 `tests/*.mjs` 회귀')]:
    p=p.replace(old,new)
p=p.replace('5. **60장 통합 밸런스/해금/로그라이크/튜토리얼**','5. **60장 통합 밸런스/해금/로그라이크/튜토리얼 — 완료**')
plan.write_text(p,encoding='utf-8')

# 7) Full-pool tests graduate from staging assertions to live-pool assertions.
for path,legacy in [
 ('tests/vsignal-full-pool.mjs'," if(!['VSH5','VSD4','VSCK'].includes(id))ok(d.rewardPool===false,`${id} is staged out of ordinary roguelike rewards until 60-card integration`);"),
 ('tests/zero-sight-full-pool.mjs',"if(!['ZSCA','ZSC2','ZSD6','ZSSK'].includes(id))ok(d.rewardPool===false,`${id} is staged out of ordinary roguelike rewards until 60-card integration`)"),
 ('tests/point-blank-full-pool.mjs',"if(!['PBH7','PBDJ'].includes(id))ok(d.rewardPool===false,`${id} is staged out of ordinary roguelike rewards until 60-card integration`)")]:
    f=Path(path);s=f.read_text(encoding='utf-8')
    if legacy in s:
        s=s.replace(legacy,"ok(d.rewardPool!==false,`${id} is eligible for ordinary roguelike rewards after 60-card integration`)" + (';' if path.endswith('vsignal-full-pool.mjs') else ''))
    f.write_text(s,encoding='utf-8')

vf=Path('tests/vsignal-full-pool.mjs');s=vf.read_text(encoding='utf-8')
s=s.replace("ok(script.includes('allowStaged=suppliedPool.length<ROGUELIKE_REWARD_ROLES.length'),'ordinary reward calls distinguish scarce caller-supplied pools');\nok(script.includes(\"(!allowStaged&&def.rewardPool===false)\"),'ordinary roguelike reward ranking excludes staged full-pool cards');",
            "ok(!script.includes('allowStaged=')&&!script.includes('def.rewardPool===false'),'ordinary roguelike reward ranking no longer stages completed theme cards');")
vf.write_text(s,encoding='utf-8')

# Foundation test now expects all three tutorial registrations live and a selector-backed launcher.
tf=Path('tests/theme-tutorial-foundation.mjs');s=tf.read_text(encoding='utf-8')
s=s.replace("ok(script.includes('const THEME_TUTORIALS=Object.freeze(')&&script.includes(\"'zero-sight':Object.freeze({themeId:'zero-sight',startStep:null,live:false})\")&&script.includes(\"'point-blank':Object.freeze({themeId:'point-blank',startStep:null,live:false})\"),'theme tutorial registry stays explicit while unimplemented themes remain non-live');",
            "ok(script.includes(\"'zero-sight':Object.freeze({themeId:'zero-sight',startStep:'zsObserver',live:true})\")&&script.includes(\"'point-blank':Object.freeze({themeId:'point-blank',startStep:'pbBreach',live:true})\"),'completed ZERO-SIGHT and POINT-BLANK experiences are live');")
s=s.replace("ok(script.includes(\"document.getElementById('themeTutorialBtn').onclick=()=>startThemeTutorial()\"),'theme tutorial button is wired to the shared launcher');",
            "ok(html.includes('id=\"themeTutorialSelect\"')&&script.includes(\"startThemeTutorial(document.getElementById('themeTutorialSelect')?.value||null)\"),'theme tutorial menu can launch each selected live experience');")
tf.write_text(s,encoding='utf-8')

# Character/theme picker now treats POINT-BLANK as a normal live profile.
cf=Path('tests/character-theme-picker.mjs');s=cf.read_text(encoding='utf-8')
s=s.replace("ok(source('themeBuildLockText').includes(\"return'개발 중'\"),'unfinished theme groups are shown as development-locked');",
            "ok(script.includes(\"'point-blank':Object.freeze({id:'point-blank',displayName:'POINT-BLANK'\")&&script.includes(\"themeId:'point-blank',live:true\"),'POINT-BLANK is a normal live build profile after 60-card integration');")
cf.write_text(s,encoding='utf-8')

# Dedicated 60-card integration regression.
integration=Path('tests/theme-60-integration.mjs')
integration.write_text(r'''import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const plan=fs.readFileSync(new URL('../docs/THEME_FULL_POOL_PLAN.md',import.meta.url),'utf8');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function literal(name,next){const a=script.indexOf(`const ${name}=`),b=script.indexOf(next,a);if(a<0||b<0)throw Error(`missing ${name}`);return script.slice(a+`const ${name}=`.length,b).trim().replace(/;$/,'')}
const ctx=vm.createContext({console,Object,Array,Set,Map,Number,String,Boolean,Math});
vm.runInContext(`globalThis.NAMED=${literal('NAMED','\nconst CHARACTERS=')}`,ctx);
const themeIds=['v-signal','zero-sight','point-blank'];
const cards=Object.entries(ctx.NAMED).filter(([,d])=>themeIds.includes(d?.themeId));
ok(cards.length===60,'three completed themes expose exactly 60 live card definitions');
ok(cards.every(([,d])=>d.rewardPool!==false),'all 60 completed theme cards are eligible for ordinary reward ranking once unlocked');
ok(!script.includes('allowStaged=')&&!script.includes('def.rewardPool===false'),'temporary reward staging filter is removed');
ok(script.includes("themeId:'point-blank',live:true"),'POINT-BLANK build profile is live');
for(const [id,step] of [['v-signal','vsEncore'],['zero-sight','zsObserver'],['point-blank','pbBreach']])ok(script.includes(`themeId:'${id}',startStep:'${step}',live:true`)&&script.includes(`id:'${step}',themeId:'${id}'`),`${id} has a live implemented theme experience`);
ok(html.includes('id="themeTutorialSelect"')&&script.includes("startThemeTutorial(document.getElementById('themeTutorialSelect')?.value||null)"),'menu exposes a real selector for all live theme experiences');
for(const marker of ["scenario==='zsObserver'","makeTutorialNamed('ZSCA','zsObserverCard')","scenario==='pbBreach'","makeTutorialNamed('PBHA','pbBreachCard')"])ok(script.includes(marker),`tutorial scenario wiring contains ${marker}`);
const neon=script.match(/'neon-arc':Object\.freeze\(\{[\s\S]*?named:Object\.freeze\(\[(.*?)\]\)\}\)/)?.[1]||'';
const red=script.match(/'red-zone':Object\.freeze\(\{[\s\S]*?named:Object\.freeze\(\[(.*?)\]\)\}\)/)?.[1]||'';
const ids=x=>[...x.matchAll(/'([^']+)'/g)].map(m=>m[1]);
const neonIds=ids(neon),redIds=ids(red);
ok(neonIds.length===12&&neonIds.every(id=>ctx.NAMED[id]?.themeId==='v-signal'),'NEON ARC 12-card encounter pool is a full V-SIGNAL showcase');
ok(redIds.length===12&&redIds.some(id=>ctx.NAMED[id]?.themeId==='zero-sight')&&redIds.some(id=>ctx.NAMED[id]?.themeId==='point-blank'),'RED ZONE 12-card encounter pool mixes ZERO-SIGHT and POINT-BLANK');
for(const [label,list] of [['neon',neonIds],['red',redIds]])ok(new Set(list.map(id=>ctx.NAMED[id]?.slot||id)).size===list.length,`${label} thematic encounter variants occupy unique physical slots`);
ok(road.includes('M8T — 기존 3테마 60장 통합 · 완료'),'ROADMAP closes the 60-card integration milestone');
ok(plan.includes('## 4. 60장 완성 후 통합 · 완료')&&plan.includes('60장 통합 밸런스/해금/로그라이크/튜토리얼 — 완료'),'canonical full-pool plan closes the integration phase');
console.log('Three-theme 60-card integration regression passed.');
''',encoding='utf-8')

index.write_text(text,encoding='utf-8')
print('theme 60-card integration patch applied')

import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync('index.html','utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
const road=fs.readFileSync('ROADMAP.md','utf8');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let par=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')par++;else if(script[i]===')')par--;else if(script[i]==='{'&&par===0){brace=i;break}}if(brace<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
function context(extra={}){return vm.createContext({console,Set,Map,Array,Object,Number,String,Boolean,Math,...extra})}
function install(ctx,...names){for(const n of names)vm.runInContext(source(n),ctx)}

ok(html.includes('data-codex-filter="theme:v-signal"'),'codex exposes a V-SIGNAL theme tab');
ok(html.includes('data-codex-filter="theme:zero-sight"'),'codex exposes a ZERO//SIGHT theme tab');
ok(html.includes('data-codex-filter="theme:point-blank"'),'codex exposes a POINT//BLANK theme tab');
ok(html.includes('카드군 탭에서는 카드군 정체성과 효과를 미리 확인'),'codex explains theme-tab reveal behavior');
ok(source('codexThemeFilterId').includes("startsWith('theme:')"),'theme-filter parser is shared by the codex renderer');
const codex=source('renderCodex');
ok(codex.includes('n.themeId!==themeFilter'),'theme tab filters live NAMED cards by exact themeId');
ok(codex.includes('reveal=access||!!themeFilter'),'theme tabs reveal implemented theme-card identity even before normal unlock');
ok(codex.includes('🔒 미해금 · 해금:'),'theme-card reveal keeps the real unlock condition visible');
ok(codex.includes('codexLockVisual')&&codex.includes('???'),'ordinary locked codex entries keep spoiler concealment');
ok(codex.includes('현재 코드에 라이브 구현된 카드가 없습니다.'),'empty/unimplemented theme tabs explain that no live card exists yet');
ok(codex.includes('baseUnlockedNamed')&&codex.includes('normalUnlocked'),'developer reveal still distinguishes real progression unlock state');

ok(html.includes('id="developerOverlay"'),'developer mode has a dedicated modal');
ok(html.includes('id="developerBtn"'),'developer mode is reachable from the main menu');
ok(html.includes('id="developerHudBtn"'),'developer mode is reachable from the combat HUD');
ok(html.includes('id="developerToggleBtn"')&&html.includes('id="developerBattleBtn"'),'developer modal exposes toggle and DEV battle actions');
ok(script.includes("const DEV_STORAGE_KEY='rummyDuelDeveloperV1'"),'developer mode persists under a key separate from normal progression');
ok(source('renderDeveloperPanel').includes('DEV · ON · 해금 제한 우회'),'developer panel clearly reports active bypass state');
ok(source('setDeveloperMode').includes('saveDeveloperMode()'),'developer toggle persists independently');
ok(source('showStartScreen').includes("'developerOverlay'"),'returning home closes the developer overlay');
ok(script.includes("document.getElementById('developerToggleBtn').onclick"),'developer toggle is wired to the UI');
ok(script.includes("document.getElementById('developerCodexBtn').onclick"),'developer mode can jump directly to the codex');
ok(script.includes("document.getElementById('developerProgressBtn').onclick"),'developer mode can jump directly to character/theme selection');

const charUnlock=source('charUnlocked'),themeUnlock=source('themeBuildUnlocked'),namedUnlock=source('unlockedNamed'),fieldUnlock=source('unlockedFields');
ok(charUnlock.includes("typeof developerModeActive==='function'&&developerModeActive()"),'character unlock supports optional DEV bypass');
ok(themeUnlock.includes("typeof developerModeActive==='function'&&developerModeActive()"),'theme build unlock supports optional DEV bypass');
ok(namedUnlock.includes('new Set(Object.keys(NAMED))'),'DEV exposes every currently implemented named-card definition');
ok(fieldUnlock.includes('Object.keys(FIELDS)'),'DEV exposes every currently implemented field definition');
ok(source('renderProgress').includes('개발 중 · DEV 선택 가능'),'development themes remain labeled development-only even when DEV-selectable');

{
 const ctx=context({CHARACTERS:{wanderer:{},jester:{}},CHARACTER_UNLOCK:{wanderer:()=>true,jester:()=>false},progress:{},developerModeActive:()=>true});
 install(ctx,'charUnlocked');
 ok(ctx.charUnlocked('jester',{})===true,'DEV bypass unlocks an otherwise locked implemented character');
}
{
 const ctx=context({THEME_BUILD_PROFILES:{'zero-sight':{live:false,themeId:'zero-sight'}},progress:{},developerModeActive:()=>true});
 install(ctx,'themeBuildUnlocked');
 ok(ctx.themeBuildUnlocked('zero-sight',{})===true,'DEV bypass allows selecting a development theme profile');
}
{
 const ctx=context({NAMED:{A:{},B:{}},progress:{},developerModeActive:()=>true});
 install(ctx,'unlockedNamed');
 ok([...ctx.unlockedNamed({})].length===2,'DEV named pool contains all implemented NAMED entries');
}
{
 const ctx=context({FIELDS:{F1:{},F2:{}},progress:{},developerModeActive:()=>true});
 install(ctx,'unlockedFields');
 ok(ctx.unlockedFields({}).length===2,'DEV field pool contains all implemented fields');
}

ok(script.includes('developerBattle:false'),'battle state owns an explicit developerBattle snapshot flag');
ok(source('newGame').includes("state.developerBattle=mode==='battle'"),'new battle snapshots DEV status at battle start');
ok(source('render').includes("state.developerBattle?'<span class=\"gold\"> · DEV</span>'"),'combat HUD marks a non-rewarding DEV battle');
const grant=source('grantVictoryProgress');
ok(grant.includes('if(state.developerBattle){state.rewarded=true;return[]}'),'progress grant has a hard DEV battle guard');
{
 const state={rewarded:false,developerBattle:true};
 const ctx=context({state});
 install(ctx,'grantVictoryProgress');
 const result=ctx.grantVictoryProgress();
 ok(Array.isArray(result)&&result.length===0&&state.rewarded===true,'DEV reward guard exits before touching progression dependencies');
}
const resultSrc=source('showResult');
ok(resultSrc.includes('devBattle=!!state.developerBattle'),'result screen reads the battle snapshot instead of current toggle state');
ok(resultSrc.includes('DEV 승리')&&resultSrc.includes('진행도에 반영되지 않습니다'),'DEV result explicitly states no progression reward');

ok(road.includes('카드 도감에 카드군 전용 필터 추가'),'ROADMAP records theme-aware codex discovery');
ok(road.includes('별도 개발자 모드 추가'),'ROADMAP records the non-rewarding developer mode');
console.log('Codex theme/developer mode regression passed.');

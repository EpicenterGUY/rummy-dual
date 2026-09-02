import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let par=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')par++;else if(script[i]===')')par--;else if(script[i]==='{'&&par===0){brace=i;break}}if(brace<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
function context(extra={}){return vm.createContext({console,Set,Map,Array,Object,Number,String,Boolean,Math,...extra})}
function install(ctx,...names){for(const n of names)vm.runInContext(source(n),ctx)}

ok(html.includes('id="themeGroupGrid"'),'character/progress screen contains a theme-group picker');
ok(html.includes('카드군 / 테마'),'theme group picker is visibly labeled');
ok(html.includes('대전 준비 · 캐릭터'),'battle setup labels the current character step');
ok(script.includes("'v-signal':Object.freeze({id:'v-signal',displayName:'V-SIGNAL'"),'V-SIGNAL build profile is registered');
ok(script.includes("'zero-sight':Object.freeze({id:'zero-sight',displayName:'ZERO-SIGHT'"),'ZERO-SIGHT is visible in build profiles');
ok(script.includes("'point-blank':Object.freeze({id:'point-blank',displayName:'POINT-BLANK'"),'POINT-BLANK is visible in build profiles');
ok(script.includes("selectedTheme:'mixed'"),'old/new progress defaults safely to mixed theme');
ok(source('normalizeProgress').includes('selectedTheme:Object.prototype.hasOwnProperty.call(THEME_BUILD_PROFILES'),'saved theme selection is normalized');
ok(source('renderProgress').includes("data-theme-build")&&source('renderProgress').includes('themeBuildUnlocked(id)'),'theme cards render with selectable/locked state');
ok(source('renderProgress').includes('setupSelectionSummary'),'selected character/theme is shown within battle setup');
ok(source('render').includes('buildTheme.displayName'),'selected theme is visible in the combat HUD');
ok(source('newGame').includes("makeSide('player',progress.selectedChar,progress.selectedTheme)"),'selected theme reaches the actual player battle deck');
ok(source('newGame').includes("makeSide('enemy',enemyChar,'mixed')"),'player theme selection does not silently force the enemy deck');

// Open theme build: prioritize unlocked theme variants, but retain ordinary named cards.
{
  const NAMED={
    VS1:{slot:'H5',themeId:'v-signal',t:'x'},
    VS2:{slot:'D4',themeId:'v-signal',t:'x'},
    N1:{slot:'S5',t:'x'},N2:{slot:'C5',t:'x'},N3:{slot:'S7',t:'x'},N4:{slot:'H7',t:'x'},N5:{slot:'D7',t:'x'},N6:{slot:'C7',t:'x'},N7:{slot:'S9',t:'x'},N8:{slot:'H9',t:'x'},N9:{slot:'D9',t:'x'}
  };
  const CHARACTERS={wanderer:{weights:{}}},TENDENCY_BY_TAG={x:['mix']},progress={selectedTheme:'mixed'};
  const math=Object.create(Math);math.random=()=>0.2;
  const ctx=context({NAMED,CHARACTERS,TENDENCY_BY_TAG,progress,Math:math});
  install(ctx,'weightedPick','namedSlot','weightedVariantSample','cardWeightForChar','chooseNamedForBuild');
  const ids=Object.keys(NAMED);
  const picked=[...ctx.chooseNamedForBuild(ids,'wanderer','v-signal')];
  ok(picked.length===9,'theme build still uses the normal nine named slots');
  ok(picked.includes('VS1')&&picked.includes('VS2'),'all currently available V-SIGNAL variants are prioritized when below the theme cap');
  ok(picked.some(id=>!NAMED[id].themeId),'V-SIGNAL selection remains an open mixed deck rather than theme-only');
}

ok(source('makeDeck').includes("const buildTheme=themeBuildUnlocked(themeId)?themeId:'mixed'"),'unavailable/development themes fall back safely to mixed at deck build time');
ok(source('themeBuildLockText').includes("return'개발 중'"),'unfinished theme groups are shown as development-locked');
console.log('Character theme picker regression passed.');

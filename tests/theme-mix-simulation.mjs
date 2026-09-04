import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const themeDoc=fs.readFileSync(new URL('../docs/THEME_GROUPS.md',import.meta.url),'utf8');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let par=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')par++;else if(script[i]===')')par--;else if(script[i]==='{'&&par===0){brace=i;break}}if(brace<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
function literal(name,next){const a=script.indexOf(`const ${name}=`);if(a<0)throw new Error(`missing ${name}`);const b=script.indexOf(next,a);if(b<0)throw new Error(`missing end ${name}`);return script.slice(a+`const ${name}=`.length,b).trim().replace(/;$/,'')}
function rng(seed){let x=seed>>>0||1;return()=>{x=(x*1664525+1013904223)>>>0;return x/4294967296}}
function makeCtx(seed=1){const math=Object.create(Math);math.random=rng(seed);const ctx=vm.createContext({console,Set,Map,Array,Object,Number,String,Boolean,Math:math});vm.runInContext(`globalThis.NAMED=${literal('NAMED','\nconst CHARACTERS=')};globalThis.CHARACTERS=${literal('CHARACTERS','\nconst TENDENCY_BY_TAG=')};globalThis.TENDENCY_BY_TAG=${literal('TENDENCY_BY_TAG','\nconst FIELDS=')};${source('weightedPick')};${source('namedSlot')};${source('weightedVariantSample')};${source('cardWeightForChar')};${source('chooseNamedForBuild')}`,ctx);return ctx}

const base=makeCtx(1),NAMED=base.NAMED;
const regularIds=Object.keys(NAMED).filter(id=>id[0]!=='J');
const themeIds=['v-signal','zero-sight','point-blank','mail-route','scrap-shift'];
const themeCards=id=>regularIds.filter(cid=>NAMED[cid]?.themeId===id);
const slotOf=id=>base.namedSlot(id);
function uniqueSlots(ids){return new Set(ids.map(slotOf))}

// 1) Maximum-density theme builds use the real build selector and always stay open/mixed.
for(const theme of themeIds){
  const available=themeCards(theme),expected=Math.min(4,uniqueSlots(available).size);
  ok(expected>0,`${theme} has live/development cards available for composition simulation`);
  for(let seed=1;seed<=64;seed++){
    const ctx=makeCtx(seed*97+theme.length),picked=[...ctx.chooseNamedForBuild(regularIds,'wanderer',theme)],slots=picked.map(id=>ctx.namedSlot(id));
    ok(picked.length===9,`${theme} seed ${seed} keeps the normal nine named-card selection size`);
    ok(new Set(slots).size===picked.length,`${theme} seed ${seed} contains no duplicate physical rank+suit slot`);
    const count=picked.filter(id=>ctx.NAMED[id]?.themeId===theme).length;
    ok(count===expected,`${theme} seed ${seed} takes the intended maximum theme priority count`);
    ok(picked.some(id=>ctx.NAMED[id]?.themeId!==theme),`${theme} seed ${seed} remains open by retaining non-theme cards`);
  }
}

// 2) Every two-theme module can coexist under the same slot-exclusive rule and still has ordinary fill.
const pairs=[];for(let i=0;i<themeIds.length;i++)for(let j=i+1;j<themeIds.length;j++)pairs.push([themeIds[i],themeIds[j]]);
for(const[a,b]of pairs){
  const ctx=makeCtx(a.length*100+b.length),aPool=themeCards(a),aCap=Math.min(4,uniqueSlots(aPool).size);
  const first=[...ctx.weightedVariantSample(aPool,aCap,()=>1)],used=new Set(first.map(id=>ctx.namedSlot(id)));
  const bPool=themeCards(b).filter(id=>!used.has(ctx.namedSlot(id))),bCap=Math.min(4,uniqueSlots(bPool).size);
  const second=[...ctx.weightedVariantSample(bPool,bCap,()=>1)];for(const id of second)used.add(ctx.namedSlot(id));
  const chosen=first.concat(second),ordinary=regularIds.filter(id=>!ctx.NAMED[id]?.themeId&&!used.has(ctx.namedSlot(id)));
  const fill=[...ctx.weightedVariantSample(ordinary,Math.max(0,9-chosen.length),()=>1)],build=chosen.concat(fill),slots=build.map(id=>ctx.namedSlot(id));
  ok(first.length>0&&second.length>0,`${a}+${b} mix represents both theme modules`);
  ok(first.length<=4&&second.length<=4,`${a}+${b} mix respects the four-card cap per theme`);
  ok(new Set(slots).size===build.length,`${a}+${b} mix resolves all physical-slot conflicts`);
  ok(build.some(id=>ctx.NAMED[id]?.themeId===a)&&build.some(id=>ctx.NAMED[id]?.themeId===b),`${a}+${b} mix represents both themes`);
  ok(build.some(id=>!ctx.NAMED[id]?.themeId),`${a}+${b} mix still leaves ordinary-card space`);
  ok(build.length===9,`${a}+${b} mix fills the standard nine named-card module slots`);
}

// 3) General mixed builds sample both ordinary and theme cards over many deterministic seeds without slot duplication.
let mixedThemeSeen=0,mixedOrdinarySeen=0;
for(let seed=1;seed<=128;seed++){
  const ctx=makeCtx(seed*131),picked=[...ctx.chooseNamedForBuild(regularIds,'wanderer','mixed')];
  ok(picked.length===9&&new Set(picked.map(id=>ctx.namedSlot(id))).size===9,`mixed seed ${seed} stays nine-slot exclusive`);
  mixedThemeSeen+=picked.filter(id=>ctx.NAMED[id]?.themeId).length;
  mixedOrdinarySeen+=picked.filter(id=>!ctx.NAMED[id]?.themeId).length;
}
ok(mixedThemeSeen>0&&mixedOrdinarySeen>0,'general mixed simulation samples both theme and ordinary named cards');

// 4) Direct-power cards remain a minority globally and among the currently implemented theme cards.
const directTags=new Set(['finalUltimatum','blackBullet','fuseRound','vBroadcastAccident','vBadClip','vReverseViral','vBanSoon','mrHazardMail','mrFinalNotice','zsBallistics','zsOneShot','ssScrapRampage']);
const allDefs=Object.values(NAMED),directAll=allDefs.filter(c=>directTags.has(c.t));
const allTheme=allDefs.filter(c=>c.themeId),directTheme=allTheme.filter(c=>directTags.has(c.t));
ok(directAll.length/allDefs.length<0.20,`direct-power tags stay below 20% of all named definitions (${directAll.length}/${allDefs.length})`);
ok(directTheme.length/allTheme.length<0.50,`direct-power tags remain a minority of implemented theme cards (${directTheme.length}/${allTheme.length})`);

ok(road.includes('테마 최대밀도 / 2테마 / 일반 혼합 구성 시뮬레이션 + 직접 위력 비율 검사'),'ROADMAP closes the composition simulation gate');
ok(themeDoc.includes('테마 구성 안정성은 최대 테마 밀도 오픈형 빌드·모든 2테마 조합·일반 mixed 다중 시드 회귀로 검사한다'),'canonical theme doc records the simulation policy');
console.log('Theme composition and direct-power ratio simulation passed.');

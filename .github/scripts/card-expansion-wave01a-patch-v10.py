from pathlib import Path
import runpy

runpy.run_path('.github/scripts/card-expansion-wave01a-patch-v9.py', run_name='__main__')

# As theme pools grow, a two-theme simulation must model the same open-module
# cap as real themed builds instead of attempting to put every card from both
# themes into a nine-card named module.
test = Path('tests/theme-mix-simulation.mjs')
t = test.read_text(encoding='utf-8')
old = """for(const[a,b]of pairs){
  const themed=[...themeCards(a),...themeCards(b)],ctx=makeCtx(a.length*100+b.length),uniqueCount=uniqueSlots(themed).size;
  const chosen=[...ctx.weightedVariantSample(themed,uniqueCount,()=>1)],used=new Set(chosen.map(id=>ctx.namedSlot(id)));
  const ordinary=regularIds.filter(id=>!ctx.NAMED[id]?.themeId&&!used.has(ctx.namedSlot(id)));
  const fill=[...ctx.weightedVariantSample(ordinary,Math.max(0,9-chosen.length),()=>1)],build=chosen.concat(fill),slots=build.map(id=>ctx.namedSlot(id));
  ok(new Set(slots).size===build.length,`${a}+${b} mix resolves all physical-slot conflicts`);
  ok(build.some(id=>ctx.NAMED[id]?.themeId===a)&&build.some(id=>ctx.NAMED[id]?.themeId===b),`${a}+${b} mix represents both themes`);
  ok(build.some(id=>!ctx.NAMED[id]?.themeId),`${a}+${b} mix still leaves ordinary-card space`);
  ok(build.length===9,`${a}+${b} mix fills the standard nine named-card module slots`);
}
"""
new = """for(const[a,b]of pairs){
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
"""
if old not in t:
    raise SystemExit('missing two-theme simulation block')
t = t.replace(old, new, 1)
test.write_text(t, encoding='utf-8')

# Preserve the canonical principle while clarifying how it scales after a
# theme has more than four live variants.
doc = Path('docs/THEME_GROUPS.md')
d = doc.read_text(encoding='utf-8')
anchor = "- 테마 구성 안정성은 최대 테마 밀도 오픈형 빌드·모든 2테마 조합·일반 mixed 다중 시드 회귀로 검사한다. 같은 숫자+무늬 슬롯은 언제나 한 변형만 남기고, 직접 누적 위력 카드는 전체 풀의 소수로 유지한다."
addition = anchor + "\n- 테마 카드 풀이 커진 뒤의 구성 시뮬레이션은 한 테마를 전부 욱여넣지 않는다. 자동 단일 테마는 최대 4장, 2테마 혼합은 각 테마 최대 4장으로 샘플링하고 최소 1장의 비테마 공간을 남겨 오픈형 모듈 원칙을 유지한다."
if anchor in d and '2테마 혼합은 각 테마 최대 4장' not in d:
    d = d.replace(anchor, addition, 1)
doc.write_text(d, encoding='utf-8')

# Dedicated Wave regression also locks the scalable composition-policy text.
wave = Path('tests/card-expansion-wave01a.mjs')
w = wave.read_text(encoding='utf-8')
needle = "ok(src.includes(\"(themeId==='mixed'||NAMED[id]?.themeId!==themeId)\"),'automatic theme fill cannot exceed the four-card theme cap');"
extra = needle + "\nconst themeMix=fs.readFileSync(new URL('./theme-mix-simulation.mjs',import.meta.url),'utf8');\nok(themeMix.includes('mix respects the four-card cap per theme'),'two-theme simulation scales by capping each theme module at four cards');"
if needle in w and 'two-theme simulation scales by capping each theme module' not in w:
    w = w.replace(needle, extra, 1)
wave.write_text(w, encoding='utf-8')

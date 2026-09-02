from pathlib import Path
import runpy

runpy.run_path('.github/scripts/card-expansion-wave01a-patch-v8.py', run_name='__main__')

index = Path('index.html')
src = index.read_text(encoding='utf-8')
old = "function chooseNamedForBuild(unlocked,charId,themeId='mixed'){const preferred=themeId==='mixed'?[]:unlocked.filter(id=>NAMED[id]?.themeId===themeId),themeChosen=weightedVariantSample(preferred,Math.min(4,preferred.length),id=>cardWeightForChar(id,charId,themeId)),used=new Set(themeChosen.map(namedSlot)),rest=unlocked.filter(id=>!used.has(namedSlot(id))),fill=weightedVariantSample(rest,Math.max(0,9-themeChosen.length),id=>cardWeightForChar(id,charId,themeId));return themeChosen.concat(fill)}"
new = "function chooseNamedForBuild(unlocked,charId,themeId='mixed'){const preferred=themeId==='mixed'?[]:unlocked.filter(id=>NAMED[id]?.themeId===themeId),themeCap=Math.min(4,new Set(preferred.map(namedSlot)).size),themeChosen=weightedVariantSample(preferred,themeCap,id=>cardWeightForChar(id,charId,themeId)),used=new Set(themeChosen.map(namedSlot)),rest=unlocked.filter(id=>!used.has(namedSlot(id))&&(themeId==='mixed'||NAMED[id]?.themeId!==themeId)),fill=weightedVariantSample(rest,Math.max(0,9-themeChosen.length),id=>cardWeightForChar(id,charId,themeId));return themeChosen.concat(fill)}"
if old not in src:
    raise SystemExit('missing chooseNamedForBuild anchor')
src = src.replace(old, new, 1)
index.write_text(src, encoding='utf-8')

test = Path('tests/card-expansion-wave01a.mjs')
t = test.read_text(encoding='utf-8')
needle = "ok(src.includes(\"pool=stagedPool.length>=ROGUELIKE_REWARD_ROLES.length?stagedPool:rawPool\"),'scarce reward pools fall back to all legal candidates instead of losing picks');"
extra = needle + "\nok(src.includes(\"themeCap=Math.min(4,new Set(preferred.map(namedSlot)).size)\"),'automatic theme build caps priority by distinct physical slots');\nok(src.includes(\"(themeId==='mixed'||NAMED[id]?.themeId!==themeId)\"),'automatic theme fill cannot exceed the four-card theme cap');"
if needle in t and 'automatic theme build caps priority' not in t:
    t = t.replace(needle, extra, 1)
test.write_text(t, encoding='utf-8')

plan = Path('docs/CARD_EXPANSION_WAVE_01.md')
p = plan.read_text(encoding='utf-8')
note = "\n> 카드 증가로 드러난 자동 테마 빌드의 상한 우회도 함께 수정했다. 테마 우선 슬롯은 물리 슬롯 기준 최대 4장이고, 나머지 5장 채우기에서는 같은 테마를 다시 뽑지 않아 오픈형 혼합 덱을 유지한다.\n"
if note.strip() not in p:
    marker = '정식 로그라이크 보상 통합은 별도 밸런스 패스에서 진행한다.\n'
    if marker in p:
        p = p.replace(marker, marker + note, 1)
    else:
        p += note
plan.write_text(p, encoding='utf-8')

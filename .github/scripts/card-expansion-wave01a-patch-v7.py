from pathlib import Path
import runpy

patch = Path('.github/scripts/card-expansion-wave01a-patch.py')
text = patch.read_text(encoding='utf-8')

# Current main wording for pre-existing anchor cards.
text = text.replace(
    "'S7':{n:'검은 탄환',t:'blackBullet',d:'상대 공개 조합에 붙여 스위치를 반환하면 누적 위력이 10 증가한다.'},",
    "'S7':{n:'검은 탄환',t:'blackBullet',d:'상대 공개 조합에 붙여 스위치를 반환할 때 누적 위력이 10 증가한다.'},",
)
text = text.replace(
    "'S3':{n:'반품 청구서',t:'returnIfIgnored',d:'상대가 버림패에서 가져간 뒤 그 턴 조합에 사용하지 못하면, 턴 종료에 원래 주인의 덱 아래로 돌아간다.'},",
    "'S3':{n:'쥐구멍',t:'returnIfIgnored',d:'버렸는데 다음 내 턴까지 버림패에 남아 있으면 손으로 돌아온다. 상대가 가져가면 그 턴에는 조합에 사용할 수 없다.'},",
)

# Keep engine constants out of Korean-facing template literals.
text = text.replace(
    "detail:`내 ${x.meld.type}${x.meld.type==='RUN'?` · CHAIN ${x.meld.chain||0}`:''}`,entry:x",
    "detail:x.meld.type==='RUN'?`내 런 · 체인 ${x.meld.chain||0}`:'내 세트',entry:x",
)

# These six cards are live for unlocks, deck construction, codex and DEV,
# but their random roguelike reward integration is deliberately staged later.
# Put rewardPool after the existing theme/name/tag contract so old tooling that
# recognizes those adjacent fields remains compatible.
for old, new in [
    ("themeId:'v-signal',n:'첫 방송',t:'vFirstBroadcast',d:", "themeId:'v-signal',n:'첫 방송',t:'vFirstBroadcast',rewardPool:false,d:"),
    ("themeId:'v-signal',n:'RAID',t:'vRaid',d:", "themeId:'v-signal',n:'RAID',t:'vRaid',rewardPool:false,d:"),
    ("themeId:'zero-sight',n:'위장망',t:'zsCamoNet',d:", "themeId:'zero-sight',n:'위장망',t:'zsCamoNet',rewardPool:false,d:"),
    ("themeId:'zero-sight',n:'철갑탄',t:'zsArmorPiercing',d:", "themeId:'zero-sight',n:'철갑탄',t:'zsArmorPiercing',rewardPool:false,d:"),
    ("themeId:'point-blank',n:'돌입 명령',t:'pbBreachOrder',d:", "themeId:'point-blank',n:'돌입 명령',t:'pbBreachOrder',rewardPool:false,d:"),
    ("themeId:'point-blank',n:'플래시뱅',t:'pbFlashbang',d:", "themeId:'point-blank',n:'플래시뱅',t:'pbFlashbang',rewardPool:false,d:"),
]:
    text = text.replace(old, new)

# Preserve existing roguelike encounter compositions and reward-ranking
# baselines in this implementation wave.
text = text.replace("if \"'VSHA','VSC6'\" not in text:", "if False:")
text = text.replace("if \"'ZSH4','ZSS7','PBCA','PBS3'\" not in text:", "if False:")
text = text.replace("if \"vFirstBroadcast:['combo','cycle']\" not in text:", "if False:")
text = text.replace("if \"'point-blank':Object.freeze(['pbBreachOrder'])\" not in text:", "if False:")

patch.write_text(text, encoding='utf-8')
runpy.run_path(str(patch), run_name='__main__')

# Teach the existing reward candidate filter to honor per-card staging.
index = Path('index.html')
src = index.read_text(encoding='utf-8')
old = "const pool=[...new Set(Array.isArray(input.poolIds)?input.poolIds:[])].filter(id=>{const def=NAMED?.[id];if(!def||String(id).startsWith('J'))return false;const slot=namedSlot(id);return profile.slots.includes(slot)&&profile.variants[slot]!==id}),seed=String(input.seed||'reward-v1'),used=new Set(),picks=[];"
new = "const pool=[...new Set(Array.isArray(input.poolIds)?input.poolIds:[])].filter(id=>{const def=NAMED?.[id];if(!def||def.rewardPool===false||String(id).startsWith('J'))return false;const slot=namedSlot(id);return profile.slots.includes(slot)&&profile.variants[slot]!==id}),seed=String(input.seed||'reward-v1'),used=new Set(),picks=[];"
if old not in src:
    raise SystemExit('missing roguelike reward candidate filter anchor')
src = src.replace(old, new, 1)
index.write_text(src, encoding='utf-8')

# Extend dedicated regression coverage for the compatibility staging contract.
test = Path('tests/card-expansion-wave01a.mjs')
t = test.read_text(encoding='utf-8')
needle = "ok(!src.includes(\"case'pbBreachOrder':if(ctx.isAttach&&ctx.targetOwner===foe){fx.bonus\"),'Breach Order never adds direct switch power');"
extra = needle + "\nfor(const id of ['VSHA','VSC6','ZSH4','ZSS7','PBCA','PBS3']){const at=src.indexOf(`'${id}':{slot:`);ok(at>=0&&src.slice(at,at+220).includes('rewardPool:false'),`${id} stays outside random roguelike reward offers for Wave 01A`)}\nok(src.includes(\"if(!def||def.rewardPool===false||String(id).startsWith('J'))return false\"),'roguelike reward candidate filter honors staged named cards');"
if needle in t and 'reward candidate filter honors staged named cards' not in t:
    t = t.replace(needle, extra, 1)
test.write_text(t, encoding='utf-8')

# Make the rollout boundary explicit in the implementation document.
plan = Path('docs/CARD_EXPANSION_WAVE_01.md')
p = plan.read_text(encoding='utf-8')
note = "\n> Wave 01-A의 6장은 일반 해금·덱빌더·도감·DEV에서 라이브다. 기존 로그라이크 지역 적 덱과 랜덤 보상 후보에는 이번 웨이브에서 넣지 않는다. 해당 통합은 보상 순위/지역 구성 밸런스 패스와 함께 별도로 진행한다.\n"
status = 'Status: WAVE 01-A LIVE (6) / WAVE 01-B·01-C TARGET (12)'
if status in p and note.strip() not in p:
    p = p.replace(status, status + note, 1)
plan.write_text(p, encoding='utf-8')

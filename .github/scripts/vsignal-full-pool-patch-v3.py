from pathlib import Path
import runpy

runpy.run_path('.github/scripts/vsignal-full-pool-patch-v2.py', run_name='__main__')

index=Path('index.html')
text=index.read_text(encoding='utf-8')
old="const rawPool=[...new Set(Array.isArray(input.poolIds)?input.poolIds:[])].filter(id=>{const def=NAMED?.[id];if(!def||String(id).startsWith('J'))return false;const slot=namedSlot(id);return profile.slots.includes(slot)&&profile.variants[slot]!==id}),stagedPool=rawPool.filter(id=>NAMED?.[id]?.rewardPool!==false),pool=stagedPool.length>=ROGUELIKE_REWARD_ROLES.length?stagedPool:rawPool,seed=String(input.seed||'reward-v1'),used=new Set(),picks=[];"
new="const suppliedPool=[...new Set(Array.isArray(input.poolIds)?input.poolIds:[])],allowStaged=suppliedPool.length<ROGUELIKE_REWARD_ROLES.length,pool=suppliedPool.filter(id=>{const def=NAMED?.[id];if(!def||String(id).startsWith('J')||(!allowStaged&&def.rewardPool===false))return false;const slot=namedSlot(id);return profile.slots.includes(slot)&&profile.variants[slot]!==id}),seed=String(input.seed||'reward-v1'),used=new Set(),picks=[];"
if old not in text: raise SystemExit('missing staged reward pool v2 anchor')
text=text.replace(old,new,1)
index.write_text(text,encoding='utf-8')

test=Path('tests/vsignal-full-pool.mjs')
t=test.read_text(encoding='utf-8')
t=t.replace("ok(script.includes('stagedPool=rawPool.filter(id=>NAMED?.[id]?.rewardPool!==false)'),'ordinary roguelike reward ranking honors staged full-pool cards');\nok(script.includes('pool=stagedPool.length>=ROGUELIKE_REWARD_ROLES.length?stagedPool:rawPool'),'scarce roguelike reward pools preserve the legal fallback');", "ok(script.includes('allowStaged=suppliedPool.length<ROGUELIKE_REWARD_ROLES.length'),'ordinary reward calls distinguish scarce caller-supplied pools');\nok(script.includes(\"(!allowStaged&&def.rewardPool===false)\"),'ordinary roguelike reward ranking excludes staged full-pool cards');")
test.write_text(t,encoding='utf-8')

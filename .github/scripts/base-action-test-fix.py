from pathlib import Path
p=Path(__file__).resolve().parents[2]/'tests'/'base-action-simplification.mjs'
s=p.read_text(encoding='utf-8')
old="g.turnStart('enemy');s.hand.push(...c);assert.equal(g.submitNewMeld('enemy',c),true);assert.equal(s.melds.length,3);"
new="g.turnStart('enemy');s.hand.push(...cards(g,'enemy',['DK']));assert.equal(g.submitNewMeld('enemy',c),true);assert.equal(s.melds.length,3);"
if old not in s and new not in s:raise SystemExit('missing base action test setup anchor')
p.write_text(s.replace(old,new,1),encoding='utf-8')
print('base action test setup fixed')

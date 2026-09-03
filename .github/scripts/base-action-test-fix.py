from pathlib import Path
p=Path(__file__).resolve().parents[2]/'tests'/'base-action-simplification.mjs'
s=p.read_text(encoding='utf-8')
fixes=[
("g.turnStart('enemy');s.hand.push(...c);assert.equal(g.submitNewMeld('enemy',c),true);assert.equal(s.melds.length,3);","g.turnStart('enemy');s.hand.push(...cards(g,'enemy',['DK']));assert.equal(g.submitNewMeld('enemy',c),true);assert.equal(s.melds.length,3);"),
("g.turnStart('enemy');assert.equal(g.attachCards('enemy',[s5],'enemy',0),true,'older own meld can be attached');","g.turnStart('enemy');s.hand.push(...cards(g,'enemy',['DK']));assert.equal(g.attachCards('enemy',[s5],'enemy',0),true,'older own meld can be attached');"),
("const h5=g.makeCard('H','5',false,'enemy');s.hand=[h5];\n  assert.equal(g.attachCards('enemy',[h5],'player',0),true,'opponent public meld can be used by attach');","const h5=g.makeCard('H','5',false,'enemy');s.hand=[h5,...cards(g,'enemy',['DK'])];\n  assert.equal(g.attachCards('enemy',[h5],'player',0),true,'opponent public meld can be used by attach');"),
("const more=cards(g,'enemy',['S5','S6','S7']);s.hand=[...more];","const more=cards(g,'enemy',['S5','S6','S7']);s.hand=[...more,...cards(g,'enemy',['DK'])];"),
("const c7=g.makeCard('C','7',false,'enemy');s.hand=[c7];const before=s.spent.length;","const c7=g.makeCard('C','7',false,'enemy');s.hand=[c7,...cards(g,'enemy',['DK'])];const before=s.spent.length;")
]
for old,new in fixes:
    if old in s:s=s.replace(old,new,1)
    elif new not in s:raise SystemExit(f'missing base action test setup anchor: {old[:72]}')
p.write_text(s,encoding='utf-8')
print('base action test setups fixed')

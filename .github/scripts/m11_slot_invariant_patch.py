from pathlib import Path

road = Path('ROADMAP.md')
r = road.read_text()
old = '- [ ] One variant per exact rank+suit slot'
new = '- [x] One variant per exact rank+suit slot — named variants canonicalize through `namedSlot()`, variant sampling removes every other candidate sharing that base slot, and battle-deck materialization keeps one selected variant per canonical regular slot'
assert old in r, 'M11 slot invariant roadmap anchor changed'
r = r.replace(old, new, 1)
road.write_text(r)

from pathlib import Path

index = Path('index.html')
road = Path('ROADMAP.md')
text = index.read_text()

old = "for(let k=1;k<=Math.min(4,hand.length);k++)"
count = text.count(old)
assert count == 2, f'expected exactly two 4-card hand search caps, found {count}'
text = text.replace(old, "for(let k=1;k<=Math.min(6,hand.length);k++)")
index.write_text(text)

r = road.read_text()
old_line = '- [ ] Search 5+ card multi-attach cases where practical'
new_line = '- [x] Search 5+ card multi-attach cases where practical — AI extension planning and stuck-state legality now enumerate up to 6-card attach combinations while preserving the existing recovery, same-turn return, and SWITCH ownership guards'
assert old_line in r, 'M10 multi-attach roadmap anchor changed'
r = r.replace(old_line, new_line, 1)
road.write_text(r)

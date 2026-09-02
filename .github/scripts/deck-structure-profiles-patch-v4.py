from pathlib import Path
import runpy

runpy.run_path('.github/scripts/deck-structure-profiles-patch-v3.py', run_name='__main__')

index=Path('index.html')
text=index.read_text(encoding='utf-8')
old="const slots=structureSlots?new Set(structureSlots):new Set(namedChosen.map(namedSlot));\n if(!structureSlots){"
new="const slots=new Set(namedChosen.map(namedSlot));\n if(structureSlots){slots.clear();for(const slot of structureSlots)slots.add(slot)}\n if(!structureSlots){"
if old not in text and new not in text:
    raise SystemExit('missing canonical slot initialization anchor')
text=text.replace(old,new,1)
index.write_text(text,encoding='utf-8')

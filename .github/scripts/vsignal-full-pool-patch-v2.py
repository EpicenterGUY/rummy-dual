from pathlib import Path
import runpy

runpy.run_path('.github/scripts/vsignal-full-pool-patch.py', run_name='__main__')

index=Path('index.html')
text=index.read_text(encoding='utf-8')
block_start=text.find('const UNLOCK_GROUPS=')
block_end=text.find('function unlockedNamed',block_start)
block=text[block_start:block_end]
if "'VSD3'" not in block:
    old="items:['S8','H5','VSH5','VSH3','VSC4','VSC6','D9','C8','D10','C3']"
    new="items:['S8','H5','VSH5','VSH3','VSD3','VSC4','VSC6','D9','C8','D10','C3']"
    if old not in text: raise SystemExit('missing g2 V-SIGNAL unlock anchor')
    text=text.replace(old,new,1)
index.write_text(text,encoding='utf-8')

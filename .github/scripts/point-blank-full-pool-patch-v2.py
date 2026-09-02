from pathlib import Path
import runpy

runpy.run_path('.github/scripts/point-blank-full-pool-patch.py', run_name='__main__')

index=Path('index.html')
text=index.read_text(encoding='utf-8')
old="for(const target of targets)if(meldType(target.cards.concat(moving))===target.type)out.push({clash,recover,moving,target})}return out}"
new="for(const target of targets)if(meldType(target.cards.concat(moving))===target.type)out.push({clash,recover,moving,target})}}return out}"
if old in text:
    text=text.replace(old,new,1)
elif new not in text:
    raise SystemExit('missing Room Clear candidate-loop anchor')
index.write_text(text,encoding='utf-8')

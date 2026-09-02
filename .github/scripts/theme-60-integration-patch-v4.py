from pathlib import Path
src=Path('.github/scripts/theme-60-integration-patch-v3.py').read_text(encoding='utf-8')
exec(compile(src,'theme-60-integration-patch-v4-base','exec'))
p=Path('tests/m11a-region-rewards.mjs')
s=p.read_text(encoding='utf-8')
old="const baselinePicks={pure:['PBH7','S4','H3'],wanderer:['C8','S4','H3'],collector:['VSD4','D4','H3'],salvager:['S8','VSD4','D7B'],jester:['D3','H9','H3']};"
new="const baselinePicks={pure:['PBH7','PBD4','H3'],wanderer:['VSC4','S4','H3'],collector:['ZSH3','PBD4','H3'],salvager:['ZSC5','PBD4','D7B'],jester:['D3','H9','H3']};"
if new not in s:
    if old not in s: raise SystemExit('missing pre-integration reward baselines')
    s=s.replace(old,new,1)
s=s.replace("starterId+' common-start ranking stays unchanged'","starterId+' integrated 60-card common-start ranking stays deterministic'",1)
p.write_text(s,encoding='utf-8')
print('theme 60-card integration v4 reward baselines locked')

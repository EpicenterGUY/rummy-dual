from pathlib import Path

src_path=Path('.github/scripts/m11b_paired_seed_patch.py')
src=src_path.read_text()
old="""wire=\"document.getElementById('m11bNewPairSeedBtn')?.addEventListener('click',()=>newM11BExperimentSeed());\"\nif wire not in s:\n    anchor=\"document.getElementById('m11bExperimentClearBtn')?.addEventListener('click',()=>{if(confirm('M11B 실험 기록을 모두 지울까요?'))clearM11BExperimentHistory()});\"\n    if anchor not in s:raise SystemExit('M11B event wiring anchor missing')\n    s=s.replace(anchor,anchor+'\\n'+wire,1)"""
new="""wire=\"document.getElementById('m11bNewPairSeedBtn').onclick=()=>newM11BExperimentSeed();\"\nif wire not in s:\n    anchor=\"document.getElementById('m11bExperimentClearBtn').onclick=()=>{if(confirm('저장된 M11B 비대칭 실험 기록을 모두 지울까요?'))clearM11BExperimentHistory()};\"\n    if anchor not in s:raise SystemExit('M11B event wiring anchor missing')\n    s=s.replace(anchor,anchor+wire,1)"""
if old not in src:
    raise SystemExit('paired-seed source anchor shim no longer matches')
src=src.replace(old,new,1)
exec(compile(src,str(src_path),'exec'),{'__name__':'__main__'})

# Older sandbox reruns left the identical cohort/copy/clear assignment block twice.
# The paired-seed wire can sit between the first and second blocks, so remove every
# complete later block regardless of adjacency and keep only the first one.
p=Path('index.html')
html=p.read_text()
start="document.querySelectorAll('[data-m11b-experiment]').forEach(b=>b.onclick=()=>startM11BExperimentBattle(b.dataset.m11bExperiment));"
clear="document.getElementById('m11bExperimentClearBtn').onclick=()=>{if(confirm('저장된 M11B 비대칭 실험 기록을 모두 지울까요?'))clearM11BExperimentHistory()};"
wire="document.getElementById('m11bNewPairSeedBtn').onclick=()=>newM11BExperimentSeed();"
positions=[]
pos=0
while True:
    i=html.find(start,pos)
    if i<0:break
    positions.append(i)
    pos=i+len(start)
for second in reversed(positions[1:]):
    second_end=html.find(clear,second)
    if second_end<0:raise SystemExit('duplicate M11B cohort block has no clear endpoint')
    second_end+=len(clear)
    html=html[:second]+html[second_end:]
if html.count(wire)!=1:
    raise SystemExit(f'expected exactly one paired-seed wire, got {html.count(wire)}')
if html.count(start)!=1:
    raise SystemExit(f'expected exactly one M11B cohort wire block, got {html.count(start)}')
if html.count(clear)!=1:
    raise SystemExit(f'expected exactly one M11B clear wire, got {html.count(clear)}')
p.write_text(html)
print('M11B paired-seed runner applied and duplicate event wiring normalized')

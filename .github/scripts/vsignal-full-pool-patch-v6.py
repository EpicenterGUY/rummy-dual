from pathlib import Path
import runpy

runpy.run_path('.github/scripts/vsignal-full-pool-patch-v5.py', run_name='__main__')

index=Path('index.html')
text=index.read_text(encoding='utf-8')

# Keep the three pre-existing V-SIGNAL cards at their exact legacy unlock arrays.
# The 21 expansion cards live in separate theme unlock groups so expanding the
# pool cannot silently rewrite old progression contracts.
reverts=[
 ("items:['S6','H7','D8','C2','ZSCA','ZSC2','VSHA','VSD2','VSCA','DA','D3']", "items:['S6','H7','D8','C2','ZSCA','ZSC2','DA','D3']"),
 ("items:['S8','H5','VSH5','VSH3','VSD3','VSC4','VSC6','D9','C8','D10','C3']", "items:['S8','H5','VSH5','D9','C8','D10','C3']"),
 ("items:['S9','H10','D2','VSD4','VSH7','VSD6','VSC8','C6','SJ','H3']", "items:['S9','H10','D2','VSD4','C6','SJ','H3']"),
 ("items:['SQ','HJ','CJ','CQ','H6','VSSA','VSS5','VSDJ','J2']", "items:['SQ','HJ','CJ','CQ','H6','J2']"),
 ("items:['S10','SK','HK','DJ','C10','S4','VSS7','VSH10','VSCJ']", "items:['S10','SK','HK','DJ','C10','S4']"),
 ("items:['SA','S2','H9','C9','VSCK','VSS9','VSHK','J4']", "items:['SA','S2','H9','C9','VSCK','J4']"),
 ("items:['VSSQ','VSDK'],fields:['F5']", "items:[],fields:['F5']"),
 ("items:['S7B','D7B','H4B','C5B','VSSK','J5']", "items:['S7B','D7B','H4B','C5B','J5']"),
]
for old,new in reverts:
    if old not in text:
        raise SystemExit(f'missing expanded unlock fragment: {old}')
    text=text.replace(old,new,1)

marker="const UNLOCK_GROUPS=[\n"
vs_groups=""" {id:'vs1',label:'전체 1클리어 · V-SIGNAL',kind:'theme',when:p=>p.totalClears>=1,items:['VSHA','VSD2','VSCA'],fields:[]},
 {id:'vs2',label:'전체 2클리어 · V-SIGNAL',kind:'theme',when:p=>p.totalClears>=2,items:['VSH3','VSD3','VSC4','VSC6'],fields:[]},
 {id:'vs3',label:'전체 3클리어 · V-SIGNAL',kind:'theme',when:p=>p.totalClears>=3,items:['VSH7','VSD6','VSC8'],fields:[]},
 {id:'vs4',label:'전체 4클리어 · V-SIGNAL',kind:'theme',when:p=>p.totalClears>=4,items:['VSSA','VSS5','VSDJ'],fields:[]},
 {id:'vs5',label:'전체 5클리어 · V-SIGNAL',kind:'theme',when:p=>p.totalClears>=5,items:['VSS7','VSH10','VSCJ'],fields:[]},
 {id:'vs6',label:'전체 6클리어 · V-SIGNAL',kind:'theme',when:p=>p.totalClears>=6,items:['VSS9','VSHK'],fields:[]},
 {id:'vs7',label:'전체 7클리어 · V-SIGNAL',kind:'theme',when:p=>p.totalClears>=7,items:['VSSQ','VSDK'],fields:[]},
 {id:'vs8',label:'전체 8클리어 · V-SIGNAL',kind:'theme',when:p=>p.totalClears>=8,items:['VSSK'],fields:[]},
"""
if marker not in text:
    raise SystemExit('missing UNLOCK_GROUPS marker')
text=text.replace(marker,marker+vs_groups,1)
index.write_text(text,encoding='utf-8')

test=Path('tests/vsignal-full-pool.mjs')
t=test.read_text(encoding='utf-8')
needle="for(const id of Object.keys(expected))ok(unlockBlock.includes(`'${id}'`),`${id} is reachable through progression unlock groups`);"
extra=needle+"\nok(unlockBlock.includes(\"items:['S8','H5','VSH5','D9','C8','D10','C3']\"),'full-pool expansion preserves Encore legacy unlock timing');\nok(unlockBlock.includes(\"items:['S9','H10','D2','VSD4','C6','SJ','H3']\"),'full-pool expansion preserves Gather All legacy unlock timing');\nok(unlockBlock.includes(\"items:['SA','S2','H9','C9','VSCK','J4']\"),'full-pool expansion preserves Endurance legacy unlock timing');\nok(unlockBlock.includes(\"id:'vs8'\")&&unlockBlock.includes(\"items:['VSSK']\"),'new V-SIGNAL cards use dedicated progression groups');"
if needle not in t:
    raise SystemExit('missing V-SIGNAL unlock assertion anchor')
if 'full-pool expansion preserves Encore legacy unlock timing' not in t:
    t=t.replace(needle,extra,1)
test.write_text(t,encoding='utf-8')

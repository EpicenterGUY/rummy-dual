from pathlib import Path
import runpy

runpy.run_path('.github/scripts/vsignal-full-pool-patch-v4.py', run_name='__main__')

index=Path('index.html')
text=index.read_text(encoding='utf-8')
old="function handleVSignalFullThemeEvent(packet){\n if(!packet?.event)return false;"
new="function handleVSignalFullThemeEvent(packet){\n if(!packet?.event)return false;if(typeof sideObj!=='function'||typeof other!=='function')return false;"
if old not in text: raise SystemExit('missing V-SIGNAL event handler header')
text=text.replace(old,new,1)
index.write_text(text,encoding='utf-8')

test=Path('tests/vsignal-full-pool.mjs')
t=test.read_text(encoding='utf-8')
needle="ok(script.includes(\"typeof noteVSignalMeldKind==='function'?noteVSignalMeldKind(w,type):{before:false,both:false,completedPair:false}\"),'common resolver keeps isolated legacy tests compatible when V-SIGNAL helper is not loaded');"
extra=needle+"\nok(script.includes(\"if(!packet?.event)return false;if(typeof sideObj!=='function'||typeof other!=='function')return false\"),'V-SIGNAL passive subscriber preserves the isolated shared-event foundation');"
if needle in t and 'passive subscriber preserves the isolated shared-event foundation' not in t:
    t=t.replace(needle,extra,1)
test.write_text(t,encoding='utf-8')

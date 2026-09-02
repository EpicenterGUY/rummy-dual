from pathlib import Path
import runpy

runpy.run_path('.github/scripts/vsignal-full-pool-patch-v3.py', run_name='__main__')

index=Path('index.html')
text=index.read_text(encoding='utf-8')
old="vSignalAction=noteVSignalMeldKind(w,type);"
new="vSignalAction=typeof noteVSignalMeldKind==='function'?noteVSignalMeldKind(w,type):{before:false,both:false,completedPair:false};"
if old not in text: raise SystemExit('missing V-SIGNAL action helper call')
text=text.replace(old,new,1)
index.write_text(text,encoding='utf-8')

test=Path('tests/vsignal-full-pool.mjs')
t=test.read_text(encoding='utf-8')
needle="ok(script.includes('function noteVSignalMeldKind('),'SET/RUN cross-play is tracked without a new numeric resource');"
extra=needle+"\nok(script.includes(\"typeof noteVSignalMeldKind==='function'?noteVSignalMeldKind(w,type):{before:false,both:false,completedPair:false}\"),'common resolver keeps isolated legacy tests compatible when V-SIGNAL helper is not loaded');"
if needle in t and 'isolated legacy tests compatible' not in t:
    t=t.replace(needle,extra,1)
test.write_text(t,encoding='utf-8')

from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

before=s
s=s.replace(";emitEffectEvent(", ";if(typeof emitEffectEvent==='function')emitEffectEvent(")
s=s.replace(";emitRecoveryEvent(", ";if(typeof emitRecoveryEvent==='function')emitRecoveryEvent(")
s=s.replace("\n    emitEffectEvent(", "\n    if(typeof emitEffectEvent==='function')emitEffectEvent(")
s=s.replace("\n    emitRecoveryEvent(", "\n    if(typeof emitRecoveryEvent==='function')emitRecoveryEvent(")

if s==before:
    raise SystemExit('no event hook calls were guarded')

p.write_text(s,encoding='utf-8')

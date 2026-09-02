from pathlib import Path
import runpy

runpy.run_path('.github/scripts/zero-sight-full-pool-patch.py', run_name='__main__')

audit=Path('tests/named-card-audit.mjs')
text=audit.read_text(encoding='utf-8')
old="'zsBallistics','zsArmorPiercing','zsCounterTrace','zsLongShot','zsOneShot'"
new="'zsArmorPiercing','zsCounterTrace','zsLongShot','zsBallistics','zsOneShot'"
if old in text:
    text=text.replace(old,new,1)
elif new not in text:
    raise SystemExit('missing ZERO-SIGHT direct-power audit sequence')
audit.write_text(text,encoding='utf-8')

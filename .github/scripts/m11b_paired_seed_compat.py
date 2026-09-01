from pathlib import Path
p=Path('tests/m11b-dev-sandbox.mjs')
s=p.read_text()
old1="ok(source('restartCurrentCombat').includes(\"startM11BExperimentBattle(state.m11bExperimentCohort||'few')\"),'result replay preserves the current experiment cohort');"
new1="ok(source('restartCurrentCombat').includes(\"startM11BExperimentBattle(state.m11bExperimentCohort||'few',state.m11bExperimentSeed||currentM11BExperimentSeed())\"),'result replay preserves the current experiment cohort and paired deck seed');"
old2="ok(source('setupM11BExperimentBattle').includes(\"e.deck=makeM11BExperimentDeck('enemy','zero')\"),'experiment opponent always uses the zero-asymmetric control deck');"
new2="ok(source('setupM11BExperimentBattle').includes(\"e.deck=makeM11BExperimentDeck('enemy','zero',pairSeed)\"),'experiment opponent always uses the zero-asymmetric control deck under the same paired seed');"
for old,new,label in [(old1,new1,'restart assertion'),(old2,new2,'enemy seed assertion')]:
    if old in s:s=s.replace(old,new,1)
    elif new not in s:raise SystemExit(f'missing {label}')
p.write_text(s)
print('M11B sandbox regression updated for paired seed')

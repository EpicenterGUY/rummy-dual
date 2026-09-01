from pathlib import Path
p=Path('tests/m11a-roguelike-run-init.mjs')
s=p.read_text()
anchor="  vm.runInContext(\"const ROGUELIKE_RUN_DRAFT_KEY='rummyDuelRoguelikeRunDraftV1'; const ROGUELIKE_COMMON_START_ZONE='common-start'; const ROGUELIKE_STARTER_IDS=Object.freeze(['wanderer','collector','salvager','jester','pure']);\",ctx);\n"
insert=anchor+"  vm.runInContext(\"const ROGUELIKE_REWARD_ALGORITHM='action-tags-v1'; const ROGUELIKE_REWARD_ROLES=Object.freeze([{id:'reinforce',label:'현재 강화'},{id:'branch',label:'새 방향'},{id:'foundation',label:'기반 보강'}]);\",ctx);\n"
if insert not in s:
    if anchor not in s: raise SystemExit('m11a run-init isolation anchor missing')
    s=s.replace(anchor,insert,1)
p.write_text(s)
print('updated M11A run-init isolated context for reward algorithm constants')

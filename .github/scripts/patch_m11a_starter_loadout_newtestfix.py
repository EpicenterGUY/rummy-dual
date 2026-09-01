from pathlib import Path
p=Path(__file__).resolve().parents[2]/'tests'/'m11a-starter-loadouts.mjs'
s=p.read_text(encoding='utf-8')
old="for(const name of ['NAMED','CHARACTERS','TENDENCY_BY_TAG','ROGUELIKE_STARTER_IDS','ROGUELIKE_STARTER_REGULAR_SLOTS','ROGUELIKE_STARTER_DECK_SIZE','ROGUELIKE_STARTER_NAMED_REGULAR_COUNT','ROGUELIKE_STARTER_LOADOUTS'])vm.runInContext(declaration(name),ctx);"
new="for(const name of ['NAMED','CHARACTERS','TENDENCY_BY_TAG','ROGUELIKE_STARTER_IDS','ROGUELIKE_STARTER_REGULAR_SLOTS','ROGUELIKE_STARTER_LOADOUTS'])vm.runInContext(declaration(name),ctx);\nvm.runInContext('const ROGUELIKE_STARTER_DECK_SIZE=30; const ROGUELIKE_STARTER_NAMED_REGULAR_COUNT=6;',ctx);"
if old not in s: raise SystemExit('missing new test declaration loop anchor')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')

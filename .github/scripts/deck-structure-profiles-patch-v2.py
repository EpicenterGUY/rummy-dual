from pathlib import Path
import runpy

runpy.run_path('.github/scripts/deck-structure-profiles-patch.py', run_name='__main__')

test=Path('tests/deck-structure-profiles.mjs')
t=test.read_text(encoding='utf-8')
t=t.replace("ok(script.includes('id=\"deckStructureGrid\"')&&script.includes('[data-deck-structure]'),'battle setup exposes an independent structure picker');","ok(html.includes('id=\"deckStructureGrid\"')&&script.includes('[data-deck-structure]'),'battle setup exposes an independent structure picker');")
test.write_text(t,encoding='utf-8')

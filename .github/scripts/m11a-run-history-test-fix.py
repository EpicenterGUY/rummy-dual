from pathlib import Path

p = Path('tests/m11a-run-completion.mjs')
text = p.read_text(encoding='utf-8')
old = "assert.deepEqual(archived.regionPath,completed.regionPath);"
new = "assert.equal(JSON.stringify(archived.regionPath),JSON.stringify(completed.regionPath));"
if old not in text:
    raise SystemExit('missing cross-realm regionPath assertion target')
text = text.replace(old, new, 1)
p.write_text(text, encoding='utf-8')

from pathlib import Path

p = Path('index.html')
text = p.read_text(encoding='utf-8')
old = "const draft=loadRoguelikeRunDraft();if(draft?.status==='completed')roguelikeArchiveCompletedRun(draft);const route=typeof roguelikeBattleProgress==='function'?"
new = "const draft=loadRoguelikeRunDraft();if(draft?.status==='completed'&&typeof roguelikeArchiveCompletedRun==='function')roguelikeArchiveCompletedRun(draft);const route=typeof roguelikeBattleProgress==='function'?"
if old not in text:
    raise SystemExit('missing archive completion guard target')
text = text.replace(old, new, 1)
old = "if(typeof renderRoguelikeRegionPicker==='function')renderRoguelikeRegionPicker(draft);if(status){status.innerHTML=roguelikeRunDraftText(draft);const archive=loadRoguelikeRunHistory();if(archive.entries.length&&draft?.status!=='completed')status.innerHTML+=`<br>${roguelikeRunArchiveText()}`;}if(prepare)"
new = "if(typeof renderRoguelikeRegionPicker==='function')renderRoguelikeRegionPicker(draft);if(status){status.innerHTML=roguelikeRunDraftText(draft);if(typeof loadRoguelikeRunHistory==='function'&&typeof roguelikeRunArchiveText==='function'){const archive=loadRoguelikeRunHistory();if(archive.entries.length&&draft?.status!=='completed')status.innerHTML+=`<br>${roguelikeRunArchiveText()}`;}}if(prepare)"
if old not in text:
    raise SystemExit('missing active archive summary guard target')
text = text.replace(old, new, 1)
p.write_text(text, encoding='utf-8')

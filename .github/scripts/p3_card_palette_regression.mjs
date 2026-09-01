import fs from 'node:fs';
const html=fs.readFileSync('index.html','utf8');
const road=fs.readFileSync('ROADMAP.md','utf8');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}

ok(html.includes('/* UI3 P3 · card surface / named frame palette */'),'P3 card palette block exists');
ok(html.includes('--card-paper:#f1eadf')&&html.includes('--card-named:#9f875f')&&html.includes('--card-red:#b95f64'),'card surfaces derive from the restrained paper/brass/red palette');
ok(html.includes('.centerSuit:not(.suitRed){color:#30383a}.suitRed{color:var(--card-red)}'),'black/red suit glyphs use the unified tabletop palette');
ok(html.includes('.card.named{border-color:#766951')&&html.includes('.card.named:before{border-color:var(--card-named)}'),'named cards use a distinct warm double-frame treatment');
const legacyMarker=html.lastIndexOf('.named:after{content:"N"');
const p3Marker=html.lastIndexOf('.named:after{content:"◆"');
ok(p3Marker>=0&&p3Marker>legacyMarker,'named identity final CSS override uses a visual brass diamond instead of the legacy N badge');
ok(html.includes('background:#b79d6b;color:#273034')&&html.includes('border:1px solid #75684f'),'named diamond uses brass/ink colors from the tactical tabletop language');
ok(html.includes('.meldMiniCard .named:after,.codexMini .named:after{right:3px;top:3px;min-width:10px;width:10px;height:10px'),'named marker scales down consistently on public-meld and codex mini cards');
ok(html.includes('.joker .centerSuit{color:#746f83}'),'Joker glyph uses the muted UI violet rather than the legacy saturated purple');
ok(html.includes('.cardBtn.selected .card{outline-color:#6f9690}')&&html.includes('.cardBtn.attachable:not(.selected) .card{outline-color:#7f9683}'),'card selection/attach cues match tactical teal/green accents');
ok(road.includes('- [x] 카드 아이콘/네임드 프레임과 새 UI 팔레트 통일'),'ROADMAP marks P3 card palette unification complete');
console.log('P3 card surface/named-frame palette regression passed.');

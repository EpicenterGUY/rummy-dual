import fs from 'node:fs';

const html = fs.readFileSync(new URL('../index.html', import.meta.url), 'utf8');
const script = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).join('\n');

function ok(condition, message) {
  if (!condition) throw new Error(message);
  console.log(`PASS: ${message}`);
}

new Function(script);

ok(html.includes('UI2 P2 · HUD hierarchy and density'), 'UI2 P2 HUD hierarchy block exists');
ok(html.includes('<details id="hudMenu" class="hudMenu">'), 'battle header collapses secondary navigation into one menu');
ok(html.includes('<summary class="pixelBtn hudMenuBtn">메뉴</summary>'), 'compact HUD menu has one clear entry point');
ok(html.includes('.coreBreakNote{display:none'), 'repeated no-pierce helper copy is removed from the always-visible HUD');
ok(html.includes('.initiativeLabel{display:none') && html.includes('.strongAttackBtn{display:none!important'), 'SWITCH board keeps only primary state, warning and core margin visible');
ok(html.includes('.meldSide{min-height:82px') && html.includes('.hand{min-height:138px'), 'meld and hand zones use tighter vertical rhythm');
ok(html.includes('세트·런을 만들거나 공개 조합에 붙여 스위치를 넘기세요.'), 'hand helper copy is reduced to one actionable sentence');
ok(html.includes('<details class="log pixel"><summary><span>전투 기록</span><small>필요할 때 펼치기</small></summary>'), 'combat log is a compact collapsed disclosure by default');
ok(html.includes('.log>summary{') && html.includes('.log>div{max-height:128px'), 'combat log gets compact summary and bounded expanded content');
ok(html.includes('.cardBtn.selected .card{outline:2px solid') && html.includes('.cardBtn.attachable:not(.selected) .card{outline:2px solid'), 'card affordances use outlines and position rather than glow');
ok(html.includes('.meldEntry.target{outline:2px solid') && html.includes('.meldMiniCard.boardPick .card{outline:2px solid'), 'meld targeting uses outline hierarchy instead of glow');
ok(html.includes("document.querySelectorAll('#hudMenu button').forEach"), 'HUD menu closes after choosing a destination');
ok(html.includes('@media(max-width:370px)') && html.includes('#charBadge{max-width:112px'), 'narrow-phone header fallback is explicitly covered');

console.log('RUMMY//DUEL UI2 HUD hierarchy regressions passed.');

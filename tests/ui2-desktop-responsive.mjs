import fs from 'node:fs';

const html = fs.readFileSync(new URL('../index.html', import.meta.url), 'utf8');
const road = fs.readFileSync(new URL('../ROADMAP.md', import.meta.url), 'utf8');

function ok(condition, message) {
  if (!condition) throw new Error(message);
  console.log(`PASS: ${message}`);
}

ok(html.includes('/* UI2 · desktop / tablet responsive battlefield */'), 'desktop responsive battlefield block exists');
ok(html.includes('@media (min-width:900px)') && html.includes('@media (min-width:1200px)'), 'tablet and desktop breakpoints are explicit');
ok(html.includes('#app{width:min(100vw,1440px)') && html.includes('#app:before{max-width:1440px'), 'desktop app shell expands beyond the mobile 480px cap with a bounded wide canvas');
ok(html.includes('grid-template-areas:') && html.includes('"enemy switch detail"') && html.includes('"arena meld detail"'), 'wide desktop battlefield uses a three-column tactical layout');
ok(html.includes('.status{grid-area:status}') && html.includes('.initiativeBoard{grid-area:switch}') && html.includes('.arena{grid-area:arena}') && html.includes('.meldZone{grid-area:meld}') && html.includes('.handZone{grid-area:hand}') && html.includes('.detail{grid-area:detail}') && html.includes('.log{grid-area:log}'), 'major battle regions receive stable desktop grid areas');
ok(html.includes('.meldRows{display:grid;grid-template-columns:repeat(2,minmax(0,1fr))'), 'public meld boards become side-by-side on wider screens');
ok(html.includes('.controls{grid-template-columns:repeat(3,minmax(0,1fr))') && html.includes('.controls{grid-template-columns:repeat(6,minmax(0,1fr))'), 'action controls scale from tablet three-column to desktop six-column rows');
ok(html.includes('.backRow .cardBack{width:34px;height:49px') && html.includes('.backRow .cardBack:nth-child(n+7){display:block}'), 'desktop restores readable opponent card backs instead of mobile compression');
ok(html.includes('.startScreen{width:100vw') && html.includes('.startShell{width:min(100%,520px)'), 'desktop start screen is no longer trapped in the 480px mobile shell');
ok(html.includes('@media (max-width:899px)') && html.includes('#app{width:min(100vw,480px)}'), 'mobile layout remains explicitly capped at 480px');
ok(road.includes('### P2.5 — 데스크톱 / 태블릿 반응형') && road.includes('1200px 이상 3열 전술 테이블'), 'roadmap records the desktop responsive pass');

console.log('RUMMY//DUEL desktop responsive layout regressions passed.');

import fs from 'node:fs';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
ok(html.includes('/* UI2 · desktop fullscreen / Korean readability / no page scroll */'),'desktop fullscreen/readability pass is registered');
ok(html.includes('"Pretendard Variable","Pretendard","Noto Sans KR","Apple SD Gothic Neo","Malgun Gothic","Segoe UI",sans-serif'),'desktop uses a Korean-readable native sans-serif fallback stack without external font assets');
ok(html.includes('@media (min-width:1200px){')&&html.includes('html,body{width:100%;height:100%;min-height:100%;overflow:hidden}'),'desktop viewport disables body/page scrolling');
ok(html.includes('#app{width:100vw;max-width:none;height:100dvh;min-height:0;overflow:hidden;border:0;border-radius:0;box-shadow:none}'),'desktop app fills the viewport instead of keeping the 1440px shell cap');
ok(html.includes('grid-template-areas:"status status status" "enemy switch detail" "arena meld detail" "hand hand hand" "log log log"'),'desktop grid removes tutorial/practice rows from battle flow');
ok(html.includes('.tutorialCoach,.practiceCoach{position:fixed'),'tutorial and practice coaches float on desktop instead of forcing page height growth');
ok(html.includes('.handZone{height:100%;min-height:0;display:flex;flex-direction:column;overflow:hidden')&&html.includes('.hand{flex:1 1 auto;min-height:0;height:auto'),'hand area is height-contained inside the desktop viewport');
ok(html.includes('details.log[open]{position:fixed')&&html.includes('max-height:42dvh'),'expanded combat log becomes an internal floating panel instead of growing the page');
ok(html.includes('.detail{position:static;height:100%;min-height:0;overflow:auto'),'long card details scroll internally rather than the entire page');
ok(html.includes('.controls .pixelBtn{font-size:12px')&&html.includes('.detailText{font-size:12px')&&html.includes('.handTitle{font-size:14px'),'desktop HUD/action/body text is materially larger than the mobile pixel-scale baseline');
ok(html.includes('@media (min-width:1200px) and (max-height:760px){')&&html.includes('grid-template-rows:52px minmax(100px,18vh) minmax(118px,1fr) 190px 28px'),'short desktop viewports receive a dedicated no-scroll compact grid');
ok(html.includes('@media (max-width:899px){#app{width:min(100vw,480px)}'),'mobile 480px layout contract remains present');
ok(road.includes('`100vw × 100dvh` 전체 전장')&&road.includes('PC 전용 한국어 산세리프 폰트 스택')&&road.includes('body/page 스크롤 제거'),'roadmap records fullscreen, font, and no-page-scroll desktop work');
console.log('RUMMY//DUEL desktop fullscreen/readability regressions passed.');

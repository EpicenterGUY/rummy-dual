import fs from 'node:fs';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}

ok(html.includes('/* UI3 P3 · restrained theme accent layer */'),'restrained P3 theme accent block exists');
ok(html.includes('startScreen.dataset.theme=themeId'),'start screen exposes the selected theme as a presentation-only data hook');
ok(html.includes("if(app)app.dataset.theme=p.themeId||'mixed'"),'battle app exposes the selected theme as a presentation-only data hook');
ok(html.includes('data-theme-card="${id}"'),'theme picker entries expose exact theme identity for accent styling');
ok(html.includes("themeClass=c.themeId?`theme-${c.themeId}`:''"),'card renderer exposes exact theme identity without changing card semantics');
ok(html.includes('--theme-vsignal:#8b7788')&&html.includes('--theme-zero:#718892')&&html.includes('--theme-pointblank:#927565'),'three theme points use muted non-neon colors');
ok(html.includes('#themeGroupGrid .charCard[data-theme-card="v-signal"]{border-left-color:var(--theme-vsignal)}'),'V-SIGNAL is limited to a theme-card accent edge');
ok(html.includes('#app[data-theme="zero-sight"] #charBadge{border-color:#60747c}'),'ZERO-SIGHT battle identity is limited to the existing HUD badge');
ok(html.includes('.card.theme-point-blank.named:after{background:var(--theme-pointblank)'),'POINT-BLANK theme identity is limited to the existing named-card diamond marker');
const block=html.slice(html.indexOf('/* UI3 P3 · restrained theme accent layer */'),html.indexOf('</style>',html.indexOf('/* UI3 P3 · restrained theme accent layer */')));
ok(!/text-shadow|filter:|animation:|box-shadow/.test(block),'theme-specific layer introduces no glow, filter, animation, or special shadow');
ok(!/#app\[data-theme=[^\]]+\]\s*\{[^}]*background/.test(block)&&!/.startScreen\[data-theme=[^\]]+\]\s*\{[^}]*background/.test(block),'theme layer does not replace the common page/battle background');
ok(road.includes('- [x] V-SIGNAL 등 테마군은 기본 UI 위에 테마 포인트만 얹고 카지노형 네온 남발 금지'),'ROADMAP marks restrained theme-accent policy complete');
console.log('P3 restrained theme accent regression passed.');

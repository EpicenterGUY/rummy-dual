import fs from 'node:fs';
const html=fs.readFileSync('index.html','utf8');
const road=fs.readFileSync('ROADMAP.md','utf8');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}

ok(html.includes('/* UI3 P3 · start/result/codex visual language */'),'P3 start/result/codex visual block exists');
ok(html.includes('.startHero:after{content:""')&&html.includes('background:linear-gradient(90deg,transparent,#9f875f 25%,#6f9690 75%,transparent)'),'start hero bridges paper/brass and tactical teal accents');
ok(html.includes('.startMenuBtn{border-color:#46555a;background:#2c373c')&&html.includes('border-left:4px solid #59676b'),'start menu uses restrained slate action cards');
ok(html.includes('.startMenuBtn .menuState{padding:3px 6px;border:1px solid #75684f;border-radius:999px;background:#332f27;color:#dec99f}'),'start-menu state is a compact brass information chip');
ok(html.includes('#overlay .modal{border:1px solid #59666b;border-radius:14px;background:#273238'),'result dialog uses the tactical slate modal language');
ok(html.includes('#resultTitle{margin:0 0 10px;padding:0 0 8px;border-bottom:1px solid #566267;font-size:22px'),'result title has explicit report hierarchy');
ok(html.includes('#circulationSummary{margin:10px 0 0;padding:8px 9px;border:1px solid #455257;border-radius:8px;background:#20292d'),'result telemetry is visually secondary but readable');
ok(html.includes('#resultUnlocks{margin-top:9px;padding:9px;border:1px solid #75684f;border-radius:8px;background:#332f27'),'new unlocks use restrained warm/brass emphasis');
ok(html.includes('.codexModal{border:1px solid #59666b!important;border-radius:14px;background:#242f34!important'),'codex shell matches result/tactical panel language');
ok(html.includes('.codexTabs .active{background:#36524f;border-color:#6f9690;box-shadow:none;color:#e4f0ed}'),'codex active tab uses tactical teal instead of legacy neon inset');
ok(html.includes('.codexEntry{border-color:#445258;background:#29343a;border-radius:8px}')&&html.includes('.codexEntry.locked{background:#20282c;color:#7f8a8b}'),'codex entries share slate surfaces with a subdued locked state');
ok(html.includes('.codexFieldIcon{border:1px solid #75684f;background:#332f27;box-shadow:none;color:#e0cda6}'),'field cards use warm brass instead of saturated purple');
ok(html.includes('@media(max-width:390px){#resultTitle{font-size:19px}#overlay .modal{padding:11px}.codexModal{border-radius:10px}.startMenuBtn{border-left-width:3px}}'),'P3 shell visuals retain a mobile-specific compact finish');
ok(road.includes('- [x] 시작창/결과창/도감의 시각 언어 통일'),'ROADMAP marks P3 shell visual unification complete');
console.log('P3 start/result/codex visual regression passed.');

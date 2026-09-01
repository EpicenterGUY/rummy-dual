import fs from 'node:fs';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}

ok(html.includes('/* UI3 P3 · tutorial tactical-board finish */'),'P3 tutorial tactical-board block exists');
ok(html.includes('.tutorialCoach{position:relative;border:1px solid #56666a!important;border-left:4px solid #6f9690!important'),'tutorial coach uses a restrained teal tactical-board edge');
ok(html.includes('.tutorialCoachHead{padding-bottom:6px;border-bottom:1px solid #445258;margin-bottom:7px}'),'tutorial header has clear low-contrast board hierarchy');
ok(html.includes('.tutorialCoachHead .badge{border:1px solid #5d7774;border-radius:999px;background:#31423f;box-shadow:none'),'tutorial step badge drops pixel/neon styling');
ok(html.includes('.tutorialCoachHint{border:1px solid #4a5c60!important;border-left:3px solid #8d8065!important'),'hint panel uses a muted brass annotation edge');
ok(html.includes('.tutorialCoachActions .pixelBtn{border-color:#46555a;background:#303b40;box-shadow:none}'),'tutorial actions use flat slate tactical buttons');
ok(html.includes('.tutorialCoachActions .pixelBtn.primary{border-color:#587a76;background:#36514e}'),'primary tutorial action uses restrained teal emphasis');
ok(html.includes('.tutorialCoach.tutorialSuccessPulse{border-left-color:#86aa8d!important;background:#293a35!important}'),'tutorial success state uses subdued green feedback');
ok(html.includes('.practiceCoach{border:1px solid #536360!important;border-left:3px solid #76938e!important'),'practice coach shares the same tactical-board language');
ok(html.includes('.tutorialTarget{outline:2px solid #7fa09a!important;outline-offset:2px!important;filter:none!important}'),'tutorial target highlight uses an outline instead of neon filtering');
ok(html.includes('.pixelBtn.tutorialTarget{border-color:#78958e!important;background:#3c514c!important;box-shadow:none!important}'),'tutorial button target remains clear without pixel glow');
ok(html.includes('@media(max-width:390px){.tutorialCoach{border-left-width:3px!important;border-radius:8px}'),'tutorial finish retains a mobile compact rule');
ok(road.includes('- [x] 튜토리얼 coach를 동일한 전술 보드 톤으로 최종 마감'),'ROADMAP marks tutorial tactical-board finish complete');
console.log('P3 tutorial tactical-board regression passed.');

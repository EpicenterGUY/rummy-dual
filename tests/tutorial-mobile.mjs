import fs from 'node:fs';

const html = fs.readFileSync(new URL('../index.html', import.meta.url), 'utf8');
const roadmap = fs.readFileSync(new URL('../ROADMAP.md', import.meta.url), 'utf8');

function ok(condition, message) {
  if (!condition) throw new Error(message);
  console.log(`PASS: ${message}`);
}

ok(html.includes('width:min(100vw,480px)') && html.includes('viewport-fit=cover'), 'mobile shell is bounded at 480px and respects safe-area viewport fitting');
ok(html.includes('button,.cardBtn,.pileVisual,.attachHereBtn,.meldMiniCard{touch-action:manipulation}'), 'primary battle and tutorial interactive surfaces use manipulation touch behavior');
ok(html.includes('/* UX1 P2 · tutorial mobile flow safety */'), 'dedicated onboarding mobile fallback block exists');
ok(/@media\(max-width:390px\)\{\.tutorialCoach\{padding:8px\}[\s\S]*?\.tutorialCoachActions\{display:grid;grid-template-columns:minmax\(0,1fr\) minmax\(0,1fr\);gap:6px\}/.test(html), '390px tutorial actions use a bounded two-column grid');
ok(/@media\(max-width:370px\)\{\.tutorialCoachActions\{grid-template-columns:1fr\}/.test(html), '370px tutorial actions fall back to one column');
ok(html.includes('.tutorialCoachActions .pixelBtn{min-width:0;min-height:42px') && html.includes('.startAux .pixelBtn{min-height:40px}'), 'small-screen onboarding buttons preserve practical touch heights');
ok(html.includes('.tutorialCoachGoal,.tutorialCoachHint{overflow-wrap:anywhere;word-break:keep-all}') && html.includes('white-space:normal') && html.includes('overflow-wrap:anywhere'), 'long Korean coach/button copy can wrap instead of clipping');
ok(roadmap.includes('- [x] 모바일 가독성 및 터치 정적 회귀') && roadmap.includes('- [x] 390px 이하 한국어 버튼/가이드 잘림 회귀 테스트'), 'UX1 P2 roadmap records automated mobile text/touch coverage');

console.log('RUMMY//DUEL onboarding mobile regressions passed.');

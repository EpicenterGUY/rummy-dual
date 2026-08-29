import fs from 'node:fs';

const html = fs.readFileSync(new URL('../index.html', import.meta.url), 'utf8');

function ok(condition, message) {
  if (!condition) throw new Error(message);
  console.log(`PASS: ${message}`);
}

new Function([...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).join('\n'));

ok(html.includes('id="switchAlert"'), 'central SWITCH board has a dedicated alert line');
ok(html.includes('내 턴 종료 시 DETONATE'), 'player-facing imminent DETONATE warning is explicit');
ok(html.includes('CPU 턴 종료 시 DETONATE'), 'enemy-facing imminent DETONATE warning is explicit');
ok(html.includes('CORE까지'), 'SWITCH board reports remaining CORE lethal margin');
ok(html.includes("phaseEl.classList.toggle('detonateRisk'"), 'main phase strip receives imminent DETONATE danger state');
ok(html.includes('BURST READY · 4번째 카드 +24 · SWITCH 반환'), 'SET readout states BURST power and SWITCH return');
ok(html.includes(' · NEXT +${chainDamage((m.chain||0)+1)} · SWITCH 반환'), 'RUN readout prominently states next CHAIN power and SWITCH return');
ok(html.includes('OVERKILL ${overkill} LOST · NO PIERCE'), 'CORE BREAK explicitly labels overkill as lost and non-piercing');
ok(html.includes('초과 피해 LOST · 다음 CORE 관통 0'), 'persistent CORE note communicates no-pierce loss');
ok(html.includes('.switchAlert.imminent'), 'imminent DETONATE alert has dedicated visual hierarchy');
ok(html.includes('.phaseText.detonateRisk'), 'phase strip has dedicated danger styling');

console.log('RUMMY//DUEL combat readability regressions passed.');

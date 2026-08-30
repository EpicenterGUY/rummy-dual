import fs from 'node:fs';

const html = fs.readFileSync(new URL('../index.html', import.meta.url), 'utf8');

function ok(condition, message) {
  if (!condition) throw new Error(message);
  console.log(`PASS: ${message}`);
}

new Function([...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).join('\n'));

ok(html.includes('id="switchAlert"'), 'central SWITCH board has a dedicated alert line');
ok(html.includes('내 턴 종료 시 폭발'), 'player-facing imminent DETONATE warning is explicit');
ok(html.includes('상대 턴 종료 시 폭발'), 'enemy-facing imminent DETONATE warning is explicit');
ok(html.includes('코어까지'), 'SWITCH board reports remaining CORE lethal margin');
ok(html.includes("phaseEl.classList.toggle('detonateRisk'"), 'main phase strip receives imminent DETONATE danger state');
ok(html.includes('버스트 준비 · 4번째 카드 +24 · 스위치 반환'), 'SET readout states BURST power and SWITCH return');
ok(html.includes(' · 다음 +${chainDamage((m.chain||0)+1)} · 스위치 반환'), 'RUN readout prominently states next CHAIN power and SWITCH return');
ok(html.includes('초과 피해 ${overkill} 소멸 · 관통 없음'), 'CORE BREAK explicitly labels overkill as lost and non-piercing');
ok(html.includes('초과 피해 소멸 · 다음 코어 관통 없음'), 'persistent CORE note communicates no-pierce loss');
ok(html.includes('.switchAlert.imminent'), 'imminent DETONATE alert has dedicated visual hierarchy');
ok(html.includes('.phaseText.detonateRisk'), 'phase strip has dedicated danger styling');

console.log('RUMMY//DUEL combat readability regressions passed.');

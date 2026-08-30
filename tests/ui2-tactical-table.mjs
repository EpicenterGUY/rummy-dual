import fs from 'node:fs';

const html = fs.readFileSync(new URL('../index.html', import.meta.url), 'utf8');
const script = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).join('\n');

function ok(condition, message) {
  if (!condition) throw new Error(message);
  console.log(`PASS: ${message}`);
}

new Function(script);

ok(html.includes('UI2 · tactical tabletop visual reset'), 'tactical tabletop visual reset block exists');
ok(html.includes('<meta name="theme-color" content="#20282d">'), 'browser theme color uses muted slate instead of casino-black');
ok(html.includes('--ui2-surface:#273238') && html.includes('--ui2-paper:#eee8dc'), 'muted slate and paper palette tokens exist');
ok(html.includes('.pixel{border:1px solid var(--ui2-edge);border-radius:10px'), 'generic panels use softer app-card framing');
ok(html.includes('.pixelBtn{border:1px solid #283239;border-radius:8px;background:#344047'), 'buttons use flat neutral tactical styling');
ok(html.includes('.pixelBtn.goldBtn{background:#3b4042') && html.includes('border-color:#8b7d63'), 'gold action is an understated outline accent rather than casino gold fill');
ok(html.includes('.startHero{background:var(--ui2-paper);color:#263038'), 'start hero is paper-like instead of neon casino panel');
ok(html.includes('.initiativeBoard{background:#222d32'), 'switch board reads as a tactical status board');
ok(html.includes('.switchBoard.playerLead .playerSide,.switchBoard.enemyLead .enemySide{animation:none'), 'normal SWITCH ownership no longer pulses continuously');
ok(html.includes('.switchBoard.lethal{animation:none'), 'lethal state uses clear static warning instead of jackpot-like pulsing');
ok(html.includes('.switchGauge i{background:#6f9690'), 'default SWITCH gauge is single restrained accent');
ok(html.includes('.switchBoard.danger .switchGauge i{background:#aa9164') && html.includes('.switchBoard.critical .switchGauge i,.switchBoard.overload .switchGauge i,.switchBoard.lethal .switchGauge i{background:#b86469'), 'gauge color escalates only with actual danger');
ok(html.includes('.card{box-shadow:0 0 0 1px #b2a58d inset'), 'playing cards use quieter paper framing');
ok(html.includes('@media (prefers-reduced-motion:reduce)'), 'reduced-motion visual safety is included');

console.log('RUMMY//DUEL UI2 tactical tabletop regressions passed.');

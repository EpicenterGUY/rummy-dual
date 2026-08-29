import fs from 'node:fs';

const html = fs.readFileSync(new URL('../index.html', import.meta.url), 'utf8');

function ok(condition, message) {
  if (!condition) throw new Error(message);
  console.log(`PASS: ${message}`);
}

new Function([...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).join('\n'));

ok(!html.includes('MAX_SHIELD'), 'shield has no hidden 40-point hard cap');
ok(!html.includes('Math.min(MAX_SHIELD'), 'shield gain is not silently clamped');
ok(!html.includes('runRetireAvailable'), 'legacy RUN-retire turn state is removed');
ok(!html.includes('function staleRunAge('), 'legacy stale-RUN age rule is removed');
ok(!html.includes('function canRetireStaleRun('), 'legacy stale-RUN retire eligibility is removed');
ok(!html.includes('function playerRetireStaleRun('), 'legacy player RUN-retire action is removed');
ok(!html.includes('function retireStaleRunAI('), 'legacy AI RUN-retire action is removed');
ok(!html.includes('function playerRetireMeld('), 'legacy free meld-retire action stub is removed');
ok(!html.includes('data-stale-retire'), 'legacy RUN-retire UI hook is removed');
ok(!html.includes('data-retire-index'), 'legacy free meld-retire UI hook is removed');
ok(!html.includes('pendingDrawChoices') && !html.includes('pendingDrawLook'), 'legacy multi-card deck-look state is removed');
for (const name of ['basicDrawLook','takeDeckChoices','commitDeckChoice','closeDrawChoice','choosePlayerDeckCard','renderDrawChoice','startPlayerDeckChoice','aiBasicDeckDraw']) {
  ok(!html.includes(`function ${name}(`), `legacy draw-preview helper ${name} is removed`);
}
ok(!html.includes('playerJustRummied') && !html.includes('enemyJustRummied'), 'obsolete generic post-RUMMY flags are removed in favor of event windows');
ok(html.includes("F6:{name:'회전교차로'") && html.includes('반환 재사용 제한은 그대로 적용'), 'Roundabout text explicitly preserves the recovered-card return guard');

console.log('RUMMY//DUEL final base-rule audit tests passed.');

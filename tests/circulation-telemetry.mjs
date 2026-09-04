import fs from 'node:fs';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
ok(html.includes('id="circulationSummary"'),'result overlay exposes circulation summary');
ok(html.includes('function blankCirculationStats()')&&html.includes('function getCirculationStats()')&&html.includes('function circulationSideStats(w)')&&html.includes('function circulationStatsSnapshot()')&&html.includes('function circulationSummaryText()'),'circulation telemetry keeps total, per-side and snapshot helpers');
ok(html.includes("typeof recordCirculationTurn==='function')recordCirculationTurn(w)"),'turn-end sampling is optional for extracted-function tests');
ok(html.includes("recordCirculationCounter('player','lowSkips')")&&html.includes("recordCirculationCounter('enemy','lowSkips')"),'low-hand protection usage keeps player/enemy identity');
ok(html.includes("recordCirculationCounter(w,'rummys')"),'RUMMY usage is counted for the acting side');
ok(html.includes("recordCirculationCounter(w,'maintenance')"),'maintenance usage is counted for the acting side');
ok(html.includes("typeof getCirculationStats==='function')getCirculationStats().fullRecirculations++"),'full recirculation usage is counted');
ok(html.includes("showResult(win){if(typeof renderCirculationSummary==='function')renderCirculationSummary();")&&html.includes("showCirculationDraw(){if(typeof renderCirculationSummary==='function')renderCirculationSummary();"),'normal and deadlock results render the metrics');
ok(road.includes('per-battle circulation telemetry'),'M4 records live circulation telemetry complete');
ok(road.includes('- [x] Structure / circulation cohort telemetry'),'M12 records persisted per-side circulation cohort telemetry');
console.log('Circulation telemetry regression passed.');

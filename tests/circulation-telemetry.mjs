import fs from 'node:fs';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
ok(html.includes('id="circulationSummary"'),'result overlay exposes circulation summary');
ok(html.includes('function getCirculationStats()')&&html.includes('function circulationSummaryText()'),'circulation telemetry helpers exist');
ok(html.includes("typeof recordCirculationTurn==='function')recordCirculationTurn(w)"),'turn-end sampling is optional for extracted-function tests');
ok(html.includes("typeof getCirculationStats==='function')getCirculationStats().lowSkips++"),'low-hand protection usage is counted without adding a hard dependency');
ok(html.includes("typeof getCirculationStats==='function')getCirculationStats().rummys++"),'RUMMY usage is counted for either side');
ok(html.includes("typeof getCirculationStats==='function')getCirculationStats().maintenance++"),'maintenance usage is counted');
ok(html.includes("typeof getCirculationStats==='function')getCirculationStats().fullRecirculations++"),'full recirculation usage is counted');
ok(html.includes("showResult(win){if(typeof renderCirculationSummary==='function')renderCirculationSummary();")&&html.includes("showCirculationDraw(){if(typeof renderCirculationSummary==='function')renderCirculationSummary();"),'normal and deadlock results render the metrics');
ok(road.includes('per-battle circulation telemetry'),'M4 records live circulation telemetry complete');
console.log('Circulation telemetry regression passed.');

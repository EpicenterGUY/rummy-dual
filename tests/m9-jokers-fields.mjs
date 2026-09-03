import fs from 'node:fs';

const html = fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const road = fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');

function ok(condition, message) {
  if (!condition) throw new Error(message);
  console.log(`PASS: ${message}`);
}

new Function([...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).join('\n'));

for (const [id, tag] of [
  ['J1','jokerKing'],['J2','jokerLast'],['J3','jokerDual'],['J4','vacancyJoker'],['J5','rebelJoker']
]) {
  ok(new RegExp(`'${id}':\\{[^\\n]*t:'${tag}'`).test(html), `${id} keeps distinct Joker identity ${tag}`);
}

const retireMeldBlock = html.match(/function retireMeld\([\s\S]*?\nfunction recoveredCardCanReturn/)?.[0] || '';
ok(
  /if\(c\.tag==='jokerKing'\)\{[\s\S]*?const home=c\.originOwner\|\|c\.owner;c\.owner=home;[\s\S]*?sideObj\(home\)\.deck\.unshift\(c\)[\s\S]*?\}else if\(c\.tag==='flexSuit'/.test(retireMeldBlock),
  'Joker King retirement restores origin owner and returns to owner deck instead of spent'
);
ok(
  retireMeldBlock.includes('const home=c.originOwner||c.owner') && retireMeldBlock.includes('sideObj(home).deck.unshift(c)'),
  'discard-control changes cannot steal Joker King permanently'
);

const fieldsBlock = html.match(/const FIELDS=\{([\s\S]*?)\n\};\nconst STARTER_NAMED=/)?.[1] || '';
const fieldIds = [...fieldsBlock.matchAll(/\bF(\d+):\{/g)].map(m => Number(m[1]));
ok(fieldIds.length === 10, 'shared field pool contains exactly 10 stabilized fields');
ok(fieldIds.every((n,i)=>n===i+1), 'shared field IDs are contiguous F1-F10');

ok(html.includes("F9:{name:'교차 선로'") && html.includes("tag:'crossLane'"), 'Cross Lane field is defined');
ok(html.includes("crossLane=state.field?.tag==='crossLane'") && html.includes('if(offSuit>((bridge||crossLane)?1:0))return false'), 'Cross Lane grants at most one off-suit RUN slot and does not stack above one');

ok(html.includes("F10:{name:'환승 터미널'") && html.includes("tag:'crossTraffic'"), 'Cross Traffic field is defined');
ok(html.includes("state.field.tag==='crossTraffic'&&ctx.isAttach&&ctx.targetOwner===other(w)&&!s.flags.crossTraffic"), 'Cross Traffic triggers only on first opponent-meld attach');
ok(html.includes('s.flags.crossTraffic=true;cycleOldestHandCard(w,cards)'), 'Cross Traffic cycles a remaining hand card');
ok(html.includes('crossTraffic:false'), 'Cross Traffic has turn-reset state');

ok(html.includes("id:'g10'") && html.includes("fields:['F9']"), 'F9 unlocks at 10 clears');
ok(html.includes("id:'g11'") && html.includes("fields:['F10']"), 'F10 unlocks at 11 clears');

for (const line of [
  '- [x] Finalize distinct Joker identities',
  '- [x] Audit Joker King return-to-owner-deck behavior',
  '- [x] Stabilize 10 behavior-changing shared fields'
]) ok(road.includes(line), `ROADMAP locks M9 item: ${line.slice(6)}`);

console.log('RUMMY//DUEL M9 Joker/field regression tests passed.');

import fs from 'node:fs';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {makeGame} from './helpers/live-game.mjs';
const p=JSON.parse(fs.readFileSync(new URL('../design/cards-v3.json',import.meta.url),'utf8')),g=makeGame();
assert.deepEqual(p.existingCards.map(r=>r.id).sort(),Object.keys(g.NAMED).sort(),'Every runtime card has one explicit design row');
assert.equal(new Set([...p.existingCards,...p.newThemeCards].map(r=>r.id)).size,146);
assert.equal(p.existingCards.filter(r=>r.implementation==='preserved').length,53);
assert.equal(p.existingCards.filter(r=>r.implementation==='implemented-wave2').length,16);
assert.equal(p.existingCards.filter(r=>r.implementation==='implemented-wave3').length,17);
assert.equal(p.existingCards.filter(r=>r.implementation==='planned').length,21);
assert.equal(p.existingCards.filter(r=>r.implementation==='implemented-wave4').length,8);
for(const r of p.existingCards){
 const c=g.NAMED[r.id];assert.equal(r.slot,c.slot||r.id);assert.equal(r.name,c.n);
 if(!['common','joker'].includes(r.theme))assert.equal(c.themeId,r.theme,`${r.id}: preserve theme identity`);
 assert.ok(r.targetEffect&&r.capabilities.length);
 if(r.implementation==='planned')assert.notEqual(c.d,r.targetEffect,`${r.id}: don't falsely mark implemented text as pending`);
 else assert.equal(c.d,r.targetEffect,`${r.id}: shipped and designed text agree`);
}
assert.equal(p.newThemeCards.length,24);assert.equal(new Set(p.newThemeCards.map(r=>r.slot)).size,24);
for(const suit of ['S','H','D','C'])assert.equal(p.newThemeCards.filter(r=>r.slot[0]===suit).length,6);
for(const r of p.newThemeCards){assert.equal(r.implementation,'planned');assert.equal(g.NAMED[r.id],undefined,'Unimplemented cards must not leak into runtime');}
execFileSync(process.execPath,['tools/render-card-plan.mjs','--check'],{cwd:new URL('../',import.meta.url)});
console.log('Card plan: all 122 runtime cards covered; 24 new candidates isolated; descriptions and generated table synchronized');

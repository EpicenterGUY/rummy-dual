import {createStatusContext} from './helpers/status-fixture.mjs';
import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function functionSource(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);const body=script.indexOf('){',start),brace=body+1;let depth=0,end=-1;for(let i=brace;i<script.length;i++){if(script[i]==='{')depth++;else if(script[i]==='}'){depth--;if(depth===0){end=i+1;break}}}if(end<0)throw new Error(`unterminated ${name}`);return script.slice(start,end)}
function install(ctx,...names){for(const n of names)vm.runInContext(functionSource(n),ctx)}
new Function(script);
ok(script.includes("{id:'status'")&&!script.includes("expectVulnerableConsumed:true,expectReset:true,completeOn:'detonate',stopAfter:true"),'official-status lesson now continues into Joker lessons');
ok(script.includes("{id:'jokerKing'")&&script.includes("expectAttachTag:'jokerKing'")&&script.includes("expectJokerDeckReturn:true"),'Joker King lesson is registered as a real wildcard BURST plus deck-return check');
ok(script.includes("{id:'jokerDual'")&&script.includes("expectAttachTag:'jokerDual'")&&script.includes("expectEndureGain:16")&&script.includes("stopAfter:true"),'Dual Joker lesson is the advanced segment endpoint and checks its endure 16 effect');
ok(script.includes("function makeTutorialJoker(id,role,owner='player')")&&script.includes("makeCard('J',id,true,owner,id)"),'tutorial Jokers use real NAMED definitions instead of fake pure cards');
ok(script.includes("makeTutorialJoker('J1','jokerKingCard')")&&script.includes("makeTutorialCard('S','9','board','player')")&&script.includes("makeTutorialCard('D','9','board','player')"),'Joker King scenario fixes a three-suit SET missing one wildcard slot');
ok(script.includes("makeTutorialJoker('J3','jokerDualCard')")&&script.includes("makeTutorialCard('S','6','board','player')")&&script.includes("makeTutorialCard('D','6','board','player')"),'Dual Joker scenario fixes a separate three-suit SET');
ok(script.includes("jokerReturnedToDeck:state.player.deck.some(c=>jokerUids.has(c.uid))")&&script.includes("jokerSpent:state.player.spent.some(c=>jokerUids.has(c.uid))"),'real attach completion reports Joker retirement destination to tutorial progress');
ok(script.includes("expectJokerDeckReturn&&!(context.jokerReturnedToDeck&&!context.jokerSpent)")&&script.includes("expectEndureGain!=null&&context.afterEndure-context.beforeEndure!==step.expectEndureGain"),'tutorial completion validates actual Joker King return and Dual Joker endure gain');
ok(script.includes("step.id==='jokerKing'?")&&script.includes("step.id==='jokerDual'?"),'coach success copy explains both Joker-specific outcomes');
ok(html.includes("고급 튜토리얼 · 회수/정비/상태/조커"),'start screen advertises the completed advanced Joker section after unlock');
ok(road.includes('- [x] 조커 고급 튜토리얼'),'UX1 P3 roadmap records Joker tutorial complete');
{
 const ctx=createStatusContext(script,{console,state:{field:null},RANK_VALUE:{A:1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,J:11,Q:12,K:13}});
 ctx.isJoker=c=>c.suit==='J';ctx.isSuitFlexible=()=>false;
 install(ctx,'setValid','runSequenceOK','runValid','meldType');
 const joker={suit:'J',rank:'J',tag:'jokerKing'},cards=[{suit:'S',rank:'9'},{suit:'H',rank:'9'},{suit:'D',rank:'9'},joker];
 ok(ctx.meldType(cards)==='SET','real meldType accepts a Joker as the missing fourth SET slot');
}
console.log('RUMMY//DUEL Joker tutorial regressions passed.');

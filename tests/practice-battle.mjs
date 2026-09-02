import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const roadmap=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(c,m){if(!c)throw new Error(m);console.log(`PASS: ${m}`)}
function functionSource(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);const body=script.indexOf('){',start),brace=body+1;let depth=0,end=-1;for(let i=brace;i<script.length;i++){if(script[i]==='{')depth++;else if(script[i]==='}'){depth--;if(depth===0){end=i+1;break}}}if(end<0)throw new Error(`unterminated ${name}`);return script.slice(start,end)}
function install(ctx,...names){for(const n of names)vm.runInContext(functionSource(n),ctx)}
new Function(script);
ok(html.includes('id="practiceStartBtn"')&&html.includes('자유 연습 · 진행도 영향 없음'),'tutorial submenu exposes free practice while the main menu keeps five primary entries');
ok(html.includes('id="tutorialPracticeBtn"')&&script.includes("practice.hidden=!(state.tutorialSegmentDone&&segmentEnd)"),'completed basic or advanced tutorial segment can continue directly into free practice');
ok(script.includes("function newGame(mode='battle'){state.sessionMode=mode;")&&functionSource('isLiveCombatSession').includes("state.sessionMode==='practice'")&&functionSource('isLiveCombatSession').includes("state.sessionMode==='roguelike'"),'battle engine has explicit practice and roguelike experiment session modes');
ok(script.includes("const actionCap=state.sessionMode==='practice'?4:6"),'practice CPU uses a reduced action cap');
ok(script.includes("if(practice){title.textContent=win?'연습전 승리':'연습전 패배'")&&script.includes("이 결과는 클리어·레벨·해금에 반영되지 않습니다."),'practice result path explicitly avoids progression rewards');
ok(script.includes("if(state.sessionMode==='practice')startPracticeBattle();else newGame('battle')"),'reset and result replay preserve practice mode');
ok(script.includes("setTimeout(()=>{if(isLiveCombatSession()&&state.battleId===battleId&&!state.gameOver)aiTurn()},430)")&&script.includes("if(isLiveCombatSession()&&state.battleId===battleId&&state.gameOver)showResult(win)"),'practice shares race-safe AI/result scheduling with battle mode');
{
 const state={sessionMode:'practice',player:{},enemy:{},selected:new Set(),selectionOrder:[],boardSelected:new Set(),target:null};
 let uid=1,logs=[],rendered=0;
 const ctx=vm.createContext({console,Math,state,CORE_HP:60,CORE_COUNT:3});
 ctx.blankStatus=()=>({vulnerable:0,seal:0,regen:0});
 ctx.makeCard=(suit,rank,named,owner)=>({uid:uid++,suit,rank,owner,named});
 ctx.turnStart=w=>{state.turnToken++;const s=w==='player'?state.player:state.enemy;s.turnStarts=(s.turnStarts||0)+1;s.newMeldCount = 0;s.returnedSwitchThisTurn=false};
 ctx.log=(msg)=>logs.push(msg);ctx.render=()=>rendered++;
 install(ctx,'makePracticeCards','makePracticeDeck','setupPracticeBattle');
 ok(ctx.setupPracticeBattle()===true,'practice setup applies successfully to a live state');
 ok(state.field===null&&state.phase==='action'&&state.turn==='player','practice skips field and mulligan to start immediately in action phase');
 ok(state.player.hand.map(c=>`${c.rank}${c.suit}`).join(',')==='3S,3H,3D,3C,4C,5C,6C,7C','practice opening hand deterministically contains both SET and RUN lessons');
 ok(state.player.shield===12&&state.player.cores===3&&state.enemy.cores===3,'practice keeps normal CORE rules and only adds first-cycle shield forgiveness');
 ok(state.player.hand.every(c=>!c.named)&&state.enemy.hand.every(c=>!c.named),'practice battle uses pure cards only');
 ok(state.player.deck.at(-1).rank==='8'&&state.player.deck.at(-1).suit==='C','practice personal deck has deterministic first draw 8 club');
 ok(logs.some(x=>x.includes('진행되지 않습니다')||x.includes('반영되지 않습니다'))&&rendered===1,'practice clearly states no progression and renders the prepared board once');
}
ok(roadmap.includes('- [x] 자유 연습전 — 순수 카드'),'UX1 P2 roadmap records free practice battle complete');
console.log('RUMMY//DUEL free practice battle regressions passed.');

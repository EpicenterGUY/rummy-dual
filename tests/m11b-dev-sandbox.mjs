import fs from 'node:fs';
import vm from 'node:vm';

const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const doc=fs.readFileSync(new URL('../docs/ASYMMETRIC_RANK_PROTOTYPE.md',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let par=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')par++;else if(script[i]===')')par--;else if(script[i]==='{'&&par===0){brace=i;break}}if(brace<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
function install(ctx,...names){for(const n of names)vm.runInContext(source(n),ctx)}
new Function(script);

ok(html.includes('data-m11b-experiment="zero"')&&html.includes('data-m11b-experiment="few"')&&html.includes('data-m11b-experiment="many"'),'developer panel exposes explicit 0 / 4 / 10 asymmetric experiment cohorts');
ok(html.includes('id="m11bExperimentOverview"')&&html.includes('id="m11bExperimentList"'),'developer panel exposes isolated M11B experiment metrics review');
ok(script.includes("const M11B_EXPERIMENT_KEY='rummyDuelM11BExperimentV1'"),'M11B experiment history uses a dedicated localStorage key');
ok(script.includes("const BATTLE_METRICS_KEY='rummyDuelBattleMetricsV1'"),'ordinary M12 battle metrics keep their original independent key');
ok(script.includes("few:Object.freeze({id:'few',label:'소수 4장',slots:Object.freeze(['H4','S5','D4','C5'])})"),'few cohort matches the four-card structural baseline');
ok(script.includes("many:Object.freeze({id:'many',label:'스트레스 10장'"),'stress cohort keeps ten synthetic X/Y slots');
ok(source('renderDeveloperPanel').includes("document.querySelectorAll('[data-m11b-experiment]').forEach(b=>b.disabled=!on)"),'experiment buttons are disabled when DEV mode is off');
ok(source('newGame').includes('state.battleMetrics=null'),'every new game resets M12 battle metrics instead of reusing saved state');
ok(source('newGame').includes('state.m11bExperimentBattle=false')&&source('newGame').includes('state.m11bExperimentStats=null'),'ordinary new games clear all previous M11B experiment flags/stats');
ok(source('applyRankChoicePlan').includes("recordM11BRankChoices(list,normalized)"),'atomic rank-plan commit records actual asymmetric choice only after success');
ok(source('saveBattleMetrics').includes("if(state.m11bExperimentBattle){st.saved=true;return saveM11BExperimentMetrics(outcome)}")&&source('saveBattleMetrics').includes('if(state.developerBattle)return false'),'experiment battles route to isolated storage while ordinary DEV battles stay unsaved');
ok(source('restartCurrentCombat').includes("startM11BExperimentBattle(state.m11bExperimentCohort||'few',state.m11bExperimentSeed||currentM11BExperimentSeed())"),'result replay preserves the current experiment cohort and paired deck seed');
ok(source('setupM11BExperimentBattle').includes("e.deck=makeM11BExperimentDeck('enemy','zero',pairSeed)"),'experiment opponent always uses the zero-asymmetric control deck under the same paired seed');
ok(source('setupM11BExperimentBattle').includes('state.developerBattle=true')&&source('setupM11BExperimentBattle').includes('state.field=null'),'experiment battle is progress-safe DEV combat with field noise removed');

// Synthetic experiment deck must keep the same 29 canonical slots + one Joker and add no NAMED definitions.
{
  const slots=['S3','S4','S5','S6','S7','S8','S9','H2','H3','H4','H7','H8','H9','D2','D3','D4','D5','D6','D7','D8','C3','C4','C5','C6','C7','C8','C9','S10','H10'];
  const specs={H4:['4','6'],S5:['5','8'],D4:['4','9'],C5:['5','K'],D6:['6','8'],C3:['3','6'],H7:['7','10'],C6:['6','J'],S8:['8','K'],D3:['3','Q']};
  let uid=1;
  const ctx=vm.createContext({console,Set,Object,CORE_IDS:slots,M11B_EXPERIMENT_SPECS:specs,m11bExperimentCohort:id=>({id,slots:id==='zero'?[]:id==='few'?['H4','S5','D4','C5']:Object.keys(specs)}),makeCard:(suit,rank,named,owner,id=null)=>({uid:uid++,id:id||suit+rank,slot:suit==='J'?'J':suit+rank,suit,rank,baseRank:suit==='J'?null:rank,topRank:suit==='J'?null:rank,bottomRank:suit==='J'?null:rank,activeRank:null,rankOrientation:null,owner,name:named?'조커':'순수 카드',named}),shuffle:x=>x});
  install(ctx,'makeM11BExperimentDeck');
  const zero=ctx.makeM11BExperimentDeck('player','zero'),few=ctx.makeM11BExperimentDeck('player','few'),many=ctx.makeM11BExperimentDeck('player','many');
  ok(zero.length===30&&few.length===30&&many.length===30,'all experiment cohorts preserve the 30-card battle deck size');
  ok(zero.filter(c=>c.m11bSynthetic).length===0&&few.filter(c=>c.m11bSynthetic).length===4&&many.filter(c=>c.m11bSynthetic).length===10,'synthetic deck builder injects exactly 0 / 4 / 10 X/Y cards');
  ok(few.filter(c=>c.suit==='J').length===1&&few.filter(c=>c.suit!=='J').length===29,'experiment deck remains 29 regular slots plus one Joker');
  ok(few.find(c=>c.slot==='H4')?.topRank==='4'&&few.find(c=>c.slot==='H4')?.bottomRank==='6','synthetic H4 card carries the designed 4/6 printed ranks');
  ok(few.filter(c=>c.m11bSynthetic).every(c=>!c.named),'synthetic X/Y cards are not live NAMED cards');
}

// Choice tracking only runs inside the experiment and distinguishes top/bottom usage.
{
  const state={m11bExperimentBattle:true,m11bExperimentStats:null,turnNo:3};
  const cards=[{uid:1,slot:'H4',m11bSynthetic:true,topRank:'4',bottomRank:'6',activeRank:'4'}];
  const ctx=vm.createContext({console,state,normalizeRequestedRankPlan:(list,p)=>p,isAsymmetricRankCard:c=>c.topRank!==c.bottomRank,battleMetricTurn:()=>7});
  install(ctx,'getM11BExperimentStats','recordM11BRankChoices');
  ok(ctx.recordM11BRankChoices(cards,[{uid:1,rank:'6',orientation:'bottom'}])===1,'experiment records one committed asymmetric rank choice');
  ok(state.m11bExperimentStats.bottom===1&&state.m11bExperimentStats.top===0&&state.m11bExperimentStats.choices[0].slot==='H4','bottom orientation is preserved in experiment telemetry');
  state.m11bExperimentBattle=false;
  ok(ctx.recordM11BRankChoices(cards,[{uid:1,rank:'4',orientation:'top'}])===0&&state.m11bExperimentStats.top===0,'ordinary battles never record M11B experiment choices');
}

// saveBattleMetrics must keep normal DEV out of both histories while routing experiment outcomes separately.
{
  const calls=[];let stored=[];
  const st={saved:false};
  const state={sessionMode:'battle',m11bExperimentBattle:true,developerBattle:true};
  const ctx=vm.createContext({console,state,getBattleMetrics:()=>st,saveM11BExperimentMetrics:o=>{calls.push(o);return true},localStorage:{getItem:()=>JSON.stringify(stored),setItem:(k,v)=>{stored=JSON.parse(v)}},battleMetricsHistory:()=>stored,battleMetricsSnapshot:o=>({outcome:o})});
  install(ctx,'saveBattleMetrics');
  ok(ctx.saveBattleMetrics('win')===true&&calls[0]==='win'&&st.saved===true,'experiment result routes to the dedicated save path before generic DEV suppression');
  st.saved=false;state.m11bExperimentBattle=false;calls.length=0;
  ok(ctx.saveBattleMetrics('loss')===false&&calls.length===0&&!st.saved,'ordinary DEV battle still writes neither normal nor M11B experiment history');
}

const namedStart=script.indexOf('const NAMED={'),namedEnd=script.indexOf('const FIELDS=',namedStart),namedBlock=script.slice(namedStart,namedEnd);
ok(!/topRank\s*:|bottomRank\s*:/.test(namedBlock),'developer sandbox keeps the live NAMED asymmetric count at zero');
ok(road.includes('- [x] 개발자 전용 0/4/10장 실제 전투 샌드박스 + 분리 지표 기록'),'ROADMAP locks the DEV-only M11B sandbox');
ok(road.includes('- [ ] 비대칭 카드 0장 / 소수 / 다수 덱의 세트·런 성공률, 패말림, 정비, 러미 빈도 비교'),'full M11B battle-flow balance criterion remains open until samples exist');
ok(road.includes('- [ ] Balance from playtest data before large content expansion'),'M12 real-playtest balance gate remains open');
ok(doc.includes('## 개발자 전용 실제 전투 샌드박스')&&doc.includes('rummyDuelM11BExperimentV1'),'prototype doc records isolated experiment setup and storage');
ok(doc.includes('상대는 항상 같은 29슬롯의 `X/X` 0장 기준덱'),'prototype doc locks the zero-cohort opponent control');
console.log('M11B developer-only asymmetric battle sandbox regression passed.');

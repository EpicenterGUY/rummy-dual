import fs from 'node:fs';
import vm from 'node:vm';

const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function fn(name){const start=script.indexOf(`function ${name}(`);if(start<0)throw new Error(`missing ${name}`);const body=script.indexOf('){',start)+1;let d=0;for(let i=body;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
function exposeConst(name,ctx){const start=script.indexOf(`const ${name}=`);if(start<0)throw new Error(`missing const ${name}`);let i=script.indexOf('=',start)+1,depth=0,quote=null;for(;i<script.length;i++){const ch=script[i];if(quote){if(ch===quote&&script[i-1]!=='\\')quote=null;continue}if(ch==='\''||ch==='"'){quote=ch;continue}if(ch==='{'||ch==='['||ch==='(')depth++;else if(ch==='}'||ch===']'||ch===')')depth--;else if(ch===';'&&depth===0)break}const src=script.slice(start,i);vm.runInContext(`${src};globalThis.${name}_REF=${name};`,ctx);return ctx[`${name}_REF`]}

const ctx=vm.createContext({console,Math,Number,Object,Array,Set,Map});
const OFFICIAL_STATUS=exposeConst('OFFICIAL_STATUS',ctx);
const EFFECT_EVENTS=exposeConst('EFFECT_EVENTS',ctx);
const EFFECT_ACTIONS=exposeConst('EFFECT_ACTIONS',ctx);
ctx.OFFICIAL_STATUS=OFFICIAL_STATUS;
ctx.EFFECT_ACTIONS=EFFECT_ACTIONS;
ctx.state={player:{turnStarts:2,hand:[],deck:[],spent:[],melds:[]},enemy:{turnStarts:4,hand:[],deck:[],spent:[],melds:[]}};
ctx.sideObj=w=>ctx.state[w];ctx.meldsOf=w=>ctx.state[w].melds;ctx.switchName=w=>w==='player'?'YOU':'CPU';ctx.log=()=>{};ctx.fxNode=()=>{};
for(const n of ['blankStatus','blankMeldStatus','meldOwnerSide','meldMarkValue','consumeMeldMark','canApplySharedMeldStatus','officialStatusBag','officialStatusAllowed','officialStatusValue','setOfficialStatus','applyOfficialStatus','consumeOfficialStatus','clearOfficialStatus','fixedStatusActive','cardFixedActive','meldFixedActive','applyMeldFixed','expireOwnerFixedStatuses','meldStatusText'])vm.runInContext(fn(n),ctx);

ok(JSON.stringify(Object.keys(OFFICIAL_STATUS))===JSON.stringify(['vulnerable','seal','silence','flexible','echo','unstable','fixed','protect','regen','loaded','damp','overheat','endure','defer','comeback','fracture','mark']),'wave 9 registers seventeen implemented shared statuses');
ok(OFFICIAL_STATUS.vulnerable.scopes.join(',')==='player','vulnerable is player-scoped');
ok(OFFICIAL_STATUS.seal.scopes.join(',')==='player,meld,card','seal supports player/meld/card scopes');
ok(OFFICIAL_STATUS.fixed.scopes.includes('meld')&&OFFICIAL_STATUS.fixed.scopes.includes('card'),'fixed supports meld/card scopes');
ok(OFFICIAL_STATUS.protect.scopes.includes('meld')&&OFFICIAL_STATUS.protect.scopes.includes('card'),'protect supports meld/card scopes');
ok(OFFICIAL_STATUS.regen.scopes.join(',')==='player','regen is player-scoped');

const player={status:ctx.blankStatus()};
ctx.applyOfficialStatus('player',player,'seal',2,{silent:true});
ok(ctx.officialStatusValue('player',player,'seal')===2,'player seal stacks in official bag');
ctx.consumeOfficialStatus('player',player,'seal');
ok(player.status.seal===1,'seal consumes exactly one blocked named effect');

const meld={cards:[],status:{protected:1,sealNamed:1}};
ok(ctx.officialStatusValue('meld',meld,'protect')===1&&ctx.officialStatusValue('meld',meld,'seal')===1,'legacy meld aliases migrate to official protect/seal');
ctx.state.player.melds=[meld];
ctx.applyMeldFixed(meld,'player');
ok(ctx.meldFixedActive(meld),'fixed is active during target owner next turn window');
ctx.state.player.turnStarts=3;
ctx.expireOwnerFixedStatuses('player');
ok(!ctx.meldFixedActive(meld),'fixed expires at target owner next turn end');
const foreignCard={officialStatus:{seal:0,fixed:1,protect:0,fixedOwner:'player',fixedThroughStart:3},status:{marked:1}};
ctx.state.enemy.melds=[{cards:[foreignCard],status:ctx.blankMeldStatus()}];
ctx.expireOwnerFixedStatuses('player');
ok(!ctx.cardFixedActive(foreignCard),'card fixed expires even while that controlled card sits in opponent public meld');

const card={officialStatus:{seal:0,fixed:1,protect:0,fixedOwner:null,fixedThroughStart:null},status:{charged:2}};
ok(ctx.cardFixedActive(card),'card fixed uses separate officialStatus bag');
ok(card.status.charged===2,'one-off card markers remain separate from official statuses');

ok(EFFECT_EVENTS.includes('onAttach')&&EFFECT_EVENTS.includes('onDetonate')&&EFFECT_EVENTS.includes('onCoreBreak'),'effect event vocabulary covers core combat timings');
ok(EFFECT_ACTIONS.includes('applyStatus')&&EFFECT_ACTIONS.includes('returnSwitch'),'effect action vocabulary exposes reusable status/SWITCH actions');
ok(script.includes("runEffectAction('applyStatus',{actor:w},{scope:'meld',target:ctx.meld,key:'seal'"),'Venom Needle routes meld seal through reusable effect action');
ok(script.includes("runEffectAction('applyStatus',{actor:w},{scope:'meld',target:ctx.meld,key:'protect'"),'Branch Link routes meld protect through reusable effect action');
ok(script.includes("if(meldFixedActive(m)||cardFixedActive(c))return false"),'basic recovery respects fixed status');
ok(script.includes("if(meldFixedActive(om))continue"),'extortion respects fixed melds');
ok(script.includes("m.cards.length<4||meldFixedActive(m)"),'RUN cutting respects fixed melds');
ok(script.includes("targetCard&&consumeOfficialStatus('card',targetCard,'protect')"),'card protect can absorb targeted interference');
ok(!html.includes('별도 수치이며 최대 40입니다'),'rules modal no longer claims obsolete shield-40 cap');
ok(html.includes('고정 · 조합/카드 · 다음 소유자 턴 종료까지 회수·강탈·절단 등 이동 불가'),'rules modal documents fixed scope/lifecycle');
console.log('STATUS ENGINE PASS');

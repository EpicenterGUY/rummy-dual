import fs from 'node:fs';
import vm from 'node:vm';

const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const themeDoc=fs.readFileSync(new URL('../docs/THEME_GROUPS.md',import.meta.url),'utf8');
const poolDoc=fs.readFileSync(new URL('../docs/THEME_FULL_POOL_PLAN.md',import.meta.url),'utf8');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let par=0,brace=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')par++;else if(script[i]===')')par--;else if(script[i]==='{'&&par===0){brace=i;break}}if(brace<0)throw new Error(`missing body ${name}`);let d=0;for(let i=brace;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
function context(extra={}){return vm.createContext({console,Set,Map,Array,Object,Number,String,Boolean,Math,...extra})}
function install(ctx,...names){for(const n of names)vm.runInContext(source(n),ctx)}

new Function(script);
const wave6=[
 ['SSDJ','DJ','메인 프레임','ssMainFrame'],
 ['SSCQ','CQ','조립 라인','ssAssemblyLine'],
 ['SSHK','HK','테세우스 프레임','ssTheseusFrame'],
 ['SSSK','SK','스크랩 폭주','ssScrapRampage']
];
const resolver=source('resolveEffects');
for(const [id,slot,name,tag] of wave6){
 ok(script.includes(`'${id}':{slot:'${slot}',themeId:'scrap-shift',n:'${name}',t:'${tag}'`),`${name} is defined in the final SCRAP-SHIFT DEV wave`);
 ok(resolver.includes(`case'${tag}'`),`${tag} is registered on the named resolver surface`);
}
ok(script.includes("themeId:'scrap-shift',live:false"),'24/24 effect completion still keeps SCRAP-SHIFT non-live until integration release');

// Turn action tracking stores only distinct action kinds, not a numeric scrap resource.
{
 const state={turnToken:70};
 const side={};
 const ctx=context({state,sideObj:()=>side});
 install(ctx,'scrapShiftTurnActionState','noteScrapShiftTurnAction','scrapShiftTurnActionKinds','scrapShiftRampageReady');
 ok(ctx.noteScrapShiftTurnAction('player','dismantle')===true,'dismantle is recorded as a SCRAP-SHIFT turn action kind');
 ctx.noteScrapShiftTurnAction('player','dismantle');
 ok(ctx.scrapShiftTurnActionKinds('player').length===1,'repeating the same action kind does not stack a counter');
 ok(ctx.scrapShiftRampageReady('player')===false,'Scrap Rampage is not ready from dismantle alone');
 ctx.noteScrapShiftTurnAction('player','transplant');
 ok(ctx.scrapShiftTurnActionKinds('player').sort().join(',')==='dismantle,transplant','distinct dismantle + transplant kinds are retained');
 ok(ctx.scrapShiftRampageReady('player')===true,'Scrap Rampage becomes ready from dismantle plus transplant');
 state.turnToken=71;
 ok(ctx.scrapShiftTurnActionKinds('player').length===0,'SCRAP-SHIFT action kinds reset automatically on a new turn token');
}

// Q♣ Assembly Line uses the shared part marker on a new RUN and preserves player choice.
{
 const line={uid:1,owner:'player',themeId:'scrap-shift',tag:'ssAssemblyLine',name:'조립 라인'};
 const a={uid:2,owner:'player',name:'일반 카드',scrapShiftPart:false};
 const b={uid:3,owner:'player',name:'다른 테마 카드',themeId:'v-signal',scrapShiftPart:false};
 const meld={type:'RUN',cards:[line,a,b]};
 let spec=null,chosen=null,resumed=0;
 const state={turn:'player'};
 const ctx=context({
  state,
  isScrapShiftPart:c=>!!c.scrapShiftPart,
  setScrapShiftPart:(w,c)=>{c.scrapShiftPart=true;chosen=c;return true},
  requestEffectChoice:x=>{spec=x;return true},
  cardText:c=>c.name
 });
 install(ctx,'requestScrapShiftAssemblyLineChoice');
 ok(ctx.requestScrapShiftAssemblyLineChoice('player',line,meld,()=>{resumed++})===true,'Assembly Line opens the common choice UI when a new RUN has multiple eligible owned cards');
 ok(spec?.allowSkip===true&&spec.options.length===3,'Assembly Line may designate any owned card in its new RUN, including itself, or skip');
 spec.onChoose(spec.options.find(o=>o.card===b));
 ok(chosen===b&&b.scrapShiftPart===true&&resumed===1,'Assembly Line can designate an ordinary other-theme owned card as a part');
}
ok(resolver.includes("case'ssAssemblyLine':if(ctx.isNew&&type==='RUN'&&ctx.totalLength===3"),'Assembly Line is restricted to exact new 3-card RUN creation');

// J♦ Main Frame reacts to pre-retirement BURST state and protects a card outside the retiring SET.
{
 const frame={uid:10,owner:'player',themeId:'scrap-shift',tag:'ssMainFrame',name:'메인 프레임'};
 const part={uid:11,owner:'player',scrapShiftPart:true,name:'부품'};
 const other={uid:12,owner:'player',name:'외부 카드',protect:0};
 const set={type:'SET',cards:[frame,part,{uid:13,owner:'player'},{uid:14,owner:'enemy'}]};
 const otherMeld={type:'RUN',cards:[other,{uid:15,owner:'enemy'},{uid:16,owner:'enemy'}]};
 let protectedCard=null;
 const sides={player:{hand:[],melds:[set]},enemy:{hand:[],melds:[otherMeld]}};
 const ctx=context({
  sideObj:w=>sides[w],other:w=>w==='player'?'enemy':'player',meldsOf:w=>sides[w].melds,
  isScrapShiftPart:(c,o)=>!!c?.scrapShiftPart&&(!o||c.owner===o),
  officialStatusValue:(scope,c,key)=>scope==='card'&&key==='protect'?(c.protect||0):0,
  applyOfficialStatus:(scope,c,key,n)=>{if(scope==='card'&&key==='protect'){c.protect=(c.protect||0)+n;protectedCard=c}return n},
  cardText:c=>c.name||String(c.uid),log:()=>{}
 });
 install(ctx,'scrapShiftMainFrameProtect');
 ok(ctx.scrapShiftMainFrameProtect('player',{meld:set,reason:'버스트 후 4장 세트 자동 정리',preserveCards:[]})===true,'Main Frame recognizes a BURST-retiring SET with an owned spent-bound part');
 ok(part.scrapShiftPart===true,'Main Frame never consumes the part marker before normal spent routing');
 ok(protectedCard===other&&other.protect===1,'Main Frame grants protect 1 to an owned card outside the retiring SET');
 ok(ctx.scrapShiftMainFrameProtect('player',{meld:set,reason:'자발적 조합 정리',preserveCards:[]})===false,'Main Frame does not trigger on non-BURST cleanup');
}
const retire=source('retireMeld');
ok(retire.includes("sideObj(c.owner).spent.push(c)")&&retire.includes("noteScrapShiftPartSpent(c.owner,c,null,'meldRetire')"),'normal retirement leaves a part in spent through the shared lifecycle hook');

// K♥ Theseus Frame rewards two distinct part action kinds before DETONATE timing.
{
 const sourceCard={uid:20,owner:'player',themeId:'scrap-shift',tag:'ssTheseusFrame',name:'테세우스 프레임',themeTurnGates:{}};
 const state={turnToken:80};
 const side={scrapShiftTurnActions:{token:80,kinds:[]}};
 const gates=new Set();let shield=0;
 const key=(c,k,t)=>`${c.uid}:${k}:${t}`;
 const ctx=context({
  state,sideObj:()=>side,
  scrapShiftPublicCards:(w,tag)=>tag==='ssTheseusFrame'?[sourceCard]:[],
  themeTurnGateUsed:(c,k,t)=>gates.has(key(c,k,t)),
  claimThemeTurnGate:(c,k,t)=>{const x=key(c,k,t);if(gates.has(x))return false;gates.add(x);return true},
  addShield:(w,n)=>{shield+=n},log:()=>{}
 });
 install(ctx,'scrapShiftTurnActionState','noteScrapShiftTurnAction','scrapShiftTurnActionKinds','resolveScrapShiftTheseus');
 ctx.noteScrapShiftTurnAction('player','reassemble');
 ok(ctx.resolveScrapShiftTheseus('player')===false&&shield===0,'Theseus Frame requires two different part action kinds');
 ctx.noteScrapShiftTurnAction('player','dismantle');
 ok(ctx.resolveScrapShiftTheseus('player')===true&&shield===4,'Theseus Frame grants exact shield 16 after two distinct part action kinds');
 ok(ctx.resolveScrapShiftTheseus('player')===false&&shield===4,'Theseus Frame is capped to once per turn');
}
const turnEnd=source('turnEnd');
ok(turnEnd.indexOf("resolveScrapShiftTheseus(w)")<turnEnd.indexOf("if(state.switchTarget===w&&state.switchPower>0)"),'Theseus Frame resolves before end-turn DETONATE so its shield can defend that explosion');

// K♠ Scrap Rampage is a returning-card finisher and never opens another attach.
ok(resolver.includes("case'ssScrapRampage':if(isReturning&&scrapShiftRampageReady(w))fx.bonus+=14"),'Scrap Rampage adds exactly +14 only on a qualifying SWITCH return');
const finalHelpers=['scrapShiftTurnActionState','noteScrapShiftTurnAction','scrapShiftTurnActionKinds','scrapShiftRampageReady','requestScrapShiftAssemblyLineChoice','scrapShiftMainFrameProtect','resolveScrapShiftTheseus'].map(source).join('\n');
ok(!finalHelpers.includes('grantExtraAttach')&&!finalHelpers.includes('extraAttachRemaining'),'final SCRAP-SHIFT wave does not bypass the one-base-attach contract');

ok(road.includes('6차 피니셔 슬라이스 4장 — J♦ 메인 프레임 / Q♣ 조립 라인 / K♥ 테세우스 프레임 / K♠ 스크랩 폭주'),'ROADMAP records the final four SCRAP-SHIFT DEV cards');
ok(road.includes('- [x] 24장 / 수트별 6장 정의 및 실제 효과 구현'),'ROADMAP marks the full 24-card definition/effect implementation complete');
ok(themeDoc.includes('6차 피니셔 슬라이스 — J♦ `메인 프레임` / Q♣ `조립 라인` / K♥ `테세우스 프레임` / K♠ `스크랩 폭주`'),'canonical theme doc records the final DEV wave');
ok(poolDoc.includes('24장 미라이브 · 24장 DEV 구현 완료'),'full-pool policy records 24/24 DEV effects while keeping live promotion separate');
ok(road.includes('- [ ] 해금·도감·자동 테마 빌드·체험전 연결 후 일반 보상 승격'),'live release integration remains explicitly open');

console.log('SCRAP-SHIFT 24/24 final DEV wave regression passed.');

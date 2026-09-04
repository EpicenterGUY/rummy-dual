import fs from 'node:fs';
import vm from 'node:vm';

const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function source(name){
 const marker=`function ${name}(`,start=script.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);
 let p=0,b=-1;for(let i=start+marker.length-1;i<script.length;i++){if(script[i]==='(')p++;else if(script[i]===')')p--;else if(script[i]==='{'&&p===0){b=i;break}}
 if(b<0)throw new Error(`missing body ${name}`);let d=0;for(let i=b;i<script.length;i++){if(script[i]==='{')d++;else if(script[i]==='}'&&--d===0)return script.slice(start,i+1)}
 throw new Error(`unterminated ${name}`);
}

new Function(script);
ok(script.includes("'twelve-bloom':Object.freeze({id:'twelve-bloom'")&&!script.includes("'twelve-bloom':Object.freeze({id:'twelve-bloom',name:'TWELVE-BLOOM',displayName:'TWELVE-BLOOM',concept:'달 · 계절맞춤 · 그림맞춤 · 윤달',live:true"),'TWELVE-BLOOM is registered but remains non-live');

const cards=[
 ['TBC5','C5','계절 표본','tbSeasonSample'],
 ['TBHA','HA','붉은 띠','tbRedRibbon'],
 ['TBHK','HK','윤달 매듭','tbLeapKnot'],
 ['TBD2','D2','봄새','tbSpringBird'],
 ['TBS6','S6','겹빛','tbDoubleLight'],
 ['TBS10','S10','낙조','tbSunset']
];
for(const[id,slot,name,tag]of cards){
 const needle=`'${id}':{slot:'${slot}',themeId:'twelve-bloom',n:'${name}',t:'${tag}'`;
 ok(script.includes(needle),`${id} definition is locked to ${slot} / ${tag}`);
}

const resolver=source('resolveEffects');
ok(resolver.includes("case'tbLeapKnot'")&&resolver.includes('requestTwelveBloomLeapMonthChoice(w,c,resume)'),'윤달 매듭 uses resumable month selection');
ok(resolver.includes("case'tbSunset'")&&resolver.includes("twelveBloomCurrentEligibleMatchKeys(w,'season:')")&&resolver.includes("fx.bonus+=10"),'낙조 adds return power only from an eligible newly completed season');
ok(resolver.includes("claimThemeTurnGate(c,'tbSunset',state.turnToken)"),'낙조 is card-gated once per turn');

const move=source('moveCardBetweenMelds');
ok(move.includes("beginTwelveBloomAction(actor,'meldMove',{card:card.uid,reason:opts.reason||'move',sourceSide,targetSide})"),'meld-move transaction step preserves source/target side metadata');

{
 const events={draw:0,shield:0,vulnerable:0,logs:[]};
 const cardsByTag={
  tbSeasonSample:[{uid:1,name:'계절 표본'}],
  tbRedRibbon:[{uid:2,name:'붉은 띠'}],
  tbSpringBird:[{uid:3,name:'봄새'}],
  tbDoubleLight:[{uid:4,name:'겹빛'}]
 };
 const claimed=new Set();
 const ctx=vm.createContext({
  console,
  twelveBloomThemePublicCards:(owner,tag)=>cardsByTag[tag]||[],
  themeTurnGateUsed:(c,key,token)=>claimed.has(`${c.uid}:${key}:${token}`),
  claimThemeTurnGate:(c,key,token)=>{const k=`${c.uid}:${key}:${token}`;if(claimed.has(k))return false;claimed.add(k);return true},
  drawOne:()=>{events.draw++;return{}},
  addShield:(w,n)=>{events.shield+=n;return n},
  other:w=>w==='player'?'enemy':'player',
  sideObj:w=>({id:w}),
  applyOfficialStatus:(scope,target,key,n)=>{if(scope==='player'&&key==='vulnerable')events.vulnerable+=n;return n},
  log:(msg)=>events.logs.push(msg),
  twelveBloomActionMovedCardTo:(packet,c,target)=>c.uid===3&&target==='enemy'
 });
 vm.runInContext(source('handleTwelveBloomThemeEvent'),ctx);
 const packet={event:'onBloomMatchChange',actor:'player',owner:'player',turnToken:9,newlyCompleted:['season:spring','picture:redRibbon'],action:'attach',actionMeta:{targetSide:'enemy',cards:[3]},steps:[]};
 const changed=ctx.handleTwelveBloomThemeEvent(packet);
 ok(changed===true,'first-slice match handler reports a resolved reaction');
 ok(events.draw===2,'계절 표본 and 봄새 each draw once on the matching action');
 ok(events.shield===3,'붉은 띠 grants shield 12 through recovery-unit scaling');
 ok(events.vulnerable===1,'겹빛 applies vulnerable 1 on season+picture simultaneous completion');
 ctx.handleTwelveBloomThemeEvent(packet);
 ok(events.draw===3&&events.vulnerable===1,'turn-gated passives do not repeat while non-gated 봄새 can react to a distinct entry event');
}

{
 let shield=0;
 const ctx=vm.createContext({
  console,
  state:{turnToken:4},
  setTwelveBloomLeapMonth:()=>({diff:{newlyCompleted:['season:winter']}}),
  twelveBloomMatchGateUsed:()=>false,
  addShield:(w,n)=>{shield+=n},
  log:()=>{}
 });
 vm.runInContext(source('applyTwelveBloomLeapMonthChoice'),ctx);
 const result=ctx.applyTwelveBloomLeapMonthChoice('player',{name:'윤달 매듭'},12);
 ok(!!result&&shield===2,'윤달 매듭 grants shield 8 only from the designation diff');
}

console.log('TWELVE-BLOOM first effect slice regression passed.');

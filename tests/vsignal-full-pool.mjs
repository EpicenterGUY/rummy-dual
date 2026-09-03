import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
const plan=fs.readFileSync(new URL('../docs/THEME_FULL_POOL_PLAN.md',import.meta.url),'utf8');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function literal(name,next){const a=script.indexOf(`const ${name}=`);if(a<0)throw new Error(`missing ${name}`);const b=script.indexOf(next,a);if(b<0)throw new Error(`missing end ${name}`);return script.slice(a+`const ${name}=`.length,b).trim().replace(/;$/,'')}
const ctx=vm.createContext({console,Object,Array,Set,Map,Number,String,Boolean,Math});
vm.runInContext(`globalThis.NAMED=${literal('NAMED','\nconst CHARACTERS=')}`,ctx);
const expected={
 VSSA:'vBroadcastAccident',VSS5:'vBadClip',VSS7:'vLiveControversy',VSS9:'vReverseViral',VSSQ:'vFlameStreamer',VSSK:'vBanSoon',
 VSHA:'vFirstBroadcast',VSH3:'vAsmr',VSH5:'vEncore',VSH7:'vFanService',VSH10:'vMilestoneBroadcast',VSHK:'vMillionSubs',
 VSD2:'vRookieSet',VSD3:'vTrioCollab',VSD4:'vGatherAll',VSD6:'vSuperchat',VSDJ:'vManager',VSDK:'vLegendIdol',
 VSCA:'vOnAir',VSC4:'vGameBroadcast',VSC6:'vRaid',VSC8:'vCollabRequest',VSCJ:'vGeniusEditor',VSCK:'vEndurance'
};
const cards=Object.entries(ctx.NAMED).filter(([,d])=>d?.themeId==='v-signal');
ok(cards.length===24,`V-SIGNAL full pool has exactly 24 definitions (${cards.length})`);
ok(new Set(cards.map(([,d])=>d.slot)).size===24,'V-SIGNAL 24 cards occupy 24 distinct physical slots');
for(const[id,tag]of Object.entries(expected)){
 const d=ctx.NAMED[id];ok(!!d,`${id} definition exists`);ok(d.themeId==='v-signal'&&d.t===tag,`${id} keeps V-SIGNAL tag ${tag}`);
ok(d.rewardPool!==false,`${id} is eligible for ordinary roguelike rewards after 60-card integration`);
}
for(const tag of ['vBroadcastAccident','vBadClip','vLiveControversy','vFlameStreamer','vBanSoon','vFirstBroadcast','vAsmr','vFanService','vRookieSet','vTrioCollab','vManager','vLegendIdol','vOnAir','vGameBroadcast','vRaid','vCollabRequest','vGeniusEditor'])ok(script.includes(`case'${tag}'`),`${tag} has a live common-resolver branch`);
for(const tag of ['vReverseViral','vSuperchat','vMilestoneBroadcast','vMillionSubs'])ok(script.includes(tag)&&script.includes('function handleVSignalFullThemeEvent('),`${tag} is wired through the passive V-SIGNAL event handler`);
ok(script.includes('function requestVSignalRaidRecoverChoice('),'RAID uses a resumable legal free-recovery chooser');
ok(script.includes('function requestVSignalEditorChoice('),'Genius Editor uses a resumable legal movement chooser');
ok(script.includes('function requestVSignalLegendChoice('),'Legend Idol uses a resumable reward choice');
ok(script.includes('function noteVSignalMeldKind('),'SET/RUN cross-play is tracked without a new numeric resource');
ok(script.includes("typeof noteVSignalMeldKind==='function'?noteVSignalMeldKind(w,type):{before:false,both:false,completedPair:false}"),'common resolver keeps isolated legacy tests compatible when V-SIGNAL helper is not loaded');
ok(script.includes("if(!packet?.event)return false;if(typeof sideObj!=='function'||typeof other!=='function')return false"),'V-SIGNAL passive subscriber preserves the isolated shared-event foundation');
ok(script.includes("themeCap=Math.min(4,new Set(preferred.map(namedSlot)).size)"),'automatic theme build caps the selected theme at four physical slots');
ok(script.includes("(themeId==='mixed'||NAMED[id]?.themeId!==themeId)"),'automatic fill cannot silently exceed the four-card theme cap');
ok(!script.includes('allowStaged=')&&cards.every(([,d])=>d.rewardPool!==false),'ordinary roguelike reward ranking no longer stages completed theme cards');
const unlockBlock=script.slice(script.indexOf('const UNLOCK_GROUPS='),script.indexOf('function unlockedNamed'));
for(const id of Object.keys(expected))ok(unlockBlock.includes(`'${id}'`),`${id} is reachable through progression unlock groups`);
ok(unlockBlock.includes("items:['S8','H5','VSH5','D9','C8','D10','C3']"),'full-pool expansion preserves Encore legacy unlock timing');
ok(unlockBlock.includes("items:['S9','H10','D2','VSD4','C6','SJ','H3']"),'full-pool expansion preserves Gather All legacy unlock timing');
ok(unlockBlock.includes("items:['SA','S2','H9','C9','VSCK','J4']"),'full-pool expansion preserves Endurance legacy unlock timing');
ok(unlockBlock.includes("id:'vs8'")&&unlockBlock.includes("items:['VSSK']"),'new V-SIGNAL cards use dedicated progression groups');
ok(!script.includes('hypeCount')&&!script.includes('HYPE_COUNT'),'V-SIGNAL still creates no HYPE resource');
ok(road.includes('V-SIGNAL 24/24 풀 카드군 구현'),'ROADMAP records the full V-SIGNAL implementation');
ok(plan.includes('| V-SIGNAL | 24 | 24 | 0 | 24/24 |'),'full-pool plan records V-SIGNAL as 24/24');
console.log('V-SIGNAL 24/24 full-pool regression passed.');

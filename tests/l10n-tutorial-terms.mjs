import fs from 'node:fs';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const road=fs.readFileSync(new URL('../ROADMAP.md',import.meta.url),'utf8');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
function functionSource(name){const scripts=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');const marker=`function ${name}(`,start=scripts.indexOf(marker);if(start<0)throw new Error(`missing ${name}`);let par=0,brace=-1;for(let i=start+marker.length-1;i<scripts.length;i++){if(scripts[i]==='(')par++;else if(scripts[i]===')')par--;else if(scripts[i]==='{'&&par===0){brace=i;break}}let d=0;for(let i=brace;i<scripts.length;i++){if(scripts[i]==='{')d++;else if(scripts[i]==='}'&&--d===0)return scripts.slice(start,i+1)}throw new Error(`unterminated ${name}`)}
const scripts=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
const ts=scripts.indexOf('const TUTORIAL_STEPS=Object.freeze(['),te=scripts.indexOf(']);\nconst NAMED=',ts);
ok(ts>=0&&te>ts,'tutorial step registry is discoverable');
const steps=scripts.slice(ts,te);
const visible=[steps,functionSource('applyTutorialScenario'),functionSource('tutorialCheckProgress'),functionSource('renderTutorialCoach')].join('\n');
const userStrings=[...visible.matchAll(/(['`])((?:(?!\1)[\s\S])*?)\1/g)].map(m=>m[2]).filter(x=>/[가-힣]/.test(x));
const renderedStrings=userStrings.map(x=>x.replace(/\$\{[^}]*\}/g,''));
for(const term of ['SET','RUN','BURST','CHAIN','SWITCH','RUMMY','DETONATE','CORE']){
  const bad=renderedStrings.filter(x=>new RegExp(`(^|[^A-Za-z])${term}([^A-Za-z]|$)`).test(x));
  ok(bad.length===0,`tutorial rendered Korean copy exposes no legacy ${term} term`);
}
ok(steps.includes("expectMeld:'SET'")&&steps.includes("expectMeld:'RUN'"),'internal tutorial meld-type keys remain engine-native SET/RUN');
ok(steps.includes("themeId:'v-signal'")&&steps.includes('V-SIGNAL'),'theme identity and V-SIGNAL proper name are preserved');
ok(steps.includes('런 회수는 체인이 1 감소하고'),'recovery hint uses 런/체인 terminology');
ok(steps.includes('내 ♥ 런의 앙코르 5♥')&&steps.includes('버스트/체인 반환에 못 쓰지만'),'V-SIGNAL hint uses official Korean battle terms');
ok(functionSource('applyTutorialScenario').includes('상대 5 세트에 재입장시켜 버스트하세요.'),'V-SIGNAL scripted log uses 버스트');
ok(functionSource('tutorialCheckProgress').includes('런 체인이 ${context.beforeChain}'),'tutorial success copy uses 런 체인');
ok(functionSource('renderTutorialCoach').includes('재입장 → 버스트로 이어지는'),'theme completion coach uses 버스트');
ok(road.includes('- [x] 튜토리얼 용어 반영'),'ROADMAP marks tutorial terminology localization complete');
console.log('Tutorial terminology localization regression passed.');

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

ok(script.includes('function deckBuildAsymmetricFlexAnalysis('),'M11B deckbuilder exposes a separate asymmetric flexibility analyzer');
ok(source('deckBuildAnalysis').includes("basis:'base-slot'"),'base distribution declares the canonical base-slot basis');
ok(!source('deckBuildAnalysis').includes('topRank')&&!source('deckBuildAnalysis').includes('bottomRank'),'base distribution never reads asymmetric printed ranks');
ok(source('renderDeckBuilder').includes('deckBuildAsymmetricFlexAnalysis(build)'),'deckbuilder renders the separate flexibility layer when available');
ok(source('renderDeckBuilder').includes('원본 52슬롯 기준')&&source('renderDeckBuilder').includes('비대칭 사용값은 중복 집계하지 않음'),'deckbuilder explicitly explains base-slot counting');
ok(html.includes('.deckFlexNote{'),'separate asymmetric-flex UI note has a dedicated style');

const RANK_VALUE={A:1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,J:11,Q:12,K:13};
const NAMED={ASYM:{slot:'S7',n:'3/7 시험',topRank:'3',bottomRank:'7'},SYM:{slot:'H7',n:'7/7 시험',topRank:'7',bottomRank:'7'},WRONG:{slot:'D9',n:'잘못된 슬롯',topRank:'2',bottomRank:'9'}};
const progress={deckBuild:{slots:['S5','S6','S7','H7','D7'],variants:{S7:'ASYM',H7:'SYM'},enabled:true,joker:'J1'}};
const ctx=vm.createContext({console,Array,Object,Set,Math,RANK_VALUE,NAMED,progress});
install(ctx,'namedSlot','parseRegularId','deckBuildAnalysis','deckBuildAsymmetricFlexAnalysis');

const base=ctx.deckBuildAnalysis(progress.deckBuild.slots);
ok(base.basis==='base-slot','analysis result is explicitly base-slot based');
ok(base.ranks['7']===3&&base.ranks['3']===0,'3/7 variant still counts only as its original 7 slot in rank distribution');
ok(base.suits.S===3&&base.suits.H===1&&base.suits.D===1,'asymmetric printed values never change suit geometry');
ok(base.setPairs===1&&base.setReady===1,'base SET material remains determined by canonical slots');
ok(base.runWindows===1&&base.longestRun===3,'base RUN windows remain S5-S6-S7 regardless of alternate printed rank');

const flex=ctx.deckBuildAsymmetricFlexAnalysis(progress.deckBuild);
ok(flex.cards===1,'only actual X/Y selected variants enter the flexibility layer');
ok(flex.alternateRankSlots===1,'one alternate rank different from base is counted once');
ok(flex.printedRanks['3']===1&&flex.printedRanks['7']===1,'flexibility layer exposes both possible printed choices without duplicating the card in base stats');
ok(flex.details[0].slot==='S7'&&flex.details[0].baseRank==='7'&&flex.details[0].topRank==='3'&&flex.details[0].bottomRank==='7','flexibility detail preserves exact original slot and both printed ranks');

progress.deckBuild.variants.S7='WRONG';
const wrong=ctx.deckBuildAsymmetricFlexAnalysis(progress.deckBuild);
ok(wrong.cards===0,'variant assigned to the wrong canonical slot cannot leak alternate ranks into deck analysis');

const namedStart=script.indexOf('const NAMED={'),namedEnd=script.indexOf('const FIELDS=',namedStart),namedBlock=script.slice(namedStart,namedEnd);
ok(!/topRank\s*:|bottomRank\s*:/.test(namedBlock),'deck-analysis groundwork still enables zero live asymmetric card definitions');
ok(road.includes('- [x] 덱빌더 숫자·무늬·세트·런 분포는 원본 52슬롯(`baseRank+suit`) 기준으로 고정하고 비대칭 `X/Y`의 선택 유연성은 별도 분석으로 분리'),'ROADMAP locks base-slot distribution versus asymmetric flexibility');
ok(doc.includes('## 덱빌더 분포 기준 — 원본 슬롯과 선택 유연성 분리'),'prototype document records the deckbuilder analysis contract');
ok(doc.includes('3과 7 두 장처럼 중복 집계하지 않는다'),'prototype document explicitly forbids double-counting X/Y values');
ok(doc.includes('실제 세트/런 성공률 증가는 M11B 밸런스 표본에서 별도로 측정'),'prototype document keeps real success-rate balance measurement separate');

console.log('M11B deckbuilder base-slot/flexibility analysis regression passed.');

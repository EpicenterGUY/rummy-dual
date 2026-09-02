import fs from 'node:fs';
import vm from 'node:vm';
export const html=fs.readFileSync(new URL('../../index.html',import.meta.url),'utf8');
export function makeGame(sourceHtml=html,seed=1,options={}){
  let code=[...sourceHtml.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
  // Load the complete shipped engine, omitting only UI event binding / menu bootstrap.
  code=code.slice(0,code.indexOf("document.getElementById('developerBtn').onclick"));
  const names=[...code.matchAll(/function (\w+)\(/g)].map(m=>m[1]);
  const exports=[...new Set(names)].filter(n=>!['rec','walk','visit','finish','resume','next','apply','done'].includes(n));
  let value=seed>>>0;
  const math=Object.create(Math);math.random=()=>{value=(Math.imul(value,1664525)+1013904223)>>>0;return value/4294967296};
  const element=()=>({classList:{add(){},remove(){},toggle(){},contains(){return false}},style:{},dataset:{},textContent:'',innerHTML:'',hidden:false,disabled:false,appendChild(){},addEventListener(){},setAttribute(){},removeAttribute(){},focus(){},closest(){return null},querySelector(){return null},querySelectorAll(){return[]}});
  const elements=new Map(),storage=options.storage||new Map();
  const localStorage=options.localStorage||{getItem:k=>storage.get(k)??null,setItem:(k,v)=>storage.set(k,String(v)),removeItem:k=>storage.delete(k)};
  const document={getElementById:id=>{if(!elements.has(id))elements.set(id,element());return elements.get(id)},querySelector:()=>null,querySelectorAll:()=>[],createElement:element,body:element(),documentElement:element()};
  const ctx=vm.createContext({console,Math:math,document,localStorage,setTimeout(){},clearTimeout(){},requestAnimationFrame(){},matchMedia:()=>({matches:true}),performance:{now:()=>0},navigator:{},window:{}});
  // Presentation is inert; all rule, status, card-effect, AI and metric functions remain real.
  code+=`\ndeveloperMode=${!!options.developer};\nrender=()=>{};combatBanner=()=>{};flashPile=()=>{};log=()=>{};renderEffectChoiceModal=()=>{};\nObject.assign(globalThis,{state,NAMED,CORE_IDS,progress,getProgress:()=>progress,getPlayerSettings:()=>playerSettings,replaceProgress:value=>progress=normalizeProgress(value),testSetDeveloperField:value=>developerField=value,${exports.map(n=>`${n}:typeof ${n}==='function'?${n}:undefined`).join(',')}});})();`;
  vm.runInContext(code,ctx);
  ctx.newGame();ctx.state.field=null;ctx.state.phase='action';ctx.state.turnToken=1;
  return ctx;
}

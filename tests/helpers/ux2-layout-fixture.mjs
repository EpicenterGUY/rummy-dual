// Development preview only. Every frame uses an in-memory store, never the player's saves.
export const uiViewports=['360x640','360x800','390x844','480x900','852x744','768x1024','1024x768','1366x768','1920x1080'];
export const uiScenarios=['home','roguelike','new','loadout','battle','reward','region','records','tutorial','setup','deck','settings','dev','dev-codex'];
export function uiFixture(html,scenario='home'){
  if(!uiScenarios.includes(scenario))scenario='home';
  const isolated="const qaStore=new Map();const localStorage={getItem:k=>qaStore.get(k)||null,setItem:(k,v)=>qaStore.set(k,String(v)),removeItem:k=>qaStore.delete(k)};";
  const setup=`
progress.totalClears=6;progress.tutorialPromptSeen=true;progress.tutorialCompleted=true;saveProgress();renderProgress();renderStartScreen();
function qaSkip(){const d=loadRoguelikeRunDraft(),n=roguelikePendingRewardNode(d);if(n)roguelikeSkipRewardNode({runId:d.runId,nodeId:n.id,revision:n.revision,deckSignature:n.deckSignature})}
function qaWin(){roguelikeCompleteBattleNode(roguelikeCurrentBattleNodeRequest(loadRoguelikeRunDraft()))}
const qaScenario=${JSON.stringify(scenario)};
if(qaScenario==='roguelike')showMenuPage('roguelike');
if(qaScenario==='new'||qaScenario==='loadout'){beginNormalRun();if(qaScenario==='loadout'){runNewStage='loadout';renderNormalRunNew()}}
if(['battle','reward','region','records'].includes(qaScenario)){
 prepareRoguelikeRunDraft('wanderer');
 if(qaScenario==='reward')qaWin();
 if(qaScenario==='region')for(let i=0;i<3;i++){qaWin();qaSkip()}
 if(qaScenario==='records')for(let i=0;i<40;i++){const d=loadRoguelikeRunDraft(),stage=roguelikeMenuStage(d);if(stage==='completed')break;if(stage==='reward')qaSkip();else if(stage==='region')roguelikeChooseRegion({...roguelikeNextRewardNodeRequest(d),regionId:ROGUELIKE_REGIONS.find(r=>!d.regionPath.includes(r.id)).id});else qaWin()}
 showMenuPage(qaScenario==='records'?'roguelike-records':'roguelike-run');
}
if(qaScenario==='tutorial')showMenuPage('tutorial');
if(qaScenario==='setup'||qaScenario==='deck'){openBattleSetup();if(qaScenario==='deck')showBattleSetupStep('deck')}
if(qaScenario==='settings')openPlayerSettings();
if(qaScenario==='dev'||qaScenario==='dev-codex'){
 setDeveloperMode(true);prepareRoguelikeRunDraft('pure');roguelikeIssueRewardNode(roguelikeNextRewardNodeRequest(loadRoguelikeRunDraft()));openDeveloperPanel();
 if(qaScenario==='dev'){document.getElementById('developerRunTools').open=true;document.querySelector('#developerBuildHost .deckBuilderGroup').open=true}
 else openCodex(true);
}
document.body.dataset.qaScenario=qaScenario;
`;
  return html.replace('(()=>{','(()=>{'+isolated).replace(/\}\)\(\);\s*<\/script>\s*<\/body>/,setup+'})();</script></body>');
}
export function uiLayoutFixture(){return `<!doctype html><html lang="en"><head><meta charset="utf-8"><title>UX2 menu layout QA</title><style>body{margin:0;background:#171f24;color:#fff;font:14px sans-serif}label,button{margin:4px}select,button{font:inherit;padding:4px}pre{max-height:160px;overflow:auto;white-space:pre-wrap;font:11px monospace;margin:4px}iframe{display:block;border:0}</style></head><body>
<label>Viewport <select id="size">${uiViewports.map(v=>`<option>${v}</option>`).join('')}</select></label>
<label>Scene <select id="scene">${uiScenarios.map(v=>`<option>${v}</option>`).join('')}</select></label><button id="measure">Measure</button><pre id="report"></pre>
<iframe id="game" title="Menu viewport" src="/qa/ui-scene?scene=home" style="width:360px;height:640px"></iframe><script>
const frame=document.getElementById('game');
function measure(){const d=frame.contentDocument,w=frame.contentWindow;if(!d?.body?.dataset.qaScenario)return;const modal=[...d.querySelectorAll('.overlay.show .modal')].at(-1),surface=modal||d.getElementById('startScreen'),r=surface.getBoundingClientRect(),visible=e=>e.getClientRects().length>0;const buttons=[...surface.querySelectorAll('button,input,select,summary')].filter(visible);const clipped=buttons.filter(e=>{const b=e.getBoundingClientRect();return b.left<r.left-1||b.right>r.right+1}).map(e=>({id:e.id,text:e.textContent.trim().slice(0,45),width:Math.round(e.getBoundingClientRect().width)}));const nav=[...d.querySelectorAll('#menuHome nav button')].filter(visible);const result={scenario:d.body.dataset.qaScenario,viewport:[w.innerWidth,w.innerHeight],documentOverflow:d.documentElement.scrollWidth-w.innerWidth,surfaceOverflow:surface.scrollWidth-surface.clientWidth,surfaceBounds:{left:r.left,right:r.right,top:r.top,bottom:r.bottom},scrollHeight:surface.scrollHeight,clientHeight:surface.clientHeight,scrollDelta:surface.scrollHeight-surface.clientHeight,overflowY:w.getComputedStyle(surface).overflowY,visiblePrimaryChoices:nav.length,clippedControls:clipped,smallestButtonHeight:Math.round(Math.min(...buttons.filter(e=>e.tagName==='BUTTON').map(e=>e.getBoundingClientRect().height)))};document.getElementById('report').textContent=JSON.stringify(result,null,2)}
document.getElementById('size').onchange=e=>{const [width,height]=e.target.value.split('x');frame.style.width=width+'px';frame.style.height=height+'px';requestAnimationFrame(()=>requestAnimationFrame(measure))};document.getElementById('scene').onchange=e=>{document.getElementById('report').textContent='Loading';frame.src='/qa/ui-scene?scene='+encodeURIComponent(e.target.value)};document.getElementById('measure').onclick=measure;frame.onload=measure;
</script></body></html>`}

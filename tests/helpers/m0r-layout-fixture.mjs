export function boardFixture(html){
  const setup=`
startBattle();state.developerBattle=true;state.phase='action';state.turn='player';state.turnNo=10;state.turnToken=20;state.field=null;
for(const w of ['player','enemy']){
  const s=sideObj(w);s.melds=['S','H','C'].map(suit=>({type:'RUN',cards:['A','2','3','4','5','6','7','8','9','10','J','Q','K'].map(rank=>makeCard(suit,rank,false,w)),chain:10,createdToken:18,createdTurn:9,lastAttachToken:null,status:blankMeldStatus(),themeMeta:{}}));
}
render();
`;
  return html.replace(/\}\)\(\);\s*<\/script>\s*<\/body>/,setup+'})();</script></body>');
}
export function layoutFixture(){return `<!doctype html><html><head><meta charset="utf-8"><title>M0R layout QA</title><style>pre{max-height:100px;overflow:auto;font:11px monospace;margin:2px}iframe{display:block}</style></head><body style="margin:0;background:#222;color:white;font:16px sans-serif"><label>Viewport <select id="size"><option>360x800</option><option>390x844</option><option>430x932</option><option>768x1024</option><option>852x744</option><option>1024x768</option><option>1366x768</option><option>1920x1080</option></select></label><button id="measure">Measure board</button><pre id="report"></pre><iframe title="Three-slot board" id="board" src="/qa/board" style="border:0;width:360px;height:800px"></iframe><script>
const frame=document.getElementById('board');
function measure(){const d=frame.contentDocument,w=frame.contentWindow;if(!d.querySelector('.meldEntry'))return;const rows=[...d.querySelectorAll('.meldCardRow')],sides=[...d.querySelectorAll('.meldSide')];const result={viewport:[w.innerWidth,w.innerHeight],documentOverflow:d.documentElement.scrollWidth-w.innerWidth,slots:sides.map(s=>s.querySelectorAll('.meldEntry').length),panels:[...d.querySelectorAll('.meldZone,.handZone')].map(e=>{const r=e.getBoundingClientRect();return{left:r.left,right:r.right,width:r.width}}),cardWidth:Math.min(...rows.map(r=>r.querySelector('.meldMiniCard').getBoundingClientRect().width)),rows:rows.map(r=>({cards:r.children.length,width:r.clientWidth,scrollWidth:r.scrollWidth,overflow:w.getComputedStyle(r).overflowX})),sides:sides.map(s=>({height:s.clientHeight,scrollHeight:s.scrollHeight,overflow:w.getComputedStyle(s).overflowY}))};document.getElementById('report').textContent=JSON.stringify(result,null,2)}
document.getElementById('size').onchange=e=>{const [w,h]=e.target.value.split('x');frame.style.width=w+'px';frame.style.height=h+'px';requestAnimationFrame(()=>requestAnimationFrame(measure))};document.getElementById('measure').onclick=measure;frame.onload=measure;
</script></body></html>`}

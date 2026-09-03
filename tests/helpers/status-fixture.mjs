import vm from 'node:vm';
// Legacy isolated-function suites now need the production shared status dependencies.
export function installStatusRuntime(ctx,script){
 if(!ctx.OFFICIAL_STATUS){const block=script.match(/const OFFICIAL_STATUS=Object.freeze\(\{[\s\S]*?\}\);/)[0];vm.runInContext(block+'globalThis.OFFICIAL_STATUS=OFFICIAL_STATUS;',ctx)}
 for(const name of ['blankStatus','blankMeldStatus','meldOwnerSide','meldMarkValue','consumeMeldMark','canApplySharedMeldStatus','officialStatusBag','officialStatusAllowed','officialStatusValue','setOfficialStatus','applyOfficialStatus','consumeOfficialStatus','clearOfficialStatus','consumeReturnStatuses','prepareTargetReturnEffects','effectReservationLabel','cancelMeldReservations','resolveEffectReservations']){
  if(typeof ctx[name]==='function')continue;
  const start=script.indexOf(`function ${name}(`);let parens=0,body=-1;
  for(let i=start+`function ${name}`.length;i<script.length;i++){if(script[i]==='(')parens++;else if(script[i]===')')parens--;else if(script[i]==='{'&&parens===0){body=i;break}}
  let depth=0,end=body;for(;end<script.length;end++){if(script[end]==='{')depth++;else if(script[end]==='}'&&--depth===0){end++;break}}
  vm.runInContext(script.slice(start,end),ctx);
 }
}

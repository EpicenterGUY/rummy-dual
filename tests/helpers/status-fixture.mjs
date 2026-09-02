import vm from 'node:vm';
// Legacy isolated-function suites now need the production shared status dependencies.
export function installStatusRuntime(ctx,script){
 if(!ctx.OFFICIAL_STATUS){const block=script.match(/const OFFICIAL_STATUS=Object.freeze\(\{[\s\S]*?\}\);/)[0];vm.runInContext(block+'globalThis.OFFICIAL_STATUS=OFFICIAL_STATUS;',ctx)}
 for(const name of ['blankStatus','blankMeldStatus','officialStatusBag','officialStatusAllowed','officialStatusValue','setOfficialStatus','applyOfficialStatus','consumeOfficialStatus','clearOfficialStatus','consumeReturnStatuses']){
  if(typeof ctx[name]==='function')continue;
  const line=script.split('\n').find(line=>line.startsWith(`function ${name}(`));
  vm.runInContext(line,ctx);
 }
}

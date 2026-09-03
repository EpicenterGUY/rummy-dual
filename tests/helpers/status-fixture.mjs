import vm from 'node:vm';
// Isolated-function suites share the production status and placement dependencies.
export function installStatusRuntime(ctx,script){
 for(const name of ['RANK_VALUE','SUIT_SYMBOL'])if(!ctx[name]){const value=script.match(new RegExp(name+'=(\\{[^}]+\\})'))?.[1];if(value)vm.runInContext('globalThis.'+name+'='+value+';',ctx)}
 if(!ctx.OFFICIAL_STATUS){const block=script.match(/const OFFICIAL_STATUS=Object.freeze\(\{[\s\S]*?\}\);/)[0];vm.runInContext(block+'globalThis.OFFICIAL_STATUS=OFFICIAL_STATUS;',ctx)}
 if(!ctx.EFFECT_ACTIONS){const block=script.match(/const EFFECT_ACTIONS=Object.freeze\(\[[^\]]+\]\);/)[0];vm.runInContext(block+'globalThis.EFFECT_ACTIONS=EFFECT_ACTIONS;',ctx)}
 if(ctx.RECOVERY_UNIT==null)ctx.RECOVERY_UNIT=Number(script.match(/\bRECOVERY_UNIT=(\d+)/)[1]);
 for(const name of ['createNumericEffectAction','numericEffectActionLive','withNumericEffectAction','numericEffectLabel','resolveNumericEffect','copyNumericEffect','numericCopyScore','requestNumericCopy','echoGrantCandidates','echoGrantScore','requestEchoGrant','activatePlacementEcho','clearPlacementEchoReservations','echoDetailText','runEffectAction','retirePreservationOffer','requestRetirePreservation','publicCardLocation','normalizePrototypeRank','ensureRankPrototype','cardPrintedRanks','isAsymmetricRankCard','isJoker','clearCardActiveRank','rankChoiceOptions','projectRankChoiceCards','rankChoicePlanLabel','legalRankChoicePlansForNewMeld','legalRankChoicePlansForAttach','flexibleRoleText','flexibleDetailText','flexibleCardMark','cardIsPublic','flexiblePlacementReady','handPlacementProjection','rankPlanPrefixPossible','collectLegalRankPlans','playerRankChoiceRequired','rankChoicePlanEquivalent','normalizeRequestedRankPlan','canTrigger','cardHasAbility','silenceMaterialRole','materialRank','materialSuit','runRuleWitness','blankStatus','blankMeldStatus','meldOwnerSide','meldMarkValue','consumeMeldMark','canApplySharedMeldStatus','officialStatusBag','officialStatusAllowed','officialStatusValue','setOfficialStatus','applyOfficialStatus','consumeOfficialStatus','clearOfficialStatus','consumeReturnStatuses','prepareTargetReturnEffects','effectReservationLabel','cancelMeldReservations','resolveEffectReservations','battleCards','activeCardLocation','clearInactiveCardStatuses','clearUnstableStatuses','applyCardUnstable','expireOwnerUnstableCards','unstableDetailText','expireOwnerSilences','silenceDurationText']){
  if(typeof ctx[name]==='function')continue;
  const start=script.indexOf(`function ${name}(`);let parens=0,body=-1;
  for(let i=start+`function ${name}`.length;i<script.length;i++){if(script[i]==='(')parens++;else if(script[i]===')')parens--;else if(script[i]==='{'&&parens===0){body=i;break}}
  let depth=0,end=body;for(;end<script.length;end++){if(script[end]==='{')depth++;else if(script[end]==='}'&&--depth===0){end++;break}}
  vm.runInContext(script.slice(start,end),ctx);
 }
}

export function createStatusContext(script,sandbox){const ctx=vm.createContext(sandbox);installStatusRuntime(ctx,script);return ctx}

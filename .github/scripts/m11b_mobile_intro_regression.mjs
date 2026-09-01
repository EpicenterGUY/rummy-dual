import fs from 'node:fs';

const html = fs.readFileSync('index.html','utf8');
const roadmap = fs.readFileSync('ROADMAP.md','utf8');
const doc = fs.readFileSync('docs/ASYMMETRIC_RANK_PROTOTYPE.md','utf8');
const script = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).join('\n');

function ok(condition, message){
  if(!condition) throw new Error(message);
  console.log(`PASS: ${message}`);
}

new Function(script);

ok(html.includes('/* M11B UI3 · asymmetric-rank first exposure / mobile clarity */'), 'M11B mobile clarity CSS layer exists');
ok(html.includes('id="asymRankIntro"') && html.includes('aria-live="polite"'), 'hand zone contains a non-blocking accessible first-exposure panel');
ok(html.includes('id="asymRankIntroClose"') && html.includes('>확인</button>'), 'first-exposure panel has an explicit acknowledgement control');
ok(html.includes('@media(max-width:390px){.asymRankIntro{grid-template-columns:28px minmax(0,1fr)') && html.includes('.asymRankIntro .pixelBtn{grid-column:1/-1;width:100%;min-height:34px'), '390px mobile fallback stacks the acknowledgement into a full-width practical touch target');

ok(script.includes('asymmetricRankIntroSeen:false'), 'new progress defaults keep asymmetric-rank onboarding unseen');
ok(script.includes("asymmetricRankIntroSeen:typeof x.asymmetricRankIntroSeen==='boolean'?x.asymmetricRankIntroSeen:false"), 'legacy progress safely migrates the onboarding flag');
for(const fn of ['asymmetricRankIntroCard','asymmetricRankRuleCopy','shouldShowAsymmetricRankIntro','renderAsymmetricRankIntro','dismissAsymmetricRankIntro']){
  ok(script.includes(`function ${fn}(`), `M11B first-exposure helper exists: ${fn}`);
}
ok(script.includes("return !!(state.player&&!progress.asymmetricRankIntroSeen&&asymmetricRankIntroCard())"), 'intro eligibility requires a real asymmetric card in the player hand and an unseen flag');
ok(script.includes("const c=asymmetricRankIntroCard(),show=!!c&&!progress.asymmetricRankIntroSeen"), 'render path stays dormant while no asymmetric card is actually in hand');
ok(script.includes('progress.asymmetricRankIntroSeen=true;saveProgress();renderAsymmetricRankIntro();return true'), 'acknowledgement persists only after the user explicitly dismisses the explanation');
ok(script.includes("document.getElementById('asymRankIntroClose').onclick=dismissAsymmetricRankIntro"), 'first-exposure acknowledgement is wired to the saved dismiss action');
ok(script.includes("renderHand();if(typeof renderAsymmetricRankIntro==='function')renderAsymmetricRankIntro();renderEnemyHand();"), 'combat render refreshes onboarding after hand contents are known');

ok(script.includes("'↕ 선택'"), 'unresolved asymmetric card surface permanently labels itself as a selectable two-rank card');
ok(!script.includes('`↕ ${p.topRank}/${p.bottomRank}`'), 'old ambiguous slash-only unresolved marker is removed');
ok(script.includes('위·아래 숫자 ${ranks}는 오타가 아닙니다.') && script.includes('두 인쇄값 중 하나를 사용값으로 직접 고릅니다.'), 'first-exposure copy explicitly says the two ranks are intentional and player-chosen');
ok(script.includes('선택한 값은 공개 조합에 있는 동안 고정되고, 손으로 돌아오면 다시 선택할 수 있습니다.'), 'first-exposure copy explains lock and reset lifecycle');

const namedBlock = script.match(/const NAMED=\{([\s\S]*?)\n\};/);
ok(!!namedBlock, 'live NAMED definition block is discoverable');
const liveAsym = [...namedBlock[1].matchAll(/topRank\s*:/g)].length + [...namedBlock[1].matchAll(/bottomRank\s*:/g)].length;
ok(liveAsym===0, 'mobile onboarding still enables zero live asymmetric card definitions');

ok(roadmap.includes('- [x] 모바일에서 상·하단 숫자가 다른 카드가 단순 오타처럼 보이지 않도록 최초 획득/튜토리얼 설명 설계'), 'ROADMAP closes the final M11B UI onboarding item');
ok(doc.includes('## 모바일 / 최초 노출 안내'), 'prototype document records the mobile first-exposure contract');
ok(doc.includes('모달로 전투를 막지 않는다') && doc.includes('가짜 튜토리얼 카드를 기본/고급 튜토리얼에 넣지 않고'), 'prototype doc keeps onboarding non-blocking and avoids fake live tutorial content');
ok(doc.includes('`asymmetricRankIntroSeen`') && doc.includes('사용자가 `확인`한 뒤에만 true'), 'prototype doc locks explicit acknowledgement persistence semantics');

console.log('M11B asymmetric-rank mobile first-exposure regression passed.');

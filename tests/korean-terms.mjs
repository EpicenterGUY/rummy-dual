import fs from 'node:fs';
import vm from 'node:vm';

const html = fs.readFileSync(new URL('../index.html', import.meta.url), 'utf8');
const script = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).join('\n');

function ok(condition, message) {
  if (!condition) throw new Error(message);
  console.log(`PASS: ${message}`);
}

function functionSource(name) {
  const marker = `function ${name}(`;
  const start = script.indexOf(marker);
  if (start < 0) throw new Error(`missing function ${name}`);
  const bodyMarker = script.indexOf('){', start);
  if (bodyMarker < 0) throw new Error(`missing body for ${name}`);
  const brace = bodyMarker + 1;
  let depth = 0;
  for (let i = brace; i < script.length; i++) {
    if (script[i] === '{') depth++;
    else if (script[i] === '}' && --depth === 0) return script.slice(start, i + 1);
  }
  throw new Error(`unterminated function ${name}`);
}

new Function(script);

ok(html.includes('세트와 런으로 폭탄을 키워 스위치를 넘기는 1:1 러미 배틀'), 'top copy uses the Korean core pitch');
ok(html.includes('<span>나 <span id="pCores"'), 'player combat label is 나');
ok(html.includes('<span>상대 <span id="eCores"'), 'opponent combat label is 상대');
ok(html.includes('버스트 준비 · 4번째 카드 +24 · 스위치 반환'), 'SET/BURST battle readout is localized');
ok(html.includes('체인 ${m.chain||0} · 다음 +${chainDamage((m.chain||0)+1)} · 스위치 반환'), 'RUN/CHAIN battle readout is localized');
ok(html.includes('합계 +${p.total} · 스위치 → 상대'), 'multi-attach preview is localized');
ok(html.includes('내 턴 종료 시 폭발 ${state.switchPower} · 반환 필요'), 'DETONATE warning uses 폭발');
ok(html.includes("state.switchPower>=100?'과부하':'',isLethal?'코어 파괴 가능':''"), 'OVERLOAD and CORE LETHAL display labels are localized');
ok(html.includes('초과 피해 ${overkill} 소멸 · 관통 없음'), 'CORE BREAK overkill feedback is localized');
ok(html.includes('<h3>세트 · 버스트</h3>') && html.includes('<h3>런 · 체인</h3>'), 'rules overlay uses official set/run terminology');
ok(html.includes('<h3>스위치 · 폭발</h3>') && html.includes('<h3>러미</h3>'), 'rules overlay uses official switch/explosion/rummy terminology');
ok(html.includes('<div class="term">런 완주</div>'), 'official glossary documents conditional RUN completion');
ok(html.includes('체인 4 이상인 내 런은 내 턴에 선택적으로 「런 완주」'), 'rules help explains the newly accepted RUN completion rule');
ok(!html.includes('CORE BREAK · 초과 피해 LOST · 다음 CORE 관통 0'), 'legacy mixed-language CORE note is gone');
ok(!html.includes('BURST READY · 4번째 카드 +24 · SWITCH 반환'), 'legacy mixed-language BURST readout is gone');
ok(!html.includes('중립 · DETONATE 없음'), 'legacy DETONATE alert is gone');

const ctx = vm.createContext({});
vm.runInContext(functionSource('switchName'), ctx);
ok(ctx.switchName('player') === '나' && ctx.switchName('enemy') === '상대', 'shared side-name helper returns Korean player-facing labels');

console.log('RUMMY//DUEL Korean terminology pass 1 regressions passed.');

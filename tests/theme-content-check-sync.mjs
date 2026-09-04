import fs from 'node:fs';
const doc=fs.readFileSync(new URL('../docs/THEME_GROUPS.md',import.meta.url),'utf8');
function ok(v,m){if(!v)throw new Error(m);console.log(`PASS: ${m}`)}
const start=doc.indexOf('# 콘텐츠 확장 전 체크');
ok(start>=0,'canonical theme doc keeps the content-expansion checklist');
const nextTop=doc.indexOf('\n# ',start+1),section=doc.slice(start,nextTop>=0?nextTop:doc.length);
ok(!/^\s*- \[ \]/m.test(section),'completed content-expansion checklist has no stale unchecked items inside its own section');
ok(section.includes('M8 첫 ~50 네임드의 선택/복사/타이밍 안정화')&&section.includes('공용 resumable choice'),'canonical checklist records named-card stabilization evidence');
ok(section.includes('`themeId`/조합 `themeMeta`')&&section.includes('`namedSlot()`'),'canonical checklist records theme metadata/slot invariant');
ok(section.includes('같은 정규 슬롯 후보 중 하나만 물질화'),'canonical checklist records one-variant-per-slot behavior');
ok(section.includes('`themeAIAttachBias` / `themeAIRecoveryBias`'),'canonical checklist records shared AI theme heuristics');
ok(section.includes('모든 2테마 조합')&&section.includes('슬롯 중복 0'),'canonical checklist records mixed-theme simulation coverage');
ok(section.includes('전체 네임드 풀 20% 미만')&&section.includes('현재 테마 카드 풀 과반 미만'),'canonical checklist records direct-power ratio guard');
console.log('Canonical theme content checklist sync regression passed.');

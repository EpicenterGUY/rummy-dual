import fs from 'node:fs';
const root=new URL('../',import.meta.url),plan=JSON.parse(fs.readFileSync(new URL('design/cards-v3.json',root),'utf8'));
const names={common:'공용 네임드','v-signal':'V-SIGNAL','zero-sight':'ZERO-SIGHT','point-blank':'POINT-BLANK',joker:'조커','season-bloom':'SEASON-BLOOM 신규 설계'};
const statuses={preserved:'유지','implemented-wave1':'1차 구현','implemented-wave2':'2차 구현','implemented-wave3':'3차 구현','implemented-wave4':'4차 구현','implemented-wave5':'5차 구현','implemented-wave6':'6차 구현',planned:'구현 대기'};
const escape=s=>String(s).replaceAll('|','\\|').replaceAll('\n',' ');
export function render(){
 const implemented=plan.existingCards.filter(r=>r.implementation.startsWith('implemented-')).length,pending=plan.existingCards.filter(r=>r.implementation==='planned').length;
 const lines=['# 전체 카드 효과 개편 설계표','',`기준: PR #35의 ${plan.sourceCommit.slice(0,7)}. 이 파일은 design/cards-v3.json에서 생성한다.`, '',
 '기존 122종을 모두 검토했다. 69종을 재설계하고 53종은 고유한 기능을 유지한다. 기존 카드 중 괴짜형은 25종(20.5%)이다. **구현 대기 효과는 현재 게임에 적용되지 않았다.**', '',
 `현재 PR의 적용 범위는 개편 ${implemented}종이며, 기존 카드 추가 ${pending}종과 신규 SEASON-BLOOM 24종은 설계 완료·구현 대기다. 카드군 전체 개편 완료는 모든 예정 카드의 구현·선택 UI·AI·혼합 회귀를 마쳤을 때만 선언한다.`,'',
 '카드 숫자는 HP/위력의 사용자 표시 단위다. 순환·재배치·대체·예약·상태 판정은 [공통 계약](STATUS_3_CONTRACT.md), 계절은 [SEASON-BLOOM 계약](SEASON_BLOOM_3.md)을 따른다. 다음 수치는 실전 밸런스 검증 전 설계값이다.',''];
 for(const [group,title] of Object.entries(names)){
  const rows=(group==='season-bloom'?plan.newThemeCards:plan.existingCards).filter(r=>r.theme===group);
  lines.push(`## ${title} · ${rows.length}종`,'','| 슬롯 / ID | 카드 | 유형 | 적용 상태 | 최종 목표 효과 |','|---|---|---|---|---|');
  for(const r of rows)lines.push(`| ${r.slot} / ${r.id} | ${escape(r.name)} | ${r.category} | ${statuses[r.implementation]} | ${escape(r.targetEffect)} |`);
  lines.push('');
 }
 return lines.join('\n')+'\n';
}
if(process.argv.includes('--check')){
 if(fs.readFileSync(new URL('docs/CARD_REDESIGN_3.md',root),'utf8')!==render())throw new Error('Run node tools/render-card-plan.mjs to refresh the card table');
}else fs.writeFileSync(new URL('docs/CARD_REDESIGN_3.md',root),render());

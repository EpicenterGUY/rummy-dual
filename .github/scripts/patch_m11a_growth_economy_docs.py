from pathlib import Path
import re

root = Path(__file__).resolve().parents[2]
roadmap_path = root / 'ROADMAP.md'
plan_path = root / 'docs' / 'ROGUELIKE_MASTER_PLAN.md'
test_path = root / 'tests' / 'm11a-growth-economy.mjs'

roadmap = roadmap_path.read_text(encoding='utf-8')
pattern = r'(?m)^- \[ \] 카드 제거와 네임드 교체의 경제적 가치 비교\s*$'
replacement = '''- [x] 카드 제거와 네임드 교체의 경제적 가치 비교
  - 현재 30장(일반 슬롯 29 + 조커 1) 기준 4,000-seed 구조 실험에서 6장 손패 조합 가능률은 32.48%, 서로 겹치지 않는 2조합 잠재력은 0.68%였다.
  - 동일 rank+suit 네임드 교체는 덱 크기와 숫자/무늬 구조를 그대로 보존하므로 구조 변화량이 0이다. 교체의 경제 가치는 카드 효과와 희소도에서 나온다.
  - 조커를 제외한 일반 슬롯 1장 제거 평균은 조합 가능률 +0.25%p, 평균 합법 3장 조합 수 +0.012였지만 2조합 잠재력은 -0.13%p였다.
  - 슬롯별 편차도 커서 H10 제거는 조합 가능률 +2.25%p, S7 제거는 -2.38%p였다. 제거는 덱 압축이 되기도 하고 핵심 RUN 축을 파괴하기도 한다.
  - 따라서 제거는 동일 슬롯 교체의 단순 상위 보상이 아니라 별도 희소 성장 행동으로 분리하고, 확정 전에 덱 구조 변화 경고/분석을 보여 준다. 정확한 비용·희귀도·노드 등급은 실전 M12 데이터 이후 확정한다.'''
roadmap2, count = re.subn(pattern, replacement, roadmap, count=1)
if count != 1:
    raise SystemExit(f'ROADMAP growth-economy anchor count={count}')
roadmap_path.write_text(roadmap2, encoding='utf-8')

plan = plan_path.read_text(encoding='utf-8')
plan = plan.replace('Updated: 2026-08-30', 'Updated: 2026-09-01', 1)
heading = '## 14. 성장 경제 구조 실험 v1 — 제거 vs 동일 슬롯 교체'
if heading not in plan:
    plan = plan.rstrip() + '''\n\n## 14. 성장 경제 구조 실험 v1 — 제거 vs 동일 슬롯 교체\n\n실전 상점 가격이나 드롭 등급을 정하기 전에, `experiments/m11a-growth-economy.mjs`로 **덱 구조 자체의 가치만 분리**해 측정했다. 실험은 현재 `index.html`의 실제 세트/런 판정을 직접 읽으며, 현재 기본 30장 구조인 `일반 rank+suit 슬롯 29장 + 조커 1장`에서 결정적 4,000 seed의 6장 손패를 비교한다. 조커 제거는 별도 경제축으로 보고 이번 제거 스윕에서 제외한다.\n\n기준 결과:\n\n- 기본 30장: 조합 가능 손패 32.48%, 세트 포함 20.03%, 런 포함 21.88%, 서로 겹치지 않는 2조합 잠재력 0.68%, 손패당 평균 합법 3장 조합 0.551.\n- 동일 슬롯 네임드 교체: 덱 크기와 원본 rank+suit 슬롯이 같으므로 위 구조 지표 변화량은 정확히 0. 경제 가치는 구조가 아니라 **네임드 효과와 희소도**에서 나온다.\n- 일반 슬롯 1장 제거 평균: 조합 가능률 32.73%로 +0.25%p, 평균 합법 조합 0.563으로 +0.012였지만 2조합 잠재력은 0.55%로 -0.13%p였다.\n- 제거 효과는 슬롯별로 크게 달랐다. H10 제거는 조합 가능률 34.73%(+2.25%p), S7 제거는 30.10%(-2.38%p)였다. 즉 주변 슬롯 제거는 남은 구조를 농축할 수 있지만, 중앙 RUN 축 제거는 오히려 덱의 조합성을 무너뜨릴 수 있다.\n\n### M11A 경제 결정\n\n- **제거를 동일 슬롯 교체의 단순 상위 업그레이드로 가격 책정하지 않는다.**\n- 동일 슬롯 교체는 기본 성장축으로 유지한다. 덱 구조를 보존하므로 보상 후보 알고리즘과 현재 `replace-slot-variant` 계약에 그대로 맞는다.\n- 제거는 `reward` 교체 후보 풀과 섞지 않고 **별도의 희소 성장 행동**으로 둔다. 상점/이벤트 등 명시적인 출처에서 제공하는 방향을 우선한다.\n- 제거 확정 UI에는 현재 덱빌더의 숫자/무늬/세트/런 분석을 재사용해 제거 전후 구조 변화를 보여 주고, 핵심 RUN 축 또는 다중 조합 잠재력이 감소하면 경고한다.\n- 조커 제거는 일반 슬롯 제거와 같은 가격표를 쓰지 않고 별도 설계 대상으로 남긴다.\n- 정확한 골드 비용, 등장 확률, 일반/엘리트/보스별 보상 등급은 이 구조 실험만으로 잠그지 않는다. M12 실전 전투 데이터와 실제 런 경제가 생긴 뒤 확정한다.\n\n이 결정은 ROADMAP의 `카드 제거와 네임드 교체의 경제적 가치 비교`를 닫지만, `보상 희귀도/전투 등급`과 실제 가격 수치는 계속 미확정으로 남긴다.\n'''
plan_path.write_text(plan, encoding='utf-8')

test = test_path.read_text(encoding='utf-8')
old = "assert.match(roadmap,/카드 제거와 네임드 교체의 경제적 가치 비교/,'roadmap must keep the growth-economy decision');\nassert.match(plan,/동일 슬롯 교체 UI 계약 v1/,'master plan must keep the replacement contract before economy conclusions');"
new = "assert.match(roadmap,/- \\[x\\] 카드 제거와 네임드 교체의 경제적 가치 비교/,'roadmap must close the structural removal-versus-replacement comparison');\nassert.match(roadmap,/H10 제거.*\\+2\\.25%p.*S7 제거.*-2\\.38%p/s,'roadmap must retain the measured slot-variance warning');\nassert.match(plan,/동일 슬롯 교체 UI 계약 v1/,'master plan must keep the replacement contract before economy conclusions');\nassert.match(plan,/성장 경제 구조 실험 v1/,'master plan must record the structural economy experiment');\nassert.match(plan,/제거를 동일 슬롯 교체의 단순 상위 업그레이드로 가격 책정하지 않는다/,'removal must remain a separate scarce growth action rather than a flat stronger replacement');"
if old not in test:
    raise SystemExit('growth-economy test anchor missing')
test_path.write_text(test.replace(old, new, 1), encoding='utf-8')

print('patched ROADMAP, roguelike master plan, and M11A economy regression')

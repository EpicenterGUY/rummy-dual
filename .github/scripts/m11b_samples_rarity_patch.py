from pathlib import Path

doc=Path('docs/ASYMMETRIC_RANK_PROTOTYPE.md')
road=Path('ROADMAP.md')
d=doc.read_text()
r=road.read_text()
anchor='숫자 차이가 작아도 두 값이 서로 다른 세트/런 핵심 구간을 동시에 덮으면 한 단계 높게 취급할 수 있다. 반대로 가장자리 A/K처럼 런 창이 좁아도 자동으로 등급을 낮추지는 않는다. 최종 판단은 실제 M11B 표본의 세트·런 성공률로 보정한다.\n'
extra='''\n#### 권장 등장 등급 — 아직 런타임 미구현\n\n이 등급은 현재 게임에 새 희귀도 시스템을 추가하는 것이 아니라, 향후 로그라이크 보상 풀을 설계할 때의 **제작 권고 메타**다. 실제 명칭·확률·색상은 M11A 보상 구조 확정 전까지 구현하지 않는다.\n\n- `소` — 일반 후보. 숫자 차이가 작고 효과 예산도 작을 때만 일반 보상 풀 진입 가능.\n- `중` — 고급 후보. 선택값에 따른 역할 분화나 작은 비용을 전제로 한다.\n- `대` — 희귀 후보. 높은 선택 유연성이 이미 주효과이므로 추가 범용 보상은 최소화한다.\n- `극단` — 특수·이벤트 후보. 일반 보상 풀의 상시 등장보다 제한적 획득을 우선 검토하며 실제 패널티를 반드시 가진다.\n\n'''
if '#### 권장 등장 등급 — 아직 런타임 미구현' not in d:
    if anchor not in d: raise SystemExit('rarity guidance anchor missing')
    d=d.replace(anchor,anchor+extra,1)
doc.write_text(d)
old='- [x] 숫자 차이가 큰 카드가 단순 상위호환이 되지 않도록 효과 예산 / 희귀도 / 패널티 기준 수립 — Δ1~2 소 / Δ3~4 중 / Δ5~6 대 / Δ7+ 극단의 제작 등급을 잠그고, Δ5+는 상시 양의 효과를 금지하며 실제 템포 비용/패널티를 요구. 한 인쇄값은 반드시 baseRank를 보존하고 직접 누적 위력은 샘플 12장 중 1장만 허용'
new=old+' · 권장 등장 등급은 소=일반 후보 / 중=고급 후보 / 대=희귀 후보 / 극단=특수·이벤트 후보로만 문서화하며 현재 런타임에는 희귀도 시스템을 추가하지 않음'
if old in r and new not in r:r=r.replace(old,new,1)
road.write_text(r)
print('M11B sample rarity guidance locked')

from pathlib import Path

p = Path('ROADMAP.md')
text = p.read_text()
anchor = '## L10N1 — 한국어 용어 / 텍스트 정리\n'
if anchor not in text:
    raise SystemExit('L10N1 anchor not found')
section = '''## UI2 — 전술 카드테이블 비주얼 리디자인\n도박/카지노/배팅 사이트로 읽히는 시각 문법을 줄이고, 카드와 조합이 주인공인 모바일 전략 카드게임/보드게임 톤으로 전환한다. 규칙과 전투 판정은 변경하지 않는다.\n\n### P1 — 카지노 톤 제거 + 기본 시각 체계 재설계\n- [x] 기존 UI의 카지노 인상 원인 감사 — 검정/금색/청록 네온, 두꺼운 이중 테두리, 상시 펄스, 과도한 패널 강조\n- [x] 기본 팔레트를 무채도 슬레이트 + 종이 카드 + 절제된 청록/웜 포인트로 교체\n- [x] 패널/버튼을 두꺼운 픽셀 박스에서 얕은 테두리·낮은 그림자의 앱 카드형으로 완화\n- [x] 금색 행동 버튼을 금색 면 채움 대신 중성 배경 + 웜 포인트 테두리로 축소\n- [x] 시작창 히어로를 네온 패널에서 종이 보드/카드 표면으로 재구성\n- [x] 스위치 보드를 전술 상태판으로 정리하고 평상시 소유권 펄스 제거\n- [x] 위험 단계가 실제로 상승할 때만 게이지가 웜/레드 계열로 변하도록 제한\n- [x] 치명/폭발 임박 상태의 반복 글로우·잭팟형 펄스를 제거하고 정적 경고 우선\n- [x] 트럼프 카드 프레임의 금색 광택을 낮추고 종이 질감/중성 프레임으로 조정\n- [x] reduced-motion 대응 및 UI2 시각 회귀 테스트 추가\n\n### P2 — 정보 위계 / 공간 정리\n- [ ] 상단 상태/캐릭터/메뉴 밀도 축소 및 모바일 우선 재배치\n- [ ] 스위치 핵심 정보와 보조 문구를 1차/2차 정보로 분리\n- [ ] 공개 조합과 손패 사이 여백·높이·스크롤 밀도 재조정\n- [ ] 전투 기록 기본 접힘/요약 방식 검토\n- [ ] 선택 가능 카드·붙이기 가능 조합 강조를 발광보다 테두리/위치 변화 중심으로 통일\n- [ ] 360~480px 실제 모바일 폭에서 버튼/상태 문구 잘림 회귀 점검\n\n### P3 — 아트/브랜드 마감\n- [ ] 카드 아이콘/네임드 프레임과 새 UI 팔레트 통일\n- [ ] 시작창/결과창/도감의 시각 언어 통일\n- [ ] 튜토리얼 coach를 동일한 전술 보드 톤으로 최종 마감\n- [ ] V-SIGNAL 등 테마군은 기본 UI 위에 테마 포인트만 얹고 카지노형 네온 남발 금지\n\n'''
text = text.replace(anchor, section + anchor, 1)
old = '''## Current next work\n1. L10N1: lock and apply the Korean user-facing terminology before tutorial copy proliferates; keep code-internal English identifiers stable.\n2. UX1 P1: start screen + first-run prompt + shared tutorial controller are live; next connect deterministic basic controls → 세트 → 런 → 붙이기 → 상대 조합 → 스위치 → 러미 scenarios to the real engine.\n3. Continue the remaining M8 choice/copy/timing audit in parallel; do not begin large M9/content expansion until the first ~50 named-card behaviors and UX1 P1 are both stable.\n'''
new = '''## Current next work\n1. UI2 P2: after the first casino-tone reset, reduce HUD density and clarify information hierarchy without weakening combat readability.\n2. UX1 P1: connect deterministic basic controls → 세트 → 런 → 붙이기 → 상대 조합 → 스위치 → 러미 scenarios to the real engine.\n3. L10N1 + M8: continue remaining text cleanup and named-card choice/copy/timing audit in parallel; do not begin large M9/content expansion until the first ~50 named-card behaviors and UX1 P1 are both stable.\n'''
if old not in text:
    raise SystemExit('current next work block not found')
text = text.replace(old, new, 1)
p.write_text(text)

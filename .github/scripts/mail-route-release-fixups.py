from pathlib import Path

REPLACEMENTS = {
    "공개된 동안 내 우편이 내 세트 목적지에 지정 도착하면 턴당 1회 카드 1장을 뽑는다.": "공개된 동안 내 우편이 내 세트 목적지에 지정 도착하면 턴당 1회 카드 1장을 뽑는다.",
    "공개된 동안 내 우편이 내 목적지에 지정 도착하면 그 목적지의 봉인 1을 제거하고, 봉인이 없으면 고정을 해제하며, 둘 다 없으면 보호 1을 부여한다. 턴당 1회.": "공개된 동안 내 우편이 내 목적지에 지정 도착하면 그 목적지의 봉인 1을 제거하고, 봉인이 없으면 고정을 해제하며, 둘 다 없으면 보호 1을 부여한다. 이 효과는 턴당 1회만 발동한다.",
    "우편 상태인 이 카드가 런 목적지에 지정 도착하면 다른 공개 조합의 내 우편 카드 1장을 무료 회수할 수 있다. 기본 반환 제한은 유지한다.": "우편 상태인 이 카드가 런 목적지에 지정 도착하면 다른 공개 조합의 내 우편 카드 1장을 무료 회수할 수 있다. 기본 반환 제한은 유지한다.",
    "이 카드를 조합에 사용하면 자신을 우편으로 발송한다. 목적지에 지정 도착하면 현재 코어 4 회복 + 보호막 8.": "이 카드를 조합에 사용하면 자신을 우편으로 발송한다. 목적지에 지정 도착하면 현재 코어를 4 회복하고 보호막 8을 얻는다.",
    "이 카드를 조합에 사용하면 자신을 우편으로 발송한다. 상대 공개 조합에 도착했지만 지정 도착이 아니라면 상대에게 취약 1.": "이 카드를 조합에 사용하면 자신을 우편으로 발송한다. 상대 공개 조합에 도착했지만 지정 도착이 아니라면 상대에게 취약 1을 부여한다.",
}

TARGETS = [
    Path('.github/scripts/mail-route-full-pool-patch.py'),
    Path('index.html'),
    Path('ROADMAP.md'),
    Path('docs/THEME_GROUPS.md'),
    Path('docs/THEME_FULL_POOL_PLAN.md'),
    Path('tests/mail-route-full-pool.mjs'),
]

changed = []
for path in TARGETS:
    if not path.exists():
        continue
    text = path.read_text(encoding='utf-8')
    original = text
    for old, new in REPLACEMENTS.items():
        if old != new:
            text = text.replace(old, new)
    if text != original:
        path.write_text(text, encoding='utf-8')
        changed.append(str(path))

print('MAIL-ROUTE release wording fixups:', ', '.join(changed) if changed else 'already clean')

from pathlib import Path
import runpy

patch = Path('.github/scripts/card-expansion-wave01a-patch.py')
text = patch.read_text(encoding='utf-8')

# Current main wording for pre-existing anchor cards.
text = text.replace(
    "'S7':{n:'검은 탄환',t:'blackBullet',d:'상대 공개 조합에 붙여 스위치를 반환하면 누적 위력이 10 증가한다.'},",
    "'S7':{n:'검은 탄환',t:'blackBullet',d:'상대 공개 조합에 붙여 스위치를 반환할 때 누적 위력이 10 증가한다.'},",
)
text = text.replace(
    "'S3':{n:'반품 청구서',t:'returnIfIgnored',d:'상대가 버림패에서 가져간 뒤 그 턴 조합에 사용하지 못하면, 턴 종료에 원래 주인의 덱 아래로 돌아간다.'},",
    "'S3':{n:'쥐구멍',t:'returnIfIgnored',d:'버렸는데 다음 내 턴까지 버림패에 남아 있으면 손으로 돌아온다. 상대가 가져가면 그 턴에는 조합에 사용할 수 없다.'},",
)

# Keep engine constants out of Korean-facing template literals.
text = text.replace(
    "detail:`내 ${x.meld.type}${x.meld.type==='RUN'?` · CHAIN ${x.meld.chain||0}`:''}`,entry:x",
    "detail:x.meld.type==='RUN'?`내 런 · 체인 ${x.meld.chain||0}`:'내 세트',entry:x",
)

# Wave 01A expands the live/player pool only. Existing roguelike encounter
# compositions and reward-ranking contracts remain unchanged in this wave.
text = text.replace("if \"'VSHA','VSC6'\" not in text:", "if False:")
text = text.replace("if \"'ZSH4','ZSS7','PBCA','PBS3'\" not in text:", "if False:")
text = text.replace("if \"vFirstBroadcast:['combo','cycle']\" not in text:", "if False:")
text = text.replace("if \"'point-blank':Object.freeze(['pbBreachOrder'])\" not in text:", "if False:")

patch.write_text(text, encoding='utf-8')
runpy.run_path(str(patch), run_name='__main__')

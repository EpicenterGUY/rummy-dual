from pathlib import Path
import runpy

patch = Path('.github/scripts/card-expansion-wave01a-patch.py')
text = patch.read_text(encoding='utf-8')

# The live card text changed during earlier balance passes; normalize the two
# exact anchors used by the Wave 01A patch to the current main-branch wording.
text = text.replace(
    "'S7':{n:'검은 탄환',t:'blackBullet',d:'상대 공개 조합에 붙여 스위치를 반환하면 누적 위력이 10 증가한다.'},",
    "'S7':{n:'검은 탄환',t:'blackBullet',d:'상대 공개 조합에 붙여 스위치를 반환할 때 누적 위력이 10 증가한다.'},",
)
text = text.replace(
    "'S3':{n:'반품 청구서',t:'returnIfIgnored',d:'상대가 버림패에서 가져간 뒤 그 턴 조합에 사용하지 못하면, 턴 종료에 원래 주인의 덱 아래로 돌아간다.'},",
    "'S3':{n:'쥐구멍',t:'returnIfIgnored',d:'버렸는데 다음 내 턴까지 버림패에 남아 있으면 손으로 돌아온다. 상대가 가져가면 그 턴에는 조합에 사용할 수 없다.'},",
)
patch.write_text(text, encoding='utf-8')
runpy.run_path(str(patch), run_name='__main__')

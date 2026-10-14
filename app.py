# 메인 실행 파일 app.py
# streamlit_app.py의 전체 기능을 그대로 실행하도록 연결된 진입점 파일입니다.
import runpy
from pathlib import Path

target_file = Path(__file__).parent / "streamlit_app.py"
runpy.run_path(str(target_file), run_name="__main__")

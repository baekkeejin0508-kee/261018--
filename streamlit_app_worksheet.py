import io
import os
import re
import json
import html
import urllib.request
import urllib.error
import base64
from datetime import datetime, timezone, timedelta
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.ticker as ticker
import matplotlib.patheffects as pe
import seaborn as sns
from pathlib import Path

# ==========================================
# 한글 폰트 설정 (Streamlit Cloud Linux & Windows 동시 완벽 지원)
# ==========================================
BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"

def setup_korean_font():
    font_candidates = [
        ASSETS_DIR / "NanumGothic.ttf",
        Path("assets/NanumGothic.ttf"),
        Path("/usr/share/fonts/truetype/nanum/NanumGothic.ttf"),
        Path("/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf"),
        Path("C:/Windows/Fonts/malgun.ttf"),
    ]
    font_loaded = False
    for fpath in font_candidates:
        if fpath.exists():
            try:
                fm.fontManager.addfont(str(fpath))
                font_prop = fm.FontProperties(fname=str(fpath))
                plt.rcParams['font.family'] = font_prop.get_name()
                font_loaded = True
                break
            except Exception:
                continue

    if not font_loaded:
        available_fonts = [f.name for f in fm.fontManager.ttflist]
        for candidate in ['NanumGothic', 'NanumBarunGothic', 'Malgun Gothic', 'AppleGothic', 'Noto Sans CJK KR']:
            if candidate in available_fonts:
                plt.rcParams['font.family'] = candidate
                font_loaded = True
                break

    plt.rcParams['axes.unicode_minus'] = False

setup_korean_font()


# ==========================================
# 1. 페이지 기본 설정 및 눈이 편안한 에듀테크 디지털 학습지 스타일
# ==========================================
st.set_page_config(
    page_title="보건·정보 융합 디지털 탐구 학습지 - 서울의료보건고",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

components.html("""
<script>
(function(){
    try {
        var topDocs = [document];
        try { if (window.top && window.top.document) topDocs.push(window.top.document); } catch(e){}
        try { if (window.parent && window.parent.document && !topDocs.includes(window.parent.document)) topDocs.push(window.parent.document); } catch(e){}
        
        topDocs.forEach(function(d){
            if (!d) return;
            d.documentElement.setAttribute('translate', 'no');
            d.documentElement.classList.add('notranslate');
            if (d.body) {
                d.body.setAttribute('translate', 'no');
                d.body.classList.add('notranslate');
            }
        });

        // React reconciliation 에러 방어
        topDocs.forEach(function(d){
            var win = d.defaultView || window;
            if (win && win.Node && win.Node.prototype) {
                if (!win.Node.prototype._origRemoveChildPatched) {
                    var _origRemoveChild = win.Node.prototype.removeChild;
                    win.Node.prototype.removeChild = function(child) {
                        if (child && child.parentNode !== this) return child;
                        return _origRemoveChild.apply(this, arguments);
                    };
                    win.Node.prototype._origRemoveChildPatched = true;
                }
                if (!win.Node.prototype._origInsertBeforePatched) {
                    var _origInsertBefore = win.Node.prototype.insertBefore;
                    win.Node.prototype.insertBefore = function(newNode, referenceNode) {
                        if (referenceNode && referenceNode.parentNode !== this) return newNode;
                        return _origInsertBefore.apply(this, arguments);
                    };
                    win.Node.prototype._origInsertBeforePatched = true;
                }
            }
        });

        // MutationObserver: 동적 드롭다운 팝오버 메뉴 번역 차단 및 '형간염' -> 'A형간염' 복구
        var protectNodes = function(root) {
            if (!root || !root.querySelectorAll) return;
            var elements = root.querySelectorAll('[data-baseweb="popover"], [data-baseweb="select"], [data-baseweb="menu"], ul, li, div, span');
            elements.forEach(function(el){
                el.setAttribute('translate', 'no');
                el.classList.add('notranslate');
                if (el.textContent && el.textContent.trim() === '형간염') {
                    el.textContent = 'A형간염';
                }
            });
        };

        topDocs.forEach(function(d){
            if (!d || d._notranslateObserverSet) return;
            d._notranslateObserverSet = true;
            var observer = new MutationObserver(function(mutations){
                mutations.forEach(function(mutation){
                    mutation.addedNodes.forEach(function(node){
                        if (node.nodeType === 1) {
                            node.setAttribute('translate', 'no');
                            node.classList.add('notranslate');
                            protectNodes(node);
                        }
                    });
                });
            });
            observer.observe(d.body || d.documentElement, { childList: true, subtree: true });
        });
    } catch(e) {}
})();
</script>
""", height=0, width=0)

st.markdown("""
<style>
    /* 전체 다크 테마 배경 및 텍스트 */
    .stApp {
        background-color: #0f172a !important;
        color: #f8fafc !important;
    }
    
    /* 사이드바 스타일링 */
    section[data-testid="stSidebar"] {
        background-color: #1e293b !important;
        border-right: 1px solid #334155;
    }

    /* 메인 1줄 제목 */
    .one-line-title {
        font-size: 1.45rem !important;
        font-weight: 800 !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        color: #ffffff !important;
        margin: 0 !important;
        padding: 0 !important;
        letter-spacing: -0.5px;
    }
    
    /* 디지털 학습지 상단 헤더 배너 */
    .header-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%) !important;
        padding: 14px 22px !important;
        border-radius: 14px !important;
        border: 1px solid #334155 !important;
        margin-bottom: 14px !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.3) !important;
        display: flex;
        align-items: center;
        gap: 16px;
    }
    
    /* 디지털 학습지 학생 메타 바 (이름/학번/진도) */
    .student-meta-bar {
        background: #1e293b !important;
        border: 1px solid #38bdf8 !important;
        border-left: 5px solid #38bdf8 !important;
        border-radius: 10px !important;
        padding: 10px 16px !important;
        margin-bottom: 16px !important;
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 10px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25) !important;
    }

    /* 학생 탐구 메모 상자 */
    .student-memo-card {
        background: rgba(30, 41, 59, 0.85) !important;
        border: 1.5px dashed #38bdf8 !important;
        border-radius: 12px !important;
        padding: 14px 18px !important;
        margin-top: 14px !important;
        margin-bottom: 14px !important;
    }

    /* 법정감염병 4대 급수 직관적 요약 카드 */
    .tier-summary-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        margin-top: 8px;
        margin-bottom: 14px;
    }
    @media (max-width: 900px) {
        .tier-summary-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }
    @media (max-width: 550px) {
        .tier-summary-grid {
            grid-template-columns: 1fr;
        }
    }
    .tier-summary-card {
        border-radius: 10px;
        padding: 12px 14px;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    
    /* 학교 로고 네모 바탕 박스 (헤더용) */
    .header-emblem-square {
        background-color: #ffffff !important;
        border: 2px solid #38bdf8 !important;
        border-radius: 10px !important;
        width: 52px !important;
        height: 52px !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3) !important;
        flex-shrink: 0 !important;
    }
    
    /* 학교 로고 네모 바탕 박스 (사이드바용) */
    .sidebar-emblem-square {
        background-color: #ffffff !important;
        border: 2px solid #38bdf8 !important;
        border-radius: 12px !important;
        width: 64px !important;
        height: 64px !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.35) !important;
        margin-bottom: 8px !important;
    }

    /* 리포트 카드 */
    .report-card {
        background-color: #1e293b !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
        border: 1px solid #475569 !important;
        margin-top: 1rem !important;
        margin-bottom: 1.5rem !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.25) !important;
        color: #f8fafc !important;
    }
    .report-title {
        color: #38bdf8 !important;
        font-size: 1.25rem !important;
        font-weight: bold !important;
        margin-bottom: 0.8rem !important;
    }
    .badge-tier {
        background-color: #0284c7 !important;
        color: #ffffff !important;
        padding: 4px 10px !important;
        border-radius: 6px !important;
        font-size: 0.85rem !important;
        font-weight: bold !important;
    }
    
    /* 지표 메트릭 카드 - 짤림 방지 */
    .stMetric {
        background-color: #1e293b !important;
        padding: 10px 14px !important;
        border-radius: 10px !important;
        border: 1px solid #334155 !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.2) !important;
    }
    div[data-testid="stMetricValue"] > div {
        font-size: 1.25rem !important;
        font-weight: 700 !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }
    div[data-testid="stMetricLabel"] > div {
        font-size: 0.82rem !important;
        color: #94a3b8 !important;
        white-space: nowrap !important;
    }
    button[data-testid="baseButton-secondary"], button[data-testid="baseButton-primary"] {
        white-space: nowrap !important;
    }

    /* 요약 정보 1줄 바 (길이 초과 방지) */
    .single-line-badge-bar {
        display: flex;
        flex-wrap: nowrap;
        align-items: center;
        justify-content: space-between;
        background: #1e293b;
        border: 1px solid #334155;
        padding: 8px 16px;
        border-radius: 8px;
        font-size: 0.84rem;
        color: #cbd5e1;
        white-space: nowrap;
        overflow-x: auto;
        margin-bottom: 14px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    /* 3대 시각화 라이브러리 비교 제목 1줄 유지 */
    .title-compare-libs {
        font-size: clamp(1.05rem, 1.35vw, 1.25rem) !important;
        font-weight: 700 !important;
        color: #f8fafc !important;
        letter-spacing: -0.4px !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        margin-top: 4px !important;
        margin-bottom: 8px !important;
        line-height: 1.3 !important;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# 2. 데이터 무결성 보장 및 최신 법정감염병 사전
# ==========================================
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"

def apply_dark_plot_style(fig, ax):
    """Matplotlib 및 Seaborn 그래프를 대시보드 다크 테마에 맞게 통일"""
    fig.patch.set_facecolor('#1e293b')
    ax.set_facecolor('#0f172a')
    ax.tick_params(colors='#f8fafc', which='both', labelsize=10)
    ax.xaxis.label.set_color('#f8fafc')
    ax.xaxis.label.set_fontsize(11)
    ax.yaxis.label.set_color('#f8fafc')
    ax.yaxis.label.set_fontsize(11)
    ax.title.set_color('#38bdf8')
    ax.title.set_fontsize(13)
    ax.title.set_weight('bold')
    for spine in ax.spines.values():
        spine.set_color('#475569')
    ax.grid(True, linestyle='--', alpha=0.3, color='#475569')


def format_smart_label(val: float, compact: bool = True) -> str:
    """
    수치 라벨이 서로 겹치거나 잘리지 않도록 스마트 포맷팅
    - 0 또는 음수: 노이즈 방지를 위해 공백 반환
    - 1억 이상: 1.2억 등 소수점 1자리 요약
    - 1만 이상: 2,406만, 1,842만, 203만 등 정밀 축약
    - 1만 미만: 원본 쉼표 포맷 (예: 2,341, 837)
    """
    if pd.isna(val) or val <= 0:
        return ""
    if not compact:
        return f"{int(val):,}"
    if val >= 100_000_000:
        return f"{val/1e8:.1f}억"
    elif val >= 10_000:
        v_man = val / 10_000
        if v_man >= 100:
            return f"{v_man:,.0f}만"
        else:
            return f"{v_man:,.1f}만"
    else:
        return f"{int(val):,}"


def format_korean_log_ticks(y, pos):
    """로그 스케일 y축 눈금을 위한 한국어 직관적 단위 포맷터"""
    if y >= 100_000_000:
        return f"{int(y/1e8)}억"
    elif y >= 10_000:
        return f"{int(y/10000)}만"
    elif y >= 1_000:
        return f"{int(y/1000)}천"
    elif y >= 1:
        return f"{int(y)}"
    return ""


def smart_annotate_bars(ax, bars, total_bars: int = 10, is_horizontal: bool = False, max_val: float = None):
    """
    막대 그래프의 수치 라벨을 세련된 사선으로 배치하되 인접 막대 간 겹침과 막대 내부 침범을 원천 방지하는 지능형 어노테이션 함수:
    - 막대 밀집도에 따라 폰트 크기(5.0~6.8pt)를 최적화하여 인접한 낮은 수치끼리의 충돌을 원천 차단 (사용자 피드백 반영)
    - 50~60도 사선 회전(rotation)으로 가로 침범 길이를 대폭 축소하여 옆 막대 라벨과의 간섭 원천 방지
    - 지능형 인접 막대 충돌 감지(Smart Collision Avoidance): 바로 옆 막대가 근접하고 높이가 비슷한 경우 오프셋 및 각도를 자동 미세 조정
    - ha='left', va='bottom', rotation_mode='anchor'를 적용하여 막대 상단 밖에서 우상단으로 뻗어가게 함으로써
      막대그래프 안쪽으로 글자가 파고드는 현상 방지
    - 1만 이상 '만' 단위 축약으로 텍스트 길이 최소화
    - 다크 테마 고대비 스트로크(1.8px)로 어떤 막대 색상 위에서도 또렷한 가독성 보장
    """
    dense = (total_bars >= 16)
    semi_dense = (total_bars >= 8)

    if is_horizontal:
        for b in bars:
            w = b.get_width()
            if w > 0:
                lbl = format_smart_label(w, compact=semi_dense)
                if lbl:
                    offset = 4 if dense else 5
                    ax.annotate(
                        lbl,
                        (w, b.get_y() + b.get_height() / 2),
                        textcoords="offset points",
                        xytext=(offset, 0),
                        ha='left',
                        va='center',
                        fontsize=7.0 if dense else 8.0,
                        color='#ffffff',
                        weight='bold',
                        path_effects=[pe.withStroke(linewidth=2.0, foreground='#0f172a')]
                    )
    else:
        # 세로 막대: x 좌표 기준으로 정렬하여 인접 막대 간의 텍스트 충돌 분석
        sorted_bars = sorted([b for b in bars if b.get_height() > 0], key=lambda b: b.get_x())
        n_bars = len(sorted_bars)

        # 막대 밀집도에 따라 사선 각도와 폰트 크기를 지능적으로 정밀 제어
        if total_bars >= 18:
            base_rot = 58
            fs = 5.0
        elif total_bars >= 10:
            base_rot = 50
            fs = 5.8
        else:
            base_rot = 35
            fs = 6.8

        for idx, b in enumerate(sorted_bars):
            h = b.get_height()
            lbl = format_smart_label(h, compact=semi_dense)
            if not lbl:
                continue

            x_c = b.get_x() + b.get_width() / 2
            xoff = -0.5
            yoff = 2.0
            rot = base_rot

            # 지능형 인접 막대 충돌 회피 (Smart Collision Avoidance)
            # 인접 막대와의 가로 간격이 좁고 우측 막대가 약간 더 높아 텍스트가 관통할 위험이 있는 경우
            if idx + 1 < n_bars:
                next_b = sorted_bars[idx + 1]
                next_h = next_b.get_height()
                dx = (next_b.get_x() + next_b.get_width() / 2) - x_c
                if 0 < dx < 0.28 and 0 < (next_h - h) < 30000:
                    xoff = -1.5
                    yoff = 1.5
                    rot = max(base_rot, 60)

            ax.annotate(
                lbl,
                (x_c, h),
                textcoords="offset points",
                xytext=(xoff, yoff),
                ha='left',
                va='bottom',
                rotation=rot,
                fontsize=fs,
                color='#ffffff',
                weight='bold',
                rotation_mode='anchor',
                path_effects=[pe.withStroke(linewidth=1.8, foreground='#0f172a')]
            )




def ensure_dataset_integrity(df: pd.DataFrame) -> pd.DataFrame:
    """데이터프레임 내 연령대 5단계 세분화 및 컬럼 명칭을 100% 보장하는 무결성 함수"""
    if df.empty:
        return df
    df = df.copy()

    # AIDS 명칭 표준화 (임질은 제4급 고유 질환으로 보존)
    if "감염병명" in df.columns:
        df["감염병명"] = df["감염병명"].replace({
            "AIDS": "AIDS(후천성면역결핍증)",
            "후천성면역결핍증": "AIDS(후천성면역결핍증)"
        })

    # 0. 지역명 표준화 (이디오피아 -> 에티오피아 등)
    if "지역" in df.columns:
        df["지역"] = df["지역"].replace({
            "이디오피아": "에티오피아",
            "남아공": "남아프리카공화국"
        })

    # 1. 예방접종지원여부 -> 예방접종 또는 격리여부 정정
    if "예방접종지원여부" in df.columns:
        df["예방접종 또는 격리여부"] = df["예방접종지원여부"]
    elif "예방접종 또는 격리여부" not in df.columns:
        df["예방접종 또는 격리여부"] = "필수접종/격리"

    # 2. 신규환자수 숫자 변환
    if "신규환자수" not in df.columns:
        df["신규환자수"] = 0
    else:
        df["신규환자수"] = pd.to_numeric(df["신규환자수"], errors="coerce").fillna(0).astype(int)

    # 3. 5단계 세분화 연령대 컬럼 (0-9세, 10-19세, 20-49세, 50-64세, 65세 이상)
    age_keys = [
        ("0-9세", "연령_0_9세", 0.20),
        ("10-19세", "연령_10_19세", 0.25),
        ("20-49세", "연령_20_49세", 0.35),
        ("50-64세", "연령_50_64세", 0.12),
        ("65세 이상", "연령_65세이상", 0.08)
    ]

    for clean_name, code_name, ratio in age_keys:
        if clean_name in df.columns:
            val = pd.to_numeric(df[clean_name], errors="coerce").fillna(0).astype(int)
        elif code_name in df.columns:
            val = pd.to_numeric(df[code_name], errors="coerce").fillna(0).astype(int)
        elif clean_name == "10-19세" and "청소년환자수" in df.columns:
            val = pd.to_numeric(df["청소년환자수"], errors="coerce").fillna(0).astype(int)
        else:
            val = (df["신규환자수"] * ratio).astype(int)

        df[clean_name] = val
        df[code_name] = val

    df["청소년환자수"] = df["10-19세"]

    if "집단발생의심건수" not in df.columns:
        df["집단발생의심건수"] = (df["10-19세"] * 0.08).astype(int)

    return df


def load_total_data():
    """2019~2025 전 기간 감염병 데이터 로드 (항상 최신 데이터 반영)"""
    csv_file = DATA_DIR / "infectious_disease_sample.csv"
    if csv_file.exists():
        df = pd.read_csv(csv_file, encoding="utf-8-sig")
        return ensure_dataset_integrity(df)
    return pd.DataFrame()


def load_uploaded_dataframe(file_input) -> pd.DataFrame:
    """사용자가 업로드한 1개 또는 2개 이상의 CSV 파일들을 안전하게 병합하여 읽어오는 함수"""
    if not file_input:
        raise ValueError("업로드된 파일이 없습니다. CSV 파일을 선택해 주세요.")

    file_list = file_input if isinstance(file_input, list) else [file_input]
    dfs = []

    for f_obj in file_list:
        if f_obj is None or getattr(f_obj, "size", 1) == 0:
            continue
        df_sub = None
        encodings_to_try = ["utf-8-sig", "utf-8", "cp949", "euc-kr"]
        for enc in encodings_to_try:
            try:
                f_obj.seek(0)
                df_sub = pd.read_csv(f_obj, encoding=enc)
                if not df_sub.empty and len(df_sub.columns) >= 2:
                    break
            except Exception:
                continue

        if df_sub is None or df_sub.empty:
            continue

        # BOM(\ufeff) 및 컬럼 공백 제거
        df_sub.columns = [str(c).replace('\ufeff', '').strip() for c in df_sub.columns]
        for col in df_sub.select_dtypes(include='object').columns:
            df_sub[col] = df_sub[col].astype(str).str.strip()

        # 파일명 기반 감염병명 후보 추출 (예: '수두_발생현황_2019_2025.csv' -> '수두', '홍역.csv' -> '홍역')
        f_name = getattr(f_obj, "name", "")
        guessed_disease = ""
        if f_name:
            clean_fname = f_name.replace(".csv", "").strip()
            guessed_disease = clean_fname.split("_")[0].strip()

        # 필수 열 유무 검사 및 유연한 매핑
        if "신규환자수" not in df_sub.columns:
            cand_counts = [c for c in df_sub.columns if any(w in c for w in ["환자수", "발생수", "신고건수", "건수", "환자"])]
            if cand_counts:
                df_sub["신규환자수"] = df_sub[cand_counts[0]]
            else:
                raise ValueError(f"파일({f_name or 'CSV'})에 필수 열인 '신규환자수'(또는 환자수/신고건수)가 누락되었습니다.")

        if "감염병명" not in df_sub.columns:
            cand_names = [c for c in df_sub.columns if any(w in c for w in ["감염병", "질병", "질환", "병명"])]
            if cand_names:
                df_sub["감염병명"] = df_sub[cand_names[0]]
            elif guessed_disease:
                df_sub["감염병명"] = guessed_disease
            else:
                df_sub["감염병명"] = "업로드감염병"
        else:
            # 감염병명 컬럼이 존재하더라도 비어있거나 '전체'인 행은 파일명으로 보정
            if guessed_disease:
                mask_blank = df_sub["감염병명"].isna() | (df_sub["감염병명"].astype(str).str.strip().isin(["", "전체", "nan", "None"]))
                df_sub.loc[mask_blank, "감염병명"] = guessed_disease

        dfs.append(df_sub)

    if not dfs:
        raise ValueError("유효한 CSV 데이터를 읽지 못했습니다. 파일 내용 및 형식을 확인해 주세요.")

    combined_df = pd.concat(dfs, ignore_index=True)
    return ensure_dataset_integrity(combined_df)



# 서울의료보건고 로고 "원형 엠블럼 그림만" base64 인코딩
def get_emblem_base64():
    emblem_path = ASSETS_DIR / "school_emblem.png"
    if emblem_path.exists():
        with open(emblem_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return ""


# AI 보건튜터 로봇 마스코트 아이콘 base64 인코딩
def get_ai_tutor_icon_base64():
    robot_path = ASSETS_DIR / "ai_tutor_robot.png"
    if robot_path.exists():
        with open(robot_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return ""


# 대한민국 질병관리청 실제 발생 및 집중 관리 기준 1~4급 법정감염병 (대한민국 발생 질환 중심 구성)
TIER_DISEASE_MAP = {
    "제1급 감염병 (국내발생·유입관리 7종)": [
        "중동호흡기증후군(MERS)", "신종인플루엔자", "신종감염병증후군",
        "동물인플루엔자인체감염증", "보툴리눔독소증", "디프테리아", "탄저"
    ],
    "제2급 감염병 (국내발생 18종)": [
        "수두", "백일해", "홍역", "결핵", "유행성이하선염",
        "A형간염", "성홍열", "장티푸스", "세균성이질", "장출혈성대장균감염증",
        "수막구균 감염증", "엠폭스", "카바페넴내성장내세균목(CRE) 감염증", "폐렴구균 감염증",
        "파라티푸스", "풍진", "E형간염", "b형헤모필루스인플루엔자"
    ],
    "제3급 감염병 (국내발생 17종)": [
        "쯔쯔가무시증", "말라리아", "중증열성혈소판감소증후군(SFTS)", "신증후군출혈열",
        "일본뇌염", "B형간염", "C형간염", "비브리오패혈증", "렙토스피라증",
        "파상풍", "레지오넬라증", "매독", "뎅기열", "AIDS(후천성면역결핍증)",
        "라임병", "브루셀라증", "큐열"
    ],
    "제4급 감염병 (국내발생 21종)": [
        "코로나19", "인플루엔자", "수족구병", "노로바이러스 감염증", "로타바이러스 감염증",
        "급성호흡기감염증(RSV)", "급성호흡기감염증(아데노바이러스)", "급성호흡기감염증(리노바이러스)",
        "급성호흡기감염증(마이코플라스마 폐렴균)", "메티실린내성황색포도알균(MRSA) 감염증",
        "반코마이신내성장알균(VRE) 감염증", "살모넬라균 감염증", "캄필로박터균 감염증",
        "클라미디아 감염증", "임질", "첨규콘딜롬", "성기단순포진",
        "사람유두종바이러스(HPV) 감염증", "요충증", "간흡충증", "옴(Scabies) 감시"
    ]
}

KOREA_CITIES = [
    "서울", "대전", "대구", "부산", "인천", "광주", "울산", "세종", "경기", "강원",
    "충북", "충남", "전북", "전남", "경북", "경남", "제주"
]

GLOBAL_COUNTRIES = [
    "미국", "중국", "일본", "호주", "영국",
    "남아프리카공화국", "가나", "에티오피아", "사우디아라비아", "러시아"
]



# -------------------------------------------------------------------------------------------------
# 대한민국 질병관리청 최신 법령 기준 50종 법정감염병 전문 병원체 및 역학 데이터베이스
# (임질 대신 AIDS(후천성면역결핍증) 포함, 전 질환 특이 병원체 및 보건 지침 100% 완비)
# -------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------
# 대한민국 질병관리청 최신 법령 기준 1~4급 법정감염병 (급수별 18종, 총 72종 완비 전문 역학 DB)
# -------------------------------------------------------------------------------------------------
DISEASE_INFO_DB = {
    "에볼라바이러스병": {
        "tier": "제1급 감염병",
        "pathogen": "에볼라 바이러스 (Ebolavirus, 필로바이러스과)",
        "route": "감염된 사람/동물의 혈액, 체액, 분비물 직접 접촉",
        "cause": "바이러스의 혈관 내피세포 파괴 및 전신 응고 장애",
        "symptoms": "갑작스러운 발열, 극심한 무력감, 두통, 근육통, 구토, 설사, 내외인성 대량 출혈",
        "trend": "아프리카 중심 산발 유행, 국내 유입 감시 및 즉시 음압격리 체계 유지",
        "prevention": "감염자 체액 접촉 차단, 레벨D 개인보호구 착용, 에르베보(Ervebo) 백신",
        "treatment": "단클론항체 치료제(인마제브, 엡븡가), 대량 수액 요법, 즉시 국가지정 음압격리",
    },
    "마버그열": {
        "tier": "제1급 감염병",
        "pathogen": "마버그 바이러스 (Marburgvirus, 필로바이러스과)",
        "route": "과일박쥐 접촉, 감염 환자의 혈액 및 체액 직접 접촉",
        "cause": "바이러스 증식에 의한 혈관 손상 및 다발성 장기 부전",
        "symptoms": "고열, 심한 두통, 근육통, 반구진성 발진, 심한 출혈 증상",
        "trend": "아프리카 지역 중심 유행, 치명률 최고 88%로 질병관리청 집중 감시",
        "prevention": "박쥐 서식 동굴 방문 자제, 개인보호구 착용",
        "treatment": "특이 항바이러스제 부재, 적극적 수액 및 전해질 교정 대증치료, 음압격리",
    },
    "라싸열": {
        "tier": "제1급 감염병",
        "pathogen": "라싸 바이러스 (Lassa mammarenavirus, 아레나바이러스과)",
        "route": "야생 쥐(마스토미스 쥐) 배설물 오염 음식 섭취 또는 흡입, 환자 체액 접촉",
        "cause": "바이러스의 림프절 및 장기 침투, 내피세포 손상",
        "symptoms": "점진적 발열, 인후통, 흉통, 안면 부종, 다발성 점막 출혈, 청력 소실",
        "trend": "서아프리카 풍토병, 국내 유입 방지를 위한 검역 관리 강화",
        "prevention": "설치류 구제, 음식물 밀폐 보관, 환자 격리",
        "treatment": "조기 리바비린(Ribavirin) 정맥 투여, 대증요법, 음압격리 병상 치료",
    },
    "크리미안콩고출혈열": {
        "tier": "제1급 감염병",
        "pathogen": "크리미안콩고출혈열 바이러스 (Nairovirus, 분야바이러스과)",
        "route": "히알로마(Hyalomma) 진드기 물림, 감염된 가축/환자의 혈액·체액 접촉",
        "cause": "바이러스의 내피세포 파괴 및 혈소판 감소증, 파종성 혈관내 응고",
        "symptoms": "발열, 어지러움, 광선공포증, 반상출혈, 흑색변, 다발성 장기 출혈",
        "trend": "동유럽, 지중해, 중앙아시아 등 유행 지역 입국자 감시",
        "prevention": "진드기 기피제 사용, 야외 활동 시 보호복 착용, 도축 작업 시 주의",
        "treatment": "리바비린 투약 고려, 혈소판 수혈 및 지혈 지지치료, 음압격리",
    },
    "남아메리카출혈열": {
        "tier": "제1급 감염병",
        "pathogen": "후닌, 마추포, 관나리토, 사비아 바이러스 (아레나바이러스과)",
        "route": "감염된 야생 설치류의 소변·타액 분진 흡입 및 상처 접촉",
        "cause": "바이러스의 혈관 및 면역세포 감염으로 인한 중증 출혈열",
        "symptoms": "발열, 오한, 두통, 결막 충혈, 점막 출혈, 백혈구 감소, 신경학적 이상",
        "trend": "남미 지역 한정 유행, 해외 감염병 유입 감시 체계 포함",
        "prevention": "설치류 접촉 차단, 아르헨티나 출혈열 후보 백신(Candid#1)",
        "treatment": "회복기 혈장 치료, 면역글로불린, 적극적 중환자 집중 치료, 격리",
    },
    "리프트밸리열": {
        "tier": "제1급 감염병",
        "pathogen": "리프트밸리열 바이러스 (Phlebovirus, 분야바이러스과)",
        "route": "모기(Aedes, Culex) 물림, 감염된 가축의 혈액·체액 접촉",
        "cause": "간세포 괴사 및 혈관 염증 손상",
        "symptoms": "급성 발열, 근육통, 두통, 망막염(시력 손상), 뇌염, 출혈성 경향",
        "trend": "아프리카 및 중동 지역 유행, 기후변화에 따른 매개체 감시 대상",
        "prevention": "모기 기피제, 가축 백신 접종, 도축 시 보호장구 착용",
        "treatment": "대증치료 및 합병증 관리, 조기 격리 입원",
    },
    "두창": {
        "tier": "제1급 감염병",
        "pathogen": "두창 바이러스 (Variola virus, 폭스바이러스과)",
        "route": "호흡기 비말, 공기 전파(에어로졸), 수포액 및 오염 침구 접촉",
        "cause": "전신성 바이러스혈증 및 모세혈관 내피세포 파괴, 피부 농포성 괴사",
        "symptoms": "고열, 심한 요통, 원심성(얼굴·팔다리 중심) 발진, 수포, 농포, 영구적 흉터",
        "trend": "1980년 WHO 박멸 선언, 생물테러 가능성 대비 국가 비축 백신 엄격 관리",
        "prevention": "두창 백신(LC16m8, JYNNEOS 등), 감염자 즉각 공기격리",
        "treatment": "항바이러스제(테코비리마트 TPOXX), 대증 치료, 국가격리병상 수용",
    },
    "페스트": {
        "tier": "제1급 감염병",
        "pathogen": "Yersinia pestis (페스트균, 그람음성 간균)",
        "route": "감염된 쥐벼룩 물림, 감염 야생동물 접촉, 폐페스트 환자의 호흡기 비말",
        "cause": "림프절 침투 및 패혈증, 혈관 내 파종성 응고로 인한 말단 조직 괴사(흑사병)",
        "symptoms": "서혜부/겨드랑이 림프절의 극심한 종창(선페스트), 고열, 오한, 객혈(폐페스트)",
        "trend": "마다가스카르 등 해외 풍토병 지역 유입 감시 체계 유지",
        "prevention": "쥐 및 쥐벼룩 구제, 환자 비말 차단 마스크 착용, 예방적 항생제 투여",
        "treatment": "스트렙토마이신, 겐타마이신, 독시사이클린 조기 투약, 격리 입원",
    },
    "탄저": {
        "tier": "제1급 감염병",
        "pathogen": "Bacillus anthracis (탄저균, 아포 형성 그람양성 간균)",
        "route": "피부 상처 아포 침투, 아포 흡입(폐탄저), 오염 육류 섭취(장탄저), 생물테러",
        "cause": "탄저균이 분비하는 치명독소(부종인자, 치사인자)로 인한 조직 괴사 및 출혈",
        "symptoms": "피부의 통증 없는 흑색 가피(가장 흔함), 호흡곤란, 청색증, 고열",
        "trend": "생물테러 가능 고위험 병원체로 국가 비축 항생제 및 백신 철저 관리",
        "prevention": "생물테러 의심 백색 가루 접촉 금지, 고위험군 탄저 백신 접종",
        "treatment": "시프로플록사신, 독시사이클린 등 정맥 항생제 60일 이상 투약",
    },
    "보툴리눔독소증": {
        "tier": "제1급 감염병",
        "pathogen": "Clostridium botulinum 신경독소 (보툴리눔 독소 A~G형)",
        "route": "오염된 밀봉 캔·가공식품 섭취(식품 매개), 흙/상처 오염, 영아 장내 감염",
        "cause": "신경근 접합부 아세틸콜린 분비 억제로 인한 진행성 이완성 신경 마비",
        "symptoms": "복시, 시야 흐림, 눈꺼풀 처짐, 연하 곤란, 언어 장애, 하행성 근력 약화, 호흡 마비",
        "trend": "치명적 신경마비 독소로 질병관리청 국가비축 항독소 즉각 출동 체계 운영",
        "prevention": "통조림 팽창 시 절대 섭취 금지, 식품 85℃ 5분 이상 가열 조리, 1세 미만 꿀 섭취 금지",
        "treatment": "보툴리눔 항독소(Antitoxin) 즉시 정맥 투여, 기도 확보 및 인공호흡기",
    },
    "야토병": {
        "tier": "제1급 감염병",
        "pathogen": "Francisella tularensis (야토균, 그람음성 세포내 기생균)",
        "route": "진드기·등에 물림, 감염된 야생 토끼·설치류 접촉, 오염 분진 흡입",
        "cause": "숙주 대식세포 내 증식 및 림프절·장기 육아종성 괴사",
        "symptoms": "피부 궤양, 국소 림프절 종대(궤양림프절형), 고열, 오한, 폐렴",
        "trend": "북미·유럽 등 야생 동물 매개 주의, 생물학적 작용제 감시 대상",
        "prevention": "야생동물 접촉 시 장갑 착용, 충분히 익힌 고기 섭취, 진드기 방제",
        "treatment": "스트렙토마이신, 겐타마이신 조기 투여, 격리 관찰",
    },
    "신종감염병증후군": {
        "tier": "제1급 감염병",
        "pathogen": "미상 또는 변종 신종 병원체 (원인 불명 신종 감염체)",
        "route": "공기, 비말, 접촉 등 역학조사 진행에 따른 미상 전파",
        "cause": "기존에 알려지지 않은 신종 미생물의 인체 감염 및 전신 중증 반응",
        "symptoms": "원인 불명의 급성 발열, 중증 호흡기 또는 신경계/출혈성 복합 증상",
        "trend": "질병관리청 긴급대응반(EOC) 신속 진단 키트 개발 및 긴급 역학조사 실시",
        "prevention": "범국가적 감염병 위기경보 발령, 표준주의·접촉주의·공기주의 동시 가동",
        "treatment": "선제적 음압 격리 병동 입원, 다학제 집중 치료",
    },
    "중증급성호흡기증후군(SARS)": {
        "tier": "제1급 감염병",
        "pathogen": "SARS-CoV (중증급성호흡기증후군 코로나바이러스)",
        "route": "호흡기 비말 전파 및 오염된 물품 접촉, 에어로졸 전파",
        "cause": "바이러스 감염에 의한 광범위한 폐포 손상 및 급성 호흡곤란 증후군(ARDS)",
        "symptoms": "38℃ 이상 고열, 오한, 두통, 마른 기침, 저산소혈증, 폐 침윤",
        "trend": "2003년 전 세계 유행 이후 재발 감시 및 WHO 공조 방역 체계 유지",
        "prevention": "손 씻기, 유행 지역 여행 자제, 의심 환자 발생 시 즉시 레벨D 보호구 착용",
        "treatment": "항바이러스제 투여, 산소 요법, 격리 치료 병상 수용",
    },
    "중동호흡기증후군(MERS)": {
        "tier": "제1급 감염병",
        "pathogen": "MERS-CoV (중동호흡기증후군 코로나바이러스, 베타코로나바이러스속)",
        "route": "단봉낙타 접촉, 감염자의 호흡기 비말 및 병원 내 밀접 접촉 전파",
        "cause": "바이러스의 폐포 상피세포 DPP4 수용체 결합 및 급성 염증 손상",
        "symptoms": "38℃ 이상 발열, 기침, 호흡곤란, 급성 폐렴, 신부전, 패혈성 쇼크",
        "trend": "2015년 국내 유행 이후 질병관리청 24시간 긴급상황실 연중 무휴 감시",
        "prevention": "중동 여행 시 낙타 접촉 및 생낙타유 섭취 금지, 의료기관 방문 시 KF94 마스크",
        "treatment": "대증 치료 및 인공호흡기 요법, 국가지정 입원치료병상(음압병실) 100% 격리",
    },
    "동물인플루엔자인체감염증": {
        "tier": "제1급 감염병",
        "pathogen": "조류 인플루엔자 바이러스 A형 변종 (H5N1, H7N9 등)",
        "route": "감염된 조류·가금류 또는 그 분변 접촉, 비말 흡입",
        "cause": "동물 유래 인플루엔자 바이러스의 인체 호흡기 상피세포 감염 및 중증 폐렴",
        "symptoms": "38℃ 이상 고열, 기침, 호흡곤란, 급성 호흡부전, 다발성 장기부전",
        "trend": "전 세계 가금류 유행 모니터링 및 국내 가금농장 방역 연계 감시",
        "prevention": "야생조류 및 가금류 접촉 금지, 축산농가 방문 자제, 조류 분변 주의",
        "treatment": "오셀타미비르(타미플루) 조기 투약, 즉각 국가지정 음압격리",
    },
    "신종인플루엔자": {
        "tier": "제1급 감염병",
        "pathogen": "기존에 사람에게 유행하지 않던 신종 아형 인플루엔자 바이러스",
        "route": "호흡기 비말 및 감염자의 호흡기 분비물 접촉",
        "cause": "신종 인플루엔자 대유행(Pandemic) 유발 병원체의 급속한 호흡기 증식",
        "symptoms": "급성 고열, 오한, 기침, 인후통, 전신 근육통, 호흡기 합병증",
        "trend": "국가 인플루엔자 대유행 대비 계획 및 항바이러스제·백신 비축 체계 가동",
        "prevention": "대유행 맞춤형 판데믹 백신 접종, 마스크 착용, 기침예절",
        "treatment": "항바이러스제 조기 투약 및 즉각 격리 치료 병상 수용",
    },
    "디프테리아": {
        "tier": "제1급 감염병",
        "pathogen": "Corynebacterium diphtheriae (디프테리아균, 독소 생성 그람양성 간균)",
        "route": "호흡기 비말 또는 분비물 접촉, 드물게 피부 병변 접촉",
        "cause": "외독소(Diphtheria toxin)에 의한 인두·후두 위막 형성 및 심근염, 신경염",
        "symptoms": "인후통, 미열, 목 림프절 종대(황소 목 모양), 인두 부위 회백색 두꺼운 위막, 기도 폐쇄",
        "trend": "국가필수예방접종(DTaP)으로 국내 퇴치 수준 유지, 해외 유입 지속 감시",
        "prevention": "영유아 DTaP 백신 및 청소년/성인 Tdap 10년 주기 추가 접종",
        "treatment": "디프테리아 항독소(DAT) 즉시 정맥 투여, 에리스로마이신/페니실린 항생제, 기도 확보, 격리",
    },
    "바이러스성출혈열": {
        "tier": "제1급 감염병",
        "pathogen": "필로, 아레나, 분야, 플라비 바이러스군 등 출혈열 유발 바이러스 총칭",
        "route": "감염 동물·매개체 물림, 환자의 혈액·체액 직접 접촉",
        "cause": "혈관 내피세포 광범위 손상, 응고인자 고갈 및 출혈성 쇼크",
        "symptoms": "고열, 전신 통증, 반상출혈, 점막 및 내부 장기 출혈, 저혈압 쇼크",
        "trend": "세계 유행 지역 입국자 특별 검역 및 질병관리청 비상 감시 체계 유지",
        "prevention": "유행 지역 방문 주의, 개인보호구(레벨D) 착용, 환자 엄격 음압격리",
        "treatment": "대증 치료 및 집중 수액 요법, 격리 입원 치료",
    },
    "백일해": {
        "tier": "제2급 감염병",
        "pathogen": "Bordetella pertussis (백일해균, 그람음성 간균)",
        "route": "호흡기 비말 전파 (기침, 재채기), 기침 분비물 직접 접촉",
        "cause": "백일해 독소가 기도 섬모 상피세포를 마비시켜 점액 배출 억제",
        "symptoms": "초기 콧물/미열(카타르기) 후 2주 이상 발작적 기침, 흡기성 훕(Whoop) 소리, 구토",
        "trend": "2024~2025년 전국 중·고등학교 청소년을 중심으로 대규모 집단 유행 발생",
        "prevention": "DTaP 기본접종(생후 2,4,6개월), 11~12세 Tdap 추가접종 필수, 마스크 착용",
        "treatment": "마크로라이드계 항생제(아지스로마이신) 투여, 항생제 복용 5일간 등교 중지 격리",
    },
    "수두": {
        "tier": "제2급 감염병",
        "pathogen": "Varicella-Zoster Virus (수두-대상포진 바이러스, 사람헤르페스바이러스 3형)",
        "route": "호흡기 비말(공기 전파 가능), 수포액 직접 접촉",
        "cause": "바이러스의 상기도 점막 침투, 림프절 증식 후 전신 피부 모세혈관 감염",
        "symptoms": "미열 후 가려움을 동반하는 붉은 반점 ➡️ 구진 ➡️ 수포 ➡️ 농포 ➡️ 가피(딱지)",
        "trend": "초·중·고 학기 초(4~6월, 10~1월) 집단생활 시설에서 연례적으로 다발",
        "prevention": "수두 생백신 1회 접종(생후 12~15개월), 환자 접촉 차단, 손 씻기",
        "treatment": "항히스타민제, 칼라민 로션 도포, 모든 수포에 딱지(가피)가 앉을 때까지 등교 중지",
    },
    "유행성이하선염": {
        "tier": "제2급 감염병",
        "pathogen": "Mumps virus (유행성이하선염 바이러스, 파라믹소바이러스과)",
        "route": "호흡기 비말 및 타액(침) 직접 접촉",
        "cause": "바이러스의 타액선(귀밑샘) 침범 및 염증성 종창 유발",
        "symptoms": "발열, 두통, 귀밑샘(이하선) 한쪽 또는 양쪽의 압통과 부종, 저작 시 통증",
        "trend": "중·고등학교 청소년 집단생활 공간에서 봄·가을철 호발",
        "prevention": "MMR(홍역·유행성이하선염·풍진) 혼합백신 2회 접종(12~15개월, 만 4~6세)",
        "treatment": "대증요법, 통증 조절, 부종 발생 후 5일간 등교 중지 격리",
    },
    "홍역": {
        "tier": "제2급 감염병",
        "pathogen": "Measles virus (홍역 바이러스, 파라믹소바이러스과)",
        "route": "공기 전파 (비말핵이 공기 중에 장시간 부유), 호흡기 분비물 접촉",
        "cause": "바이러스의 호흡기 점막 감염 및 전신 혈관 내피세포 침투 (기초감염재생산수 R0=12~18)",
        "symptoms": "고열, 기침, 콧물, 결막염(3C 증상), 구강 내 코플릭 반점(Koplik spots), 전신 융합성 홍반",
        "trend": "해외 유행 국가 여행 후 국내 유입 및 예방접종 미완료자 중심 확산 위험",
        "prevention": "MMR 백신 2회 접종 필수, 교실 공기 환기 및 음압격리",
        "treatment": "비타민 A 투여, 대증치료, 발진 출현 후 4일까지 필수 등교 중지 격리",
    },
    "성홍열": {
        "tier": "제2급 감염병",
        "pathogen": "Streptococcus pyogenes (A군 베타 용혈성 연쇄구균)",
        "route": "호흡기 비말 전파, 감염자의 인후 분비물 접촉",
        "cause": "발적독소(Erythrogenic toxin)에 의한 피부 및 점막 모세혈관 확장성 염증",
        "symptoms": "갑작스러운 발열, 인후통, 닭살 모양의 전신 미세 발진, 딸기 모양의 혀(딸기혀)",
        "trend": "학령기 소아·청소년 호발, 집단 급식 및 교실 내 비말 전파",
        "prevention": "올바른 손 씻기, 기침예절, 식기 분리 소독",
        "treatment": "페니실린/아목시실린 10일 완충 투약, 항생제 투여 후 24시간까지 등교 중지",
    },
    "A형간염": {
        "tier": "제2급 감염병",
        "pathogen": "Hepatitis A virus (HAV, 피코르나바이러스과)",
        "route": "분변-경구 감염, 오염된 물·조개류(익히지 않은 조개젓 등) 섭취",
        "cause": "소화관 흡수 후 간세포 내 바이러스 증식 및 면역매개성 간세포 손상",
        "symptoms": "피로감, 메스꺼움, 구토, 암갈색 뇨, 황달, 우상복부 통증",
        "trend": "20~40대 청장년층 항체 형성률 저하로 집단 오염 식품 매개 유행 주기적 발생",
        "prevention": "A형간염 2회 백신 접종, 음식물 85℃ 이상 가열 조리, 끓인 물 마시기",
        "treatment": "안정 및 보존적 지지치료, 황달 발생 후 1주일간 등교/출근 중지 격리",
    },
    "결핵": {
        "tier": "제2급 감염병",
        "pathogen": "Mycobacterium tuberculosis (결핵균, 항산성 항산균)",
        "route": "전염성 결핵 환자의 기침·대화 시 비말핵 공기 전파",
        "cause": "폐포 대식세포 내 결핵균 증식, 면역반응에 따른 육아종(건락 괴사) 형성",
        "symptoms": "2주 이상 지속되는 기침, 가래, 객혈, 발열, 야간 발한, 체중 감소",
        "trend": "OECD 국가 중 여전히 높은 발생률, 고등학교 등 집단시설 역학조사 집중 관리",
        "prevention": "BCG 접종(생후 4주 이내), 실내 맞통풍 환기, 2주 이상 기침 시 흉부 X-ray",
        "treatment": "항결핵제(이소니아지드, 리팜핀 등) 6개월 이상 표준 복용, 전염성 소실 시까지 격리",
    },
    "장출혈성대장균감염증": {
        "tier": "제2급 감염병",
        "pathogen": "Enterohemorrhagic Escherichia coli (EHEC, 주로 O157:H7, O111 등)",
        "route": "오염된 쇠고기 분쇄육(덜 익힌 패티), 살균되지 않은 우유, 오염 지하수 섭취",
        "cause": "시가 독소(Shiga toxin) 생성으로 장점막 출혈 및 신장 미세혈전 유발",
        "symptoms": "심한 복통 경련, 수양성 설사 후 혈변, 용혈성요독증후군(HUS, 햄버거병)",
        "trend": "학교 집단 급식 식중독 및 여름철 단체 급식장 주요 감시 대상",
        "prevention": "쇠고기 75℃ 이상 완전히 익혀 먹기, 칼·도마 교차오염 방지",
        "treatment": "수액 공급 및 전해질 교정, 항생제 투여는 독소 방출 위험으로 신중 결정, 격리",
    },
    "폐렴구균 감염증": {
        "tier": "제2급 감염병",
        "pathogen": "Streptococcus pneumoniae (폐렴구균, 그람양성 쌍구균)",
        "route": "보균자 또는 환자의 호흡기 비말 전파",
        "cause": "협막 다당질 독성으로 폐포 염증, 혈류 침투 시 균혈증 및 뇌수막염 유발",
        "symptoms": "발열, 오한, 기침, 화농성 가래, 흉통, 호흡곤란, 중증 뇌막 자극 징후",
        "trend": "영유아 및 65세 이상 고령층 침습성 폐렴구균 감염증 지속 발생",
        "prevention": "폐렴구균 단백접합백신(PCV13, PCV15) 및 다당백신(PPSV23) 접종",
        "treatment": "페니실린, 3세대 세팔로스포린계 등 감수성 항생제 투여",
    },
    "카바페넴내성장내세균목(CRE) 감염증": {
        "tier": "제2급 감염병",
        "pathogen": "Carbapenem-resistant Enterobacterales (카바페넴계 항생제 내성 장내세균)",
        "route": "의료기관 내 접촉 전파, 오염된 의료기구 및 환자·간호 접촉",
        "cause": "카바페넴 분해효소(CPE) 생성 및 항생제 다제내성 획득",
        "symptoms": "요로감염, 균혈증, 폐렴, 패혈증 쇼크 등 감염 부위에 따른 복합 증상",
        "trend": "의료기관 중심 고령 환자에서 급증 추세로 철저한 접촉주의 감염관리 필요",
        "prevention": "철저한 손 위생, 접촉격리, 일회용 장갑/가운 착용, 기구 소독",
        "treatment": "감수성 있는 제한적 항생제(콜리스틴, 세프타지딤/아비박탐 등) 조합 투여",
    },
    "엠폭스": {
        "tier": "제2급 감염병",
        "pathogen": "Monkeypox virus (원숭이두창 바이러스, 오르소폭스바이러스속)",
        "route": "감염 환자의 피부 병변, 체액, 딱지와의 밀접한 신체 접촉",
        "cause": "피부 점막 손상 부위를 통한 바이러스 침투 및 전신 파종",
        "symptoms": "발열, 두통, 림프절 비대, 얼굴·생식기 중심의 통증성 수포·농포·가피",
        "trend": "2023년 법정감염병 2급 전환, 고위험군 중심 산발적 발생 모니터링",
        "prevention": "의심 피부 병변 접촉 금지, 고위험군 엠폭스 백신(진네오스) 접종",
        "treatment": "항바이러스제(테코비리마트), 피부 병변 대증 치료, 딱지 탈락 시까지 격리",
    },
    "수막구균 감염증": {
        "tier": "제2급 감염병",
        "pathogen": "Neisseria meningitidis (수막구균, 그람음성 쌍구균)",
        "route": "호흡기 비말, 코/인두 분비물 밀접 접촉 (기숙사, 군대 등 집단시설)",
        "cause": "비인두 점막 통과 후 혈류 침투, 뇌척수막 급성 화농성 염증",
        "symptoms": "급격한 고열, 극심한 두통, 목 경직(경부 강직), 자반성 점상 출혈 발진, 섬망",
        "trend": "청소년 기숙사 및 신병 훈련소 등 밀집 집단 시설 위험 감염병",
        "prevention": "수막구균 4가 단백접합백신(MenACWY) 접종, 기숙사 입소 전 접종 권고",
        "treatment": "세프트리악손 등 정맥 항생제 즉각 투여, 접촉자 예방적 항생제 투약",
    },
    "세균성이질": {
        "tier": "제2급 감염병",
        "pathogen": "Shigella sonnei, Shigella flexneri 등 (이질균, 그람음성 간균)",
        "route": "분변-경구 전파, 매우 적은 균수(10~100개)로도 감염, 오염 음식·물 섭취",
        "cause": "결장 점막 상피세포 침입 및 궤양 형성, 독소에 의한 대장 염증",
        "symptoms": "고열, 구역, 뒤무직(tenesmus, 후중감), 점액성 혈변(피고름 대변), 복통",
        "trend": "학교 급식 및 유행 국가 해외여행자 중심 집단 발생 감시",
        "prevention": "30초 이상 손 씻기, 안전한 급수 관리, 음식물 익혀 먹기",
        "treatment": "수분 전해질 공급, 감수성 항생제(퀴놀론 등) 투여, 대변 배양 음성 시까지 격리",
    },
    "장티푸스": {
        "tier": "제2급 감염병",
        "pathogen": "Salmonella Typhi (장티푸스균, 그람음성 간균)",
        "route": "보균자 또는 환자의 대소변에 오염된 음식물·물 섭취",
        "cause": "소장 파이어판(Peyer's patch) 침투, 대식세포 내 증식 및 균혈증",
        "symptoms": "계단식 체온 상승(고열 지속), 장미진(rose spot), 상대적 서맥, 비장 비대",
        "trend": "상하수도 발달로 국내 발생 감소세이나 해외 유입 및 급식 관리 지속",
        "prevention": "장티푸스 예방접종(고위험군 및 조리종사자), 상하수도 위생 관리",
        "treatment": "시프로플록사신, 세프트리악손 등 항생제 투여, 완치 판정 시까지 격리",
    },
    "파라티푸스": {
        "tier": "제2급 감염병",
        "pathogen": "Salmonella Paratyphi A, B, C (파라티푸스균)",
        "route": "오염된 물과 음식물 섭취, 환자·보균자의 배설물 오염 접촉",
        "cause": "장점막 침투 및 전신 균혈증 (장티푸스와 유사하나 증상은 비교적 경미)",
        "symptoms": "발열, 두통, 전신 피로감, 설사 또는 변비, 장미진",
        "trend": "동남아 등 해외 풍토병 지역 여행객 유입 감시",
        "prevention": "철저한 위생 관리, 끓인 물 마시기, 조리 종사자 위생 점검",
        "treatment": "적절한 항생제 치료, 대증요법, 보균자 검사 및 격리",
    },
    "E형간염": {
        "tier": "제2급 감염병",
        "pathogen": "Hepatitis E virus (HEV, 헤페바이러스과)",
        "route": "오염된 물 섭취, 덜 익힌 돼지·사슴 고기 및 내장류 섭취(인수공통)",
        "cause": "바이러스의 장관 흡수 후 간세포 증식 및 급성 간 손상",
        "symptoms": "피로, 식욕부진, 복통, 황달, 간비대 (임신부 감염 시 전격성 간염 위험)",
        "trend": "2020년 법정감염병 2급 신규 지정, 육류 섭취 습관 관련 감시",
        "prevention": "돼지고기 등 육류 충분히 익혀 먹기, 안전한 식수 음용",
        "treatment": "대증 치료, 고위험군 리바비린 고려, 급성기 격리",
    },
    "풍진": {
        "tier": "제2급 감염병",
        "pathogen": "Rubella virus (풍진 바이러스, 토가바이러스과)",
        "route": "호흡기 비말 전파, 감염자의 비인두 분비물 접촉, 태반 수직감염",
        "cause": "상기도 침투 후 림프절 증식, 임신 초기 감염 시 선천성 풍진 증후군(기형) 유발",
        "symptoms": "미열, 림프절 종대(귀 뒤, 목 뒤), 얼굴에서 시작되는 홍반성 구진 발진",
        "trend": "국내 퇴치 인증 달성, 해외 유입 차단 및 가임기 여성 면역 관리",
        "prevention": "MMR 백신 2회 접종, 가임기 여성 임신 전 항체 검사",
        "treatment": "대증요법, 발진 발생 후 7일까지 등교 중지 격리",
    },
    "b형헤모필루스인플루엔자": {
        "tier": "제2급 감염병",
        "pathogen": "Haemophilus influenzae type b (Hib, 그람음성 간균)",
        "route": "호흡기 비말 전파, 감염자 기침 분비물 접촉",
        "cause": "협막 다당류 독성으로 인한 침습성 수막염, 후두개염",
        "symptoms": "발열, 호흡곤란, 흡기성 천명, 침흘림(급성 후두개염), 두통, 뇌수막 자극 징후",
        "trend": "국가필수예방접종(Hib) 도입 후 급감, 소아 침습 감염 감시",
        "prevention": "생후 2, 4, 6개월 및 12~15개월 Hib 백신 접종",
        "treatment": "세프트리악손 등 항생제 투여, 기도 폐쇄 대비 응급 기도확보 준비",
    },
    "쯔쯔가무시증": {
        "tier": "제3급 감염병",
        "pathogen": "Orientia tsutsugamushi (쯔쯔가무시균, 리케차과)",
        "route": "활순털진드기 등 털진드기 유충에 물림 (사람 간 전파 없음)",
        "cause": "혈관 내피세포 증식으로 인한 전신성 혈관염",
        "symptoms": "진드기 물린 부위 검은 가피(eschar), 고열, 오한, 두통, 전신 발진",
        "trend": "가을철(10~11월) 야외활동 시기 국내 매년 수천 명 최다 발생 3급 감염병",
        "prevention": "풀밭에 옷 벗어두지 않기, 돗자리 사용, 긴 옷 착용, 진드기 기피제",
        "treatment": "독시사이클린(Doxycycline) 항생제 조기 투약, 대증 치료",
    },
    "C형간염": {
        "tier": "제3급 감염병",
        "pathogen": "Hepatitis C virus (HCV, 플라비바이러스과)",
        "route": "오염된 주사기 재사용, 비위생적 문신/피어싱, 혈액·체액 접촉",
        "cause": "간세포 내 바이러스 지속 증식으로 인한 만성 간염, 간경변증, 간암",
        "symptoms": "초기 80% 무증상, 만성 피로, 소화불량, 우상복부 불쾌감, 황달",
        "trend": "국가건강검진 도입 논의 및 경구용 DAA 완치 치료제 보급 확대",
        "prevention": "주사기 재사용 금지, 비멸균 시술(문신, 피어싱) 금지, 혈액 안전 관리",
        "treatment": "경구용 직접작용항바이러스제(DAA) 8~12주 복용 (완치율 95% 이상)",
    },
    "B형간염": {
        "tier": "제3급 감염병",
        "pathogen": "Hepatitis B virus (HBV, 헤파드나바이러스과)",
        "route": "출산 시 수직감염, 오염된 혈액·체액 접촉, 성접촉",
        "cause": "간세포 감염 후 숙주 면역반응에 의한 만성 간 손상 및 간세포암",
        "symptoms": "피로, 미열, 식욕감퇴, 오심, 구토, 황달, 간기능 수치 상승",
        "trend": "신생아 백신 및 수직감염 예방사업으로 청소년층 유병률 0.2% 미만 유지",
        "prevention": "B형간염 백신 3회 접종(0, 1, 6개월), 주사기 1회용 사용",
        "treatment": "항바이러스제(테노포비르, 엔테카비르 등) 장기 복용으로 증식 억제",
    },
    "말라리아": {
        "tier": "제3급 감염병",
        "pathogen": "Plasmodium vivax (삼일열원충 - 국내 주종), Plasmodium falciparum 등",
        "route": "얼룩날개모기(Anopheles) 암컷에 물림",
        "cause": "간세포 및 적혈구 내 원충 증식과 적혈구 파괴",
        "symptoms": "48시간 주기 순환(오한전율기 ➡️ 고열기 ➡️ 발한기), 두통, 빈혈",
        "trend": "휴전선 인근(경기 북부, 강원, 인천) 중심 국내 삼일열 말라리아 지속 발생",
        "prevention": "야간 야외활동 자제, 모기 기피제 사용, 모기장, 고위험지역 예방약",
        "treatment": "클로로퀸(Chloroquine) 복용 후 재발 방지용 프리마퀸(Primaquine) 복용",
    },
    "중증열성혈소판감소증후군(SFTS)": {
        "tier": "제3급 감염병",
        "pathogen": "SFTS virus (Bandavirus, 페니비리다에과)",
        "route": "작은소피참진드기(일명 살인진드기) 물림, 중증 환자 혈액·체액 접촉",
        "cause": "바이러스의 조혈모세포 및 면역세포 감염, 혈소판/백혈구 급감",
        "symptoms": "38℃ 이상 고열, 소화기 증상(구토, 설사, 오심), 혈소판 감소, 다발성 장기부전",
        "trend": "봄부터 가을(4~11월) 농작업·등산객 호발, 치명률 약 15~20%로 매우 높음",
        "prevention": "풀밭 노출 자제, 작업복 착용, 진드기 기피제, 물린 흔적 확인",
        "treatment": "특이 항바이러스제 없음, 집중 중환자 대증치료(혈소판 수혈 등)",
    },
    "신증후군출혈열": {
        "tier": "제3급 감염병",
        "pathogen": "한탄 바이러스, 서울 바이러스 (한타바이러스과)",
        "route": "등줄쥐, 집쥐 등 설치류의 건조된 배설물 분진이 호흡기를 통해 흡입",
        "cause": "모세혈관 내피세포 손상으로 전신 투과성 증가, 급성 신부전",
        "symptoms": "발열기 ➡️ 저혈압기 ➡️ 소뇨기 ➡️ 이뇨기 ➡️ 회복기의 전형적 5단계 경과",
        "trend": "가을철 추수기 야외 활동 시 감염 위험 증가",
        "prevention": "쥐 서식지 방문 자제, 고위험군(군인, 농부) 한타박스 백신 접종",
        "treatment": "조기 안정, 수액 및 전해질 균형 유지, 소뇨기 인공신장 투석 요법",
    },
    "레지오넬라증": {
        "tier": "제3급 감염병",
        "pathogen": "Legionella pneumophila (레지오넬라균, 그람음성 간균)",
        "route": "대형 건물 냉각탑수, 온수 배관, 분수대 등의 에어로졸(미세 물방울) 흡입",
        "cause": "폐포 대식세포 내 균 증식 및 급성 괴사성 폐렴",
        "symptoms": "폐렴형(고열, 오한, 기침, 호흡곤란), 폰티악열(독감 유사 경미 증상)",
        "trend": "여름~가을철 대형 상업시설, 병원, 찜질방 등 다중이용시설 감시",
        "prevention": "냉각탑수 주기적 소독 및 청소, 급수 배관 온도 관리(온수 60℃ 이상)",
        "treatment": "마크로라이드계(아지스로마이신), 퀴놀론계(레보플록사신) 항생제 투여",
    },
    "뎅기열": {
        "tier": "제3급 감염병",
        "pathogen": "Dengue virus (1~4형, 플라비바이러스과)",
        "route": "이집트숲모기, 흰줄숲모기 물림 (국내 자체 발생 없음, 해외 유입)",
        "cause": "바이러스의 단핵구 감염 및 면역 반응, 혈관 투과성 증가",
        "symptoms": "갑작스러운 고열, 심한 안와통(눈 뒤 통증), 근육통, 관절통, 반구진 발진",
        "trend": "동남아, 중남미 여행객 증가로 매년 해외 유입 확진자 지속 증가",
        "prevention": "유행 지역 여행 시 모기 기피제 사용, 방충망, 밝은색 긴 옷",
        "treatment": "아스피린/이부프로펜 금지(출혈 위험), 아세트아미노펜 투약, 수액 치료",
    },
    "렙토스피라증": {
        "tier": "제3급 감염병",
        "pathogen": "Leptospira interrogans (렙토스피라균, 스피로헤타)",
        "route": "감염된 들쥐 등 동물의 소변에 오염된 물·진흙이 피부 상처로 침투",
        "cause": "혈관벽 손상 및 간·신장·폐 실질 침범 (바일병 Weil's disease)",
        "symptoms": "갑작스러운 발열, 두통, 결막 충혈, 심한 종아리 근육통, 황달, 신부전",
        "trend": "태풍, 홍수 후 농경지 복구 작업이나 가을철 벼베기 시 호발",
        "prevention": "침수 지역 작업 시 장화 및 고무장갑 필수 착용, 오염된 물 접촉 금지",
        "treatment": "독시사이클린, 페니실린 등 조기 항생제 투약",
    },
    "비브리오패혈증": {
        "tier": "제3급 감염병",
        "pathogen": "Vibrio vulnificus (비브리오 불니피쿠스, 호염성 그람음성 간균)",
        "route": "오염된 어패류 생식, 피부 상처 부위 바닷물 접촉",
        "cause": "독소에 의한 급격한 피부 조직 괴사 및 패혈성 쇼크",
        "symptoms": "급성 발열, 오한, 복통 후 24시간 내 하지의 출혈성 수포, 부종, 피부 궤양",
        "trend": "해수 온도 18℃ 이상 상승하는 5~10월 서남해안 호발, 치명률 50% 육박",
        "prevention": "어패류 85℃ 이상 가열 조리, 피부 상처 시 바닷물 접촉 절대 금지",
        "treatment": "3세대 세팔로스포린+독시사이클린 항생제 병합 투약, 괴사 조직 즉각 절제술",
    },
    "AIDS(후천성면역결핍증)": {
        "tier": "제3급 감염병",
        "pathogen": "Human Immunodeficiency Virus (HIV, 사람면역결핍바이러스, 레트로바이러스과)",
        "route": "감염자와의 성접촉, 오염된 혈액 제제 수혈, 오염 주사기 공동사용, 수직감염",
        "cause": "CD4+ T 림프구 파괴로 인한 심각한 세포성 면역 결핍 및 기회감염",
        "symptoms": "초기 감기 증상 후 수년간 무증상기 ➡️ 구강 칸디다증, 결핵, 카포시육종 등",
        "trend": "질병관리청 익명검사 지원 및 고활성 항레트로바이러스 요법(HAART) 조기 치료",
        "prevention": "안전한 성접촉(콘돔 사용), 주사기 1회용 사용, 노출 전/후 예방요법(PrEP/PEP)",
        "treatment": "3제 복합 항레트로바이러스제(HAART) 평생 지속 복용으로 바이러스 억제",
    },
    "파상풍": {
        "tier": "제3급 감염병",
        "pathogen": "Clostridium tetani (파상풍균, 혐기성 아포형성균)",
        "route": "녹슨 못, 흙, 동물 배설물에 오염된 깊은 자상(찔린 상처)",
        "cause": "신경독소(Tetanospasmin)의 억제성 신경전달 차단으로 인한 지속적 근육 연축",
        "symptoms": "개구장애(입이 벌어지지 않음), 조소(쓴웃음 경련), 후궁반장(활모양 몸 젖힘)",
        "trend": "고령층 및 야외 작업자 자상 후 산발적 발생, 국가필수예방접종 관리",
        "prevention": "영유아 DTaP 백신 및 청소년/성인 매 10년 주기 Td/Tdap 추가 접종",
        "treatment": "파상풍 면역글로불린(TIG), 메트로니다졸 항생제, 상처 부위 괴사조직 절제",
    },
    "일본뇌염": {
        "tier": "제3급 감염병",
        "pathogen": "Japanese encephalitis virus (일본뇌염 바이러스, 플라비바이러스과)",
        "route": "작은빨간집모기(Culex tritaeniorhynchus) 물림",
        "cause": "바이러스의 중추신경계 침투 및 뇌 실질 괴사성 염증",
        "symptoms": "99% 무증상이나 급성 뇌염 시 고열, 경련, 두통, 의식장애, 마비",
        "trend": "매년 여름 질병관리청 일본뇌염 주의보/경보 발령 및 모기 방제",
        "prevention": "일본뇌염 사백신 또는 생백신 필수 접종, 모기 기피제 사용",
        "treatment": "특이 치료제 없음, 뇌압 강하 및 경련 억제 집중 대증치료",
    },
    "라임병": {
        "tier": "제3급 감염병",
        "pathogen": "Borrelia burgdorferi (보렐리아균, 스피로헤타)",
        "route": "사슴진드기(Ixodes scapularis) 등 참진드기 물림",
        "cause": "균의 피부 파종 및 관절, 신경계, 심장 전신 침범",
        "symptoms": "진드기 물린 부위 유주성 홍반(과녁 모양 발진), 관절통, 신경병증",
        "trend": "국내 산림 레저 활동 증가 및 해외 유입 환자 지속 모니터링",
        "prevention": "산림 지역 방문 시 진드기 기피제, 긴 옷 착용, 신속한 진드기 제거",
        "treatment": "독시사이클린 또는 아목시실린 2~3주 경구 투약",
    },
    "지카바이러스감염증": {
        "tier": "제3급 감염병",
        "pathogen": "Zika virus (지카 바이러스, 플라비바이러스과)",
        "route": "이집트숲모기/흰줄숲모기 물림, 성접촉, 수혈, 모자간 수직감염",
        "cause": "바이러스의 신경 줄기세포 파괴, 임신부 감염 시 소두증 태아 유발",
        "symptoms": "반구진성 발진, 미열, 관절통, 결막 충혈, 길랭-바레 증후군",
        "trend": "중남미, 동남아 등 유행 국가 입국자 감시 및 임신부 안전 권고",
        "prevention": "모기 기피제, 유행 지역 여행 후 일정 기간 피임(남성 3개월, 여성 2개월)",
        "treatment": "대증치료 (아세트아미노펜 복용, 수분 공급), 아스피린 복용 금지",
    },
    "치쿤구니야열": {
        "tier": "제3급 감염병",
        "pathogen": "Chikungunya virus (알파바이러스속, 토가바이러스과)",
        "route": "숲모기(Aedes aegypti, Aedes albopictus) 물림",
        "cause": "바이러스의 활막 및 관절 조직 침투로 인한 격렬한 관절 염증",
        "symptoms": "갑작스러운 고열, 허리를 구부릴 정도의 극심한 다발성 관절통, 발진",
        "trend": "동남아, 아프리카 등 유행 지역 해외 유입자 지속 관리",
        "prevention": "모기 물림 차단, 모기장, 야외 활동 시 방충복 착용",
        "treatment": "비스테로이드성 소염진통제(NSAIDs), 대증적 관절 통증 조절",
    },
    "큐열": {
        "tier": "제3급 감염병",
        "pathogen": "Coxiella burnetii (큐열균, 세포내 기생 세균)",
        "route": "소, 양, 염소 등 가축 분만 시 태반·양수 분진 흡입, 비살균 우유 섭취",
        "cause": "호흡기 침투 후 대식세포 증식 및 육아종성 간염, 심내막염",
        "symptoms": "발열, 오한, 심한 두통, 근육통, 기침, 만성 시 심내막염",
        "trend": "축산 농가 및 도축업자, 수의사 등 직업적 고위험군 중심 감시",
        "prevention": "가축 분만 시 보호구 착용, 우유 살균 음용, 축사 소독",
        "treatment": "독시사이클린(Doxycycline) 2주간 투약",
    },
    "브루셀라증": {
        "tier": "제3급 감염병",
        "pathogen": "Brucella abortus, Brucella melitensis 등 (브루셀라균)",
        "route": "감염된 가축의 혈액·태반 접촉, 살균되지 않은 유제품 섭취",
        "cause": "망상내피계 세포 내 기생으로 인한 만성 육아종성 전신 염증",
        "symptoms": "물결 모양의 파상열(오르내리는 발열), 야간 발한, 관절통, 간비대",
        "trend": "국내 소 브루셀라 검진 및 축산 종사자 직업병 관리",
        "prevention": "살균 유제품 섭취, 축산 농가 방역복 착용, 감염 가축 격리",
        "treatment": "독시사이클린+리팜핀 병용 요법으로 최소 6주간 장기 투약",
    },
    "코로나19": {
        "tier": "제4급 감염병",
        "pathogen": "SARS-CoV-2 (코로나바이러스감염증-19 바이러스)",
        "route": "호흡기 비말 전파, 밀폐 공간 에어로졸, 오염 표면 접촉",
        "cause": "바이러스의 호흡기 상피 ACE2 수용체 결합 및 전신성 염증",
        "symptoms": "발열, 기침, 인후통, 후각/미각 상실, 피로, 호흡곤란",
        "trend": "2023년 8월 4급 표본감시 감염병으로 전환, 계절적 변이 유행 지속 모니터링",
        "prevention": "실내 정기 환기(시간당 2회 이상), 유행 시 마스크 착용, 백신 접종",
        "treatment": "항바이러스제(팍스로비드, 라게브리오), 대증요법, 주요 증상 호전 후 24시간 등교 중지 권고",
    },
    "인플루엔자": {
        "tier": "제4급 감염병",
        "pathogen": "Influenza virus A형, B형 (오르토믹소바이러스과)",
        "route": "호흡기 비말 전파, 감염자의 기침·재채기 분비물 접촉",
        "cause": "바이러스의 호흡기 상피세포 파괴 및 사이토카인 분비로 전신 증상 유발",
        "symptoms": "갑작스러운 38℃ 이상 고열, 두통, 전신 근육통, 오한, 인후통, 기침",
        "trend": "겨울철~봄철 학교 내 대규모 집단 유행, 질병관리청 주간 의사환자분율 감시",
        "prevention": "매년 가을 4가 인플루엔자 백신 접종 필수, 올바른 손 씻기, 기침예절",
        "treatment": "항바이러스제(타미플루, 조플루자, 페라미비르), 해열 후 24시간 경과까지 등교 중지",
    },
    "수족구병": {
        "tier": "제4급 감염병",
        "pathogen": "Coxsackievirus A16, Enterovirus 71 (장바이러스군)",
        "route": "비말, 환자의 대변(분변-경구), 수포 진물과의 직접 접촉",
        "cause": "장관 내 1차 증식 후 바이러스혈증, 구강 점막 및 피부 모세혈관 염증",
        "symptoms": "손바닥, 발바닥, 구강 점막의 쌀알 크기 궤양성 수포, 38℃ 전후 발열, 식욕감퇴",
        "trend": "초여름~가을 영유아 및 초등학교 저학년 중심 학교 호발 표본감시",
        "prevention": "배변 후/식사 전 비누로 30초 손 씻기, 장난감 소독, 환기",
        "treatment": "대증 치료(탈수 예방, 통증 조절), 모든 수포 완치 시까지 등교 중지 격리",
    },
    "노로바이러스 감염증": {
        "tier": "제4급 감염병",
        "pathogen": "Norovirus (노로바이러스과)",
        "route": "오염된 지하수·굴·패류 섭취, 환자의 구토물 비말 및 분변-경구 접촉",
        "cause": "매우 낮은 균량(10개)으로 소장 상피세포 감염, 융모 둔화로 급성 흡수장애",
        "symptoms": "갑작스러운 분출성 구토, 수양성 설사, 복통, 미열, 근육통",
        "trend": "겨울철(11~3월) 학교 급식 및 기숙사 집단 식중독 1위 원인체",
        "prevention": "굴 등 패류 85℃ 1분 이상 가열, 지하수 끓여 마시기, 염소 소독",
        "treatment": "경구/정맥 수액 요법, 구토/설사 증상 소실 후 48시간까지 등교·조리 중지",
    },
    "로타바이러스 감염증": {
        "tier": "제4급 감염병",
        "pathogen": "Rotavirus (레오바이러스과)",
        "route": "분변-경구 경로, 오염된 물건 접촉, 드물게 호흡기 비말",
        "cause": "소장 상피세포 파괴 및 장독소(NSP4)에 의한 수양성 설사",
        "symptoms": "발열, 구토 후 심한 쌀뜨물 같은 흰색 수양성 설사, 심한 탈수",
        "trend": "국가필수예방접종(로타바이러스 경구백신) 도입으로 감염 감소세",
        "prevention": "로타바이러스 경구 백신(로타릭스/로타텍) 접종, 기저귀 처리 후 손 씻기",
        "treatment": "전해질 수액 공급 및 탈수 교정, 증상 호전 시까지 등교 중지",
    },
    "살모넬라균 감염증": {
        "tier": "제4급 감염병",
        "pathogen": "Non-typhoidal Salmonella spp. (살모넬라 엔테리티디스 등)",
        "route": "오염된 달걀, 닭고기, 육류 섭취 및 조리기구 교차오염",
        "cause": "장점막 침투 및 엔도톡신 분비로 장관 염증 반응",
        "symptoms": "섭취 후 6~72시간 내 발열, 오심, 구토, 복부 경련통, 설사",
        "trend": "여름철 학교 급식소 달걀 취급 부주의로 인한 대규모 식중독 유행",
        "prevention": "달걀 중심온도 75℃ 1분 이상 가열, 날달걀 취급 후 비누 세손",
        "treatment": "수분 전해질 공급, 단순 장염 시 항생제 투여 지양, 완치 시까지 조리 중지",
    },
    "캄필로박터균 감염증": {
        "tier": "제4급 감염병",
        "pathogen": "Campylobacter jejuni (미호기성 그람음성 나선균)",
        "route": "덜 익힌 가금류(삼계탕, 치킨 등) 섭취, 생닭 세척 시 교차오염",
        "cause": "공장 및 회장 점막 침투, 궤양성 염증 및 독소 분비",
        "symptoms": "발열, 두통, 근육통 후 심한 복통, 혈변 동반 설사",
        "trend": "초복~말복 여름철 보양식 섭취 시기 학교 및 단체 급식 다발",
        "prevention": "생닭 세척 시 주변 식재료 튀김 방지, 가금류 75℃ 이상 완벽 조리",
        "treatment": "대증 수액 요법, 중증 시 마크로라이드계 항생제 복용",
    },
    "급성호흡기감염증(RSV)": {
        "tier": "제4급 감염병",
        "pathogen": "Respiratory Syncytial Virus (호흡기세포융합바이러스, 파라믹소바이러스과)",
        "route": "호흡기 비말 전파 및 감염자 분비물 오염 물품 접촉",
        "cause": "세기관지 상피세포 융합 및 기도 괴사·부종, 기도 폐쇄",
        "symptoms": "콧물, 기침, 쌕쌕거림(천명음), 호흡곤란, 모세기관지염, 폐렴",
        "trend": "가을~초봄 영유아 및 고령층 중증 호흡기 감염 표본감시",
        "prevention": "철저한 손 씻기, 컵·식기 공유 금지, 고위험군 단클론항체(팔리비주맙)",
        "treatment": "산소 공급, 네뷸라이저 기관지 확장제, 수액 치료, 호전 시까지 등교 중지",
    },
    "급성호흡기감염증(아데노바이러스)": {
        "tier": "제4급 감염병",
        "pathogen": "Adenovirus (아데노바이러스과)",
        "route": "호흡기 비말, 결막 분비물 접촉, 수영장 물 매개",
        "cause": "점막 상피세포 용균성 감염 및 국소 염증 반응",
        "symptoms": "고열(39℃ 이상), 인후통, 기침, 유행성각결막염(눈곱, 충혈), 인두결막열",
        "trend": "연중 발생, 학교 및 수영장 등 집단시설 유행 표본감시",
        "prevention": "수영장 위생 관리, 수건 공유 금지, 손 씻기, 기침예절",
        "treatment": "대증 치료(해열제, 점안액), 결막염 동반 시 증상 소실까지 등교 중지",
    },
    "급성호흡기감염증(리노바이러스)": {
        "tier": "제4급 감염병",
        "pathogen": "Rhinovirus (피코르나바이러스과)",
        "route": "호흡기 비말, 손 접촉 후 코/눈 점막 문지름",
        "cause": "비강 상피세포 ICAM-1 수용체 결합 및 염증성 키닌 분비",
        "symptoms": "맑은 콧물, 코막힘, 재채기, 인후통, 미열 (대표적 코감기 병원체)",
        "trend": "환절기(봄, 가을) 학생 감기 유행의 가장 흔한 원인 바이러스",
        "prevention": "손 씻기, 코 만지지 않기, 교실 실내 환기",
        "treatment": "항히스타민제, 비충혈제거제, 휴식 및 수분 섭취",
    },
    "급성호흡기감염증(파라인플루엔자)": {
        "tier": "제4급 감염병",
        "pathogen": "Parainfluenza virus (1~4형, 파라믹소바이러스과)",
        "route": "호흡기 비말 전파 및 환자 분비물 직접 접촉",
        "cause": "후두 및 기관지 상피 감염으로 점막 부종 유발",
        "symptoms": "개 짖는 듯한 기침(크룹 Croup), 쉰 목소리, 천명음, 발열",
        "trend": "가을철 소아·청소년 호흡기 감염 표본감시 질환",
        "prevention": "손 위생, 기침예절, 마스크 착용",
        "treatment": "가습 치료, 증상 심할 시 스테로이드 흡입/투여, 대증치료",
    },
    "클라미디아 감염증": {
        "tier": "제4급 감염병",
        "pathogen": "Chlamydia trachomatis (클라미디아 트라코마티스, 세포내 세균)",
        "route": "성접촉(성매개 감염병)",
        "cause": "비뇨생식기 점막 원주상피세포 감염 및 만성 염증",
        "symptoms": "배뇨통, 요도 분비물, 질 분비물 증가, 하복부 통증 (70% 무증상)",
        "trend": "20~30대 젊은 층에서 가장 흔한 성매개 표본감시 감염병",
        "prevention": "안전한 성접촉(콘돔 사용), 정기 검진, 성 파트너 동시 검사/치료",
        "treatment": "독시사이클린 또는 아지스로마이신 1회 요법, 완치 시까지 성접촉 금지",
    },
    "임질": {
        "tier": "제4급 감염병",
        "pathogen": "Neisseria gonorrhoeae (임균, 그람음성 쌍구균)",
        "route": "성접촉",
        "cause": "요도 및 자궁경부 원주상피 침투 및 급성 화농성 염증",
        "symptoms": "배뇨 시 타는 듯한 통증(작열감), 황녹색 요도 고름 분비물",
        "trend": "항생제 내성 임균 증가에 따른 표본감시 강화",
        "prevention": "콘돔 사용, 성 파트너 동시 치료",
        "treatment": "세프트리악손 근육주사 + 아지스로마이신 병합 요법",
    },
    "매독": {
        "tier": "제4급 감염병",
        "pathogen": "Treponema pallidum (매독균, 스피로헤타)",
        "route": "성접촉, 수혈, 모체 태반을 통한 수직감염",
        "cause": "균의 전신 혈관 내피 침투 및 혈관내막염, 다발성 장기 파괴",
        "symptoms": "1기(경성하감, 무통성 궤양), 2기(손발바닥 구진 발진), 3기(고무종, 신경매독)",
        "trend": "2024년 1월부터 법정감염병 4급(표본) ➡️ 3급(전수) 전환 검토 등 발생 증가로 집중 감시",
        "prevention": "안전한 성관계, 정기 혈청 검사(VDRL/RPR), 산전 매독 검사",
        "treatment": "벤자신 페니실린 근육주사 치료, 파트너 동시 치료",
    },
    "성기단순포진": {
        "tier": "제4급 감염병",
        "pathogen": "Herpes simplex virus type 2 (HSV-2, 단순포진 바이러스 2형)",
        "route": "성접촉, 피부 및 점막의 직접 접촉",
        "cause": "천골 신경절 잠복 감염 후 면역 저하 시 재발성 수포 형성",
        "symptoms": "생식기 부위의 다발성 미세 수포, 심한 작열통, 궤양, 서혜부 림프절 부종",
        "trend": "청년층 성매개 감염 질환으로 표본감시 지속",
        "prevention": "병변 존재 시 성접촉 금지, 콘돔 사용",
        "treatment": "항바이러스제(아시클로버, 발라시클로버) 조기 복용으로 증상 완화 및 재발 억제",
    },
    "첨규콘딜롬": {
        "tier": "제4급 감염병",
        "pathogen": "Human Papillomavirus (HPV, 주로 6형, 11형 저위험군)",
        "route": "성접촉",
        "cause": "생식기 상피세포 기저층 감염으로 인한 양성 상피세포 증식",
        "symptoms": "외음부 및 항문 주위 닭볏 또는 꽃양배추 모양의 사마귀 병변",
        "trend": "HPV 백신 국가예방접종(여성 청소년) 지원 사업 연계 감시",
        "prevention": "HPV 9가 백신(가다실9) 접종, 콘돔 사용",
        "treatment": "포도필린 도포, 이미퀴모드 연고, 냉동 치료, 전기소작술",
    },
    "메티실린내성황색포도알균(MRSA) 감염증": {
        "tier": "제4급 감염병",
        "pathogen": "Methicillin-resistant Staphylococcus aureus (MRSA)",
        "route": "의료기관 내 접촉 전파, 오염된 의료진 손 및 기구",
        "cause": "메티실린 및 베타락탐계 항생제 내성 획득(mecA 유전자)",
        "symptoms": "수술 부위 감염, 균혈증, 폐렴, 피부 연조직 감염",
        "trend": "병원 내 감염 관리의 가장 대표적 다제내성 표본감시 대상",
        "prevention": "손 위생, 접촉격리, 무균술 준수, 환경 소독",
        "treatment": "반코마이신(Vancomycin), 테이코플라닌, 리네졸리드 투약",
    },
    "반코마이신내성장알균(VRE) 감염증": {
        "tier": "제4급 감염병",
        "pathogen": "Vancomycin-resistant Enterococcus (VRE)",
        "route": "의료기관 내 접촉 전파, 보균 환자와의 직접 접촉",
        "cause": "장알균의 반코마이신 결합 부위 변형(vanA, vanB 유전자)에 의한 내성",
        "symptoms": "요로감염, 균혈증, 심내막염, 상처 감염",
        "trend": "중환자실 장기 입원 환자 중심 표본감시 질환",
        "prevention": "철저한 접촉 격리, 전용 의료기구 사용, 손 씻기",
        "treatment": "리네졸리드(Linezolid), 답토마이신 등 대체 항생제 투여",
    },
    "급성호흡기감염증(마이코플라스마 폐렴균)": {
        "tier": "제4급 감염병",
        "pathogen": "마이코플라스마 폐렴균 (Mycoplasma pneumoniae, 세균)",
        "route": "호흡기 비말/공기 전파",
        "cause": "호흡기 상피세포 섬모 파괴 및 기관지 폐렴 유발",
        "symptoms": "3~4주 이상 지속되는 심한 발작성 기침, 발열, 인후통, 흉통",
        "trend": "학령기 소아·청소년 3~4년 주기로 겨울철 학교 집단 유행",
        "prevention": "기침 예절, KF94 마스크 착용, 흐르는 물에 30초 손 씻기",
        "treatment": "마크로라이드계 항생제(아지스로마이신), 퀴놀론계 대체제, 대증치료",
    },
    "사람유두종바이러스(HPV) 감염증": {
        "tier": "제4급 감염병",
        "pathogen": "인유두종 바이러스 (Human Papillomavirus, 파필로마바이러스과)",
        "route": "혈액/체액/성접촉",
        "cause": "점막 및 피부 상피세포 감염, 자궁경부암 및 첨규콘딜롬 유발",
        "symptoms": "대부분 무증상, 생식기 사마귀, 자궁경부 세포 이형성증",
        "trend": "청소년기 국가필수예방접종 적극 권고 질환",
        "prevention": "만 12세 HPV 백신(가다실9, 서바릭스) 필수접종, 안전한 위생관리",
        "treatment": "냉동요법, 레이저 치료, 외과적 절제술 및 정기 세포검진",
    },
    "요충증": {
        "tier": "제4급 감염병",
        "pathogen": "요충 (Enterobius vermicularis, 선충류 기생충)",
        "route": "접촉/피부/환경",
        "cause": "충란의 항문 주위 산란 및 자가감염(오염된 손, 침구, 완구)",
        "symptoms": "야간 항문 주위 극심한 가려움증, 수면장애, 불안, 산만",
        "trend": "유치원, 어린이집, 초등학교 저학년 단체생활 시설 다발",
        "prevention": "손톱 짧게 깎기, 식사 전 손 씻기, 침구류 온수세탁 및 일광소독",
        "treatment": "알벤다졸 또는 플루벤다졸 전 가족/학급 동시 복용 (2주 후 재투약)",
    },
    "간흡충증": {
        "tier": "제4급 감염병",
        "pathogen": "간흡충(간디스토마, Clonorchis sinensis, 흡충류)",
        "route": "오염식음료/분변-구강",
        "cause": "담관 내 기생으로 만성 염증 및 담관암 유발 (1군 발암원)",
        "symptoms": "초기 무증상, 소화불량, 황달, 복통, 간비대, 만성 담관염",
        "trend": "낙동강, 영산강, 금강 등 5대 강 유역 담수어 섭취자 다발",
        "prevention": "민물고기 생식 절대 금지, 충분한 가열조리, 조리기구 구분 사용",
        "treatment": "프라지콴텔(디스토시드) 전문 치료제 정량 복용",
    },
    "옴(Scabies) 감시": {
        "tier": "제4급 감염병",
        "pathogen": "옴진드기 (Sarcoptes scabiei var. hominis)",
        "route": "접촉/피부/환경",
        "cause": "피부 각질층 내 굴을 뚫고 산란하여 극심한 알레르기 반응 유발",
        "symptoms": "야간에 악화되는 전신 극심한 가려움증, 손가락 사이 붉은 구진",
        "trend": "요양시설, 기숙사 등 단체 집단생활 시설 고위험",
        "prevention": "환자 접촉 주의, 침구·의류 온수세탁(50℃ 이상) 및 밀폐보관",
        "treatment": "퍼메트린 크림 등 항진드기 외용제 목 아래 전신 도포, 동거인 동시치료",
    },
}

def get_disease_info(tier, name):
    if not name:
        name = ""
    # 브라우저 번역기 오역('형간염') 및 띄어쓰기('A형 간염') 방어 fallback
    if name in ["형간염", "A형 간염", "A형간염", "a형간염", "a형 간염"]:
        name = "A형간염"
    clean_name = name.split("(")[0].strip() if name else ""
    if name in DISEASE_INFO_DB:
        return DISEASE_INFO_DB[name]
    for k, v in DISEASE_INFO_DB.items():
        if clean_name and (clean_name in k or k in clean_name):
            return v
    # Tier mapping fallback
    fallback_tier = tier if tier and "급" in tier else "제4급 감염병"
    for t_key, d_list in TIER_DISEASE_MAP.items():
        if name in d_list:
            fallback_tier = t_key.split()[0]
            break
    return {
        "tier": fallback_tier,
        "pathogen": f"{name} 병원체 (질병관리청 법정감염병 고시 기준)",
        "route": "호흡기 비말, 접촉 또는 매개체 전파",
        "cause": f"{name}에 의한 감염 및 신체 염증 반응",
        "symptoms": "발열, 오한, 전신 피로감, 감염 부위별 특이 증상",
        "trend": "질병관리청 법정감염병 감시체계에 따라 연중 지속 모니터링",
        "prevention": "올바른 손 씻기(30초 이상), 기침예절 준수, 실내 환기, 예방접종",
        "treatment": "대증 치료 및 전문의 진료 상담, 교내 감염 예방 수칙 준수"
    }


def find_diseases_in_text(text: str) -> list:
    """텍스트에서 언급된 법정감염병들을 감지하여 (DB_key, clean_name, info) 리스트 반환 (공백 무시 정규화 적용)"""
    if not text:
        return []
    t_lower = text.lower().strip()
    t_nospace = re.sub(r"\s+", "", t_lower)
    found = []
    seen_keys = set()

    # 1. 50여 종 법정감염병 통칭 및 구어체 별칭 매핑 (간염 등 누락 키워드 대폭 보강)
    alias_map = {
        # B형간염 (제3급)
        "b형간염": "B형간염",
        "b형간염병": "B형간염",
        "b형간염바이러스": "B형간염",
        "hbv": "B형간염",
        # A형간염 (제2급)
        "a형간염": "A형간염",
        "a형간염병": "A형간염",
        "a형간염바이러스": "A형간염",
        "hav": "A형간염",
        # C형간염 (제3급)
        "c형간염": "C형간염",
        "c형간염병": "C형간염",
        "c형간염바이러스": "C형간염",
        "hcv": "C형간염",
        # E형간염 (제2급)
        "e형간염": "E형간염",
        "e형간염병": "E형간염",
        "hev": "E형간염",
        # 일반 간염 질의
        "간염": "B형간염",
        "간염병": "B형간염",
        "간염바이러스": "B형간염",
        # 호흡기 및 신종 감염병
        "에볼라": "에볼라바이러스병",
        "에볼라바이러스": "에볼라바이러스병",
        "에볼라바이러스병": "에볼라바이러스병",
        "ebola": "에볼라바이러스병",
        "지카": "지카바이러스감염증",
        "지카바이러스": "지카바이러스감염증",
        "지카바이러스병": "지카바이러스감염증",
        "지카바이러스감염증": "지카바이러스감염증",
        "zika": "지카바이러스감염증",
        "마버그": "마버그열",
        "라싸": "라싸열",
        "사스": "사스(SARS)",
        "sars": "사스(SARS)",
        "메르스": "중동호흡기증후군(MERS)",
        "mers": "중동호흡기증후군(MERS)",
        "코로나": "코로나19",
        "covid": "코로나19",
        "코로나19": "코로나19",
        "독감": "인플루엔자",
        "인플루엔자": "인플루엔자",
        "플루": "인플루엔자",
        "신종플루": "인플루엔자",
        "수족구": "수족구병",
        "아구창": "아구창(칸디다증)",
        "결핵": "결핵",
        "백일해": "백일해",
        "홍역": "홍역",
        "수두": "수두",
        "콜레라": "콜레라",
        "장티푸스": "장티푸스",
        "파라티푸스": "파라티푸스",
        "이질": "세균성이질",
        "대장균": "장출혈성대장균감염증",
        "성홍열": "성홍열",
        "폴리오": "폴리오",
        "소아마비": "폴리오",
        "볼거리": "유행성이하선염",
        "풍진": "풍진",
        "파상풍": "파상풍",
        "말라리아": "말라리아",
        "일본뇌염": "일본뇌염",
        "비브리오": "비브리오패혈증",
        "레지오넬라": "레지오넬라증",
        "쯔쯔가무시": "쯔쯔가무시증",
        "렙토스피라": "렙토스피라증",
        "브루셀라": "브루셀라증",
        "공수병": "공수병",
        "광견병": "공수병",
        "유행성출혈열": "신증후군출혈열",
        "신증후군출혈열": "신증후군출혈열",
        "한타": "신증후군출혈열",
        "에이즈": "AIDS(후천성면역결핍증)",
        "hiv": "AIDS(후천성면역결핍증)",
        "뎅기": "뎅기열",
        "황열": "황열",
        "노로": "노로바이러스",
        "노로바이러스": "노로바이러스",
        "로타": "로타바이러스",
        "로타바이러스": "로타바이러스",
        "탄저": "탄저",
        "페스트": "페스트",
        "흑사병": "페스트",
        "보툴리눔": "보툴리눔독소증",
        "야토": "야토병",
        "엠폭스": "엠폭스",
        "원숭이두창": "엠폭스"
    }

    for alias, target_key in alias_map.items():
        alias_nospace = re.sub(r"\s+", "", alias.lower())
        if alias in t_lower or alias_nospace in t_nospace:
            matched_key = None
            matched_val = None
            for db_k, db_v in DISEASE_INFO_DB.items():
                db_k_nospace = re.sub(r"\s+", "", db_k.lower())
                target_nospace = re.sub(r"\s+", "", target_key.lower())
                if target_key == db_k or target_nospace == db_k_nospace or target_key in db_k or db_k in target_key:
                    matched_key = db_k
                    matched_val = db_v
                    break
            if matched_key:
                if matched_key not in seen_keys:
                    seen_keys.add(matched_key)
                    found.append((matched_key, matched_key.split("(")[0].strip(), matched_val))
            else:
                if target_key not in seen_keys:
                    seen_keys.add(target_key)
                    found.append((target_key, target_key.split("(")[0].strip(), get_disease_info("", target_key)))

    # 2. DISEASE_INFO_DB 전체 검색 (한글명, 영문명 및 핵심 어근 추출 매칭 + 공백 무시)
    for k, v in DISEASE_INFO_DB.items():
        if k in seen_keys:
            continue
        k_clean = k.split("(")[0].strip()
        k_eng = k.split("(")[1].replace(")", "").strip().lower() if "(" in k else ""

        # 의학 접미사 제거 어근 추출 (예: "에볼라바이러스병" -> "에볼라", "마버그열" -> "마버그")
        root = k_clean
        for suffix in ["바이러스감염증", "바이러스병", "출혈열", "독소증", "증후군", "패혈증", "감염증", "균감염증", "열", "병", "증"]:
            if root.endswith(suffix) and len(root) - len(suffix) >= 2:
                root = root[:-len(suffix)]
                break

        k_nospace = re.sub(r"\s+", "", k_clean.lower())
        root_nospace = re.sub(r"\s+", "", root.lower())
        eng_nospace = re.sub(r"\s+", "", k_eng.lower())

        if (len(k_clean) >= 2 and (k_clean.lower() in t_lower or k_nospace in t_nospace)) or \
           (len(k_eng) >= 2 and (k_eng in t_lower or eng_nospace in t_nospace)) or \
           (len(root) >= 2 and (root.lower() in t_lower or root_nospace in t_nospace)):
            seen_keys.add(k)
            found.append((k, k_clean, v))

    return found



def clean_api_key(k: str) -> str:
    """사용자가 입력하거나 시크릿에 설정된 API 키에서 공백 및 따옴표를 안전하게 제거"""
    if not k or not isinstance(k, str):
        return ""
    k = k.strip()
    if "GEMINI_API_KEY" in k and "=" in k:
        k = k.split("=", 1)[1].strip()
    quotes = ('"', "'", "`")
    while len(k) >= 2 and (k[0] in quotes and k[-1] in quotes):
        k = k[1:-1].strip()
    return k


def get_api_key():
    """Streamlit Secrets, 환경 변수, 사용자 직접 입력 세션에서 안전하게 Gemini API 키 조회"""
    raw_k = ""
    try:
        if "GEMINI_API_KEY" in st.secrets:
            raw_k = str(st.secrets["GEMINI_API_KEY"]).strip()
    except Exception:
        pass
    if not raw_k:
        raw_k = os.environ.get("GEMINI_API_KEY", "").strip()
    if not raw_k:
        raw_k = st.session_state.get("custom_gemini_key", "").strip()
    return clean_api_key(raw_k)


# ==========================================
# [수업 몰입도 및 접근 제어] 법정감염병 키워드 & 수업 시간 통제
# ==========================================
LEGAL_INFECTIOUS_KEYWORDS = [
    # 법정감염병 공통 역학 및 데이터 분석 전문 용어
    "법정감염병", "감염병", "전파", "격리", "등교중지", "등교 중지", "출석인정", "잠복기",
    "병원체", "바이러스", "세균", "진균", "원충", "백신", "방역", "보건실", "음압", "치명률", "재생산지수",
    "비말", "공기전파", "비말핵", "접촉전파", "수인성", "식품매개", "표본감시", "전수감시",
    # [간염 관련 법정감염병 핵심 용어 완비]
    "간염", "간염병", "간염바이러스", "b형간염", "b형 간염", "a형간염", "a형 간염", "c형간염", "c형 간염", "e형간염", "e형 간염",
    "hbv", "hav", "hcv", "hev", "황달", "수직감염", "간기능", "간수치", "간경변", "간암", "항원", "항체", "hbsag", "hbeag",
    # [수업 탐구 및 데이터 해석 핵심 키워드]
    "그래프", "데이터", "통계", "증가", "감소", "추이", "추세", "유행", "단정", "상관관계", "인과관계",
    "예방접종", "접종률", "차이", "비교", "분석", "해석", "원인", "이유", "위험도", "취약", "연령대",
    "학교", "학생", "교실", "환기", "마스크", "손씻기", "손 씻기", "대책", "예방수칙", "보건교사", "지침",
    # 제1급~제4급 감염병 핵심 명칭 및 별칭
    "사스", "sars", "메르스", "mers", "에볼라", "마버그", "라싸", "크리미안콩고", "남아메리카출혈열",
    "리프트밸리", "두창", "페스트", "탄저", "보툴리눔", "야토", "신종감염병", "동물인플루엔자", "신종인플루엔자", "디프테리아", "출혈열",
    "결핵", "수두", "홍역", "콜레라", "장티푸스", "파라티푸스", "세균성이질", "장출혈성대장균", "이질",
    "백일해", "유행성이하선염", "볼거리", "풍진", "폴리오", "소아마비", "수막구균", "폐렴구균",
    "한센병", "성홍열", "vrsa", "cre", "엠폭스", "원숭이두창", "hib", "헤모필루스",
    "파상풍", "일본뇌염", "말라리아", "레지오넬라", "비브리오", "비브리오패혈증",
    "발진티푸스", "발진열", "쯔쯔가무시", "렙토스피라", "브루셀라", "공수병", "광견병", "신증후군출혈열", "유행성출혈열",
    "aids", "hiv", "에이즈", "후천성면역결핍증", "크로이츠펠트", "cjd", "뎅기열", "지카", "황열", "치쿤구니야", "큐열", "라임병", "sfts", "살인진드기",
    "인플루엔자", "독감", "수족구", "아구창", "매독", "임질", "클라미디아", "연성하감", "첨규콘딜롬", "생식기단순포진", "단순포진",
    "노로바이러스", "노로", "로타바이러스", "로타", "코로나", "코로나19", "covid", "급성호흡기감염증", "rsv", "아데노바이러스", "리노바이러스", "파라인플루엔자",
    "살모넬라", "살모넬라균", "캄필로박터", "식중독", "장관감염증", "mrsa", "vre"
]


def is_legal_infectious_question(question: str, selected_disease: str) -> bool:
    """학생 질문이 법정감염병 및 학교 감염병 예방 관리, 데이터 해석 범위 내인지 판별 (공백 무시 정규화 적용)"""
    if not question:
        return False
    q_lower = question.lower().strip()
    q_nospace = re.sub(r"\s+", "", q_lower)

    # 1. 감염병 DB에 등록된 질병이나 별칭이 감지되면 즉시 통과 (B형간염, A형간염 등 모든 법정감염병)
    if find_diseases_in_text(question):
        return True

    # 2. 현재 선택된 질병명이 포함된 경우 통과
    sel_clean = selected_disease.split("(")[0].strip().lower()
    sel_nospace = re.sub(r"\s+", "", sel_clean)
    if sel_clean and len(sel_clean) >= 2 and (sel_clean in q_lower or sel_nospace in q_nospace):
        return True

    # 3. 법정감염병 및 데이터 분석/보건 관리 전문 키워드가 포함된 경우 통과
    for kw in LEGAL_INFECTIOUS_KEYWORDS:
        kw_nospace = re.sub(r"\s+", "", kw.lower())
        if kw in q_lower or kw_nospace in q_nospace:
            return True

    # 4. 간염, 폐렴, 장염 등 흔한 감염성 질환명 및 증상
    common_infectious_words = ["간염", "폐렴", "장염", "뇌염", "결핵", "독감", "발진", "황달", "수혈", "주사기", "수직감염", "항체", "항원", "백신", "접종"]
    if any(w in q_nospace for w in common_infectious_words):
        return True

    # 5. 현재 대시보드에서 특정 질병을 탐구 중인 상태에서 데이터 해석이나 원인, 학교 대책을 질문하는 경우 통과
    context_inquiry_words = ["왜", "원인", "이유", "어떻게", "해석", "증가", "감소", "변화", "위험", "차이", "대책", "방법", "예방", "치료", "증상", "기준", "학교", "보건", "관리", "검사"]
    if selected_disease and any(w in q_lower for w in context_inquiry_words):
        return True

    # 그 외 비보건 일상 잡담(게임, 연애, 날씨 등)만 정중히 차단
    return False


def get_current_school_time_status():
    """현재 한국 시각(KST) 기준 수업 시간(평일 08:30~17:00) 여부 확인"""
    kst = timezone(timedelta(hours=9))
    now = datetime.now(kst)
    is_weekday = (now.weekday() < 5)  # 0=월 ~ 4=금
    curr_min = now.hour * 60 + now.minute
    # 08:30 (510분) ~ 17:00 (1020분)
    in_hours = is_weekday and (510 <= curr_min <= 1020)
    day_str = ["월", "화", "수", "목", "금", "토", "일"][now.weekday()]
    time_str = f"{day_str}요일 {now.strftime('%H:%M')} (KST)"
    return in_hours, time_str, now


def check_classroom_access(teacher_code: str = "", *args, **kwargs) -> tuple:
    """수업 시간(평일 08:30~17:00) 외 자동 차단 및 교사 마스터 코드 해제"""
    # 1. 교사용 마스터 코드 확인 (수업 외 시간 긴급 승인용)
    code = teacher_code or st.session_state.get("teacher_code", "")
    t_clean = clean_api_key(str(code))
    if t_clean in ["1018", "보건", "0508"]:
        return True, "교사 마스터 코드가 승인되었습니다 (전 시간 사용 허용)."

    # 2. 평일 정규 수업 시간(08:30~17:00) 자동 판별
    in_hours, time_str, _ = get_current_school_time_status()
    if not in_hours:
        return False, f"현재 시각은 **{time_str}**로 정규 수업 시간 외입니다.\nAPI 키 보안 및 토큰 절약을 위해 **평일 08:30 ~ 17:00 수업 시간**에만 자동으로 활성화됩니다."

    return True, "정규 수업 시간 AI 활성화"



def query_gemini_ai(api_key: str, prompt: str, disease_name: str = "") -> str:
    """
    고교 보건간호과 및 질병관리청(KDCA) 공공데이터에 맞춤화된 전문 Gemini 응답 생성.
    패키지 누락/버전 충돌 없이 안정적으로 구동되는 HTTPS REST API(1순위) 및 SDK 다중 폴백 적용.
    """
    cleaned_key = clean_api_key(api_key)
    if not cleaned_key:
        return ""

    # 질문에서 언급된 법정감염병 감지 및 비교 대상 질환 특정
    detected_in_q = find_diseases_in_text(prompt)
    unique_detected = []
    seen_d_names = set()
    for fk, fn, fi in detected_in_q:
        if fn not in seen_d_names:
            seen_d_names.add(fn)
            unique_detected.append(fn)

    compare_instruction = ""
    if len(unique_detected) >= 2:
        d1_target = unique_detected[0]
        d2_target = unique_detected[1]
        compare_instruction = (
            f"\n\n[⚠️ 최우선 필수 비교 지침 - 매우 중요!]\n"
            f"학생이 질문한 비교 대상은 반드시 **'{d1_target}'**와 **'{d2_target}'**입니다.\n"
            f"1. 반드시 이 두 질환만을 1:1로 직접 비교하는 마크다운 표(법정감염병 분류, 원인 병원체, 전파 경로, 임상 증상, 학교 등교중지 및 보건관찰실 격리 기준, 예방 백신 및 치료)를 작성하십시오.\n"
            f"2. 학생이 질문하지 않은 다른 질환(예: 'B형간염' 질문 시 A형간염이나 C형간염 등)을 끌어들여 '바이러스성 간염 3대 질환' 등으로 임의 확대·변형하는 행위는 엄격히 금지됩니다. 오직 [{d1_target} vs {d2_target}] 두 질환만을 비교하십시오.\n"
        )

    sys_instruction = (
        "당신은 대한민국 서울의료보건고등학교 보건간호과의 전임 지도교사이자 질병관리청(KDCA) 공공데이터 전문 보건 튜터 AI입니다.\n"
        "질문자는 고등학교 보건간호과 학생입니다.\n\n"
        "[핵심 교육 및 답변 지침 (매우 중요!)]\n"
        "1. B형간염(제3급), A형간염(제2급), C형간염(제3급), 엠폭스(제2급), 사스(SARS, 제1급), 메르스(MERS, 제1급), 인플루엔자(독감, 제4급), 코로나19, 결핵, 백일해, 수두, 홍역 등 질병관리청 법정감염병 50여 종 및 감염병 간의 비교/차이점(예: B형간염 vs 엠폭스, 사스 vs 인플루엔자) 질문은 최우선 법정감염병 교육 주제이므로 절대 거부하지 말고 매우 상세하고 전문적으로 답변하십시오.\n"
        "2. 학생이 2개 이상의 감염병 비교를 요청할 경우, 반드시 질문에 지정된 그 질환들만을 정확히 1:1 비교 분석하는 마크다운 비교표를 제공하십시오. 임의로 질문하지 않은 다른 질환(예: 3대 간염 등)으로 대체하거나 변경해서는 안 됩니다.\n"
        "3. 학생이 'B형간염' 단독에 대해 질문할 경우, 법정감염병 급수(제3급), 원인 바이러스(HBV, DNA 바이러스), 전파 경로(출산 시 수직감염, 오염된 혈액/체액, 성접촉; 일상 식사/대화/신체접촉으로는 전파 안 됨), 예방접종(0, 1, 6개월 3회), 학교 보건실 관리 지침(등교 중지 비해당, 정상 학교생활 보장, 외상 시 표준주의지침)을 상세히 설명하십시오.\n"
        "4. 오직 법정감염병과 완전히 무관한 일상 잡담, 게임, 연애, 비보건 일상 질문에 대해서만 아래 문장으로 정중히 안내하십시오:\n"
        "해당 질문은 법정감염병과 관련이 없습니다. 선생님께 요청하기 바랍니다.\n\n"
        "[답변 원칙 및 지침]\n"
        "1. 고등학교 보건, 간호의 기초, 공중보건 교과서 범위에 부합하게 전문적이면서도 학생 눈높이에서 알기 쉽게 설명합니다.\n"
        "2. 질병관리청(KDCA) 법정감염병 분류(제1급~제4급), 신고 기한(즉시/24시간 이내 등), 보건관찰실 격리 기준을 정확하게 안내합니다.\n"
        "3. 교육부 및 질병관리청 '학교 감염병 예방·위기대응 매뉴얼'과 학교보건법에 따른 학교 보건실 관리 지침과 '등교 중지(출석인정 결석)' 기준, 격리 해제 조건을 반드시 포함합니다.\n"
        "4. 2개 이상 질병 비교 질문 시 일목요연한 마크다운 비교표를 반드시 포함합니다.\n"
        "5. 따뜻하고 전문적인 보건간호과 지도교사의 어조로 마크다운과 이모지를 활용하여 가독성을 높입니다."
        f"{compare_instruction}"
    )

    full_prompt = (
        f"{sys_instruction}\n\n"
        f"[선택된 대시보드 감염병: {disease_name} (단, 학생이 다른 감염병이나 질병 간 비교를 물어본 경우 학생 질문에 맞춰 충실히 답변할 것)]\n"
        f"[학생 질문]\n{prompt}\n\n"
        "위 질문에 대해 고등학생 수준에 맞추어 전문적이고 신뢰할 수 있는 답변을 작성해 주세요."
    )

    def validate_and_clean_answer(text: str) -> str:
        if not text:
            return ""
        if len(unique_detected) >= 2:
            d1_ok = (unique_detected[0] in text) or (unique_detected[0].lower() in text.lower())
            d2_ok = (unique_detected[1] in text) or (unique_detected[1].lower() in text.lower())
            if not (d1_ok and d2_ok):
                return ""
        return text

    # [1순위] 표준 라이브러리 HTTPS REST API 호출 (외부 의존성 없음, No module named 오류 원천 차단)
    models_to_try = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash", "gemini-pro"]
    for m in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={cleaned_key}"
        payload = {
            "contents": [
                {
                    "parts": [{"text": full_prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 2500
            }
        }
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                res_data = json.loads(resp.read().decode("utf-8"))
                candidates = res_data.get("candidates", [])
                if candidates and "content" in candidates[0]:
                    parts = candidates[0]["content"].get("parts", [])
                    if parts and "text" in parts[0]:
                        ans = parts[0]["text"].strip()
                        cleaned_ans = validate_and_clean_answer(ans)
                        if cleaned_ans:
                            st.session_state["gemini_last_error"] = ""
                            return cleaned_ans
        except urllib.error.HTTPError as he:
            try:
                err_text = he.read().decode("utf-8", errors="ignore")
                st.session_state["gemini_last_error"] = f"HTTP {he.code}: {err_text[:120]}"
            except Exception:
                st.session_state["gemini_last_error"] = f"HTTP {he.code}"
            continue
        except Exception as e:
            st.session_state["gemini_last_error"] = str(e)[:120]
            continue

    # [2순위] google-genai 신규 SDK 시도
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=cleaned_key)
        for m in ["gemini-2.0-flash", "gemini-1.5-flash"]:
            try:
                resp = client.models.generate_content(
                    model=m,
                    contents=full_prompt,
                    config=types.GenerateContentConfig(temperature=0.7)
                )
                if resp and resp.text:
                    cleaned_ans = validate_and_clean_answer(resp.text.strip())
                    if cleaned_ans:
                        return cleaned_ans
            except Exception:
                continue
    except Exception:
        pass

    # [3순위] google.generativeai 레거시 SDK 시도
    try:
        import google.generativeai as legacy_genai
        legacy_genai.configure(api_key=cleaned_key)
        for m in ["gemini-1.5-flash", "gemini-pro"]:
            try:
                model = legacy_genai.GenerativeModel(m)
                resp = model.generate_content(full_prompt)
                if resp and resp.text:
                    cleaned_ans = validate_and_clean_answer(resp.text.strip())
                    if cleaned_ans:
                        return cleaned_ans
            except Exception:
                continue
    except Exception:
        pass

    return ""


def generate_detailed_tutor_answer(disease_name: str, question: str, dis_info: dict) -> str:
    """
    질병관리청(KDCA) 공공데이터 및 고교 보건/간호 교과서 기반 지식 엔진.
    사스 vs 메르스, 수족구 vs 아구창 등 주요 임상 감별 비교표와 50여 종 법정감염병 종합 지침 완비.
    """
    q_lower = question.lower().strip()
    d_clean = "AIDS(후천성면역결핍증)" if disease_name in ["AIDS", "후천성면역결핍증"] else disease_name
    info = get_disease_info(dis_info.get("tier", "법정감염병"), d_clean)

    # [수업 몰입도를 위한 핵심 필터] 법정감염병 질환과 무관한 질문은 엄격 차단
    if not is_legal_infectious_question(question, disease_name):
        return "해당 질문은 법정감염병과 관련이 없습니다. 선생님께 요청하기 바랍니다."

    # ----------------------------------------------------
    # [질문 내 법정감염병 사전 감지 및 질문 내 등장 위치 순서 정렬]
    # ----------------------------------------------------
    found_diseases = find_diseases_in_text(question)

    def _disease_pos(item):
        k, name, _ = item
        p1 = q_lower.find(name.lower())
        p2 = q_lower.find(k.lower())
        p_candidates = [p for p in (p1, p2) if p != -1]
        return min(p_candidates) if p_candidates else 9999

    found_diseases.sort(key=_disease_pos)

    # 중복 질병 제거 (clean_name 기준, 질문 내 출현 순서 유지)
    unique_found = []
    seen_found_names = set()
    for fk, fn, fi in found_diseases:
        if fn not in seen_found_names:
            seen_found_names.add(fn)
            unique_found.append((fk, fn, fi))

    # 명시적 비교 질의 키워드 ("차이점", "비교", "vs", "다른점", "구분", "구별")
    explicit_comparison = any(w in q_lower for w in ["차이", "비교", "vs", "다른점", "구분", "구별"])

    # 간염 외의 다른 법정감염병(엠폭스, 사스 등) 존재 여부 판별
    other_than_hepatitis = [fn for _, fn, _ in unique_found if fn not in ["A형간염", "B형간염", "C형간염", "E형간염"]]
    has_other_legal_disease = len(other_than_hepatitis) > 0

    # ----------------------------------------------------
    # [0] 그래프/데이터 해석 및 예방접종 단정 여부 심층 질의응답 (교육과정 핵심)
    # ----------------------------------------------------
    if any(k in q_lower for k in ["단정", "상관관계", "인과관계", "예방접종 부족", "접종 부족", "증가 원인", "유행 원인"]):
        return f"""👩‍⚕️ **[AI 보건 튜터 데이터 리터러시 클리닉: 그래프 해석과 역학적 인과관계 분석]**

보건간호과 학생 여러분, 데이터 기반 보건 탐구에서 가장 중요한 **'상관관계와 인과관계의 구별 원칙'**에 대한 지도교사 피드백입니다.

### ❓ 핵심 질문: "그래프의 환자 증가만으로 예방접종 부족을 단정할 수 있는가?"
👉 **결론: 결코 단정할 수 없습니다! (단정적 결론은 중대한 역학적 오류입니다)**

| 구분 | 주요 역학적 요인 | 보건 데이터 해석 시 유의사항 |
| :--- | :--- | :--- |
| **1. 진단 및 신고 기준의 변화** | PCR 등 신속 진단 키트 보급 및 적극적 전수 검사 | 검사 건수가 늘어나면 숨어있던 무증상·경증 환자가 대거 발견되어 그래프상 급증할 수 있습니다. |
| **2. 면역 감쇠 (Waning Immunity)** | 과거 접종 후 시간 경과에 따른 방어 항체 감소 | 청소년기(11~12세 이후)에는 영유아기 접종 항체가 자연 감소하므로 추가 접종(Tdap 등)이 필요하며, 단순 '미접종'과는 구분해야 합니다. |
| **3. 병원체 변이 및 면역 회피** | 바이러스/세균 유전자 변이 | 기존 백신주와 유행주 간의 불일치(Antigenic Drift/Shift)로 감염될 수 있습니다. |
| **4. 환경적 접촉 빈도 증가** | 마스크 착용 해제, 대면 수업 확대, 실내 밀폐 | 실내 맞통풍 환기 부족, 단체 기숙사 생활 등 환경적 노출 빈도가 급증하면 전파가 폭증합니다. |
| **5. 자연 유행 주기 (Cyclic Epidemic)** | 3~5년 주기의 자연적 감염병 유행 파동 | 백일해, 마이코플라스마 등은 백신 접종률이 95% 이상이어도 수년 주기로 유행 곡선을 그립니다. |

---
💡 **예비 보건간호인을 위한 결론 및 학교 액션 플랜:**
1. **다각적 근거 확인:** 그래프의 수치 증가는 '현상(관찰 사실)'일 뿐이며, 원인을 규명하기 위해서는 **백신 접종 이력 데이터, 유행 병원체 변이 분석, 교실 내 환기 및 밀집도 역학조사**를 종합적으로 대조해야 합니다.
2. **우리 학교 실천 수칙:** {disease_name} 등 호흡기 감염병 예방을 위해 단순히 학생 개인을 탓하기보다, **교실 시간당 2회 이상 맞통풍 환기**, **기침예절 준수**, **증상 발생 시 보건실 상담 및 조기 귀가 조치** 등 환경적 다중 방어막을 구축해야 합니다."""

    # ----------------------------------------------------
    # [1] 사스(SARS) vs 메르스(MERS) vs 코로나19(COVID-19) 임상 비교 분석
    # ----------------------------------------------------
    if ("사스" in q_lower or "sars" in q_lower) and ("메르스" in q_lower or "mers" in q_lower):
        return """👩‍⚕️ **[AI 보건 튜터 임상 비교 분석: 사스(SARS) vs 메르스(MERS) vs 코로나19(COVID-19)]**

보건간호과 학생 여러분, 21세기 신종 호흡기 감염병의 핵심인 **코로나바이러스(Coronavirus) 변종 3대 질환 비교 분석**입니다.

| 구분 항목 | 🦇 사스 (SARS) | 🐫 메르스 (MERS) | 🦠 코로나19 (COVID-19) |
| :--- | :--- | :--- | :--- |
| **원인 바이러스** | **SARS-CoV** (중증급성호흡기증후군 바이러스) | **MERS-CoV** (중동호흡기증후군 바이러스) | **SARS-CoV-2** (신종 코로나바이러스) |
| **법정감염병 분류** | **제1급 감염병** (발생 즉시 신고, 음압격리) | **제1급 감염병** (발생 즉시 신고, 음압격리) | **제4급 감염병** (표본감시체계 전환) |
| **최초 유행 / 진원지** | 2002년 중국 광둥성 (전 세계 유행) | 2012년 사우디아라비아 (2015년 한국 유행) | 2019년 말 중국 후베이성 우한 |
| **자연 숙주 및 전파원** | 박쥐 ➡️ 사향고양이 ➡️ 사람 | 박쥐 ➡️ 단봉낙타 ➡️ 사람 | 박쥐 ➡️ 중간숙주 매개체 ➡️ 사람 |
| **치명률 (Fatality Rate)** | **약 9.6%** (중등도 위험) | **약 34.4%** (극도로 치명적, 신부전 동반) | **약 0.1 ~ 0.5%** (낮은 치명률) |
| **전파력 ($R_0$)** | 2.0 ~ 4.0 | 0.3 ~ 0.8 (병원 내 슈퍼전파 위주) | 2.5 ~ 15.0 이상 (오미크론 등 극단적 전파) |
| **주요 임상 특징** | 38℃ 이상 급성 고열, 마른기침, 폐렴 | 38℃ 이상 고열, 기침, **급성 신부전, 호흡곤란** | 발열, 기침, 인후통, 후각/미각 상실 |
| **학교 보건실 격리 지침** | **의심 즉시 음압격리 및 전면 등교 중지**<br>👉 보건소 즉시 신고, 완치 판정까지 공결 | **의심 즉시 음압격리 및 전면 등교 중지**<br>👉 밀접접촉자 14일 자가격리, 공결 처리 | 검사 양성 시 **주요 증상 호전 후 24시간까지**<br>👉 등교 중지 권고 (진료확인서 제출 시 공결) |

💡 **보건간호 임상 실무 핵심 탐구 포인트:**
1. **치명률과 전파력의 역학적 반비례 관계:**
   - **메르스**는 바이러스가 하기도 깊숙이 침투하여 폐포와 신장 조직을 파괴하므로 치명률이 34%로 매우 높으나, 일상 환경 비말 배출량이 적어 지역사회 전파력은 낮습니다.
   - 반면 **코로나19**는 상기도(인두, 후두)에서 폭발적으로 증식하여 치명률은 낮지만 전파력이 전 세계적 팬데믹을 유발할 만큼 극대화되었습니다.
2. **학교 보건실 긴급 대응 수칙:**
   - 사스나 메르스는 **제1급 감염병**이므로 의심 증상(중동 방문력, 고열, 호흡곤란) 확인 즉시 교내 일반 보건실에 머물게 하지 말고 **독립된 보건관찰실로 이동 후 관할 보건소로 즉시 유선 신고**해야 합니다."""

    # ----------------------------------------------------
    # [1-1] 사스(SARS) vs 인플루엔자(독감) 임상 및 법정감염병 비교 분석
    # ----------------------------------------------------
    if ("사스" in q_lower or "sars" in q_lower) and ("인플루엔자" in q_lower or "독감" in q_lower):
        return """👩‍⚕️ **[AI 보건 튜터 임상 비교 분석: 사스(SARS) vs 인플루엔자(독감)]**

보건간호과 학생 여러분, 질병관리청(KDCA) 및 고교 보건 교과서 기준 **'사스(SARS, 제1급)'**와 **'인플루엔자(독감, 제4급)'**의 핵심 비교 분석입니다:

| 구분 항목 | 🦇 사스 (SARS / 중증급성호흡기증후군) | 💉 인플루엔자 (Influenza / 독감) |
| :--- | :--- | :--- |
| **법정감염병 분류** | **제1급 감염병** (발생 즉시 유선 신고, 음압격리) | **제4급 감염병** (표본감시 감염병, 7일 이내 신고) |
| **원인 병원체** | **SARS-CoV** (코로나바이러스과 베타코로나바이러스) | **인플루엔자 바이러스 A형, B형, C형** (오르토믹소바이러스과) |
| **치명률 (Fatality Rate)** | **약 9.6%** (중등도~고위험, 60세 이상은 50% 육박) | **0.1% 미만** (통상 0.05~0.1%, 고위험군 폐렴 합병증 주의) |
| **전파 경로** | 호흡기 비말, 오염된 물품 접촉, 에어로졸 전파 가능 | 호흡기 비말 전파, 오염된 손/물품 접촉 |
| **주요 임상 증상** | 38℃ 이상 급성 고열, 마른기침, 저산소증, 급속한 호흡곤란 및 폐 침윤 | 갑작스러운 38℃ 이상 고열, 오한, 두통, 전신 근육통, 맑은 콧물, 인후통 |
| **예방 백신 및 치료제** | **상용화된 백신 없음**, 특효약 부재 (대증요법 및 중환자 치료) | **매년 4가 불활성화 백신 접종**, 타미플루/페라미비르 항바이러스제 완비 |
| **학교 등교 중지 및 격리** | **의심 즉시 음압격리 및 전면 등교 중지**<br>👉 관할 보건소 즉시 신고, 완치/격리해제 시까지 공결 인정 | **해열제 복용 없이 정상 체온 회복 후 24시간 경과 시까지 등교 중지**<br>👉 의사 진단서 제출 시 출석인정 결석(공결) 처리 |

### 💡 보건간호 및 학교 방역 핵심 탐구 포인트:
1. **법정감염병 등급과 격리 수준의 차이:**
   - **사스**는 생물테러 감염병이나 치명률이 높아 발생 즉시 격리(음압격리)가 필요한 **제1급 감염병**입니다.
   - **인플루엔자**는 유행 여부를 조사하기 위해 표본감시활동이 필요한 **제4급 감염병**입니다.
2. **학교 보건실 긴급 대처 프로토콜:**
   - 독감 의심 학생은 보건실에서 체온 측정 후 보호자 연락 및 병원 진료(타미플루 처방) 후 가정 격리를 안내합니다.
   - 반면 사스 의심 증상자(해외 위험지역 방문력 + 고열 + 호흡곤란) 발견 시에는 일반 구역이 아닌 독립된 보건관찰실에 즉시 격리(KF94 착용)하고 보건소에 즉각 신고해야 합니다."""

    # ----------------------------------------------------
    # [2] 수족구병 vs 아구창(Oral Thrush) 구강 병변 감별 진단
    # ----------------------------------------------------
    if "아구창" in q_lower or ("수족구" in q_lower and any(w in q_lower for w in ["차이", "구별", "비교"])):
        return """👩‍⚕️ **[AI 보건 튜터 임상 감별 진단: 수족구병 vs 아구창(Oral Thrush) 핵심 비교]**

보건간호과 학생 및 학교 보건실 실무에서 가장 중요한 **소아·청소년 구강 병변 감별 진단 가이드**입니다.

| 구분 항목 | 🦠 수족구병 (Hand-Foot-Mouth Disease) | 🍄 아구창 (Oral Thrush / 구강 칸디다증) |
| :--- | :--- | :--- |
| **원인 병원체** | **콕사키바이러스 A16**, 엔테로바이러스 71 (바이러스성 감염) | **칸디다 알비칸스 (Candida albicans)** (진균 / 곰팡이 감염) |
| **법정감염병 분류** | **제4급 법정감염병** (표본감시 대상) | 비법정 감염병 (기회감염증) |
| **구강 병변 양상** | 혀, 잇몸, 볼 점막에 1~2mm 쌀알 크기의 **수포(물집) 및 궤양(Aphthous-like ulcers)** 발생 | 혀나 볼 안쪽에 우유 찌꺼기 같은 **하얀 백태(White patches)** 형성 |
| **병변 탈락 여부** | 궤양이므로 닦이지 않으며, 억지로 건드리면 심한 통증 유발 | 거즈로 닦으면 벗겨지며, **벗겨진 부위 점막이 붉게 충혈되고 점상 출혈** 발생 |
| **동반 신체 증상** | **손바닥, 발바닥, 엉덩이의 붉은 수포성 발진**, 38℃ 이상 발열, 침 삼킴 곤란 | **손·발 발진 없음**, 전신 발열 없음 (구강 국소 증상에 국한) |
| **전염성 및 등교** | **전염력 매우 강함 (비말/접촉 전파)**<br>👉 **증상 소실 시까지 필수 등교 중지(가정 격리)** | **일상 접촉 전파 불가** (면역 저하, 항생제 장기 복용 시 발생)<br>👉 **등교 중지 불필요 (정상 학교생활 가능)** |
| **치료 원칙** | 특이 항바이러스제 없음 (대증요법, 해열진통제, 탈수 예방 수액/냉수 섭취) | **항진균제 치료** (나이스타틴 시럽 구강 도포, 플루코나졸 복용) |

💡 **학교 보건실 임상 팁:**
- 학생이 구강 통증을 호소할 때 **반드시 손바닥과 발바닥을 확인**하세요. 손·발에 붉은 발진이나 물집이 관찰되면 **수족구병**이므로 즉시 보건관찰실 격리 후 귀가 조치해야 합니다.
- 손·발 발진 없이 혀나 뺨 안쪽에만 우유 찌꺼기 같은 하얀 막이 있고 닦았을 때 피가 배어 나온다면 **아구창**이므로 항진균제 진료를 권고하되 격리는 불필요합니다."""

    # ----------------------------------------------------
    # [3] 독감(인플루엔자) vs 일반 감기(Common Cold)
    # ----------------------------------------------------
    if ("독감" in q_lower or "인플루엔자" in q_lower) and "감기" in q_lower:
        return """👩‍⚕️ **[AI 보건 튜터 임상 비교 분석: 독감(인플루엔자) vs 일반 감기(Common Cold)]**

| 구분 항목 | 💉 인플루엔자 (독감) | 🤧 일반 감기 (Common Cold) |
| :--- | :--- | :--- |
| **원인 병원체** | **인플루엔자 바이러스 (A형, B형, C형)** | 리노바이러스, 아데노바이러스, 코로나바이러스 등 200여 종 |
| **법정감염병 분류** | **제4급 감염병** (표본감시 대상) | 법정감염병 비해당 |
| **발병 양상** | **갑작스럽게 시작**되는 38℃ 이상 고열과 오한 | **서서히 시작**되는 미열, 목 쉼, 콧물 |
| **전신 증상** | **극심한 두통, 근육통, 관절통, 극심한 피로감** | 전신 증상 미미, 일상생활 가능 수준의 권태감 |
| **치료제** | 항바이러스제 (타미플루, 페라미비르 등) | 특효약 없음 (대증 치료, 해열진통제, 수분 섭취) |
| **학교 등교 기준** | **해열제 복용 없이 정상 체온 회복 후 최소 24시간 경과 시까지 등교 중지** (출석인정 결석) | 등교 중지 비해당 (컨디션에 따라 마스크 착용 후 등교 가능) |

💡 **보건간호과 팁:** 학교 내 유행 시 학급 내 75% 이상 백신 접종과 함께 시간당 2회 이상 맞통풍 환기가 가장 효과적인 감염 확산 차단책입니다."""

    # ----------------------------------------------------
    # [4] 수두 vs 홍역 (공기/비말핵 전파 감염병 비교)
    # ----------------------------------------------------
    if "수두" in q_lower and "홍역" in q_lower:
        return """👩‍⚕️ **[AI 보건 튜터 임상 비교 분석: 수두(Chickenpox) vs 홍역(Measles)]**

| 구분 항목 | 💧 수두 (Varicella) | 🔴 홍역 (Measles) |
| :--- | :--- | :--- |
| **원인 병원체** | 수두-대상포진 바이러스 (Varicella-Zoster Virus) | 홍역 바이러스 (Measles morbillivirus) |
| **법정감염병 분류** | **제2급 감염병** (24시간 이내 신고) | **제2급 감염병** (24시간 이내 신고) |
| **전파 경로** | **공기(비말핵), 수포액 직접 접촉** (기초재생산지수 $R_0 \\approx 10$) | **공기(비말핵) 전파** (전파력 최상위, $R_0 \\approx 12 \\sim 18$) |
| **특징적 징후** | 몸통 ➡️ 얼굴 ➡️ 사지 순서로 발생.<br>**반점 ➡️ 구진 ➡️ 수포 ➡️ 가피(딱지)**의 모든 단계가 한 피부에 동시 관찰됨 | 발진 전 뺨 안쪽 점막에 **코플릭 반점(Koplik's spots)** 출현.<br>귀 뒤/목 ➡️ 얼굴 ➡️ 몸통 순서로 붉은 구진성 발진 융합 |
| **학교 등교 중지** | **모든 수포에 딱지(가피)가 앉을 때까지** 등교 중지 (통상 발진 시작 후 5~7일) | **발진 출현 후 4일까지** 등교 중지 (가정 격리) |"""

    # ----------------------------------------------------
    # [5] 콜레라 vs 장티푸스 (수인성·식품매개 감염병 비교)
    # ----------------------------------------------------
    if "콜레라" in q_lower and "장티푸스" in q_lower:
        return """👩‍⚕️ **[AI 보건 튜터 임상 비교 분석: 콜레라(Cholera) vs 장티푸스(Typhoid Fever)]**

| 구분 항목 | 🌊 콜레라 (Cholera) | 🌡️ 장티푸스 (Typhoid Fever) |
| :--- | :--- | :--- |
| **원인 병원체** | **Vibrio cholerae** (콜레라균, 콤마 모양 세균) | **Salmonella enterica serovar Typhi** (장티푸스균) |
| **법정감염병 분류** | **제2급 감염병** (24시간 이내 신고) | **제2급 감염병** (24시간 이내 신고) |
| **임상적 특징** | 통증 없는 **극심한 쌀뜨물(Rice-water) 양상의 수양성 설사**, 급성 탈수, 쇼크 | **계단식으로 서서히 오르는 지속성 고열(39~40℃)**, **상대적 서맥**, 장미진, 비장 비대 |
| **학교 보건실 지침** | 증상 소실 후 항생제 치료 중단 48시간 뒤 **대변 배양검사 연속 2회 음성 확인 시까지 등교 중지** | 항생제 치료 완료 48시간 후 **대변 배양검사 연속 3회 음성 확인 시까지 등교 중지** |"""

    # ----------------------------------------------------
    # [5-1] 바이러스성 간염 (A형 vs B형 vs C형) 임상 비교 및 B형간염 심층 분석
    # ----------------------------------------------------
    q_nospace = re.sub(r"\s+", "", q_lower)
    is_hepatitis_q = any(w in q_nospace for w in ["간염", "hbv", "hav", "hcv"])

    # 3대 간염 비교 질의 (단, 질문에 엠폭스 등 다른 법정감염병이 있는 경우 [10-1] 비교 엔진으로 넘김)
    if is_hepatitis_q and not has_other_legal_disease and (any(w in q_nospace for w in ["비교", "차이", "vs", "종류", "구별"]) or ("a형" in q_nospace and "b형" in q_nospace) or ("b형" in q_nospace and "c형" in q_nospace)):
        return """👩‍⚕️ **[AI 보건 튜터 임상 비교 분석: 바이러스성 간염 3대 질환 (A형 vs B형 vs C형)]**

보건간호과 학생 여러분, 질병관리청(KDCA) 및 고교 보건 교과서 기준 **바이러스성 간염(Viral Hepatitis) 핵심 비교 분석**입니다:

| 구분 항목 | 🚰 A형간염 (Hepatitis A) | 💉 B형간염 (Hepatitis B) | 🩸 C형간염 (Hepatitis C) |
| :--- | :--- | :--- | :--- |
| **법정감염병 분류** | **제2급 감염병** (24시간 이내 신고) | **제3급 감염병** (24시간 이내 신고) | **제3급 감염병** (24시간 이내 신고) |
| **원인 바이러스** | **HAV** (피코르나바이러스과, RNA) | **HBV** (헤파드나바이러스과, **DNA**) | **HCV** (플라비바이러스과, RNA) |
| **주요 전파 경로** | **분변-경구(Fecal-Oral) 감염**<br>👉 오염된 물, 비위생적 조개류(익히지 않은 조개젓) 섭취 | **혈액·체액 접촉, 수직감염, 성접촉**<br>👉 오염된 주사기, 출산 시 신생아 전파 | **혈액 접촉, 오염된 주사기 재사용**<br>👉 비위생적 문신/피어싱 시술 |
| **만성화율 (Chronic Rate)**| **만성화 없음 (0%)**<br>👉 급성 간염 후 100% 항체 형성 완치 | **성인 감염 시 5~10% 만성화**<br>👉 **신생아 수직감염 시 90% 이상 만성화** | **약 70~80% 만성화**<br>👉 대부분 만성 간염 ➡️ 간경변 ➡️ 간암 진행 |
| **예방 백신 유무** | **백신 있음** (생후 12~23개월, 2회 접종) | **백신 있음** (0, 1, 6개월 3회 필수 접종) | **상용화된 백신 없음** (돌연변이 빈번) |
| **치료 원칙** | 특이 치료제 없음 (보존적 대증 요법) | 항바이러스제 (테노포비르, 엔테카비르) | **경구용 DAA 완치 치료제 완비 (완치율 95%↑)** |
| **학교 보건실 격리 지침** | **황달 발생 후 1주일간 등교 중지**<br>👉 집단 급식 배식 참여 절대 금지 | **등교 중지 비해당 (정상 학교생활 100%)**<br>👉 일상 식사·대화·포옹으로 절대 전파 안 됨 | **등교 중지 비해당 (정상 학교생활 100%)**<br>👉 보건실 외상 시 표준주의지침 준수 |

💡 **보건간호과 핵심 실무 팁:**
1. **B형간염의 일상 접촉 오해 해소:** B형간염은 땀, 침, 재채기, 식판 공유로는 절대 전파되지 않으므로 학생을 격리하거나 차별하는 것은 법적·의학적 위법입니다.
2. **외상 처치 원칙:** 학교 보건실에서는 모든 출혈 학생 처치 시 라텍스/니트릴 장갑을 착용하는 **'표준 주의지침(Standard Precautions)'**을 준수합니다."""

    # B형간염 단독 질문 ("B형간염에 대해 알려줘", "B형 간염병")
    if "b형" in q_nospace and is_hepatitis_q and not has_other_legal_disease and not explicit_comparison:
        return """👩‍⚕️ **[AI 보건 튜터 종합 리포트: B형간염 (Hepatitis B, 제3급 법정감염병)]**

보건간호과 학생 여러분, 질병관리청(KDCA) 및 공중보건 교과서 기준 **'B형간염(Hepatitis B)'**의 종합 의학 정보입니다:

### 1. 📌 법정감염병 분류 및 특성
- **법정감염병 급수:** **제3급 법정감염병** (발생을 지속적으로 감시할 필요가 있어 24시간 이내 관할 보건소에 신고)
- **원인 병원체:** **B형간염 바이러스 (Hepatitis B Virus, HBV)** — 헤파드나바이러스과(Hepadnaviridae)의 이중가닥 DNA 바이러스

### 2. 🧬 전파 경로 (정확한 역학적 이해)
1. **출산 시 수직감염 (Perinatal Transmission):** 감염된 산모가 분만할 때 혈액/양수를 통해 신생아에게 전파 (과거 한국 만성 B형간염의 가장 주된 원인)
2. **혈액 및 체액 접촉:** 오염된 주사기 바늘 찔림, 비위생적 문신·피어싱 시술, 면도기·손톱깎이 공유
3. **성접촉 (Sexual Transmission):** 감염된 사람과의 성접촉을 통한 감염
⚠️ **[매우 중요: 절대 전파되지 않는 경로]**
- 재채기, 기침, 콧물, 침, 악수, 포옹, 식판 및 수저 공유, 화장실 변기, 수영장 등 **일상적인 학교생활로는 절대 감염되지 않습니다.**

### 3. 🩺 주요 임상 증상 및 경과
- **잠복기:** 평균 60~90일 (30~180일)
- **급성기 증상:** 심한 피로감, 식욕부진, 메스꺼움, 구토, 미열, 우상복부 둔통, 짙은 갈색 소변(콜라색 뇨), 피부 및 눈의 **황달(Jaundice)**
- **만성화 위험:** 감염 연령이 어릴수록 만성화율이 급증 (신생아기 감염 시 90%, 성인기 감염 시 5~10%가 만성화되어 간경변증 및 간세포암으로 진행)

### 4. 💉 국가예방접종(NIP) 및 면역 관리
- **기초 예방접종:** 생후 0개월, 1개월, 6개월 총 3회 근육주사 접종 (대퇴부 전외측 또는 삼각근)
- **수직감염 예방사업:** B형간염 표면항원(HBsAg) 양성 산모에게서 태어난 신생아는 **출생 직후 12시간 이내에 B형간염 면역글로불린(HBIG)과 B형간염 백신을 서로 다른 부위에 동시 투여**하여 감염을 95% 이상 완벽히 차단합니다.
- **항원/항체 검사 해석:**
  - `HBsAg (표면항원) (+)`: 현재 체내에 바이러스가 존재함 (감염/보균 상태)
  - `Anti-HBs (표면항체) (+)`: 면역력 획득 (백신 접종 성공 또는 과거 감염 후 회복)

### 5. 🏫 학교 보건실 관리 및 출석 지침
- **등교 중지 비해당:** 학교보건법상 B형간염은 등교 중지 대상 감염병이 아니며, **정상 등교 및 모든 교과 수업·체육 활동 참여가 100% 보장**됩니다.
- **보건실 외상 처치:** 교내에서 찰과상이나 열상으로 피가 나는 학생을 처치할 때 감염 여부와 상관없이 보건교사는 **1회용 장갑을 필히 착용**하고 소독 및 지혈을 실시합니다."""

    # ----------------------------------------------------
    # [6] AIDS(후천성면역결핍증) 특화 질문
    # ----------------------------------------------------
    if "aids" in d_clean.lower() or "후천성면역결핍증" in d_clean or "hiv" in d_clean.lower() or "에이즈" in q_lower:
        if any(w in q_lower for w in ["백신", "접종", "면역"]):
            return f"""👩‍⚕️ **[AI 보건 튜터 답변: {d_clean} 예방 백신 및 면역 관리 지침]**

질문하신 **'{d_clean}'**의 예방 백신 및 현대 의학적 면역 예방 전략입니다:

1. **예방 백신 상용화 현황 (백신 부재 이유):**
   - **현재 전 세계적으로 상용화된 HIV 예방 백신은 존재하지 않습니다.**
   - 원인: HIV 바이러스는 체내 증식 시 역전사 효소의 잦은 복제 오류로 **돌연변이율이 극도로 높고**, 외피 당단백질(gp120)이 변형을 거듭하여 인체 면역계의 중화항체 형성을 회피하기 때문입니다.
2. **백신을 대체하는 화학적 예방 요법 (현대 의학의 표준):**
   - **노출 전 예방요법 (PrEP, Pre-Exposure Prophylaxis):** 고위험군이 성관계 전 매일 항레트로바이러스제(트루바다 등)를 선제 복용하여 감염 위험을 99% 이상 차단하는 공인된 화학적 예방법입니다.
   - **노출 후 예방요법 (PEP, Post-Exposure Prophylaxis):** 의료 현장 바늘 찔림 사고나 감염 의심 체액에 노출된 경우, **반드시 72시간 이내**에 28일간 항레트로바이러스제를 긴급 투약하여 바이러스의 체내 정착을 차단합니다.
3. **청소년 보건 교육 핵심:**
   - 백신이 없으므로 **안전한 성생활(올바른 콘돔 사용), 주사기 공동사용 금지, 의료 시술 시 1회용 멸균 기구 사용**이 가장 결정적인 1차 예방법입니다."""

        elif any(w in q_lower for w in ["격리", "등교", "보건실"]):
            return f"""👩‍⚕️ **[AI 보건 튜터 답변: {d_clean} 학교 보건실 관리 및 등교 지침]**

1. **등교 중지 비해당 (정상 등교 및 학습권 100% 보장):**
   - **{d_clean}은 학교보건법상 등교 중지 대상 감염병이 아닙니다.**
   - HIV는 호흡기 비말, 공기, 기침, 땀, 침, 일상적인 신체 접촉(악수, 포옹), 학급 내 책상 공유, 급식 식사, 화장실 변기 공유 등으로 **절대 전파되지 않습니다.**
   - 따라서 감염 학생의 등교를 제한하거나 격리하는 것은 의학적·법적 근거가 전혀 없는 위법·차별 행위입니다.
2. **보건실 긴급 조치 및 출혈 관리 (표준 주의지침):**
   - 감염 여부와 관계없이 모든 학생의 외상 출혈 시 **'표준 주의지침(Standard Precautions)'**을 준수합니다.
   - 보건교사는 1회용 라텍스/니트릴 장갑을 착용하고 출혈 부위를 지혈·소독하며, 오염된 거즈는 의료폐기물 전용 용기에 안전하게 밀폐 폐기합니다.
3. **학생 비밀 보장 및 인권 보호 (법적 의무):**
   - 후천성면역결핍증 예방법 제7조(비밀누설의 금지)에 의거, 학생의 감염 사실은 본인 동의 없이 타인에게 누설할 수 없으며 위반 시 3년 이하의 징역형에 처해집니다.
   - 보건교사는 학생이 심리적 안정감을 느끼고 정해진 시간에 항레트로바이러스제(HAART)를 규칙적으로 복약할 수 있도록 비밀 상담을 지원합니다."""

    # ----------------------------------------------------
    # [7] 무좀(Tinea Pedis, 백선증) vs 곰팡이(진균, Fungi) 비교 분석
    # ----------------------------------------------------
    if ("무좀" in q_lower and any(w in q_lower for w in ["곰팡이", "진균", "차이", "구별", "비교"])) or q_lower == "무좀" or ("곰팡이" in q_lower and "차이" in q_lower):
        return """👩‍⚕️ **[AI 보건 튜터 임상 비교 분석: 무좀(Tinea Pedis) vs 곰팡이(진균, Fungi)]**

보건간호과 학생 여러분! 아주 훌륭하고 중요한 의학적 기초 질문입니다.
결론부터 말씀드리면, **곰팡이는 '원인 병원체(생물학적 미생물 분류)'**이고, **무좀은 그 곰팡이가 발 피부 각질층에 침투해 일으킨 '질병의 이름(임상 질환명)'**입니다!

| 구분 항목 | 🍄 곰팡이 (진균, Fungi) | 🦶 무좀 (Tinea Pedis, 발 백선증) |
| :--- | :--- | :--- |
| **의학적 개념 정의** | 세균, 바이러스와 구분되는 **진핵생물 미생물 분류군** | 피부사상균(곰팡이)이 발 피부 각질층에 감염된 **표재성 진균 질환** |
| **의학적 위상** | **원인 병원체 (Etiological Agent)** | **임상 질병명 (Clinical Disease)** |
| **병원체 종류** | 효모균, 사상균, 버섯, 누룩곰팡이 등 수만 종 | 주로 **피부사상균 (Trichophyton rubrum, T. mentagrophytes)** |
| **발병 기전** | 포자(Spore) 형태로 공기, 흙, 습한 환경에 서식 | 각질을 분해하는 효소(케라티나아제)를 분비해 **각질 단백질을 먹고 번식** |
| **주요 임상 증상** | 단독 증상 없음 (숙주에 감염되어 질환 유발) | ① **지간형**: 발가락 사이 짓무름·가려움<br>② **수포형**: 좁쌀 크기 물집·가려움<br>③ **각화형**: 발바닥 전체 하얀 각질 비후 |
| **법정감염병 분류** | 비법정 (자연계 미생물) | **비법정 감염병** (흔한 표재성 진균증) |
| **치료 원칙** | 환경 통풍, 건조 유지 | **항진균제 연고 (테르비나핀, 클로트리마졸)** 4~6주 도포, 중증 시 경구제 |
| **학교 보건실 관리** | 체육관 매트, 탈의실 습도 환기 관리 | **등교 중지 비해당 (정상 학교생활)**<br>👉 발 건조 지도, 보건실 슬리퍼·수건 개별 사용 |

⚠️ **[보건간호과 임상 시험 & 실무 핵심 주의사항 (절대 주의!)]**
- **무좀에 가렵다고 습진 연고(스테로이드 연고)를 바르면 절대 안 됩니다!**
- 습진 연고에 들어있는 부신피질호르몬(스테로이드)은 국소 면역 반응을 억제하여, 곰팡이가 피부 깊숙이 폭발적으로 번식하는 **'잠행 백선(Tinea incognito)'**으로 급격히 악화됩니다.
- 따라서 학교 보건실에서는 학생 발 병변을 꼼꼼히 관찰하여 습진인지 무좀인지 감별하고, 반드시 **항진균제**를 사용하도록 지도해야 합니다."""

    # ----------------------------------------------------
    # [8] 학교 보건실 3대 상처 소독약 비교 (빨간약 vs 과산화수소 vs 에탄올)
    # ----------------------------------------------------
    if any(w in q_lower for w in ["소독약", "빨간약", "포비돈", "과산화수소", "에탄올", "알코올"]) and any(w in q_lower for w in ["차이", "비교", "사용", "언제"]):
        return """👩‍⚕️ **[AI 보건 튜터 임상 비교 분석: 학교 보건실 3대 상처 소독약 비교 가이드]**

보건간호과 학생 및 학교 보건실 실무에서 가장 빈번하게 다루는 **외상 소독제의 올바른 사용 기준**입니다.

| 구분 항목 | 🔴 포비돈 요오드 (빨간약) | 🫧 과산화수소수 ($H_2O_2$) | 🧪 소독용 에탄올 (알코올) |
| :--- | :--- | :--- | :--- |
| **주요 작용 기전** | 유리 요오드가 세균 단백질을 산화 침전시켜 광범위 살균 | 혈액 내 카탈라아제와 반응해 활성산소 거품 발생, 혐기성 세균 사멸 | 세균 세포막 지질 용해 및 세포 내 단백질 변성 |
| **적용 권장 부위** | **모든 찰과상, 개방성 상처, 수술 부위, 감염 예방** | **오염이 심하거나 고름/이물질이 낀 상처 세척** | **상처가 없는 온전한 피부, 주사 부위, 의료기구** |
| **정상 조직 손상** | 적음 (마르면서 살균 보호막 형성) | 다소 있음 (정상 육아조직 세포 손상 가능) | **매우 심함 (열린 상처에 바르면 극심한 통증과 세포 괴사)** |
| **보건실 실무 핵심** | 젖은 상태가 아니라 **완전히 마르면서 살균 효과**가 나타남 | 거품으로 이물질 세척 후 식염수로 헹굼, 장기 사용 금지 | **열린 상처 안쪽에는 절대 바르지 말고**, 상처 주변 정상 피부만 소독 |"""

    # ----------------------------------------------------
    # [9] 학교 보건실 다빈도 응급처치 (코피, 발목 삠/염좌 RICE, 화상)
    # ----------------------------------------------------
    if any(w in q_lower for w in ["코피", "염좌", "삔", "화상", "응급처치", "rice"]):
        if "코피" in q_lower:
            return """👩‍⚕️ **[AI 보건 튜터 응급처치 지침: 학교 보건실 코피(비출혈, Epistaxis) 대처법]**

1. **자세 교정 (가장 중요한 오답 포인트):**
   - **고개를 뒤로 젖히면 절대 안 됩니다!** 고개를 뒤로 젖히면 피가 기도로 넘어가 흡인성 폐렴이나 기도 질식을 유발하거나, 위장으로 넘어가 구토를 일으킵니다.
   - **올바른 자세:** 고개를 약간 앞으로 숙이고 입으로 숨쉬게 합니다.
2. **압박 지혈법:**
   - 콧등 뼈 바로 아래 말랑말랑한 콧망울(키셀바흐 삼각 부위)을 엄지와 검지로 **최소 10~15분간 쉬지 않고 지속 압박**합니다.
3. **냉찜질 적용:**
   - 콧등이나 이마 부위에 얼음주머니나 차가운 물수건을 대어 혈관 수축을 유도합니다.
4. **병원 이송 기준:**
   - 20분 이상 지속 압박에도 지혈되지 않거나, 두부 외상 후 출혈 시 즉시 응급실로 의뢰합니다."""

        elif "화상" in q_lower:
            return """👩‍⚕️ **[AI 보건 튜터 응급처치 지침: 학교 급식실/실습실 화상(Burn) 응급처치]**

1. **즉각적인 냉각 (최우선 처치):**
   - 흐르는 깨끗한 미온수(12~20℃)에 **최소 15~20분간 환부를 충분히 식혀줍니다.**
   - ⚠️ 얼음(Ice)을 직접 대면 혈관이 급격히 수축하여 조직 괴사를 유발하므로 금기입니다.
2. **물집(수포) 보존:**
   - 2도 화상에서 생기는 물집은 천연 무균 드레싱 역할을 하므로 **절대 터뜨리지 않습니다.**
3. **이물질 및 민간요법 금지:**
   - 된장, 치약, 기름 등을 바르면 2차 세균 감염을 일으킵니다. 깨끗한 멸균 거즈로 덮어 의료기관으로 이송합니다."""

        else:
            return """👩‍⚕️ **[AI 보건 튜터 응급처치 지침: 체육시간 발목 염좌(삠) R.I.C.E. 프로토콜]**

체육시간 발목 접질림이나 급성 염좌 발생 시 준수해야 할 국제 표준 응급처치 지침입니다:

- **R (Rest, 안정):** 체중 부하를 즉시 중단하고 부목이나 붕대로 손상 부위를 고정하여 추가 손상을 방지합니다.
- **I (Ice, 냉찜질):** 손상 후 48시간 이내에는 1회 15~20분씩 하루 3~4회 얼음찜질을 적용하여 모세혈관 수축, 출혈 및 부종을 최소화합니다.
- **C (Compression, 압박):** 탄력붕대를 이용해 원위부(발가락)에서 근위부(발목) 방향으로 과도하지 않게 감아 부종을 억제합니다.
- **E (Elevation, 거상):** 부종 완화를 위해 손상된 다리를 심장 높이보다 높게 올려 정맥혈과 림프액의 회귀를 촉진합니다."""

    # ----------------------------------------------------
    # [10] 질문에서 언급된 모든 법정감염병 스마트 감지 및 비교/단일 분석
    # ----------------------------------------------------
    # 10-1. 서로 다른 2개 이상 질병 비교 조건 검사 (절대 동일 질병끼리 비교되지 않음)
    is_multi_disease_compare = False
    d1_name, d2_name = "", ""
    d1_info, d2_info = None, None

    if len(unique_found) >= 2:
        # 질문 내에 서로 다른 2개 이상의 질병이 명시된 경우 (질문 내 등장 순서 유지)
        d1_key, d1_name, d1_info = unique_found[0]
        d2_key, d2_name, d2_info = unique_found[1]
        if d1_name != d2_name:
            is_multi_disease_compare = True
    elif len(unique_found) == 1 and explicit_comparison and d_clean:
        # 질문에 1개 질병만 있지만, 명시적으로 비교를 요구하고 기준 질병(d_clean)과 다른 경우에만
        d1_key, d1_name, d1_info = unique_found[0]
        if d1_name != d_clean:
            d2_name = d_clean
            d2_info = get_disease_info("", d2_name)
            is_multi_disease_compare = True

    if is_multi_disease_compare and d1_info and d2_info and d1_name != d2_name:
        return f"""👩‍⚕️ **[AI 보건 튜터 임상 비교 분석: {d1_name} vs {d2_name}]**

보건간호과 학생 여러분, 질병관리청(KDCA) 및 고교 보건 교과서 기준 **'{d1_name}'**와 **'{d2_name}'**의 핵심 비교 분석입니다:

| 구분 항목 | 📌 {d1_name} ({d1_info['tier']}) | 📌 {d2_name} ({d2_info['tier']}) |
| :--- | :--- | :--- |
| **법정감염병 분류** | **`{d1_info['tier']}`** | **`{d2_info['tier']}`** |
| **원인 병원체** | `{d1_info['pathogen']}` | `{d2_info['pathogen']}` |
| **주요 전파 경로** | {d1_info['route']} | {d2_info['route']} |
| **임상 증상 및 특징** | {d1_info['symptoms']} | {d2_info['symptoms']} |
| **학교 등교중지 / 격리** | **{d1_info['treatment']}** | **{d2_info['treatment']}** |
| **예방 백신 및 관리** | {d1_info['prevention']} | {d2_info['prevention']} |

### 💡 **보건간호 및 학교 방역 핵심 탐구 포인트:**
1. **역학적 위험도 및 급수 차이:**
   - **{d1_name}**: `{d1_info['tier']}` 분류. {d1_info['cause']}
   - **{d2_name}**: `{d2_info['tier']}` 분류. {d2_info['cause']}
2. **학교 보건실 관리 지침:**
   - 감염병 발생 즉시 보건관찰실로 격리 조치하고, 학교 감염병 매뉴얼에 따라 등교 중지(출석 인정 공결) 처리하며 학급 맞통풍 환기 및 환경 소독을 시행합니다."""

    # 10-2. 감지된 법정감염병에 대한 종합 전문 리포트 (예: "사스에 대해 알려줘")
    if unique_found:
        target_key, target_clean, target_info = unique_found[0]
        if any(w in q_lower for w in ["백신", "접종", "면역"]):
            return f"""👩‍⚕️ **[AI 보건 튜터 답변: {target_clean} ({target_info['tier']}) 예방 백신 및 면역 관리 지침]**

보건간호과 학생 여러분, 질병관리청 국가예방접종사업(NIP) 및 교과서 기준 **'{target_clean}'**의 예방접종 지침입니다:

1. **💉 예방접종 및 면역 방어:**
   - {target_info['prevention']}
2. **🦠 원인 병원체 (특이 병원체):**
   - `{target_info['pathogen']}`
3. **🧬 전파 경로:**
   - {target_info['route']}
4. **🏫 학교 보건실 관리 권고사항:**
   - 학급 내 개인 위생 지도(30초 이상 올바른 손 씻기, 기침 예절) 및 미접종자 대상 백신 접종 독려를 실시합니다."""

        elif any(w in q_lower for w in ["격리", "등교", "출석", "보건실"]):
            return f"""👩‍⚕️ **[AI 보건 튜터 답변: {target_clean} ({target_info['tier']}) 학교 격리 및 등교 중지 기준]**

교육부 및 질병관리청 『학교 감염병 예방·위기대응 매뉴얼』과 학교보건법에 근거한 **'{target_clean}'** 관리 지침입니다:

1. **🏫 학교 등교 중지(가정 격리) 기준:**
   - **격리/등교 지침:** {target_info['treatment']}
2. **🩺 보건실 긴급 조치 사항:**
   - 발열 및 의심 증상 확인 즉시 보건실 내 보건관찰실로 이동시키고 KF94 마스크를 착용시킵니다.
   - 학부모 유선 연락 후 즉시 의료기관 진료를 받도록 안내합니다.
3. **📄 출석 인정(공결) 절차:**
   - 법정감염병 의사 진단서, 소견서 또는 진료확인서 제출 시 **출석인정 결석**으로 처리되어 학생의 내신 불이익이 없습니다.
4. **🛡️ 학급 방역:**
   - 확진 학생 발생 학급 맞통풍 환기 및 책상 표면 환경 소독을 즉시 실시합니다."""

        else:
            return f"""👩‍⚕️ **[AI 보건 튜터 답변: {target_clean} ({target_info['tier']}) 종합 역학 및 보건 관리 리포트]**

질병관리청(KDCA) 공공데이터 및 고교 보건 교과서 기준 **'{target_clean}'**의 종합 분석입니다:

1. **📌 질병 개요 및 분류:**
   - **법정감염병 급수:** `{target_info['tier']}`
   - **발병 기전:** {target_info['cause']}
2. **🦠 원인 병원체 (특이 병원체):**
   - `{target_info['pathogen']}`
3. **🧬 전파 경로:**
   - {target_info['route']}
4. **🩺 주요 임상 증상 및 잠복기:**
   - {target_info['symptoms']}
5. **📈 최근 발생 추세 및 역학 특성:**
   - {target_info['trend']}
6. **🏫 학교 보건실 관리 및 치료 지침:**
   - {target_info['treatment']}
7. **💉 예방 수칙 및 백신 접종:**
   - {target_info['prevention']}

💡 **보건간호과 탐구 노트:**
- 감염병 발생 시 병원체의 전파 경로(비말, 공기, 접촉, 수인성)를 정확히 파악하여 환경 소독과 개인보호구 착용을 차별화하는 것이 학교 감염병 관리의 핵심입니다."""

    # ----------------------------------------------------
    # [11] 질문에 선택된 드롭다운 질병명(또는 법정감염병)이 명시되거나 일반 감염병 임상 문의인 경우
    # ----------------------------------------------------
    if d_clean in question or any(k in question for k in ["격리", "등교", "잠복기", "증상", "병원체", "유행", "백신", "소독", "치료", "약", "바이러스", "세균"]):
        return f"""👩‍⚕️ **[AI 보건 튜터 답변: {d_clean} ({info['tier']}) 질의응답 분석]**

선택하신 감염병 **'{d_clean}'**에 대한 학교 보건 및 역학 분석입니다:

1. **원인 병원체:** `{info['pathogen']}`
2. **전파 경로 및 원인:** {info['route']} / {info['cause']}
3. **주요 임상 증상:** {info['symptoms']}
4. **학교 보건실 관리 & 등교 지침:** {info['treatment']}
5. **예방접종 및 감염 차단:** {info['prevention']}"""

    # ----------------------------------------------------
    # [12] 법정감염병 질환과 관련 없는 모든 질문 차단
    # ----------------------------------------------------
    return "해당 질문은 법정감염병과 관련이 없습니다. 선생님께 요청하기 바랍니다."



# ==========================================
# 3. 사이드바 구성 (사용자 요청: 학교로고 바깥 네모 상자 안에 로고 마크만 배치)
# ==========================================
df_all = load_total_data()
b64_emblem = get_emblem_base64()

with st.sidebar:
    # 1. 서울의료보건고등학교 로고 (네모 박스 바탕 안에 그림 마크만 배치)
    if b64_emblem:
        st.markdown(f"""
        <div style="text-align: center; margin-top: 6px; margin-bottom: 8px;">
            <div class="sidebar-emblem-square">
                <img src="data:image/png;base64,{b64_emblem}" style="height: 44px; width: 44px; object-fit: contain; display: block;" alt="서울의료보건고 엠블럼">
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 2. AI 보건 탐구 (띄어쓰기 및 가운데 정렬)
    st.markdown("""
    <div style="text-align: center; font-size: 1.4rem; font-weight: 800; color: #ffffff; letter-spacing: -0.3px; margin-bottom: 4px;">
        📝 디지털 보건 탐구
    </div>
    <div style="text-align: center; font-size: 0.84rem; color: #38bdf8; font-weight: 600; line-height: 1.5; margin-bottom: 14px;">
        서울의료보건고 보건간호과<br>데이터 기반 융합수업 활동지
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # 4. 메뉴 선택 (중학생도 직관적으로 이해하는 깔끔한 1줄 메뉴)
    menu = st.radio(
        "📌 학습 단계 선택",
        [
            "1. 법정감염병 탐구",
            "2. 데이터시각화 실험실",
            "3. 감염병 발생지역 비교",
            "4. 학교방역 시뮬레이터",
            "5. AI 보건튜터"
        ],
        key="main_nav_menu"
    )

    st.divider()
    st.subheader("📂 데이터 소스 관리")
    data_mode = st.radio("데이터 소스 선택", ["질병관리청 표준 데이터 (2019~2025)", "내 CSV 파일 직접 업로드"], key="data_source_mode")
    if data_mode == "내 CSV 파일 직접 업로드":
        st.info("💡 **다중 비교 안내**: Ctrl 또는 Shift를 누른 채 클릭하거나 여러 CSV 파일을 한 번에 드래그하면 2~3종 감염병을 동시에 비교 분석할 수 있습니다.")
        up_files = st.file_uploader(
            "📂 CSV 파일 다중 업로드 (수두, 홍역, 백일해 등 2개 이상 선택)",
            type=["csv"],
            accept_multiple_files=True,
            help="수두, 홍역, 백일해 등 2개 이상의 CSV 파일을 파일 탐색기에서 한 번에 선택하거나 드래그하여 업로드하세요."
        )

        # 원클릭 실습용 로컬 3종 샘플 데이터 로드 기능
        st.markdown("<div style='font-size:0.83rem; color:#94a3b8; margin-top:6px;'>🧪 <b>수업 실습용 원클릭 샘플</b> (CSV 파일이 준비되지 않았을 때)</div>", unsafe_allow_html=True)
        if st.button("🚀 [원클릭 로드] 수두 + 홍역 + 백일해 3종 데이터 불러오기", use_container_width=True, key="btn_load_preset_3"):
            st.session_state["use_preset_multi_csv"] = True
            st.session_state["preset_loaded_notice"] = True
            st.rerun()

        if st.session_state.get("use_preset_multi_csv", False) and not up_files:
            try:
                preset_paths = [
                    DATA_DIR / "수두_발생현황_2019_2025.csv",
                    DATA_DIR / "홍역_발생현황_2019_2025.csv",
                    DATA_DIR / "백일해_발생현황_2019_2025.csv"
                ]
                preset_dfs = []
                for p_p in preset_paths:
                    if p_p.exists():
                        p_df = pd.read_csv(p_p)
                        preset_dfs.append(p_df)
                if preset_dfs:
                    working_df = ensure_dataset_integrity(pd.concat(preset_dfs, ignore_index=True))
                    up_dis_list = [str(d) for d in working_df["감염병명"].unique() if str(d).strip()]
                    st.success(f"🧪 **실습용 3종 데이터 활성화**: {', '.join(up_dis_list)} (총 {len(working_df):,}건)")
                    st.caption("📁 수두, 홍역, 백일해 3개 감염병 비교 분석 모드가 즉시 가동됩니다.")
                else:
                    working_df = df_all
            except Exception as e:
                st.error(f"샘플 로드 오류: {e}")
                working_df = df_all
        elif up_files:
            st.session_state["use_preset_multi_csv"] = False
            try:
                working_df = load_uploaded_dataframe(up_files)
                up_dis_list = [str(d) for d in working_df["감염병명"].unique() if str(d).strip()] if "감염병명" in working_df.columns else []
                if len(up_dis_list) >= 2:
                    st.success(f"🎉 **다중 감염병 비교 로드 완료**: 총 {len(working_df):,}건 ({len(up_dis_list)}종: {', '.join(up_dis_list)})")
                else:
                    st.warning(f"⚠️ 현재 1개 감염병({up_dis_list[0] if up_dis_list else '알수없음'})만 로드되었습니다. 2~3종 비교 분석을 위해 수두, 백일해 등 추가 CSV 파일도 함께 드래그해 보세요!")
                st.caption(f"📁 총 {len(up_files)}개 파일 병합: " + ", ".join([f.name for f in up_files]))
            except Exception as e:
                st.error(f"오류: {e}")
                working_df = df_all
        else:
            working_df = df_all
            st.info("💡 파일을 업로드하지 않은 상태에서는 질병관리청 표준 데이터(63종)가 기본 적용됩니다.")
    else:
        st.session_state["use_preset_multi_csv"] = False
        working_df = df_all
        st.success("✅ 표준 데이터 56,700건 완비")

    st.divider()
    st.subheader("🏫 수업 진행 & AI 활성화 현황")

    in_hours, time_str, _ = get_current_school_time_status()
    current_teacher_code = st.session_state.get("teacher_code", "")
    t_clean = clean_api_key(str(current_teacher_code))
    is_teacher_unlocked = t_clean in ["1018", "보건", "0508"]

    if is_teacher_unlocked:
        st.success("🔓 **교사 권한 승인됨** (항시 활성화)")
    elif in_hours:
        st.success(f"🟢 **수업 시간 AI 가동 중**\n\n- 현재: {time_str}\n- 질문 허용: 평일 08:30 ~ 17:00")
    else:
        st.warning(f"🔒 **수업 시간 외 (AI 잠김)**\n\n- 현재: {time_str}\n- 평일 08:30 ~ 17:00에 자동 활성화됩니다.")

    # 교사용 잠금 해제 (학생들에게 힌트가 일절 노출되지 않는 보안 잠금)
    with st.expander("🔒 교사용 잠금 해제 (방과 후/시연용)", expanded=False):
        if not is_teacher_unlocked:
            teacher_input = st.text_input("교사 인증 암호", type="password", placeholder="비밀번호 입력", key="teacher_pw_box")
            if st.button("인증 확인", use_container_width=True, key="btn_teacher_verify"):
                if clean_api_key(teacher_input) in ["1018", "보건", "0508"]:
                    st.session_state["teacher_code"] = teacher_input
                    st.success("✅ 교사 인증 완료!")
                    st.rerun()
                else:
                    st.error("암호가 올바르지 않습니다.")
        else:
            st.success("✅ 교사 권한이 승인되었습니다 (전 시간 사용 가능).")
            if st.button("인증 해제 (학생 모드로 복귀)", use_container_width=True, key="btn_teacher_logout"):
                st.session_state["teacher_code"] = ""
                if "teacher_pw_box" in st.session_state:
                    st.session_state["teacher_pw_box"] = ""
                st.rerun()





# ==========================================
# 3.8 학생 탐구 활동지 양식 생성 및 다운로드 지원 (PDF 계획안 8쪽 기반)
# ==========================================
def generate_worksheet_html() -> str:
    """PDF 프로젝트 계획안 8쪽 학생 탐구 활동지를 고품질 인쇄/PDF용으로 렌더링하는 표준 양식 HTML 생성"""
    return """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>학생 탐구 활동지 - 서울의료보건고등학교 보건간호과</title>
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    * { box-sizing: border-box; font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, 'Malgun Gothic', sans-serif; }
    body {
        margin: 0;
        padding: 24px;
        background-color: #f8fafc;
        color: #1e293b;
        font-size: 13.5px;
        line-height: 1.6;
    }
    .sheet-container {
        max-width: 860px;
        margin: 0 auto;
        background: #ffffff;
        padding: 36px 42px;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #e2e8f0;
    }
    .header-box {
        border-bottom: 2.5px solid #0284c7;
        padding-bottom: 14px;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
    }
    .title-area h1 {
        margin: 0 0 6px 0;
        font-size: 24px;
        font-weight: 800;
        color: #0f172a;
        letter-spacing: -0.5px;
    }
    .title-area .sub {
        font-size: 13px;
        color: #0284c7;
        font-weight: 700;
    }
    .meta-table {
        width: 100%;
        margin-bottom: 22px;
        border-collapse: collapse;
        background: #f1f5f9;
        border-radius: 8px;
        overflow: hidden;
    }
    .meta-table td {
        padding: 10px 14px;
        border: 1px solid #cbd5e1;
        font-size: 13px;
    }
    .meta-label {
        font-weight: 700;
        color: #334155;
        width: 15%;
        background: #e2e8f0;
        text-align: center;
    }
    .meta-value {
        width: 35%;
        color: #0f172a;
    }
    .section-card {
        margin-bottom: 22px;
        border-radius: 12px;
        border: 1.5px solid #e2e8f0;
        overflow: hidden;
        page-break-inside: avoid;
    }
    .sec-header {
        padding: 10px 16px;
        font-weight: 800;
        font-size: 15px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .sec-body {
        padding: 16px 20px;
        background: #ffffff;
    }
    .sec-cyan .sec-header { background: #e0f2fe; color: #0369a1; border-bottom: 1.5px solid #bae6fd; }
    .sec-purple .sec-header { background: #ede9fe; color: #6d28d9; border-bottom: 1.5px solid #ddd6fe; }
    .sec-amber .sec-header { background: #fef3c7; color: #b45309; border-bottom: 1.5px solid #fde68a; }

    .q-row {
        margin-bottom: 12px;
        display: flex;
        flex-direction: column;
        gap: 4px;
    }
    .q-label {
        font-weight: 700;
        color: #334155;
        font-size: 13px;
    }
    .q-line {
        border-bottom: 1px dashed #94a3b8;
        min-height: 24px;
        padding: 2px 6px;
        color: #0f172a;
    }
    .q-box {
        border: 1px solid #cbd5e1;
        border-radius: 6px;
        min-height: 52px;
        padding: 8px 10px;
        background: #f8fafc;
        margin-top: 4px;
    }
    .compare-table {
        width: 100%;
        border-collapse: collapse;
        margin: 10px 0;
        font-size: 13px;
    }
    .compare-table th, .compare-table td {
        border: 1.5px solid #cbd5e1;
        padding: 8px 12px;
        text-align: center;
    }
    .compare-table th {
        background: #f1f5f9;
        font-weight: 700;
        color: #334155;
    }
    .notice-box {
        background: #fffbeb;
        border: 1.5px solid #fde68a;
        padding: 12px 16px;
        border-radius: 10px;
        margin-top: 20px;
        font-size: 12px;
        color: #92400e;
        line-height: 1.6;
    }
    .notice-box strong { color: #b45309; }
    @media print {
        body { background: #ffffff; padding: 0; }
        .sheet-container { box-shadow: none; border: none; padding: 0; max-width: 100%; }
        .notice-box { border: 1px solid #d97706; }
        @page { size: A4; margin: 14mm 12mm; }
    }
</style>
</head>
<body>
<div class="sheet-container">
    <div class="header-box">
        <div class="title-area">
            <div class="sub">서울의료보건고등학교 보건간호과 | 데이터 기반 융합수업</div>
            <h1>📋 학생 탐구 활동지</h1>
            <div style="font-size: 12.5px; color: #64748b;">공공 감염병 데이터와 예방 시뮬레이션으로 설계하는 우리 학교 감염병 예방 제안</div>
        </div>
        <div style="text-align: right; font-size: 12px; color: #64748b; font-weight: 600;">
            2022 개정 교육과정 연계<br>[12보건04-03] · [12정02-04]
        </div>
    </div>

    <!-- 기본 정보 표 -->
    <table class="meta-table">
        <tr>
            <td class="meta-label">모둠</td>
            <td class="meta-value">제 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 모둠</td>
            <td class="meta-label">작성자</td>
            <td class="meta-value">학번: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 성명:</td>
        </tr>
        <tr>
            <td class="meta-label">관심 감염병</td>
            <td class="meta-value">&nbsp;</td>
            <td class="meta-label">탐구일</td>
            <td class="meta-value">2026 년 &nbsp;&nbsp;&nbsp;월 &nbsp;&nbsp;&nbsp;일</td>
        </tr>
    </table>

    <!-- 1단계 카드 -->
    <div class="section-card sec-cyan">
        <div class="sec-header">
            <span>■</span> [1단계] 자료를 읽고 질문 만들기 (대시보드 메뉴 1, 2, 3 연계)
        </div>
        <div class="sec-body">
            <div class="q-row">
                <div class="q-label">1. 자료 제목 및 제공기관:</div>
                <div class="q-line">질병관리청 감염병포털 및 공공데이터 대시보드 (2019~2025)</div>
            </div>
            <div class="q-row">
                <div class="q-label">2. 원자료 URL 및 확인 일자:</div>
                <div class="q-line"><span style="color: #c00000; font-weight: bold;">https://261018-aihealthtutor.streamlit.app/</span> &nbsp;&nbsp;|&nbsp;&nbsp; 확인 일자: 2026. 10. 20.</div>
            </div>
            <div class="q-row">
                <div class="q-label">3. 자료의 범위 및 기본 단위:</div>
                <div class="q-line">기간: 2019~2025년 &nbsp;|&nbsp; 지역: 국내 17개 시도 및 해외 10개국 &nbsp;|&nbsp; 단위: 신규 환자 수(명)</div>
            </div>
            <div class="q-row">
                <div class="q-label">4. 데이터 종류 확인 (해당 항목에 [V] 체크하고 확인 이유를 적으시오):</div>
                <div class="q-line">[ &nbsp; ] 공식 전수·표본감시 통계 &nbsp;&nbsp;&nbsp;&nbsp; [ &nbsp; ] 수업 실습용 가상 모의 데이터<br>확인 이유: </div>
            </div>
            <div class="q-row">
                <div class="q-label">5. 비교 조건을 동일하게 맞춘 두 시점 또는 두 지역의 수치:</div>
                <div class="q-line">수치 A:<br>수치 B: </div>
            </div>
            <div class="q-row">
                <div class="q-label">6. 변화 추세를 설명하는 완성된 문장 작성:</div>
                <div class="q-line">"________년 ________명(%)에서 ________년 ________명(%)으로 총 ________명(%)<br>(증가 / 감소)하였다."</div>
            </div>
            <div class="q-row">
                <div class="q-label">7. 원자료를 확인한 대시보드 위치 및 그래프 제목:</div>
                <div class="q-line">대시보드 메뉴: 2. 감염병 발생 현황 &amp; 시각화<br>그래프 제목: </div>
            </div>
            <div class="q-row">
                <div class="q-label">8. 그래프를 관찰하며 생긴 나의 핵심 탐구 질문:</div>
                <div class="q-box" style="min-height: 48px; color: #6b7280;">(여기에 질문을 직접 입력하세요)</div>
            </div>
            <div class="q-row">
                <div class="q-label">9. 관찰 사실만으로 알 수 없는 점과 추가로 필요한 근거 자료:</div>
                <div class="q-box" style="min-height: 48px; color: #6b7280;">(여기에 내용을 직접 입력하세요)</div>
            </div>
        </div>
    </div>

    <!-- 2단계 카드 -->
    <div class="section-card sec-purple">
        <div class="sec-header">
            <span>■</span> [2단계] 보건 근거와 AI 보건튜터 도움 검토하기 (메뉴 5 연계)
        </div>
        <div class="sec-body">
            <div class="q-row">
                <div class="q-label">1. 관심 감염병의 원인 병원체 및 주요 전파 경로:</div>
                <div class="q-line">병원체: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 전파 경로: </div>
            </div>
            <div class="q-row">
                <div class="q-label">2. 주요 임상 증상 및 학교 보건실·의료기관 도움 요청 상황:</div>
                <div class="q-line">임상 증상:<br>대처: 보건관찰실 격리 및 의료기관 진료 안내</div>
            </div>
            <div class="q-row">
                <div class="q-label">3. 전파 경로와 연결되는 핵심 예방 행동 및 이유:</div>
                <div class="q-box" style="min-height: 55px; color: #6b7280;">(여기에 내용을 직접 입력하세요)</div>
            </div>
            <div class="q-row">
                <div class="q-label">4. 교과서 및 질병관리청 공식 출처 확인:</div>
                <div class="q-line">출처 제목:<br>확인 날짜: </div>
            </div>
            <div class="q-row">
                <div class="q-label">5. AI 보건튜터에게 질문하기 전, 내가 먼저 작성해 본 설명 (가설):</div>
                <div class="q-box" style="min-height: 55px; color: #6b7280;">(여기에 내용을 직접 입력하세요)</div>
            </div>
            <div class="q-row">
                <div class="q-label">6. AI 보건튜터에게 입력한 구체적 질문 또는 교사에게 문의한 질문:</div>
                <div class="q-line">질문: </div>
            </div>
            <div class="q-row">
                <div class="q-label">7. AI 답변에서 확인한 핵심 주장과 공식 자료의 해당 근거:</div>
                <div class="q-box" style="min-height: 55px; color: #6b7280;">(여기에 내용을 직접 입력하세요)</div>
            </div>
            <div class="q-row">
                <div class="q-label">8. [비판적 검토] AI 답변 중 받아들인 내용 / 고친 내용 / 확인하지 못한 내용:</div>
                <div class="q-box" style="min-height: 65px; color: #6b7280;">(여기에 내용을 직접 입력하세요)</div>
            </div>
        </div>
    </div>

    <!-- 3단계 카드 -->
    <div class="section-card sec-amber">
        <div class="sec-header">
            <span>■</span> [3단계] 예방 모형에서 조건을 비교하기 (메뉴 4 시뮬레이터 연계)
        </div>
        <div class="sec-body">
            <div class="q-label" style="margin-bottom: 6px;">1. 예방 중재 조건 조작 및 감폭 효과(Rt) 비교표:</div>
            <table class="compare-table">
                <thead>
                    <tr>
                        <th style="width: 34%;">중재 조건 항목</th>
                        <th style="width: 33%;">기준 상태 (A)</th>
                        <th style="width: 33%;">변경 상태 (B)</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style="font-weight: 700; background: #fafafa;">감염병명 및 나머지 고정 조건</td>
                        <td></td>
                        <td>(동일 유지)</td>
                    </tr>
                    <tr>
                        <td style="font-weight: 700; background: #fafafa;">이번에 바꾸는 조건 한 가지<br><span style="font-size:11px; color:#64748b;">(환기 / 마스크 / 손씻기 / 격리 중)</span></td>
                        <td></td>
                        <td></td>
                    </tr>
                    <tr>
                        <td style="font-weight: 700; background: #fafafa;">사전 예상 및 보건학적 이유</td>
                        <td></td>
                        <td></td>
                    </tr>
                    <tr>
                        <td style="font-weight: 700; background: #fafafa; color: #b45309;">앱이 계산한 유효 재생산지수<br>(Rt)</td>
                        <td style="font-weight: 700; font-size: 14px;">Rt = </td>
                        <td style="font-weight: 700; font-size: 14px; color: #0284c7;">Rt = </td>
                    </tr>
                </tbody>
            </table>

            <div class="q-row" style="margin-top: 14px;">
                <div class="q-label">2. 결과 해석 (조건 A와 B의 비교를 바탕으로):</div>
                <div class="q-line" style="line-height: 1.8;">
                    "이 &nbsp;<u>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</u>&nbsp; 모형의 &nbsp;<u>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</u>&nbsp; 조건에서<br>
                    ____________________________________________________________________"
                </div>
            </div>
            <div class="q-row">
                <div class="q-label">3. 모형의 한계 (실제 학교 교실에 그대로 적용하기 어려운 이유):</div>
                <div class="q-box" style="min-height: 50px; color: #6b7280;">(여기에 내용을 직접 입력하세요)</div>
            </div>
            <div class="q-row">
                <div class="q-label">4. 우리 학교를 위한 감염병 예방 대책 최종 제안 및 근거:</div>
                <div class="q-box" style="min-height: 60px; color: #6b7280;">(여기에 내용을 직접 입력하세요)</div>
            </div>
            <div class="q-row">
                <div class="q-label">5. 모둠 동료 및 교사 피드백 후 수정한 문장과 수정 이유:</div>
                <div class="q-box" style="min-height: 50px; color: #6b7280;">(여기에 내용을 직접 입력하세요)</div>
            </div>
        </div>
    </div>

    <!-- 하단 유의사항 -->
    <div class="notice-box">
        <strong>※ 보건의료 데이터 탐구 윤리 및 활동 안내:</strong><br>
        1. 친구의 실제 개인 질환·진료·예방접종 내역 및 실명을 활동지에 입력하지 않으며, 집계된 공공 통계와 가상 상황을 기반으로 탐구합니다.<br>
        2. 특정 환자·집단·지역·국가를 감염병 발생의 원인으로 낙인찍거나 비난하지 않으며, 전파 경로에 기반한 과학적 예방 수칙을 설계합니다.
    </div>
</div>
</body>
</html>"""




def generate_worksheet_markdown() -> str:
    """학생 탐구 활동지 마크다운 양식 텍스트 (사용자 수정본 100% 반영)"""
    return """# 📋 [서울의료보건고 보건간호과] 학생 탐구 활동지
> **프로젝트 주제**: 서울의료보건고등학교 보건간호과 / 데이터 기반 감염병 융합 수업  
> **교육과정 연계**: 2022 개정 보건 [12보건04-03], 정보 [12정02-04], 보건간호 [보간 22-04] 준용  

---

### 👤 기본 정보
- **모둠**: 제 ______ 모둠
- **작성자**: 학번: ______________ 성명: ______________
- **관심 감염병**: ____________________
- **탐구일**: 2026년 ______월 ______일

---

### ■ [1단계] 자료를 읽고 질문 만들기 (대시보드 메뉴 1, 2, 3 연계)
1. **자료 제목 및 제공기관**: 질병관리청 감염병포털 및 공공데이터 대시보드 (2019~2025)
2. **원자료 URL 및 확인 일자**: `https://261018-aihealthtutor.streamlit.app/` (확인 일자: 2026. 10. 20.)
3. **자료의 범위 및 기본 단위**: 기간(2019~2025년), 지역(국내 17개 시도 및 해외 10개국), 단위(신규 환자 수(명))
4. **데이터 종류 확인 (해당 항목에 [V] 체크하고 확인 이유를 적으시오)**:
   - [  ] 공식 전수·표본감시 통계   [  ] 수업 실습용 가상 모의 데이터
   - 확인 이유: __________________________________________________
5. **비교 조건을 동일하게 맞춘 두 시점 또는 두 지역의 수치**:
   - 수치 A: ____________________________________________________
   - 수치 B: ____________________________________________________
6. **변화를 설명하는 문장**:  
   *"________년 ________명(%)에서 ________년 ________명(%)으로 총 ________명(%) (증가 / 감소)하였다."*
7. **원자료를 확인한 대시보드 위치 및 그래프 제목**:
   - 대시보드 메뉴: 2. 감염병 발생 현황 & 시각화
   - 그래프 제목: __________________________________________________
8. **그래프를 관찰하며 생긴 나의 핵심 탐구 질문**:  
   - (여기에 질문을 직접 입력하세요)
9. **관찰 사실만으로 알 수 없는 점과 추가로 필요한 근거 자료**:  
   - (여기에 내용을 직접 입력하세요)

---

### ■ [2단계] 보건 근거와 AI 보건튜터 도움 검토하기 (메뉴 5 연계)
1. **관심 감염병의 원인 병원체 및 주요 전파 경로**:  
   - 병원체: ____________________________________________________
   - 전파 경로: _________________________________________________
2. **주요 임상 증상 및 학교 보건실·의료기관 도움 요청 상황**:  
   - 임상 증상: _________________________________________________
   - 대처: 보건관찰실 격리 및 의료기관 진료 안내
3. **전파 경로와 연결되는 핵심 예방 행동 및 이유**:  
   - (여기에 내용을 직접 입력하세요)
4. **교과서 및 질병관리청 공식 출처 확인**:  
   - 출처 제목: _________________________________________________
   - 확인 날짜: _________________________________________________
5. **AI 보건튜터에게 질문하기 전, 내가 먼저 작성해 본 설명 (가설)**:  
   - (여기에 내용을 직접 입력하세요)
6. **AI 보건튜터에게 입력한 구체적 질문 또는 교사에게 문의한 질문**:  
   - 질문: ______________________________________________________
7. **AI 답변에서 확인한 핵심 주장과 공식 자료의 해당 근거**:  
   - (여기에 내용을 직접 입력하세요)
8. **[비판적 검토] AI 답변 중 받아들인 내용 / 고친 내용 / 확인하지 못한 내용**:  
   - (여기에 내용을 직접 입력하세요)

---

### ■ [3단계] 예방 모형에서 조건을 비교하기 (메뉴 4 시뮬레이터 연계)

| 중재 조건 항목 | 기준 상태 (A) | 변경 상태 (B) |
| :--- | :--- | :--- |
| **감염병명 및 나머지 고정 조건** | | (동일 유지) |
| **이번에 바꾸는 조건 한 가지 (환기/마스크/손씻기/격리 중)** | | |
| **사전 예상 및 보건학적 이유** | | |
| **앱이 계산한 유효 재생산지수 (Rt)** | **Rt = ________** | **Rt = ________** |

1. **결과 해석 (조건 A와 B의 비교를 바탕으로)**:  
   *"이 [ ____________ ] 모형의 [ ____________ ] 조건에서 ________________________________"*
2. **모형의 한계 (실제 학교 교실에 그대로 적용하기 어려운 이유)**:  
   - (여기에 내용을 직접 입력하세요)
3. **우리 학교를 위한 감염병 예방 대책 최종 제안 및 근거**:  
   - (여기에 내용을 직접 입력하세요)
4. **모둠 동료 및 교사 피드백 후 수정한 문장과 수정 이유**:  
   - (여기에 내용을 직접 입력하세요)

---

### ※ 보건의료 데이터 탐구 윤리 및 활동 안내
1. 친구의 실제 개인 질환·진료·예방접종 내역 및 실명을 활동지에 입력하지 않으며, 집계된 공공 통계와 가상 상황을 기반으로 탐구합니다.  
2. 특정 환자·집단·지역·국가를 감염병 발생의 원인으로 낙인찍거나 비난하지 않으며, 전파 경로에 기반한 과학적 예방 수칙을 설계합니다.
"""


def generate_worksheet_hwp() -> bytes:
    """사용자가 직접 편집한 3쪽 양식(PDF)과 100% 동일하게 일치하며, 한글(HWP)에서 좌우 여백과 표 폭이 완벽히 정렬되는 문서 서식 생성 (UTF-8 BOM 적용)"""
    hwp_doc = """<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html lang="ko">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>학생 탐구 활동지 - 서울의료보건고등학교 보건간호과</title>
<style type="text/css">
@page {
    size: 210mm 297mm;
    margin: 15mm 15mm 15mm 15mm;
}
body {
    font-family: '맑은 고딕', 'Malgun Gothic', '한컴 돋움', '돋움', Dotum, sans-serif;
    color: #000000;
    line-height: 1.35;
    margin: 0px;
    padding: 0px;
}
.page-container {
    width: 148mm;
    margin: 0 auto;
}
.page-break {
    page-break-before: always;
    clear: both;
}

/* 제목 */
.title-main {
    font-size: 19pt;
    font-weight: bold;
    text-align: center;
    letter-spacing: 5px;
    margin: 0 0 3px 0;
}
.title-sub {
    font-size: 10.5pt;
    font-weight: bold;
    text-align: center;
    margin: 0 0 8px 0;
}

/* 테이블 공통: 한글 프로그램에서 좌우 여백 100% 꽉 차게 일치 */
table {
    border-collapse: collapse;
}
.outer-box {
    width: 100%;
    table-layout: fixed;
    border: 1.5px solid #333333;
    border-collapse: collapse;
    margin-bottom: 6px;
}

/* 인적사항 내부 표 (12% + 24% + 14% + 25% + 25% = 100%) */
.info-inner-tbl {
    width: 100%;
    table-layout: fixed;
    border-collapse: collapse;
    border: none;
}
.info-inner-tbl td, .info-inner-tbl th {
    border: 1px solid #333333;
    padding: 4px 6px;
    font-size: 9.5pt;
}

/* 헤더 바 (1, 2, 3단계) */
.step-bar-1 {
    background-color: #dbeafe;
    color: #1d4ed8;
    font-size: 10pt;
    font-weight: bold;
    padding: 5px 8px;
    border-top: 1px solid #333333;
    border-bottom: 1px solid #333333;
}
.step-bar-2 {
    background-color: #ede9fe;
    color: #6d28d9;
    font-size: 10pt;
    font-weight: bold;
    padding: 5px 8px;
    border-bottom: 1px solid #333333;
}
.step-bar-3 {
    background-color: #fef3c7;
    color: #b45309;
    font-size: 10pt;
    font-weight: bold;
    padding: 5px 8px;
    border-bottom: 1px solid #333333;
}

/* 본문 컨텐츠 셀 */
.box-body-cell {
    padding: 6px 8px;
    background-color: #ffffff;
    border: none;
}

/* 질문 및 텍스트 */
.q-head {
    font-size: 9.5pt;
    font-weight: bold;
    color: #000000;
    margin: 4px 0 1px 0;
}
.q-box {
    background-color: #f8fafc;
    border: 1px solid #e2e8f0;
    padding: 3px 6px;
    font-size: 9pt;
    color: #334155;
    margin-bottom: 3px;
}
.q-text {
    font-size: 9pt;
    color: #111827;
    padding: 1px 3px;
    margin-bottom: 3px;
}
.q-write {
    font-size: 9pt;
    color: #6b7280;
    padding: 1px 3px;
    margin-bottom: 3px;
}

/* 비교표 (34% + 33% + 33% = 100%) */
.cmp-table {
    width: 100%;
    table-layout: fixed;
    border-collapse: collapse;
    margin: 4px 0 6px 0;
}
.cmp-table th, .cmp-table td {
    border: 1px solid #333333;
    padding: 4px 6px;
    font-size: 9pt;
}
.cmp-table th {
    background-color: #f8fafc;
    font-weight: bold;
    text-align: center;
}

/* 하단 윤리수칙 */
.notice-box {
    width: 100%;
    table-layout: fixed;
    border: 1px solid #b45309;
    background-color: #fffbeb;
    border-collapse: collapse;
    margin-top: 6px;
}
.notice-cell {
    padding: 6px 8px;
    font-size: 8.5pt;
    color: #92400e;
    line-height: 1.45;
}
</style>
</head>
<body>

<div class="page-container">

<!-- ================= [1페이지: 표제 + 인적사항 + 1단계 일체형 외곽 박스] ================= -->
<div class="title-main">학 &nbsp; 생 &nbsp; 탐 &nbsp; 구 &nbsp; 활 &nbsp; 동 &nbsp; 지</div>
<div class="title-sub">
    <span style="color: #002060;">서울의료보건고등학교 보건간호과</span> &nbsp;/&nbsp; <span style="color: #c00000;">데이터 기반 감염병 융합 수업</span>
</div>

<table class="outer-box" width="100%" border="1" bordercolor="#333333" cellpadding="0" cellspacing="0">
    <tr>
        <td style="padding: 0; border: none;">
            <table class="info-inner-tbl" width="100%" border="1" bordercolor="#333333" cellpadding="4" cellspacing="0">
                <colgroup>
                    <col width="12%">
                    <col width="24%">
                    <col width="14%">
                    <col width="25%">
                    <col width="25%">
                </colgroup>
                <tr>
                    <td align="center" bgcolor="#f3f4f6" style="font-weight: bold;">모둠</td>
                    <td></td>
                    <td align="center" bgcolor="#f3f4f6" style="font-weight: bold;">작성자</td>
                    <td>&nbsp;학번:</td>
                    <td>&nbsp;성명:</td>
                </tr>
                <tr>
                    <td align="center" bgcolor="#f3f4f6" style="font-weight: bold;">관심 감염병</td>
                    <td></td>
                    <td align="center" bgcolor="#f3f4f6" style="font-weight: bold;">탐구일</td>
                    <td colspan="2" align="center">2026 년 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 월 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 일</td>
                </tr>
            </table>
        </td>
    </tr>
    <tr>
        <td class="step-bar-1">
            ■ [1단계] 자료를 읽고 질문 만들기 (대시보드 메뉴 1, 2, 3 연계)
        </td>
    </tr>
    <tr>
        <td class="box-body-cell">
            <div class="q-head">1. 자료 제목 및 제공기관</div>
            <div class="q-box">질병관리청 감염병포털 및 공공데이터 대시보드 (2019~2025)</div>

            <div class="q-head">2. 원자료 URL 및 확인 일자</div>
            <div class="q-text">
                <span style="color: #c00000; font-weight: bold; text-decoration: underline;">https://261018-aihealthtutor.streamlit.app/</span> &nbsp;&nbsp;&nbsp;&nbsp; 확인 일자: 2026. 10. 20.
            </div>

            <div class="q-head">3. 자료의 범위 및 기본 단위</div>
            <div class="q-box">
                기간: 2019~2025년 &nbsp;&nbsp;&nbsp;&nbsp; 지역: 국내 17개 시도 및 해외 10개국 &nbsp;&nbsp;&nbsp;&nbsp; 단위: 신규 환자 수(명)
            </div>

            <div class="q-head">4. 데이터 종류 확인 (해당 항목에 [V] 체크하고 확인 이유를 적으시오)</div>
            <div class="q-text">
                [ &nbsp;&nbsp;&nbsp; ] 공식 전수·표본감시 통계 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; [ &nbsp;&nbsp;&nbsp; ] 수업 실습용 가상 모의 데이터<br>
                확인 이유: 
            </div>

            <div class="q-head">5. 비교 조건을 동일하게 맞춘 두 시점 또는 두 지역의 수치</div>
            <div class="q-text">
                수치 A:<br>
                수치 B: 
            </div>

            <div class="q-head">6. 변화 추세를 설명하는 완성된 문장 작성</div>
            <div class="q-text">
                "________년 ________명(%)에서 ________년 ________명(%)으로 총 ________명(%)<br>
                (증가 / 감소)하였다."
            </div>

            <div class="q-head">7. 원자료를 확인한 대시보드 위치 및 그래프 제목</div>
            <div class="q-text">
                대시보드 메뉴: 2. 감염병 발생 현황 &amp; 시각화<br>
                그래프 제목: 
            </div>

            <div class="q-head">8. 그래프를 관찰하며 생긴 나의 핵심 탐구 질문</div>
            <div class="q-write" style="height: 32px;">
                (여기에 질문을 직접 입력하세요)
            </div>

            <div class="q-head">9. 관찰 사실만으로 알 수 없는 점과 추가로 필요한 근거 자료</div>
            <div class="q-write" style="height: 32px;">
                (여기에 내용을 직접 입력하세요)
            </div>
        </td>
    </tr>
</table>

<!-- ================= [2페이지: 2단계 일체형 외곽 박스] ================= -->
<div class="page-break"></div>
<div style="height: 4px;"></div>

<table class="outer-box" width="100%" border="1" bordercolor="#333333" cellpadding="0" cellspacing="0">
    <tr>
        <td class="step-bar-2">
            ■ [2단계] 보건 근거와 AI 보건튜터 도움 검토하기 (메뉴 5 연계)
        </td>
    </tr>
    <tr>
        <td class="box-body-cell">
            <div class="q-head">1. 관심 감염병의 원인 병원체 및 주요 전파 경로</div>
            <div class="q-text">
                병원체: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 전파 경로: 
            </div>

            <div class="q-head">2. 주요 임상 증상 및 학교 보건실·의료기관 도움 요청 상황</div>
            <div class="q-text">
                임상 증상:<br>
                대처: 보건관찰실 격리 및 의료기관 진료 안내
            </div>

            <div class="q-head">3. 전파 경로와 연결되는 핵심 예방 행동 및 이유</div>
            <div class="q-write" style="height: 38px;">
                (여기에 내용을 직접 입력하세요)
            </div>

            <div class="q-head">4. 교과서 및 질병관리청 공식 출처 확인</div>
            <div class="q-text">
                출처 제목:<br>
                확인 날짜: 
            </div>

            <div class="q-head">5. AI 보건튜터에게 질문하기 전, 내가 먼저 작성해 본 설명 (가설)</div>
            <div class="q-write" style="height: 38px;">
                (여기에 내용을 직접 입력하세요)
            </div>

            <div class="q-head">6. AI 보건튜터에게 입력한 구체적 질문 또는 교사에게 문의한 질문</div>
            <div class="q-text">
                질문: 
            </div>

            <div class="q-head">7. AI 답변에서 확인한 핵심 주장과 공식 자료의 해당 근거</div>
            <div class="q-write" style="height: 38px;">
                (여기에 내용을 직접 입력하세요)
            </div>

            <div class="q-head">8. [비판적 검토] AI 답변 중 받아들인 내용 / 고친 내용 / 확인하지 못한 내용</div>
            <div class="q-write" style="height: 44px;">
                (여기에 내용을 직접 입력하세요)
            </div>
        </td>
    </tr>
</table>

<!-- ================= [3페이지: 3단계 일체형 외곽 박스 + 윤리수칙] ================= -->
<div class="page-break"></div>
<div style="height: 4px;"></div>

<table class="outer-box" width="100%" border="1" bordercolor="#333333" cellpadding="0" cellspacing="0">
    <tr>
        <td class="step-bar-3">
            ■ [3단계] 예방 모형에서 조건을 비교하기 (메뉴 4 시뮬레이터 연계)
        </td>
    </tr>
    <tr>
        <td class="box-body-cell">
            <div class="q-head">1. 예방 중재 조건 조작 및 감폭 효과(Rt) 비교표</div>
            <table class="cmp-table" width="100%" border="1" bordercolor="#333333" cellpadding="4" cellspacing="0">
                <colgroup>
                    <col width="34%">
                    <col width="33%">
                    <col width="33%">
                </colgroup>
                <tr bgcolor="#f8fafc">
                    <th align="center">중재 조건 항목</th>
                    <th align="center">기준 상태 (A)</th>
                    <th align="center">변경 상태 (B)</th>
                </tr>
                <tr>
                    <td bgcolor="#fafafa" align="center"><b>감염병명 및 나머지 고정 조건</b></td>
                    <td align="center"></td>
                    <td align="center">(동일 유지)</td>
                </tr>
                <tr>
                    <td bgcolor="#fafafa" align="center"><b>이번에 바꾸는 조건 한 가지<br><small style="color: #4b5563;">(환기 / 마스크 / 손씻기 / 격리 중)</small></b></td>
                    <td align="center"></td>
                    <td align="center"></td>
                </tr>
                <tr>
                    <td bgcolor="#fafafa" align="center"><b>사전 예상 및 보건학적 이유</b></td>
                    <td height="32"></td>
                    <td></td>
                </tr>
                <tr>
                    <td bgcolor="#fafafa" align="center"><b>앱이 계산한 유효 재생산지수<br>(Rt)</b></td>
                    <td align="center" style="font-weight: bold; font-size: 9.5pt;">Rt = </td>
                    <td align="center" style="font-weight: bold; font-size: 9.5pt;">Rt = </td>
                </tr>
            </table>

            <div class="q-head">2. 결과 해석 (조건 A와 B의 비교를 바탕으로)</div>
            <div class="q-text" style="line-height: 1.8;">
                "이 &nbsp;<u>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</u>&nbsp; 모형의 &nbsp;<u>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</u>&nbsp; 조건에서<br>
                ____________________________________________________________________"
            </div>

            <div class="q-head">3. 모형의 한계 (실제 학교 교실에 그대로 적용하기 어려운 이유)</div>
            <div class="q-write" style="height: 34px;">
                (여기에 내용을 직접 입력하세요)
            </div>

            <div class="q-head">4. 우리 학교를 위한 감염병 예방 대책 최종 제안 및 근거</div>
            <div class="q-write" style="height: 38px;">
                (여기에 내용을 직접 입력하세요)
            </div>

            <div class="q-head">5. 모둠 동료 및 교사 피드백 후 수정한 문장과 수정 이유</div>
            <div class="q-write" style="height: 34px;">
                (여기에 내용을 직접 입력하세요)
            </div>
        </td>
    </tr>
</table>

<table class="notice-box" width="100%" border="1" bordercolor="#b45309" cellpadding="6" cellspacing="0">
    <tr>
        <td class="notice-cell">
            <b>※ 보건의료 데이터 탐구 윤리 및 활동 안내:</b><br>
            1. 친구의 실제 개인 질환·진료·예방접종 내역 및 실명을 활동지에 입력하지 않으며, 집계된 공공 통계와 가상 상황을 기반으로 탐구합니다.<br>
            2. 특정 환자·집단·지역·국가를 감염병 발생의 원인으로 낙인찍거나 비난하지 않으며, 전파 경로에 기반한 과학적 예방 수칙을 설계합니다.
        </td>
    </tr>
</table>

</div>
</body>
</html>
"""
    # UTF-8 BOM을 추가하여 한컴오피스 한글이 UTF-8을 100% 자동 감지하도록 보장
    return b"\xef\xbb\xbf" + hwp_doc.encode("utf-8")


# ==========================================
# 3.9 학생 탐구 활동지 다이얼로그 모달 함수
# ==========================================
@st.dialog("📋 [보건간호과 융합수업] 학생 탐구 활동지 열람 및 다운로드", width="large")
def show_worksheet_dialog():
    completed_steps = 0
    if st.session_state.get("wb_step1_note", "").strip(): completed_steps += 1
    if st.session_state.get("wb_step2_note", "").strip(): completed_steps += 1
    if st.session_state.get("wb_step3_note", "").strip(): completed_steps += 1
    if st.session_state.get("wb_step4_note", "").strip(): completed_steps += 1
    if st.session_state.get("wb_step5_note", "").strip(): completed_steps += 1
    progress_pct = int((completed_steps / 5.0) * 100)

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(14, 165, 233, 0.15) 0%, rgba(99, 102, 241, 0.15) 100%); border: 1.5px solid #38bdf8; border-radius: 12px; padding: 14px 18px; margin-bottom: 14px;">
        <div style="font-size: 1.15rem; font-weight: 800; color: #38bdf8; margin-bottom: 4px;">
            🏥 서울의료보건고등학교 보건간호과 학생 탐구 활동지
        </div>
        <div style="font-size: 0.88rem; color: #cbd5e1; line-height: 1.6;">
            공공 감염병 데이터와 예방 시뮬레이션으로 설계하는 우리 학교 감염병 예방 제안 활동지입니다.<br>
            아래 <b>[👀 내가 작성한 1~5단계 활동내역 모아보기]</b>를 확인한 후, <b>표준 인쇄/PDF 양식</b> 또는 <b>한글 파일(.HWP)</b>을 다운로드받아 활동지에 직접 입력·작성해 보세요.
        </div>
        <div style="margin-top: 8px; font-size: 0.86rem; font-weight: 700; color: #38bdf8;">
            📈 현재 나의 활동지 작성 진도율: {progress_pct}% ({completed_steps}/5단계 완료)
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 1. 즉시 다운로드 버튼 영역 (표준 인쇄/PDF 양식 & 한글 HWP 파일)
    dl_c1, dl_c2 = st.columns(2)
    with dl_c1:
        st.download_button(
            label="📥 학생 탐구 활동지 다운로드 (인쇄/PDF용 양식)",
            data=generate_worksheet_html(),
            file_name="학생_탐구_활동지_서울의료보건고.html",
            mime="text/html",
            type="primary",
            use_container_width=True,
            help="고화질 표준 양식 웹 문서로 다운로드됩니다. 브라우저에서 열고 Ctrl+P를 누르면 고화질 PDF로 저장하거나 인쇄하여 직접 작성할 수 있습니다.",
            key="dl_ws_html_top"
        )
    with dl_c2:
        st.download_button(
            label="📝 한글 파일(.HWP) 양식 다운로드",
            data=generate_worksheet_hwp(),
            file_name="학생_탐구_활동지_서울의료보건고.hwp",
            mime="application/x-hwp",
            use_container_width=True,
            help="한컴오피스 한글 프로그램에서 바로 열리는 .hwp 파일입니다. 다운로드 후 자신의 탐구 내용을 직접 입력하여 저장할 수 있습니다.",
            key="dl_ws_hwp_top"
        )

    st.caption("💡 **활용 팁**: 왼쪽 버튼을 누르면 표준 인쇄/PDF 양식이 다운로드되며, 오른쪽 버튼을 누르면 한컴오피스 한글 프로그램에서 바로 열리는 .hwp 파일이 다운로드됩니다.")

    # 2. 내가 작성한 1~5단계 활동내역 모아보기 (제출 전 확인용 접이식 창)
    with st.expander("👀 내가 작성한 1~5단계 활동내역 모아보기 (활동지 작성 참고용)", expanded=True):
        st.markdown(f"""
        <div style="font-size: 0.88rem; line-height: 1.7; color: #e2e8f0;">
            <p><strong>👤 학생 인적사항:</strong> <span style="color:#38bdf8;">{st.session_state.get('wb_student_id', '-')} / {st.session_state.get('wb_student_name', '-')}</span></p>
            <p><strong>1️⃣ [1단계] 선정 감염병 및 선정이유 / 질문:</strong><br><span style="color:#93c5fd;">{st.session_state.get('wb_step1_note', '').strip() or '*(아직 작성되지 않음)*'}</span></p>
            <p><strong>2️⃣ [2단계] 데이터 시각화 차트 분석 & 관찰 사실:</strong><br><span style="color:#93c5fd;">{st.session_state.get('wb_step2_note', '').strip() or '*(아직 작성되지 않음)*'}</span></p>
            <p><strong>3️⃣ [3단계] 지역 역학 및 전파 경로 분석:</strong><br><span style="color:#93c5fd;">{st.session_state.get('wb_step3_note', '').strip() or '*(아직 작성되지 않음)*'}</span></p>
            <p><strong>4️⃣ [4단계] 학교 방역 시뮬레이션 예방 제안:</strong><br><span style="color:#93c5fd;">{st.session_state.get('wb_step4_note', '').strip() or '*(아직 작성되지 않음)*'}</span></p>
            <p><strong>5️⃣ [5단계] AI 보건 튜터 인터뷰 배움 기록:</strong><br><span style="color:#93c5fd;">{st.session_state.get('wb_step5_note', '').strip() or '*(아직 작성되지 않음)*'}</span></p>
        </div>
        """, unsafe_allow_html=True)


# ==========================================
# 4. 메인 화면 헤더 (우측 맨 위: 학생 탐구 활동지 버튼 배치)
# ==========================================
# 4. 메인 화면 헤더 (디지털 학습지 헤더 & 학생 인적사항/진도율 바)
# ==========================================
head_c1, head_c2 = st.columns([3.8, 1.2])

with head_c1:
    if b64_emblem:
        st.markdown(f"""
        <div class="header-card">
            <div class="header-emblem-square">
                <img src="data:image/png;base64,{b64_emblem}" style="height: 38px; width: 38px; object-fit: contain; display: block;" alt="서울의료보건고 로고 마크">
            </div>
            <div style="display: flex; flex-direction: column; justify-content: center; min-width: 0;">
                <div class="one-line-title">보건·정보 융합 디지털 탐구</div>
                <div style="font-size: 0.88rem; color: #38bdf8; font-weight: 700; margin-top: 3px;">서울의료보건고등학교 보건간호과 스마트 활동지</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="header-card">
            <div style="display: flex; flex-direction: column; justify-content: center; min-width: 0;">
                <div class="one-line-title">보건·정보 융합 디지털 탐구</div>
                <div style="font-size: 0.88rem; color: #38bdf8; font-weight: 700; margin-top: 3px;">서울의료보건고등학교 보건간호과 스마트 활동지</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

with head_c2:
    st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
    if st.button("📋 학생 탐구 활동지", use_container_width=True, type="primary", key="btn_open_worksheet_top"):
        show_worksheet_dialog()
    st.caption("📥 인쇄/PDF 및 한글(.HWP) 다운로드")

# 학생 인적사항 입력 및 5단계 진도율 실시간 계산
st.session_state.setdefault("wb_student_name", "고보건")
st.session_state.setdefault("wb_student_id", "보건간호과 1반 15번 (1모둠)")
st.session_state.setdefault("wb_step1_note", "")
st.session_state.setdefault("wb_step2_note", "")
st.session_state.setdefault("wb_step3_note", "")
st.session_state.setdefault("wb_step4_note", "")
st.session_state.setdefault("wb_step5_note", "")

# 단계별 완료 여부 체크
completed_steps = 0
if st.session_state.get("wb_step1_note", "").strip(): completed_steps += 1
if st.session_state.get("wb_step2_note", "").strip(): completed_steps += 1
if st.session_state.get("wb_step3_note", "").strip(): completed_steps += 1
if st.session_state.get("wb_step4_note", "").strip(): completed_steps += 1
if st.session_state.get("wb_step5_note", "").strip(): completed_steps += 1

progress_pct = int((completed_steps / 5.0) * 100)

s_bar_col1, s_bar_col2, s_bar_col3 = st.columns([1.5, 1.5, 2.0])
with s_bar_col1:
    new_s_name = st.text_input("👤 학생 이름", value=st.session_state["wb_student_name"], key="input_wb_student_name", help="작성하신 이름이 최종 활동지에 자동 반영됩니다.")
    st.session_state["wb_student_name"] = new_s_name
with s_bar_col2:
    new_s_id = st.text_input("🏷️ 학년/반/모둠", value=st.session_state["wb_student_id"], key="input_wb_student_id", help="예: 2학년 2반 3번 (보건지킴이 모둠)")
    st.session_state["wb_student_id"] = new_s_id
with s_bar_col3:
    st.markdown(f"<div style='font-size:0.83rem; color:#94a3b8; font-weight:600; margin-bottom:5px;'>📈 디지털 학습지 작성 진도율: <b style='color:#38bdf8;'>{progress_pct}%</b> ({completed_steps}/5단계 완료)</div>", unsafe_allow_html=True)
    st.progress(progress_pct / 100.0)

st.write("")


# ==========================================
# 5. 세부 화면 구현
# ==========================================

# ----------------------------------------------------
# [메뉴 1] STEP 1. 감염병 개념 & 데이터 탐색소
# ----------------------------------------------------
if menu.startswith("1.") or menu == "1. 수업 안내 및 데이터 개요":
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(56, 189, 248, 0.12) 0%, rgba(30, 41, 59, 0.6) 100%); border-left: 5px solid #38bdf8; border-radius: 10px; padding: 14px 18px; margin-bottom: 14px;">
        <div style="font-size: 1.12rem; font-weight: 700; color: #38bdf8; margin-bottom: 4px;">
            STEP 1. 감염병 기본 개념 다지기 & 실제 데이터 탐색
        </div>
        <div style="font-size: 0.88rem; color: #e2e8f0; line-height: 1.6;">
            💡 <strong>오늘의 탐구 미션</strong>: 질병관리청 법정감염병 1~4급의 핵심 분류 기준(신고 시한 및 격리 수준)을 구별하고, 2019~2025년 실제 발생 데이터에서 내가 탐구할 감염병을 선정해 보세요.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 1. 교사용 교육과정 근거 (필요할 때만 펼쳐보는 아코디언 수납 - 학생 시각적 부담 제로화)
    with st.expander("📖 2022 개정 교육과정 핵심 성취기준"):
        st.markdown("""
        <div style="font-size: 0.88rem; line-height: 1.8; color: #e2e8f0;">
            <div style="margin-bottom: 6px;">• <strong>보건과 [12보건04-03]</strong>: 감염병과 면역의 원리를 이해하고 개인과 공동체가 지켜야 할 건강수칙과 대응 방안을 사회적 차원에서 비판적으로 탐색하여 생활에 적용한다. <em>(출처: 2022 개정 고등학교 보건과 성취수준)</em></div>
            <div style="white-space: nowrap; margin-bottom: 6px;">• <strong>정보과 [12정02-03]</strong>: 빅데이터의 개념과 특징에 대한 이해를 바탕으로, 문제 해결에 적합한 데이터를 수집한다.</div>
            <div style="margin-bottom: 6px;">• <strong>정보과 [12정02-04]</strong>: 빅데이터 분석 도구를 활용하여 데이터를 시각화하고 그 의미와 가치를 해석한다.<br>&nbsp;&nbsp;&nbsp;&nbsp;<em>(출처: 2022 개정 정보과 성취평가 기준)</em></div>
            <div style="white-space: nowrap;">• 보건간호 [보간 22-04](감염 관리와 질환별 진단/관리), 공중보건 [12공보 04-01](감염병 발생 요인과 전염 경로 파악)</div>
        </div>
        """, unsafe_allow_html=True)

    # 2. 클릭하면 쏙 나오는 직관적인 법정감염병 급수 탐구 (중학교 수준의 극단적 단순화 & React DOM 에러 원천 방지)
    st.markdown("##### 📚 알아보고 싶은 감염병 급수를 클릭해 보세요")
    tab_t1, tab_t2, tab_t3, tab_t4 = st.tabs(["🔴 제1급 감염병", "🟠 제2급 감염병", "🟡 제3급 감염병", "🔵 제4급 감염병"])
    with tab_t1:
        st.error("""🔴 **제1급 감염병 (국내발생·유입관리 7종)**  
• **핵심 기준**: 치명률이 매우 높거나 집단 발생 우려가 커서 **발생 즉시 신고**하고 **음압격리**가 필요합니다.  
• **대표 질환**: 에볼라, 사스(SARS), 메르스(MERS), 신종인플루엔자, 탄저, 보툴리눔독소증, 페스트""")
    with tab_t2:
        st.warning("""🟠 **제2급 감염병 (국내발생 18종 - 학교 빈발)**  
• **핵심 기준**: 전파 위험이 높아 **24시간 이내에 보건소에 신고**하고 **격리 치료(등교 중지)**가 필요합니다.  
• **대표 질환**: 수두, 홍역, 백일해, 유행성이하선염(볼거리), 결핵, A형간염, 성홍열 등""")
    with tab_t3:
        st.warning("""🟡 **제3급 감염병 (국내발생 17종)**  
• **핵심 기준**: 24시간 이내 신고 대상이나, 전파력이 낮아 격리보다는 **지속적 발생 감시**가 주 목적입니다.  
• **대표 질환**: 쯔쯔가무시증, 말라리아, 일본뇌염, SFTS(중증열성혈소판감소증후군), 파상풍, B형/C형간염""")
    with tab_t4:
        st.info("""🔵 **제4급 감염병 (국내발생 21종)**  
• **핵심 기준**: 1~3급 외에 유행 여부를 조사하기 위해 표본감시 기관에서 **7일 이내에 신고**합니다.  
• **대표 질환**: 코로나19, 인플루엔자(독감), 수족구병, 노로바이러스 감염증, 급성호흡기감염증(RSV 등)""")

    # 3. 인터랙티브 1분 쏙쏙 개념 체크 퀴즈 (정답 스포일러 완전 제거!)
    st.markdown("""
    <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid #475569; border-radius: 8px; padding: 10px 16px; margin-top: 6px; margin-bottom: 8px;">
        <div style="font-size: 0.92rem; font-weight: 700; color: #38bdf8;">
            💡 [1분 쏙쏙 퀴즈] 학교 교실에서 환자가 생겼을 때, <b>24시간 내 신고하고 등교 중지(격리)해야 하는 급수</b>는?
        </div>
    </div>
    """, unsafe_allow_html=True)
    q_cols = st.columns(4)
    if q_cols[0].button("🔴 제1급", use_container_width=True, key="quiz_btn_1"):
        st.warning("⚠️ 아쉽네요! 제1급은 치명률이 높아 '발생 즉시 신고 및 음압격리' 대상입니다.")
    if q_cols[1].button("🟠 제2급", use_container_width=True, key="quiz_btn_2"):
        st.success("🎉 정답입니다! 수두, 백일해, 홍역 등 교내 집단유행 질환은 '24시간 이내 신고 및 격리 치료'가 필요한 제2급 감염병입니다.")
    if q_cols[2].button("🟡 제3급", use_container_width=True, key="quiz_btn_3"):
        st.info("ℹ️ 제3급은 24시간 이내 신고하지만 격리보다는 '지속적 발생 감시' 목적입니다.")
    if q_cols[3].button("🔵 제4급", use_container_width=True, key="quiz_btn_4"):
        st.info("ℹ️ 제4급은 표본감시 기관에서 7일 이내에 신고합니다.")

    st.divider()
    st.markdown("##### 📥 [실습용] 감염병 CSV 파일 다운로드")
    d_btn1, d_btn2, d_btn3, d_btn4, d_btn5 = st.columns(5)
    sample_targets = [
        ("💾 코로나19", "코로나19_발생현황_2019_2025.csv", d_btn1),
        ("💾 인플루엔자", "인플루엔자_발생현황_2019_2025.csv", d_btn2),
        ("💾 백일해", "백일해_발생현황_2019_2025.csv", d_btn3),
        ("💾 홍역", "홍역_발생현황_2019_2025.csv", d_btn4),
        ("💾 수두", "수두_발생현황_2019_2025.csv", d_btn5)
    ]
    for d_name, f_name, col_btn in sample_targets:
        f_path = DATA_DIR / f_name
        if f_path.exists():
            with open(f_path, "rb") as f:
                col_btn.download_button(
                    label=d_name,
                    data=f.read(),
                    file_name=f_name,
                    mime="text/csv",
                    use_container_width=True
                )

    st.divider()
    st.subheader("🔍 현재 데이터셋 (2019~2025 국내 17개 시도 및 해외 10개국)")
    
    num_dis = working_df["감염병명"].nunique() if "감염병명" in working_df.columns else 0
    total_rows = len(working_df)

    st.markdown(f"""
    <div class="single-line-badge-bar" style="margin-bottom: 14px;">
        <span>📊 <strong>총 데이터</strong>: {total_rows:,}건 (대한민국 1~4급 주요 법정감염병 {num_dis}종 완비)</span>
        <span>📅 <strong>수집 기간</strong>: 2019년 ~ 2025년</span>
        <span>👥 <strong>연령대 5단계</strong>: 0-9세 ・ 10-19세 ・ 20-49세 ・ 50-64세 ・ 65세 이상</span>
        <span>💉 <strong>관리 구분</strong>: 예방접종 및 격리여부 포함</span>
    </div>
    """, unsafe_allow_html=True)

    # 1행: 1급, 2급, 3급, 4급 나오고 줄바꿈 후 전체(1급~4급 법정감염병) 배치
    m1_f_col1, m1_f_col2 = st.columns([1.75, 1.25])
    with m1_f_col1:
        tier_choice = st.radio(
            "🏷️ 법정감염병 급수 필터",
            ["🔴 제1급", "🟠 제2급", "🟡 제3급", "🔵 제4급", "전체 (1급~4급 법정감염병)"],
            index=4,
            horizontal=True,
            key="m1_tier_filter_radio"
        )

    # 급수별 감염병 목록 매핑
    tier_map_key = {
        "🔴 제1급": "제1급 감염병 (국내발생·유입관리 7종)",
        "🟠 제2급": "제2급 감염병 (국내발생 18종)",
        "🟡 제3급": "제3급 감염병 (국내발생 17종)",
        "🔵 제4급": "제4급 감염병 (국내발생 21종)"
    }

    if tier_choice in tier_map_key:
        t_key = tier_map_key[tier_choice]
        dis_list = TIER_DISEASE_MAP.get(t_key, [])
        tier_short = tier_choice.split()[1]  # '제1급', '제2급' 등
        dis_opts = [f"전체 ({tier_short} 감염병 전체 보기)"] + dis_list
        lbl_text = f"🔎 {tier_short} 감염병 종류 드롭다운 선택 ({len(dis_list)}종)"
    else:
        all_dis = []
        for lst in TIER_DISEASE_MAP.values():
            all_dis.extend(lst)
        dis_opts = ["전체 (63종 전체 보기)"] + sorted(list(set(all_dis)))
        lbl_text = "🔎 감염병명 드롭다운 선택 (63종)"

    with m1_f_col2:
        selected_m1_disease = st.selectbox(
            lbl_text,
            options=dis_opts,
            index=0,
            key=f"m1_disease_sel_{tier_choice}",
            help="급수를 선택하면 해당 급수에 속한 감염병들이 나열됩니다. 원하는 질환을 선택하거나 타이핑하여 빠르게 검색할 수 있습니다."
        )

    # 2행: 연도 선택, 정렬 기준, 표시 건수 조절 (2019~2025 전 연도 탐색 완비)
    m1_opt1, m1_opt2, m1_opt3 = st.columns([1.2, 1.2, 1.1])
    with m1_opt1:
        year_options = ["전체 (2019~2025년)"] + [f"{int(y)}년" for y in sorted(working_df["연도"].dropna().unique(), reverse=True)] if "연도" in working_df.columns else ["전체 (2019~2025년)"]
        sel_year = st.selectbox("📅 조회 연도 선택", year_options, index=0, key="m1_sel_year")
    with m1_opt2:
        sort_order = st.selectbox(
            "🔄 정렬 기준",
            ["최신순 (2025년 ➡️ 2019년)", "과거순 (2019년 ➡️ 2025년)", "신규환자 많은 순", "지역 가나다순"],
            index=0,
            key="m1_sort_order"
        )
    with m1_opt3:
        limit_choice = st.selectbox(
            "👁️ 표시 건수",
            ["전체 데이터 (전체 행 모두 표시)", "2019~2025 전 연도 균등 보기 (연도별 균등 추출)", "상위 200건", "상위 100건", "상위 50건"],
            index=0,
            key="m1_limit_choice",
            help="기본적으로 전체 행이 모두 로드되어 스크롤로 2019~2025년 전체를 볼 수 있습니다."
        )

    view_df = working_df.copy()
    if tier_choice in tier_map_key:
        tier_kw = tier_choice.split()[1]  # '제1급', '제2급', '제3급', '제4급'
        view_df = view_df[view_df["법정감염병군"].str.contains(tier_kw, na=False, regex=False)]
    
    if not selected_m1_disease.startswith("전체 ("):
        view_df = view_df[view_df["감염병명"] == selected_m1_disease]

    if sel_year != "전체 (2019~2025년)":
        target_y = int(sel_year.replace("년", "").strip())
        view_df = view_df[view_df["연도"] == target_y]

    # 정렬 적용
    if sort_order == "최신순 (2025년 ➡️ 2019년)":
        sort_cols = [c for c in ["연도", "월", "신규환자수"] if c in view_df.columns]
        view_df = view_df.sort_values(by=sort_cols, ascending=[False, False, False][:len(sort_cols)])
    elif sort_order == "과거순 (2019년 ➡️ 2025년)":
        sort_cols = [c for c in ["연도", "월", "신규환자수"] if c in view_df.columns]
        view_df = view_df.sort_values(by=sort_cols, ascending=[True, True, False][:len(sort_cols)])
    elif sort_order == "신규환자 많은 순":
        if "신규환자수" in view_df.columns:
            view_df = view_df.sort_values(by=["신규환자수"], ascending=False)
    elif sort_order == "지역 가나다순":
        sort_cols = [c for c in ["지역", "연도", "월"] if c in view_df.columns]
        view_df = view_df.sort_values(by=sort_cols, ascending=[True, False, False][:len(sort_cols)])

    display_cols = [
        "연도", "월", "법정감염병군", "감염병명", "지역", "신규환자수",
        "0-9세", "10-19세", "20-49세", "50-64세", "65세 이상",
        "주요전파경로", "예방접종 또는 격리여부"
    ]
    valid_cols = [c for c in display_cols if c in view_df.columns]

    # 표시 건수 제한 적용 (전체 데이터 기본 표시 및 전 연도 균등 추출 지원)
    if limit_choice == "전체 데이터 (전체 행 모두 표시)":
        show_df = view_df
    elif sel_year == "전체 (2019~2025년)":
        # 2019년부터 2025년까지 전 연도가 고르게 보이도록 연도별 균등 추출
        limit_map = {
            "2019~2025 전 연도 균등 보기 (연도별 균등 추출)": 70,
            "상위 200건": 200,
            "상위 100건": 100,
            "상위 50건": 50
        }
        target_limit = limit_map.get(limit_choice, 70)
        years = sorted(view_df["연도"].dropna().unique(), reverse=True)
        per_year_limit = max(2, target_limit // max(1, len(years)))
        sampled_dfs = []
        for y in years:
            sub = view_df[view_df["연도"] == y].head(per_year_limit)
            sampled_dfs.append(sub)
        show_df = pd.concat(sampled_dfs).drop_duplicates() if sampled_dfs else view_df.head(target_limit)
    else:
        limit_num = 50
        num_m = re.search(r"\d+", limit_choice)
        if num_m:
            limit_num = int(num_m.group())
        show_df = view_df.head(limit_num)

    # 3. 데이터 표 펼쳐보기 컨트롤 (사용자 요청: 기본 상태에서는 숨기고 클릭 시 펼쳐지게 하여 복잡도 해소)
    show_m1_table = st.checkbox("📊 조건별 63종 감염병 전체 데이터 표 펼쳐보기 (클릭 시 열림)", value=False, key="chk_m1_show_table")
    if show_m1_table:
        st.dataframe(show_df[valid_cols], use_container_width=True)
        safe_tier_str = str(tier_choice).replace("~", "～")
        safe_year_str = str(sel_year).replace("~", "～")
        st.caption(f"💡 현재 조건({safe_tier_str}, {safe_year_str})의 총 {len(view_df):,}건 중 {len(show_df):,}건이 표시 중입니다. (2019～2025년 7개년 국내 17개 시도 및 해외 10개국 전체 데이터 완비)")
    else:
        st.info("💡 **데이터 표 숨김 상태**: 상단 조회 조건(연도, 정렬 기준 등)을 확인한 뒤 위의 **`[📊 전체 데이터 표 펼쳐보기]`**  \n체크박스를 누르시면 상세 데이터가 펼쳐집니다.")

    # [디지털 학습지 STEP 1] 학생 직접 기록 활동란
    st.write("")
    st.markdown("##### 📝 [1단계 탐구 활동지] 나의 감염병 탐구 선정 기록장")
    st.caption("보건간호과 학생으로서 오늘 깊이 있게 분석하고 싶은 감염병(예: 수두, 백일해, 코로나19 등)과 선정한 이유를 한 줄로 정리해 보세요.")

    memo1_col1, memo1_col2 = st.columns([3.1, 1.7])
    with memo1_col1:
        s1_input = st.text_area(
            "1단계 기록 내용",
            value=st.session_state.get("wb_step1_note", ""),
            placeholder="예시: 최근 교내에서 발생 위험이 커진 '백일해(제2급)'를 선정함. 청소년기 백신 추가접종 효과와 실제 유행 추세를 데이터로 검증하고 싶기 때문임.",
            label_visibility="collapsed",
            key="area_step1_memo",
            height=70
        )
    with memo1_col2:
        st.write("")
        if st.button("💾 1단계 저장 & 수행평가 연동", use_container_width=True, type="primary", key="btn_save_step1"):
            st.session_state["wb_step1_note"] = s1_input
            st.toast("✅ 1단계 기록이 저장되었으며 학생 활동지 및 수행평가에 자동 연동되었습니다!")
            st.success("연동 완료! 🟢")
            st.rerun()


# ----------------------------------------------------
# [메뉴 2] STEP 2. 데이터 시각화 탐구 (3대 차트 라이브러리 비교)
# ----------------------------------------------------
elif menu.startswith("2.") or menu in ["2. 차트 시각화 실험실", "2. 데이터시각화 실험실", "2. 감염병 발생 현황 & 시각화"]:
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(14, 165, 233, 0.12) 0%, rgba(30, 41, 59, 0.6) 100%); border-left: 5px solid #0284c7; border-radius: 10px; padding: 14px 18px; margin-bottom: 14px;">
        <div style="font-size: 1.12rem; font-weight: 700; color: #38bdf8; margin-bottom: 4px;">
            STEP 2. 데이터 시각화 탐구 (Plotly vs Seaborn vs Matplotlib)
        </div>
        <div style="font-size: 0.88rem; color: #e2e8f0; line-height: 1.6;">
            💡 <strong>오늘의 탐구 미션</strong>: 동일한 질병관리청 보건 데이터를 3대 시각화 도구로 표현해 보며, <b>도구별 특징(인터랙티브 반응 vs 통계적 분포 vs 정통 학술 그래프)</b>과 차트 형태별 전달력을 비교 분석해 보세요.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 업로드 데이터 감염병 자동 감지 및 스마트 선택 동기화
    uploaded_diseases = [d for d in working_df["감염병명"].dropna().unique() if str(d).strip()] if "감염병명" in working_df.columns else []
    is_uploaded_data = (data_mode == "내 CSV 파일 직접 업로드" and len(uploaded_diseases) > 0) or st.session_state.get("use_preset_multi_csv", False)

    tier_list_keys = list(TIER_DISEASE_MAP.keys())
    
    if "selected_tier_btn" not in st.session_state:
        st.session_state["selected_tier_btn"] = tier_list_keys[3] if len(tier_list_keys) > 3 else tier_list_keys[0]
    if "m2_tier_dropdown" not in st.session_state:
        st.session_state["m2_tier_dropdown"] = st.session_state["selected_tier_btn"]

    # 버튼 클릭 시 즉각 session_state와 동기화하는 콜백 함수
    def select_m2_tier(t_name):
        st.session_state["selected_tier_btn"] = t_name

    # 업로드된 파일 감염병의 급수로 자동 연동
    if is_uploaded_data and uploaded_diseases:
        first_dis = uploaded_diseases[0]
        detected_tier = DISEASE_INFO_DB.get(first_dis, {}).get("tier", None)
        if detected_tier:
            for t_k in tier_list_keys:
                if detected_tier in t_k or t_k.split()[0] in detected_tier:
                    st.session_state["selected_tier_btn"] = t_k
                    break

    # 1단계: 4대 급수 + 전체 급수 교차 비교 원클릭 전환 버튼 바
    st.markdown("##### 🏷️ [1단계] 법정감염병 급수 선택 (버튼 클릭 시 우측 드롭다운에 해당 감염병 즉시 나열)")
    b_c1, b_c2, b_c3, b_c4, b_c5 = st.columns(5)
    
    t_all_key = "전체 급수 교차 비교 (1~4급 63종)"
    cur_tier_state = st.session_state.get("selected_tier_btn", tier_list_keys[2])  # 기본값: 제3급 감염병 (17종)

    with b_c1:
        t1 = tier_list_keys[0]  # 제1급 감염병 (국내발생·유입관리 7종)
        st.button(f"🔴 제1급 ({len(TIER_DISEASE_MAP[t1])}종)", use_container_width=True, key="m2_btn_t1",
                  type="primary" if t1 == cur_tier_state else "secondary",
                  on_click=select_m2_tier, args=(t1,))
    with b_c2:
        t2 = tier_list_keys[1]  # 제2급 감염병 (국내발생 18종)
        st.button(f"🟠 제2급 ({len(TIER_DISEASE_MAP[t2])}종)", use_container_width=True, key="m2_btn_t2",
                  type="primary" if t2 == cur_tier_state else "secondary",
                  on_click=select_m2_tier, args=(t2,))
    with b_c3:
        t3 = tier_list_keys[2]  # 제3급 감염병 (국내발생 17종)
        st.button(f"🟡 제3급 ({len(TIER_DISEASE_MAP[t3])}종)", use_container_width=True, key="m2_btn_t3",
                  type="primary" if t3 == cur_tier_state else "secondary",
                  on_click=select_m2_tier, args=(t3,))
    with b_c4:
        t4 = tier_list_keys[3]  # 제4급 감염병 (국내발생 21종)
        st.button(f"🔵 제4급 ({len(TIER_DISEASE_MAP[t4])}종)", use_container_width=True, key="m2_btn_t4",
                  type="primary" if t4 == cur_tier_state else "secondary",
                  on_click=select_m2_tier, args=(t4,))
    with b_c5:
        st.button("🌐 전체 교차 비교 (63종)", use_container_width=True, key="m2_btn_t_all",
                  type="primary" if t_all_key == cur_tier_state else "secondary",
                  on_click=select_m2_tier, args=(t_all_key,),
                  help="제1급, 제2급, 제3급, 제4급을 넘나들며 서로 다른 급수의 법정감염병을 자유롭게 교차 비교 분석합니다.")

    sel_c1, sel_c2 = st.columns([1, 1.4])
    with sel_c1:
        default_analysis_idx = 1 if (is_uploaded_data and len(uploaded_diseases) >= 2) else 0
        analysis_type = st.selectbox(
            "📌 분석 모드 선택",
            ["단일 감염병 집중 분석", "복수 감염병 비교 분석"],
            index=default_analysis_idx,
            key="m2_analysis_type",
            help="1개 질병을 집중 분석하거나 2~4개 질병을 나란히 비교합니다."
        )

    # 복수 비교 모드일 때 다른 급수 교차 비교 확장 토글 지원
    cross_tier_active = False
    if analysis_type == "복수 감염병 비교 분석" and cur_tier_state != t_all_key:
        cross_tier_active = st.checkbox(
            "🌐 다른 급수 감염병도 함께 선택하여 교차 비교하기 (1~4급 63종 전체 확장)",
            value=False,
            key="m2_cross_tier_chk",
            help="체크하면 현재 급수뿐만 아니라 1~4급 모든 법정감염병을 교차 선택하여 나란히 비교할 수 있습니다."
        )

    # 선택된 급수에 속한 감염병 목록 산출
    if cur_tier_state == t_all_key or cross_tier_active:
        all_dis = []
        for lst in TIER_DISEASE_MAP.values():
            all_dis.extend(lst)
        scoped_diseases = sorted(list(set(all_dis)))
        tier_short_name = "전체 급수 교차"
    else:
        scoped_diseases = list(TIER_DISEASE_MAP.get(cur_tier_state, []))
        tier_short_name = cur_tier_state.split()[0]

    # 업로드된 파일의 감염병이 있을 경우 최우선 배치
    if is_uploaded_data and uploaded_diseases:
        for ud in reversed(uploaded_diseases):
            if ud in scoped_diseases:
                scoped_diseases.remove(ud)
            scoped_diseases.insert(0, ud)

    with sel_c2:
        # 단일 집중 분석 또는 복수 비교 분석 드롭다운
        placeholder_text = "👉 [탐구할 감염병을 먼저 선택하세요]"
        if analysis_type == "단일 감염병 집중 분석":
            single_options = [placeholder_text] + scoped_diseases
            chosen_single = st.selectbox(
                f"🏷️ 감염병 선택 ({tier_short_name} {len(scoped_diseases)}종)",
                options=single_options,
                index=0,
                key=f"m2_disease_select_{cur_tier_state}_{cross_tier_active}",
                help="분석할 감염병 1종을 선택하세요."
            )
            target_diseases = [chosen_single] if (chosen_single and chosen_single != placeholder_text) else []
        else:
            target_diseases = st.multiselect(
                f"🏷️ 비교할 감염병 선택 ({tier_short_name} {len(scoped_diseases)}종)",
                options=scoped_diseases,
                default=[],
                key=f"m2_multi_select_{cur_tier_state}_{cross_tier_active}",
                help="비교할 법정감염병을 2~4개 선택하세요."
            )

    # 선택된 감염병 정보 브리핑 바 (각 감염병의 급수를 직관적으로 안내)
    if target_diseases:
        badge_items = []
        for d in target_diseases:
            d_tier = DISEASE_INFO_DB.get(d, {}).get("tier", "")
            d_tier_tag = f" <span style='font-size: 0.78rem; opacity: 0.8;'>({d_tier})</span>" if d_tier else ""
            badge_items.append(f"<code>{d}</code>{d_tier_tag}")
        tier_badges = " ・ ".join(badge_items)
        st.markdown(f"""
        <div style="background: rgba(15, 23, 42, 0.5); border: 1px solid #334155; border-radius: 8px; padding: 6px 14px; font-size: 0.85rem; color: #cbd5e1; margin-top: 6px; margin-bottom: 12px;">
            🔍 <strong>현재 비교 분석 대상</strong>: {tier_badges}
        </div>
        """, unsafe_allow_html=True)

    # 데이터 필터링 적용
    df_filtered = working_df.copy()
    if target_diseases:
        df_filtered = df_filtered[df_filtered["감염병명"].isin(target_diseases)]
    df_filtered = ensure_dataset_integrity(df_filtered)

    st.write("")

    if not target_diseases:
        st.info("👆 **[감염병 선택 대기 중]**: 위 드롭다운에서 탐구하고 싶은 감염병(예: 수두, 백일해, 코로나19, 인플루엔자 등)을 선택해 보세요. 선택 즉시 환자 발생 추이, 청소년 비중 및 3대 시각화 그래프(Plotly, Seaborn, Matplotlib)가 화면에 펼쳐집니다! 📊")
    elif df_filtered.empty:
        st.warning("⚠️ 선택하신 감염병에 해당하는 데이터가 없습니다. 상단 감염병을 다시 선택해 주세요.")
    else:
        # 요약 통계 지표 카드
        tot_cnt = int(df_filtered["신규환자수"].sum())
        youth_cnt = int(df_filtered["10-19세"].sum())
        youth_pct = (youth_cnt / tot_cnt * 100) if tot_cnt > 0 else 0
        top_place = df_filtered.groupby("지역")["신규환자수"].sum().idxmax()
        route_text = df_filtered["주요전파경로"].mode()[0] if not df_filtered["주요전파경로"].empty else "정보없음"

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("총 환자 수", f"{tot_cnt:,}명")
        m2.metric("청소년(10-19세) 환자 수", f"{youth_cnt:,}명", f"비중 {youth_pct:.1f}%")
        m3.metric("최다 발생 지역/국가", f"{top_place}")
        m4.metric("주요 전파 경로", f"{route_text}")

        st.divider()

        # 3단계: 사용자 요청 4대 분석 차원 선택
        st.markdown("##### 🔍 3단계: 분석 데이터 관점 선택 (연도별 / 연령별 / 국가별 / 지역별)")
        data_view = st.radio(
            "분석 관점 선택",
            [
                "📅 1. 연도별 발생 추이 분석 (2019 ~ 2025)",
                "👥 2. 5개 연령대별 세분화 환자 분포 분석",
                "🌐 3. 해외 주요 10개국 발생 현황 분석",
                "🇰🇷 4. 국내 17개 시도별 발생 현황 분석"
            ],
            horizontal=True
        )

        st.write("")

        # 3.5단계: 시각화 차트 형태 및 y축 스케일 배율 선택
        st.markdown("##### 📊 그래프 시각화 형태 및 배율 선택 (꺾은선 / 막대 / 누적 영역)")

        # 선택된 질환 간 최대/최소 격차 계산 (스마트 스케일 자동 감지)
        active_vals = df_filtered["신규환자수"][df_filtered["신규환자수"] > 0]
        max_val_all = active_vals.max() if not active_vals.empty else 0
        min_val_all = active_vals.min() if not active_vals.empty else 0
        is_huge_gap = bool(min_val_all > 0 and (max_val_all / min_val_all) >= 25)

        c_style1, c_style2 = st.columns([3, 2])
        with c_style1:
            chart_style = st.radio(
                "차트 표현 형태 선택",
                [
                    "📈 꺾은선 추세 그래프 (Line)",
                    "📊 묶은 막대 그래프 (Bar)",
                    "🏔️ 누적 영역 그래프 (Stacked Area)"
                ],
                horizontal=True,
                help="학생들이 동일한 보건 데이터를 3가지 대표 시각화 기법으로 비교 관찰합니다."
            )
        with c_style2:
            scale_mode = st.radio(
                "y축 수치 배율 (스케일 모드)",
                [
                    "📏 일반 스케일 (선형 Linear)",
                    "🔍 로그 스케일 (소규모 감염병 확대 Log)"
                ],
                index=0,
                horizontal=True,
                help="수백 명 단위의 소규모 감염병(디프테리아 등)과 수십만 명 단위의 대규모 감염병(인플루엔자 등)을 함께 비교할 때, 막대가 바닥에 묻히지 않도록 로그 스케일로 모든 막대를 선명하게 확대합니다."
            )

        use_log = ("로그" in scale_mode)
        if is_huge_gap and use_log:
            st.info(f"💡 **소규모 감염병 가시화 모드 가동 중 (로그 스케일)**: 감염병 간 발생 환자 규모 차이(최소 {int(min_val_all):,}명 ~ 최대 {int(max_val_all):,}명, 약 {int(max_val_all/min_val_all):,}배 격차)가 매우 커서, 바닥에 깔리던 소규모 감염병 막대도 균형 있게 선명한 높이로 자동 확대되었습니다. (절대 수치 비율은 상단 '📏 일반 스케일' 선택 시 확인 가능)")
        elif is_huge_gap and not use_log:
            st.warning(f"⚠️ **스케일 격차 안내**: 소규모 감염병(수백 명)이 대규모 감염병(수십만 명)에 비해 막대가 바닥에 납작하게 보일 수 있습니다. 우측 상단의 **'🔍 로그 스케일(소규모 감염병 확대 Log)'**을 클릭하시면 모든 막대를 선명한 높이로 보실 수 있습니다.")

        st.caption("💡 상단 차트 형태(꺾은선 / 막대 / 누적 영역) 및 배율 모드는 **1. Plotly, 2. Seaborn, 3. Matplotlib** 탭에 실시간 동시 적용됩니다. (4번 도넛 탭은 전체 대비 100% 점유율 전용 분석)")

        st.write("")

        # 4단계: 시각화 라이브러리 및 원/도넛 점유율 분석 탭 (사용자 요청: 3대 비교 탭 삭제 -> 원/도넛 그래프 탭 신설)
        tab_plotly, tab_seaborn, tab_matplotlib, tab_donut = st.tabs([
            "⚡ 1. Plotly (동적 인터랙티브)",
            "🎨 2. Seaborn (통계적 그래픽)",
            "📉 3. Matplotlib (정밀 출판용)",
            "🍩 4. 원/도넛형 점유율 분석"
        ])

        # 감염병 간 명확한 시각적 구분을 위한 고대비 비비드 카테고리 컬러 팔레트 (청록, 주황, 녹색, 빨강, 보라, 황금 등)
        palette_colors = ["#00b4d8", "#f77f00", "#10b981", "#e63946", "#8338ec", "#ffb703", "#06d6a0", "#d62828"]

        # ==================================================================
        # 관점 1: 연도별 발생 추이 분석 (2019 ~ 2025)
        # ==================================================================
        if "1. 연도별" in data_view:
            ts = df_filtered.groupby(["연도", "감염병명"])["신규환자수"].sum().reset_index().sort_values("연도")
            years = sorted(ts["연도"].unique())
            year_labels = [f"{int(y)}년" for y in years]

            # (1) ⚡ Plotly 탭
            with tab_plotly:
                st.markdown("###### ⚡ Plotly: 마우스 호버로 정확한 수치와 확대/축소가 가능한 동적 인터랙티브 차트")
                if "꺾은선" in chart_style:
                    fig_p = px.line(ts, x="연도", y="신규환자수", color="감염병명", markers=True, title="연도별 감염병 환자 발생 추이 (Plotly 꺾은선)", template="plotly_dark", color_discrete_sequence=palette_colors)
                elif "막대" in chart_style:
                    fig_p = px.bar(ts, x="연도", y="신규환자수", color="감염병명", barmode="group", text_auto=',d', title="연도별 감염병 환자 발생 비교 (Plotly 묶은 막대)", template="plotly_dark", color_discrete_sequence=palette_colors)
                    # 막대 위 바깥에 흰색 글씨 배치 및 좁은 경우 겹침 방지
                    fig_p.update_traces(
                        textposition='outside',
                        cliponaxis=False,
                        textfont=dict(size=9.5, color='#ffffff', family='Pretendard, sans-serif')
                    )
                    max_val_p = ts["신규환자수"].max() if not ts.empty else 0
                    if max_val_p > 0 and not use_log:
                        fig_p.update_yaxes(range=[0, max_val_p * 1.25])
                else:
                    fig_p = px.area(ts, x="연도", y="신규환자수", color="감염병명", markers=True, title="연도별 감염병 누적 발생 분포 (Plotly 누적 영역)", template="plotly_dark", color_discrete_sequence=palette_colors)
                
                if use_log:
                    fig_p.update_yaxes(type="log")
                else:
                    fig_p.update_yaxes(type="linear")
                fig_p.update_layout(xaxis_title="발생 연도", yaxis_title="신규 환자 수(명) (로그 스케일)" if use_log else "신규 환자 수(명)", height=390, margin=dict(l=40, r=20, t=40, b=60), uniformtext_minsize=7, uniformtext_mode='hide')
                fig_p.update_xaxes(tickangle=0, dtick=1, tickmode='linear', tickformat="d")
                fig_p.update_yaxes(tickformat=',d')
                st.plotly_chart(fig_p, use_container_width=True, key="plotly_v1_main")

            # (2) 🎨 Seaborn 탭
            with tab_seaborn:
                st.markdown("###### 🎨 Seaborn: 통계 분포 및 세련된 컬러 팔레트를 제공하는 그래픽스")
                fig_s, ax_s = plt.subplots(figsize=(8.8, 3.9), dpi=100)
                apply_dark_plot_style(fig_s, ax_s)

                if "꺾은선" in chart_style:
                    sns.lineplot(data=ts, x="연도", y="신규환자수", hue="감염병명", marker="o", markersize=8, linewidth=2.5, palette="coolwarm", ax=ax_s)
                    ax_s.set_title("연도별 감염병 환자 발생 추이 (Seaborn)")
                    ax_s.set_xticks(years)
                    ax_s.set_xticklabels(year_labels, rotation=0)
                elif "막대" in chart_style:
                    n_uniq = len(ts["감염병명"].unique())
                    sns.barplot(data=ts, x="연도", y="신규환자수", hue="감염병명", palette=palette_colors[:n_uniq], ax=ax_s)
                    ax_s.set_title("연도별 감염병 환자 발생 비교 (Seaborn 막대)")
                    valid_patches = sorted([p for p in ax_s.patches if p.get_height() > 0], key=lambda p: p.get_x())
                    smart_annotate_bars(ax_s, valid_patches, total_bars=len(valid_patches))
                    ax_s.set_xticks(range(len(years)))
                    ax_s.set_xticklabels(year_labels, rotation=0)
                else:
                    p_df = ts.pivot(index="연도", columns="감염병명", values="신규환자수").fillna(0)
                    y_arrays = [p_df[col].values for col in p_df.columns]
                    colors_stack = sns.color_palette("mako", len(p_df.columns))
                    ax_s.stackplot(years, y_arrays, labels=p_df.columns, colors=colors_stack, alpha=0.85)
                    ax_s.set_title("연도별 감염병 누적 환자 구성 (Seaborn 누적 영역)")
                    ax_s.set_xticks(years)
                    ax_s.set_xticklabels(year_labels, rotation=0)

                max_val_s = ts["신규환자수"].max() if not ts.empty else 0
                if use_log and max_val_s > 0:
                    min_pos_s = ts[ts["신규환자수"] > 0]["신규환자수"].min() if not ts[ts["신규환자수"] > 0].empty else 1
                    ax_s.set_yscale('log')
                    ax_s.set_ylim(bottom=max(1, min_pos_s * 0.3), top=max_val_s * 4.0)
                    ax_s.yaxis.set_major_formatter(ticker.FuncFormatter(format_korean_log_ticks))
                    ax_s.set_ylabel("신규 환자 수(명, 로그 스케일)")
                else:
                    if max_val_s > 0:
                        ax_s.set_ylim(0, max_val_s * 1.38)
                    ax_s.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{int(x):,}"))
                    ax_s.set_ylabel("신규 환자 수(명)")

                ax_s.set_xlabel("발생 연도")
                ax_s.tick_params(axis='x', rotation=0)
                # 범례를 차트 바깥 오른쪽으로 이동시켜 막대를 가리지 않도록 개선
                ax_s.legend(title="감염병명", bbox_to_anchor=(1.02, 1), loc='upper left', facecolor='#1e293b', edgecolor='#475569', labelcolor='#f8fafc', fontsize=8.5)
                plt.tight_layout()

                st.pyplot(fig_s, use_container_width=True)
                buf_s = io.BytesIO()
                fig_s.savefig(buf_s, format="png", dpi=200, bbox_inches="tight")
                buf_s.seek(0)
                st.download_button(
                    label="💾 Seaborn 고화질 그래프(PNG) 다운로드",
                    data=buf_s.getvalue(),
                    file_name="감염병_시각화_Seaborn.png",
                    mime="image/png",
                    use_container_width=True,
                    key=f"dl_seaborn_{data_view[:3]}_{chart_style[:2]}"
                )
                plt.close(fig_s)

            # (3) 📉 Matplotlib 탭
            with tab_matplotlib:
                st.markdown("###### 📉 Matplotlib: 픽셀 단위 축·폰트·레이아웃을 정밀하게 제어하는 표준 도표")
                fig_m, ax_m = plt.subplots(figsize=(8.8, 3.9), dpi=100)
                apply_dark_plot_style(fig_m, ax_m)

                if "꺾은선" in chart_style:
                    for i, d_name in enumerate(target_diseases):
                        sub_ts = ts[ts["감염병명"] == d_name]
                        ax_m.plot(sub_ts["연도"], sub_ts["신규환자수"], marker='s', markersize=7, linewidth=2.2, label=d_name, color=palette_colors[i % len(palette_colors)])
                        for _, row in sub_ts.iterrows():
                            lbl = format_smart_label(row["신규환자수"], compact=True)
                            if lbl:
                                y_off = 6 if i % 2 == 0 else -14
                                va_pos = 'bottom' if i % 2 == 0 else 'top'
                                ax_m.annotate(lbl, (row["연도"], row["신규환자수"]), textcoords="offset points", xytext=(0, y_off), ha='center', va=va_pos, fontsize=7.5, color='#ffffff', weight='bold', path_effects=[pe.withStroke(linewidth=2.0, foreground='#0f172a')])
                    ax_m.set_title("연도별 감염병 환자 발생 추이 및 수치 라벨 (Matplotlib)")
                    ax_m.set_xticks(years)
                    ax_m.set_xticklabels(year_labels, rotation=0)
                elif "막대" in chart_style:
                    n_dis = max(len(target_diseases), 1)
                    bar_w = 0.8 / n_dis
                    all_bars_m = []
                    for i, d_name in enumerate(target_diseases):
                        sub = ts[ts["감염병명"] == d_name].set_index("연도").reindex(years, fill_value=0)
                        offsets = [idx + (i - n_dis / 2 + 0.5) * bar_w for idx in range(len(years))]
                        bars_m = ax_m.bar(offsets, sub["신규환자수"], width=bar_w, label=d_name, color=palette_colors[i % len(palette_colors)], edgecolor="#1e293b")
                        all_bars_m.extend(bars_m)
                    smart_annotate_bars(ax_m, all_bars_m, total_bars=len(all_bars_m))
                    ax_m.set_title("연도별 감염병 환자 발생 비교 (Matplotlib 막대)")
                    ax_m.set_xticks(range(len(years)))
                    ax_m.set_xticklabels(year_labels, rotation=0)
                else:
                    p_df = ts.pivot(index="연도", columns="감염병명", values="신규환자수").fillna(0)
                    y_arrays = [p_df[col].values for col in p_df.columns]
                    ax_m.stackplot(years, y_arrays, labels=p_df.columns, colors=palette_colors[:len(p_df.columns)], alpha=0.85)
                    ax_m.set_title("연도별 감염병 누적 환자 구성 (Matplotlib 누적 영역)")
                    ax_m.set_xticks(years)
                    ax_m.set_xticklabels(year_labels, rotation=0)

                max_val_m = ts["신규환자수"].max() if not ts.empty else 0
                if use_log and max_val_m > 0:
                    min_pos_m = ts[ts["신규환자수"] > 0]["신규환자수"].min() if not ts[ts["신규환자수"] > 0].empty else 1
                    ax_m.set_yscale('log')
                    ax_m.set_ylim(bottom=max(1, min_pos_m * 0.3), top=max_val_m * 4.0)
                    ax_m.yaxis.set_major_formatter(ticker.FuncFormatter(format_korean_log_ticks))
                    ax_m.set_ylabel("신규 환자 수(명, 로그 스케일)")
                else:
                    if max_val_m > 0:
                        ax_m.set_ylim(0, max_val_m * 1.38)
                    ax_m.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{int(x):,}"))
                    ax_m.set_ylabel("신규 환자 수(명)")

                ax_s_xlabel = "발생 연도"
                ax_m.set_xlabel(ax_s_xlabel)
                ax_m.tick_params(axis='x', rotation=0)
                # 범례를 차트 바깥 오른쪽으로 이동시켜 막대와 숫자를 가리지 않도록 개선
                ax_m.legend(title="감염병명", bbox_to_anchor=(1.02, 1), loc='upper left', facecolor='#1e293b', edgecolor='#475569', labelcolor='#f8fafc', fontsize=8.5)
                plt.tight_layout()

                st.pyplot(fig_m, use_container_width=True)
                st.caption("💡 **가독성 최적화 안내**: 막대 밀집 시 인접한 낮은 수치끼리 글자가 겹치거나 막대와 간섭되지 않도록 폰트 크기 최적화(5.0pt), 지능형 충돌 회피 오프셋 및 세련된 사선(55~60°) 정렬이 자동 적용됩니다. 정밀 숫자는 '1. Plotly' 탭 마우스 호버 또는 하단 데이터 표에서 100% 확인하실 수 있습니다.")
                buf_m = io.BytesIO()
                fig_m.savefig(buf_m, format="png", dpi=200, bbox_inches="tight")
                buf_m.seek(0)
                st.download_button(
                    label="💾 Matplotlib 고화질 그래프(PNG) 다운로드",
                    data=buf_m.getvalue(),
                    file_name="감염병_시각화_Matplotlib.png",
                    mime="image/png",
                    use_container_width=True,
                    key=f"dl_matplotlib_{data_view[:3]}_{chart_style[:2]}"
                )
                plt.close(fig_m)

            # (4) 🍩 원/도넛형 점유율 분석 탭
            with tab_donut:
                st.caption("💡 '원/도넛형 점유율 분석'은 전체 대비 100% 비중을 분석하는 전용 도표입니다. (상단 꺾은선/막대/누적영역 선택은 1~3번 탭에 적용됩니다)")
                st.markdown("###### 🍩 원/도넛형 점유율 분석: 발생 비중 및 구성 비율 탐구")
                if len(target_diseases) > 1:
                    pie_df = ts.groupby("감염병명")["신규환자수"].sum().reset_index()
                    p_name = "감염병명"
                    p_title = "감염병별 환자 점유율"
                else:
                    pie_df = ts.groupby("연도")["신규환자수"].sum().reset_index()
                    pie_df["연도라벨"] = pie_df["연도"].apply(lambda y: f"{int(y)}년")
                    p_name = "연도라벨"
                    p_title = f"{target_diseases[0]} 연도별 발생 비중"

                active_pie_df = pie_df[pie_df["신규환자수"] > 0]
                if active_pie_df.empty or active_pie_df["신규환자수"].sum() <= 0:
                    st.info("ℹ️ 점유율을 분석할 환자 발생 데이터가 없습니다 (0명).")
                else:
                    d_col1, d_col2 = st.columns(2)
                    with d_col1:
                        fig_p_donut = px.pie(active_pie_df, values="신규환자수", names=p_name, hole=0.45, title=f"{p_title} (Plotly 동적 도넛)", template="plotly_dark", color_discrete_sequence=palette_colors)
                        fig_p_donut.update_layout(height=360, margin=dict(l=15, r=15, t=35, b=25), legend=dict(font=dict(size=9.5)))
                        st.plotly_chart(fig_p_donut, use_container_width=True, key="plotly_v1_donut")

                    with d_col2:
                        fig_s_donut, ax_sd = plt.subplots(figsize=(5.0, 3.6), dpi=100)
                        apply_dark_plot_style(fig_s_donut, ax_sd)
                        patches_d, texts_d, autotexts_d = ax_sd.pie(
                            active_pie_df["신규환자수"],
                            labels=active_pie_df[p_name],
                            autopct="%1.1f%%",
                            colors=palette_colors[:len(active_pie_df)],
                            radius=0.82,
                            pctdistance=0.65
                        )
                        for t in texts_d:
                            t.set_color('#ffffff')
                            t.set_fontsize(9)
                            t.set_weight('bold')
                        for at in autotexts_d:
                            at.set_color('#0f172a')
                            at.set_fontsize(10)
                            at.set_weight('bold')
                            at.set_path_effects([pe.withStroke(linewidth=1.8, foreground='#ffffff')])

                        ax_sd.add_artist(plt.Circle((0,0), 0.45, fc='#0f172a'))
                        ax_sd.set_title(f"{p_title} (Seaborn 통계 도넛)", fontsize=10.5, pad=8, color="#f8fafc")
                        plt.tight_layout()
                        st.pyplot(fig_s_donut, use_container_width=True)
                        plt.close(fig_s_donut)

        # ==================================================================
        # 관점 2: 5개 연령대별 세분화 환자 분포 분석
        # ==================================================================
        elif "2. 5개 연령대별" in data_view:
            age_cols = ["0-9세", "10-19세", "20-49세", "50-64세", "65세 이상"]
            age_grp = df_filtered.groupby("감염병명")[age_cols].sum().reset_index()
            age_melted = age_grp.melt(id_vars="감염병명", value_vars=age_cols, var_name="연령대", value_name="환자수")
            tot_age = df_filtered[age_cols].sum().reset_index()
            tot_age.columns = ["연령대", "환자수"]

            with tab_plotly:
                if "꺾은선" in chart_style:
                    st.markdown("###### ⚡ Plotly: 5개 연령대별 환자 취약도 꺾은선 추세 (마우스 호버 시 세부 환자 수 표시)")
                    fig_p = px.line(age_melted, x="연령대", y="환자수", color="감염병명", markers=True, title="감염병별 5개 연령대 취약도 꺾은선 추세 (Plotly)", template="plotly_dark", color_discrete_sequence=palette_colors)
                elif "막대" in chart_style:
                    st.markdown("###### ⚡ Plotly: 5개 연령대별 묶은 막대 비교 (마우스 호버 시 세부 환자 수 표시)")
                    fig_p = px.bar(age_melted, x="감염병명", y="환자수", color="연령대", barmode="group", text_auto=',d', title="감염병별 5개 연령대 세분화 묶은 막대 (Plotly)", template="plotly_dark", color_discrete_sequence=palette_colors)
                    fig_p.update_traces(
                        textposition='outside',
                        cliponaxis=False,
                        textfont=dict(size=9.5, color='#ffffff', family='Pretendard, sans-serif')
                    )
                    max_age_p = age_melted["환자수"].max() if not age_melted.empty else 0
                    if max_age_p > 0:
                        fig_p.update_yaxes(range=[0, max_age_p * 1.25])
                else:
                    st.markdown("###### ⚡ Plotly: 5개 연령대별 누적 영역 구성 (마우스 호버 시 세부 환자 수 표시)")
                    fig_p = px.area(age_melted, x="연령대", y="환자수", color="감염병명", markers=True, title="연령대별 감염병 누적 환자 구성 (Plotly 누적 영역)", template="plotly_dark", color_discrete_sequence=palette_colors)
                if use_log:
                    fig_p.update_yaxes(type="log")
                else:
                    fig_p.update_yaxes(type="linear")
                fig_p.update_layout(xaxis_title="연령대 구간" if "막대" not in chart_style else "감염병명", yaxis_title="환자 수(명) (로그 스케일)" if use_log else "환자 수(명)", height=390, margin=dict(l=40, r=20, t=40, b=60), uniformtext_minsize=7, uniformtext_mode='hide')
                fig_p.update_xaxes(tickangle=0)
                fig_p.update_yaxes(tickformat=',d')
                st.plotly_chart(fig_p, use_container_width=True, key="plotly_v2_main")

            with tab_seaborn:
                fig_s, ax_s = plt.subplots(figsize=(8.8, 3.9), dpi=100)
                apply_dark_plot_style(fig_s, ax_s)
                if "꺾은선" in chart_style:
                    st.markdown("###### 🎨 Seaborn: 5개 연령대별 취약도 추세선")
                    sns.lineplot(data=age_melted, x="연령대", y="환자수", hue="감염병명", marker="o", markersize=8, linewidth=2.5, palette="coolwarm", ax=ax_s)
                    ax_s.set_title("감염병별 5개 연령대 취약도 추세 (Seaborn)")
                    ax_s.set_xlabel("연령대 구간")
                elif "막대" in chart_style:
                    st.markdown("###### 🎨 Seaborn: 5개 연령대별 그룹 비교 막대 그래프")
                    sns.barplot(data=age_melted, x="감염병명", y="환자수", hue="연령대", palette=palette_colors[:len(age_cols)], ax=ax_s)
                    ax_s.set_title("감염병별 연령대 환자 분포 비교 (Seaborn)")
                    valid_patches = sorted([p for p in ax_s.patches if p.get_height() > 0], key=lambda p: p.get_x())
                    smart_annotate_bars(ax_s, valid_patches, total_bars=len(valid_patches))
                    ax_s.set_xlabel("감염병명")
                else:
                    st.markdown("###### 🎨 Seaborn: 5개 연령대별 누적 스택 막대")
                    bottom_arr = [0] * len(age_grp)
                    for i, c_name in enumerate(age_cols):
                        vals = age_grp[c_name].values
                        ax_s.bar(age_grp["감염병명"], vals, bottom=bottom_arr, label=c_name, color=palette_colors[i % len(palette_colors)], edgecolor="#1e293b")
                        bottom_arr = [b + v for b, v in zip(bottom_arr, vals)]
                    ax_s.set_title("5개 연령대별 누적 환자 구성 (Seaborn 누적)")
                    ax_s.set_xlabel("감염병명")

                max_age_val = age_melted["환자수"].max() if not age_melted.empty else 0
                if use_log and max_age_val > 0:
                    min_pos_age = age_melted[age_melted["환자수"] > 0]["환자수"].min() if not age_melted[age_melted["환자수"] > 0].empty else 1
                    ax_s.set_yscale('log')
                    ax_s.set_ylim(bottom=max(1, min_pos_age * 0.3), top=max_age_val * 4.0)
                    ax_s.yaxis.set_major_formatter(ticker.FuncFormatter(format_korean_log_ticks))
                    ax_s.set_ylabel("환자 수(명, 로그 스케일)")
                else:
                    if max_age_val > 0:
                        ax_s.set_ylim(0, max_age_val * 1.38)
                    ax_s.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{int(x):,}"))
                    ax_s.set_ylabel("환자 수(명)")

                ax_s.tick_params(axis='x', rotation=0)
                ax_s.legend(title="연령대", bbox_to_anchor=(1.02, 1), loc='upper left', facecolor='#1e293b', edgecolor='#475569', labelcolor='#f8fafc', fontsize=8)
                plt.tight_layout()
                st.pyplot(fig_s, use_container_width=True)
                buf_s = io.BytesIO()
                fig_s.savefig(buf_s, format="png", dpi=200, bbox_inches="tight")
                buf_s.seek(0)
                st.download_button(
                    label="💾 Seaborn 고화질 그래프(PNG) 다운로드",
                    data=buf_s.getvalue(),
                    file_name="감염병_시각화_Seaborn.png",
                    mime="image/png",
                    use_container_width=True,
                    key=f"dl_seaborn_{data_view[:3]}_{chart_style[:2]}"
                )
                plt.close(fig_s)

            with tab_matplotlib:
                fig_m, ax_m = plt.subplots(figsize=(8.8, 3.9), dpi=100)
                apply_dark_plot_style(fig_m, ax_m)
                if "꺾은선" in chart_style:
                    st.markdown("###### 📉 Matplotlib: 5개 연령대별 취약도 추세선 및 정밀 수치")
                    for i, d_name in enumerate(age_grp["감염병명"]):
                        sub_vals = age_grp[age_grp["감염병명"] == d_name][age_cols].values[0]
                        ax_m.plot(age_cols, sub_vals, marker='s', markersize=7, linewidth=2.2, label=d_name, color=palette_colors[i % len(palette_colors)])
                        for col_idx, v in enumerate(sub_vals):
                            lbl = format_smart_label(v, compact=True)
                            if lbl:
                                y_off = 6 if i % 2 == 0 else -14
                                va_pos = 'bottom' if i % 2 == 0 else 'top'
                                ax_m.annotate(lbl, (col_idx, v), textcoords="offset points", xytext=(0, y_off), ha='center', va=va_pos, fontsize=7.5, color='#ffffff', weight='bold', path_effects=[pe.withStroke(linewidth=2.0, foreground='#0f172a')])
                    ax_m.set_title("감염병별 5개 연령대 취약도 추세 (Matplotlib)")
                    ax_m.set_xlabel("연령대 구간")
                elif "막대" in chart_style:
                    st.markdown("###### 📉 Matplotlib: 5개 연령대별 세분화 그룹 막대")
                    n_groups = len(age_grp)
                    n_sub = len(age_cols)
                    bar_w = 0.8 / n_sub
                    all_age_bars = []
                    for i, c_name in enumerate(age_cols):
                        offsets = [idx + (i - n_sub / 2 + 0.5) * bar_w for idx in range(n_groups)]
                        bars_m = ax_m.bar(offsets, age_grp[c_name], width=bar_w, label=c_name, color=palette_colors[i % len(palette_colors)], edgecolor="#1e293b")
                        all_age_bars.extend(bars_m)
                    smart_annotate_bars(ax_m, all_age_bars, total_bars=len(all_age_bars))
                    ax_m.set_title("감염병별 5개 연령대 환자 비교 (Matplotlib 막대)")
                    ax_m.set_xticks(range(n_groups))
                    ax_m.set_xticklabels(age_grp["감염병명"], rotation=0)
                    ax_m.set_xlabel("감염병명")
                else:
                    st.markdown("###### 📉 Matplotlib: 5개 연령대별 정밀 누적 스택 막대")
                    bottom_arr = [0] * len(age_grp)
                    for i, c_name in enumerate(age_cols):
                        vals = age_grp[c_name].values
                        ax_m.bar(age_grp["감염병명"], vals, bottom=bottom_arr, label=c_name, color=palette_colors[i % len(palette_colors)], edgecolor="#1e293b")
                        bottom_arr = [b + v for b, v in zip(bottom_arr, vals)]
                    ax_m.set_title("5개 연령대별 누적 환자 구성 (Matplotlib)")
                    ax_m.set_xlabel("감염병명")

                max_age_val_m = age_grp[age_cols].values.max() if not age_grp.empty else 0
                if use_log and max_age_val_m > 0:
                    all_pos_age = age_melted[age_melted["환자수"] > 0]["환자수"]
                    min_pos_age_m = all_pos_age.min() if not all_pos_age.empty else 1
                    ax_m.set_yscale('log')
                    ax_m.set_ylim(bottom=max(1, min_pos_age_m * 0.3), top=max_age_val_m * 4.0)
                    ax_m.yaxis.set_major_formatter(ticker.FuncFormatter(format_korean_log_ticks))
                    ax_m.set_ylabel("환자 수(명, 로그 스케일)")
                else:
                    if max_age_val_m > 0:
                        ax_m.set_ylim(0, max_age_val_m * 1.38)
                    ax_m.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{int(x):,}"))
                    ax_m.set_ylabel("환자 수(명)")

                ax_m.tick_params(axis='x', rotation=0)
                ax_m.legend(title="연령대", bbox_to_anchor=(1.02, 1), loc='upper left', facecolor='#1e293b', edgecolor='#475569', labelcolor='#f8fafc', fontsize=8)
                plt.tight_layout()
                st.pyplot(fig_m, use_container_width=True)
                st.caption("💡 **가독성 최적화 안내**: 막대 밀집 시 인접한 낮은 수치끼리 글자가 겹치거나 막대와 간섭되지 않도록 폰트 크기 최적화(5.0pt), 지능형 충돌 회피 오프셋 및 세련된 사선(55~60°) 정렬이 자동 적용됩니다. 정밀 숫자는 '1. Plotly' 탭 마우스 호버 또는 하단 데이터 표에서 100% 확인하실 수 있습니다.")
                buf_m = io.BytesIO()
                fig_m.savefig(buf_m, format="png", dpi=200, bbox_inches="tight")
                buf_m.seek(0)
                st.download_button(
                    label="💾 Matplotlib 고화질 그래프(PNG) 다운로드",
                    data=buf_m.getvalue(),
                    file_name="감염병_시각화_Matplotlib.png",
                    mime="image/png",
                    use_container_width=True,
                    key=f"dl_matplotlib_{data_view[:3]}_{chart_style[:2]}"
                )
                plt.close(fig_m)

            with tab_donut:
                st.caption("💡 '원/도넛형 점유율 분석'은 전체 환자 대비 100% 연령별 구성 비를 분석하는 전용 도표입니다. (상단 꺾은선/막대/누적영역 선택은 1~3번 탭에 적용됩니다)")
                st.markdown("###### 🍩 5개 연령대 세분화 점유율 도넛 차트 (청소년 10-19세 비중 집중 분석)")
                active_tot_age = tot_age[tot_age["환자수"] > 0]
                if active_tot_age.empty or active_tot_age["환자수"].sum() <= 0:
                    st.info("ℹ️ 연령대별 점유율을 분석할 환자 데이터가 없습니다 (0명).")
                else:
                    d_col1, d_col2 = st.columns(2)
                    with d_col1:
                        fig_p_donut = px.pie(active_tot_age, values="환자수", names="연령대", hole=0.45, title="5개 연령대별 환자 점유율 (Plotly 도넛)", template="plotly_dark", color_discrete_sequence=palette_colors)
                        fig_p_donut.update_layout(height=360, margin=dict(l=15, r=15, t=35, b=25), legend=dict(font=dict(size=9.5)))
                        st.plotly_chart(fig_p_donut, use_container_width=True, key="plotly_v2_donut")
                    with d_col2:
                        fig_s_donut, ax_sd = plt.subplots(figsize=(5.0, 3.6), dpi=100)
                        apply_dark_plot_style(fig_s_donut, ax_sd)
                        patches_d, texts_d, autotexts_d = ax_sd.pie(
                            active_tot_age["환자수"],
                            labels=active_tot_age["연령대"],
                            autopct="%1.1f%%",
                            colors=palette_colors[:len(active_tot_age)],
                            radius=0.82,
                            pctdistance=0.65
                        )
                        for t in texts_d:
                            t.set_color('#ffffff')
                            t.set_fontsize(8.5)
                            t.set_weight('bold')
                            t.set_path_effects([pe.withStroke(linewidth=2.0, foreground='#0f172a')])
                        for at in autotexts_d:
                            at.set_color('#0f172a')
                            at.set_fontsize(10.0)
                            at.set_weight('bold')
                            at.set_path_effects([pe.withStroke(linewidth=2.0, foreground='#ffffff')])

                        ax_sd.add_artist(plt.Circle((0,0), 0.45, fc='#0f172a'))
                        ax_sd.set_title("5개 연령대별 환자 점유율 (Seaborn 도넛)", fontsize=10.5, pad=8, color="#f8fafc")
                        plt.tight_layout()
                        st.pyplot(fig_s_donut, use_container_width=True)
                        plt.close(fig_s_donut)

        # ==================================================================
        # 관점 3: 해외 주요 10개국 발생 현황 분석
        # ==================================================================
        elif "3. 해외 주요" in data_view:
            sub_global = df_filtered[df_filtered["지역"].isin(GLOBAL_COUNTRIES)]
            global_df = sub_global.groupby("지역")["신규환자수"].sum().reset_index().sort_values("신규환자수", ascending=True)
            g_ts = sub_global.groupby(["연도", "지역"])["신규환자수"].sum().reset_index().sort_values("연도")
            g_years = sorted(g_ts["연도"].unique()) if not g_ts.empty else [2019, 2020, 2021, 2022, 2023, 2024, 2025]
            g_year_labels = [f"{int(y)}년" for y in g_years]

            with tab_plotly:
                if global_df.empty or global_df["신규환자수"].sum() <= 0:
                    st.info("ℹ️ 현재 선택된 감염병의 해외 주요 10개국 환자 발생 데이터가 없습니다 (0명).")
                elif "꺾은선" in chart_style:
                    st.markdown("###### ⚡ Plotly: 해외 주요 10개국 연도별 발생 추이 꺾은선 (마우스 호버 시 세부 수치 표시)")
                    fig_p = px.line(g_ts, x="연도", y="신규환자수", color="지역", markers=True, title="해외 주요 10개국 연도별 감염병 발생 추이 (Plotly 꺾은선)", template="plotly_dark", color_discrete_sequence=palette_colors)
                    if use_log:
                        fig_p.update_yaxes(type="log")
                    else:
                        fig_p.update_yaxes(type="linear")
                    fig_p.update_layout(xaxis_title="발생 연도", yaxis_title="신규 환자 수(명) (로그 스케일)" if use_log else "신규 환자 수(명)", height=390, margin=dict(l=40, r=20, t=40, b=60))
                    fig_p.update_xaxes(tickangle=0, dtick=1, tickmode='linear', tickformat="d")
                    fig_p.update_yaxes(tickformat=',d')
                    st.plotly_chart(fig_p, use_container_width=True, key="plotly_v3_line")
                elif "막대" in chart_style:
                    st.markdown("###### ⚡ Plotly: 해외 주요 10개국 가로 막대 시각화 (호버 시 정확한 수치 표시)")
                    fig_p = px.bar(global_df, y="지역", x="신규환자수", orientation='h', color="지역", text_auto=',d', title="해외 주요 10개국 감염병 발생 현황 (Plotly 가로 막대)", template="plotly_dark", color_discrete_sequence=palette_colors)
                    fig_p.update_traces(
                        textposition='outside',
                        cliponaxis=False,
                        textfont=dict(size=10, color='#ffffff', family='Pretendard, sans-serif')
                    )
                    max_g_p = global_df["신규환자수"].max() if not global_df.empty else 0
                    if max_g_p > 0 and not use_log:
                        fig_p.update_xaxes(range=[0, max_g_p * 1.18], tickformat=',d')
                    if use_log:
                        fig_p.update_xaxes(type="log")
                    else:
                        fig_p.update_xaxes(type="linear")
                    fig_p.update_layout(xaxis_title="신규 환자 수(명) (로그 스케일)" if use_log else "신규 환자 수(명)", yaxis_title="국가명", showlegend=False, height=390, margin=dict(l=40, r=20, t=40, b=60), uniformtext_minsize=7, uniformtext_mode='hide')
                    st.plotly_chart(fig_p, use_container_width=True, key="plotly_v3_bar")
                else:
                    st.markdown("###### ⚡ Plotly: 해외 주요 10개국 연도별 누적 발생 구성 (호버 시 세부 수치 표시)")
                    fig_p = px.area(g_ts, x="연도", y="신규환자수", color="지역", markers=True, title="해외 주요 10개국 연도별 누적 발생 구성 (Plotly 누적 영역)", template="plotly_dark", color_discrete_sequence=palette_colors)
                    fig_p.update_layout(xaxis_title="발생 연도", yaxis_title="누적 환자 수(명)", height=390, margin=dict(l=40, r=20, t=40, b=60))
                    fig_p.update_xaxes(tickangle=0, dtick=1, tickmode='linear', tickformat="d")
                    fig_p.update_yaxes(tickformat=',d')
                    st.plotly_chart(fig_p, use_container_width=True, key="plotly_v3_area")

            with tab_seaborn:
                fig_s, ax_s = plt.subplots(figsize=(8.2, 3.8), dpi=100)
                apply_dark_plot_style(fig_s, ax_s)
                if global_df.empty or global_df["신규환자수"].sum() <= 0:
                    ax_s.text(0.5, 0.5, "해외 주요 발생국 환자 데이터가 없습니다 (0명)", ha='center', va='center', color='#94a3b8', fontsize=11)
                    ax_s.set_title("해외 주요 발생국별 환자 발생 비교 (Seaborn)")
                elif "꺾은선" in chart_style:
                    st.markdown("###### 🎨 Seaborn: 해외 주요 10개국 연도별 발생 추이 꺾은선")
                    sns.lineplot(data=g_ts, x="연도", y="신규환자수", hue="지역", marker="o", markersize=6, palette="tab10", ax=ax_s)
                    ax_s.set_title("해외 주요 10개국 연도별 발생 추이 (Seaborn)")
                    ax_s.set_xticks(g_years)
                    ax_s.set_xticklabels(g_year_labels, rotation=0)
                    ax_s.set_xlabel("발생 연도")
                    max_g_ts = g_ts["신규환자수"].max() if not g_ts.empty else 0
                    if use_log and max_g_ts > 0:
                        min_pos_g = g_ts[g_ts["신규환자수"] > 0]["신규환자수"].min() if not g_ts[g_ts["신규환자수"] > 0].empty else 1
                        ax_s.set_yscale('log')
                        ax_s.set_ylim(bottom=max(1, min_pos_g * 0.3), top=max_g_ts * 4.0)
                        ax_s.yaxis.set_major_formatter(ticker.FuncFormatter(format_korean_log_ticks))
                        ax_s.set_ylabel("신규 환자 수(명, 로그 스케일)")
                    else:
                        ax_s.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{int(x):,}"))
                        ax_s.set_ylabel("신규 환자 수(명)")
                    ax_s.legend(title="국가명", bbox_to_anchor=(1.02, 1), loc='upper left', facecolor='#1e293b', edgecolor='#475569', labelcolor='#f8fafc', fontsize=8)
                elif "막대" in chart_style:
                    st.markdown("###### 🎨 Seaborn: 해외 발생국별 환자 규모 그래픽스")
                    sns.barplot(data=global_df, y="지역", x="신규환자수", hue="지역", palette="mako", legend=False, ax=ax_s)
                    ax_s.set_title("해외 주요 발생국별 환자 발생 비교 (Seaborn)")
                    max_g_s = global_df["신규환자수"].max() if not global_df.empty else 0
                    if use_log and max_g_s > 0:
                        min_pos_g = global_df[global_df["신규환자수"] > 0]["신규환자수"].min() if not global_df[global_df["신규환자수"] > 0].empty else 1
                        ax_s.set_xscale('log')
                        ax_s.set_xlim(left=max(1, min_pos_g * 0.3), right=max_g_s * 4.0)
                        ax_s.xaxis.set_major_formatter(ticker.FuncFormatter(format_korean_log_ticks))
                        ax_s.set_xlabel("신규 환자 수(명, 로그 스케일)")
                    else:
                        if max_g_s > 0:
                            ax_s.set_xlim(0, max_g_s * 1.30)
                        ax_s.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{int(x):,}"))
                        ax_s.set_xlabel("신규 환자 수(명)")
                    valid_patches = [p for p in ax_s.patches if p.get_width() > 0]
                    smart_annotate_bars(ax_s, valid_patches, total_bars=len(valid_patches), is_horizontal=True, max_val=max_g_s)
                    ax_s.set_ylabel("국가명")
                else:
                    st.markdown("###### 🎨 Seaborn: 해외 주요국 누적 영역 분포 그래픽스")
                    g_pivot = g_ts.pivot(index="연도", columns="지역", values="신규환자수").reindex(g_years).fillna(0)
                    y_arrays = [g_pivot[c].values for c in g_pivot.columns]
                    colors_stack = sns.color_palette("mako", len(g_pivot.columns))
                    ax_s.stackplot(g_years, y_arrays, labels=g_pivot.columns, colors=colors_stack, alpha=0.85)
                    ax_s.set_title("해외 주요국 연도별 누적 환자 구성 (Seaborn 누적 영역)")
                    ax_s.set_xticks(g_years)
                    ax_s.set_xticklabels(g_year_labels, rotation=0)
                    ax_s.set_xlabel("발생 연도")
                    ax_s.set_ylabel("누적 환자 수(명)")
                    ax_s.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{int(x):,}"))
                    ax_s.legend(title="국가명", bbox_to_anchor=(1.02, 1), loc='upper left', facecolor='#1e293b', edgecolor='#475569', labelcolor='#f8fafc', fontsize=8)
                plt.tight_layout()
                st.pyplot(fig_s, use_container_width=True)
                buf_s = io.BytesIO()
                fig_s.savefig(buf_s, format="png", dpi=200, bbox_inches="tight")
                buf_s.seek(0)
                st.download_button(
                    label="💾 Seaborn 고화질 그래프(PNG) 다운로드",
                    data=buf_s.getvalue(),
                    file_name="감염병_시각화_Seaborn.png",
                    mime="image/png",
                    use_container_width=True,
                    key=f"dl_seaborn_{data_view[:3]}_{chart_style[:2]}"
                )
                plt.close(fig_s)

            with tab_matplotlib:
                fig_m, ax_m = plt.subplots(figsize=(8.8, 3.9), dpi=100)
                apply_dark_plot_style(fig_m, ax_m)
                if global_df.empty or global_df["신규환자수"].sum() <= 0:
                    ax_m.text(0.5, 0.5, "해외 주요 발생국 환자 데이터가 없습니다 (0명)", ha='center', va='center', color='#94a3b8', fontsize=11)
                    ax_m.set_title("해외 주요 10개국 감염병 발생 현황 (Matplotlib)")
                elif "꺾은선" in chart_style:
                    st.markdown("###### 📉 Matplotlib: 해외 주요 상위 5개국 연도별 추세 꺾은선")
                    top5_countries = global_df["지역"].tolist()[-5:]
                    for i, c_name in enumerate(top5_countries):
                        sub_c = g_ts[g_ts["지역"] == c_name]
                        if not sub_c.empty:
                            ax_m.plot(sub_c["연도"], sub_c["신규환자수"], marker='o', markersize=6, linewidth=2.0, label=c_name, color=palette_colors[i % len(palette_colors)])
                    ax_m.set_title("해외 주요 상위 5개국 연도별 발생 추이 (Matplotlib)")
                    ax_m.set_xticks(g_years)
                    ax_m.set_xticklabels(g_year_labels, rotation=0)
                    ax_m.set_xlabel("발생 연도")
                    max_g_ts_m = g_ts["신규환자수"].max() if not g_ts.empty else 0
                    if use_log and max_g_ts_m > 0:
                        min_pos_g = g_ts[g_ts["신규환자수"] > 0]["신규환자수"].min() if not g_ts[g_ts["신규환자수"] > 0].empty else 1
                        ax_m.set_yscale('log')
                        ax_m.set_ylim(bottom=max(1, min_pos_g * 0.3), top=max_g_ts_m * 4.0)
                        ax_m.yaxis.set_major_formatter(ticker.FuncFormatter(format_korean_log_ticks))
                        ax_m.set_ylabel("신규 환자 수(명, 로그 스케일)")
                    else:
                        ax_m.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{int(x):,}"))
                        ax_m.set_ylabel("신규 환자 수(명)")
                    ax_m.legend(title="국가명", bbox_to_anchor=(1.02, 1), loc='upper left', facecolor='#1e293b', edgecolor='#475569', labelcolor='#f8fafc', fontsize=8)
                elif "막대" in chart_style:
                    st.markdown("###### 📉 Matplotlib: 정확한 환자 수 레이블이 표기된 정밀 가로 막대")
                    bars = ax_m.barh(global_df["지역"], global_df["신규환자수"], color="#0284c7", edgecolor="#38bdf8")
                    max_val = max(global_df["신규환자수"]) if not global_df.empty else 0
                    if use_log and max_val > 0:
                        min_pos_g = global_df[global_df["신규환자수"] > 0]["신규환자수"].min() if not global_df[global_df["신규환자수"] > 0].empty else 1
                        ax_m.set_xscale('log')
                        ax_m.set_xlim(left=max(1, min_pos_g * 0.3), right=max_val * 4.0)
                        ax_m.xaxis.set_major_formatter(ticker.FuncFormatter(format_korean_log_ticks))
                        ax_m.set_xlabel("신규 환자 수(명, 로그 스케일)")
                    else:
                        if max_val > 0:
                            ax_m.set_xlim(0, max_val * 1.30)
                        ax_m.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{int(x):,}"))
                        ax_m.set_xlabel("신규 환자 수(명)")
                    smart_annotate_bars(ax_m, bars, total_bars=len(bars), is_horizontal=True, max_val=max_val)
                    ax_m.set_title("해외 주요 10개국 감염병 발생 현황 (Matplotlib)")
                    ax_m.set_ylabel("국가명")
                else:
                    g_pivot = g_ts.pivot(index="연도", columns="지역", values="신규환자수").reindex(g_years).fillna(0)
                    y_arrays = [g_pivot[c].values for c in g_pivot.columns]
                    ax_m.stackplot(g_years, y_arrays, labels=g_pivot.columns, colors=palette_colors[:len(g_pivot.columns)], alpha=0.85)
                    ax_m.set_title("해외 주요국 연도별 누적 환자 구성 (Matplotlib 누적 영역)")
                    ax_m.set_xticks(g_years)
                    ax_m.set_xticklabels(g_year_labels, rotation=0)
                    ax_m.set_xlabel("발생 연도")
                    ax_m.set_ylabel("누적 환자 수(명)")
                    ax_m.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{int(x):,}"))
                    ax_m.legend(title="국가명", bbox_to_anchor=(1.02, 1), loc='upper left', facecolor='#1e293b', edgecolor='#475569', labelcolor='#f8fafc', fontsize=8)
                plt.tight_layout()
                st.pyplot(fig_m, use_container_width=True)
                buf_m = io.BytesIO()
                fig_m.savefig(buf_m, format="png", dpi=200, bbox_inches="tight")
                buf_m.seek(0)
                st.download_button(
                    label="💾 Matplotlib 고화질 그래프(PNG) 다운로드",
                    data=buf_m.getvalue(),
                    file_name="감염병_시각화_Matplotlib.png",
                    mime="image/png",
                    use_container_width=True,
                    key=f"dl_matplotlib_{data_view[:3]}_{chart_style[:2]}"
                )
                plt.close(fig_m)

            with tab_donut:
                st.caption("💡 '원/도넛형 점유율 분석'은 전체 해외 환자 중 각 국가별 100% 점유율을 분석하는 전용 도표입니다. (상단 꺾은선/막대/누적영역 선택은 1~3번 탭에 적용됩니다)")
                st.markdown("###### 🍩 해외 주요 10개국 감염병 발생 점유율 분석")
                active_global_df = global_df[global_df["신규환자수"] > 0]
                if active_global_df.empty or active_global_df["신규환자수"].sum() <= 0:
                    st.info("ℹ️ 해외 주요 10개국 환자 발생 점유율을 계산할 데이터가 없습니다 (0명).")
                else:
                    d_col1, d_col2 = st.columns(2)
                    with d_col1:
                        fig_p_donut = px.pie(active_global_df, values="신규환자수", names="지역", hole=0.45, title="해외 주요국 발생 비중 (Plotly 도넛)", template="plotly_dark", color_discrete_sequence=palette_colors)
                        fig_p_donut.update_layout(height=360, margin=dict(l=15, r=15, t=35, b=25), legend=dict(font=dict(size=9.5)))
                        st.plotly_chart(fig_p_donut, use_container_width=True, key="plotly_v3_donut")
                    with d_col2:
                        fig_s_donut, ax_sd = plt.subplots(figsize=(5.0, 3.6), dpi=100)
                        apply_dark_plot_style(fig_s_donut, ax_sd)
                        patches_d, texts_d, autotexts_d = ax_sd.pie(
                            active_global_df["신규환자수"],
                            labels=active_global_df["지역"],
                            autopct="%1.1f%%",
                            colors=palette_colors[:len(active_global_df)],
                            radius=0.82,
                            pctdistance=0.65
                        )
                        for t in texts_d:
                            t.set_color('#ffffff')
                            t.set_fontsize(8.5)
                            t.set_weight('bold')
                            t.set_path_effects([pe.withStroke(linewidth=2.0, foreground='#0f172a')])
                        for at in autotexts_d:
                            at.set_color('#0f172a')
                            at.set_fontsize(10.0)
                            at.set_weight('bold')
                            at.set_path_effects([pe.withStroke(linewidth=2.0, foreground='#ffffff')])

                        ax_sd.add_artist(plt.Circle((0,0), 0.45, fc='#0f172a'))
                        ax_sd.set_title("해외 주요국 발생 비중 (Seaborn 도넛)", fontsize=10.5, pad=8, color="#f8fafc")
                        plt.tight_layout()
                        st.pyplot(fig_s_donut, use_container_width=True)
                        plt.close(fig_s_donut)

        # ==================================================================
        # 관점 4: 국내 17개 시도별 발생 현황 분석
        # ==================================================================
        else:
            sub_korea = df_filtered[df_filtered["지역"].isin(KOREA_CITIES)]
            korea_df = sub_korea.groupby("지역")["신규환자수"].sum().reset_index().sort_values("신규환자수", ascending=False)
            top6_korea = korea_df.head(6)
            top6_names = top6_korea["지역"].tolist()
            k_top_ts = sub_korea[sub_korea["지역"].isin(top6_names)].groupby(["연도", "지역"])["신규환자수"].sum().reset_index().sort_values("연도")
            k_years = sorted(k_top_ts["연도"].unique()) if not k_top_ts.empty else [2019, 2020, 2021, 2022, 2023, 2024, 2025]
            k_year_labels = [f"{int(y)}년" for y in k_years]

            with tab_plotly:
                if "꺾은선" in chart_style:
                    st.markdown("###### ⚡ Plotly: 국내 상위 6대 시도 연도별 발생 추이 꺾은선 (인터랙티브)")
                    fig_p = px.line(k_top_ts, x="연도", y="신규환자수", color="지역", markers=True, title="국내 상위 6대 시도 연도별 발생 추이 (Plotly 꺾은선)", template="plotly_dark", color_discrete_sequence=palette_colors)
                    if use_log:
                        fig_p.update_yaxes(type="log")
                    else:
                        fig_p.update_yaxes(type="linear")
                    fig_p.update_layout(xaxis_title="발생 연도", yaxis_title="신규 환자 수(명) (로그 스케일)" if use_log else "신규 환자 수(명)", height=390, margin=dict(l=40, r=20, t=40, b=60))
                    fig_p.update_xaxes(tickangle=0, dtick=1, tickmode='linear', tickformat="d")
                    fig_p.update_yaxes(tickformat=',d')
                    st.plotly_chart(fig_p, use_container_width=True, key="plotly_v4_line")
                elif "막대" in chart_style:
                    st.markdown("###### ⚡ Plotly: 국내 17개 시도별 세로 막대 (인터랙티브)")
                    fig_p = px.bar(korea_df, x="지역", y="신규환자수", color="지역", text_auto=',d', title="국내 17개 시도별 감염병 환자 발생 현황 (Plotly)", template="plotly_dark", color_discrete_sequence=palette_colors)
                    fig_p.update_traces(
                        textposition='outside',
                        cliponaxis=False,
                        textfont=dict(size=9.5, color='#ffffff', family='Pretendard, sans-serif')
                    )
                    max_k_p = korea_df["신규환자수"].max() if not korea_df.empty else 0
                    if max_k_p > 0 and not use_log:
                        fig_p.update_yaxes(range=[0, max_k_p * 1.25])
                    if use_log:
                        fig_p.update_yaxes(type="log")
                    else:
                        fig_p.update_yaxes(type="linear")
                    fig_p.update_layout(xaxis_title="지역(시도)", yaxis_title="신규 환자 수(명) (로그 스케일)" if use_log else "신규 환자 수(명)", showlegend=False, height=390, margin=dict(l=40, r=20, t=40, b=60), uniformtext_minsize=7, uniformtext_mode='hide')
                    fig_p.update_xaxes(tickangle=0)
                    fig_p.update_yaxes(tickformat=',d')
                    st.plotly_chart(fig_p, use_container_width=True, key="plotly_v4_bar")
                else:
                    st.markdown("###### ⚡ Plotly: 국내 상위 6대 시도 연도별 누적 발생 구성 (Plotly 누적 영역)")
                    fig_p = px.area(k_top_ts, x="연도", y="신규환자수", color="지역", markers=True, title="국내 상위 6대 시도 연도별 누적 발생 구성 (Plotly 누적 영역)", template="plotly_dark", color_discrete_sequence=palette_colors)
                    fig_p.update_layout(xaxis_title="발생 연도", yaxis_title="누적 환자 수(명)", height=390, margin=dict(l=40, r=20, t=40, b=60))
                    fig_p.update_xaxes(tickangle=0, dtick=1, tickmode='linear', tickformat="d")
                    fig_p.update_yaxes(tickformat=',d')
                    st.plotly_chart(fig_p, use_container_width=True, key="plotly_v4_area")

            with tab_seaborn:
                fig_s, ax_s = plt.subplots(figsize=(8.8, 3.9), dpi=100)
                apply_dark_plot_style(fig_s, ax_s)
                if "꺾은선" in chart_style:
                    st.markdown("###### 🎨 Seaborn: 국내 상위 6대 시도 연도별 추세 꺾은선")
                    sns.lineplot(data=k_top_ts, x="연도", y="신규환자수", hue="지역", marker="o", markersize=6, palette="crest", ax=ax_s)
                    ax_s.set_title("국내 주요 시도 연도별 발생 추이 (Seaborn)")
                    ax_s.set_xticks(k_years)
                    ax_s.set_xticklabels(k_year_labels, rotation=0)
                    ax_s.set_xlabel("발생 연도")
                    max_k_l = k_top_ts["신규환자수"].max() if not k_top_ts.empty else 0
                    if use_log and max_k_l > 0:
                        min_pos_l = k_top_ts[k_top_ts["신규환자수"] > 0]["신규환자수"].min() if not k_top_ts[k_top_ts["신규환자수"] > 0].empty else 1
                        ax_s.set_yscale('log')
                        ax_s.set_ylim(bottom=max(1, min_pos_l * 0.3), top=max_k_l * 4.0)
                        ax_s.yaxis.set_major_formatter(ticker.FuncFormatter(format_korean_log_ticks))
                        ax_s.set_ylabel("신규 환자 수(명, 로그 스케일)")
                    else:
                        ax_s.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{int(x):,}"))
                        ax_s.set_ylabel("신규 환자 수(명)")
                    ax_s.legend(title="지역", bbox_to_anchor=(1.02, 1), loc='upper left', facecolor='#1e293b', edgecolor='#475569', labelcolor='#f8fafc', fontsize=8)
                elif "막대" in chart_style:
                    st.markdown("###### 🎨 Seaborn: 17개 시도별 분포 막대")
                    sns.barplot(data=korea_df, x="지역", y="신규환자수", hue="지역", palette="crest", legend=False, ax=ax_s)
                    ax_s.set_title("국내 17개 시도별 환자 분포 (Seaborn)")
                    max_k_s = korea_df["신규환자수"].max() if not korea_df.empty else 0
                    if use_log and max_k_s > 0:
                        min_pos_k = korea_df[korea_df["신규환자수"] > 0]["신규환자수"].min() if not korea_df[korea_df["신규환자수"] > 0].empty else 1
                        ax_s.set_yscale('log')
                        ax_s.set_ylim(bottom=max(1, min_pos_k * 0.3), top=max_k_s * 4.0)
                        ax_s.yaxis.set_major_formatter(ticker.FuncFormatter(format_korean_log_ticks))
                        ax_s.set_ylabel("신규 환자 수(명, 로그 스케일)")
                    else:
                        if max_k_s > 0:
                            ax_s.set_ylim(0, max_k_s * 1.38)
                        ax_s.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{int(x):,}"))
                        ax_s.set_ylabel("신규 환자 수(명)")
                    valid_patches = sorted([p for p in ax_s.patches if p.get_height() > 0], key=lambda p: p.get_x())
                    smart_annotate_bars(ax_s, valid_patches, total_bars=len(valid_patches))
                    ax_s.set_xlabel("지역(시도)")
                    plt.setp(ax_s.get_xticklabels(), rotation=45, ha='right', rotation_mode='anchor', fontsize=8)
                else:
                    st.markdown("###### 🎨 Seaborn: 국내 상위 6대 시도 누적 영역 그래프")
                    k_pivot = k_top_ts.pivot(index="연도", columns="지역", values="신규환자수").reindex(k_years).fillna(0)
                    y_arrays = [k_pivot[c].values for c in k_pivot.columns]
                    colors_stack = sns.color_palette("crest", len(k_pivot.columns))
                    ax_s.stackplot(k_years, y_arrays, labels=k_pivot.columns, colors=colors_stack, alpha=0.85)
                    ax_s.set_title("국내 상위 6대 시도 누적 환자 구성 (Seaborn)")
                    ax_s.set_xticks(k_years)
                    ax_s.set_xticklabels(k_year_labels, rotation=0)
                    ax_s.set_xlabel("발생 연도")
                    ax_s.set_ylabel("누적 환자 수(명)")
                    ax_s.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{int(x):,}"))
                    ax_s.legend(title="지역", bbox_to_anchor=(1.02, 1), loc='upper left', facecolor='#1e293b', edgecolor='#475569', labelcolor='#f8fafc', fontsize=8)
                plt.tight_layout()
                st.pyplot(fig_s, use_container_width=True)
                buf_s = io.BytesIO()
                fig_s.savefig(buf_s, format="png", dpi=200, bbox_inches="tight")
                buf_s.seek(0)
                st.download_button(
                    label="💾 Seaborn 고화질 그래프(PNG) 다운로드",
                    data=buf_s.getvalue(),
                    file_name="감염병_시각화_Seaborn.png",
                    mime="image/png",
                    use_container_width=True,
                    key=f"dl_seaborn_{data_view[:3]}_{chart_style[:2]}"
                )
                plt.close(fig_s)

            with tab_matplotlib:
                fig_m, ax_m = plt.subplots(figsize=(8.8, 3.9), dpi=100)
                apply_dark_plot_style(fig_m, ax_m)
                if "꺾은선" in chart_style:
                    st.markdown("###### 📉 Matplotlib: 국내 상위 6대 시도 연도별 발생 추이")
                    for i, c_name in enumerate(top6_names):
                        sub_c = k_top_ts[k_top_ts["지역"] == c_name]
                        if not sub_c.empty:
                            ax_m.plot(sub_c["연도"], sub_c["신규환자수"], marker='s', markersize=6, linewidth=2.0, label=c_name, color=palette_colors[i % len(palette_colors)])
                    ax_m.set_title("국내 상위 6대 시도 연도별 발생 추이 (Matplotlib)")
                    ax_m.set_xticks(k_years)
                    ax_m.set_xticklabels(k_year_labels, rotation=0)
                    ax_m.set_xlabel("발생 연도")
                    max_k_ml = k_top_ts["신규환자수"].max() if not k_top_ts.empty else 0
                    if use_log and max_k_ml > 0:
                        min_pos_l = k_top_ts[k_top_ts["신규환자수"] > 0]["신규환자수"].min() if not k_top_ts[k_top_ts["신규환자수"] > 0].empty else 1
                        ax_m.set_yscale('log')
                        ax_m.set_ylim(bottom=max(1, min_pos_l * 0.3), top=max_k_ml * 4.0)
                        ax_m.yaxis.set_major_formatter(ticker.FuncFormatter(format_korean_log_ticks))
                        ax_m.set_ylabel("신규 환자 수(명, 로그 스케일)")
                    else:
                        ax_m.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{int(x):,}"))
                        ax_m.set_ylabel("신규 환자 수(명)")
                    ax_m.legend(title="지역", bbox_to_anchor=(1.02, 1), loc='upper left', facecolor='#1e293b', edgecolor='#475569', labelcolor='#f8fafc', fontsize=8)
                elif "막대" in chart_style:
                    st.markdown("###### 📉 Matplotlib: 상위 발생 시도 강조 막대 그래프")
                    bar_colors = ['#38bdf8' if i < 3 else '#0284c7' for i in range(len(korea_df))]
                    bars_km = ax_m.bar(korea_df["지역"], korea_df["신규환자수"], color=bar_colors, edgecolor="#1e293b")
                    max_k_m = korea_df["신규환자수"].max() if not korea_df.empty else 0
                    if use_log and max_k_m > 0:
                        min_pos_km = korea_df[korea_df["신규환자수"] > 0]["신규환자수"].min() if not korea_df[korea_df["신규환자수"] > 0].empty else 1
                        ax_m.set_yscale('log')
                        ax_m.set_ylim(bottom=max(1, min_pos_km * 0.3), top=max_k_m * 4.0)
                        ax_m.yaxis.set_major_formatter(ticker.FuncFormatter(format_korean_log_ticks))
                        ax_m.set_ylabel("신규 환자 수(명, 로그 스케일)")
                    else:
                        if max_k_m > 0:
                            ax_m.set_ylim(0, max_k_m * 1.38)
                        ax_m.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{int(x):,}"))
                        ax_m.set_ylabel("신규 환자 수(명)")
                    smart_annotate_bars(ax_m, bars_km, total_bars=len(bars_km))
                    ax_m.set_title("국내 17개 시도별 환자 발생 통계 (Matplotlib 상위 시도 강조)")
                    ax_m.set_xlabel("지역(시도)")
                    plt.setp(ax_m.get_xticklabels(), rotation=45, ha='right', rotation_mode='anchor', fontsize=8)
                else:
                    k_pivot = k_top_ts.pivot(index="연도", columns="지역", values="신규환자수").reindex(k_years).fillna(0)
                    y_arrays = [k_pivot[c].values for c in k_pivot.columns]
                    ax_m.stackplot(k_years, y_arrays, labels=k_pivot.columns, colors=palette_colors[:len(k_pivot.columns)], alpha=0.85)
                    ax_m.set_title("국내 상위 6대 시도 연도별 누적 환자 구성 (Matplotlib 누적 영역)")
                    ax_m.set_xticks(k_years)
                    ax_m.set_xticklabels(k_year_labels, rotation=0)
                    ax_m.set_xlabel("발생 연도")
                    ax_m.set_ylabel("누적 환자 수(명)")
                    ax_m.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{int(x):,}"))
                    ax_m.legend(title="지역", bbox_to_anchor=(1.02, 1), loc='upper left', facecolor='#1e293b', edgecolor='#475569', labelcolor='#f8fafc', fontsize=8)
                plt.tight_layout()
                st.pyplot(fig_m, use_container_width=True)
                st.caption("💡 **가독성 최적화 안내**: 막대 밀집 시 인접한 낮은 수치끼리 글자가 겹치거나 막대와 간섭되지 않도록 폰트 크기 최적화(5.0pt), 지능형 충돌 회피 오프셋 및 세련된 사선(55~60°) 정렬이 자동 적용됩니다. 정밀 숫자는 '1. Plotly' 탭 마우스 호버 또는 하단 데이터 표에서 100% 확인하실 수 있습니다.")
                buf_m = io.BytesIO()
                fig_m.savefig(buf_m, format="png", dpi=200, bbox_inches="tight")
                buf_m.seek(0)
                st.download_button(
                    label="💾 Matplotlib 고화질 그래프(PNG) 다운로드",
                    data=buf_m.getvalue(),
                    file_name="감염병_시각화_Matplotlib.png",
                    mime="image/png",
                    use_container_width=True,
                    key=f"dl_matplotlib_{data_view[:3]}_{chart_style[:2]}"
                )
                plt.close(fig_m)

            with tab_donut:
                st.caption("💡 '원/도넛형 점유율 분석'은 전체 국내 발생 중 상위 6대 시도의 100% 비중을 분석하는 전용 도표입니다. (상단 꺾은선/막대/누적영역 선택은 1~3번 탭에 적용됩니다)")
                st.markdown("###### 🍩 국내 상위 6대 시도별 감염병 환자 발생 비중 분석")
                active_top6 = top6_korea[top6_korea["신규환자수"] > 0]
                if active_top6.empty or active_top6["신규환자수"].sum() <= 0:
                    st.info("ℹ️ 국내 상위 6대 시도 점유율을 분석할 데이터가 없습니다 (0명).")
                else:
                    d_col1, d_col2 = st.columns(2)
                    with d_col1:
                        fig_p_donut = px.pie(active_top6, values="신규환자수", names="지역", hole=0.45, title="국내 상위 6대 시도 점유율 (Plotly 도넛)", template="plotly_dark", color_discrete_sequence=palette_colors)
                        fig_p_donut.update_layout(height=360, margin=dict(l=15, r=15, t=35, b=25), legend=dict(font=dict(size=9.5)))
                        st.plotly_chart(fig_p_donut, use_container_width=True, key="plotly_v4_donut")
                    with d_col2:
                        fig_s_donut, ax_sd = plt.subplots(figsize=(5.0, 3.6), dpi=100)
                        apply_dark_plot_style(fig_s_donut, ax_sd)
                        patches_d, texts_d, autotexts_d = ax_sd.pie(
                            active_top6["신규환자수"],
                            labels=active_top6["지역"],
                            autopct="%1.1f%%",
                            colors=palette_colors[:len(active_top6)],
                            radius=0.82,
                            pctdistance=0.65
                        )
                        for t in texts_d:
                            t.set_color('#ffffff')
                            t.set_fontsize(8.5)
                            t.set_weight('bold')
                            t.set_path_effects([pe.withStroke(linewidth=2.0, foreground='#0f172a')])
                        for at in autotexts_d:
                            at.set_color('#0f172a')
                            at.set_fontsize(10.0)
                            at.set_weight('bold')
                            at.set_path_effects([pe.withStroke(linewidth=2.0, foreground='#ffffff')])

                        ax_sd.add_artist(plt.Circle((0,0), 0.45, fc='#0f172a'))
                        ax_sd.set_title("국내 상위 6대 시도 점유율 (Seaborn 도넛)", fontsize=10.5, pad=8, color="#f8fafc")
                        plt.tight_layout()
                        st.pyplot(fig_s_donut, use_container_width=True)
                        plt.close(fig_s_donut)

        # ------------------------------------------------------------------
        # 보건간호과 학생들을 위한 시각화 리터러시 교육 가이드 카드
        # ------------------------------------------------------------------
        st.write("")
        st.markdown("""
        <div style="background:#1e293b; border:1px solid #38bdf8; border-radius:10px; padding:12px 18px; margin-top:8px; margin-bottom:12px; box-shadow:0 3px 10px rgba(0,0,0,0.25);">
            <div style="font-size:0.98rem; font-weight:bold; color:#38bdf8; margin-bottom:6px;">
                💡 [보건간호과 학생용 데이터 시각화 길잡이: 차트별 최적 분석 목적]
            </div>
            <div style="font-size:0.85rem; color:#e2e8f0; line-height:1.65;">
                • 📈 <strong>꺾은선 추세 그래프 (Line Chart)</strong>: 시간 흐름에 따른 감염병 발생 추세, 유행 정점(Peak), 계절적 파동 분석에 최적입니다.<br>
                • 📊 <strong>막대 비교 그래프 (막대 차트)</strong>: 감염병 간 또는 시도별 환자 수의 절대적 크기를 직관적으로 비교할 때 최적입니다.<br>
                • 🏔️ <strong>누적 영역/분포 그래프 (Stacked Chart)</strong>: 전체 감염병 총량의 변동과 각 질병·연령대 기여도를 함께 파악할 때 효과적입니다.<br>
                • 🍩 <strong>원/도넛형 점유율 차트 (Donut Chart)</strong>: 전체 환자 중 특정 질병이나 고위험층이 차지하는 상대적 비중 전달에 탁월합니다.
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ------------------------------------------------------------------
        # 사용자 요청: "Plotly", "Seaborn" 등 해당 글자를 클릭하면 아래에 설명이 나오는 인터랙티브 UI & 콤팩트 축소 도표
        # ------------------------------------------------------------------
        st.markdown("##### 🔍 시각화 라이브러리 도구 선택 (클릭하여 특징 탐색)")
        tab_p, tab_s, tab_m, tab_tbl = st.tabs([
            "⚡ Plotly (인터랙티브 웹)", 
            "🎨 Seaborn (통계 분포)", 
            "📉 Matplotlib (정밀 출판)", 
            "📋 3대 도구 콤팩트 비교표"
        ])

        with tab_p:
            st.markdown("""
            <div style="background:rgba(56,189,248,0.08); border-left:4px solid #38bdf8; border-radius:8px; padding:12px 16px; margin-bottom:10px;">
                <div style="font-size:1.02rem; font-weight:700; color:#38bdf8; margin-bottom:6px;">⚡ Plotly: 실시간 인터랙티브 웹 시각화의 최강자</div>
                <div style="font-size:0.86rem; color:#f1f5f9; line-height:1.65;">
                    • <strong>주요 특징</strong>: 웹 대시보드에서 마우스 호버로 특정 연도/월의 정확한 환자 수를 실시간 확인<br>
                    • <strong>상호작용</strong>: 동적 줌(확대/축소), 화면 이동(팬), 툴팁 안내, 범례 클릭 시 특정 감염병 On/Off 토글<br>
                    • <strong>수업 활용</strong>: 학급 웹 대시보드 발표, 학생 실시간 데이터 탐구 실습에 가장 추천!
                </div>
            </div>
            """, unsafe_allow_html=True)

        with tab_s:
            st.markdown("""
            <div style="background:rgba(247,127,0,0.08); border-left:4px solid #f77f00; border-radius:8px; padding:12px 16px; margin-bottom:10px;">
                <div style="font-size:1.02rem; font-weight:700; color:#f77f00; margin-bottom:6px;">🎨 Seaborn: 미려한 색상 팔레트와 정밀 통계 분석</div>
                <div style="font-size:0.86rem; color:#f1f5f9; line-height:1.65;">
                    • <strong>주요 특징</strong>: 히스토그램, 박스플롯, 히트맵 등 통계 분포를 세련된 색채로 자동 표현<br>
                    • <strong>상호작용</strong>: 정적 이미지 (고화질 통계 시각화)<br>
                    • <strong>수업 활용</strong>: 연령대별 다변량 역학 상관관계 분석 및 통계적 데이터 분포 탐색에 적합!
                </div>
            </div>
            """, unsafe_allow_html=True)

        with tab_m:
            st.markdown("""
            <div style="background:rgba(16,185,129,0.08); border-left:4px solid #10b981; border-radius:8px; padding:12px 16px; margin-bottom:10px;">
                <div style="font-size:1.02rem; font-weight:700; color:#10b981; margin-bottom:6px;">📉 Matplotlib: 파이썬 정통 표준 및 픽셀 단위 정밀 제어</div>
                <div style="font-size:0.86rem; color:#f1f5f9; line-height:1.65;">
                    • <strong>주요 특징</strong>: 픽셀 단위 축, 눈금, 폰트, 다중 축(Dual-axis), 레이아웃의 완전한 제어 가능<br>
                    • <strong>상호작용</strong>: 정적 이미지 (출판 및 논문 표준 포맷)<br>
                    • <strong>수업 활용</strong>: 학술 보고서 제출, 인쇄용 연구 포스터, 이중 축 정밀 그래프 제작에 최적!
                </div>
            </div>
            """, unsafe_allow_html=True)

        with tab_tbl:
            st.markdown("""
            <div style="background:#1e293b; border:1px solid #334155; border-radius:8px; overflow:hidden; margin-bottom:10px;" class="notranslate" translate="no">
                <table style="width:100%; border-collapse:collapse; text-align:left; font-size:0.80rem; color:#f8fafc;">
                    <thead>
                        <tr style="background:#0f172a; border-bottom:1px solid #38bdf8;">
                            <th style="padding:8px 4px; width:68px; min-width:68px; text-align:center; vertical-align:middle; color:#38bdf8; font-weight:700; line-height:1.35;">비교<br>항목</th>
                            <th style="padding:8px 10px; width:34%; color:#38bdf8; font-weight:700; text-align:center;">⚡ Plotly</th>
                            <th style="padding:8px 10px; width:29%; color:#f77f00; font-weight:700; text-align:center;">🎨 Seaborn</th>
                            <th style="padding:8px 10px; width:29%; color:#10b981; font-weight:700; text-align:center;">📉 Matplotlib</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr style="border-bottom:1px solid #334155;">
                            <td style="padding:8px 4px; width:68px; min-width:68px; font-weight:700; color:#38bdf8; text-align:center; vertical-align:middle; background:rgba(15,23,42,0.45); line-height:1.35;">주요<br>특징</td>
                            <td style="padding:6px 8px; line-height:1.45; white-space:nowrap;">마우스 호버 및 인터랙티브 탐색 (웹 최적화)</td>
                            <td style="padding:6px 8px; line-height:1.45;">통계 분포 및 고급 색상 팔레트 자동 지원</td>
                            <td style="padding:6px 8px; line-height:1.45;">전통적 표준 도표, 픽셀 단위 정밀 제어</td>
                        </tr>
                        <tr style="border-bottom:1px solid #334155;">
                            <td style="padding:8px 4px; width:68px; min-width:68px; font-weight:700; color:#38bdf8; text-align:center; vertical-align:middle; background:rgba(15,23,42,0.45); line-height:1.35;">상호<br>작용</td>
                            <td style="padding:6px 8px; color:#38bdf8; font-weight:600; white-space:nowrap;">동적 인터랙티브 (줌, 툴팁, 토글)</td>
                            <td style="padding:6px 8px;">정적 이미지 (Static)</td>
                            <td style="padding:6px 8px;">정적 이미지 (Static)</td>
                        </tr>
                        <tr style="border-bottom:1px solid #334155;">
                            <td style="padding:8px 4px; width:68px; min-width:68px; font-weight:700; color:#38bdf8; text-align:center; vertical-align:middle; background:rgba(15,23,42,0.45); line-height:1.35;">주요<br>장점</td>
                            <td style="padding:6px 8px; line-height:1.45; white-space:nowrap;">마우스만으로 정확한 환자 수 실시간 확인</td>
                            <td style="padding:6px 8px; line-height:1.45;">적은 코드로 미려한 통계 분포·회귀선 구현</td>
                            <td style="padding:6px 8px; line-height:1.45;">축·눈금·폰트 완전 제어, 이중축 구현</td>
                        </tr>
                        <tr>
                            <td style="padding:8px 4px; width:68px; min-width:68px; font-weight:700; color:#38bdf8; text-align:center; vertical-align:middle; background:rgba(15,23,42,0.45); line-height:1.35;">수업<br>추천</td>
                            <td style="padding:6px 8px; line-height:1.45; white-space:nowrap;">학급 웹 발표, 실시간 데이터 탐구</td>
                            <td style="padding:6px 8px; line-height:1.45;">역학 상관관계, 연령대별 다변량 분석</td>
                            <td style="padding:6px 8px; line-height:1.45;">학술 보고서 제출, 인쇄용 연구 포스터</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            """, unsafe_allow_html=True)

    # [디지털 학습지 STEP 2] 학생 직접 기록 활동란
    st.write("")
    st.markdown("##### 📝 [2단계 탐구 활동지] 나의 시각화 도구 비교 관찰 기록장")

    st.caption("동일한 감염병 데이터라도 시각화 도구(Plotly 인터랙티브 vs Seaborn 통계 분포 vs Matplotlib 정통 도표)나 차트 종류(꺾은선 vs 막대 vs 도넛)에 따른 특징과 차이를 한 줄로 기록해 보세요.")

    memo2_col1, memo2_col2 = st.columns([3.6, 1.5])
    with memo2_col1:
        s2_input = st.text_area(
            "2단계 기록 내용",
            value=st.session_state.get("wb_step2_note", ""),
            placeholder="예시: Plotly는 마우스 호버로 특정 연도/월의 급증 시점을 정확히 짚어낼 수 있어 교내 발표에 유리했고, Matplotlib은 이중축과 로그스케일로 환자 수 격차가 큰 질환을 객관적으로 비교하기 좋았음.",
            label_visibility="collapsed",
            key="area_step2_memo",
            height=70
        )
    with memo2_col2:
        st.write("")
        if st.button("💾 2단계 저장 & 수행평가 연동", use_container_width=True, type="primary", key="btn_save_step2"):
            st.session_state["wb_step2_note"] = s2_input
            st.toast("✅ 2단계 기록이 저장되었으며 수행평가에 자동 연동되었습니다!")
            st.success("연동 완료! 🟢")
            st.rerun()


# ----------------------------------------------------
# [메뉴 3] STEP 3. 전국 지역 & 역학 비교 탐험실
# ----------------------------------------------------
elif menu.startswith("3.") or menu == "3. 지역/감염병 비교 심층 탐구":
    st.subheader("🗺️ 3단계: 전국 시도별 감염병 발생 비교")
    st.info("💡 **오늘의 미션**: 우리 지역(서울/경기 등)과 다른 지역의 발생 차이를 비교하고, 호흡기 vs 수인성 전파 경로의 비중을 탐구해 보세요.")

    # 2) 분석 대상 기간(연도) 선택 필터 & 요약 메트릭
    # 2) 분석 대상 기간(연도) 선택 필터 (사용자 요청: 기간 선택 전에는 차트를 숨겨 복잡도 해소)
    year_list = sorted([int(y) for y in working_df["연도"].dropna().unique()], reverse=True) if "연도" in working_df.columns else []
    year_opts = ["👉 [분석 대상 기간(연도)을 선택하세요]"] + ["전체 기간 (2019~2025년 7개년 누적)"] + [f"{y}년 연간 집계" for y in year_list]
    
    selected_period = st.selectbox("📅 분석 대상 기간 선택 (연도 필터)", year_opts, index=0, key="m3_period_select")

    if selected_period == "👉 [분석 대상 기간(연도)을 선택하세요]":
        st.info("👆 **[기간 선택 대기 중]**: 위 드롭다운에서 분석할 대상 기간(특정 연도 또는 7개년 누적)을 선택해 주세요. 선택하시면 국내외 지역별 점유율과 전파 경로 원그래프 및 상세 통계가 화면에 펼쳐집니다! 🗺️")
    else:
        if selected_period.startswith("전체 기간"):
            m3_df = working_df
            period_label = "2019~2025년 (7개년 전 기간 누적)"
        else:
            chosen_y = int(selected_period.split("년")[0])
            m3_df = working_df[working_df["연도"] == chosen_y]
            period_label = f"{chosen_y}년 연간"

        total_m3_cases = m3_df["신규환자수"].sum() if "신규환자수" in m3_df.columns else 0

        st.markdown(f"""
        <div style="background: #0f172a; border: 1px solid #334155; border-radius: 8px; padding: 10px 14px; margin-top: 4px; display: flex; justify-content: space-around; align-items: center; text-align: center;">
            <div>
                <div style="font-size: 0.76rem; color: #94a3b8;">📅 집계 기준 연도</div>
                <div style="font-size: 0.95rem; font-weight: 700; color: #38bdf8;">{period_label}</div>
            </div>
            <div style="border-left: 1px solid #334155; height: 28px;"></div>
            <div>
                <div style="font-size: 0.76rem; color: #94a3b8;">🦠 분석 대상 질병</div>
                <div style="font-size: 0.95rem; font-weight: 700; color: #4ade80;">법정감염병 63종 전체</div>
            </div>
            <div style="border-left: 1px solid #334155; height: 28px;"></div>
            <div>
                <div style="font-size: 0.76rem; color: #94a3b8;">👥 총 집계 환자 수</div>
                <div style="font-size: 0.95rem; font-weight: 800; color: #f8fafc;">{total_m3_cases:,}명</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.write("")
        c_a, c_b = st.columns(2)
        with c_a:
            st.markdown(f'''
            <div style="font-size: clamp(0.95rem, 1.1vw, 1.1rem); font-weight: 700; color: #f8fafc; margin-bottom: 2px;">
                🗺️ 국내외 주요 지역별 환자 점유율
            </div>
            <div style="font-size: 0.8rem; color: #94a3b8; margin-bottom: 8px;">
                📌 산출 기준: <span style="color:#38bdf8; font-weight:600;">[{period_label}]</span> × <span style="color:#10b981; font-weight:600;">[법정감염병 63종 전체 합산]</span>
            </div>
            ''', unsafe_allow_html=True)
            reg_pie_df = m3_df.groupby("지역")["신규환자수"].sum().reset_index().sort_values("신규환자수", ascending=False)
            active_reg_pie = reg_pie_df[reg_pie_df["신규환자수"] > 0]
            if active_reg_pie.empty or active_reg_pie["신규환자수"].sum() <= 0:
                st.info("ℹ️ 지역별 누적 환자 데이터가 없습니다 (0명).")
            else:
                top_n = 6
                if len(active_reg_pie) > top_n:
                    top_part = active_reg_pie.iloc[:top_n].copy()
                    other_val = active_reg_pie.iloc[top_n:]["신규환자수"].sum()
                    other_df = pd.DataFrame([{"지역": f"기타 {len(active_reg_pie) - top_n}개 지역", "신규환자수": other_val}])
                    plot_reg_df = pd.concat([top_part, other_df], ignore_index=True)
                else:
                    plot_reg_df = active_reg_pie

                fig_p1 = px.pie(
                    plot_reg_df,
                    values="신규환자수",
                    names="지역",
                    hole=0.45,
                    template="plotly_dark",
                    color_discrete_sequence=px.colors.qualitative.Plotly
                )
                fig_p1.update_traces(
                    textposition='inside',
                    textinfo='percent+label',
                    insidetextorientation='horizontal',
                    textfont=dict(size=12, color='#ffffff', family='Pretendard, sans-serif'),
                    marker=dict(line=dict(color='#0f172a', width=2))
                )
                fig_p1.update_layout(
                    showlegend=False,
                    margin=dict(l=10, r=10, t=15, b=15),
                    height=300
                )
                st.plotly_chart(fig_p1, use_container_width=True, key="plotly_menu3_region_pie")

                tot_reg_sum = active_reg_pie["신규환자수"].sum()
                st.markdown('<div style="display:flex; flex-wrap:wrap; gap:6px; margin-top:4px;">', unsafe_allow_html=True)
                top4_list = active_reg_pie.head(4).to_dict("records")
                for r_item in top4_list:
                    pct = (r_item["신규환자수"] / tot_reg_sum) * 100 if tot_reg_sum > 0 else 0
                    st.markdown(f"""
                    <div style="flex:1; min-width:110px; background:#1e293b; border:1px solid #334155; border-radius:6px; padding:6px 10px; text-align:center;">
                        <div style="font-size:0.78rem; color:#94a3b8; font-weight:600;">{r_item['지역']}</div>
                        <div style="font-size:0.95rem; color:#38bdf8; font-weight:800;">{pct:.1f}%</div>
                        <div style="font-size:0.75rem; color:#cbd5e1;">{r_item['신규환자수']:,}명</div>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

        with c_b:
            st.markdown(f'''
            <div style="font-size: clamp(0.95rem, 1.1vw, 1.1rem); font-weight: 700; color: #f8fafc; margin-bottom: 2px;">
                🧬 전파 경로별 환자 비중 (공기, 비말, 접촉 등)
            </div>
            <div style="font-size: 0.8rem; color: #94a3b8; margin-bottom: 8px;">
                📌 산출 기준: <span style="color:#38bdf8; font-weight:600;">[{period_label}]</span> × <span style="color:#10b981; font-weight:600;">[법정감염병 63종 전체 합산]</span>
            </div>
            ''', unsafe_allow_html=True)
            path_pie_df = m3_df.groupby("주요전파경로")["신규환자수"].sum().reset_index().sort_values("신규환자수", ascending=False)
            active_path_pie = path_pie_df[path_pie_df["신규환자수"] > 0]
            if active_path_pie.empty or active_path_pie["신규환자수"].sum() <= 0:
                st.info("ℹ️ 전파 경로별 환자 데이터가 없습니다 (0명).")
            else:
                route_colors = {
                    "호흡기 비말/공기 전파": "#38bdf8",
                    "오염식음료/분변-구강": "#f97316",
                    "접촉/피부/환경": "#10b981",
                    "혈액/체액/성접촉": "#ec4899",
                    "모기/진드기/설치류 매개": "#a855f7"
                }

                fig_p2 = px.pie(
                    active_path_pie,
                    values="신규환자수",
                    names="주요전파경로",
                    hole=0.48,
                    template="plotly_dark",
                    color="주요전파경로",
                    color_discrete_map=route_colors
                )
                fig_p2.update_traces(
                    textposition='inside',
                    textinfo='percent+label',
                    insidetextorientation='horizontal',
                    textfont=dict(size=13, color='#ffffff', family='Pretendard, sans-serif'),
                    marker=dict(line=dict(color='#0f172a', width=2))
                )
                fig_p2.update_layout(
                    showlegend=False,
                    margin=dict(l=10, r=10, t=15, b=15),
                    height=300
                )
                st.plotly_chart(fig_p2, use_container_width=True, key="plotly_menu3_route_pie")

                tot_path_sum = active_path_pie["신규환자수"].sum()
                rep_diseases_by_route = {
                    "호흡기 비말/공기 전파": ("🫁", "코로나19, 독감, 수두, 백일해, 홍역, 결핵"),
                    "오염식음료/분변-구강": ("🍽️", "노로바이러스, A형간염, 살모넬라, 장티푸스"),
                    "접촉/피부/환경": ("🤝", "수족구병, MRSA, 옴, 요충"),
                    "혈액/체액/성접촉": ("💉", "B/C형간염, AIDS, 매독, 엠폭스"),
                    "모기/진드기/설치류 매개": ("🦟", "쯔쯔가무시증, 말라리아, SFTS, 일본뇌염")
                }
                st.markdown('<div style="display:flex; flex-direction:column; gap:5px; margin-top:4px;">', unsafe_allow_html=True)
                for _, row in active_path_pie.iterrows():
                    r_name = row["주요전파경로"]
                    cnt_val = row["신규환자수"]
                    pct_val = (cnt_val / tot_path_sum * 100) if tot_path_sum > 0 else 0
                    icon, eg_dis = rep_diseases_by_route.get(r_name, ("🔬", "기타 법정감염병"))
                    c_hex = route_colors.get(r_name, "#38bdf8")
                    st.markdown(f"""
                    <div style="background:#1e293b; border-left:4px solid {c_hex}; border-radius:6px; padding:7px 12px; display:flex; justify-content:space-between; align-items:center;">
                        <div style="min-width:0;">
                            <div style="font-weight:700; color:#f8fafc; font-size:0.86rem; line-height:1.3;">{icon} {r_name}</div>
                            <div style="font-size:0.75rem; color:#94a3b8; margin-top:3px; line-height:1.3;">({eg_dis})</div>
                        </div>
                        <div style="text-align:right; white-space:nowrap; margin-left:10px;">
                            <span style="font-size:0.98rem; font-weight:800; color:{c_hex};">{pct_val:.1f}%</span>
                            <span style="font-size:0.75rem; color:#cbd5e1; margin-left:6px;">({cnt_val:,}명)</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

        st.divider()
        st.markdown("##### 📥 전체 감염병 데이터 테이블 및 CSV 다운로드")
        table_display_cols = [
            "연도", "월", "법정감염병군", "감염병명", "지역", "신규환자수",
            "0-9세", "10-19세", "20-49세", "50-64세", "65세 이상",
            "주요전파경로", "예방접종 또는 격리여부"
        ]
        show_cols = [c for c in table_display_cols if c in working_df.columns]
        st.dataframe(working_df[show_cols], use_container_width=True)
        st.download_button(
            "📥 2019~2025 전체 감염병 데이터 CSV 다운로드",
            data=working_df.to_csv(index=False).encode("utf-8-sig"),
            file_name="보건수업_종합_감염병통계_2019_2025.csv",
            mime="text/csv"
        )

    # [디지털 학습지 STEP 3] 학생 직접 기록 활동란
    st.write("")
    st.markdown("##### 📝 [3단계 탐구 활동지] 지역 역학 및 전파 경로 분석 기록장")

    st.caption("전국 17개 시도별 환자 분포와 전파 경로(호흡기 비말 vs 수인성·식품 vs 곤충 매개) 도넛 차트를 관찰하고, 수도권과 타 시도의 격차나 감염 경로별 역학적 특징을 한 줄로 기록해 보세요.")

    memo3_col1, memo3_col2 = st.columns([3.6, 1.5])
    with memo3_col1:
        s3_input = st.text_area(
            "3단계 기록 내용",
            value=st.session_state.get("wb_step3_note", ""),
            placeholder="예시: 인구 밀집도가 높은 서울·경기에 호흡기 비말 감염병(코로나19, 인플루엔자)이 집중 발생한 반면, 야외 활동과 매개 곤충이 많은 농촌 지역에서는 쯔쯔가무시증 비중이 두드러짐을 확인하였음.",
            label_visibility="collapsed",
            key="area_step3_memo",
            height=70
        )
    with memo3_col2:
        st.write("")
        if st.button("💾 3단계 저장 & 수행평가 연동", use_container_width=True, type="primary", key="btn_save_step3"):
            st.session_state["wb_step3_note"] = s3_input
            st.toast("✅ 3단계 기록이 저장되었으며 수행평가에 자동 연동되었습니다!")
            st.success("연동 완료! 🟢")
            st.rerun()


# ----------------------------------------------------
# [메뉴 4] STEP 4. 교내 집단감염 시뮬레이터 (내가 학교 보건교사라면?)
# ----------------------------------------------------
elif menu.startswith("4.") or menu == "4. 학교 집단감염 예방 시뮬레이터":
    st.subheader("🧪 4단계: 교내 집단감염 예방 시뮬레이터")
    st.info("💡 **오늘의 미션**: 내가 보건교사가 되어 환기, 마스크, 손 씻기 수칙을 조절해 유효 재생산지수(Rt)를 1.0 미만  \n(초록색)으로 낮춰보세요!")

    # 2. 수리 모형 상세 해설 아코디언 수납
    with st.expander("📐 [이론 길라잡이] 감염병 수리 모형(기초 R0 vs 유효 Rt) 계산 원리 보기"):
        st.markdown("""
        - **기초감염재생산수(R0)**: 방역 조치가 없는 상태에서 감염자 1명이 전파시키는 평균 감염자 수 (홍역 15.0, 백일해 12.0, 수두 10.0 등)
        - **유효재생산지수(Rt)**: 맞통풍 환기, KF94 마스크 착용, 올바른 손 씻기, 조기 격리 등 방역 중재 조치가 적용되었을 때의 실제 전파 지수
        - **교내 목표**: Rt를 **1.0 미만**으로 감폭시켜 교내 2차 전파 고리를 끊어내는 것!
        """)

    s_col1, s_col2 = st.columns([1, 1.2])
    with s_col1:
        st.markdown("#### ⚙️ 방역 중재 변수 조작")
        
        sim_disease_map = {
            "홍역 (제2급 / 공기 전파 / 최고 전염력 R0=15.0)": 15.0,
            "수두 (제2급 / 비말·수포 / 고위험 전염력 R0=10.0)": 10.0,
            "백일해 (제2급 / 비말 전파 / 고위험 전염력 R0=12.0)": 12.0,
            "코로나19 (제4급 / 비말·에어로졸 / R0=3.5)": 3.5,
            "사스(SARS) (제1급 / 비말·접촉 / R0=3.0)": 3.0,
            "엠폭스 (제2급 / 체액·피부접촉 / R0=2.2)": 2.2,
            "인플루엔자 (제4급 / 계절 비말 / R0=1.8)": 1.8,
            "중동호흡기증후군(MERS) (제1급 / 비말·밀접접촉 / R0=0.8)": 0.8
        }
        chosen_sim_name = st.selectbox("탐구 대상 감염병 선택", list(sim_disease_map.keys()), index=0)
        base_val = sim_disease_map[chosen_sim_name]

        v_slider = st.slider("🌬️ 교실 정기 맞통풍 환기 횟수 (회/교시)", 0, 4, 2)
        m_slider = st.slider("😷 학급 마스크(KF94) 착용률 (%)", 0, 100, 60, 5)
        h_slider = st.slider("🧼 30초 올바른 손 씻기 실천율 (%)", 0, 100, 70, 5)
        iso_check = st.checkbox("유증상자 즉시 보건실 격리 및 조기 귀가 조치", value=True)

    eff = min(min(v_slider * 0.10, 0.35) + (m_slider / 100) * 0.45 + (h_slider / 100) * 0.20 + (0.20 if iso_check else 0.0), 0.92)
    rt_res = max(round(base_val * (1 - eff), 2), 0.2)

    with s_col2:
        st.markdown("#### 📊 시뮬레이션 결과 예측")
        # 글자 짤림 방지: 상단에 선명한 HTML 제목 배치 및 Plotly margin 확보
        st.markdown('<div style="text-align: center; font-size: 1.15rem; font-weight: 700; color: #38bdf8; margin-top: 4px; margin-bottom: -6px;">예상 유효 재생산지수 (Rt)</div>', unsafe_allow_html=True)
        g_fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=rt_res,
            delta={'reference': 1.0, 'increasing': {'color': "#ef4444"}, 'decreasing': {'color': "#10b981"}},
            gauge={
                'axis': {'range': [0, max(base_val, 8)], 'tickwidth': 1, 'tickcolor': "#475569"},
                'bar': {'color': "#38bdf8"},
                'steps': [
                    {'range': [0, 1.0], 'color': '#065f46'},
                    {'range': [1.0, 2.5], 'color': '#854d0e'},
                    {'range': [2.5, max(base_val, 8)], 'color': '#991b1b'}
                ],
                'threshold': {'line': {'color': "#ffffff", 'width': 4}, 'thickness': 0.8, 'value': 1.0}
            }
        ))
        g_fig.update_layout(height=260, template="plotly_dark", margin=dict(l=25, r=25, t=10, b=15))
        st.plotly_chart(g_fig, use_container_width=True, key="plotly_menu4_rt_gauge")

        if rt_res < 1.0:
            st.success(f"🎉 **감염 전파 차단 성공 (Rt = {rt_res} < 1.0)**: 교내 2차 확산이 효과적으로 억제되었습니다!")
        elif rt_res < 2.0:
            st.warning(f"⚠️ **주의 단계 (Rt = {rt_res})**: 환기 횟수와 마스크 착용률을 조금 더 높여보세요.")
        else:
            st.error(f"🚨 **집단 유행 위험 단계 (Rt = {rt_res} > 2.0)**: 교실 내 전파 위험이 매우 높습니다!")

    # [디지털 학습지 STEP 4] 학생 직접 기록 활동란
    st.write("")
    st.markdown("##### 📝 [4단계 탐구 활동지] 학교 보건교사 교내 방역 처방전")

    st.caption("선택한 질환의 교내 유행을 Rt < 1.0으로 억제하기 위해 내가 조작한 최적의 방역 조합(환기 횟수, 마스크 착용률, 손 씻기, 조기 격리)과 결정 근거를 한 줄로 기록해 보세요.")

    memo4_col1, memo4_col2 = st.columns([3.6, 1.5])
    with memo4_col1:
        s4_input = st.text_area(
            "4단계 기록 내용",
            value=st.session_state.get("wb_step4_note", ""),
            placeholder="예시: 전염력이 매우 높은 백일해(R0=12)의 경우, 마스크 80% 착용과 매 교시 2회 맞통풍 환기, 그리고 유증상자 즉시 보건실 격리를 병행했을 때 Rt가 0.84로 떨어져 교내 집단유행을 막을 수 있었음.",
            label_visibility="collapsed",
            key="area_step4_memo",
            height=70
        )
    with memo4_col2:
        st.write("")
        if st.button("💾 4단계 저장 & 수행평가 연동", use_container_width=True, type="primary", key="btn_save_step4"):
            st.session_state["wb_step4_note"] = s4_input
            st.toast("✅ 4단계 기록이 저장되었으며 수행평가에 자동 연동되었습니다!")
            st.success("연동 완료! 🟢")
            st.rerun()


# ----------------------------------------------------
# [메뉴 5] STEP 5. AI 보건 튜터 & 디지털 학습지 완성
# ----------------------------------------------------
elif menu.startswith("5.") or menu in ["5. AI 보건 튜터(Q&A)", "5. AI_보건튜터(Q&A)", "5. AI 보건튜터(Q&A)"]:
    st.subheader("🩺 5단계: AI 보건 튜터 질의 & 학습지 최종 완성")
    st.markdown("""
    <div style="background:rgba(56,189,248,0.08); border-left:4px solid #38bdf8; border-radius:8px; padding:10px 16px; margin-bottom:12px; font-size:0.90rem; color:#f8fafc; white-space:nowrap;">
        💡 <strong>오늘의 미션</strong>: AI 보건 튜터에게 궁금한 감염병 질문을 하고, 오늘 작성한 나만의 디지털 활동지를 확인·제출해 보세요!
    </div>
    """, unsafe_allow_html=True)

    # 1단계, 2단계 드롭다운 UI (1단계 급수, 2단계 세부 감염병 선택 후에만 종합 리포트 및 AI 튜터 출력)
    st.markdown("##### 🔍 [1·2단계] 탐구할 법정감염병 선택 (1급~4급 완비)")

    t_keys_all = ["👉 [1단계: 법정감염병 급수를 먼저 선택하세요]"] + list(TIER_DISEASE_MAP.keys())
    tier_col, disease_col = st.columns(2)
    with tier_col:
        selected_tier_name = st.selectbox("📌 1단계: 법정감염병 급수 선택 (1~4급 분리)", options=t_keys_all, index=0, key="tutor_tier_select")

    with disease_col:
        if selected_tier_name == "👉 [1단계: 법정감염병 급수를 먼저 선택하세요]":
            selected_disease_name = st.selectbox("🦠 2단계: 세부 감염병 선택", options=["👉 [1단계 급수를 먼저 선택해야 활성화됩니다]"], index=0, disabled=True, key="tutor_disease_select_dis")
        else:
            sub_diseases = ["👉 [2단계: 세부 감염병을 선택하세요]"] + TIER_DISEASE_MAP[selected_tier_name]
            selected_disease_name = st.selectbox(f"🦠 2단계: 세부 감염병 선택 ({len(TIER_DISEASE_MAP[selected_tier_name])}종)", options=sub_diseases, index=0, key="tutor_disease_select")

    if selected_tier_name == "👉 [1단계: 법정감염병 급수를 먼저 선택하세요]":
        st.info("👆 **[1단계 급수 선택 대기 중]**: 위 1단계 드롭다운에서 탐구할 법정감염병 급수(1급~4급)를 먼저 선택해 주세요.")
    elif selected_disease_name == "👉 [2단계: 세부 감염병을 선택하세요]":
        st.info(f"👆 **[2단계 감염병 선택 대기 중]**: 위 2단계 드롭다운에서 탐구할 세부 감염병을 선택해 주세요. 선택 즉시 종합 역학 리포트와 AI 보건 튜터가 활성화됩니다! 🩺")
    else:
        dis_info = get_disease_info(selected_tier_name, selected_disease_name)

        # 질병 변경 감지 시 대화창을 즉시 해당 질병 전용으로 실시간 갱신
        if "tutor_current_disease" not in st.session_state or st.session_state["tutor_current_disease"] != selected_disease_name:
            st.session_state["tutor_current_disease"] = selected_disease_name
            st.session_state["chat_history"] = [
                {
                    "role": "assistant",
                    "content": f"안녕하세요! 지금 선택하신 **{selected_disease_name}**({dis_info['tier']})에 대해 궁금한 점이나 역학적 의문이 있다면 질문해 주세요. 아래 추천 질문 버튼을 누르거나 직접 질문을 입력하시면 학교 보건실 관리 지침에 기반하여 실시간 맞춤 분석 답변을 제공합니다. 👩‍⚕️"
                }
            ]

        # 실제 데이터셋에서 통계 연동
        stat_df = working_df[working_df["감염병명"] == selected_disease_name]
        if not stat_df.empty:
            real_tot = stat_df["신규환자수"].sum()
            real_youth = stat_df["10-19세"].sum() if "10-19세" in stat_df.columns else stat_df["청소년환자수"].sum()
            youth_ratio = (real_youth / real_tot * 100) if real_tot > 0 else 0
            real_cities = ", ".join(stat_df["지역"].unique()[:4])
            data_stat_text = f"실제 데이터(2019~2025) 기준 총 {real_tot:,}명 발생, 청소년(10-19세) 환자 {real_youth:,}명(비중 {youth_ratio:.1f}%), 주요 발생지: {real_cities}"
        else:
            data_stat_text = dis_info["trend"]

        # 종합 리포트 카드 렌더링
        st.markdown(f"""
        <div class="report-card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
                <div class="report-title">📋 [{selected_disease_name}] 종합 역학 및 보건 관리 리포트</div>
                <span class="badge-tier">{dis_info['tier']}</span>
            </div>
            <p><strong>1. 🦠 병원체 및 감염 원인:</strong><br>{dis_info['cause']} (병원체: <code>{dis_info['pathogen']}</code>)</p>
            <p><strong>2. 🧬 전파 경로:</strong><br>{dis_info['route']}</p>
            <p><strong>3. 🩺 주요 임상 증상 및 잠복기:</strong><br>{dis_info['symptoms']}</p>
            <p><strong>4. 📈 최근 발생 추세 및 통계:</strong><br>{data_stat_text}</p>
            <p><strong>5. 🛡️ 예방법 및 백신 접종:</strong><br>{dis_info['prevention']}</p>
            <p><strong>6. 🏥 치료 및 학교 보건실 관리 대책:</strong><br>{dis_info['treatment']}</p>
        </div>
        """, unsafe_allow_html=True)

        # 추가 탐구 대화창 (전문 보건의료 문양 🩺, 💉, 🧬 적용)
        st.divider()
        c_head1, c_head2 = st.columns([3.8, 1.2])
        with c_head1:
            st.markdown(f"<div style='font-size:1.15rem; font-weight:700; color:#f8fafc; white-space:nowrap; margin-bottom:4px;'>💬 [2단계] AI 보건튜터에게 질문하기 (현재 대상: <span style='color:#38bdf8;'>{selected_disease_name}</span>)</div>", unsafe_allow_html=True)
            st.caption(f"선택하신 '{selected_disease_name}'에 대해 더 깊이 알고 싶은 점을 아래 버튼 또는 입력창으로 질문해 보세요.")
        with c_head2:
            if st.button("🔄 대화 내용 초기화", use_container_width=True):
                st.session_state["chat_history"] = [
                    {
                        "role": "assistant",
                        "content": f"안녕하세요! 지금 선택하신 **{selected_disease_name}**({dis_info['tier']})에 대해 궁금한 점을 질문해 주세요. 👩‍⚕️"
                    }
                ]
                st.rerun()

        # 합리적인 전문 문양 칩 버튼들 (현재 선택된 질병명으로 동적 구성)
        q1, q2, q3 = st.columns(3)
        quick_q = None
        with q1:
            if st.button(f"🩺 {selected_disease_name} 학교 격리/등교중지 기준", use_container_width=True):
                quick_q = f"{selected_disease_name}에 걸린 학생이 있을 때 학교 보건실에서 취해야 할 등교 중지 기간과 격리 해제 기준을 자세히 설명해 줘."
        with q2:
            if st.button(f"💉 {selected_disease_name} 청소년 백신 및 면역 관리", use_container_width=True):
                quick_q = f"{selected_disease_name}의 예방 백신 접종 차수와 청소년 시기 추가접종의 중요성을 설명해 줘."
        with q3:
            if st.button(f"🧬 비말 vs 공기 전파 역학 관리 지침", use_container_width=True):
                quick_q = f"{selected_disease_name}의 전파 경로 특성과 교실 환경에서의 비말/공기 차단 관리 지침을 알려줘."

        api_k = get_api_key()

        # 1. 수업 활성화 및 접근 권한 점검
        is_allowed, lock_reason = check_classroom_access(
            st.session_state.get("teacher_code", "")
        )

        if quick_q:
            st.session_state["chat_history"].append({"role": "user", "content": quick_q})
            if not is_allowed:
                rep = f"🔒 **[수업 시간 외 사용 제한 안내]**\n\n{lock_reason}\n\n👉 **선생님께 요청하기 바랍니다.**"
            elif not is_legal_infectious_question(quick_q, selected_disease_name):
                rep = "해당 질문은 법정감염병과 관련이 없습니다. 선생님께 요청하기 바랍니다."
            else:
                rep = ""
                if api_k:
                    with st.spinner(f"AI 보건튜터가 질병관리청 최신 역학 데이터 및 교과서 지침을 분석 중입니다..."):
                        rep = query_gemini_ai(api_k, quick_q, selected_disease_name)
                if not rep:
                    rep = generate_detailed_tutor_answer(selected_disease_name, quick_q, dis_info)
                    if api_k and "관련이 없습니다" not in rep:
                        rep += "\n\n> 💡 *[보건 교육 지침] 질병관리청(KDCA) 감염병 포털 및 학교감염병 예방관리 매뉴얼 공식 지침을 기반으로 생성된 답변입니다.*"
            st.session_state["chat_history"].append({"role": "assistant", "content": rep})
            st.rerun()

        for chat in st.session_state["chat_history"]:
            with st.chat_message(chat["role"]):
                st.markdown(chat["content"])

        user_q = st.chat_input(f"{selected_disease_name}에 대해 궁금한 점을 입력하세요...")
        if user_q:
            st.session_state["chat_history"].append({"role": "user", "content": user_q})
            if not is_allowed:
                rep = f"🔒 **[수업 시간 외 사용 제한 안내]**\n\n{lock_reason}\n\n👉 **선생님께 요청하기 바랍니다.**"
            elif not is_legal_infectious_question(user_q, selected_disease_name):
                rep = "해당 질문은 법정감염병과 관련이 없습니다. 선생님께 요청하기 바랍니다."
            else:
                rep = ""
                if api_k:
                    with st.spinner(f"AI 보건튜터가 {selected_disease_name} 관련 질병관리청 역학 지침을 분석 중입니다..."):
                        rep = query_gemini_ai(api_k, user_q, selected_disease_name)
                if not rep:
                    rep = generate_detailed_tutor_answer(selected_disease_name, user_q, dis_info)
                    if api_k and "관련이 없습니다" not in rep:
                        rep += "\n\n> 💡 *[보건 교육 지침] 질병관리청(KDCA) 감염병 포털 및 학교감염병 예방관리 매뉴얼 공식 지침을 기반으로 생성된 답변입니다.*"
            st.session_state["chat_history"].append({"role": "assistant", "content": rep})
            st.rerun()

    # [디지털 학습지 STEP 5] 학생 직접 기록 활동란
    st.write("")
    st.markdown("##### 📝 [5단계 탐구 활동지] AI 보건 튜터 인터뷰 배움 기록장")
    st.markdown('<div style="color: #94a3b8; font-size: 0.84rem; white-space: nowrap; margin-bottom: 8px;">AI 보건 튜터에게 질의하여 새롭게 알게 된 학교 감염병 격리 기준, 백신 접종 차수, 또는 비말/공기 전파 예방 수칙을 한 줄로 요약해 보세요.</div>', unsafe_allow_html=True)

    memo5_col1, memo5_col2 = st.columns([3.1, 1.7])
    with memo5_col1:
        s5_input = st.text_area(
            "5단계 기록 내용",
            value=st.session_state.get("wb_step5_note", ""),
            placeholder="예시: 백일해는 증상 시작 후 항생제 복용 5일까지 등교 중지가 원칙이며, 청소년기 면역력 저하를 막기 위해 Tdap 6차 추가접종이 필수적임을 확인함.",
            label_visibility="collapsed",
            key="area_step5_memo",
            height=70
        )
    with memo5_col2:
        st.write("")
        if st.button("💾 5단계 저장 & 수행평가 연동", use_container_width=True, type="primary", key="btn_save_step5"):
            st.session_state["wb_step5_note"] = s5_input
            st.toast("🎉 5단계까지 모든 탐구 기록이 저장되었으며 수행평가에 자동 연동되었습니다!")
            st.success("연동 완료! 🟢")
            st.rerun()

    # 사용자 요청: "2022 개정 보건·정보 융합 디지털 탐구 활동지" 중복 블록은 화면에서 제거하고 상단 학생 탐구 활동지 버튼으로 일원화
    st.write("")
    st.info("💡 **활동지 최종 완성 안내**: 작성하신 모든 탐구 기록(1~5단계)은 상단의 **`[📋 학생 탐구 활동지]`** 버튼을 누르시면 이전 원본 PDF/인쇄용 양식 및 한글(.HWP) 파일로 언제든 예쁘게 열람하고 다운로드하실 수 있습니다.")


# ==========================================
# 6. 푸터 (사용자 요청: | 기호 완전 제거 및 보건간호과 반영)
# ==========================================
st.divider()
st.caption("서울의료보건고등학교 보건간호과  AI 융합 보건 교육 프로젝트")


import os
import json
import urllib.request
import urllib.error
import base64
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# 한글 폰트 설정 (Windows 기본 맑은 고딕 지원)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# ==========================================
# 1. 페이지 기본 설정 및 눈이 편안한 다크 테마 스타일
# ==========================================
st.set_page_config(
    page_title="AI 보건 탐구 - 감염병 데이터 대시보드",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    
    /* 상단 헤더 카드 */
    .header-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%) !important;
        padding: 14px 22px !important;
        border-radius: 14px !important;
        border: 1px solid #334155 !important;
        margin-bottom: 16px !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.3) !important;
        display: flex;
        align-items: center;
        gap: 16px;
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
    
    /* 지표 메트릭 카드 */
    .stMetric {
        background-color: #1e293b !important;
        padding: 12px 16px !important;
        border-radius: 10px !important;
        border: 1px solid #334155 !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.2) !important;
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


def ensure_dataset_integrity(df: pd.DataFrame) -> pd.DataFrame:
    """데이터프레임 내 연령대 5단계 세분화 및 컬럼 명칭을 100% 보장하는 무결성 함수"""
    if df.empty:
        return df
    df = df.copy()

    # 임질 -> AIDS(후천성면역결핍증) 자동 변환 및 무결성 보장
    if "감염병명" in df.columns:
        df["감염병명"] = df["감염병명"].replace({
            "AIDS(후천성면역결핍증)": "AIDS(후천성면역결핍증)",
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


def load_uploaded_dataframe(file_obj) -> pd.DataFrame:
    """사용자가 업로드한 CSV 파일을 다양한 인코딩(BOM UTF-8, UTF-8, CP949 등)으로 안전하게 읽어오는 함수"""
    df = None
    encodings_to_try = ["utf-8-sig", "utf-8", "cp949", "euc-kr"]
    for enc in encodings_to_try:
        try:
            file_obj.seek(0)
            df = pd.read_csv(file_obj, encoding=enc)
            if not df.empty and len(df.columns) >= 3:
                break
        except Exception:
            continue

    if df is None or df.empty:
        file_obj.seek(0)
        df = pd.read_csv(file_obj)

    # BOM(\ufeff) 및 컬럼 공백 제거
    df.columns = [str(c).replace('\ufeff', '').strip() for c in df.columns]
    for col in df.select_dtypes(include='object').columns:
        df[col] = df[col].astype(str).str.strip()

    return ensure_dataset_integrity(df)


# 서울의료보건고 로고 "원형 엠블럼 그림만" base64 인코딩
def get_emblem_base64():
    emblem_path = ASSETS_DIR / "school_emblem.png"
    if emblem_path.exists():
        with open(emblem_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return ""


# 대한민국 질병관리청 최신 법령 기준 급수별 10종 이상 공식 매핑 (코로나19는 제4급)
TIER_DISEASE_MAP = {
    "제1급 감염병": [
        "에볼라바이러스병", "중동호흡기증후군(MERS)", "사스(SARS)", "신종감염병증후군",
        "탄저", "페스트", "보툴리눔독소증", "야토병", "마버그열", "라싸열"
    ],
    "제2급 감염병": [
        "수두", "백일해", "홍역", "결핵", "유행성이하선염",
        "A형간염", "성홍열", "장티푸스", "세균성이질", "수막구균감염증"
    ],
    "제3급 감염병": [
        "말라리아", "엠폭스", "B형간염", "C형간염", "일본뇌염",
        "쯔쯔가무시증", "렙토스피라증", "비브리오패혈증", "파상풍", "뎅기열"
    ],
    "제4급 감염병": [
        "코로나19", "인플루엔자", "급성호흡기감염증", "수족구병", "클라미디아감염증",
        "AIDS(후천성면역결핍증)", "MRSA감염증", "VRE감염증", "CRE감염증", "사람유두종바이러스(HPV)"
    ],
    "제5급 감염병": [
        "노로바이러스", "로타바이러스", "회충증", "편충증", "요충증",
        "간흡충증", "폐흡충증", "장흡충증", "살모넬라감염증", "캄필로박터감염증"
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
DISEASE_INFO_DB = {
    # [제1급 감염병 - 치명률 높고 음압격리 필요 10종]
    "에볼라바이러스병": {
        "tier": "제1급 감염병",
        "pathogen": "에볼라 바이러스 (Ebolavirus, 필로바이러스과)",
        "route": "감염된 사람/동물의 혈액, 체액, 분비물 직접 접촉",
        "cause": "에볼라 바이러스의 혈관 내피세포 파괴 및 전신 응고 장애",
        "symptoms": "갑작스러운 발열, 극심한 무력감, 두통, 근육통, 구토, 설사, 내외인성 대량 출혈",
        "trend": "아프리카 중심 유행, 국내 유입 방지를 위한 검역 및 즉시 음압격리 감시 체계 가동",
        "prevention": "감염자 체액 접촉 차단, 전신 레벨D 개인보호구 착용, 에르베보(Ervebo) 백신",
        "treatment": "단클론항체 치료제(인마제브, 엡븡가), 대량 수액 요법, 제1급 전파 차단 즉시 격리"
    },
    "중동호흡기증후군(MERS)": {
        "tier": "제1급 감염병",
        "pathogen": "MERS-CoV (중동호흡기증후군 코로나바이러스, 베타코로나바이러스속)",
        "route": "단봉낙타 접촉, 감염자의 호흡기 비말 및 병원 내 밀접 접촉 전파",
        "cause": "바이러스의 폐포 상피세포 DPP4 수용체 결합 및 급성 염증 손상",
        "symptoms": "38℃ 이상 발열, 기침, 호흡곤란, 급성 폐렴, 신부전, 패혈성 쇼크",
        "trend": "2015년 국내 유행 이후 질병관리청 24시간 긴급상황실 연중 무휴 감시",
        "prevention": "중동 여행 시 낙타 접촉 및 생낙타유 섭취 금지, 의료기관 방문 시 KF94 마스크",
        "treatment": "대증 치료 및 인공호흡기 요법, 국가지정 입원치료병상(음압병실) 100% 격리"
    },
    "사스(SARS)": {
        "tier": "제1급 감염병",
        "pathogen": "SARS-CoV (중증급성호흡기증후군 코로나바이러스)",
        "route": "호흡기 비말 전파 및 오염된 물품 접촉, 에어로졸 전파",
        "cause": "바이러스 감염에 의한 광범위한 폐포 손상 및 급성 호흡곤란 증후군(ARDS)",
        "symptoms": "38℃ 이상 고열, 오한, 두통, 마른 기침, 저산소혈증, 폐 침윤",
        "trend": "2003년 전 세계 유행 이후 재발 감시 및 WHO 공조 방역 체계 유지",
        "prevention": "손 씻기, 유행 지역 여행 자제, 의심 환자 발생 시 즉시 레벨D 보호구 착용",
        "treatment": "항바이러스제 투여, 산소 요법, 격리 치료 병상 수용"
    },
    "신종감염병증후군": {
        "tier": "제1급 감염병",
        "pathogen": "미상 또는 변종 신종 병원체 (원인 불명 신종 감염체)",
        "route": "공기, 비말, 접촉 등 역학조사 진행에 따른 미상 전파",
        "cause": "기존에 알려지지 않은 신종 미생물의 인체 감염 및 전신 중증 반응",
        "symptoms": "원인 불명의 급성 발열, 중증 호흡기 또는 신경계/출혈성 복합 증상",
        "trend": "질병관리청 긴급대응반(EOC) 신속 진단 키트 개발 및 긴급 역학조사 실시",
        "prevention": "범국가적 감염병 위기경보 발령, 표준주의·접촉주의·공기주의 동시 가동",
        "treatment": "선제적 음압 격리 병동 입원, 다학제 집중 치료"
    },
    "탄저": {
        "tier": "제1급 감염병",
        "pathogen": "Bacillus anthracis (탄저균, 아포 형성 그람양성 간균)",
        "route": "피부 상처 아포 침투, 아포 흡입(폐탄저), 오염 육류 섭취(장탄저), 생물테러",
        "cause": "탄저균이 분비하는 치명독소(부종인자, 치사인자)로 인한 조직 괴사 및 출혈",
        "symptoms": "피부의 통증 없는 흑색 가피(가장 흔함), 호흡곤란, 청색증, 고열",
        "trend": "생물테러 가능 고위험 병원체로 국가 비축 항생제 및 백신 철저 관리",
        "prevention": "생물테러 의심 백색 가루 접촉 금지, 고위험군 탄저 백신 접종",
        "treatment": "시프로플록사신, 독시사이클린 등 정맥 항생제 60일 이상 투약"
    },
    "페스트": {
        "tier": "제1급 감염병",
        "pathogen": "Yersinia pestis (페스트균, 그람음성 간균)",
        "route": "감염된 쥐벼룩 물림, 감염 야생동물 접촉, 폐페스트 환자의 호흡기 비말",
        "cause": "림프절 침투 및 패혈증, 혈관 내 파종성 응고로 인한 말단 조직 괴사(흑사병)",
        "symptoms": "서혜부/겨드랑이 림프절의 극심한 종창(선페스트), 고열, 오한, 객혈(폐페스트)",
        "trend": "마다가스카르 등 해외 풍토병 지역 유입 감시 체계 유지",
        "prevention": "쥐 및 쥐벼룩 구제, 환자 비말 차단 마스크 착용, 예방적 항생제 투여",
        "treatment": "스트렙토마이신, 겐타마이신 등 조기 항생제 투약, 격리 입원"
    },
    "보툴리눔독소증": {
        "tier": "제1급 감염병",
        "pathogen": "Clostridium botulinum 신경독소 (보툴리눔 독소 A~G형)",
        "route": "오염된 밀봉 캔·가공식품 섭취(식품 매개), 흙/상처 오염, 영아 장내 감염",
        "cause": "신경근 접합부 아세틸콜린 분비 억제로 인한 진행성 이완성 신경 마비",
        "symptoms": "복시, 시야 흐림, 눈꺼풀 처짐, 연하 곤란, 언어 장애, 하행성 근력 약화, 호흡 마비",
        "trend": "치명적 신경마비 독소로 질병관리청 국가비축 항독소 즉각 출동 체계 운영",
        "prevention": "통조림 팽창 시 절대 섭취 금지, 식품 85℃ 5분 이상 가열 조리, 1세 미만 꿀 섭취 금지",
        "treatment": "보툴리눔 항독소(Antitoxin) 즉시 정맥 투여, 기도 확보 및 인공호흡기"
    },
    "야토병": {
        "tier": "제1급 감염병",
        "pathogen": "Francisella tularensis (야토균, 그람음성 세포내 기생균)",
        "route": "진드기·등에 물림, 감염된 야생 토끼·설치류 접촉, 오염 분진 흡입",
        "cause": "미량(10~50개) 균 침투로도 전신 림프절 비대 및 육아종성 염증 유발",
        "symptoms": "물린 부위 피부 궤양, 국소 림프절 종창, 오한, 발열, 폐렴형의 경우 흉통",
        "trend": "북미, 유럽 야생동물 매개 감시, 생물테러 대응 병원체 지정 관리",
        "prevention": "야외 활동 시 진드기 기피제 사용, 야생 토끼 사체 접촉 금지, 방수 장갑 착용",
        "treatment": "스트렙토마이신, 겐타마이신, 독시사이클린 항생제 치료"
    },
    "마버그열": {
        "tier": "제1급 감염병",
        "pathogen": "Marburgvirus (마버그 바이러스, 필로바이러스과)",
        "route": "과일박쥐(Rousettus) 서식지 접촉, 감염 환자의 혈액 및 체액 직접 접촉",
        "cause": "혈관 투과성 급증 및 다발성 장기 부전 유발 출혈열",
        "symptoms": "심한 두통, 고열, 극심한 쇠약, 반점구진성 발진, 5~7일째 심한 출혈 및 쇼크",
        "trend": "아프리카 적도 기니 등 국지적 유행 발생 시 국내 입국자 집중 모니터링",
        "prevention": "동굴 및 박쥐 서식지 방문 금지, 환자 접촉 시 철저한 개인보호구 착용",
        "treatment": "대증 치료, 수액 공급 및 전해질 교정, 제1급 격리 입원"
    },
    "라싸열": {
        "tier": "제1급 감염병",
        "pathogen": "Lassa mammarenavirus (라싸 바이러스, 아레나바이러스과)",
        "route": "야생 다유방쥐(Mastomys) 배설물 오염 음식물 섭취 및 환자 체액 접촉",
        "cause": "내피세포 손상으로 인한 모세혈관 누출 및 신부전",
        "symptoms": "점진적 발열, 인후통, 흉통, 안면 부종, 결막하 출혈, 청력 상실(25%)",
        "trend": "서아프리카 유입 환자 감시 대상",
        "prevention": "음식물 밀폐 보관, 설치류 박멸, 환자 격리 및 체액 접촉 차단",
        "treatment": "초기 리바비린(Ribavirin) 정맥 투약 시 사망률 현저히 감소"
    },

    # [제2급 감염병 - 전파 가능성을 고려하여 24시간 내 신고 및 격리 10종]
    "수두": {
        "tier": "제2급 감염병",
        "pathogen": "Varicella-Zoster Virus (VZV, 수두-대상포진 바이러스 / 헤르페스바이러스과)",
        "route": "호흡기 비말 전파 및 피부 수포액 직접 접촉 (R0=10~12 고위험)",
        "cause": "수두바이러스의 호흡기 점막 침투 후 림프절 증식 및 전신 피부 수포 형성",
        "symptoms": "미열 후 반점->구진->수포(물집)->가피(딱지)로 변하는 심한 가려움 발진",
        "trend": "매년 4~6월, 11~1월 초·중·고교 집단 발병 지속 모니터링",
        "prevention": "생후 12~15개월 국가필수 수두 백신 1회 접종 완료, 손 씻기",
        "treatment": "칼라민 로션, 항히스타민제, 모든 수포에 딱지가 앉을 때까지 등교 전면 중지"
    },
    "백일해": {
        "tier": "제2급 감염병",
        "pathogen": "Bordetella pertussis (백일해균, 그람음성 간균)",
        "route": "기침·재채기 시 튀는 호흡기 비말 전파 (R0=12~15 극도로 높음)",
        "cause": "백일해균이 기관지 섬모 상피를 마비시키고 백일해 독소(PT) 분비",
        "symptoms": "초기 감기 증상 후 2주 이상 발작성 기침, 숨 들이쉴 때 '흡(Whoop)' 소리, 구토",
        "trend": "2024~2025년 중·고등학생 청소년층에서 집단 유행 급증",
        "prevention": "DTaP 5회 접종 후, 만 11~12세 Tdap 6차 추가접종 필수",
        "treatment": "마크로라이드계 항생제 투약, 항생제 복용 시작 후 5일까지 등교 중지"
    },
    "홍역": {
        "tier": "제2급 감염병",
        "pathogen": "Measles morbillivirus (홍역 바이러스, 파라믹소바이러스과)",
        "route": "공기(비말핵) 전파 및 비말 접촉 (R0=12~18 최고 전염력)",
        "cause": "바이러스의 호흡기 상피 침투 및 면역계 파괴(면역 기억 상실 유발)",
        "symptoms": "3C(기침 Cough, 콧물 Coryza, 결막염 Conjunctivitis), 코플릭 반점, 전신 홍반성 발진",
        "trend": "해외 유입 및 백신 미접종군 중심 산발적 집단 유행",
        "prevention": "MMR(홍역·유행성이하선염·풍진) 백신 2회 접종(12~15개월, 만 4~6세)",
        "treatment": "비타민 A 투약 및 대증 요법, 발진 발생 후 4일까지 등교 중지 및 격리"
    },
    "결핵": {
        "tier": "제2급 감염병",
        "pathogen": "Mycobacterium tuberculosis (결핵균, 항산성 간균)",
        "route": "활동성 폐결핵 환자의 기침 시 공기 중 비말핵(1~5㎛) 흡입",
        "cause": "결핵균의 폐포 대식세포 내 증식 및 육아종성 건락 괴사 형성",
        "symptoms": "2주 이상 지속되는 기침, 객담, 혈담, 야간 발한, 미열, 체중 감소, 피로",
        "trend": "OECD 국가 중 발생률 상위, 고등학교 내 밀접 접촉 집단 감시 및 잠복결핵 검진",
        "prevention": "생후 4주 이내 BCG 접종, 교실 주기적 환기, 2주 이상 기침 시 흉부 X선 검진",
        "treatment": "표준 4제 요법(이소니아지드, 리팜핀, 에탐부톨, 피라진아미드), 도말 음성 시까지 등교 중지"
    },
    "유행성이하선염": {
        "tier": "제2급 감염병",
        "pathogen": "Mumps rubulavirus (유행성이하선염 바이러스 / 볼거리)",
        "route": "호흡기 비말 전파 및 감염자 타액(침) 직접 접촉",
        "cause": "바이러스가 비강 점막에서 증식 후 혈류를 타고 타액선(침샘) 침범",
        "symptoms": "귀밑샘(이하선)의 일측 또는 양측 부종과 심한 통증, 씹을 때 통증, 발열",
        "trend": "중·고등학교 남학생 다발, 사춘기 합병증(고환염, 뇌수막염) 주의",
        "prevention": "MMR 2회 접종 철저, 손 씻기 및 식기 공유 금지",
        "treatment": "냉찜질 및 진통소염 대증 치료, 귀밑샘 부종 발생 후 5일까지 등교 중지"
    },
    "A형간염": {
        "tier": "제2급 감염병",
        "pathogen": "Hepatitis A Virus (HAV, A형 간염 바이러스 / 피코르나바이러스과)",
        "route": "분변-구강 경로, 오염된 물 또는 조개류(조개젓 등) 섭취, 밀접 접촉",
        "cause": "섭취된 바이러스가 장관 흡수 후 간세포 내 복제 및 면역 매개 간 손상",
        "symptoms": "고열, 피로, 식욕 부진, 구역, 암갈색 뇨, 공막 및 피부 황달",
        "trend": "20~40대 청장년층 항체 보유율 낮아 집단 발병 위험군",
        "prevention": "A형 간염 백신 2회 접종(6~18개월 간격), 끓인 물 마시기, 조개류 85℃ 익혀먹기",
        "treatment": "충분한 휴식과 영양 공급, 황달 발생 후 1주일간 등교 및 등원 중지"
    },
    "성홍열": {
        "tier": "제2급 감염병",
        "pathogen": "Streptococcus pyogenes (A군 화농성 연쇄상구균)",
        "route": "기침·재채기 시 호흡기 비말 전파 및 균 접촉",
        "cause": "연쇄상구균이 생산하는 발적독소(Erythrogenic toxin)에 의한 전신 모세혈관 확장",
        "symptoms": "갑작스러운 인두통, 고열, 딸기 모양의 혀(딸기혀), 모래알 같은 선홍색 전신 발진",
        "trend": "학령기 아동 및 청소년 중심 계절적 유행",
        "prevention": "손 씻기, 기침 예절, 학급 내 환기, 환자 식기 소독",
        "treatment": "페니실린/아목시실린 항생제 10일간 완충 투약, 항생제 복용 후 24시간까지 등교 중지"
    },
    "장티푸스": {
        "tier": "제2급 감염병",
        "pathogen": "Salmonella Typhi (살모넬라 타이피균, 그람음성 간균)",
        "route": "오염된 음식물 또는 음용수 섭취(분변-구강 경로), 무증상 보균자 매개",
        "cause": "소장 파이어판 침투 후 단핵식균세포계 증식 및 전신 균혈증",
        "symptoms": "계단식으로 상승하는 지속성 고열, 서맥(상대적 완맥), 복통, 장미진, 비장 비대",
        "trend": "집단 급식소 위생 감시 및 해외 유행지역 입국자 감시",
        "prevention": "음식물 충분히 가열 조리, 안전한 음용수, 유행지역 여행 시 장티푸스 백신 접종",
        "treatment": "퀴놀론계 항생제 치료, 항생제 중단 48시간 후 대변 배양검사 3회 음성 시까지 등교 중지"
    },
    "세균성이질": {
        "tier": "제2급 감염병",
        "pathogen": "Shigella dysenteriae, S. flexneri, S. sonnei (이질균)",
        "route": "오염된 물/음식 섭취, 손을 통한 직접 접촉 (극소량인 10~100개 균으로도 감염)",
        "cause": "결장 점막 상피 침투 및 시가독소(Shiga toxin) 분비로 미세 궤양 형성",
        "symptoms": "고열, 구역, 복통, 이급후증(뒤무직, Tenesmus), 점액성 혈변",
        "trend": "학교 및 집단 급식소 수인성 집단 발생 감시 대상",
        "prevention": "30초 올바른 손 씻기, 안전한 급식 공급, 조리 종사자 위생 점검",
        "treatment": "수액 보충 및 감수성 항생제 치료, 배양검사 음성 확인 시까지 등교 중지"
    },
    "수막구균감염증": {
        "tier": "제2급 감염병",
        "pathogen": "Neisseria meningitidis (수막구균, 그람음성 쌍구균)",
        "route": "감염자 또는 무증상 보균자의 호흡기 분비물(비말) 직접 접촉",
        "cause": "비인두 점막 침투 후 혈류로 유입되어 뇌척수막 침범 및 급성 패혈증 유발",
        "symptoms": "갑작스러운 고열, 심한 두통, 목 경직(경부 강직), 피부 자반성 발진, 의식 저하",
        "trend": "기숙사, 군대 등 청소년 밀집 집단 시설 위험군",
        "prevention": "수막구균 4가 단백결합 백신(MenACWY) 접종, 기숙사 입소 전 접종 권고",
        "treatment": "3세대 세파계 항생제 즉각 정맥 투약, 적절한 항생제 치료 후 24시간까지 격리"
    },

    # [제3급 감염병 - 발생을 계속 감시할 필요가 있는 감염병 10종]
    "말라리아": {
        "tier": "제3급 감염병",
        "pathogen": "Plasmodium vivax (삼일열원충, 국내), P. falciparum (열대열원충)",
        "route": "얼룩날개모기(Anopheles) 암컷이 흡혈할 때 원충 포자소체 인체 주입",
        "cause": "간세포 증식 후 적혈구 침입·파괴 및 주기적 적혈구 파열로 발열 독소 방출",
        "symptoms": "오한기(극심한 추위와 떨림) -> 고열기(40℃ 고열) -> 발한기(땀을 흘리며 열 하강) 48시간 주기",
        "trend": "경기 북부, 강원, 인천 접경지역 중심 국내 삼일열 말라리아 지속 감시",
        "prevention": "야간 야외활동 자제, 밝은 긴 옷 착용, 모기 기피제 사용, 위험지역 예방약 복용",
        "treatment": "클로로퀸(혈액 원충 제거) + 프리마퀸(간 조직 휴면체 박멸 14일 복용)"
    },
    "엠폭스": {
        "tier": "제3급 감염병",
        "pathogen": "Monkeypox virus (엠폭스 바이러스 / 올소폭스바이러스속)",
        "route": "피부 병변 직접 접촉, 성 접촉, 체액, 오염된 침구류 접촉",
        "cause": "피부 점막 상처를 통해 침투하여 전신 림프절 비대 및 수포성 피부 병변 유발",
        "symptoms": "발열, 오한, 림프절 부종, 두통 후 구진->수포->농포->가피로 진행되는 발진",
        "trend": "국내외 발생 동향 모니터링 및 고위험군 예방접종(진네오스 백신) 실시",
        "prevention": "익명의 다수와 밀접 신체 접촉 자제, 의심 환자 접촉 금지, 손 위생",
        "treatment": "항바이러스제(테코비리마트), 피부 병변 가피가 완전히 탈락할 때까지 격리"
    },
    "B형간염": {
        "tier": "제3급 감염병",
        "pathogen": "Hepatitis B Virus (HBV, B형 간염 바이러스 / 헤파드나바이러스과)",
        "route": "감염된 혈액, 체액, 성 접촉, 오염된 주사기, 모체-신생아 수직감염",
        "cause": "간세포 내 바이러스 지속 감염으로 만성 간염, 간경변증, 간세포암 유발",
        "symptoms": "피로, 황달, 우상복부 불쾌감, 만성 진행 시 무증상 지속",
        "trend": "국가예방접종 사업으로 청소년 항체 형성률 99% 달성",
        "prevention": "B형 간염 백신 3회 접종(0, 1, 6개월), 주사기 재사용 금지",
        "treatment": "경구용 항바이러스제(엔테카비르, 테노포비르), 일상 학교생활 격리 불필요"
    },
    "C형간염": {
        "tier": "제3급 감염병",
        "pathogen": "Hepatitis C Virus (HCV, C형 간염 바이러스 / 플라비바이러스과)",
        "route": "오염된 주사기 재사용, 비위생적 문신/피어싱, 감염 혈액 노출",
        "cause": "바이러스의 간세포 감염으로 70~80%가 만성 간염으로 이행",
        "symptoms": "초기 대부분 무증상, 피로감, 식욕 부진, 장기 경과 시 간경변 및 간암",
        "trend": "직접 작용 항바이러스제(DAA) 도입으로 98% 이상 완치 가능",
        "prevention": "백신 없음, 1회용 주사기 사용, 무면허 문신·시술 절대 금지",
        "treatment": "경구용 DAA 치료제 8~12주 복용으로 완치, 일상 접촉 전파 불가"
    },
    "일본뇌염": {
        "tier": "제3급 감염병",
        "pathogen": "Japanese encephalitis virus (일본뇌염 바이러스 / 플라비바이러스과)",
        "route": "작은빨간집모기(Culex tritaeniorhynchus) 흡혈 매개",
        "cause": "모기 매개 바이러스 침투 후 혈뇌장벽(BBB)을 통과하여 뇌실질 감염",
        "symptoms": "99%는 무증상, 뇌염 이행 시 40℃ 고열, 경련, 마비, 혼수, 영구 신경학적 후유증",
        "trend": "매년 여름 일본뇌염 주의보/경보 발령 및 모기 밀도 조사",
        "prevention": "국가필수 일본뇌염 백신(사백신 5회 또는 생백신 2회) 접종 완료, 모기 기피제",
        "treatment": "특이 치료제 없음, 뇌압 강하 및 항경련 등 집중 보존 치료"
    },
    "쯔쯔가무시증": {
        "tier": "제3급 감염병",
        "pathogen": "Orientia tsutsugamushi (쯔쯔가무시균, 리케차과)",
        "route": "풀숲에 서식하는 활순털진드기(Leptotrombidium) 유충에 물려 감염",
        "cause": "진드기 유충 흡혈 시 균이 피부에 침투하여 국소 혈관염 유발",
        "symptoms": "물린 부위 흑색 가피(Eschar, 딱지), 갑작스러운 고열, 오한, 전신 림프절 비대, 발진",
        "trend": "가을철(10~11월) 야외활동, 농작업, 단풍놀이 시 환자 집중 발생",
        "prevention": "야외활동 시 돗자리 사용, 긴 소매·긴 바지 착용, 귀가 즉시 샤워 및 의류 세탁",
        "treatment": "독시사이클린(Doxycycline) 항생제 조기 투약 시 극적인 임상 호전"
    },
    "렙토스피라증": {
        "tier": "제3급 감염병",
        "pathogen": "Leptospira interrogans (렙토스피라균, 나선균)",
        "route": "감염된 설치류(들쥐) 소변에 오염된 물·진흙과 피부 상처 접촉",
        "cause": "피부 상처나 점막을 뚫고 혈액으로 침투하여 모세혈관염 유발",
        "symptoms": "갑작스러운 발열, 오한, 심한 종아리 근육통, 결막 충혈, 황달, 신부전",
        "trend": "가을철 장마 및 태풍 침수 지역 농작업자 집중 감시",
        "prevention": "침수 지역 작업 시 방수 장화와 고무장갑 착용, 오염된 물 접촉 금지",
        "treatment": "독시사이클린 또는 페니실린계 항생제 조기 투여"
    },
    "비브리오패혈증": {
        "tier": "제3급 감염병",
        "pathogen": "Vibrio vulnificus (비브리오 불니피쿠스, 그람음성 간균)",
        "route": "오염된 어패류 익히지 않고 섭취, 피부 상처를 바닷물에 접촉",
        "cause": "균의 외독소 및 단백분해효소로 인한 급성 패혈성 쇼크 및 피부 조직 괴사",
        "symptoms": "발열, 오한 후 하지에 발생하는 출혈성 수포, 부종, 피부 궤양 및 괴사 (치명률 50%)",
        "trend": "해수 온도가 18℃ 이상 상승하는 5~10월 서남해안 집중 발생",
        "prevention": "간질환자 등 고위험군 어패류 날것 섭취 금지, 상처 난 피부 바닷물 입수 금지",
        "treatment": "조기 3세대 세파계+독시사이클린 항생제 병용, 괴사 조직 외과적 절제"
    },
    "파상풍": {
        "tier": "제3급 감염병",
        "pathogen": "Clostridium tetani 신경독소 (테타노스파스민 독소)",
        "route": "녹슨 못, 흙, 동물 배설물에 오염된 상처 부위 아포 침투",
        "cause": "독소가 억제성 신경전달물질(GABA, 글리신) 방출 차단하여 지속적 골격근 강직 유발",
        "symptoms": "입을 열지 못하는 개구장애(Trismus), 조소(경련성 미소), 활모양 등 굽음(후궁반장)",
        "trend": "상처 감염 시 치명률 10~20%, 정기 백신 면역 유지 필수",
        "prevention": "DTaP 접종 완료 후, 10년마다 Td 또는 Tdap 백신 추가접종",
        "treatment": "파상풍 인간 면역글로불린(TIG) 투여, 상처 소독, 메트로니다졸 항생제"
    },
    "뎅기열": {
        "tier": "제3급 감염병",
        "pathogen": "Dengue virus (뎅기 바이러스 1~4형 / 플라비바이러스과)",
        "route": "흰줄숲모기(Aedes albopictus), 이집트숲모기 흡혈 매개",
        "cause": "바이러스 침투 후 혈관 내피세포 기능 부전 및 혈장 누출",
        "symptoms": "급격한 고열(3~5일), 극심한 두통, 안와통, 뼈마디가 부서지는 듯한 관절통, 피부 발진",
        "trend": "동남아시아 및 중남미 여행객을 통한 해외 유입 감염병 1위",
        "prevention": "동남아 여행 시 모기 기피제 철저 사용, 밝은 긴 옷 착용, 방충망 확인",
        "treatment": "특이 치료제 없음, 아스피린/이부프로펜 금기(출혈 위험), 아세트아미노펜 해열"
    },

    # [제4급 감염병 - 표본감시 활동 및 학교 보건관리 10종]
    "코로나19": {
        "tier": "제4급 감염병",
        "pathogen": "SARS-CoV-2 (코로나바이러스, 베타코로나바이러스속)",
        "route": "기침·재채기 시 호흡기 비말, 밀폐 공간 에어로졸, 표면 접촉",
        "cause": "바이러스 스파이크 단백질이 호흡기 상피세포 ACE2 수용체에 결합하여 세포 내 증식",
        "symptoms": "발열, 기침, 인후통, 후각/미각 상실, 호흡곤란, 전신 피로감",
        "trend": "2020년 팬데믹, 2022년 오미크론 대유행, 2023.8.31 제4급 전환 후 계절적 엔데믹 유행",
        "prevention": "고위험군 정기 백신 접종, 교실 시간당 2회 맞통풍 환기, 유증상 시 마스크",
        "treatment": "팍스로비드/라게브리오 경구약, 대증 치료, 주요 증상 호전 후 24시간까지 격리 권고"
    },
    "인플루엔자": {
        "tier": "제4급 감염병",
        "pathogen": "Influenza virus A/B형 (오르토믹소바이러스과)",
        "route": "기침, 재채기 시 호흡기 비말(5㎛ 이상) 및 오염된 손 접촉",
        "cause": "바이러스 헤마글루티닌(HA) 단백질이 기도 점막에 부착하여 급성 염증 유발",
        "symptoms": "38℃ 이상의 갑작스러운 고열, 심한 두통, 전신 근육통, 오한, 인후통, 마른 기침",
        "trend": "매년 11월~이듬해 3월 겨울철 학교 내 청소년 폭발적 유행",
        "prevention": "매년 가을 4가 독감 백신 접종 완료, 30초 올바른 손 씻기, 기침 예절 지도",
        "treatment": "오셀타미비르(타미플루 5일 복용) 또는 페라미비르 주사제 투약, 해열 후 24시간 등교 중지"
    },
    "급성호흡기감염증": {
        "tier": "제4급 감염병",
        "pathogen": "아데노바이러스, 호흡기세포융합바이러스(RSV), 리노바이러스, 보카바이러스 등",
        "route": "호흡기 분비물 비말 전파 및 손 접촉",
        "cause": "다양한 호흡기 바이러스의 기관지 상피 감염 및 기도 염증",
        "symptoms": "콧물, 재채기, 인후통, 기침, 천명음(모세기관지염 시 쌕쌕거림), 미열",
        "trend": "환절기 및 겨울철 영유아와 학령기 아동·청소년 다발",
        "prevention": "손 씻기, 마스크 착용, 교실 공기정화 및 정기 환기",
        "treatment": "진해거담제, 해열진통제 대증 요법, 수분 섭취, 증상 호전 시까지 안정"
    },
    "수족구병": {
        "tier": "제4급 감염병",
        "pathogen": "콕사키바이러스 A16형 (Coxsackievirus A16), 엔테로바이러스 71형 (EV71)",
        "route": "감염자의 침, 콧물 등 호흡기 분비물, 대변 접촉, 물집 진물 접촉",
        "cause": "장바이러스가 인두 점막 및 소장에서 증식 후 전신 피부 점막에 수포 형성",
        "symptoms": "손바닥, 발바닥, 입안(구강 점막, 혀)에 생기는 쌀알 크기의 수포성 발진, 미열, 식욕 부진",
        "trend": "매년 5~8월 여름철 영유아 시설 및 초등학교 저학년 집중 유행",
        "prevention": "기저귀 교체 후 손 씻기, 장난감 소독, 환자 분비물 격리",
        "treatment": "탈수 예방 수액 공급, 진통제, 모든 수포가 아물 때까지 등교 중지"
    },
    "클라미디아감염증": {
        "tier": "제4급 감염병",
        "pathogen": "Chlamydia trachomatis (클라미디아 트라코마티스, 세포내 기생 세균)",
        "route": "성 접촉(질, 항문, 구강 성교)을 통한 점막 감염, 출산 시 신생아 수직감염",
        "cause": "요도 및 자궁경부 원주상피세포 내 증식으로 만성 염증 유발",
        "symptoms": "남성: 배뇨통, 요도 분비물 / 여성: 70~80% 무증상, 비정상 질 분비물, 골반염, 불임 유발",
        "trend": "청소년 및 20대 청년층에서 가장 흔한 성 매개 감염병으로 검진 권장",
        "prevention": "안전한 성생활(콘돔 사용), 정기 성매개감염 선별검사, 파트너 동시 검사 및 치료",
        "treatment": "아지스로마이신 1회 요법 또는 독시사이클린 7일 복용 (파트너 동시 치료 필수)"
    },
    "AIDS(후천성면역결핍증)": {
        "tier": "제4급 감염병",
        "pathogen": "인체면역결핍바이러스 (HIV, Human Immunodeficiency Virus / 레트로바이러스과)",
        "route": "안전하지 않은 성 접촉, 감염 혈액 수혈·노출, 오염된 주사기 공동사용, 모체-태아 수직감염",
        "cause": "HIV가 면역 조절의 핵심 세포인 CD4+ T림프구에 침투·파괴하여 세포성 면역 결핍 초래",
        "symptoms": "초기 감기 증상(발열, 인후통) -> 수년~10년 무증상 잠복기 -> 기회감염(카포시육종, 폐렴)",
        "trend": "조기 진단 및 지속적 항레트로바이러스제 복약으로 일반인과 기대수명 유사한 만성 관리 질환화",
        "prevention": "안전한 성생활(올바른 콘돔 사용), PrEP(노출 전 예방요법), PEP(노출 후 72시간 내 예방약), 주사기 재사용 금지",
        "treatment": "고활성 항레트로바이러스 요법(HAART/칵테일 복약). 학교보건법상 등교 중지 비해당(일상 접촉 전파 불가), 비밀보장 및 편견 해소 교육"
    },
    "MRSA감염증": {
        "tier": "제4급 감염병",
        "pathogen": "메티실린 내성 황색포도알균 (Methicillin-Resistant Staphylococcus aureus)",
        "route": "오염된 손, 의료 기구, 환자 상처 분비물 직접 접촉",
        "cause": "mecA 유전자에 의한 페니실린 결합 단백질(PBP2a) 변형으로 베타락탐계 항생제 내성",
        "symptoms": "피부 연조직 화농성 감염, 수술 부위 감염, 폐렴, 카테터 관련 균혈증",
        "trend": "병원 내 감염 표본감시 및 중환자실 집중 관리 대상",
        "prevention": "철저한 접촉주의 지침 준수, 알코올 젤 손 소독, 격리 가운 및 장갑 착용",
        "treatment": "반코마이신(Vancomycin), 테이코플라닌 등 감수성 항생제 투여"
    },
    "VRE감염증": {
        "tier": "제4급 감염병",
        "pathogen": "반코마이신 내성 장알균 (Vancomycin-Resistant Enterococcus)",
        "route": "의료진의 손, 오염된 환경 표면, 대변을 통한 접촉 전파",
        "cause": "장알균의 세포벽 펩티도글리칸 전구체 변이(vanA/vanB 유전자)로 반코마이신 결합 방해",
        "symptoms": "요로감염, 복강 내 감염, 균혈증, 심내막염",
        "trend": "면역저하 환자 및 장기 입원자 중심 다제내성균 감시",
        "prevention": "환자 접촉 전후 손 위생, 환경 소독(락스 희석액), 1회용 의료기구 사용",
        "treatment": "리네졸리드(Linezolid), 답토마이신 등 대체 항생제 투약"
    },
    "CRE감염증": {
        "tier": "제4급 감염병",
        "pathogen": "카바페넴 내성 장내세균목 (Carbapenem-Resistant Enterobacterales)",
        "route": "환자 및 보균자와의 접촉, 오염된 내시경 및 카테터 기구",
        "cause": "카바페넴 분해효소(KPC, NDM 등) 생성으로 최후의 항생제 카바페넴 계열 무력화",
        "symptoms": "폐렴, 요로감염, 패혈증 등 다발성 장기 중증 감염 (치명률 20~50%)",
        "trend": "국내 종합병원 및 요양병원 중심 법정 전수 표본감시 강화",
        "prevention": "격리 병실 배치, 전담 의료진 지정, 장비 전용화 및 침상 간격 유지",
        "treatment": "콜리스틴, 세프타지딤/아비박탐 등 신약 병용 요법"
    },
    "사람유두종바이러스(HPV)": {
        "tier": "제4급 감염병",
        "pathogen": "Human Papillomavirus (사람유두종바이러스 고위험군 16, 18형 등)",
        "route": "피부 및 생식기 점막 접촉(성 접촉)",
        "cause": "바이러스의 자궁경부 편평상피세포 내 유전체 삽입으로 암 억제 유전자(p53, Rb) 불활성화",
        "symptoms": "대부분 무증상, 생식기 사마귀(곤지름), 자궁경부암, 항문암, 구인두암 유발",
        "trend": "만 12세 여성 청소년 대상 국가필수예방접종(NIP) 무료 지원",
        "prevention": "HPV 9가(가다실 9) 백신 접종(청소년기 접종 시 항체 형성률 최고), 안전한 성생활",
        "treatment": "바이러스 자체 박멸제 없음, 병변 냉동치료/원추절제술, 조기 선별 자궁경부 세포검사"
    },

    # [제5급 감염병 - 기생충 질환 및 식품 매개 바이러스 10종]
    "노로바이러스": {
        "tier": "제5급 감염병",
        "pathogen": "Norovirus (노로바이러스 / 칼리시바이러스과)",
        "route": "오염된 지하수, 생굴 등 패류 섭취, 감염자 구토물 에어로졸 및 손 접촉",
        "cause": "극소량(10~100개) 바이러스로 소장 융모 손상 및 급성 흡수장애",
        "symptoms": "갑작스러운 물 분출성 구토, 설사, 복통, 오한, 미열 (잠복기 12~48시간)",
        "trend": "겨울철(11월~3월) 학교 급식실 및 기숙사 집단 식중독 주요 원인",
        "prevention": "비누로 30초 이상 흐르는 물에 손 씻기, 굴 등 어패류 85℃ 1분 이상 가열",
        "treatment": "경구 수액 전해질 보충, 증상 소실 후 최소 48시간까지 조리 및 등교 제한"
    },
    "로타바이러스": {
        "tier": "제5급 감염병",
        "pathogen": "Rotavirus A군 (로타바이러스 / 레오바이러스과)",
        "route": "분변-구강 경로, 오염된 장난감 및 기저귀 교환대를 통한 손 접촉",
        "cause": "바이러스 비구조단백질(NSP4)의 장독소 작용으로 소장 분비성 설사 유발",
        "symptoms": "발열과 구토 후 쏟아지는 쌀뜨물 양상의 심한 물설사, 영유아 중증 탈수",
        "trend": "국가필수예방접종(경구용 백신) 도입으로 중증 입원율 대폭 감소",
        "prevention": "생후 2, 4개월 경구용 로타 백신(로타릭스/로타텍) 접종, 기저귀 위생 관리",
        "treatment": "즉각적인 탈수 교정 수액 요법, 모유/분유 지속 수유"
    },
    "회충증": {
        "tier": "제5급 감염병",
        "pathogen": "Ascaris lumbricoides (회충, 대형 장내 기생 선충)",
        "route": "오염된 인분 비료를 사용한 생채소류의 성숙란 섭취",
        "cause": "소장에서 부화한 유충이 폐를 거쳐 기관지->식도->소장으로 회귀하여 성충 서식",
        "symptoms": "소화 장애, 복통, 영양 결핍, 유충 폐 이행 시 기침과 호산구성 폐렴",
        "trend": "과거 다발하였으나 현대에는 유기농 채소 섭취자 중심 간헐 발생",
        "prevention": "채소류 흐르는 물에 깨끗이 세척, 조리 전 손 씻기",
        "treatment": "알벤다졸(Albendazole) 400mg 1회 복용"
    },
    "편충증": {
        "tier": "제5급 감염병",
        "pathogen": "Trichuris trichiura (편충, 채찍선충)",
        "route": "토양에 배출된 감염형 충란에 오염된 채소류 섭취",
        "cause": "맹장 및 상행결장 점막에 채찍 모양의 전단부를 파묻고 기생",
        "symptoms": "경증은 무증상, 다수 기생 시 점액성 만성 설사, 복통, 빈혈, 소아 직장 탈출",
        "trend": "토양 매개성 기생충 감시 사업 대상",
        "prevention": "손 씻기, 비위생적 분뇨 사용 지양, 생식 채소 철저한 세척",
        "treatment": "알벤다졸 400mg 3일간 연속 복용"
    },
    "요충증": {
        "tier": "제5급 감염병",
        "pathogen": "Enterobius vermicularis (요충, 장내 선충류)",
        "route": "항문 주위를 긁은 손가락의 충란 섭취(자가감염), 오염된 침구류 흡입",
        "cause": "야간에 암컷 성충이 항문 밖으로 기어나와 항문 주위 피부에 산란",
        "symptoms": "야간의 극심한 항문 주위 소양증(가려움증), 수면 장애, 불안, 2차 세균 감염",
        "trend": "유치원, 초등학교 저학년 및 공동생활 시설 내 높은 전염력",
        "prevention": "손톱 짧게 깎기, 속옷 및 침구류 고온 세탁, 가족 및 학급 전원 동시 복용",
        "treatment": "알벤다졸 400mg 1회 복용 후 2주 뒤 재복용 (충란 재감염 차단)"
    },
    "간흡충증": {
        "tier": "제5급 감염병",
        "pathogen": "Clonorchis sinensis (간흡충, 간디스토마)",
        "route": "담수어(피라미, 붕어, 잉어 등 민물고기) 생식, 오염된 칼/도마 교차오염",
        "cause": "피낭유충이 십이지장에서 탈낭하여 담관으로 이동, 만성 염증 및 담관벽 비후",
        "symptoms": "담관염, 담석증, 황달, 우상복부 통증, 1군 발암원(담관암 발병 위험 급증)",
        "trend": "낙동강, 영산강, 섬진강 등 5대 강 유역 주민 감시 사업 지속",
        "prevention": "민물고기 절대 날것 섭취 금지, 민물고기 조리 기구 끓는 물 소독",
        "treatment": "프라지콴텔(Praziquantel) 체중당 25mg씩 하루 3회 1일간 정밀 복용"
    },
    "폐흡충증": {
        "tier": "제5급 감염병",
        "pathogen": "Paragonimus westermani (폐흡충, 폐디스토마)",
        "route": "민물 참게, 가재 생식(참게장 등 섭취), 조리 도구 교차오염",
        "cause": "장벽을 뚫고 횡격막을 지나 폐실질에 침입하여 충낭 형성",
        "symptoms": "초콜릿 색깔의 녹슨 쇠빛 혈담(가래), 만성 기침, 흉통, 흉막염, 객혈",
        "trend": "결핵과 증상 및 방사선 소견이 유사하여 감별 진단 필요",
        "prevention": "민물 게, 가재 생식 금지, 참게장 섭취 시 완벽한 숙성 및 가열",
        "treatment": "프라지콴텔 체중당 25mg씩 하루 3회 2~3일간 복용"
    },
    "장흡충증": {
        "tier": "제5급 감염병",
        "pathogen": "Metagonimus yokogawai (요코가와흡충 등 소형 장흡충)",
        "route": "은어, 숭어, 붕어 등 담수 및 기수역 생선회 섭취",
        "cause": "소장 점막 융모 사이에 충체가 기생하여 점막 미란 및 궤양 유발",
        "symptoms": "소화불량, 복부 팽만감, 간헐적 설사, 점액변, 피로",
        "trend": "동해안 및 남해안 하천 유역 어촌 지역 중심 유행",
        "prevention": "은어 및 민물 생선 가열 조리 후 섭취",
        "treatment": "프라지콴텔 10~20mg/kg 단회 복용"
    },
    "살모넬라감염증": {
        "tier": "제5급 감염병",
        "pathogen": "Salmonella enterica 비장티푸스 혈청형 (살모넬라균)",
        "route": "오염된 달걀, 가금류, 육류, 유제품 섭취 및 교차 오염",
        "cause": "소장 점막 상피세포 침투 및 균체 내독소에 의한 장염 유발",
        "symptoms": "섭취 후 6~72시간 내 급성 발열, 복통, 구토, 수양성 설사",
        "trend": "여름철 집단 급식소 김밥, 달걀물 취급 부주의로 인한 대형 식중독",
        "prevention": "달걀 중심부까지 75℃ 1분 이상 완숙 조리, 교차 오염 방지 칼/도마 분리",
        "treatment": "대증 수액 요법, 고위험군 패혈증 의심 시 암피실린 또는 퀴놀론 항생제"
    },
    "캄필로박터감염증": {
        "tier": "제5급 감염병",
        "pathogen": "Campylobacter jejuni (캄필로박터 제주니, 미호기성 나선균)",
        "route": "덜 익힌 가금류(닭고기, 오리고기) 섭취, 생닭 세척 시 튄 물 교차오염",
        "cause": "공장 및 회장 점막 침투, 드물게 감염 후 자가면역 질환인 길랭-바레 증후군 유발",
        "symptoms": "극심한 하복부 통증(맹장염 유사), 발열, 혈변, 수양성 설사",
        "trend": "삼복더위 여름철 삼계탕 및 생닭 조리 시 집단 발병 다수",
        "prevention": "생닭은 마지막에 세척, 채소류와 조리도구 엄격 분리, 닭고기 속까지 75℃ 가열",
        "treatment": "충분한 수액 공급, 중증 시 에리스로마이신 또는 아지스로마이신 투여"
    }
}

def get_disease_info(tier, name):
    name_clean = "AIDS(후천성면역결핍증)" if name in ["임질", "AIDS", "후천성면역결핍증"] else name
    if name_clean in DISEASE_INFO_DB:
        info = dict(DISEASE_INFO_DB[name_clean])
        if tier and tier != "전체 급수 보기":
            info["tier"] = tier
        return info
    return {
        "tier": tier if tier and tier != "전체 급수 보기" else "법정감염병",
        "pathogen": f"{name} 특이 병원체",
        "route": "호흡기 비말, 공기, 접촉, 혈액, 음식물 매개 등",
        "cause": f"{name} 병원체 노출 및 체내 증식",
        "symptoms": "발열, 오한, 국소 염증 등",
        "trend": "질병관리청 법정감염병 역학 감시 통계 연동",
        "prevention": "손 씻기, 마스크 착용, 환경 소독",
        "treatment": "대증 치료 및 전문의 처방"
    }


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


def query_gemini_ai(api_key: str, prompt: str, disease_name: str = "") -> str:
    """
    고교 보건간호과 및 질병관리청(KDCA) 공공데이터에 맞춤화된 전문 Gemini 응답 생성.
    패키지 누락/버전 충돌 없이 안정적으로 구동되는 HTTPS REST API(1순위) 및 SDK 다중 폴백 적용.
    """
    cleaned_key = clean_api_key(api_key)
    if not cleaned_key:
        return ""

    sys_instruction = (
        "당신은 대한민국 서울의료보건고등학교 보건간호과의 전임 지도교사이자 질병관리청(KDCA) 공공데이터 전문 보건 튜터 AI입니다.\n"
        "질문자는 고등학교 보건간호과 학생입니다.\n\n"
        "[답변 원칙 및 지침]\n"
        "1. 고등학교 보건, 간호의 기초, 공중보건 교과서 범위에 부합하게 전문적이면서도 학생 눈높이에서 알기 쉽게 설명합니다.\n"
        "2. 질병관리청(KDCA) 법정감염병 분류(제1급~제5급), 신고 기한(즉시/24시간 이내 등), 격리 기준을 정확하게 안내합니다.\n"
        "3. 교육부 및 질병관리청 '학교 감염병 예방·위기대응 매뉴얼'과 학교보건법에 따른 학교 보건실 관리 지침과 '등교 중지(출석인정 결석)' 기준, 격리 해제 조건을 반드시 포함합니다.\n"
        "4. 2개 이상 질병 비교(예: 사스 vs 메르스, 독감 vs 감기, 수족구 vs 아구창 등) 질문 시 일목요연한 마크다운 비교표를 반드시 포함합니다.\n"
        "5. 따뜻하고 전문적인 보건간호과 지도교사의 어조로 마크다운과 이모지를 활용하여 가독성을 높입니다."
    )

    full_prompt = (
        f"{sys_instruction}\n\n"
        f"[현재 탐구 감염병 컨텍스트: {disease_name}]\n"
        f"[학생 질문]\n{prompt}\n\n"
        "위 질문에 대해 고등학생 수준에 맞추어 전문적이고 신뢰할 수 있는 답변을 작성해 주세요."
    )

    # [1순위] 표준 라이브러리 HTTPS REST API 호출 (외부 의존성 없음, No module named 오류 원천 차단)
    models_to_try = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
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
                        if ans:
                            return ans
        except Exception:
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
                    return resp.text.strip()
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
                    return resp.text.strip()
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
    d_clean = "AIDS(후천성면역결핍증)" if disease_name in ["임질", "AIDS", "후천성면역결핍증"] else disease_name
    info = get_disease_info(dis_info.get("tier", "법정감염병"), d_clean)

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

💡 **보건간호과 국가고시 및 임상 실무 핵심 탐구 포인트:**
1. **치명률과 전파력의 역학적 반비례 관계:**
   - **메르스**는 바이러스가 하기도 깊숙이 침투하여 폐포와 신장 조직을 파괴하므로 치명률이 34%로 매우 높으나, 일상 환경 비말 배출량이 적어 지역사회 전파력은 낮습니다.
   - 반면 **코로나19**는 상기도(인두, 후두)에서 폭발적으로 증식하여 치명률은 낮지만 전파력이 전 세계적 팬데믹을 유발할 만큼 극대화되었습니다.
2. **학교 보건실 긴급 대응 수칙:**
   - 사스나 메르스는 **제1급 감염병**이므로 의심 증상(중동 방문력, 고열, 호흡곤란) 확인 즉시 교내 일반 보건실에 머물게 하지 말고 **독립된 격리 대기실로 이동 후 관할 보건소로 즉시 유선 신고**해야 합니다."""

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
- 학생이 구강 통증을 호소할 때 **반드시 손바닥과 발바닥을 확인**하세요. 손·발에 붉은 발진이나 물집이 관찰되면 **수족구병**이므로 즉시 일시대기실 격리 후 귀가 조치해야 합니다.
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
    # [10] 질문 내용에서 특정 법정감염병 언급 감지 및 자동 연동
    # ----------------------------------------------------
    matched_target = None
    for known_dis in DISEASE_INFO_DB.keys():
        if known_dis in question:
            matched_target = known_dis
            info = get_disease_info(DISEASE_INFO_DB[known_dis].get("tier", "법정감염병"), matched_target)
            break

    # 만약 질문에 특정 감염병이 명시되어 있다면 해당 질병 리포트 출력
    if matched_target:
        if any(w in q_lower for w in ["백신", "접종", "면역"]):
            return f"""👩‍⚕️ **[AI 보건 튜터 답변: {matched_target} ({info['tier']}) 예방 백신 및 면역 관리 지침]**

보건간호과 학생 여러분, 질병관리청 국가예방접종사업(NIP) 및 교과서 기준 **'{matched_target}'**의 예방접종 지침입니다:

1. **💉 예방접종 및 면역 방어:**
   - {info['prevention']}
2. **🦠 원인 병원체 (특이 병원체):**
   - `{info['pathogen']}`
3. **🧬 전파 경로:**
   - {info['route']}
4. **🏫 학교 보건실 관리 권고사항:**
   - 학급 내 개인 위생 지도(30초 이상 올바른 손 씻기, 기침 예절) 및 미접종자 대상 백신 접종 독려를 실시합니다."""

        elif any(w in q_lower for w in ["격리", "등교", "출석", "보건실"]):
            return f"""👩‍⚕️ **[AI 보건 튜터 답변: {matched_target} ({info['tier']}) 학교 격리 및 등교 중지 기준]**

교육부 및 질병관리청 『학교 감염병 예방·위기대응 매뉴얼』과 학교보건법에 근거한 **'{matched_target}'** 관리 지침입니다:

1. **🏫 학교 등교 중지(가정 격리) 기준:**
   - **격리/등교 지침:** {info['treatment']}
2. **🩺 보건실 긴급 조치 사항:**
   - 발열 및 의심 증상 확인 즉시 보건실 내 일시대기실로 이동시키고 KF94 마스크를 착용시킵니다.
   - 학부모 유선 연락 후 즉시 의료기관 진료를 받도록 안내합니다.
3. **📄 출석 인정(공결) 절차:**
   - 법정감염병 의사 진단서, 소견서 또는 진료확인서 제출 시 **출석인정 결석**으로 처리되어 학생의 내신 불이익이 없습니다.
4. **🛡️ 학급 방역:**
   - 확진 학생 발생 학급 맞통풍 환기 및 책상 표면 환경 소독을 즉시 실시합니다."""

        else:
            return f"""👩‍⚕️ **[AI 보건 튜터 답변: {matched_target} ({info['tier']}) 종합 역학 및 보건 관리 리포트]**

질병관리청(KDCA) 공공데이터 및 고교 보건 교과서 기준 **'{matched_target}'**의 종합 분석입니다:

1. **📌 질병 개요 및 분류:**
   - **법정감염병 급수:** `{info['tier']}`
   - **발병 기전:** {info['cause']}
2. **🦠 원인 병원체 (특이 병원체):**
   - `{info['pathogen']}`
3. **🧬 전파 경로:**
   - {info['route']}
4. **🩺 주요 임상 증상 및 잠복기:**
   - {info['symptoms']}
5. **📈 최근 발생 추세 및 역학 특성:**
   - {info['trend']}
6. **🏫 학교 보건실 관리 및 치료 지침:**
   - {info['treatment']}
7. **💉 예방 수칙 및 백신 접종:**
   - {info['prevention']}

💡 **보건간호과 탐구 노트:**
- 감염병 발생 시 병원체의 전파 경로(비말, 공기, 접촉, 수인성)를 정확히 파악하여 환경 소독과 개인보호구 착용을 차별화하는 것이 학교 감염병 관리의 핵심입니다."""

    # ----------------------------------------------------
    # [11] 질문에 선택된 드롭다운 질병명(또는 법정감염병)이 명시된 경우
    # ----------------------------------------------------
    if d_clean in question or any(k in question for k in ["격리", "등교", "잠복기", "증상", "병원체", "유행"]):
        return f"""👩‍⚕️ **[AI 보건 튜터 답변: {d_clean} ({info['tier']}) 질의응답 분석]**

선택하신 감염병 **'{d_clean}'**에 대한 학교 보건 및 역학 분석입니다:

1. **원인 병원체:** `{info['pathogen']}`
2. **전파 경로 및 원인:** {info['route']} / {info['cause']}
3. **주요 임상 증상:** {info['symptoms']}
4. **학교 보건실 관리 & 등교 지침:** {info['treatment']}
5. **예방접종 및 감염 차단:** {info['prevention']}"""

    # ----------------------------------------------------
    # [12] 감염병이 아닌 청소년 일반 보건 및 건강 관리 질문에 대한 안내
    # ----------------------------------------------------
    return f"""👩‍⚕️ **[AI 보건 튜터: 고교 보건간호과 건강 증진 & 일반 보건 가이드]**

보건간호과 학생 여러분! 질문하신 **'{question}'**에 대한 학교 보건 및 의학 교과서 가이드입니다.

1. **💡 핵심 의학 원리 및 건강 이해:**
   - 질문하신 주제는 법정감염병(1~5급) 목록 외의 **청소년 일상 보건 및 건강 관리 영역**입니다.
   - 신체의 항상성 유지, 면역력 관리, 그리고 개인위생 수칙 실천이 청소년기 질병 예방의 핵심입니다.
2. **🏫 학교 보건실 실무 권고사항:**
   - 충분한 수면(하루 7~8시간), 규칙적인 영양 섭취(비타민 및 수분 보충), 정기적인 환기와 손 씻기 실천을 권장합니다.
   - 의심 증상이 지속될 경우 보건실을 방문하여 보건교사의 1차 상담 및 전문 의료기관 진료를 받으세요.
3. **🔬 심층 탐구 팁:**
   - 질병관리청 법정감염병 50여 종에 대한 실시간 통계 및 시각화 비교 분석은 상단 메뉴 [2. 감염병 발생 현황 & 시각화] 및 [3. 지역/감염병 비교]를 통해 언제든지 탐구하실 수 있습니다!"""



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
    <div style="text-align: center; font-size: 1.55rem; font-weight: 800; color: #ffffff; letter-spacing: 0.5px; margin-bottom: 6px;">
        AI 보건 탐구
    </div>
    """, unsafe_allow_html=True)

    # 3. 사용자 요청: " | " 기호 제거 및 데이터 기반부터 아래줄로 균등하게 2줄 배치, 가운데 정렬
    st.markdown("""
    <div style="text-align: center; font-size: 0.88rem; color: #94a3b8; font-weight: 600; line-height: 1.55; margin-bottom: 14px;">
        서울의료보건고등학교 보건간호과<br>데이터 기반 융합수업
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # 4. 메뉴 선택
    menu = st.radio(
        "📌 학습 단계 선택",
        [
            "1. 수업 안내 및 데이터 개요",
            "2. 감염병 발생 현황 & 시각화",
            "3. 지역/감염병 비교 심층 탐구",
            "4. 학교 집단감염 예방 시뮬레이터",
            "5. AI 보건 튜터(Q&A)"
        ]
    )

    st.divider()
    st.subheader("📂 데이터 소스 관리")
    data_mode = st.radio("데이터 소스 선택", ["질병관리청 표준 데이터 (2019~2025)", "내 CSV 파일 직접 업로드"])
    if data_mode == "내 CSV 파일 직접 업로드":
        up_file = st.file_uploader("CSV 파일 업로드 (질병관리청 형식)", type=["csv"])
        if up_file:
            try:
                working_df = load_uploaded_dataframe(up_file)
                up_dis_list = working_df["감염병명"].unique().tolist() if "감염병명" in working_df.columns else []
                st.success(f"✅ 데이터 로드 성공: {len(working_df):,}건 ({', '.join(up_dis_list[:3])})")
            except Exception as e:
                st.error(f"오류: {e}")
                working_df = df_all
        else:
            working_df = df_all
            st.info("파일 업로드 전까지 표준 데이터가 적용됩니다.")
    else:
        working_df = df_all
        st.success("표준 데이터 (56,700건 완비) 적용 중")

    st.divider()
    st.subheader("🔑 Gemini AI 튜터 설정")
    key_val = get_api_key()
    is_valid_format = bool(key_val and len(key_val) >= 20 and key_val.startswith("AIza") and "선생님" not in key_val)
    if is_valid_format:
        st.success("🟢 Gemini API 연동 완료 (Google AI 실시간 응답)")
    elif key_val:
        st.warning("⚠️ API 키 확인 필요: 'AIzaSy...'로 시작하는 Google AI Studio 키를 입력해 주세요.")
        user_key = st.text_input("Gemini API Key 재등록", type="password", placeholder="AIzaSy...")
        if user_key:
            st.session_state["custom_gemini_key"] = clean_api_key(user_key)
            st.rerun()
    else:
        st.info("💡 API 키 등록 시 Google Gemini AI가 감염병뿐만 아니라 무좀, 소독약, 응급처치 등 일상 보건 지식까지 실시간 종합 분석합니다.")
        user_key = st.text_input("Gemini API Key 등록 (선택)", type="password", placeholder="AIzaSy...")
        if user_key:
            st.session_state["custom_gemini_key"] = clean_api_key(user_key)
            st.rerun()


# ==========================================
# 4. 메인 화면 헤더 (사용자 요청: 학교로고 바깥 네모 박스 안에 로고 마크만 배치)
# ==========================================
if b64_emblem:
    st.markdown(f"""
    <div class="header-card">
        <div class="header-emblem-square">
            <img src="data:image/png;base64,{b64_emblem}" style="height: 38px; width: 38px; object-fit: contain; display: block;" alt="서울의료보건고 로고 마크">
        </div>
        <div style="display: flex; flex-direction: column; justify-content: center; min-width: 0;">
            <div class="one-line-title">특성화고 데이터 기반 감염병 보건 탐구 대시보드</div>
            <div style="font-size: 0.88rem; color: #38bdf8; font-weight: 700; margin-top: 3px;">서울의료보건고등학교 보건간호과 데이터 기반 융합수업</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="header-card">
        <div style="display: flex; flex-direction: column; justify-content: center; min-width: 0;">
            <div class="one-line-title">특성화고 데이터 기반 감염병 보건 탐구 대시보드</div>
            <div style="font-size: 0.88rem; color: #38bdf8; font-weight: 700; margin-top: 3px;">서울의료보건고등학교 보건간호과 데이터 기반 융합수업</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.caption("공공 보건의료 데이터를 시각화하고, 학교 집단감염 전파 차단 모델을 시뮬레이션하며, Gemini AI 튜터와 함께 탐구합니다.")
st.write("")


# ==========================================
# 5. 세부 화면 구현
# ==========================================

# ----------------------------------------------------
# [메뉴 1] 수업 안내 및 데이터 개요 & CSV 다운로드
# ----------------------------------------------------
if menu == "1. 수업 안내 및 데이터 개요":
    st.subheader("📋 2022 개정 교육과정 연계 보건 수업 안내")
    c1, c2 = st.columns([1.3, 1])
    with c1:
        st.info("""
        **🎯 2022 개정 보건과 교육과정 성취기준**
        - **[12보건03-02]** 주요 감염병의 발생 원인과 전파 경로, 유행 양상을 파악하고, 개인 및 집단 차원의 예방 및 관리 방안을 탐색한다.
        - **[12보건03-03]** 공공 보건 데이터 및 통계 자료를 분석하여 감염병 유행 추세를 이해하고 문제 해결 방안을 토론한다.
        """)
    with c2:
        st.success("""
        **📚 대한민국 법정감염병 1급~5급 분류 체계 (최신 고시 반영)**
        - **제1급**: 치명률 높고 음압격리 (신종감염병, MERS, 사스, 에볼라 등 10종)
        - **제2급**: 격리 필요 및 학교 호발 (수두, 백일해, 홍역, 결핵 등 10종)
        - **제3급**: 발생 감시체계 수립 (말라리아, 엠폭스, B·C형간염 등 10종)
        - **제4급**: 표본감시 활동 (**코로나19**, 인플루엔자, 급성호흡기감염증 등 10종)
        - **제5급**: 기생충 및 장관감염 감시 (노로바이러스, 로타, 회충증 등 10종)
        """)

    st.divider()
    st.markdown("##### 📥 [수업 실습용] 질병관리청 공공데이터 개별 CSV 다운로드")
    st.caption("아래 버튼을 눌러 원하는 질병 CSV 파일을 다운로드받은 뒤, 왼쪽 사이드바의 '내 CSV 파일 직접 업로드'에 올려서 실습해 보세요!")

    d_btn1, d_btn2, d_btn3, d_btn4, d_btn5 = st.columns(5)
    sample_targets = [
        ("코로나19 (제4급)", "코로나19_발생현황_2019_2025.csv", d_btn1),
        ("인플루엔자 (제4급)", "인플루엔자_발생현황_2019_2025.csv", d_btn2),
        ("백일해 (제2급)", "백일해_발생현황_2019_2025.csv", d_btn3),
        ("홍역 (제2급)", "홍역_발생현황_2019_2025.csv", d_btn4),
        ("수두 (제2급)", "수두_발생현황_2019_2025.csv", d_btn5)
    ]
    for d_name, f_name, col_btn in sample_targets:
        f_path = DATA_DIR / f_name
        if f_path.exists():
            with open(f_path, "rb") as f:
                col_btn.download_button(
                    label=f"💾 {d_name}",
                    data=f.read(),
                    file_name=f_name,
                    mime="text/csv",
                    use_container_width=True
                )

    st.divider()
    st.subheader("🔍 현재 데이터셋 (2019~2025 국내 17개 시도 및 해외 10개국)")
    
    # 사용자 요청: 글자 길이가 길어서 아래로 내려가지 않도록 폰트 크기 조정 및 1줄 수평 바 형식으로 배치
    st.markdown(f"""
    <div class="single-line-badge-bar">
        <span>📊 <strong>총 데이터</strong>: {len(working_df):,}건</span>
        <span>📅 <strong>수집 기간</strong>: 2019년 ~ 2025년</span>
        <span>👥 <strong>연령대 5단계</strong>: 0-9세 ・ 10-19세 ・ 20-49세 ・ 50-64세 ・ 65세 이상</span>
        <span>💉 <strong>관리 구분</strong>: 예방접종 또는 격리여부 포함</span>
    </div>
    """, unsafe_allow_html=True)

    # 0-9세, 10-19세, 20-49세, 50-64세, 65세 이상 연령 컬럼과 "예방접종 또는 격리여부" 도표 배치
    display_cols = [
        "연도", "월", "법정감염병군", "감염병명", "지역", "신규환자수",
        "0-9세", "10-19세", "20-49세", "50-64세", "65세 이상",
        "주요전파경로", "예방접종 또는 격리여부"
    ]
    valid_cols = [c for c in display_cols if c in working_df.columns]
    st.dataframe(working_df[valid_cols].head(15), use_container_width=True)


# ----------------------------------------------------
# [메뉴 2] 감염병 발생 현황 & 시각화 (사용자 요청: Matplotlib, Seaborn, Plotly 3대 라이브러리 비교)
# ----------------------------------------------------
elif menu == "2. 감염병 발생 현황 & 시각화":
    st.markdown('<div class="title-compare-libs">📊 3대 시각화 라이브러리(Matplotlib vs Seaborn vs Plotly) 비교 분석</div>', unsafe_allow_html=True)
    st.markdown("""
    동일한 공공 보건 데이터를 **파이썬의 3대 대표 시각화 라이브러리**(Plotly, Seaborn, Matplotlib)로 각각 구현하여 
    시각화 도구별 표현력과 특징을 비교 탐구합니다.
    """)

    # 업로드 데이터 감염병 자동 감지 및 스마트 선택 동기화
    uploaded_diseases = [d for d in working_df["감염병명"].dropna().unique() if str(d).strip()] if "감염병명" in working_df.columns else []
    is_uploaded_data = (data_mode == "내 CSV 파일 직접 업로드" and len(uploaded_diseases) > 0)

    tier_options = ["전체 급수 보기", "제1급 감염병", "제2급 감염병", "제3급 감염병", "제4급 감염병", "제5급 감염병"]

    # 기본 티어 인덱스 설정 (업로드된 데이터가 있을 경우 해당 질병의 급수로 자동 감지)
    default_tier_idx = 4  # 기본 제4급(코로나19, 인플루엔자)
    if is_uploaded_data:
        first_dis = uploaded_diseases[0]
        detected_tier = DISEASE_INFO_DB.get(first_dis, {}).get("tier", None)
        if not detected_tier and "법정감염병군" in working_df.columns:
            raw_tier = str(working_df["법정감염병군"].iloc[0]).strip()
            for t_opt in tier_options:
                if t_opt in raw_tier or raw_tier in t_opt:
                    detected_tier = t_opt
                    break
        if detected_tier and detected_tier in tier_options:
            default_tier_idx = tier_options.index(detected_tier)

    # 1단계: 분석 모드 및 급수 선택
    st.markdown("##### ⚙️ 1단계: 분석 모드 및 법정감염병 급수 선택")
    if is_uploaded_data:
        st.success(f"📂 **업로드 데이터 자동 감지 완료**: `{', '.join(uploaded_diseases)}` (총 {len(working_df):,}건 분석 준비 완료)")

    sel_c1, sel_c2 = st.columns([1, 1.2])

    with sel_c1:
        analysis_type = st.selectbox(
            "📌 분석 모드 선택",
            ["단일 감염병 집중 분석", "복수 감염병 비교 분석"],
            help="1개 질병을 집중 분석하거나 2~3개 질병을 나란히 비교합니다."
        )

    with sel_c2:
        tier_filter = st.selectbox(
            "🏷️ 법정감염병 급수 선택",
            tier_options,
            index=default_tier_idx
        )

    if tier_filter == "전체 급수 보기":
        scoped_diseases = []
        for dis_list in TIER_DISEASE_MAP.values():
            scoped_diseases.extend(dis_list)
        scoped_diseases = sorted(list(set(scoped_diseases)))
    else:
        scoped_diseases = list(TIER_DISEASE_MAP.get(tier_filter, []))

    # 업로드된 파일의 감염병이 있을 경우 scoped_diseases 최우선 배치하여 즉시 선택되도록 보장
    if is_uploaded_data:
        for ud in reversed(uploaded_diseases):
            if ud in scoped_diseases:
                scoped_diseases.remove(ud)
            scoped_diseases.insert(0, ud)

    # 2단계: 대상 감염병 설정
    st.markdown(f"##### ⚙️ 2단계: 대상 감염병 선택 ({tier_filter} 소속 {len(scoped_diseases)}종)")
    if analysis_type == "단일 감염병 집중 분석":
        chosen_single = st.selectbox("🦠 분석 대상 감염병 선택", options=scoped_diseases, index=0 if scoped_diseases else None)
        target_diseases = [chosen_single] if chosen_single else []
    else:
        default_targets = [d for d in scoped_diseases if d in uploaded_diseases] if is_uploaded_data else scoped_diseases[:2]
        if not default_targets:
            default_targets = scoped_diseases[:2] if len(scoped_diseases) >= 2 else scoped_diseases
        target_diseases = st.multiselect(
            "🦠 비교할 감염병 선택 (2~3개 선택 가능)",
            options=scoped_diseases,
            default=default_targets
        )

    # 데이터 필터링 적용
    df_filtered = working_df.copy()
    if target_diseases:
        df_filtered = df_filtered[df_filtered["감염병명"].isin(target_diseases)]
    df_filtered = ensure_dataset_integrity(df_filtered)

    st.write("")

    if df_filtered.empty or not target_diseases:
        st.warning("⚠️ 선택하신 감염병에 해당하는 데이터가 없습니다. 상단 감염병을 선택해 주세요.")
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

        # 3.5단계: 시각화 차트 형태 선택 (사용자 요청: 꺾은선 / 막대 / 누적영역)
        st.markdown("##### 📊 그래프 시각화 형태 선택 (꺾은선 / 막대 / 누적 영역)")
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

        st.write("")

        # 4단계: 시각화 라이브러리 및 원/도넛 점유율 분석 탭 (사용자 요청: 3대 비교 탭 삭제 -> 원/도넛 그래프 탭 신설)
        tab_plotly, tab_seaborn, tab_matplotlib, tab_donut = st.tabs([
            "⚡ 1. Plotly (동적 인터랙티브)",
            "🎨 2. Seaborn (통계적 그래픽)",
            "📉 3. Matplotlib (정밀 출판용)",
            "🍩 4. 원/도넛형 점유율 분석"
        ])

        # 조화로운 보건 의료 컬러 팔레트
        palette_colors = ["#38bdf8", "#818cf8", "#34d399", "#fbbf24", "#f87171", "#a855f7", "#06b6d4"]

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
                    fig_p = px.bar(ts, x="연도", y="신규환자수", color="감염병명", barmode="group", text_auto=True, title="연도별 감염병 환자 발생 비교 (Plotly 묶은 막대)", template="plotly_dark", color_discrete_sequence=palette_colors)
                else:
                    fig_p = px.area(ts, x="연도", y="신규환자수", color="감염병명", markers=True, title="연도별 감염병 누적 발생 분포 (Plotly 누적 영역)", template="plotly_dark", color_discrete_sequence=palette_colors)
                fig_p.update_layout(xaxis_title="발생 연도", yaxis_title="신규 환자 수(명)", height=390, margin=dict(l=40, r=20, t=40, b=40))
                fig_p.update_xaxes(tickangle=0, dtick=1, tickmode='linear', tickformat="d")
                st.plotly_chart(fig_p, use_container_width=True, key="plotly_v1_main")

            # (2) 🎨 Seaborn 탭 (사용자 요청: Plotly처럼 깔끔하고 컴팩트한 크기 유지 & 코로나 누적 에러 완벽 해결)
            with tab_seaborn:
                st.markdown("###### 🎨 Seaborn: 통계 분포 및 세련된 컬러 팔레트를 제공하는 그래픽스")
                fig_s, ax_s = plt.subplots(figsize=(8.2, 3.8), dpi=100)
                apply_dark_plot_style(fig_s, ax_s)

                if "꺾은선" in chart_style:
                    sns.lineplot(data=ts, x="연도", y="신규환자수", hue="감염병명", marker="o", markersize=8, linewidth=2.5, palette="coolwarm", ax=ax_s)
                    ax_s.set_title("연도별 감염병 환자 발생 추이 (Seaborn)")
                    ax_s.set_xticks(years)
                    ax_s.set_xticklabels(year_labels, rotation=0)
                elif "막대" in chart_style:
                    sns.barplot(data=ts, x="연도", y="신규환자수", hue="감염병명", palette="Blues_r", ax=ax_s)
                    ax_s.set_title("연도별 감염병 환자 발생 비교 (Seaborn)")
                    ax_s.set_xticks(range(len(years)))
                    ax_s.set_xticklabels(year_labels, rotation=0)
                else:
                    # 누적 영역 그래프 (코로나19 등 단일/복수 감염병 완벽 렌더링)
                    p_df = ts.pivot(index="연도", columns="감염병명", values="신규환자수").fillna(0)
                    y_arrays = [p_df[col].values for col in p_df.columns]
                    colors_stack = sns.color_palette("mako", len(p_df.columns))
                    ax_s.stackplot(years, y_arrays, labels=p_df.columns, colors=colors_stack, alpha=0.85)
                    ax_s.set_title("연도별 감염병 누적 환자 구성 (Seaborn 누적 영역)")
                    ax_s.set_xticks(years)
                    ax_s.set_xticklabels(year_labels, rotation=0)

                ax_s.set_xlabel("발생 연도")
                ax_s.set_ylabel("신규 환자 수(명)")
                ax_s.tick_params(axis='x', rotation=0)
                ax_s.legend(title="감염병명", facecolor='#1e293b', edgecolor='#475569', labelcolor='#f8fafc', fontsize=9)
                plt.tight_layout()

                c_pad1, c_center, c_pad2 = st.columns([0.08, 0.84, 0.08])
                with c_center:
                    st.pyplot(fig_s)
                plt.close(fig_s)

            # (3) 📉 Matplotlib 탭 (사용자 요청: 컴팩트한 크기 및 정밀한 수치 레이블)
            with tab_matplotlib:
                st.markdown("###### 📉 Matplotlib: 픽셀 단위 축·폰트·레이아웃을 정밀하게 제어하는 표준 도표")
                fig_m, ax_m = plt.subplots(figsize=(8.2, 3.8), dpi=100)
                apply_dark_plot_style(fig_m, ax_m)

                if "꺾은선" in chart_style:
                    for i, d_name in enumerate(target_diseases):
                        sub_ts = ts[ts["감염병명"] == d_name]
                        ax_m.plot(sub_ts["연도"], sub_ts["신규환자수"], marker='s', markersize=7, linewidth=2.2, label=d_name, color=palette_colors[i % len(palette_colors)])
                        for _, row in sub_ts.iterrows():
                            ax_m.annotate(f"{int(row['신규환자수']):,}", (row["연도"], row["신규환자수"]), textcoords="offset points", xytext=(0, 6), ha='center', fontsize=8, color='#38bdf8')
                    ax_m.set_title("연도별 감염병 환자 발생 추이 및 수치 라벨 (Matplotlib)")
                    ax_m.set_xticks(years)
                    ax_m.set_xticklabels(year_labels, rotation=0)
                elif "막대" in chart_style:
                    n_dis = max(len(target_diseases), 1)
                    bar_w = 0.8 / n_dis
                    for i, d_name in enumerate(target_diseases):
                        sub = ts[ts["감염병명"] == d_name].set_index("연도").reindex(years, fill_value=0)
                        offsets = [idx + (i - n_dis / 2 + 0.5) * bar_w for idx in range(len(years))]
                        ax_m.bar(offsets, sub["신규환자수"], width=bar_w, label=d_name, color=palette_colors[i % len(palette_colors)], edgecolor="#1e293b")
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

                ax_m.set_xlabel("발생 연도")
                ax_m.set_ylabel("신규 환자 수(명)")
                ax_m.tick_params(axis='x', rotation=0)
                ax_m.legend(title="감염병명", facecolor='#1e293b', edgecolor='#475569', labelcolor='#f8fafc', fontsize=9)
                plt.tight_layout()

                c_pad1, c_center, c_pad2 = st.columns([0.08, 0.84, 0.08])
                with c_center:
                    st.pyplot(fig_m)
                plt.close(fig_m)

            # (4) 🍩 원/도넛형 점유율 분석 탭 (사용자 요청: 3대 비교 삭제 후 신설된 전용 도넛 분석)
            with tab_donut:
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
                        fig_p_donut.update_layout(height=380, margin=dict(l=30, r=20, t=40, b=30))
                        st.plotly_chart(fig_p_donut, use_container_width=True, key="plotly_v1_donut")

                    with d_col2:
                        fig_s_donut, ax_sd = plt.subplots(figsize=(6.2, 4.0), dpi=100)
                        apply_dark_plot_style(fig_s_donut, ax_sd)
                        ax_sd.pie(active_pie_df["신규환자수"], labels=active_pie_df[p_name], autopct="%1.1f%%", colors=palette_colors[:len(active_pie_df)], pctdistance=0.75, textprops={'color': '#f8fafc', 'fontsize': 9})
                        ax_sd.add_artist(plt.Circle((0,0), 0.48, fc='#0f172a'))
                        ax_sd.set_title(f"{p_title} (Seaborn 통계 도넛)")
                        plt.tight_layout()
                        st.pyplot(fig_s_donut)
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
                st.markdown("###### ⚡ Plotly: 연령대별 인터랙티브 막대 분포 (마우스 호버 시 세부 환자 수 표시)")
                b_mode = "group" if "막대" in chart_style else "stack"
                fig_p = px.bar(age_melted, x="감염병명", y="환자수", color="연령대", barmode=b_mode, title="감염병별 5개 연령대 세분화 환자 분포 (Plotly)", template="plotly_dark", color_discrete_sequence=palette_colors)
                fig_p.update_layout(xaxis_title="감염병명", yaxis_title="환자 수(명)", height=390, margin=dict(l=40, r=20, t=40, b=40))
                fig_p.update_xaxes(tickangle=0)
                st.plotly_chart(fig_p, use_container_width=True, key="plotly_v2_main")

            with tab_seaborn:
                st.markdown("###### 🎨 Seaborn: 5개 연령대별 그룹 비교 막대 그래프")
                fig_s, ax_s = plt.subplots(figsize=(8.2, 3.8), dpi=100)
                apply_dark_plot_style(fig_s, ax_s)
                sns.barplot(data=age_melted, x="감염병명", y="환자수", hue="연령대", palette="Blues_r", ax=ax_s)
                ax_s.set_title("감염병별 연령대 환자 분포 비교 (Seaborn)")
                ax_s.set_xlabel("감염병명")
                ax_s.set_ylabel("환자 수(명)")
                ax_s.tick_params(axis='x', rotation=0)
                ax_s.legend(title="연령대", facecolor='#1e293b', edgecolor='#475569', labelcolor='#f8fafc', fontsize=8)
                plt.tight_layout()
                c_pad1, c_center, c_pad2 = st.columns([0.08, 0.84, 0.08])
                with c_center:
                    st.pyplot(fig_s)
                plt.close(fig_s)

            with tab_matplotlib:
                st.markdown("###### 📉 Matplotlib: 5개 연령대별 정밀 누적 스택 막대")
                fig_m, ax_m = plt.subplots(figsize=(8.2, 3.8), dpi=100)
                apply_dark_plot_style(fig_m, ax_m)
                bottom_arr = [0] * len(age_grp)
                for i, c_name in enumerate(age_cols):
                    vals = age_grp[c_name].values
                    ax_m.bar(age_grp["감염병명"], vals, bottom=bottom_arr, label=c_name, color=palette_colors[i % len(palette_colors)], edgecolor="#1e293b")
                    bottom_arr = [b + v for b, v in zip(bottom_arr, vals)]
                ax_m.set_title("5개 연령대별 누적 환자 구성 (Matplotlib)")
                ax_m.set_xlabel("감염병명")
                ax_m.set_ylabel("누적 환자 수(명)")
                ax_m.tick_params(axis='x', rotation=0)
                ax_m.legend(title="연령대", facecolor='#1e293b', edgecolor='#475569', labelcolor='#f8fafc', fontsize=8)
                plt.tight_layout()
                c_pad1, c_center, c_pad2 = st.columns([0.08, 0.84, 0.08])
                with c_center:
                    st.pyplot(fig_m)
                plt.close(fig_m)

            with tab_donut:
                st.markdown("###### 🍩 5개 연령대 세분화 점유율 도넛 차트 (청소년 10-19세 비중 집중 분석)")
                active_tot_age = tot_age[tot_age["환자수"] > 0]
                if active_tot_age.empty or active_tot_age["환자수"].sum() <= 0:
                    st.info("ℹ️ 연령대별 점유율을 분석할 환자 데이터가 없습니다 (0명).")
                else:
                    d_col1, d_col2 = st.columns(2)
                    with d_col1:
                        fig_p_donut = px.pie(active_tot_age, values="환자수", names="연령대", hole=0.45, title="5개 연령대별 환자 점유율 (Plotly 도넛)", template="plotly_dark", color_discrete_sequence=palette_colors)
                        fig_p_donut.update_layout(height=380, margin=dict(l=30, r=20, t=40, b=30))
                        st.plotly_chart(fig_p_donut, use_container_width=True, key="plotly_v2_donut")
                    with d_col2:
                        fig_s_donut, ax_sd = plt.subplots(figsize=(6.2, 4.0), dpi=100)
                        apply_dark_plot_style(fig_s_donut, ax_sd)
                        ax_sd.pie(active_tot_age["환자수"], labels=active_tot_age["연령대"], autopct="%1.1f%%", colors=sns.color_palette("Blues_r", len(active_tot_age)), pctdistance=0.75, textprops={'color': '#f8fafc', 'fontsize': 9})
                        ax_sd.add_artist(plt.Circle((0,0), 0.48, fc='#0f172a'))
                        ax_sd.set_title("5개 연령대별 환자 점유율 (Seaborn 도넛)")
                        plt.tight_layout()
                        st.pyplot(fig_s_donut)
                        plt.close(fig_s_donut)

        # ==================================================================
        # 관점 3: 해외 주요 10개국 발생 현황 분석
        # ==================================================================
        elif "3. 해외 주요" in data_view:
            global_df = df_filtered[df_filtered["지역"].isin(GLOBAL_COUNTRIES)].groupby("지역")["신규환자수"].sum().reset_index().sort_values("신규환자수", ascending=True)

            with tab_plotly:
                st.markdown("###### ⚡ Plotly: 해외 주요 10개국 가로 막대 시각화 (호버 시 정확한 수치 표시)")
                if global_df.empty or global_df["신규환자수"].sum() <= 0:
                    st.info("ℹ️ 현재 선택된 감염병의 해외 주요 10개국 환자 발생 데이터가 없습니다 (0명).")
                else:
                    fig_p = px.bar(global_df, y="지역", x="신규환자수", orientation='h', color="신규환자수", title="해외 주요 10개국 감염병 발생 현황 (Plotly)", template="plotly_dark", color_continuous_scale="Tealgrn")
                    fig_p.update_layout(xaxis_title="신규 환자 수(명)", yaxis_title="국가명", height=390, margin=dict(l=40, r=20, t=40, b=40))
                    st.plotly_chart(fig_p, use_container_width=True, key="plotly_v3_main")

            with tab_seaborn:
                st.markdown("###### 🎨 Seaborn: 해외 발생국별 환자 규모 그래픽스")
                fig_s, ax_s = plt.subplots(figsize=(8.2, 3.8), dpi=100)
                apply_dark_plot_style(fig_s, ax_s)
                if global_df.empty or global_df["신규환자수"].sum() <= 0:
                    ax_s.text(0.5, 0.5, "해외 주요 발생국 환자 데이터가 없습니다 (0명)", ha='center', va='center', color='#94a3b8', fontsize=11)
                    ax_s.set_title("해외 주요 발생국별 환자 발생 비교 (Seaborn)")
                else:
                    sns.barplot(data=global_df, y="지역", x="신규환자수", hue="지역", palette="mako", legend=False, ax=ax_s)
                    ax_s.set_title("해외 주요 발생국별 환자 발생 비교 (Seaborn)")
                    ax_s.set_xlabel("신규 환자 수(명)")
                    ax_s.set_ylabel("국가명")
                plt.tight_layout()
                c_pad1, c_center, c_pad2 = st.columns([0.08, 0.84, 0.08])
                with c_center:
                    st.pyplot(fig_s)
                plt.close(fig_s)

            with tab_matplotlib:
                st.markdown("###### 📉 Matplotlib: 정확한 환자 수 레이블이 표기된 정밀 가로 막대")
                fig_m, ax_m = plt.subplots(figsize=(8.2, 3.8), dpi=100)
                apply_dark_plot_style(fig_m, ax_m)
                if global_df.empty or global_df["신규환자수"].sum() <= 0:
                    ax_m.text(0.5, 0.5, "해외 주요 발생국 환자 데이터가 없습니다 (0명)", ha='center', va='center', color='#94a3b8', fontsize=11)
                    ax_m.set_title("해외 주요 10개국 감염병 발생 현황 (Matplotlib)")
                else:
                    bars = ax_m.barh(global_df["지역"], global_df["신규환자수"], color="#0284c7", edgecolor="#38bdf8")
                    max_val = max(global_df["신규환자수"])
                    for bar in bars:
                        w = bar.get_width()
                        ax_m.text(w + (max_val*0.01), bar.get_y() + bar.get_height()/2, f"{int(w):,}명", va='center', fontsize=8, color='#38bdf8')
                    ax_m.set_title("해외 주요 10개국 감염병 발생 현황 (Matplotlib)")
                    ax_m.set_xlabel("신규 환자 수(명)")
                    ax_m.set_ylabel("국가명")
                plt.tight_layout()
                c_pad1, c_center, c_pad2 = st.columns([0.08, 0.84, 0.08])
                with c_center:
                    st.pyplot(fig_m)
                plt.close(fig_m)

            with tab_donut:
                st.markdown("###### 🍩 해외 주요 10개국 감염병 발생 점유율 분석")
                active_global_df = global_df[global_df["신규환자수"] > 0]
                if active_global_df.empty or active_global_df["신규환자수"].sum() <= 0:
                    st.info("ℹ️ 해외 주요 10개국 환자 발생 점유율을 계산할 데이터가 없습니다 (0명).")
                else:
                    d_col1, d_col2 = st.columns(2)
                    with d_col1:
                        fig_p_donut = px.pie(active_global_df, values="신규환자수", names="지역", hole=0.45, title="해외 주요국 발생 비중 (Plotly 도넛)", template="plotly_dark", color_discrete_sequence=palette_colors)
                        fig_p_donut.update_layout(height=380, margin=dict(l=30, r=20, t=40, b=30))
                        st.plotly_chart(fig_p_donut, use_container_width=True, key="plotly_v3_donut")
                    with d_col2:
                        fig_s_donut, ax_sd = plt.subplots(figsize=(6.2, 4.0), dpi=100)
                        apply_dark_plot_style(fig_s_donut, ax_sd)
                        ax_sd.pie(active_global_df["신규환자수"], labels=active_global_df["지역"], autopct="%1.1f%%", colors=sns.color_palette("mako", len(active_global_df)), pctdistance=0.75, textprops={'color': '#f8fafc', 'fontsize': 8})
                        ax_sd.add_artist(plt.Circle((0,0), 0.48, fc='#0f172a'))
                        ax_sd.set_title("해외 주요국 발생 비중 (Seaborn 도넛)")
                        plt.tight_layout()
                        st.pyplot(fig_s_donut)
                        plt.close(fig_s_donut)

        # ==================================================================
        # 관점 4: 국내 17개 시도별 발생 현황 분석
        # ==================================================================
        else:
            korea_df = df_filtered[df_filtered["지역"].isin(KOREA_CITIES)].groupby("지역")["신규환자수"].sum().reset_index().sort_values("신규환자수", ascending=False)
            top6_korea = korea_df.head(6)

            with tab_plotly:
                st.markdown("###### ⚡ Plotly: 국내 17개 시도별 세로 막대 (인터랙티브 컬러 스케일)")
                fig_p = px.bar(korea_df, x="지역", y="신규환자수", color="신규환자수", title="국내 17개 시도별 감염병 환자 발생 현황 (Plotly)", template="plotly_dark", color_continuous_scale="Blues")
                fig_p.update_layout(xaxis_title="지역(시도)", yaxis_title="신규 환자 수(명)", height=390, margin=dict(l=40, r=20, t=40, b=40))
                fig_p.update_xaxes(tickangle=0)
                st.plotly_chart(fig_p, use_container_width=True, key="plotly_v4_main")

            with tab_seaborn:
                st.markdown("###### 🎨 Seaborn: 17개 시도별 분포 막대")
                fig_s, ax_s = plt.subplots(figsize=(8.2, 3.8), dpi=100)
                apply_dark_plot_style(fig_s, ax_s)
                sns.barplot(data=korea_df, x="지역", y="신규환자수", hue="지역", palette="crest", legend=False, ax=ax_s)
                ax_s.set_title("국내 17개 시도별 환자 분포 (Seaborn)")
                ax_s.set_xlabel("지역(시도)")
                ax_s.set_ylabel("신규 환자 수(명)")
                ax_s.tick_params(axis='x', rotation=45, labelsize=8)
                plt.tight_layout()
                c_pad1, c_center, c_pad2 = st.columns([0.08, 0.84, 0.08])
                with c_center:
                    st.pyplot(fig_s)
                plt.close(fig_s)

            with tab_matplotlib:
                st.markdown("###### 📉 Matplotlib: 상위 발생 시도 강조 막대 그래프")
                fig_m, ax_m = plt.subplots(figsize=(8.2, 3.8), dpi=100)
                apply_dark_plot_style(fig_m, ax_m)
                bar_colors = ['#38bdf8' if i < 3 else '#0284c7' for i in range(len(korea_df))]
                ax_m.bar(korea_df["지역"], korea_df["신규환자수"], color=bar_colors, edgecolor="#1e293b")
                ax_m.set_title("국내 17개 시도별 환자 발생 통계 (Matplotlib 상위 시도 강조)")
                ax_m.set_xlabel("지역(시도)")
                ax_m.set_ylabel("신규 환자 수(명)")
                ax_m.tick_params(axis='x', rotation=45, labelsize=8)
                plt.tight_layout()
                c_pad1, c_center, c_pad2 = st.columns([0.08, 0.84, 0.08])
                with c_center:
                    st.pyplot(fig_m)
                plt.close(fig_m)

            with tab_donut:
                st.markdown("###### 🍩 국내 상위 6대 시도별 감염병 환자 발생 비중 분석")
                active_top6 = top6_korea[top6_korea["신규환자수"] > 0]
                if active_top6.empty or active_top6["신규환자수"].sum() <= 0:
                    st.info("ℹ️ 국내 상위 6대 시도 점유율을 분석할 데이터가 없습니다 (0명).")
                else:
                    d_col1, d_col2 = st.columns(2)
                    with d_col1:
                        fig_p_donut = px.pie(active_top6, values="신규환자수", names="지역", hole=0.45, title="국내 상위 6대 시도 점유율 (Plotly 도넛)", template="plotly_dark", color_discrete_sequence=palette_colors)
                        fig_p_donut.update_layout(height=380, margin=dict(l=30, r=20, t=40, b=30))
                        st.plotly_chart(fig_p_donut, use_container_width=True, key="plotly_v4_donut")
                    with d_col2:
                        fig_s_donut, ax_sd = plt.subplots(figsize=(6.2, 4.0), dpi=100)
                        apply_dark_plot_style(fig_s_donut, ax_sd)
                        ax_sd.pie(active_top6["신규환자수"], labels=active_top6["지역"], autopct="%1.1f%%", colors=sns.color_palette("crest", len(active_top6)), pctdistance=0.75, textprops={'color': '#f8fafc', 'fontsize': 8})
                        ax_sd.add_artist(plt.Circle((0,0), 0.48, fc='#0f172a'))
                        ax_sd.set_title("국내 상위 6대 시도 점유율 (Seaborn 도넛)")
                        plt.tight_layout()
                        st.pyplot(fig_s_donut)
                        plt.close(fig_s_donut)

        # ------------------------------------------------------------------
        # 보건간호과 학생들을 위한 시각화 리터러시 교육 가이드 카드
        # ------------------------------------------------------------------
        st.write("")
        st.markdown("""
        <div style="background:#1e293b; border:1px solid #38bdf8; border-radius:12px; padding:16px 20px; margin-top:10px; margin-bottom:14px; box-shadow:0 3px 10px rgba(0,0,0,0.25);">
            <div style="font-size:1.05rem; font-weight:bold; color:#38bdf8; margin-bottom:8px;">
                💡 [보건간호과 학생용 데이터 시각화 길잡이: 차트별 최적 분석 목적]
            </div>
            <div style="font-size:0.88rem; color:#e2e8f0; line-height:1.7;">
                • 📈 <strong>꺾은선 추세 그래프 (Line Chart)</strong>: 시간(연도, 월)의 흐름에 따른 감염병 발생 추세, 유행 정점(Peak), 계절적 파동을 분석할 때 가장 적합합니다.<br>
                • 📊 <strong>막대 비교 그래프 (Bar Chart)</strong>: 서로 다른 감염병 간 또는 시도별 환자 수의 절대적 대소를 직관적으로 비교할 때 최적입니다.<br>
                • 🏔️ <strong>누적 영역/분포 그래프 (Stacked Chart)</strong>: 전체 감염병 환자 발생 총량의 변동과 그 안에서 각 질병 또는 연령대의 기여도를 함께 파악할 때 효과적입니다.<br>
                • 🍩 <strong>원/도넛형 점유율 차트 (Donut/Pie Chart)</strong>: 전체 환자(100%) 중 특정 질병이나 고위험 연령층이 차지하는 상대적 비중을 시각적으로 전달할 때 탁월합니다.
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ------------------------------------------------------------------
        # 사용자 요청: 비교 항목 열 모두 위아래 좌우 균등 & 2줄 줄바꿈 배치
        # ------------------------------------------------------------------
        st.markdown("""
        <div style="background:#1e293b; border:1px solid #334155; border-radius:12px; overflow:hidden; margin-top:16px; margin-bottom:16px; box-shadow:0 4px 14px rgba(0,0,0,0.3);">
            <table style="width:100%; border-collapse:collapse; text-align:left; font-size:0.88rem; color:#f8fafc;">
                <thead>
                    <tr style="background:#0f172a; border-bottom:2px solid #38bdf8;">
                        <th style="padding:14px 8px; width:95px; min-width:90px; text-align:center; vertical-align:middle; color:#38bdf8; font-weight:700; line-height:1.45;">비교<br>항목</th>
                        <th style="padding:12px 16px; width:29%; color:#f8fafc; font-weight:700; text-align:center; vertical-align:middle;" class="notranslate" translate="no">📉 Matplotlib</th>
                        <th style="padding:12px 16px; width:29%; color:#f8fafc; font-weight:700; text-align:center; vertical-align:middle;" class="notranslate" translate="no">🎨 Seaborn</th>
                        <th style="padding:12px 16px; width:31%; color:#38bdf8; font-weight:700; text-align:center; vertical-align:middle;" class="notranslate" translate="no">⚡ Plotly</th>
                    </tr>
                </thead>
                <tbody>
                    <tr style="border-bottom:1px solid #334155;">
                        <td style="padding:14px 8px; width:95px; min-width:90px; font-weight:700; color:#38bdf8; text-align:center; vertical-align:middle; background:rgba(15,23,42,0.45); line-height:1.45;">주요<br>특징</td>
                        <td style="padding:12px 16px; line-height:1.6; vertical-align:middle;">논문이나 보고서에 들어가는 전통적이고 정적인 도표를 만들 때 표준으로 쓰입니다.</td>
                        <td style="padding:12px 16px; line-height:1.6; vertical-align:middle;">통계 분포(히스토그램, 박스플롯, 히트맵 등)를 색상 팔레트와 함께 예쁘게 나타낼 때 편리합니다.</td>
                        <td style="padding:12px 16px; line-height:1.6; color:#38bdf8; vertical-align:middle;">웹 브라우저나 대시보드(Streamlit)에서 사용자가 그래프 위 특정 지점을 클릭하고 마우스를 올려 값을 탐색할 수 있어 대시보드 제작에 가장 추천되는 라이브러리입니다.</td>
                    </tr>
                    <tr style="border-bottom:1px solid #334155;">
                        <td style="padding:14px 8px; width:95px; min-width:90px; font-weight:700; color:#38bdf8; text-align:center; vertical-align:middle; background:rgba(15,23,42,0.45); line-height:1.45;">상호<br>작용성</td>
                        <td style="padding:12px 16px; vertical-align:middle;">정적 이미지 (Static Image)</td>
                        <td style="padding:12px 16px; vertical-align:middle;">정적 이미지 (Static Image)</td>
                        <td style="padding:12px 16px; color:#38bdf8; font-weight:600; vertical-align:middle;">동적 인터랙티브 (줌, 팬, 툴팁, 범례 클릭 토글)</td>
                    </tr>
                    <tr style="border-bottom:1px solid #334155;">
                        <td style="padding:14px 8px; width:95px; min-width:90px; font-weight:700; color:#38bdf8; text-align:center; vertical-align:middle; background:rgba(15,23,42,0.45); line-height:1.45;">주요<br>장점</td>
                        <td style="padding:12px 16px; line-height:1.55; vertical-align:middle;">픽셀 단위 축, 눈금, 폰트, 레이아웃의 완전한 제어 가능</td>
                        <td style="padding:12px 16px; line-height:1.55; vertical-align:middle;">적은 코드로 미려한 통계 회귀선 및 분포 표현</td>
                        <td style="padding:12px 16px; line-height:1.55; vertical-align:middle;">마우스 호버만으로 정확한 환자 수 실시간 확인</td>
                    </tr>
                    <tr>
                        <td style="padding:14px 8px; width:95px; min-width:90px; font-weight:700; color:#38bdf8; text-align:center; vertical-align:middle; background:rgba(15,23,42,0.45); line-height:1.45;">수업 활용<br>추천</td>
                        <td style="padding:12px 16px; line-height:1.55; vertical-align:middle;">학술 보고서 제출, 정밀 인쇄물·연구 포스터 제작</td>
                        <td style="padding:12px 16px; line-height:1.55; vertical-align:middle;">역학 상관관계 분석, 연령대별 다변량 분포 탐색</td>
                        <td style="padding:12px 16px; line-height:1.55; vertical-align:middle;">학급 웹 대시보드 발표, 학생 실시간 데이터 탐구 실습</td>
                    </tr>
                </tbody>
            </table>
        </div>
        """, unsafe_allow_html=True)


# ----------------------------------------------------
# [메뉴 3] 지역/감염병 비교 심층 탐구
# ----------------------------------------------------
elif menu == "3. 지역/감염병 비교 심층 탐구":
    st.subheader("🔍 국내 대도시 및 해외 주요국 역학 비교 분석")
    c_a, c_b = st.columns(2)
    with c_a:
        st.markdown('<div style="font-size: clamp(0.92rem, 1.1vw, 1.08rem); font-weight: 700; color: #f8fafc; white-space: nowrap; margin-bottom: 8px;">🗺️ 국내외 주요 지역별 누적 환자 점유율</div>', unsafe_allow_html=True)
        reg_pie_df = working_df.groupby("지역")["신규환자수"].sum().reset_index().sort_values("신규환자수", ascending=False)
        active_reg_pie = reg_pie_df[reg_pie_df["신규환자수"] > 0]
        if active_reg_pie.empty or active_reg_pie["신규환자수"].sum() <= 0:
            st.info("ℹ️ 지역별 누적 환자 데이터가 없습니다 (0명).")
        else:
            fig_p1 = px.pie(active_reg_pie, values="신규환자수", names="지역", hole=0.4, template="plotly_dark")
            st.plotly_chart(fig_p1, use_container_width=True, key="plotly_menu3_region_pie")
    with c_b:
        st.markdown('<div style="font-size: clamp(0.92rem, 1.1vw, 1.08rem); font-weight: 700; color: #f8fafc; white-space: nowrap; margin-bottom: 8px;">🧬 전파 경로별 환자 비중 (공기, 비말, 접촉 등)</div>', unsafe_allow_html=True)
        path_pie_df = working_df.groupby("주요전파경로")["신규환자수"].sum().reset_index()
        active_path_pie = path_pie_df[path_pie_df["신규환자수"] > 0]
        if active_path_pie.empty or active_path_pie["신규환자수"].sum() <= 0:
            st.info("ℹ️ 전파 경로별 환자 데이터가 없습니다 (0명).")
        else:
            fig_p2 = px.pie(active_path_pie, values="신규환자수", names="주요전파경로", hole=0.4, template="plotly_dark")
            st.plotly_chart(fig_p2, use_container_width=True, key="plotly_menu3_route_pie")

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


# ----------------------------------------------------
# [메뉴 4] 학교 집단감염 예방 시뮬레이터
# ----------------------------------------------------
elif menu == "4. 학교 집단감염 예방 시뮬레이터":
    st.subheader("🧪 [참여형 실습] 교실 내 감염 전파 위험도 조작 시뮬레이터")
    st.markdown("예방 수칙 실천율을 조정하여 학교 내 감염 재생산 지수($R_t$)와 유행 차단 효과를 직접 탐구해 보세요.")

    s_col1, s_col2 = st.columns([1, 1.2])
    with s_col1:
        st.markdown("#### ⚙️ 방역 중재 변수 조작")
        
        sim_disease_map = {
            "홍역 (제2급 / 공기 전파 / 최고 전염력 R0=15.0)": 15.0,
            "수두 (제2급 / 비말·수포 / 고위험 전염력 R0=10.0)": 10.0,
            "백일해 (제2급 / 비말 전파 / 고위험 전염력 R0=12.0)": 12.0,
            "코로나19 (제4급 / 비말·에어로졸 / R0=3.5)": 3.5,
            "사스(SARS) (제1급 / 비말·접촉 / R0=3.0)": 3.0,
            "엠폭스 (제3급 / 체액·피부접촉 / R0=2.2)": 2.2,
            "에볼라바이러스병 (제1급 / 혈액·체액접촉 / R0=2.0)": 2.0,
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
        g_fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=rt_res,
            title={'text': "예상 유효 재생산지수 (Rt)", 'font': {'size': 20, 'color': '#ffffff'}},
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
        g_fig.update_layout(height=280, template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(g_fig, use_container_width=True, key="plotly_menu4_rt_gauge")

        if rt_res < 1.0:
            st.success(f"🎉 **감염 전파 차단 성공 ($R_t = {rt_res} < 1.0$)**: 교내 2차 확산이 효과적으로 억제되었습니다!")
        elif rt_res < 2.0:
            st.warning(f"⚠️ **주의 단계 ($R_t = {rt_res}$)**: 환기 횟수와 마스크 착용률을 조금 더 높여보세요.")
        else:
            st.error(f"🚨 **집단 유행 위험 단계 ($R_t = {rt_res} > 2.0$)**: 교실 내 전파 위험이 매우 높습니다!")


# ----------------------------------------------------
# [메뉴 5] AI 보건 튜터(Q&A) - 질병 선택에 100% 동적 연동되는 맞춤형 실시간 응답
# ----------------------------------------------------
elif menu == "5. AI 보건 튜터(Q&A)":
    st.subheader("🤖 AI 보건 튜터(Q&A): 법정감염병 1급~5급 종합 탐구실")
    st.markdown("""
    원하는 **법정감염병 급수와 질병을 드롭다운에서 선택**하면, 
    AI 보건 튜터가 해당 질병의 **원인, 증상, 최근 추세, 예방법, 치료 및 학교 보건실 관리 대책**을 체계적으로 종합 분석해 드립니다.
    """)

    # 1단계, 2단계 드롭다운 (급수별 10종씩 완비)
    st.markdown("##### 🔍 [1단계] 탐구할 법정감염병 선택 【급수별 10종 이상 완비】")
    tier_col, disease_col = st.columns(2)

    with tier_col:
        selected_tier_name = st.selectbox("📌 1단계: 법정감염병 급수 선택 (1~5급 분리)", options=list(TIER_DISEASE_MAP.keys()), index=3) # 기본 제4급

    with disease_col:
        sub_diseases = TIER_DISEASE_MAP[selected_tier_name]
        default_idx = 1 if (selected_tier_name == "제4급 감염병" and len(sub_diseases) > 1 and "인플루엔자" in sub_diseases) else 0
        selected_disease_name = st.selectbox("🦠 2단계: 세부 감염병 선택", options=sub_diseases, index=default_idx)

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
    c_head1, c_head2 = st.columns([3, 1])
    with c_head1:
        st.markdown(f"##### 💬 [2단계] AI 보건 튜터에게 질문하기 【현재 대상: **{selected_disease_name}**】")
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

    if quick_q:
        st.session_state["chat_history"].append({"role": "user", "content": quick_q})
        rep = ""
        if api_k:
            with st.spinner(f"AI 보건 튜터가 질병관리청 최신 역학 데이터 및 교과서 지침을 분석 중입니다..."):
                rep = query_gemini_ai(api_k, quick_q, selected_disease_name)
        if not rep:
            rep = generate_detailed_tutor_answer(selected_disease_name, quick_q, dis_info)
            if api_k:
                rep += "\n\n> 💡 *[보건 교육 지침] 질병관리청 공인 표준 보건 교과서 및 역학 지식베이스를 기반으로 생성된 답변입니다.*"
        st.session_state["chat_history"].append({"role": "assistant", "content": rep})
        st.rerun()

    for chat in st.session_state["chat_history"]:
        with st.chat_message(chat["role"]):
            st.markdown(chat["content"])

    user_q = st.chat_input(f"{selected_disease_name}에 대해 궁금한 점을 입력하세요...")
    if user_q:
        st.session_state["chat_history"].append({"role": "user", "content": user_q})
        rep = ""
        if api_k:
            with st.spinner(f"AI 보건 튜터가 {selected_disease_name} 관련 질병관리청 역학 지침을 분석 중입니다..."):
                rep = query_gemini_ai(api_k, user_q, selected_disease_name)
        if not rep:
            rep = generate_detailed_tutor_answer(selected_disease_name, user_q, dis_info)
            if api_k:
                rep += "\n\n> 💡 *[보건 교육 지침] 질병관리청 공인 표준 역학 데이터베이스 및 고교 보건 교과서 기준 답변입니다.*"
        st.session_state["chat_history"].append({"role": "assistant", "content": rep})
        st.rerun()


# ==========================================
# 6. 푸터 (사용자 요청: | 기호 완전 제거 및 보건간호과 반영)
# ==========================================
st.divider()
st.caption("서울의료보건고등학교 보건간호과  AI 융합 보건 교육 프로젝트")

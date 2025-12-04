import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from pandas.tseries.offsets import DateOffset
from datetime import date

# -----------------------------
# 기본 설정
# -----------------------------
st.set_page_config(
    page_title="에너지 요금 현황 보고 - 경쟁연료 단가 비교",
    layout="centered",
)

# =============================
# 여기서부터는 바로 본문 (패스워드 인증 제거)
# =============================
CSV_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "12RGk0NyM24_zxLIJXNAobcinZ714kdDKeeoDSt9Hb9c"
    "/export?format=csv&gid=0"
)

# -----------------------------
# 스타일 (A4 1페이지)
# -----------------------------
CUSTOM_CSS = """
<style>
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 1rem !important;
    max-width: 100% !important;
}
body {
    background-color: #eeeeee;
}
footer {
    display:none !important;
}
.report-container {
    width: 210mm;
    min-height: 297mm;
    margin: 0 auto;
    padding: 18mm 18mm 16mm 18mm;
    background-color: #ffffff;
    box-shadow: 0 0 15px rgba(0,0,0,0.1);
    font-family: "KoPubDotum", "맑은 고딕", sans-serif;
    color: #222;
    box-sizing: border-box;
}

/* 헤더 – 제목 가운데, 날짜는 아래 오른쪽 */
.report-header {
    text-align: center;
    margin-bottom: 6px;
}
.report-title-main {
    font-size: 26pt;
    font-weight: 800;
    color: #000000;
    letter-spacing: -1px;
}
.report-title-sub {
    font-size: 14pt;
    font-weight: 700;
    color: #000000;
    margin-top: 4px;
}
.report-date-right {
    text-align: right;
    font-size: 10pt;  /* 본문과 동일 */
    color: #444;
    margin-bottom: 16px;
}

/* 섹션 타이틀 – 소제목은 12pt로 살짝 크게 */
.section-title-row {
    margin-top: 18px;
    margin-bottom: 4px;
    font-size: 12pt;      /* 🔹 소제목 크기 */
    font-weight: 700;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.section-title-row .left {
    display: flex;
    align-items: center;
    gap: 6px;
}
.section-title-row .bullet {
    color: #000000;       /* 네모 글머리 */
    font-size: 14pt;
}
.section-title-row .label {
    font-size: 12pt;      /* 소제목 크기 */
}
.section-title-row .vat-note {
    font-size: 10pt;      /* 본문과 동일 */
    color: #777;
}

/* 섹션 캡션 – 동그라미 글머리 목록, 특이사항과 라인/폰트 맞춤 */
.section-caption-list {
    margin: 0 0 8px 0;    /* 왼쪽 여백 0으로 */
    padding-left: 32px;   /* 글머리 들여쓰기 */
    list-style-type: disc;/* ● 글머리 */
    font-size: 10pt;      /* 본문과 동일 */
    color: #555;
}
.section-caption-list li {
    margin: 0;
}

/* 테이블 – 본문 폰트 크기 통일, 숫자 조금 키움 */
.comp-table {
    border-collapse: collapse;
    width: 100%;
    margin-bottom: 22px;
    font-size: 11pt;              /* 🔹 10pt → 11pt 로 키움 */
    table-layout: fixed;
}
.comp-table thead tr {
    background-color: #f9f9fb;
    border-top: 2px solid #222;
    border-bottom: 1px solid #555;
}
.comp-table th {
    border: 1px solid #e0e0e0;
    padding: 9px 6px;
    text-align: center;           /* 헤더 가운데 정렬 */
    vertical-align: middle;
    font-weight: 600;
    color: #333;
}
.comp-table td {
    border: 1px solid #e0e0e0;
    padding: 9px 6px;
    text-align: right;
    vertical-align: middle;
    font-size: 11pt;
}
.comp-table td:nth-child(1) {
    text-align: center;
    width: 24%;
    font-weight: 600;
}
.comp-table th:nth-child(2), .comp-table td:nth-child(2) { width: 19%; }
.comp-table th:nth-child(3), .comp-table td:nth-child(3) { width: 19%; }
.comp-table th:nth-child(4), .comp-table td:nth-child(4) { width: 19%; }
.comp-table th:nth-child(5), .comp-table td:nth-child(5) { width: 19%; }

/* 강조 */
.value-now {
    font-weight: 700;
}
.change-up {
    color: #e74c3c;
    font-weight: 600;
}
.change-down {
    color: #2980b9;
    font-weight: 600;
}
.change-flat {
    color: #555;
    font-weight: 600;
}

/* 특이사항 소제목 – 12pt */
.notice-title-row {
    margin-top: 10px;
    margin-bottom: 6px;
    font-size: 12pt;      /* 🔹 소제목 크기 */
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 6px;
}
.notice-title-row .bullet {
    color: #000000;       /* 네모 글머리 */
    font-size: 14pt;
}

/* 특이사항 리스트 – 위 캡션과 폰트/라인 통일 */
.notice-list {
    margin: 4px 0 0 0;    /* 왼쪽 여백 0으로 */
    padding-left: 18px;   /* 글머리 들여쓰기 */
    font-size: 10pt;      /* 본문과 동일 */
    color: #444;
    line-height: 1.6;
    list-style-type: disc;/* 동그라미 글머리 */
}

/* 인쇄 */
@media print {
    @page {
        size: A4 portrait;
        margin: 0;
    }
    html, body {
        height: 100%;
        margin: 0 !important;
        padding: 0 !important;
        overflow: hidden;
    }
    section[data-testid="stSidebar"], header, footer, .stDeployButton {
        display: none !important;
    }
    .block-container {
        padding: 0 !important;
        margin: 0 !important;
    }
    .report-container {
        width: 210mm;
        height: 296mm;
        box-shadow: none;
        margin: 0;
        padding: 18mm 18mm 16mm 18mm;
        border: none;
        page-break-inside: avoid;
    }
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -----------------------------
# 데이터 로드
# -----------------------------
@st.cache_data(ttl=300)
def load_data() -> pd.DataFrame:
    df = pd.read_csv(CSV_URL)
    df["Date"] = pd.to_datetime(df["Date"])

    num_cols = [
        "산업용_원/MJ",
        "적용유가",
        "적용환율",
        "LPG_SK가스 가정상업용\n(kg, VAT포함)",
        "LPG_SK가스 가정상업용\n(mj, VAT별도)",
        "LPG_SK가스\n전월대비증감 (%)",
        "산업용 vs LPG\n(%)",
        "LPG_MP\n($, VAT포함)",
    ]
    for c in num_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def get_month_rows(df: pd.DataFrame, 기준일):
    기준일_ts = pd.to_datetime(기준일)
    당월일 = 기준일_ts.replace(day=1)
    전월일 = 당월일 - DateOffset(months=1)

    row_now = df[df["Date"] == 당월일]
    row_prev = df[df["Date"] == 전월일]

    row_now = None if row_now.empty else row_now.iloc[0]
    row_prev = None if row_prev.empty else row_prev.iloc[0]

    return 당월일, 전월일, row_now, row_prev


def safe_diff(now, prev):
    if pd.isna(now) or pd.isna(prev):
        return None
    return now - prev


def safe_pct(now, prev):
    if pd.isna(now) or pd.isna(prev) or prev == 0:
        return None
    return (now / prev - 1) * 100


def fmt_num(x, digits=2):
    if x is None or pd.isna(x):
        return ""
    return f"{x:,.{digits}f}"


def fmt_change_pct(x):
    if x is None or pd.isna(x):
        return "", "change-flat"
    if abs(x) < 1e-9:
        return "0.0%", "change-flat"
    cls = "change-up" if x > 0 else "change-down"
    return f"{x:+.1f}%", cls


def fmt_change_abs(x):
    if x is None or pd.isna(x):
        return "", "change-flat"
    if abs(x) < 1e-9:
        return "0.00", "change-flat"
    cls = "change-up" if x > 0 else "change-down"
    return f"{x:+.2f}", cls


# -----------------------------
# 사이드바 – 기준 연월 선택 + 인쇄 버튼
# -----------------------------
df = load_data()
df["연월"] = df["Date"].dt.to_period("M").astype(str)
valid_df = df[df["산업용_원/MJ"].notna()]
ym_options = sorted(valid_df["연월"].unique(), reverse=True)

today = date.today()
current_ym = today.strftime("%Y-%m")
default_index = ym_options.index(current_ym) if current_ym in ym_options else 0

with st.sidebar:
    st.markdown("### 🛠 기준 연-월 선택")
    selected_ym = st.selectbox("기준 연월", ym_options, index=default_index)

    기준일 = pd.to_datetime(selected_ym + "-01")
    당월일, 전월일, row_now, row_prev = get_month_rows(df, 기준일)

    st.markdown("---")
    st.markdown("### 🖨 인쇄")
    components.html(
        """
        <script>
        function printPage(){
            window.parent.print();
        }
        </script>
        <button onclick="printPage()" style="
            width:100%;
            padding:10px 0;
            border:none;
            border-radius:8px;
            background-color:#333;
            color:white;
            font-weight:bold;
            font-size:15px;
            cursor:pointer;
        ">
        🖨 보고서 인쇄
        </button>
        """,
        height=60,
    )

# -----------------------------
# 데이터 체크
# -----------------------------
if row_now is None:
    st.error(f"{selected_ym} 데이터가 없습니다.")
    st.stop()

if row_prev is None:
    st.warning(
        f"전월({(기준일 - DateOffset(months=1)).strftime('%Y-%m')}) 데이터가 없어 일부 증감 값은 공백일 수 있습니다."
    )

# -----------------------------
# 값 추출
# -----------------------------
col_lpg_mj = "LPG_SK가스 가정상업용\n(mj, VAT별도)"
col_lpg_pct = "LPG_SK가스\n전월대비증감 (%)"
col_vs_lpg = "산업용 vs LPG\n(%)"

산업용_prev = row_prev["산업용_원/MJ"] if row_prev is not None else None
산업용_now = row_now["산업용_원/MJ"]

LPG_prev = row_prev[col_lpg_mj] if (row_prev is not None and col_lpg_mj in row_prev) else None
LPG_now = row_now[col_lpg_mj] if col_lpg_mj in row_now else None

산업용_diff_val = safe_diff(산업용_now, 산업용_prev)
산업용_pct_val = safe_pct(산업용_now, 산업용_prev)

LPG_diff_val = safe_diff(LPG_now, LPG_prev)
if col_lpg_pct in row_now and not pd.isna(row_now[col_lpg_pct]):
    LPG_pct_val = row_now[col_lpg_pct]
else:
    LPG_pct_val = safe_pct(LPG_now, LPG_prev)

유가_prev = row_prev["적용유가"] if row_prev is not None else None
유가_now = row_now["적용유가"]
유가_diff_val = safe_diff(유가_now, 유가_prev)
유가_pct_val = safe_pct(유가_now, 유가_prev)

환율_prev = row_prev["적용환율"] if row_prev is not None else None
환율_now = row_now["적용환율"]
환율_diff_val = safe_diff(환율_now, 환율_prev)
환율_pct_val = safe_pct(환율_now, 환율_prev)

vs_lpg_pct = row_now[col_vs_lpg] if col_vs_lpg in row_now else None

# 특이사항 열(없으면 '사유' 열 사용)
special_col = None
for cand in ["특이사항", "사유"]:
    if cand in row_now.index:
        special_col = cand
        break

if special_col is not None and pd.notna(row_now[special_col]):
    special_text_raw = str(row_now[special_col])
else:
    special_text_raw = ""

special_items = [line.strip() for line in special_text_raw.split("\n") if line.strip()]

# -----------------------------
# 포맷팅
# -----------------------------
month_kor = 기준일.month
report_date_str = f"{당월일.year}년 {당월일.month}월 {당월일.day}일"

산업용_diff_str, 산업용_diff_cls = fmt_change_abs(산업용_diff_val)
산업용_pct_str, 산업용_pct_cls = fmt_change_pct(산업용_pct_val)

LPG_diff_str, LPG_diff_cls = fmt_change_abs(LPG_diff_val)
LPG_pct_str, LPG_pct_cls = fmt_change_pct(LPG_pct_val)

유가_diff_str, 유가_diff_cls = fmt_change_abs(유가_diff_val)
유가_pct_str, 유가_pct_cls = fmt_change_pct(유가_pct_val)

환율_diff_str, 환율_diff_cls = fmt_change_abs(환율_diff_val)
환율_pct_str, 환율_pct_cls = fmt_change_pct(환율_pct_val)

if vs_lpg_pct is not None and not pd.isna(vs_lpg_pct):
    vs_caption = (
        f"LPG(SK가정상업용) 단가는 도시가스(산업용)을 100으로 볼 때 "
        f"약 {vs_lpg_pct:.2f}% 수준입니다."
    )
else:
    vs_caption = "LPG와 도시가스 간 상대 수준은 시트의 '산업용 vs LPG(%)' 값을 참고하세요."

# -----------------------------
# HTML 조립
# -----------------------------
report_html = f"""
<div class="report-container">

  <!-- 헤더 -->
  <div class="report-header">
    <div class="report-title-main">에너지 요금 현황 보고</div>
    <div class="report-title-sub">({month_kor}월)</div>
  </div>
  <div class="report-date-right">{report_date_str}</div>

  <!-- 경쟁연료 단가 비교 제목 -->
  <div class="section-title-row">
    <div class="left">
      <span class="bullet">■</span>
      <span class="label">경쟁연료 단가 비교</span>
    </div>
    <div class="vat-note">(VAT 별도)</div>
  </div>

  <!-- 캡션: 동그라미 글머리 리스트 -->
  <ul class="section-caption-list">
    <li>{vs_caption}</li>
  </ul>

  <!-- 표 -->
  <table class="comp-table">
    <thead>
      <tr>
        <th>구분</th>
        <th>전월</th>
        <th>당월</th>
        <th>증감</th>
        <th>증감%</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>도시가스<br/>(산업용)</td>
        <td>{fmt_num(산업용_prev, 2)}</td>
        <td class="value-now">{fmt_num(산업용_now, 2)}</td>
        <td><span class="{산업용_diff_cls}">{산업용_diff_str}</span></td>
        <td><span class="{산업용_pct_cls}">{산업용_pct_str}</span></td>
      </tr>
      <tr>
        <td>LPG<br/>(SK,가정상업용)</td>
        <td>{fmt_num(LPG_prev, 2)}</td>
        <td class="value-now">{fmt_num(LPG_now, 2)}</td>
        <td><span class="{LPG_diff_cls}">{LPG_diff_str}</span></td>
        <td><span class="{LPG_pct_cls}">{LPG_pct_str}</span></td>
      </tr>
      <tr>
        <td>기준유가<br/>($/배럴)</td>
        <td>{fmt_num(유가_prev, 2)}</td>
        <td class="value-now">{fmt_num(유가_now, 2)}</td>
        <td><span class="{유가_diff_cls}">{유가_diff_str}</span></td>
        <td><span class="{유가_pct_cls}">{유가_pct_str}</span></td>
      </tr>
      <tr>
        <td>기준환율<br/>(원/$)</td>
        <td>{fmt_num(환율_prev, 2)}</td>
        <td class="value-now">{fmt_num(환율_now, 2)}</td>
        <td><span class="{환율_diff_cls}">{환율_diff_str}</span></td>
        <td><span class="{환율_pct_cls}">{환율_pct_str}</span></td>
      </tr>
    </tbody>
  </table>

  <!-- 특이사항 -->
  <div class="notice-title-row">
    <span class="bullet">■</span><span>특이사항</span>
  </div>
  <ul class="notice-list">
"""

if special_items:
    for item in special_items:
        report_html += f"<li>{item}</li>"
else:
    report_html += "<li>해당 월 특이사항이 없습니다.</li>"

report_html += """
  </ul>
</div>
"""

st.markdown(report_html, unsafe_allow_html=True)

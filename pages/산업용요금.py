import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from pandas.tseries.offsets import DateOffset
from datetime import date

# -----------------------------
# 기본 설정
# -----------------------------
st.set_page_config(
    page_title="대성에너지 도시가스 산업용 요금 안내",
    layout="centered",
)

CSV_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "12RGk0NyM24_zxLIJXNAobcinZ714kdDKeeoDSt9Hb9c"
    "/export?format=csv&gid=0"
)

# -----------------------------
# 스타일 (A4 1페이지 + 사이드바 인쇄 제외 설정)
# -----------------------------
CUSTOM_CSS = """
<style>
/* 1. Streamlit 기본 여백 및 배경 설정 */
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 1rem !important;
    max-width: 100% !important;
}

footer { display: none !important; }
body { background-color: #eeeeee; }

/* 2. A4 용지 레이아웃 정의 */
.report-container {
    width: 210mm;
    min-height: 297mm;
    margin: 0 auto;
    padding: 15mm;
    background-color: #ffffff;
    box-shadow: 0 0 15px rgba(0,0,0,0.1);
    font-family: "KoPubDotum", "맑은 고딕", sans-serif;
    color: #222;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
}

/* 3. 헤더 및 텍스트 스타일 */
.report-header { margin-bottom: 25px; text-align: center; }
.report-title-main { font-size: 22pt; font-weight: 800; letter-spacing: -0.5px; margin-bottom: 8px; }
.report-title-sub { font-size: 13pt; font-weight: 500; color: #555; margin-bottom: 15px; }
.report-meta-right { font-size: 10pt; color: #777; text-align: right; border-bottom: 2px solid #222; padding-bottom: 8px; }

.section-title { font-size: 13pt; font-weight: 700; margin-top: 25px; margin-bottom: 8px; border-left: 5px solid #0055b8; padding-left: 10px; }
.section-caption { font-size: 10pt; color: #666; margin-bottom: 10px; }

/* 4. 테이블 스타일 */
.styled-table { border-collapse: collapse; width: 100%; font-size: 10.5pt; margin-bottom: 20px; table-layout: fixed; }
.styled-table thead tr { background-color: #f0f4f8; border-top: 2px solid #444; border-bottom: 1px solid #444; }
.styled-table th, .styled-table td { border: 1px solid #e0e0e0; padding: 10px 5px; text-align: right; vertical-align: middle; }
.styled-table th { font-weight: 600; color: #333; text-align: center; background-color: #f4f4f8; }

.styled-table th:nth-child(1), .styled-table td:nth-child(1) { width: 28%; text-align: left; padding-left: 15px; background-color: #fafafa; font-weight: 600; white-space: nowrap; }
.styled-table th:nth-child(2), .styled-table td:nth-child(2) { width: 18%; }
.styled-table th:nth-child(3), .styled-table td:nth-child(3) { width: 18%; }
.styled-table th:nth-child(4), .styled-table td:nth-child(4) { width: 20%; }
.styled-table th:nth-child(5), .styled-table td:nth-child(5) { width: 16%; }

/* 5. 푸터 주석 */
.footer-note { margin-top: auto; padding-top: 20px; border-top: 1px solid #eee; font-size: 9pt; color: #888; line-height: 1.5; }
.footer-note strong { color: #e74c3c; }
.footer-note a { color: #2980b9; text-decoration: none; }

/* 6. 인쇄 설정 */
@media print {
    @page { size: A4 portrait; margin: 0; }
    html, body { height: 100%; margin: 0 !important; padding: 0 !important; overflow: hidden; }
    section[data-testid="stSidebar"], header, footer, .stDeployButton { display: none !important; }
    .block-container { padding: 0 !important; margin: 0 !important; }
    .report-container { width: 210mm; height: 296mm; box-shadow: none; margin: 0; padding: 15mm; border: none; page-break-inside: avoid; }
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -----------------------------
# 데이터 로드 및 함수
# -----------------------------
@st.cache_data(ttl=300)
def load_data() -> pd.DataFrame:
    df = pd.read_csv(CSV_URL)
    df["Date"] = pd.to_datetime(df["Date"])
    num_cols = [
        "원/㎥", "열량", "원료비", "가스공사 공급비용", "대성에너지 공급비용",
        "산업용_원/MJ", "미수금", "연료전지(MJ)", "열병합(MJ)",
        "자가열전용(MJ)", "일반용(MJ)", "적용유가", "적용환율"
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
    if pd.isna(now) or pd.isna(prev): return None
    return now - prev

def safe_pct(now, prev):
    if pd.isna(now) or pd.isna(prev) or prev == 0: return None
    return (now / prev - 1) * 100

def fmt2(x): return "" if pd.isna(x) else f"{x:,.2f}"
def fmt2_money(x): return "" if pd.isna(x) else f"{x:,.2f}"

# -----------------------------
# 사이드바 설정 & 인쇄 버튼
# -----------------------------
df = load_data()
df["연월"] = df["Date"].dt.to_period("M").astype(str)

valid_df = df[df["산업용_원/MJ"].notna()]
ym_options = sorted(valid_df["연월"].unique(), reverse=True)

today = date.today()
current_ym = today.strftime("%Y-%m")
default_index = ym_options.index(current_ym) if current_ym in ym_options else 0

with st.sidebar:
    st.markdown("### 🛠 설정")
    selected_ym = st.selectbox("기준 연-월 선택", ym_options, index=default_index)
    
    # [추가됨] 기준열량 입력 받기 (이 값으로 전월/당월 모두 곱함)
    # 초기값은 선택된 달의 열량 데이터 사용
    기준일 = pd.to_datetime(selected_ym + "-01")
    당월일, 전월일, row_now, row_prev = get_month_rows(df, 기준일)
    
    if row_now is not None:
        default_cal = row_now["열량"] if pd.notna(row_now["열량"]) else 42.0
    else:
        default_cal = 42.0
        
    st.markdown("---")
    st.markdown("### 🔥 기준열량 변경")
    input_cal = st.number_input("MJ/㎥", value=float(default_cal), format="%.4f")
    st.caption("입력하신 기준열량을 전월/당월 요금에 동일하게 곱하여 산출합니다.")

    st.markdown("---")
    st.markdown("### 🖨 보고서 인쇄")
    components.html(
        """
        <script> function printPage() { window.parent.print(); } </script>
        <style>
            .print-btn { width: 100%; background-color: #333; color: white; border: none; padding: 12px 0; border-radius: 8px; font-size: 16px; font-weight: bold; cursor: pointer; font-family: "맑은 고딕", sans-serif; display: flex; align-items: center; justify-content: center; gap: 8px; transition: background-color 0.2s; }
            .print-btn:hover { background-color: #555; }
        </style>
        <button class="print-btn" onclick="printPage()">🖨️ 인쇄하기</button>
        """,
        height=60
    )

if row_now is None:
    st.error(f"{당월일.date()} 데이터가 없습니다.")
    st.stop()
if row_prev is None:
    st.warning(f"전월({전월일.date()}) 데이터가 없어 증감 계산 일부 공백일 수 있습니다.")
today_str = today.strftime("%Y-%m-%d")

# -----------------------------
# 데이터 가공
# -----------------------------
산업용_prev = row_prev["산업용_원/MJ"] if row_prev is not None else None
산업용_now = row_now["산업용_원/MJ"]
유가_prev = row_prev["적용유가"] if row_prev is not None else None
유가_now = row_now["적용유가"]
환율_prev = row_prev["적용환율"] if row_prev is not None else None
환율_now = row_now["적용환율"]

rows = [
    ["산업용", 산업용_prev, 산업용_now],
    ["기준유가 ($/배럴)", 유가_prev, 유가_now],
    ["기준환율 (원/$)", 환율_prev, 환율_now],
]
table1 = pd.DataFrame(rows, columns=["용도", "전월(원/MJ)", "당월(원/MJ)"])
table1["증감(원/MJ)"] = [safe_diff(n, p) for p, n in zip(table1["전월(원/MJ)"], table1["당월(원/MJ)"])]
table1["증감(%)"] = [safe_pct(n, p) for p, n in zip(table1["전월(원/MJ)"], table1["당월(원/MJ)"])]

table1_disp = table1.copy()
for col in ["전월(원/MJ)", "당월(원/MJ)", "증감(원/MJ)", "증감(%)"]:
    table1_disp[col] = table1_disp[col].apply(fmt2)

# [수정됨] 루베(m3) 환산 로직: 사용자가 입력한 input_cal 값을 양쪽에 동일하게 곱함
가격_m3_prev = 산업용_prev * input_cal if 산업용_prev is not None else None
가격_m3_now = 산업용_now * input_cal
증감_m3 = safe_diff(가격_m3_now, 가격_m3_prev)
증감_pct_m3 = safe_pct(가격_m3_now, 가격_m3_prev)

table2 = pd.DataFrame({
    "용도": ["산업용"],
    "변경전(원/㎥)": [가격_m3_prev],
    "변경후(원/㎥)": [가격_m3_now],
    "증감(원/㎥)": [증감_m3],
    "증감(%)": [증감_pct_m3],
})
table2_disp = table2.copy()
for c in ["변경전(원/㎥)", "변경후(원/㎥)", "증감(원/㎥)", "증감(%)"]:
    table2_disp[c] = table2_disp[c].apply(fmt2_money)

# -----------------------------
# HTML 조립
# -----------------------------
report_html = ""
report_html += '<div class="report-container">'

report_html += f"""<div class="report-header">
<div class="report-title-main">대성에너지 도시가스 요금 보고서</div>
<div class="report-title-sub">산업용 요금 단가 변동 현황</div>
<div class="report-meta-right">
기준 연월: <strong>{selected_ym}</strong><br/>
보고서 생성일: {today_str}
</div>
</div>"""

report_html += """<div class="section-title">1. 단위: 원/MJ (VAT별도)</div>
<div class="section-caption">
산업용 요금 및 기준유가·환율의 전월 대비 변동 현황입니다.
</div>"""
report_html += table1_disp.to_html(classes="styled-table", index=False)

report_html += """<div class="section-title">2. 단위: 원/㎥</div>
<div class="section-caption">
매월 열량 변경으로 인한 오차가 존재할 수 있어, 참고용으로만 활용하시기 바랍니다.
</div>"""
# [수정됨] 입력된 기준열량 표시
report_html += f"<div class='section-caption'>기준열량: <strong>{input_cal:,.3f} MJ/㎥</strong> (설정값 적용)</div>"
report_html += table2_disp.to_html(classes="styled-table", index=False)

report_html += """<div class="footer-note">
※ <strong>주의</strong> : 원/㎥ 단위 요금은 설정된 기준열량({cal} MJ/㎥)으로 환산한 값입니다.<br/>
※ 도시가스 요금단가 안내:
<a href="https://cyber.daesungenergy.com/charge/pricetable" target="_blank">
https://cyber.daesungenergy.com/charge/pricetable
</a><br/>
※ 사용기간에 따른 평균 요금:
<a href="https://cyber.daesungenergy.com/charge/solvAvgMJ" target="_blank">
https://cyber.daesungenergy.com/charge/solvAvgMJ
</a>
</div>""".format(cal=f"{input_cal:,.3f}")

report_html += "</div>"
st.markdown(report_html, unsafe_allow_html=True)
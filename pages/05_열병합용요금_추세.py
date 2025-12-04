import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# -----------------------------
# 기본 설정
# -----------------------------
st.set_page_config(
    page_title="열병합용 도시가스 요금 추세",
    layout="wide",
)

CSV_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "12RGk0NyM24_zxLIJXNAobcinZ714kdDKeeoDSt9Hb9c"
    "/export?format=csv&gid=0"
)

# -----------------------------
# 데이터 로드
# -----------------------------
@st.cache_data(ttl=300)
def load_data():
    df = pd.read_csv(CSV_URL)

    # 날짜 컬럼 & 연월
    df["Date"] = pd.to_datetime(df["Date"])
    df["연월"] = df["Date"].dt.to_period("M").astype(str)

    col_heat_raw = "열병합(MJ)"

    # 숫자형 변환
    for c in [col_heat_raw, "열량"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # 보기 좋은 이름으로 리네임
    df = df.rename(
        columns={
            col_heat_raw: "열병합용(원/MJ)",
        }
    )

    return df

df = load_data()

# 컬럼 이름 상수
COL_HEAT = "열병합용(원/MJ)"

# 유효 데이터만 기준으로 연월 목록 생성
valid_df = df.dropna(subset=[COL_HEAT])
ym_list = sorted(valid_df["연월"].unique())

if not ym_list:
    st.error("그래프를 그릴 수 있는 열병합용 데이터가 없습니다.")
    st.stop()

# 열량 기본값: 있으면 마지막 값, 없으면 42.0
if "열량" in df.columns and df["열량"].notna().any():
    default_cal = float(df["열량"].dropna().iloc[-1])
else:
    default_cal = 42.0

# -----------------------------
# 사이드바: 슬라이더 / 단위 / 열량
# -----------------------------
with st.sidebar:
    st.markdown("### 🔍 조회 설정")

    start_ym, end_ym = st.select_slider(
        "조회 연월 범위",
        options=ym_list,
        value=(ym_list[0], ym_list[-1]),
    )

    st.markdown("---")
    st.markdown("### 🔁 환산 열량 설정")
    cal_value = st.number_input(
        "환산 열량 (MJ/㎥)",
        value=float(default_cal),
        format="%.3f",
        min_value=0.0001,
        step=0.1,
        help="MJ 단가를 ㎥ 단가로 바꿀 때 곱해줄 값입니다.",
    )

    st.markdown("---")
    st.markdown("### 📏 표시 단위")
    unit_option = st.radio(
        "단위 선택",
        ["원/MJ", "원/㎥"],
        index=0,
        horizontal=True,
    )

# -----------------------------
# 데이터 필터링 & 단위 변환
# -----------------------------
mask = (valid_df["연월"] >= start_ym) & (valid_df["연월"] <= end_ym)
plot_df = valid_df.loc[mask].copy()

if plot_df.empty:
    st.warning("선택한 기간에 해당하는 열병합용 데이터가 없습니다.")
    st.stop()

# 기준 단위: 원/MJ
y_heat_mj = plot_df[COL_HEAT].copy()

# 단위 변환
if unit_option == "원/㎥":
    y_heat = y_heat_mj * cal_value
    y_unit = "원/㎥"
else:
    y_heat = y_heat_mj
    y_unit = "원/MJ"

x_vals = plot_df["연월"].astype(str)

# -----------------------------
# 1) 열병합용 요금 추세 그래프
# -----------------------------
st.title("열병합용 도시가스 요금 추세")
st.caption("단위: " + y_unit)

hover_tmpl = (
    "연월 : %{x}<br>"
    "열병합용 요금 : %{y:,.2f} " + y_unit + "<extra></extra>"
)

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=x_vals,
        y=y_heat,
        mode="lines+markers",
        name="열병합용 요금",
        hovertemplate=hover_tmpl,
    )
)

fig.update_layout(
    xaxis_title="연월",
    yaxis_title=y_unit,
    hovermode="x",
    margin=dict(l=40, r=20, t=40, b=40),
    legend=dict(
        x=0,
        y=1,
        xanchor="left",
        yanchor="bottom",
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor="lightgray",
        borderwidth=1,
    ),
)
fig.update_xaxes(tickangle=-45)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# 2) 데이터 테이블 (토글)
# -----------------------------
table_df = pd.DataFrame({
    "연월": x_vals,
    "열병합용요금(원/MJ)": y_heat_mj,
    f"열병합용요금({y_unit})": y_heat,
})

with st.expander("📊 데이터 테이블 열기 / 닫기", expanded=False):
    st.dataframe(
        table_df.style.format({
            "열병합용요금(원/MJ)": "{:,.2f}",
            f"열병합용요금({y_unit})": "{:,.2f}",
        }),
        use_container_width=True,
    )

st.caption(
    "※ 환산 열량을 변경하면 단위가 원/㎥일 때 열병합용 요금이 함께 재계산됩니다."
)

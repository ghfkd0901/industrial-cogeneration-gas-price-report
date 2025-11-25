import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# -----------------------------
# 기본 설정
# -----------------------------
st.set_page_config(
    page_title="도시가스 산업용 vs LPG 요금 비교",
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

    col_city_raw = "산업용_원/MJ"
    col_lpg_raw = "LPG_SK가스 가정상업용\n(mj, VAT별도)"

    # 숫자형 변환
    for c in [col_city_raw, col_lpg_raw, "열량"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # 보기 좋은 이름으로 리네임
    df = df.rename(
        columns={
            col_city_raw: "도시가스_산업용(원/MJ)",
            col_lpg_raw: "LPG_SK_가정상업용(원/MJ)",
        }
    )

    return df

df = load_data()

# 컬럼 이름 상수
COL_CITY = "도시가스_산업용(원/MJ)"
COL_LPG = "LPG_SK_가정상업용(원/MJ)"

# 유효 데이터만 기준으로 연월 목록 생성
valid_df = df.dropna(subset=[COL_CITY, COL_LPG])
ym_list = sorted(valid_df["연월"].unique())

if not ym_list:
    st.error("그래프를 그릴 수 있는 데이터가 없습니다.")
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
    st.warning("선택한 기간에 해당하는 데이터가 없습니다.")
    st.stop()

# 기준 단위: 원/MJ
y_city = plot_df[COL_CITY].copy()
y_lpg = plot_df[COL_LPG].copy()

# 단위 변환
if unit_option == "원/㎥":
    y_city = y_city * cal_value
    y_lpg = y_lpg * cal_value
    y_unit = "원/㎥"
else:
    y_unit = "원/MJ"

x_vals = plot_df["연월"].astype(str)
x_vals_list = list(x_vals)  # 기준선용

# -----------------------------
# 비율 계산 (LPG / 도시가스 산업용)
# -----------------------------
ratio = y_lpg / y_city.replace({0: np.nan})
ratio = ratio.replace([np.inf, -np.inf], np.nan)

# hover용 customdata (도시가스, LPG 같이 넣기)
customdata = np.stack([y_city, y_lpg], axis=-1)

hover_tmpl = (
    "연월 : %{x}<br>"
    "도시가스 산업용 요금 : %{customdata[0]:,.2f} " + y_unit + "<br>"
    "LPG 요금 : %{customdata[1]:,.2f} " + y_unit + "<extra></extra>"
)

# -----------------------------
# 1) 단가 그래프 (도시가스 산업용 vs LPG)
# -----------------------------
st.title("도시가스 산업용 vs LPG 요금 비교 그래프")
st.caption("단위: " + y_unit)

fig = go.Figure()

# 도시가스 산업용 trace (툴팁 담당)
fig.add_trace(
    go.Scatter(
        x=x_vals,
        y=y_city,
        mode="lines+markers",
        name="도시가스 산업용 요금",
        customdata=customdata,
        hovertemplate=hover_tmpl,
    )
)

# LPG trace (선/점만, 툴팁은 스킵)
fig.add_trace(
    go.Scatter(
        x=x_vals,
        y=y_lpg,
        mode="lines+markers",
        name="LPG 요금",
        hoverinfo="skip",
        showlegend=True,
    )
)

fig.update_layout(
    xaxis_title="연월",
    yaxis_title=y_unit,
    hovermode="x",
    margin=dict(l=40, r=20, t=40, b=40),
    legend=dict(          # ✅ 범례 왼쪽 상단으로 이동
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
# 2) 비율 그래프 (LPG / 도시가스 산업용)
# -----------------------------
st.subheader("LPG / 도시가스 산업용 요금 비율")

ratio_hover = (
    "연월 : %{x}<br>"
    "비율(LPG ÷ 도시가스 산업용) : %{y:.3f} 배<extra></extra>"
)

fig_ratio = go.Figure()

fig_ratio.add_trace(
    go.Scatter(
        x=x_vals,
        y=ratio,
        mode="lines+markers",
        name="LPG / 도시가스 산업용 비율",
        hovertemplate=ratio_hover,
    )
)

# y = 1 기준선 (빨간 점선)
if len(x_vals_list) > 0:
    fig_ratio.add_shape(
        type="line",
        xref="x",
        yref="y",
        x0=x_vals_list[0],
        x1=x_vals_list[-1],
        y0=1,
        y1=1,
        line=dict(
            color="red",
            width=2,
            dash="dash",
        ),
    )

    fig_ratio.add_annotation(
        x=x_vals_list[-1],
        y=1,
        xanchor="left",
        yanchor="bottom",
        showarrow=False,
        text="기준선 (1배)",
        font=dict(color="red"),
    )

fig_ratio.update_layout(
    xaxis_title="연월",
    yaxis_title="배 (LPG ÷ 도시가스 산업용)",
    hovermode="x",
    margin=dict(l=40, r=20, t=40, b=40),
)
fig_ratio.update_xaxes(tickangle=-45)

st.plotly_chart(fig_ratio, use_container_width=True)

# -----------------------------
# 3) 데이터 테이블 (토글)
# -----------------------------
table_df = pd.DataFrame({
    "연월": x_vals,
    f"도시가스산업용요금({y_unit})": y_city,
    f"LPG요금({y_unit})": y_lpg,
    "비율(LPG/도시가스산업용)": ratio,
})

with st.expander("📊 데이터 테이블 열기 / 닫기", expanded=False):
    st.dataframe(
        table_df.style.format({
            f"도시가스산업용요금({y_unit})": "{:,.2f}",
            f"LPG요금({y_unit})": "{:,.2f}",
            "비율(LPG/도시가스산업용)": "{:.3f}",
        }),
        use_container_width=True,
    )

st.caption(
    "※ 비율(LPG/도시가스 산업용)은 현재 선택된 단위와 상관없이 동일하며, "
    "1보다 크면 LPG가 도시가스 산업용보다 비싼 구간입니다."
)

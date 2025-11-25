import streamlit as st
import pandas as pd

# -----------------------------
# 기본 설정
# -----------------------------
st.set_page_config(
    page_title="담당자 메일 발송 리스트",
    layout="wide",
)

# -----------------------------
# 🔐 비밀번호 불러오기 (st.secrets 사용)
# -----------------------------
try:
    # Streamlit Cloud의 Secrets 또는 로컬의 .streamlit/secrets.toml 에서 가져옴
    SECRET_PASSWORD = st.secrets["private_password"]
except Exception as e:
    st.error("🔐 비밀번호 설정이 되어있지 않습니다. 관리자에게 문의하세요.")
    st.stop()

# -----------------------------
# 데이터 로드 (두 번째 시트 gid 적용)
# -----------------------------
CSV_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "12RGk0NyM24_zxLIJXNAobcinZ714kdDKeeoDSt9Hb9c"
    "/export?format=csv&gid=1582710939"
)

@st.cache_data(ttl=600)
def load_contact_data():
    try:
        df = pd.read_csv(CSV_URL)
        df = df.fillna("")
        return df
    except Exception as e:
        st.error(f"데이터를 불러오는데 실패했습니다: {e}")
        return pd.DataFrame()

# -----------------------------
# 로그인 로직
# -----------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def check_password():
    if st.session_state.password_input == SECRET_PASSWORD:
        st.session_state.authenticated = True
    else:
        st.session_state.authenticated = False
        st.error("비밀번호가 틀렸습니다. 다시 확인해주세요.")

# -----------------------------
# 화면 구성
# -----------------------------

# 1. 로그인 전 화면
if not st.session_state.authenticated:
    st.markdown("### 🔒 보안 접근")
    st.markdown("관계자 외 접근이 제한된 페이지입니다. 비밀번호를 입력하세요.")
    
    st.text_input(
        "비밀번호", 
        type="password", 
        key="password_input", 
        on_change=check_password
    )
    st.stop()

# 2. 로그인 후 화면
st.title("📧 담당자 메일 발송 리스트")
st.caption("구글 스프레드시트의 최신 담당자 정보를 불러옵니다.")

df = load_contact_data()

if not df.empty:
    search_term = st.text_input("🔍 업체명 또는 담당자 검색", placeholder="검색어를 입력하세요...")
    
    if search_term:
        mask = (
            df["업체명"].astype(str).str.contains(search_term) | 
            df["담당자"].astype(str).str.contains(search_term)
        )
        df_display = df[mask]
    else:
        df_display = df

    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "이메일": st.column_config.TextColumn(
                "이메일",
                help="복사하려면 셀을 클릭하세요",
                validate="^\\S+@\\S+$"
            ),
             "연락처": st.column_config.TextColumn(
                "연락처",
                help="전화번호"
            ),
        }
    )
    
    st.markdown(f"**총 조회된 업체:** {len(df_display)}개")

    csv = df_display.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 리스트 다운로드 (CSV)",
        data=csv,
        file_name='담당자_연락처_리스트.csv',
        mime='text/csv',
    )
else:
    st.warning("데이터가 없거나 불러올 수 없습니다.")
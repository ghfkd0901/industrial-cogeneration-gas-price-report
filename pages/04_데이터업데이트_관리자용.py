import streamlit as st
import streamlit.components.v1 as components

# -----------------------------
# 기본 설정
# -----------------------------
st.set_page_config(
    page_title="원본데이터 입력하기 (관리자용)",
    layout="centered",
)

# ✅ 비밀번호 설정
# .streamlit/secrets.toml 에 DATA_INPUT_PASSWORD="원하는비번" 추가해두는 걸 추천
PASSWORD = st.secrets.get("DATA_INPUT_PASSWORD", "1234")  # 없으면 임시로 1234

# ✅ 원본데이터 입력용 구글 스프레드시트 편집 URL
DATA_INPUT_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "12RGk0NyM24_zxLIJXNAobcinZ714kdDKeeoDSt9Hb9c"
    "/edit#gid=0"
)

# -----------------------------
# 인증 상태 관리
# -----------------------------
if "data_input_authenticated" not in st.session_state:
    st.session_state["data_input_authenticated"] = False

def check_password():
    """비밀번호 입력/검증 UI"""
    st.title("🔒 원본데이터 입력 (관리자 전용)")

    with st.form("password_form"):
        pw = st.text_input("비밀번호를 입력하세요.", type="password")
        submitted = st.form_submit_button("입장하기")

    if submitted:
        if pw == PASSWORD:
            st.session_state["data_input_authenticated"] = True
            st.success("인증되었습니다. 아래 버튼을 눌러 원본데이터 입력 화면으로 이동하세요.")
        else:
            st.error("비밀번호가 올바르지 않습니다.")

    return st.session_state["data_input_authenticated"]

# -----------------------------
# 메인 로직
# -----------------------------
if not st.session_state["data_input_authenticated"]:
    # 아직 인증 안 된 상태 → 비밀번호 입력 화면만 노출
    authenticated = check_password()
    if not authenticated:
        st.stop()

# 여기부터는 인증된 사람만 볼 수 있음
st.title("원본데이터 입력하기")

st.info(
    "이 화면은 **원본 데이터 입력/수정 담당자 전용**입니다.\n\n"
    "아래 버튼 또는 링크를 통해 원본데이터 입력 페이지로 이동하세요."
)

# 1) 텍스트 링크
st.markdown(
    f"""
- [원본데이터 입력 스프레드시트 열기]({DATA_INPUT_URL})
    """,
    unsafe_allow_html=True,
)

# 2) 새 탭으로 여는 버튼 (눈에 잘 띄게)
components.html(
    f"""
    <style>
    .open-link-btn {{
        background-color: #0055b8;
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        font-size: 16px;
        font-weight: 600;
        cursor: pointer;
        font-family: "맑은 고딕", sans-serif;
    }}
    .open-link-btn:hover {{
        background-color: #003f88;
    }}
    </style>
    <button class="open-link-btn" onclick="window.open('{DATA_INPUT_URL}', '_blank')">
        원본데이터 입력 화면 열기
    </button>
    """,
    height=80,
)

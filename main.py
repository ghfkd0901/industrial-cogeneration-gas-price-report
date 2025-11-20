import streamlit as st

st.set_page_config(
    page_title="대성에너지 도시가스 요금 안내",
    page_icon="🔥",
    layout="centered"
)

st.title("🔥 대성에너지 도시가스 요금 안내")

st.markdown("---")

st.markdown("""
### 👋 환영합니다!

이 서비스는 **대성에너지**의 도시가스 요금 단가 변동 내역을 
매월 자동으로 확인하고 보고서 형태로 제공합니다.

왼쪽 사이드바 메뉴에서 원하시는 **요금 종류**를 선택해주세요.

<br>

#### 📑 제공되는 보고서
* **🏭 [산업용 요금 보고서]**: 산업용 가스 단가 및 기준 유가/환율 변동
* **⚡ [열병합 요금 보고서]**: 열병합 및 자가열전용 가스 단가 변동

""", unsafe_allow_html=True)

st.info("👈 왼쪽 사이드바를 열어 메뉴를 선택해주세요.")
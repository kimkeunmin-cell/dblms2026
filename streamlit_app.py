import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# ------------------------------------------------------
# CSV 파일: accounts.csv (학생 로그인), sheets.csv (학생별 구글 시트)
# accounts.csv → id,password,role  ← 역할 추가 (student / admin)
# ------------------------------------------------------

ACCOUNTS_FILE = "accounts.csv"
SHEETS_FILE = "sheets.csv"

st.set_page_config(page_title="Login System", layout="centered")

# ------------------------------------------------------
# 로그인 유효성 검사
# ------------------------------------------------------
def check_login(user_id, user_pw):
    try:
        df = pd.read_csv(ACCOUNTS_FILE, dtype=str)
    except FileNotFoundError:
        st.error("⚠️ accounts.csv 파일이 없습니다.")
        return None

    row = df[(df['id'] == user_id) & (df['password'] == user_pw)]
    if row.empty:
        return None
    return row.iloc[0]  # id, password, role 포함

# ------------------------------------------------------
# 사용자 역할별 페이지 라우팅
# ------------------------------------------------------
def login_page():
    st.title("로그인")

    user_id = st.text_input("아이디", "")
    user_pw = st.text_input("비밀번호", "", type="password")

    if st.button("로그인"):
        user = check_login(user_id, user_pw)
        if user is not None:
            st.session_state["logged_in"] = True
            st.session_state["user_id"] = user_id
            st.session_state["role"] = user.get("role", "student")
            st.rerun()
        else:
            st.error("❌ 로그인 실패: 아이디 또는 비밀번호가 잘못되었습니다.")

# ------------------------------------------------------
# 📱 모바일 최적화: 사이드바·버튼 크기 확장
# ------------------------------------------------------
def mobile_header():
    st.markdown(
        "<style> .stButton>button { width:100%; height:50px; font-size:20px; } </style>",
        unsafe_allow_html=True
    )

# ------------------------------------------------------
# 👨‍🎓 학생 메인 화면
def student_page():
    mobile_header()
    st.title("학생 페이지")
    st.write(f"{st.session_state['user_id']}님 환영합니다.")

    # 학생별 구글 시트 가져오기
    try:
        df = pd.read_csv(SHEETS_FILE, dtype=str)
        row = df[df['id'] == st.session_state['user_id']]
        sheet_url = row.iloc[0]['sheet_url'] if not row.empty else None
    except FileNotFoundError:
        sheet_url = None
        st.error("⚠️ sheets.csv 파일이 없습니다.")

    st.subheader("📄 학습 기록 보기 (모바일·PC 고정행/열 지원)")("📄 학습 기록 보기")

    # 기간 선택
    period = st.selectbox("기간 선택", ["전체", "이번주", "이번달", "최근 7일"])

        # Google sheet embed — 모바일에서도 고정행/열 정상 표시되는 모드(widget=true) 적용
    if sheet_url:
        mobile_friendly_url = sheet_url + "&widget=true&headers=true"
        st.components.v1.html(f"""
            <iframe src='{mobile_friendly_url}' style='width:100%; height:700px; border:none;'></iframe>
        """, height=720)
    else:
        st.warning("해당 학생의 시트 정보가 없습니다.")
        st.warning("해당 학생의 시트 정보가 없습니다.")

    st.markdown("---")

    if st.button("🔙 로그아웃"):
        st.session_state.clear()
        st.rerun()

# ------------------------------------------------------
# 👨‍🏫 관리자 페이지
# ------------------------------------------------------
def admin_page():
    mobile_header()

    st.title("관리자 모드")
    st.write("학생 관리 / 전체 보고서 / 링크 설정 기능 제공")

    tab1, tab2 = st.tabs(["📁 전체 학생 리스트", "⚙️ 시트 매핑 관리"])

    # 전체 계정 확인
    with tab1:
        try:
            df = pd.read_csv(ACCOUNTS_FILE)
            st.dataframe(df)
        except:
            st.error("accounts.csv 불러오기 실패")

    # Google Sheet 매핑 관리
    with tab2:
        try:
            df2 = pd.read_csv(SHEETS_FILE)
            st.dataframe(df2)
        except:
            st.error("sheets.csv 불러오기 실패")

    st.markdown("---")

    if st.button("🔙 로그아웃"):
        st.session_state.clear()
        st.rerun()

# ------------------------------------------------------
# 🚀 앱 실행
# ------------------------------------------------------
def app():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if not st.session_state["logged_in"]:
        login_page()
    else:
        if st.session_state.get("role", "student") == "admin":
            admin_page()
        else:
            student_page()

if __name__ == "__main__":
    app()

import streamlit as st
import pandas as pd

# ------------------------------------------------------
# 🔐 1) 계정 정보: accounts.csv 파일로 관리 (ID, PW)
# ------------------------------------------------------
# CSV 예시
# id,password
# 30628,두둥탁
# 30111,abcd1234
# 30222,qwerty

ACCOUNTS_FILE = "accounts.csv"

st.set_page_config(page_title="Login System", layout="centered")

# ------------------------------------------------------
# 🔑 로그인 체크 함수
# ------------------------------------------------------
def check_login(user_id, user_pw):
    try:
        df = pd.read_csv(ACCOUNTS_FILE, dtype=str)
    except FileNotFoundError:
        st.error("⚠️ accounts.csv 파일이 없습니다. GitHub에 업로드해주세요.")
        return False

    match = df[(df['id'] == user_id) & (df['password'] == user_pw)]
    return not match.empty

# ------------------------------------------------------
# 🟦 로그인 페이지
# ------------------------------------------------------
def login_page():
    st.title("로그인")

    user_id = st.text_input("아이디", "", placeholder="아이디 입력")
    user_pw = st.text_input("비밀번호", "", placeholder="비밀번호 입력", type="password")

    if st.button("로그인"):
        if check_login(user_id, user_pw):
            st.session_state["logged_in"] = True
            st.session_state["user_id"] = user_id
            st.rerun()
        else:
            st.error("❌ 아이디 또는 비밀번호가 올바르지 않습니다.")

# ------------------------------------------------------
# 🟩 메인 화면
# ------------------------------------------------------
def main_page():
    st.title("메인 화면")
    st.write(f"**{st.session_state['user_id']}** 님 반갑습니다.")
    st.write("원하는 버튼을 선택하세요.")

    # Button 1 → Google Sheet
    if st.button("Google Sheet 열기"):
        st.markdown(
            "<meta http-equiv='refresh' content='0; url=https://docs.google.com/spreadsheets/d/19G9cu2tY-Y8_KtkPgQF-b96w1ZPnumVBGT2doeOaBmo/edit?usp=drive_link'>",
            unsafe_allow_html=True
        )

    # Button 2 → Local HTML display
    html_file = "2026ver.html"
    if st.button("통계 HTML 보기"):
        try:
            with open(html_file, "r", encoding="utf-8") as f:
                html_content = f.read()
            st.components.v1.html(html_content, height=800, scrolling=True)
        except FileNotFoundError:
            st.error("⚠️ 2026ver.html 파일이 GitHub에 없습니다.")

    st.markdown("---")

    # 🔙 뒤로가기 버튼
    if st.button("🔙 로그아웃 / 뒤로가기"):
        st.session_state["logged_in"] = False
        st.session_state["user_id"] = None
        st.rerun()

# ------------------------------------------------------
# 🚀 앱 실행 로직
# ------------------------------------------------------
def app():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
        st.session_state["user_id"] = None

    if st.session_state["logged_in"]:
        main_page()
    else:
        login_page()

if __name__ == "__main__":
    app()

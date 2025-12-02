import streamlit as st
import base64

# --- Config ---
st.set_page_config(page_title="Login Demo", layout="centered")

# Hardcoded login credentials
VALID_ID = "30628"
VALID_PW = "두둥탁"

# --- Login Page ---
def login_page():
    st.title("로그인")

    user_id = st.text_input("아이디", value="", placeholder="아이디 입력", key="id")
    password = st.text_input("비밀번호", value="", placeholder="비밀번호 입력", type="password", key="pw")

    if st.button("로그인"):
        if user_id == VALID_ID and password == VALID_PW:
            st.session_state["logged_in"] = True
            st.rerun()
        else:
            st.error("아이디 또는 비밀번호가 올바르지 않습니다.")

# --- Page with Two Buttons ---
def main_page():
    st.title("메인 화면")
    st.write("원하는 버튼을 선택하세요.")

    # Button 1 → Google Sheet
    if st.button("Google Sheet 열기"):
        st.markdown("<meta http-equiv='refresh' content='0; url=https://docs.google.com/spreadsheets/d/19G9cu2tY-Y8_KtkPgQF-b96w1ZPnumVBGT2doeOaBmo/edit?usp=drive_link'>", unsafe_allow_html=True)

    # Button 2 → Local HTML display
    uploaded_html = "2026ver.html"
    try:
        with open(uploaded_html, "r", encoding="utf-8") as f:
            html_content = f.read()
        if st.button("통계 HTML 보기"):
            st.components.v1.html(html_content, height=800, scrolling=True)
    except FileNotFoundError:
        st.warning("2026ver.html 파일이 현재 폴더에 없습니다. GitHub에 업로드했는지 확인하세요.")

# --- App Logic ---
def app():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if not st.session_state["logged_in"]:
        login_page()
    else:
        main_page()

if __name__ == "__main__":
    app()

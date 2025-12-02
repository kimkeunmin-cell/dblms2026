import streamlit as st
import pandas as pd
import plotly.graph_objects as go

ACCOUNTS_FILE = "accounts.csv"
SHEETS_FILE = "sheets.csv"

ANALYSIS_COLUMNS = [
    "낮잠(시간)", "밤잠(시간)", "수면(시간)", "문학(시간)", "비문학(시간)", "화언(시간)", "국어기타(시간)", "국어합(시간)",
    "대수(시간)", "미적(시간)", "확통(시간)", "수학기타(시간)", "수학합(시간)",
    "어휘문법(시간)", "듣기(시간)", "독해(시간)", "영어기타(시간)", "영어합(시간)",
    "통사(시간)", "통과(시간)", "탐구기타(시간)", "내신기타(시간)", "탐구합(시간)", "전체합(시간)"
]

st.set_page_config(page_title="학습 관리 시스템", layout="centered")

# ------------------ 로그인 ------------------
def check_login(user_id, user_pw):
    try:
        df = pd.read_csv(ACCOUNTS_FILE, dtype=str)
    except Exception as e:
        st.warning(f"accounts.csv 읽기 실패: {e}")
        return None

    row = df[(df['id'] == user_id) & (df['password'] == user_pw)]
    if row.empty:
        return None
    return row.iloc[0]

def login_page():
    st.title("로그인")
    user_id = st.text_input("아이디", value="")
    user_pw = st.text_input("비밀번호", value="", type="password")

    login_clicked = st.button("로그인")
    if login_clicked:
        user = check_login(user_id, user_pw)
        if user is not None:
            st.session_state['logged_in'] = True
            st.session_state['user_id'] = user_id
            st.session_state['role'] = user.get('role', 'student')
            st.experimental_rerun()
        else:
            st.error("아이디 또는 비밀번호가 잘못되었습니다.")

# ------------------ 학생 페이지 ------------------
def student_page():
    st.title(f"학생 페이지 - {st.session_state['user_id']}")

    # 시트 URL 가져오기
    sheet_url = None
    try:
        df_sheets = pd.read_csv(SHEETS_FILE, dtype=str)
        row = df_sheets[df_sheets['id'] == st.session_state['user_id']]
        if not row.empty:
            sheet_url = row.iloc[0]['sheet_url']
    except Exception as e:
        st.warning(f"sheets.csv 읽기 실패: {e}")

    if sheet_url:
        device = st.radio("PC 또는 모바일(스마트폰, 태블릿PC)", ["PC", "모바일(스마트폰, 태블릿PC)"])
        if device == "PC":
            try:
                pc_url = sheet_url + "&widget=true&headers=true"
                st.components.v1.html(f"<iframe src='{pc_url}' style='width:200%; height:600px; border:none;'></iframe>", height=600)
            except Exception as e:
                st.warning(f"iframe 렌더링 실패: {e}")
        else:
            st.markdown(f"<a href='{sheet_url}' target='_blank'>📄 Google Sheet 새 탭에서 열기</a>", unsafe_allow_html=True)

        # CSV로 변환 후 DataFrame 확인
        st.markdown("---")
        st.subheader("CSV 데이터 확인")
        try:
            # 시트 ID 추출 및 CSV URL 생성
            sheet_id = sheet_url.split('/d/')[1].split('/')[0]
            csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"

            df_csv = pd.read_csv(csv_url, engine='python', on_bad_lines='skip')
            df_csv.columns = df_csv.columns.str.strip().str.replace('\r','').str.replace('\n','').str.replace(' ','_')

            st.write("상위 10행 샘플 데이터")
            st.dataframe(df_csv.head(10))

            st.write("컬럼 목록")
            st.write(df_csv.columns.tolist())

        except Exception as e:
            st.warning(f"CSV 로드 실패: {e}")

    else:
        st.warning("해당 학생의 시트 정보가 없습니다.")

    if st.button("🔙 로그아웃"):
        st.session_state.clear()
        st.experimental_rerun()

# ------------------ 관리자 페이지 ------------------
def admin_page():
    st.title("관리자 모드")
    st.write("학생 관리 / 전체 보고서 / 링크 설정 기능 제공")

# ------------------ 앱 시작 ------------------
def app():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        login_page()
    else:
        role = st.session_state.get('role', 'student')
        if role == 'admin':
            admin_page()
        else:
            student_page()

if __name__ == "__main__":
    app()

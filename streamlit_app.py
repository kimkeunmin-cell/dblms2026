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
            st.experimental_rerun()  # 버튼 클릭 시 안전하게 호출
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

    # 환경 선택
    if sheet_url:
        device = st.radio("PC 또는 모바일", ["PC", "모바일"])
        if device == "PC":
            try:
                pc_url = sheet_url + "&widget=true&headers=true"
                st.components.v1.html(f"<iframe src='{pc_url}' style='width:100%; height:600px; border:none;'></iframe>", height=600)
            except Exception as e:
                st.warning(f"iframe 렌더링 실패: {e}")
        else:
            st.markdown(f"<a href='{sheet_url}' target='_blank'>📄 Google Sheet 새 탭에서 열기</a>", unsafe_allow_html=True)

    else:
        st.warning("해당 학생의 시트 정보가 없습니다.")

    # 통계 및 시각화
    data_df = None
    if sheet_url:
        try:
            csv_url = sheet_url.replace('/edit?usp=sharing', '/gviz/tq?tqx=out:csv')
            data_df = pd.read_csv(csv_url, engine='python', on_bad_lines='skip', header=0)
            data_df.columns = data_df.columns.str.strip().str.replace('\r','')
            if '일시' in data_df.columns:
                data_df['일시'] = pd.to_datetime(data_df['일시'], errors='coerce')
            else:
                st.warning(f"CSV 컬럼 확인 필요: {data_df.columns.tolist()}")
                data_df = None
        except Exception as e:
            st.warning(f"CSV 로드 실패: {e}")
            data_df = None

    if data_df is not None:
        st.write("### 분석 기간 및 변수 선택")
        start_date, end_date = st.date_input("기간 선택", [data_df['일시'].min(), data_df['일시'].max()])
        selected_cols = st.multiselect("분석할 변수 선택", options=ANALYSIS_COLUMNS, default=ANALYSIS_COLUMNS)

        mask = (data_df['일시'] >= pd.to_datetime(start_date)) & (data_df['일시'] <= pd.to_datetime(end_date))
        filtered_df = data_df.loc[mask]

        if not filtered_df.empty:
            fig = go.Figure()
            for col in selected_cols:
                fig.add_trace(go.Bar(
                    y=filtered_df['일시'].dt.strftime('%Y-%m-%d'),
                    x=filtered_df[col],
                    name=col,
                    orientation='h'
                ))
            fig.update_layout(barmode='stack', title='가로형 누적 막대그래프', xaxis_title='시간', yaxis_title='일시', height=500)
            st.plotly_chart(fig, use_container_width=True)

            # 목표값 비교 그래프
            goal_df = pd.read_csv(csv_url, engine='python', quotechar='"', nrows=2, on_bad_lines='skip', header=None)
            goals = pd.to_numeric(goal_df.iloc[1, 1:], errors='coerce')
            means = filtered_df[selected_cols].mean()

            fig2 = go.Figure()
            fig2.add_trace(go.Bar(x=selected_cols, y=means, name='실제 평균', marker_color='skyblue'))
            fig2.add_trace(go.Scatter(x=selected_cols, y=goals, mode='lines+markers', name='목표', line=dict(color='red', dash='dash')))
            fig2.update_layout(title='목표 대비 평균', yaxis_title='시간', height=400)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("선택된 기간에 데이터가 없습니다.")

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

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

ACCOUNTS_FILE = "accounts.csv"
SHEETS_FILE = "sheets.csv"

st.set_page_config(page_title="Login System", layout="centered")

def check_login(user_id, user_pw):
    try:
        df = pd.read_csv(ACCOUNTS_FILE, dtype=str)
    except FileNotFoundError:
        st.error("⚠️ accounts.csv 파일이 없습니다.")
        return None

    row = df[(df['id'] == user_id) & (df['password'] == user_pw)]
    if row.empty:
        return None
    return row.iloc[0]

def mobile_header():
    st.markdown(
        "<style> .stButton>button { width:100%; height:50px; font-size:20px; } </style>",
        unsafe_allow_html=True
    )

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

def student_page():
    mobile_header()
    st.title("학생 페이지")
    st.write(f"{st.session_state['user_id']}님 환영합니다.")

    try:
        df = pd.read_csv(SHEETS_FILE, dtype=str)
        row = df[df['id'] == st.session_state['user_id']]
        sheet_url = row.iloc[0]['sheet_url'] if not row.empty else None
    except FileNotFoundError:
        sheet_url = None
        st.error("⚠️ sheets.csv 파일이 없습니다.")

    st.subheader("📄 학습 기록 보기")

    if sheet_url:
        st.write("사용하실 환경을 선택하세요:")
        device = st.radio("PC 또는 모바일", ["PC", "모바일"])

        if device == "PC":
            pc_url = sheet_url + "&widget=true&headers=true"
            st.components.v1.html(f"<iframe src='{pc_url}' style='width:100%; height:400px; border:none;'></iframe>", height=420)
        else:
            st.markdown(f"""
            <div style='text-align:center; margin:20px 0;'>
                <a href='{sheet_url}' target='_blank' style='
                    display:inline-block;
                    background-color:#4CAF50;
                    color:white;
                    padding:15px 25px;
                    font-size:18px;
                    font-weight:bold;
                    border-radius:8px;
                    text-decoration:none;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.2);
                    transition: 0.3s;
                ' onmouseover="this.style.backgroundColor='#45a049'" onmouseout="this.style.backgroundColor='#4CAF50'">
                    📄 Google Sheet 새 탭에서 열기
                </a>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("📊 학습 통계 (인터랙티브)")

        try:
            csv_url = sheet_url.replace('/edit?usp=sharing', '/gviz/tq?tqx=out:csv')
            data_df = pd.read_csv(csv_url)
            data_df['date'] = pd.to_datetime(data_df['date'], errors='coerce')

            # 목표값 추출 (2행)
            goal_df = pd.read_csv(csv_url, header=None, nrows=2)
            goals = goal_df.iloc[1, 1:]

            # 사용자 입력
            st.write("### 분석 기간 및 과목 선택")
            start_date = st.date_input("시작일", value=data_df['date'].min())
            end_date = st.date_input("종료일", value=data_df['date'].max())
            cols = st.multiselect("분석할 과목 선택", options=data_df.columns[1:], default=data_df.columns[1:])

            mask = (data_df['date'] >= pd.to_datetime(start_date)) & (data_df['date'] <= pd.to_datetime(end_date))
            filtered_df = data_df.loc[mask]

            # --------------------
            # 가로형 누적 막대그래프 (Plotly)
            # --------------------
            if not filtered_df.empty:
                fig = go.Figure()
                for col in cols:
                    fig.add_trace(go.Bar(
                        y=filtered_df['date'].dt.strftime('%Y-%m-%d'),
                        x=filtered_df[col],
                        name=col,
                        orientation='h'
                    ))
                fig.update_layout(barmode='stack', title='가로형 누적 막대그래프', xaxis_title='시간', yaxis_title='날짜', height=500)
                st.plotly_chart(fig, use_container_width=True)

                # --------------------
                # 목표 대비 평균 세로형 막대그래프
                # --------------------
                means = filtered_df[cols].mean()
                fig2 = go.Figure()
                fig2.add_trace(go.Bar(x=cols, y=means, name='실제 평균', marker_color='skyblue'))
                fig2.add_trace(go.Scatter(x=cols, y=goals.values, mode='lines+markers', name='목표', line=dict(color='red', dash='dash')))
                fig2.update_layout(title='목표 대비 평균', yaxis_title='시간', height=400)
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("선택된 기간에 데이터가 없습니다.")

        except Exception as e:
            st.warning(f"통계 불러오기 실패: {e}")

    else:
        st.warning("해당 학생의 시트 정보가 없습니다.")

    if st.button("🔙 로그아웃"):
        st.session_state.clear()
        st.rerun()

def admin_page():
    mobile_header()
    st.title("관리자 모드")
    st.write("학생 관리 / 전체 보고서 / 링크 설정 기능 제공")

    tab1, tab2 = st.tabs(["📁 전체 학생 리스트", "⚙️ 시트 매핑 관리"])

    with tab1:
        try:
            df = pd.read_csv(ACCOUNTS_FILE)
            st.dataframe(df)
        except:
            st.error("accounts.csv 불러오기 실패")

    with tab2:
        try:
            df2 = pd.read_csv(SHEETS_FILE)
            st.dataframe(df2)
        except:
            st.error("sheets.csv 불러오기 실패")

    if st.button("🔙 로그아웃"):
        st.session_state.clear()
        st.rerun()

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

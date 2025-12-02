import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

ACCOUNTS_FILE = "accounts.csv"
SHEETS_FILE = "sheets.csv"

ANALYSIS_COLUMNS = [
    "낮잠(시간)", "밤잠(시간)", "수면(시간)", "문학(시간)", "비문학(시간)", "화언(시간)", "국어기타(시간)", "국어합(시간)",
    "대수(시간)", "미적(시간)", "확통(시간)", "수학기타(시간)", "수학합(시간)",
    "어휘문법(시간)", "듣기(시간)", "독해(시간)", "영어기타(시간)", "영어합(시간)",
    "통사(시간)", "통과(시간)", "탐구기타(시간)", "내신기타(시간)", "탐구합(시간)", "전체합(시간)"
]

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
            st.components.v1.html(
                f"<iframe src='{pc_url}' style='width:100%; height:900px; border:none;'></iframe>",
                height=900
            )
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
            data_df = pd.read_csv(csv_url, engine='python', quotechar='"', on_bad_lines='skip', header=0)

            # 컬럼 이름 앞뒤 공백 제거 
            data_df.columns = data_df.columns.str.strip().str.replace('\r','')

            # 일시 컬럼 확인 후 변환
            if '일시' not in data_df.columns:
                st.error(f"CSV 컬럼 확인 필요: {data_df.columns.tolist()}")
                return
            data_df['일시'] = pd.to_datetime(data_df['일시'], errors='coerce')

            # 목표값 추출 (2행)
            goal_df = pd.read_csv(csv_url, engine='python', quotechar='"', nrows=2, on_bad_lines='skip', header=None)
            goals = pd.to_numeric(goal_df.iloc[1, 1:], errors='coerce')

            # 사용자 입력: 시작일, 종료일, 변수 선택
            st.write("### 분석 기간 및 변수 선택")
            start_date, end_date = st.date_input("기간 선택 (시작일, 종료일)", [data_df['일시'].min(), data_df['일시'].max()])
            selected_cols = st.multiselect("분석할 변수 선택", options=ANALYSIS_COLUMNS, default=ANALYSIS_COLUMNS)

            mask = (data_df['일시'] >= pd.to_datetime(start_date)) & (data_df['일시'] <= pd.to_datetime(end_date))
            filtered_df = data_df.loc[mask]

            # 가로형 누적 막대그래프
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

                # 목표 대비 평균 세로형 막대그래프
                means = filtered_df[selected_cols].mean()
                fig2 = go.Figure()
                fig2.add_trace(go.Bar(x=selected_cols, y=means, name='실제 평균', marker_color='skyblue'))
                fig2.add_trace(go.Scatter(x=selected_cols, y=goals, mode='lines+markers', name='목표', line=dict(color='red', dash='dash')))
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

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

ACCOUNTS_FILE = "accounts.csv"
SHEETS_FILE = "sheets.csv"

# ------------------------
# 그룹 정의
# ------------------------
GROUPS = {
    "수면": ["낮잠(시간)", "밤잠(시간)", "수면(시간)"],
    "국어": ["문학(시간)", "비문학(시간)", "화언(시간)", "국어기타(시간)"],
    "수학": ["대수(시간)", "미적(시간)", "확통(시간)", "수학기타(시간)"],
    "영어": ["어휘문법(시간)", "듣기(시간)", "독해(시간)", "영어기타(시간)"],
    "탐구": ["통사(시간)", "통과(시간)", "탐구기타(시간)", "내신기타(시간)"],
    "종합": ["국어합(시간)", "수학합(시간)", "영어합(시간)", "탐구합(시간)"]
}

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
    if st.button("로그인"):
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

    # ------------------ Google Sheet URL 가져오기 ------------------
    sheet_url = None
    try:
        df_sheets = pd.read_csv(SHEETS_FILE, dtype=str)
        row = df_sheets[df_sheets['id'] == st.session_state['user_id']]
        if not row.empty:
            sheet_url = row.iloc[0]['sheet_url']
    except Exception as e:
        st.warning(f"sheets.csv 읽기 실패: {e}")

    if not sheet_url:
        st.warning("해당 학생의 시트 정보가 없습니다.")
        return

    # ------------------ Google Sheet iframe/링크 표시 ------------------
    device = st.radio("PC 또는 모바일", ["PC", "모바일"])
    if device == "PC":
        try:
            pc_url = sheet_url + "&widget=true&headers=true"
            st.components.v1.html(
                f"<iframe src='{pc_url}' style='width:100%; height:600px; border:none;'></iframe>",
                height=600
            )
        except Exception as e:
            st.warning(f"iframe 렌더링 실패: {e}")
    else:
        st.markdown(f"<a href='{sheet_url}' target='_blank'>📄 Google Sheet 새 탭에서 열기</a>", unsafe_allow_html=True)

    # ------------------ CSV 로드 ------------------
    try:
        sheet_id = sheet_url.split('/d/')[1].split('/')[0]
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"
        df_csv = pd.read_csv(csv_url, engine='python', on_bad_lines='skip')

        # 컬럼 정규화
        df_csv.columns = (
            df_csv.columns
            .str.strip()
            .str.replace('\r','',regex=False)
            .str.replace('\n','',regex=False)
            .str.replace(' ','',regex=False)
            .str.replace('　','',regex=False)
        )

    except Exception as e:
        st.warning(f"CSV 로드 실패: {e}")
        return

    # ------------------ 날짜 범위 선택 ------------------
    st.markdown("---")
    st.subheader("📊 시각화를 위한 기간 선택")
    try:
        df_csv["일시"] = pd.to_datetime(df_csv["일시"], errors='coerce')
        df_csv = df_csv.dropna(subset=["일시"])
    except:
        st.error("❌ '일시' 컬럼 날짜 변환 실패.")
        return

    min_date = df_csv["일시"].min()
    max_date = df_csv["일시"].max()
    start_date = st.date_input("📅 시작 날짜", value=min_date, min_value=min_date, max_value=max_date)
    end_date = st.date_input("📅 종료 날짜", value=max_date, min_value=min_date, max_value=max_date)
    if start_date > end_date:
        st.warning("⚠ 종료 날짜가 시작 날짜보다 빠를 수 없습니다.")
        return

    df_range = df_csv[(df_csv["일시"] >= pd.to_datetime(start_date)) &
                      (df_csv["일시"] <= pd.to_datetime(end_date))]

    st.markdown("---")
    st.subheader("선택 날짜 범위 데이터")
    st.dataframe(df_range)

    # ------------------ 그룹 + 변수 선택 ------------------
    st.markdown("---")
    st.subheader("그룹 선택 및 변수 선택")
    selected_group = st.selectbox("그룹 선택", list(GROUPS.keys()))
    variables = GROUPS[selected_group]
    selected_vars = st.multiselect("변수 선택", variables, default=variables)

    if not selected_vars:
        st.info("하나 이상의 변수를 선택해주세요.")
        return

    # ------------------ 누적 막대 그래프 ------------------
    st.markdown("---")
    st.subheader("📊 누적 막대 그래프")
    fig = go.Figure()
    for var in selected_vars:
        fig.add_trace(go.Bar(
            y=df_range["일시"].dt.strftime("%Y-%m-%d"),
            x=pd.to_numeric(df_range[var], errors='coerce').fillna(0),
            orientation='h',
            name=var,
            text=pd.to_numeric(df_range[var], errors='coerce').fillna(0).round(2),
            texttemplate='%{text}',
            textposition='inside',
            hovertemplate='(%{y}) %{x:.2f}시간<extra></extra>'
        ))
    fig.update_layout(
        barmode='stack',
        xaxis_title="시간(시간)",
        yaxis_title="날짜",
        yaxis={'autorange':'reversed'},
        height=600,
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True)

    # ------------------ 목표 대비 평균 그래프 ------------------
    st.markdown("---")
    st.subheader("🎯 목표 대비 평균 비교")
    goal_values = df_csv[selected_vars].iloc[0]
    avg_values = df_range[selected_vars].mean()

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=selected_vars,
        y=avg_values.round(2),
        name="평균",
        marker_color='skyblue',
        text=avg_values.round(2),
        texttemplate='%{text}',
        textposition='outside',
        hovertemplate='(%{x}) %{y:.2f}시간<extra></extra>'
    ))
    fig2.add_trace(go.Bar(
        x=selected_vars,
        y=goal_values.round(2),
        name="목표",
        marker_color='orange',
        text=goal_values.round(2),
        texttemplate='%{text}',
        textposition='outside',
        hovertemplate='(%{x}) %{y:.2f}시간<extra></extra>'
    ))
    fig2.update_layout(
        yaxis_title="시간(시간)",
        xaxis_title="항목",
        xaxis=dict(tickangle=-45),
        height=500,
        barmode='group',
        template="plotly_white"
    )
    st.plotly_chart(fig2, use_container_width=True)

    # ------------------ 로그아웃 ------------------
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

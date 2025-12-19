import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import datetime
import plotly.express as px

# ================== 기본 설정 ==================
st.set_page_config(page_title="학습 관리 시스템", layout="centered")

ACCOUNTS_FILE = "accounts.csv"
SHEETS_FILE = "sheets.csv"

# 변수 정의
GROUPS = {
    "수면": ["낮잠(시간)", "밤잠(시간)"],
    "종합": ["국어합(시간)", "수학합(시간)", "영어합(시간)", "탐구합(시간)"],
    "국어": ["문학(시간)", "비문학(시간)", "화언(시간)", "국어기타(시간)"],
    "수학": ["대수(시간)", "미적(시간)", "확통(시간)", "수학기타(시간)"],
    "영어": ["어휘문법(시간)", "듣기(시간)", "독해(시간)", "영어기타(시간)"],
    "탐구": ["통사(시간)", "통과(시간)", "탐구기타(시간)", "내신기타(시간)"]
}

# 주간 리포트용 기간
PRESET_PERIODS = {
    "1주차 (3/1~3/7)": ("2026-03-01", "2026-03-07"),
    "2주차 (3/8~3/14)": ("2026-03-08", "2026-03-14"),
    "중간고사 대비 주간": ("2026-04-10", "2026-04-16"),
    "기말고사 대비 주간": ("2026-06-01", "2026-06-07"),
}

# ================== 로그인 ==================
def check_login(user_id, user_pw):
    try:
        df = pd.read_csv(ACCOUNTS_FILE, dtype=str)
    except:
        st.warning(f"accounts.csv 읽기 실패: {e}")
        return Nonedf[(df["id"] == user_id) & (df["password"] == user_pw)]
    if row.empty:
        return None
    return row.iloc[0]

def login_page():
    st.title("로그인")

    with st.form("login_form"):
        user_id = st.text_input("아이디")
        user_pw = st.text_input("비밀번호", type="password")
        submitted = st.form_submit_button("로그인")

    if submitted:
        user = check_login(user_id, user_pw)
        if user is not None:
            st.session_state["logged_in"] = True
            st.session_state["user_id"] = user_id
            st.session_state["role"] = user.get("role", "student")
            st.rerun()
        else:
            st.error("아이디 또는 비밀번호가 잘못되었습니다.")

# ================== 학생 페이지 ==================
def student_page():
    st.title(f"학생 페이지 - {st.session_state['user_id']}")

    tab1, tab2 = st.tabs(["📅 직접 기간 선택", "📊 주간별 리포트"])

    # ---------------- TAB 1 ----------------
    with tab1:
        st.subheader("직접 기간 선택")

        try:
            df_sheets = pd.read_csv(SHEETS_FILE, dtype=str)
            row = df_sheets[df_sheets["id"] == st.session_state["user_id"]]
            if row.empty:
                st.warning("시트가 연결되지 않았습니다.")
                return
            sheet_url = row.iloc[0]["sheet_url"]
        except:
            st.warning("시트 정보를 불러올 수 없습니다.")
            return

        sheet_id = sheet_url.split("/d/")[1].split("/")[0]
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"

        try:
            df_csv = pd.read_csv(csv_url)
            df_csv.columns = df_csv.columns.str.strip()
            df_csv["일시"] = pd.to_datetime(df_csv["일시"], errors="coerce")
            df_csv = df_csv.dropna(subset=["일시"])
            st.session_state["df_csv"] = df_csv
        except:
            st.warning("CSV 로드 실패")
            return

        min_date = df_csv["일시"].min().date()
        max_date = df_csv["일시"].max().date()

        start_date = st.date_input("시작일", min_date)
        end_date = st.date_input("종료일", max_date)

        if start_date > end_date:
            st.warning("날짜 범위 오류")
            return

        df_range = df_csv[
            (df_csv["일시"] >= pd.to_datetime(start_date)) &
            (df_csv["일시"] <= pd.to_datetime(end_date))
        ]

        st.dataframe(df_range)

    # ---------------- TAB 2 ----------------
    with tab2:
        st.subheader("주간별 리포트")

        if "df_csv" not in st.session_state:
            st.warning("TAB1에서 데이터를 먼저 불러오세요.")
            return

        df_csv = st.session_state["df_csv"]

        if "weekly_mode" not in st.session_state:
            st.session_state["weekly_mode"] = False

        period = st.selectbox("기간 선택", list(PRESET_PERIODS.keys()))

        if st.button("리포트 보기"):
            st.session_state["weekly_mode"] = True
            st.session_state["weekly_period"] = period
            st.rerun()

        if not st.session_state["weekly_mode"]:
            return

        start, end = PRESET_PERIODS[st.session_state["weekly_period"]]
        df_range = df_csv[(df_csv["일시"] >= start) & (df_csv["일시"] <= end)]

        if df_range.empty:
            st.warning("데이터 없음")
            return

        st.dataframe(df_range)

        group = st.selectbox("그룹", list(GROUPS.keys()))
        vars_ = st.multiselect("변수", GROUPS[group], default=GROUPS[group])

        if not vars_:
            st.info("변수를 선택하세요.")
            return

        fig = go.Figure()
        for v in vars_:
            fig.add_trace(go.Bar(
                y=df_range["일시"].dt.strftime("%Y-%m-%d"),
                x=pd.to_numeric(df_range[v], errors="coerce").fillna(0),
                orientation="h",
                name=v
            ))

        fig.update_layout(barmode="stack", height=600)
        st.plotly_chart(fig, use_container_width=True)

    if st.button("🔙 로그아웃"):
        st.session_state.clear()
        st.rerun()

# ================== 앱 진입 ==================
def app():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if not st.session_state["logged_in"]:
        login_page()
    else:
        student_page()

app()

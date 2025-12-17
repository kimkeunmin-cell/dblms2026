import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import datetime
import plotly.express as px

# Constants
ACCOUNTS_FILE = "accounts.csv"
SHEETS_FILE = "sheets.csv"
GROUPS = {
    "수면": ["낮잠(시간)", "밤잠(시간)"],
    "종합": ["국어합(시간)", "수학합(시간)", "영어합(시간)", "탐구합(시간)"],
    "국어": ["문학(시간)", "비문학(시간)", "화언(시간)", "국어기타(시간)"],
    "수학": ["대수(시간)", "미적(시간)", "확통(시간)", "수학기타(시간)"],
    "영어": ["어휘문법(시간)", "듣기(시간)", "독해(시간)", "영어기타(시간)"],
    "탐구": ["통사(시간)", "통과(시간)", "탐구기타(시간)", "내신기타(시간)"]
}
PRESET_PERIODS = {
    "1주차 (3/1~3/7)": ("2026-03-01", "2026-03-07"),
    "2주차 (3/8~3/14)": ("2026-03-08", "2026-03-14"),
    "중간고사 대비 주간": ("2026-04-10", "2026-04-16"),
    "기말고사 대비 주간": ("2026-06-01", "2026-06-07")
}

st.set_page_config(page_title="학습 관리 시스템", layout="centered")

def login_page():
    ...  # Login logic implementation

def student_page():
    ...  # Student page logic implementation


def admin_page():
    st.title("관리자 모드")


def app():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if not st.session_state["logged_in"]:
        login_page()
    else:
        role = st.session_state.get("role", "student")
        if role == "admin":
            admin_page()
        else:
            student_page()

if __name__ == "__main__":
    app()
    with tab3:
        st.subheader("📈 변수별 주간 평균 추이")

        st.caption("각 변수의 1주일 평균 학습시간을 꺾은선 그래프로 표시합니다.")

        # ------------------ 그룹 & 변수 선택 ------------------
        selected_group = st.selectbox(
            "그룹 선택 (주간 평균)",
            list(GROUPS.keys()),
            key="weekly_line_group"
        )

        variables = GROUPS[selected_group]

        selected_vars = st.multiselect(
            "변수 선택 (주간 평균)",
            variables,
            default=variables,
            key="weekly_line_vars"
        )

        if not selected_vars:
            st.info("하나 이상의 변수를 선택해주세요.")
            st.stop()

        # ------------------ 날짜 전처리 ------------------
        df_line = df_csv.copy()
        df_line["일시"] = pd.to_datetime(df_line["일시"], errors="coerce")
        df_line = df_line.dropna(subset=["일시"])

        # 주차 컬럼 (월요일 기준 주)
        df_line["주차"] = df_line["일시"].dt.to_period("W-MON").astype(str)

        # ------------------ 주차별 평균 계산 ------------------
        weekly_avg = (
            df_line
            .groupby("주차")[selected_vars]
            .mean()
            .reset_index()
        )

        if weekly_avg.empty:
            st.warning("주간 평균을 계산할 데이터가 없습니다.")
            st.stop()

        # ------------------ 꺾은선 그래프 ------------------
        fig = go.Figure()

        for var in selected_vars:
            fig.add_trace(go.Scatter(
                x=weekly_avg["주차"],
                y=weekly_avg[var],
                mode="lines+markers",
                name=var,
                hovertemplate=(
                    f"{var}<br>"
                    "주차: %{x}<br>"
                    "평균: %{y:.2f}시간"
                    "<extra></extra>"
                )
            ))

        fig.update_layout(
            xaxis_title="주차",
            yaxis_title="주간 평균 시간(시간)",
            template="plotly_white",
            height=600,
            legend_title="변수",
            hovermode="x unified",
            margin=dict(l=40, r=40, t=60, b=120)
        )

        fig.update_traces(marker=dict(size=8), line=dict(width=3))

        st.plotly_chart(fig, use_container_width=True)

        if st.button("🔙 로그아웃"):
            st.session_state.clear()
            st.experimental_rerun()
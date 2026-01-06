import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import datetime
import plotly.express as px
import io

# ================== 기본 설정 ==================
st.set_page_config(page_title="학습 관리 시스템", layout="centered")

# ================== GitHub 주간 순위 ==================
BASE_GITHUB_URL = (
    "https://raw.githubusercontent.com/kimkeunmin-cell/dblms2026/main/weekly_rank"
)

ACCOUNTS_FILE = "accounts.csv"
SHEETS_FILE = "sheets.csv"

# ---------- 기준값 ----------
MIN_STUDY_HOURS = 45.5    # 주당 최소 공부 시간 (6.5h * 7)
MIN_SLEEP_HOURS = 45.5    # 주당 최소 수면 시간 (6.5h * 7)


# 변수 정의
GROUPS = {
    "수면": ["낮잠(시간)", "밤잠(시간)"],
    "종합": ["국어합(시간)", "수학합(시간)", "영어합(시간)", "탐구합(시간)"],
    "국어": ["문학(시간)", "비문학(시간)", "화언(시간)", "국어기타(시간)"],
    "수학": ["대수(시간)", "미적(시간)", "확통(시간)", "수학기타(시간)"],
    "영어": ["어휘문법(시간)", "듣기(시간)", "독해(시간)", "영어기타(시간)"],
    "탐구": ["통사(시간)", "통과(시간)", "탐구기타(시간)", "내신기타(시간)"]
}

# GROUPS 전체 변수 (중복 제거)
ALL_VARS = []
for vars_ in GROUPS.values():
    for v in vars_:
        if v not in ALL_VARS:
            ALL_VARS.append(v)

# 합산 대상
SUM_VARS = ["국어합(시간)", "수학합(시간)", "영어합(시간)", "탐구합(시간)"]

# 주간 리포트용 기간
PRESET_PERIODS = {
    "1주차 (3/1~3/7)": ("2026-03-01", "2026-03-07"),
    "2주차 (3/8~3/14)": ("2026-03-08", "2026-03-14"),
    "3주차 (3/15~3/21)": ("2026-03-15", "2026-03-21"),
    "4주차 (3/22~3/28)": ("2026-03-22", "2026-03-28"),
    "5주차 (3/29~4/4)": ("2026-03-29", "2026-04-04"),
    "6주차 (4/5~4/11)": ("2026-04-05", "2026-04-11"),
    "7주차 (4/12~4/18)": ("2026-04-12", "2026-04-18"),
    "8주차 (4/19~4/25)": ("2026-04-19", "2026-04-25"),
    "9주차 (4/26~5/2)": ("2026-04-26", "2026-05-02"),
    "10주차 (5/3~5/9)": ("2026-05-03", "2026-05-09"),
    "11주차 (5/10~5/16)": ("2026-05-10", "2026-05-16"),
    "12주차 (5/17~5/23)": ("2026-05-17", "2026-05-23"),
    "13주차 (5/24~5/30)": ("2026-05-24", "2026-05-30"),
    "14주차 (5/31~6/6)": ("2026-05-31", "2026-06-06"),
    "15주차 (6/7~6/13)": ("2026-06-07", "2026-06-13"),
    "16주차 (6/14~6/20)": ("2026-06-14", "2026-06-20"),
    "17주차 (6/21~6/27)": ("2026-06-21", "2026-06-27"),
    "18주차 (6/28~7/4)": ("2026-06-28", "2026-07-04"),
    "19주차 (7/5~7/11)": ("2026-07-05", "2026-07-11"),
    "20주차 (7/12~7/18)": ("2026-07-12", "2026-07-18"),
    "21주차 (7/19~7/25)": ("2026-07-19", "2026-07-25"),
    "22주차 (7/26~8/1)": ("2026-07-26", "2026-08-01"),
    "23주차 (8/2~8/8)": ("2026-08-02", "2026-08-08"),
    "24주차 (8/9~8/15)": ("2026-08-09", "2026-08-15"),
    "25주차 (8/16~8/22)": ("2026-08-16", "2026-08-22"),
    "26주차 (8/23~8/29)": ("2026-08-23", "2026-08-29"),
    "27주차 (8/30~9/5)": ("2026-08-30", "2026-09-05"),
    "28주차 (9/6~9/12)": ("2026-09-06", "2026-09-12"),
    "29주차 (9/13~9/19)": ("2026-09-13", "2026-09-19"),
    "30주차 (9/20~9/26)": ("2026-09-20", "2026-09-26"),
    "31주차 (9/27~10/3)": ("2026-09-27", "2026-10-03"),
    "32주차 (10/4~10/10)": ("2026-10-04", "2026-10-10"),
    "33주차 (10/11~10/17)": ("2026-10-11", "2026-10-17"),
    "34주차 (10/18~10/24)": ("2026-10-18", "2026-10-24"),
    "35주차 (10/25~10/31)": ("2026-10-25", "2026-10-31"),
    "36주차 (11/1~11/7)": ("2026-11-01", "2026-11-07"),
    "37주차 (11/8~11/14)": ("2026-11-08", "2026-11-14"),
    "38주차 (11/15~11/21)": ("2026-11-15", "2026-11-21"),
    "39주차 (11/22~11/28)": ("2026-11-22", "2026-11-28"),
    "40주차 (11/29~12/5)": ("2026-11-29", "2026-12-05"),
    "41주차 (12/6~12/12)": ("2026-12-06", "2026-12-12"),
    "42주차 (12/13~12/19)": ("2026-12-13", "2026-12-19"),
    "43주차 (12/20~12/26)": ("2026-12-20", "2026-12-26"),
    "44주차 (12/27~12/31)": ("2026-12-27", "2026-12-31")}

# 통계 다운로드용
def dataframe_to_xlsx_bytes(df, sheet_name="통계"):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(
            writer,
            index=False,
            sheet_name=sheet_name
        )
    output.seek(0)
    return output

# 교사용 코멘트 (여러 가지 경우의 수 만들어야 함) #######################################################################################
def make_teacher_comment_soft(curr, prev):
    study_diff = curr["공부총합"] - prev["공부총합"]

    if study_diff > 0:
        comment = (
            "이전 주보다 학습량이 증가하였습니다. 긍정적인 변화입니다. "
            "앞으로도 꾸준히 이어나가되, 과도한 무리로 흐름을 깨지 않도록 합시다."
        )
    elif study_diff < 0:
        comment = (
            "학습량이 다소 감소하였습니다. 꾸준히 모습이 보입니다. "
            "무리하지 않는 선에서 학습 리듬을 다시 잡아갈 필요가 있습니다."
        )
    else:
        comment = (
            "학습량이 비교적 안정적으로 유지되고 있습니다. "
            "현재의 학습 패턴을 꾸준히 이어가길 기대합니다."
        )

    if curr["수면합"] < MIN_SLEEP_HOURS:
        comment += " 충분한 수면과 휴식이 있어야 안정적인 컨디션 관리를 할 수 있음에 유의합시다."

    return comment

# 교사용 코멘트 (여러 가지 경우의 수 만들어야 함) #######################################################################################

# 주간 리포트 요약
def make_student_weekly_summary(df_student, student_goals):
    if df_student.empty:
        return "선택 주차에 데이터가 없습니다."

    df_student["수면합"] = df_student.get("낮잠(시간)",0) + df_student.get("밤잠(시간)",0)
    df_student["공부총합"] = df_student.get("국어합(시간)",0) + df_student.get("수학합(시간)",0) + \
                              df_student.get("영어합(시간)",0) + df_student.get("탐구합(시간)",0)

    avg_dict = {var: df_student[var].mean() for var in ["수면합","공부총합"]}
    summary = []

    for var, avg in avg_dict.items():
        goal = student_goals.get(var)
        if goal is None:
            continue
        diff = avg - goal
        if var == "수면합":
            if diff < -1:
                summary.append(f"⚠️ 평균 수면시간이 목표보다 부족합니다 ({avg:.1f}시간 vs {goal}시간).")
            elif diff > 1:
                summary.append(f"⚠️ 평균 수면시간이 목표보다 많습니다 ({avg:.1f}시간 vs {goal}시간).")
            else:
                summary.append(f"💤 수면량이 목표에 잘 맞습니다 ({avg:.1f}시간).")
        elif var == "공부총합":
            if diff < -1:
                summary.append(f"⚠️ 평균 공부시간이 목표보다 부족합니다 ({avg:.1f}시간 vs {goal}시간).")
            else:
                summary.append(f"📚 공부량이 목표에 잘 맞습니다 ({avg:.1f}시간).")

    return summary

# ================== 로그인 ==================
def check_login(user_id, user_pw):
    try:
        df = pd.read_csv(ACCOUNTS_FILE, dtype=str)
    except Exception as e:
        st.warning(f"accounts.csv 읽기 실패: {e}")
        return None

    row = df[(df["id"] == user_id) & (df["password"] == user_pw)]
    if row.empty:
        return None
    return row.iloc[0]

def login_page():
    st.title("휘문고 DB-LMS 로그인")

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
    current_user_id = st.session_state["user_id"]

    df_accounts = pd.read_csv(ACCOUNTS_FILE, dtype=str)
    df_accounts["id"] = df_accounts["id"].str.strip()

    row = df_accounts[df_accounts["id"] == current_user_id]
    student_name = row.iloc[0]["name"] if not row.empty else "이름없음"
    
    # st.title("학생 페이지")
    st.title(f" 익명 : {student_name} · 학번 : {current_user_id}")
    # st.caption(f"👤 {student_name} · ID: {current_user_id}")
    
    st.markdown("""
        <style>
            /* 토글 버튼 컨테이너 */
            .toggle-container {
                display: flex;
                gap: 10px;
                margin: 10px 0 20px 0;
            }

            /* 기본 버튼 */
            .toggle-btn {
                flex: 1;
                padding: 12px 0;
                border-radius: 12px;
                background: #f0f2f6;
                border: 1px solid #d0d0d0;
                text-align: center;
                font-weight: 600;
                color: #555;
                cursor: pointer;
                transition: all 0.2s ease;
            }

            /* 마우스 오버 */
            .toggle-btn:hover {
                background: #e4e7ec;
            }

            /* 선택된 버튼 */
            .toggle-btn-selected {
                background: #4a8af4;
                color: white;
                border-color: #2a6ad8;
                box-shadow: 0 4px 10px rgba(74, 138, 244, 0.4);
            }

            /* Google Sheet 버튼 */
            .open-sheet-btn {
                display: inline-block;
                padding: 12px 20px;
                margin-top: 15px;
                border-radius: 10px;
                font-weight: 600;
                color: white !important;
                background: linear-gradient(135deg, #4a8af4, #567dfc);
                text-decoration: none;
                box-shadow: 0 4px 10px rgba(74, 138, 244, 0.35);
                transition: 0.2s ease;
            }

            .open-sheet-btn:hover {
                background: linear-gradient(135deg, #3f7aec, #4a6ef5);
                box-shadow: 0 5px 14px rgba(74, 138, 244, 0.45);
            }
        </style>
    """, unsafe_allow_html=True)

    # ===================== ADMIN =====================
    if st.session_state["role"] == "admin":
        tabs = st.tabs(["🧑‍🏫 관리자"])

        with tabs[0]:
            st.subheader("🧑‍🏫 전체 학생 · 전체 과목 주간 통계 CSV")
            st.caption("모든 학생의 Google Sheet를 불러와 과목별 · 주차별 평균을 생성합니다.")
            
            st.markdown("### 🗓 주차 범위 선택")
            week_keys = list(PRESET_PERIODS.keys())
            col1, col2 = st.columns(2)

            with col1:
                admin_start_week = st.selectbox(
                    "시작 주차",
                    week_keys,
                    index=0,
                    key="admin_start_week"
                )

            with col2:
                admin_end_week = st.selectbox(
                    "끝 주차",
                    week_keys,
                    index=len(week_keys)-1,
                    key="admin_end_week"
                )

            start_idx = week_keys.index(admin_start_week)
            end_idx = week_keys.index(admin_end_week)

            if start_idx > end_idx:
                st.error("시작 주차는 끝 주차보다 클 수 없습니다.")

            start_date = pd.to_datetime(PRESET_PERIODS[admin_start_week][0])
            end_date = pd.to_datetime(PRESET_PERIODS[admin_end_week][1]) 


            df_accounts = pd.read_csv(ACCOUNTS_FILE, dtype=str)
            df_sheets = pd.read_csv(SHEETS_FILE, dtype=str)
            df_accounts["id"] = df_accounts["id"].str.strip()
            df_sheets["id"] = df_sheets["id"].str.strip()


            students_df = df_accounts[df_accounts["role"] == "student"]
            st.write("학생 수:", len(students_df))
            st.write("시트 연결된 학생 수:", len(df_sheets))
            st.write("📋 시트 연결 ID 목록:", df_sheets["id"].tolist())

            if students_df.empty:
                st.warning("학생 계정이 없습니다.")

            if st.button("📥 전체 과목 주간 통계 CSV 생성"):
                all_results = []

                with st.spinner("학생 데이터 처리 중..."):
                    # 주차 테이블
                    week_rows = []
                    for i in range(start_idx, end_idx + 1):
                        w = week_keys[i]
                        s, e = PRESET_PERIODS[w]
                        week_rows.append({
                            "주차번호": int(w.split("주차")[0]),
                            "주차": w,
                            "start": pd.to_datetime(s),
                            "end": pd.to_datetime(e)
                        })
                    df_weeks = pd.DataFrame(week_rows)

                    for w, (s, e) in PRESET_PERIODS.items():
                        week_rows.append({
                            "주차번호": int(w.split("주차")[0]),
                            "주차": w,
                            "start": pd.to_datetime(s),
                            "end": pd.to_datetime(e)
                        })
                    df_weeks = pd.DataFrame(week_rows)
                    
                    # 학생별 처리
                    for _, acc in students_df.iterrows():
                        user_id = acc["id"]
                        student_name = acc["name"]
                        real_name = acc["real"]
                        
                        row_sheet = df_sheets[df_sheets["id"] == user_id]
                        if row_sheet.empty:
                            continue

                        sheet_url = row_sheet.iloc[0]["sheet_url"]
                        if "/d/" not in sheet_url:
                            continue

                        sheet_id = sheet_url.split("/d/")[1].split("/")[0]
                        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"

                        try:
                            df = pd.read_csv(csv_url, engine="python", on_bad_lines="skip")
                            # 컬럼 정규화
                            df.columns = (
                                df.columns
                                .str.strip()
                                .str.replace('\r','',regex=False)
                                .str.replace('\n','',regex=False)
                                .str.replace(' ','',regex=False)
                                .str.replace('　','',regex=False)
                            )                       
                        except:
                            continue

                        if "일시" not in df.columns:
                            continue

                        # 목표 추출
                        goals = {}
                        for var in ALL_VARS:
                            goals[var] = float(df.get(var, [0])[0])
                        goals["수면합"]=float(df.get("수면(시간)", [0])[0])  
                        goals["공부총합"]=float(df.get("전체합(시간)", [0])[0])
                        
                        df["일시"] = pd.to_datetime(df["일시"], errors="coerce")
                        df = df.dropna(subset=["일시"])
                        df = df[(df["일시"] >= start_date) & (df["일시"] <= end_date)]

                        for v in ALL_VARS:
                            if v not in df.columns:
                                df[v] = np.nan
                            else:
                                df[v] = pd.to_numeric(df[v], errors="coerce")

                        means = df[ALL_VARS].mean()
               
                        row_data = {"학생ID": user_id, "익명": student_name, "실명":real_name}

                        for v in ALL_VARS:
                            row_data[v] = round(means.get(v, np.nan), 2)

                        total_sum = 0
                        for v in SUM_VARS:
                            val = row_data.get(v)
                            if not pd.isna(val):
                                total_sum += val

                        sleep_sum = 0
                        for i in ["낮잠(시간)", "밤잠(시간)"]:
                            vv = row_data.get(i)
                            if not pd.isna(vv):
                                sleep_sum += vv

                        row_data["수면합"] = round(sleep_sum, 2)
                        row_data["공부총합"] = round(total_sum, 2)
                        all_results.append(row_data)

                # -------------------------------
                # 결과 처리
                # -------------------------------
                if not all_results:
                    st.warning("생성된 데이터가 없습니다.")
        
                result_df = pd.DataFrame(all_results)
                final_cols = ["학생ID", "익명", "실명", "낮잠(시간)", "밤잠(시간)", "수면합", 
                              "문학(시간)", "비문학(시간)", "화언(시간)", "국어기타(시간)", "국어합(시간)",
                              "대수(시간)", "미적(시간)", "확통(시간)", "수학기타(시간)", "수학합(시간)",
                              "어휘문법(시간)", "듣기(시간)", "독해(시간)", "영어기타(시간)", "영어합(시간)",
                              "통사(시간)", "통과(시간)", "탐구기타(시간)", "내신기타(시간)", "탐구합(시간)", "공부총합"]
                result_df = result_df[final_cols]

                result_df["순위"] = result_df["공부총합"].rank(method='min', ascending=False)
 
                # 학생
                summary_rows = []

                for student_id, df_s in result_df.groupby("학생ID"):
                    summary_rows.append({
                        "학생ID": student_id,
                        "요약": make_student_weekly_summary(df, goals)
                    })

                summary_df = pd.DataFrame(summary_rows)

                result_df = result_df.merge(summary_df, on="학생ID", how="left")
         
                st.success("CSV 생성 완료!")
                st.markdown("### 👀 CSV 미리보기 (상위 100행)")
                st.dataframe(
                    result_df.head(100),
                    use_container_width=True
                )
                xlsx_bytes = dataframe_to_xlsx_bytes(
                    result_df,
                    sheet_name="전체학생_주간통계"
                )

                st.download_button(
                    label="⬇️ 전체 학생 주간 통계 XLSX 다운로드",
                    data=xlsx_bytes,
                    file_name="전체학생_전체과목_주간통계.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="admin_weekly_xlsx_download"
                )
        
                st.markdown("### 📝 학생별 자동 요약")

                for student_id, df_s in result_df.groupby("학생ID"):
                    summary = make_student_weekly_summary(df, goals)
                    st.info(f"👤 {student_id} : {summary}")

        
        if st.button("🔙 로그아웃"):
            st.session_state.clear()
            st.rerun()
        return   # ← 이 줄이 핵심
    else:
        tab1, tab2, tab3, tab4 = st.tabs(
            ["📅 직접 기간 선택", "📊 주간별 리포트", "📈 주간 평균 변화", "🏆 주간 공부 시간 순위"]
        )

    # ---------------- TAB 1 ----------------
    with tab1:
        st.subheader("직접 기간 선택")
        st.write("직접 시작일과 종료일을 선택해서 차트를 볼 수 있습니다.")
        st.markdown("<div class='section-title'>📱 화면 환경 선택</div>", unsafe_allow_html=True)

        # 저장된 선택값 유지
        if "device" not in st.session_state:
            st.session_state["device"] = "PC"

        # ------------------ 토글 버튼 랜더링 ------------------
        st.markdown("<div class='toggle-container'>", unsafe_allow_html=True)

        pc_selected = "toggle-btn-selected" if st.session_state["device"] == "PC" else ""
        mobile_selected = "toggle-btn-selected" if st.session_state["device"] == "모바일" else ""

        col1, col2 = st.columns(2)
    
        with col1:
            if st.button("💻 PC(컴퓨터, 노트북)", key="pc_btn"):
                st.session_state["device"] = "PC"

        with col2:
            if st.button("📱 모바일(핸드폰, 태블릿)", key="mobile_btn"):
                st.session_state["device"] = "모바일"

        st.markdown("</div>", unsafe_allow_html=True)

        # ------------------ 화면 전환 ------------------
        device = st.session_state["device"]
        st.markdown('미리보기는 PC버전입니다. 모바일로 입력하려면 모바일 버튼을 눌러주세요.')

        # Google Sheet url 가져오기
        sheet_url = None
        try:
            df_sheets = pd.read_csv(SHEETS_FILE, dtype=str)
            row = df_sheets[df_sheets["id"] == st.session_state["user_id"]]
            if row.empty:
                st.warning("시트가 연결되지 않았습니다.")
                st.stop()
            sheet_url = row.iloc[0]["sheet_url"]
        except:
            st.warning("시트 정보를 불러올 수 없습니다.")
            st.stop()

        if device == "PC":
            try:
                pc_url = sheet_url + "&widget=true&headers=true"
                st.components.v1.html(
                    f"<iframe src='{pc_url}' style='width:100%; height:600px; border:none; border-radius:12px;'></iframe>",
                    height=600
                )
            except Exception as e:
                st.warning(f"iframe 렌더링 실패: {e}")

        else:
            st.markdown(
                f"<a class='open-sheet-btn' href='{sheet_url}' target='_blank'>📄 Google Sheet 새 탭에서 열기</a>",
                unsafe_allow_html=True
            )
            
        sheet_id = sheet_url.split("/d/")[1].split("/")[0]
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"

        try:
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
            df_csv["일시"] = pd.to_datetime(df_csv["일시"], errors="coerce")
            df_csv = df_csv.dropna(subset=["일시"])
            st.session_state["df_csv"] = df_csv
            goals = {}
            for var in ALL_VARS:
                goals[var] = float(df_csv.get(var, [0])[0])
                goals["수면합"]=float(df_csv.get("수면(시간)", [0])[0])  
                goals["공부총합"]=float(df_csv.get("전체합(시간)", [0])[0])
        except:
            st.warning("CSV 로드 실패")

        # 날짜 범위 선택
        st.markdown("---")
        st.subheader("📊 시각화를 위한 기간 선택")
        try:
            df_csv["일시"] = pd.to_datetime(df_csv["일시"], errors='coerce')
            df_csv = df_csv.dropna(subset=["일시"])
        except:
            st.error("❌ '일시' 컬럼 날짜 변환 실패.")

        min_date = df_csv["일시"].min().date()
        max_date = df_csv["일시"].max().date()

        # 기본값: 오늘 기준 1주일 전 ~ 오늘
        today = datetime.date.today()
        default_start = max(today - datetime.timedelta(days=7), min_date)
        default_end = min(today, max_date)

        # 범위가 유효하지 않으면 데이터의 첫 날짜부터 8일
        if default_start > max_date or default_end < min_date:
            default_start = min_date
            default_end = min(min_date + datetime.timedelta(days=7), max_date)

        start_date = st.date_input(
            "📅 시작 날짜",
            value=default_start,
            min_value=min_date,
            max_value=max_date,
            key='start_date_picker'
            )
        end_date = st.date_input(
            "📅 종료 날짜",
            value=default_end,
            min_value=min_date,
            max_value=max_date,
            key='end_date_picker'
            )

        min_date = df_csv["일시"].min()
        max_date = df_csv["일시"].max()
        
        if start_date > end_date:
            st.warning("⚠ 종료 날짜가 시작 날짜보다 빠를 수 없습니다.")

        df_range = df_csv[
            (df_csv["일시"] >= pd.to_datetime(start_date)) &
            (df_csv["일시"] <= pd.to_datetime(end_date))
        ]

        st.markdown("---")
        st.subheader("선택 날짜 범위 데이터")
        # 원하는 컬럼만 선택
        display_cols = [
        "일시", "낮잠(시간)", "밤잠(시간)", "수면(시간)", "문학(시간)", "비문학(시간)", "화언(시간)", "국어기타(시간)", "국어합(시간)",
        "대수(시간)", "미적(시간)", "확통(시간)", "수학기타(시간)", "수학합(시간)",
        "어휘문법(시간)", "듣기(시간)", "독해(시간)", "영어기타(시간)", "영어합(시간)",
        "통사(시간)", "통과(시간)", "탐구기타(시간)", "내신기타(시간)", "탐구합(시간)", "전체합(시간)"]
        
        df_display = df_range.copy()

        # 일시 컬럼을 yyyy-mm-dd 형식으로 변환
        df_display["일시"] = df_display["일시"].dt.strftime("%Y-%m-%d")

        # 선택한 컬럼만 남기기
        df_display = df_display[[col for col in display_cols if col in df_display.columns]]
        df_display = df_display.round(2)
        st.dataframe(df_display)
    
        # ------------------ 그룹 + 변수 선택 ------------------
        st.markdown("---")
        st.subheader("그룹 선택 및 변수 선택")
        selected_group = st.selectbox("그룹 선택", list(GROUPS.keys()))
        variables = GROUPS[selected_group]
        selected_vars = st.multiselect("변수 선택", variables, default=variables)
    
        if not selected_vars:
            st.info("하나 이상의 변수를 선택해주세요.")

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
            template="plotly_white",
            legend_traceorder='normal',
            colorway=px.colors.qualitative.Pastel
        )
        fig.update_traces(textfont_size=14)

        st.plotly_chart(fig, use_container_width=True)

        # ------------------ 목표 대비 실천 그래프 ------------------
        st.markdown("---")
        st.subheader("🎯 목표 대비 실천 비교")

        # --- 안전한 수치 변환 (문자열/빈값 대비) ---
        goal_raw = df_csv[selected_vars].iloc[0]  # 원래 코드
        goal_num = goal_raw.apply(pd.to_numeric, errors='coerce')  # NaN 허용
        avg_num = df_range[selected_vars].apply(pd.to_numeric, errors='coerce').mean()
    
        # --- 리스트 생성: 텍스트, hover_text, color 등 ---
        avg_texts = []
        avg_hover = []
        goal_texts = []
        goal_hover = []
        colors_dynamic = []

        for var in selected_vars:
            g = goal_num.get(var, np.nan)
            a = avg_num.get(var, np.nan)

            # 평균 텍스트 (항상 표시)
            if pd.isna(a):
                avg_text = ""
                avg_hover_text = f"({var}) 실천: -"
            else:
                avg_text = f"{a:.2f}"
                avg_hover_text = f"({var}) 실천: {a:.2f}시간"

            # 목표 텍스트
            if pd.isna(g):
                goal_text = ""
                goal_hover_text = f"({var}) 목표: -"
            else:
                goal_text = f"{g:.2f}"
                goal_hover_text = f"({var}) 목표: {g:.2f}시간"

            # 목표가 0 또는 NaN이면 퍼센트 표시 안함, 색은 중립(회색)
            if pd.isna(g) or g == 0:
                pct_part = ""  # 퍼센트 표시 없음
                colors_dynamic.append("#9e9e9e")  # gray for undefined target
                # hover에 퍼센트 없음
                avg_hover_text += ""
            else:
                # 퍼센트 계산 (평균이 NaN이면 NaN 처리)
                pct = ((a) / g * 100) if (not pd.isna(a)) else np.nan
                if pd.isna(pct):
                    pct_part = ""
                else:
                    pct_part = f" ({pct:+.1f}%)"  # + / - 포함해서 표시
                # 색: 달성(녹색) vs 미달(빨강)
                if not pd.isna(a) and a >= g:
                    colors_dynamic.append("#2ecc71")  # green
                else:
                    colors_dynamic.append("#e74c3c")  # red
    
                avg_hover_text += f"<br>목표 대비: {pct:+.1f}%"

            # 평균 막대 위 텍스트 (h 단위 표기를 기존 스타일에 맞춰 유지)
            avg_texts.append(f"{avg_text}시간{pct_part}" if avg_text != "" else "")
            avg_hover.append(avg_hover_text)

            # 목표 막대 텍스트 / hover
            goal_texts.append(f"{goal_text}시간" if goal_text != "" else "")
            goal_hover.append(goal_hover_text)
    
        # --- Plotly 차트 구성 ---
        fig2 = go.Figure()
    
        # 평균값 Bar (개별 색/텍스트/hover 적용)
        fig2.add_trace(go.Bar(
            x=selected_vars,
            y=[float(x) if not pd.isna(x) else 0 for x in avg_num.values],   
            name="실천",
            marker_color=colors_dynamic,
            text=avg_texts,
            texttemplate='%{text}',
            textposition='outside',
            hovertext=avg_hover,
            hovertemplate='%{hovertext}<extra></extra>'
        ))

        # 목표값 Bar
        fig2.add_trace(go.Bar(
            x=selected_vars,
            y=[float(x) if not pd.isna(x) else 0 for x in goal_num.values],
            name="목표",
            marker_color='orange',
            text=goal_texts,
            texttemplate='%{text}',
            textposition='outside',
            hovertext=goal_hover,
            hovertemplate='%{hovertext}<extra></extra>'
        ))

        # 레이아웃 유지 + 약간의 margin 조정
        fig2.update_layout(
            yaxis_title="시간(시간)",
            xaxis_title="항목",
            xaxis=dict(tickangle=-45),
            height=600,
            barmode='group',
            template="plotly_white",
            colorway=px.colors.qualitative.Pastel,
            margin=dict(l=30, r=30, t=50, b=150)
        )

        fig2.update_traces(textfont_size=14)

        st.plotly_chart(fig2, use_container_width=True)

    # ---------------- TAB 2 ----------------
    with tab2:
        st.subheader("주간별 리포트")
        if "df_csv" not in st.session_state:
            st.warning("📅 먼저 [직접 기간 선택] 탭에서 데이터를 불러주세요.")
            st.stop()
        df_csv = st.session_state["df_csv"]

        # --- State 초기화 ---
        if "weekly_report_mode" not in st.session_state:
            st.session_state["weekly_report_mode"] = False
        if "weekly_period" not in st.session_state:
            st.session_state["weekly_period"] = None

        # --- 기본 화면: 기간 선택 + 버튼 ---
        period_name = st.selectbox(
            "보고 싶은 기간을 선택하세요", 
            list(PRESET_PERIODS.keys()),
            key="weekly_period_select"
        )

        if st.button("리포트 보기", key="weekly_report_show"):
            st.session_state["weekly_report_mode"] = True
            st.session_state["weekly_period"] = period_name
            st.rerun()

        # --- 여기부터 리포트 모드 ---
        if st.session_state["weekly_report_mode"]:

            period_name = st.session_state["weekly_period"]
            start_str, end_str = PRESET_PERIODS[period_name]

            st.info(f"📌 선택한 기간: **{start_str} ~ {end_str}**")

            # 데이터 필터링
            df_range = df_csv[(df_csv["일시"] >= start_str) & (df_csv["일시"] <= end_str)]

            display_cols = [
                "일시", "낮잠(시간)", "밤잠(시간)", "수면(시간)", "문학(시간)", "비문학(시간)",
                "화언(시간)", "국어기타(시간)", "국어합(시간)",
                "대수(시간)", "미적(시간)", "확통(시간)", "수학기타(시간)", "수학합(시간)",
                "어휘문법(시간)", "듣기(시간)", "독해(시간)", "영어기타(시간)", "영어합(시간)",
                "통사(시간)", "통과(시간)", "탐구기타(시간)", "내신기타(시간)", "탐구합(시간)", "전체합(시간)"
            ]

            # 표 출력
            df_display = df_range.copy()
            df_display["일시"] = df_display["일시"].dt.strftime("%Y-%m-%d")
            df_display = df_display[[c for c in display_cols if c in df_display.columns]]
            df_display = df_display.round(2)

            st.dataframe(df_display, use_container_width=True)

            st.markdown("---")
            st.subheader("그룹 선택 및 변수 선택")

            selected_group = st.selectbox("그룹 선택(주간 리포트)", list(GROUPS.keys()), key="weekly_group")
            variables = GROUPS[selected_group]

            selected_vars = st.multiselect(
                "변수 선택(주간 리포트)", 
                variables, 
                default=variables,
                key="weekly_vars"
            )

            if not selected_vars:
                st.info("하나 이상의 변수를 선택해주세요.")

            if df_range.empty:
                st.warning("선택한 기간에 데이터가 없습니다.")
         
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
                    template="plotly_white",
                    legend_traceorder='normal',
                    colorway=px.colors.qualitative.Pastel
                )
                fig.update_traces(textfont_size=14)
            st.plotly_chart(fig, use_container_width=True, key="fig_week_chart")
            # ------------------ 목표 대비 실천 그래프 ------------------
            st.markdown("---")
            st.subheader("🎯 목표 대비 실천 비교")
    
            # --- 안전한 수치 변환 (문자열/빈값 대비) ---
            goal_raw = df_csv[selected_vars].iloc[0]  # 원래 코드
            goal_num = goal_raw.apply(pd.to_numeric, errors='coerce')  # NaN 허용
            avg_num = df_range[selected_vars].apply(pd.to_numeric, errors='coerce').mean()

            # --- 리스트 생성: 텍스트, hover_text, color 등 ---
            avg_texts = []
            avg_hover = []
            goal_texts = []
            goal_hover = []
            colors_dynamic = []
            for var in selected_vars:
                g = goal_num.get(var, np.nan)
                a = avg_num.get(var, np.nan)
                # 평균 텍스트 (항상 표시)
                if pd.isna(a):
                    avg_text = ""
                    avg_hover_text = f"({var}) 실천: -"
                else:
                    avg_text = f"{a:.2f}"
                    avg_hover_text = f"({var}) 실천: {a:.2f}시간"
                # 목표 텍스트
                if pd.isna(g):
                    goal_text = ""
                    goal_hover_text = f"({var}) 목표: -"
                else:
                    goal_text = f"{g:.2f}"
                    goal_hover_text = f"({var}) 목표: {g:.2f}시간"

                 # 목표가 0 또는 NaN이면 퍼센트 표시 안함, 색은 중립(회색)
                if pd.isna(g) or g == 0:
                    pct_part = ""  # 퍼센트 표시 없음
                    colors_dynamic.append("#9e9e9e")  # gray for undefined target
                    # hover에 퍼센트 없음
                    avg_hover_text += ""
                else:
                    # 퍼센트 계산 (평균이 NaN이면 NaN 처리)
                    pct = ((a) / g * 100) if (not pd.isna(a)) else np.nan
                    if pd.isna(pct):
                        pct_part = ""
                    else:
                        pct_part = f" ({pct:+.1f}%)"  # + / - 포함해서 표시
                    # 색: 달성(녹색) vs 미달(빨강)
                    if not pd.isna(a) and a >= g:
                        colors_dynamic.append("#2ecc71")  # green
                    else:
                        colors_dynamic.append("#e74c3c")  # red
        
                    avg_hover_text += f"<br>목표 대비: {pct:+.1f}%"
    
                # 평균 막대 위 텍스트 (h 단위 표기를 기존 스타일에 맞춰 유지)
                avg_texts.append(f"{avg_text}시간{pct_part}" if avg_text != "" else "")
                avg_hover.append(avg_hover_text)
                # 목표 막대 텍스트 / hover
                goal_texts.append(f"{goal_text}시간" if goal_text != "" else "")
                goal_hover.append(goal_hover_text)

            # --- Plotly 차트 구성 ---
            fig2 = go.Figure()
    
            # 평균값 Bar (개별 색/텍스트/hover 적용)
            fig2.add_trace(go.Bar(
                x=selected_vars,
                y=[float(x) if not pd.isna(x) else 0 for x in avg_num.values],   
                name="실천",
                marker_color=colors_dynamic,
                text=avg_texts,
                texttemplate='%{text}',
                textposition='outside',
                hovertext=avg_hover,
                hovertemplate='%{hovertext}<extra></extra>'
            ))
    
            # 목표값 Bar
            fig2.add_trace(go.Bar(
                x=selected_vars,
                y=[float(x) if not pd.isna(x) else 0 for x in goal_num.values],
                name="목표",
                marker_color='orange',
                text=goal_texts,
                texttemplate='%{text}',
                textposition='outside',
                hovertext=goal_hover,
                hovertemplate='%{hovertext}<extra></extra>'
            ))
    
            # 레이아웃 유지 + 약간의 margin 조정
            fig2.update_layout(
                yaxis_title="시간(시간)",
                xaxis_title="항목",
                xaxis=dict(tickangle=-45),
                height=600,
                barmode='group',
                template="plotly_white",
                colorway=px.colors.qualitative.Pastel,
                margin=dict(l=30, r=30, t=50, b=150)
            )        

            fig2.update_traces(textfont_size=14)
  
            st.plotly_chart(fig2, use_container_width=True, key="fig_w_target_chart")

        st.markdown("### 📝 이번 주 학습 요약")

        summary = make_student_weekly_summary(df_display, goals)
        st.success(summary[0])
        st.success(summary[1])

    # ---------------- TAB 3 ----------------
    with tab3:
        st.subheader("주간별 평균 변화")
        if "df_csv" not in st.session_state:
            st.warning("📅 먼저 [직접 기간 선택] 탭에서 데이터를 불러주세요.")
            st.stop()
        
        df = st.session_state["df_csv"].copy()
        df["일시"] = pd.to_datetime(df["일시"], errors="coerce")
        df = df.dropna(subset=["일시"])

        # 기간 선택
        st.markdown("### 🗓 주차 범위 선택")
        week_keys = list(PRESET_PERIODS.keys())
        col1, col2 = st.columns(2)

        with col1:
            start_week = st.selectbox(
                "시작 주차",
                week_keys,
                index=0,
                key="tab3_start_week"
            )

        with col2:
            end_week = st.selectbox(
                "끝 주차",
                week_keys,
                index=10,
                key="tab3_end_week"
            )
        # ------------------ 선택 검증 ------------------
        start_idx = week_keys.index(start_week)
        end_idx = week_keys.index(end_week)
    
        if start_idx > end_idx:
            st.error("시작 주차는 끝 주차보다 클 수 없습니다.")
        
        # ------------------ 날짜 범위 계산 ------------------
        start_date = pd.to_datetime(PRESET_PERIODS[start_week][0]).normalize()
        end_date = (
            pd.to_datetime(PRESET_PERIODS[end_week][1])
            .normalize()
            + pd.Timedelta(days=1)
            - pd.Timedelta(seconds=1)
        )

        st.info(
            # f"📌 선택 기간: **{start_week} ~ {end_week}**  \n"
            f"📌 선택 기간: ({start_date.date()} ~ {end_date.date()})"
        )

        # ------------------ 데이터 필터 ------------------
        df_period = df[
            (df["일시"] >= start_date) &
            (df["일시"] <= end_date)
        ]

        if df_period.empty:
            st.warning("선택한 기간에 데이터가 없습니다.")
       
        # 그룹 & 변수 선택
        selected_group = st.selectbox(
            "그룹 선택 (주간 누적)",
            list(GROUPS.keys()),
            key="tab3_group"
        )
        
        selected_vars = st.multiselect(
            "변수 선택 (주간 누적)",
            GROUPS[selected_group],
            default=GROUPS[selected_group],
            key="tab3_vars"
        )

        if not selected_vars:
            st.info("하나 이상의 변수를 선택해주세요.")
        
        # ------------------ 주차 기준 테이블 생성 ------------------
        week_rows = []

        for week_name, (start, end) in PRESET_PERIODS.items():
            week_num = int(week_name.split("주차")[0])
            week_rows.append({
                "주차번호": week_num,
                "주차": week_name,
                "start": pd.to_datetime(start),
                "end": pd.to_datetime(end)
            })

        df_weeks = pd.DataFrame(week_rows)

        # ------------------ 날짜 → 주차 매핑 ------------------
        df_period = df_period.copy()
        df_period["주차번호"] = np.nan
        df_period["주차"] = ""
        df_period["주차번호"] = df_period["주차번호"].astype("float")

        for _, row in df_weeks.iterrows():
            mask = (
                (df_period["일시"] >= row["start"]) &
                (df_period["일시"] <= row["end"])
            )
            df_period.loc[mask, "주차번호"] = row["주차번호"]
            df_period.loc[mask, "주차"] = row["주차"]

        start_week_num = int(start_week.split("주차")[0])
        end_week_num = int(end_week.split("주차")[0])
      
        df_period = df_period[
            (df_period["주차번호"] >= start_week_num) &
            (df_period["주차번호"] <= end_week_num)
        ]

        # 주차별 평균
        weekly_avg = (
            df_period
            .groupby(["주차번호", "주차"])[selected_vars]
            .mean()
            .reset_index()
            .sort_values("주차번호")
        )

        # 누적 막대 그래프
        fig = go.Figure()

        for var in selected_vars:
            fig.add_trace(go.Bar(
                y=weekly_avg["주차"],
                x=pd.to_numeric(weekly_avg[var], errors="coerce").fillna(0),
                orientation="h",
                name=var,
                text=pd.to_numeric(weekly_avg[var], errors="coerce").fillna(0).round(2),
                texttemplate="%{text}",
                textposition="inside",
                hovertemplate=(
                    f"{var}<br>"
                    "주차: %{y}<br>"
                    "합계: %{x:.2f}시간"
                    "<extra></extra>"
                )
            ))

        fig.update_layout(
            barmode="stack",
            xaxis_title="주간 평균 시간(시간)",
            yaxis_title="주차",
            yaxis=dict(autorange="reversed"),
            height=600,
            template="plotly_white",
            legend_title="변수",
            margin=dict(l=40, r=40, t=60, b=80)
        )

        fig.update_traces(textfont_size=13)

        st.plotly_chart(fig, use_container_width=True)

    # ---------------- TAB 4 ----------------
    with tab4:
        st.subheader("🏆 주간 공부 시간 순위")

    # ===============================
    # 주차 선택
    # ===============================
        week_options = {
                "1주차 (3/1~3/7)": "rank20260301_20260307.xlsx",
                "2주차 (3/8~3/14)": "rank20260308_20260314.xlsx",
                "3주차 (3/15~3/21)": "rank20260315_20260321.xlsx"
        }

        selected_week = st.selectbox(
            "주간 선택",
            list(week_options.keys())
        )

        file_name = week_options[selected_week]
        file_url = f"{BASE_GITHUB_URL}/{file_name}"

        try:
        # ===============================
        # 파일 로드
        # ===============================
            df = pd.read_excel(file_url)
            
            if df.empty:
                raise ValueError
        # ===============================
        # (3) 전 주 대비 변화
        # ===============================
            week_keys = list(week_options.keys())
            cur_idx = week_keys.index(selected_week)

            if cur_idx > 0:
                prev_file = week_options[week_keys[cur_idx - 1]]
                prev_url = f"{BASE_GITHUB_URL}/{prev_file}"

                try:
                    df_prev = pd.read_excel(prev_url)
                    prev_map = dict(
                        zip(df_prev["학생ID"], df_prev["공부총합"])
                    )

                    def diff_arrow(row):
                        prev = prev_map.get(row["학생ID"])
                        if prev is None:
                            return "—"
                        if row["공부총합"] > prev:
                            return "▲"
                        if row["공부총합"] < prev:
                            return "▼"
                        return "—"

                    df["변화"] = df.apply(diff_arrow, axis=1)

                except:
                    df["변화"] = "—"
            else:
                df["변화"] = "—"

        # ===============================
        # 표시용 테이블
        # ===============================
            show_df = df[["학생ID","순위", "익명", "공부총합", "변화"]].copy()
            show_df = show_df.sort_values(["순위", "익명"], ascending=[True, True])
            show_df["학생ID"]=show_df["학생ID"].astype(str).str.strip()
            my_id = str(st.session_state.get("user_id").strip())
            my_row = show_df.loc[show_df["학생ID"] == my_id]
            # ===============================
            # (1) 내 행 여부 컬럼
            # ===============================
            show_df["_me"] = show_df["학생ID"] == my_id
            # ===============================
            # (2) 보여줄 컬럼만
            # ===============================
            display_df = show_df[["순위", "익명", "공부총합", "변화", "_me"]]
            # ===============================
            # (3) 출력 (강조는 emoji로)
            # ===============================
            display_df["익명"] = display_df.apply(
                lambda r: "👉 " + r["익명"] if r["_me"] else r["익명"],
                axis=1
            )
            display_df["공부총합"] = display_df["공부총합"].round(2)
            st.dataframe(
                display_df.drop(columns=["_me"]),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "순위": st.column_config.NumberColumn(
                    "순위",
                    help="주간 순위",
                    format="%d",
                    align="center"
                ),
                    "익명": st.column_config.TextColumn(
                    "익명",
                    align="center"
                ),
                    "공부총합": st.column_config.NumberColumn(
                    "공부총합",
                    format="%.2f",
                    align="center"
                ),
                    "변화": st.column_config.NumberColumn(
                    "변화",
                    format="%.2f",
                    align="center"
                ),
            })
            
            if not my_row.empty:
                r = int(my_row["순위"].iloc[0])
                avg = round(my_row["공부총합"].iloc[0], 2)
                arrow = my_row["변화"].iloc[0]
                total = len(df)
                
                st.success(
                    f"🙋‍♂️ 학생은 **{total}명 중 {r}위**입니다.\n\n"
                    f"📚 주간 평균 공부 시간: **{avg}시간** (변화 : {arrow})"
                )

        except Exception:
            st.info("📭 아직 주간 순위가 없습니다.")
    
    # 로그아웃
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

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import datetime
import plotly.express as px


ACCOUNTS_FILE = "accounts.csv"
SHEETS_FILE = "sheets.csv"

# ------------------------
# 그룹 정의
# ------------------------
GROUPS = {
    "수면": ["낮잠(시간)", "밤잠(시간)"],
    "종합": ["국어합(시간)", "수학합(시간)", "영어합(시간)", "탐구합(시간)"],
    "국어": ["문학(시간)", "비문학(시간)", "화언(시간)", "국어기타(시간)"],
    "수학": ["대수(시간)", "미적(시간)", "확통(시간)", "수학기타(시간)"],
    "영어": ["어휘문법(시간)", "듣기(시간)", "독해(시간)", "영어기타(시간)"],
    "탐구": ["통사(시간)", "통과(시간)", "탐구기타(시간)", "내신기타(시간)"]    
}

# 교사가 미리 설정해둔 기간들
PRESET_PERIODS = {
    "1주차 (3/1~3/7)": ("2026-03-01", "2026-03-07"),
    "2주차 (3/8~3/14)": ("2026-03-08", "2026-03-14"),
    "중간고사 대비 주간": ("2026-04-10", "2026-04-16"),
    "기말고사 대비 주간": ("2026-06-01", "2026-06-07"),
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
    login_clicked = st.button("로그인")
    if login_clicked:
        user = check_login(user_id, user_pw)
        if user is not None and not user.empty:  # ⚠ 여기서 None 체크
            st.session_state['logged_in'] = True
            st.session_state['user_id'] = user_id
            st.session_state['role'] = user.get('role', 'student')
        else:
            st.error("아이디 또는 비밀번호가 잘못되었습니다.")

# ------------------ 학생 페이지 ------------------
def student_page():
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

    st.title(f"학생 페이지 - {st.session_state['user_id']}")

    tab1, tab2 = st.tabs(["📅 직접 기간 선택", "📊 주간별 리포트"])

    # --------------------------------------------
    # 📅 TAB 1: 기존 기능 (학생이 직접 기간 선택)
    # --------------------------------------------
    with tab1:
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
            return

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
            return

        df_range = df_csv[(df_csv["일시"] >= pd.to_datetime(start_date)) &
                          (df_csv["일시"] <= pd.to_datetime(end_date))]

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
            template="plotly_white",
            legend_traceorder='normal',
            colorway=px.colors.qualitative.Pastel
        )
        fig.update_traces(textfont_size=14)

        st.plotly_chart(fig, use_container_width=True)

        # ------------------ 목표 대비 평균 그래프 ------------------
        st.markdown("---")
        st.subheader("🎯 목표 대비 평균 비교")

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
                avg_hover_text = f"({var}) 평균: -"
            else:
                avg_text = f"{a:.2f}"
                avg_hover_text = f"({var}) 평균: {a:.2f}시간"

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
            name="평균",
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

    # --------------------------------------------
    # 📊 TAB 2: 주간별 리포트 — 사전 설정된 기간
    # --------------------------------------------
    with tab2:
        st.subheader("주간별 리포트")

        period_name = st.selectbox("보고 싶은 기간을 선택하세요", list(PRESET_PERIODS.keys()))
        
        if "weekly_report_mode" not in st.session_state:
            st.session_state["weekly_report_mode"] = False
    
        if st.button("리포트 보기"):
            st.session_state["weekly_report_mode"] = True
            if st.session_state["weekly_report_mode"]:
                start_str, end_str = PRESET_PERIODS[period_name]
                start_date = pd.to_datetime(start_str)
                end_date = pd.to_datetime(end_str)

                st.info(f"📌 선택한 기간: **{start_str} ~ {end_str}**")
    
                # 해당 기간 데이터 필터
                df_range = df_csv[(df_csv['일시'] >= start_str) & (df_csv['일시'] <= end_str)]
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
                selected_group = st.selectbox("그룹 선택(주간 리포트)", list(GROUPS.keys()))
                variables = GROUPS[selected_group]
                selected_vars = st.multiselect("변수 선택(주간 리포트)", variables, default=variables)
    
                if not selected_vars:
                    st.info("하나 이상의 변수를 선택해주세요.")
                    return

                if df_range.empty:
                    st.warning("선택한 기간에 데이터가 없습니다.")
                else:
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

                    # ------------------ 목표 대비 평균 그래프 ------------------
                    st.markdown("---")
                    st.subheader("🎯 목표 대비 평균 비교")
    
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
                            avg_hover_text = f"({var}) 평균: -"
                        else:
                            avg_text = f"{a:.2f}"
                            avg_hover_text = f"({var}) 평균: {a:.2f}시간"

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
                        name="평균",
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

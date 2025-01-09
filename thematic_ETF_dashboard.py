import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import os

# 기본 설정
st.title("Thematic ETF Dashboard 📊")
st.sidebar.header("Settings")

# 날짜 선택 및 파일 경로 생성
st.sidebar.subheader("날짜 선택")
selected_date = st.sidebar.date_input("날짜를 선택하세요", pd.to_datetime("today"))

# 선택된 날짜에 따라 파일 경로 설정
file_name = f"Thematic ETF_{selected_date.strftime('%Y%m%d')}.xlsx"
file_path = os.path.join(".", file_name)  # 파일이 동일 디렉토리에 있다고 가정

st.sidebar.write(f"선택된 파일: `{file_name}`")

# 파일 존재 여부 확인
if not os.path.exists(file_path):
    st.error(f"{file_name} 파일이 존재하지 않습니다. 업로드해주세요.")
    uploaded_file = st.file_uploader("엑셀 파일을 업로드하세요", type=["xlsx"])
    if uploaded_file:
        file_path = uploaded_file
        st.success("파일이 성공적으로 업로드되었습니다!")
else:
    st.success(f"{file_name} 파일이 존재합니다. 데이터를 로드합니다!")

# 파일 읽기
if file_path:
    excel_data = pd.ExcelFile(file_path)

    # 데이터 로드
    summary_data = excel_data.parse('Summary')
    raw_data = excel_data.parse('RAW')

    # 1년 수익률 데이터 전처리
    raw_data["1년 수익률"] = raw_data["1년 수익률"] * 100
    raw_data["1년 수익률"] = raw_data["1년 수익률"].astype(str)  # 문자열로 변환
    raw_data["1년 수익률"] = raw_data["1년 수익률"].str.replace("%", "")  # '%' 제거
    raw_data["1년 수익률"] = raw_data["1년 수익률"].str.replace(",", "")  # ',' 제거
    raw_data["1년 수익률"] = pd.to_numeric(raw_data["1년 수익률"], errors="coerce")  # 숫자로 변환

    # 변환 후 NaN 값을 확인하고 처리
    st.write("1년 수익률 NaN 개수:", raw_data["1년 수익률"].isna().sum())
    raw_data["1년 수익률"].fillna(0, inplace=True)  # NaN 값을 0으로 대체

    # Summary 데이터 시각화
    st.header("Summary Data Overview")
    st.write("테마별 현황")

    # 테마별 AUM 및 시장 점유율 시각화
    st.subheader("전체 테마별 AUM 및 시장 점유율")
    summary_cleaned = summary_data.iloc[1:-2]  # 헤더 정리
    summary_cleaned.columns = summary_data.iloc[0]  # 첫 행을 컬럼으로 설정
    summary_cleaned = summary_cleaned.dropna(subset=["테마"])  # NA 제거

    # AUM 및 Market Share 시각화
    aum_chart = alt.Chart(summary_cleaned).mark_bar().encode(
        x="테마:O",
        y="AUM:Q",
        color="국가:N",
        tooltip=["테마", "국가", "AUM"]
    ).properties(title="테마별 AUM")

    st.altair_chart(aum_chart, use_container_width=True)

    # 수익률 순위 기능 추가
    st.subheader("테마형 ETF 1년 수익률 순위")
    sorted_data = raw_data[["티커", "ETF명", "1년 수익률", "AUM", "테마"]].copy()
    sorted_data = sorted_data.sort_values(by="1년 수익률", ascending=False).reset_index(drop=True)

    # 슬라이더로 순위 범위 선택
    rank_range = st.slider("1년 수익률 순위 선택 (상위)", 1, len(sorted_data), (1, 10))
    ranked_data = sorted_data.iloc[rank_range[0]-1:rank_range[1]]

    st.write(f"선택한 수익률 순위: {rank_range[0]}위 ~ {rank_range[1]}위")
    st.dataframe(ranked_data)

    # 수익률 상위 ETF 시각화
    st.subheader("1년 수익률 상위 ETF")
    rank_chart = alt.Chart(ranked_data).mark_bar().encode(
        x="1년 수익률:Q",
        y=alt.Y("ETF명:N", sort="-x"),
        color="테마:N",
        tooltip=["티커", "ETF명", "1년 수익률", "AUM"]
    ).properties(title="1년 수익률 상위 ETF")

    st.altair_chart(rank_chart, use_container_width=True)

    # AUM 및 순유입 시각화
    if "순유입" in summary_cleaned.columns:
        summary_cleaned["순유입"] = pd.to_numeric(summary_cleaned["순유입"], errors="coerce")
        inflow_chart = alt.Chart(summary_cleaned).mark_bar().encode(
            x="테마:O",
            y="순유입:Q",
            color="국가:N",
            tooltip=["테마", "국가", "순유입"]
        ).properties(title="테마별 AUM 순유입")
        st.altair_chart(inflow_chart, use_container_width=True)
    else:
        st.warning("Summary 데이터에 '순유입' 열이 없습니다.")

    # RAW 데이터 탐색
    st.header("ETF 상세 정보 탐색")
    st.write("RAW 데이터는 각 ETF의 상세 정보를 포함합니다.")

    # AUM 순유입 필터링
    if "AUM 순유입" in raw_data.columns:
        st.subheader("AUM 순유입 상위 ETF")
        sorted_inflow_data = raw_data.sort_values(by="AUM 순유입", ascending=False).reset_index(drop=True)

        # 슬라이더로 순위 범위 선택
        inflow_rank_range = st.slider("AUM 순유입 순위 선택 (상위)", 1, len(sorted_inflow_data), (1, 10))
        ranked_inflow_data = sorted_inflow_data.iloc[inflow_rank_range[0]-1:inflow_rank_range[1]]

        # 순위 결과 표시
        st.write(f"선택한 AUM 순유입 순위: {inflow_rank_range[0]}위 ~ {inflow_rank_range[1]}위")
        st.dataframe(ranked_inflow_data)

        # AUM 순유입 상위 ETF 시각화
        inflow_chart = alt.Chart(ranked_inflow_data).mark_bar().encode(
            x="AUM 순유입:Q",
            y=alt.Y("ETF명:N", sort="-x"),
            color="테마:N",
            tooltip=["티커", "ETF명", "AUM 순유입", "테마"]
        ).properties(title="AUM 순유입 상위 ETF")
        st.altair_chart(inflow_chart, use_container_width=True)
    else:
        st.warning("RAW 데이터에 'AUM 순유입' 열이 없습니다.")

    # 수익률 vs AUM 순유입 시각화
    if "1년 수익률" in raw_data.columns and "AUM 순유입" in raw_data.columns:
        raw_data["1년 수익률"] = pd.to_numeric(raw_data["1년 수익률"], errors="coerce") * 100
        st.subheader("수익률 vs AUM 순유입")
        scatter_chart = alt.Chart(raw_data).mark_circle(size=60).encode(
            x="AUM 순유입:Q",
            y="1년 수익률:Q",
            color="테마:N",
            tooltip=["티커", "ETF명", "AUM 순유입", "1년 수익률"]
        ).interactive()
        st.altair_chart(scatter_chart, use_container_width=True)
    else:
        st.warning("필요한 데이터(1년 수익률 또는 AUM 순유입)가 RAW 데이터에 없습니다.")

    # RAW 데이터 탐색
    st.header("테마형 ETF 상세 정보")
    st.write("각 ETF별 상세 정보")

    # ETF 필터링
    theme_filter = st.sidebar.multiselect("테마 선택", raw_data["테마"].unique(), default=raw_data["테마"].unique())
    filtered_data = raw_data[raw_data["테마"].isin(theme_filter)]

    st.dataframe(filtered_data)

    # 수익률 vs AUM 시각화
    st.subheader("1년 수익률 vs AUM")
    scatter_chart = alt.Chart(filtered_data).mark_circle(size=60).encode(
        x="AUM:Q",
        y="1년 수익률:Q",
        color="테마:N",
        tooltip=["티커", "ETF명", "AUM", "1년 수익률"]
    ).interactive()

    st.altair_chart(scatter_chart, use_container_width=True)

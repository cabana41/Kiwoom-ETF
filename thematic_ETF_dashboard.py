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

    # 수익률 변환: 곱하기 100 및 % 단위 추가
    raw_data["1년 수익률"] = pd.to_numeric(raw_data["1년 수익률"], errors="coerce") * 100
    raw_data["1년 수익률(%)"] = raw_data["1년 수익률"].map("{:.2f}%".format)

    # Summary 데이터 시각화
    st.header("Summary Data Overview")
    st.write("Summary 데이터는 테마별 시장 데이터를 보여줍니다.")

    # 테마별 AUM 및 시장 점유율 시각화
    st.subheader("테마별 AUM 및 시장 점유율")
    summary_cleaned = summary_data.iloc[1:]  # 헤더 정리
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

    # RAW 데이터 탐색
    st.header("ETF 상세 정보 탐색")
    st.write("RAW 데이터는 각 ETF의 상세 정보를 포함합니다.")

    # ETF 필터링
    theme_filter = st.sidebar.multiselect("테마 선택", raw_data["테마"].unique(), default=raw_data["테마"].unique())
    filtered_data = raw_data[raw_data["테마"].isin(theme_filter)]

    st.dataframe(filtered_data)

    # 수익률 순위 기능 추가
    st.subheader("ETF 수익률 순위")
    sorted_data = raw_data[["티커", "ETF명", "1년 수익률(%)", "AUM", "테마"]].copy()
    sorted_data = sorted_data.sort_values(by="1년 수익률", ascending=False).reset_index(drop=True)

    # 슬라이더로 순위 범위 선택
    rank_range = st.slider("수익률 순위 선택 (상위)", 1, len(sorted_data), (1, 10))
    ranked_data = sorted_data.iloc[rank_range[0]-1:rank_range[1]]

    st.write(f"선택한 수익률 순위: {rank_range[0]}위 ~ {rank_range[1]}위")
    st.dataframe(ranked_data)

    # 수익률 상위 ETF 시각화
    st.subheader("수익률 상위 ETF 시각화")
    rank_chart = alt.Chart(ranked_data).mark_bar().encode(
        x="1년 수익률:Q",
        y=alt.Y("ETF명:N", sort="-x"),
        color="테마:N",
        tooltip=["티커", "ETF명", "1년 수익률(%)", "AUM"]
    ).properties(title="수익률 상위 ETF")

    st.altair_chart(rank_chart, use_container_width=True)

    # 수익률 vs AUM 시각화
    st.subheader("수익률 vs AUM")
    scatter_chart = alt.Chart(filtered_data).mark_circle(size=60).encode(
        x="AUM:Q",
        y="1년 수익률:Q",
        color="테마:N",
        tooltip=["티커", "ETF명", "AUM", "1년 수익률(%)"]
    ).interactive()

    st.altair_chart(scatter_chart, use_container_width=True)
).interactive()

st.altair_chart(scatter_chart, use_container_width=True)

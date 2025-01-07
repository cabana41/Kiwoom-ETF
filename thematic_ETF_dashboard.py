import streamlit as st
import pandas as pd
import altair as alt

# 파일 읽기
file_path = "Thematic ETF_20250106.xlsx"  # 로컬 파일 경로
excel_data = pd.ExcelFile(file_path)

# 데이터 로드
summary_data = excel_data.parse('Summary')
raw_data = excel_data.parse('RAW')

# Streamlit 앱 시작
st.title("Thematic ETF Dashboard 📊")
st.sidebar.header("Settings")

# Summary 데이터 시각화
st.header("Summary Data Overview")
st.write("Summary 데이터는 테마별 시장 데이터를 보여줍니다.")

# 테마별 AUM 및 시장 점유율 시각화
st.subheader("테마별 AUM 및 시장 점유율")
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

# RAW 데이터 탐색
st.header("ETF 상세 정보 탐색")
st.write("RAW 데이터는 각 ETF의 상세 정보를 포함합니다.")

# ETF 필터링
theme_filter = st.sidebar.multiselect("테마 선택", raw_data["테마"].unique(), default=raw_data["테마"].unique())
filtered_data = raw_data[raw_data["테마"].isin(theme_filter)]

st.dataframe(filtered_data)

# 수익률 vs AUM 시각화
st.subheader("수익률 vs AUM")
scatter_chart = alt.Chart(filtered_data).mark_circle(size=60).encode(
    x="AUM:Q",
    y="1년 수익률:Q",
    color="테마:N",
    tooltip=["티커", "ETF명", "AUM", "1년 수익률"]
).interactive()

st.altair_chart(scatter_chart, use_container_width=True)

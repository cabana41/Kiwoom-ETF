import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import os

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
# 수익률 데이터 정리 및 정렬
sorted_data = raw_data[["티커", "ETF명", "1년 수익률", "AUM", "테마"]].copy()
sorted_data["1년 수익률"] = pd.to_numeric(sorted_data["1년 수익률"], errors="coerce")
sorted_data = sorted_data.sort_values(by="1년 수익률", ascending=False).reset_index(drop=True)

# 슬라이더로 순위 범위 선택
rank_range = st.slider("수익률 순위 선택 (상위)", 1, len(sorted_data), (1, 10))
ranked_data = sorted_data.iloc[rank_range[0]-1:rank_range[1]]

# 순위 결과 표시
st.write(f"선택한 수익률 순위: {rank_range[0]}위 ~ {rank_range[1]}위")
st.dataframe(ranked_data)

# 수익률 상위 ETF 시각화
st.subheader("수익률 상위 ETF 시각화")
rank_chart = alt.Chart(ranked_data).mark_bar().encode(
    x="1년 수익률:Q",
    y=alt.Y("ETF명:N", sort="-x"),
    color="테마:N",
    tooltip=["티커", "ETF명", "1년 수익률", "AUM"]
).properties(title="수익률 상위 ETF")

st.altair_chart(rank_chart, use_container_width=True)

# 수익률 vs AUM 시각화
st.subheader("수익률 vs AUM")
scatter_chart = alt.Chart(filtered_data).mark_circle(size=60).encode(
    x="AUM:Q",
    y="1년 수익률:Q",
    color="테마:N",
    tooltip=["티커", "ETF명", "AUM", "1년 수익률"]
).interactive()

st.altair_chart(scatter_chart, use_container_width=True)

import streamlit as st
import pandas as pd
import plotly.express as px


# --------------------------------------------------
# 기본 설정
# --------------------------------------------------
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")
st.write(
    "1년간 박스오피스 10위권에 든 영화 중 "
    "이 기간에 개봉한 영화들의 분포와 관계를 살펴봅니다."
)


# --------------------------------------------------
# 데이터 불러오기
# --------------------------------------------------
DATA_URL = (
    "https://raw.githubusercontent.com/greatsong/modudata/"
    "main/data/kobis_movies.csv"
)

try:
    df = pd.read_csv(DATA_URL)

except Exception as e:
    st.error("데이터를 불러오지 못했습니다.")
    st.write(f"오류 내용: {e}")
    st.stop()


# --------------------------------------------------
# 데이터 전처리
# --------------------------------------------------

# 개봉일
df["openDt"] = pd.to_datetime(
    df["openDt"].astype(str),
    format="%Y%m%d",
    errors="coerce"
)

# 숫자형으로 변환
numeric_columns = [
    "movieCd",
    "first_scrn",
    "first_show",
    "first_week_audi",
    "total_audi",
    "days_in_top10"
]

for column in numeric_columns:
    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )


# 여러 장르가 있으면 첫 번째 장르만 사용
# 예: 액션|범죄|스릴러 → 액션
df["genre_first"] = (
    df["genre"]
    .fillna("미상")
    .astype(str)
    .str.split("|")
    .str[0]
    .str.strip()
)

df.loc[
    df["genre_first"].isin(["", "nan"]),
    "genre_first"
] = "미상"


# 제작 국가 결측값 처리
df["nation"] = (
    df["nation"]
    .fillna("미상")
    .astype(str)
    .str.strip()
)

df.loc[
    df["nation"].isin(["", "nan"]),
    "nation"
] = "미상"


# --------------------------------------------------
# 데이터 정보
# --------------------------------------------------
st.info(
    f"🎬 분석 대상 영화: {len(df):,}편"
)


# ==================================================
# 그래프 1
# ==================================================

st.divider()
st.header("1. 장르별 영화 편수")

st.write(
    "여러 장르가 있는 경우 첫 번째 장르만 사용하여 "
    "장르별 영화 편수를 비교합니다."
)

genre_count = (
    df["genre_first"]
    .value_counts()
    .reset_index()
)

genre_count.columns = ["장르", "영화 편수"]

fig1 = px.pie(
    genre_count,
    names="장르",
    values="영화 편수",
    hole=0.55,
    title="장르별 영화 편수"
)

fig1.update_traces(
    textinfo="percent",
    hovertemplate=(
        "장르: %{label}<br>"
        "영화 편수: %{value}편<br>"
        "비율: %{percent}<extra></extra>"
    )
)

fig1.update_layout(
    height=600,
    legend_title_text="장르"
)

st.plotly_chart(fig1, use_container_width=True)

st.markdown("### 📝 이 그래프로 알 수 있는 것")

st.text_area(
    "첫 번째 그래프에서 알 수 있는 것을 한 문장으로 적어 보세요.",
    placeholder="예: 특정 장르의 영화가 전체 영화에서 가장 큰 비중을 차지한다.",
    height=100,
    key="graph1_note"
)


# ==================================================
# 그래프 2
# ==================================================

st.divider()
st.header("2. 장르 속 영화별 총 관객")

st.write(
    "장르 안에 어떤 영화들이 있는지 살펴보고, "
    "칸의 크기를 총 관객 수에 비례하도록 나타냅니다."
)

treemap_df = df[
    [
        "genre_first",
        "movieNm",
        "total_audi"
    ]
].copy()

treemap_df = treemap_df.dropna(
    subset=["movieNm", "total_audi"]
)

treemap_df = treemap_df[
    treemap_df["total_audi"] > 0
]

fig2 = px.treemap(
    treemap_df,
    path=["genre_first", "movieNm"],
    values="total_audi",
    title="장르별 영화와 총 관객",
    labels={
        "genre_first": "장르",
        "movieNm": "영화",
        "total_audi": "총 관객"
    }
)

fig2.update_traces(
    hovertemplate=(
        "영화: %{label}<br>"
        "총 관객: %{value:,}명<extra></extra>"
    )
)

fig2.update_layout(height=700)

st.plotly_chart(fig2, use_container_width=True)

st.markdown("### 📝 이 그래프로 알 수 있는 것")

st.text_area(
    "두 번째 그래프에서 알 수 있는 것을 한 문장으로 적어 보세요.",
    placeholder="예: 같은 장르 안에서도 영화에 따라 총 관객 수의 차이가 크게 나타난다.",
    height=100,
    key="graph2_note"
)


# ==================================================
# 그래프 3
# ==================================================

st.divider()
st.header("3. 총 관객 수의 분포")

st.write(
    "영화별 총 관객 수가 어느 구간에 많이 몰려 있는지 확인합니다."
)

hist_df = df.dropna(
    subset=["total_audi"]
).copy()

fig3 = px.histogram(
    hist_df,
    x="total_audi",
    nbins=20,
    title="영화별 총 관객 수 히스토그램",
    labels={
        "total_audi": "총 관객 수",
        "count": "영화 편수"
    }
)

fig3.update_traces(
    hovertemplate=(
        "총 관객 구간: %{x}<br>"
        "영화 편수: %{y}편<extra></extra>"
    )
)

fig3.update_layout(
    height=600,
    xaxis_tickformat=","
)

st.plotly_chart(fig3, use_container_width=True)


# 가장 관객이 많은 영화
max_audience_row = df.loc[
    df["total_audi"].idxmax()
]

max_movie_name = max_audience_row["movieNm"]
max_audience = max_audience_row["total_audi"]

st.markdown(
    f"**📌 이 그래프로 알 수 있는 것:** "
    f"대부분의 영화가 총 관객 수의 낮은 구간에 몰려 있으며, "
    f"가장 많은 관객을 기록한 영화는 **{max_movie_name}**으로 "
    f"총 **{max_audience:,.0f}명**의 관객을 기록했습니다."
)


# ==================================================
# 그래프 4
# ==================================================

st.divider()
st.header("4. 개봉일 스크린수와 총 관객의 관계")

st.write(
    "개봉일에 확보한 스크린 수와 영화의 총 관객 수 사이의 관계를 살펴봅니다."
)

scatter_df = df.dropna(
    subset=[
        "first_scrn",
        "total_audi",
        "movieNm",
        "genre_first"
    ]
).copy()

fig4 = px.scatter(
    scatter_df,
    x="first_scrn",
    y="total_audi",
    color="genre_first",
    hover_name="movieNm",
    title="개봉일 스크린수와 총 관객의 관계",
    labels={
        "first_scrn": "개봉일 스크린 수",
        "total_audi": "총 관객",
        "genre_first": "장르"
    }
)

fig4.update_traces(
    hovertemplate=(
        "영화: %{hovertext}<br>"
        "개봉일 스크린 수: %{x:,}개<br>"
        "총 관객: %{y:,}명<extra></extra>"
    )
)

fig4.update_layout(height=650)

st.plotly_chart(fig4, use_container_width=True)

st.markdown("### 📝 이 그래프로 알 수 있는 것")

st.text_area(
    "네 번째 그래프에서 알 수 있는 것을 한 문장으로 적어 보세요.",
    placeholder="예: 개봉일 스크린 수가 많은 영화에서 총 관객이 많은 경우가 나타나는지 확인할 수 있다.",
    height=100,
    key="graph4_note"
)


# ==================================================
# 그래프 5
# ==================================================

st.divider()
st.header("5. 영화가 많은 장르의 총 관객 분포")

st.write(
    "영화가 10편 이상인 장르만 골라 장르별 총 관객 분포를 비교합니다."
)

genre_counts = (
    df["genre_first"]
    .value_counts()
)

valid_genres = genre_counts[
    genre_counts >= 10
].index.tolist()

box_df = df[
    df["genre_first"].isin(valid_genres)
].dropna(
    subset=[
        "genre_first",
        "total_audi",
        "movieNm"
    ]
).copy()

fig5 = px.box(
    box_df,
    x="genre_first",
    y="total_audi",
    color="genre_first",
    points="outliers",
    hover_name="movieNm",
    title="영화가 10편 이상인 장르의 총 관객 분포",
    labels={
        "genre_first": "장르",
        "total_audi": "총 관객"
    }
)

fig5.update_traces(
    hovertemplate=(
        "영화: %{hovertext}<br>"
        "총 관객: %{y:,}명<extra></extra>"
    )
)

fig5.update_layout(
    height=650,
    showlegend=False
)

st.plotly_chart(fig5, use_container_width=True)

st.markdown("### 📝 이 그래프로 알 수 있는 것")

st.text_area(
    "다섯 번째 그래프에서 알 수 있는 것을 한 문장으로 적어 보세요.",
    placeholder="예: 장르에 따라 총 관객의 중앙값과 관객 수의 분포가 다르게 나타난다.",
    height=100,
    key="graph5_note"
)


# ==================================================
# 그래프 6
# ==================================================

st.divider()
st.header("6. 첫 주 관객을 크기로 나타낸 버블 그래프")

st.write(
    "네 번째 산점도에 첫 주 관객 수를 점의 크기로 추가했습니다."
)

bubble_df = df.dropna(
    subset=[
        "first_scrn",
        "total_audi",
        "first_week_audi",
        "movieNm",
        "genre_first"
    ]
).copy()

bubble_df = bubble_df[
    bubble_df["first_week_audi"] > 0
]

fig6 = px.scatter(
    bubble_df,
    x="first_scrn",
    y="total_audi",
    size="first_week_audi",
    color="genre_first",
    hover_name="movieNm",
    size_max=50,
    title="개봉일 스크린수와 총 관객의 관계 - 첫 주 관객 버블",
    labels={
        "first_scrn": "개봉일 스크린 수",
        "total_audi": "총 관객",
        "first_week_audi": "첫 주 관객",
        "genre_first": "장르"
    }
)

fig6.update_traces(
    hovertemplate=(
        "영화: %{hovertext}<br>"
        "개봉일 스크린 수: %{x:,}개<br>"
        "총 관객: %{y:,}명<br>"
        "첫 주 관객: %{marker.size:,}명"
        "<extra></extra>"
    )
)

fig6.update_layout(height=700)

st.plotly_chart(fig6, use_container_width=True)

st.markdown("### 📝 이 그래프로 알 수 있는 것")

st.text_area(
    "여섯 번째 그래프에서 알 수 있는 것을 한 문장으로 적어 보세요.",
    placeholder="예: 첫 주 관객이 많은 영화가 총 관객에서도 높은 수치를 보이는지 확인할 수 있다.",
    height=100,
    key="graph6_note"
)


# ==================================================
# 그래프 7
# ==================================================

st.divider()
st.header("7. 제작 국가에서 장르로 내려가는 영화 분포")

st.write(
    "제작 국가에서 장르로 내려가면서 영화가 어떻게 분포하는지 "
    "선버스트 그래프로 나타냅니다."
)

sunburst_df = df[
    [
        "nation",
        "genre_first",
        "movieNm"
    ]
].dropna().copy()

fig7 = px.sunburst(
    sunburst_df,
    path=[
        "nation",
        "genre_first",
        "movieNm"
    ],
    title="제작 국가 → 장르 → 영화",
    labels={
        "nation": "제작 국가",
        "genre_first": "장르",
        "movieNm": "영화"
    }
)

fig7.update_traces(
    hovertemplate=(
        "%{label}<br>"
        "영화 편수: %{value}편<extra></extra>"
    )
)

fig7.update_layout(height=750)

st.plotly_chart(fig7, use_container_width=True)

st.markdown("### 📝 이 그래프로 알 수 있는 것")

st.text_area(
    "일곱 번째 그래프에서 알 수 있는 것을 한 문장으로 적어 보세요.",
    placeholder="예: 국가별로 제작되는 영화의 장르 구성에 차이가 있음을 알 수 있다.",
    height=100,
    key="graph7_note"
)


# ==================================================
# 그래프 8
# ==================================================

st.divider()

question8 = "첫 주에 관객을 많이 모은 영화는 최종적으로도 총 관객이 많은가?"

st.header("8. " + question8)

st.write(
    "첫 주 관객 수와 최종 총 관객 수의 관계를 산점도로 살펴봅니다."
)

relation_df = df.dropna(
    subset=[
        "first_week_audi",
        "total_audi",
        "movieNm"
    ]
).copy()

relation_df = relation_df[
    relation_df["first_week_audi"] >= 0
]

fig8 = px.scatter(
    relation_df,
    x="first_week_audi",
    y="total_audi",
    hover_name="movieNm",
    title=question8,
    labels={
        "first_week_audi": "첫 주 관객",
        "total_audi": "총 관객"
    }
)

fig8.update_traces(
    hovertemplate=(
        "영화: %{hovertext}<br>"
        "첫 주 관객: %{x:,}명<br>"
        "총 관객: %{y:,}명<extra></extra>"
    )
)

fig8.update_layout(
    height=650,
    xaxis_tickformat=",",
    yaxis_tickformat=","
)

st.plotly_chart(
    fig8,
    use_container_width=True
)

st.markdown("### 📝 이 그래프로 알 수 있는 것")

st.text_area(
    "여덟 번째 그래프에서 알 수 있는 것을 한 문장으로 적어 보세요.",
    placeholder="예: 첫 주 관객이 많은 영화일수록 총 관객도 많은 경향이 나타나는지 확인할 수 있다.",
    height=100,
    key="graph8_note"
)


# --------------------------------------------------
# 데이터 출처
# --------------------------------------------------
st.divider()

st.caption(
    "데이터 출처: 영화관입장권통합전산망(KOBIS) 영화 데이터"
)

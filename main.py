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
DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"

try:
    df = pd.read_csv(DATA_URL)

except Exception as e:
    st.error("데이터를 불러오지 못했습니다.")
    st.write(f"오류 내용: {e}")
    st.stop()


# --------------------------------------------------
# 데이터 전처리
# --------------------------------------------------

# 개봉일: 8자리 숫자 → 날짜
df["openDt"] = pd.to_datetime(
    df["openDt"].astype(str),
    format="%Y%m%d",
    errors="coerce"
)

# 숫자로 사용할 열
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


# genre에 여러 장르가 있으면 첫 번째 장르만 사용
# 예: "액션|범죄|스릴러" → "액션"
df["genre_first"] = (
    df["genre"]
    .fillna("미상")
    .astype(str)
    .str.split("|")
    .str[0]
    .str.strip()
)

# 빈 장르는 미상으로 처리
df.loc[
    df["genre_first"].isin(["", "nan"]),
    "genre_first"
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
    "이 기간에 개봉하여 10위권에 진입한 영화들을 "
    "첫 번째 장르를 기준으로 분류했습니다."
)


# 장르별 영화 편수 계산
genre_count = (
    df["genre_first"]
    .value_counts()
    .reset_index()
)

genre_count.columns = ["장르", "영화 편수"]


# 도넛 그래프
fig1 = px.pie(
    genre_count,
    names="장르",
    values="영화 편수",
    hole=0.55,
    title="장르별 영화 편수",
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


st.plotly_chart(
    fig1,
    use_container_width=True
)


# --------------------------------------------------
# 그래프에서 알 수 있는 것
# --------------------------------------------------

st.markdown("### 📝 이 그래프로 알 수 있는 것")

st.text_area(
    "장르별 분포를 보고 한 문장으로 적어 보세요.",
    placeholder="예: 이 기간에 10위권에 진입한 영화 중 특정 장르의 비중이 가장 높게 나타난다.",
    height=100,
    key="graph1_note"
)


# ==================================================
# 다음 그래프를 위한 공간
# ==================================================

st.divider()

st.header("2. 다음 그래프")

st.info(
    "다음 그래프를 추가할 공간입니다."
)

st.markdown("### 📝 이 그래프로 알 수 있는 것")

st.text_area(
    "두 번째 그래프에서 알 수 있는 것을 적어 보세요.",
    placeholder="새로운 그래프를 추가한 뒤 내용을 적어 보세요.",
    height=100,
    key="graph2_note"
)


st.divider()

st.caption(
    "데이터 출처: 영화관입장권통합전산망(KOBIS) 영화 데이터"
)

import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------------
# 기본 설정
# ---------------------------------------
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")
st.caption("1년간 박스오피스 10위권에 든 영화 216편의 데이터를 살펴봅니다.")


# ---------------------------------------
# 데이터 불러오기
# ---------------------------------------
DATA_URL = (
    "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
)


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 개봉일
    df["openDt"] = df["openDt"].astype(str).str.zfill(8)

    # 여러 장르가 | 로 연결되어 있다면 첫 번째 장르만 사용
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
        df["genre_first"].isin(["", "nan", "None"]),
        "genre_first"
    ] = "미상"

    # 숫자형 데이터 변환
    numeric_columns = [
        "first_scrn",
        "first_show",
        "first_week_audi",
        "total_audi",
        "days_in_top10"
    ]

    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )

    return df


try:
    df = load_data()

except Exception as e:
    st.error("데이터를 불러오는 중 오류가 발생했습니다.")
    st.exception(e)
    st.stop()


# ---------------------------------------
# 데이터 개수
# ---------------------------------------
st.info(f"📊 불러온 영화 데이터: **{len(df)}편**")


# =======================================
# 1. 장르별 영화 편수
# =======================================
st.divider()

st.header("1️⃣ 장르별 영화 편수")

genre_counts = (
    df["genre_first"]
    .value_counts()
    .reset_index()
)

genre_counts.columns = ["장르", "영화 편수"]


fig1 = px.pie(
    genre_counts,
    names="장르",
    values="영화 편수",
    hole=0.55,
    title="장르별 영화 편수"
)

fig1.update_traces(
    textinfo="percent",
    hovertemplate=(
        "<b>%{label}</b><br>"
        "영화 편수: %{value}편<br>"
        "비율: %{percent}<extra></extra>"
    )
)

fig1.update_layout(
    legend_title="장르",
    height=550
)

st.plotly_chart(
    fig1,
    use_container_width=True
)


# ---------------------------------------
# 그래프 1 설명
# ---------------------------------------
st.subheader("💡 이 그래프로 알 수 있는 것")

st.write(
    "어떤 장르의 영화가 많이 제작·개봉되었는지 알 수 있다."
)


# =======================================
# 2. 장르별 영화 트리맵
# =======================================
st.divider()

st.header("2️⃣ 장르별 영화와 총 관객")

st.caption(
    "각 장르 안에 영화가 들어 있으며, 영화 칸의 크기는 총 관객 수를 나타냅니다."
)


treemap_df = df[
    [
        "genre_first",
        "movieNm",
        "total_audi"
    ]
].copy()


# 영화명 처리
treemap_df["movieNm"] = (
    treemap_df["movieNm"]
    .fillna("영화명 미상")
    .astype(str)
)


# 총 관객이 0 이하인 데이터 제외
treemap_df = treemap_df[
    treemap_df["total_audi"] > 0
].copy()


fig2 = px.treemap(
    treemap_df,
    path=["genre_first", "movieNm"],
    values="total_audi",
    title="장르별 영화 트리맵"
)

fig2.update_traces(
    hovertemplate=(
        "<b>%{label}</b><br>"
        "총 관객: %{value:,.0f}명"
        "<extra></extra>"
    )
)

fig2.update_layout(
    height=750,
    margin=dict(
        t=60,
        l=10,
        r=10,
        b=10
    )
)

st.plotly_chart(
    fig2,
    use_container_width=True
)


# ---------------------------------------
# 그래프 2 설명
# ---------------------------------------
st.subheader("💡 이 그래프로 알 수 있는 것")

st.write(
    "각 장르에서 어떤 영화가 많은 관객을 모았는지 비교할 수 있다."
)


# =======================================
# 3. 총 관객 히스토그램
# =======================================
st.divider()

st.header("3️⃣ 영화별 총 관객 분포")

st.caption(
    "영화들의 총 관객 수가 어떤 구간에 많이 분포하는지 확인합니다."
)


# 총 관객 데이터 준비
hist_df = df[
    ["movieNm", "total_audi"]
].copy()

hist_df = hist_df.dropna(
    subset=["total_audi"]
)

hist_df = hist_df[
    hist_df["total_audi"] >= 0
]


# ---------------------------------------
# 히스토그램
# ---------------------------------------
fig3 = px.histogram(
    hist_df,
    x="total_audi",
    nbins=20,
    title="총 관객 수 분포",
    labels={
        "total_audi": "총 관객 수",
        "count": "영화 편수"
    }
)

fig3.update_traces(
    hovertemplate=(
        "관객 구간: %{x}<br>"
        "영화 편수: %{y}편"
        "<extra></extra>"
    )
)

fig3.update_layout(
    height=550,
    xaxis_title="총 관객 수",
    yaxis_title="영화 편수"
)

st.plotly_chart(
    fig3,
    use_container_width=True
)


# ---------------------------------------
# 대부분의 영화가 몰려 있는 구간 계산
# ---------------------------------------
hist_values = hist_df["total_audi"]

# 최대값과 최소값
min_audience = hist_values.min()
max_audience = hist_values.max()

# 20개 구간으로 나누기
bins = 20

bin_counts, bin_edges = pd.cut(
    hist_values,
    bins=bins,
    include_lowest=True,
    retbins=True
)

most_common_bin = bin_counts.value_counts().idxmax()

bin_left = most_common_bin.left
bin_right = most_common_bin.right

most_common_count = (
    bin_counts.value_counts().max()
)


# ---------------------------------------
# 가장 관객이 많은 영화
# ---------------------------------------
max_index = hist_df["total_audi"].idxmax()

top_movie = hist_df.loc[
    max_index,
    "movieNm"
]

top_movie_audience = hist_df.loc[
    max_index,
    "total_audi"
]


# ---------------------------------------
# 그래프 3 설명
# ---------------------------------------
st.subheader("💡 이 그래프로 알 수 있는 것")

st.write(
    f"대부분의 영화는 **약 {bin_left:,.0f}명~{bin_right:,.0f}명** "
    f"구간에 몰려 있으며, 가장 관객이 많은 영화는 "
    f"**{top_movie}**로 총 **{top_movie_audience:,.0f}명**의 관객을 기록했다."
)


# =======================================
# 데이터 미리보기
# =======================================
st.divider()

st.subheader("📋 사용한 데이터")

display_columns = [
    "movieCd",
    "movieNm",
    "openDt",
    "genre",
    "nation",
    "first_scrn",
    "first_show",
    "first_week_audi",
    "total_audi",
    "days_in_top10"
]

available_columns = [
    col for col in display_columns
    if col in df.columns
]

st.dataframe(
    df[available_columns],
    use_container_width=True,
    hide_index=True
)

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
DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 개봉일은 문자열로 처리
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

    # 총 관객을 숫자로 변환
    df["total_audi"] = pd.to_numeric(
        df["total_audi"],
        errors="coerce"
    ).fillna(0)

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
# 그래프 1 설명 작성 공간
# ---------------------------------------
st.subheader("💡 이 그래프로 알 수 있는 것")

st.text_area(
    "한 문장으로 작성해 보세요.",
    placeholder="예: 어떤 장르의 영화가 가장 많이 포함되어 있는지 알 수 있다.",
    height=80,
    key="graph1_note"
)


# =======================================
# 2. 장르별 영화 트리맵
# =======================================
st.divider()

st.header("2️⃣ 장르별 영화와 총 관객")

st.caption(
    "각 장르 안에 영화가 들어 있으며, 영화 칸의 크기는 총 관객 수를 나타냅니다."
)


# 트리맵에 사용할 데이터
treemap_df = df[
    [
        "genre_first",
        "movieNm",
        "total_audi"
    ]
].copy()

# 영화명이 비어 있는 경우 처리
treemap_df["movieNm"] = (
    treemap_df["movieNm"]
    .fillna("영화명 미상")
    .astype(str)
)

# 총 관객이 0 이하인 데이터는 트리맵 크기 계산에 적합하지 않으므로 제외
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
# 그래프 2 설명 작성 공간
# ---------------------------------------
st.subheader("💡 이 그래프로 알 수 있는 것")

st.text_area(
    "한 문장으로 작성해 보세요.",
    placeholder="예: 장르별로 어떤 영화가 많은 관객을 모았는지 비교할 수 있다.",
    height=80,
    key="graph2_note"
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

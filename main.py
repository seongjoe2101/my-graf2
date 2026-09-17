import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------------
# 기본 설정
# -----------------------------------
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    layout="wide"
)

st.title("영화 데이터 그래프 도감 2 - 분포와 관계")
st.write("1년간 박스오피스 10위권에 든 영화 216편의 데이터를 살펴봅니다.")

# -----------------------------------
# 데이터 불러오기
# -----------------------------------
DATA_URL = (
    "https://raw.githubusercontent.com/greatsong/modudata/"
    "main/data/kobis_movies.csv"
)


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 개봉일: YYYYMMDD → 날짜 형식
    df["openDt"] = pd.to_datetime(
        df["openDt"].astype(str),
        format="%Y%m%d",
        errors="coerce"
    )

    # 여러 장르가 |로 연결되어 있다면 첫 번째 장르만 사용
    df["genre"] = (
        df["genre"]
        .fillna("미상")
        .astype(str)
        .str.split("|")
        .str[0]
        .str.strip()
    )

    # 빈 장르는 미상으로 처리
    df["genre"] = df["genre"].replace("", "미상")

    # 총 관객 수를 숫자로 변환
    df["total_audi"] = pd.to_numeric(
        df["total_audi"],
        errors="coerce"
    ).fillna(0)

    return df


try:
    df = load_data()

except Exception as e:
    st.error("데이터를 불러오는 중 문제가 발생했습니다.")
    st.error(str(e))
    st.stop()


# ===================================
# 데이터 정보
# ===================================
st.subheader("데이터 정보")

col1, col2 = st.columns(2)

with col1:
    st.metric("영화 편수", f"{len(df):,}편")

with col2:
    st.metric("장르 종류", f"{df['genre'].nunique():,}개")


# ===================================
# 그래프 1
# ===================================
st.divider()
st.header("그래프 1. 장르별 영화 편수")

genre_counts = (
    df["genre"]
    .value_counts()
    .reset_index()
)

genre_counts.columns = ["장르", "영화편수"]

fig1 = px.pie(
    genre_counts,
    names="장르",
    values="영화편수",
    hole=0.45,
    title="장르별 영화 편수"
)

fig1.update_traces(
    textposition="inside",
    textinfo="percent",
    hovertemplate=(
        "<b>%{label}</b><br>"
        "편수: %{value}편<br>"
        "비율: %{percent}<extra></extra>"
    )
)

fig1.update_layout(
    height=550,
    legend_title_text="장르"
)

st.plotly_chart(
    fig1,
    use_container_width=True
)

st.subheader("이 그래프로 알 수 있는 것")

st.text_area(
    "한 문장으로 정리해 보세요.",
    placeholder=(
        "예: 이 기간에는 ○○ 장르의 영화가 가장 많았고, "
        "전체 영화 중 약 ○○%를 차지했다."
    ),
    height=80,
    key="graph1_note"
)


# ===================================
# 그래프 2
# ===================================
st.divider()
st.header("그래프 2. 장르별 영화와 총 관객 트리맵")

st.write(
    "장르 안에 각 영화가 들어 있으며, "
    "칸의 크기는 총 관객 수를 나타냅니다."
)

treemap_df = df[
    ["genre", "movieNm", "total_audi"]
].copy()

treemap_df["movieNm"] = (
    treemap_df["movieNm"]
    .fillna("영화명 미상")
    .astype(str)
)

treemap_df["트리맵크기"] = treemap_df["total_audi"]

fig2 = px.treemap(
    treemap_df,
    path=["genre", "movieNm"],
    values="트리맵크기",
    title="장르별 영화 총 관객 트리맵"
)

fig2.update_traces(
    hovertemplate=(
        "<b>%{label}</b><br>"
        "총 관객: %{value:,.0f}명"
        "<extra></extra>"
    )
)

fig2.update_layout(
    height=700
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

st.subheader("이 그래프로 알 수 있는 것")

st.text_area(
    "한 문장으로 정리해 보세요.",
    placeholder=(
        "예: 총 관객이 많은 영화는 ○○ 장르에 많이 분포하며, "
        "특히 ○○ 영화의 관객 규모가 크게 나타난다."
    ),
    height=80,
    key="graph2_note"
)


# ===================================
# 그래프 3
# ===================================
st.divider()
st.header("그래프 3. 총 관객 분포")

st.write(
    "영화별 total_audi(총 관객)가 어느 구간에 많이 분포하는지 확인합니다."
)

# 총 관객 데이터
hist_df = df[
    ["movieNm", "total_audi"]
].copy()

hist_df["movieNm"] = (
    hist_df["movieNm"]
    .fillna("영화명 미상")
    .astype(str)
)

# 히스토그램
fig3 = px.histogram(
    hist_df,
    x="total_audi",
    nbins=20,
    title="영화별 총 관객 분포",
    labels={
        "total_audi": "총 관객",
        "count": "영화 편수"
    }
)

fig3.update_traces(
    hovertemplate=(
        "총 관객 구간: %{x}<br>"
        "영화 편수: %{y}편"
        "<extra></extra>"
    )
)

fig3.update_layout(
    height=550,
    xaxis_title="총 관객",
    yaxis_title="영화 편수"
)

st.plotly_chart(
    fig3,
    use_container_width=True
)


# -----------------------------------
# 가장 많이 몰린 구간 계산
# -----------------------------------
hist_counts, bin_edges = pd.cut(
    hist_df["total_audi"],
    bins=20,
    include_lowest=True,
    retbins=True
)

most_common_bin = hist_counts.value_counts().idxmax()

bin_start = most_common_bin.left
bin_end = most_common_bin.right

# 총 관객이 가장 많은 영화
max_audience_row = hist_df.loc[
    hist_df["total_audi"].idxmax()
]

max_movie_name = max_audience_row["movieNm"]
max_audience = max_audience_row["total_audi"]


# -----------------------------------
# 그래프 아래 결과 문구
# -----------------------------------
st.subheader("이 그래프로 알 수 있는 것")

st.write(
    f"대부분의 영화는 **{bin_start:,.0f}명 ~ {bin_end:,.0f}명** "
    f"정도의 총 관객 구간에 몰려 있습니다."
)

st.write(
    f"총 관객이 가장 많은 영화는 **{max_movie_name}**으로, "
    f"총 **{max_audience:,.0f}명**의 관객을 기록했습니다."
)

st.text_area(
    "한 문장으로 정리해 보세요.",
    placeholder=(
        "예: 대부분의 영화는 ○○명~○○명 구간에 몰려 있으며, "
        "가장 많은 관객을 기록한 영화는 ○○이다."
    ),
    height=80,
    key="graph3_note"
)


# ===================================
# 원본 데이터
# ===================================
st.divider()
st.subheader("원본 데이터 확인")

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)

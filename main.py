import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px


# --------------------------------------------------
# 페이지 설정
# --------------------------------------------------
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    layout="wide"
)


# --------------------------------------------------
# 제목
# --------------------------------------------------
st.title("영화 데이터 그래프 도감 2 - 분포와 관계")

st.write(
    "영화의 장르, 관객 수, 개봉 첫날 상영 규모, 첫 주 관객 등의 "
    "데이터를 다양한 그래프로 살펴봅니다."
)


# --------------------------------------------------
# 데이터 불러오기
# --------------------------------------------------
@st.cache_data
def load_data():

    url = (
        "https://raw.githubusercontent.com/greatsong/modudata/"
        "main/data/kobis_movies.csv"
    )

    df = pd.read_csv(url)

    # 개봉일 변환
    df["openDt"] = pd.to_datetime(
        df["openDt"].astype(str),
        format="%Y%m%d",
        errors="coerce"
    )

    # 여러 장르가 있으면 첫 번째 장르만 사용
    df["genre"] = (
        df["genre"]
        .fillna("미상")
        .astype(str)
        .str.split("|")
        .str[0]
        .str.strip()
    )

    # 빈 장르는 미상으로 처리
    df.loc[df["genre"].eq(""), "genre"] = "미상"

    # 숫자형 데이터 변환
    numeric_columns = [
        "first_scrn",
        "first_show",
        "first_week_audi",
        "total_audi",
        "days_in_top10"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    return df


df = load_data()


# ==================================================
# 데이터 기본 정보
# ==================================================
st.header("데이터 살펴보기")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "영화 수",
        f"{len(df):,}편"
    )

with col2:
    st.metric(
        "평균 총 관객",
        f"{df['total_audi'].mean():,.0f}명"
    )

with col3:
    st.metric(
        "최대 총 관객",
        f"{df['total_audi'].max():,.0f}명"
    )

with col4:
    st.metric(
        "평균 첫 주 관객",
        f"{df['first_week_audi'].mean():,.0f}명"
    )


# ==================================================
# 그래프 1
# 장르별 영화 수 도넛 차트
# ==================================================
st.header("그래프 1. 장르별 영화 수")

genre_counts = (
    df["genre"]
    .value_counts()
    .reset_index()
)

genre_counts.columns = [
    "genre",
    "count"
]

fig1 = px.pie(
    genre_counts,
    names="genre",
    values="count",
    hole=0.45,
    title="장르별 영화 수"
)

fig1.update_traces(
    textinfo="label+percent",
    hovertemplate=(
        "장르: %{label}<br>"
        "영화 수: %{value}편<br>"
        "비율: %{percent}"
        "<extra></extra>"
    )
)

fig1.update_layout(
    height=600
)

st.plotly_chart(
    fig1,
    use_container_width=True
)

st.subheader("이 그래프로 알 수 있는 것")

st.text_area(
    "한 문장으로 정리해 보세요.",
    placeholder="예: 가장 많은 영화가 만들어진 장르는 ○○ 장르이다.",
    height=80,
    key="graph1_note"
)


# ==================================================
# 그래프 2
# 장르 → 영화 트리맵
# ==================================================
st.header("그래프 2. 장르별 영화의 총 관객")

treemap_df = df.dropna(
    subset=["total_audi"]
).copy()

treemap_df["movieNm"] = (
    treemap_df["movieNm"]
    .fillna("영화명 미상")
    .astype(str)
)

fig2 = px.treemap(
    treemap_df,
    path=["genre", "movieNm"],
    values="total_audi",
    color="genre",
    title="장르 → 영화별 총 관객",
    hover_data={
        "total_audi": ":,.0f"
    }
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
    placeholder="예: ○○ 장르에서 관객이 많은 영화가 여러 편 나타난다.",
    height=80,
    key="graph2_note"
)


# ==================================================
# 그래프 3
# 총 관객 히스토그램
# ==================================================
st.header("그래프 3. 영화별 총 관객 분포")

hist_df = df.dropna(
    subset=["total_audi"]
).copy()

fig3 = px.histogram(
    hist_df,
    x="total_audi",
    nbins=20,
    title="영화별 총 관객 분포",
    labels={
        "total_audi": "총 관객"
    }
)

fig3.update_layout(
    height=600,
    xaxis_title="총 관객",
    yaxis_title="영화 수"
)

st.plotly_chart(
    fig3,
    use_container_width=True
)


# 가장 많은 영화가 몰린 구간 계산
# pd.np가 아니라 numpy를 사용
hist_counts, bin_edges = np.histogram(
    hist_df["total_audi"],
    bins=20
)

max_bin_index = hist_counts.argmax()

range_start = bin_edges[max_bin_index]
range_end = bin_edges[max_bin_index + 1]


# 총 관객이 가장 많은 영화
max_movie_row = (
    hist_df
    .sort_values(
        "total_audi",
        ascending=False
    )
    .iloc[0]
)

max_movie_name = max_movie_row["movieNm"]
max_movie_audience = max_movie_row["total_audi"]

st.info(
    f"가장 많은 영화가 몰려 있는 관객 구간은 "
    f"약 {range_start:,.0f}명 ~ {range_end:,.0f}명입니다."
)

st.info(
    f"총 관객이 가장 많은 영화는 "
    f"'{max_movie_name}'으로, "
    f"총 관객은 {max_movie_audience:,.0f}명입니다."
)

st.subheader("이 그래프로 알 수 있는 것")

st.text_area(
    "한 문장으로 정리해 보세요.",
    placeholder=(
        "예: 대부분의 영화는 총 관객이 ○○명 구간에 집중되어 있다."
    ),
    height=80,
    key="graph3_note"
)


# ==================================================
# 그래프 4
# 개봉일 스크린 수 vs 총 관객 산점도
# ==================================================
st.header("그래프 4. 개봉일 스크린 수와 총 관객의 관계")

scatter_df = df.dropna(
    subset=[
        "first_scrn",
        "total_audi"
    ]
).copy()

scatter_df["movieNm"] = (
    scatter_df["movieNm"]
    .fillna("영화명 미상")
    .astype(str)
)

fig4 = px.scatter(
    scatter_df,
    x="first_scrn",
    y="total_audi",
    color="genre",
    hover_name="movieNm",
    hover_data={
        "genre": True,
        "first_scrn": ":,.0f",
        "total_audi": ":,.0f"
    },
    labels={
        "first_scrn": "개봉일 스크린 수",
        "total_audi": "총 관객",
        "genre": "장르"
    },
    title="개봉일 스크린 수와 총 관객의 관계"
)

fig4.update_traces(
    hovertemplate=(
        "<b>%{hovertext}</b><br>"
        "장르: %{customdata[0]}<br>"
        "개봉일 스크린 수: %{x:,.0f}개<br>"
        "총 관객: %{y:,.0f}명"
        "<extra></extra>"
    )
)

fig4.update_layout(
    height=650,
    xaxis_title="개봉일 스크린 수",
    yaxis_title="총 관객"
)

st.plotly_chart(
    fig4,
    use_container_width=True
)

st.write(
    "※ 각 점은 하나의 영화를 나타내며, 장르별로 색을 다르게 표시했습니다."
)

st.subheader("이 그래프로 알 수 있는 것")

st.text_area(
    "한 문장으로 정리해 보세요.",
    placeholder=(
        "예: 개봉일 스크린 수가 많은 영화일수록 총 관객도 높은 경향이 나타난다."
    ),
    height=80,
    key="graph4_note"
)


# ==================================================
# 그래프 5
# 장르별 총 관객 박스플롯
# ==================================================
st.header("그래프 5. 장르별 총 관객 분포")

genre_movie_counts = (
    df["genre"]
    .value_counts()
)

valid_genres = genre_movie_counts[
    genre_movie_counts >= 10
].index.tolist()

boxplot_df = df[
    df["genre"].isin(valid_genres)
].copy()

boxplot_df = boxplot_df.dropna(
    subset=["total_audi"]
)

boxplot_df["movieNm"] = (
    boxplot_df["movieNm"]
    .fillna("영화명 미상")
    .astype(str)
)

if len(valid_genres) == 0:

    st.warning(
        "영화가 10편 이상인 장르가 없어 박스플롯을 그릴 수 없습니다."
    )

else:

    fig5 = px.box(
        boxplot_df,
        x="genre",
        y="total_audi",
        color="genre",
        points="outliers",
        hover_name="movieNm",
        hover_data={
            "genre": True,
            "total_audi": ":,.0f"
        },
        labels={
            "genre": "장르",
            "total_audi": "총 관객"
        },
        title="영화가 10편 이상인 장르의 총 관객 분포"
    )

    fig5.update_traces(
        hovertemplate=(
            "<b>%{hovertext}</b><br>"
            "장르: %{customdata[0]}<br>"
            "총 관객: %{y:,.0f}명"
            "<extra></extra>"
        )
    )

    fig5.update_layout(
        height=650,
        xaxis_title="장르",
        yaxis_title="총 관객",
        showlegend=False
    )

    st.plotly_chart(
        fig5,
        use_container_width=True
    )

    st.write(
        "※ 상자 밖에 표시된 점은 해당 장르의 일반적인 관객 분포에서 "
        "벗어난 값이며, 마우스를 올리면 영화명을 확인할 수 있습니다."
    )

st.subheader("이 그래프로 알 수 있는 것")

st.text_area(
    "한 문장으로 정리해 보세요.",
    placeholder=(
        "예: ○○ 장르는 총 관객의 분포가 넓고, "
        "○○ 장르에서는 관객이 특히 많은 영화가 이상치로 나타난다."
    ),
    height=80,
    key="graph5_note"
)


# ==================================================
# 그래프 6
# 첫 주 관객을 점 크기로 사용하는 버블 그래프
# ==================================================
st.header("그래프 6. 첫 주 관객을 나타낸 버블 그래프")

bubble_df = df.dropna(
    subset=[
        "first_scrn",
        "total_audi",
        "first_week_audi"
    ]
).copy()

bubble_df["movieNm"] = (
    bubble_df["movieNm"]
    .fillna("영화명 미상")
    .astype(str)
)

fig6 = px.scatter(
    bubble_df,
    x="first_scrn",
    y="total_audi",
    size="first_week_audi",
    color="genre",
    hover_name="movieNm",
    size_max=55,
    labels={
        "first_scrn": "개봉일 스크린 수",
        "total_audi": "총 관객",
        "first_week_audi": "첫 주 관객",
        "genre": "장르"
    },
    title="개봉일 스크린 수 × 총 관객 × 첫 주 관객"
)

fig6.update_traces(
    hovertemplate=(
        "<b>%{hovertext}</b><br>"
        "장르: %{customdata[0]}<br>"
        "개봉일 스크린 수: %{x:,.0f}개<br>"
        "총 관객: %{y:,.0f}명"
        "<extra></extra>"
    )
)

fig6.update_layout(
    height=700,
    xaxis_title="개봉일 스크린 수",
    yaxis_title="총 관객"
)

st.plotly_chart(
    fig6,
    use_container_width=True
)

st.write(
    "※ 점 하나가 영화 한 편을 나타냅니다. "
    "점의 크기가 클수록 첫 주 관객이 많다는 뜻입니다."
)

st.subheader("이 그래프로 알 수 있는 것")

st.text_area(
    "한 문장으로 정리해 보세요.",
    placeholder=(
        "예: 첫 주 관객이 많은 영화는 버블 크기가 크게 나타난다."
    ),
    height=80,
    key="graph6_note"
)


# ==================================================
# 원본 데이터
# ==================================================
st.header("원본 데이터")

st.dataframe(
    df,
    use_container_width=True
)

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
DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"

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

    return df


try:
    df = load_data()

except Exception as e:
    st.error("데이터를 불러오는 중 문제가 발생했습니다.")
    st.error(str(e))
    st.stop()


# -----------------------------------
# 데이터 확인
# -----------------------------------
st.subheader("데이터 정보")

col1, col2 = st.columns(2)

with col1:
    st.metric("영화 편수", f"{len(df):,}편")

with col2:
    st.metric("장르 종류", f"{df['genre'].nunique():,}개")


# -----------------------------------
# 그래프 1
# -----------------------------------
st.divider()
st.header("그래프 1. 장르별 영화 편수")

# 장르별 영화 편수 계산
genre_counts = (
    df["genre"]
    .value_counts()
    .reset_index()
)

genre_counts.columns = ["장르", "영화편수"]

# 도넛 그래프
fig = px.pie(
    genre_counts,
    names="장르",
    values="영화편수",
    hole=0.45,
    title="장르별 영화 편수"
)

fig.update_traces(
    textposition="inside",
    textinfo="percent",
    hovertemplate=(
        "<b>%{label}</b><br>"
        "편수: %{value}편<br>"
        "비율: %{percent}<extra></extra>"
    )
)

fig.update_layout(
    height=550,
    legend_title_text="장르"
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------------
# 설명 작성 공간
# -----------------------------------
st.subheader("이 그래프로 알 수 있는 것")

st.text_area(
    "한 문장으로 정리해 보세요.",
    placeholder="예: 이 기간에는 ○○ 장르의 영화가 가장 많았고, 전체 영화 중 약 ○○%를 차지했다.",
    height=80,
    key="graph1_note"
)


# -----------------------------------
# 원본 데이터 일부 확인
# -----------------------------------
st.divider()
st.subheader("원본 데이터 확인")

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)

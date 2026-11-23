
import streamlit as st
import pandas as pd
import plotly.express as px
from urllib.parse import quote

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score

st.set_page_config(
    page_title="베이커리 지역 분석",
    page_icon="🥐",
    layout="wide"
)

st.title("🥐 우리 동네 베이커리 분석")
st.write("지역별 제과점 현황과 가게 정보를 확인할 수 있는 사이트입니다.")

# -------------------------
# 데이터 불러오기
# -------------------------

@st.cache_data
def load_data():
    encodings = ["cp949", "euc-kr", "utf-8-sig", "utf-8"]

    for encoding in encodings:
        try:
            return pd.read_csv(
                "bakery2.csv",
                encoding=encoding
            )
        except UnicodeDecodeError:
            continue

    raise ValueError("CSV 파일의 인코딩을 확인해 주세요.")

uploaded_file = st.sidebar.file_uploader(
    "CSV 파일을 직접 업로드할 수도 있어요",
    type=["csv"]
)

try:
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file, encoding="cp949")
    else:
        df = load_data()

except FileNotFoundError:
    st.error("GitHub 저장소에 bakery2.csv 파일을 올려주세요.")
    st.stop()

except Exception as e:
    st.error(f"데이터를 불러오지 못했습니다: {e}")
    st.stop()

# -------------------------
# 실제 데이터 열 확인
# -------------------------

required_columns = ["사업장명", "영업상태명"]

for col in required_columns:
    if col not in df.columns:
        st.error(f"CSV에 '{col}' 열이 없습니다.")
        st.write("현재 데이터 열:", list(df.columns))
        st.stop()

# 주소: 도로명주소가 없으면 지번주소 사용
df["주소"] = ""

if "도로명주소" in df.columns:
    df["주소"] = df["도로명주소"].fillna("")

if "지번주소" in df.columns:
    df["주소"] = df["주소"].where(
        df["주소"].astype(str).str.strip() != "",
        df["지번주소"].fillna("")
    )

df["사업장명"] = df["사업장명"].fillna("상호명 미확인")
df["영업상태명"] = df["영업상태명"].fillna("상태 미확인")

# -------------------------
# 지역 추출
# -------------------------

def get_region(address):
    if pd.isna(address):
        return "주소 미확인"

    words = str(address).strip().split()

    if len(words) >= 2:
        return words[0] + " " + words[1]
    elif len(words) == 1:
        return words[0]

    return "주소 미확인"

df["지역"] = df["주소"].apply(get_region)

# -------------------------
# 사이드바 지역 선택
# -------------------------

st.sidebar.header("📍 지역 선택")

regions = sorted(
    df.loc[df["지역"] != "주소 미확인", "지역"].unique()
)

if not regions:
    st.error("주소에서 지역을 찾을 수 없습니다.")
    st.stop()

selected_region = st.sidebar.selectbox(
    "분석할 지역을 선택하세요",
    regions
)

region_df = df[df["지역"] == selected_region].copy()

# -------------------------
# 검색
# -------------------------

st.subheader(f"📍 {selected_region} 베이커리 현황")

# 실제 데이터의 영업상태는 영업/정상, 폐업 등으로 구성
active_count = (
    region_df["영업상태명"]
    .astype(str)
    .str.contains("영업/정상", na=False)
    .sum()
)

closed_count = (
    region_df["영업상태명"]
    .astype(str)
    .str.contains("폐업", na=False)
    .sum()
)

col1, col2, col3 = st.columns(3)

col1.metric("전체 제과점", f"{len(region_df):,}개")
col2.metric("영업 중", f"{active_count:,}개")
col3.metric("폐업", f"{closed_count:,}개")

st.divider()

# -------------------------
# 전국 지역별 제과점 그래프
# -------------------------

st.subheader("📊 지역별 제과점 분포")

region_count = (
    df[df["지역"] != "주소 미확인"]
    .groupby("지역")
    .size()
    .reset_index(name="제과점 수")
    .sort_values("제과점 수", ascending=False)
)

fig = px.bar(
    region_count,
    x="지역",
    y="제과점 수",
    color="제과점 수",
    text="제과점 수",
    title="지역별 제과점 수 비교"
)

fig.update_layout(
    xaxis_title="지역",
    yaxis_title="제과점 수",
    xaxis_tickangle=-45
)

st.plotly_chart(fig, use_container_width=True)

# -------------------------
# 영업상태 그래프
# -------------------------

st.subheader("📈 선택 지역 영업상태")

status_count = (
    region_df["영업상태명"]
    .value_counts()
    .reset_index()
)

status_count.columns = ["영업상태", "가게 수"]

fig2 = px.pie(
    status_count,
    names="영업상태",
    values="가게 수",
    hole=0.4,
    title=f"{selected_region} 영업상태 비율"
)

st.plotly_chart(fig2, use_container_width=True)

st.divider()

# -------------------------
# 가게 목록
# -------------------------

st.subheader("🥐 지역별 베이커리 가게")

search = st.text_input("가게 이름으로 검색하기")

show_df = region_df.copy()

if search:
    show_df = show_df[
        show_df["사업장명"].astype(str).str.contains(
            search,
            case=False,
            na=False
        )
    ]

st.write(f"검색된 가게: **{len(show_df):,}개**")

for _, shop in show_df.iterrows():

    name = str(shop["사업장명"])
    address = str(shop["주소"])
    status = str(shop["영업상태명"])

    with st.container(border=True):

        st.markdown(f"### 🥐 {name}")

        st.write(f"📍 주소: {address}")
        st.write(f"📌 영업상태: {status}")

        if "전화번호" in df.columns:
            phone = shop["전화번호"]

            if pd.notna(phone) and str(phone).strip():
                st.write(f"☎️ 전화번호: {phone}")

        if "홈페이지" in df.columns:
            homepage = shop["홈페이지"]

            if pd.notna(homepage) and str(homepage).strip():
                st.markdown(
                    f"[🌐 홈페이지 방문]({homepage})"
                )

        map_url = (
            "https://map.naver.com/p/search/"
            + quote(name + " " + address)
        )

        st.markdown(
            f"[🗺️ 네이버 지도에서 위치 보기]({map_url})"
        )

if show_df.empty:
    st.info("검색 결과가 없습니다.")

st.divider()

# -------------------------
# 의사결정나무 분류 알고리즘
# -------------------------

st.subheader("🌳 의사결정나무 분류 분석")

st.write(
    "지역과 업태 정보를 이용해 제과점의 영업상태를 "
    "분류하는 머신러닝 모델입니다."
)

model_df = df.copy()

model_df["분류결과"] = model_df["영업상태명"].astype(str).apply(
    lambda x: "영업 중" if "영업/정상" in x else (
        "폐업" if "폐업" in x else None
    )
)

feature_columns = ["지역"]

if "업태구분명" in model_df.columns:
    feature_columns.append("업태구분명")

if "위생업태명" in model_df.columns:
    feature_columns.append("위생업태명")

model_df = model_df.dropna(subset=["분류결과"])

for col in feature_columns:
    model_df[col] = model_df[col].fillna("정보 없음").astype(str)

if model_df["분류결과"].nunique() == 2 and (
    model_df["분류결과"].value_counts().min() >= 2
):

    X = model_df[feature_columns]
    y = model_df["분류결과"]

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "category",
                OneHotEncoder(handle_unknown="ignore"),
                feature_columns
            )
        ]
    )

    model = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", DecisionTreeClassifier(
            max_depth=5,
            random_state=42,
            class_weight="balanced"
        ))
    ])

    try:
        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=42,
            stratify=y
        )

        model.fit(X_train, y_train)

        prediction = model.predict(X_test)

        accuracy = accuracy_score(y_test, prediction)

        st.metric(
            "모델 분류 정확도",
            f"{accuracy * 100:.1f}%"
        )

        st.caption(
            "테스트 데이터 기준 정확도입니다. "
            "지역과 업태 정보만을 이용하므로 실제 영업 여부를 "
            "확정하는 결과는 아닙니다."
        )

    except ValueError:
        st.warning("데이터가 부족해 모델을 학습할 수 없습니다.")

else:
    st.warning("분류에 필요한 영업상태 데이터가 부족합니다.")

# -------------------------
# 데이터 다운로드
# -------------------------

st.divider()

csv = df.to_csv(
    index=False,
    encoding="utf-8-sig"
)

st.download_button(
    "📥 분석 데이터 다운로드",
    data=csv,
    file_name="bakery_analysis.csv",
    mime="text/csv"
)

st.caption(
    "분석 자료: 사용자가 제공한 bakery2.csv"
)

import streamlit as st
import pandas as pd
import plotly.express as px
import re
from urllib.parse import quote

from sklearn.tree import DecisionTreeClassifier
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

st.set_page_config(
    page_title="우리 동네 베이커리 찾기",
    page_icon="🥐",
    layout="wide"
)

st.title("🥐 우리 동네 베이커리 시장 분석")
st.write("지역을 선택하고 해당 지역의 베이커리와 시장 현황을 확인해 보세요.")

# -----------------------------
# 데이터 불러오기
# -----------------------------

@st.cache_data
def load_data(file):
    encodings = ["utf-8-sig", "cp949", "euc-kr", "utf-8"]

    for encoding in encodings:
        try:
            if file is None:
                return pd.read_csv(
                    "전국제과점업소표준데이터.csv",
                    encoding=encoding
                )
            return pd.read_csv(file, encoding=encoding)
        except UnicodeDecodeError:
            continue

    raise ValueError("CSV 파일의 인코딩을 읽을 수 없습니다.")

uploaded_file = st.sidebar.file_uploader(
    "전국 제과점 CSV 파일 업로드",
    type=["csv"]
)

try:
    df = load_data(uploaded_file)
except FileNotFoundError:
    st.warning("왼쪽에서 전국 제과점 CSV 파일을 업로드해 주세요.")
    st.stop()
except Exception as e:
    st.error(f"데이터를 불러오지 못했습니다: {e}")
    st.stop()

# -----------------------------
# 열 이름 자동 인식
# -----------------------------

def find_column(possible_names):
    for name in possible_names:
        if name in df.columns:
            return name
    return None

name_col = find_column(["사업장명", "업소명", "상호명"])
address_col = find_column([
    "도로명전체주소", "도로명주소",
    "소재지전체주소", "소재지주소", "지번주소"
])
phone_col = find_column(["전화번호", "소재지전화"])
status_col = find_column(["영업상태명", "영업상태"])
date_col = find_column(["인허가일자", "허가일자"])

if name_col is None or address_col is None:
    st.error("사업장명 또는 주소 열을 찾을 수 없습니다.")
    st.write("현재 CSV의 열 이름:", list(df.columns))
    st.stop()

# -----------------------------
# 주소와 지역 정리
# -----------------------------

region_aliases = {
    "서울시": "서울특별시",
    "서울": "서울특별시",
    "부산": "부산광역시",
    "대구": "대구광역시",
    "인천": "인천광역시",
    "광주": "광주광역시",
    "대전": "대전광역시",
    "울산": "울산광역시",
    "세종": "세종특별자치시",
    "경기": "경기도",
    "강원": "강원특별자치도",
    "충북": "충청북도",
    "충남": "충청남도",
    "전북": "전북특별자치도",
    "전남": "전라남도",
    "경북": "경상북도",
    "경남": "경상남도",
    "제주": "제주특별자치도"
}

def get_region(address):
    if pd.isna(address):
        return "주소 미확인"

    address = str(address).strip()
    first_word = address.split(" ")[0]

    return region_aliases.get(first_word, first_word)

df["지역"] = df[address_col].apply(get_region)
df[name_col] = df[name_col].fillna("상호명 미확인")
df[address_col] = df[address_col].fillna("주소 미확인")

# 인허가 연도 만들기
if date_col:
    df["인허가연도"] = pd.to_datetime(
        df[date_col].astype(str),
        errors="coerce"
    ).dt.year
else:
    df["인허가연도"] = None

# -----------------------------
# 지역 선택
# -----------------------------

regions = sorted([
    r for r in df["지역"].unique()
    if r != "주소 미확인"
])

if not regions:
    st.error("주소에서 지역 정보를 찾을 수 없습니다. CSV 주소 열을 확인해 주세요.")
    st.stop()

selected_region = st.sidebar.selectbox(
    "📍 지역 선택",
    regions
)

region_df = df[df["지역"] == selected_region].copy()

# -----------------------------
# 핵심 통계
# -----------------------------

st.subheader(f"📍 {selected_region} 베이커리 현황")

total_count = len(region_df)

if status_col:
    status_text = region_df[status_col].astype(str)
    active_count = status_text.str.contains(
        "영업|정상", case=False, na=False
    ).sum()
else:
    active_count = 0

col1, col2, col3 = st.columns(3)

col1.metric("전체 제과점 수", f"{total_count:,}개")
col2.metric("영업 중인 제과점", f"{active_count:,}개")
col3.metric(
    "비영업 또는 상태 미확인",
    f"{total_count - active_count:,}개"
)

st.divider()

# -----------------------------
# 그래프
# -----------------------------

st.subheader("📊 지역별 베이커리 분포")

region_count = (
    df.groupby("지역")
    .size()
    .reset_index(name="제과점 수")
    .sort_values("제과점 수", ascending=False)
)

fig = px.bar(
    region_count,
    x="지역",
    y="제과점 수",
    title="전국 지역별 제과점 수",
    color="제과점 수",
    text="제과점 수"
)

fig.update_layout(
    xaxis_title="지역",
    yaxis_title="제과점 수",
    xaxis_tickangle=-35
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# 선택 지역 가게 목록
# -----------------------------

st.subheader(f"🏠 {selected_region} 베이커리 목록")

search_word = st.text_input("가게 이름 검색")

if search_word:
    region_df = region_df[
        region_df[name_col].astype(str).str.contains(
            search_word, case=False, na=False
        )
    ]

st.write(f"검색 결과: **{len(region_df):,}개**")

for _, shop in region_df.iterrows():
    shop_name = str(shop[name_col])
    address = str(shop[address_col])

    with st.container(border=True):
        st.markdown(f"### 🥐 {shop_name}")
        st.write(f"📍 주소: {address}")

        if phone_col and pd.notna(shop[phone_col]):
            st.write(f"☎️ 전화번호: {shop[phone_col]}")

        if status_col and pd.notna(shop[status_col]):
            st.write(f"영업상태: {shop[status_col]}")

        if date_col and pd.notna(shop[date_col]):
            st.write(f"인허가일자: {shop[date_col]}")

        # 실제 가게 홈페이지가 아닌 지도 검색 링크
        map_url = (
            "https://map.naver.com/p/search/"
            + quote(shop_name + " " + address)
        )

        st.markdown(f"[🗺️ 지도에서 가게 위치 보기]({map_url})")

if region_df.empty:
    st.info("검색 결과가 없습니다.")

# -----------------------------
# 의사결정나무 분류 알고리즘
# -----------------------------

st.divider()
st.subheader("🌳 의사결정나무를 이용한 영업상태 분류")

st.write(
    "지역과 인허가 연도 데이터를 활용해 "
    "제과점의 영업 여부를 분류하는 모델을 학습합니다."
)

if status_col and date_col:
    model_df = df[["지역", "인허가연도", status_col]].copy()

    model_df["영업분류"] = model_df[status_col].astype(str).apply(
        lambda x: "영업 중"
        if ("영업" in x or "정상" in x) and "폐업" not in x
        else "비영업"
    )

    model_df = model_df.dropna(
        subset=["지역", "인허가연도", "영업분류"]
    )

    class_counts = model_df["영업분류"].value_counts()

    if len(class_counts) == 2 and class_counts.min() >= 2:
        X = model_df[["지역", "인허가연도"]]
        y = model_df["영업분류"]

        preprocessor = ColumnTransformer(
            transformers=[
                (
                    "region",
                    OneHotEncoder(handle_unknown="ignore"),
                    ["지역"]
                ),
                ("year", "passthrough", ["인허가연도"])
            ]
        )

        model = Pipeline([
            ("preprocessor", preprocessor),
            ("classifier", DecisionTreeClassifier(
                max_depth=4,
                random_state=42
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
            predictions = model.predict(X_test)

            accuracy = accuracy_score(y_test, predictions)

            st.metric(
                "분류 모델 정확도",
                f"{accuracy * 100:.1f}%"
            )

            st.caption(
                "정확도는 테스트 데이터에 대한 결과이며, "
                "지역과 인허가 연도만으로 영업상태를 예측한 값입니다."
            )

        except ValueError:
            st.info("데이터의 분포가 부족해 모델을 학습하기 어렵습니다.")
    else:
        st.info("영업상태 데이터가 충분하지 않아 분류 모델을 학습할 수 없습니다.")
else:
    st.info("CSV에 영업상태명과 인허가일자 열이 있어야 분류 모델을 사용할 수 있습니다.")

# -----------------------------
# 데이터 다운로드
# -----------------------------

st.divider()

csv_data = df.to_csv(index=False).encode("utf-8-sig")

st.download_button(
    label="📥 정리된 데이터 CSV 다운로드",
    data=csv_data,
    file_name="베이커리_지역분석.csv",
    mime="text/csv"
)

st.caption(
    "자료: 행정안전부 전국제과점업소표준데이터. "
    "데이터에 등록된 인허가 정보를 기준으로 분석합니다."
)

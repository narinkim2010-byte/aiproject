
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 페이지 설정
st.set_page_config(
    page_title="월별 기온분석",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 월별 기온분석")
st.write("원하는 월을 선택하면 연도별 최고기온과 최저기온을 확인할 수 있습니다.")

# CSV 파일 불러오기 및 한글 인코딩 처리
@st.cache_data
def load_data():
    encodings = ["utf-8-sig", "cp949", "euc-kr", "utf-8"]

    for encoding in encodings:
        try:
            data = pd.read_csv(
                "temperature.csv",
                encoding=encoding
            )
            return data
        except UnicodeDecodeError:
            continue

    st.error("CSV 파일의 인코딩을 확인해주세요.")
    st.stop()

df = load_data()

# 날짜에서 연도와 월 추출
df["일시"] = pd.to_datetime(
    df["일시"],
    format="%b-%y",
    errors="coerce"
)

df["연도"] = df["일시"].dt.year
df["월"] = df["일시"].dt.month

# 기온 데이터 숫자형으로 변환
df["최고기온(℃)"] = pd.to_numeric(
    df["최고기온(℃)"], errors="coerce"
)

df["최저기온(℃)"] = pd.to_numeric(
    df["최저기온(℃)"], errors="coerce"
)

# 월 선택
month_names = {
    1: "1월", 2: "2월", 3: "3월",
    4: "4월", 5: "5월", 6: "6월",
    7: "7월", 8: "8월", 9: "9월",
    10: "10월", 11: "11월", 12: "12월"
}

selected_month = st.selectbox(
    "📅 분석할 월을 선택하세요.",
    options=list(month_names.keys()),
    format_func=lambda x: month_names[x]
)

# 선택한 월의 데이터 추출
filtered_df = df[df["월"] == selected_month].copy()

# 연도별 최고기온과 최저기온 계산
yearly_temp = filtered_df.groupby("연도").agg({
    "최고기온(℃)": "max",
    "최저기온(℃)": "min"
}).reset_index()

# 연도순 정렬
yearly_temp = yearly_temp.sort_values("연도")

# 그래프 출력
if not yearly_temp.empty:

    fig = go.Figure()

    # 최고기온 그래프
    fig.add_trace(go.Scatter(
        x=yearly_temp["연도"],
        y=yearly_temp["최고기온(℃)"],
        mode="lines+markers",
        name="최고기온",
        line=dict(color="hotpink", width=3),
        marker=dict(size=8)
    ))

    # 최저기온 그래프
    fig.add_trace(go.Scatter(
        x=yearly_temp["연도"],
        y=yearly_temp["최저기온(℃)"],
        mode="lines+markers",
        name="최저기온",
        line=dict(color="skyblue", width=3),
        marker=dict(size=8)
    ))

    # 그래프 제목 및 축 설정
    fig.update_layout(
        title="월별 기온분석",
        xaxis_title="연도",
        yaxis_title="온도 (℃)",
        legend_title="기온 구분",
        template="plotly_white",
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)

    # 데이터 표
    st.subheader("📊 연도별 기온 데이터")
    st.dataframe(yearly_temp, use_container_width=True)

else:
    st.warning("선택한 월에 해당하는 데이터가 없습니다.")

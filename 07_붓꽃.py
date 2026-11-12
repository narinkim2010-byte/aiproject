프로젝트 폴더
 ├── app.py
 ├── Iris.csv
 └── requirements.txt

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from matplotlib.colors import ListedColormap

# 페이지 설정
st.set_page_config(
    page_title="붓꽃 품종 예측",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 붓꽃 품종 예측 프로그램")
st.write("꽃잎의 길이와 너비를 입력하면 붓꽃의 품종을 예측합니다.")

# 데이터 불러오기
@st.cache_data
def load_data():
    try:
        return pd.read_csv("Iris.csv", encoding="cp949")
    except UnicodeDecodeError:
        return pd.read_csv("Iris.csv", encoding="utf-8-sig")

df = load_data()

# 사용할 데이터 선택
X = df[["꽃잎너비", "꽃잎길이"]]
y = df["품종"]

# 랜덤 포레스트 모델 생성
model = RandomForestClassifier(
    n_estimators=200,
    random_state=42
)

model.fit(X, y)

# 품종별 색상
colors = {
    "Iris-setosa": "#3498DB",
    "Iris-versicolor": "#F39C12",
    "Iris-virginica": "#E74C3C"
}

# 입력 영역
st.subheader("🔍 꽃잎 크기 입력")

col1, col2 = st.columns(2)

with col1:
    petal_width = st.number_input(
        "꽃잎 너비 (cm)",
        min_value=0.0,
        max_value=5.0,
        value=0.3,
        step=0.1
    )

with col2:
    petal_length = st.number_input(
        "꽃잎 길이 (cm)",
        min_value=0.0,
        max_value=10.0,
        value=1.5,
        step=0.1
    )

# 예측 버튼
if st.button("🌸 품종 예측하기", type="primary"):

    # 입력값으로 예측
    input_data = pd.DataFrame(
        [[petal_width, petal_length]],
        columns=["꽃잎너비", "꽃잎길이"]
    )

    prediction = model.predict(input_data)[0]
    probabilities = model.predict_proba(input_data)[0]

    st.divider()

    # 예측 결과
    st.subheader("🎯 예측 결과")

    st.success(f"예측된 붓꽃 품종: {prediction}")

    st.write(
        f"꽃잎 너비: {petal_width} cm"
    )
    st.write(
        f"꽃잎 길이: {petal_length} cm"
    )

    # 확률 표시
    st.subheader("📊 품종별 예측 확률")

    prob_df = pd.DataFrame({
        "품종": model.classes_,
        "예측 확률": probabilities
    })

    st.bar_chart(
        prob_df.set_index("품종")
    )

    for name, prob in zip(model.classes_, probabilities):
        st.write(f"{name}: {prob * 100:.1f}%")

    st.divider()

    # 그래프 영역
    st.subheader("📈 붓꽃 품종 분류 시각화")

    # 그래프 범위 설정
    x_min = min(0, X["꽃잎너비"].min() - 0.5)
    x_max = max(3.0, X["꽃잎너비"].max() + 0.5)
    y_min = min(0, X["꽃잎길이"].min() - 0.5)
    y_max = max(8.0, X["꽃잎길이"].max() + 0.5)

    xx, yy = np.meshgrid(
        np.arange(x_min, x_max, 0.02),
        np.arange(y_min, y_max, 0.02)
    )

    # 모든 좌표의 품종 예측
    grid = pd.DataFrame({
        "꽃잎너비": xx.ravel(),
        "꽃잎길이": yy.ravel()
    })

    Z = model.predict(grid)
    
    # 품종을 숫자로 변환
    class_to_num = {
        name: i for i, name in enumerate(model.classes_)
    }

    Z_num = np.array(
        [class_to_num[name] for name in Z]
    ).reshape(xx.shape)

    # 그래프 생성
    fig, ax = plt.subplots(figsize=(10, 7))

    cmap_bg = ListedColormap([
        "#DCEEFF",
        "#FFF0D5",
        "#FADBD8"
    ])

    # 분류 영역 표시
    ax.contourf(
        xx, yy, Z_num,
        alpha=0.35,
        cmap=cmap_bg
    )

    # 기존 데이터 표시
    for species in model.classes_:
        subset = df[df["품종"] == species]

        ax.scatter(
            subset["꽃잎너비"],
            subset["꽃잎길이"],
            c=colors[species],
            label=species,
            s=45,
            alpha=0.8,
            edgecolors="black",
            linewidths=0.3
        )

    # 사용자가 입력한 값 표시
    ax.scatter(
        petal_width,
        petal_length,
        marker="*",
        s=500,
        c="lime",
        edgecolors="black",
        linewidths=1.2,
        label="입력한 데이터",
        zorder=10
    )

    # 입력값 설명
    ax.annotate(
        "입력한 값",
        (petal_width, petal_length),
        xytext=(12, 12),
        textcoords="offset points",
        fontsize=11,
        fontweight="bold"
    )

    ax.set_xlabel("Petal Width (cm)", fontsize=12)
    ax.set_ylabel("Petal Length (cm)", fontsize=12)
    ax.set_title("Iris Species Classification", fontsize=15)

    ax.legend()
    ax.grid(alpha=0.2)

    st.pyplot(fig)
    plt.close(fig)

    # 분류 이유 설명
    st.subheader("💡 왜 이 품종으로 분류되었을까?")

    st.write(
        f"입력한 꽃잎 너비 {petal_width}cm와 "
        f"꽃잎 길이 {petal_length}cm의 위치를 "
        "기존 붓꽃 데이터와 비교했습니다."
    )

    st.write(
        f"그래프에서 초록색 별이 위치한 배경 영역은 "
        f"{prediction}으로 분류되는 영역입니다."
    )

    best_prob = max(probabilities) * 100

    st.info(
        f"랜덤 포레스트의 여러 결정 트리가 투표한 결과 "
        f"{prediction}이 가장 높은 확률인 {best_prob:.1f}%로 "
        "예측되었습니다."
    )

    st.caption(
        "※ 예측 확률은 여러 결정 트리의 투표 비율이며 "
        "실제 품종일 확률을 보장하지는 않습니다."
    )

else:
    st.info("꽃잎의 길이와 너비를 입력한 후 예측 버튼을 눌러주세요.")

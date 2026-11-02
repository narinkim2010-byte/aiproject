
import streamlit as st
import folium
from streamlit_folium import st_folium

# 페이지 설정
st.set_page_config(
    page_title="서울 관광지 TOP 10",
    page_icon="🗺️",
    layout="wide"
)

# 제목
st.title("🗺️ 외국인이 좋아하는 서울 관광지 TOP 10")
st.write("서울의 대표적인 관광 명소 10곳을 지도에서 확인해 보세요!")

# 관광지 데이터
places = [
    {
        "name": "경복궁",
        "lat": 37.5796,
        "lon": 126.9770,
        "category": "역사·문화",
        "desc": "조선 왕조의 대표 궁궐입니다. 아름다운 전통 건축물과 한국의 역사를 경험할 수 있습니다."
    },
    {
        "name": "명동",
        "lat": 37.5636,
        "lon": 126.9869,
        "category": "쇼핑·먹거리",
        "desc": "화장품과 패션 매장이 많으며 다양한 길거리 음식을 즐길 수 있는 쇼핑 명소입니다."
    },
    {
        "name": "남산서울타워",
        "lat": 37.5512,
        "lon": 126.9882,
        "category": "전망·랜드마크",
        "desc": "서울의 아름다운 전경과 야경을 감상할 수 있는 대표적인 관광 명소입니다."
    },
    {
        "name": "북촌한옥마을",
        "lat": 37.5826,
        "lon": 126.9830,
        "category": "전통·문화",
        "desc": "전통 한옥이 모여 있는 마을로 한국의 옛 주거 문화를 느낄 수 있습니다."
    },
    {
        "name": "인사동",
        "lat": 37.5710,
        "lon": 126.9850,
        "category": "전통·예술",
        "desc": "전통 공예품과 갤러리, 전통 찻집 등을 경험할 수 있는 문화 거리입니다."
    },
    {
        "name": "홍대거리",
        "lat": 37.5563,
        "lon": 126.9236,
        "category": "문화·엔터테인먼트",
        "desc": "개성 있는 카페와 상점, 거리 공연 등을 즐길 수 있는 활기찬 거리입니다."
    },
    {
        "name": "동대문디자인플라자",
        "lat": 37.5671,
        "lon": 127.0095,
        "category": "건축·전시",
        "desc": "독특한 건축 디자인이 특징이며 다양한 전시와 디자인 행사가 열리는 공간입니다."
    },
    {
        "name": "청계천",
        "lat": 37.5692,
        "lon": 126.9788,
        "category": "산책·휴식",
        "desc": "서울 도심을 흐르는 하천으로 산책과 휴식을 즐기기 좋은 장소입니다."
    },
    {
        "name": "롯데월드",
        "lat": 37.5111,
        "lon": 127.0982,
        "category": "테마파크",
        "desc": "다양한 놀이기구와 퍼레이드를 즐길 수 있는 대형 테마파크입니다."
    },
    {
        "name": "코엑스·별마당도서관",
        "lat": 37.5116,
        "lon": 127.0592,
        "category": "쇼핑·문화",
        "desc": "대형 쇼핑 공간과 독특한 책장으로 유명한 별마당도서관이 있는 명소입니다."
    }
]

# 서울 중심으로 지도 생성
m = folium.Map(
    location=[37.5665, 126.9780],
    zoom_start=11,
    tiles="OpenStreetMap"
)

# 지도에 관광지 마커 표시
for idx, place in enumerate(places, start=1):

    popup_text = f"""
    <b>{idx}. {place['name']}</b><br>
    <small>{place['category']}</small><br>
    {place['desc']}
    """

    folium.Marker(
        location=[place["lat"], place["lon"]],
        tooltip=f"{idx}. {place['name']}",
        popup=folium.Popup(
            popup_text,
            max_width=260
        ),
        icon=folium.DivIcon(
            html=f"""
            <div style="
                background-color:#e63946;
                color:white;
                border:2px solid white;
                border-radius:50%;
                width:28px;
                height:28px;
                text-align:center;
                line-height:24px;
                font-weight:bold;
                font-size:13px;
                box-shadow:0 1px 4px #555;">
                {idx}
            </div>
            """
        )
    ).add_to(m)

# 지도 출력
st.subheader("📍 서울 관광지 위치")

st_folium(
    m,
    use_container_width=True,
    height=560,
    returned_objects=[]
)

# 지도 아래 관광지 설명
st.subheader("✨ 서울 관광지 TOP 10 소개")

# 두 개의 열로 관광지 배치
col1, col2 = st.columns(2)

for i, place in enumerate(places):

    if i % 2 == 0:
        with col1:
            st.markdown(
                f"### {i+1}. {place['name']}"
            )
            st.caption(place["category"])
            st.write(place["desc"])
            st.divider()

    else:
        with col2:
            st.markdown(
                f"### {i+1}. {place['name']}"
            )
            st.caption(place["category"])
            st.write(place["desc"])
            st.divider()

# 하단 안내
st.info(
    "이 목록은 외국인 관광객에게 잘 알려진 "
    "서울의 대표 관광 명소를 선정한 예시입니다."
)

st.caption(
    "지도 출처: OpenStreetMap | 관광지 좌표는 대표 지점 기준입니다."
)

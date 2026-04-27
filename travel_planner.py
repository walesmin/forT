import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="7인팟 여행 플래너", layout="wide")
st.title("🗺️ 7인팟 1박 2일 여행 플래너")

# 1. 7명 멤버의 초기 출발지 데이터 (위도/경도)
# 구글 맵스에서 우클릭하면 위도, 경도를 쉽게 복사할 수 있습니다.
initial_members = [
    {"이름": "첫째형", "위도": 37.5665, "경도": 126.9780},  # 서울시청
    {"이름": "둘째형", "위도": 37.3943, "경도": 127.1114},  # 판교
    {"이름": "셋째형", "위도": 37.4563, "경도": 126.7052},  # 인천
    {"이름": "넷째형", "위도": 37.2636, "경도": 127.0286},  # 수원
    {"이름": "다섯째", "위도": 37.6584, "경도": 126.8320},  # 일산
    {"이름": "여섯째", "위도": 37.5326, "경도": 127.0246},  # 한남동
    {"이름": "막내", "위도": 37.6688, "경도": 127.0471},    # 도봉구
]

# 2. 추천 여행지 데이터
destinations = [
    {"장소명": "가평 빠지촌", "위도": 37.8315, "경도": 127.5095},
    {"장소명": "강릉 안목해변", "위도": 37.7714, "경도": 128.9458},
    {"장소명": "태안 꽃지해수욕장", "위도": 36.5002, "경도": 126.3353},
    {"장소명": "단양 패러글라이딩", "위도": 36.9845, "경도": 128.3655}
]

# UI 레이아웃 분할
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("🚗 멤버 출발지 설정")
    st.write("표의 데이터를 더블 클릭하여 직접 수정할 수 있습니다.")
    # Streamlit의 데이터 에디터를 통해 웹에서 바로 위경도 수정 가능
    df_members = st.data_editor(pd.DataFrame(initial_members), num_rows="dynamic")
    
    # 중앙 지점 계산 (위도 경도의 평균)
    center_lat = df_members["위도"].mean()
    center_lng = df_members["경도"].mean()
    
    st.success(f"📍 **우리들의 중간 지점**\n\n위도: {center_lat:.4f}, 경도: {center_lng:.4f}")

    st.subheader("🛣️ 여행지 길찾기 (중간 지점 출발)")
    st.write("버튼을 누르면 카카오맵 자동차 길찾기로 연결됩니다.")
    for dest in destinations:
        # 카카오맵 목적지 링크 생성
        url = f"https://map.kakao.com/link/to/{dest['장소명']},{dest['위도']},{dest['경도']}"
        st.markdown(f"- **{dest['장소명']}**: [자동차 경로 확인하기]({url})")

with col2:
    st.subheader("🗺️ 한눈에 보는 동선 지도")
    
    # 지도 객체 생성 (중앙 지점 기준)
    m = folium.Map(location=[center_lat, center_lng], zoom_start=9)
    
    # 멤버 마커 추가 (빨간색)
    for idx, row in df_members.iterrows():
        folium.Marker(
            [row["위도"], row["경도"]],
            popup=row["이름"],
            tooltip=f"{row['이름']}의 집",
            icon=folium.Icon(color="red", icon="user")
        ).add_to(m)
        
    # 중앙 지점 마커 추가 (별 모양)
    folium.Marker(
        [center_lat, center_lng],
        popup="🔥 중간 지점",
        tooltip="모두의 중간 지점",
        icon=folium.Icon(color="purple", icon="star")
    ).add_to(m)

    # 추천 여행지 마커 추가 (파란색)
    for dest in destinations:
        folium.Marker(
            [dest["위도"], dest["경도"]],
            popup=dest["장소명"],
            tooltip=f"추천: {dest['장소명']}",
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(m)

    # 지도를 웹 페이지에 렌더링
    st_folium(m, width=800, height=600)
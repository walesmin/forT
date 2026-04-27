import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import os

# 페이지 설정
st.set_page_config(page_title="7인팟 여행 플래너", layout="wide")
st.title("🗺️ 7인팟 1박 2일 여행 플래너")

# 데이터를 저장할 파일 이름 지정 (이게 공용 칠판 역할을 합니다)
DATA_FILE = "shared_locations.csv"

# 1. 초기 출발지 데이터
initial_members = [
    {"이름": "첫째형", "위도": 37.5665, "경도": 126.9780},
    {"이름": "둘째형", "위도": 37.3943, "경도": 127.1114},
    {"이름": "셋째형", "위도": 37.4563, "경도": 126.7052},
    {"이름": "넷째형", "위도": 37.2636, "경도": 127.0286},
    {"이름": "다섯째", "위도": 37.6584, "경도": 126.8320},
    {"이름": "여섯째", "위도": 37.5326, "경도": 127.0246},
    {"이름": "막내", "위도": 37.6688, "경도": 127.0471},
]

# 서버에 파일이 없으면 처음에 한 번 만들어줌
if not os.path.exists(DATA_FILE):
    pd.DataFrame(initial_members).to_csv(DATA_FILE, index=False)

# 2. 파일에서 현재 저장된 데이터 불러오기
df_members = pd.read_csv(DATA_FILE)

# 3. 추천 여행지 데이터
destinations = [
    {"장소명": "가평 빠지촌", "위도": 37.8315, "경도": 127.5095},
    {"장소명": "강릉 안목해변", "위도": 37.7714, "경도": 128.9458},
    {"장소명": "태안 꽃지해수욕장", "위도": 36.5002, "경도": 126.3353},
    {"장소명": "단양 패러글라이딩", "위도": 36.9845, "경도": 128.3655}
]

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("🚗 멤버 출발지 설정")
    st.write("수정한 뒤 반드시 아래 **[저장하기]** 버튼을 눌러야 모두에게 반영됩니다!")
    
    # 웹에서 표를 수정할 수 있게 하고, 수정한 결과를 edited_df에 담음
    edited_df = st.data_editor(df_members, num_rows="dynamic")
    
    # 💡 공유 칠판에 업데이트하는 버튼
    if st.button("💾 수정한 위치 모두에게 저장하기", type="primary"):
        edited_df.to_csv(DATA_FILE, index=False)
        st.success("✅ 저장 완료! 이제 새로고침해도 안 날아갑니다. (다른 형들도 새로고침하면 바뀐 위치가 보입니다)")
        st.rerun() # 화면 새로고침

    center_lat = edited_df["위도"].mean()
    center_lng = edited_df["경도"].mean()
    
    st.success(f"📍 **우리들의 중간 지점**\n\n위도: {center_lat:.4f}, 경도: {center_lng:.4f}")

    st.subheader("🛣️ 여행지 길찾기 (중간 지점 출발)")
    for dest in destinations:
        url = f"https://map.kakao.com/link/to/{dest['장소명']},{dest['위도']},{dest['경도']}"
        st.markdown(f"- **{dest['장소명']}**: [카카오맵 경로 보기]({url})")

with col2:
    st.subheader("🗺️ 한눈에 보는 동선 지도")
    
    m = folium.Map(location=[center_lat, center_lng], zoom_start=9)
    
    for idx, row in edited_df.iterrows():
        folium.Marker(
            [row["위도"], row["경도"]],
            popup=row["이름"],
            tooltip=f"{row['이름']}의 집",
            icon=folium.Icon(color="red", icon="user")
        ).add_to(m)
        
    folium.Marker(
        [center_lat, center_lng],
        popup="🔥 중간 지점",
        tooltip="모두의 중간 지점",
        icon=folium.Icon(color="purple", icon="star")
    ).add_to(m)

    for dest in destinations:
        folium.Marker(
            [dest["위도"], dest["경도"]],
            popup=dest["장소명"],
            tooltip=f"추천: {dest['장소명']}",
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(m)

    st_folium(m, width=800, height=600)
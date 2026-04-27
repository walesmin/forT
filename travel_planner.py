import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import os
import requests

# 🔐 스트림릿 Secrets에서 카카오 API 키를 가져옵니다.
KAKAO_REST_API_KEY = st.secrets["KAKAO_REST_API_KEY"]

st.set_page_config(page_title="7인팟 여행 플래너", layout="wide")
st.title("🗺️ 7인팟 1박 2일 여행 플래너")

DATA_FILE = "shared_locations.csv"

# 카카오 API로 장소명을 좌표로 변환하는 함수
def get_lat_lng(place_name):
    if not place_name or str(place_name).strip() == "":
        return None, None
    
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"}
    params = {"query": place_name}
    
    try:
        response = requests.get(url, headers=headers, params=params).json()
        if response.get('documents'):
            return float(response['documents'][0]['y']), float(response['documents'][0]['x'])
    except Exception as e:
        st.error(f"주소 검색 오류: {e}")
    return None, None

# 1. 7명의 초기 데이터 설정
initial_members = [
    {"이름": "재진형", "출발지": "서울시청", "위도": 37.5665, "경도": 126.9780},
    {"이름": "진환형", "출발지": "판교역", "위도": 37.3943, "경도": 127.1114},
    {"이름": "승민형", "출발지": "인천시청", "위도": 37.4563, "경도": 126.7052},
    {"이름": "지용형", "출발지": "수원역", "위도": 37.2636, "경도": 127.0286},
    {"이름": "현준형", "출발지": "일산 킨텍스", "위도": 37.6693, "경도": 126.7454},
    {"이름": "동현형", "출발지": "한남동", "위도": 37.5326, "경도": 127.0246},
    {"이름": "경빈", "출발지": "도봉구청", "위도": 37.6688, "경도": 127.0471},
]

# 파일이 없으면 생성
if not os.path.exists(DATA_FILE):
    pd.DataFrame(initial_members).to_csv(DATA_FILE, index=False)

# 현재 데이터 불러오기
df_members = pd.read_csv(DATA_FILE)

# 💡 [핵심 에러 방어 코드] 
# 서버에 있는 파일이 옛날 버전이라서 "출발지" 열이 없다면, 에러 내지 말고 최신 양식으로 덮어씌움
required_columns = ["이름", "출발지", "위도", "경도"]
if not all(col in df_members.columns for col in required_columns):
    df_members = pd.DataFrame(initial_members)
    df_members.to_csv(DATA_FILE, index=False)

# 추천 여행지
destinations = [
    {"장소명": "가평 빠지촌", "위도": 37.8315, "경도": 127.5095},
    {"장소명": "강릉 안목해변", "위도": 37.7714, "경도": 128.9458},
    {"장소명": "태안 꽃지해수욕장", "위도": 36.5002, "경도": 126.3353},
    {"장소명": "단양 패러글라이딩", "위도": 36.9845, "경도": 128.3655}
]

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("🚗 멤버 출발지 설정")
    st.write("각자 **동네 이름**이나 **역 이름**을 적고 아래 버튼을 누르세요!")
    
    # 수정 가능한 표 (이름과 출발지만 노출)
    editable_df = st.data_editor(df_members[["이름", "출발지"]], num_rows="dynamic")
    
    if st.button("📍 주소 검색 및 모두에게 저장", type="primary"):
        with st.spinner('위치를 업데이트하는 중...'):
            new_rows = []
            for idx, row in editable_df.iterrows():
                lat, lng = get_lat_lng(row["출발지"])
                
                if lat and lng:
                    new_rows.append({"이름": row["이름"], "출발지": row["출발지"], "위도": lat, "경도": lng})
                else:
                    # 검색 실패 시 기존 데이터 유지 (안전 장치)
                    try:
                        old_lat = df_members.iloc[idx]["위도"]
                        old_lng = df_members.iloc[idx]["경도"]
                    except IndexError:
                        old_lat, old_lng = 37.5665, 126.9780 # 새로 추가된 사람인데 검색 실패하면 서울시청
                    
                    new_rows.append({"이름": row["이름"], "출발지": row["출발지"], "위도": old_lat, "경도": old_lng})
            
            final_df = pd.DataFrame(new_rows)
            final_df.to_csv(DATA_FILE, index=False)
            st.success("✅ 저장이 완료되었습니다!")
            st.rerun()

    # 중앙 지점 계산
    center_lat = df_members["위도"].mean()
    center_lng = df_members["경도"].mean()
    
    st.info(f"💡 **중간 지점 기준 길찾기**")
    for dest in destinations:
        url = f"https://map.kakao.com/link/to/{dest['장소명']},{dest['위도']},{dest['경도']}"
        st.markdown(f"- [{dest['장소명']} 경로 보기]({url})")

with col2:
    st.subheader("🗺️ 실시간 동선 지도")
    m = folium.Map(location=[center_lat, center_lng], zoom_start=9)
    
    # 멤버 마커 (빨간색)
    for _, row in df_members.iterrows():
        folium.Marker(
            [row["위도"], row["경도"]],
            tooltip=f"{row['이름']} ({row['출발지']})",
            icon=folium.Icon(color="red", icon="user")
        ).add_to(m)
        
    # 중간 지점 마커 (보라색 별)
    folium.Marker(
        [center_lat, center_lng],
        popup="🔥 중간 지점",
        icon=folium.Icon(color="purple", icon="star")
    ).add_to(m)

    # 여행지 마커 (파란색)
    for dest in destinations:
        folium.Marker(
            [dest["위도"], dest["경도"]],
            tooltip=dest["장소명"],
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(m)

    st_folium(m, width=800, height=600)
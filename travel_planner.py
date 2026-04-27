import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import os
import requests
import streamlit.components.v1 as components

# ---------------------------
# ✅ 기본 설정 (무조건 최상단)
# ---------------------------
st.set_page_config(page_title="7인팟 여행 플래너", layout="wide")

# ---------------------------
# 📂 파일 경로
# ---------------------------
DATA_FILE = "shared_locations.csv"
DATE_FILE = "shared_dates.csv"

# 파일 없으면 생성
if not os.path.exists(DATA_FILE):
    initial_members = [
        {"이름": "재진형", "출발지": "서울시청", "위도": 37.5665, "경도": 126.9780},
        {"이름": "진환형", "출발지": "판교역", "위도": 37.3943, "경도": 127.1114},
        {"이름": "승민형", "출발지": "인천시청", "위도": 37.4563, "경도": 126.7052},
        {"이름": "지용형", "출발지": "수원역", "위도": 37.2636, "경도": 127.0286},
        {"이름": "현준형", "출발지": "일산 킨텍스", "위도": 37.6693, "경도": 126.7454},
        {"이름": "동현형", "출발지": "한남동", "위도": 37.5326, "경도": 127.0246},
        {"이름": "경빈", "출발지": "도봉구청", "위도": 37.6688, "경도": 127.0471},
    ]
    pd.DataFrame(initial_members).to_csv(DATA_FILE, index=False)

if not os.path.exists(DATE_FILE):
    pd.DataFrame(columns=["이름", "날짜"]).to_csv(DATE_FILE, index=False)

# 🔐 카카오 API
KAKAO_REST_API_KEY = st.secrets["KAKAO_REST_API_KEY"]

# ---------------------------
# 📌 페이지 선택
# ---------------------------
page = st.sidebar.radio(
    "📌 메뉴",
    ["📅 날짜 조율", "🗺️ 지도 & 출발지"]
)

# =====================================================
# 📅 1페이지 - 날짜 조율
# =====================================================
if page == "📅 날짜 조율":

    st.title("📅 여행 날짜 조율")

    # HTML 달력 유지
    with open("여행.html", "r", encoding="utf-8") as f:
        html_code = f.read()

    components.html(html_code, height=800, scrolling=True)

    st.markdown("---")

    # 공유 입력
    st.subheader("📌 (공유용) 안되는 날짜 입력")

    name = st.text_input("이름")
    dates = st.date_input("안되는 날짜 선택", [])

    if st.button("📌 저장"):
        if name and dates:
            df = pd.read_csv(DATE_FILE)
            new_rows = [{"이름": name, "날짜": str(d)} for d in dates]
            df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
            df.to_csv(DATE_FILE, index=False)
            st.success("✅ 저장 완료")
            st.rerun()

    # 공유 데이터 보기
    df_dates = pd.read_csv(DATE_FILE)

    if not df_dates.empty:
        st.subheader("👥 전체 일정")

        pivot = df_dates.pivot_table(
            index="날짜",
            values="이름",
            aggfunc=lambda x: ", ".join(x)
        )

        st.dataframe(pivot)

# =====================================================
# 🗺️ 2페이지 - 지도 & 출발지
# =====================================================
elif page == "🗺️ 지도 & 출발지":

    st.title("🗺️ 출발지 & 동선 지도")

    # 📍 좌표 변환 함수
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

    # 데이터 불러오기
    df_members = pd.read_csv(DATA_FILE)

    # 추천 여행지
    destinations = [
        {"장소명": "가평 빠지촌", "위도": 37.8315, "경도": 127.5095},
        {"장소명": "강릉 안목해변", "위도": 37.7714, "경도": 128.9458},
        {"장소명": "태안 꽃지해수욕장", "위도": 36.5002, "경도": 126.3353},
        {"장소명": "단양 패러글라이딩", "위도": 36.9845, "경도": 128.3655}
    ]

    col1, col2 = st.columns([1, 2])

    # ---------------------------
    # 🚗 출발지 설정
    # ---------------------------
    with col1:
        st.subheader("🚗 출발지 설정")

        editable_df = st.data_editor(
            df_members[["이름", "출발지"]],
            num_rows="dynamic"
        )

        if st.button("📍 주소 검색 및 저장", type="primary"):
            with st.spinner("위치 업데이트 중..."):
                new_rows = []

                for idx, row in editable_df.iterrows():
                    lat, lng = get_lat_lng(row["출발지"])

                    if lat and lng:
                        new_rows.append({
                            "이름": row["이름"],
                            "출발지": row["출발지"],
                            "위도": lat,
                            "경도": lng
                        })
                    else:
                        old_lat = df_members.iloc[idx]["위도"]
                        old_lng = df_members.iloc[idx]["경도"]

                        new_rows.append({
                            "이름": row["이름"],
                            "출발지": row["출발지"],
                            "위도": old_lat,
                            "경도": old_lng
                        })

                pd.DataFrame(new_rows).to_csv(DATA_FILE, index=False)
                st.success("✅ 저장 완료")
                st.rerun()

    # ---------------------------
    # 🗺️ 지도
    # ---------------------------
    with col2:
        st.subheader("🗺️ 실시간 지도")

        df_members = pd.read_csv(DATA_FILE)  # 🔥 다시 읽기 (핵심)

        center_lat = df_members["위도"].mean()
        center_lng = df_members["경도"].mean()

        m = folium.Map(location=[center_lat, center_lng], zoom_start=9)

        # 멤버
        for _, row in df_members.iterrows():
            folium.Marker(
                [row["위도"], row["경도"]],
                tooltip=f"{row['이름']} ({row['출발지']})",
                icon=folium.Icon(color="red")
            ).add_to(m)

        # 중간지점
        folium.Marker(
            [center_lat, center_lng],
            popup="중간 지점",
            icon=folium.Icon(color="purple")
        ).add_to(m)

        # 여행지
        for dest in destinations:
            folium.Marker(
                [dest["위도"], dest["경도"]],
                tooltip=dest["장소명"],
                icon=folium.Icon(color="blue")
            ).add_to(m)

        st_folium(m, width=800, height=600)

    # 길찾기 링크
    st.markdown("---")
    st.subheader("🚗 추천 여행지 길찾기")

    for dest in destinations:
        url = f"https://map.kakao.com/link/to/{dest['장소명']},{dest['위도']},{dest['경도']}"
        st.markdown(f"- [{dest['장소명']} 경로 보기]({url})")
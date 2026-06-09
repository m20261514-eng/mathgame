import streamlit as st
import random
import time
import json
import base64
import os

# 1. 페이지 기본 설정
st.set_page_config(page_title="수학 게임 대모험 메인", page_icon="🎲", layout="centered")

# 🛠️ [경로 치트키] 현재 파이썬 파일과 '같은 폴더'에 있는 배경 이미지를 강제로 연결합니다.
current_dir = os.path.dirname(__file__)
IMAGE_PATH = os.path.join(current_dir, "main_background.png")

# 이미지를 세션 상태 주입용 Base64로 변환하는 함수
def get_base64_image(img_path):
    try:
        with open(img_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return ""

img_base64 = get_base64_image(IMAGE_PATH)

# --- 💾 핀번호 기반 데이터 저장/로드 유틸리티 ---
DATA_DIR = "student_data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def get_user_filepath(pin):
    return os.path.join(DATA_DIR, f"{pin}.json")

def load_user_data(pin):
    filepath = get_user_filepath(pin)
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("gold", 0), set(data.get("my_collection", []))
    return 0, set()

def save_user_data():
    if "current_pin" in st.session_state and st.session_state.current_pin:
        pin = st.session_state.current_pin
        filepath = get_user_filepath(pin)
        data_to_save = {
            "gold": st.session_state.gold,
            "my_collection": list(st.session_state.my_collection)
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)

# --- 🌟 세션 상태 전역 초기화 ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_pin" not in st.session_state:
    st.session_state.current_pin = ""
if "gold" not in st.session_state:
    st.session_state.gold = 0
if "my_collection" not in st.session_state:
    st.session_state.my_collection = set()

# 2. 게임별 동물 데이터 정의 (총 3종류)
multiply_animals = {
    "일반": ["🐿️ 다람쥐", "🐥 병아리", "🐹 햄스터", "🐰 토끼", "🦔 도치", "🐭 생쥐", "🐱고양이", "🐻곰돌이"],
    "희귀": ["🦊🔥 불꽃여우", "🐱✨ 우주고양이", "🐧❄️ 아기 펭귄", "🐼 푸바오", "🐨 코알라", "🐺 은빛 늑대", "🦫 카피바라", "🐿️🌰 볼빵빵 다람쥐"],
    "전설": ["🐲 황금용", "🌈🦄 레인보우 유니콘", "🦁👑 사자왕", "🏆🐯 위대한 호랑이"]
}

reverse_multiply_animals = {
    "일반": ["🐟 물고기", "🦑 오징어", "🦀 꽃게", "🦞 바닷가재", "🐙 문어", "⭐ 불가사리", "🦪 굴", "🌿 해초" ],
    "희귀": ["🦐 안녕하새우", "🐡 뾰족 복어", "💎🐟 보석 물고기", "🌈🐠 레인보우 열대어"],
    "전설": ["🔱🐳 바다의 신 고래", "💕🐬 분홍 돌고래", "🦈 심해의 메가로돈", "🧜‍♀️ 바다의 인어"]
}

divide_animals = {
    "일반": ["🔩 우주 나사","📡 녹슨 안테나","🔭 소형 망원경","🔧 우주 스패너","🛰️ 낡은 위성", "🚀 꼬마 로켓", "🧀 우주 치즈", "🧪 우주 식량"],
    "희귀": ["🐭 우주 실험쥐","🤖 고장난 로봇","🛸 은하수 순찰 UFO", "👾 픽셀 몬스터"],
    "전설": ["👽 초록 외계인","🐰 달토끼","🧬 돌연변이 우주 슬라임","🌟 반짝이는 초신성"]
}

all_animals = []
for tier in multiply_animals.values(): all_animals.extend(tier)
for tier in reverse_multiply_animals.values(): all_animals.extend(tier)
for tier in divide_animals.values(): all_animals.extend(tier)


# --- 🌌 어두운 네이비 & 새벽빛 테마 CSS 스타일링 ---
background_html = f"""
<div class="custom-lobby-bg"></div>
<div class="dawn-particles-bg">
    <div class="aurora-lights"></div>
</div>

<style>
/* 🎯 [투명 박스 완전 격리] 마크다운과 그 바깥 감싸는 Streamlit 컨테이너들의 선/배경을 원천 차단합니다 */
div[data-testid="stMarkdownContainer"], 
div[data-testid="element-container"],
div[data-style="stBlock"],
.stMarkdown {{
    border: none !important;
    background: transparent !important;
    background-color: transparent !important;
    box-shadow: none !important;
}}

/* 1. 배경화면 고정 레이어 (복구 상태 유지) */
.custom-lobby-bg {{
    position: fixed;
    top: -10px; left: -10px; 
    width: calc(100vw + 20px); 
    height: calc(100vh + 20px);
    background-image: url("data:image/png;base64,{img_base64}") !important;
    background-repeat: no-repeat !important;
    background-position: center center !important;
    background-size: cover !important;
    filter: blur(4px) brightness(0.45) contrast(1.1); 
    z-index: -3; 
    pointer-events: none;
}}

/* 2. Streamlit 기본 컴포넌트 투명화 */
.stApp, 
section.main,
[data-testid="stAppViewContainer"], 
[data-testid="stHeader"], 
[data-testid="stMainViewContainer"], 
[data-testid="stMain"],
[data-testid="stDecoration"] {{
    background-color: transparent !important;
    background: transparent !important;
    color: #E2E8F0 !important;
}}

/* 3. 새벽 차원의 빛무리 반짝이 효과 */
.dawn-particles-bg {{
    position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
    z-index: -1; pointer-events: none; overflow: hidden;
}}
.aurora-lights {{
    position: absolute; width: 6px; height: 6px; border-radius: 50%;
    background: transparent;
    box-shadow: 
        10vw 40vh rgba(147, 197, 253, 0.4), 50vw 20vh rgba(167, 139, 250, 0.3), 30vw 70vh rgba(255, 255, 255, 0.5), 
        80vw 30vh rgba(147, 197, 253, 0.3), 70vw 80vh rgba(167, 139, 250, 0.4), 90vw 60vh rgba(255, 255, 255, 0.4);
    animation: dawnGlow 20s linear infinite;
}}
@keyframes dawnGlow {{
    0% {{ transform: translateY(5vh); opacity: 0.3; }}
    50% {{ opacity: 0.7; }}
    100% {{ transform: translateY(-95vh); opacity: 0.3; }}
}}

/* 글자 텍스트 크로매틱 에버레이션 (새벽의 차원문 느낌 텍스트 연출) */
@keyframes dimension-shift {{
    0%, 100% {{ text-shadow: -2px 0 rgba(167, 139, 250, 0.8), 2px 0 rgba(147, 197, 253, 0.8), 0 0 15px rgba(0,0,0,0.5); }}
    50% {{ text-shadow: -3px 0 rgba(167, 139, 250, 0.9), 3px 0 rgba(147, 197, 253, 0.9), 0 0 25px rgba(147, 197, 253, 0.4); }}
}}

.main-title {{
    font-size: 7.5vw;
    font-weight: bold; 
    color: #FFFFFF !important; 
    text-align: center;
    margin-bottom: 25px; 
    margin-top: 10px; 
    letter-spacing: 2px;
    white-space: nowrap; 
    animation: dimension-shift 2.5s ease-in-out infinite;
    display: inline-block; 
    width: 100%;
}}
@media (min-width: 600px) {{ .main-title {{ font-size: 2.6rem !important; }} }}

.guide-text {{ 
    color: #93C5FD !important; 
    font-weight: bold; 
    text-align: center; 
    font-size: 1.15rem; 
    margin-bottom: 25px;
    line-height: 1.6;
    text-shadow: 1px 1px 4px rgba(0, 0, 0, 0.6);
}}
.guide-text br {{ display: none; }}
@media (max-width: 600px) {{ .guide-text br {{ display: inline !important; }} }}

/* 🔑 로그인 박스 (독립적인 실선 테두리 제공) */
.login-box {{
    background: rgba(15, 23, 42, 0.85) !important;
    padding: 30px;
    border-radius: 25px;
    border: 2px solid #475569 !important;
    box-shadow: 0px 10px 25px rgba(0,0,0,0.5);
    margin-top: 5px;
}}
.login-box h3, .login-box p, div[data-testid="stMarkdownContainer"] p {{
    color: #F8FAFC !important;
}}

/* 🧭 게임 입장 대형 네온 버튼 */
div[data-testid="stButton"] button {{
    display: block !important; width: 100% !important; padding: 14px 0 !important;
    border-radius: 20px !important;
    background: linear-gradient(135deg, #1E1B4B 0%, #0F172A 100%) !important;
    color: #E2E8F0 !important; border: 3px solid #6366F1 !important;
    box-shadow: 0 6px 15px rgba(99, 102, 241, 0.3) !important; 
    transition: 0.15s all ease !important; height: auto !important;
}}
div[data-testid="stButton"] button p {{
    font-size: 18px !important; font-weight: bold !important; color: #FFFFFF !important;
}}
div[data-testid="stButton"] button:hover {{ 
    background: linear-gradient(135deg, #312E81 0%, #1E1B4B 100%) !important; 
    border-color: #818CF8 !important;
    box-shadow: 0 8px 20px rgba(99, 102, 241, 0.5) !important;
    transform: translateY(-2px) !important; 
}}
div[data-testid="stButton"] button:active {{
    transform: translateY(3px) !important;
    box-shadow: 0 2px 5px rgba(99, 102, 241, 0.3) !important;
}}

/* 📊 도감 스타일링 */
.tier-title {{
    font-size: 1.25rem; font-weight: bold; color: #C084FC;
    margin-top: 25px; margin-bottom: 12px; padding-left: 8px; border-left: 5px solid #818CF8;
}}
.animal-card-locked {{
    background: rgba(30, 41, 59, 0.7); border-radius: 15px; padding: 15px 10px; text-align: center;
    border: 2px dashed #475569; color: #64748B; font-size: 0.95rem; opacity: 0.5; margin-bottom: 10px;
}}
.animal-card-unlocked {{
    background: rgba(15, 23, 42, 0.9); border-radius: 15px; padding: 15px 10px; text-align: center;
    border: 2px solid #818CF8; color: #F1F5F9; font-size: 0.95rem; font-weight: bold;
    box-shadow: 0 5px 15px rgba(99, 102, 241, 0.15); margin-bottom: 10px;
}}
.animal-emoji {{ font-size: 2.2rem; display: block; margin-bottom: 5px; }}

/* 입력창 다크 모드 고정 패치 */
div[data-testid="stTextInput"] input {{
    background-color: #0F172A !important;
    color: #F8FAFC !important;
    -webkit-text-fill-color: #F8FAFC !important;
    border: 2px solid #475569 !important;
}}
</style>
"""

if not img_base64:
    st.error("🚨 [파일 인식 실패] 폴더 안에 'main_background.png' 파일이 없는 것 같습니다. 파일명을 확인해 주세요!")

# 배경 및 스타일 적용
st.markdown(background_html, unsafe_allow_html=True)

# 메인 타이틀 출력
st.markdown("<div class='main-title'>🌌 수학 차원 대모험 🧭</div>", unsafe_allow_html=True)

# --- 🔐 로그인 화면 분기 ---
if not st.session_state.logged_in:
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    st.subheader("🔑 새벽의 빛을 따라온 모험가 로그인")
    st.write("나만의 고유 핀번호를 입력하고 새로운 차원의 문을 열어보세요!")
    
    input_pin = st.text_input("숫자 핀번호 입력 (예: 나의 학년 반 번호 + 좋아하는 숫자 등)", type="password", key="pin_input")
    
    if st.button("🚀 차원의 문 입장하기", use_container_width=True):
        if input_pin.strip() == "":
            st.warning("핀번호를 적어주세요!")
        else:
            gold, collection = load_user_data(input_pin.strip())
            st.session_state.gold = gold
            st.session_state.my_collection = collection
            st.session_state.current_pin = input_pin.strip()
            st.session_state.logged_in = True
            st.success(f"🎮 대원 [{input_pin}]호 탐사선 시스템 활성화!")
            time.sleep(1)
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# --- 🏠 로그인 성공 시 게임 로비 로드 ---
else:
    col_user, col_logout = st.columns([2, 1])
    with col_user:
        st.markdown(f"👤 **차원 탐사 대원:** `{st.session_state.current_pin}` 호")
    with col_logout:
        if st.button("🚪 차원 로그아웃", use_container_width=True):
            save_user_data()
            st.session_state.logged_in = False
            st.session_state.current_pin = ""
            st.session_state.gold = 0
            st.session_state.my_collection = set()
            st.rerun()

    st.markdown(f"<h3 style='text-align:center; color:#38BDF8; margin-bottom:5px;'>💰 은하계 보유 자산: {st.session_state.gold} G</h3>", unsafe_allow_html=True)
    
    st.markdown("<div class='guide-text'>차원 전설의 유물을 깨우기 위해<br>수학 차원 게이트로 진입하세요!</div>", unsafe_allow_html=True)

    # 1.곱셈, 2.역곱셈, 3.나눗셈 관문 버튼 배치
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("⚔️ 곱셈 차원", use_container_width=True):
            save_user_data()
            st.switch_page("pages/1_곱셈_게임.py")
    with col2:
        if st.button("🛡️ 역곱셈 차원", use_container_width=True):
            save_user_data()
            st.switch_page("pages/2_역곱셈_게임.py")
    with col3:
        if st.button("🏹 나눗셈 차원", use_container_width=True):
            save_user_data()
            st.switch_page("pages/3_나눗셈_게임.py")

    st.write("---")

    st.markdown("### 🪐 나의 우주 신비 도감")
    st.write(f"📊 **전체 차원 유물 아카이브 수집률:** {len(st.session_state.my_collection)} / {len(all_animals)} 개")

    # 도감 탭 분할 구성
    tab1, tab2, tab3 = st.tabs(["⚔️ 초원 아카이브", "🐬 바다 아카이브", "🛸 우주 아카이브"])

    def draw_zoo_grid(animal_dict):
        for tier, title_list in animal_dict.items():
            st.markdown(f"<div class='tier-title'>{tier} 등급</div>", unsafe_allow_html=True)
            cols = st.columns(4)
            for idx, animal_string in enumerate(title_list):
                col_target = cols[idx % 4]
                
                parts = animal_string.split()
                emoji = parts[0]
                name = " ".join(parts[1:])
                
                if animal_string in st.session_state.my_collection:
                    card_html = f"<div class='animal-card-unlocked'><span class='animal-emoji'>{emoji}</span>{name}</div>"
                else:
                    card_html = f"<div class='animal-card-locked'><span class='animal-emoji' style='filter: grayscale(100%);'>❓</span>🔒 미확인</div>"
                col_target.markdown(card_html, unsafe_allow_html=True)

    with tab1: 
        draw_zoo_grid(multiply_animals)
        
    with tab2:
        draw_zoo_grid(reverse_multiply_animals)
        
    with tab3: 
        draw_zoo_grid(divide_animals)

    st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)

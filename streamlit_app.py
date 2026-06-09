import streamlit as st
import random
import time
import json
import os

# 1. 페이지 기본 설정
st.set_page_config(page_title="수학 게임 대모험 메인", page_icon="🎲", layout="centered")

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

# 2. 동물 데이터 정의
multiply_animals = {
    "일반": ["🐿️ 다람쥐", "🐥 병아리", "🐹 햄스터", "🐰 토끼", "🦔 도치", "🐭 생쥐", "🐱고양이", "🐻곰돌이"],
    "희귀": ["🦊🔥 불꽃여우", "🐱✨ 우주고양이", "🐧❄️ 아기 펭귄", "🐼 푸바오", "🐨 코알라", "🐺 은빛 늑대", "🦫 카피바라", "🐿️🌰 볼빵빵 다람쥐"],
    "전설": ["🐲 황금용", "🌈🦄 레인보우 유니콘", "🦁👑 사자왕", "🏆🐯 위대한 호랑이"]
}

divide_animals = {
    "일반": ["🦋 나비", "🐝 꿀벌", "🐞 무당벌레", "🐌 달팽이", "🐜 개미", "🐟 물고기", "🐸 개구리", "🦀 꽃게"],
    "희귀": ["🦑 오징어징어", "🦐 안녕하새우", "🐡 뾰족 복어", "🐢 조용한 거북이", "🦎 우파루파", "💎🐟 보석 물고기", "🐍스르륵 아기뱀", "🌈🐠 레인보우 열대어"],
    "전설": ["🔱🐳 바다의 신 고래", "👑🐸 개구리 왕자", "🦈 심해의 메가로돈", "🦖 티라노사우루스"]
}

all_animals = []
for tier in multiply_animals.values(): all_animals.extend(tier)
for tier in divide_animals.values(): all_animals.extend(tier)

# CSS 디자인 스타일링
st.markdown("""
    <style>
    .stApp { background-color: #FFFDF0; color: #222222; }
    [data-testid="stAppViewContainer"], [data-testid="stMain"] { background: #FFFDF0; }
    
    @keyframes chromatic-aberration {
        0%, 100% { text-shadow: -2px 0 #FF00FF, 2px 0 #00FFFF, 0 0 20px rgba(0, 0, 0, 0.2); }
        50% { text-shadow: -3px 0 #FF00FF, 3px 0 #00FFFF, 0 0 20px rgba(0, 0, 0, 0.2); }
    }
    
    /* 📱 [모바일 대응 반응형 타이틀 수정] */
    .main-title {
        font-size: 8vw; /* 화면 너비에 맞춰 자동 조절 */
        font-weight: bold; 
        color: #000000; 
        text-align: center;
        margin-bottom: 15px; 
        margin-top: 10px; 
        letter-spacing: 1px;
        white-space: nowrap; 
        animation: chromatic-aberration 2s ease-in-out infinite;
        display: inline-block; 
        width: 100%;
    }
    
    /* 화면이 넓은 PC 모니터용 해상도 가드라인 (일정 크기 이상 커지지 않게 고정) */
    @media (min-width: 600px) {
        .main-title {
            font-size: 2.5rem !important;
        }
    }
    
    .guide-text { color: #156580 !important; font-weight: bold; text-align: center; font-size: 1.1rem; margin-bottom: 25px;}
    
    /* 🛠️ 버튼 글자 크기도 모바일 환경에 깨지지 않도록 적정 선인 22px로 조절 */
    div[data-testid="stButton"] button p {
        font-size: 22px !important;
        font-weight: bold !important;
    }
    
    /* 버튼 배경 및 테두리 설정 */
    div[data-testid="stButton"] button {
        display: block !important; width: 100% !important; padding: 12px 0 !important;
        border-radius: 20px !important;
        background: linear-gradient(90deg, #FFF9C6 0%, #BDF6F6 100%) !important;
        color: #2D2D2D !important; border: 4px solid #FFD93D !important;
        box-shadow: 0 6px 0 #FFD93D55 !important; transition: 0.1s all ease !important; height: auto !important;
    }
    div[data-testid="stButton"] button:hover { background: #FFE77C !important; transform: scale(1.02) !important; }
    
    .tier-title {
        font-size: 1.2rem; font-weight: bold; color: #4A4A4A;
        margin-top: 25px; margin-bottom: 12px; padding-left: 8px; border-left: 5px solid #FFD93D;
    }
    .animal-card-locked {
        background: #F1F3F5; border-radius: 15px; padding: 15px 10px; text-align: center;
        border: 2px dashed #CED4DA; color: #ADB5BD; font-size: 0.95rem; opacity: 0.6; margin-bottom: 10px;
    }
    .animal-card-unlocked {
        background: #FFFFFF; border-radius: 15px; padding: 15px 10px; text-align: center;
        border: 2px solid #FFD93D; color: #2B2D42; font-size: 0.95rem; font-weight: bold;
        box-shadow: 0 5px 10px rgba(0,0,0,0.05); margin-bottom: 10px;
    }
    .animal-emoji { font-size: 2.2rem; display: block; margin-bottom: 5px; }
    
""", unsafe_allow_html=True)

st.markdown("<div class='main-title'>🥚수학 게임 대모험🎲</div>", unsafe_allow_html=True)

# --- 🔐 로그인 화면 분기 ---
if not st.session_state.logged_in:
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    st.subheader("🔑 모험가 로그인")
    st.write("나만의 고유 핀번호를 입력하고 이어서 모험을 시작하세요!")
    
    input_pin = st.text_input("숫자 핀번호 입력 (예: 자기 생일 + 좋아하는 숫자 등)", type="password", key="pin_input")
    
    if st.button("🚀 모험 입장하기", use_container_width=True):
        if input_pin.strip() == "":
            st.warning("핀번호를 적어주세요!")
        else:
            gold, collection = load_user_data(input_pin.strip())
            st.session_state.gold = gold
            st.session_state.my_collection = collection
            st.session_state.current_pin = input_pin.strip()
            st.session_state.logged_in = True
            st.success(f"🎮 모험가 [{input_pin}]님 데이터 로드 완료!")
            time.sleep(1)
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# --- 🏠 로그인 성공 시 게임 로비 로드 ---
else:
    col_user, col_logout = st.columns([2, 1])
    with col_user:
        st.markdown(f"👤 **정보:** `{st.session_state.current_pin}` 번 대원")
    with col_logout:
        if st.button("🚪 로그아웃", use_container_width=True):
            save_user_data()
            st.session_state.logged_in = False
            st.session_state.current_pin = ""
            st.session_state.gold = 0
            st.session_state.my_collection = set()
            st.rerun()

    st.markdown(f"<h3 style='text-align:center; color:#099268; margin-bottom:5px;'>💰 통합 보유 골드: {st.session_state.gold} G</h3>", unsafe_allow_html=True)
    st.markdown("<div class='guide-text'>훈련장에 도전하여 전설의 생물을 부화시킬 골드를 모으세요!</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⚔️ 역곱셈 게임 입장", use_container_width=True):
            save_user_data()
            st.switch_page("pages/1_역곱셈_게임.py")
    with col2:
        if st.button("🏹 나눗셈 게임 입장", use_container_width=True):
            save_user_data()
            st.switch_page("pages/2_나눗셈_게임.py")

    st.write("---")

    st.markdown("### 🦁 나의 신비한 동물 도감")
    st.write(f"📊 **전체 마스터 등급 수집률:** {len(st.session_state.my_collection)} / {len(all_animals)} 마리")

    tab1, tab2 = st.tabs(["🐣 역곱셈 도감", "🤿 나눗셈 도감"])

    def draw_zoo_grid(animal_dict):
        for tier, title_list in animal_dict.items():
            st.markdown(f"<div class='tier-title'>{tier}</div>", unsafe_allow_html=True)
            cols = st.columns(4)
            for idx, animal_string in enumerate(title_list):
                col_target = cols[idx % 4]
                emoji = animal_string.split()[0]
                name = animal_string.split()[-1]
                
                if animal_string in st.session_state.my_collection:
                    card_html = f"<div class='animal-card-unlocked'><span class='animal-emoji'>{emoji}</span>{name}</div>"
                else:
                    card_html = f"<div class='animal-card-locked'><span class='animal-emoji' style='filter: grayscale(100%);'>❓</span>🔒 미획득</div>"
                col_target.markdown(card_html, unsafe_allow_html=True)

    with tab1: draw_zoo_grid(multiply_animals)
    with tab2: draw_zoo_grid(divide_animals)
    st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)

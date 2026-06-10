import streamlit as st
import random
import time
import json
import base64
import os

st.set_page_config(page_title="마법의 숲 곱셈 퀘스트", page_icon="🌿", layout="centered")

# 🛠️ 현재 파이썬 파일과 '같은 폴더'에 있는 이미지를 강제로 연결합니다.
current_dir = os.path.dirname(__file__)
IMAGE_PATH = os.path.join(current_dir, "multiple_background.png")

# 이미지를 세션 상태 주입용 Base64로 변환하는 함수
def get_base64_image(img_path):
    try:
        with open(img_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return ""

img_base64 = get_base64_image(IMAGE_PATH)

# 로그인 체크 분기
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("로그인이 필요합니다. 메인 페이지로 돌아가세요!")
    if st.button("🏠 메인 로비로 이동"): st.switch_page("streamlit_app.py")
    st.stop()

# 데이터 강제 저장 유틸리티
def force_file_save():
    data_to_save = {"gold": st.session_state.gold, "my_collection": list(st.session_state.my_collection)}
    with open(f"student_data/{st.session_state.current_pin}.json", "w", encoding="utf-8") as f:
        json.dump(data_to_save, f, ensure_ascii=False, indent=4)

# 다음 문제 생성 유틸리티
def next_question():
    st.session_state.factor1 = random.randint(2, 9)
    st.session_state.factor2 = random.randint(2, 9)
    st.session_state.target_answer = st.session_state.factor1 * st.session_state.factor2
    st.session_state.inputs = []
    st.session_state.status = "playing" 

# 세션 상태 초기화
if "game_score" not in st.session_state: st.session_state.game_score = 0
if "inputs" not in st.session_state: st.session_state.inputs = []
if "gacha_step" not in st.session_state: st.session_state.gacha_step = "idle"
if "status" not in st.session_state: st.session_state.status = "playing"
if "last_reward" not in st.session_state: st.session_state.last_reward = 0
if "revealed_animal" not in st.session_state: st.session_state.revealed_animal = None
if "factor1" not in st.session_state:
    st.session_state.factor1 = random.randint(2, 9)
    st.session_state.factor2 = random.randint(2, 9)
    st.session_state.target_answer = st.session_state.factor1 * st.session_state.factor2

# 마법의 숲 동물 데이터 세팅
animals_data = {
    "일반": ["🐿️ 다람쥐", "🐥 병아리", "🐹 햄스터", "🐰 토끼", "🦔 도치", "🐭 생쥐", "🐱고양이", "🐻곰돌이"],
    "희귀": ["🦊🔥 불꽃여우", "🐱✨ 우주고양이", "🐧❄️ 아기 펭귄", "🐼 푸바오", "🐨 코알라", "🐺 은빛 늑대", "🦫 카피바라", "🐿️🌰 볼빵빵 다람쥐"],
    "전설": ["🐲 황금용", "🌈🦄 레인보우 유니콘", "🦁👑 사자왕", "🏆🐯 위대한 호랑이"]
}

# 나뭇잎 캡슐 뽑기 로직
def start_gacha():
    if st.session_state.gold >= 100:
        st.session_state.gold -= 100
        st.session_state.gacha_step = "shaking"
        rand = random.random()
        if rand < 0.7: tier = "일반"
        elif rand < 0.95: tier = "희귀"
        else: tier = "전설"
        selected_animal = random.choice(animals_data[tier])
        st.session_state.revealed_animal = (tier, selected_animal)
        st.session_state.my_collection.add(selected_animal)
        force_file_save()
    else:
        st.error("골드가 부족해요 🌿")

# --- ✨ 파스텔 요정숲 테마 디자인 패치 리뉴얼 ---
background_html = f"""
<div class="custom-magic-bg"></div>

<style>
/* 1. 배경화면 고정 레이어 */
.custom-magic-bg {{
    position: fixed;
    top: -10px; left: -10px; 
    width: calc(100vw + 20px); 
    height: calc(100vh + 20px);
    background-image: url("data:image/png;base64,{img_base64}") !important;
    background-repeat: no-repeat !important;
    background-position: center center !important;
    background-size: cover !important;
    filter: blur(6px) brightness(0.5); 
    z-index: -3; 
    pointer-events: none;
}}

/* 2. Streamlit 레이어 투명화 */
.stApp, 
section.main,
[data-testid="stAppViewContainer"], 
[data-testid="stHeader"], 
[data-testid="stMainViewContainer"], 
[data-testid="stMain"],
[data-testid="stDecoration"] {{
    background-color: transparent !important;
    background: transparent !important;
}}

/* 3. 특수효과 컨테이너 */
.magic-forest-bg {{
    position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
    z-index: -1; pointer-events: none; overflow: hidden;
}}

/* 4. 은은한 금빛 반짝이 */
.gold-particles {{
    position: absolute; width: 3px; height: 3px; border-radius: 50%;
    background: transparent;
    box-shadow: 
        10vw 20vh #FFD700, 30vw 40vh #FFDF00, 50vw 80vh #FFF8DC, 
        70vw 10vh #FFD700, 90vw 60vh #FFDF00, 20vw 80vh #FFF8DC,
        40vw 15vh #FFD700, 80vw 35vh #FFDF00, 60vw 90vh #FFF8DC;
    animation: floatUp 20s linear infinite;
    opacity: 0.4; filter: blur(0.5px);
}}
.gold-particles::after {{
    content: ""; position: absolute; top: 100vh; width: 3px; height: 3px;
    background: transparent; box-shadow: inherit;
}}
@keyframes floatUp {{
    0% {{ transform: translateY(0); opacity: 0.5; }}
    50% {{ opacity: 0.2; }}
    100% {{ transform: translateY(-100vh); opacity: 0.5; }}
}}

/* 타이틀 디자인 */
.game-title {{ font-size: 5.2vw; font-weight: bold; color: #E8F5E9; text-shadow: 2px 2px 5px rgba(0,0,0,0.6); margin: 0; white-space: nowrap; }}
@media (min-width: 600px) {{ .game-title {{ font-size: 2.1rem !important; }} }}

[data-testid="stHorizontalBlock"] {{ display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important; width: 100% !important; gap: 8px !important; }}
[data-testid="stHorizontalBlock"] > div {{ flex: 1 1 0% !important; min-width: 0 !important; }}

/* 🧩 문제 상자 디자인 (소프트 파스텔 크림) */
.quiz-box {{ 
    background: rgba(244, 249, 246, 0.96); padding: 25px; border-radius: 25px; text-align: center; 
    font-size: 42px; font-weight: bold; color: #2D4A3E !important; 
    border: 4px solid #A3E4D7; box-shadow: 0px 8px 15px rgba(0,0,0,0.3); margin-bottom: 30px; 
}}

/* 📊 대시보드 (파스텔 세이지그린민트) */
.dashboard {{ 
    background: rgba(220, 239, 233, 0.85); padding: 15px; border-radius: 20px; border: 2.5px solid #74C69D; 
    font-size: 22px; font-weight: bold; color: #1E3A2F !important; display: flex; justify-content: space-between; 
    box-shadow: 0px 4px 10px rgba(0,0,0,0.2); margin-bottom: 15px;
}}

/* 🌿 키패드 및 상점 버튼 (살짝 밝고 화사한 파스텔 민트/세이지) */
div[data-testid="stButton"] button {{ 
    font-size: 28px !important; font-weight: bold !important; border-radius: 18px !important; 
    background-color: #74C69D !important; color: #FFFFFF !important; height: 68px !important; 
    width: 100% !important; border: none !important; box-shadow: 0px 5px 0px #40916C !important; 
    transition: all 0.05s ease-in-out !important;
}}
div[data-testid="stButton"] button p {{
    color: #FFFFFF !important; font-size: 26px !important; font-weight: bold !important;
}}
div[data-testid="stButton"] button:hover {{ 
    background-color: #95D5B2 !important; 
    box-shadow: 0px 5px 0px #52B788 !important;
}}
div[data-testid="stButton"] button:active {{ 
    transform: translateY(4px) !important; 
    box-shadow: 0px 1px 0px #40916C !important; 
}}
div[data-testid="stButton"] button:disabled {{
    background-color: #B7E4C7 !important; color: #E8F5E9 !important; box-shadow: 0px 5px 0px #95D5B2 !important;
    transform: none !important; cursor: not-allowed !important; opacity: 0.85 !important;
}}

/* 🏠 상단 로비 버튼 (차분하고 세련된 다운톤 민트) */
.lobby-btn button {{ 
    background-color: rgba(64, 145, 108, 0.85) !important; color: #FFFFFF !important; height: 45px !important; 
    font-size: 16px !important; box-shadow: 0px 4px 0px #2D6A4F !important; font-weight: bold !important;
}}
.lobby-btn button p {{ font-size: 16px !important; }}
.lobby-btn button:hover {{ background-color: #52B788 !important; }}
.lobby-btn button:active {{ transform: translateY(3px) !important; box-shadow: 0px 1px 0px #2D6A4F !important; }}

/* 가챠 상자 애니메이션 효과 */
@keyframes leaf-vibrate {{ 0% {{ transform: translate(0) rotate(0deg); }} 20% {{ transform: translate(-4px, 4px) rotate(-3deg); }} 40% {{ transform: translate(-4px, -4px) rotate(3deg); }} 60% {{ transform: translate(4px, 4px) rotate(-3deg); }} 80% {{ transform: translate(-4px, -4px) rotate(3deg); }} 100% {{ transform: translate(0) rotate(0deg); }} }}
.capsule-shaking {{ font-size: 150px; text-align: center; display: block; margin: 20px auto; animation: leaf-vibrate 0.14s linear infinite; }}
.reveal-card {{ background: rgba(255,255,255,0.95); border-radius: 30px; padding: 40px; text-align: center; border: 5px solid #74C69D; box-shadow: 0 10px 30px rgba(0,0,0,0.3); margin: 20px 0; }}
.animal-icon {{ font-size: 100px; margin-bottom: 10px; }}
.animal-name {{ font-size: 32px; font-weight: bold; color: #1B4332 !important; }}
</style>

<div class="magic-forest-bg">
    <div class="gold-particles"></div>
</div>
"""

if not img_base64:
    st.error("🚨 [파일 인식 실패] 'pages' 폴더 안에 'multiple_background.png' 파일이 없는 것 같습니다. 철자가 완

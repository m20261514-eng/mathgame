import streamlit as st
import random
import time
import json
import base64
import os

st.set_page_config(page_title="신비한 바다 역곱셈 퀘스트", page_icon="🔱", layout="centered")

# 🛠️ [경로 치트키] 현재 파이썬 파일과 '같은 폴더'에 있는 배경 이미지를 강제로 연결합니다.
current_dir = os.path.dirname(__file__)
IMAGE_PATH = os.path.join(current_dir, "inverse_background.png")

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
    st.session_state.target_product = st.session_state.factor1 * st.session_state.factor2
    st.session_state.inputs = []
    st.session_state.status = "playing"
    st.session_state.is_answered = False
    if "last_reward" in st.session_state:
        del st.session_state.last_reward

# 🛠️ [에러 해결] 세션 상태 초기화 유틸리티 (하나씩 개별 검사하여 빈틈없이 생성)
if "game_score" not in st.session_state: st.session_state.game_score = 0
if "inputs" not in st.session_state: st.session_state.inputs = []
if "status" not in st.session_state: st.session_state.status = "playing"
if "gacha_step" not in st.session_state: st.session_state.gacha_step = "idle"
if "revealed_animal" not in st.session_state: st.session_state.revealed_animal = None
if "is_answered" not in st.session_state: st.session_state.is_answered = False

# 문제용 변수가 하나라도 없으면 통째로 새로 출제
if "target_product" not in st.session_state or "factor1" not in st.session_state or "factor2" not in st.session_state:
    st.session_state.factor1 = random.randint(2, 9)
    st.session_state.factor2 = random.randint(2, 9)
    st.session_state.target_product = st.session_state.factor1 * st.session_state.factor2

# 🦀 바다 & 자연 생물 데이터 세팅
animals_data = {
    "일반": ["🐟 물고기", "🦑 오징어", "🦀 꽃게", "🦞 바닷가재", "🐙 문어", "⭐ 불가사리", "🦪 굴", "🌿 해초" ],
    "희귀": ["🦐 안녕하새우", "🐡 뾰족 복어", "🐢 조용한 거북이", "💎🐟 보석 물고기", "🌈🐠 레인보우 열대어"],
    "전설": ["🔱🐳 바다의 신 고래", "💕🐬 분홍 돌고래", "🦈 심해의 메가로돈", "🧜‍♀️ 바다의 인어"]
}

# 진주 방울 뽑기 로직
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
        st.error("골드가 부족해요! 🔮")

# --- 🌊 신비한 바다 테마 CSS ---
background_html = f"""
<div class="custom-inverse-bg"></div>

<style>
/* 1. 배경화면 고정 레이어 (은은하게 어둡고 블러) */
.custom-inverse-bg {{
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

/* 2. Streamlit 기본 판때기 완벽 투명화 */
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

/* 3. 은은한 심해 물방울 반짝이 효과 */
.magic-particles-bg {{
    position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
    z-index: -1; pointer-events: none; overflow: hidden;
}}
.blue-sparkles {{
    position: absolute; width: 4px; height: 4px; border-radius: 50%;
    background: transparent;
    box-shadow: 
        15vw 25vh rgba(255,255,255,0.6), 35vw 45vh rgba(144,224,239,0.5), 55vw 75vh rgba(255,255,255,0.6), 
        75vw 15vh rgba(144,224,239,0.5), 85vw 55vh rgba(255,255,255,0.6), 25vw 85vh rgba(144,224,239,0.5);
    animation: floatUp 18s linear infinite;
    filter: blur(0.5px);
}}
@keyframes floatUp {{
    0% {{ transform: translateY(0); opacity: 0.5; }}
    50% {{ opacity: 0.2; }}
    100% {{ transform: translateY(-100vh); opacity: 0.5; }}
}}

/* 컴포넌트 스타일 */
.game-title {{ font-size: 5.2vw; font-weight: bold; color: #FFFFFF; text-shadow: 2px 2px 4px rgba(0,0,0,0.8); margin: 0; white-space: nowrap; }}
@media (min-width: 600px) {{ .game-title {{ font-size: 2.1rem !important; }} }}

[data-testid="stHorizontalBlock"] {{ display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important; width: 100% !important; gap: 8px !important; }}
[data-testid="stHorizontalBlock"] > div {{ flex: 1 1 0% !important; min-width: 0 !important; }}

.quiz-box {{ 
    background: rgba(255, 255, 255, 0.95); padding: 25px; border-radius: 25px; text-align: center; 
    font-size: 42px; font-weight: bold; color: #03045E !important; 
    border: 5px solid #00B4D8; box-shadow: 0px 8px 15px rgba(0,0,0,0.4); margin-bottom: 30px; 
}}
.dashboard {{ 
    background: rgba(224, 251, 252, 0.9); padding: 15px; border-radius: 20px; border: 3px solid #0077B6; 
    font-size: 22px; font-weight: bold; color: #03045E !important; display: flex; justify-content: space-between;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.3); margin-bottom: 15px;
}}

@keyframes vibrate {{ 0% {{ transform: translate(0); }} 20% {{ transform: translate(-5px, 5px); }} 40% {{ transform: translate(-5px, -5px); }} 60% {{ transform: translate(5px, 5px); }} 80% {{ transform: translate(-5px, -5px); }} 100% {{ transform: translate(0); }} }}
.pearl-shaking {{ font-size: 150px; text-align: center; display: block; margin: 20px auto; animation: vibrate 0.15s linear infinite; }}
.reveal-card {{ background: rgba(255,255,255,0.95); border-radius: 30px; padding: 40px; text-align: center; border: 5px solid #00B4D8; box-shadow: 0 10px 30px rgba(0,0,0,0.3); margin: 20px 0; }}
.animal-icon {{ font-size: 100px; margin-bottom: 10px; }}
.animal-name {{ font-size: 32px; font-weight: bold; color: #03045E !important; }}

div[data-testid="stButton"] button {{ 
    font-size: 32px !important; font-weight: bold !important; border-radius: 18px !important; 
    background-color: #00B4D8 !important; color: #FFFFFF !important; height: 68px !important; 
    width: 100% !important; border: none !important; box-shadow: 0px 6px 0px #0077B6 !important; 
    transition: all 0.05s ease-in-out !important;
}}
div[data-testid="stButton"] button:hover {{ background-color: #90E0EF !important; color: #03045E !important; }}
div[data-testid="stButton"] button:active {{ transform: translateY(4px) !important; box-shadow: 0px 2px 0px #0077B6 !important; }}
div[data-testid="stButton"] button:disabled {{
    background-color: #90E0EF !important; color: #03045E !important; box-shadow: 0px 6px 0px #0077B6 !important;
    transform: none !important; cursor: not-allowed !important; opacity: 0.85 !important;
}}

.lobby-btn button {{ 
    background-color: rgba(3, 4, 94, 0.9) !important; color: #FFFFFF !important; height: 45px !important; 
    font-size: 17px !important; box-shadow: 0px 4px 0px #000814 !important; font-weight: bold !important;
}}
.lobby-btn button:active {{ transform: translateY(3px) !important; box-shadow: 0px 1px 0px #000814 !important; }}

@media (max-width: 600px) {{
    .lobby-btn button {{ height: 36px !important; font-size: 13px !important; padding: 0px 4px !important; box-shadow: 0px 3px 0px #000814 !important; }}
    .lobby-btn button:active {{ transform: translateY(2px) !important; box-shadow: 0px 1px 0px #000814 !important; }}
}}
</style>

<div class="magic-particles-bg">
    <div class="blue-sparkles"></div>
</div>
"""

if not img_base64:
    st.error("🚨 [파일 인식 실패] 폴더 안에 'inverse_background.png' 파일이 없는 것 같습니다. 철자가 완벽히 똑같은지 다시 확인해 주세요!")

st.markdown(background_html, unsafe_allow_html=True)

# 上단 레이아웃 네비바
cols_nav = st.columns([2.9, 1.1])
with cols_nav[0]: 
    st.markdown("<div style='padding-top: 5px;'><h2 class='game-title'>🔱 신비한 바다 역곱셈</h2></div>", unsafe_allow_html=True)
with cols_nav[1]:
    st.markdown("<div class='lobby-btn'>", unsafe_allow_html=True)
    if st.button("🏠 로비로", use_container_width=True):
        force_file_save()
        st.switch_page("streamlit_app.py")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown(f"<div class='dashboard'><span>⭐ 점수: {st.session_state.game_score}점</span><span>💰 지갑: {st.session_state.gold} G</span></div>", unsafe_allow_html=True)

# 가챠(진주 방울 뽑기) 연출 단계 처리
if st.session_state.gacha_step == "shaking":
    st.markdown("<span class='pearl-shaking'>🔮</span>", unsafe_allow_html=True)
    time.sleep(2.0)
    st.session_state.gacha_step = "revealed"
    st.rerun()
elif st.session_state.gacha_step == "revealed":
    tier, animal = st.session_state.revealed_animal
    st.markdown(f"""
        <div class='reveal-card'>
            <div class='animal-icon'>{animal.split()[0]}</div>
            <div class='animal-name'>[{tier}] {animal.split()[-1]}</div>
        </div>
    """, unsafe_allow_html=True)
    if "전설" in tier: st.balloons()
    
    col_confirm1, col_confirm2 = st.columns(2)
    with col_confirm1:
        if st.button("확인", use_container_width=True):
            st.session_state.gacha_step = "idle"
            force_file_save()
            st.rerun()
    with col_confirm2:
        if st.button("도감 보기", use_container_width=True):
            st.session_state.gacha_step = "idle"
            force_file_save()
            st.switch_page("streamlit_app.py")

# 기본 플레이 화면 UI
if st.session_state.gacha_step == "idle":
    with st.expander("🔮 [진주 방울 뽑기 상점]", expanded=False):
        st.button("🔮 진주 방울 뽑기 시작! (100 G)", on_click=start_gacha, use_container_width=True)

    if st.session_state.status == "hint":
        p1 = f"<span style='color: #E03131; font-weight: 900;'>{st.session_state.factor1}</span>"
        p2 = str(st.session_state.inputs[1]) if len(st.session_state.inputs) >= 2 else " ? "
    else:
        p1 = str(st.session_state.inputs[0]) if len(st.session_state.inputs) >= 1 else " ? "
        p2 = str(st.session_state.inputs[1]) if len(st.session_state.inputs) >= 2 else " ? "
    
    st.markdown(f"<div class='quiz-box'>{st.session_state.target_product} = [ {p1} ] × [ {p2} ]</div>", unsafe_allow_html=True)

    is_keyboard_locked = (st.session_state.status == "correct_waiting") or ("last_reward" in st.session_state)

    key_matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    for row in key_matrix:
        pad_cols = st.columns(3)
        for i, num in enumerate(row):
            if pad_cols[i].button(str(num), key=f"pad_{num}", use_container_width=True, disabled=is_keyboard_locked):
                if len(st.session_state.inputs) < 2:
                    st.session_state.inputs.append(num)
                    st.session_state.is_answered = True
                    st.rerun()

    if st.button("⌫ 지우기", use_container_width=True, disabled=is_keyboard_locked):
        if st.session_state.status == "hint":
            st.session_state.inputs = []
            st.session_state.status = "playing"
        elif len(st.session_state.inputs) > 0:
            st.session_state.inputs.pop()
        st.rerun()

    if "last_reward" in st.session_state:
        st.success(f"💙 정답! 바다의 축복으로 +{st.session_state.last_reward}G 획득!")
        time.sleep(1.5)
        next_question()
        st.rerun()

    if len(st.session_state.inputs) == 2 and st.session_state.is_answered:
        u1, u2 = st.session_state.inputs
        if u1 * u2 == st.session_state.target_product:
            reward = random.randint(8, 13)
            st.session_state.gold += reward
            st.session_state.game_score += 1
            st.session_state.last_reward = reward
            st.session_state.status = "correct_waiting"
            force_file_save()
            st.rerun()
        else:
            st.session_state.status = "hint"
            st.session_state.inputs = [st.session_state.factor1]
            st.session_state.is_answered = False
            st.rerun()

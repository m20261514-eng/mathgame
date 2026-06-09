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

# --- 🌲 [초강력 수정] HTML 직접 삽입 및 무조건 투명화 CSS 🌲 ---
background_html = f"""
<div class="custom-magic-bg"></div>

<style>
/* 1. 배경화면 전용 완전 고정 레이어 (블러 + 어둡게) */
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
    z-index: -3; /* 모든 Streamlit 요소보다 아래에 배치 */
    pointer-events: none;
}}

/* 2. Streamlit의 모든 하얀색 판때기들을 모조리 투명하게 뚫어버림 */
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

/* 3. 흔들리는 나뭇잎 & 금빛 입자 컨테이너 */
.magic-forest-bg {{
    position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
    z-index: -1; pointer-events: none; overflow: hidden;
}}

/* 4. 금빛 반짝이 애니메이션 */
.gold-particles {{
    position: absolute; width: 4px; height: 4px; border-radius: 50%;
    background: transparent;
    box-shadow: 
        10vw 20vh #FFD700, 30vw 40vh #FFDF00, 50vw 80vh #FFF8DC, 
        70vw 10vh #FFD700, 90vw 60vh #FFDF00, 20vw 80vh #FFF8DC,
        40vw 15vh #FFD700, 80vw 35vh #FFDF00, 60vw 90vh #FFF8DC,
        15vw 50vh #FFD700, 85vw 70vh #FFF8DC, 45vw 90vh #FFDF00;
    animation: floatUp 15s linear infinite;
    opacity: 0.6; filter: blur(1px);
}}
.gold-particles::after {{
    content: ""; position: absolute; top: 100vh; width: 4px; height: 4px;
    background: transparent; box-shadow: inherit;
}}
@keyframes floatUp {{
    0% {{ transform: translateY(0); opacity: 0.8; }}
    50% {{ opacity: 0.3; }}
    100% {{ transform: translateY(-100vh); opacity: 0.8; }}
}}

/* 5. 살랑살랑 떨어지는 나뭇잎 애니메이션 */
.leaf {{
    position: absolute; font-size: 24px; animation: swayAndFall linear infinite; opacity: 0.8;
}}
.leaf:nth-child(2) {{ left: 10%; top: -10%; animation-duration: 12s; animation-delay: 0s; }}
.leaf:nth-child(3) {{ left: 30%; top: -10%; animation-duration: 15s; animation-delay: 3s; font-size: 18px; }}
.leaf:nth-child(4) {{ left: 60%; top: -10%; animation-duration: 11s; animation-delay: 1s; font-size: 28px; }}
.leaf:nth-child(5) {{ left: 80%; top: -10%; animation-duration: 16s; animation-delay: 5s; }}
.leaf:nth-child(6) {{ left: 45%; top: -10%; animation-duration: 14s; animation-delay: 7s; font-size: 20px;}}

@keyframes swayAndFall {{
    0% {{ transform: translateY(-10vh) rotate(0deg) translateX(0); }}
    25% {{ transform: translateY(25vh) rotate(45deg) translateX(30px); }}
    50% {{ transform: translateY(50vh) rotate(90deg) translateX(-20px); }}
    75% {{ transform: translateY(75vh) rotate(135deg) translateX(40px); }}
    100% {{ transform: translateY(110vh) rotate(180deg) translateX(-30px); }}
}}

/* 기존 컴포넌트 스타일 유지 */
.game-title {{ font-size: 5.2vw; font-weight: bold; color: #FFFFFF; text-shadow: 2px 2px 4px rgba(0,0,0,0.8); margin: 0; white-space: nowrap; }}
@media (min-width: 600px) {{ .game-title {{ font-size: 2.1rem !important; }} }}

[data-testid="stHorizontalBlock"] {{ display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important; width: 100% !important; gap: 8px !important; }}
[data-testid="stHorizontalBlock"] > div {{ flex: 1 1 0% !important; min-width: 0 !important; }}

.quiz-box {{ 
    background: rgba(255, 255, 255, 0.95); padding: 25px; border-radius: 25px; text-align: center; 
    font-size: 42px; font-weight: bold; color: #1B4332 !important; 
    border: 5px solid #74C69D; box-shadow: 0px 8px 15px rgba(0,0,0,0.4); margin-bottom: 30px; 
}}
.dashboard {{ 
    background: rgba(232, 245, 233, 0.9); padding: 15px; border-radius: 20px; border: 3px solid #2D6A4F; 
    font-size: 22px; font-weight: bold; color: #1B4332 !important; display: flex; justify-content: space-between; 
    box-shadow: 0px 4px 10px rgba(0,0,0,0.3); margin-bottom: 15px;
}}

div[data-testid="stButton"] button {{ 
    font-size: 32px !important; font-weight: bold !important; border-radius: 18px !important; 
    background-color: #40916C !important; color: #FFFFFF !important; height: 68px !important; 
    width: 100% !important; border: none !important; box-shadow: 0px 6px 0px #1B4332 !important; 
    transition: all 0.05s ease-in-out !important;
}}
div[data-testid="stButton"] button:hover {{ background-color: #52B788 !important; }}
div[data-testid="stButton"] button:active {{ transform: translateY(4px) !important; box-shadow: 0px 2px 0px #1B4332 !important; }}
div[data-testid="stButton"] button:disabled {{
    background-color: #74C69D !important; color: #FFFFFF !important; box-shadow: 0px 6px 0px #40916C !important;
    transform: none !important; cursor: not-allowed !important; opacity: 0.85 !important;
}}

.lobby-btn button {{ 
    background-color: rgba(27, 67, 50, 0.9) !important; color: #FFFFFF !important; height: 45px !important; 
    font-size: 17px !important; box-shadow: 0px 4px 0px #081C15 !important; font-weight: bold !important;
}}
.lobby-btn button:active {{ transform: translateY(3px) !important; box-shadow: 0px 1px 0px #081C15 !important; }}

@keyframes leaf-vibrate {{ 0% {{ transform: translate(0) rotate(0deg); }} 20% {{ transform: translate(-4px, 4px) rotate(-3deg); }} 40% {{ transform: translate(-4px, -4px) rotate(3deg); }} 60% {{ transform: translate(4px, 4px) rotate(-3deg); }} 80% {{ transform: translate(-4px, -4px) rotate(3deg); }} 100% {{ transform: translate(0) rotate(0deg); }} }}
.capsule-shaking {{ font-size: 150px; text-align: center; display: block; margin: 20px auto; animation: leaf-vibrate 0.14s linear infinite; }}
.reveal-card {{ background: rgba(255,255,255,0.95); border-radius: 30px; padding: 40px; text-align: center; border: 5px solid #52B788; box-shadow: 0 10px 30px rgba(0,0,0,0.3); margin: 20px 0; }}
.animal-icon {{ font-size: 100px; margin-bottom: 10px; }}
.animal-name {{ font-size: 32px; font-weight: bold; color: #1B4332 !important; }}
</style>

<div class="magic-forest-bg">
    <div class="gold-particles"></div>
    <div class="leaf">🍃</div>
    <div class="leaf">🌿</div>
    <div class="leaf">🍃</div>
    <div class="leaf">🍂</div>
    <div class="leaf">🌿</div>
</div>
"""

# 🛠️ 만약 컴퓨터가 이미지를 아예 못 읽으면 상단에 명확하게 빨간 에러창을 띄워주는 안전장치
if not img_base64:
    st.error("🚨 [파일 인식 실패] 'pages' 폴더 안에 'multiple_background.png' 파일이 없는 것 같습니다. 철자가 완벽히 똑같은지 다시 확인해 주세요!")

st.markdown(background_html, unsafe_allow_html=True)

# 상단 비율 세팅 및 로비 연결
cols_nav = st.columns([2.9, 1.1])
with cols_nav[0]: 
    st.markdown("<div style='padding-top: 5px;'><h2 class='game-title'>🌲 마법의 숲 곱셈 게임</h2></div>", unsafe_allow_html=True)
with cols_nav[1]:
    st.markdown("<div class='lobby-btn'>", unsafe_allow_html=True)
    if st.button("🏠 로비로", use_container_width=True):
        force_file_save()
        st.switch_page("streamlit_app.py")
    st.markdown("</div>", unsafe_allow_html=True)

# 점수판 대시보드
st.markdown(f"<div class='dashboard'><span>⭐ 점수: {st.session_state.game_score}점</span><span>💰 지갑: {st.session_state.gold} G</span></div>", unsafe_allow_html=True)

# 캡슐 뽑기 연출 트리거 분기
if st.session_state.gacha_step == "shaking":
    st.markdown("<span class='capsule-shaking'>🍃</span>", unsafe_allow_html=True)
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
            next_question() 
            force_file_save()
            st.rerun()
    with col_confirm2:
        if st.button("도감 보기", use_container_width=True):
            st.session_state.gacha_step = "idle"
            next_question()
            force_file_save()
            st.switch_page("streamlit_app.py")

# 평상시 게임 플레이 UI 로드
if st.session_state.gacha_step == "idle":
    with st.expander("🍃 [나뭇잎 캡슐 뽑기 상점]", expanded=False):
        st.button("🔮 캡슐 뽑기 시작! (100 G)", on_click=start_gacha, use_container_width=True)

    # 정답 알림 상자를 미리 자리만 잡아둡니다.
    notice_box = st.empty()

    user_input_str = "".join(map(str, st.session_state.inputs)) if st.session_state.inputs else " ? "
    
    # 문제 출제 상자 
    st.markdown(f"<div class='quiz-box'>{st.session_state.factor1} × {st.session_state.factor2} = [ {user_input_str} ]</div>", unsafe_allow_html=True)

    # 정답을 맞힌 상태일 경우 키패드 잠금
    is_locked = (st.session_state.status == "correct_waiting")

    # 1 ~ 9 키패드 
    key_matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    for row in key_matrix:
        pad_cols = st.columns(3)
        for i, num in enumerate(row):
            if pad_cols[i].button(str(num), key=f"pad_{num}", use_container_width=True, disabled=is_locked):
                if len(st.session_state.inputs) < 2:
                    st.session_state.inputs.append(num)
                    st.rerun()

    last_row_cols = st.columns(3)
    
    if last_row_cols[0].button("⌫", key="pad_del", use_container_width=True, disabled=is_locked):
        if len(st.session_state.inputs) > 0:
            st.session_state.inputs.pop()
            st.rerun()
            
    if last_row_cols[1].button("0", key="pad_0", use_container_width=True, disabled=is_locked):
        if len(st.session_state.inputs) < 2:
            st.session_state.inputs.append(0)
            st.rerun()
            
    if last_row_cols[2].button("확인", key="pad_enter", use_container_width=True, disabled=is_locked):
        if st.session_state.inputs:
            user_val = int("".join(map(str, st.session_state.inputs)))
            
            if user_val == st.session_state.target_answer:
                reward = random.randint(8, 13)
                st.session_state.gold += reward
                st.session_state.game_score += 1
                st.session_state.last_reward = reward
                st.session_state.status = "correct_waiting" 
                force_file_save()
                st.rerun() 
            else:
                st.session_state.inputs = []
                st.toast("앗! 나뭇잎이 흔들려요. 다시 계산해봐요! ❌")
                st.rerun()

    # UI가 모두 그려진 후, 상태를 확인하여 1.5초 대기하고 새 문제로 넘깁니다.
    if st.session_state.status == "correct_waiting":
        notice_box.success(f"🎉 정답입니다! 마법 나무가 +{st.session_state.last_reward}G 보상을 떨어뜨렸습니다!")
        time.sleep(1.5)
        next_question()
        st.rerun()

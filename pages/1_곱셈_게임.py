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
    st.session_state.is_locked = False # 🔒 새 문제가 나오면 키보드 잠금 해제

# 세션 상태 초기화
if "game_score" not in st.session_state: st.session_state.game_score = 0
if "inputs" not in st.session_state: st.session_state.inputs = []
if "gacha_step" not in st.session_state: st.session_state.gacha_step = "idle"
if "status" not in st.session_state: st.session_state.status = "playing"
if "last_reward" not in st.session_state: st.session_state.last_reward = 0
if "is_locked" not in st.session_state: st.session_state.is_locked = False
if "revealed_animal" not in st.session_state: st.session_state.revealed_animal = None
if "factor1" not in st.session_state:
    next_question()

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

# 🎯 키패드 버튼 클릭 콜백 함수
def press_key(num):
    if not st.session_state.is_locked and len(st.session_state.inputs) < 2:
        st.session_state.inputs.append(num)

def press_del():
    if not st.session_state.is_locked and len(st.session_state.inputs) > 0:
        st.session_state.inputs.pop()

# --- ✨ 파스텔 요정숲 테마 디자인 패치 리뉴얼 ---
background_html = f"""
<div class="custom-magic-bg"></div>

<style>
/* 배경 및 기본 설정 */
.custom-magic-bg {{ position: fixed; top: -10px; left: -10px; width: calc(100vw + 20px); height: calc(100vh + 20px); background-image: url("data:image/png;base64,{img_base64}") !important; background-repeat: no-repeat !important; background-position: center center !important; background-size: cover !important; filter: blur(6px) brightness(0.5); z-index: -3; pointer-events: none; }}
.stApp, section.main, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stMainViewContainer"], [data-testid="stMain"], [data-testid="stDecoration"] {{ background-color: transparent !important; background: transparent !important; }}
.magic-forest-bg {{ position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: -1; pointer-events: none; overflow: hidden; }}
.gold-particles {{ position: absolute; width: 3px; height: 3px; border-radius: 50%; background: transparent; box-shadow: 10vw 20vh #FFD700, 30vw 40vh #FFDF00, 50vw 80vh #FFF8DC, 70vw 10vh #FFD700, 90vw 60vh #FFDF00, 20vw 80vh #FFF8DC, 40vw 15vh #FFD700, 80vw 35vh #FFDF00, 60vw 90vh #FFF8DC; animation: floatUp 20s linear infinite; opacity: 0.4; filter: blur(0.5px); }}
.gold-particles::after {{ content: ""; position: absolute; top: 100vh; width: 3px; height: 3px; background: transparent; box-shadow: inherit; }}
@keyframes floatUp {{ 0% {{ transform: translateY(0); opacity: 0.5; }} 50% {{ opacity: 0.2; }} 100% {{ transform: translateY(-100vh); opacity: 0.5; }} }}

/* 타이틀 디자인 */
.game-title {{ font-size: 5.2vw; font-weight: bold; color: #E8F5E9; text-shadow: 2px 2px 5px rgba(0,0,0,0.6); margin: 0; white-space: nowrap; }}
@media (min-width: 600px) {{ .game-title {{ font-size: 2.1rem !important; }} }}
[data-testid="stHorizontalBlock"] {{ display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important; width: 100% !important; gap: 8px !important; }}
[data-testid="stHorizontalBlock"] > div {{ flex: 1 1 0% !important; min-width: 0 !important; }}

/* 🧩 문제 상자 디자인 */
.quiz-box {{ background: rgba(244, 249, 246, 0.96); padding: 25px; border-radius: 25px; text-align: center; font-size: 42px; font-weight: bold; color: #2D4A3E !important; border: 4px solid #A3E4D7; box-shadow: 0px 8px 15px rgba(0,0,0,0.3); margin-bottom: 30px; }}

/* 📊 대시보드 */
.dashboard {{ background: rgba(220, 239, 233, 0.85); padding: 15px; border-radius: 20px; border: 2.5px solid #74C69D; font-size: 22px; font-weight: bold; color: #1E3A2F !important; display: flex; justify-content: space-between; box-shadow: 0px 4px 10px rgba(0,0,0,0.2); margin-bottom: 15px; }}

/* 🌿 키패드 버튼 디자인 */
div[data-testid="stButton"] button {{ font-size: 28px !important; font-weight: bold !important; border-radius: 18px !important; background-color: #74C69D !important; color: #FFFFFF !important; height: 68px !important; width: 100% !important; border: none !important; box-shadow: 0px 5px 0px #40916C !important; transition: all 0.05s ease-in-out !important; }}
div[data-testid="stButton"] button p {{ color: #FFFFFF !important; font-size: 26px !important; font-weight: bold !important; }}
div[data-testid="stButton"] button:hover {{ background-color: #95D5B2 !important; box-shadow: 0px 5px 0px #52B788 !important; }}
div[data-testid="stButton"] button:active {{ transform: translateY(4px) !important; box-shadow: 0px 1px 0px #40916C !important; }}

/* 🔒 잠긴 버튼(정답 후) 비활성화 디자인 */
div[data-testid="stButton"] button:disabled {{ background-color: #95D5B2 !important; color: #E8F5E9 !important; box-shadow: 0px 5px 0px #74C69D !important; transform: none !important; cursor: not-allowed !important; opacity: 0.6 !important; }}

/* 🏠 상단 로비 버튼 */
.lobby-btn button {{ background-color: rgba(64, 145, 108, 0.85) !important; color: #FFFFFF !important; height: 45px !important; font-size: 16px !important; box-shadow: 0px 4px 0px #2D6A4F !important; font-weight: bold !important; }}
.lobby-btn button p {{ font-size: 16px !important; }}

/* 💬 새로 추가된 피드백 메시지 박스 */
.feedback-success {{ background: rgba(212, 237, 218, 0.95); color: #155724; padding: 15px; border-radius: 15px; text-align: center; font-size: 22px; font-weight: bold; border: 3px solid #A3E4D7; margin-top: 20px; box-shadow: 0px 4px 10px rgba(0,0,0,0.1); }}
.feedback-error {{ background: rgba(248, 215, 218, 0.95); color: #721C24; padding: 15px; border-radius: 15px; text-align: center; font-size: 22px; font-weight: bold; border: 3px solid #F5C6CB; margin-top: 20px; box-shadow: 0px 4px 10px rgba(0,0,0,0.1); }}

/* 가챠 애니메이션 */
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

st.markdown(background_html, unsafe_allow_html=True)

# 상단 로비 연결
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

# 가챠 렌더링
if st.session_state.gacha_step == "shaking":
    st.markdown("<span class='capsule-shaking'>🍃</span>", unsafe_allow_html=True)
    time.sleep(2.0)
    st.session_state.gacha_step = "revealed"
    st.rerun()
elif st.session_state.gacha_step == "revealed":
    tier, animal = st.session_state.revealed_animal
    st.markdown(f"<div class='reveal-card'><div class='animal-icon'>{animal.split()[0]}</div><div class='animal-name'>[{tier}] {animal.split()[-1]}</div></div>", unsafe_allow_html=True)
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

# 평상시 게임 플레이 UI
if st.session_state.gacha_step == "idle":
    with st.expander("🍃 [나뭇잎 캡슐 뽑기 상점]", expanded=False):
        st.button("🔮 캡슐 뽑기 시작! (100 G)", on_click=start_gacha, use_container_width=True)

    # 🎯 정답 판별 로직 (콜백 적용 후, 화면을 그리기 직전에 검사)
    feedback_msg = ""
    feedback_type = ""

    if st.session_state.inputs:
        user_val = int("".join(map(str, st.session_state.inputs)))
        target_str = str(st.session_state.target_answer)

        # 1. 정답일 경우
        if user_val == st.session_state.target_answer:
            if not st.session_state.is_locked: # 🔒 중복 골드 지급 및 클릭 방어망
                reward = random.randint(8, 13)
                st.session_state.gold += reward
                st.session_state.game_score += 1
                st.session_state.last_reward = reward
                force_file_save()
                st.session_state.is_locked = True # 판정 즉시 키보드 잠금
            feedback_msg = f"🎉 정답! 마법 나무가 +{st.session_state.last_reward}G를 줬어요! 🍃"
            feedback_type = "success"

        # 2. 오답일 경우 (자릿수가 정답과 똑같아졌을 때)
        elif len(st.session_state.inputs) == len(target_str):
            if not st.session_state.is_locked:
                st.session_state.is_locked = True # 에러 메시지를 보여주는 동안 키보드 잠금
            feedback_msg = "앗! 나뭇잎이 흔들려요. 다시 계산해봐요! ❌"
            feedback_type = "error"

    # 문제 출제 상자 
    user_input_str = "".join(map(str, st.session_state.inputs)) if st.session_state.inputs else " ? "
    st.markdown(f"<div class='quiz-box'>{st.session_state.factor1} × {st.session_state.factor2} = [ {user_input_str} ]</div>", unsafe_allow_html=True)

    # 1 ~ 9 키패드 렌더링 (disabled 속성으로 잠금 연동)
    key_matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    for row in key_matrix:
        pad_cols = st.columns(3)
        for i, num in enumerate(row):
            pad_cols[i].button(str(num), key=f"pad_{num}", on_click=press_key, args=(num,), use_container_width=True, disabled=st.session_state.is_locked)

    # 0과 지우기 키패드
    last_row_cols = st.columns(3)
    last_row_cols[1].button("0", key="pad_0", on_click=press_key, args=(0,), use_container_width=True, disabled=st.session_state.is_locked)
    last_row_cols[2].button("⌫", key="pad_del", on_click=press_del, use_container_width=True, disabled=st.session_state.is_locked)

    # 💬 피드백 박스 렌더링
    if feedback_msg:
        css_class = "feedback-success" if feedback_type == "success" else "feedback-error"
        st.markdown(f"<div class='{css_class}'>{feedback_msg}</div>", unsafe_allow_html=True)
    else:
        # 화면 깜빡임을 방지하기 위해 빈 공간을 마련해둡니다
        st.markdown("<div style='height: 60px; margin-top: 20px;'></div>", unsafe_allow_html=True)

    # ⏳ 화면을 예쁘게 그려준 뒤 자동으로 넘어가도록 대기 & 리런
    if feedback_type == "success":
        time.sleep(1.2) # 정답 피드백과 잠긴 키보드를 1.2초간 보여줌
        next_question()
        st.rerun()
    elif feedback_type == "error":
        time.sleep(0.8) # 오답 메시지를 0.8초간 보여줌
        st.session_state.inputs = []
        st.session_state.is_locked = False
        st.rerun()

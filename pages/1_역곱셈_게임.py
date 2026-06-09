import streamlit as st
import random
import time
import json

st.set_page_config(page_title="신비의 알 역곱셈 퀘스트", page_icon="🥚", layout="centered")

# 로그인 튕김 방지 안전 가드
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("로그인이 필요합니다. 메인 페이지로 돌아가세요!")
    if st.button("🏠 메인 로비로 이동"): st.switch_page("streamlit_app.py")
    st.stop()

def force_file_save():
    data_to_save = {"gold": st.session_state.gold, "my_collection": list(st.session_state.my_collection)}
    with open(f"student_data/{st.session_state.current_pin}.json", "w", encoding="utf-8") as f:
        json.dump(data_to_save, f, ensure_ascii=False, indent=4)

def next_question():
    st.session_state.factor1 = random.randint(2, 9)
    st.session_state.factor2 = random.randint(2, 9)
    st.session_state.target_product = st.session_state.factor1 * st.session_state.factor2
    st.session_state.inputs = []
    st.session_state.status = "playing"
    st.session_state.is_answered = False
    if "last_reward" in st.session_state:
        del st.session_state.last_reward

if "game_score" not in st.session_state:
    st.session_state.game_score = 0
    st.session_state.inputs = []
    st.session_state.status = "playing"
    st.session_state.gacha_step = "idle"
    st.session_state.revealed_animal = None
    st.session_state.is_answered = False
    st.session_state.factor1 = random.randint(2, 9)
    st.session_state.factor2 = random.randint(2, 9)
    st.session_state.target_product = st.session_state.factor1 * st.session_state.factor2

animals_data = {
    "일반": ["🐿️ 다람쥐", "🐥 병아리", "🐹 햄스터", "🐰 토끼", "🦔 도치", "🐭 생쥐", "🐱고양이", "🐻곰돌이"],
    "희귀": ["🦊🔥 불꽃여우", "🐱✨ 우주고양이", "🐧❄️ 아기 펭귄", "🐼 푸바오", "🐨 코알라", "🐺 은빛 늑대", "🦫 카피바라", "🐿️🌰 볼빵빵 다람쥐"],
    "전설": ["🐲 황금용", "🌈🦄 레인보우 유니콘", "🦁👑 사자왕", "🏆🐯 위대한 호랑이"]
}

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
        st.error("골드가 부족해요!")

st.markdown("""
    <style>
    .stApp { background-color: #FFFDF0; }
    [data-testid="stAppViewContainer"], [data-testid="stMain"] { background: #FFFDF0; }
    .quiz-box { background: white; padding: 25px; border-radius: 25px; text-align: center; font-size: 42px; font-weight: bold; border: 5px solid #FFD93D; box-shadow: 0px 8px 0px #FFD93D55; margin-bottom: 30px; }
    @keyframes vibrate { 0% { transform: translate(0); } 20% { transform: translate(-5px, 5px); } 40% { transform: translate(-5px, -5px); } 60% { transform: translate(5px, 5px); } 80% { transform: translate(-5px, -5px); } 100% { transform: translate(0); } }
    .egg-shaking { font-size: 150px; text-align: center; display: block; margin: 20px auto; animation: vibrate 0.15s linear infinite; }
    .reveal-card { background: white; border-radius: 30px; padding: 40px; text-align: center; border: 5px solid #FFD93D; box-shadow: 0 10px 30px rgba(0,0,0,0.1); margin: 20px 0; }
    .animal-icon { font-size: 100px; margin-bottom: 10px; }
    .animal-name { font-size: 32px; font-weight: bold; }
    .dashboard { background: #E3FAFC; padding: 15px; border-radius: 20px; border: 2px solid #10B981; font-size: 20px; font-weight: bold; color: #099268; display: flex; justify-content: space-between; margin-bottom: 20px; }
    
    /* 🛠️ 도각도각 노란색 입체 버튼 디자인 */
    div[data-testid="stButton"] button { 
        font-size: 32px !important; 
        font-weight: bold !important;
        border-radius: 18px !important; 
        background-color: #FFD93D !important; 
        color: #222222 !important; 
        height: 68px !important; 
        width: 100% !important; 
        border: none !important;
        box-shadow: 0px 6px 0px #D6B21E !important; 
        transition: all 0.05s ease-in-out !important;
    }
    div[data-testid="stButton"] button:hover { background-color: #FFE169 !important; }
    div[data-testid="stButton"] button:active {
        transform: translateY(4px) !important;
        box-shadow: 0px 2px 0px #D6B21E !important;
    }

    /* 🔒 잠금(비활성화) 상태의 버튼 디자인 가이드 (모양과 색상은 유지하되 도각거림 멈춤) */
    div[data-testid="stButton"] button:disabled {
        background-color: #FFD93D !important;
        color: #222222 !important;
        box-shadow: 0px 6px 0px #D6B21E !important;
        transform: none !important;
        cursor: not-allowed !important;
        opacity: 0.9 !important;
    }

    /* 우측 상단 '로비로' 가는 버튼 전용 디자인 */
    .lobby-btn button { 
        background-color: #475569 !important; 
        color: white !important; 
        height: 45px !important; 
        font-size: 25px !important; 
        box-shadow: 0px 4px 0px #334155 !important;
    }
    .lobby-btn button:active {
        transform: translateY(3px) !important;
        box-shadow: 0px 1px 0px #334155 !important;
    }
    </style>
""", unsafe_allow_html=True)

cols_nav = st.columns([3, 1])
with cols_nav[0]: st.title("⚔️ 역곱셈 게임")
with cols_nav[1]:
    st.markdown("<div class='lobby-btn'>", unsafe_allow_html=True)
    if st.button("🏠 로비로", use_container_width=True):
        force_file_save()
        st.switch_page("streamlit_app.py")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown(f"<div class='dashboard'><span>⭐ 점수: {st.session_state.game_score}점</span><span>💰 지갑: {st.session_state.gold} G</span></div>", unsafe_allow_html=True)

if st.session_state.gacha_step == "shaking":
    st.markdown("<span class='egg-shaking'>🥚</span>", unsafe_allow_html=True)
    time.sleep(2.0)
    st.session_state.gacha_step = "revealed"
    st.rerun()
elif st.session_state.gacha_step == "revealed":
    tier, animal = st.session_state.revealed_animal
    st.markdown("<div class='reveal-card'>", unsafe_allow_html=True)
    if "전설" in tier: st.balloons()
    st.markdown(f"<div class='animal-icon'>{animal.split()[0]}</div><div class='animal-name'>[{tier}] {animal.split()[-1]}</div></div>", unsafe_allow_html=True)
   # 🛠️ 버튼 분리: 확인(계속하기) vs 도감 보러가기
    col_confirm1, col_confirm2 = st.columns(2)
    with col_confirm1:
        if st.button("확인", use_container_width=True):
            st.session_state.gacha_step = "idle"
            force_file_save()
            st.rerun()  # 훈련장에 그대로 남음
    with col_confirm2:
        if st.button("도감 보기", use_container_width=True):
            st.session_state.gacha_step = "idle"
            force_file_save()
            st.switch_page("streamlit_app.py") # 로비로 이동
            
if st.session_state.gacha_step == "idle":
    with st.expander("🥚 [신비의 알뽑기 상점]", expanded=False):
        st.button("🔮 알뽑기 시작! (100 G)", on_click=start_gacha, use_container_width=True)

    p1 = str(st.session_state.inputs[0]) if len(st.session_state.inputs) >= 1 else " ? "
    p2 = str(st.session_state.inputs[1]) if len(st.session_state.inputs) >= 2 else " ? "
    if st.session_state.status == "hint": p1 = f"<span style='color:red;'>{st.session_state.factor1}</span>"
    
    st.markdown(f"<div class='quiz-box'>{st.session_state.target_product} = [ {p1} ] × [ {p2} ]</div>", unsafe_allow_html=True)

    if st.session_state.status == "hint":
        time.sleep(2.5)
        st.session_state.inputs = []
        st.session_state.status = "playing"
        st.session_state.is_answered = False
        st.rerun()

    # 🛑 [잠금 가드 시스템] 정답 처리 진행 중이거나 힌트 대기 상태라면 키보드를 비활성화(True) 시킵니다.
    is_keyboard_locked = (st.session_state.status != "playing") or ("last_reward" in st.session_state)

    # ⌨️ 숫자 키패드 배치 구역
    key_matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    for row in key_matrix:
        pad_cols = st.columns(3)
        for i, num in enumerate(row):
            # disabled 옵션을 주어 잠금 시 버튼이 전혀 눌리지 않게 차단합니다.
            if pad_cols[i].button(str(num), key=f"pad_{num}", use_container_width=True, disabled=is_keyboard_locked):
                if len(st.session_state.inputs) < 2 and st.session_state.status == "playing":
                    st.session_state.inputs.append(num)
                    st.session_state.is_answered = True
                    st.rerun()

    if st.button("⌫ 지우기", use_container_width=True, disabled=is_keyboard_locked):
        if len(st.session_state.inputs) > 0 and st.session_state.status == "playing":
            st.session_state.inputs.pop()
        st.rerun()

    # 🟢 정답 효과창 (키보드 최하단 유지 및 안전한 지연처리)
    if "last_reward" in st.session_state:
        st.success(f"🎉 정답! +{st.session_state.last_reward}G 획득!")
        time.sleep(1.5)
        next_question()
        st.rerun()

    # 입력 완료 시 검증 로직
    if len(st.session_state.inputs) == 2 and st.session_state.status == "playing" and st.session_state.is_answered:
        u1, u2 = st.session_state.inputs
        if u1 * u2 == st.session_state.target_product:
            reward = random.randint(8, 13)
            
            st.session_state.gold += reward
            st.session_state.game_score += 1
            st.session_state.last_reward = reward  
            st.session_state.status = "correct_waiting" # 연타 방지를 위한 즉시 임시 상태 변경 보장
            
            force_file_save()
            st.rerun()
        else:
            st.session_state.status = "hint"
            st.session_state.inputs = [st.session_state.factor1]
            st.rerun()

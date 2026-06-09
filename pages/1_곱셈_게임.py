import streamlit as st
import random
import time
import json

st.set_page_config(page_title="마법의 숲 곱셈 퀘스트", page_icon="🌿", layout="centered")

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
    st.session_state.status = "playing" # 게임 상태 초기화 (키보드 잠금 해제)

# 🛠️ [핵심 수정] 세션 상태 초기화 (각 변수별로 독립적으로 체크하여 안전성 강화)
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

# --- 🌲 [마법의 숲] 힐링 그린 그라데이션 CSS 스타일링 🌲 ---
st.markdown("""
<style>
.stApp { 
    background: linear-gradient(135deg, #134E3A 0%, #2D6A4F 40%, #52B788 80%, #D8F3DC 100%) !important; 
    color: #111111 !important; 
}
[data-testid="stAppViewContainer"], [data-testid="stMain"] { background: transparent; }

.game-title {
    font-size: 5.2vw;
    font-weight: bold;
    color: #FFFFFF;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.4);
    margin: 0;
    white-space: nowrap;
}
@media (min-width: 600px) {
    .game-title { font-size: 2.1rem !important; }
}

[data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    width: 100% !important;
    gap: 8px !important;
}
[data-testid="stHorizontalBlock"] > div {
    flex: 1 1 0% !important;
    min-width: 0 !important;
}

.quiz-box { 
    background: rgba(255, 255, 255, 0.95); padding: 25px; border-radius: 25px; text-align: center; 
    font-size: 42px; font-weight: bold; color: #1B4332 !important; 
    border: 5px solid #74C69D; box-shadow: 0px 8px 0px rgba(45, 106, 79, 0.3); margin-bottom: 30px; 
}

.dashboard { 
    background: #E8F5E9; padding: 15px; border-radius: 20px; border: 3px solid #2D6A4F; 
    font-size: 22px; font-weight: bold; color: #1B4332 !important; display: flex; justify-content: space-between; 
    box-shadow: 0px 4px 10px rgba(0,0,0,0.1); margin-bottom: 15px;
}

div[data-testid="stButton"] button { 
    font-size: 32px !important; font-weight: bold !important; border-radius: 18px !important; 
    background-color: #40916C !important; color: #FFFFFF !important; height: 68px !important; 
    width: 100% !important; border: none !important; box-shadow: 0px 6px 0px #1B4332 !important; 
    transition: all 0.05s ease-in-out !important;
}
div[data-testid="stButton"] button:hover { background-color: #52B788 !important; }
div[data-testid="stButton"] button:active { transform: translateY(4px) !important; box-shadow: 0px 2px 0px #1B4332 !important; }
div[data-testid="stButton"] button:disabled {
    background-color: #74C69D !important; color: #FFFFFF !important; box-shadow: 0px 6px 0px #40916C !important;
    transform: none !important; cursor: not-allowed !important; opacity: 0.85 !important;
}

.lobby-btn button { 
    background-color: #1B4332 !important; color: #FFFFFF !important; height: 45px !important; 
    font-size: 17px !important; box-shadow: 0px 4px 0px #081C15 !important; font-weight: bold !important;
}
.lobby-btn button:active { transform: translateY(3px) !important; box-shadow: 0px 1px 0px #081C15 !important; }

@keyframes leaf-vibrate { 0% { transform: translate(0) rotate(0deg); } 20% { transform: translate(-4px, 4px) rotate(-3deg); } 40% { transform: translate(-4px, -4px) rotate(3deg); } 60% { transform: translate(4px, 4px) rotate(-3deg); } 80% { transform: translate(-4px, -4px) rotate(3deg); } 100% { transform: translate(0) rotate(0deg); } }
.capsule-shaking { font-size: 150px; text-align: center; display: block; margin: 20px auto; animation: leaf-vibrate 0.14s linear infinite; }
.reveal-card { background: white; border-radius: 30px; padding: 40px; text-align: center; border: 5px solid #52B788; box-shadow: 0 10px 30px rgba(0,0,0,0.15); margin: 20px 0; }
.animal-icon { font-size: 100px; margin-bottom: 10px; }
.animal-name { font-size: 32px; font-weight: bold; color: #1B4332 !important; }
</style>
""", unsafe_allow_html=True)

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

    # 정답 판정 후 1.5초 대기 시 화면 렌더링을 위한 최상단 흐름
    if st.session_state.status == "correct_waiting":
        st.success(f"🎉 정답입니다! 마법 나무가 +{st.session_state.last_reward}G 보상을 떨어뜨렸습니다!")
        time.sleep(1.5)
        next_question()
        st.rerun()

    user_input_str = "".join(map(str, st.session_state.inputs)) if st.session_state.inputs else " ? "
    
    # 문제 출제 상자
    st.markdown(f"<div class='quiz-box'>{st.session_state.factor1} × {st.session_state.factor2} = [ {user_input_str} ]</div>", unsafe_allow_html=True)

    # 정답을 맞힌 상태(correct_waiting)일 경우 모든 키패드 변수에 잠금(True) 처리
    is_locked = (st.session_state.status == "correct_waiting")

    # 1 ~ 9 나뭇잎 초록색 키패드 매트릭스 배치
    key_matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    for row in key_matrix:
        pad_cols = st.columns(3)
        for i, num in enumerate(row):
            if pad_cols[i].button(str(num), key=f"pad_{num}", use_container_width=True, disabled=is_locked):
                if len(st.session_state.inputs) < 2:
                    st.session_state.inputs.append(num)
                    st.rerun()

    # 지우기, 0, 확인 키패드 하단 제어 행
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
                # 보상 계산 및 상태 변경
                reward = random.randint(8, 13)
                st.session_state.gold += reward
                st.session_state.game_score += 1
                st.session_state.last_reward = reward
                st.session_state.status = "correct_waiting" # 🔒 상태 변경: 키보드 즉시 잠금
                force_file_save()
                
                # 상태가 업데이트된 채로 화면을 다시 그림 -> 위쪽의 success 메시지 + 키보드 잠김
                st.rerun() 
            else:
                st.session_state.inputs = []
                st.toast("앗! 나뭇잎이 흔들려요. 다시 계산해봐요! ❌")
                st.rerun()

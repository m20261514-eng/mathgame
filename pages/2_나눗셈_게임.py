import streamlit as st
import random
import time
import json

st.set_page_config(page_title="신비의 알 나눗셈 퀘스트", page_icon="🥚", layout="centered")

# 로그인 튕김 방지 안전 가드
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("로그인이 필요합니다!")
    if st.button("🏠 메인 로비로 이동"): st.switch_page("streamlit_app.py")
    st.stop()

def force_file_save():
    data_to_save = {"gold": st.session_state.gold, "my_collection": list(st.session_state.my_collection)}
    with open(f"student_data/{st.session_state.current_pin}.json", "w", encoding="utf-8") as f:
        json.dump(data_to_save, f, ensure_ascii=False, indent=4)

def make_division_question():
    divisor = random.randint(2, 9)
    answer = random.randint(2, 9)
    st.session_state.dividend = divisor * answer
    st.session_state.divisor = divisor
    st.session_state.correct_answer = answer
    st.session_state.inputs = []
    st.session_state.status = "playing"
    st.session_state.is_answered = False
    if "last_reward" in st.session_state:
        del st.session_state.last_reward

if 'score' not in st.session_state:
    st.session_state.score = 0
    st.session_state.gacha_step = "idle"
    st.session_state.revealed_animal = None
    make_division_question()

animals_data = {
    "일반": ["🦋 나비", "🐝 꿀벌", "🐞 무당벌레", "🐌 달팽이", "🐜 개미", "🐟 물고기", "🐸 개구리", "🦀 꽃게"],
    "희귀": ["🦑 오징어징어", "🦐 안녕하새우", "🐡 뾰족 복어", "🐢 조용한 거북이", "🦎 우파루파", "💎🐟 보석 물고기", "🐍스르륵 아기뱀", "🌈🐠 레인보우 열대어"],
    "전설": ["🔱🐳 바다의 신 고래", "👑🐸 개구리 왕자", "🦈 심해의 메가로돈", "🦖 티라노사우루스"]
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
    /* 전체 기본 글자색을 아주 선명하고 어두운 검은색으로 고정 */
    .stApp { background-color: #FFFDF0; color: #111111 !important; }
    [data-testid="stAppViewContainer"], [data-testid="stMain"] { background: #FFFDF0; }
    
    /* 🎯 퀴즈 박스 글자색: 완전한 진한 검은색(#111111) */
    .quiz-box { 
        background: white; 
        padding: 25px; 
        border-radius: 25px; 
        text-align: center; 
        font-size: 42px; 
        font-weight: bold; 
        color: #111111 !important; 
        border: 5px solid #FFD93D; 
        box-shadow: 0px 8px 0px #FFD93D55; 
        margin-bottom: 25px; 
    }
    
    /* 💡 힌트 상자 디자인 모바일 최적화 (글자 진하게 고대비 처리) */
    .hint-box { 
        color: #B91C1C !important; 
        font-size: 32px !important; 
        font-weight: bold; 
        text-align: center; 
        background-color: #FFEBEB; 
        padding: 20px; 
        border-radius: 20px; 
        border: 4px dashed #FF4B4B;
        box-shadow: 0px 6px 0px #FF4B4B22;
        margin-top: 15px;
        margin-bottom: 25px;
    }
    
    @keyframes vibrate { 0% { transform: translate(0); } 20% { transform: translate(-5px, 5px); } 40% { transform: translate(-5px, -5px); } 60% { transform: translate(5px, 5px); } 80% { transform: translate(5px, -5px); } 100% { transform: translate(0); } }
    .egg-shaking { font-size: 150px; text-align: center; display: block; margin: 20px auto; animation: vibrate 0.15s linear infinite; }
    
    /* 🥚 결과 확인 카드 글자색 선명하게 조정 */
    .reveal-card { background: white; border-radius: 30px; padding: 40px; text-align: center; border: 5px solid #FFD93D; box-shadow: 0 10px 30px rgba(0,0,0,0.1); margin: 20px 0; }
    .animal-icon { font-size: 100px; }
    .animal-name { font-size: 38px; font-weight: bold; color: #111111 !important; }
    
    /* 📊 상단 대시보드 글자색: 선명하고 깊은 다크 그린(#044E34) */
    .dashboard { 
        background: #E3FAFC; 
        padding: 15px; 
        border-radius: 20px; 
        border: 3px solid #099268; 
        font-size: 22px; 
        font-weight: bold; 
        color: #044E34 !important; 
        display: flex; 
        justify-content: space-between; 
        margin-bottom: 20px; 
    }
    
    /* ⌨️ 숫자 키패드 글자색: 완전 찐한 검은색(#111111) 및 입체 양각 버튼 */
    div[data-testid="stButton"] button { 
        font-size: 32px !important; 
        font-weight: bold !important;
        border-radius: 18px !important; 
        background-color: #FFD93D !important; 
        color: #111111 !important; 
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
    div[data-testid="stButton"] button:disabled {
        background-color: #FFD93D !important;
        color: #111111 !important;
        box-shadow: 0px 6px 0px #D6B21E !important;
        transform: none !important;
        cursor: not-allowed !important;
        opacity: 0.85 !important;
    }

    /* 🏠 로비로 가기 버튼 패널 */
    .lobby-btn button { 
        background-color: #1E293B !important; 
        color: #FFFFFF !important; 
        height: 45px !important; 
        font-size: 18px !important; 
        box-shadow: 0px 4px 0px #0F172A !important;
        font-weight: bold !important;
    }
    .lobby-btn button:active {
        transform: translateY(3px) !important;
        box-shadow: 0px 1px 0px #0F172A !important;
    }
    </style>
""", unsafe_allow_html=True)

cols_header = st.columns([3, 1])
with cols_header[0]: st.title("🏹 나눗셈 게임")
with cols_header[1]:
    st.markdown("<div class='lobby-btn'>", unsafe_allow_html=True)
    if st.button("🏠 로비로", use_container_width=True):
        force_file_save()
        st.switch_page("streamlit_app.py")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown(f"<div class='dashboard'><span>⭐ 점수: {st.session_state.score}점</span><span>💰 지갑: {st.session_state.gold} G</span></div>", unsafe_allow_html=True)

# --- 신비의 알 뽑기 연출 구역 ---
if st.session_state.gacha_step == "shaking":
    st.markdown("<span class='egg-shaking'>🥚</span>", unsafe_allow_html=True)
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
    
    if "전설" in tier: 
        st.balloons()
    
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

# --- 게임 인터페이스 구역 ---
if st.session_state.gacha_step == "idle":
    with st.expander("🥚 [신비의 알뽑기 상점]", expanded=False):
        st.button("🔮 알뽑기 시작! (100 G)", on_click=start_gacha, use_container_width=True)
    
    # 🎨 오답 시 입력창 물음표 색상 선명한 붉은색 고정
    if st.session_state.status == "hint":
        p_ans = "<span style='color: #E03131; font-weight: 900;'> ? </span>"
    else:
        p_ans = str(st.session_state.inputs[0]) if len(st.session_state.inputs) >= 1 else " ? "
        
    st.markdown(f"<div class='quiz-box'>{st.session_state.dividend} ÷ {st.session_state.divisor} = [ {p_ans} ]</div>", unsafe_allow_html=True)

    # 정답 딜레이 연출 중에만 키패드를 잠급니다. (힌트일 때는 잠그지 않음)
    is_keyboard_locked = (st.session_state.status == "correct_waiting") or ("last_reward" in st.session_state)

    keypad = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    for row in keypad:
        cols = st.columns(3)
        for i, val in enumerate(row):
            if cols[i].button(str(val), key=f"key_{val}", use_container_width=True, disabled=is_keyboard_locked):
                # 힌트 창이 켜져있을 때 번호를 누르면 즉시 힌트가 꺼지며 입력되도록 개선
                if st.session_state.status == "hint":
                    st.session_state.status = "playing"
                
                if len(st.session_state.inputs) < 1:
                    st.session_state.inputs.append(val)
                    st.session_state.is_answered = True
                    st.rerun()
        
    if st.button("⌫ 지우기", key="del_btn", use_container_width=True, disabled=is_keyboard_locked):
        st.session_state.inputs = []
        st.session_state.status = "playing"
        st.rerun()

    # 💡 [핵심 변경] 하단 구구단 역산 힌트 상시 표기 (time.sleep 제거)
    if st.session_state.status == "hint":
        st.markdown(f"<div class='hint-box'>💡 힌트 곱셈식: {st.session_state.divisor} × <span style='text-decoration: underline;'>{st.session_state.correct_answer}</span> = {st.session_state.dividend}</div>", unsafe_allow_html=True)

    # 🎉 정답 성공 메시지창 지연 처리 구역
    if "last_reward" in st.session_state:
        st.success(f"✅ 정답! +{st.session_state.last_reward}G 획득!")
        time.sleep(1.2)
        make_division_question()
        st.rerun()

    # 실시간 입력 확인 로직
    if len(st.session_state.inputs) == 1 and st.session_state.status == "playing" and st.session_state.is_answered:
        if st.session_state.inputs[0] == st.session_state.correct_answer:
            reward = random.randint(8, 13)
            st.session_state.score += 1
            st.session_state.gold += reward
            st.session_state.last_reward = reward
            st.session_state.status = "correct_waiting" # 연타 잠금
            force_file_save()
            st.rerun()
        else:
            # 틀렸을 시 시간 끌지 않고 상태만 바꾸어 힌트 박스를 아래에 즉시 렌더링
            st.session_state.status = "hint"
            st.session_state.inputs = []
            st.session_state.is_answered = False
            st.rerun()

import streamlit as st
import random
import time

# 1. 페이지 설정
st.set_page_config(page_title="신비의 알 나눗셈 퀘스트", page_icon="🥚", layout="centered")

# --- 🌟 [중요] 메인 포털과 연동되는 전역 세션 및 로컬 세션 초기화 ---
if "gold" not in st.session_state:
    st.session_state.gold = 0  # 메인과 공유하는 돈지갑

if "my_collection" not in st.session_state:
    st.session_state.my_collection = set()  # 메인과 공유하는 도감 (set 구조)

# 나눗셈 게임 전용 로컬 상태 및 문제 생성 로직
def make_division_question():
    divisor = random.randint(2, 9)       # 나누는 수 (예: 7)
    answer = random.randint(2, 9)        # 실제 정답 (예: 8)
    dividend = divisor * answer          # 나누어지는 수 (예: 56)
    
    st.session_state.dividend = dividend
    st.session_state.divisor = divisor
    st.session_state.correct_answer = answer
    st.session_state.inputs = []
    st.session_state.status = "playing"
    st.session_state.is_answered = False

if 'score' not in st.session_state:
    st.session_state.score, st.session_state.total = 0, 0
    st.session_state.gacha_step = "idle"
    st.session_state.revealed_animal = None
    make_division_question()

if 'is_answered' not in st.session_state:
    st.session_state.is_answered = False 

def next_question():
    make_division_question()

# 키패드 콜백 함수
def press_key(val):
    if st.session_state.is_answered:
        return
    st.session_state.inputs.append(val)
    st.session_state.is_answered = True 

def press_delete():
    if st.session_state.is_answered:
        return
    if len(st.session_state.inputs) > 0:
        st.session_state.inputs.pop()

# 2. 동물 데이터 정의 (메인과 완벽 일치 및 확률 숨김)
animals_data = {
    "✨ 일반 등급": ["🦋 나비", "🐝 꿀벌", "🐞 무당벌레", "🐌 달팽이", "🐜 개미"],
    "🌟 희귀 등급": ["🐸 궁금한 개구리", "🦑 오징어징어", "🦐 안녕하새우", "🐡 뾰족 복어", "🐢 조용한 거북이", "🦎 우파루파"],
    "👑 전설 등급": ["🔱🐳 바다의 신 고래", "🌈🐠 레인보우 열대어", "🦈 심해의 메가로돈", "💎🐟 보석 물고기", "🦖 티라노사우루스"]
}

# 3. 상점 가챠 로직 (숨겨진 확률로 계산하되 등급 이름은 비밀로!)
def start_gacha():
    if st.session_state.gold >= 100:
        st.session_state.gold -= 100
        st.session_state.gacha_step = "shaking"
        rand = random.random()
        
        # 내부적으로만 확률을 계산하고 겉으로는 예쁜 등급 이름 매칭
        if rand < 0.7: tier = "✨ 일반 등급"
        elif rand < 0.95: tier = "🌟 희귀 등급"
        else: tier = "👑 전설 등급"
        
        selected_animal = random.choice(animals_data[tier])
        st.session_state.revealed_animal = (tier, selected_animal)
        
        # 메인 도감(set)에 즉시 누적 저장
        st.session_state.my_collection.add(selected_animal)
    else:
        st.error("골드가 부족해요! 문제를 더 풀어서 골드를 모으세요!")

# CSS (스타일 유지 및 모바일 반응형)
st.markdown("""
    <style>
    .stApp { background-color: #FFFDF0; color: #222222; }
    [data-testid="stAppViewContainer"], [data-testid="stMain"] { background: #FFFDF0; }
    
    .quiz-box {
        background: white; padding: 25px; border-radius: 25px;
        text-align: center; font-size: 42px; font-weight: bold;
        color: #222222; border: 5px solid #FFD93D;
        box-shadow: 0px 8px 0px #FFD93D55; margin-bottom: 25px;
    }
    .hint-box {
        color: #FF4B4B !important; font-size: 32px !important; font-weight: bold;
        text-align: center; margin-top: 15px; margin-bottom: 20px;
        background-color: #FFEBEB; padding: 15px; border-radius: 15px;
        border: 3px dashed #FF4B4B; box-shadow: 0px 4px 0px #FFC1C1;
    }
    @keyframes vibrate {
        0% { transform: translate(0); }
        20% { transform: translate(-5px, 5px); }
        40% { transform: translate(-5px, -5px); }
        60% { transform: translate(5px, 5px); }
        80% { transform: translate(5px, -5px); }
        100% { transform: translate(0); }
    }
    .egg-shaking {
        font-size: 150px; text-align: center;
        display: block; margin: 20px auto;
        animation: vibrate 0.15s linear infinite;
        text-shadow: 1px 1px 6px #FFD93D44;
    }
    .reveal-card {
        background: white; border-radius: 30px; padding: 40px;
        text-align: center; border: 5px solid #FFD93D;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1); margin: 20px 0;
    }
    .animal-icon { font-size: 100px; margin-bottom: 10px; }
    .animal-name { font-size: 38px; font-weight: bold; color: #1C2833; }

    .dashboard {
        background: #E3FAFC; padding: 15px; border-radius: 20px;
        border: 2px solid #10B981; font-size: 20px; font-weight: bold;
        color: #12615C; display: flex; justify-content: space-between;
        margin-bottom: 20px; text-shadow: 0 1px 0 #fff;
    }
    
    .stButton>button {
        font-size: 30px !important; border-radius: 15px !important;
        background-color: #FFD93D !important; color: #222222 !important;
        height: 65px !important; width: 100% !important;
        box-shadow: 0px 5px 0px #E6C229 !important; font-weight: bold !important;
        transition: all 0.1s ease; border: 2px solid #C0A100 !important;
    }
    .stButton>button:active { transform: translateY(3px); }
    
    div.keypad-container + div .stButton>button {
        background-color: #FF9233 !important; color: #fff !important;
        box-shadow: 0px 5px 0px #DD6B11 !important;
        border: 2px solid #B96009 !important; margin-top: 10px;
    }
    
    .lobby-btn button {
        background-color: #475569 !important; color: white !important;
        box-shadow: 0px 4px 0px #1e293b !important; height: 45px !important; font-size: 18px !important;
        border: 2px solid #334155 !important;
    }

    @media (max-width: 768px) {
        .quiz-box, .reveal-card, .animal-name, .dashboard, .hint-box { font-size: 5vw !important; }
        .stButton>button { font-size: 6vw !important; height: 55px !important; }
        .animal-icon { font-size: 12vw; }
        
        div[data-testid="stHorizontalBlock"] {
            display: flex !important; flex-direction: row !important;
            flex-wrap: nowrap !important; gap: 8px !important;
        }
        div[data-testid="stHorizontalBlock"] > div { width: 33.33% !important; min-width: 0 !important; }
    }
    </style>
""", unsafe_allow_html=True)

# --- 상단 레이아웃 및 로비 버튼 네비게이션 ---
cols_header = st.columns([3, 1])
with cols_header[0]:
    st.title("🏹 나눗셈 훈련장")
with cols_header[1]:
    st.markdown('<div class="lobby-btn">', unsafe_allow_html=True)
    if st.button("🏠 로비로", use_container_width=True):
        st.switch_page("streamlit_app.py")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown(f"<div class='dashboard'><span>⭐ 점수: {st.session_state.score}</span><span>💰 내 지갑: {st.session_state.gold} G</span></div>", unsafe_allow_html=True)

# 5. 알 부화 연출 제어 시퀀스
if st.session_state.gacha_step == "shaking":
    st.markdown("<span class='egg-shaking'>🥚</span>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>알이 부르르~ 깨지려고 해요!</h3>", unsafe_allow_html=True)
    time.sleep(2.5)
    st.session_state.gacha_step = "revealed"
    st.rerun()
elif st.session_state.gacha_step == "revealed":
    tier, animal = st.session_state.revealed_animal
    st.markdown("<div class='reveal-card'>", unsafe_allow_html=True)
    if "전설" in tier: st.balloons()
    elif "희귀" in tier: st.snow()
    st.markdown(f"<div class='animal-icon'>{animal.split()[0]}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='animal-name'>[{tier}] {animal.split()[-1]}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    if st.button("확인 (도감 확인하러 가기)", use_container_width=True):
        st.session_state.gacha_step = "idle"
        st.switch_page("streamlit_app.py")

# 6. 기본 게임 모드
if st.session_state.gacha_step == "idle":
    with st.expander("🥚 [신비의 알뽑기 상점 열기]", expanded=False):
        st.write("100골드로 새로운 바다 동물을 깨워보세요!")
        st.button("🔮 알뽑기 시작!", on_click=start_gacha, use_container_width=True)
    
    p_ans = str(st.session_state.inputs[0]) if len(st.session_state.inputs) >= 1 else " ? "
    st.markdown(f"<div class='quiz-box'>{st.session_state.dividend} ÷ {st.session_state.divisor} = [ {p_ans} ]</div>", unsafe_allow_html=True)

    if st.session_state.status == "hint":
        div_num = st.session_state.divisor
        ans_num = st.session_state.correct_answer
        total_num = st.session_state.dividend
        
        st.markdown(f"<div class='hint-box'>💡 구구단 힌트: {div_num} × {ans_num} = {total_num}</div>", unsafe_allow_html=True)
        st.error("❌ 틀렸습니다! 곱셈 관계를 생각하며 다시 풀어보세요.")
        
        time.sleep(2.8) 
        st.session_state.inputs = []
        st.session_state.status = "playing"
        st.session_state.is_answered = False 
        st.rerun()

    if st.session_state.status == "playing":
        st.markdown('<div class="keypad-container"></div>', unsafe_allow_html=True)
        
        keypad = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        for row in keypad:
            cols = st.columns(3, gap="small")
            for i, val in enumerate(row):
                cols[i].button(str(val), key=f"key_{val}", use_container_width=True, 
                               disabled=st.session_state.is_answered, 
                               on_click=press_key, args=(val,))
        
        st.button("⌫ 지우기", key="del_btn", use_container_width=True, 
                  disabled=st.session_state.is_answered, 
                  on_click=press_delete)

    if len(st.session_state.inputs) == 1 and st.session_state.is_answered and st.session_state.status == "playing":
        time.sleep(0.4)
        user_answer = st.session_state.inputs[0]
        
        if user_answer == st.session_state.correct_answer:
            get_gold = random.randint(8, 13)
            st.success(f"✅ 정답! {get_gold} 골드를 얻었습니다! 💰")
            st.session_state.score += 1
            st.session_state.gold += get_gold
            st.session_state.total += 1
            time.sleep(1.8)
            next_question()
            st.rerun()
        else:
            st.session_state.status = "hint"
            st.rerun()

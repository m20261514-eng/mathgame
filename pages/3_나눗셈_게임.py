import streamlit as st
import random
import time
import json
import base64
import os

st.set_page_config(page_title="신비로운 우주 나눗셈 퀘스트", page_icon="🚀", layout="centered")

# 🛠️ [경로 치트키] 현재 파이썬 파일과 '같은 폴더'에 있는 배경 이미지를 강제로 연결합니다.
current_dir = os.path.dirname(__file__)
IMAGE_PATH = os.path.join(current_dir, "division_background.png")

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
    st.warning("로그인이 필요합니다! 메인 로비로 이동하세요.")
    if st.button("🏠 메인 로비로 이동"): st.switch_page("streamlit_app.py")
    st.stop()

# 데이터 강제 저장 유틸리티
def force_file_save():
    data_to_save = {"gold": st.session_state.gold, "my_collection": list(st.session_state.my_collection)}
    with open(f"student_data/{st.session_state.current_pin}.json", "w", encoding="utf-8") as f:
        json.dump(data_to_save, f, ensure_ascii=False, indent=4)

# 다음 문제 생성 유틸리티
def make_division_question():
    divisor = random.randint(2, 9)
    answer = random.randint(2, 9)
    st.session_state.dividend = divisor * answer
    st.session_state.divisor = divisor
    st.session_state.correct_answer = answer
    st.session_state.inputs = []
    st.session_state.status = "playing"
    st.session_state.is_locked = False # 🔒 새 문제 시작 시 키보드 잠금 해제

# 🛠️ 세션 상태 초기화 (AttributeError 원천 차단)
if 'score' not in st.session_state: st.session_state.score = 0
if 'inputs' not in st.session_state: st.session_state.inputs = []
if 'status' not in st.session_state: st.session_state.status = "playing"
if 'gacha_step' not in st.session_state: st.session_state.gacha_step = "idle"
if 'revealed_animal' not in st.session_state: st.session_state.revealed_animal = None
if 'is_locked' not in st.session_state: st.session_state.is_locked = False
if 'last_reward' not in st.session_state: st.session_state.last_reward = 0

# 나눗셈용 필수 수학 변수가 세션에 없으면 즉시 생성
if 'dividend' not in st.session_state or 'divisor' not in st.session_state or 'correct_answer' not in st.session_state:
    make_division_question()

# 우주 테마 콜렉션 데이터 세팅
animals_data = {
    "일반": ["🔩 우주 나사","📡 녹슨 안테나","🔭 소형 망원경","🔧 우주 스패너","🛰️ 낡은 위성", "🚀 꼬마 로켓", "🧀 우주 치즈", "🧪 우주 식량"],
    "희귀": ["🐭 우주 실험쥐","🤖 고장난 로봇","🛸 은하수 순찰 UFO", "👾 픽셀 몬스터"],
    "전설": ["👽 초록 외계인","🐰 달토끼","🧬 돌연변이 우주 슬라임","🌟 반짝이는 초신성"]
}

# 빛나는 운석 뽑기 로직
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
        st.error("골드가 부족해요! 🪐")

# 🎯 키패드 버튼 클릭 콜백 함수
def press_key(num):
    if not st.session_state.is_locked and len(st.session_state.inputs) < 1:
        st.session_state.inputs.append(num)

def press_del():
    if not st.session_state.is_locked:
        st.session_state.inputs = []
        st.session_state.status = "playing"

# --- 🌌 우주 테마 CSS ---
background_html = f"""
<div class="custom-space-bg"></div>

<style>
/* 1. 배경화면 고정 레이어 */
.custom-space-bg {{
    position: fixed; top: -10px; left: -10px; width: calc(100vw + 20px); height: calc(100vh + 20px);
    background-image: url("data:image/png;base64,{img_base64}") !important;
    background-repeat: no-repeat !important; background-position: center center !important;
    background-size: cover !important; filter: blur(5px) brightness(0.4); 
    z-index: -3; pointer-events: none;
}}

/* 2. Streamlit 기본 컴포넌트 투명화 */
.stApp, section.main, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stMainViewContainer"], [data-testid="stMain"], [data-testid="stDecoration"] {{
    background-color: transparent !important; background: transparent !important;
}}

/* 3. 신비로운 네온 우주선 반짝이 효과 */
.space-particles-bg {{ position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: -1; pointer-events: none; overflow: hidden; }}
.pink-purple-sparkles {{
    position: absolute; width: 4px; height: 4px; border-radius: 50%; background: transparent;
    box-shadow: 20vw 30vh rgba(255, 0, 127, 0.6), 40vw 50vh rgba(138, 43, 226, 0.6), 60vw 20vh rgba(255, 255, 255, 0.7), 
                80vw 70vh rgba(255, 0, 127, 0.5), 15vw 80vh rgba(138, 43, 226, 0.6), 85vw 15vh rgba(255, 255, 255, 0.5);
    animation: galaxyOrbit 25s linear infinite;
}}
@keyframes galaxyOrbit {{ 0% {{ transform: translateY(0) rotate(0deg); opacity: 0.6; }} 50% {{ opacity: 0.2; }} 100% {{ transform: translateY(-100vh) rotate(360deg); opacity: 0.6; }} }}

/* 타이틀 디자인 */
.game-title {{ font-size: 5.2vw; font-weight: bold; color: #FFFFFF; text-shadow: 2px 2px 8px rgba(255, 0, 127, 0.8); margin: 0; white-space: nowrap; }}
@media (min-width: 600px) {{ .game-title {{ font-size: 2.1rem !important; }} }}

[data-testid="stHorizontalBlock"] {{ display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important; width: 100% !important; gap: 8px !important; }}
[data-testid="stHorizontalBlock"] > div {{ flex: 1 1 0% !important; min-width: 0 !important; }}

/* 🧩 문제 상자 디자인 */
.quiz-box {{ 
    background: rgba(255, 255, 255, 0.95); padding: 25px; border-radius: 25px; text-align: center; 
    font-size: 42px; font-weight: bold; color: #2D004D !important; 
    border: 5px solid #8A2BE2; box-shadow: 0px 8px 20px rgba(138, 43, 226, 0.4); margin-bottom: 25px; 
}}

.hint-box {{ font-family: Arial; font-size: 20px; color: #FF007F; font-weight: bold; background-color: rgba(255, 255, 255, 0.85); padding: 15px; border-radius: 15px; text-align: center; margin-top: 10px; border: 3px dashed #FF007F; }}

/* 📊 대시보드 */
.dashboard {{ 
    background: rgba(243, 230, 255, 0.92); padding: 15px; border-radius: 20px; border: 3px solid #FF007F; 
    font-size: 22px; font-weight: bold; color: #4A004A !important; display: flex; justify-content: space-between; margin-bottom: 20px; 
    box-shadow: 0px 4px 12px rgba(255, 0, 127, 0.2);
}}

/* 🚀 키패드 및 하단 버튼 디자인 */
div[data-testid="stButton"] button {{ 
    font-size: 28px !important; font-weight: bold !important; border-radius: 18px !important; 
    background-color: #8A2BE2 !important; color: #FFFFFF !important; height: 68px !important; 
    width: 100% !important; border: none !important; box-shadow: 0px 5px 0px #5A189A !important; 
    transition: all 0.05s ease-in-out !important;
}}
div[data-testid="stButton"] button p {{ color: #FFFFFF !important; font-size: 26px !important; font-weight: bold !important; }}
div[data-testid="stButton"] button:hover {{ background-color: #FF007F !important; box-shadow: 0px 5px 0px #C1005B !important; }}
div[data-testid="stButton"] button:active {{ transform: translateY(4px) !important; box-shadow: 0px 1px 0px #5A189A !important; }}

/* 🔒 잠긴 버튼(정답 후) 비활성화 디자인 */
div[data-testid="stButton"] button:disabled {{
    background-color: #C89BFA !important; color: #FFFFFF !important; box-shadow: 0px 5px 0px #8A2BE2 !important;
    transform: none !important; cursor: not-allowed !important; opacity: 0.7 !important;
}}

/* 🏠 상단 로비 버튼 */
.lobby-btn button {{ 
    background-color: rgba(45, 0, 77, 0.85) !important; color: #FFFFFF !important; height: 45px !important; 
    font-size: 16px !important; box-shadow: 0px 4px 0px #1A0033 !important; font-weight: bold !important;
}}
.lobby-btn button p {{ font-size: 16px !important; font-weight: bold !important; color: #FFFFFF !important; }}
.lobby-btn button:hover {{ background-color: #FF007F !important; box-shadow: 0px 4px 0px #C1005B !important; color: #FFFFFF !important; }}
.lobby-btn button:active {{ transform: translateY(3px) !important; box-shadow: 0px 1px 0px #1A0033 !important; }}

/* 💬 새로 추가된 우주 테마 피드백 메시지 박스 */
.feedback-success {{ background: rgba(243, 230, 255, 0.95); color: #4A004A; padding: 15px; border-radius: 15px; text-align: center; font-size: 22px; font-weight: bold; border: 3px solid #8A2BE2; margin-top: 20px; box-shadow: 0px 4px 12px rgba(138, 43, 226, 0.3); }}
.feedback-error {{ background: rgba(255, 227, 240, 0.95); color: #8B0045; padding: 15px; border-radius: 15px; text-align: center; font-size: 22px; font-weight: bold; border: 3px solid #FF007F; margin-top: 20px; box-shadow: 0px 4px 12px rgba(255, 0, 127, 0.3); }}

/* 운석 충돌 진동 애니메이션 효과 */
@keyframes vibrate {{ 0% {{ transform: translate(0) rotate(0deg); }} 20% {{ transform: translate(-5px, 5px) rotate(-3deg); }} 40% {{ transform: translate(-5px, -5px) rotate(3deg); }} 60% {{ transform: translate(5px, 5px) rotate(-3deg); }} 80% {{ transform: translate(5px, -5px) rotate(3deg); }} 100% {{ transform: translate(0) rotate(0deg); }} }}
.meteor-shaking {{ font-size: 150px; text-align: center; display: block; margin: 20px auto; animation: vibrate 0.12s linear infinite; }}
.reveal-card {{ background: rgba(255, 255, 255, 0.95); border-radius: 30px; padding: 40px; text-align: center; border: 5px solid #FF007F; box-shadow: 0 10px 30px rgba(255, 0, 127, 0.3); margin: 20px 0; }}
.animal-icon {{ font-size: 100px; }}
.animal-name {{ font-size: 38px; font-weight: bold; color: #2D004D !important; }}

</style>

<div class="space-particles-bg">
    <div class="pink-purple-sparkles"></div>
</div>
"""

if not img_base64:
    st.error("🚨 [파일 인식 실패] 폴더 안에 'division_background.png' 파일이 없는 것 같습니다. 파일명이 완벽히 똑같은지 다시 확인해 주세요!")

st.markdown(background_html, unsafe_allow_html=True)

# 상단 헤더 및 네비게이션 구조화
cols_header = st.columns([2.9, 1.1])
with cols_header[0]: 
    st.markdown("<div style='padding-top: 5px;'><h2 class='game-title'>🪐 신비한 우주 나눗셈</h2></div>", unsafe_allow_html=True)
with cols_header[1]:
    st.markdown("<div class='lobby-btn'>", unsafe_allow_html=True)
    if st.button("🏠 로비로", use_container_width=True):
        force_file_save()
        st.switch_page("streamlit_app.py")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown(f"<div class='dashboard'><span>⭐ 점수: {st.session_state.score}점</span><span>💰 지갑: {st.session_state.gold} G</span></div>", unsafe_allow_html=True)

# 가챠(빛나는 운석 뽑기) 연출 단계 처리
if st.session_state.gacha_step == "shaking":
    st.markdown("<span class='meteor-shaking'>☄️</span>", unsafe_allow_html=True)
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
            make_division_question()
            force_file_save()
            st.rerun()
    with col_confirm2:
        if st.button("도감 보기", use_container_width=True):
            st.session_state.gacha_step = "idle"
            make_division_question()
            force_file_save()
            st.switch_page("streamlit_app.py")

# 기본 플레이 화면 UI 로드
if st.session_state.gacha_step == "idle":
    with st.expander("☄️ [빛나는 운석 뽑기 상점]", expanded=False):
        st.button("🔮 운석 파편 분석 시작! (100 G)", on_click=start_gacha, use_container_width=True)

    # 🎯 정답 판별 로직 (화면 그리기 전 검사)
    feedback_msg = ""
    feedback_type = ""

    if len(st.session_state.inputs) == 1:
        u_ans = st.session_state.inputs[0]
        if u_ans == st.session_state.correct_answer:
            if not st.session_state.is_locked: # 🔒 중복 획득 방지
                reward = random.randint(8, 13)
                st.session_state.score += 1
                st.session_state.gold += reward
                st.session_state.last_reward = reward
                force_file_save()
                st.session_state.is_locked = True
            feedback_msg = f"🎆 우주의 축복! 정답입니다! +{st.session_state.last_reward}G 획득! 🚀"
            feedback_type = "success"
        else:
            if not st.session_state.is_locked:
                st.session_state.is_locked = True # 에러 메시지 출력 중 잠금
            feedback_msg = "궤도를 이탈했습니다! 은하수 힌트를 확인해보세요! ☄️"
            feedback_type = "error"

    # 문제 출제 상자 렌더링
    if st.session_state.status == "hint":
        p_ans = "<span style='color: #FF007F; font-weight: 900;'> ? </span>"
    else:
        p_ans = str(st.session_state.inputs[0]) if len(st.session_state.inputs) >= 1 else " ? "
        
    st.markdown(f"<div class='quiz-box'>{st.session_state.dividend} ÷ {st.session_state.divisor} = [ {p_ans} ]</div>", unsafe_allow_html=True)

    # 계산기 패드 배치
    keypad = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    for row in keypad:
        cols = st.columns(3)
        for i, val in enumerate(row):
            cols[i].button(str(val), key=f"key_{val}", on_click=press_key, args=(val,), use_container_width=True, disabled=st.session_state.is_locked)
        
    # 하단 전체 지우기 패널
    st.button("⌫ 지우기", key="del_btn", on_click=press_del, use_container_width=True, disabled=st.session_state.is_locked)

    # 💬 피드백 박스 & 힌트 박스 렌더링
    if feedback_msg:
        css_class = "feedback-success" if feedback_type == "success" else "feedback-error"
        st.markdown(f"<div class='{css_class}'>{feedback_msg}</div>", unsafe_allow_html=True)
    else:
        if st.session_state.status == "hint":
            st.markdown(f"<div class='hint-box'>💡 은하수 힌트: {st.session_state.divisor} × <span style='text-decoration: underline;'>{st.session_state.correct_answer}</span> = {st.session_state.dividend}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='height: 60px; margin-top: 20px;'></div>", unsafe_allow_html=True)

    # ⏳ 피드백 딜레이 후 화면 자동 전환
    if feedback_type == "success":
        time.sleep(1.2)
        make_division_question()
        st.rerun()
    elif feedback_type == "error":
        time.sleep(1.0)
        # 오답일 경우 힌트 모드로 전환 후 입력창 초기화
        st.session_state.status = "hint"
        st.session_state.inputs = []
        st.session_state.is_locked = False
        st.rerun()

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

if "game_score" not in st.session_state:
    st.session_state.game_score = 0
    st.session_state.inputs = []
    st.session_state.status = "playing"
    st.session_state.gacha_step = "idle"
    st.session_state.revealed_animal = None
    st.session_state.factor1 = random.randint(2, 9)
    st.session_state.factor2 = random.randint(2, 9)
    st.session_state.target_product = st.session_state.factor1 * st.session_state.factor2

def next_question():
    st.session_state.factor1 = random.randint(2, 9)
    st.session_state.factor2 = random.randint(2, 9)
    st.session_state.target_product = st.session_state.factor1 * st.session_state.factor2
    st.session_state.inputs = []
    st.session_state.status = "playing"

animals_data = {
    "✨ 일반 등급": ["🍼 아기오리", "🐥 병아리", "🐹 햄스터", "🐰 토끼", "🦔 도치"],
    "🌟 희귀 등급": ["🦊 불꽃여우", "🐱 우주고양이", "🦄 페가수스", "🐼 푸바오", "🐨 코알라", "🐺 은빛 늑대"],
    "👑 전설 등급": ["🐲 황금용", "🦄 레인보우 유니콘", "🦁 사자왕", "🐋 거대 고래", "🦊 구미호"]
}

def start_gacha():
    if st.session_state.gold >= 100:
        st.session_state.gold -= 100
        st.session_state.gacha_step = "shaking"
        rand = random.random()
        if rand < 0.7: tier = "✨ 일반 등급"
        elif rand < 0.95: tier = "🌟 희귀 등급"
        else: tier = "👑 전설 등급"
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
    .quiz-box { background: white; padding: 25px; border-radius: 25px; text-align: center; font-size: 42px; font-weight: bold; border: 5px solid #FFD93D; box-shadow: 0px 8px 0px #FFD93D55; margin-bottom: 25px; }
    @keyframes vibrate { 0% { transform: translate(0); } 20% { transform: translate(-5px, 5px); } 40% { transform: translate(-5px, -5px); } 60% { transform: translate(5px, 5px); } 80% { transform: translate(5px, -5px); } 100% { transform: translate(0); } }
    .egg-shaking { font-size: 150px; text-align: center; display: block; margin: 20px auto; animation: vibrate 0.15s linear infinite; }
    .reveal-card { background: white; border-radius: 30px; padding: 40px; text-align: center; border: 5px solid #FFD93D; box-shadow: 0 10px 30px rgba(0,0,0,0.1); margin: 20px 0; }
    .animal-icon { font-size: 100px; margin-bottom: 10px; }
    .animal-name { font-size: 32px; font-weight: bold; }
    .dashboard { background: #E3FAFC; padding: 15px; border-radius: 20px; border: 2px solid #10B981; font-size: 20px; font-weight: bold; color: #099268; display: flex; justify-content: space-between; margin-bottom: 20px; }
    div[data-testid="stButton"] button { font-size: 28px !important; border-radius: 15px !important; background-color: #FFD93D !important; color: #4A4A4A !important; height: 65px !important; width: 100% !important; box-shadow: 0px 5px 0px #E6C229 !important; font-weight: bold !important; }
    .lobby-btn button { background-color: #475569 !important; color: white !important; height: 45px !important; font-size: 18px !important; }
    </style>
""", unsafe_allow_html=True)

cols_nav = st.columns([3, 1])
with cols_nav[0]: st.title("⚔️ 역곱셈 훈련장")
with cols_nav[1]:
    if st.button("🏠 로비로", use_container_width=True):
        force_file_save()
        st.switch_page("streamlit_app.py")

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
    if st.button("확인 (도감으로 가기)", use_container_width=True):
        st.session_state.gacha_step = "idle"
        force_file_save()
        st.switch_page("streamlit_app.py")

if st.session_state.gacha_step == "idle":
    with st.expander("🥚 [신비의 알뽑기 상점]", expanded=False):
        st.button("🔮 알뽑기 시작! (100 G)", on_click=start_gacha, use_container_width=True)

    p1 = str(st.session_state.inputs[0]) if len(st.session_state.inputs) >= 1 else " ? "
    p2 = str(st.session_state.inputs[1]) if len(st.session_state.inputs) >= 2 else " ? "
    if st.session_state.status == "hint": p1 = f"<span style='color:red;'>{st.session_state.factor1}</span>"
    
    st.markdown(f"<div class='quiz-box'>{st.session_state.target_product} = [ {p1} ] × [ {p2} ]</div>", unsafe_allow_html=True)

    key_matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    for row in key_matrix:
        pad_cols = st.columns(3)
        for i, num in enumerate(row):
            if pad_cols[i].button(str(num), key=f"pad_{num}", use_container_width=True):
                if len(st.session_state.inputs) < 2:
                    st.session_state.inputs.append(num)
                    st.rerun()

    if st.button("⌫ 지우기", use_container_width=True):
        if len(st.session_state.inputs) > 0:
            st.session_state.inputs.pop()
            st.rerun()

    if len(st.session_state.inputs) == 2:
        time.sleep(0.4)
        u1, u2 = st.session_state.inputs
        if u1 * u2 == st.session_state.target_product:
            reward = random.randint(8, 13)
            st.success(f"🎉 정답! +{reward}G 획득!")
            st.session_state.game_score += 1
            st.session_state.gold += reward
            force_file_save()
            time.sleep(1.2)
            next_question()
            st.rerun()
        else:
            st.session_state.status = "hint"
            st.session_state.inputs = [st.session_state.factor1]
            st.rerun()

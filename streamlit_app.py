import streamlit as st
import random
import time

# 1. 페이지 기본 설정
st.set_page_config(page_title="수학 게임 대모험 메인", page_icon="🎲", layout="centered")

# --- 🌟 하위 모든 게임 페이지가 공유할 전역 세션 상태 초기화 ---
if "my_collection" not in st.session_state:
    st.session_state.my_collection = set()  # 중복 방지를 위한 set 구조 (수집 도감)

if "gold" not in st.session_state:
    st.session_state.gold = 0  # 모든 게임에서 공용으로 사용할 통합 골드 지갑

# 2. 동물 데이터 정의 (확률 텍스트 제거 및 분리)
multiply_animals = {
    "✨ 일반 등급": ["🍼 아기오리", "🐥 병아리", "🐹 햄스터", "🐰 토끼", "🦔 도치"],
    "🌟 희귀 등급": ["🦊 불꽃여우", "🐱 우주고양이", "🦄 페가수스", "🐼 푸바오", "🐨 코알라", "🐺 은빛 늑대"],
    "👑 전설 등급": ["🐲 황금용", "🦄 레인보우 유니콘", "🦁 사자왕", "🐋 거대 고래", "🦊 구미호"]
}

divide_animals = {
    "✨ 일반 등급": ["🦋 나비", "🐝 꿀벌", "🐞 무당벌레", "🐌 달팽이", "🐜 개미"],
    "🌟 희귀 등급": ["🐸 궁금한 개구리", "🦑 오징어징어", "🦐 안녕하새우", "🐡 뾰족 복어", "🐢 조용한 거북이", "🦎 우파루파"],
    "👑 전설 등급": ["🔱🐳 바다의 신 고래", "🌈🐠 레인보우 열대어", "🦈 심해의 메가로돈", "💎🐟 보석 물고기", "🦖 티라노사우루스"]
}

# 수집률 계산을 위한 전체 동물 리스트 생성
all_animals = []
for tier in multiply_animals.values(): all_animals.extend(tier)
for tier in divide_animals.values(): all_animals.extend(tier)

# 3. 메인 로비 전용 CSS 스타일링
st.markdown("""
    <style>
    /* 전체 배경 크림색 설정 */
    .stApp { background-color: #FFFDF0; color: #222222; }
    [data-testid="stAppViewContainer"], [data-testid="stMain"] { background: #FFFDF0; }
    
    /* 타이틀 애니메이션 효과 */
    @keyframes chromatic-aberration {
        0%, 100% { text-shadow: -2px 0 #FF00FF, 2px 0 #00FFFF, 0 0 30px rgba(0, 0, 0, 0.4); }
        50% { text-shadow: -3px 0 #FF00FF, 3px 0 #00FFFF, 0 0 30px rgba(0, 0, 0, 0.4); }
    }
    
    .main-title {
        font-size: 3rem; font-weight: bold; color: #000000; text-align: center;
        margin-bottom: 20px; margin-top: 15px; letter-spacing: 2px;
        white-space: nowrap; animation: chromatic-aberration 2s ease-in-out infinite;
        display: inline-block; width: 100%;
    }
    
    .guide-text { color: #156580 !important; font-weight: bold; text-align: center; font-size: 1.2rem; margin-bottom: 30px;}
    
    /* 게임 입장 버튼 커스텀 스타일 */
    button[kind="primary"] {
        display: block !important; width: 100% !important; padding: 25px 0 !important;
        font-size: 1.6rem !important; font-weight: bold !important; border-radius: 20px !important;
        background: linear-gradient(90deg, #FFF9C6 0%, #BDF6F6 100%) !important;
        color: #2D2D2D !important; border: 4px solid #FFD93D !important;
        box-shadow: 0 8px 0 #FFD93D55 !important;
        transition: 0.1s all ease !important;
        height: auto !important;
    }
    button[kind="primary"]:hover { background: #FFE77C !important; transform: scale(1.03) !important; }
    button[kind="primary"]:active { transform: translateY(4px) !important; box-shadow: 0 4px 0 #FFD93D55 !important; }
    
    /* 동물 도감 타이틀 배치 스타일 */
    .tier-title {
        font-size: 1.2rem; font-weight: bold; color: #4A4A4A;
        margin-top: 25px; margin-bottom: 12px; padding-left: 8px;
        border-left: 5px solid #FFD93D;
    }
    
    /* 동물 카드 레이아웃 (미획득 상태) */
    .animal-card-locked {
        background: #F1F3F5; border-radius: 15px; padding: 15px 10px; text-align: center;
        border: 2px dashed #CED4DA; color: #ADB5BD; font-size: 0.95rem; opacity: 0.6;
        margin-bottom: 10px; box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);
    }
    /* 동물 카드 레이아웃 (해금 상태) */
    .animal-card-unlocked {
        background: #FFFFFF; border-radius: 15px; padding: 15px 10px; text-align: center;
        border: 2px solid #FFD93D; color: #2B2D42; font-size: 0.95rem; font-weight: bold;
        box-shadow: 0 5px 10px rgba(0,0,0,0.05); margin-bottom: 10px;
    }
    .animal-emoji { font-size: 2.2rem; display: block; margin-bottom: 5px; }

    /* 모바일 환경 대응 */
    @media (max-width: 600px) {
        .main-title { font-size: 1.7rem !important; white-space: normal !important; word-break: keep-all; }
        button[kind="primary"] { font-size: 1.2rem !important; padding: 15px 0 !important; border-radius: 15px !important; }
        div[data-testid="column"] { min-width: 0 !important; }
        div[data-testid="stHorizontalBlock"] { flex-wrap: nowrap !important; gap: 6px !important; }
    }
    </style>
""", unsafe_allow_html=True)

# --- 🏠 화면 상단 로비 구성 ---
st.markdown("<div class='main-title'>🥚수학 게임 대모험🎲</div>", unsafe_allow_html=True)

# 통합 지갑 상태 출력
st.markdown(f"<h3 style='text-align:center; color:#099268; margin-bottom:5px;'>💰 통합 보유 골드: {st.session_state.gold} G</h3>", unsafe_allow_html=True)
st.markdown("<div class='guide-text'>원하는 훈련장에 입장하여 동물을 부화시킬 골드를 모으세요!</div>", unsafe_allow_html=True)

# 게임 페이지 전환 단추 배치 (2열 레이아웃)
col1, col2 = st.columns(2)
with col1:
    if st.button("⚔️ 역곱셈 게임 입장", use_container_width=True, type="primary"):
        st.switch_page("pages/1_역곱셈_게임.py")

with col2:
    if st.button("🏹 나눗셈 게임 입장", use_container_width=True, type="primary"):
        st.switch_page("pages/2_나눗셈_게임.py")

st.write("---")

# --- 🦁 하단 통합 수집 도감 시스템 ---
st.markdown("### 🦁 나의 신비한 동물 도감")
st.write(f"📊 **전체 마스터 등급 수집률:** {len(st.session_state.my_collection)} / {len(all_animals)} 마리 획득 완료")

# [개발용 시뮬레이터] 테스트 버튼 구성
if st.button("🧪 시뮬레이터: 무작위 동물 1종 강제 해금 테스트", use_container_width=True, type="secondary"):
    chosen = random.choice(all_animals)
    st.session_state.my_collection.add(chosen)
    st.success(f"🎉 신비의 알 부화 성공! 도감에 [ {chosen} ] 가 기록되었습니다.")
    time.sleep(1)
    st.rerun()

# 탭 기능으로 두 게임의 도감을 깔끔하게 분리
tab1, tab2 = st.tabs(["🐣 역곱셈 도감 (육지 동물)", "🤿 나눗셈 도감 (바다·곤충)"])

# 함수: 도감 바둑판 그리드를 그려주는 로직
def draw_zoo_grid(animal_dict):
    for tier, title_list in animal_dict.items():
        st.markdown(f"<div class='tier-title'>{tier}</div>", unsafe_allow_html=True)
        cols = st.columns(4)
        for idx, animal_string in enumerate(title_list):
            col_target = cols[idx % 4]
            
            # 아이콘과 이름 분리
            emoji = animal_string.split()[0]
            name = animal_string.split()[-1]
            
            # 세션 상태 대조 (역곱셈/나눗셈 게임 페이지에서 저장할 때 쓰인 문자열 그대로 체크)
            if animal_string in st.session_state.my_collection:
                card_html = f"""
                <div class='animal-card-unlocked'>
                    <span class='animal-emoji'>{emoji}</span>
                    {name}
                </div>
                """
            else:
                card_html = f"""
                <div class='animal-card-locked'>
                    <span class='animal-emoji' style='filter: grayscale(100%);'>❓</span>
                    🔒 미획득
                </div>
                """
            col_target.markdown(card_html, unsafe_allow_html=True)

# 각 탭에 맞게 도감 출력
with tab1:
    draw_zoo_grid(multiply_animals)

with tab2:
    draw_zoo_grid(divide_animals)

# 하단 공백 확보용 마무리 마진
st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)

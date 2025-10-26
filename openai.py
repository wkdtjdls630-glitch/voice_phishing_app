import streamlit as st
from openai import OpenAI
import json
from datetime import datetime

# 페이지 설정
st.set_page_config(page_title="보이스피싱 예방 시뮬레이션", layout="wide")

# OpenAI 클라이언트 초기화
if 'client' not in st.session_state:
    st.session_state.client = None

# OpenAI API 키 설정 (사이드바에서 입력받기)
with st.sidebar:
    st.header("⚙️ 설정")
    api_key = st.text_input("OpenAI API Key", type="password")
    if api_key:
        st.session_state.client = OpenAI(api_key=api_key)
    
    st.markdown("---")
    st.markdown("### 사용 방법")
    st.markdown("""
    1. API 키 입력
    2. 사용자 정보 입력
    3. AI가 맞춤 시나리오 생성
    4. 시뮬레이션 진행
    5. 결과 분석 확인
    """)

# 세션 상태 초기화
if 'page' not in st.session_state:
    st.session_state.page = 'intro'
if 'user_info' not in st.session_state:
    st.session_state.user_info = {}
if 'scenario' not in st.session_state:
    st.session_state.scenario = None
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'current_step' not in st.session_state:
    st.session_state.current_step = 0
if 'responses' not in st.session_state:
    st.session_state.responses = []

# AI를 사용한 시나리오 생성 함수
def generate_scenario(user_info):
    """사용자 정보를 바탕으로 맞춤형 보이스피싱 시나리오 생성"""
    
    prompt = f"""
당신은 보이스피싱 예방 교육 전문가입니다. 다음 사용자 정보를 바탕으로 가장 취약할 수 있는 보이스피싱 시나리오를 생성하세요.

사용자 정보:
- 성별: {user_info['gender']}
- 나이: {user_info['age']}세
- 자녀 유무: {'있음' if user_info['has_children'] else '없음'}
- 직업: {user_info['occupation']}

요구사항:
1. 이 사용자가 가장 취약할 만한 현실적인 보이스피싱 상황 1개를 선택하세요
2. 5단계의 대화 흐름을 만드세요
3. 각 단계마다 사기범의 대사와 3개의 선택지를 제공하세요
4. 각 선택지에는 위험도(low/medium/high)와 설명을 포함하세요

JSON 형식으로 응답하세요:
{{
  "scenario_name": "시나리오 이름",
  "scenario_description": "왜 이 사용자가 이 시나리오에 취약한지 설명",
  "risk_level": "high",
  "steps": [
    {{
      "step_number": 1,
      "scammer_message": "사기범의 대사",
      "context": "상황 설명",
      "options": [
        {{
          "text": "선택지 1",
          "risk": "low/medium/high",
          "explanation": "이 선택이 왜 좋거나 나쁜지 설명"
        }}
      ]
    }}
  ]
}}
"""
    
    try:
        client = st.session_state.client
        if not client:
            st.error("OpenAI API 키를 먼저 입력해주세요.")
            return None
            
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "당신은 보이스피싱 예방 교육 전문가입니다. 항상 JSON 형식으로 응답합니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        scenario = json.loads(response.choices[0].message.content)
        return scenario
    except Exception as e:
        st.error(f"시나리오 생성 중 오류 발생: {str(e)}")
        return None

# AI를 사용한 응답 분석 함수
def analyze_response(user_info, scenario, responses):
    """사용자의 응답을 분석하고 피드백 생성"""
    
    prompt = f"""
다음 보이스피싱 시뮬레이션 결과를 분석하고 상세한 피드백을 제공하세요.

사용자 정보:
- 나이: {user_info['age']}세
- 직업: {user_info['occupation']}

시나리오: {scenario['scenario_name']}

사용자의 응답:
{json.dumps(responses, indent=2, ensure_ascii=False)}

다음 내용을 JSON 형식으로 제공하세요:
{{
  "overall_score": 0-100점,
  "risk_assessment": "전체적인 위험도 평가",
  "strengths": ["잘한 점 목록"],
  "weaknesses": ["개선할 점 목록"],
  "detailed_feedback": [
    {{
      "step": 1,
      "your_choice": "사용자가 선택한 답변",
      "risk_level": "선택의 위험도",
      "feedback": "이 선택에 대한 상세 피드백",
      "better_choice": "더 나은 선택이 있었다면"
    }}
  ],
  "prevention_tips": ["이 유형의 사기를 예방하는 구체적인 방법들"],
  "warning_signs": ["이 시나리오에서 주의해야 할 경고 신호들"]
}}
"""
    
    try:
        client = st.session_state.client
        if not client:
            st.error("OpenAI API 키를 먼저 입력해주세요.")
            return None
            
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "당신은 보이스피싱 예방 교육 전문가입니다. 항상 JSON 형식으로 응답합니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        analysis = json.loads(response.choices[0].message.content)
        return analysis
    except Exception as e:
        st.error(f"분석 중 오류 발생: {str(e)}")
        return None

# 페이지 1: 사용자 정보 입력
def show_intro_page():
    st.title("🛡️ 보이스피싱 예방 시뮬레이션")
    st.markdown("### 실전처럼 배우는 보이스피싱 대응법")
    
    st.info("💡 당신의 정보를 바탕으로 AI가 맞춤형 보이스피싱 시나리오를 생성합니다.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        gender = st.selectbox("성별", ["남성", "여성", "기타"])
        age = st.number_input("나이", min_value=10, max_value=100, value=30)
        has_children = st.checkbox("자녀가 있습니까?")
    
    with col2:
        occupation = st.selectbox(
            "직업",
            ["학생", "직장인", "자영업", "주부", "은퇴/무직", "프리랜서", "기타"]
        )
        tech_literacy = st.select_slider(
            "디지털 기기 사용 능숙도",
            options=["매우 낮음", "낮음", "보통", "높음", "매우 높음"],
            value="보통"
        )
    
    st.markdown("---")
    
    if not api_key:
        st.warning("⚠️ 사이드바에서 OpenAI API 키를 입력해주세요.")
        return
    
    if not st.session_state.client:
        st.error("OpenAI 클라이언트가 초기화되지 않았습니다.")
        return
    
    if st.button("🚀 시뮬레이션 시작", type="primary", use_container_width=True):
        st.session_state.user_info = {
            'gender': gender,
            'age': age,
            'has_children': has_children,
            'occupation': occupation,
            'tech_literacy': tech_literacy
        }
        
        with st.spinner("당신에게 맞는 시나리오를 생성하고 있습니다..."):
            scenario = generate_scenario(st.session_state.user_info)
            
            if scenario:
                st.session_state.scenario = scenario
                st.session_state.page = 'simulation'
                st.rerun()

# 페이지 2: 시뮬레이션
def show_simulation_page():
    scenario = st.session_state.scenario
    current_step = st.session_state.current_step
    
    # 진행률 표시
    progress = (current_step) / len(scenario['steps'])
    st.progress(progress)
    st.caption(f"진행률: {current_step}/{len(scenario['steps'])} 단계")
    
    # 시나리오 정보
    with st.expander("📋 시나리오 정보", expanded=False):
        st.write(f"**시나리오:** {scenario['scenario_name']}")
        st.write(f"**설명:** {scenario['scenario_description']}")
        st.write(f"**위험도:** {scenario['risk_level'].upper()}")
    
    st.markdown("---")
    
    # 대화 기록 표시
    st.subheader("📞 통화 중...")
    
    for i, response in enumerate(st.session_state.responses):
        step_data = scenario['steps'][i]
        
        # 사기범 메시지
        st.markdown(f"""
        <div style='background-color: #ffebee; padding: 15px; border-radius: 10px; margin: 10px 0;'>
            <strong>🎭 사기범:</strong><br>{step_data['scammer_message']}
        </div>
        """, unsafe_allow_html=True)
        
        # 사용자 응답
        st.markdown(f"""
        <div style='background-color: #e3f2fd; padding: 15px; border-radius: 10px; margin: 10px 0;'>
            <strong>👤 나:</strong><br>{response['text']}
        </div>
        """, unsafe_allow_html=True)
    
    # 현재 단계
    if current_step < len(scenario['steps']):
        step_data = scenario['steps'][current_step]
        
        # 새로운 사기범 메시지
        st.markdown(f"""
        <div style='background-color: #ffebee; padding: 15px; border-radius: 10px; margin: 10px 0;'>
            <strong>🎭 사기범:</strong><br>{step_data['scammer_message']}
        </div>
        """, unsafe_allow_html=True)
        
        if 'context' in step_data:
            st.info(f"💭 {step_data['context']}")
        
        st.markdown("### 어떻게 대응하시겠습니까?")
        
        # 선택지
        for idx, option in enumerate(step_data['options']):
            if st.button(
                option['text'],
                key=f"option_{current_step}_{idx}",
                use_container_width=True
            ):
                # 응답 저장
                st.session_state.responses.append({
                    'step': current_step,
                    'text': option['text'],
                    'risk': option['risk'],
                    'explanation': option['explanation']
                })
                st.session_state.current_step += 1
                
                # 마지막 단계면 분석 페이지로
                if st.session_state.current_step >= len(scenario['steps']):
                    st.session_state.page = 'analysis'
                
                st.rerun()
    
    # 처음부터 다시 시작
    st.markdown("---")
    if st.button("🔄 처음부터 다시 시작"):
        st.session_state.page = 'intro'
        st.session_state.current_step = 0
        st.session_state.responses = []
        st.session_state.scenario = None
        st.rerun()

# 페이지 3: 결과 분석
def show_analysis_page():
    st.title("📊 시뮬레이션 결과 분석")
    
    with st.spinner("AI가 당신의 응답을 분석하고 있습니다..."):
        analysis = analyze_response(
            st.session_state.user_info,
            st.session_state.scenario,
            st.session_state.responses
        )
    
    if not analysis:
        st.error("분석을 생성할 수 없습니다.")
        return
    
    # 전체 점수
    score = analysis.get('overall_score', 0)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("종합 점수", f"{score}점")
    
    with col2:
        risk_color = {"low": "🟢", "medium": "🟡", "high": "🔴"}
        avg_risk = sum(1 for r in st.session_state.responses if r['risk'] == 'high')
        risk_label = "높음" if avg_risk > 2 else "보통" if avg_risk > 0 else "낮음"
        st.metric("위험 수준", risk_label)
    
    with col3:
        correct = sum(1 for r in st.session_state.responses if r['risk'] == 'low')
        st.metric("안전한 선택", f"{correct}/{len(st.session_state.responses)}")
    
    st.markdown("---")
    
    # 전체 평가
    st.subheader("📝 전체 평가")
    st.write(analysis.get('risk_assessment', ''))
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ✅ 잘한 점")
        for strength in analysis.get('strengths', []):
            st.success(f"✓ {strength}")
    
    with col2:
        st.markdown("### ⚠️ 개선할 점")
        for weakness in analysis.get('weaknesses', []):
            st.warning(f"• {weakness}")
    
    st.markdown("---")
    
    # 단계별 상세 분석
    st.subheader("🔍 단계별 상세 분석")
    
    for feedback in analysis.get('detailed_feedback', []):
        with st.expander(f"**{feedback['step']}단계: {feedback['your_choice']}**"):
            risk_emoji = {"low": "🟢", "medium": "🟡", "high": "🔴"}
            st.markdown(f"{risk_emoji.get(feedback['risk_level'], '⚪')} **위험도: {feedback['risk_level']}**")
            st.write(feedback['feedback'])
            
            if 'better_choice' in feedback and feedback['better_choice']:
                st.info(f"💡 더 나은 선택: {feedback['better_choice']}")
    
    st.markdown("---")
    
    # 예방 팁
    st.subheader("🛡️ 보이스피싱 예방 가이드")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 예방 방법")
        for tip in analysis.get('prevention_tips', []):
            st.markdown(f"- {tip}")
    
    with col2:
        st.markdown("### 경고 신호")
        for warning in analysis.get('warning_signs', []):
            st.markdown(f"- ⚠️ {warning}")
    
    st.markdown("---")
    
    # 다시 시작
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 다른 시나리오 시작", use_container_width=True):
            st.session_state.page = 'intro'
            st.session_state.current_step = 0
            st.session_state.responses = []
            st.session_state.scenario = None
            st.rerun()
    
    with col2:
        if st.button("📥 결과 다운로드", use_container_width=True):
            # JSON 형식으로 결과 저장
            result_data = {
                'user_info': st.session_state.user_info,
                'scenario': st.session_state.scenario['scenario_name'],
                'responses': st.session_state.responses,
                'analysis': analysis,
                'timestamp': datetime.now().isoformat()
            }
            
            st.download_button(
                "다운로드",
                data=json.dumps(result_data, ensure_ascii=False, indent=2),
                file_name=f"simulation_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

# 메인 라우터
def main():
    page = st.session_state.page
    
    if page == 'intro':
        show_intro_page()
    elif page == 'simulation':
        show_simulation_page()
    elif page == 'analysis':
        show_analysis_page()

if __name__ == "__main__":
    main()
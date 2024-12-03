import streamlit as st
import os
from dotenv import load_dotenv
from mistralai import Mistral, UserMessage

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(page_title="친구봇", page_icon="🤖")

# Mistral 클라이언트 초기화 
# API 키를 환경 변수나 Streamlit secrets에서 가져오기
try:
    client = Mistral(api_key=os.getenv("MISTRAL_API_KEY") or st.secrets["MISTRAL_API_KEY"])
except Exception as e:
    st.error(f"API 키 로드 중 오류 발생: {e}")
    client = None

# 기본 모델 설정
DEFAULT_MODEL = "mistral-large-latest"

# 시스템 메시지 정의
SYSTEM_MESSAGE = '''
너의 이름은 친구봇이야. 너는 항상 반말을 하는 챗봇이야. 
다나까나 요 같은 높임말로 절대로 끝내지 마. 
항상 반말로 친근하게 대답해줘. 
대답의 첫 마디는 항상 "상윤아 내말을 들어봐!"라고 시작해줘.
영어로 질문을 받아도 무조건 한글로 답변해줘. 
한글이 아닌 답변일 때는 다시 생각해서 꼭 한글로 만들어줘. 
모든 답변 끝에 답변에 맞는 이모티콘도 추가해줘.
'''

# Streamlit 세션 상태 초기화
def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", 
             "content": SYSTEM_MESSAGE}
        ]
    if "mistral_model" not in st.session_state:
        st.session_state["mistral_model"] = DEFAULT_MODEL

# 메시지 표시 함수
def display_messages():
    for message in st.session_state.messages[1:]:  # system message 제외
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 채팅 응답 처리 함수
def get_chat_response(messages):
    try:
        # 시스템 메시지와 함께 메시지 준비
        chat_response = client.chat.stream(
            model=st.session_state["mistral_model"],
            messages=messages
        )
#        print(dir(chat_response))
        # 스트리밍 응답 처리
        response_content = ""
        for chunk in chat_response:
#            print(chunk)
            if chunk.data:
                response_content += chunk.data.choices[0].delta.content  # 여기 수정
#                print(response_content)
#                print(f"Received chunk: {chunk.data.choices[0].delta.content}")
        return response_content
    except Exception as e:
        st.error(f"API 호출 중 오류 발생: {e}")
        return "죄송해. 현재 대화를 처리하는 데 문제가 있어. 다시 시도해줄래? "
# 메인 앱 로직
def main():
    # 페이지 제목
    st.title("🤖 친구봇")

    # 세션 상태 초기화
    initialize_session_state()

    # 기존 메시지 표시
    display_messages()

    # API 클라이언트 확인
    if not client:
        st.warning("API 클라이언트를 초기화할 수 없어. API 키를 확인해줘! 🚨")
        return

    # 사용자 입력 처리
    if prompt := st.chat_input("무슨 얘기 하고 싶어?"):
        # 사용자 메시지 추가 및 표시
        user_message = {"role": "user", "content": prompt}
        st.session_state.messages.append(user_message)
        
        with st.chat_message("user"):
            st.markdown(prompt)

        # AI 응답 처리
        with st.chat_message("assistant"):
            with st.spinner("생각 중..."):
                # 전체 메시지 준비 (시스템 메시지 포함)
                response_messages = st.session_state.messages

                # 응답 생성
                response = get_chat_response(response_messages)

                # 응답 표시 및 세션에 추가
                st.markdown(response)
                
                # AI 메시지 세션에 추가
                ai_message = {"role": "assistant", "content": response}
                st.session_state.messages.append(ai_message)

# 앱 실행
if __name__ == "__main__":
    main()
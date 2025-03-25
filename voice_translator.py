import streamlit as st
from dotenv import load_dotenv
import os
import openai
from audiorecorder import audiorecorder
from datetime import datetime
import base64

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

client = openai.OpenAI(api_key=OPENAI_API_KEY)

def STT(speech, language):
    filename='input.mp3'
    speech.export(filename, format="mp3")

    with open(filename, "rb") as audio_file:
        if language == "ko":
            transcription = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file
            )
        else:
            translation = client.audio.translations.create(
                model="whisper-1", 
                file=audio_file
            )
            print(translation.text)

    os.remove(filename)
    return transcription.text + " 한국어로 답변해 주세요." if language == "ko" else translation.text + "and answer in english."

def ask_gpt(prompt, model):
    response = client.chat.completions.create(
        model=model, 
        messages=prompt
    )
    return response.choices[0].message.content


def TTS(text):
    filename = "output.mp3"
    with client.audio.speech.with_streaming_response.create(
        model="tts-1",
        voice="alloy",
        input=text
    ) as response:
        response.stream_to_file(filename)

    with open(filename, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio autoplay="True">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)

    os.remove(filename)


def main():
    st.set_page_config(
        page_title="음성 챗봇 프로그램",
        layout="wide")
    
    st.header("음성 챗봇 프로그램")

    st.markdown("---")

    with st.expander("음성 챗봇 프로그램에 관하여", expanded=True):
        st.write(
        """     
        - 음성 번역 챗봇 프로그램의 UI는 스트림릿을 활용합니다.
        - STT(Speech-To-Text)는 OpenAI의 Whisper를 활용합니다. 
        - 답변은 OpenAI의 GPT 모델을 활용합니다. 
        - TTS(Text-To-Speech)는 OpenAI의 TTS를 활용합니다.
        """
        )

        st.markdown("")

    system_content = "You are a thoughtful assistant. Respond to all input in 25 words and answer in korea"

    if "chat" not in st.session_state:
        st.session_state["chat"] = []

    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "system", "content": system_content}]

    if "check_reset" not in st.session_state:
        st.session_state["check_reset"] = False

    with st.sidebar:
        model = st.radio(label="GPT 모델", options=["gpt-3.5-turbo", "gpt-4o", "gpt-4-turbo"])
        language = st.radio(label="언어", options=["ko", "en"])

        st.markdown("---")

        if st.button(label="초기화"):
            st.session_state["chat"] = []
            st.session_state["messages"] = [{"role": "system", "content": system_content}]
            st.session_state["check_reset"] = True
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("질문하기")

        audio = audiorecorder()
        if (audio.duration_seconds > 0) and (st.session_state["check_reset"]==False):
            st.audio(audio.export().read())

            question = STT(audio, language)
            now = datetime.now().strftime("%H:%M")
            st.session_state["chat"] = st.session_state["chat"] + [("user", now, question)]
            st.session_state["messages"] = st.session_state["messages"] + [{"role": "user", "content": question}]

    with col2:
        st.subheader("질문/답변")

        if  (audio.duration_seconds > 0)  and (st.session_state["check_reset"]==False):
            response = ask_gpt(st.session_state["messages"], model)
            st.session_state["messages"] = st.session_state["messages"] + [{"role": "assistant", "content": response}]
            now = datetime.now().strftime("%H:%M")
            st.session_state["chat"] = st.session_state["chat"] + [("bot", now, response)]

            for sender, time, message in st.session_state["chat"]:
                if sender == "user":
                    st.write(f'<div style="display:flex;align-items:center;"><div style="background-color:#007AFF;color:white;border-radius:12px;padding:8px 12px;margin-right:8px;">{message}</div><div style="font-size:0.8rem;color:gray;">{time}</div></div>', 
                             unsafe_allow_html=True)
                    st.write("")
                else:
                    st.write(f'<div style="display:flex;align-items:center;justify-content:flex-end;"><div style="background-color:lightgray;border-radius:12px;padding:8px 12px;margin-left:8px;">{message}</div><div style="font-size:0.8rem;color:gray;">{time}</div></div>', 
                             unsafe_allow_html=True)
                    st.write("")

            TTS(response)
                    
        else:
            st.session_state["check_reset"] = False

if __name__=="__main__":
    main()
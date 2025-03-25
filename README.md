# 음성 챗봇 프로그램

OpenAI API를 활용한 음성 기반 챗봇 프로그램입니다.

## 주요 기능

- 음성 입력을 텍스트로 변환 (STT - Whisper API)
- GPT를 통한 대화 처리
- 텍스트 응답을 음성으로 변환 (TTS)
- 한국어/영어 지원

## 설치 방법

1. 저장소 클론
```bash
git clone https://github.com/sw326/OpenAiStreamlit.git
```

2. 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

3. 환경 변수 설정
- `.env` 파일을 생성하고 OpenAI API 키를 설정
```
OPENAI_API_KEY=your-api-key
```

4. 실행
```bash
streamlit run voice_translator.py
```

## 사용된 기술
- Streamlit
- OpenAI (Whisper, GPT, TTS)
- Python
# JAPGAME

# 🕹 Unity 프로젝트 - 백엔드 실행 가이드

## 📦 백엔드 실행 순서

1. **가상환경 생성 및 실행**
   ```bash
   해당 폴더로 이동후 shift + 우클릭 에서 powershell실행
   python -m venv venv
   
   source venv/bin/activate  # 윈도우는 venv\Scripts\activate <--처음 사용시
## 필요 패키지 설치
pip install fastapi uvicorn
FastAPI 서버 실행
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

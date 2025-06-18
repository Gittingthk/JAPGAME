# 🎮 JAPGAME

Unity 기반 게임과 FastAPI 백엔드 연동 프로젝트입니다.

---

## 📁 프로젝트 구조

APGAME/
├── backend/ # FastAPI 서버 코드
├── frontend/ # Unity 프로젝트 (Assets, ProjectSettings 등)
└── Build/ # 최종 빌드 결과물 (.exe 포함)


---

## 🚀 백엔드 실행 가이드 (FastAPI)

### 1. 가상환경 생성 및 실행

```bash
# 해당 폴더로 이동 후 PowerShell 실행 (Shift + 우클릭)
python -m venv venv
# 가상환경 활성화 (Windows 기준)
venv\Scripts\activate

pip install fastapi uvicorn


uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

🛠 Unity에서 IP 수정 방법
Unity 에디터에서 프로젝트 열기

Assets/Scripts/ 폴더 내 IP 설정 코드 열기
예:

csharp
Copy
Edit
string serverUrl = "ws://192.168.0.39:8000/ws"; // ← 본인 IP로 수정
저장 후 File > Build Settings > Build를 다시 수행

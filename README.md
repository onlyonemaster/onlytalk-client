# OnlyTalk Windows Client

[![Build Status](https://github.com/onlyonemaster/onlytalk-client/workflows/Build%20OnlyTalk%20Windows%20EXE/badge.svg)](https://github.com/onlyonemaster/onlytalk-client/actions)

OnlyTalk는 카카오톡 친구 자동 추가 및 메시지 전송을 위한 Windows 클라이언트입니다.

## 🎉 v2.0 주요 기능

### ✨ 이미지 인식 기술
- OpenCV를 활용한 '사람+' 아이콘 자동 검색
- 창 크기나 해상도에 상관없이 작동
- 다양한 confidence 레벨로 안정적 검색 (90%, 80%, 70%, 60%)

### 💪 강화된 창 관리
- Windows API(pywin32)를 사용한 강력한 창 활성화
- 매 작업 후 카카오톡 창을 자동으로 최상단으로 이동
- 터미널을 클릭해도 작업 중단 없음

### 🔧 향상된 안정성
- 아이콘을 찾지 못하면 자동으로 기본 좌표 사용
- 에러 발생 시에도 창 관리 유지

## 📦 시스템 요구사항

- Windows 10 이상
- Python 3.10 이상
- 카카오톡 (Windows용)

## 🚀 설치 및 사용

### 방법 1: EXE 파일 사용 (권장)

1. [Releases](https://github.com/onlyonemaster/onlytalk-client/releases) 페이지에서 최신 버전 다운로드
2. `OnlyTalkSetup-YYYYMMDD-vX.X.exe` 실행
3. 라이선스 키 입력 후 사용

### 방법 2: 소스코드에서 실행

```bash
# 1. 저장소 클론
git clone https://github.com/onlyonemaster/onlytalk-client.git
cd onlytalk-client

# 2. 패키지 설치
pip install -r requirements.txt

# 3. 실행
python client_main.py
```

## 📋 필요한 패키지

- requests - 서버 API 통신
- flask, flask-cors - 로컬 웹 대시보드
- pyautogui - GUI 자동화
- pyperclip - 클립보드 관리
- pygetwindow - 창 관리
- pywin32 - Windows API
- opencv-python - 이미지 인식
- numpy - 이미지 처리

## 🔧 개발

### 로컬 빌드

```bash
# PyInstaller로 EXE 생성
pyinstaller --onefile --windowed --name "OnlyTalk" client_main.py
```

### GitHub Actions로 자동 빌드

1. 버전 태그 생성 및 푸시:
```bash
git tag v2.0
git push origin v2.0
```

2. 또는 GitHub Actions 탭에서 수동 실행:
   - `Actions` → `Build OnlyTalk Windows EXE` → `Run workflow`
   - 버전 입력 (예: v2.0)

3. 빌드 완료 후 [Releases](https://github.com/onlyonemaster/onlytalk-client/releases)에서 다운로드

## 📁 프로젝트 구조

```
onlytalk-client/
├── .github/
│   └── workflows/
│       └── build-exe.yml       # GitHub Actions 워크플로우
├── templates/
│   └── index.html              # 웹 대시보드 UI
├── app.py                      # Flask 서버 (v2.0)
├── client_main.py              # 메인 진입점
├── installer.py                # 설치 스크립트
├── person_plus_icon.png        # 이미지 인식용 아이콘
├── kakao_friends.csv           # 친구 목록 샘플
├── START_ONLYTALK.bat          # 실행 배치 파일
├── README_CLIENT.md            # 사용자 가이드
├── requirements.txt            # Python 패키지 목록
└── README.md                   # 프로젝트 문서
```

## ⚠️ 주의사항

1. **카카오톡 정책 준수**
   - 하루 100~200명 이하 추가 권장
   - 딜레이 시간 1.5초 이상 권장
   - 분산 작업 (여러 날에 걸쳐)

2. **라이선스**
   - 1개 라이선스 = 1대 PC
   - 라이선스는 https://only-talk.kiam.kr 에서 구매

3. **작업 중 주의**
   - 작업 중에는 마우스/키보드 사용 금지
   - 카카오톡 창이 보이도록 배치

## 📞 지원

- 웹사이트: https://only-talk.kiam.kr
- 이메일: support@only-talk.kiam.kr

## 📝 업데이트 히스토리

### v2.0 (2025-12-23)
- ✅ 이미지 인식으로 '사람+' 아이콘 자동 검색
- ✅ 창 활성화 강화 (Windows API 사용)
- ✅ 매 작업 후 창 최상단 이동
- ✅ opencv-python 패키지 추가
- ✅ 다양한 해상도/창 크기 지원

### v1.0 (2025-12-20)
- 서버 연동 라이선스 검증
- 구글 시트 연동
- 웹 대시보드 인터페이스
- 기본 친구 추가 + 메시지 전송

---

**작성자:** 아리 (Claude Code)
**라이선스:** Proprietary
**최종 업데이트:** 2025-12-23

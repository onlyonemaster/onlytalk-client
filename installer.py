"""
OnlyTalk 설치 프로그램
사용자 플로우:
1. 설치 시 대시보드 오픈 (CMD 미오픈, 특정 메뉴만 작동)
2. 특정 메뉴 클릭 시 자동으로:
   - 카톡 실행 확인
   - CMD 오픈
   - python app.py 자동 실행
3. 모든 기능 정상화
"""
import os
import sys
import shutil
import subprocess
import webbrowser
from pathlib import Path

class OnlyTalkInstaller:
    def __init__(self):
        self.install_dir = Path.home() / "OnlyTalk"
        self.app_running = False

    def install(self):
        """설치 진행"""
        print("=" * 60)
        print("  OnlyTalk 설치")
        print("=" * 60)

        # 1. 설치 디렉토리 생성
        self.install_dir.mkdir(parents=True, exist_ok=True)
        print(f"✓ 설치 경로: {self.install_dir}")

        # 2. 필요한 파일 복사
        files_to_copy = [
            "client_main.py",
            "app.py",
            "kakao_friends.csv",
            "README_CLIENT.md"
        ]

        for file in files_to_copy:
            if os.path.exists(file):
                shutil.copy(file, self.install_dir / file)
                print(f"✓ {file} 복사 완료")

        # templates 폴더 복사
        if os.path.exists("templates"):
            shutil.copytree("templates", self.install_dir / "templates", dirs_exist_ok=True)
            print("✓ templates 폴더 복사 완료")

        # 3. 바탕화면 바로가기 생성
        self.create_shortcut()

        # 4. 설정 파일 생성
        self.create_launcher()

        print("\n✓ 설치 완료!")
        print(f"설치 경로: {self.install_dir}")

        # 5. 대시보드 열기 (CMD 미오픈 상태)
        print("\n대시보드를 엽니다...")
        self.open_dashboard_limited()

    def create_shortcut(self):
        """바탕화면 바로가기 생성"""
        desktop = Path.home() / "Desktop"
        shortcut_path = desktop / "OnlyTalk.lnk"

        try:
            import win32com.client
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(str(shortcut_path))
            shortcut.TargetPath = str(self.install_dir / "OnlyTalk_Launcher.bat")
            shortcut.WorkingDirectory = str(self.install_dir)
            shortcut.IconLocation = str(self.install_dir / "client_main.py")
            shortcut.save()
            print("✓ 바탕화면 바로가기 생성 완료")
        except:
            print("⚠ 바로가기 생성 실패 (수동으로 생성하세요)")

    def create_launcher(self):
        """실행 스크립트 생성"""
        launcher_bat = self.install_dir / "OnlyTalk_Launcher.bat"
        launcher_content = f"""@echo off
chcp 65001 >nul
cd /d "{self.install_dir}"
python client_main.py
pause
"""
        launcher_bat.write_text(launcher_content, encoding='utf-8')
        print("✓ 실행 스크립트 생성 완료")

        # 카톡 자동 실행 스크립트
        kakao_launcher = self.install_dir / "Start_KakaoTalk.bat"
        kakao_content = """@echo off
echo 카카오톡을 실행합니다...
start "" "C:\\Program Files (x86)\\Kakao\\KakaoTalk\\KakaoTalk.exe"
if not exist "C:\\Program Files (x86)\\Kakao\\KakaoTalk\\KakaoTalk.exe" (
    start "" "C:\\Program Files\\Kakao\\KakaoTalk\\KakaoTalk.exe"
)
"""
        kakao_launcher.write_text(kakao_content)

        # 앱 자동 실행 스크립트
        app_launcher = self.install_dir / "Start_Dashboard.bat"
        app_content = f"""@echo off
chcp 65001 >nul
cd /d "{self.install_dir}"
echo 대시보드를 시작합니다...
echo http://localhost:5000 에 접속하세요.
python app.py
"""
        app_launcher.write_text(app_content, encoding='utf-8')
        print("✓ 자동 실행 스크립트 생성 완료")

    def open_dashboard_limited(self):
        """제한된 대시보드 열기 (CMD 미오픈 상태)"""
        # 간단한 HTML 페이지를 열어서 안내
        limited_html = self.install_dir / "limited_dashboard.html"
        html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>OnlyTalk - 설치 완료</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 100px auto;
            padding: 40px;
            background: linear-gradient(135deg, #FEE500 0%, #FDD400 100%);
            text-align: center;
        }}
        .card {{
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        h1 {{ color: #333; }}
        .btn {{
            display: inline-block;
            background: #FEE500;
            color: #333;
            padding: 15px 30px;
            margin: 20px 0;
            border-radius: 8px;
            text-decoration: none;
            font-weight: bold;
            font-size: 18px;
        }}
        .btn:hover {{ background: #FDD400; }}
        .instructions {{
            text-align: left;
            margin: 30px 0;
            line-height: 1.8;
        }}
    </style>
</head>
<body>
    <div class="card">
        <h1>🎉 OnlyTalk 설치 완료!</h1>
        <p>카카오톡 친구 자동 추가 서비스가 설치되었습니다.</p>

        <div class="instructions">
            <h3>📝 시작 방법:</h3>
            <ol>
                <li>카카오톡이 실행 중인지 확인하세요</li>
                <li>아래 버튼을 클릭하여 서비스를 시작하세요</li>
                <li>자동으로 대시보드가 열립니다</li>
            </ol>
        </div>

        <a href="#" class="btn" onclick="startService()">🚀 서비스 시작하기</a>

        <p style="color: #666; margin-top: 30px; font-size: 14px;">
            설치 경로: {self.install_dir}
        </p>
    </div>

    <script>
        function startService() {{
            // 사용자에게 안내
            alert('카카오톡과 대시보드를 시작합니다.\\n\\n잠시만 기다려주세요...');

            // 카톡 실행
            window.location.href = 'file:///{self.install_dir}/Start_KakaoTalk.bat';

            // 2초 후 앱 실행
            setTimeout(function() {{
                window.location.href = 'file:///{self.install_dir}/Start_Dashboard.bat';
            }}, 2000);

            // 5초 후 대시보드 열기
            setTimeout(function() {{
                window.location.href = 'http://localhost:5000';
            }}, 5000);
        }}
    </script>
</body>
</html>"""
        limited_html.write_text(html_content, encoding='utf-8')

        # 브라우저에서 열기
        webbrowser.open(str(limited_html))
        print(f"✓ 안내 페이지를 열었습니다: {limited_html}")

if __name__ == "__main__":
    installer = OnlyTalkInstaller()
    installer.install()

    input("\n설치가 완료되었습니다. Enter를 눌러 종료하세요...")

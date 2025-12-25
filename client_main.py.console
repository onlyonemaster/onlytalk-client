"""
OnlyTalk Windows 클라이언트
작성자: 아리 (Claude Code)
날짜: 2025-12-20

서버 연동 버전 - 라이선스 검증 및 구글 시트 데이터 불러오기
"""

import sys
import os
import requests
import json
import subprocess
import time
import uuid
from pathlib import Path

# 설정
API_BASE_URL = "https://only-talk.kiam.kr/api"
CONFIG_FILE = "onlytalk_config.json"

class OnlyTalkClient:
    def __init__(self):
        self.license_key = None
        self.device_id = self.get_device_id()
        self.config = self.load_config()

    def get_device_id(self):
        """기기 고유 ID 생성"""
        # Windows 컴퓨터 이름과 MAC 주소 조합
        computer_name = os.environ.get('COMPUTERNAME', 'UNKNOWN')
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                       for elements in range(0,8*6,8)][::-1])
        return f"{computer_name}-{mac}"

    def load_config(self):
        """설정 파일 로드"""
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        return {}

    def save_config(self, config):
        """설정 파일 저장"""
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        self.config = config

    def verify_license(self, license_key):
        """라이선스 검증"""
        try:
            response = requests.post(
                f"{API_BASE_URL}/licenses/verify/",
                json={
                    "license_key": license_key,
                    "device_id": self.device_id
                },
                timeout=10,
                verify=False  # 개발 환경에서는 SSL 검증 비활성화
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('valid'):
                    print(f"✓ 라이선스 인증 성공!")
                    print(f"  사용자: {data['license']['user']}")
                    print(f"  플랜: {data['license']['plan']}")
                    print(f"  만료일: {data['license']['expires_at']}")
                    return True, data
                else:
                    print(f"✗ 라이선스 인증 실패: {data.get('message')}")
                    return False, data
            else:
                print(f"✗ 서버 오류: {response.status_code}")
                return False, None

        except requests.exceptions.RequestException as e:
            print(f"✗ 네트워크 오류: {e}")
            return False, None

    def download_google_sheet_data(self, sheet_url):
        """구글 시트에서 CSV 데이터 다운로드"""
        try:
            # 구글 시트 URL을 CSV export URL로 변환
            if '/edit' in sheet_url:
                sheet_id = sheet_url.split('/d/')[1].split('/')[0]
                export_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
            else:
                export_url = sheet_url

            response = requests.get(export_url, timeout=10)
            response.encoding = 'utf-8'

            if response.status_code == 200:
                # CSV 파일로 저장
                with open('kakao_friends.csv', 'w', encoding='utf-8') as f:
                    f.write(response.text)

                lines = response.text.strip().split('\n')
                print(f"✓ 구글 시트에서 {len(lines)}명의 데이터 다운로드 완료")
                return True
            else:
                print(f"✗ 구글 시트 다운로드 실패: {response.status_code}")
                return False

        except Exception as e:
            print(f"✗ 구글 시트 다운로드 오류: {e}")
            return False

    def start_flask_server(self):
        """Flask 웹 서버 시작"""
        print("\n🌐 웹 대시보드를 시작합니다...")
        print("   접속 주소: http://localhost:5000")
        print("   종료하려면 이 창을 닫으세요.\n")

        # Flask 서버 실행
        subprocess.Popen([sys.executable, "app.py"])

        # 브라우저 자동 실행
        time.sleep(2)
        os.system("start http://localhost:5000")

    def run(self):
        """메인 실행"""
        print("=" * 60)
        print("  OnlyTalk - 카카오톡 친구 자동 추가 클라이언트")
        print("=" * 60)
        print()

        # 1. 라이선스 확인
        if 'license_key' in self.config:
            self.license_key = self.config['license_key']
            print(f"저장된 라이선스: {self.license_key}")
        else:
            print("라이선스 키가 등록되지 않았습니다.")
            self.license_key = input("라이선스 키를 입력하세요: ").strip()

        # 2. 라이선스 검증
        print(f"\n기기 ID: {self.device_id}")
        print("라이선스 인증 중...")

        valid, license_data = self.verify_license(self.license_key)

        if not valid:
            print("\n✗ 라이선스 인증 실패!")
            print("   https://only-talk.kiam.kr 에서 라이선스를 구매하세요.")
            input("\nEnter를 눌러 종료...")
            return

        # 3. 설정 저장
        self.config['license_key'] = self.license_key
        self.config['device_id'] = self.device_id
        self.save_config(self.config)

        # 4. 구글 시트 URL 확인 (선택사항)
        print("\n" + "=" * 60)
        if 'google_sheet_url' in self.config:
            print(f"구글 시트 URL: {self.config['google_sheet_url']}")
            update = input("구글 시트 URL을 변경하시겠습니까? (y/N): ").strip().lower()
            if update == 'y':
                sheet_url = input("새 구글 시트 URL: ").strip()
                self.config['google_sheet_url'] = sheet_url
                self.save_config(self.config)
        else:
            print("구글 시트 URL이 등록되지 않았습니다.")
            print("로컬 CSV 파일(kakao_friends.csv)을 사용하거나 구글 시트를 연동할 수 있습니다.")
            use_sheet = input("구글 시트를 사용하시겠습니까? (y/N): ").strip().lower()
            if use_sheet == 'y':
                sheet_url = input("구글 시트 URL을 입력하세요: ").strip()
                self.config['google_sheet_url'] = sheet_url
                self.save_config(self.config)

        # 5. 구글 시트 데이터 다운로드
        if 'google_sheet_url' in self.config:
            print("\n구글 시트 데이터 다운로드 중...")
            self.download_google_sheet_data(self.config['google_sheet_url'])

        # 6. Flask 웹 대시보드 실행
        print("\n" + "=" * 60)
        self.start_flask_server()

if __name__ == "__main__":
    # Windows 인코딩 설정 (PyInstaller 호환)
    if sys.platform == 'win32':
        try:
            import io
            # stdout/stderr가 None이 아닐 때만 설정
            if hasattr(sys.stdout, 'buffer') and sys.stdout.buffer is not None:
                sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
            if hasattr(sys.stderr, 'buffer') and sys.stderr.buffer is not None:
                sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
        except (AttributeError, TypeError):
            # PyInstaller로 빌드된 경우 무시
            pass

    # SSL 경고 무시
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    client = OnlyTalkClient()
    client.run()

"""
OnlyTalk Windows 클라이언트 (GUI 버전)
작성자: 아리 (Claude Code)
날짜: 2025-12-25

서버 연동 버전 - 라이선스 검증 및 구글 시트 데이터 불러오기
PyInstaller --windowed 호환
"""

import sys
import os
import requests
import json
import subprocess
import time
import uuid
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, simpledialog

# 설정
API_BASE_URL = "https://only-talk.kiam.kr/api"
CONFIG_FILE = "onlytalk_config.json"

class OnlyTalkClient:
    def __init__(self):
        self.license_key = None
        self.device_id = self.get_device_id()
        self.config = self.load_config()
        # Tkinter root 창 (숨김)
        self.root = tk.Tk()
        self.root.withdraw()

    def get_device_id(self):
        """기기 고유 ID 생성"""
        computer_name = os.environ.get('COMPUTERNAME', 'UNKNOWN')
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                       for elements in range(0,8*6,8)][::-1])
        return f"{computer_name}-{mac}"

    def load_config(self):
        """설정 파일 로드"""
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def save_config(self, config):
        """설정 파일 저장"""
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        self.config = config

    def show_message(self, title, message, type='info'):
        """메시지 박스 표시"""
        if type == 'info':
            messagebox.showinfo(title, message)
        elif type == 'error':
            messagebox.showerror(title, message)
        elif type == 'warning':
            messagebox.showwarning(title, message)

    def get_input(self, title, prompt, initial=''):
        """입력 대화상자"""
        return simpledialog.askstring(title, prompt, initialvalue=initial)

    def ask_yes_no(self, title, message):
        """예/아니오 대화상자"""
        return messagebox.askyesno(title, message)

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
                verify=False
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('valid'):
                    return True, data
                else:
                    return False, data
            else:
                return False, None

        except requests.exceptions.RequestException as e:
            self.show_message("네트워크 오류", f"서버 연결 실패: {e}", 'error')
            return False, None

    def download_google_sheet_data(self, sheet_url):
        """구글 시트에서 CSV 데이터 다운로드"""
        try:
            if '/edit' in sheet_url:
                sheet_id = sheet_url.split('/d/')[1].split('/')[0]
                export_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
            else:
                export_url = sheet_url

            response = requests.get(export_url, timeout=10)
            response.encoding = 'utf-8'

            if response.status_code == 200:
                with open('kakao_friends.csv', 'w', encoding='utf-8') as f:
                    f.write(response.text)
                lines = response.text.strip().split('\n')
                self.show_message("성공", f"구글 시트에서 {len(lines)}명의 데이터 다운로드 완료")
                return True
            else:
                self.show_message("오류", f"구글 시트 다운로드 실패: {response.status_code}", 'error')
                return False

        except Exception as e:
            self.show_message("오류", f"구글 시트 다운로드 오류: {e}", 'error')
            return False

    def start_flask_server(self):
        """Flask 웹 서버 시작"""
        # Flask 서버 실행
        creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        subprocess.Popen([sys.executable, "app.py"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        creationflags=creationflags)

        # 브라우저 자동 실행
        time.sleep(2)
        os.system("start http://localhost:5000")

    def run(self):
        """메인 실행"""
        try:
            # 1. 라이선스 확인
            if 'license_key' in self.config and self.config['license_key']:
                self.license_key = self.config['license_key']
            else:
                # 라이선스 키 입력 요청
                self.license_key = self.get_input(
                    "OnlyTalk 라이선스",
                    "라이선스 키를 입력하세요:\n\nhttps://only-talk.kiam.kr 에서 구매",
                    ""
                )

                if not self.license_key:
                    self.show_message("취소", "라이선스 키가 필요합니다.", 'warning')
                    return

            # 2. 라이선스 검증
            valid, license_data = self.verify_license(self.license_key)

            if not valid:
                error_msg = "라이선스 인증 실패!\n\n"
                if license_data:
                    error_msg += license_data.get('message', '알 수 없는 오류')
                else:
                    error_msg += "서버 연결 실패"
                error_msg += "\n\nhttps://only-talk.kiam.kr 에서\n라이선스를 구매하세요."

                self.show_message("인증 실패", error_msg, 'error')
                return

            # 인증 성공
            success_msg = f"라이선스 인증 성공!\n\n"
            success_msg += f"사용자: {license_data['license']['user']}\n"
            success_msg += f"플랜: {license_data['license']['plan']}\n"
            success_msg += f"만료일: {license_data['license']['expires_at']}"
            self.show_message("인증 성공", success_msg)

            # 3. 설정 저장
            self.config['license_key'] = self.license_key
            self.config['device_id'] = self.device_id
            self.save_config(self.config)

            # 4. 구글 시트 URL 확인 (선택사항)
            if 'google_sheet_url' in self.config and self.config['google_sheet_url']:
                # 기존 URL이 있으면 변경 여부 확인
                if self.ask_yes_no(
                    "구글 시트 설정",
                    f"저장된 구글 시트:\n{self.config['google_sheet_url']}\n\n변경하시겠습니까?"
                ):
                    sheet_url = self.get_input(
                        "구글 시트 URL",
                        "새 구글 시트 URL을 입력하세요:",
                        self.config['google_sheet_url']
                    )
                    if sheet_url:
                        self.config['google_sheet_url'] = sheet_url
                        self.save_config(self.config)
            else:
                # 구글 시트 사용 여부 확인
                if self.ask_yes_no(
                    "구글 시트 연동",
                    "구글 시트를 사용하시겠습니까?\n\n'아니오'를 선택하면 로컬 CSV 파일을 사용합니다."
                ):
                    sheet_url = self.get_input(
                        "구글 시트 URL",
                        "구글 시트 URL을 입력하세요:",
                        ""
                    )
                    if sheet_url:
                        self.config['google_sheet_url'] = sheet_url
                        self.save_config(self.config)

            # 5. 구글 시트 데이터 다운로드
            if 'google_sheet_url' in self.config and self.config['google_sheet_url']:
                self.download_google_sheet_data(self.config['google_sheet_url'])

            # 6. Flask 웹 대시보드 실행
            self.show_message(
                "OnlyTalk 시작",
                "웹 대시보드가 자동으로 열립니다.\n\n주소: http://localhost:5000\n\n종료하려면 시스템 트레이에서\nPython 프로세스를 종료하세요."
            )
            self.start_flask_server()

        except Exception as e:
            self.show_message("오류", f"프로그램 실행 중 오류 발생:\n{str(e)}", 'error')
        finally:
            # Tkinter 종료
            try:
                self.root.destroy()
            except:
                pass

if __name__ == "__main__":
    # SSL 경고 무시
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # 프로그램 실행
    client = OnlyTalkClient()
    client.run()

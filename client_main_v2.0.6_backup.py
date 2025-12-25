"""
OnlyTalk Windows 클라이언트 v2.0.5
Flask 서버를 threading으로 통합
"""
import sys
import os
import requests
import json
import time
import uuid
import tkinter as tk
from tkinter import messagebox, simpledialog
import threading
import webbrowser

# 설정
API_BASE_URL = "https://only-talk.kiam.kr/api"
CONFIG_FILE = "onlytalk_config.json"

class LargeInputDialog(simpledialog.Dialog):
    """큰 입력 대화상자"""
    def __init__(self, parent, title, prompt, initial=''):
        self.prompt = prompt
        self.initial = initial
        self.result = None
        super().__init__(parent, title)

    def body(self, frame):
        label = tk.Label(frame, text=self.prompt, justify=tk.LEFT)
        label.grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)
        self.entry = tk.Entry(frame, width=60)
        self.entry.grid(row=1, column=0, padx=10, pady=10)
        self.entry.insert(0, self.initial)
        return self.entry

    def apply(self):
        self.result = self.entry.get()

class OnlyTalkClient:
    def __init__(self):
        self.license_key = None
        self.device_id = self.get_device_id()
        self.config = self.load_config()
        self.root = tk.Tk()
        self.root.withdraw()
        self.flask_thread = None

    def get_device_id(self):
        computer_name = os.environ.get('COMPUTERNAME', 'UNKNOWN')
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                       for elements in range(0,8*6,8)][::-1])
        return f"{computer_name}-{mac}"

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_config(self, config):
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            self.config = config
        except Exception as e:
            self.show_message("오류", f"설정 저장 실패: {e}", 'error')

    def show_message(self, title, message, type='info'):
        if type == 'info':
            messagebox.showinfo(title, message)
        elif type == 'error':
            messagebox.showerror(title, message)
        elif type == 'warning':
            messagebox.showwarning(title, message)

    def get_input(self, title, prompt, initial=''):
        dialog = LargeInputDialog(self.root, title, prompt, initial)
        return dialog.result

    def ask_yes_no(self, title, message):
        return messagebox.askyesno(title, message)

    def verify_license(self, license_key):
        try:
            response = requests.post(
                f"{API_BASE_URL}/licenses/verify/",
                json={"license_key": license_key, "device_id": self.device_id},
                timeout=10,
                verify=False
            )
            if response.status_code == 200:
                data = response.json()
                return data.get('valid'), data
            return False, None
        except requests.exceptions.RequestException as e:
            self.show_message("네트워크 오류", f"서버 연결 실패:\n{e}", 'error')
            return False, None

    def download_google_sheet_data(self, sheet_url):
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
            self.show_message("오류", f"구글 시트 다운로드 오류:\n{e}", 'error')
            return False

    def start_flask_server_thread(self):
        """Flask 서버를 스레드로 시작"""
        def run_flask():
            # PyInstaller 경로 처리
            if getattr(sys, 'frozen', False):
                bundle_dir = getattr(sys, '_MEIPASS', os.path.dirname(__file__))
            else:
                bundle_dir = os.path.dirname(__file__)

            # app.py 임포트 및 실행
            app_py = os.path.join(bundle_dir, 'app.py')

            if os.path.exists(app_py):
                # app.py를 동적으로 실행
                import importlib.util
                spec = importlib.util.spec_from_file_location("flask_app", app_py)
                flask_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(flask_module)

                # Flask 앱 실행
                flask_module.app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
            else:
                print(f"app.py not found at {app_py}")

        self.flask_thread = threading.Thread(target=run_flask, daemon=True)
        self.flask_thread.start()

        # 서버 시작 대기
        for i in range(15):
            time.sleep(1)
            try:
                response = requests.get("http://localhost:5000", timeout=1)
                if response.status_code in [200, 404]:
                    return True
            except:
                continue

        return False

    def run(self):
        try:
            # 1. 라이선스 확인
            if 'license_key' in self.config and self.config['license_key']:
                self.license_key = self.config['license_key']
            else:
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

            # 4. 구글 시트 URL 확인
            if 'google_sheet_url' in self.config and self.config['google_sheet_url']:
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
                if self.ask_yes_no(
                    "구글 시트 연동",
                    "구글 시트를 사용하시겠습니까?\n\n'아니오'를 선택하면 로컬 CSV 파일을 사용합니다."
                ):
                    sheet_url = self.get_input(
                        "구글 시트 URL",
                        "구글 시트 공유 URL을 입력하세요:\n(예: https://docs.google.com/spreadsheets/d/...)",
                        ""
                    )
                    if sheet_url:
                        self.config['google_sheet_url'] = sheet_url
                        self.save_config(self.config)

            # 5. 구글 시트 데이터 다운로드
            if 'google_sheet_url' in self.config and self.config['google_sheet_url']:
                self.download_google_sheet_data(self.config['google_sheet_url'])

            # 6. Flask 서버 시작
            if self.start_flask_server_thread():
                webbrowser.open("http://localhost:5000")
                self.show_message(
                    "OnlyTalk 시작 완료",
                    "웹 대시보드가 열렸습니다.\n\n주소: http://localhost:5000\n\n종료하려면 이 창을 닫으세요."
                )
                # Tkinter 메인 루프 실행 (창이 닫힐 때까지 대기)
                self.root.deiconify()  # 창 표시
                self.root.title("OnlyTalk - 실행 중")
                self.root.geometry("300x100")
                tk.Label(self.root, text="OnlyTalk이 실행 중입니다.\n이 창을 닫으면 프로그램이 종료됩니다.",
                        font=("맑은 고딕", 10), pady=20).pack()
                tk.Button(self.root, text="종료", command=self.root.destroy,
                         bg="#f44336", fg="white", padx=20, pady=10).pack()
                self.root.mainloop()
            else:
                self.show_message("오류", "Flask 서버 시작 실패", 'error')

        except Exception as e:
            import traceback
            self.show_message("오류", f"프로그램 실행 중 오류:\n\n{str(e)}\n\n{traceback.format_exc()[:200]}", 'error')
        finally:
            try:
                self.root.destroy()
            except:
                pass

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    client = OnlyTalkClient()
    client.run()

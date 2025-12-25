"""
OnlyTalk Windows Client v2.0.7
Flask app and HTML template fully integrated into single file

Changes:
- Integrated Flask routes from app.py into client_main.py
- Embedded HTML template using render_template_string
- PyInstaller --onefile mode for single EXE deployment
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

# Flask and automation
from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
import csv
import pyautogui
import pyperclip
import pygetwindow as gw
import random
from io import StringIO
import win32gui
import win32con
import cv2
import numpy as np

# Configuration
API_BASE_URL = "https://only-talk.kiam.kr/api"
CONFIG_FILE = "onlytalk_config.json"

# HTML Template
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>카카오톡 친구 자동 추가 대시보드</title>
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            background-color: #f8f9fa;
            padding: 20px;
        }
        .dashboard-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .card {
            border: none;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .card-header {
            background-color: #667eea;
            color: white;
            border-radius: 10px 10px 0 0 !important;
            font-weight: bold;
        }
        .log-container {
            background-color: #1e1e1e;
            color: #d4d4d4;
            padding: 15px;
            border-radius: 5px;
            height: 300px;
            overflow-y: auto;
            font-family: 'Consolas', monospace;
            font-size: 13px;
        }
        .log-entry {
            margin-bottom: 5px;
        }
        .log-time {
            color: #858585;
            margin-right: 10px;
        }
        .progress {
            height: 30px;
            font-size: 14px;
        }
        .btn-start {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            padding: 12px 30px;
            font-size: 16px;
        }
        .btn-stop {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            border: none;
            padding: 12px 30px;
            font-size: 16px;
        }
        .friend-table {
            max-height: 400px;
            overflow-y: auto;
        }
        .status-badge {
            font-size: 14px;
            padding: 8px 15px;
        }
    </style>
</head>
<body>
    <div class="container-fluid">
        <!-- 헤더 -->
        <div class="dashboard-header">
            <div class="d-flex justify-content-between align-items-start">
                <div>
                    <h1>🎯 카카오톡 친구 자동 추가 대시보드</h1>
                    <p class="mb-0">구글 시트 데이터를 읽어서 자동으로 친구를 추가하고 메시지를 전송합니다</p>
                </div>
                <button class="btn btn-light btn-lg" onclick="showManual()" style="white-space: nowrap;">
                    📖 이용 매뉴얼
                </button>
            </div>
        </div>

        <div class="row">
            <!-- 왼쪽: 설정 및 컨트롤 -->
            <div class="col-md-6">
                <!-- 구글 시트 설정 -->
                <div class="card">
                    <div class="card-header">
                        📊 구글 시트 설정
                    </div>
                    <div class="card-body">
                        <div class="mb-3">
                            <label class="form-label fw-bold">구글 시트 URL</label>
                            <div class="input-group">
                                <input type="text" class="form-control" id="sheetUrl"
                                       placeholder="https://docs.google.com/spreadsheets/d/...">
                                <button class="btn btn-primary" onclick="updateSheetUrl()">
                                    🔄 적용
                                </button>
                            </div>
                            <small class="text-muted">
                                구글 시트 URL을 입력하면 실시간으로 최신 데이터를 불러옵니다
                            </small>
                        </div>
                        <div class="d-grid">
                            <button class="btn btn-outline-primary btn-sm" onclick="refreshFriends()">
                                🔃 목록 새로고침
                            </button>
                        </div>
                    </div>
                </div>

                <!-- 친구 목록 -->
                <div class="card">
                    <div class="card-header">
                        📋 친구 목록
                    </div>
                    <div class="card-body">
                        <div class="friend-table">
                            <table class="table table-sm table-hover">
                                <thead>
                                    <tr>
                                        <th>번호</th>
                                        <th>이름</th>
                                        <th>전화번호</th>
                                        <th>메시지</th>
                                    </tr>
                                </thead>
                                <tbody id="friendList">
                                    <tr>
                                        <td colspan="4" class="text-center">로딩 중...</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                        <div class="text-end mt-2">
                            <span class="badge bg-primary status-badge" id="totalFriends">총 0명</span>
                        </div>
                    </div>
                </div>

                <!-- 설정 -->
                <div class="card">
                    <div class="card-header">
                        ⚙️ 설정
                    </div>
                    <div class="card-body">
                        <!-- 범위 설정 -->
                        <div class="mb-3">
                            <label class="form-label fw-bold">📍 범위 설정</label>
                            <div class="row">
                                <div class="col-6">
                                    <input type="number" class="form-control" id="startNum" placeholder="시작 번호" value="1" min="1">
                                </div>
                                <div class="col-6">
                                    <input type="number" class="form-control" id="endNum" placeholder="끝 번호" value="1" min="1">
                                </div>
                            </div>
                            <small class="text-muted">예: 시작=5, 끝=10 → 5번부터 10번까지</small>
                        </div>

                        <!-- 랜덤 딜레이 -->
                        <div class="mb-3">
                            <label class="form-label fw-bold">⏰ 랜덤 딜레이 (초)</label>
                            <div class="row">
                                <div class="col-6">
                                    <input type="number" class="form-control" id="delayMin" placeholder="최소" value="5" min="0" step="0.5">
                                </div>
                                <div class="col-6">
                                    <input type="number" class="form-control" id="delayMax" placeholder="최대" value="30" min="0" step="0.5">
                                </div>
                            </div>
                            <small class="text-muted">각 친구 처리 후 대기 시간 (최소~최대 범위에서 랜덤)</small>
                        </div>

                        <!-- 시작/중단 버튼 -->
                        <div class="d-grid gap-2">
                            <button class="btn btn-primary btn-start" id="startBtn" onclick="startTask()">
                                🚀 시작하기
                            </button>
                            <button class="btn btn-danger btn-stop" id="stopBtn" onclick="stopTask()" style="display:none;">
                                ⏹️ 중단하기
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 오른쪽: 진행 상황 및 로그 -->
            <div class="col-md-6">
                <!-- 진행 상황 -->
                <div class="card">
                    <div class="card-header">
                        📊 진행 상황
                    </div>
                    <div class="card-body">
                        <div class="mb-3">
                            <div class="d-flex justify-content-between mb-2">
                                <span id="progressText">대기 중...</span>
                                <span id="progressPercent">0%</span>
                            </div>
                            <div class="progress">
                                <div class="progress-bar progress-bar-striped progress-bar-animated"
                                     id="progressBar"
                                     role="progressbar"
                                     style="width: 0%">
                                </div>
                            </div>
                        </div>

                        <div class="row text-center mt-4">
                            <div class="col-4">
                                <div class="card bg-light">
                                    <div class="card-body">
                                        <h3 class="text-success mb-0" id="successCount">0</h3>
                                        <small class="text-muted">성공</small>
                                    </div>
                                </div>
                            </div>
                            <div class="col-4">
                                <div class="card bg-light">
                                    <div class="card-body">
                                        <h3 class="text-danger mb-0" id="failCount">0</h3>
                                        <small class="text-muted">실패</small>
                                    </div>
                                </div>
                            </div>
                            <div class="col-4">
                                <div class="card bg-light">
                                    <div class="card-body">
                                        <h3 class="text-primary mb-0" id="totalCount">0</h3>
                                        <small class="text-muted">전체</small>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 로그 -->
                <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <span>📝 실시간 로그</span>
                        <button class="btn btn-sm btn-outline-light" onclick="clearLogs()">지우기</button>
                    </div>
                    <div class="card-body p-0">
                        <div class="log-container" id="logContainer">
                            <div class="text-muted">로그가 여기에 표시됩니다...</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- 이용 매뉴얼 모달 -->
    <div class="modal fade" id="manualModal" tabindex="-1" aria-labelledby="manualModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-xl modal-dialog-scrollable">
            <div class="modal-content">
                <div class="modal-header" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                    <h5 class="modal-title" id="manualModalLabel">📖 카카오톡 친구 자동 추가 - 이용 매뉴얼</h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body" style="padding: 30px;">
                    <!-- 매뉴얼 내용 -->
                    <div class="manual-content">
                        <h2>🔹 1단계: 노트북 부팅 및 준비</h2>

                        <h4>1-1. 노트북 켜기</h4>
                        <p>Windows 부팅 완료까지 대기</p>

                        <h4>1-2. 필수 사항 확인</h4>
                        <div class="alert alert-success">
                            <strong>✅ 인터넷 연결 확인</strong><br>
                            구글 시트 데이터를 불러오기 위해 필요 (Wi-Fi 또는 유선 연결)
                        </div>

                        <hr class="my-4">

                        <h2>🔹 2단계: 카카오톡 실행 및 배치</h2>

                        <h4>2-1. 카카오톡 실행</h4>
                        <p>바탕화면 또는 시작 메뉴에서 <strong>카카오톡</strong> 실행 후 로그인 완료 대기</p>

                        <h4>2-2. 카카오톡 창 배치 (⚠️ 중요!)</h4>
                        <div class="alert alert-warning">
                            <ul>
                                <li>✅ 카카오톡 메인창을 화면 중앙에 배치</li>
                                <li>✅ 다른 창에 가려지지 않게 하기</li>
                                <li>✅ 최소화하지 말고 화면에 표시</li>
                                <li>✅ 카톡 창 크기는 기본 크기 유지 (너무 작거나 크게 하지 말기)</li>
                            </ul>
                            <strong>주의:</strong> 채팅창이 아닌 <strong>메인 친구 목록 창</strong>이어야 함
                        </div>

                        <hr class="my-4">

                        <h2>🔹 3단계: 서버 실행</h2>

                        <h4>3-1. CMD(명령 프롬프트) 열기</h4>
                        <p><kbd>Windows 키 + R</kbd> → <code>cmd</code> 입력 → Enter</p>

                        <h4>3-2. 프로젝트 폴더로 이동</h4>
                        <pre class="bg-dark text-light p-3 rounded"><code>cd D:\projects\claude</code></pre>

                        <h4>3-3. Flask 서버 실행</h4>
                        <pre class="bg-dark text-light p-3 rounded"><code>python app.py</code></pre>

                        <div class="alert alert-info">
                            <strong>✅ 성공 화면:</strong><br>
                            <code>Running on http://127.0.0.1:5000</code> 메시지가 표시되면 성공!
                        </div>

                        <hr class="my-4">

                        <h2>🔹 4단계: 브라우저에서 대시보드 접속</h2>

                        <p>브라우저 주소창에 입력:</p>
                        <pre class="bg-primary text-white p-3 rounded text-center"><code style="font-size: 18px;">http://localhost:5000</code></pre>

                        <hr class="my-4">

                        <h2>🔹 5단계: 구글 시트 설정</h2>

                        <h4>5-1. 구글 시트 준비</h4>
                        <table class="table table-bordered">
                            <thead class="table-light">
                                <tr>
                                    <th>A열 (이름)</th>
                                    <th>B열 (전화번호)</th>
                                    <th>C열 (메시지)</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>김철수</td>
                                    <td>01012345678</td>
                                    <td>안녕하세요</td>
                                </tr>
                                <tr>
                                    <td>이영희</td>
                                    <td>01087654321</td>
                                    <td>반갑습니다</td>
                                </tr>
                            </tbody>
                        </table>

                        <div class="alert alert-warning">
                            <strong>⚠️ 주의:</strong>
                            <ul class="mb-0">
                                <li>전화번호는 <strong>하이픈 없이</strong> (01012345678 ✅, 010-1234-5678 ❌)</li>
                                <li>첫 번째 행부터 데이터 입력 (헤더 행 없음)</li>
                                <li>메시지는 선택사항 (없으면 친구만 추가)</li>
                            </ul>
                        </div>

                        <h4>5-2. 구글 시트 URL 복사 및 설정</h4>
                        <ol>
                            <li>구글 시트 열기</li>
                            <li>주소창의 URL 전체 복사</li>
                            <li>대시보드 왼쪽 상단 <strong>"📊 구글 시트 설정"</strong> 카드 찾기</li>
                            <li>URL 입력란에 붙여넣기</li>
                            <li><strong>"🔄 적용"</strong> 버튼 클릭</li>
                        </ol>

                        <div class="alert alert-danger">
                            <strong>공유 설정 필수:</strong><br>
                            구글 시트 공유 → <strong>"링크가 있는 모든 사용자"</strong>로 변경 (권한: 뷰어 이상)
                        </div>

                        <hr class="my-4">

                        <h2>🔹 6단계: 작업 설정</h2>

                        <h4>6-1. 범위 설정</h4>
                        <ul>
                            <li><strong>시작 번호</strong>: 처음 추가할 친구 번호 (예: 1)</li>
                            <li><strong>끝 번호</strong>: 마지막 친구 번호 (예: 10)</li>
                        </ul>

                        <div class="alert alert-info">
                            <strong>💡 처음 테스트 시:</strong> 1~2명 정도로 작게 시작하세요!
                        </div>

                        <h4>6-2. 랜덤 딜레이 설정</h4>
                        <ul>
                            <li><strong>최소</strong>: 5초</li>
                            <li><strong>최대</strong>: 30초</li>
                        </ul>
                        <p>각 친구 처리 후 5~30초 사이에서 랜덤하게 대기 (스팸 차단 방지)</p>

                        <div class="alert alert-success">
                            <strong>권장 설정:</strong><br>
                            안전 모드: 최소 10초, 최대 40초<br>
                            일반 모드: 최소 5초, 최대 30초
                        </div>

                        <hr class="my-4">

                        <h2>🔹 7단계: 작업 시작</h2>

                        <h4>7-1. 최종 확인 체크리스트</h4>
                        <div class="alert alert-primary">
                            <ul class="mb-0">
                                <li>☑️ 카카오톡 메인창이 화면에 보이는가?</li>
                                <li>☑️ 카톡 창이 다른 창에 가려지지 않았는가?</li>
                                <li>☑️ 친구 목록이 정상적으로 로드되었는가?</li>
                                <li>☑️ 범위 설정이 올바른가?</li>
                                <li>☑️ 테스트라면 1~2명으로 설정했는가?</li>
                            </ul>
                        </div>

                        <h4>7-2. 시작 버튼 클릭</h4>
                        <p><strong>"🚀 시작하기"</strong> 버튼 클릭 → 확인 팝업에서 "확인" 클릭</p>

                        <hr class="my-4">

                        <h2>🔹 8단계: 작업 모니터링</h2>

                        <h4>작업 중 주의사항</h4>
                        <div class="alert alert-danger">
                            <strong>⚠️ 절대 금지:</strong>
                            <ul class="mb-0">
                                <li>❌ 마우스나 키보드 사용하지 말 것</li>
                                <li>❌ 카톡 창을 옮기거나 최소화하지 말 것</li>
                                <li>❌ 다른 창을 카톡 위에 올리지 말 것</li>
                                <li>❌ 절전 모드로 들어가지 않도록 설정</li>
                            </ul>
                        </div>

                        <div class="alert alert-success">
                            <strong>✅ 가능:</strong>
                            <ul class="mb-0">
                                <li>✅ 대시보드 화면 보기 (읽기만)</li>
                                <li>✅ 다른 모니터 사용 (카톡 화면 건드리지 않기)</li>
                            </ul>
                        </div>

                        <h4>중단이 필요한 경우</h4>
                        <p><strong>"⏹️ 중단하기"</strong> 버튼 클릭 (현재 작업 완료 후 중단됨)</p>

                        <hr class="my-4">

                        <h2>🔹 자주 발생하는 오류 및 해결책</h2>

                        <h4>오류 1: "카카오톡 창을 찾을 수 없습니다"</h4>
                        <p><strong>해결:</strong></p>
                        <ul>
                            <li>카카오톡 실행 확인</li>
                            <li>메인 친구 목록 창인지 확인 (채팅창 아님)</li>
                            <li>카톡을 완전히 종료 후 재실행</li>
                        </ul>

                        <h4>오류 2: "창 활성화 실패"</h4>
                        <p><strong>해결:</strong></p>
                        <ul>
                            <li>카톡 창을 화면 중앙에 배치</li>
                            <li>최대화 하지 말고 보통 크기로</li>
                            <li>다른 창 모두 닫기</li>
                        </ul>

                        <h4>오류 3: 친구 추가가 실패함</h4>
                        <p><strong>해결:</strong></p>
                        <ul>
                            <li>구글 시트에서 전화번호 형식 확인 (01012345678)</li>
                            <li>이미 친구인 경우 스킵됨 (정상 동작)</li>
                            <li>카톡 최신 버전으로 업데이트</li>
                        </ul>

                        <h4>오류 4: 서버가 갑자기 중단됨</h4>
                        <p><strong>해결:</strong></p>
                        <ul>
                            <li>CMD 창에서 오류 메시지 확인</li>
                            <li><code>python app.py</code> 다시 실행</li>
                        </ul>

                        <hr class="my-4">

                        <h2>💡 Pro Tips</h2>

                        <div class="row">
                            <div class="col-md-6">
                                <div class="card mb-3">
                                    <div class="card-header bg-primary text-white">
                                        <strong>효율적인 일정 관리</strong>
                                    </div>
                                    <div class="card-body">
                                        <ul class="mb-0">
                                            <li>오전: 1~50번 (50명)</li>
                                            <li>점심: 서버 켜둔 채로 휴식</li>
                                            <li>오후: 51~100번 (50명)</li>
                                        </ul>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="card mb-3">
                                    <div class="card-header bg-success text-white">
                                        <strong>안전한 사용</strong>
                                    </div>
                                    <div class="card-body">
                                        <ul class="mb-0">
                                            <li>하루 100명 이상은 권장하지 않음</li>
                                            <li>딜레이를 충분히 길게 설정</li>
                                            <li>카톡 계정 차단 방지</li>
                                        </ul>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="alert alert-info mt-3">
                            <strong>📌 일일 작업 루틴 (익숙해진 후):</strong><br>
                            1. 노트북 켜기 → 2. 카톡 실행 (화면 중앙) → 3. CMD: <code>python app.py</code> →
                            4. 브라우저: <code>http://localhost:5000</code> → 5. 범위/딜레이 설정 → 6. 시작!
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">닫기</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>

    <script>
        let eventSource = null;

        // 페이지 로드 시 친구 목록 가져오기
        window.onload = function() {
            loadFriends();
            startStatusPolling();
        };

        // 친구 목록 로드
        function loadFriends() {
            fetch('/api/friends')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const tbody = document.getElementById('friendList');
                        tbody.innerHTML = '';

                        data.friends.forEach((friend, index) => {
                            const row = document.createElement('tr');
                            const hasMessage = friend.message ? '✓' : '-';
                            const messagePreview = friend.message ?
                                (friend.message.substring(0, 20) + '...') : '-';

                            row.innerHTML = `
                                <td>${index + 1}</td>
                                <td>${friend.name}</td>
                                <td>${friend.phone}</td>
                                <td><small>${messagePreview}</small></td>
                            `;
                            tbody.appendChild(row);
                        });

                        document.getElementById('totalFriends').textContent = `총 ${data.total}명`;
                        document.getElementById('endNum').value = data.total;

                        // 구글 시트 URL 표시
                        if (data.sheet_url) {
                            document.getElementById('sheetUrl').value = data.sheet_url;
                        }
                    } else {
                        alert('친구 데이터를 불러올 수 없습니다: ' + data.message);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('서버 오류가 발생했습니다.');
                });
        }

        // 구글 시트 URL 업데이트
        function updateSheetUrl() {
            const url = document.getElementById('sheetUrl').value.trim();

            if (!url) {
                alert('구글 시트 URL을 입력해주세요.');
                return;
            }

            fetch('/api/sheet-url', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url: url })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('✓ ' + data.message);
                    refreshFriends();
                } else {
                    alert('✗ ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('서버 오류가 발생했습니다.');
            });
        }

        // 친구 목록 새로고침
        function refreshFriends() {
            const tbody = document.getElementById('friendList');
            tbody.innerHTML = '<tr><td colspan="4" class="text-center">새로고침 중...</td></tr>';
            loadFriends();
        }

        // 작업 시작
        function startTask() {
            const start = parseInt(document.getElementById('startNum').value);
            const end = parseInt(document.getElementById('endNum').value);
            const delayMin = parseFloat(document.getElementById('delayMin').value);
            const delayMax = parseFloat(document.getElementById('delayMax').value);

            if (start < 1 || end < start) {
                alert('올바른 범위를 입력해주세요.');
                return;
            }

            if (delayMin < 0 || delayMax < delayMin) {
                alert('올바른 딜레이 범위를 입력해주세요.');
                return;
            }

            if (!confirm(`${start}번부터 ${end}번까지 ${end - start + 1}명을 처리하시겠습니까?`)) {
                return;
            }

            fetch('/api/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    start: start,
                    end: end,
                    delay_min: delayMin,
                    delay_max: delayMax
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('startBtn').style.display = 'none';
                    document.getElementById('stopBtn').style.display = 'block';
                    startLogStream();
                } else {
                    alert(data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('서버 오류가 발생했습니다.');
            });
        }

        // 작업 중단
        function stopTask() {
            if (!confirm('작업을 중단하시겠습니까?')) {
                return;
            }

            fetch('/api/stop', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
            });
        }

        // 상태 폴링
        function startStatusPolling() {
            setInterval(() => {
                fetch('/api/status')
                    .then(response => response.json())
                    .then(data => {
                        // 진행률 업데이트
                        const percent = data.total > 0 ? Math.round((data.current / data.total) * 100) : 0;
                        document.getElementById('progressBar').style.width = percent + '%';
                        document.getElementById('progressPercent').textContent = percent + '%';
                        document.getElementById('progressText').textContent =
                            data.running ? `진행 중: ${data.current} / ${data.total}` : '대기 중...';

                        // 카운터 업데이트
                        document.getElementById('successCount').textContent = data.success_count;
                        document.getElementById('failCount').textContent = data.fail_count;
                        document.getElementById('totalCount').textContent = data.total;

                        // 버튼 상태 업데이트
                        if (!data.running) {
                            document.getElementById('startBtn').style.display = 'block';
                            document.getElementById('stopBtn').style.display = 'none';
                        }
                    });
            }, 1000);
        }

        // 로그 스트리밍
        function startLogStream() {
            if (eventSource) {
                eventSource.close();
            }

            eventSource = new EventSource('/api/logs/stream');
            eventSource.onmessage = function(event) {
                const log = JSON.parse(event.data);
                addLog(log);
            };
        }

        // 로그 추가
        function addLog(log) {
            const logContainer = document.getElementById('logContainer');
            const entry = document.createElement('div');
            entry.className = 'log-entry';
            entry.innerHTML = `<span class="log-time">[${log.time}]</span>${log.message}`;
            logContainer.appendChild(entry);
            logContainer.scrollTop = logContainer.scrollHeight;
        }

        // 로그 지우기
        function clearLogs() {
            document.getElementById('logContainer').innerHTML = '';
        }

        // 이용 매뉴얼 모달 열기
        function showManual() {
            const manualModal = new bootstrap.Modal(document.getElementById('manualModal'));
            manualModal.show();
        }
    </script>
</body>
</html>
"""

# Flask app initialization
flask_app = Flask(__name__)
flask_app.config['JSON_AS_ASCII'] = False
CORS(flask_app)

# 한글 인코딩 문제 해결
CORS(app)

# 서버 API 설정
API_BASE_URL = "https://only-talk.kiam.kr/api"
CONFIG_FILE = "onlytalk_config.json"

# 구글 시트 설정 (기본값)
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1zDsFPQyrpSGiUvJ3eAqJyR5luwyecVohxKRdetGFGns/export?format=csv&gid=0"

# 전역 변수
current_task = None
task_status = {
    'running': False,
    'current': 0,
    'total': 0,
    'logs': [],
    'success_count': 0,
    'fail_count': 0,
    'sheet_url': GOOGLE_SHEET_URL,
    'selected_addressbook': None,
    'icon_found': False,  # v2.0: 아이콘 발견 여부
    'icon_location': None  # v2.0: 아이콘 위치
}

# v2.0: 전역 변수 - 아이콘 위치
ICON_LOCATION = None

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def get_license_key():
    config = load_config()
    return config.get('license_key', None)

def log_message(message):
    task_status['logs'].append({
        'time': time.strftime('%H:%M:%S'),
        'message': message
    })
    # 최근 100개만 유지
    if len(task_status['logs']) > 100:
        task_status['logs'] = task_status['logs'][-100:]

def read_friends_data(sheet_url=None):
    if sheet_url is None:
        sheet_url = GOOGLE_SHEET_URL

    friends = []
    try:
        # 구글 시트에서 CSV 다운로드
        log_message("📥 구글 시트에서 데이터 불러오는 중...")
        response = requests.get(sheet_url, timeout=10)
        response.raise_for_status()

        # UTF-8 인코딩 명시
        response.encoding = 'utf-8'

        # CSV 파싱
        csv_data = StringIO(response.text)
        csv_reader = csv.reader(csv_data)

        for row in csv_reader:
            if len(row) >= 2:
                name = row[0].strip()
                phone = row[1].strip()
                message = row[2].strip() if len(row) >= 3 else ""
                friends.append({
                    'name': name,
                    'phone': phone,
                    'message': message
                })

        log_message(f"✓ {len(friends)}명의 데이터 로드 완료")
        return friends

    except requests.exceptions.RequestException as e:
        log_message(f"✗ 구글 시트 접근 실패: {e}")
        # 로컬 CSV 파일 fallback
        try:
            log_message("📂 로컬 CSV 파일 시도...")
            with open('kakao_friends_full.csv', 'r', encoding='utf-8') as f:
                csv_reader = csv.reader(f)
                for row in csv_reader:
                    if len(row) >= 2:
                        name = row[0].strip()
                        phone = row[1].strip()
                        message = row[2].strip() if len(row) >= 3 else ""
                        friends.append({
                            'name': name,
                            'phone': phone,
                            'message': message
                        })
            log_message(f"✓ 로컬 파일에서 {len(friends)}명 로드")
            return friends
        except FileNotFoundError:
            log_message("✗ 로컬 CSV 파일도 없음")
            return None
    except Exception as e:
        log_message(f"✗ 데이터 읽기 실패: {e}")
        return None

def find_main_kakao_window():
    all_windows = gw.getAllWindows()
    kakao_candidates = []

    for window in all_windows:
        title = window.title
        if not title.strip():
            continue

        if '카카오톡' in title or 'KakaoTalk' in title or 'kakao' in title.lower():
            is_main = (title == "카카오톡" or title == "KakaoTalk" or len(title) < 20)
            kakao_candidates.append({
                'window': window,
                'title': title,
                'is_main': is_main
            })

    if not kakao_candidates:
        return None

    for candidate in kakao_candidates:
        if candidate['is_main']:
            return candidate['window']

    return kakao_candidates[0]['window']

def activate_window(window, silent=False):
    v2.0: 창을 최상단으로 강제로 가져옵니다 (Windows API 사용)

    Args:
        window: 활성화할 창
        silent: True면 로그를 출력하지 않음
    try:
        # 최소화되어 있으면 복원
        if window.isMinimized:
            if not silent:
                log_message("최소화된 창 복원 중...")
            try:
                hwnd = window._hWnd
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                time.sleep(1.0)
            except:
                pass

        # 창 활성화 (여러 번 강력하게 시도)
        if not silent:
            log_message("창 활성화 시도 (5회 강력하게)...")
        for i in range(5):
            try:
                window.activate()
                time.sleep(0.3)
            except:
                pass

        # 최상위로 올리기 (maximize/restore 트릭)
        try:
            window.maximize()
            time.sleep(0.2)
            window.restore()
            time.sleep(0.3)
        except:
            pass

        # 한 번 더 activate
        try:
            window.activate()
            time.sleep(0.5)
        except:
            pass

        # v2.0: 최상위 고정 시도 (Windows API 사용)
        try:
            hwnd = window._hWnd
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                 win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
            time.sleep(0.2)
            win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                                 win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
        except:
            pass

        # 최종 활성화
        try:
            window.activate()
            time.sleep(1.0)
        except:
            pass

        if not silent:
            log_message("✓ 창 활성화 완료!")
        return True

    except Exception as e:
        if not silent:
            log_message(f"✗ 창 활성화 실패: {e}")
        return False

def find_person_plus_icon(window):
    v2.0: 이미지 인식으로 '사람+' 아이콘의 위치를 찾습니다.

    Returns:
        dict: {'x': x좌표, 'y': y좌표, 'offset_x': 오프셋x, 'offset_y': 오프셋y, 'confidence': 신뢰도}
        None: 찾지 못한 경우
    log_message("🔍 '사람+' 아이콘 위치 찾기 (이미지 인식)")

    icon_path = "person_plus_icon.png"

    # 아이콘 파일 확인
    if not os.path.exists(icon_path):
        log_message(f"✗ 아이콘 파일이 없습니다: {icon_path}")
        log_message(f"→ 기본 좌표 사용 (offset +450, +66)")
        return None

    log_message(f"✓ 아이콘 파일 발견: {icon_path}")

    # 여러 confidence 값으로 시도
    confidences = [0.9, 0.8, 0.7, 0.6]

    log_message("이미지 인식 시작...")

    for conf in confidences:
        try:
            log_message(f"  시도: confidence={conf*100:.0f}%")

            location = pyautogui.locateOnScreen(icon_path, confidence=conf)

            if location:
                x, y = pyautogui.center(location)

                offset_x = x - window.left
                offset_y = y - window.top

                log_message(f"✓ 아이콘 발견!")
                log_message(f"  화면 좌표: ({x}, {y})")
                log_message(f"  창 오프셋: (+{offset_x}, +{offset_y})")
                log_message(f"  신뢰도: {conf*100:.0f}%")

                return {
                    'x': x,
                    'y': y,
                    'offset_x': offset_x,
                    'offset_y': offset_y,
                    'confidence': conf
                }
        except Exception as e:
            # 파일 없음 에러가 아니면 로그 출력
            if 'could not' not in str(e).lower() and 'file' not in str(e).lower():
                log_message(f"  에러: {e}")

    log_message("✗ 아이콘을 찾을 수 없습니다")
    log_message("→ 기본 좌표 사용 (offset +450, +66)")
    return None

def add_friend_and_send_message(window, friend_data):
    v2.0: 한 명의 친구 추가 및 메시지 전송 (이미지 인식 사용)
    name = friend_data['name']
    phone = friend_data['phone']
    message = friend_data['message']

    try:
        global ICON_LOCATION

        # 1. '사람+' 아이콘 클릭
        # v2.0: 이미지 인식 결과 사용 (있으면)
        if ICON_LOCATION:
            x = window.left + ICON_LOCATION['offset_x']
            y = window.top + ICON_LOCATION['offset_y']
            log_message(f"  위치: 이미지 인식 (offset +{ICON_LOCATION['offset_x']}, +{ICON_LOCATION['offset_y']})")
        else:
            # 기본 좌표 사용
            x = window.left + 450
            y = window.top + 66
            log_message(f"  위치: 기본 좌표 (offset +450, +66)")

        pyautogui.click(x, y)
        time.sleep(1.8)

        # 2. 이름 붙여넣기
        pyperclip.copy(name)
        time.sleep(0.3)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.8)

        # 3. Tab 3회 → 폰번호 입력창
        for i in range(3):
            pyautogui.press('tab')
            time.sleep(0.3)

        # 4. 폰번호 붙여넣기
        pyperclip.copy(phone)
        time.sleep(0.3)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.8)

        # 5. Tab 1회 + Enter → 친구 등록
        pyautogui.press('tab')
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(2.0)

        # 6. Enter → 일대일채팅 창 열기
        pyautogui.press('enter')
        time.sleep(2.5)

        # 7. 메시지 전송 (있는 경우만)
        try:
            if message:
                pyautogui.hotkey('alt', 'tab')
                time.sleep(0.8)

                pyperclip.copy(message)
                time.sleep(0.3)
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(1.0)

                pyautogui.press('enter')
                time.sleep(1.0)
            else:
                pyautogui.hotkey('alt', 'tab')
                time.sleep(0.5)

            # 8. 채팅창 닫기
            pyautogui.press('esc')
            time.sleep(1.0)

            # v2.0: 9. 카톡 메인창을 다시 최상단으로
            log_message("  카톡 메인창을 최상단으로 이동...")
            activate_window(window, silent=True)
            time.sleep(0.5)

            return True

        except Exception as e:
            # 친구 추가 실패 케이스
            for i in range(3):
                pyautogui.press('esc')
                time.sleep(0.5)

            # v2.0: 실패해도 창 최상단으로
            activate_window(window, silent=True)
            time.sleep(0.5)

            return False

    except Exception as e:
        log_message(f"✗ 에러: {e}")

        # v2.0: 에러 시에도 창 최상단으로
        try:
            activate_window(window, silent=True)
        except:
            pass

        return False

def run_task(start, end, delay_min, delay_max):
    global task_status, ICON_LOCATION

    task_status['running'] = True
    task_status['current'] = 0
    task_status['logs'] = []
    task_status['success_count'] = 0
    task_status['fail_count'] = 0

    log_message("🚀 작업 시작!")

    # 친구 데이터 읽기
    friends = read_friends_data()
    if not friends:
        log_message("✗ 친구 데이터를 읽을 수 없습니다.")
        task_status['running'] = False
        return

    friends_to_process = friends[start-1:end]
    task_status['total'] = len(friends_to_process)

    log_message(f"📋 {start}번부터 {end}번까지 총 {len(friends_to_process)}명 처리")

    # 카톡 창 찾기
    main_window = find_main_kakao_window()
    if not main_window:
        log_message("✗ 카카오톡 창을 찾을 수 없습니다!")
        task_status['running'] = False
        return

    log_message(f"✓ 카톡 창 발견: {main_window.title}")

    # 창 활성화
    if not activate_window(main_window):
        log_message("✗ 창 활성화 실패!")
        task_status['running'] = False
        return

    log_message("✓ 창 활성화 완료!")

    # v2.0: 이미지 인식으로 아이콘 위치 찾기
    log_message("⚠️ 이미지 인식을 위해 카톡 창을 최상단으로 가져옵니다...")
    activate_window(main_window, silent=True)
    time.sleep(1.0)

    ICON_LOCATION = find_person_plus_icon(main_window)

    if ICON_LOCATION:
        log_message(f"✓ 아이콘 위치 자동 검색 성공! (offset +{ICON_LOCATION['offset_x']}, +{ICON_LOCATION['offset_y']})")
        task_status['icon_found'] = True
        task_status['icon_location'] = ICON_LOCATION
    else:
        log_message(f"⚠ 아이콘 위치 자동 검색 실패, 기본 좌표 사용 (+450, +66)")
        task_status['icon_found'] = False

    # 3초 카운트다운
    for i in range(3, 0, -1):
        log_message(f"⏰ {i}초...")
        time.sleep(1)

    # v2.0: 작업 시작 전 창 최상단으로
    log_message("카톡 창을 최상단으로 가져옵니다...")
    activate_window(main_window, silent=True)
    time.sleep(1.0)

    # 친구 추가 시작
    for i, friend in enumerate(friends_to_process, 1):
        if not task_status['running']:  # 중단 체크
            log_message("⚠️ 작업이 중단되었습니다.")
            break

        task_status['current'] = i
        actual_number = start + i - 1

        log_message(f"👤 [{i}/{len(friends_to_process)}] (번호: {actual_number}) {friend['name']}")

        if add_friend_and_send_message(main_window, friend):
            task_status['success_count'] += 1
            log_message(f"✅ {friend['name']} 완료!")
        else:
            task_status['fail_count'] += 1
            log_message(f"⚠️ {friend['name']} 실패")

        # 랜덤 딜레이
        if i < len(friends_to_process):
            if delay_min == delay_max:
                wait_time = delay_min
            else:
                wait_time = random.uniform(delay_min, delay_max)

            log_message(f"⏰ {wait_time:.1f}초 대기...")
            time.sleep(wait_time)

    # 완료
    log_message("=" * 40)
    log_message("📊 작업 완료!")
    log_message(f"✅ 성공: {task_status['success_count']}명")
    log_message(f"❌ 실패: {task_status['fail_count']}명")
    log_message("=" * 40)

    task_status['running'] = False

@flask_app.route('/')
def index():
    return render_template('index.html')

@flask_app.route('/api/friends')
def get_friends():
    friends = read_friends_data()
    if friends:
        return jsonify({
            'success': True,
            'friends': friends,
            'total': len(friends),
            'sheet_url': task_status['sheet_url']
        })
    else:
        return jsonify({
            'success': False,
            'message': '구글 시트 또는 CSV 파일을 찾을 수 없습니다.'
        })

@flask_app.route('/api/sheet-url', methods=['GET', 'POST'])
def sheet_url():
    global GOOGLE_SHEET_URL

    if request.method == 'POST':
        data = request.json
        new_url = data.get('url', '')

        if not new_url:
            return jsonify({
                'success': False,
                'message': 'URL을 입력해주세요.'
            })

        # URL 유효성 검사
        if 'docs.google.com/spreadsheets' not in new_url:
            return jsonify({
                'success': False,
                'message': '올바른 구글 시트 URL이 아닙니다.'
            })

        # export URL로 변환
        if '/edit' in new_url:
            sheet_id = new_url.split('/d/')[1].split('/')[0]
            new_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"

        GOOGLE_SHEET_URL = new_url
        task_status['sheet_url'] = new_url

        return jsonify({
            'success': True,
            'message': '구글 시트 URL이 업데이트되었습니다.',
            'url': new_url
        })
    else:
        return jsonify({
            'success': True,
            'url': task_status['sheet_url']
        })

@flask_app.route('/api/addressbooks')
def get_addressbooks():
    license_key = get_license_key()

    if not license_key:
        return jsonify({
            'success': False,
            'message': '라이선스 키가 없습니다. 클라이언트를 다시 시작해주세요.'
        })

    try:
        # 서버 API 호출
        response = requests.get(
            f"{API_BASE_URL}/accounts/addressbooks/",
            headers={
                'Authorization': f'Bearer {license_key}',
                'Content-Type': 'application/json'
            },
            timeout=10,
            verify=False
        )

        if response.status_code == 200:
            data = response.json()

            # 배열로 변환
            addressbooks = []
            if isinstance(data, list):
                addressbooks = data
            elif isinstance(data, dict) and 'results' in data:
                addressbooks = data['results']

            return jsonify({
                'success': True,
                'addressbooks': addressbooks
            })
        else:
            return jsonify({
                'success': False,
                'message': f'서버 오류: {response.status_code}'
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'오류: {str(e)}'
        })

@flask_app.route('/api/select-addressbook', methods=['POST'])
def select_addressbook():
    global GOOGLE_SHEET_URL

    data = request.json
    addressbook_id = data.get('id')
    google_sheet_url = data.get('google_sheet_url')
    name = data.get('name')

    if not google_sheet_url:
        return jsonify({
            'success': False,
            'message': '주소록 URL이 없습니다.'
        })

    # export URL로 변환
    if '/edit' in google_sheet_url:
        sheet_id = google_sheet_url.split('/d/')[1].split('/')[0]
        export_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
    else:
        export_url = google_sheet_url

    GOOGLE_SHEET_URL = export_url
    task_status['sheet_url'] = export_url
    task_status['selected_addressbook'] = {
        'id': addressbook_id,
        'name': name,
        'url': google_sheet_url
    }

    return jsonify({
        'success': True,
        'message': f'주소록 "{name}"이 선택되었습니다.',
        'export_url': export_url
    })

@flask_app.route('/api/start', methods=['POST'])
def start_task():
    global current_task

    if task_status['running']:
        return jsonify({
            'success': False,
            'message': '이미 작업이 실행 중입니다.'
        })

    data = request.json
    start = int(data.get('start', 1))
    end = int(data.get('end', 1))
    delay_min = float(data.get('delay_min', 1.5))
    delay_max = float(data.get('delay_max', 1.5))

    # 백그라운드 스레드로 실행
    current_task = threading.Thread(
        target=run_task,
        args=(start, end, delay_min, delay_max)
    )
    current_task.daemon = True
    current_task.start()

    return jsonify({
        'success': True,
        'message': '작업이 시작되었습니다.'
    })

@flask_app.route('/api/stop', methods=['POST'])
def stop_task():
    task_status['running'] = False
    return jsonify({
        'success': True,
        'message': '작업 중단 요청이 접수되었습니다.'
    })

@flask_app.route('/api/status')
def get_status():
    return jsonify(task_status)

@flask_app.route('/api/logs/stream')
def stream_logs():
    def generate():
        last_log_count = 0
        while True:
            current_log_count = len(task_status['logs'])
            if current_log_count > last_log_count:
                # 새로운 로그만 전송
                new_logs = task_status['logs'][last_log_count:]
                for log in new_logs:
                    yield f"data: {json.dumps(log)}\n\n"
                last_log_count = current_log_count
            time.sleep(0.5)

    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    import sys
    import io

    # UTF-8 출력 설정 (Windows 인코딩 문제 해결)
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print("="*60)
    print("  카카오톡 친구 자동 추가 웹 대시보드 v2.0")
    print("="*60)
    print("\nv2.0 변경사항:")
    print("  - 이미지 인식으로 '사람+' 아이콘 자동 검색")
    print("  - 창 활성화 강화 (Windows API 사용)")
    print("  - 매 작업 후 창 최상단 이동")
    print("\n🌐 서버 시작 중...")
    print("\n접속 주소:")
    print("  - 이 컴퓨터: http://localhost:5000")
    print("  - 같은 네트워크: http://[내 IP]:5000")
    print("\n⚠️  서버를 중단하려면 Ctrl+C를 누르세요.")
    print("="*60)
    print()

    # 0.0.0.0으로 바인딩하면 외부에서도 접속 가능
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)


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

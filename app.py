from flask import Flask, request, render_template, redirect
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
import os
import json

app = Flask(__name__)

# ------------------------ 設定ファイル管理 ------------------------

def load_settings():
    with open("settings.json", "r", encoding="utf-8") as f:
        return json.load(f)

def save_settings(data):
    with open("settings.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        new_settings = {
            "title": request.form.get("title"),
            "button_color": request.form.get("button_color")
        }
        save_settings(new_settings)
        return redirect('/admin')

    current_settings = load_settings()
    return render_template('admin.html', settings=current_settings)

# ------------------------ Google Sheets ------------------------

def get_sheet(sheet_name):
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)
    return client.open(sheet_name).sheet1

# ------------------------ LINE通知 ------------------------

LINE_ACCESS_TOKEN = os.environ.get("LINE_ACCESS_TOKEN")

def line_notify(to, message):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_ACCESS_TOKEN}"
    }
    body = {
        "to": to,
        "messages": [{"type": "text", "text": message}]
    }
    requests.post(url, headers=headers, json=body)

# ------------------------ 教室側 ------------------------

@app.route('/')
def index():
    return render_template('form.html')

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name')
    location = request.form.get('location')
    date = request.form.get('date')
    experience = request.form.get('experience')

    sheet = get_sheet("教室登録シート")
    sheet.append_row([name, location, date, experience])

    return "送信が完了しました！LINEに戻ってください。"

# ------------------------ アルバイト側 ------------------------

@app.route('/register_alb')
def register_alb():
    settings = load_settings()
    return render_template('form_alb.html', settings=settings)

@app.route('/submit_alb', methods=['POST'])
def submit_alb():
    try:
        name = request.form.get('name')
        gym = request.form.get('gym')
        cheer = request.form.get('cheer')
        area = request.form.get('area')
        available = request.form.get('available')
        user_id = request.form.get('user_id')

        # デバッグ用に表示（任意）
        print(f"🔍 name={name}, gym={gym}, cheer={cheer}, area={area}, available={available}, user_id={user_id}")

        # スプレッドシートに保存
        sheet = get_sheet("アルバイト登録シート")
        sheet.append_row([name, gym, cheer, area, available, user_id])

        # LINE通知
        line_notify(user_id, f"{name}さん、アルバイト登録ありがとうございます！")

        return "登録ありがとうございます！LINEに戻ってください。"

    except Exception as e:
        print("❌ submit_alb エラー:", e)
        return "Internal Server Error", 500


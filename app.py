from flask import Flask, request, render_template, redirect
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
import os
import json

app = Flask(__name__)

# ------------------------ 設定ファイル管理 ------------------------

def load_settings():
    default_settings = {
        "title": "アルバイト登録",
        "button_color": "#00b900",
        "form_label_name": "お名前",
        "form_label_area": "希望エリア",
        "form_label_available": "出勤可能日",
        "custom_fields": []
    }
    try:
        with open("settings.json", "r", encoding="utf-8") as f:
            saved = json.load(f)
        if "custom_fields" not in saved:
            saved["custom_fields"] = []
        default_settings.update(saved)
    except Exception as e:
        print("⚠️ load_settings error:", e)
    return default_settings


def save_settings(data):
    with open("settings.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        # 基本設定の取得
        new_settings = {
            "title": request.form.get("title"),
            "button_color": request.form.get("button_color"),
            "form_label_name": request.form.get("form_label_name"),
            "form_label_area": request.form.get("form_label_area"),
            "form_label_available": request.form.get("form_label_available"),
            "custom_fields": []
        }

        # カスタム項目の数を取得してループ
        custom_count = int(request.form.get("custom_count", 0))
        for i in range(1, custom_count + 1):
            label = request.form.get(f"custom_label_{i}")
            name = request.form.get(f"custom_name_{i}")
            if label and name:
                new_settings["custom_fields"].append({
                    "label": label,
                    "name": name
                })

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
        settings = load_settings()

        # 基本項目の取得
        name = request.form.get('name')
        gym = request.form.get('gym')
        cheer = request.form.get('cheer')
        area = request.form.get('area')
        available = request.form.get('available')
        user_id = request.form.get('user_id')

        # カスタム項目の取得
        custom_values = []
        for field in settings.get("custom_fields", []):
            value = request.form.get(field["name"], "")
            custom_values.append(value)

        # デバッグ出力
        print(f"🔍 name={name}, gym={gym}, cheer={cheer}, area={area}, available={available}, user_id={user_id}")
        for i, field in enumerate(settings.get("custom_fields", [])):
            print(f"📝 {field['label']} ({field['name']}): {custom_values[i]}")

        # スプレッドシートに保存
        sheet = get_sheet("アルバイト登録シート")
        row = [name, gym, cheer, area, available, user_id] + custom_values
        sheet.append_row(row)

        # LINE通知
        line_notify(user_id, f"{name}さん、アルバイト登録ありがとうございます！")

        return "登録ありがとうございます！LINEに戻ってください。"

    except Exception as e:
        print("❌ submit_alb エラー:", e)
        return "Internal Server Error", 500



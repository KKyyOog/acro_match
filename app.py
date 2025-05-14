from flask import Flask, request, render_template
import gspread
from oauth2client.service_account import ServiceAccountCredentials


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('form.html')

def get_sheet(sheet_name):
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)
    return client.open(sheet_name).sheet1


@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name')
    location = request.form.get('location')
    date = request.form.get('date')
    experience = request.form.get('experience')

    sheet = get_sheet("教室登録シート")
    sheet.append_row([name, location, date, experience])

    return "送信が完了しました！LINEに戻ってください。"


if __name__ == '__main__':
    app.run(debug=True)

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

@app.route('/register_alb')
def register_alb():
    return render_template('form_alb.html')

@app.route('/submit_alb', methods=['POST'])
def submit_alb():
    name = request.form.get('name')
    gym = request.form.get('gym')
    cheer = request.form.get('cheer')
    area = request.form.get('area')
    available = request.form.get('available')

    sheet = get_sheet("アルバイト登録シート")
    sheet.append_row([name, gym, cheer, area, available])

    return "登録ありがとうございます！LINEに戻ってください。"


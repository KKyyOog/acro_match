from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('form.html')

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name')
    location = request.form.get('location')
    date = request.form.get('date')
    experience = request.form.get('experience')

    print(f"教室名: {name}, 場所: {location}, 日時: {date}, 希望条件: {experience}")
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

    print(f"[アルバイト登録] 名前: {name}, 体操: {gym}, チア: {cheer}, エリア: {area}, 稼働可能: {available}")
    return "登録ありがとうございます！LINEに戻ってください。"

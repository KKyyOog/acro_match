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

sfrom flask import Flask, render_template, request
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import schedule
import time
from datetime import datetime, timedelta
import threading
import re

app = Flask(__name__)

# Gmailの設定
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
GMAIL_USER = 'your_email@gmail.com'
GMAIL_PASSWORD = 'your_password'

# メール送信時間の設定
email_send_time = "21:00"  # デフォルトの送信時間

# 授業のスケジュールを入力
schedule_dict = {
    0: ["9:00 - Math", "11:00 - English"],
    1: ["10:00 - History", "14:00 - Physics"],
    2: ["9:00 - Chemistry", "13:00 - Biology"],
    3: ["11:00 - Music", "15:00 - Art"],
    4: ["8:00 - PE", "10:00 - Computer Science"],
}

# ログファイルのパス
log_file_path = "email_log.txt"

def send_email(subject, body, to):
    msg = MIMEMultipart()
    msg['From'] = GMAIL_USER
    msg['To'] = to
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(GMAIL_USER, to, text)
        server.quit()
        print(f"Email sent to {to}!")
    except Exception as e:
        print(f"Failed to send email: {e}")

def notify_schedule():
    today_date_str = datetime.now().strftime("%Y-%m-%d")
    tomorrow = (datetime.now() + timedelta(days=1)).weekday()

    if tomorrow in schedule_dict:
        subject = "明日の授業予定"
        body = "明日の授業は以下の通りです:\n" + "\n".join(schedule_dict[tomorrow])
        
        try:
            with open(log_file_path, "r") as log_file:
                sent_dates = log_file.read().splitlines()
        except FileNotFoundError:
            sent_dates = []

        if today_date_str not in sent_dates:
            send_email(subject, body, 'your_email@gmail.com')
            with open(log_file_path, "a") as log_file:
                log_file.write(today_date_str + "\n")

def run_scheduler():
    try:
        schedule.every().day.at(email_send_time).do(notify_schedule)
        print(f"Scheduler started, will run at {email_send_time} daily")
        while True:
            schedule.run_pending()
            time.sleep(60)
    except schedule.ScheduleValueError as e:
        print(f"Error in scheduling: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start')
def start():
    thread = threading.Thread(target=run_scheduler)
    thread.daemon = True
    thread.start()
    return "Scheduler started!"

@app.route('/set_time', methods=['POST'])
def set_time():
    global email_send_time
    new_time = request.form.get('send_time')
    if new_time and re.match(r"^\d{2}:\d{2}(:\d{2})?$", new_time):
        email_send_time = new_time
        return f"Email send time updated to {new_time}"
    return "Invalid time format. Please use HH:MM or HH:MM:SS format."

@app.route('/set_schedule', methods=['POST'])
def set_schedule():
    global schedule_dict
    try:
        day = int(request.form.get('day'))
        schedule = request.form.get('schedule').split(',')
        schedule_dict[day] = schedule
        return "Schedule updated successfully"
    except ValueError:
        return "Invalid input"

if __name__ == "__main__":
    app.run(debug=True)




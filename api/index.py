from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import random
import sqlite3
import time

app = Flask(__name__)

# إعداد قاعدة البيانات
def init_db():
    conn = sqlite3.connect('reports.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            channel_link TEXT,
            group_link TEXT,
            account_link TEXT,
            status TEXT,
            response TEXT
        )
    ''')
    conn.commit()
    conn.close()

# دالة لإضافة البلاغ إلى قاعدة البيانات
def add_report_to_db(user_id, channel_link, group_link, account_link, status, response):
    conn = sqlite3.connect('reports.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO reports (user_id, channel_link, group_link, account_link, status, response)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, channel_link, group_link, account_link, status, response))
    conn.commit()
    conn.close()

# إعداد المتغيرات المحظورة
BLOCKED_IDS = ["7762072754"]
BLOCKED_LINKS = ["https://t.me/APIZXLLLL", "https://t.me/MMMMMMMIRS"]

@app.route('/send_report', methods=['GET'])
def send_report():
    # قراءة المدخلات من طلب GET
    user_id = request.args.get('user_id', '')
    channel_link = request.args.get('channel_link', '')
    group_link = request.args.get('group_link', '')
    account_link = request.args.get('account_link', '')
    messages = request.args.getlist('message')  # قائمة من الرسائل
    emails = request.args.getlist('email')  # قائمة من الإيميلات
    phones = request.args.getlist('phone')  # قائمة من الأرقام
    names = request.args.getlist('name')  # قائمة من الأسماء
    max_reports = int(request.args.get('max_reports', 1))  # الحد الأقصى للبلاغات (الافتراضي 1)

    # التحقق من القيم المحظورة
    if user_id in BLOCKED_IDS or channel_link in BLOCKED_LINKS or group_link in BLOCKED_LINKS:
        return jsonify({
            "status": "error",
            "message": "يا مطي تحاول تبلغ عن سيدك ولا روح ارقد🤣"
        })

    url = "https://telegram.org/support"
    headers = {
        'authority': 'telegram.org',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://telegram.org',
        'referer': 'https://telegram.org/support',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    }

    responses = []
    report_count = 0  # عداد البلاغات

    # إرسال البلاغات بناءً على القيم المدخلة
    for message in messages:
        for email in emails:
            for phone in phones:
                for name in names:
                    if report_count >= max_reports:  # إذا تم الوصول للحد الأقصى للبلاغات
                        break

                    data = {
                        'message': message,
                        'legal_name': name,
                        'email': email,
                        'phone': phone,
                        'setln': '',
                    }

                    try:
                        response = requests.post(url, data=data, headers=headers)
                        soup = BeautifulSoup(response.text, 'html.parser')
                        success_message = soup.find('b', text="Thanks for your report!")
                        
                        if success_message:
                            status = "success"
                            response_text = success_message.text
                        else:
                            status = "failed"
                            response_text = "Report may not have been successful. Please check the data."

                        # إضافة البلاغ إلى قاعدة البيانات
                        add_report_to_db(user_id, channel_link, group_link, account_link, status, response_text)

                        # إضافة النتيجة إلى القائمة
                        responses.append({
                            "status": status,
                            "response": response_text
                        })
                    except Exception as e:
                        responses.append({
                            "status": "error",
                            "response": str(e)
                        })

                    report_count += 1  # زيادة عداد البلاغات
                    time.sleep(0.2)  # تأخير صغير بين البلاغات لتجنب الحظر

    return jsonify({
        "total_reports": report_count,
        "responses": responses
    })

if __name__ == '__main__':
    init_db()
    app.run(debug=True)

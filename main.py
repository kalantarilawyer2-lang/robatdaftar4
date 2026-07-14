import requests
import json
import time
import threading
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- تنظیمات هوش مصنوعی ---
AI_API_KEY = "sk-B56u9PbH8TMlJTd8eJqlUD7TIG9o0oV8tlcEZKig2Eq9duBW" 
AI_URL = "https://api.gapgpt.app/v1/chat/completions"

# --- توکن‌های ربات بله (هر دو ربات فعال شدند) ---
TOKENS = [
    "1259089716:LUlKgHHfs8fAgk4KEkDEj4KOAiATIdMCx0I",
    "1766837022:UKMhkAfTRaSC54UcvYlVD-jLv_Idg_p5K1g"
]

# --- تنظیمات دفتر وکالت ---
OFFICE_NAME = "⚖️ دفتر وکالت اکبر کلانتری ⚖️"
ADMIN_USERNAMES = ["Edalat_khahan_nikomanesh"] 
LOGO_URL = "https://data.1024tera.com/thumbnail/76cb21b60b101a13fc993ebbfd0c77ed" 
LAT, LON = 35.69704164675403, 51.25442710834557

admin_ids = set()

# --- بخش ضد-مرگ برای لیارا (Health Check) ---
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bale Bot is running healthy!")

def start_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    try:
        server = HTTPServer(('0.0.0.0', port), DummyHandler)
        print(f"🌐 Health-check server started on port {port}...")
        server.serve_forever()
    except Exception as e:
        print(f"Server Error: {e}")

# --- توابع کمکی ---
def get_ai_response(user_text):
    try:
        payload = {
            "model": "gpt-4o", 
            "messages": [
                {"role": "system", "content": f"شما یک دستیار حقوقی ارشد و بسیار مودب برای {OFFICE_NAME} هستید. پاسخ‌ها را کوتاه، حرفه‌ای و کاربردی بنویسید."},
                {"role": "user", "content": user_text}
            ],
            "temperature": 0.7
        }
        headers = {'Authorization': f'Bearer {AI_API_KEY}', 'Content-Type': 'application/json'}
        response = requests.post(AI_URL, json=payload, headers=headers, timeout=15)
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return "سیستم مشاوره هوشمند در دسترس نیست. لطفاً با دفتر تماس بگیرید."

def call_bale_api(token, method, params=None):
    try:
        url = f"https://tapi.bale.ai/bot{token}/{method}"
        if method == "getUpdates":
            response = requests.get(url, params=params, timeout=20)
        else:
            response = requests.post(url, json=params, timeout=20)

        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return None

def run_bot_worker(token):
    global admin_ids
    offset = 0
    print(f"🚀 ربات بله با توکن {token[:10]}... فعال شد.")

    keyboard = {
        "keyboard": [
            [{"text": "🤖 مشاوره هوشمند (AI)"}], 
            [{"text": "🟢 درخواست تماس فوری", "request_contact": True}],
            [{"text": "🔵 ارسال مدارک پرونده"}, {"text": "🟡 پیگیری وضعیت"}],
            [{"text": "📞 تلفن و ساعت کاری"}, {"text": "🏢 آدرس دفتر"}, {"text": "📍 نقشه (لوکیشن)"}]
        ], "resize_keyboard": True
    }

    while True:
        try:
            updates = call_bale_api(token, "getUpdates", {"offset": offset, "timeout": 10})
            if updates and updates.get("ok"):
                for up in updates["result"]:
                    offset = up["update_id"] + 1
                    if "message" not in up: continue
                    msg = up["message"]

                    cid = msg["chat"]["id"]
                    fname = msg["from"].get("first_name", "کاربر")
                    uname = msg["from"].get("username", "")

                    if uname in ADMIN_USERNAMES:
                        admin_ids.add(cid)

                    if "contact" in msg:
                        phone = msg['contact']['phone_number']
                        for aid in admin_ids:
                            call_bale_api(token, "sendMessage", {"chat_id": aid, "text": f"🚨 درخواست تماس (بله)\n👤 {fname}\n📞 {phone}"})
                        call_bale_api(token, "sendMessage", {"chat_id": cid, "text": "✅ شماره شما دریافت شد. خانم گلزار با شما تماس می‌گیرند.", "reply_markup": keyboard})
                        continue

                    if "text" in msg:
                        txt = msg["text"]
                        if txt == "/start":
                            call_bale_api(token, "sendPhoto", {"chat_id": cid, "photo": LOGO_URL, "caption": f"✨ سلام جناب {fname}\nبه سامانه رسمی و فوق‌هوشمند {OFFICE_NAME} خوش آمدید."})
                            call_bale_api(token, "sendMessage", {"chat_id": cid, "text": "لطفاً یک گزینه را انتخاب کنید:", "reply_markup": keyboard})
                        elif txt == "🤖 مشاوره هوشمند (AI)":
                            call_bale_api(token, "sendMessage", {"chat_id": cid, "text": "🤖 بخش مشاوره هوشمند فعال است. سوال خود را بنویسید.", "reply_markup": keyboard})
                        elif txt == "📞 تلفن و ساعت کاری":
                            call_bale_api(token, "sendMessage", {"chat_id": cid, "text": "⏳ ساعت کاری: ۱۷ الی ۲۰\n☎️ ثابت: 02144526484\n📱 مدیریت (خانم گلزار): 09120746035", "reply_markup": keyboard})
                        elif txt == "🏢 آدرس دفتر":
                            call_bale_api(token, "sendMessage", {"chat_id": cid, "text": "🏢 تهران، تهرانسر، بلوار اصلی، نبش خیابان ۱۸، ساختمان مهرگان، پلاک ۱۲، طبقه ۴، واحد ۱۴", "reply_markup": keyboard})
                        elif txt == "📍 نقشه (لوکیشن)":
                            neshan_link = f"https://nshn.ir/ee_bvgtGIxJZ84/search?q={LAT},{LON}"
                            call_bale_api(token, "sendMessage", {"chat_id": cid, "text": f"📍 لینک نقشه نشان:\n{neshan_link}", "reply_markup": keyboard})
                            call_bale_api(token, "sendLocation", {"chat_id": cid, "latitude": LAT, "longitude": LON})
                        elif txt == "🔵 ارسال مدارک پرونده":
                            call_bale_api(token, "sendMessage", {"chat_id": cid, "text": "لطفاً مدارک خود را به صورت عکس یا فایل PDF ارسال کنید. 📄", "reply_markup": keyboard})
                        elif txt == "🟡 پیگیری وضعیت":
                            call_bale_api(token, "sendMessage", {"chat_id": cid, "text": "لطفاً نام کامل و شماره پرونده خود را ارسال کنید. ⏳", "reply_markup": keyboard})
                        else:
                            ai_ans = get_ai_response(txt)
                            call_bale_api(token, "sendMessage", {"chat_id": cid, "text": f"🤖 پاسخ دستیار هوشمند:\n\n{ai_ans}", "reply_markup": keyboard})
                            for aid in admin_ids:
                                call_bale_api(token, "sendMessage", {"chat_id": aid, "text": f"📩 سوال {fname} در بله:\n{txt}\n\n🤖 AI:\n{ai_ans}"})

                    elif ("photo" in msg or "document" in msg):
                        for aid in admin_ids:
                            call_bale_api(token, "forwardMessage", {"chat_id": aid, "from_chat_id": cid, "message_id": msg["message_id"]})

                        call_bale_api(token, "sendMessage", {"chat_id": cid, "text": "✅ فایل دریافت شد و برای مدیریت ارسال گردید.", "reply_markup": keyboard})

            time.sleep(1)
        except Exception as e:
            print(f"Worker Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    print(f"🚀 در حال راه اندSازی سیستم وکالت جناب کلانتری (نسخه بله)...")
    threading.Thread(target=start_dummy_server, daemon=True).start()
    threads = []
    for t in TOKENS:
        thread = threading.Thread(target=run_bot_worker, args=(t,))
        thread.start()
        threads.append(thread)
    while True:
        time.sleep(1)

import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import telebot
from yt_dlp import YoutubeDL

# Render serveri 24/7 to'xtamay ishlashi uchun ichki veb-server (Health Check)
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_health_check_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

# Veb-serverni orqa fonda ishga tushirish
threading.Thread(target=run_health_check_server, daemon=True).start()

TOKEN = "8807227538:AAGIzOc1Txeqq05e8ljMuR8ycwgvP66_b7A"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message, 
        "🎵 Salom! Qaysi musiqani qidiryapsiz?\n\n"
        "Qo'shiq nomi yoki ijrochini yozib yuboring:"
    )

@bot.message_handler(func=lambda message: True)
def download_and_send_music(message):
    query = message.text
    status_msg = bot.reply_to(message, "⚡ Qidirilmoqda...")

    file_path = None
    try:
        ydl_opts = {
            'format': 'ba[ext=m4a]/ba/b',
            'outtmpl': 'music.%(ext)s',
            'quiet': True,
            'default_search': 'ytsearch1',
            'nocheckcertificate': True
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=True)
            if 'entries' in info:
                video_info = info['entries'][0]
            else:
                video_info = info

            title = video_info.get('title', 'Musiqa')
            file_path = ydl.prepare_filename(video_info)

        with open(file_path, 'rb') as audio:
            bot.send_audio(
                message.chat.id, 
                audio, 
                title=title, 
                caption="🤖 @my_melody_music_bot"
            )

        bot.delete_message(message.chat.id, status_msg.message_id)

    except Exception as e:
        bot.edit_message_text(
            "❌ Musiqa topilmadi.", 
            message.chat.id, 
            status_msg.message_id
        )
    finally:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)

bot.infinity_polling()
               

import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import telebot
from yt_dlp import YoutubeDL

# Render serveri 24/7 o'chmay ishlashi uchun veb-server (Health Check)
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_health_check_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

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
            'format': 'bestaudio/best',
            'outtmpl': 'music.%(ext)s',
            'quiet': True,
            'no_warnings': True,
            'default_search': 'ytsearch1',
            'nocheckcertificate': True,
            'geo_bypass': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=True)
            if info and 'entries' in info and len(info['entries']) > 0:
                video_info = info['entries'][0]
            elif info:
                video_info = info
            else:
                raise Exception("Musiqa topilmadi")

            title = video_info.get('title', 'Musiqa')
            file_path = ydl.prepare_filename(video_info)

        if file_path and os.path.exists(file_path):
            with open(file_path, 'rb') as audio:
                bot.send_audio(
                    message.chat.id, 
                    audio, 
                    title=title, 
                    caption="🤖 @my_melody_music_bot"
                )
            bot.delete_message(message.chat.id, status_msg.message_id)
        else:
            raise Exception("Fayl saqlanmadi")

    except Exception as e:
        print(f"XATOLIK: {e}")
        bot.edit_message_text(
            "❌ Musiqa topilmadi yoki yuklashda xatolik bo'ldi.", 
            message.chat.id, 
            status_msg.message_id
        )
    finally:
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass

bot.infinity_polling()

               

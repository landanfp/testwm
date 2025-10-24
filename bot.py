from pyrogram import Client, filters
from fastapi import FastAPI
import threading, os
from watermark import add_animated_watermark

API_ID = '3335796'
API_HASH = '138b992a0e672e8346d8439c3f42ea78'
BOT_TOKEN = '8189638115:AAEYMDvummCXAPgdpavZbYHa3YuXpOzkRBY'

# مسیر پوشه دانلودها
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# --- Pyrogram bot ---
bot = Client("watermark-bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot.on_message(filters.command("start"))
async def start(_, message):
    await message.reply_text("👋 سلام! ویدیوت رو بفرست تا واترمارک متحرک روی اون اضافه کنم 🎬")

@bot.on_message(filters.video)
async def handle_video(_, message):
    await message.reply_text("⏳ در حال پردازش واترمارک...")
    input_path = os.path.join(DOWNLOAD_DIR, f"{message.video.file_unique_id}.mp4")
    output_path = os.path.join(DOWNLOAD_DIR, f"out_{message.video.file_unique_id}.mp4")

    # دانلود ویدیو
    video_file = await message.download(file_name=input_path)

    # پردازش واترمارک در thread جداگانه
    def process_and_send():
        try:
            add_animated_watermark(input_path, "logo.png", output_path)
            # ارسال ویدیو پس از اتمام
            bot.send_video(message.chat.id, output_path, caption="✅ واترمارک اضافه شد!")
        finally:
            if os.path.exists(input_path):
                os.remove(input_path)
            if os.path.exists(output_path):
                os.remove(output_path)

    threading.Thread(target=process_and_send, daemon=True).start()

# --- FastAPI برای Health Check ---
api = FastAPI()

@api.get("/")
def health():
    return {"status": "ok"}

def run_api():
    import uvicorn
    uvicorn.run(api, host="0.0.0.0", port=8080)

threading.Thread(target=run_api, daemon=True).start()

# --- اجرای Pyrogram ---
bot.run()

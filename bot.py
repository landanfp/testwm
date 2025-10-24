from pyrogram import Client, filters
from fastapi import FastAPI
import threading
import uvicorn

API_ID = '3335796'
API_HASH = '138b992a0e672e8346d8439c3f42ea78'
BOT_TOKEN = '8189638115:AAEYMDvummCXAPgdpavZbYHa3YuXpOzkRBY'

app = Client("watermark-bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- FastAPI برای Health Check ---
api = FastAPI()

@api.get("/")
def health():
    return {"status": "ok"}

# --- اجرای FastAPI در Thread جدا ---
def run_api():
    uvicorn.run(api, host="0.0.0.0", port=8080)

threading.Thread(target=run_api).start()

# --- Pyrogram bot ---
@app.on_message(filters.command("start"))
async def start(_, message):
    await message.reply_text("سلام! ویدیوت رو بفرست تا واترمارک اضافه کنم 🎬")

@app.on_message(filters.video)
async def handle_video(_, message):
    await message.reply_text("⏳ در حال پردازش واترمارک...")
    # کد واترمارک خودت اینجا اضافه شود

app.run()

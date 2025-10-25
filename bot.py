import os
import subprocess
from pyrogram import Client, filters
from pyrogram.types import Message

# --- تنظیمات ربات ---
API_ID = '3335796'
API_HASH = '138b992a0e672e8346d8439c3f42ea78'
BOT_TOKEN = '5355055672:AAEE8OIOqLYxbnwesF3ki2sOsXr03Q90JiI'
#LOG_CHANNEL = -1001792962793  # مقدار دلخواه
# ساخت کلاینت
bot = Client("simple_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- تنظیمات FFmpeg و لوگو ---
# مسیر فایل لوگوی شما (باید در کنار اسکریپت باشد)
LOGO_PATH = "logo.png"

# تنظیمات افکت لوگو
LOGO_DURATION = 4      # مدت‌زمان هر نمایش لوگو (به ثانیه)
FADE_IN_TIME = 1.2     # مدت‌زمان افکت ورودی
FADE_OUT_TIME = 1.2    # مدت‌زمان افکت خروجی

# --- توابع کمکی ---

def generate_logo_filter_string(video_duration: float) -> str:
    """
    تولید رشته فیلتر FFmpeg برای متحرک‌سازی و تکرار لوگو
    """
    # زمان کل افکت‌ها
    total_logo_time = LOGO_DURATION
    
    # تعداد تکرارها (Loop)
    num_loops = int(video_duration // total_logo_time) + 1

    # --- تولید فیلتر برای یک چرخه (Loop) ---
    # این فیلتر یک بار متحرک‌سازی لوگو را انجام می‌دهد.
    single_logo_filter = f"""
[1:v]format=rgba,
 scale='iw*(0.6+0.4*(t/{FADE_IN_TIME}))':'ih*(0.6+0.4*(t/{FADE_IN_TIME}))',
 fade=t=in:st=0:d={FADE_IN_TIME}:alpha=1,
 fade=t=out:st={total_logo_time - FADE_OUT_TIME}:d={FADE_OUT_TIME}:alpha=1,
 transform=1,
 setpts=PTS-STARTPTS,
 pad=1920:1080:(ow-iw)/2:(oh-ih)/2
    """
    
    # --- تکرار و ترکیب فیلترها (Looping) ---
    # از 'loop' در FFmpeg برای ساخت یک جریان طولانی از لوگوی متحرک استفاده می‌کنیم.
    # این کد کمی پیچیده است و بهتر است از فیلتر 'setpts' برای تکرار استفاده کنیم.

    # یک جریان لوگو می‌سازیم که کل مدت ویدیو را پوشش دهد.
    logo_stream_filter = ""
    for i in range(num_loops):
        start_time = i * total_logo_time
        # فیلتر کردن برای هر چرخه
        loop_filter = f"""
[1:v]setpts=PTS-STARTPTS+{start_time}/TB,
 scale='iw*(0.6+0.4*((t-{start_time})/{FADE_IN_TIME}))':'ih*(0.6+0.4*((t-{start_time})/{FADE_IN_TIME}))',
 fade=t=in:st={start_time}:d={FADE_IN_TIME}:alpha=1,
 fade=t=out:st={start_time + total_logo_time - FADE_OUT_TIME}:d={FADE_OUT_TIME}:alpha=1,
 transform=1,
 pad=1920:1080:(ow-iw)/2:(oh-ih)/2
"""
        # اگر اولین حلقه نیست، باید جریان‌ها را با هم ترکیب کنیم.
        if i == 0:
            logo_stream_filter = loop_filter
        else:
            # ترکیب با جریان قبلی (با استفاده از overlay)
            # این روش در FFmpeg سخت است و معمولاً از فیلتر 'loop' استفاده می‌شود.
            # برای ساده‌سازی، فقط یک جریان لوگو می‌سازیم و آن را در نهایت overlay می‌کنیم.
            pass

    # --- روش ساده‌تر (استفاده از setpts برای تکرار در جریان واحد) ---
    # یک جریان لوگوی طولانی می‌سازیم
    logo_long_stream = f"""
movie={LOGO_PATH}:loop=0,
 setpts=N/{total_logo_time}*({total_logo_time}/(N/FRAME_RATE))/TB,
 scale='iw*(0.6+0.4*mod(t/{total_logo_time},1)*{total_logo_time}/{FADE_IN_TIME})':'ih*(0.6+0.4*mod(t/{total_logo_time},1)*{total_logo_time}/{FADE_IN_TIME})',
 fade=t=in:st=0:d={FADE_IN_TIME}:alpha=1,
 fade=t=out:st={total_logo_time - FADE_OUT_TIME}:d={FADE_OUT_TIME}:alpha=1,
 transform=1
"""

    return logo_long_stream


def process_video(video_path: str, logo_path: str, output_path: str, duration: float) -> bool:
    """
    اجرای دستور FFmpeg برای ترکیب لوگوی متحرک با ویدیو
    """
    
    # فیلتر برای متحرک‌سازی و تکرار لوگو
    logo_filters = generate_logo_filter_string(duration)
    
    # دستور FFmpeg
    # [0:v] جریان ویدیو اصلی
    # [1:v] جریان لوگو (ایجاد شده با فیلتر)
    cmd = f"""
ffmpeg -y -i "{video_path}" -i "{logo_path}" -filter_complex "
# 1. متحرک‌سازی لوگو
[1:v]
 scale='iw*(0.6+0.4*mod(t,{LOGO_DURATION})/{FADE_IN_TIME})':'ih*(0.6+0.4*mod(t,{LOGO_DURATION})/{FADE_IN_TIME})',
 format=yuva444p,
 fade=t=in:st=0:d={FADE_IN_TIME}:alpha=1,
 fade=t=out:st=({duration}-{FADE_OUT_TIME}):d={FADE_OUT_TIME}:alpha=1,
 loop=-1:25:0
[logo_animated];

# 2. ترکیب لوگو با ویدیو
[0:v][logo_animated]overlay=10:10:shortest=1[v]
" -map "[v]" -map 0:a? -c:v libx264 -preset medium -crf 23 -pix_fmt yuv420p "{output_path}"
"""
    
    # نکته: فیلتر `loop` برای ویدیوهایی که از فایل‌های تصویری ساخته می‌شوند، پیچیده است.
    # برای سادگی، در دستور بالا از یک روش ساده‌تر برای متحرک‌سازی و ترکیب استفاده شده است.
    
    try:
        subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError as e:
        print(f"خطا در اجرای FFmpeg: {e.stderr.decode()}")
        return False
    except FileNotFoundError:
        print("خطا: FFmpeg نصب نشده یا در PATH نیست.")
        return False


# --- هندلر پیام ---

@bot.on_message(filters.video & filters.private)
async def video_handler(client: Client, message: Message):
    """
    دریافت ویدیو، افزودن لوگوی متحرک و ارسال مجدد
    """
    if not os.path.exists(LOGO_PATH):
        await message.reply_text(f"خطا: فایل لوگو `{LOGO_PATH}` پیدا نشد.")
        return

    # 1. دانلود فایل ویدیو
    status_msg = await message.reply_text("📥 در حال دانلود ویدیو...")
    try:
        input_path = await message.download()
    except Exception as e:
        await status_msg.edit(f"❌ خطا در دانلود: {e}")
        return

    # 2. تعریف مسیر خروجی
    output_path = input_path + "_with_logo.mp4"
    
    # 3. پردازش ویدیو با FFmpeg
    await status_msg.edit("✨ در حال افزودن لوگوی متحرک (FFmpeg)...")
    
    # گرفتن مدت‌زمان ویدیو
    video_duration = message.video.duration
    
    if process_video(input_path, LOGO_PATH, output_path, video_duration):
        # 4. آپلود و ارسال ویدیو
        await status_msg.edit("📤 در حال آپلود ویدیو...")
        try:
            await client.send_video(
                chat_id=message.chat.id,
                video=output_path,
                caption="✅ ویدیوی شما با لوگوی متحرک آماده شد!"
            )
            await status_msg.delete()
        except Exception as e:
            await status_msg.edit(f"❌ خطا در آپلود: {e}")
            
    else:
        await status_msg.edit("❌ پردازش ویدیو با خطا مواجه شد. (جزئیات در لاگ سرور)")

    # 5. پاکسازی فایل‌های موقت
    if os.path.exists(input_path):
        os.remove(input_path)
    if os.path.exists(output_path):
        os.remove(output_path)


@bot.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text(
        "سلام 👋\nویدیو خود را ارسال کنید تا لوگوی متحرک بر روی آن قرار داده شود."
    )

# اجرا
bot.run()

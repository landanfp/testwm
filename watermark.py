import subprocess

def add_animated_watermark(input_file, logo_path, output_file):
    """
    اضافه کردن واترمارک PNG با انیمیشن Fade و Pulsing به ویدیو.
    """
    
    # --- پارامترهای انیمیشن ---
    fade_in_dur = 1  # مدت زمان ورود محوشونده (ثانیه)
    # شروع خروج محوشونده (ثانیه) - بهتر است این مقدار را به طول ویدیو وابسته کنید!
    # اگر ویدیو کوتاه باشد، ممکن است زودتر از موعد ناپدید شود.
    fade_out_start = 5 
    fade_out_dur = 1   # مدت زمان خروج محوشونده (ثانیه)

    # --- فیلتر FFmpeg با انیمیشن‌های ترکیبی ---
    filter_complex = f"""
    [1]format=rgba,
    fade=t=in:st=0:d={fade_in_dur}:alpha=1,
    fade=t=out:st={fade_out_start}:d={fade_out_dur}:alpha=1,
    scale='iw*(1+0.1*sin(2*PI*t/3))':'ih*(1+0.1*sin(2*PI*t/3))'[wm];
    [0][wm]overlay=W-w-40:H-h-40:format=auto
    """

    cmd = [
        "ffmpeg",
        "-i", input_file,
        "-i", logo_path,
        "-filter_complex", filter_complex,
        "-c:a", "copy",
        # اضافه کردن pix_fmt برای سازگاری بهتر با برخی پلیرها/تلگرام
        "-pix_fmt", "yuv420p", 
        output_file,
        "-y" # بازنویسی فایل خروجی در صورت وجود
    ]
    
    # اجرا و بررسی خطا
    subprocess.run(cmd, check=True)

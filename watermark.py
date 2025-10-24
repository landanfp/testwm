import subprocess

def add_animated_watermark(input_file, logo_path, output_file):
    """
    اضافه کردن لوگو + متن SeriesPlus1 به ویدیو
    متن هر 5 ثانیه تکرار می‌شود (از راست می‌آید و داخل لوگو محو می‌شود)
    """
    # مثال ساده، متن پایین و گوشه راست
    text_filter = (
        "drawtext=text='SeriesPlus1':"
        "fontcolor=white:fontsize=36:x=w-tw-10*t:y=h-60:"
        "enable='between(mod(t\,10)\,0\,5)',"
        "drawtext=text='SeriesPlus1':"
        "fontcolor=white:fontsize=36:x=-tw+10*t:y=h-60:"
        "enable='between(mod(t\,10)\,5\,10)'"
    )

    # ffmpeg اجرا می‌شود و فایل خروجی تولید می‌شود
    cmd = [
        "ffmpeg",
        "-i", input_file,
        "-i", logo_path,
        "-filter_complex",
        f"[1:v]scale=100:-1[logo];[0:v][logo]overlay=10:10,{text_filter}",
        "-c:a", "copy",
        output_file,
        "-y"
    ]
    subprocess.run(cmd, check=True)

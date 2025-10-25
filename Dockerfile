# -------------------------------
#  Base Image
# -------------------------------
FROM python:3.10-slim

# جلوگیری از پرسش‌های interactive
ENV DEBIAN_FRONTEND=noninteractive

# نصب ابزارهای مورد نیاز
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# تنظیم مسیر کاری
WORKDIR /app

# کپی فایل‌های پروژه داخل کانتینر
COPY . /app

# نصب پکیج‌ها
RUN pip install --no-cache-dir -r requirements.txt

# درصورت نیاز: لوگو را به مسیر درست کپی کن (اگر در ریپو داری)
# COPY logo.png /app/logo.png

# پورت اختیاری برای health check
EXPOSE 8000

# فرمان اجرا
CMD ["python", "bot.py"]

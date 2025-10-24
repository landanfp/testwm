# مرحله 1: استفاده از تصویر پایه پایتون سبک
FROM python:3.11-slim

# جلوگیری از پرسیدن سوال در حین نصب
ENV DEBIAN_FRONTEND=noninteractive

# نصب ffmpeg برای واترمارک و ابزارهای ضروری
RUN apt-get update && apt-get install -y ffmpeg && apt-get clean

# ایجاد پوشه کاری داخل کانتینر
WORKDIR /app

# کپی فایل‌های پروژه به کانتینر
COPY . .

# نصب نیازمندی‌ها
RUN pip install --no-cache-dir -r requirements.txt

# پورت اختیاری (برای FastAPI در صورت توسعه بعدی)
EXPOSE 8080

# اجرای ربات
CMD ["python", "bot.py"]

#!/usr/bin/env python3
# خادم بسيط لتشغيل Neon Trader V7 على Windows
import os
import webbrowser
import http.server
import socketserver
from pathlib import Path

print("🪟 Neon Trader V7 - Windows Server")
print("=" * 40)

# البحث عن مجلد الملفات
possible_paths = [
    r"C:\Users\alkra\Desktop\neon_trader_v7\src\static",
    r"C:\Users\alkra\Downloads\neon_trader_v7\src\static", 
    r"C:\Users\alkra\Documents\neon_trader_v7\src\static",
    r".\neon_trader_v7\src\static",
    r".\src\static",
    r"static"
]

static_folder = None
for path in possible_paths:
    if os.path.exists(path):
        static_folder = path
        print(f"✅ وجدت الملفات في: {path}")
        break

if not static_folder:
    print("❌ لم أجد مجلد الملفات!")
    print("📁 ضع هذا الملف في نفس مجلد neon_trader_v7")
    input("اضغط Enter للخروج...")
    exit()

# تغيير المجلد الحالي
os.chdir(static_folder)
print(f"📂 المجلد الحالي: {os.getcwd()}")

# فحص وجود index.html
if not os.path.exists("index.html"):
    print("❌ ملف index.html غير موجود!")
    print("تأكد من وجود الملفات في المجلد الصحيح")
    input("اضغط Enter للخروج...")
    exit()

# تشغيل الخادم
PORT = 8080
print(f"🚀 بدء تشغيل الخادم على المنفذ {PORT}...")

try:
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        url = f"http://localhost:{PORT}"
        print(f"✅ الخادم يعمل على: {url}")
        print("🌐 سيتم فتح المتصفح تلقائياً...")
        print("⏹️  لإيقاف الخادم: اضغط Ctrl+C")
        print("-" * 40)
        
        # فتح المتصفح تلقائياً
        webbrowser.open(url)
        
        # تشغيل الخادم
        httpd.serve_forever()
        
except KeyboardInterrupt:
    print("\n👋 تم إيقاف الخادم بنجاح!")
except Exception as e:
    print(f"❌ خطأ: {e}")
    print("💡 جرب تشغيل الملف كـ Administrator")
    input("اضغط Enter للخروج...")


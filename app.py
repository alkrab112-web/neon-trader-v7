from flask import Flask, send_from_directory, jsonify

# نستخدم نفس المجلد كـ static و template (لأن index.html و css و js بنفس المكان)
app = Flask(__name__, static_folder=".", template_folder=".")

# الصفحة الرئيسية → تعرض index.html
@app.route("/")
def home():
    return send_from_directory(".", "index.html")

# أي ملفات ثابتة (CSS/JS/صور)
@app.route("/<path:path>")
def static_proxy(path):
    return send_from_directory(".", path)

# نقطة فحص للتأكد أن السيرفر شغال
@app.route("/api/health")
def health():
    return jsonify(status="ok", app="neon-trader-v7")

if __name__ == "__main__":
    print(">> Starting Flask on http://127.0.0.1:5600")
    app.run(debug=True, port=5600)


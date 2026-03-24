from flask import Flask, request, jsonify, send_from_directory
from meck import handle
import json
import os
from datetime import datetime

app = Flask(__name__)

USERS_FILE = "users.json"
LOGS_FILE = "logs.json"
KB_FILE = "knowledge.json"

# =========================
# SAFE LOAD FUNCTIONS
# =========================
def load_json(file, default):
    try:
        with open(file) as f:
            return json.load(f)
    except:
        return default

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

# =========================
# ROUTES
# =========================

# 👉 AI PAGE
@app.route("/")
def index():
    return send_from_directory(".", "web.html")


# =========================
# USER REGISTER
# =========================
@app.route("/register", methods=["POST"])
def register():
    username = request.json.get("username", "").strip()
    if not username:
        return jsonify({"status": "error"})

    users = load_json(USERS_FILE, {})

    if username not in users:
        users[username] = {
            "joined": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        save_json(USERS_FILE, users)

    return jsonify({"status": "ok"})


# =========================
# MAIN AI COMMAND
# =========================
@app.route("/command", methods=["POST"])
def command():
    data = request.json
    text = data.get("text", "")
    username = data.get("username", "web-user")

    reply = handle(text, web_mode=True)

    logs = load_json(LOGS_FILE, [])
    logs.append({
        "user": username,
        "question": text,
        "reply": reply,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    save_json(LOGS_FILE, logs)

    return jsonify({"reply": reply})


# =========================
# ADMIN
# =========================
@app.route("/admin-data")
def admin_data():
    users = load_json(USERS_FILE, {})
    logs = load_json(LOGS_FILE, [])

    return jsonify({
        "total_users": len(users),
        "total_logs": len(logs),
        "users": users,
        "logs": logs
    })


# =========================
# KNOWLEDGE VIEW
# =========================
@app.route("/knowledge")
def view_knowledge():
    return jsonify(load_json(KB_FILE, {}))


# =========================
# KNOWLEDGE UI
# =========================
@app.route("/knowledge-ui")
def knowledge_ui():
    return send_from_directory(".", "knowledge_admin.html")


@app.route("/knowledge-data")
def knowledge_data():
    return jsonify(load_json(KB_FILE, {}))


# =========================
# ADD KNOWLEDGE
# =========================
@app.route("/knowledge-add", methods=["POST"])
def knowledge_add():
    data = request.json
    question = data.get("question", "").strip().lower()
    answer = data.get("answer", "").strip()

    if not question or not answer:
        return jsonify({"status": "error"})

    kb = load_json(KB_FILE, {})
    kb[question] = answer
    save_json(KB_FILE, kb)

    return jsonify({"status": "ok"})


# =========================
# DELETE KNOWLEDGE
# =========================
@app.route("/knowledge-delete", methods=["POST"])
def knowledge_delete():
    question = request.json.get("question", "").strip().lower()

    kb = load_json(KB_FILE, {})

    if question in kb:
        del kb[question]
        save_json(KB_FILE, kb)
        return jsonify({"status": "deleted"})

    return jsonify({"status": "not_found"})


# =========================
# JSON UPLOAD (MERGE)
# =========================
@app.route("/knowledge-upload", methods=["POST"])
def knowledge_upload():
    if "file" not in request.files:
        return jsonify({"status": "no_file"})

    file = request.files["file"]

    if not file.filename.endswith(".json"):
        return jsonify({"status": "invalid_file"})

    try:
        uploaded = json.load(file)
        if not isinstance(uploaded, dict):
            return jsonify({"status": "invalid_json"})
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)})

    kb = load_json(KB_FILE, {})
    kb.update(uploaded)

    save_json(KB_FILE, kb)

    return jsonify({
        "status": "ok",
        "added": len(uploaded)
    })


# =========================
# RUN (RENDER READY)
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

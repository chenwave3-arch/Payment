# =========================================================
#  么͢⃟ TRY ⎯͢⎯⃝𝑪𝒉𝒆𝒏 | 黑金名媛 — PAYMENT BOT
#  🔥 BLACK-GOLD PREMIUM EDITION 🔥
#  Bot Telegram + Web Admin Panel (1 File)
# =========================================================

from telebot import TeleBot, types
from datetime import datetime
import qrcode
import time
import json
import os
from threading import Thread

# ================= WEB ADMIN (Flask) =================
try:
    from flask import Flask, render_template_string, request, redirect, flash, jsonify, make_response
    from werkzeug.utils import secure_filename
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("⚠️ Flask not installed. Admin panel disabled.")
    print("   Install: pip install flask werkzeug")

# ================= CONFIG FILE =================
CONFIG_FILE = "bot_config.json"

DEFAULT_CONFIG = {
    "TOKEN": "8830910496:AAGr7AW7STS8eemJtqnbjM3X3emuQZ4RgfY",
    "ADMIN_ID": 6870427036,
    "OWNER_USERNAME": "ChenwavePRO",
    "BOT_NAME": "么͢⃟ TRY ⎯͢⎯⃝𝑪𝒉𝒆𝒏 | 黑金名媛",
    "DANA_NUMBER": "083832175672",
    "GOPAY_NUMBER": "083898331732",
    "SEABANK_NUMBER": "901301871184",
    "QRIS_STRING": "00020101021126610014COM.GO-JEK.WWW01189360091438123565060210G8123565060303UMI51440014ID.CO.QRIS.WWW0215ID10265142840030303UMI5204899953033605802ID5925FastDrop CN , Digital & K6008SUKABUMI61054315462070703A016304BD32",
    "WELCOME_IMAGE": "welcome.jpg",
    "DANA_ENABLED": True,
    "GOPAY_ENABLED": True,
    "SEABANK_ENABLED": True,
    "QRIS_ENABLED": True,
    "CUSTOM_METHODS": [],
    "THEME": "blackgold",
    "WELCOME_TEXT": "Selamat datang di bot pembayaran premium.\n\n💎 Fast Response\n💎 Auto Notification\n💎 Modern Inline UI\n💎 24 Jam Online",
    "ADMIN_PASSWORD": "admin123"
}

# ================= LOAD/SAVE CONFIG =================

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)

config = load_config()

# ================= EXTRACT VALUES =================
TOKEN = config["TOKEN"]
ADMIN_ID = config["ADMIN_ID"]
OWNER_USERNAME = config["OWNER_USERNAME"]
BOT_NAME = config["BOT_NAME"]
DANA_NUMBER = config["DANA_NUMBER"]
GOPAY_NUMBER = config["GOPAY_NUMBER"]
SEABANK_NUMBER = config["SEABANK_NUMBER"]
QRIS_STRING = config["QRIS_STRING"]
WELCOME_IMAGE = config["WELCOME_IMAGE"]

bot = TeleBot(TOKEN, parse_mode="HTML")

# ================= QRIS GENERATOR =================

def generate_qris():
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(QRIS_STRING)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save("qris.png")
    return "qris.png"

# ================= MAIN MENU KEYBOARD =================

def main_menu():
    kb = types.InlineKeyboardMarkup(row_width=2)
    cfg = load_config()

    buttons = []

    if cfg.get("DANA_ENABLED", True):
        buttons.append(types.InlineKeyboardButton("💙 DANA", callback_data="dana"))

    if cfg.get("GOPAY_ENABLED", True):
        buttons.append(types.InlineKeyboardButton("💚 GOPAY", callback_data="gopay"))

    if cfg.get("SEABANK_ENABLED", True):
        buttons.append(types.InlineKeyboardButton("🌊 SEABANK", callback_data="seabank"))

    if cfg.get("QRIS_ENABLED", True):
        buttons.append(types.InlineKeyboardButton("🔴 QRIS", callback_data="qris"))

    for method in cfg.get("CUSTOM_METHODS", []):
        if method.get("enabled", True):
            emoji = {"ovo": "🟣", "shopeepay": "🟠", "linkaja": "🔵", "ovo": "🟣"}.get(method["name"].lower(), "💳")
            buttons.append(types.InlineKeyboardButton(
                f"{emoji} {method['name'].upper()}",
                callback_data=f"custom_{method['name']}"
            ))

    for i in range(0, len(buttons), 2):
        if i + 1 < len(buttons):
            kb.add(buttons[i], buttons[i+1])
        else:
            kb.add(buttons[i])

    kb.add(
        types.InlineKeyboardButton("👑 OWNER", url=f"https://t.me/{OWNER_USERNAME}"),
        types.InlineKeyboardButton("🔄 REFRESH", callback_data="refresh")
    )

    return kb

# ================= START COMMAND =================

@bot.message_handler(commands=['start'])
def start(message):
    try:
        cfg = load_config()
        welcome_text = cfg.get("WELCOME_TEXT", DEFAULT_CONFIG["WELCOME_TEXT"])

        caption = f"""
╔══════════════════════════════════╗
  ✦ <b>{cfg['BOT_NAME']}</b> ✦
╚══════════════════════════════════╝

<blockquote expandable>
{welcome_text}
</blockquote>

━━━━━━━━━━━━━━━━━━━━━━━
💳 <b>METODE PEMBAYARAN:</b>
• DANA
• GOPAY  
• SEABANK
• QRIS ALL PAYMENT
━━━━━━━━━━━━━━━━━━━━━━━

⚡ <i>Silakan pilih metode pembayaran</i>
"""

        welcome_img = cfg.get("WELCOME_IMAGE", "welcome.jpg")
        if os.path.exists(welcome_img):
            photo = open(welcome_img, "rb")
            bot.send_photo(
                message.chat.id,
                photo,
                caption=caption,
                reply_markup=main_menu()
            )
        else:
            bot.send_message(
                message.chat.id,
                caption,
                reply_markup=main_menu()
            )
    except Exception as e:
        bot.reply_to(message, f"❌ ERROR:\n<code>{e}</code>")

# ================= CALLBACK HANDLER =================

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    cfg = load_config()

    if call.data == "refresh":
        bot.answer_callback_query(call.id, "✅ Menu direfresh")
        bot.edit_message_reply_markup(
            call.message.chat.id,
            call.message.message_id,
            reply_markup=main_menu()
        )
        return

    elif call.data == "done":
        waktu = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        user = call.from_user

        notif = f"""
🚨 <b>NOTIFIKASI PEMBAYARAN MASUK</b>

👤 <b>USER:</b> {user.first_name}
🆔 <b>ID:</b> <code>{user.id}</code>
👤 <b>USERNAME:</b> @{user.username or 'N/A'}
⏰ <b>WAKTU:</b> {waktu}

━━━━━━━━━━━━━━━━━━━━━━━
⚠️ USER MENEKAN TOMBOL "SUDAH TRANSFER"
━━━━━━━━━━━━━━━━━━━━━━━
"""

        bot.send_message(cfg["ADMIN_ID"], notif)
        bot.answer_callback_query(call.id, "✅ Notifikasi terkirim ke admin")

        done_text = """
╔══════════════════════════════════╗
           ✅ BERHASIL
╚══════════════════════════════════╝

<blockquote>
Notifikasi pembayaran berhasil
dikirim ke admin.
</blockquote>

⏳ <i>Mohon tunggu proses pengecekan...</i>
"""
        bot.send_message(call.message.chat.id, done_text)
        return

    methods = {
        "dana": ("💙 DANA", cfg.get("DANA_NUMBER", "")),
        "gopay": ("💚 GOPAY", cfg.get("GOPAY_NUMBER", "")),
        "seabank": ("🌊 SEABANK", cfg.get("SEABANK_NUMBER", ""))
    }

    if call.data in methods:
        name, number = methods[call.data]
        kb = types.InlineKeyboardMarkup(row_width=1)
        kb.add(
            types.InlineKeyboardButton("📋 SALIN NOMOR", url=f"https://t.me/share/url?url={number}"),
            types.InlineKeyboardButton("✅ SUDAH TRANSFER", callback_data="done"),
            types.InlineKeyboardButton("👑 HUBUNGI OWNER", url=f"https://t.me/{cfg['OWNER_USERNAME']}")
        )

        text = f"""
╔═══〔 {name} PAYMENT 〕═══╗

<blockquote>
Nomor {name.replace("💙 ", "").replace("💚 ", "").replace("🌊 ", "")}:
<code>{number}</code>
</blockquote>

⚠️ Transfer sesuai nominal.
Setelah transfer klik tombol di bawah.
"""
        bot.send_message(call.message.chat.id, text, reply_markup=kb)

    elif call.data == "qris":
        generate_qris()
        kb = types.InlineKeyboardMarkup(row_width=1)
        kb.add(
            types.InlineKeyboardButton("✅ SUDAH TRANSFER", callback_data="done"),
            types.InlineKeyboardButton("👑 HUBUNGI OWNER", url=f"https://t.me/{cfg['OWNER_USERNAME']}")
        )

        photo = open("qris.png", "rb")
        bot.send_photo(
            call.message.chat.id,
            photo,
            caption="""
╔═══〔 🔴 QRIS PAYMENT 〕═══╗

<blockquote>
Silakan scan QRIS di atas
untuk melakukan pembayaran.
</blockquote>

⚡ Support semua e-wallet & bank.
""",
            reply_markup=kb
        )

    elif call.data.startswith("custom_"):
        method_name = call.data.replace("custom_", "")
        for method in cfg.get("CUSTOM_METHODS", []):
            if method["name"].lower() == method_name.lower():
                emoji = {"ovo": "🟣", "shopeepay": "🟠", "linkaja": "🔵"}.get(method_name.lower(), "💳")
                kb = types.InlineKeyboardMarkup(row_width=1)
                kb.add(
                    types.InlineKeyboardButton("📋 SALIN NOMOR", url=f"https://t.me/share/url?url={method['number']}"),
                    types.InlineKeyboardButton("✅ SUDAH TRANSFER", callback_data="done"),
                    types.InlineKeyboardButton("👑 HUBUNGI OWNER", url=f"https://t.me/{cfg['OWNER_USERNAME']}")
                )
                text = f"""
╔═══〔 {emoji} {method_name.upper()} PAYMENT 〕═══╗

<blockquote>
Nomor {method_name.upper()}:
<code>{method['number']}</code>
</blockquote>

⚠️ Transfer sesuai nominal.
"""
                bot.send_message(call.message.chat.id, text, reply_markup=kb)
                break

# ================= ADMIN COMMANDS =================

@bot.message_handler(commands=['ping'])
def ping(message):
    bot.reply_to(message, "🏓 BOT AKTIF 24 JAM — 么͢⃟ TRY ⎯͢⎯⃝𝑪𝒉𝒆𝒏 | 黑金名媛")

@bot.message_handler(commands=['admin'])
def admin_cmd(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Lu bukan admin!")
        return

    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton("🌐 BUKA ADMIN PANEL", url="http://localhost:5000/admin"))
    bot.reply_to(message, "👑 Admin Panel:\nhttp://localhost:5000/admin", reply_markup=kb)

# ================= FLASK ADMIN PANEL HTML =================

ADMIN_HTML = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>黑金名媛 — Admin Panel</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --gold: #D4AF37;
            --gold-light: #F4E4BC;
            --gold-dark: #B8941F;
            --black: #0a0a0a;
            --black-light: #141414;
            --black-lighter: #1a1a1a;
            --red: #DC2626;
            --green: #16A34A;
            --blue: #2563EB;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Inter', sans-serif;
            background: var(--black);
            color: #e5e5e5;
            min-height: 100vh;
        }

        .login-container {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
        }

        .login-box {
            background: var(--black-lighter);
            border: 1px solid var(--gold-dark);
            border-radius: 16px;
            padding: 40px;
            width: 100%;
            max-width: 400px;
            box-shadow: 0 0 40px rgba(212, 175, 55, 0.1);
        }

        .login-box h1 {
            font-family: 'Orbitron', sans-serif;
            color: var(--gold);
            text-align: center;
            margin-bottom: 8px;
            font-size: 24px;
            letter-spacing: 2px;
        }

        .login-box .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 12px;
        }

        .form-group {
            margin-bottom: 20px;
        }

        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: var(--gold-light);
            font-size: 13px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .form-group input {
            width: 100%;
            padding: 14px 16px;
            background: var(--black);
            border: 1px solid #333;
            border-radius: 10px;
            color: #fff;
            font-size: 14px;
            transition: all 0.3s;
        }

        .form-group input:focus {
            outline: none;
            border-color: var(--gold);
            box-shadow: 0 0 10px rgba(212, 175, 55, 0.2);
        }

        .btn {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, var(--gold) 0%, var(--gold-dark) 100%);
            border: none;
            border-radius: 10px;
            color: var(--black);
            font-weight: 700;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s;
            text-transform: uppercase;
            letter-spacing: 2px;
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(212, 175, 55, 0.3);
        }

        .dashboard { display: none; }

        .sidebar {
            position: fixed;
            left: 0;
            top: 0;
            width: 260px;
            height: 100vh;
            background: var(--black-light);
            border-right: 1px solid #222;
            padding: 30px 20px;
            overflow-y: auto;
        }

        .sidebar-brand {
            font-family: 'Orbitron', sans-serif;
            color: var(--gold);
            font-size: 18px;
            text-align: center;
            margin-bottom: 8px;
            letter-spacing: 1px;
        }

        .sidebar-brand-sub {
            text-align: center;
            color: #666;
            font-size: 10px;
            margin-bottom: 30px;
            letter-spacing: 2px;
        }

        .nav-item {
            display: flex;
            align-items: center;
            padding: 12px 16px;
            margin-bottom: 4px;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s;
            color: #999;
            font-size: 14px;
        }

        .nav-item:hover, .nav-item.active {
            background: rgba(212, 175, 55, 0.1);
            color: var(--gold);
        }

        .nav-item span { margin-right: 12px; font-size: 18px; }

        .main-content {
            margin-left: 260px;
            padding: 30px 40px;
            min-height: 100vh;
        }

        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid #222;
        }

        .header h2 {
            font-family: 'Orbitron', sans-serif;
            color: var(--gold);
            font-size: 20px;
        }

        .header .status {
            display: flex;
            align-items: center;
            gap: 8px;
            background: rgba(22, 163, 74, 0.1);
            color: var(--green);
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }

        .status-dot {
            width: 8px;
            height: 8px;
            background: var(--green);
            border-radius: 50%;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .card-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .card {
            background: var(--black-light);
            border: 1px solid #222;
            border-radius: 16px;
            padding: 24px;
            transition: all 0.3s;
        }

        .card:hover {
            border-color: var(--gold-dark);
            transform: translateY(-2px);
        }

        .card-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 20px;
        }

        .card-icon {
            width: 48px;
            height: 48px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
        }

        .card-icon.dana { background: rgba(0, 120, 215, 0.1); }
        .card-icon.gopay { background: rgba(0, 168, 89, 0.1); }
        .card-icon.seabank { background: rgba(0, 100, 200, 0.1); }
        .card-icon.qris { background: rgba(220, 38, 38, 0.1); }
        .card-icon.bot { background: rgba(212, 175, 55, 0.1); }
        .card-icon.custom { background: rgba(139, 92, 246, 0.1); }

        .card-title { font-weight: 700; color: #fff; font-size: 16px; }
        .card-subtitle { color: #666; font-size: 12px; }

        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
        }

        .form-group-panel { margin-bottom: 16px; }

        .form-group-panel label {
            display: block;
            margin-bottom: 6px;
            color: #999;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .form-group-panel input, .form-group-panel textarea, .form-group-panel select {
            width: 100%;
            padding: 12px 14px;
            background: var(--black);
            border: 1px solid #333;
            border-radius: 10px;
            color: #fff;
            font-size: 14px;
            transition: all 0.3s;
            font-family: 'Inter', sans-serif;
        }

        .form-group-panel input:focus, .form-group-panel textarea:focus, .form-group-panel select:focus {
            outline: none;
            border-color: var(--gold);
        }

        .form-group-panel textarea { min-height: 100px; resize: vertical; }

        .toggle-switch {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-top: 8px;
        }

        .toggle {
            position: relative;
            width: 50px;
            height: 26px;
            background: #333;
            border-radius: 13px;
            cursor: pointer;
            transition: all 0.3s;
        }

        .toggle.active { background: var(--gold); }

        .toggle::after {
            content: '';
            position: absolute;
            width: 22px;
            height: 22px;
            background: #fff;
            border-radius: 50%;
            top: 2px;
            left: 2px;
            transition: all 0.3s;
        }

        .toggle.active::after { left: 26px; }
        .toggle-label { font-size: 13px; color: #999; }

        .btn-save {
            background: linear-gradient(135deg, var(--gold) 0%, var(--gold-dark) 100%);
            border: none;
            padding: 14px 32px;
            border-radius: 10px;
            color: var(--black);
            font-weight: 700;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 20px;
        }

        .btn-save:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(212, 175, 55, 0.3);
        }

        .btn-danger {
            background: rgba(220, 38, 38, 0.2);
            border: 1px solid var(--red);
            color: var(--red);
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 12px;
            transition: all 0.3s;
        }

        .btn-danger:hover { background: var(--red); color: #fff; }

        .btn-add {
            background: rgba(22, 163, 74, 0.2);
            border: 1px solid var(--green);
            color: var(--green);
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 12px;
            transition: all 0.3s;
            margin-bottom: 16px;
        }

        .btn-add:hover { background: var(--green); color: #fff; }

        .custom-method-item {
            background: var(--black);
            border: 1px solid #333;
            border-radius: 10px;
            padding: 16px;
            margin-bottom: 12px;
        }

        .method-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }

        .alert {
            padding: 16px 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            font-size: 14px;
        }

        .alert-success {
            background: rgba(22, 163, 74, 0.1);
            border: 1px solid var(--green);
            color: var(--green);
        }

        .alert-error {
            background: rgba(220, 38, 38, 0.1);
            border: 1px solid var(--red);
            color: var(--red);
        }

        .section-title {
            font-family: 'Orbitron', sans-serif;
            color: var(--gold);
            font-size: 16px;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid #222;
        }

        .preview-box {
            background: var(--black);
            border: 1px solid #333;
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
        }

        .preview-box h4 {
            color: var(--gold);
            margin-bottom: 12px;
            font-size: 14px;
        }

        .preview-text {
            color: #999;
            font-size: 13px;
            line-height: 1.6;
            white-space: pre-wrap;
        }

        .file-input-wrapper {
            position: relative;
            overflow: hidden;
            display: inline-block;
        }

        .file-input-wrapper input[type=file] {
            position: absolute;
            left: 0;
            top: 0;
            opacity: 0;
            cursor: pointer;
            width: 100%;
            height: 100%;
        }

        .file-input-label {
            display: inline-block;
            padding: 12px 20px;
            background: var(--black-lighter);
            border: 1px dashed #444;
            border-radius: 10px;
            color: #999;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 13px;
        }

        .file-input-label:hover {
            border-color: var(--gold);
            color: var(--gold);
        }

        .image-preview {
            max-width: 200px;
            max-height: 150px;
            border-radius: 10px;
            border: 1px solid #333;
            margin-top: 12px;
        }

        .hidden { display: none; }

        @media (max-width: 768px) {
            .sidebar { width: 100%; position: relative; height: auto; }
            .main-content { margin-left: 0; }
            .form-row { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="login-container" id="loginPage">
        <div class="login-box">
            <h1>黑金名媛</h1>
            <p class="subtitle">ADMIN PANEL — PREMIUM EDITION</p>
            <form method="POST" action="/admin/login">
                <div class="form-group">
                    <label>Password</label>
                    <input type="password" name="password" placeholder="Enter admin password" required>
                </div>
                <button type="submit" class="btn">LOGIN</button>
            </form>
        </div>
    </div>

    <div class="dashboard" id="dashboard">
        <div class="sidebar">
            <div class="sidebar-brand">黑金名媛</div>
            <div class="sidebar-brand-sub">TRY CHEN — ADMIN</div>

            <div class="nav-item active" onclick="showTab('general')">
                <span>⚙️</span> General Settings
            </div>
            <div class="nav-item" onclick="showTab('payments')">
                <span>💳</span> Payment Methods
            </div>
            <div class="nav-item" onclick="showTab('custom')">
                <span>➕</span> Custom Methods
            </div>
            <div class="nav-item" onclick="showTab('appearance')">
                <span>🎨</span> Appearance
            </div>
            <div class="nav-item" onclick="showTab('qris')">
                <span>🔴</span> QRIS Settings
            </div>
            <div class="nav-item" onclick="location.href='/admin/logout'">
                <span>🚪</span> Logout
            </div>
        </div>

        <div class="main-content">
            <div class="header">
                <h2 id="pageTitle">⚙️ GENERAL SETTINGS</h2>
                <div class="status">
                    <div class="status-dot"></div>
                    <span>BOT ONLINE</span>
                </div>
            </div>

            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="alert alert-{{ category }}">{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}

            <form method="POST" action="/admin/save" enctype="multipart/form-data">

                <div id="tab-general" class="tab-content">
                    <div class="card-grid">
                        <div class="card">
                            <div class="card-header">
                                <div class="card-icon bot">🤖</div>
                                <div>
                                    <div class="card-title">Bot Configuration</div>
                                    <div class="card-subtitle">Token & Identity</div>
                                </div>
                            </div>
                            <div class="form-group-panel">
                                <label>Bot Token</label>
                                <input type="text" name="TOKEN" value="{{ config.TOKEN }}" placeholder="APIKEY_BOT">
                            </div>
                            <div class="form-row">
                                <div class="form-group-panel">
                                    <label>Admin ID</label>
                                    <input type="number" name="ADMIN_ID" value="{{ config.ADMIN_ID }}">
                                </div>
                                <div class="form-group-panel">
                                    <label>Owner Username</label>
                                    <input type="text" name="OWNER_USERNAME" value="{{ config.OWNER_USERNAME }}" placeholder="tanpa @">
                                </div>
                            </div>
                        </div>

                        <div class="card">
                            <div class="card-header">
                                <div class="card-icon bot">✨</div>
                                <div>
                                    <div class="card-title">Bot Name & Welcome</div>
                                    <div class="card-subtitle">Branding & Greeting</div>
                                </div>
                            </div>
                            <div class="form-group-panel">
                                <label>Bot Name</label>
                                <input type="text" name="BOT_NAME" value="{{ config.BOT_NAME }}">
                            </div>
                            <div class="form-group-panel">
                                <label>Welcome Text</label>
                                <textarea name="WELCOME_TEXT" rows="4">{{ config.WELCOME_TEXT }}</textarea>
                            </div>
                        </div>
                    </div>
                </div>

                <div id="tab-payments" class="tab-content hidden">
                    <div class="card-grid">
                        <div class="card">
                            <div class="card-header">
                                <div class="card-icon dana">💙</div>
                                <div>
                                    <div class="card-title">DANA</div>
                                    <div class="card-subtitle">Blue E-Wallet</div>
                                </div>
                            </div>
                            <div class="form-group-panel">
                                <label>Nomor DANA</label>
                                <input type="text" name="DANA_NUMBER" value="{{ config.DANA_NUMBER }}">
                            </div>
                            <div class="toggle-switch">
                                <div class="toggle {{ 'active' if config.DANA_ENABLED else '' }}" onclick="toggleSwitch(this, 'DANA_ENABLED')"></div>
                                <span class="toggle-label">{{ 'Aktif' if config.DANA_ENABLED else 'Nonaktif' }}</span>
                                <input type="hidden" name="DANA_ENABLED" value="{{ 'true' if config.DANA_ENABLED else 'false' }}">
                            </div>
                        </div>

                        <div class="card">
                            <div class="card-header">
                                <div class="card-icon gopay">💚</div>
                                <div>
                                    <div class="card-title">GOPAY</div>
                                    <div class="card-subtitle">Green E-Wallet</div>
                                </div>
                            </div>
                            <div class="form-group-panel">
                                <label>Nomor GOPAY</label>
                                <input type="text" name="GOPAY_NUMBER" value="{{ config.GOPAY_NUMBER }}">
                            </div>
                            <div class="toggle-switch">
                                <div class="toggle {{ 'active' if config.GOPAY_ENABLED else '' }}" onclick="toggleSwitch(this, 'GOPAY_ENABLED')"></div>
                                <span class="toggle-label">{{ 'Aktif' if config.GOPAY_ENABLED else 'Nonaktif' }}</span>
                                <input type="hidden" name="GOPAY_ENABLED" value="{{ 'true' if config.GOPAY_ENABLED else 'false' }}">
                            </div>
                        </div>

                        <div class="card">
                            <div class="card-header">
                                <div class="card-icon seabank">🌊</div>
                                <div>
                                    <div class="card-title">SEABANK</div>
                                    <div class="card-subtitle">Sea Digital Bank</div>
                                </div>
                            </div>
                            <div class="form-group-panel">
                                <label>Nomor SeaBank</label>
                                <input type="text" name="SEABANK_NUMBER" value="{{ config.SEABANK_NUMBER }}">
                            </div>
                            <div class="toggle-switch">
                                <div class="toggle {{ 'active' if config.SEABANK_ENABLED else '' }}" onclick="toggleSwitch(this, 'SEABANK_ENABLED')"></div>
                                <span class="toggle-label">{{ 'Aktif' if config.SEABANK_ENABLED else 'Nonaktif' }}</span>
                                <input type="hidden" name="SEABANK_ENABLED" value="{{ 'true' if config.SEABANK_ENABLED else 'false' }}">
                            </div>
                        </div>
                    </div>
                </div>

                <div id="tab-custom" class="tab-content hidden">
                    <div class="section-title">➕ CUSTOM PAYMENT METHODS</div>
                    <p style="color:#666; margin-bottom:20px; font-size:13px;">Tambah metode pembayaran lain (OVO, ShopeePay, LinkAja, dll)</p>

                    <div id="customMethods">
                        {% for method in config.CUSTOM_METHODS %}
                        <div class="custom-method-item">
                            <div class="method-header">
                                <span style="color:#fff; font-weight:600;">{{ method.name }}</span>
                                <button type="button" class="btn-danger" onclick="this.closest('.custom-method-item').remove()">HAPUS</button>
                            </div>
                            <div class="form-row">
                                <div class="form-group-panel">
                                    <label>Nama Metode</label>
                                    <input type="text" name="custom_name[]" value="{{ method.name }}">
                                </div>
                                <div class="form-group-panel">
                                    <label>Nomor</label>
                                    <input type="text" name="custom_number[]" value="{{ method.number }}">
                                </div>
                            </div>
                            <div class="toggle-switch">
                                <div class="toggle {{ 'active' if method.enabled else '' }}" onclick="toggleSwitch(this, 'custom_enabled_{{ loop.index0 }}')"></div>
                                <span class="toggle-label">{{ 'Aktif' if method.enabled else 'Nonaktif' }}</span>
                                <input type="hidden" name="custom_enabled[]" value="{{ 'true' if method.enabled else 'false' }}">
                            </div>
                        </div>
                        {% endfor %}
                    </div>

                    <button type="button" class="btn-add" onclick="addCustomMethod()">+ TAMBAH METODE</button>
                </div>

                <div id="tab-appearance" class="tab-content hidden">
                    <div class="card-grid">
                        <div class="card">
                            <div class="card-header">
                                <div class="card-icon bot">🖼️</div>
                                <div>
                                    <div class="card-title">Welcome Image</div>
                                    <div class="card-subtitle">Gambar start command</div>
                                </div>
                            </div>
                            <div class="form-group-panel">
                                <label>Upload Gambar Baru</label>
                                <div class="file-input-wrapper">
                                    <div class="file-input-label">📁 Pilih File (JPG/PNG)</div>
                                    <input type="file" name="welcome_image" accept="image/*" onchange="previewImage(this)">
                                </div>
                            </div>
                            {% if config.WELCOME_IMAGE and config.WELCOME_IMAGE != 'welcome.jpg' %}
                            <div style="margin-top:12px; color:#666; font-size:12px;">
                                Current: {{ config.WELCOME_IMAGE }}
                            </div>
                            {% endif %}
                            <div id="imagePreviewContainer" style="display:none;">
                                <img id="imagePreview" class="image-preview" src="" alt="Preview">
                            </div>
                        </div>

                        <div class="card">
                            <div class="card-header">
                                <div class="card-icon bot">🔐</div>
                                <div>
                                    <div class="card-title">Admin Password</div>
                                    <div class="card-subtitle">Ganti password panel</div>
                                </div>
                            </div>
                            <div class="form-group-panel">
                                <label>Password Baru (kosongkan = tetap)</label>
                                <input type="password" name="ADMIN_PASSWORD_NEW" placeholder="••••••">
                            </div>
                        </div>
                    </div>

                    <div class="preview-box">
                        <h4>👁️ PREVIEW WELCOME TEXT</h4>
                        <div class="preview-text">{{ config.WELCOME_TEXT }}</div>
                    </div>
                </div>

                <div id="tab-qris" class="tab-content hidden">
                    <div class="card">
                        <div class="card-header">
                            <div class="card-icon qris">🔴</div>
                            <div>
                                <div class="card-title">QRIS Configuration</div>
                                <div class="card-subtitle">All Payment QR Code</div>
                            </div>
                        </div>
                        <div class="form-group-panel">
                            <label>QRIS String (EMVCo)</label>
                            <textarea name="QRIS_STRING" rows="6">{{ config.QRIS_STRING }}</textarea>
                        </div>
                        <div class="toggle-switch">
                            <div class="toggle {{ 'active' if config.QRIS_ENABLED else '' }}" onclick="toggleSwitch(this, 'QRIS_ENABLED')"></div>
                            <span class="toggle-label">{{ 'Aktif' if config.QRIS_ENABLED else 'Nonaktif' }}</span>
                            <input type="hidden" name="QRIS_ENABLED" value="{{ 'true' if config.QRIS_ENABLED else 'false' }}">
                        </div>
                    </div>
                </div>

                <div style="position: sticky; bottom: 0; background: var(--black); padding: 20px 0; border-top: 1px solid #222; margin-top: 30px;">
                    <button type="submit" class="btn-save">💾 SIMPAN SEMUA PERUBAHAN</button>
                </div>
            </form>
        </div>
    </div>

    <script>
        {% if logged_in %}
        document.getElementById('loginPage').style.display = 'none';
        document.getElementById('dashboard').style.display = 'block';
        {% endif %}

        function showTab(tab) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
            document.getElementById('tab-' + tab).classList.remove('hidden');
            document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
            event.target.closest('.nav-item').classList.add('active');

            const titles = {
                'general': '⚙️ GENERAL SETTINGS',
                'payments': '💳 PAYMENT METHODS',
                'custom': '➕ CUSTOM METHODS',
                'appearance': '🎨 APPEARANCE',
                'qris': '🔴 QRIS SETTINGS'
            };
            document.getElementById('pageTitle').textContent = titles[tab];
        }

        function toggleSwitch(el, inputName) {
            el.classList.toggle('active');
            const input = document.querySelector('input[name="' + inputName + '"]');
            if (input) {
                input.value = el.classList.contains('active') ? 'true' : 'false';
            }
            const label = el.nextElementSibling;
            label.textContent = el.classList.contains('active') ? 'Aktif' : 'Nonaktif';
        }

        function addCustomMethod() {
            const container = document.getElementById('customMethods');
            const id = Date.now();
            const div = document.createElement('div');
            div.className = 'custom-method-item';
            div.innerHTML = `
                <div class="method-header">
                    <span style="color:#fff; font-weight:600;">Metode Baru</span>
                    <button type="button" class="btn-danger" onclick="this.closest('.custom-method-item').remove()">HAPUS</button>
                </div>
                <div class="form-row">
                    <div class="form-group-panel">
                        <label>Nama Metode</label>
                        <input type="text" name="custom_name[]" placeholder="Contoh: OVO">
                    </div>
                    <div class="form-group-panel">
                        <label>Nomor</label>
                        <input type="text" name="custom_number[]" placeholder="08xxxxxxxx">
                    </div>
                </div>
                <div class="toggle-switch">
                    <div class="toggle active" onclick="toggleSwitch(this, 'custom_enabled_${id}')"></div>
                    <span class="toggle-label">Aktif</span>
                    <input type="hidden" name="custom_enabled[]" value="true">
                </div>
            `;
            container.appendChild(div);
        }

        function previewImage(input) {
            if (input.files && input.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    document.getElementById('imagePreview').src = e.target.result;
                    document.getElementById('imagePreviewContainer').style.display = 'block';
                };
                reader.readAsDataURL(input.files[0]);

                const label = input.previousElementSibling;
                label.textContent = '📁 ' + input.files[0].name;
                label.style.borderColor = 'var(--gold)';
                label.style.color = 'var(--gold)';
            }
        }
    </script>
</body>
</html>
"""

# ================= FLASK APP =================

app = Flask(__name__)
app.secret_key = "blackgold_premium_secret_key_2026"

@app.route("/admin", methods=["GET"])
def admin_panel():
    if not FLASK_AVAILABLE:
        return "Flask not installed. Run: pip install flask werkzeug"

    cfg = load_config()
    logged_in = request.args.get("logged_in") == "1" or request.cookies.get("admin_auth") == "1"
    return render_template_string(ADMIN_HTML, config=cfg, logged_in=logged_in)

@app.route("/admin/login", methods=["POST"])
def admin_login():
    cfg = load_config()
    password = request.form.get("password", "")

    if password == cfg.get("ADMIN_PASSWORD", "admin123"):
        response = redirect("/admin?logged_in=1")
        response.set_cookie("admin_auth", "1", max_age=3600)
        return response
    else:
        flash("Password salah!", "error")
        return redirect("/admin")

@app.route("/admin/logout")
def admin_logout():
    response = redirect("/admin")
    response.set_cookie("admin_auth", "", expires=0)
    return response

@app.route("/admin/save", methods=["POST"])
def admin_save():
    if request.cookies.get("admin_auth") != "1":
        flash("Silakan login dulu!", "error")
        return redirect("/admin")

    cfg = load_config()

    for field in ["TOKEN", "ADMIN_ID", "OWNER_USERNAME", "BOT_NAME", 
                  "DANA_NUMBER", "GOPAY_NUMBER", "SEABANK_NUMBER", 
                  "QRIS_STRING", "WELCOME_TEXT"]:
        if field in request.form:
            if field == "ADMIN_ID":
                cfg[field] = int(request.form[field])
            else:
                cfg[field] = request.form[field]

    for toggle in ["DANA_ENABLED", "GOPAY_ENABLED", "SEABANK_ENABLED", "QRIS_ENABLED"]:
        cfg[toggle] = request.form.get(toggle) == "true"

    custom_names = request.form.getlist("custom_name[]")
    custom_numbers = request.form.getlist("custom_number[]")
    custom_enabled = request.form.getlist("custom_enabled[]")

    cfg["CUSTOM_METHODS"] = []
    for i in range(len(custom_names)):
        if custom_names[i].strip():
            cfg["CUSTOM_METHODS"].append({
                "name": custom_names[i].strip(),
                "number": custom_numbers[i].strip() if i < len(custom_numbers) else "",
                "enabled": custom_enabled[i] == "true" if i < len(custom_enabled) else True
            })

    if "welcome_image" in request.files:
        file = request.files["welcome_image"]
        if file and file.filename:
            filename = secure_filename(file.filename)
            file.save(filename)
            cfg["WELCOME_IMAGE"] = filename

    new_password = request.form.get("ADMIN_PASSWORD_NEW", "").strip()
    if new_password:
        cfg["ADMIN_PASSWORD"] = new_password

    save_config(cfg)

    global TOKEN, ADMIN_ID, OWNER_USERNAME, BOT_NAME, DANA_NUMBER, GOPAY_NUMBER, SEABANK_NUMBER, QRIS_STRING, WELCOME_IMAGE
    TOKEN = cfg["TOKEN"]
    ADMIN_ID = cfg["ADMIN_ID"]
    OWNER_USERNAME = cfg["OWNER_USERNAME"]
    BOT_NAME = cfg["BOT_NAME"]
    DANA_NUMBER = cfg["DANA_NUMBER"]
    GOPAY_NUMBER = cfg["GOPAY_NUMBER"]
    SEABANK_NUMBER = cfg["SEABANK_NUMBER"]
    QRIS_STRING = cfg["QRIS_STRING"]
    WELCOME_IMAGE = cfg["WELCOME_IMAGE"]

    flash("✅ Semua perubahan berhasil disimpan!", "success")
    return redirect("/admin?logged_in=1")

@app.route("/admin/api/config", methods=["GET"])
def api_config():
    if request.cookies.get("admin_auth") != "1":
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify(load_config())

# ================= RUN EVERYTHING =================

def run_flask():
    if FLASK_AVAILABLE:
        app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)

if __name__ == "__main__":
    if FLASK_AVAILABLE:
        flask_thread = Thread(target=run_flask, daemon=True)
        flask_thread.start()
        print("🌐 Admin Panel: http://localhost:5000/admin")
        print("   Default Password: admin123")

    print("🔥 么͢⃟ TRY ⎯͢⎯⃝𝑪𝒉𝒆𝒏 | 黑金名媛 — BOT AKTIF 🔥")

    while True:
        try:
            bot.infinity_polling(skip_pending=True)
        except Exception as e:
            print(f"ERROR: {e}")
            time.sleep(5)

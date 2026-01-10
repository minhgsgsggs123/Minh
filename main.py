import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask, render_template_string
import json
import threading
import os
import datetime

# --- CẤU HÌNH ---
TOKEN = "MTQxMTczNjAwMTg5MzYzNDI2MA.GRvwrb.DqwRCosvO7B3p_8UHyEyCNZu79MBW0IzSLFPHY"  # <--- THAY TOKEN CỦA BẠN VÀO ĐÂY
DATA_FILE = "data.json"

# --- NỘI DUNG HTML (ĐÃ TÍCH HỢP JINJA2) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Clone Tab Roblox cloud phone</title>
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="Web tải clone Roblox treo tab cloud phone" />
    <link rel="icon" href="https://sf-static.upanhlaylink.com/img/image_202511288379248b5631b4dfcdf9230690b6d489.jpg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/particles.js/2.0.0/particles.min.js"></script>
    <style>
        body { margin: 0; padding: 20px 20px 80px; font-family: 'Poppins', sans-serif; color: #fff; background: #000; overflow-x: hidden; min-height: 100vh; }
        #particles-js { position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: -1; }
        .main-title { text-align: center; font-weight: 800; font-size: 3.5em; margin: 20px 0 10px; text-shadow: 0 0 15px rgba(255,255,255,0.6); }
        .subtitle { text-align: center; color: #ffeaa7; font-size: 1.3em; margin-bottom: 50px; }
        .game-list { list-style: none; padding: 0; max-width: 1100px; margin: 0 auto; display: grid; grid-template-columns: repeat(auto-fit, minmax(340px, 1fr)); gap: 30px; }
        .game-item { background: rgba(0,0,0,0.6); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.15); border-radius: 20px; padding: 25px; text-align: center; transition: all 0.4s ease; }
        .game-item:hover { transform: translateY(-12px); box-shadow: 0 20px 40px rgba(253,121,168,0.3); }
        .game-item img { width: 120px; height: 120px; border-radius: 16px; margin-bottom: 15px; box-shadow: 0 6px 15px rgba(0,0,0,0.5); object-fit: cover; }
        .game-item h2 { margin: 0 0 15px; font-size: 1.5em; }
        .status-section { margin: 20px 0; }
        .status-title { color: #ffeaa7; text-transform: uppercase; font-weight: 800; margin-bottom: 10px; }
        .status-line { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.1); font-size: 0.95em; }
        .status-line:last-child { border: none; }
        .download-btn { display: block; width: 88%; margin: 12px auto; padding: 14px; border-radius: 50px; text-decoration: none; color: #fff; font-weight: 600; font-size: 1.05em; position: relative; overflow: hidden; transition: all 0.3s; z-index: 1; }
        .download-btn:hover { transform: translateY(-4px); box-shadow: 0 10px 25px rgba(0,0,0,0.5); }
        .download-btn-international { background: linear-gradient(90deg, #00A65A, #00D878); box-shadow: 0 8px 20px rgba(0,216,120,0.5); }
        .download-btn-vng { background: linear-gradient(135deg, #C0392B, #E74C3C); box-shadow: 0 8px 20px rgba(192,57,43,0.6); }
        .download-btn.disabled { background: #555; pointer-events: none; opacity: 0.7; }

        /* Hiệu ứng nền nút */
        .download-btn-international::before { content: '🌐'; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 120px; opacity: 0.25; pointer-events: none; z-index: -1; }
        .download-btn-vng::before { content: '★'; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 140px; color: #FBC02D; opacity: 0.35; pointer-events: none; z-index: -1; }

        .discord-btn, .music-btn { position: fixed; right: 20px; background: rgba(0, 0, 0, 0.7); backdrop-filter: blur(10px); color: white; padding: 12px 20px; border-radius: 50px; font-weight: 600; box-shadow: 0 6px 20px rgba(0,0,0,0.5); z-index: 1000; transition: 0.3s; border: 1px solid rgba(255, 255, 255, 0.2); display: flex; align-items: center; gap: 10px; font-size: 0.95em; }
        .discord-btn:hover, .music-btn:hover { background: rgba(0, 0, 0, 0.9); transform: scale(1.08); }
        .discord-btn { bottom: 20px; background: rgba(88, 101, 242, 0.8); }
        .music-btn { bottom: 85px; background: rgba(255, 255, 255, 0.15); }

        .preview-image { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0, 0, 0, 0); white-space: nowrap; border: 0; }
        footer { text-align: center; margin: 60px 0 20px; color: #aaa; }

        @media (max-width: 768px) { .main-title { font-size: 2.6em; } }
    </style>
</head>
<body>

<div class="preview-image">
    <img src="https://sf-static.upanhlaylink.com/img/image_202511288379248b5631b4dfcdf9230690b6d489.jpg" alt="Preview" width="1200" height="630">
</div>

<div id="particles-js"></div>

<audio id="backgroundAudio" loop preload="auto" style="display:none;">
    <source src="{{ data.music_url }}" type="audio/mpeg">
</audio>

<h1 class="main-title">TẢI CÔNG CỤ HACK ROBLOX</h1>
<p class="subtitle">Clone Client cho cloud phone (Quốc Tế & VNG)</p>

<ul class="game-list">
    {% for tab in data.tabs %}
    <li class="game-item">
        <img src="{{ tab.avatar }}" alt="{{ tab.name }}">
        <h2>{{ tab.name }}</h2>
        <div class="status-section">
            <div class="status-title">Status</div>
            <div class="status-line"><span>Quốc tế</span><span class="status">{{ tab.status_qt }}</span></div>
            <div class="status-line"><span>VNG</span><span class="status">{{ tab.status_vng }}</span></div>
        </div>

        {% if tab.link_qt %}
            <a href="{{ tab.link_qt }}" class="download-btn download-btn-international">Quốc Tế</a>
        {% else %}
            <a href="#" class="download-btn disabled">QT (Chưa có link)</a>
        {% endif %}

        {% if tab.link_vng %}
            <a href="{{ tab.link_vng }}" class="download-btn download-btn-vng">VNG</a>
        {% else %}
            <a href="#" class="download-btn disabled">VNG (Chưa có link)</a>
        {% endif %}
    </li>
    {% endfor %}
</ul>

<a href="{{ data.discord_url }}" class="discord-btn" target="_blank">
    <i class="fab fa-discord btn-icon"></i> Support
</a>

<button id="toggleMusicBtn" class="music-btn">
    <i class="fas fa-music btn-icon"></i>
    <span id="musicText">Bật nhạc</span>
</button>

<footer><p>© 2025 Trang clone hack roblox của mèo béo</p></footer>

<script>
    particlesJS('particles-js', {"particles":{"number":{"value":140,"density":{"enable":true,"value_area":800}},"color":{"value":"#ffffff"},"shape":{"type":"circle"},"opacity":{"value":0.8,"random":true,"anim":{"enable":true,"speed":1,"opacity_min":0.2,"sync":false}},"size":{"value":3,"random":true,"anim":{"enable":true,"speed":2,"size_min":0.3}},"line_linked":{"enable":true,"distance":130,"color":"#ffffff","opacity":0.35,"width":1},"move":{"enable":true,"speed":1.5,"direction":"none","random":true,"straight":false,"out_mode":"out"}},"interactivity":{"detect_on":"canvas","events":{"onhover":{"enable":true,"mode":"grab"},"onclick":{"enable":true,"mode":"push"},"resize":true},"modes":{"grab":{"distance":140,"line_linked":{"opacity":1}},"push":{"particles_nb":4}}},"retina_detect":true});

    const audio = document.getElementById('backgroundAudio');
    const btn = document.getElementById('toggleMusicBtn');
    const musicText = document.getElementById('musicText');
    audio.volume = 0.25;

    btn.addEventListener('click', () => {
        if (audio.paused) {
            audio.play().then(() => {
                musicText.textContent = 'Tắt nhạc';
            }).catch(error => {
                alert('Trình duyệt chặn phát nhạc tự động. Vui lòng bấm lại.');
            });
        } else {
            audio.pause();
            musicText.textContent = 'Bật nhạc';
        }
    });
</script>
</body>
</html>
"""

# --- KHỞI TẠO FLASK ---
app = Flask(__name__)

def load_data():
    if not os.path.exists(DATA_FILE):
        # Dữ liệu mẫu nếu chưa có file
        default_data = {
            "music_url": "https://pomf2.lain.la/f/r72xqmpk.mp3",
            "discord_url": "https://discord.gg/qqNyGW6rcX",
            "tabs": [
                {
                    "name": "Clone Delta",
                    "avatar": "https://sf-static.upanhlaylink.com/img/image_2025110728cf4c9241c606466a1b9f17da738ed3.jpg",
                    "link_qt": "https://gofile.io/d/tPUHO3",
                    "link_vng": "https://gofile.io/d/dYoSMM",
                    "status_qt": "🟢",
                    "status_vng": "🟢"
                }
            ]
        }
        save_data(default_data)
        return default_data

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

@app.route("/")
def home():
    data = load_data()
    # Dùng render_template_string để render trực tiếp từ biến HTML_TEMPLATE
    return render_template_string(HTML_TEMPLATE, data=data)

def run_flask():
    app.run(host="0.0.0.0", port=8080)

# --- KHỞI TẠO DISCORD BOT ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot đã online: {bot.user}")
    print("🌍 Web đang chạy tại http://0.0.0.0:8080")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Đã đồng bộ {len(synced)} lệnh Slash.")
    except Exception as e:
        print(e)

# --- CÁC LỆNH PREFIX (!) ---

@bot.command(name="thay")
async def thay_thong_tin(ctx, *, args: str):
    # Cú pháp: !thay nhạc [link] hoặc !thay link discord [link]
    data = load_data()

    if args.startswith("nhạc"):
        link_nhac = args.replace("nhạc", "", 1).strip()
        data["music_url"] = link_nhac
        save_data(data)
        await ctx.send(f"✅ Đã thay đổi nhạc nền web thành: <{link_nhac}>")

    elif args.startswith("link discord"):
        link_ds = args.replace("link discord", "", 1).strip()
        data["discord_url"] = link_ds
        save_data(data)
        await ctx.send(f"✅ Đã thay đổi nút Discord web thành: <{link_ds}>")
    else:
        await ctx.send("❌ Sai cú pháp. Dùng: `!thay nhạc [link]` hoặc `!thay link discord [link]`")

# --- CÁC LỆNH SLASH (/) ---

@bot.tree.command(name="add_tab", description="Thêm một tab game mới vào web")
@app_commands.describe(
    ten="Tên của bản hack/game",
    avatar="Link ảnh đại diện",
    link_quoc_te="Link tải bản QT (Không nhập = 🔴)",
    link_vng="Link tải bản VNG (Không nhập = 🔴)"
)
async def add_tab(interaction: discord.Interaction, ten: str, avatar: str, link_quoc_te: str = None, link_vng: str = None):
    data = load_data()

    status_qt = "🟢" if link_quoc_te else "🔴"
    status_vng = "🟢" if link_vng else "🔴"

    new_tab = {
        "name": ten,
        "avatar": avatar,
        "link_qt": link_quoc_te if link_quoc_te else "",
        "link_vng": link_vng if link_vng else "",
        "status_qt": status_qt,
        "status_vng": status_vng
    }

    data["tabs"].append(new_tab)
    save_data(data)

    embed = discord.Embed(title="✅ Đã thêm Tab mới", color=discord.Color.green())
    embed.add_field(name="Tên", value=ten)
    embed.add_field(name="Status QT", value=status_qt)
    embed.add_field(name="Status VNG", value=status_vng)
    embed.set_thumbnail(url=avatar)

    await interaction.response.send_message(embed=embed)

# Hàm hỗ trợ Autocomplete để gợi ý tên Tab
async def tab_autocomplete(interaction: discord.Interaction, current: str):
    data = load_data()
    tabs = [tab["name"] for tab in data["tabs"]]
    return [
        app_commands.Choice(name=tab_name, value=tab_name)
        for tab_name in tabs if current.lower() in tab_name.lower()
    ]

@bot.tree.command(name="set_link", description="Sửa link tải cho tab có sẵn")
@app_commands.autocomplete(tab=tab_autocomplete)
async def set_link(interaction: discord.Interaction, tab: str, link_quoc_te: str = None, link_vng: str = None):
    data = load_data()
    found = False

    for item in data["tabs"]:
        if item["name"] == tab:
            if link_quoc_te is not None:
                item["link_qt"] = link_quoc_te
                item["status_qt"] = "🟢" if link_quoc_te else "🔴"

            if link_vng is not None:
                item["link_vng"] = link_vng
                item["status_vng"] = "🟢" if link_vng else "🔴"

            found = True
            break

    if found:
        save_data(data)
        await interaction.response.send_message(f"✅ Đã cập nhật link cho tab **{tab}**.")
    else:
        await interaction.response.send_message(f"❌ Không tìm thấy tab tên **{tab}**.", ephemeral=True)

@bot.tree.command(name="set_status", description="Chỉnh tay trạng thái (🟢, 🔴, 🟡...)")
@app_commands.autocomplete(tab=tab_autocomplete)
async def set_status(interaction: discord.Interaction, tab: str, quoc_te: str = None, vng: str = None):
    data = load_data()
    found = False

    for item in data["tabs"]:
        if item["name"] == tab:
            if quoc_te: item["status_qt"] = quoc_te
            if vng: item["status_vng"] = vng
            found = True
            break

    if found:
        save_data(data)
        await interaction.response.send_message(f"✅ Đã cập nhật trạng thái cho tab **{tab}**.\nQT: {item['status_qt']} | VNG: {item['status_vng']}")
    else:
        await interaction.response.send_message(f"❌ Không tìm thấy tab tên **{tab}**.", ephemeral=True)

# --- CHẠY SERVER ---
if __name__ == "__main__":
    t = threading.Thread(target=run_flask)
    t.start()
    bot.run(TOKEN)

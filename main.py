# app.py (Web Backend & API)
from flask import Flask, render_template, request, jsonify, url_for
import sqlite3
import uuid
import requests
import asyncio
import os
import discord # Thư viện Discord cho chức năng gửi DM

app = Flask(__name__)

# --- CẤU HÌNH CỦA BẠN (PHẢI GIỐNG VỚI bot.py) ---
DATABASE = 'mcoin.db'
API_SECRET_KEY = "meowbot" # Dùng để bảo mật giữa Web và Bot
DISCORD_BOT_TOKEN = "MTQxOTY4MDU0NTAxNjY0MzY4Ng.Gj1wmQ.Qe5h8nQfXg_OVIAcusnKlJ2nOibxnWR7Tsh1k" # Dùng để gửi DM

# --- SETUP DISCORD CLIENT CHỈ ĐỂ GỬI DM ---
# Không dùng commands.Bot, chỉ dùng discord.Client
# Khởi tạo Client để gửi DM. Lưu ý: Cần chạy trong asyncio loop.
discord_client = discord.Client(intents=discord.Intents.default())

@discord_client.event
async def on_ready():
    print(f'Discord Client (cho DM) đã sẵn sàng.')

# Hàm kết nối DB
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row 
    return conn

# Hàm gửi DM cho người dùng
async def gui_dm_thanh_cong(user_id, amount):
    # Chờ Discord Client sẵn sàng
    await discord_client.wait_until_ready()
    
    try:
        user = await discord_client.fetch_user(user_id)
        if user:
            embed = discord.Embed(
                title="💰 Nhận Mcoin Thành Công!",
                description=f"Bạn đã nhận **{amount} Mcoin** từ nhiệm vụ vượt link.",
                color=0xffd700 # Vàng
            )
            await user.send(embed=embed)
            print(f"Đã gửi DM cho user {user_id}")
        else:
            print(f"Không tìm thấy user với ID: {user_id}")
    except Exception as e:
        print(f"Lỗi khi gửi DM: {e}")

# --- API CHO DISCORD BOT GỌI ĐỂ TẠO NHIỆM VỤ ---
@app.route('/api/create_task', methods=['POST'])
def create_task():
    # Bảo mật: Kiểm tra secret key
    if request.headers.get('Authorization') != API_SECRET_KEY:
        return jsonify({"status": False, "message": "Unauthorized"}), 401

    data = request.json
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({"status": False, "message": "Missing user_id"}), 400

    new_token = str(uuid.uuid4())
    
    conn = get_db_connection()
    try:
        # 0 = CHUA_NHAN, 1 = DA_NHAN
        conn.execute("INSERT INTO rewards (token, user_id, status) VALUES (?, ?, 0)", 
                     (new_token, user_id))
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({"status": False, "message": "Token creation failed"}), 500
    finally:
        conn.close()

    # Trả về URL mà Discord Bot sẽ rút gọn
    claim_url = url_for('claim_reward', token=new_token, _external=True)
    return jsonify({
        "status": True, 
        "token": new_token,
        "claim_url": claim_url
    })

# --- TUYẾN ĐƯỜNG HIỂN THỊ TRANG NHẬN COIN ---
@app.route('/claim')
def claim_reward():
    token = request.args.get('token')
    
    if not token:
        return "Lỗi: Thiếu Token nhiệm vụ.", 400

    conn = get_db_connection()
    reward = conn.execute('SELECT * FROM rewards WHERE token = ?', (token,)).fetchone()
    conn.close()

    if not reward:
        return "Lỗi: Token không hợp lệ.", 404
        
    is_claimed = reward['status'] == 1
    
    return render_template('claim.html', token=token, is_claimed=is_claimed)

# --- API XỬ LÝ NHẬN THƯỞNG AN TOÀN ---
@app.route('/api/claim', methods=['POST'])
def api_claim():
    data = request.json
    token = data.get('token')
    AMOUNT = 200 # Số lượng Mcoin thưởng
    
    if not token:
        return jsonify({"status": "error", "message": "Thiếu token."}), 400

    conn = get_db_connection()
    try:
        reward = conn.execute('SELECT * FROM rewards WHERE token = ?', (token,)).fetchone()

        if not reward:
            return jsonify({"status": "error", "message": "Token không hợp lệ."}), 404

        if reward['status'] == 1:
            return jsonify({"status": "claimed", "message": "Bạn đã nhận Mcoin rồi."}), 200

        # --- BƯỚC AN TOÀN: CỘNG MCOIN VÀ CẬP NHẬT TRẠNG THÁI ---
        user_id = reward['user_id']

        # 1. Cập nhật trạng thái trong DB (Ngăn tải lại trang nhận thêm)
        conn.execute("UPDATE rewards SET status = 1 WHERE token = ?", (token,))
        
        # 2. Cộng Mcoin vào bảng Users
        conn.execute('''
            INSERT INTO users (user_id, mcoin) VALUES (?, ?) 
            ON CONFLICT(user_id) DO UPDATE SET mcoin = mcoin + ?
        ''', (user_id, AMOUNT, AMOUNT))
        
        conn.commit()

        # 3. Gửi DM thông báo qua Discord Client (Chạy trong Background)
        asyncio.run_coroutine_threadsafe(gui_dm_thanh_cong(user_id, AMOUNT), app.loop)
            
        return jsonify({"status": "success", "message": "Đã cộng Mcoin thành công!", "amount": AMOUNT})

    except Exception as e:
        conn.rollback()
        print(f"Lỗi hệ thống: {e}")
        return jsonify({"status": "error", "message": "Đã xảy ra lỗi hệ thống."}), 500
    finally:
        conn.close()


# --- CHẠY CẢ FLASK VÀ DISCORD CLIENT ---
def run_flask_and_discord():
    # 1. Khởi chạy Discord Client (dùng asyncio)
    loop = asyncio.get_event_loop()
    loop.create_task(discord_client.start(DISCORD_BOT_TOKEN))
    
    # 2. Chạy Flask Web Server
    # Thiết lập app.loop cho Flask để dùng trong hàm gui_dm_thanh_cong
    app.loop = loop 
    app.run(debug=True, use_reloader=False, port=5000)

if __name__ == '__main__':
    # Chạy Web Backend và Discord Client DM trong cùng một process
    run_flask_and_discord()

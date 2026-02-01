const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

const app = express();
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

const NOTIFICATION_FILE = path.join(__dirname, 'notifications.json');
const PORT = process.env.PORT || 8080;

// Load notifications từ file
function loadNotifications() {
  try {
    if (fs.existsSync(NOTIFICATION_FILE)) {
      return JSON.parse(fs.readFileSync(NOTIFICATION_FILE, 'utf-8'));
    }
  } catch (err) {
    console.error('Lỗi load notifications:', err);
  }
  return [];
}

// Save notifications vào file
function saveNotifications(data) {
  try {
    fs.writeFileSync(NOTIFICATION_FILE, JSON.stringify(data, null, 2));
  } catch (err) {
    console.error('Lỗi save notifications:', err);
  }
}

// ============ CALLBACK ENDPOINT (từ gachthefasl) ============
app.post('/callback', (req, res) => {
  const callbackData = req.body;
  const requestId = callbackData.request_id;

  if (!requestId) {
    return res.json({ status: 0, message: 'request_id not found' });
  }

  console.log(`[CALLBACK] Nhận callback từ gachthefasl - Request ID: ${requestId}`);
  console.log(`[CALLBACK] Data:`, callbackData);

  // Lưu callback vào queue
  const notifications = loadNotifications();
  
  // Kiểm tra xem đã có callback này chưa
  const existingIndex = notifications.findIndex(n => n.request_id === requestId);
  
  if (existingIndex !== -1) {
    notifications[existingIndex] = {
      ...callbackData,
      timestamp: new Date().toISOString()
    };
    console.log(`[CALLBACK] Cập nhật callback đã tồn tại`);
  } else {
    notifications.push({
      ...callbackData,
      timestamp: new Date().toISOString()
    });
    console.log(`[CALLBACK] Lưu callback mới vào queue`);
  }

  saveNotifications(notifications);

  // Trả lời gachthefasl ngay
  res.json({ status: 1, message: 'OK' });
});

// ============ POLLING ENDPOINT (Bot hỏi) ============
app.get('/api/notifications', (req, res) => {
  const notifications = loadNotifications();

  if (notifications.length === 0) {
    return res.json({ 
      status: 0, 
      message: 'Không có thông báo',
      data: [] 
    });
  }

  console.log(`[API] Bot hỏi, trả ${notifications.length} thông báo`);

  // Trả toàn bộ 100% callback cho bot
  res.json({
    status: 1,
    message: 'Có thông báo',
    data: notifications,
    count: notifications.length
  });
});

// ============ DELETE ENDPOINT (Bot xóa sau khi xử lý) ============
app.post('/api/delete-notification', (req, res) => {
  const { request_id } = req.body;

  if (!request_id) {
    return res.json({ status: 0, message: 'request_id not found' });
  }

  const notifications = loadNotifications();
  const newNotifications = notifications.filter(n => n.request_id !== request_id);

  if (newNotifications.length === notifications.length) {
    return res.json({ status: 0, message: 'request_id không tồn tại' });
  }

  saveNotifications(newNotifications);
  console.log(`[API] Đã xóa notification: ${request_id}`);

  res.json({ status: 1, message: 'Đã xóa' });
});

// ============ DELETE ALL (Clear hết) ============
app.post('/api/clear-all', (req, res) => {
  saveNotifications([]);
  console.log(`[API] Đã clear toàn bộ notifications`);
  res.json({ status: 1, message: 'Đã xóa hết' });
});

// ============ HOME PAGE ============
app.get('/', (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html lang="vi">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>GẠCH THẺ MEOW - API</title>
      <script src="https://cdn.tailwindcss.com"></script>
      <style>
        body { font-family: 'Inter', sans-serif; background: #0a0a0a; overflow: hidden; }
        .glass { background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(20px); border: 1px solid rgba(255, 255, 255, 0.08); }
        .status-dot { animation: pulse 2s infinite; box-shadow: 0 0 12px #00ff88; }
        @keyframes pulse { 0%, 100% { transform: scale(1); opacity: 1; } 50% { transform: scale(1.4); opacity: 0.4; } }
      </style>
    </head>
    <body class="h-screen flex items-center justify-center">
      <div class="glass p-12 rounded-[32px] max-w-md w-[90%] text-center shadow-2xl">
        <img src="https://sf-static.upanhlaylink.com/img/image_202511288379248b5631b4dfcdf9230690b6d489.jpg" class="w-24 h-24 rounded-3xl mx-auto mb-6 border border-white/10 p-1 shadow-lg">
        <div class="inline-flex items-center bg-green-500/10 text-[#00ff88] px-4 py-1.5 rounded-full text-xs font-bold tracking-widest mb-6 border border-green-500/20">
          <span class="status-dot w-2 h-2 bg-[#00ff88] rounded-full mr-2"></span> API ONLINE
        </div>
        <h1 class="text-3xl font-extrabold tracking-tighter mb-4 uppercase bg-gradient-to-br from-white to-[#ffcc00] bg-clip-text text-transparent">GẠCH THẺ MEOW</h1>
        <div class="w-10 h-0.5 bg-[#ffcc00]/50 mx-auto mb-6"></div>
        <p class="text-white/60 leading-relaxed font-light text-sm">API Server đang hoạt động</p>
        <div class="mt-8 text-left bg-black/30 p-4 rounded-lg border border-white/10">
          <p class="text-[#00ff88] text-xs font-mono font-bold mb-2">📡 ENDPOINTS:</p>
          <p class="text-white/40 text-xs font-mono mb-1">POST /callback - Nhận callback từ gachthefasl</p>
          <p class="text-white/40 text-xs font-mono mb-1">GET /api/notifications - Bot hỏi thông báo</p>
          <p class="text-white/40 text-xs font-mono">POST /api/delete-notification - Xóa thông báo</p>
        </div>
      </div>
    </body>
    </html>
  `);
});

app.listen(PORT, () => {
  console.log(`[WEB] API Server chạy tại http://localhost:${PORT}`);
  console.log(`[WEB] POST /callback - Nhận callback từ gachthefasl`);
  console.log(`[WEB] GET /api/notifications - Bot poll thông báo`);
  console.log(`[WEB] POST /api/delete-notification - Bot xóa thông báo`);
});

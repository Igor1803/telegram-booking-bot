#!/usr/bin/env python3
"""
Веб-интерфейс для мониторинга Telegram бота на Replit.
Опциональный файл для отслеживания статуса бота через веб-интерфейс.
"""

import threading
import time
import os
from datetime import datetime
from flask import Flask, render_template_string, jsonify

app = Flask(__name__)

# HTML шаблон для веб-интерфейса
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Telegram Bot Monitor</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .status { padding: 15px; border-radius: 5px; margin: 20px 0; }
        .status.running { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .status.error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0; }
        .info-card { background: #f8f9fa; padding: 15px; border-radius: 5px; }
        .refresh-btn { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        .refresh-btn:hover { background: #0056b3; }
        .logs { background: #f8f9fa; padding: 15px; border-radius: 5px; max-height: 300px; overflow-y: auto; font-family: monospace; font-size: 12px; }
    </style>
    <script>
        function refreshStatus() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('status').innerHTML = 
                        `<div class="status ${data.status === 'running' ? 'running' : 'error'}">
                            🤖 Статус бота: ${data.status === 'running' ? '✅ Работает' : '❌ Остановлен'}
                        </div>`;
                    document.getElementById('uptime').textContent = data.uptime;
                    document.getElementById('last-check').textContent = data.timestamp;
                })
                .catch(error => {
                    document.getElementById('status').innerHTML = 
                        '<div class="status error">❌ Ошибка получения статуса</div>';
                });
        }
        
        setInterval(refreshStatus, 30000); // Обновление каждые 30 секунд
    </script>
</head>
<body>
    <div class="container">
        <h1>🤖 Telegram Bot Monitor</h1>
        <p>Мониторинг бота для бронирования билетов</p>
        
        <div id="status">
            <div class="status running">
                🤖 Статус бота: ✅ Работает
            </div>
        </div>
        
        <div class="info-grid">
            <div class="info-card">
                <h3>📊 Информация</h3>
                <p><strong>Время работы:</strong> <span id="uptime">{{ uptime }}</span></p>
                <p><strong>Последняя проверка:</strong> <span id="last-check">{{ timestamp }}</span></p>
                <p><strong>База данных:</strong> {{ db_status }}</p>
            </div>
            
            <div class="info-card">
                <h3>⚙️ Конфигурация</h3>
                <p><strong>Токен бота:</strong> {{ bot_token_status }}</p>
                <p><strong>Администраторы:</strong> {{ admin_count }}</p>
                <p><strong>Среда:</strong> Replit</p>
            </div>
        </div>
        
        <button class="refresh-btn" onclick="refreshStatus()">🔄 Обновить статус</button>
        
        <h3>📝 Последние логи</h3>
        <div class="logs">
            {{ logs }}
        </div>
        
        <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; color: #666; font-size: 12px;">
            <p>💡 <strong>Совет:</strong> Для непрерывной работы бота включите "Always On" в настройках Replit</p>
            <p>🔗 <strong>Управление:</strong> Отправьте /start боту в Telegram для проверки работы</p>
        </div>
    </div>
</body>
</html>
"""

class BotMonitor:
    def __init__(self):
        self.start_time = time.time()
        self.bot_status = "running"
    
    def get_uptime(self):
        uptime_seconds = int(time.time() - self.start_time)
        hours = uptime_seconds // 3600
        minutes = (uptime_seconds % 3600) // 60
        return f"{hours}ч {minutes}м"
    
    def get_logs(self):
        try:
            if os.path.exists('bot.log'):
                with open('bot.log', 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    return ''.join(lines[-20:])  # Последние 20 строк
            return "Логи не найдены"
        except Exception:
            return "Ошибка чтения логов"
    
    def get_db_status(self):
        return "✅ Подключена" if os.path.exists('bot_database.db') else "❌ Не найдена"
    
    def get_bot_token_status(self):
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        if token and ':' in token:
            return f"✅ Настроен ({token[:10]}...)"
        return "❌ Не настроен"
    
    def get_admin_count(self):
        admin_ids = os.getenv('ADMIN_IDS', '')
        if admin_ids:
            count = len([x for x in admin_ids.split(',') if x.strip()])
            return f"✅ {count} администратор(ов)"
        return "⚠️ Не настроены"

monitor = BotMonitor()

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE,
        uptime=monitor.get_uptime(),
        timestamp=datetime.now().strftime('%H:%M:%S'),
        db_status=monitor.get_db_status(),
        bot_token_status=monitor.get_bot_token_status(),
        admin_count=monitor.get_admin_count(),
        logs=monitor.get_logs()
    )

@app.route('/api/status')
def api_status():
    return jsonify({
        'status': monitor.bot_status,
        'uptime': monitor.get_uptime(),
        'timestamp': datetime.now().strftime('%H:%M:%S'),
        'db_exists': os.path.exists('bot_database.db'),
        'token_configured': bool(os.getenv('TELEGRAM_BOT_TOKEN'))
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'ok',
        'timestamp': time.time(),
        'uptime': monitor.get_uptime()
    })

def run_web_server():
    """Запуск веб-сервера в отдельном потоке."""
    app.run(host='0.0.0.0', port=8080, debug=False)

def start_bot_with_monitor():
    """Запуск бота с веб-мониторингом."""
    # Запуск веб-сервера в отдельном потоке
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()
    
    print("🌐 Веб-мониторинг запущен на порту 8080")
    print("🤖 Запуск Telegram бота...")
    
    # Запуск основного бота
    try:
        from main import main
        main()
    except Exception as e:
        monitor.bot_status = "error"
        print(f"❌ Ошибка запуска бота: {e}")
        raise

if __name__ == "__main__":
    start_bot_with_monitor()
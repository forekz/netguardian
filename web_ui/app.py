from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
from flask_login import LoginManager, UserMixin, login_required
import yaml
import redis
from elasticsearch import Elasticsearch
import jwt
from datetime import datetime, timedelta
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app)
login_manager = LoginManager()
login_manager.init_app(app)

# Загрузка конфигурации
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Подключение к Redis для кэширования
redis_client = redis.Redis(
    host=config['redis']['host'],
    port=config['redis']['port'],
    db=config['redis']['db']
)

# Подключение к Elasticsearch для логов
es_client = Elasticsearch(config['elasticsearch']['hosts'])

class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/')
@login_required
def index():
    """Главная страница"""
    return render_template('index.html')

@app.route('/api/agents')
@login_required
def get_agents():
    """Получение списка агентов"""
    agents = redis_client.hgetall('agents')
    return jsonify([
        {
            'id': agent_id.decode(),
            'data': json.loads(agent_data.decode())
        }
        for agent_id, agent_data in agents.items()
    ])

@app.route('/api/metrics')
@login_required
def get_metrics():
    """Получение метрик"""
    timeframe = request.args.get('timeframe', '1h')
    
    # Формируем временной диапазон
    now = datetime.now()
    if timeframe == '1h':
        start_time = now - timedelta(hours=1)
    elif timeframe == '24h':
        start_time = now - timedelta(days=1)
    elif timeframe == '7d':
        start_time = now - timedelta(days=7)
    else:
        start_time = now - timedelta(hours=1)
    
    # Запрос к Elasticsearch
    query = {
        "query": {
            "range": {
                "timestamp": {
                    "gte": start_time.isoformat(),
                    "lte": now.isoformat()
                }
            }
        },
        "aggs": {
            "cpu_usage": {
                "avg": {"field": "cpu_percent"}
            },
            "memory_usage": {
                "avg": {"field": "memory_percent"}
            },
            "network_traffic": {
                "sum": {"field": "network.bytes_sent"}
            }
        }
    }
    
    result = es_client.search(
        index=f"{config['elasticsearch']['index_prefix']}-metrics-*",
        body=query
    )
    
    return jsonify(result['aggregations'])

@app.route('/api/alerts')
@login_required
def get_alerts():
    """Получение списка оповещений"""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    severity = request.args.get('min_severity')
    
    query = {
        "sort": [{"timestamp": {"order": "desc"}}],
        "from": (page - 1) * per_page,
        "size": per_page,
        "query": {
            "bool": {
                "must": [
                    {"range": {"severity": {"gte": severity}}} if severity else {"match_all": {}}
                ]
            }
        }
    }
    
    result = es_client.search(
        index=f"{config['elasticsearch']['index_prefix']}-alerts-*",
        body=query
    )
    
    return jsonify({
        'total': result['hits']['total']['value'],
        'alerts': [hit['_source'] for hit in result['hits']['hits']]
    })

@socketio.on('connect')
@login_required
def handle_connect():
    """Обработка подключения WebSocket"""
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    """Обработка отключения WebSocket"""
    print('Client disconnected')

def send_realtime_update(data):
    """Отправка обновлений через WebSocket"""
    socketio.emit('update', data)

if __name__ == '__main__':
    socketio.run(
        app,
        host=config['web_ui']['host'],
        port=config['web_ui']['port'],
        debug=True
    ) 
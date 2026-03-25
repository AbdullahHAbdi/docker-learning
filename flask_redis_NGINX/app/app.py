from flask import Flask, render_template, jsonify
import redis
import os
import time
from datetime import datetime

app = Flask(__name__)

redis_host = os.getenv("REDIS_HOST", "redis")
redis_port = int(os.getenv("REDIS_PORT", 6379))

r = redis.Redis(host=redis_host, port=redis_port)

@app.route('/')
def home():
    return render_template('index.html', year=datetime.now().year)

@app.route('/count')
def count():
    visits = r.incr('visits')
    hour_key = f"visits:hour:{int(time.time() // 3600)}"
    r.incr(hour_key)
    r.expire(hour_key, 86400)
    r.set('last_visit', time.time())
    return jsonify({'visits': int(visits)})

@app.route('/analytics')
def analytics():
    total = int(r.get('visits') or 0)
    now = int(time.time() // 3600)
    chart_labels = []
    chart_data = []
    for i in range(11, -1, -1):
        hour = now - i
        label = f"{int(time.strftime('%H', time.localtime(hour * 3600)))}:00"
        count = int(r.get(f"visits:hour:{hour}") or 0)
        chart_labels.append(label)
        chart_data.append(count)
    return jsonify({
        'total': total,
        'chart_labels': chart_labels,
        'chart_data': chart_data
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
# backend/app.py
from flask import Flask, request, jsonify
from celery import Celery
import os

app = Flask(__name__)
celery = Celery('tasks', broker=os.getenv('REDIS_URL'), backend=os.getenv('REDIS_URL'))

@app.route('/api/check', methods=['POST'])
def check_url():
    url = request.json.get('url')
    task = celery.send_task('tasks.check_availability', args=[url])
    return jsonify({"task_id": task.id}), 202

@app.route('/api/status/<task_id>', methods=['GET'])
def get_status(task_id):
    res = celery.AsyncResult(task_id)
    return jsonify({"status": res.status, "result": res.result})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

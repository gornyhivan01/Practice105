import string
import random
import time
from flask import Flask, request, jsonify
from celery import Celery

app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'redis://redis:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://redis:6379/0'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

@celery.task(bind=True)
def generate_password_task(self, length=12, use_digits=True, use_special=True):
    chars = string.ascii_letters
    if use_digits:
        chars += string.digits
    if use_special:
        chars += string.punctuation
    password = ''.join(random.choice(chars) for _ in range(length))
    return password

@app.route('/api/generate', methods=['POST'])
def generate():
    data = request.get_json() or {}
    length = int(data.get('length', 12))
    use_digits = data.get('use_digits', True)
    use_special = data.get('use_special', True)
    task = generate_password_task.delay(length, use_digits, use_special)
    return jsonify({'task_id': task.id}), 202

@app.route('/api/status/<task_id>')
def task_status(task_id):
    task = generate_password_task.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {'state': task.state, 'status': 'Задача ожидает выполнения...'}
    elif task.state == 'SUCCESS':
        response = {'state': task.state, 'result': task.result}
    else:
        response = {'state': task.state, 'status': str(task.info)}
    return jsonify(response)
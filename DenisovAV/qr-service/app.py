import io
import time
import base64
import qrcode
from flask import Flask, request, jsonify
from celery import Celery

app = Flask(__name__)

app.config.update(
    CELERY_BROKER_URL='redis://redis:6379/0',
    CELERY_RESULT_BACKEND='redis://redis:6379/0'
)

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'], backend=app.config['CELERY_RESULT_BACKEND'])

@celery.task
def create_qr_task(text: str):
    """Generates a QR code image asynchronously, returning base64 string."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    time.sleep(5)  # Simulate long processing time
    
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    # Return as base64 so it can be serialized by Celery easily
    return base64.b64encode(img_buffer.getvalue()).decode('utf-8')

@app.route('/generate', methods=['POST'])
def generate_qr_async():
    data = request.json
    text = data.get('text')
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
        
    try:
        task = create_qr_task.delay(text)
        return jsonify({"task_id": task.id}), 202
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/status/<task_id>', methods=['GET'])
def get_status(task_id):
    task = create_qr_task.AsyncResult(task_id)
    if task.state == 'PENDING':
        return jsonify({"status": "PENDING"}), 200
    elif task.state != 'FAILURE':
        return jsonify({
            "status": "SUCCESS",
            "image_base64": task.info
        }), 200
    else:
        return jsonify({
            "status": "FAILURE",
            "error": str(task.info)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)

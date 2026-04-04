import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

QR_SERVICE_GENERATE_URL = 'http://qr-service:5001/generate'
QR_SERVICE_STATUS_URL = 'http://qr-service:5001/status/'

@app.route('/api/generate', methods=['POST'])
def generate_qr():
    data = request.json
    text = data.get('text') if data else None
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
        
    try:
        # Forward the request to the qr-service
        response = requests.post(QR_SERVICE_GENERATE_URL, json={"text": text})
        
        if response.status_code != 202:
            error_data = response.json()
            return jsonify({"error": error_data.get("error", "QR task failed")}), response.status_code
            
        task_data = response.json()
        return jsonify(task_data), 202
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/status/<task_id>', methods=['GET'])
def check_status(task_id):
    try:
        response = requests.get(f"{QR_SERVICE_STATUS_URL}{task_id}")
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

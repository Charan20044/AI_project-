import requests
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

GEMINI_API_KEY = "AIzaSyD9EN07C_f10-mWn9EE8FuvgEIP6F7yXY8"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

def get_health_report(patient_data):
    """Send patient data to Gemini API and get a health check report."""
    prompt_text = f"""
    Analyze the following patient vitals and provide a detailed health check report:

    - Body Temperature: {patient_data['body_temperature_celcius']}°C
    - Blood Pressure: {patient_data['blood_pressure_systolic_mm_hg']}/{patient_data['blood_pressure_diastolic_mm_hg']} mmHg
    - Heart Rate: {patient_data['resting_heart_rate_bpm']} BPM
    - Respiratory Rate: {patient_data['respiratory_rate_bpm']} BPM
    - Blood Glucose: {patient_data['blood_glucose_mg_dL']} mg/dL
    - Blood Saturation: {patient_data['blood_saturation']}%

    Provide:
    1. A short health summary
    2. Potential health risks
    3. Recommended actions
    """

    payload = {
        "contents": [{
            "parts": [{"text": prompt_text}]
        }]
    }

    headers = {"Content-Type": "application/json"}
    response = requests.post(GEMINI_API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        response_data = response.json()
        return response_data["candidates"][0]["content"]["parts"][0]["text"]
    else:
        return f"Error: {response.status_code}, {response.text}"

@app.route('/health-check', methods=['POST'])
def health_check():
    """Receive patient data and send it to Gemini API for analysis."""
    patient_data = request.json
    health_report = get_health_report(patient_data)
    return jsonify({"health_report": health_report})

if __name__ == '__main__':
    app.run(debug=True)

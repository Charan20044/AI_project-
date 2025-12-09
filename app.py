from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import json
import os
from patient import Patient , DISEASES

app = Flask(__name__)
app.secret_key = 'your_secret_key'


# User database (For simplicity, storing in a JSON file)
# User database (For simplicity, storing in a JSON file)
USER_FILE = "users.json"

# Load users
def load_users():
    if not os.path.exists(USER_FILE):
        return {}
    with open(USER_FILE, "r") as file:
        return json.load(file)

# Save users
def save_users(users):
    with open(USER_FILE, "w") as file:
        json.dump(users, file, indent=4)

@app.route('/')
def home():
    return redirect(url_for('register'))  


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_users()

        if username in users:
            flash('Username already exists!', 'error') 
            return redirect(url_for('register'))

        users[username] = {'password': password}
        save_users(users)
        flash('Registration successful! Please login.', 'success')  
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_users()

        if username in users and users[username]['password'] == password:
            session['username'] = username
            flash('Login successful!', 'success') 
            return redirect(url_for('dashboard'))
        else:
            flash('Incorrect username or password!', 'error')  
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash('You need to login first!', 'danger')
        return redirect(url_for('login'))

    try:
        patient_data = Patient.load_patient_data()
        patient = Patient(**patient_data)
    except Exception as e:
        flash('Error loading patient data. Initializing with default values.', 'danger')
        patient = Patient()  

    return render_template('dashboard.html', vitals=patient.__dict__, username=session['username'])

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

import requests

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
    - Sodium Rate: {patient_data['sodium_rate']} mEq/L
    - Potassium Rate: {patient_data['potassium_rate']} mEq/L

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

@app.route('/update_vital', methods=['POST'])
def update_vital():
    """Update patient vital values dynamically and get a Gemini AI health report."""
    data = request.json
    vital_name = data['vital']
    new_value = float(data['value'])

    patient_data = Patient.load_patient_data()

    # Ensure correct mapping for blood pressure and other values
    if vital_name == "bp_systolic":
        patient_data["blood_pressure_systolic_mm_hg"] = new_value
    elif vital_name == "bp_diastolic":
        patient_data["blood_pressure_diastolic_mm_hg"] = new_value
    elif vital_name == "blood_glucose":
        patient_data["blood_glucose_mg_dL"] = new_value
    elif vital_name == "body_temperature":
        patient_data["body_temperature_celcius"] = new_value
    elif vital_name == "respiratory_rate":
        patient_data["respiratory_rate_bpm"] = new_value
    elif vital_name == "heart_rate":
        patient_data["resting_heart_rate_bpm"] = new_value
    elif vital_name == "blood_saturation":
        patient_data["blood_saturation"] = new_value
    else:
        print(f"Warning: Unrecognized vital '{vital_name}'")
    
    # Save the updated patient data
    Patient.save_patient_data(patient_data)

    # Recreate a valid Patient object
    patient = Patient(**patient_data)

    # Recalculate disease prediction
    possible_disease = None
    for disease_fn in DISEASES:
        disease_name = disease_fn(patient)
        if disease_name:
            possible_disease = disease_name
            break  # Stop after first match

    # 🔥 Get a detailed health check report from Gemini AI
    health_report = get_health_report(patient_data)

    return jsonify({
        "status": "success",
        "updated_data": patient_data,
        "disease": possible_disease,
        "health_report": health_report
    })


# ✅ Corrected `if __name__` statement
if __name__ == '__main__':
    app.run(debug=True)

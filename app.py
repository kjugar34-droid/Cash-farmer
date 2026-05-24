import os
import subprocess
import sys

# --- ફ્લાસ્ક ઇન્સ્ટોલર (જે Pydroid માં સરળતાથી થઈ જાય છે) ---
try:
    from flask import Flask, render_template, request, jsonify
except ImportError:
    print("[+] Flask Pydroid 3 માં મળ્યું નથી. ઇન્સ્ટોલ થઈ રહ્યું છે...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "flask"])
    from flask import Flask, render_template, request, jsonify

try:
    import requests
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

import uuid

app = Flask(__name__)

# --- Appwrite ના સ્ક્રીનશોટ મુજબનું કન્ફિગરેશન ---
APPWRITE_ENDPOINT = 'https://cloud.appwrite.io/v1'
PROJECT_ID = 'YOUR_APPWRITE_PROJECT_ID'  # પાયડ્રોઈડમાં રન કરવા અહીં તમારી પ્રોજેક્ટ ID નાખો
API_KEY = 'YOUR_APPWRITE_API_KEY'        # તમારી સિક્રેટ API કી અહીં નાખો

# તમારા ફોટામાં દેખાતી પરફેક્ટ આઈડી
DATABASE_ID = "6a0c59ac002413005872"
COLLECTION_ID = "user_information"

@app.route('/')
def index():
    # તમારા ઓરિજિનલ HTML ને કોઈ પણ ફેરફાર વગર રન કરશે
    return render_template('index.html')

@app.route('/api/signup', methods=['POST'])
def handle_signup():
    """
    ડાયરેક્ટ Appwrite REST API નો ઉપયોગ કરીને ડેટાબેઝમાં મોકલશે, 
    જેથી Pydroid 3 માં મોટી લાઇબ્રેરી વગર એરર ફિક્સ થઈ જાય.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "ફ્રન્ટએન્ડ તરફથી કોઈ ડેટા મળ્યો નથી."}), 400

        # ફોર્મ ડેટા
        nickname = data.get('nickname')
        email = data.get('email')
        password = data.get('password')
        refer_code = data.get('refer_code', '')

        # Appwrite સર્વર માટેના કસ્ટમ હેડર્સ
        headers = {
            'X-Appwrite-Project': PROJECT_ID,
            'X-Appwrite-Key': API_KEY,
            'Content-Type': 'application/json'
        }

        # નવો યુનિક ડોક્યુમેન્ટ આઈડી જનરેટ કરવા માટે
        document_id = str(uuid.uuid4().hex)[:20]

        # Appwrite ની ઓફિશિયલ API બોડી
        payload = {
            "documentId": document_id,
            "data": {
                "nickname": nickname,
                "email": email,
                "password": password,
                "refer_code": refer_code
            }
        }

        # Appwrite ના કલેક્શનના પાથ પર ડાયરેક્ટ ડેટા પુશ
        url = f"{APPWRITE_ENDPOINT}/databases/{DATABASE_ID}/collections/{COLLECTION_ID}/documents"
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code in [200, 201]:
            return jsonify({
                "status": "success", 
                "message": "યુઝર ડેટા સક્સેસફુલી Appwrite ડેટાબેઝમાં સેવ થઈ ગયો છે!", 
                "data": response.json()
            })
        else:
            # જો Appwrite સર્વર તરફથી કોઈ ભૂલ આવે (જેમ કે ખોટી પ્રોજેક્ટ આઈડી કે પરમિશન)
            return jsonify({
                "status": "error", 
                "message": f"Appwrite રિજેક્શન એરર: {response.text}"
            }), response.status_code

    except Exception as e:
        # કોઈ પણ અણધારી લોકલ સિસ્ટમ કે કનેક્શન એરર સ્ક્રીન પર ટ્રાન્સફર થશે
        return jsonify({
            "status": "error", 
            "message": f"સર્વર કનેક્શન એરર: {str(e)}"
        }), 500

if __name__ == '__main__':
    # Pydroid 3 લોકલ ડેવલપમેન્ટ સર્વર
    app.run(debug=True, host='0.0.0.0', port=5000)

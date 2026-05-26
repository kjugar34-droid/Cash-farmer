Import random
import smtplib
import threading  # ૧૦ મિનિટના ટાઈમર માટે ઉમેરેલ
import time  # ટાઈમ આઉટ માટે ઉમેરેલ
from email.mime.text import MIMEText
from flask import Flask, jsonify, request
from flask_cors import CORS
# Appwrite SDK ઇમ્પોર્ટ
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.query import Query

app = Flask(__name__)
# HTML ફાઇળ અને સર્વર વચ્ચે કનેક્શન પ્રોબ્લેમ (CORS) ન થાય તે માટે
CORS(app)

# --- Appwrite ડેટાબેઝ કન્ફિગરેશન ---
APPWRITE_ENDPOINT = "https://fra.cloud.appwrite.io/v1"
APPWRITE_PROJECT_ID = "6985aa6e0018fb6d3ef8"
APPWRITE_DATABASE_ID = "6a0c59ac002413005872"
APPWRITE_COLLECTION_ID = "user_information"

# Appwrite ક્લાયન્ટ સેટઅપ
client = Client()
client.set_endpoint(APPWRITE_ENDPOINT)
client.set_project(APPWRITE_PROJECT_ID)
databases = Databases(client)

# હંગામી ધોરણે OTP સેવ કરવા માટેનું ડિક્શનરી
otp_store = {}

# --- ઈમેલ મોકલવાનું કન્ફિગરેશન ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "jigarthakor12322@gmail.com"
# તમારો સાચો ૧૬ અંકનો એપ પાસવર્ડ
SENDER_PASSWORD = "noammnlfvrgqnlan"


def send_email(receiver_email, subject, body):
    """યુઝરને ઈમેલ મોકલવા માટેનું હેલ્પર ફંક્શન"""
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = SENDER_EMAIL
        msg["To"] = receiver_email

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        return True
    except Exception as e:
        print(f"Email sending error: {e}")
        return False


# HTML ફોર્મેટમાં મોટો અને સુંદર મોકલવા માટેનું નવું ફંક્શન
def send_html_email(receiver_email, subject, nickname, otp):
    try:
        html_content = f"""
        <html>
        <head>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
                body {{
                    font-family: 'Poppins', sans-serif;
                    background-color: #f2f2f7;
                    margin: 0;
                    padding: 20px;
                }}
                .email-wrapper {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: #f2f2f7;
                    padding: 20px;
                }}
                .email-container {{
                    background-color: #ffffff;
                    border-radius: 24px;
                    overflow: hidden;
                    padding: 0 0 40px 0;
                    box-shadow: 0 4px 10px rgba(0,0,0,0.03);
                }}
                .header-banner {{
                    background-color: #9d56cf;
                    padding: 35px 20px;
                    text-align: center;
                }}
                .header-title {{
                    font-family: 'Poppins', sans-serif;
                    font-size: 28px;
                    color: #ffffff;
                    margin: 0;
                    font-weight: 700;
                    letter-spacing: 0.5px;
                }}
                .content {{
                    padding: 40px 40px 0 40px;
                    color: #333333;
                    text-align: center;
                }}
                .salutation {{
                    font-family: 'Poppins', sans-serif;
                    font-size: 22px;
                    color: #9d56cf;
                    margin-bottom: 20px;
                    font-weight: 600;
                }}
                .message-text {{
                    font-family: 'Poppins', sans-serif;
                    font-size: 15px;
                    color: #555555;
                    line-height: 1.6;
                    margin-bottom: 30px;
                }}
                .otp-box {{
                    font-family: 'Poppins', sans-serif;
                    font-size: 36px;
                    font-weight: 700;
                    color: #333333;
                    letter-spacing: 6px;
                    padding: 20px 40px;
                    background-color: #f4ecf9;
                    border: 2px dashed #9d56cf;
                    border-radius: 12px;
                    display: inline-block;
                    margin-bottom: 30px;
                }}
                .warning-text {{
                    font-family: 'Poppins', sans-serif;
                    font-size: 13px;
                    color: #666666;
                    line-height: 1.6;
                    margin-top: 20px;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    font-family: 'Poppins', sans-serif;
                    font-size: 13px;
                    color: #888888;
                }}
            </style>
        </head>
        <body>
            <div class="email-wrapper">
                <div class="email-container">
                    <div class="header-banner">
                        <div class="header-title">Welcome to Cash Farmer!</div>
                    </div>
                    <div class="content">
                        <div class="salutation">Hi {nickname},</div>
                        <div class="message-text">
                            Thank you for registering with us. To complete your account setup,<br>
                            please use the One-Time Password (OTP) below:
                        </div>
                        <div class="otp-box">{otp}</div>
                        <div class="warning-text">
                            The OTP is valid for the next 10 minutes. Please do not share this OTP with anyone.<br><br>
                            If you did not request this, please contact our support team immediately.
                        </div>
                    </div>
                </div>
                <div class="footer">
                    © 2026 Cash Farmer. All rights reserved.
                </div>
            </div>
        </body>
        </html>
        """
        msg = MIMEText(html_content, "html")
        msg["Subject"] = subject
        msg["From"] = f"Cash Farmer <{SENDER_EMAIL}>"
        msg["To"] = receiver_email

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        return True
    except Exception as e:
        print(f"HTML Email sending error: {e}")
        return False


# ફોરગોટ પાસવર્ડ માટે સુંદર મોટો ઇમેઇલ બોક્સ મોકલવાનું નવું ફંક્શન
def send_forgot_password_html_email(receiver_email, subject, nickname, password):
    try:
        html_content = f"""
        <html>
        <head>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
                body {{
                    font-family: 'Poppins', sans-serif;
                    background-color: #f2f2f7;
                    margin: 0;
                    padding: 20px;
                }}
                .email-wrapper {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: #f2f2f7;
                    padding: 20px;
                }}
                .email-container {{
                    background-color: #ffffff;
                    border-radius: 24px;
                    overflow: hidden;
                    padding: 0 0 40px 0;
                    box-shadow: 0 4px 10px rgba(0,0,0,0.03);
                }}
                .header-banner {{
                    background-color: #9d56cf;
                    padding: 35px 20px;
                    text-align: center;
                }}
                .header-title {{
                    font-family: 'Poppins', sans-serif;
                    font-size: 28px;
                    color: #ffffff;
                    margin: 0;
                    font-weight: 700;
                    letter-spacing: 0.5px;
                }}
                .content {{
                    padding: 40px 40px 0 40px;
                    color: #333333;
                    text-align: center;
                }}
                .salutation {{
                    font-family: 'Poppins', sans-serif;
                    font-size: 22px;
                    color: #9d56cf;
                    margin-bottom: 20px;
                    font-weight: 600;
                    text-align: left;
                }}
                .message-text {{
                    font-family: 'Poppins', sans-serif;
                    font-size: 15px;
                    color: #555555;
                    line-height: 1.6;
                    margin-bottom: 30px;
                    text-align: left;
                }}
                .password-box {{
                    font-family: 'Poppins', sans-serif;
                    font-size: 26px;
                    font-weight: 700;
                    color: #333333;
                    padding: 20px 40px;
                    background-color: #f4ecf9;
                    border: 2px dashed #9d56cf;
                    border-radius: 12px;
                    display: inline-block;
                    margin-bottom: 30px;
                    text-align: center;
                }}
                .warning-text {{
                    font-family: 'Poppins', sans-serif;
                    font-size: 13px;
                    color: #666666;
                    line-height: 1.6;
                    margin-top: 20px;
                    text-align: left;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    font-family: 'Poppins', sans-serif;
                    font-size: 13px;
                    color: #888888;
                }}
            </style>
        </head>
        <body>
            <div class="email-wrapper">
                <div class="email-container">
                    <div class="header-banner">
                        <div class="header-title">Forgot Your Password?</div>
                    </div>
                    <div class="content">
                        <div class="salutation">Hello {nickname},</div>
                        <div class="message-text">
                            You requested to retrieve your password. Here is your current password:
                        </div>
                        <div class="password-box">{password}</div>
                        <div class="warning-text">
                            If you did not request this, please change your password immediately for security reasons.<br><br>
                            If you have any questions, feel free to contact our support team.
                        </div>
                    </div>
                </div>
                <div class="footer">
                    © 2026 Cash Farmer. All rights reserved.
                </div>
            </div>
        </body>
        </html>
        """
        msg = MIMEText(html_content, "html")
        msg["Subject"] = subject
        msg["From"] = f"Cash Farmer <{SENDER_EMAIL}>"
        msg["To"] = receiver_email

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        return True
    except Exception as e:
        print(f"[ERROR] Forgot Password Email sending error: {e}")
        return False


# ૧૦ મિનિટ પછી જો યુઝર વેરિફાય ન થયો હોય તો રો (Row) ડીલીટ કરવાનું બેકગ્રાઉન્ડ ફંક્શન
def delete_row_after_10_minutes(document_id):
    time.sleep(600)  # ૬૦૦ સેકન્ડ એટલે કે ૧૦ મિનિટ રાહ જોશે
    try:
        user_doc = databases.get_document(
            database_id=APPWRITE_DATABASE_ID,
            collection_id=APPWRITE_COLLECTION_ID,
            document_id=str(document_id)
        )
        
        # --- Appwrite ઓબ્જેક્ટ અથવા ડિક્શનરીમાંથી સુરક્ષિત રીતે ડેટા મેળવવો (સુધારેલ) ---
        if isinstance(user_doc, dict):
            is_verified = user_doc.get("is_verified", False)
        else:
            is_verified = getattr(user_doc, 'is_verified', None)
            if is_verified is None and hasattr(user_doc, 'data'):
                is_verified = user_doc.data.get("is_verified", False)
        
        # જો હજી પણ વેરિફાય ન થયું હોય (False હોય) તો આખી રો ડીલીટ કરવાનું લોજિક અહીંથી કાઢી નાખ્યું છે.
        if not is_verified:
            print(f"[Appwrite] Row {document_id} was not verified, but delete logic is skipped.")
    except Exception as e:
        print(f"[Cleanup Error] Error occurred: {e}")


# =========================================================================
# ૧. OTP મોકલવાનો રૂટ (/send_otp)
# =========================================================================
@app.route("/send_otp", methods=["POST"])
def send_otp():
    data = request.json
    nickname = data.get("nickname")
    gmail_id = data.get("gmail_id")
    password = data.get("password")

    if not gmail_id:
        return jsonify({"status": "error", "message": "Email is required"}), 400

    otp = str(random.randint(10000, 99999))
    otp_store[gmail_id] = otp

    try:
        response = databases.list_documents(
            database_id=APPWRITE_DATABASE_ID,
            collection_id=APPWRITE_COLLECTION_ID,
            queries=[Query.equal("user_gmail_account", gmail_id)]
        )
        
        # એરર ફ્રી ઓબ્જેક્ટ હેન્ડલિંગ
        documents = response.get('documents') if isinstance(response, dict) else getattr(response, 'documents', [])
        if documents and len(documents) > 0:
            user_doc = documents[0]
            document_id = user_doc.get('$id') if isinstance(user_doc, dict) else getattr(user_doc, 'id', getattr(user_doc, '$id', None))
            
            try:
                databases.update_document(
                    database_id=APPWRITE_DATABASE_ID, collection_id=APPWRITE_COLLECTION_ID,
                    document_id=str(document_id), data={"user_gmail_otp": int(otp), "is_verified": False}
                )
            except Exception:
                databases.update_document(
                    database_id=APPWRITE_DATABASE_ID, collection_id=APPWRITE_COLLECTION_ID,
                    document_id=str(document_id), data={"user_gmail_otp": str(otp), "is_verified": False}
                )
            print(f"[Appwrite] Updated user_gmail_otp for existing user {gmail_id}.")
            
            # જૂના અનવેરિફાઇડ યુઝર માટે ફરીથી ૧૦ મિનિટનું નવું ટાઈમર ચાલુ કરવું
            threading.Thread(target=delete_row_after_10_minutes, args=(document_id,)).start()
        else:
            try:
                new_doc = databases.create_document(
                    database_id=APPWRITE_DATABASE_ID, collection_id=APPWRITE_COLLECTION_ID,
                    document_id="unique()", data={"user_gmail_account": gmail_id, "user_nickname": nickname if nickname else "User", "user_gmail_otp": int(otp), "user_password": password if password else "", "is_verified": False}
                )
            except Exception:
                new_doc = databases.create_document(
                    database_id=APPWRITE_DATABASE_ID, collection_id=APPWRITE_COLLECTION_ID,
                    document_id="unique()", data={"user_gmail_account": gmail_id, "user_nickname": nickname if nickname else "User", "user_gmail_otp": str(otp), "user_password": password if password else "", "is_verified": False}
                )
            print(f"[Appwrite] Created new user with user_gmail_otp.")
            
            # નવો યુઝર બને એટલે તરત ૧૦ મિનિટનું બેકગ્રાઉન્ડ ટાઈમર રન કરવું
            new_doc_id = new_doc.get('$id') if isinstance(new_doc, dict) else getattr(new_doc, 'id', getattr(new_doc, '$id', None))
            threading.Thread(target=delete_row_after_10_minutes, args=(new_doc_id,)).start()
            
    except Exception as appwrite_err:
        print(f"[Appwrite Error]: {appwrite_err}")

    subject = "Welcome to Cash Farmer."
    display_name = nickname if nickname else "User"

    if send_html_email(gmail_id, subject, display_name, otp):
        return jsonify({"status": "success", "message": "OTP sent successfully"})
    else:
        return jsonify({"status": "error", "message": "Failed to send email"}), 500


# =========================================================================
# ૨. OTP વેરિફાય કરવાનો રૂટ (/verify_otp)
# =========================================================================
@app.route("/verify_otp", methods=["POST"])
def verify_otp():
    data = request.json
    gmail_id = data.get("gmail_id")
    entered_otp = data.get("otp")

    # ટર્મિનલમાં રિક્વેસ્ટ આવી તે દર્શાવવા માટે
    print(f"\n[REQUEST] /verify_otp root par request aavi che. Gmail: {gmail_id}, Entered OTP: {entered_otp}")

    if not gmail_id or not entered_otp:
        return jsonify({"status": "error", "message": "Missing email or OTP"}), 400

    try:
        db_response = databases.list_documents(
            database_id=APPWRITE_DATABASE_ID,
            collection_id=APPWRITE_COLLECTION_ID,
            queries=[Query.equal("user_gmail_account", gmail_id)]
        )
        
        documents = db_response.get('documents') if isinstance(db_response, dict) else getattr(db_response, 'documents', [])
        
        if documents and len(documents) > 0:
            user_doc = documents[0]
            
            # --- Appwrite ઓબ્જેક્ટ અથવા ડિક્શનરીમાંથી સુરક્ષિત રીતે સાચો ડેટા મેળવવો (સુધારેલ) ---
            if isinstance(user_doc, dict):
                appwrite_otp = user_doc.get("user_gmail_otp")
                nickname = user_doc.get("user_nickname", "User")
                password = user_doc.get("user_password", "")
                doc_id = user_doc.get('$id')
            else:
                appwrite_otp = getattr(user_doc, 'user_gmail_otp', None)
                nickname = getattr(user_doc, 'user_nickname', "User")
                password = getattr(user_doc, 'user_password', "")
                doc_id = getattr(user_doc, 'id', getattr(user_doc, '$id', None))
                
                if appwrite_otp is None and hasattr(user_doc, 'data'):
                    appwrite_otp = user_doc.data.get("user_gmail_otp")
                    nickname = user_doc.data.get("user_nickname", "User")
                    password = user_doc.data.get("user_password", "")
                    if doc_id is None:
                        doc_id = user_doc.data.get('$id') if '$id' in user_doc.data else user_doc.data.get('id')
            
            print(f"[DATABASE INFO] Database OTP: {appwrite_otp}, Document ID: {doc_id}")

            # OTP ચેક કરો
            if appwrite_otp and str(entered_otp) == str(appwrite_otp):
                
                print(f"[SUCCESS] OTP Match thayo! Document update thay che: id={doc_id} -> is_verified=True")
                
                # OTP મેચ થયો, હવે OTP ને 0 કરી દો અને is_verified ને True સેટ કરી દો (આ કાયમ સેવ રહેશે)
                databases.update_document(
                    database_id=APPWRITE_DATABASE_ID, collection_id=APPWRITE_COLLECTION_ID,
                    document_id=str(doc_id), data={"user_gmail_otp": 0, "is_verified": True}
                )

                print(f"[DATABASE UPDATED] Appwrite ma successfully row verify thai gai che.")

                # otp_store માંથી પણ કાઢી નાખો
                otp_store.pop(gmail_id, None)

                return jsonify({
                    "status": "success", 
                    "message": "OTP verified successfully.",
                    "user_data": {
                        "nickname": nickname,
                        "gmail_account": gmail_id,
                        "password": password
                    }
                })
            else:
                print(f"[WRONG OTP] OTP match nathi thayo. Entered: {entered_otp}, DB: {appwrite_otp}")
                # ખોટો OTP નાખે ત્યારે ડેટાબેઝમાંથી રો (row) ડીલીટ કરવાનું લોજિક અહીંથી કાઢી નાખ્યું છે.
                return jsonify({"status": "wrong_otp", "message": "Invalid OTP"}), 200
        else:
            print(f"[NOT FOUND] User database ma nathi malyo: {gmail_id}")
            return jsonify({"status": "error", "message": "User not found"}), 404
            
    except Exception as e:
        print(f"[Verify Error Exception]: {e}")
        return jsonify({"status": "error", "0message": "Internal server error"}), 500


# =========================================================================
# ૩. ફોરગોટ પાસવર્ડ ચેકિંગ રૂટ (/forgot_password)
# =========================================================================
@app.route("/forgot_password", methods=["POST"])
def forgot_password():
    data = request.json
    gmail_id = data.get("forgotEmailInput") if data.get("forgotEmailInput") else data.get("gmail_id")

    if not gmail_id:
        return jsonify({"status": "error", "message": "Email is required"}), 400

    try:
        db_response = databases.list_documents(
            database_id=APPWRITE_DATABASE_ID,
            collection_id=APPWRITE_COLLECTION_ID,
            queries=[Query.equal("user_gmail_account", gmail_id)]
        )

        documents = db_response.get('documents') if isinstance(db_response, dict) else getattr(db_response, 'documents', [])
        if documents and len(documents) > 0:
            user_doc = documents[0]
            
            if isinstance(user_doc, dict):
                db_password = user_doc.get("user_password")
                nickname = user_doc.get("user_nickname", "User")
                is_verified = user_doc.get("is_verified", False)  # ડેટા મેળવ્યો
            else:
                db_password = getattr(user_doc, 'user_password', None)
                nickname = getattr(user_doc, 'user_nickname', "User")
                is_verified = getattr(user_doc, 'is_verified', False)  # ડેટા મેળવ્યો
                if db_password is None and hasattr(user_doc, 'data'):
                    db_password = user_doc.data.get("user_password")
                    nickname = user_doc.data.get("user_nickname", "User")
                    is_verified = user_doc.data.get("is_verified", False)  # ડેટા મેળવ્યો

            # જો કોલમમાં value False હોય તો 'Email not found in database' (જીમેલ નથી) તેવો જ રિસ્પોન્સ આપવો
            if not is_verified:
                return jsonify({"status": "fail", "message": "Email not found in database"}), 200

            if db_password:
                subject = "Welcome to Cash Farmer."
                if send_forgot_password_html_email(gmail_id, subject, nickname, db_password):
                    return jsonify({"status": "success", "message": "Password sent successfully"})
                else:
                    return jsonify({"status": "error", "message": "Failed to send email"}), 500
            else:
                return jsonify({"status": "fail", "message": "Password column is empty"}), 200
        else:
            return jsonify({"status": "fail", "message": "Email not found in database"}), 200

    except Exception as forgot_err:
        return jsonify({"status": "error", "message": "Internal server error"}), 500


# =========================================================================
# ૪. નવો OTP ફરીથી મોકલવાનો રૂટ (/resend_otp)
# =========================================================================
@app.route("/resend_otp", methods=["POST"])
def resend_otp():
    data = request.json
    gmail_id = data.get("gmail_id")

    if not gmail_id:
        return jsonify({"status": "error", "message": "Email is required"}), 400

    new_otp = str(random.randint(10000, 99999))
    otp_store[gmail_id] = new_otp

    nickname = "User"
    try:
        response = databases.list_documents(
            database_id=APPWRITE_DATABASE_ID,
            collection_id=APPWRITE_COLLECTION_ID,
            queries=[Query.equal("user_gmail_account", gmail_id)]
        )
        
        # સુરક્ષિત રીતે ઓબ્જેક્ટ અથવા ડિક્શનરીમાંથી ડેટા મેળવવો
        documents = response.get('documents') if isinstance(response, dict) else getattr(response, 'documents', [])
        if documents and len(documents) > 0:
            user_doc = documents[0]
            
            if isinstance(user_doc, dict):
                nickname = user_doc.get("user_nickname", "User")
                document_id = user_doc.get('$id')
            else:
                nickname = getattr(user_doc, 'user_nickname', "User")
                document_id = getattr(user_doc, 'id', getattr(user_doc, '$id', None))
                if document_id is None and hasattr(user_doc, 'data'):
                    nickname = user_doc.data.get("user_nickname", "User")

            # સીધો જ નવો જનરેટ થયેલો કોડ 'int(new_otp)' તરીકે અપડેટ થશે, સહેજ પણ એરર વગર
            try:
                databases.update_document(
                    database_id=APPWRITE_DATABASE_ID, 
                    collection_id=APPWRITE_COLLECTION_ID,
                    document_id=str(document_id), 
                    data={"user_gmail_otp": int(new_otp), "is_verified": False}
                )
                print(f"[Appwrite] Resend: user_gmail_otp updated as Integer for {gmail_id}.")
            except Exception as e:
                databases.update_document(
                    database_id=APPWRITE_DATABASE_ID, 
                    collection_id=APPWRITE_COLLECTION_ID,
                    document_id=str(document_id), 
                    data={"user_gmail_otp": str(new_otp), "is_verified": False}
                )
                
            # રીસેન્ડ વખતે પણ વેરિફિકેશન પિરિયડનું ટાઈમર ફરી શરૂ થશે
            threading.Thread(target=delete_row_after_10_minutes, args=(document_id,)).start()
        else:
            return jsonify({"status": "error", "message": "User record not found"}), 404
            
    except Exception as appwrite_err:
        print(f"[Appwrite Resend Error]: {appwrite_err}")
        return jsonify({"status": "error", "message": "Database update failed"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True
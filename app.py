from flask import Flask, render_template, request, redirect, url_for, flash
import base64
import cv2
import numpy as np
import pymysql
import qrcode
import io
import random
import string
import datetime
import face_recognition
import pickle
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Add this line
# Admin credentials
admin_username = "admin"
admin_password = "admin123"

# Store QR keys temporarily (reset on server restart)
user_qr_keys = {}

# MySQL connection
def get_db_connection():
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='Sarbaj@199',
        database='e_authentication',
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection

# ✅ Face match function added here
def match_face_with_user(saved_face_img, input_face_img):
    # Encode saved face
    saved_face_locations = face_recognition.face_locations(saved_face_img)
    if not saved_face_locations:
        print("No face found in saved image.")
        return False
    saved_face_encoding = face_recognition.face_encodings(saved_face_img, saved_face_locations)[0]

    # Encode input face
    input_face_locations = face_recognition.face_locations(input_face_img)
    if not input_face_locations:
        print("No face found in input image.")
        return False
    input_face_encoding = face_recognition.face_encodings(input_face_img, input_face_locations)[0]

    # Compare
    results = face_recognition.compare_faces([saved_face_encoding], input_face_encoding)
    return results[0]

@app.route('/')
def home():
    return redirect("/register")

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == admin_username and password == admin_password:
            return redirect(url_for('admin_dashboard'))
        else:
            return "<h3>❌ Invalid admin credentials. Try again!</h3>"
    return render_template("admin_login.html")

@app.route('/admin_dashboard')
def admin_dashboard():
    connection = get_db_connection()
    cursor = connection.cursor()

    # Fetch registered users from MySQL
    cursor.execute("SELECT * FROM users")
    registered = cursor.fetchall()

    # Fetch authenticated users from MySQL
    cursor.execute("SELECT * FROM authenticated_users")
    authenticated = cursor.fetchall()

    # Fetch login logs from MySQL
    cursor.execute("SELECT * FROM login_logs")
    login_logs = cursor.fetchall()

    connection.close()

    return render_template("admin_dashboard.html", registered=registered, authenticated=authenticated, login_logs=login_logs)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        mobile = request.form['mobile']
        username = request.form['username']
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO users (name, email, mobile, username, registered_at, status) VALUES (%s, %s, %s, %s, %s, %s)",
                       (name, email, mobile, username, datetime.datetime.now(), 'Registered'))
        connection.commit()
        connection.close()
        return redirect(url_for('capture_ui', username=username))
    return render_template("register.html")

@app.route('/capture_face')
def capture_ui():
    username = request.args.get('username')
    return render_template("capture.html", username=username)

@app.route('/save_capture', methods=['POST'])
def save_capture():
    username = request.form['username']
    img_data = request.form['imageData'].split(',')[1]
    img_bytes = base64.b64decode(img_data)
    np_arr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    # ✅ Check if face is detected in the image
    face_locations = face_recognition.face_locations(img)
    if not face_locations:
        return f"<h3>❌ No face detected. Please try again.</h3><a href='/capture_face?username={username}'>Try Again</a>"

    # ✅ Encode and save only if face is detected
    encoded_face = base64.b64encode(cv2.imencode('.jpg', img)[1]).decode('utf-8')
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE users SET status = %s, face_image = %s WHERE username = %s", 
                   ('Face Captured', encoded_face, username))
    connection.commit()
    connection.close()

    # ✅ Redirect to login instead of just showing a message
    flash(f"✅ Face captured successfully for user: {username}. Please login to continue.", 'success')
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        return redirect(url_for('login_face_ui', username=username))
    return render_template("login.html")

@app.route('/login_face')
def login_face_ui():
    username = request.args.get('username')
    return render_template("login_face.html", username=username)

@app.route('/match_face', methods=['POST'])
def match_face():
    username = request.form['username']
    img_data = request.form['imageData'].split(',')[1]
    img_bytes = base64.b64decode(img_data)
    np_arr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    connection = get_db_connection()
    cursor = connection.cursor()

    # Fetch user details along with the face image
    cursor.execute("SELECT name, email, mobile, face_image FROM users WHERE username = %s", (username,))
    result = cursor.fetchone()

    if result and result['face_image']:
        # Decode the stored face image and compare
        saved_face = base64.b64decode(result['face_image'])
        saved_face_img = cv2.imdecode(np.frombuffer(saved_face, np.uint8), cv2.IMREAD_COLOR)

        # Match the face with the uploaded image
        is_match = match_face_with_user(saved_face_img, img)

        if is_match:
            # Update the user status to 'Authenticated'
            cursor.execute("UPDATE users SET status = %s WHERE username = %s", ('Authenticated', username))
            connection.commit()

            # Insert into authenticated_users table only if not already present
            cursor.execute("SELECT * FROM authenticated_users WHERE username = %s", (username,))
            already_authenticated = cursor.fetchone()

            if not already_authenticated:
                cursor.execute("SELECT name, email, mobile FROM users WHERE username = %s", (username,))
                user_data = cursor.fetchone()
                cursor.execute("INSERT INTO authenticated_users (username, name, email, mobile, authenticated_at) VALUES (%s, %s, %s, %s, %s)",
                               (username, user_data['name'], user_data['email'], user_data['mobile'], datetime.datetime.now()))
                connection.commit()

            # Insert login entry into login_logs table
            cursor.execute("INSERT INTO login_logs (username) VALUES (%s)", (username,))
            connection.commit()

            connection.close()

            # Proceed to QR authentication
            return redirect(url_for('qr_auth', username=username))
        else:
            connection.close()
            return f"<h3>❌ Face did not match for user {username}.</h3><a href='/login'>Try Again</a>"
    else:
        connection.close()
        return f"<h3>❌ User {username} not found or no face image stored.</h3>"

@app.route('/qr_auth')
def qr_auth():
    username = request.args.get('username')
    random_key = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    user_qr_keys[username] = random_key
    qr = qrcode.make(random_key)
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    qr_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return render_template("qr_auth.html", qr_code=qr_b64, username=username)

@app.route('/delete_user', methods=['POST'])
def delete_user():
    username = request.form['username']
    connection = get_db_connection()
    cursor = connection.cursor()
    
    # Delete the user from the 'users' table
    cursor.execute("DELETE FROM users WHERE username = %s", (username,))
    connection.commit()

    # Also delete from 'authenticated_users' table
    cursor.execute("DELETE FROM authenticated_users WHERE username = %s", (username,))
    connection.commit()

    # Delete user from login_logs (optional, depends on your need)
    cursor.execute("DELETE FROM login_logs WHERE username = %s", (username,))
    connection.commit()

    connection.close()
    
    # Flash a success message and redirect back to the admin dashboard
    flash(f"User {username} has been deleted successfully.", 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/verify_qr', methods=['POST'])
def verify_qr():
    username = request.form['username']
    scanned_data = request.form['scanned_data']
    expected_key = user_qr_keys.get(username)
    if scanned_data.strip() == expected_key:
        return render_template("dashboard.html", username=username)
    else:
        return f"<h3>❌ QR Code mismatch. Try again!</h3><a href='/login'>Back to Login</a>"

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)

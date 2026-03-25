import os
import numpy as np
import spacy
from flask import Flask, request, render_template, jsonify, redirect, url_for, send_from_directory, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.optimizers import Adamax
from PIL import Image
from werkzeug.utils import secure_filename

# Flask app setup
app = Flask(__name__)
app.secret_key = 'nailvision_secure_key_123'  # Required for session
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Ensure upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# MySQL database connection
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='NER'
    )

# Fetch nail condition details from DB


# Home page
@app.route('/')
def home():
    return render_template('index.html')

# Login/Signup pages
@app.route('/login-page')
def loginPage():
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/signup-page')
def signup_page():
    return render_template('signup.html')

# Signup API
@app.route('/signup', methods=['POST'])
def signup():
    if 'profileImage' not in request.files:
        return jsonify(success=False, message="Profile image is required."), 400

    profile_image = request.files['profileImage']
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')

    if not name or not email or not password or not profile_image:
        return jsonify(success=False, message="All fields are required."), 400

    hashed_password = generate_password_hash(password)

    # Create 'static/uploads/users/' if it doesn't exist
    user_upload_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'users')
    os.makedirs(user_upload_folder, exist_ok=True)

    # Save image
    filename = secure_filename(profile_image.filename)
    filepath = os.path.join(user_upload_folder, filename)
    profile_image.save(filepath)

    # Store relative path in DB (e.g., 'users/image.png')
    relative_path = f'users/{filename}'

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Check if email exists
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            return jsonify(success=False, message="Email already exists."), 409

        # Insert new user
        cursor.execute(
            "INSERT INTO users (name, email, password, profileImage) VALUES (%s, %s, %s, %s)",
            (name, email, hashed_password, relative_path)
        )
        conn.commit()

        return jsonify(success=True, message="User registered successfully!")
    except mysql.connector.Error as err:
        return jsonify(success=False, message=f"Database error: {err}"), 500
    finally:
        cursor.close()
        conn.close()


# Login API with session
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()

        if not email or not password:
            return jsonify({"success": False, "message": "Email and password are required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['email'] = user['email']
            return jsonify({
                "success": True,
                "user": {
                    "name": user.get("name"),
                    "email": user.get("email"),
                    "password": user.get("password"),
                    "profileImage": user.get("profileImage")

                }
            })
        else:
            return jsonify({"success": False, "message": "Invalid email or password"}), 401

    except Exception as e:
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500




@app.route('/update-user', methods=['POST'])
def update_user():
    current_email = request.form.get('email')  # Used as identifier

    new_name = request.form.get('name')
    new_email = request.form.get('new_email')  # Optional: to change email
    new_password = request.form.get('password')
    new_image = request.files.get('profileImage')  # Optional

    if not current_email:
        return jsonify(success=False, message="Current email is required."), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Check if user exists
        cursor.execute("SELECT * FROM users WHERE email = %s", (current_email,))
        user = cursor.fetchone()
        if not user:
            return jsonify(success=False, message="User not found."), 404

        updates = []
        values = []

        if new_name:
            updates.append("name = %s")
            values.append(new_name)

        if new_email:
            updates.append("email = %s")
            values.append(new_email)

        if new_password:
            hashed = generate_password_hash(new_password)
            updates.append("password = %s")
            values.append(hashed)

        if new_image:
            filename = secure_filename(new_image.filename)
            user_upload_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'users')
            os.makedirs(user_upload_folder, exist_ok=True)
            filepath = os.path.join(user_upload_folder, filename)
            new_image.save(filepath)
            relative_path = f'users/{filename}'

            updates.append("profileImage = %s")
            values.append(relative_path)

        if not updates:
            return jsonify(success=False, message="No update fields provided."), 400

        values.append(current_email)  # WHERE clause value

        sql = f"UPDATE users SET {', '.join(updates)} WHERE email = %s"
        cursor.execute(sql, values)
        conn.commit()

        return jsonify(success=True, message="User updated successfully!")

    except Exception as e:
        return jsonify(success=False, message=f"Error: {str(e)}"), 500
    finally:
        cursor.close()
        conn.close()




# Load your trained spaCy NER model
nlp = spacy.load("output/model-last")  # Change path if needed

@app.route('/ner', methods=['POST'])
def ner():
    data = request.get_json()
    paragraph = data.get("text", "").strip()

    if not paragraph or len(paragraph) > 500:
        return jsonify({"error": "Paragraph is empty or exceeds 500 characters."}), 400

    doc = nlp(paragraph)

    entity_colors = {
        "PER": "#ff6b6b",
        "LOC": "#4dabf7",
        "ORG": "#ffd43b",
        "DATE": "#63e6be"
    }

    result = ""
    last_idx = 0
    entity_count = 0

    for ent in doc.ents:
        result += paragraph[last_idx:ent.start_char]
        color = entity_colors.get(ent.label_, "#ccc")
        result += (
            f'<span style="background-color:{color}; '
            f'border:2px solid white; border-radius:6px; padding:2px 6px; margin:1px; color:black;">'
            f'{ent.text} <small style="font-weight:bold; border:1px solid white; padding: 2px 4px; color: white">{ent.label_}</small></span>'
        )
        last_idx = ent.end_char
        entity_count += 1

    result += paragraph[last_idx:]

    # Store in DB only if there are entities
    email = session.get('email')
    if email:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO history (email, predictedText) VALUES (%s, %s)",
            (email, result)
        )
        conn.commit()
        cursor.close()
        conn.close()

    return jsonify({
        "highlighted": result,
        "char_count": len(paragraph),
        "word_count": len(paragraph.split()),
        "entity_count": entity_count
    })


@app.route('/rener', methods=['POST'])
def rener():
    data = request.get_json()
    paragraph = data.get("text", "").strip()

    if not paragraph or len(paragraph) > 500:
        return jsonify({"error": "Paragraph is empty or exceeds 500 characters."}), 400

    doc = nlp(paragraph)

    entity_colors = {
        "PER": "#ff6b6b",
        "LOC": "#4dabf7",
        "ORG": "#ffd43b",
        "DATE": "#63e6be"
    }

    result = ""
    last_idx = 0
    entity_count = 0

    for ent in doc.ents:
        result += paragraph[last_idx:ent.start_char]
        color = entity_colors.get(ent.label_, "#ccc")
        result += (
            f'<span style="background-color:{color}; '
            f'border:2px solid white; border-radius:6px; padding:2px 6px; margin:1px; color:black;">'
            f'{ent.text} <small style="font-weight:bold; border:1px solid white; padding: 2px 4px; color: white">{ent.label_}</small></span>'
        )
        last_idx = ent.end_char
        entity_count += 1

    result += paragraph[last_idx:]
    return jsonify({
        "highlighted": result,
        "char_count": len(paragraph),
        "word_count": len(paragraph.split()),
        "entity_count": entity_count
    })


@app.route('/get-history')
def get_history():
    email = session.get("email")
    if not email:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, predictedText, date FROM history WHERE email = %s ORDER BY date DESC", (email,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify(rows)


@app.route('/delete-history/<int:id>', methods=['DELETE'])
def delete_history(id):
    email = session.get("email")
    if not email:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM history WHERE id = %s AND email = %s", (id, email))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})


@app.route('/update-history/<int:id>', methods=['PUT'])
def update_history(id):
    email = session.get("email")
    if not email:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    new_prediction = data.get("predictedText", "").strip()

    if not new_prediction:
        return jsonify({"error": "Updated prediction is empty"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE history SET predictedText = %s WHERE id = %s AND email = %s",
        (new_prediction, id, email)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"success": True})






@app.route('/history', methods=['GET'])
def history():
    email = request.args.get('email')  # 👈 Get email from query string
    if not email:
        return jsonify({"error": "Missing email"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT image, predictedDeepFake, date
        FROM history
        WHERE email = %s
        ORDER BY date DESC
    """, (email,))
    records = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(records)


# Predict nail condition
def predict_deepFake(model, image_path):
    class_labels = [
        "Fake","Real"
    ]

    img = Image.open(image_path).convert('RGB').resize((224, 224))
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0)

    predictions = model.predict(img_array)
    score = tf.nn.softmax(predictions[0])
    predicted_class_index = np.argmax(score)

    predicted_class = class_labels[predicted_class_index]

    return predicted_class, score[predicted_class_index].numpy() * 100


# Serve uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Run server
if __name__ == '__main__':
    app.run(debug=True)

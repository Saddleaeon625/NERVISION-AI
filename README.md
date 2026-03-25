# 🤖 NERVISION AI

An AI-powered Named Entity Recognition (NER) system designed to analyze Somali text and extract meaningful entities such as persons, locations, organizations, and dates. This project demonstrates full-stack development combined with machine learning integration.

---

## 🚀 Features

* 🔐 User Authentication (Signup & Login)
* 🔒 Secure Password Hashing
* 👤 Profile Image Upload
* 🧠 AI-Based NER Prediction (spaCy Model)
* 🎨 Highlighted Entity Visualization (PER, LOC, ORG, DATE)
* 📊 Interactive Dashboard
* 🕒 Prediction History Tracking
* ✏️ Update & Delete History
* 📱 Responsive UI (Mobile & Desktop)
* ⚡ Ready-to-use database setup with included SQL file

---

## 🧠 Entity Types Supported

* 👤 **PER** → Person (e.g., Axmed Barre)
* 📍 **LOC** → Location (e.g., Muqdisho)
* 🏢 **ORG** → Organization (e.g., Midowga Afrika)
* 📅 **DATE** → Date (e.g., 12-kii Febraayo 2024)

---

## 📸 Screenshots

### 🏠 Home Page

<p align="center">
  <img src="docs/Home.png" width="800">
</p>

### ℹ️ About Section

<p align="center">
  <img src="docs/About.png" width="800">
</p>

### ✨ Features Section

<p align="center">
  <img src="docs/Features.png" width="800">
</p>

### 👥 Team Section

<p align="center">
  <img src="docs/Teams.png" width="800">
</p>

### 🔐 Login Page

<p align="center">
  <img src="docs/Login.png" width="600">
</p>

### 📝 Signup Page

<p align="center">
  <img src="docs/Signup.png" width="600">
</p>

### 🤖 Prediction Dashboard

<p align="center">
  <img src="docs/Prediction_dashboard.png" width="800">
</p>

### 📜 History Dashboard

<p align="center">
  <img src="docs/History_dashboard.png" width="800">
</p>

---

## 🛠️ Tech Stack

### Frontend

* HTML
* CSS
* Bootstrap
* JavaScript
* jQuery

### Backend

* Flask (Python)

### Database

* MySQL

### AI / NLP

* spaCy (Custom Trained Model)

---

## 🧠 Concepts Applied

* Full-Stack Web Development
* REST API Design
* Session-Based Authentication
* File Upload Handling
* Natural Language Processing (NLP)
* Machine Learning Model Integration
* Data Persistence & History Tracking

---

## 📁 Project Structure

```
NERVISION SYSTEM/
│
├── docs/                  # Screenshots
│   ├── Home.png
│   ├── About.png
│   ├── Features.png
│   ├── Teams.png
│   ├── Login.png
│   ├── Signup.png
│   ├── Prediction_dashboard.png
│   └── History_dashboard.png
│
├── database/
│   └── ner.sql            # Database file
│
├── .venv/
├── node_modules/
├── output/                # spaCy trained model (ignored)
├── static/
├── templates/
│
├── .gitignore
├── app.py
└── README.md
```

---

## 🗄️ Database Setup

### 1. Create Database

```
CREATE DATABASE NER;
```

---

### 2. Import SQL File

```
mysql -u root -p NER < database/ner.sql
```

---

### 3. Configure Connection

Update `app.py` if needed:

```python
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='NER'
    )
```

---

### 📌 Note

* `ner.sql` already contains:

  * users table
  * history table
* Make sure MySQL server is running

---

## ⚙️ Getting Started

### 1. Clone Repository

```
git clone https://github.com/tubeec1/NERVISION-AI.git
cd NERVISION-AI
```

---

### 2. Install Dependencies

```
pip install flask numpy spacy mysql-connector-python werkzeug tensorflow pillow
```

---

### 3. Run Application

```
python app.py
```

---

### 4. Open Browser

```
http://localhost:5000
```

---

## 🔍 Example

**Input:**

```
Axmed Barre ayaa tagay Muqdisho 12-kii Febraayo 2024
```

**Output:**

* Axmed Barre → PER
* Muqdisho → LOC
* 12-kii Febraayo 2024 → DATE

---

## ⚠️ Important Notes

* AI model files are excluded due to GitHub size limits
* Ensure `output/model-last` exists locally
* Do not upload `.venv`, `node_modules`, or model files

---

## 🌍 Future Improvements

* 🌐 Deploy to cloud (Render / Railway)
* 📱 Improve mobile responsiveness
* 🌎 Multi-language NER support
* 🤖 Advanced deep learning models
* 📊 Analytics dashboard

---

## 👨‍💻 Author

**Mohamed Suleyman Ibrahim (Full Stack Developer)**

---

## ⭐ Support

If you like this project, give it a ⭐ on GitHub!

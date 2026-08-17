# 🔐 StegaVault 2.0

### Secure Multi-Media Steganography & Encryption Platform

> **StegaVault 2.0** is a secure web-based platform that hides secret messages inside **images, audio, and video files** using LSB steganography, with optional password-based encryption for an additional layer of security.

---

## 📌 Overview

Steganography is the technique of hiding information inside an ordinary-looking file so that the existence of the secret message is not obvious.

StegaVault combines **steganography and cryptography**:

**Without password:**

```text
Secret Message
      ↓
Binary Conversion
      ↓
LSB Embedding
      ↓
Stego Media
```

**With password:**

```text
Secret Message
      ↓
PBKDF2 Key Derivation
      ↓
Fernet Encryption
      ↓
Binary Conversion
      ↓
LSB Embedding
      ↓
Stego Media
```

The platform supports image, audio, and video steganography together with user authentication, operation history, vault management, administrator security monitoring, dark mode, live progress tracking, and a multilingual interface.

---

## ✨ Key Features

* 🔐 Password-based message encryption
* 🖼️ Image steganography using LSB
* 🎵 WAV audio steganography
* 🎥 Video steganography using lossless FFV1
* 👤 User registration and authentication
* 🛡️ Role-based access control
* 📜 Encode/decode operation history
* 🔎 Login activity and security monitoring
* 🔒 Admin account lock/unlock
* 🔑 Admin password reset
* 🌙 Dark mode
* 📊 Live processing progress
* 🌐 English, Hindi, Spanish and French interface
* 🛡️ CSRF protection
* 📁 Secure file-upload validation
* 💾 SQLite database
* 📈 Media capacity indicator

---

## 🧠 How Steganography Works

StegaVault uses **Least Significant Bit (LSB) steganography**.

For example, an RGB value can be changed from:

```text
11001000 = 200
```

to:

```text
11001001 = 201
```

Only the last bit changes, producing a very small modification that is normally invisible to the human eye.

The secret message is converted into binary and embedded into the least significant bits of the media data.

An end marker is added so that the decoder knows where the hidden message ends:

```text
1111111111111110
```

---

## 🔒 Encryption

Steganography hides the existence of information, while encryption protects the information itself.

When a password is provided, StegaVault encrypts the message before embedding it.

### Encryption Pipeline

```text
Password
   ↓
PBKDF2-SHA256
   ↓
32-byte Key
   ↓
Fernet Encryption
   ↓
Encrypted Payload
   ↓
LSB Steganography
```

### Security Details

* **Encryption:** Fernet
* **Cipher:** AES-128-CBC
* **Integrity:** HMAC-SHA256
* **Key Derivation:** PBKDF2-HMAC-SHA256
* **PBKDF2 Iterations:** 480,000
* **Salt:** Random 16-byte salt
* **Encryption Marker:** `SVENC1:`

The password itself is never stored in the database, history, or logs.

> ⚠️ A lost encryption password cannot be recovered.

---

## 🖼️ Image Steganography

StegaVault modifies the least significant bits of image color values to store the secret message.

### Recommended Format

| Format | Support           | Reason                                    |
| ------ | ----------------- | ----------------------------------------- |
| PNG    | ✅ Recommended     | Lossless                                  |
| JPEG   | ❌ Not recommended | Lossy compression can destroy hidden bits |

PNG should be used for reliable extraction.

---

## 🎵 Audio Steganography

For audio, the same LSB concept is applied to audio samples.

### Recommended Format

| Format | Support           | Reason                                    |
| ------ | ----------------- | ----------------------------------------- |
| WAV    | ✅ Recommended     | Lossless                                  |
| MP3    | ❌ Not recommended | Lossy compression can destroy hidden bits |

Small changes in audio sample values are generally inaudible.

---

## 🎥 Video Steganography

Video is processed frame by frame because each frame can be treated similarly to an image.

StegaVault uses:

```text
AVI Container
      +
FFV1 Lossless Codec
```

### Why FFV1?

Lossy codecs such as `mp4v` can rewrite pixel values during compression and destroy the hidden LSB data.

The project therefore uses **FFV1**, a lossless codec, to preserve the embedded information.

> The resulting video files can be significantly larger because lossless storage is required.

---

## 🏗️ System Architecture

```text
┌──────────────────────────────────────┐
│              Browser                 │
│ HTML + CSS + JavaScript + Jinja2     │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│          Flask Application            │
│        Application Factory            │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│             Routes Layer             │
│ Auth │ Image │ Audio │ Video │ Admin │
│ History │ Profile │ Settings │ etc.  │
└───────────────┬───────────┬──────────┘
                │           │
                ▼           ▼
       ┌──────────────┐ ┌──────────────┐
       │ Utils Layer  │ │ Models Layer │
       │              │ │              │
       │ Image        │ │ Users        │
       │ Audio        │ │ History      │
       │ Video        │ │ Login Logs   │
       │ Crypto       │ │              │
       └──────────────┘ └──────┬───────┘
                               │
                               ▼
                       ┌──────────────┐
                       │    SQLite    │
                       │  Database    │
                       └──────────────┘
```

The application follows an MVC-style structure with Flask Blueprints separating different features.

---

## 🗄️ Database

StegaVault uses SQLite with SQLAlchemy.

### Main Tables

#### `users`

Stores:

* User ID
* Username
* Email
* Password hash
* Profile information
* Role
* Account status
* Registration date
* Last login

#### `history`

Records:

* User
* Media type
* Encode/decode action
* Input/output filename
* Message information
* File size
* Processing time
* Operation status
* Timestamp

#### `login_logs`

Records:

* User/email
* Login status
* Failure reason
* IP address
* User agent
* Timestamp

---

## 🛠️ Technology Stack

| Technology                 | Purpose                   |
| -------------------------- | ------------------------- |
| **Python 3.8+**            | Core programming language |
| **Flask 3.1.3**            | Web framework             |
| **Flask-SQLAlchemy 3.1.1** | Database ORM              |
| **SQLAlchemy 2.0.51**      | Database abstraction      |
| **SQLite**                 | Database                  |
| **Pillow 12.3.0**          | Image processing          |
| **NumPy 2.5.1**            | Fast numerical processing |
| **OpenCV 5.0.0.93**        | Video processing          |
| **Cryptography 49.0.0**    | Encryption                |
| **Flask-Login 0.6.3**      | Authentication            |
| **Flask-WTF 1.3.0**        | CSRF protection           |
| **Flask-Babel 4.0.0**      | Internationalization      |
| **Jinja2 3.1.6**           | HTML templating           |
| **Flask-Migrate 4.1.0**    | Database migrations       |
| **python-dotenv 1.2.2**    | Environment configuration |

---

## 📁 Project Structure

```text
StegaVault-2/
│
├── app.py
├── config.py
├── extensions.py
├── models.py
├── history.py
├── login_log.py
├── requirements.txt
├── .env
│
├── routes/
│   ├── auth.py
│   ├── dashboard.py
│   ├── image.py
│   ├── audio.py
│   ├── video.py
│   ├── history.py
│   ├── profile.py
│   ├── settings.py
│   ├── admin.py
│   └── progress.py
│
├── utils/
│   ├── image_steganography.py
│   ├── audio_steganography.py
│   ├── video_steganography.py
│   ├── crypto.py
│   └── progress.py
│
├── templates/
├── static/
├── translations/
├── uploads/
├── outputs/
│
└── instance/
    └── stegavault.db
```

---

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Yugantt/StegaVault-2.0.git
cd StegaVault-2.0
```

### 2. Create a Virtual Environment

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file:

```env
SECRET_KEY=your-secret-key
```

> Never commit your real `SECRET_KEY` to GitHub.

### 5. Run the Application

```bash
python app.py
```

Then open the local address displayed by Flask in your browser.

---

## 🚀 Application Workflow

### Encoding

```text
Select Media
     ↓
Enter Secret Message
     ↓
Optional Password
     ↓
Encrypt Message
     ↓
Convert to Binary
     ↓
Check Media Capacity
     ↓
Embed Using LSB
     ↓
Generate Stego File
     ↓
Save / Download
     ↓
Record History
```

### Decoding

```text
Upload Stego Media
       ↓
Extract LSB Data
       ↓
Find End Marker
       ↓
Check Encryption Marker
       ↓
Enter Password if Required
       ↓
Decrypt Message
       ↓
Display Secret Message
       ↓
Record Operation
```

---

## 🛡️ Security Measures

StegaVault includes multiple security protections:

| Threat                     | Protection                                |
| -------------------------- | ----------------------------------------- |
| Database password exposure | Passwords stored as secure hashes         |
| Message disclosure         | Fernet encryption                         |
| Password attacks           | PBKDF2 with 480,000 iterations            |
| CSRF attacks               | Flask-WTF CSRF tokens                     |
| Session tampering          | Cryptographically signed session cookie   |
| SQL injection              | SQLAlchemy parameterized queries          |
| XSS                        | Jinja2 auto-escaping                      |
| Malicious uploads          | Extension whitelist + `secure_filename()` |
| Oversized uploads          | 500 MB maximum upload limit               |
| Brute-force monitoring     | Login attempt logging + account locking   |
| Unauthorized admin access  | Admin-only route protection               |
| Ciphertext tampering       | Fernet HMAC verification                  |
| Secret exposure in source  | `.env` configuration                      |

---

## 📊 Capacity

For images, capacity is approximately:

```text
Width × Height × 3 bits
```

The application also provides a browser-side capacity indicator before encoding.

For example, a `1920 × 1080` RGB image provides approximately:

```text
1920 × 1080 × 3
≈ 6.2 million bits
≈ 777,000 characters
```

Actual usable capacity is lower when encryption overhead and the end marker are included.

---

## 📈 Live Progress

Large video files can take significant processing time.

StegaVault provides real progress updates through a polling architecture:

```text
Browser
   │
   │ POST /video/encode
   ▼
Flask Server
   │
   │ Encoding
   ▼
Progress Tracker
   │
   │ GET /progress/<job_id>
   ▼
Browser Progress Bar
```

The browser polls the server approximately every 300 ms while processing is active.

---

## 🌐 Multi-Language Support

StegaVault supports four interface languages:

* 🇬🇧 English
* 🇮🇳 Hindi
* 🇪🇸 Spanish
* 🇫🇷 French

Internationalization is implemented using **Flask-Babel**.

---

## 👨‍💼 Admin & Security Dashboard

Administrators can monitor application security and user activity.

### Admin capabilities

* View registered users
* View operation history
* Monitor login attempts
* Lock/unlock accounts
* Force password resets
* Promote users to administrator
* Monitor failed login attempts
* View security statistics

---

## ⚠️ Limitations

The current version has some known limitations:

* PNG is required for reliable image steganography.
* WAV is required for reliable audio steganography.
* Video output uses AVI with FFV1.
* Lossy compression can destroy hidden data.
* LSB steganography can be detected through statistical steganalysis.
* Login rate limiting is not currently implemented.
* The development server uses HTTP rather than HTTPS.
* Progress state is stored in memory.
* The current application is not intended for production deployment.
* Language preference is session-based.

---

## 🔮 Future Scope

Possible future improvements include:

* 🔒 HTTPS/TLS deployment
* 🚦 Login rate limiting
* 📦 Batch media processing
* 🌐 REST API
* 🧠 Advanced steganography techniques
* 📊 Improved resistance against steganalysis
* 💾 Persistent progress storage using Redis
* 🌍 Permanent language preferences
* 📱 Mobile application
* 🚀 Production deployment using Gunicorn and Nginx

---

## 🧪 Testing

The project can be tested using:

### Image

```text
PNG → Encode → Decode → Verify Message
```

### Audio

```text
WAV → Encode → Decode → Verify Message
```

### Video

```text
AVI + FFV1 → Encode → Decode → Verify Message
```

### Encryption

```text
Correct Password → Successful Decryption
Wrong Password   → Decryption Failure
Tampered Data    → Integrity Failure
```

---

## 🔍 Important Technical Notes

### Why not JPEG?

JPEG uses lossy compression, which can modify pixel values and destroy the least significant bits containing the hidden message.

### Why not MP3?

MP3 compression can modify audio samples, which can destroy LSB-embedded information.

### Why FFV1?

FFV1 is lossless, allowing the embedded video data to survive encoding.

### Why NumPy?

Large images contain millions of pixel values. NumPy provides efficient array operations for processing these values.

### Why SQLite?

SQLite provides a simple, zero-configuration database suitable for the current project scale.

---

## 📚 Project Statistics

According to the project guide:

* **14,198+ lines of code**
* **58 files**
* **3 media types**
* **4 interface languages**
* **10 Flask Blueprints**
* **SQLite database**
* **LSB steganography**
* **Fernet encryption**
* **PBKDF2-SHA256 key derivation**

---

## 🎯 Use Cases

StegaVault can demonstrate applications in:

* 🔐 Secure communication
* 🕵️ Privacy-oriented data hiding
* 📁 Secure data storage
* 🧪 Cybersecurity education
* 🎓 Academic steganography research
* 🔎 Digital security experiments
* 🛡️ Information protection

---

## ⚠️ Security Disclaimer

StegaVault is an **academic/project implementation** and is not currently production-ready.

The project guide identifies missing production protections such as HTTPS, login rate limiting, persistent progress storage, and deployment behind a production server.

Do not use the development server to handle real sensitive information.

---

## 👨‍💻 Project

**Project:** StegaVault 3.0
**Category:** Cybersecurity / Steganography
**Platform:** Web Application
**Language:** Python
**Framework:** Flask
**Database:** SQLite

---

## ⭐ Support

If you find this project useful for learning about **steganography, encryption, Flask, or multimedia security**, consider giving the repository a ⭐.

---

### 🔐 StegaVault 3.0

> **Hide the message. Protect the information. Secure the data.**

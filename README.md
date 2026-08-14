🔐 StegaVault 3.0

Secure Multi-Media Steganography Platform

StegaVault 3.0 is a web-based security application that combines LSB
steganography with optional password-based encryption to protect
sensitive information.
---------------------------------------------------------------------------------
✨ Features

🖼️ Image steganography using LSB

🎵 Audio steganography using WAV

🎬 Video steganography using AVI + FFV1

🔐 Fernet encryption with PBKDF2-derived keys

👤 User registration, login and session management

🧾 Encoding/decoding history

🛡️ Admin dashboard and security monitoring

🌙 Responsive UI and dark mode

🌐 Multi-language support

📈 Live progress for video processing
---------------------------------------------------------------------------------------
🏗️ Architecture

Browser
   │
   ▼
Flask Web Application
   │
   ├── Authentication
   ├── Image Module ── LSB
   ├── Audio Module ── LSB
   ├── Video Module ── Frame + LSB
   ├── Encryption ─── Fernet + PBKDF2
   └── Admin / History
             │
             ▼
          SQLite
---------------------
🔄 Encoding Workflow
---------------------
Cover Media
    ↓
Secret Message
    ↓
Optional Password
    ↓
Encrypt Message
    ↓
Convert to Binary
    ↓
LSB Embedding
    ↓
Stego-Media
    ↓
Save + Record History

---------------------
🔓 Decoding Workflow
---------------------

Stego-Media
    ↓
Read LSB Bits
    ↓
Detect End Marker
    ↓
Rebuild Hidden Data
    ↓
Detect Encrypted Payload
    ↓
Decrypt with Password
    ↓
Original Message


----------------------------
🧩 Technology Stack
----------------------------
Category               Technology

Language               Python 3.8+
Framework              Flask
Database               SQLite
ORM                    Flask-SQLAlchemy
Image Processing       Pillow
Numerical Processing   NumPy
Video Processing       OpenCV
Cryptography           Python Cryptography
Front-End              HTML, CSS, JavaScript
Templates              Jinja2
Steganography          LSB


==============================================================
🔐 Security

StegaVault uses a layered approach:

Secret → Encryption → LSB Embedding → Stego-Media

Security-related features include:

Password hashing

Fernet authenticated encryption

PBKDF2 key derivation

CSRF protection

Signed sessions

SQLAlchemy parameterized queries

Jinja2 auto-escaping

Secure filename handling

File-extension validation

Login activity logging

Admin account controls

The encryption password is not stored as plaintext in the database or
activity logs.

📁 Supported Media

Image

Recommended: PNG

JPEG is not recommended for reliable LSB extraction because lossy
compression can modify hidden bits.

Audio

Recommended: WAV

MP3 compression can corrupt hidden LSB data.

Video

Recommended: AVI + FFV1

FFV1 is used as a lossless codec so embedded information can survive
video encoding.

🚀 Installation

1. Clone

git clone https://github.com/Yugantt/StegaVault-2.0.git
cd StegaVault-2.0

2. Virtual environment

Windows:

python -m venv venv
venv\Scripts\activate

Linux/macOS:

python3 -m venv venv
source venv/bin/activate

3. Install dependencies

pip install -r requirements.txt

4. Run

python app.py

Open the local Flask address shown in the terminal.

📂 Project Modules

StegaVault
├── Authentication
├── Image Steganography
├── Audio Steganography
├── Video Steganography
├── Encryption
├── History
├── Admin Dashboard
└── SQLite Database

📊 Results

Media   Format       Result

Image   PNG          ✅ Supported
Image   JPEG         ⚠️ Lossy compression may corrupt data
Audio   WAV          ✅ Supported
Audio   MP3          ⚠️ Lossy compression may corrupt data
Video   AVI + FFV1   ✅ Supported

Approximate project metrics:

Metric                Image PNG    Audio WAV   Video AVI/FFV1

Embedding Speed      ~0.8 MB/s   ~0.5 MB/s       ~0.3 MB/s
Extraction Speed     ~0.6 MB/s   ~0.4 MB/s       ~0.2 MB/s
Approx. Capacity          ~30%        ~20%            ~15%

Actual performance depends on hardware and media characteristics.

📸 Screenshots

Recommended repository structure:

docs/
├── register.png
├── dashboard.png
├── image-steganography.png
├── audio-steganography.png
├── video-steganography.png
├── admin-dashboard.png
├── security.png
└── history.png

Example:

![StegaVault Dashboard](docs/dashboard.png)

🎯 Use Cases

Cybersecurity education

Steganography experiments

Secure communication research

Data privacy demonstrations

Multimedia security research

Digital watermarking research

Forensic security experiments

⚠️ Limitations

Basic LSB can be vulnerable to statistical steganalysis.

Lossy formats can damage hidden information.

Lossless video produces larger files.

Development configuration should not be treated as a production
deployment.

Production deployments should use HTTPS/TLS and appropriate server
infrastructure.

🔮 Future Scope

DCT/DWT-based steganography

Improved resistance against steganalysis

Batch processing

REST API

Cloud storage integration

Mobile application

Multi-factor authentication

Production-grade rate limiting

Redis-backed progress tracking

Gunicorn + Nginx deployment

👨‍💻 Project Information

Project: StegaVault 3.0
Type: Web-Based Security / Steganography Application
Technology: Python + Flask
Database: SQLite
Technique: LSB Steganography
Encryption: Fernet + PBKDF2

📜 License

This project is intended for educational, academic and research
purposes. Add a project-specific LICENSE file before public
distribution.

🙏 Acknowledgement

Developed as part of vocational/academic training to demonstrate
practical concepts in web development, cryptography, steganography,
database management, authentication, multimedia processing and
cybersecurity.

⭐ If you find the project useful, consider starring the repository.

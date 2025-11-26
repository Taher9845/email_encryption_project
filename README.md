Secure Email Encryption and Digital Signature System Using RSA-OAEP, AES-GCM, and SHA-256

This project implements a complete end-to-end secure email communication system using a hybrid cryptographic design. It integrates AES-GCM for fast symmetric encryption, RSA-OAEP for secure key encapsulation, RSA-PSS for digital signatures, SHA-256 for hashing, and a CRL mechanism for trust management. The system is implemented using Python and Flask to provide a lightweight and user-friendly secure email platform suitable for academic and research purposes.

Features
Hybrid Encryption

AES-256 GCM for authenticated symmetric encryption

RSA-OAEP for secure key wrapping

Combined design ensures confidentiality, integrity, and efficient performance

Digital Signatures

RSA-PSS for robust, standards-compliant signing

SHA-256 hashing of message headers and content

Ensures sender authenticity and tamper detection

Security Enhancements

Header integrity verification using SHA-256

Key Revocation List (CRL) for blocking compromised keys

AES-GCM tag validation for tamper detection

Web Interface (Flask)

Compose, encrypt, and sign emails

View encrypted inbox

Verify and decrypt received messages

Easy-to-use REST-based structure

Project Structure
email_encryption_project/
│── app.py                  # Flask application and routing
│── crypto.py               # All cryptographic operations
│── requirements.txt        # Python dependencies
│── README.md               # Documentation
│── templates/              # HTML templates (UI)
│── static/style.css        # CSS for UI
│── outbox/                 # Encrypted email storage
│── keys/                   # Public/Private keys (demo only)
│── crl.json                # Key Revocation List
│── .gitignore

Installation and Setup
1. Clone the Repository
git clone https://github.com/Taher9845/email_encryption_project.git
cd email_encryption_project

2. Create Virtual Environment
python -m venv venv

3. Activate Environment

Windows:

venv\Scripts\activate


Linux/Mac:

source venv/bin/activate

4. Install Required Packages
pip install -r requirements.txt

5. Start the Application
python app.py

6. Access in Browser
http://127.0.0.1:5000/

Key Generation

To generate RSA public and private keys, use:

python crypto.py


Note: Never commit private keys to public repositories.

Deployment (Render Recommended)
Steps:

Push the project to a GitHub repository

Go to https://render.com
 and create a new Web Service

Connect your GitHub repo

Configure:

Build Command

pip install -r requirements.txt


Start Command

gunicorn app:app --bind 0.0.0.0:$PORT


Environment Variables

FLASK_ENV=production
SECRET_KEY=<your-secret-key>

Performance Summary

The system was evaluated using benchmark simulations for message sizes from 1 KB to 1 MB.
Key observations:

AES-GCM shows linear, predictable scaling

RSA-OAEP and RSA-PSS operations remain constant regardless of message size

End-to-end overhead for sender and receiver stays around 70–73 ms

System supports real-time encrypted communication without noticeable delay

Performance graphs included in the report show:

AES-GCM encryption/decryption time

RSA operation cost

Combined hybrid overhead

Security Notes

Private keys must never be stored in public repositories

Use environment variables for sensitive data

For production, keys should be stored in a Hardware Security Module (HSM)

Enable HTTPS when deploying online

Contributors

Mohammed Taher

Mohammed Anzar Shah

Under the guidance of
Prof. Jesy Janet Kumari
Department of Computer Science and Engineering
The Oxford College of Engineering

License

MIT License
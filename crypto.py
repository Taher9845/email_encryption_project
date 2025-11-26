import os
import json
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import secrets
from base64 import b64encode, b64decode

def generate_rsa_keypair(bits=2048):
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=bits)
    public_key = private_key.public_key()
    return private_key, public_key

def serialize_private_key(private_key, path, password=None):
    enc = serialization.BestAvailableEncryption(password.encode()) if password else serialization.NoEncryption()
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=enc
    )
    with open(path, "wb") as f:
        f.write(pem)

def serialize_public_key(public_key, path):
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    with open(path, "wb") as f:
        f.write(pem)

def load_private_key(path, password=None):
    with open(path, "rb") as f:
        data = f.read()
    return serialization.load_pem_private_key(data, password=password.encode() if password else None)

def load_public_key(path):
    with open(path, "rb") as f:
        data = f.read()
    return serialization.load_pem_public_key(data)

# Hybrid encryption: AES-GCM for data, RSA for AES key
def hybrid_encrypt(plaintext: bytes, receiver_pubkey):
    aes_key = AESGCM.generate_key(bit_length=256)
    aesgcm = AESGCM(aes_key)
    nonce = secrets.token_bytes(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    # encrypt aes_key with receiver public key
    enc_key = receiver_pubkey.encrypt(
        aes_key,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    )
    envelope = {
        "enc_key": b64encode(enc_key).decode(),
        "nonce": b64encode(nonce).decode(),
        "ciphertext": b64encode(ciphertext).decode()
    }
    return envelope

def hybrid_decrypt(envelope: dict, receiver_privkey):
    from base64 import b64decode
    enc_key = b64decode(envelope["enc_key"])
    nonce = b64decode(envelope["nonce"])
    ciphertext = b64decode(envelope["ciphertext"])
    aes_key = receiver_privkey.decrypt(
        enc_key,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    )
    aesgcm = AESGCM(aes_key)
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    return plaintext

# Signing (RSA-PSS + SHA-256)
def sign_message(private_key, message: bytes):
    sig = private_key.sign(
        message,
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256()
    )
    from base64 import b64encode
    return b64encode(sig).decode()

def verify_signature(public_key, message: bytes, signature_b64: str):
    from base64 import b64decode
    sig = b64decode(signature_b64)
    try:
        public_key.verify(
            sig,
            message,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )
        return True
    except Exception:
        return False

# Header hashing (simple canonicalization)
def header_hash(headers: dict):
    # Only use selected headers in deterministic order
    keys = ['From', 'To', 'Subject', 'Date']
    h = "".join((headers.get(k, "").strip() for k in keys)).encode()
    digest = hashes.Hash(hashes.SHA256())
    digest.update(h)
    return digest.finalize()

def load_crl(path):
    if not os.path.exists(path):
        return {"revoked": []}
    with open(path, "r") as f:
        return json.load(f)

def is_key_revoked(pubkey_path, crl_path):
    crl = load_crl(crl_path)
    # Compare filename or full key text
    pubname = os.path.basename(pubkey_path)
    return pubname in crl.get("revoked", [])

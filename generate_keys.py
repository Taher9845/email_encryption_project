from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import os

os.makedirs('keys', exist_ok=True)

def gen_keypair(name, passphrase=None, bits=2048):
    priv = rsa.generate_private_key(public_exponent=65537, key_size=bits)
    if passphrase:
        encryption = serialization.BestAvailableEncryption(passphrase.encode())
    else:
        encryption = serialization.NoEncryption()
    priv_pem = priv.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=encryption
    )
    pub_pem = priv.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    with open(f'keys/{name}_priv.pem', 'wb') as f: f.write(priv_pem)
    with open(f'keys/{name}_pub.pem', 'wb') as f: f.write(pub_pem)

if __name__ == "__main__":
    gen_keypair('server', passphrase=None)
    print("Generated server keypair in ./keys")

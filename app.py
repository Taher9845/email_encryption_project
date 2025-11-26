from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from werkzeug.utils import secure_filename
import os, json
from crypto import generate_rsa_keypair, serialize_private_key, serialize_public_key, load_public_key, load_private_key, hybrid_encrypt, hybrid_decrypt, sign_message, verify_signature, header_hash, is_key_revoked
from pathlib import Path
from base64 import b64encode, b64decode

APP_ROOT = Path(__file__).parent
KEYS_DIR = APP_ROOT / "keys"
CRL_PATH = APP_ROOT / "crl.json"
ALLOWED_EXT = set(["txt"])

app = Flask(__name__)
app.secret_key = "supersecretdevkey"

def list_keys():
    return [p.name for p in KEYS_DIR.glob("*.pem")]

@app.route("/")
def index():
    return render_template("index.html", keys=list_keys())

@app.route("/generate_keys", methods=["POST"])
def generate_keys():
    name = request.form.get("name","user")
    bits = int(request.form.get("bits", "2048"))
    priv, pub = generate_rsa_keypair(bits)
    priv_path = KEYS_DIR / f"{name}_priv.pem"
    pub_path = KEYS_DIR / f"{name}_pub.pem"
    serialize_private_key(priv, str(priv_path))
    serialize_public_key(pub, str(pub_path))
    flash(f"Keys generated: {pub_path.name}")
    return redirect(url_for("index"))

@app.route("/compose", methods=["GET","POST"])
def compose():
    if request.method == "POST":
        sender = request.form["sender"]
        receiver = request.form["receiver"]
        subject = request.form["subject"]
        body = request.form["body"].encode()
        # load receiver pubkey
        recv_pub = load_public_key(str(KEYS_DIR / (receiver + "_pub.pem")))
        env = hybrid_encrypt(body, recv_pub)
        # header hash and sign with sender privkey
        headers = { "From": sender, "To": receiver, "Subject": subject, "Date": request.form.get("date","")}
        hh = header_hash(headers)
        # sign header hash + ciphertext bytes
        signer = load_private_key(str(KEYS_DIR / (sender + "_priv.pem")))
        # sign concatenated data (safe simple approach)
        payload_to_sign = hh + b"::" + env['ciphertext'].encode()
        signature = sign_message(signer, payload_to_sign)
        # create envelope json
        envelope = {
            "headers": headers,
            "envelope": env,
            "signature": signature,
            "sender_pub": f"{sender}_pub.pem"
        }
        # save message to file (simulate sending)
        outpath = APP_ROOT / "outbox"
        outpath.mkdir(exist_ok=True)
        idx = len(list(outpath.glob("*.json")))+1
        msgpath = outpath / f"msg_{idx}.json"
        with open(msgpath, "w") as f:
            json.dump(envelope, f)
        flash(f"Message composed and saved as {msgpath.name}")
        return redirect(url_for("index"))
    return render_template("compose.html", keys=list_keys())

@app.route("/inbox")
def inbox():
    outpath = APP_ROOT / "outbox"
    msgs = []
    if outpath.exists():
        for p in sorted(outpath.glob("*.json")):
            with open(p,"r") as f:
                data = json.load(f)
            msgs.append({"file": p.name, "from": data["headers"].get("From"), "subject": data["headers"].get("Subject")})
    return render_template("inbox.html", msgs=msgs)

@app.route("/view/<filename>")
def view_message(filename):
    p = APP_ROOT / "outbox" / filename
    if not p.exists():
        flash("Message not found")
        return redirect(url_for("inbox"))
    with open(p,"r") as f:
        data = json.load(f)
    return render_template("view.html", msg=data, filename=filename)

@app.route("/verify/<filename>", methods=["POST"])
def verify(filename):
    p = APP_ROOT / "outbox" / filename
    with open(p,"r") as f:
        data = json.load(f)
    sender_pub_path = KEYS_DIR / data.get("sender_pub")
    # CRL check
    revoked = is_key_revoked(str(sender_pub_path), str(CRL_PATH))
    if revoked:
        result = {"status":"revoked", "reason":"sender public key is revoked (CRL)"}
        return render_template("result.html", result=result)
    # reconstruct verification blob
    hh = header_hash(data["headers"])
    payload_to_verify = hh + b"::" + data["envelope"]["ciphertext"].encode()
    pub = load_public_key(str(sender_pub_path))
    ok = verify_signature(pub, payload_to_verify, data["signature"])
    if not ok:
        result = {"status":"failed", "reason":"signature verification failed"}
        return render_template("result.html", result=result)
    # decrypt with receiver private key (assume receiver selected via form)
    receiver = request.form.get("receiver_for_verify")
    try:
        recv_priv = load_private_key(str(KEYS_DIR / (receiver + "_priv.pem")))
    except Exception as e:
        result = {"status":"error","reason":"receiver private key not found: "+str(e)}
        return render_template("result.html", result=result)
    plaintext = hybrid_decrypt(data["envelope"], recv_priv)
    result = {"status":"ok","plaintext": plaintext.decode(), "headers": data["headers"]}
    return render_template("result.html", result=result)

if __name__ == "__main__":
    app.run(debug=True, port=5000)

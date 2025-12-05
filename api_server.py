from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import base64
import os
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256
from totp_utils import generate_totp_code, verify_totp_code

app = FastAPI()

SEED_FILE = "seed.txt"
PRIVATE_KEY_FILE = "student_private.pem"

# --------------------
# Request models
# --------------------
class DecryptSeedRequest(BaseModel):
    encrypted_seed: str

class Verify2FARequest(BaseModel):
    code: str

# --------------------
# Endpoint 1: Decrypt Seed
# --------------------
@app.post("/decrypt-seed")
def decrypt_seed(req: DecryptSeedRequest):
    try:
        # Load private key
        with open(PRIVATE_KEY_FILE, "rb") as f:
            private_key = RSA.import_key(f.read())

        # Decode and decrypt
        encrypted_bytes = base64.b64decode(req.encrypted_seed)
        cipher = PKCS1_OAEP.new(private_key, hashAlgo=SHA256)
        decrypted_bytes = cipher.decrypt(encrypted_bytes)
        hex_seed = decrypted_bytes.decode("utf-8").strip()

        # Validate 64-char hex
        if len(hex_seed) != 64 or not all(c in "0123456789abcdef" for c in hex_seed.lower()):
            raise ValueError("Invalid seed format")

        # Save seed
        with open(SEED_FILE, "w") as f:
            f.write(hex_seed)

        return {"status": "ok"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Decryption failed: {str(e)}")

# --------------------
# Endpoint 2: Generate 2FA
# --------------------
@app.get("/generate-2fa")
def generate_2fa():
    if not os.path.exists(SEED_FILE):
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")

    with open(SEED_FILE, "r") as f:
        hex_seed = f.read().strip()

    code = generate_totp_code(hex_seed)
    # Remaining seconds in current 30s period
    import time
    valid_for = 30 - (int(time.time()) % 30)
    
    return {"code": code, "valid_for": valid_for}

# --------------------
# Endpoint 3: Verify 2FA
# --------------------
@app.post("/verify-2fa")
def verify_2fa(req: Verify2FARequest):
    if not req.code:
        raise HTTPException(status_code=400, detail="Missing code")
    
    if not os.path.exists(SEED_FILE):
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")

    with open(SEED_FILE, "r") as f:
        hex_seed = f.read().strip()

    is_valid = verify_totp_code(hex_seed, req.code)
    return {"valid": is_valid}

# --------------------
# Run: uvicorn api_server:app --reload
# --------------------

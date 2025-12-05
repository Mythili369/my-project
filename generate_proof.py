#!/usr/bin/env python3
"""
generate_proof.py

- Reads latest commit hash from git
- Signs ASCII commit hash with student_private.pem using RSA-PSS (SHA-256, max salt length)
- Encrypts signature with instructor_public.pem using RSA/OAEP (SHA-256, MGF1)
- Prints:
    Commit Hash: <40-char hex>
    Encrypted Signature (base64, single line): <BASE64>
"""

import subprocess
import base64
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa, utils
from cryptography.hazmat.backends import default_backend
from pathlib import Path
import sys

# ---------- Utility functions ----------

def load_private_key(path: str):
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Private key not found: {path}")
    data = p.read_bytes()
    return serialization.load_pem_private_key(data, password=None, backend=default_backend())

def load_public_key(path: str):
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Public key not found: {path}")
    data = p.read_bytes()
    return serialization.load_pem_public_key(data, backend=default_backend())

def get_latest_commit_hash() -> str:
    """Return the latest commit hash (40-char hex). Requires git and to be run in repo."""
    try:
        out = subprocess.check_output(["git", "log", "-1", "--format=%H"], stderr=subprocess.STDOUT)
        commit_hash = out.decode().strip()
        if len(commit_hash) != 40:
            raise ValueError(f"Unexpected commit hash length: '{commit_hash}'")
        return commit_hash
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to get commit hash via git: {e.output.decode().strip()}")

def sign_message(message: str, private_key) -> bytes:
    """
    Sign a message using RSA-PSS with SHA-256 and maximum salt length.

    - message: ASCII string (commit hash)
    - private_key: cryptography private key object

    Returns signature bytes.
    """
    message_bytes = message.encode("utf-8")  # CRITICAL: sign ASCII/UTF-8 string
    signature = private_key.sign(
        message_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature

def encrypt_with_public_key(data: bytes, public_key) -> bytes:
    """
    Encrypt data using RSA/OAEP with SHA-256 and MGF1(SHA-256).
    Returns ciphertext bytes.
    """
    ciphertext = public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return ciphertext

# ---------- Main ----------

def main():
    # Paths (adjust if needed)
    student_priv_path = "student_private.pem"
    instructor_pub_path = "instructor_public.pem"

    try:
        commit_hash = get_latest_commit_hash()
    except Exception as e:
        print("ERROR: could not get commit hash:", e, file=sys.stderr)
        sys.exit(1)

    try:
        priv = load_private_key(student_priv_path)
    except Exception as e:
        print("ERROR: could not load student private key:", e, file=sys.stderr)
        sys.exit(1)

    try:
        instr_pub = load_public_key(instructor_pub_path)
    except Exception as e:
        print("ERROR: could not load instructor public key:", e, file=sys.stderr)
        sys.exit(1)

    try:
        signature = sign_message(commit_hash, priv)
    except Exception as e:
        print("ERROR: signing failed:", e, file=sys.stderr)
        sys.exit(1)

    try:
        encrypted_sig = encrypt_with_public_key(signature, instr_pub)
    except Exception as e:
        print("ERROR: encryption with instructor public key failed:", e, file=sys.stderr)
        sys.exit(1)

    b64_encrypted = base64.b64encode(encrypted_sig).decode("utf-8")

    # Output (exactly as required)
    print("Commit Hash:", commit_hash)
    print("Encrypted Signature (base64):")
    print(b64_encrypted)   # single-line base64

if __name__ == "__main__":
    main()

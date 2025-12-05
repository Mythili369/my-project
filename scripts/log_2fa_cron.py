#!/usr/bin/env python3
import os
import datetime
import pyotp
import base64

# Path to the seed file
SEED_FILE = "/data/seed.txt"

# Path to the output file (cron log)
OUTPUT_FILE = "/cron/last_code.txt"

try:
    # 1️⃣ Read the seed
    with open(SEED_FILE, "r") as f:
        seed = f.read().strip()  # Remove whitespace/newlines

    # 2️⃣ Convert hex seed to base32 (if not already base32)
    try:
        # Try decoding as base32 to check
        base64.b32decode(seed, casefold=True)
        base32_seed = seed  # Already valid base32
    except Exception:
        # Assume hex and convert
        base32_seed = base64.b32encode(bytes.fromhex(seed)).decode()

    # 3️⃣ Create TOTP
    totp = pyotp.TOTP(base32_seed)
    code = totp.now()

    # 4️⃣ Get UTC timestamp
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    # 5️⃣ Format output
    output_line = f"{timestamp} - 2FA Code: {code}\n"

except FileNotFoundError:
    output_line = f"{datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} - Seed file not found\n"
except Exception as e:
    output_line = f"{datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} - Error: {e}\n"

# Append to log
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
with open(OUTPUT_FILE, "a") as f:
    f.write(output_line)

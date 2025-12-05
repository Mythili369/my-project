import base64
import pyotp

def hex_to_base32(hex_seed: str) -> str:
    """
    Convert 64-char hex seed → bytes → base32 string
    """
    seed_bytes = bytes.fromhex(hex_seed)
    base32_seed = base64.b32encode(seed_bytes).decode("utf-8")
    return base32_seed


def generate_totp_code(hex_seed: str) -> str:
    """
    Generate current 6-digit TOTP code.
    """
    base32_seed = hex_to_base32(hex_seed)
    totp = pyotp.TOTP(base32_seed)
    return totp.now()


def verify_totp_code(hex_seed: str, code: str, valid_window: int = 1) -> bool:
    """
    Verify a TOTP code (±30s default tolerance)
    """
    base32_seed = hex_to_base32(hex_seed)
    totp = pyotp.TOTP(base32_seed)
    return totp.verify(code, valid_window=valid_window)


# --- OPTIONAL DEMO ---
if __name__ == "__main__":
    # Load your decrypted 64-char hex seed
    with open("seed.txt", "r") as f:
        hex_seed = f.read().strip()

    current_code = generate_totp_code(hex_seed)
    print("TOTP:", current_code)

    print("Verifies?", verify_totp_code(hex_seed, current_code))


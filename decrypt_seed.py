import base64
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

def decrypt_seed(encrypted_seed_b64: str, private_key):
    """
    Decrypt base64-encoded encrypted seed using RSA/OAEP + SHA-256
    """
    # Step 1: Base64 decode
    encrypted_bytes = base64.b64decode(encrypted_seed_b64)

    # Step 2: RSA Decrypt
    decrypted_bytes = private_key.decrypt(
        encrypted_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Step 3: Convert bytes → UTF-8 string
    seed_hex = decrypted_bytes.decode("utf-8")

    # Step 4: Validate hex string
    if len(seed_hex) != 64:
        raise ValueError("Invalid seed length (must be 64 hex chars).")

    allowed = "0123456789abcdef"
    if any(ch not in allowed for ch in seed_hex.lower()):
        raise ValueError("Seed contains invalid characters.")

    return seed_hex


if __name__ == "__main__":
    # Load your private key
    with open("student_private.pem", "rb") as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=None,
        )

    # Read encrypted seed (from Step 4)
    with open("encrypted_seed.txt", "r") as f:
        encrypted_seed_b64 = f.read().strip()

    # Decrypt
    seed = decrypt_seed(encrypted_seed_b64, private_key)
    print("Decrypted Seed:", seed)

    # Save seed to container location later (/data/seed.txt)
    with open("seed.txt", "w") as f:
        f.write(seed)

    print("Saved seed to seed.txt")

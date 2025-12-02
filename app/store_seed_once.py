# app/store_seed_once.py

from app.crypto_utils import decrypt_seed
import os


def main():
    # read encrypted seed from file
    with open("encrypted_seed.txt", "r") as f:
        encrypted_b64 = f.read().strip()

    hex_seed = decrypt_seed(encrypted_b64)

    os.makedirs("data", exist_ok=True)
    with open("data/seed.txt", "w") as f:
        f.write(hex_seed + "\n")

    print("Decrypted seed stored in data/seed.txt")


if __name__ == "_main_":
    main()
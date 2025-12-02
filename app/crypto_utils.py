
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from typing import Tuple
import base64
import os
import requests




def generate_rsa_keypair(key_size: int = 4096) -> Tuple[bytes, bytes]:
    
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
    )
    public_key = private_key.public_key()

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )

    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    return private_pem, public_pem


def save_student_keys():
    
    os.makedirs("keys", exist_ok=True)
    private_pem, public_pem = generate_rsa_keypair()

    with open("keys/student_private.pem", "wb") as f:
        f.write(private_pem)

    with open("keys/student_public.pem", "wb") as f:
        f.write(public_pem)

    print("Saved keys in keys/student_private.pem and keys/student_public.pem")



def request_seed(student_id: str, github_repo_url: str, api_url: str) -> None:
   
    with open("keys/student_public.pem", "r") as f:
        public_key_pem = f.read()

    payload = {
        "student_id": student_id,
        "github_repo_url": github_repo_url,
        "public_key": public_key_pem
    }

    resp = requests.post(api_url, json=payload, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    if data.get("status") != "success":
        raise RuntimeError(f"API error: {data}")

    encrypted_seed = data["encrypted_seed"]

    with open("encrypted_seed.txt", "w") as f:
        f.write(encrypted_seed)

    print("Encrypted seed saved to encrypted_seed.txt")



def _load_private_key():
    with open("keys/student_private.pem", "rb") as f:
        private_pem = f.read()
    private_key = serialization.load_pem_private_key(
        private_pem,
        password=None,
    )
    return private_key


def decrypt_seed(encrypted_seed_b64: str) -> str:
    private_key = _load_private_key()

    # 1. base64 decode
    cipher_bytes = base64.b64decode(encrypted_seed_b64)

    # 2. RSA/OAEP decrypt
    plain_bytes = private_key.decrypt(
        cipher_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    hex_seed = plain_bytes.decode("utf-8").strip()

    # 3. validation: 64-char hex
    if len(hex_seed) != 64:
        raise ValueError("Seed must be 64 characters")

    allowed = set("0123456789abcdef")
    if any(c not in allowed for c in hex_seed):
        raise ValueError("Seed must be lowercase hex")

    # 4. NEW — Save automatically to data/seed.txt
    os.makedirs("data", exist_ok=True)
    with open("data/seed.txt", "w") as f:
        f.write(hex_seed)

    print("Decrypted seed saved to data/seed.txt")

    return hex_seed

# app/main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

from app.crypto_utils import decrypt_seed
from app.totp_utils import (
    generate_totp_code,
    seconds_remaining_in_period,
    verify_totp_code,
)

app = FastAPI()

SEED_PATH = "/data/seed.txt"  # this path will be used inside Docker


# ------------ Models ------------

class DecryptRequest(BaseModel):
    encrypted_seed: str


class Generate2FAResponse(BaseModel):
    code: str
    valid_for: int


class VerifyRequest(BaseModel):
    code: str


class VerifyResponse(BaseModel):
    valid: bool


# ------------ Helpers ------------

def _read_hex_seed() -> str:
    if not os.path.exists(SEED_PATH):
        raise FileNotFoundError("Seed not decrypted yet")
    with open(SEED_PATH, "r") as f:
        return f.read().strip()


# ------------ Endpoint 1: POST /decrypt-seed ------------

@app.post("/decrypt-seed")
def decrypt_seed_endpoint(body: DecryptRequest):
    try:
        hex_seed = decrypt_seed(body.encrypted_seed)
        os.makedirs(os.path.dirname(SEED_PATH), exist_ok=True)
        with open(SEED_PATH, "w") as f:
            f.write(hex_seed + "\n")
        return {"status": "ok"}
    except Exception:
        raise HTTPException(status_code=500, detail="Decryption failed")


# ------------ Endpoint 2: GET /generate-2fa ------------

@app.get("/generate-2fa", response_model=Generate2FAResponse)
def generate_2fa():
    try:
        hex_seed = _read_hex_seed()
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")

    code = generate_totp_code(hex_seed)
    valid_for = seconds_remaining_in_period()
    return {"code": code, "valid_for": valid_for}


# ------------ Endpoint 3: POST /verify-2fa ------------

@app.post("/verify-2fa", response_model=VerifyResponse)
def verify_2fa(body: VerifyRequest):
    if not body.code:
        raise HTTPException(status_code=400, detail="Missing code")

    try:
        hex_seed = _read_hex_seed()
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")

    is_valid = verify_totp_code(hex_seed, body.code, valid_window=1)
    return {"valid": is_valid}

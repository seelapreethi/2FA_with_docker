# app/totp_utils.py

import base64
import time
import hashlib
import pyotp


def _hex_to_base32(hex_seed: str) -> str:
    raw_bytes = bytes.fromhex(hex_seed)
    b32_bytes = base64.b32encode(raw_bytes)
    return b32_bytes.decode("utf-8")


def generate_totp_code(hex_seed: str) -> str:
    """
    Generate current 6-digit TOTP code from hex seed.
    """
    base32_seed = _hex_to_base32(hex_seed)
    totp = pyotp.TOTP(
        base32_seed,
        digits=6,
        interval=30,
        digest=hashlib.sha1,
    )
    return totp.now()


def seconds_remaining_in_period(interval: int = 30) -> int:
    now = time.time()
    elapsed = int(now % interval)
    return interval - elapsed


def verify_totp_code(hex_seed: str, code: str, valid_window: int = 1) -> bool:
    base32_seed = _hex_to_base32(hex_seed)
    totp = pyotp.TOTP(
        base32_seed,
        digits=6,
        interval=30,
        digest=hashlib.sha1,
    )
    return totp.verify(code, valid_window=valid_window)

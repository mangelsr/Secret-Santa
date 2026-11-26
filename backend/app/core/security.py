import hashlib
import hmac
import os

PBKDF2_PREFIX = "pbkdf2_sha256"
PBKDF2_ALGORITHM = "sha256"
PBKDF2_ITERATIONS = 200_000
SALT_BYTES = 16


def hash_passcode(passcode: str) -> str:
    """Hash a passcode with PBKDF2-HMAC-SHA256 and a random 16-byte salt."""
    salt = os.urandom(SALT_BYTES)
    derived_key = hashlib.pbkdf2_hmac(
        PBKDF2_ALGORITHM,
        passcode.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    )
    return f"{PBKDF2_PREFIX}${PBKDF2_ITERATIONS}${salt.hex()}${derived_key.hex()}"


def verify_passcode(plain_passcode: str, stored_passcode: str) -> bool:
    """Verify a plaintext passcode against a PBKDF2 hash or legacy plaintext value."""
    if not plain_passcode or not stored_passcode:
        return False

    if stored_passcode.startswith(f"{PBKDF2_PREFIX}$"):
        parts = stored_passcode.split("$")
        if len(parts) != 4:
            return False
        _, iter_str, salt_hex, hash_hex = parts
        try:
            iterations = int(iter_str)
            salt = bytes.fromhex(salt_hex)
            expected_hash = bytes.fromhex(hash_hex)
        except ValueError:
            return False

        candidate_hash = hashlib.pbkdf2_hmac(
            PBKDF2_ALGORITHM,
            plain_passcode.encode("utf-8"),
            salt,
            iterations,
        )
        return hmac.compare_digest(candidate_hash, expected_hash)

    return hmac.compare_digest(plain_passcode, stored_passcode)

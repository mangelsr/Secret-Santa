from app.core.security import PBKDF2_PREFIX, hash_passcode, mask_email, verify_passcode


def test_hash_and_verify_passcode():
    hashed_a = hash_passcode("santa2026")
    hashed_b = hash_passcode("santa2026")

    assert hashed_a.startswith(f"{PBKDF2_PREFIX}$")
    assert hashed_a != hashed_b  # Unique random salt per hash
    assert verify_passcode("santa2026", hashed_a) is True
    assert verify_passcode("santa2026", hashed_b) is True
    assert verify_passcode("wrongpass", hashed_a) is False
    assert verify_passcode("", hashed_a) is False


def test_verify_legacy_plaintext_and_malformed_hash():
    assert verify_passcode("1234", "1234") is True
    assert verify_passcode("9999", "1234") is False
    assert verify_passcode("1234", f"{PBKDF2_PREFIX}$bad$format") is False
    assert verify_passcode("1234", f"{PBKDF2_PREFIX}$notint$aa$bb") is False


def test_mask_email():
    assert mask_email("carlos@example.com") == "ca***@example.com"
    assert mask_email("ab@example.com") == "a***@example.com"
    assert mask_email("a@b.co") == "a***@b.co"
    assert mask_email("invalid") == "***"


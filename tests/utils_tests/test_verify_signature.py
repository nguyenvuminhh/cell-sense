"""
Tests for signature verification utility.
"""

import base64
import json
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from server.utils.verify_signature import verify_signature

# Get the test assets directory
TEST_ASSETS_DIR = Path(__file__).parent.parent / "assets"
TEST_PRIVATE_KEY_PATH = TEST_ASSETS_DIR / "private.pem"
TEST_PUBLIC_KEY_PATH = TEST_ASSETS_DIR / "public.pem"


def _sign_payload(payload: dict, full_url: str) -> str:
    """Helper function to sign a payload using the test private key."""
    # Reconstruct the signed message exactly like GAS
    data = json.dumps(payload, separators=(",", ":")) + full_url

    # Load the private key
    with open(TEST_PRIVATE_KEY_PATH, "r") as key_file:
        private_key_pem = key_file.read()

    private_key = serialization.load_pem_private_key(
        private_key_pem.encode(), password=None
    )

    if not isinstance(private_key, rsa.RSAPrivateKey):
        raise TypeError(
            "Expected RSA private key, got: " + type(private_key).__name__
        )

    # Sign the data
    signature = private_key.sign(
        data.encode("utf-8"), padding.PKCS1v15(), hashes.SHA256()
    )

    # Return base64-encoded signature
    return base64.b64encode(signature).decode("utf-8")


def test_verify_signature_valid():
    """Test verifying a valid signature."""
    payload = {"message": "Hello World", "timestamp": 1234567890}
    full_url = "https://example.com/api/test"

    # Sign the payload
    signature = _sign_payload(payload, full_url)

    # Verify the signature
    result = verify_signature(payload, full_url, signature)

    assert result is True


def test_verify_signature_invalid_signature():
    """Test that an invalid signature fails verification."""
    payload = {"message": "Hello World", "timestamp": 1234567890}
    full_url = "https://example.com/api/test"

    # Create an invalid signature
    invalid_signature = base64.b64encode(b"invalid_signature_data").decode(
        "utf-8"
    )

    # Verify should fail
    result = verify_signature(payload, full_url, invalid_signature)

    assert result is False


def test_verify_signature_tampered_payload():
    """Test that tampering with the payload fails verification."""
    payload = {"message": "Hello World", "timestamp": 1234567890}
    full_url = "https://example.com/api/test"

    # Sign the original payload
    signature = _sign_payload(payload, full_url)

    # Tamper with the payload
    tampered_payload = {"message": "Goodbye World", "timestamp": 1234567890}

    # Verification should fail
    result = verify_signature(tampered_payload, full_url, signature)

    assert result is False


def test_verify_signature_tampered_url():
    """Test that tampering with the URL fails verification."""
    payload = {"message": "Hello World", "timestamp": 1234567890}
    full_url = "https://example.com/api/test"

    # Sign with original URL
    signature = _sign_payload(payload, full_url)

    # Try to verify with different URL
    tampered_url = "https://example.com/api/different"
    result = verify_signature(payload, tampered_url, signature)

    assert result is False


def test_verify_signature_complex_payload():
    """Test verification with a complex nested payload."""
    payload = {
        "user": {"id": 123, "name": "Test User", "roles": ["admin", "user"]},
        "data": {"items": [1, 2, 3], "metadata": {"version": "1.0"}},
        "timestamp": 1234567890,
    }
    full_url = "https://api.example.com/v1/users/123/data"

    signature = _sign_payload(payload, full_url)
    result = verify_signature(payload, full_url, signature)

    assert result is True


def test_verify_signature_empty_payload():
    """Test verification with an empty payload."""
    payload = {}
    full_url = "https://example.com/api/test"

    signature = _sign_payload(payload, full_url)
    result = verify_signature(payload, full_url, signature)

    assert result is True


def test_verify_signature_special_characters_in_url():
    """Test verification with special characters in URL."""
    payload = {"message": "Test", "id": 42}
    full_url = "https://example.com/api/test?param=value&other=123"

    signature = _sign_payload(payload, full_url)
    result = verify_signature(payload, full_url, signature)

    assert result is True


def test_verify_signature_unicode_in_payload():
    """Test verification with Unicode characters in payload."""
    payload = {
        "message": "Hello 世界 🌍",
        "text": "Émile Café",
        "timestamp": 1234567890,
    }
    full_url = "https://example.com/api/test"

    signature = _sign_payload(payload, full_url)
    result = verify_signature(payload, full_url, signature)

    assert result is True


def test_verify_signature_json_key_order_matters():
    """Test that JSON key order is preserved (using separators)."""
    # The verify_signature function uses json.dumps with separators=(",", ":")
    # which should produce consistent output
    payload = {"b": 2, "a": 1, "c": 3}
    full_url = "https://example.com/api/test"

    signature = _sign_payload(payload, full_url)
    result = verify_signature(payload, full_url, signature)

    assert result is True


def test_verify_signature_numeric_values():
    """Test verification with various numeric values."""
    payload = {
        "integer": 42,
        "float": 3.14159,
        "negative": -100,
        "zero": 0,
        "large": 9999999999,
    }
    full_url = "https://example.com/api/numbers"

    signature = _sign_payload(payload, full_url)
    result = verify_signature(payload, full_url, signature)

    assert result is True


def test_verify_signature_boolean_and_null():
    """Test verification with boolean and null values."""
    payload = {"is_active": True, "is_deleted": False, "optional": None}
    full_url = "https://example.com/api/test"

    signature = _sign_payload(payload, full_url)
    result = verify_signature(payload, full_url, signature)

    assert result is True


def test_verify_signature_malformed_base64():
    """Test that malformed base64 signature fails gracefully."""
    payload = {"message": "Test"}
    full_url = "https://example.com/api/test"

    # Use invalid base64 string
    invalid_signature = "not-valid-base64!@#$"
    try:
        result = verify_signature(payload, full_url, invalid_signature)
    except Exception:
        result = False

    assert result is False


def test_verify_signature_empty_signature():
    """Test that an empty signature fails verification."""
    payload = {"message": "Test"}
    full_url = "https://example.com/api/test"

    # Empty signature encoded as base64
    empty_signature = base64.b64encode(b"").decode("utf-8")

    result = verify_signature(payload, full_url, empty_signature)

    assert result is False


def test_verify_signature_url_with_fragment():
    """Test verification with URL containing fragment."""
    payload = {"data": "test"}
    full_url = "https://example.com/api/test#section"

    signature = _sign_payload(payload, full_url)
    result = verify_signature(payload, full_url, signature)

    assert result is True


def test_verify_signature_long_payload():
    """Test verification with a very long payload."""
    payload = {
        "data": "A" * 10000,  # Very long string
        "items": list(range(1000)),  # Large list
        "metadata": {"key_" + str(i): f"value_{i}" for i in range(100)},
    }
    full_url = "https://example.com/api/large"

    signature = _sign_payload(payload, full_url)
    result = verify_signature(payload, full_url, signature)

    assert result is True


def test_verify_signature_different_payload_same_signature():
    """Test that using the same signature for different payloads fails."""
    payload1 = {"message": "First message"}
    payload2 = {"message": "Second message"}
    full_url = "https://example.com/api/test"

    # Sign first payload
    signature = _sign_payload(payload1, full_url)

    # Try to verify second payload with first signature
    result = verify_signature(payload2, full_url, signature)

    assert result is False

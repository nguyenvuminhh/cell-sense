import base64
import json

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from server.config import SIGNATURE_PUBLIC_KEY_PATH
from server.models.exception_models import InternalServerError


def verify_signature(payload: dict, full_url: str, signature_b64: str) -> bool:
    # 1. Reconstruct signed message exactly like GAS
    data = json.dumps(payload, separators=(",", ":")) + full_url

    # 2. Load the public key
    if not SIGNATURE_PUBLIC_KEY_PATH:
        raise InternalServerError("SIGNATURE_PUBLIC_KEY_PATH is not set.")
    with open(SIGNATURE_PUBLIC_KEY_PATH, "r") as key_file:
        public_key_pem = key_file.read()

    public_key = serialization.load_pem_public_key(public_key_pem.encode())

    if not isinstance(public_key, rsa.RSAPublicKey):
        raise InternalServerError(
            "Expected RSA public key, got: " + type(public_key).__name__
        )

    # 3. Decode base64 signature
    signature = base64.b64decode(signature_b64)

    # 4. Verify RSA-SHA256 signature
    try:
        public_key.verify(
            signature,
            data.encode("utf-8"),
            padding.PKCS1v15(),
            hashes.SHA256(),
        )
        print("Signature is valid. Url:", full_url)
        return True
    except Exception:
        return False

"""
Security and AES-256 Encryption Helpers for MTIS.
Safely encrypts and decrypts tenant-specific API credentials using AES-256-GCM.
Plaintext API keys are never stored in databases, logs, or repositories.
"""
import os
import base64
import hashlib
from typing import Optional
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from app.config import settings


def _get_aes_key() -> bytes:
    """Derives a deterministic 256-bit (32-byte) key from APP_SECRET using SHA-256."""
    secret = (getattr(settings, "APP_SECRET", None) or os.getenv("APP_SECRET", "mtis-fallback-secret-key-32chars")).encode("utf-8")
    return hashlib.sha256(secret).digest()


def encrypt_api_key(plain_key: str) -> str:
    """
    Encrypts a plaintext API key with AES-256-GCM.
    Returns: base64-encoded string prefixed with 'enc_aes256:'
    """
    if not plain_key or not plain_key.strip():
        return ""
    key = _get_aes_key()
    aesgcm = AESGCM(key)
    # 96-bit (12-byte) unique random nonce
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plain_key.strip().encode("utf-8"), None)
    # Pack nonce + ciphertext
    payload = nonce + ciphertext
    b64_payload = base64.b64encode(payload).decode("utf-8")
    return f"enc_aes256:{b64_payload}"


def decrypt_api_key(encrypted_token: Optional[str]) -> Optional[str]:
    """
    Decrypts an AES-256-GCM encrypted API key.
    Returns decrypted plaintext key in memory. Never written to logs.
    """
    if not encrypted_token or not encrypted_token.strip():
        return None
    token = encrypted_token.strip()
    if token.startswith("enc_aes256:"):
        token = token[len("enc_aes256:"):]
    try:
        raw = base64.b64decode(token)
        if len(raw) < 12:
            return None
        nonce = raw[:12]
        ciphertext = raw[12:]
        key = _get_aes_key()
        aesgcm = AESGCM(key)
        decrypted = aesgcm.decrypt(nonce, ciphertext, None)
        return decrypted.decode("utf-8")
    except Exception:
        return None


def mask_api_key(key: Optional[str]) -> str:
    """
    Returns a masked preview safe for UI display: e.g. 'sk-...a1b2'.
    Never reveals the actual full secret.
    """
    if not key:
        return ""
    clean = key.strip()
    if clean.startswith("enc_aes256:"):
        decrypted = decrypt_api_key(clean)
        clean = decrypted or ""
    if not clean:
        return ""
    if len(clean) <= 8:
        return "sk-***"
    prefix = clean[:3] if clean.startswith("sk-") else clean[:2]
    suffix = clean[-4:]
    return f"{prefix}...{suffix}"

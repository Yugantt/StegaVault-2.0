"""AES-based message encryption applied before steganographic embedding.

The message is encrypted with a key derived from the user's password, so an
attacker who extracts the hidden bits still cannot read the message.
"""

import base64
import os

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

MARKER = "SVENC1:"
SALT_SIZE = 16
ITERATIONS = 480000


def _derive_key(password, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=ITERATIONS,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode("utf-8")))


def encrypt_message(message, password):
    """Return the encrypted message, prefixed with a marker."""
    salt = os.urandom(SALT_SIZE)
    token = Fernet(_derive_key(password, salt)).encrypt(message.encode("utf-8"))
    return MARKER + base64.urlsafe_b64encode(salt + token).decode("ascii")


def is_encrypted(message):
    return isinstance(message, str) and message.startswith(MARKER)


def decrypt_message(message, password):
    """Reverse encrypt_message. Raises ValueError on a wrong password."""
    if not is_encrypted(message):
        return message

    try:
        raw = base64.urlsafe_b64decode(message[len(MARKER):])
    except Exception:
        raise ValueError("The hidden data is damaged and cannot be decrypted.")

    salt, token = raw[:SALT_SIZE], raw[SALT_SIZE:]

    try:
        plain = Fernet(_derive_key(password, salt)).decrypt(token)
    except InvalidToken:
        raise ValueError("Wrong password. The message could not be decrypted.")

    return plain.decode("utf-8")

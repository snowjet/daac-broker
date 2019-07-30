import passgen
import hashlib
import binascii
import os
import secrets

from app.core.log import logger


def generate_session_secret(num_bytes=32):
    """Generate a 32 hex string"""

    logger.debug("Generate a 32 hex string")
    return secrets.token_hex(num_bytes)


def generate_password():
    """Generate a password."""

    logger.debug("Generate a password")
    return passgen.passgen(length=32)


def hash_password(password):
    """Hash a password for storing"""

    logger.debug("Hash a password for storing")
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode("ascii")
    pwdhash = hashlib.pbkdf2_hmac("sha512", password.encode("utf-8"), salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode("ascii")


def verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by user"""

    logger.debug("Verify a stored password against one provided by user")
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac(
        "sha512", provided_password.encode("utf-8"), salt.encode("ascii"), 100000
    )
    pwdhash = binascii.hexlify(pwdhash).decode("ascii")
    return pwdhash == stored_password

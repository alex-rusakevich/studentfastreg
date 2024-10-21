# https://gist.github.com/tscholl2/dc7dc15dc132ea70a98e8542fefffa28

import hashlib
import os
from binascii import hexlify, unhexlify
from typing import Union

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def deriveKey(passphrase: str, salt: bytes = None) -> Union[str, bytes]:
    if salt is None:
        salt = os.urandom(16)

    return hashlib.pbkdf2_hmac("sha256", passphrase.encode("utf8"), salt, 600000), salt


def encrypt(plaintext: str, passphrase: str) -> str:
    key, salt = deriveKey(passphrase)
    aes = AESGCM(key)
    iv = os.urandom(12)
    plaintext = plaintext.encode("utf8")
    ciphertext = aes.encrypt(iv, plaintext, None)
    return "%s-%s-%s" % (
        hexlify(salt).decode("utf8"),
        hexlify(iv).decode("utf8"),
        hexlify(ciphertext).decode("utf8"),
    )


def decrypt(ciphertext: str, passphrase: str) -> str:
    salt, iv, ciphertext = map(unhexlify, ciphertext.split("-"))
    key, _ = deriveKey(passphrase, salt)
    aes = AESGCM(key)
    plaintext = aes.decrypt(iv, ciphertext, None)
    return plaintext.decode("utf8")

import base64
import hashlib
import json
import subprocess

AES_BLOCK_SIZE = 16


def _openssl_crypt(data: bytes, key_hex: str, iv_hex: str, decrypt: bool) -> bytes:
    command = [
        "openssl",
        "enc",
        "-aes-256-cbc",
        "-K",
        key_hex,
        "-iv",
        iv_hex,
    ]
    if decrypt:
        command.insert(2, "-d")

    result = subprocess.run(
        command,
        input=data,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return result.stdout


def decrypt_feishu_payload(encrypt_key: str, encrypted: str) -> dict:
    raw = base64.b64decode(encrypted)
    iv = raw[:AES_BLOCK_SIZE]
    ciphertext = raw[AES_BLOCK_SIZE:]
    key = hashlib.sha256(encrypt_key.encode("utf-8")).digest()
    decrypted = _openssl_crypt(ciphertext, key.hex(), iv.hex(), decrypt=True)
    body = decrypted.decode("utf-8")
    return json.loads(body)

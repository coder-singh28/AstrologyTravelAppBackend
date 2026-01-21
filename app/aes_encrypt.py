"""
AES-256-CBC Encryption/Decryption Module
Provides encryption and decryption utilities for sensitive data using AES-256 in CBC mode.
WARNING: Hardcoded credentials below should be moved to environment variables.
"""

from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES
import base64
import json
import os

# Configuration constants (TODO: Move to environment variables)
REQ_ENC_DEC_SALT_LENGTH = 10
REQ_ENC_DEC_PASS_PHRASE_LENGTH = 5
REQ_ENC_DEC_IV_LENGTH = 16

# Hardcoded credentials (SECURITY RISK - move to .env)
ENCRYPTION_SALT = "2da43c30d136618c9d88"
ENCRYPTION_IV = "930b9760ce9fec3f4b18fec88258e313"
ENCRYPTION_PASS_PHRASE = "9486900ed0"


def generate_random_hex(length: int) -> str:
    """
    Generate random hexadecimal string of specified byte length.
    
    Args:
        length (int): Number of bytes to generate (function creates 2x chars)
    
    Returns:
        str: Hexadecimal representation of random bytes
    """
    random_bytes = os.urandom(length // 2)
    return random_bytes.hex()


def generate_salt() -> str:
    """
    Generate random salt for key derivation.
    
    Returns:
        str: Hexadecimal salt string
    """
    return generate_random_hex(REQ_ENC_DEC_SALT_LENGTH)


def generate_iv_and_pass_phrase() -> tuple:
    """
    Generate random initialization vector and passphrase.
    
    Returns:
        tuple: (pass_phrase: str, iv: str) both as hex strings
    """
    pass_phrase = generate_random_hex(REQ_ENC_DEC_PASS_PHRASE_LENGTH)
    iv = generate_random_hex(REQ_ENC_DEC_IV_LENGTH)
    return pass_phrase, iv


def generate_key(salt: str, pass_phrase: str) -> bytes:
    """
    Derive AES-256 encryption key from salt and passphrase using PBKDF2.
    
    Args:
        salt (str): Hexadecimal salt string
        pass_phrase (str): Password/passphrase
    
    Returns:
        bytes: 32-byte AES-256 key
    """
    key = PBKDF2(
        pass_phrase.encode(),
        bytes.fromhex(salt),
        dkLen=32,
        count=1000
    )
    return key


def encrypt(
    data,
    salt: str = ENCRYPTION_SALT,
    iv_key: str = ENCRYPTION_IV,
    pass_phrase: str = ENCRYPTION_PASS_PHRASE
) -> str:
    """
    Encrypt data using AES-256-CBC.
    
    Args:
        data: Dictionary, list, or string to encrypt
        salt (str): Hexadecimal salt for key derivation
        iv_key (str): Hexadecimal initialization vector (32 chars = 16 bytes)
        pass_phrase (str): Passphrase for key derivation
    
    Returns:
        str: Base64-encoded ciphertext
    """
    # Convert JSON data to string if needed
    if isinstance(data, (dict, list)):
        data = json.dumps(data, separators=(",", ":"))
    
    # Generate encryption key
    key = generate_key(salt, pass_phrase)
    
    # Create cipher in CBC mode
    cipher = AES.new(
        key,
        AES.MODE_CBC,
        bytes.fromhex(iv_key)
    )
    
    # Encrypt with PKCS7 padding
    ciphertext = cipher.encrypt(
        pad(data.encode("utf-8"), AES.block_size)
    )
    
    # Encode to Base64 for transmission
    return base64.b64encode(ciphertext).decode("utf-8")


def decrypt_string(
    data: str,
    salt: str = ENCRYPTION_SALT,
    iv_key: str = ENCRYPTION_IV,
    pass_phrase: str = ENCRYPTION_PASS_PHRASE
) -> str:
    """
    Decrypt Base64-encoded AES-256-CBC ciphertext.
    
    Args:
        data (str): Base64-encoded ciphertext
        salt (str): Hexadecimal salt for key derivation
        iv_key (str): Hexadecimal initialization vector
        pass_phrase (str): Passphrase for key derivation
    
    Returns:
        str: Decrypted plaintext (returns input on error)
    """
    try:
        # Generate decryption key
        key = generate_key(salt, pass_phrase)
        
        # Create cipher in CBC mode
        cipher = AES.new(key, AES.MODE_CBC, bytes.fromhex(iv_key))
        
        # Decode from Base64
        ciphertext = base64.b64decode(data)
        
        # Decrypt and remove PKCS7 padding
        decrypted_data = unpad(
            cipher.decrypt(ciphertext),
            AES.block_size
        ).decode("utf-8")
    
    except Exception as e:
        # Return original data if decryption fails
        decrypted_data = data
    
    return decrypted_data


def json_string(text: str) -> dict:
    """
    Parse JSON string to dictionary.
    
    Args:
        text (str): JSON string
    
    Returns:
        dict: Parsed JSON object
    """
    return json.loads(text)


def decrypt(
    data: str,
    salt: str = ENCRYPTION_SALT,
    iv_key: str = ENCRYPTION_IV,
    pass_phrase: str = ENCRYPTION_PASS_PHRASE
) -> dict:
    """
    Decrypt AES-256-CBC encrypted data and parse as JSON.
    
    Args:
        data (str): Base64-encoded ciphertext
        salt (str): Hexadecimal salt for key derivation
        iv_key (str): Hexadecimal initialization vector
        pass_phrase (str): Passphrase for key derivation
    
    Returns:
        dict: Decrypted and parsed JSON object
    """
    dec_data = decrypt_string(data, salt, iv_key, pass_phrase)
    return json_string(dec_data)


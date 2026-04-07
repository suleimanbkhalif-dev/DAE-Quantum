import os
import sys
import time
import requests
import subprocess
import platform
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

sound_file = "success.mp3"  # Place your MP3 in the same folder as this script

def play_sound(file_path):
    try:
        system = platform.system()
        if system == "Darwin":  # macOS
            subprocess.run(["afplay", file_path])
        elif system == "Windows":
            subprocess.run(["powershell", "-c", f"(New-Object Media.SoundPlayer '{file_path}').PlaySync();"])
        else:  # Linux
            subprocess.run(["mpg123", file_path])
    except Exception as e:
        print(f"[!] Could not play sound: {e}")

def loading_bar(progress, total, bar_length=30):
    filled = int(bar_length * progress // total)
    bar = '█' * filled + '░' * (bar_length - filled)
    percent = int(100 * progress / total)
    print(f'\r[{bar}] {percent}%', end='', flush=True)
    if progress == total:
        print(' Done')

def get_quantum_random_bytes(num_bytes=16):
    api_key = os.getenv("ANU_API_KEY")
    if not api_key:
        raise ValueError("ANU_API_KEY not set. Use export ANU_API_KEY='your_key_here'")
    try:
        url = "https://qrng.anu.edu.au/API/jsonI.php"
        params = {"length": num_bytes, "type": "uint8", "size": 1}
        headers = {"x-api-key": api_key}
        response = requests.get(url, params=params, headers=headers, timeout=5)
        data = response.json()
        if data.get("success", False):
            return bytes(data["data"])
        else:
            raise Exception("API returned failure")
    except Exception:
        return os.urandom(num_bytes)

def derive_key(password, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=200000
    )
    return kdf.derive(password.encode())

def encrypt(plaintext, password):
    total_steps = 100
    progress = 0
    loading_bar(progress, total_steps)

    salt = get_quantum_random_bytes(16)
    progress += 30
    loading_bar(progress, total_steps)
    time.sleep(0.5)

    key = derive_key(password, salt)
    progress += 30
    loading_bar(progress, total_steps)
    time.sleep(0.5)

    nonce = os.urandom(12)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), None)
    for i in range(10):
        progress += 1
        loading_bar(progress, total_steps)
        time.sleep(0.05)

    progress = total_steps
    loading_bar(progress, total_steps)

    # Play success sound after encryption is done
    play_sound(sound_file)

    return f"{salt.hex()}|{nonce.hex()}|{ciphertext.hex()}"

def decrypt(data, password):
    try:
        salt_hex, nonce_hex, ciphertext_hex = data.split("|")
    except ValueError:
        return "Error: Invalid input format"

    total_steps = 100
    progress = 0
    loading_bar(progress, total_steps)

    salt = bytes.fromhex(salt_hex)
    nonce = bytes.fromhex(nonce_hex)
    ciphertext = bytes.fromhex(ciphertext_hex)

    key = derive_key(password, salt)
    progress += 50
    loading_bar(progress, total_steps)
    time.sleep(0.5)

    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    for i in range(49):
        progress += 1
        loading_bar(progress, total_steps)
        time.sleep(0.02)

    progress = total_steps
    loading_bar(progress, total_steps)
    return plaintext.decode()

def main():
    print("Quantum-Enhanced Encryption (AES-256-GCM)")
    print("Commands:")
    print("  encrypt: (text)")
    print("  decrypt: (data)")
    print("  quit")
    print("-" * 50)

    while True:
        user_input = input("\n> ").strip()
        if user_input.lower() == "quit":
            print("Goodbye!")
            break
        elif user_input.lower().startswith("encrypt:"):
            text = user_input[8:].strip()
            if not text:
                print("Error: No text provided")
                continue
            password = input("Password: ")
            print("Encrypting...")
            result = encrypt(text, password)
            print(f"\nEncrypted:\n{result}\n")
        elif user_input.lower().startswith("decrypt:"):
            data = user_input[8:].strip()
            if not data:
                print("Error: No data provided")
                continue
            password = input("Password: ")
            print("Decrypting...")
            result = decrypt(data, password)
            print(f"\nDecrypted:\n{result}\n")
        else:
            print("Unknown command")

if __name__ == "__main__":
    main()
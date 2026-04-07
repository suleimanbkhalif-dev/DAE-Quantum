from qiskit import QuantumCircuit
from qiskit_aer import Aer
from qiskit import transpile
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import re
import sys

def loading_bar(progress, total, bar_length=30):
    filled = int(bar_length * progress // total)
    bar = '█' * filled + '░' * (bar_length - filled)
    percent = int(100 * progress / total)
    print(f'\r[{bar}] {percent}%', end='', flush=True)
    if progress == total:
        print(' Done')

def quantum_random_bit():
    qc = QuantumCircuit(1, 1)
    qc.h(0)
    qc.measure(0, 0)
    backend = Aer.get_backend('qasm_simulator')
    transpiled_circuit = transpile(qc, backend)
    job = backend.run(transpiled_circuit, shots=1)
    result = job.result()
    counts = result.get_counts()
    return int(list(counts.keys())[0])

def quantum_generate_random_bytes(num_bytes, progress_tracker=None):
    bytes_result = bytearray()
    for byte_idx in range(num_bytes):
        byte_val = 0
        for bit_pos in range(8):
            byte_val = (byte_val << 1) | quantum_random_bit()
        bytes_result.append(byte_val)
        if progress_tracker:
            progress_tracker(byte_idx + 1, num_bytes)
    return bytes(bytes_result)

def hybrid_encrypt(plaintext):
    total_steps = 32 + 16 + 64 + 32
    current_step = 0
    
    print("Encrypting...")
    
    aes_key = quantum_generate_random_bytes(32, lambda x, y: loading_bar(current_step + x, total_steps))
    current_step += 32
    
    iv = quantum_generate_random_bytes(16, lambda x, y: loading_bar(current_step + x, total_steps))
    current_step += 16
    
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(plaintext.encode()) + padder.finalize()
    
    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    aes_ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    
    aes_key_hex = aes_key.hex()
    
    quantum_obfuscated_key = []
    for idx, char in enumerate(aes_key_hex):
        if quantum_random_bit() == 0:
            quantum_obfuscated_key.append(char.lower())
        else:
            quantum_obfuscated_key.append(char.upper())
        loading_bar(current_step + idx + 1, total_steps)
    current_step += len(aes_key_hex)
    
    iv_hex = iv.hex()
    hidden_iv = []
    for idx, char in enumerate(iv_hex):
        if quantum_random_bit() == 0:
            hidden_iv.append(char.lower())
        else:
            hidden_iv.append(char.upper())
        loading_bar(current_step + idx + 1, total_steps)
    
    result = {
        'encrypted_key': ''.join(quantum_obfuscated_key),
        'iv': ''.join(hidden_iv),
        'ciphertext': aes_ciphertext.hex()
    }
    
    print()
    return result

def hybrid_decrypt(encrypted_key, iv_string, ciphertext_hex):
    print("Decrypting...")
    
    total_steps = len(encrypted_key) + len(iv_string)
    current_step = 0
    
    aes_key_hex_chars = []
    for char in encrypted_key:
        loading_bar(current_step + 1, total_steps)
        current_step += 1
        aes_key_hex_chars.append(char.lower())
    
    aes_key_hex = ''.join(aes_key_hex_chars)
    
    try:
        aes_key = bytes.fromhex(aes_key_hex)
        if len(aes_key) != 32:
            return f"Error: Invalid AES key length. Got {len(aes_key)} bytes, expected 32"
    except Exception as e:
        return f"Error: Failed to decode AES key - {str(e)}"
    
    iv_hex_chars = []
    for char in iv_string:
        loading_bar(current_step + 1, total_steps)
        current_step += 1
        iv_hex_chars.append(char.lower())
    
    iv_hex = ''.join(iv_hex_chars)
    
    try:
        iv = bytes.fromhex(iv_hex)
        if len(iv) != 16:
            return f"Error: Invalid IV length. Got {len(iv)} bytes, expected 16"
    except Exception as e:
        return f"Error: Failed to decode IV - {str(e)}"
    
    print()
    
    try:
        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_padded = decryptor.update(bytes.fromhex(ciphertext_hex)) + decryptor.finalize()
        
        unpadder = padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(decrypted_padded) + unpadder.finalize()
        
        return plaintext.decode()
    except Exception as e:
        return f"Decryption failed: {str(e)}"

def encrypt_command(text):
    result = hybrid_encrypt(text)
    return f"{result['encrypted_key']}|{result['iv']}|{result['ciphertext']}"

def decrypt_command(cipher_text):
    parts = cipher_text.split('|')
    if len(parts) == 3:
        encrypted_key, iv, ciphertext = parts
        return hybrid_decrypt(encrypted_key, iv, ciphertext)
    else:
        return "Error: Invalid cipher format"

if __name__ == "__main__":
    print("Quantum Hybrid Encryption System (AES-256 + Quantum)")
    print("Commands:")
    print("  encrypt: (text) - Encrypts the given text")
    print("  decrypt: (cipher) - Decrypts the given cipher")
    print("  quit - Exit the program")
    print("-" * 50)
    
    while True:
        user_input = input("\n> ").strip()
        
        if user_input.lower() == 'quit':
            print("Goodbye!")
            break
        
        if user_input.lower().startswith('encrypt:'):
            text = user_input[8:].strip()
            if not text:
                print("Error: No text to encrypt")
                continue
            
            encrypted = encrypt_command(text)
            print(f"\nEncrypted: {encrypted}\n")
        
        elif user_input.lower().startswith('decrypt:'):
            cipher = user_input[8:].strip()
            if not cipher:
                print("Error: No cipher to decrypt")
                continue
            
            decrypted = decrypt_command(cipher)
            print(f"\nDecrypted: {decrypted}\n")
        
        else:
            print("Error: Unknown command. Use 'encrypt:', 'decrypt:', or 'quit'")
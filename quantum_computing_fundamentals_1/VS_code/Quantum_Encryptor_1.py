enfrom qiskit import QuantumCircuit
from qiskit_aer import Aer
from qiskit import transpile
import re

def a1z26(text):
    return [ord(ch.upper()) - ord('A') + 1 for ch in text if ch.isalpha()]

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

def encrypt_letter(plain_letter):
    target_letter = plain_letter.upper()
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    
    count_target = 0
    for _ in alphabet:
        if quantum_random_bit() == 0:
            count_target += 1
    
    encrypted_num = count_target
    if encrypted_num == 0:
        encrypted_num = 26
    return encrypted_num

def encrypt_text(text):
    text = text.upper()
    plain_numbers = a1z26(text)
    encrypted_letters = []
    
    for ch in text:
        if ch.isalpha():
            enc_num = encrypt_letter(ch)
            enc_letter = chr(enc_num + ord('A') - 1)
            encrypted_letters.append(enc_letter)
        else:
            encrypted_letters.append(ch)
    
    result_parts = []
    for i, num in enumerate(plain_numbers):
        result_parts.append(str(num))
        result_parts.append(encrypted_letters[i])
    
    return ''.join(result_parts)

def decrypt_text(hybrid_cipher):
    pairs = re.findall(r'(\d+)([A-Z])', hybrid_cipher)
    
    decrypted = []
    for num_str, _ in pairs:
        original_num = int(num_str)
        original_letter = chr(original_num + ord('A') - 1)
        decrypted.append(original_letter)
    
    return ''.join(decrypted)

if __name__ == "__main__":
    print("Quantum Encryption/Decryption System")
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
            
            print(f"\nOriginal: {text}")
            cipher = encrypt_text(text)
            print(f"Encrypted: {cipher}")
        
        elif user_input.lower().startswith('decrypt:'):
            cipher = user_input[8:].strip()
            if not cipher:
                print("Error: No cipher to decrypt")
                continue
            
            if not re.match(r'^[\dA-Z]+$', cipher):
                print("Error: Invalid cipher format. Should contain only numbers and letters.")
                continue
            
            try:
                decrypted = decrypt_text(cipher)
                print(f"Decrypted: {decrypted}")
            except Exception as e:
                print(f"Error during decryption: {e}")
        
        else:
            print("Error: Unknown command. Use 'encrypt:', 'decrypt:', or 'quit'")
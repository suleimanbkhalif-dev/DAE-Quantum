from qiskit import QuantumCircuit
from qiskit_aer import Aer
from qiskit import transpile
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

def encrypt_text(text):
    text_upper = text.upper()
    result = []
    letters = [c for c in text_upper if c.isalpha()]
    total_ops = len(letters) * 26
    current_op = 0
    
    for ch in text_upper:
        if ch.isalpha():
            count_target = 0
            for _ in range(26):
                if quantum_random_bit() == 0:
                    count_target += 1
                current_op += 1
                loading_bar(current_op, total_ops)
            
            if count_target == 0:
                count_target = 26
            
            encrypted_letter = chr(count_target + ord('A') - 1)
            
            original_num = ord(ch) - ord('A') + 1
            binary = format(original_num, '05b')
            
            case_result = []
            for bit in binary:
                if bit == '0':
                    case_result.append(encrypted_letter.lower())
                else:
                    case_result.append(encrypted_letter.upper())
            
            result.append(''.join(case_result))
        else:
            result.append(ch)
    
    print()
    return ''.join(result)

def decrypt_text(cipher_text):
    print("Decrypting...")
    result = []
    letters_only = [c for c in cipher_text if c.isalpha()]
    total_letters = len(letters_only) // 5
    current = 0
    
    temp_binary = ''
    letter_count = 0
    
    for ch in cipher_text:
        if ch.isalpha():
            if ch.islower():
                temp_binary += '0'
            else:
                temp_binary += '1'
            
            if len(temp_binary) == 5:
                num = int(temp_binary, 2)
                if 1 <= num <= 26:
                    result.append(chr(num + ord('A') - 1))
                temp_binary = ''
                letter_count += 1
                loading_bar(letter_count, total_letters)
        else:
            if temp_binary:
                while len(temp_binary) < 5:
                    temp_binary += '0'
                num = int(temp_binary, 2)
                if 1 <= num <= 26:
                    result.append(chr(num + ord('A') - 1))
                temp_binary = ''
            result.append(ch)
    
    if temp_binary:
        while len(temp_binary) < 5:
            temp_binary += '0'
        num = int(temp_binary, 2)
        if 1 <= num <= 26:
            result.append(chr(num + ord('A') - 1))
    
    print()
    return ''.join(result)

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
            print("Encrypting...")
            encrypted = encrypt_text(text)
            print(f"Encrypted: {encrypted}\n")
        
        elif user_input.lower().startswith('decrypt:'):
            cipher = user_input[8:].strip()
            if not cipher:
                print("Error: No cipher to decrypt")
                continue
            
            decrypted = decrypt_text(cipher)
            print(f"Decrypted: {decrypted}\n")
        
        else:
            print("Error: Unknown command. Use 'encrypt:', 'decrypt:', or 'quit'")
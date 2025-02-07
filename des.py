# @title
import os
import sys
from pathlib import Path
from Crypto.Cipher import AES

def unpad_data(data):
    pad_len = data[-1]
    return data[:-pad_len]

def decrypt_file(encrypted_file, key):
    encrypted_file = str(encrypted_file)
    original_file = encrypted_file.replace('.encrypt', '')

    try:
        with open(encrypted_file, 'rb') as f:
            iv = f.read(16)  # Baca IV
            ciphertext = f.read()

        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted_data = unpad_data(cipher.decrypt(ciphertext))

        with open(original_file, 'wb') as f:
            f.write(decrypted_data)

        os.remove(encrypted_file)  # Hapus file terenkripsi setelah dekripsi
        print(f"Berhasil mendekripsi: {encrypted_file} -> {original_file}")
    except Exception as e:
        print(f"Gagal mendekripsi {encrypted_file}: {e}")

def main():
    directory = input("Masukkan path direktori yang ingin didekripsi: ")
    if not os.path.exists(directory) or not os.path.isdir(directory):
        print("Path tidak valid atau bukan direktori.")
        return

    key_file = 'encryption_key_256.bin'
    if not os.path.exists(key_file):
        print("File kunci tidak ditemukan. Tidak bisa mendekripsi.")
        return

    with open(key_file, 'rb') as f:
        key_hex = f.read().decode('utf-8')
        key = bytes.fromhex(key_hex)

    for item in Path(directory).rglob("*.encrypt"):
        decrypt_file(item, key)

if __name__ == "__main__":
    main()
import os
import hashlib
from cryptography.fernet import Fernet

ZIPFILEDIRPATH = os.path.abspath("ZipFiles")
KEYFILEPATH = os.path.abspath("key.txt")
FILECACHEDIRPATH = os.path.abspath("FileCache")
def return_encrypted(text: bytes, key: bytes) -> bytes:
    fernet = Fernet(key)
    return fernet.encrypt(text)


def return_decrypted(text: bytes, key: bytes) -> bytes:
    fernet = Fernet(key)
    return fernet.decrypt(text)


# encrypts file with provided filename and (optional) keypath, places it in encrypted_file_location
def master_encrypt(filename, key: bytes, encypted_file_location=FILECACHEDIRPATH) -> str:
    global KEYFILEPATH
    global ZIPFILEDIRPATH
    global FILECACHEDIRPATH

    print()
    print("---------------------------------")
    print("(1/3) STARTING ENCRYPTION...")

    if not os.path.exists(filename):
        filename = os.path.join(ZIPFILEDIRPATH, filename)
        if not os.path.exists(filename):
            raise Exception("!File not found")

    basename = os.path.basename(filename)
    print(f"(2/3) TARGET FILE {basename} FOUND...")
    filelocation = os.path.join(encypted_file_location, basename)

    with open(filename, "rb") as f, open(filelocation, "wb") as fout:
        fout.write(return_encrypted(f.read(), key))
    print("(3/3) ENCRYPTION FINISHED")
    print("---------------------------------")

    return filelocation


def master_decrypt(filename, key: bytes, decrypted_file_location=ZIPFILEDIRPATH) -> str:
    global KEYFILEPATH
    global ZIPFILEDIRPATH
    global FILECACHEDIRPATH

    print()
    print("---------------------------------")
    print("(1/3) STARTING DECRYPTION...")

    if not os.path.exists(filename):
        filename = os.path.join(FILECACHEDIRPATH, filename)
        if not os.path.exists(filename):
            raise Exception("!File not found")

    basename = os.path.basename(filename)
    print(f"(2/3) TARGET FILE {basename} FOUND...")
    filelocation = os.path.join(decrypted_file_location, basename)

    with open(filename, "rb") as f, open(filelocation, "wb") as fout:
        fout.write(return_decrypted(f.read(), key))
    print("(3/3) DECRYPTION FINISHED!")

    return filelocation


# reads key from specified filepath,
# if not found, searches in KEYFILEPATH
# if still not found, raises exception
def return_key_from_file(keypath=KEYFILEPATH) -> bytes:
    with open(keypath, 'rb') as f:
        return f.read()


# returns the SHA256 hash of a file
# if file not found, searches inside FILECACHEDIRPATH,
# if still not found, raises exception
def return_hash_of_file(filepath: os.path, dirpath=FILECACHEDIRPATH) -> str:
    if not os.path.exists(filepath):
        filepath = os.path.join(dirpath, filepath)
        if not os.path.exists(filepath):
            raise Exception("!File not found")

    with open(filepath, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def return_hash_of_str(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def return_hash_of_bytes(text: bytes) -> str:
    return hashlib.sha256(text).hexdigest()

from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

def encrypt(password, decryptedtext, salt, iv):
    key = PBKDF2(bytes(password,'utf-8'), bytes(salt,'utf-8'))
    data=decryptedtext.encode('utf-8')
    data_padded = pad(data,16)
    aes = AES.new(key, AES.MODE_CBC, iv)
    encrypted = aes.encrypt(data_padded)
    return encrypted

def decrypt(password, encrypted, salt, iv):
    key = PBKDF2(bytes(password,'utf-8'), bytes(salt,'utf-8'))
    data_padded = encrypted
    aes = AES.new(key, AES.MODE_CBC, iv)
    decrypted = aes.decrypt(data_padded)
    return unpad(decrypted,16).decode('utf-8')

def generate_iv():
    return get_random_bytes(16)
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from base64 import b64encode, b64decode
import json

def aes_encrypt(key, plaintext):
    # 使用PKCS7填充
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(plaintext.encode('utf-8')) + padder.finalize()

    # 创建AES加密器
    cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
    encryptor = cipher.encryptor()

    # 加密数据
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    # 返回Base64编码的密文
    return b64encode(ciphertext).decode('utf-8')

def aes_decrypt(key, ciphertext):
    # 解码Base64
    ciphertext = b64decode(ciphertext)

    # 创建AES解密器
    cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
    decryptor = cipher.decryptor()

    # 解密数据
    decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()

    # 使用PKCS7反向填充
    unpadder = padding.PKCS7(128).unpadder()
    unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()

    # 返回解密后的明文
    return unpadded_data.decode('utf-8')

# 128位的AES密钥（16字节），这里使用字节类型
# key = b'sixteen_byte_key'
key = b'ux8wsa448ze7if3h'
plaintext = 'heima290'

# 加密
encrypted_text = aes_encrypt(key, plaintext)
print(f'Encrypted Text: {encrypted_text}')

# 解密
decrypted_text = aes_decrypt(key, encrypted_text)
print(f'Decrypted Text: {decrypted_text}')
#
decrypted_text2 = aes_decrypt(key, 'x6WKCfdYmKunqzw/X+Y2Gg==')
print(f'Decrypted Text: {decrypted_text2}')
#
# print(float(aes_decrypt(key, str('OHdB2Vrw2ybADeBW4SUY2w=='))))


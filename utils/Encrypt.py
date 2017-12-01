# -*- coding:utf-8 -*-
import binascii
from Crypto.Cipher import AES   # from https://github.com/Legrandin/pycryptodome
# https://github.com/zrong/blog/blob/8c413bade8732d804517b884bf74e15c11dcdb1f/source/_posts/2655.md
class Encrypt:

    @staticmethod
    def encrypt(key, plain_text):
        mod = len(plain_text) % 16
        if mod > 0:
            # 补齐16的倍数
            zero = '\0' * (16 - mod)
            plain_text += zero
        aes = AES.new(key.encode(), AES.MODE_ECB)
        cipher_text = binascii.hexlify(aes.encrypt(plain_text.encode('utf-8'))).decode()
        return cipher_text

    @staticmethod
    def decrypt(key, cipher_text):
        aes = AES.new(key.encode(), AES.MODE_ECB)
        plain_text = aes.decrypt(binascii.unhexlify(cipher_text)).decode('utf-8').rstrip('\0')
        return plain_text

if __name__ == '__main__':
    key = "dfhelo2017!dfdfd"
    content = "123456ddfr%%"
    print('加密前：%s' % content)
    encStr = Encrypt.encrypt(key, content)
    print('加密后：%s' % encStr)
    print('解密后：%s' % Encrypt.decrypt(key, encStr))

import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


class AESCipher:
    def __init__(self, _key):
        self.key = _key

    def encrypt(self, _plaintext):
        _cipher = AES.new(self.key.encode(), AES.MODE_CBC)
        _plaintext = pad(_plaintext.encode(), AES.block_size)
        _encrypted_text = _cipher.iv + _cipher.encrypt(_plaintext)
        return base64.b64encode(_encrypted_text).decode()[:128]

    def decrypt(self, ciphertext):
        ciphertext = base64.b64decode(ciphertext)
        iv = ciphertext[:AES.block_size]
        _cipher = AES.new(self.key.encode(), AES.MODE_CBC, iv)
        _decrypted_text = unpad(_cipher.decrypt(ciphertext[AES.block_size:]), AES.block_size)
        return _decrypted_text.decode()


class Server:
    key_type = {
        'uptime': [int],
        'system': [str],
        'cpu_cores': [int],
        'cpu': [int, float],  # CPU 使用率
        'cpu_model': [str],
        'load_1': [int, float, str],
        'load_5': [int, float, str],
        'load_15': [int, float, str],
        'memory_total': [int],
        'memory_used': [int],
        'swap_total': [int],
        'swap_used': [int],
        'hdd_total': [int],
        'hdd_used': [int],
        'network_in': [str],
        'network_out': [str],
        'process': [int],
        'thread': [int],
        'tcp': [int],
        'udp': [int],
        'interval': [int],
    }

    def __init__(self, data):
        self.data = data

    def check_data(self):
        # 缺少字段，直接不合规
        for k in self.key_type.keys():
            if k not in self.data.keys():
                return False, f'Missing field: {k}'
            key_type = type(self.data.get(k))
            need_type = self.key_type[k]
            if key_type not in need_type:
                return False, f'Invalid field: {k}:{key_type}, need {str(need_type)}'
        return True, ''


if __name__ == '__main__':
    import uuid

    # 示例用法
    secret_key = str(uuid.uuid4()).replace('-', '')[:32]  # 生成32字节的随机密钥
    print(secret_key)
    cipher = AESCipher(secret_key)

    plaintext = "1::ssssssssssssssss::https://tendcode.com/monitor/push"
    encrypted_text = cipher.encrypt(plaintext)
    print("Encrypted:", encrypted_text)

    decrypted_text = cipher.decrypt(encrypted_text)
    print("Decrypted:", decrypted_text)

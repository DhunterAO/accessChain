from fastecdsa import keys, curve, ecdsa
from fastecdsa.point import Point
from hashlib import sha256
import logging
import json
import os

CURVE = curve.secp256k1
HASH_FUNC = sha256


class FastKey:
    def __init__(self, private_key=None):
        if private_key is None:
            self.private_key, self.public_key = keys.gen_keypair(CURVE)
        else:
            self.private_key = int(private_key, 16)
            self.public_key = keys.get_public_key(self.private_key, CURVE)

    def get_prikey(self):
        return hex(self.private_key)[2:].zfill(64)

    def get_pubkey(self):
        return from_pubkey_to_address(self.public_key)

    def sign_message(self, message):
        r, s = ecdsa.sign(message, self.private_key, CURVE, HASH_FUNC)
        # print(len(hex(r)), len(hex(s)))
        r = hex(r)[2:].zfill(64)
        s = hex(s)[2:].zfill(64)
        return r + s

    def valid(self):
        return self.public_key == keys.get_public_key(self.private_key, CURVE)

    def sign_obj(self, obj):
        m = obj.calc_hash()
        return self.sign_message(m)

    def to_json(self):
        key_json = {
            'public_key': self.get_pubkey(),
            'private_key': self.get_prikey()
        }
        return key_json

    def from_json(self, key_json):
        required = ['public_key', 'private_key']
        if not all(k in key_json for k in required):
            logging.warning(f'key.py line 45: value missing in {required}')
            return False

        if not isinstance(key_json['public_key'], str):
            logging.warning('key.py line 49: public_key should be type<str>')
            return False
        if not isinstance(key_json['private_key'], str):
            logging.warning('key.py line 52: private_key should be type<str>')
            return False

        self.public_key = from_address_to_pubkey(key_json["public_key"])
        self.private_key = int(key_json["private_key"], 16)
        return self.valid()

    def store_key(self, path='KeyFile', file='key.json'):
        if not os.path.exists(path):
            os.mkdir(path)
        key_file = os.path.join(path, file)
        with open(key_file, 'w') as store_file:
            store_file.write(json.dumps(self.to_json(), indent=4, separators=(',', ':')))
        return True

    def load_key(self, path='KeyFile', file='key.json'):
        if not os.path.exists(path):
            os.mkdir(path)
        key_file = os.path.join(path, file)
        with open(key_file, 'r') as load_file:
            account_json = load_file.read()
            self.from_json(json.loads(account_json))
        return True

    def __str__(self):
        return str(self.get_pubkey())


def from_pubkey_to_address(point):
    return hex(point.x)[2:].zfill(64) + hex(point.y)[2:].zfill(64)


def from_address_to_pubkey(address):
    x, y = address[:64], address[64:]
    x_int = int(x, 16)
    y_int = int(y, 16)
    return Point(x_int, y_int, CURVE)


def verify_signature(pubkey, message, signature):
    r = int(signature[:64], 16)
    s = int(signature[64:], 16)
    return ecdsa.verify((r, s), message, from_address_to_pubkey(pubkey), CURVE, HASH_FUNC)


# def base58CheckEncode(version, payload):
#     print(chr(version).encode('ascii', errors='replace'))
#     print(chr(version))
#     s = version.encode() + binascii.b2a_hex(payload)
#     print(s)
#     print(binascii.b2a_hex(payload))
#     checksum = hashlib.sha256(hashlib.sha256(s).digest()).digest()[0:4]
#     print(binascii.b2a_hex(checksum))
#
#
# sk = '0C28FCA386C7A227600B2FE50B7CAE11EC86D3BF1FBE471BE89827E19D72AA1D'
# print(base58CheckEncode(0x80, bytes.fromhex(sk)))

if __name__ == '__main__':
    m = 'hello'
    from util.constant import PK_list, key_list
    for i in range(len(key_list)):
        sk = key_list[i]
        # pk = PK_list[i]
        # print(len(sk), len(pk))
        key = FastKey(sk)
        print(key.get_pubkey())
        # sig = key.sign_message(m)
        # print(verify_signature(pk, m, sig))


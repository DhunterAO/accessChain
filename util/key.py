# import binascii
# import logging
# import ecdsa
# import json
# import os
#
#
# class Key:
#     def __init__(self, private_key=None):
#         if private_key is None:
#             self._private_key = ecdsa.SigningKey.generate()
#             self._public_key = self._private_key.get_verifying_key()
#         else:
#             self._private_key = ecdsa.SigningKey.from_string(binascii.unhexlify(private_key))
#             self._public_key = self._private_key.get_verifying_key()
#
#     def sign_message(self, message):
#         return self._private_key.sign(message.encode("utf-8")).hex()
#
#     def sign_obj(self, obj):
#         m = obj.calc_hash()
#         return self.sign_message(m)
#
#     def get_pubkey(self):
#         return self._public_key.to_string().hex()
#
#     def get_prikey(self):
#         return self._private_key.to_string().hex()
#
#     def valid(self):
#         return self._public_key.to_string() == self._private_key.get_verifying_key().to_string()
#
#     def to_json(self):
#         key_json = {
#             'public_key': self._public_key.to_string().hex(),
#             'private_key': self._private_key.to_string().hex()
#         }
#         return key_json
#
#     def from_json(self, key_json):
#         required = ['public_key', 'private_key']
#         if not all(k in key_json for k in required):
#             logging.warning(f'key.py line 45: value missing in {required}')
#             return False
#
#         if not isinstance(key_json['public_key'], str):
#             logging.warning('key.py line 49: public_key should be both type<str>')
#             return False
#         if not isinstance(key_json['private_key'], str):
#             logging.warning('key.py line 52: private_key should be both type<str>')
#             return False
#
#         self._public_key = ecdsa.VerifyingKey.from_string(binascii.unhexlify(key_json["public_key"]))
#         self._private_key = ecdsa.SigningKey.from_string(binascii.unhexlify(key_json["private_key"]))
#         return self.valid()
#
#     def store_key(self, path='KeyFile', file='key.json'):
#         if not os.path.exists(path):
#             os.mkdir(path)
#         key_file = os.path.join(path, file)
#         with open(key_file, 'w') as store_file:
#             store_file.write(json.dumps(self.to_json(), indent=4, separators=(',', ':')))
#         return True
#
#     def load_key(self, path='KeyFile', file='key.json'):
#         if not os.path.exists(path):
#             os.mkdir(path)
#         key_file = os.path.join(path, file)
#         with open(key_file, 'r') as load_file:
#             account_json = load_file.read()
#             self.from_json(json.loads(account_json))
#         return True
#
#     def __str__(self):
#         return str(self.get_pubkey())
#
#
# if __name__ == '__main__':
#     u = Key('2ab90eae3c520338c057b2853c5817628a99ffe3068070e0')
#     print(u.to_json())
#     print(u.valid())
#     print(u)
#     print(len(str(u)))
#     m = 'hello'
#     print(u.sign_message(m))

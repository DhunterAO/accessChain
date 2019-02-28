import logging
import copy

from BLOCKCHAINclass.attribute import Attribute
from util.tool import verify_signature, hash_message
# from util.fastkey import verify_signature


class Authorization:
    def __init__(self, input='', nonce=0, output='', attributes=None, signature=''):
        self.input_address = input
        self.nonce = nonce
        self.output_address = output
        if attributes is not None:
            self.attributes = copy.deepcopy(attributes)
        else:
            self.attributes = []
        self.signature = signature

    def add_attribute(self, attribute):
        new_attribute = copy.deepcopy(attribute)
        self.attributes.append(new_attribute)

    def calc_hash(self):
        return hash_message(str(self))

    def sign(self, signature):
        self.signature = signature

    def check_signature(self):
        return verify_signature(pubkey=self.input_address, message=self.calc_hash(), signature=self.signature)

    def to_json(self):
        attributes_json = []
        for attribute in self.attributes:
            attributes_json.append(attribute.to_json())
        authorization_json = {
            'input': self.input_address,
            'nonce': self.nonce,
            'output': self.output_address,
            'attributes': attributes_json,
            'signature': self.signature
        }
        return authorization_json

    def from_json(self, authorization_json):
        required = ['input', 'nonce', 'output', 'attributes', 'signature']
        if not all(k in authorization_json for k in required):
            logging.warning(f"authorization.py line 72: value missing in {required}")
            return False

        self.input_address = authorization_json['input']
        self.nonce = authorization_json['nonce']
        self.output_address = authorization_json['output']
        self.attributes = []
        for attribute_json in authorization_json['attributes']:
            attribute = Attribute()
            attribute.from_json(attribute_json)
            self.attributes.append(attribute)
        self.signature = authorization_json['signature']
        return True

    def __str__(self):
        authorization_str = str(self.input_address) + str(self.nonce) + str(self.output_address)
        for attribute in self.attributes:
            authorization_str += str(attribute)
        return authorization_str


if __name__ == '__main__':
    from src.key import Key

    keyA = Key()
    userA = keyA.get_pubkey()
    userB = "1d89771346e71ebd82a2595033e44daa671a53523d423448d47ebc4ebe78cb42415dd6427fe786604da9969664fcf519"
    a = Authorization(input=userA, output=userB, attributes=[])
    a.sign(keyA.sign_obj(a))
    print(a.to_json())
    print(a)

    b = Authorization()
    b.from_json(a.to_json())
    print(b.to_json())

    print(b.check_signature())

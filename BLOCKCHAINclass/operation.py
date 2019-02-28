import logging

from util.tool import hash_message


class Operation:
    def __init__(self, address='', nonce=0, student_id='', op='', field='', data='', signature=None):
        self.address = address
        self.nonce = nonce
        self.studentId = student_id
        self.op = op
        self.field = field
        self.data = data
        self.signature = signature

    def to_json(self):
        operation_json = {
            'address': self.address,
            'nonce': self.nonce,
            'student_id': self.studentId,
            'operation': self.op,
            'field': self.field,
            'data': self.data,
            'signature': self.signature
        }
        return operation_json

    def from_json(self, operation_json):
        required = ['address', 'nonce', 'student_id', 'operation', 'field', 'data', 'signature']
        if not all(k in operation_json for k in required):
            logging.warning(f"operation.py line 52: value missing in {required}")
            return False

        self.address = operation_json['address']
        self.nonce = operation_json['nonce']
        self.studentId = operation_json['student_id']
        self.op = operation_json['operation']
        self.field = operation_json['field']
        self.data = operation_json['data']
        self.signature = operation_json['signature']
        return True

    def sign(self, signature):
        self.signature = signature

    def calc_hash(self):
        return hash_message(str(self))

    def __str__(self):
        return str(self.address) + str(self.nonce) + \
               str(self.studentId) + str(self.op) + str(self.field) + str(self.data)


if __name__ == '__main__':
    user_address = '9f11c5b5f49399bdda26411ceb0f642fbfd8b311f08d5066e679fb9f60c9a81683fca7baab4a51b78953671a30deb3b4'
    operation = Operation(address=user_address, student_id='2017322381', op='read')
    print(operation)
    print(operation.to_json())


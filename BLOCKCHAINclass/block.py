import hashlib
import logging
import json

from util.tool import current_time

from BLOCKCHAINclass.operation import Operation
from BLOCKCHAINclass.authorization import Authorization


class Block:
    def __init__(self,
                 prev_hash='',
                 timestamp=None,
                 hash_root='5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9',
                 now_hash='',
                 # height=0,
                 authorizations=None,
                 operations=None):

        self.authorizations = []

        if authorizations is not None:
            for authorization in authorizations:
                new_authorization = Authorization()
                new_authorization.from_json(authorization.to_json())
                self.authorizations.append(new_authorization)

        self.operations = []
        if operations is not None:
            for operation in operations:
                new_operation = Operation()
                new_operation.from_json(operation.to_json())
                self.operations.append(new_operation)

        self.hashRoot = hash_root
        # self.height = height

        if timestamp is None:
            timestamp = current_time()
        self.timestamp = timestamp

        self.prevHash = prev_hash
        self.hash = now_hash
        return

    def get_authorization(self, index):
        return self.authorizations[index]

    def add_authorization(self, authorization):
        self.authorizations.append(authorization)
        return

    def get_operations(self):
        return self.operations

    def calc_hash_root(self):
        m = "5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9"
        for authorization in self.authorizations:
            m += str(authorization)
            m = hashlib.sha256(m.encode()).hexdigest()
        for operation in self.operations:
            m += str(operation)
            m = hashlib.sha256(m.encode()).hexdigest()
        return m

    def set_hash_root(self):
        self.hashRoot = self.calc_hash_root()

    def get_timestamp(self):
        return self.timestamp

    def calc_hash(self):
        return hashlib.sha256(str(self).encode()).hexdigest()

    def set_prev_hash(self, prev_hash):
        self.prevHash = prev_hash
        return

    def set_now_hash(self):
        self.hash = self.calc_hash()
        return

    def update_time(self):
        self.timestamp = current_time()
        return

    def to_json(self):
        block_json = {
            'num': len(self.operations) + len(self.authorizations),
            'prev_hash': self.prevHash,
            'now_hash': self.hash,
            'timestamp': self.timestamp,
            'hash_root': self.hashRoot,
            'authorizations': [],
            'operations': []
        }
        for authorization in self.authorizations:
            block_json['authorizations'].append(authorization.to_json())
        for operation in self.operations:
            block_json['operations'].append(operation.to_json())
        return block_json

    def from_json(self, block_json):
        required = ['prev_hash', 'now_hash', 'timestamp', 'hash_root', 'authorizations', 'operations']
        if not all(k in block_json for k in required):
            logging.warning(f'value missing in {required}')
            return False

        if not isinstance(block_json['prev_hash'], str):
            logging.warning("prev_hash should be type<str>")
            return False
        if not isinstance(block_json['now_hash'], str):
            logging.warning("now_hash should be type<str>")
            return False
        if not isinstance(block_json['timestamp'], int):
            logging.warning("timestamp should be type<int>")
            return False
        if not isinstance(block_json['hash_root'], str):
            logging.warning("hash_root should be type<str>")
            return False
        if not isinstance(block_json['authorizations'], list):
            logging.warning("authorizations should be type<list>")
            return False
        if not isinstance(block_json['operations'], list):
            logging.warning("operations should be type<list>")
            return False

        authorizations = []
        for authorization_json in block_json['authorizations']:
            authorization = Authorization()
            if not authorization.from_json(authorization_json):
                return False
            authorizations.append(authorization)

        operations = []
        for operation_json in block_json['operations']:
            operation = Operation()
            if not operation.from_json(operation_json):
                return False
            operations.append(operation)

        self.timestamp = block_json['timestamp']
        self.prevHash = block_json['prev_hash']
        self.hashRoot = block_json['hash_root']
        self.hash = block_json['now_hash']
        self.authorizations = authorizations
        self.operations = operations
        return True

    def __str__(self):
        return str(self.prevHash) + str(self.hashRoot) + str(self.timestamp)

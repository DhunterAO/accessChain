import logging
from util.tool import verify_signature, hash_message
from util.constant import PK_list


class Commit:
    def __init__(self, view_id=None, node_id=None, block_hash=None, signature=None):
        self.infoId = 'Commit'
        self.viewId = view_id
        self.nodeId = node_id
        self.blockHash = block_hash
        self.signature = signature

    def sign(self, signature):
        self.signature = signature

    def to_json(self):
        commit_json = {
            'infoId': self.infoId,
            'viewId': self.viewId,
            'nodeId': self.nodeId,
            'blockHash': self.blockHash,
            'signature': self.signature
        }
        return commit_json

    def from_json(self, commit_json):
        required = ['infoId', 'viewId', 'nodeId', 'blockHash', 'signature']
        if not all(k in commit_json for k in required):
            logging.warning(f'value missing in {required}')
            return False
        if commit_json['infoId'] != 'Commit':
            return False
        self.infoId = commit_json['infoId']
        self.viewId = commit_json['viewId']
        self.nodeId = commit_json['nodeId']
        self.blockHash = commit_json['blockHash']
        self.signature = commit_json['signature']
        return True

    def calc_hash(self):
        return hash_message(str(self))

    def check_signature(self):
        if not verify_signature(PK_list[self.nodeId], self.calc_hash(), self.signature):
            print(PK_list[self.nodeId], self.calc_hash(), self.signature)
            return False
        return True

    def __str__(self):
        return str(self.infoId) + str(self.viewId) + str(self.nodeId) + str(self.blockHash)


if __name__ == '__main__':
    c = Commit(0, 0, 'ds')
    print(c)
    print(c.to_json())

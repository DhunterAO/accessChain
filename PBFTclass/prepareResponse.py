from util.tool import verify_signature
from BLOCKCHAINclass.block import Block
from util.constant import PK_list
from util.tool import hash_message


class PrepareResponse:
    def __init__(self, node_id, view_id, blockHash, signature=None):
        self.infoId = 'PrepareResponse'
        self.nodeId = node_id
        self.viewId = view_id
        self.blockHash = blockHash
        self.signature = signature

    def sign(self, signature):
        self.signature = signature
        return

    def to_json(self):
        response_json = {
            'infoId': self.infoId,
            'nodeId': self.nodeId,
            'viewId': self.viewId,
            'blockHash': self.blockHash,
            'signature': self.signature
        }
        return response_json

    def from_json(self, response_json):
        self.infoId = response_json['infoId']
        self.nodeId = response_json['nodeId']
        self.viewId = response_json['viewId']
        self.blockHash = response_json['blockHash']
        self.signature = response_json['signature']
        return

    def calc_hash(self):
        return hash_message(str(self))

    def check_signature(self):
        return verify_signature(PK_list[self.nodeId], self.calc_hash(), self.signature)

    def __str__(self):
        return str(self.infoId) + str(self.nodeId) + str(self.viewId) + str(self.blockHash)

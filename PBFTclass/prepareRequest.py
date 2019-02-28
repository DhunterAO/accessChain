from util.tool import verify_signature
from BLOCKCHAINclass.block import Block
from util.constant import PK_list
from util.tool import hash_message


class PrepareRequest:
    def __init__(self, node_id, view_id, block_json=None, signature=None):
        self.infoId = 'PrepareRequest'
        self.nodeId = node_id
        self.viewId = view_id
        self.block = Block()
        if block_json is not None:
            self.block.from_json(block_json)
        self.signature = signature

    def sign(self, signature):
        self.signature = signature

    def get_signature(self):
        return self.signature

    def to_json(self):
        request_json = {
            'infoId': self.infoId,
            'nodeId': self.nodeId,
            'viewId': self.viewId,
            'block': self.block.to_json(),
            'signature': self.signature
        }
        return request_json

    def from_json(self, request_json):
        self.infoId = request_json['infoId']
        self.nodeId = request_json['nodeId']
        self.viewId = request_json['viewId']
        self.block.from_json(request_json['block'])
        self.signature = request_json['signature']
        return

    def calc_hash(self):
        return hash_message(str(self))

    def check_signature(self):
        return verify_signature(PK_list[self.nodeId], self.calc_hash(), self.signature)

    def __str__(self):
        return str(self.infoId) + str(self.nodeId) + str(self.viewId) + str(self.block.hash)

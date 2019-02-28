from util.tool import hash_message


class ViewChange:
    def __init__(self, node_id, new_view_id, signature=None):
        self.infoId = 'ViewChange'
        self.nodeId = node_id
        self.newViewId = new_view_id
        self.signature = signature

    def get_info_id(self):
        return self.infoId

    def get_node_id(self):
        return self.nodeId

    def get_new_view_id(self):
        return self.newViewId

    def sign(self, signature):
        self.signature = signature

    def get_signature(self):
        return self.signature

    def from_json(self, view_change_json):
        self.infoId = view_change_json['infoId']
        self.nodeId = view_change_json['nodeId']
        self.newViewId = view_change_json['newViewId']
        self.signature = view_change_json['signature']
        return

    def to_json(self):
        view_change_json = {
            'infoId': self.infoId,
            'nodeId': self.nodeId,
            'newViewId': self.newViewId,
            'signature': self.signature
        }
        return view_change_json

    def calc_hash(self):
        return hash_message(str(self))

    def __str__(self):
        return str(self.infoId) + str(self.nodeId) + str(self.newViewId)

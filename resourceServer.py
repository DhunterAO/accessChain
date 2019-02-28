from flask import Flask, jsonify, request
import json

from BLOCKCHAINclass.chain import Chain
from BLOCKCHAINclass.block import Block
from util.fastkey import FastKey
from PBFTclass.commit import Commit
from util.constant import Neighbor_list


class ResourceServer:
    def __init__(self, host, port, sk, pk_list, data_dir='./ResourceServerData'):
        self._host = host
        self._port = port
        self._data_dir = data_dir
        self._chain = Chain(data_dir=data_dir+'/blockchain')
        self._key = FastKey(sk)
        self.app = Flask(__name__)
        self.n = len(pk_list) - 1
        self.f = (self.n - 1) // 3

        @self.app.route('/store', methods=['GET'])
        def get_state():
            return jsonify(self._chain.chain_store())

        @self.app.route('/block_with_proof', methods=['POST'])
        def receive_block_with_proof():
            data = json.loads(request.data)
            block_json = data.get('block')
            proof_json = data.get('proof')

            block = Block()
            block.from_json(block_json)
            if block.prevHash != self._chain.get_block(-1).hash:
                print('previous hash not match ', block.prevHash, ':', self._chain.get_block(-1).hash)
                return jsonify(False)

            block_hash = block.hash
            node_set = set()
            for commit_json in proof_json:
                commit = Commit()
                commit.from_json(commit_json)
                if commit.blockHash != block_hash:
                    print('commit hash not match')
                    return jsonify(False)
                node_set.add(commit.nodeId)
                if not commit.check_signature():
                    print('signature not match')
                    return jsonify(False)
            if len(node_set) < self.n-self.f:
                print(len(node_set), ' less than ', self.n-self.f)
                return jsonify(False)

            self._chain.add_new_block(block)
            return jsonify(True)

    def start_listen(self):
        self.app.run(host=self._host, port=self._port, debug=False)
        return


if __name__ == '__main__':
    server = ResourceServer(host='127.0.0.1', port=8785,
                            sk='e0c1386e67e1b8e2810d1676063cea2d4af359186cecf3b2',
                            pk_list=Neighbor_list[:1] + Neighbor_list[-1:],
                            data_dir='./ResourceServerData')
    server.start_listen()

from BLOCKCHAINclass.block import Block
from PBFTclass.commit import Commit


class BlockWithProof:
    def __init__(self, block):
        self._block = block
        self._proof = []

    def add_proof(self, commit):
        self._proof.append(commit)

    def to_json(self):
        proof_json = []
        for commit in self._proof:
            proof_json.append(commit.to_json())
        block_with_proof_json = {
            'block': self._block.to_json(),
            'proof': proof_json
        }
        return block_with_proof_json

    def from_json(self, proof_json):
        self._block = Block()
        self._block.from_json(proof_json['block'])
        for commit_json in proof_json['proof']:
            commit = Commit()
            commit.from_json(commit_json)
            self._proof.append(commit)
        return

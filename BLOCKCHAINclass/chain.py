import threading
import logging
import json
import time
import copy

from util.constant import BlockInterval
from util.tool import current_time

from PBFTclass.myTimer import MyTimer

from BLOCKCHAINclass.block import Block
from BLOCKCHAINclass.state import State
from BLOCKCHAINclass.operationPool import OperationPool
from BLOCKCHAINclass.authorizationPool import AuthorizationPool


class Chain:
    def __init__(self,
                 chain_file=None,
                 genesis_file='/genesis_block.json',
                 data_dir='./data/blockchain'):
        self._data_dir = data_dir

        genesis_block_path = data_dir + genesis_file
        # print(genesis_block_path)
        with open(genesis_block_path, 'r') as genesis_block_file:
            genesis_block_str = genesis_block_file.read()
            genesis_block_json = json.loads(genesis_block_str)
            timestamp = genesis_block_json['timestamp']
            self._genesis_block = Block(prev_hash='0'*64, timestamp=timestamp)
            self._genesis_block.set_now_hash()

        if chain_file is None:
            self._blockchain = []
            self._blockchain.append(self._genesis_block)
            # print(self._blockchain[0].to_json())
        else:
            chain_path = data_dir + chain_file
            with open(chain_path, 'r') as blockchain_file:
                blockchain_str = blockchain_file.read()
                # print(blockchain_str)
                blockchain_json = json.loads(blockchain_str)
                # print(blockchain_json)
                self.from_json(blockchain_json)
            if self._blockchain[0] is not self._genesis_block:
                logging.error("genesis_block mismatch the blockchain")
                return
        # print(genesis_block_json['governor_list'])
        self.state = State(gm_list=genesis_block_json['governor_list'])
        self.operationPool = OperationPool()
        self.authorizationPool = AuthorizationPool()
        # self.authorizationPool.pre_add_authorization()
        self._mining_timer = MyTimer(name='mining', interval=BlockInterval, f=self.mining_new_block)
        self._blockchainLock = threading.Lock()
        return

    def get_height(self):
        return len(self._blockchain)

    def get_block(self, block_number):
        return self._blockchain[block_number]

    def get_authorization(self, block_number, authorization_number):
        return self.get_block(block_number).get_authorization(authorization_number)

    def get_output(self, block_number, authorization_number, output_number):
        try:
            output = self._blockchain[block_number].get_authorization(authorization_number).get_output(output_number)
        except IndexError:
            logging.error("index out of range")
            return None
        else:
            return output

    def start_mining(self):
        self._mining_timer.restart()
        return

    def end_mining(self):
        self._mining_timer.stop()
        return

    def mining_new_block(self):
        new_block = self.generate_new_block()
        self.add_new_block(new_block)
        print('mined one new block: ' + new_block.hash)
        self._mining_timer.start()
        return new_block

    def generate_new_block(self):
        with self._blockchainLock:
            authorizations = self.authorizationPool.get_authorizations()
            operations = self.operationPool.get_operations()

            virtual_state = copy.deepcopy(self.state)

            chosen_authorizations = []
            for authorization in authorizations:
                if virtual_state.check_authorization(authorization):
                    chosen_authorizations.append(authorization)
                    virtual_state.change_from_authorization(authorization)
                    if len(chosen_authorizations) > 500:
                        break

            chosen_operations = []
            for operation in operations:
                if virtual_state.check_operation(operation):
                    chosen_operations.append(operation)
                    virtual_state.change_from_operation(operation)
                    if len(chosen_operations) > 500:
                        break

            new_block = Block(prev_hash=self._blockchain[-1].hash,
                              authorizations=chosen_authorizations,
                              operations=chosen_operations,
                              timestamp=current_time())
            new_block.set_now_hash()
            return new_block

    def check_new_block(self, block):
        if block.hash != block.calc_hash():
            logging.warning(f'chain.py line 187: block hash not matched block {block.hash} vs {block.calc_hash()}')
            return False

        if block.prevHash != self._blockchain[-1].hash:
            logging.warning(f'chain.py line 187: block hash not matched last one {block.prevHash} vs {self._blockchain[-1].hash}')
            return False

        v_state = copy.deepcopy(self.state)
        if not v_state.check_authorizations(block.authorizations):
            logging.warning('chain.py line 190: block authorizations invalid')
            return False

        if not v_state.check_operations(block.operations):
            logging.warning('chain.py line 193: block operations invalid')
            return False
        return True

    def add_new_block(self, block):
        with self._blockchainLock:
            print('add new block into blockchain: ', block.hash)
        # if block.prevHash == self._blockchain[-1].hash:
            self._blockchain.append(block)
            print('after add new block, blockchain is in height: ', len(self._blockchain))
            self.state.change_from_authorizations(block.authorizations)
            self.state.change_from_operations(block.operations)

            self.authorizationPool.delete_authorizations(block.authorizations)
            self.operationPool.delete_operations(block.operations)
        # else:
        #     logging.error("chain.py line 130: the new block does not match the blockchain")
        #     return False
        return True

    def valid(self):
        with self._blockchainLock:
            if self._blockchain[0] != self._genesis_block:
                logging.warning('the head of blockchain should be GENESIS_BLOCK')
                return False
            for i in range(1, len(self._blockchain)):
                if self._blockchain[i].get_prev_hash() != self._blockchain[i-1].hash:
                    logging.warning(f'the {i}th block does not match the previous one')
                    return False
            return True

    def contain_block(self, block_hash):
        with self._blockchainLock:
            for block in self._blockchain:
                if block.hash == block_hash:
                    return True
            return False

    def to_json(self):
        chain_json = {
            'blockchain': []
        }
        for block in self._blockchain:
            chain_json['blockchain'].append(block.to_json())
        return chain_json

    def from_json(self, chain_json):
        required = ['height', 'blockchain']
        if not all(k in chain_json for k in required):
            logging.warning(f'value missing in {required}')
            return False

        if not isinstance(chain_json['height'], int):
            logging.warning("height should be type<int>")
            return False
        if not isinstance(chain_json['blockchain'], list):
            logging.warning("blockchain should be type<list>")
            return False

        chain = []
        for block_json in chain_json['blockchain']:
            new_block = Block()
            if not new_block.from_json(block_json):
                return False
            chain.append(new_block)
        self._blockchain = chain
        return True

    def chain_store(self, chain_path='BlockchainFile/chain.json'):
        with open(chain_path, 'w') as chain_file:
            chain_file.write(json.dumps(self.to_json(), indent=4, separators=(',', ':')))
        return

    def chain_load(self, chain_path='BlockchainFile/chain.json'):
        with open(chain_path, 'r') as chain_file:
            chain_json = chain_file.read()
            self.from_json(json.loads(chain_json))
        return

    def add_authorization(self, authorization):
        input_address = authorization.input_address
        input_account = self.state.get_account_from_address(input_address)
        if input_account is None:
            logging.warning('chain.py line 219: no such input_account')
            return False
        if input_account.nonce > authorization.nonce:
            logging.warning('chain.py line 222: the nonce in authorization expire')
            return False
        return self.authorizationPool.add_authorization(authorization)

    def add_operation(self, operation):
        return self.operationPool.add_operation(operation)

    def get_authorization_pool(self):
        return self.authorizationPool

    def get_operation_pool(self):
        return self.operationPool

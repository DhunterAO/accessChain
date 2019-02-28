from util.tool import current_time
import threading
import logging

from util.fastkey import FastKey
from PBFTclass.myTimer import MyTimer
from PBFTclass.commit import Commit
from PBFTclass.prepareRequest import PrepareRequest
from PBFTclass.prepareResponse import PrepareResponse
from PBFTclass.viewChange import ViewChange
from util.constant import PK_list, Neighbor_list, BlockInterval, NullRequestTimeOut, ViewChangeInterval, ViewChangeTimeOut
from util.tool import broadcast_message, post
from PBFTclass.blockWithProof import BlockWithProof


class Pbft:
    def __init__(self, node_id, sk,
                 chain,
                 pk_list=None,
                 neighbor_list=None,
                 data_dir='./data/pbft',
                 block_interval=BlockInterval, null_request_time_out=NullRequestTimeOut,
                 view_change_interval=ViewChangeInterval):

        self.node_id = node_id
        self.key = FastKey(sk)

        if pk_list is None:
            self._pk_list = PK_list
        else:
            self._pk_list = pk_list

        if neighbor_list is None:
            self._neighbor_list = Neighbor_list
        else:
            self._neighbor_list = neighbor_list

        self.neighbor = self._neighbor_list[:self.node_id] + self._neighbor_list[self.node_id:]

        self.n = len(self._neighbor_list)-1
        self.f = (self.n - 1) // 3

        self._running = False

        self.viewLock = threading.Lock()
        self._inViewChangeLock = threading.Lock()
        self.view = 0
        self.newView = 0
        self.viewPool = {}
        self._view_change_interval = view_change_interval
        self._view_change_timer = MyTimer('view_change', self._view_change_interval, self.change_view)
        self._view_change_resend_time = 10
        self._view_change_resend_timer = MyTimer('view_change_resend', self._view_change_resend_time, self.change_view)
        self._inViewChange = False

        self._next_block_hash = None
        self._prepare_request_pool = {}
        self._prepare_response_pool = {}
        self._commit_pool = {}

        self._null_request_time_out = null_request_time_out
        self._null_request_timer = MyTimer('null_request', self._null_request_time_out, self.change_view)

        self._block_interval = block_interval
        self._new_block_timer = MyTimer('new_block', self._block_interval, self.new_block)

        self._block_time_out = block_interval / 2
        self._block_timer = MyTimer('block_time_out', self._block_time_out, self.change_view)

        self.chain = chain
        self._block_pool = {}
        # print('pbft inited')

    def start_running(self):
        self._running = True
        self._view_change_timer.start(args=['start running'])
        self._new_block_timer.start(args=['start running'])
        return

    def end_running(self):
        self._running = False
        self._view_change_timer.stop()
        self._view_change_resend_timer.stop()

        self._block_timer.stop()
        self._null_request_timer.stop()
        print('pbft end')
        return

    def change_view(self, reason=None):
        if reason is not None:
            print(f'{reason} cause view change')
        self._view_change_timer.stop()
        self._view_change_resend_timer.stop()

        self._null_request_timer.stop()
        self._block_timer.stop()
        self._new_block_timer.stop()

        with self.viewLock:
            self.newView += 1
            self._view_change_resend_time *= 2
            if self._view_change_resend_time > 60:
                self._view_change_resend_time = 60
            vc = ViewChange(self.node_id, self.newView)
            self._view_change_resend_timer.restart(interval=self._view_change_resend_time,
                                                   args=['view change resend time out '])

        vc.sign(self.key.sign_obj(vc))
        self.broadcast_view_change(vc)
        return

    def broadcast_view_change(self, view_change):
        response_thread = threading.Thread(target=broadcast_message,
                                           args=[self._neighbor_list[:-1], '/pbft/viewChange', view_change.to_json()])
        response_thread.start()
        return

    def receive_view_change(self, view_change):
        with self.viewLock:
            node_id = view_change.nodeId
            new_view_id = view_change.get_new_view_id()

            if new_view_id <= self.view:
                logging.warning(f'pbft.py line 137: view id invalid {new_view_id} vs {self.view}')
                return False

            if new_view_id not in self.viewPool:
                self.viewPool[new_view_id] = set()

            self.viewPool[new_view_id].add(node_id)

            if len(self.viewPool[new_view_id]) >= self.n - self.f:
                self.view = new_view_id
                self.newView = self.view

                self._view_change_resend_timer.stop()
                self._view_change_timer.restart(interval=ViewChangeInterval, args=['view change finished, a new turn starts '])
                self._new_block_timer.restart(args=['view change finished, a new turn starts '])

        with self._inViewChangeLock:
            self._inViewChange = False
        return

    # send new block to all neighbors or ask for a new block
    def new_block(self, reason=None):
        if reason is not None:
            print(f'{reason} starts a new block')
        if self.view % self.n == self.node_id:
            print('i am the miner')
            new_block = self.chain.generate_new_block()
            prepare_request = PrepareRequest(node_id=self.node_id, view_id=self.view, block_json=new_block.to_json())
            prepare_request.sign(self.key.sign_obj(prepare_request))
            print(prepare_request.check_signature())
            print('generate prepare_request: ', prepare_request.to_json())
            print(prepare_request.check_signature())
            self.broadcast_prepare_request(prepare_request)
        else:
            print('i am a listener')
            self._null_request_timer.restart(args=['null request '])
        self._new_block_timer.restart(args=['this block starts, a new block waiting '])
        self._block_timer.restart(args=['this block starts, a new block waiting '])

    # broadcast request to all neighbors
    def broadcast_prepare_request(self, prepare_request):
        response_thread = threading.Thread(target=broadcast_message,
                                           args=[self._neighbor_list[:-1], '/pbft/prepareRequest', prepare_request.to_json()])
        response_thread.start()
        return

    def check_prepare_request(self, prepare_request):
        if prepare_request.infoId != 'PrepareRequest':
            logging.warning(f'pbft.py line 172: info id in prepare_request is invalid {prepare_request.infoId}')
            return False

        if prepare_request.viewId != self.view:
            logging.warning(f'pbft.py line 176: view id in prepare_request not match {prepare_request.viewId} vs {self.view}')
            return False

        if prepare_request.nodeId != self.view % self.n:
            logging.warning(f'pbft.py line 189: node id in prepare_request is invalid {prepare_request.nodeId} vs {self.view % self.n}')
            return False

        if not prepare_request.check_signature():
            logging.warning(f'pbft.py line 192: signature in prepare_request is invalid')
            return False
        return True

    # once prepare_request received is valid(checked in server), then broadcast prepare_response to this block
    def receive_prepare_request(self, prepare_request):
        print('Receive prepare request', prepare_request.to_json())

        self._null_request_timer.stop()

        block = prepare_request.block
        self._block_pool[block.hash] = block

        prepare_response = PrepareResponse(self.node_id, self.view, block.hash)
        prepare_response.sign(self.key.sign_obj(prepare_response))
        self.broadcast_prepare_response(prepare_response)
        return True

    # broadcast response to all neighbors
    def broadcast_prepare_response(self, prepare_response):
        response_thread = threading.Thread(target=broadcast_message,
                                           args=[self._neighbor_list[:-1], '/pbft/prepareResponse', prepare_response.to_json()])
        response_thread.start()
        # broadcast_message(self._neighbor_list, '/pbft/prepareResponse', prepare_response.to_json())
        return

    # check if prepare response is valid
    def check_prepare_response(self, prepare_response):
        if prepare_response.infoId != 'PrepareResponse':
            return False
        if prepare_response.nodeId != self.view % self.n:
            return False
        if not prepare_response.check_signature():
            return False
        return True

    # once prepare_response received is valid(checked above), then add it into pool
    # if prepare_response_pool is large or equal than n-f, then broadcast commit of this block
    def receive_prepare_response(self, prepare_response):
        print('Receive prepare response', prepare_response)

        block_hash = prepare_response.blockHash

        node_id = prepare_response.nodeId
        if block_hash not in self._prepare_response_pool:
            self._prepare_response_pool[block_hash] = set()
        self._prepare_response_pool[block_hash].add(node_id)

        if len(self._prepare_response_pool[block_hash]) >= self.n-self.f:
            commit = Commit(self.view, self.node_id, block_hash)
            commit.sign(self.key.sign_obj(commit))

            self.broadcast_commit(commit)
            self._prepare_response_pool[block_hash].clear()
            return True
        return False

    # broadcast commit to all neighbors
    def broadcast_commit(self, commit):
        response_thread = threading.Thread(target=broadcast_message,
                                           args=[self._neighbor_list[:-1], '/pbft/commit', commit.to_json()])
        response_thread.start()
        return True

    # if commit received is valid, then add it into pool
    # if commit_pool is large or equal than n-f, then add this block into blockchain and operation it
    def receive_commit(self, commit):
        if not commit.check_signature():
            logging.warning('pbft.py line 249: commit signature invalid')
            return False

        block_hash = commit.blockHash
        if block_hash not in self._commit_pool:
            self._commit_pool[block_hash] = set()
        self._commit_pool[block_hash].add(commit)

        if len(self._commit_pool[block_hash]) >= self.n-self.f:
            self._block_timer.stop()
            if block_hash in self._block_pool:
                new_block = self._block_pool[block_hash]
                self.chain.add_new_block(new_block)
                block_with_proof = BlockWithProof(block=new_block)
                for commit in self._commit_pool[block_hash]:
                    block_with_proof.add_proof(commit)
                self._commit_pool[block_hash].clear()
                commit_database_thread = threading.Thread(target=post,
                                                          args=[self._neighbor_list[-1],
                                                                '/block_with_proof',
                                                                block_with_proof.to_json()])
                commit_database_thread.start()
            return True
        return True


if __name__ == '__main__':
    p = Pbft(0, '2e0f100bfd35cbea547a132b37a87f132b8b948bd8aa5d4e')
    p.start_running()

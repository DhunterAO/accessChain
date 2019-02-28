#coding=utf-8
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from AuthorizationServer import AuthorizationServer
from util.constant import Neighbor_list
from threading import Thread
import asyncio
import os


def deploy_authorization_server(host, port, node_id, sk, data_dir, neighbor_list, block_interval, null_request_time_out,
                                view_change_interval):
    asyncio.set_event_loop(asyncio.new_event_loop())
    server = AuthorizationServer(host=host, port=port, node_id=node_id,
                                 sk=sk,
                                 data_dir=data_dir,
                                 neighbor_list=neighbor_list,
                                 block_interval=block_interval,
                                 null_request_time_out=null_request_time_out,
                                 view_change_interval=view_change_interval)

    server.start_pbft()
    http_server = HTTPServer(WSGIContainer(server.app))
    http_server.listen(port)
    IOLoop.instance().start()


if __name__ == '__main__':
    # thread = Thread(target=deploy_authorization_server,
    #                 args=['127.0.0.1', 8880, 0, '2e0f100bfd35cbea547a132b37a87f132b8b948bd8aa5d4e',
    #                       './AuthorizationServerData', Neighbor_list[:1] + Neighbor_list[-1:],
    #                       2, 1, 10])
    # thread.start()

    pid = os.fork()
    if pid == 0:
        deploy_authorization_server('127.0.0.1', 8880, 0, '2e0f100bfd35cbea547a132b37a87f132b8b948bd8aa5d4e',
                                    './AuthorizationServerData', Neighbor_list, 2, 1, 60)

    pid = os.fork()
    if pid == 0:
        deploy_authorization_server('127.0.0.1', 8881, 1, '9f485650bc6522b4eda2834f9c41df12d64a5ba8105ac416',
                                    './AuthorizationServerData', Neighbor_list, 2, 1, 60)

    pid = os.fork()
    if pid == 0:
        deploy_authorization_server('127.0.0.1', 8882, 2, '5e63445f7abed5c08f39292c81e185179245a5fdb9086db8',
                                        './AuthorizationServerData', Neighbor_list, 2, 1, 60)

    deploy_authorization_server('127.0.0.1', 8883, 3, 'a340b17aff9a18d611366a754cbc05d24830c12860ff2575',
                                './AuthorizationServerData', Neighbor_list, 2, 1, 60)



    # node_0 = Thread(target=deploy_authorization_server,
    #                 args=['127.0.0.1', 8880, 0, '2e0f100bfd35cbea547a132b37a87f132b8b948bd8aa5d4e',
    #                       './AuthorizationServerData', Neighbor_list,
    #                       2, 1, 60])
    # node_1 = Thread(target=deploy_authorization_server,
    #                 args=['127.0.0.1', 8881, 1, '9f485650bc6522b4eda2834f9c41df12d64a5ba8105ac416',
    #                       './AuthorizationServerData', Neighbor_list,
    #                       2, 1, 60])
    # node_2 = Thread(target=deploy_authorization_server,
    #                 args=['127.0.0.1', 8882, 2, '5e63445f7abed5c08f39292c81e185179245a5fdb9086db8',
    #                       './AuthorizationServerData', Neighbor_list,
    #                       2, 1, 60])
    # node_3 = Thread(target=deploy_authorization_server,
    #                 args=['127.0.0.1', 8883, 3, 'a340b17aff9a18d611366a754cbc05d24830c12860ff2575',
    #                       './AuthorizationServerData', Neighbor_list,
    #                       2, 1, 60])
    # node_0.start()
    # node_1.start()
    # node_2.start()
    # node_3.start()

# coding=utf-8
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from resourceServer import ResourceServer
from util.constant import Neighbor_list, PK_list


server = ResourceServer(host='127.0.0.1', port=8785,
                        sk='cbe6cb935e85270b5f3ac3d2b839093eaaf67178bb748885',
                        pk_list=PK_list[:1]+PK_list[-1:],
                        data_dir='./ResourceServerData')

http_server = HTTPServer(WSGIContainer(server.app))
http_server.listen(8785)
IOLoop.instance().start()

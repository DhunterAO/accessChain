from BLOCKCHAINclass.operation import Operation
from BLOCKCHAINclass.authorization import Authorization
from BLOCKCHAINclass.attribute import Attribute
from BLOCKCHAINclass.duration import Duration
from util.fastkey import FastKey
from util.tool import check_operation_signature, check_authorization_signature, verify_signature

import json
import requests
import sys
import hashlib

userId = '130493'
key = 'e52935a8-3d5c-44c1-8081-9d52c8a22ddc'


def genCheckSum(body, secret):
    encryStr = body + secret
    res = hashlib.md5(encryStr.encode('utf-8')).hexdigest()
    return res[14:18].lower()


print(genCheckSum("body", key))

article = {
    'ArticleUrl': 'https://mp.weixin.qq.com/s?__biz=MzA3NTQ3NzUzNA==&mid=2651828567&idx=1&sn=b4b99bb337f6a01cb4f87c7343f3c436&chksm=8494f626b3e37f303f777bd0cb9498ca3ab137f4f0f34a8970188854cbb4ad717092cc7a6dde#rd'
}

body = json.dumps(article)

headers = {
    'Content-Type': 'application/json',
    'userid': userId,
    'checksum': genCheckSum(body=body, secret=key)
}
# r = requests.post(url='http://openapi.xiguaji.com/v3/Article/AddArticleRealTimeLog', headers=headers, json=article)
#
# print(r.text)
qry = {
    "LogId": 448086
}
body = json.dumps(qry)

headers = {
    'Content-Type': 'application/json',
    'userid': userId,
    'checksum': genCheckSum(body=body, secret=key)
}
rr = requests.post(url='http://openapi.xiguaji.com/v3/Article/GetArticleRealTimeInfo', headers=headers, json=qry)
print(rr.text)

# USER_N = 100
# TX_N = 1000
#
# pk = []
# sk = []
# with open('ClientData/user.txt', 'r') as user_file:
#     for i in range(USER_N):
#         k = user_file.readline().split(' ')
#         pk.append(k[0])
#         sk.append(k[1][:-1])
#         print(len(pk[-1]), len(sk[-1]))
#
# print('finish read users')
# print(len(pk))

def TestTransaction(auth, op):
    # try operation without permission
    no_permission = post(server_address, '/api/operation', op.to_json())
    print(no_permission)
    # get permission
    post(server_address, '/api/authorization', auth.to_json())
    # try operation again with permission
    with_permission = post(server_address, '/api/operation', op.to_json())
    print(with_permission)

# result without permission
{state: 'no permission', data:''}
# result with permission
{state: 'ok', data:'{"name": "Alice", "age": "20"}'}

def TestAuthorization():
    auth = Authorization(
            input='8f40a2d93bb7ad3f9e9edc4441bb5900e158554332209b3167d7cbc1a9c6fe77\
                   6a1b683733f4fba2366655d1fa3719f8bc389469cd90dadc135031d04cb854c1',
            nonce=0, 
            output='eeb277ff1c3207d02542270529d3348b19f6db0f48807d710700c986c2137747\
                    8f2fa277a0768488f475cf92c97c947ca192d48ab7071072f94959602fd49332', 
            attributes=[{"name": "1", "duration": {"start": 0, "end": 10000}}], 
            signature='938844a01d7f89701a8045790b3c2b0e88bdf708714a1200b911c6d98bc29449\
                       90059e0e5fe5f62c847ea34dc850b167e5546d93fa0a664cdd52c5afab019dd5'
        )
    post(server_address, '/api/authorization', auth.to_json())



{
    "height":5,
    "prev_hash":"b1557d0b565ceb513bf91034fb0e90ead9dd346f9b7f2c7e17979283f49d1067",
    "now_hash":"e5df7408af2e986c70de0ef951c14be307704c6a8c4200fa966931261109fa91",
    "hash_root":"5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9",
    "authorizations":[{
        "attributes":[{
            "duration":{
                "end":10000,
                "start":0
            },
            "name":"1"
        }],
        "input":"8f40a2d93bb7ad3f9e9edc4441bb5900e158554332209b3167d7cbc1a9c6fe77\
                 6a1b683733f4fba2366655d1fa3719f8bc389469cd90dadc135031d04cb854c1",
        "nonce":0,
        "output":"eeb277ff1c3207d02542270529d3348b19f6db0f48807d710700c986c2137747\
                  8f2fa277a0768488f475cf92c97c947ca192d48ab7071072f94959602fd49332",
        "signature":"938844a01d7f89701a8045790b3c2b0e88bdf708714a1200b911c6d98bc29449\
                     90059e0e5fe5f62c847ea34dc850b167e5546d93fa0a664cdd52c5afab019dd5"
    }...]
    "operations":[],
    "num": 75,
    "timestamp":1543824623907
}


"blockchain":[...
    {
        "prev_hash":"a2e48aa69948ef8329ecce04d1dc3e5199c0aed4ddb8d4a262cafa6c46fdf732",
        "now_hash":"576af9a7a9632a774c85527494ea142b0478d951fd8eac9fbc3e3f16f4634874",
        "authorizations":...,
        "hash_root":"19297709e644a1924f5a25cf50b51290430b2fbbb71d8a344563401e01ac6ed6",
        "num":109,
        "operations":...,
        "timestamp":1531297846094
    },{
        "prev_hash":"a2e48aa69948ef8329ecce04d1dc3e5199c0aed4ddb8d4a262cafa6c46fdf732",
        "now_hash":"47a1782833f62fff0293a5be1c2a5d13885560ac7c2f977e07aeeb1361426d24",
        "authorizations":...,
        "hash_root":"949218c204640ade655ec9cc0d6ad5545e864c35b7aee3aa244dc39a4ec62b99",
        "num":105,
        "operations":...,
        "timestamp":1543824593825
    },...
]




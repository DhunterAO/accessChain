import requests
import traceback
import threading
import binascii
import logging
import urllib3
from fastecdsa import ecdsa
from util.fastkey import CURVE, HASH_FUNC, from_address_to_pubkey
import time
import json
import re


def current_time():
    return int(round(time.time() * 1000))


def is_valid_ip(ip):
    q = ip.split('.')
    return len(q) == 4 and len(list(filter(lambda x: 0 <= x <= 255, map(int, filter(lambda x: x.isdigit(), q))))) == 4


def verify_signature(pubkey, message, signature):
    r = int(signature[:64], 16)
    s = int(signature[64:], 16)
    return ecdsa.verify((r, s), message, from_address_to_pubkey(pubkey), CURVE, HASH_FUNC)


# def verify_signature(pubkey, message, signature):
#     try:
#         public_key = ecdsa.VerifyingKey.from_string(binascii.unhexlify(pubkey))
#         public_key.verify(bytes.fromhex(signature), message.encode("utf-8"))
#     except (ValueError, AssertionError, ecdsa.keys.BadSignatureError):
#         logging.warning('tool.py line 23: verify signature failed !')
#         return False
#     else:
#         return True


def check_address(address):
    if isinstance(address, str) and len(address) == 128 and re.match("^[a-z0-9]+$", address):
        return True
    return False


def check_operation_signature(operation):
    if not verify_signature(operation.address, operation.calc_hash(), operation.signature):
        logging.warning('tool.py line 42: operation signature not matched')
        return False
    return True


def check_authorization_signature(authorization):
    if not verify_signature(authorization.input_address, authorization.calc_hash(), authorization.signature):
        logging.warning('tool.py line 49: authorization signature not matched')
        return False
    return True


def hash_message(message):
    return HASH_FUNC(message.encode('utf-8')).hexdigest()


def get(address, url=''):
    get_pool = urllib3.PoolManager()

    try:
        response = get_pool.request('GET', address + url)
        return json.loads(response.data)
    except:
        # traceback.print_exc()
        return False


def post(address, url, json_data):
    try:
        print('POST ', address + url)
        response = requests.post(address + url, data=json.dumps(json_data))
    except requests.exceptions.ConnectionError as e:
        logging.warning('tool.py line 46: ' + str(e))
        # traceback.print_exc()
        # logging.warning('sending error')
        return False
    return response.text


def t_post(server_address_list, url, json_data=None):
    po = threading.Thread(target=post, args=[server_address_list, url, json_data])
    po.start()
    return


def broadcast_message(address_list, url, data):
    for address in address_list:
        post(address, url, data)
    return


def broadcast_operation(address_list, operation):
    operation_thread = threading.Thread(target=broadcast_message,
                                        args=[address_list, '/api/operation', operation.to_json()])
    operation_thread.start()
    return


def broadcast_authorization(address_list, authorization):
    authorization_thread = threading.Thread(target=broadcast_message,
                                            args=[address_list, '/api/authorization', authorization.to_json()])
    authorization_thread.start()
    return


def load_server_address_list(path):
    with open(path, 'r') as server_address_file:
        server_address_list_str = server_address_file.read()
        server_address_list_json = json.loads(server_address_list_str)
        required = ['server_address_list']
        if not all(k in server_address_list_json for k in required):
            logging.warning(f"value missing in {required}")
            return False
        return server_address_list_json['server_address_list']

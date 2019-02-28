import json, os
from util.tool import t_post, post, load_server_address_list
from dataGen import TX_N, USER_N
from time import sleep
from multiprocessing import Process

server_address = load_server_address_list(path='ClientData/serverAddress.json')[0]
print(server_address)

connection_num = 25


def run_sending(user_id):
    # print(user_id, os.getpid())
    for i in range(USER_N // connection_num):
        cur_id = user_id+i*connection_num
        if cur_id == 0:
            continue
        json_file = f'ClientData/json{cur_id}.txt'
        with open(json_file, 'r') as json_input:
            for _ in range(USER_N-1):
                flag = json_input.readline()
                auth_json = json.loads(json_input.readline())
                post(server_address, '/api/authorization', auth_json)

        #
        # for _ in range(TX_N-USER_N):
        #
        #     # sleep(0.02)
        #     # print(i)
        #     # if i > 99:
        #     #     break
        #     flag = json_input.readline()
        #     # if i < 10:
        #     #     continue
        #     # print(flag)
        #     if flag == 'au\n':
        #         auth_json = json.loads(json_input.readline())
        #         t_post(server_address, '/api/authorization', auth_json)
        #     elif flag == 'op\n':
        #         op_json = json.loads(json_input.readline())
        #         t_post(server_address, '/api/operation', op_json)
        #     else:
        #         print(flag)


if __name__ == '__main__':
    json_file = 'ClientData/json.txt'
    with open(json_file, 'r') as json_input:
        for _ in range(USER_N-1):
            flag = json_input.readline()
            auth_json = json.loads(json_input.readline())
            post(server_address, '/api/authorization', auth_json)

    for i in range(0, connection_num):
        p = Process(target=run_sending, args=(i,))
        p.start()
        # p.join()
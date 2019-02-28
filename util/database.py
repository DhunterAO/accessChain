from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, WriteError

info = MongoClient('127.0.0.1', 27017)['BlockchainDB'].studentInfo


def create_new_user(student_id, student_info):
    print('create', student_id)
    try:
        student_info['_id'] = student_id
        info.insert(student_info)
    except DuplicateKeyError:
        return False
    else:
        return True


def query_user_info(student_id):
    print('query', student_id)
    res = info.find_one(
        {
            '_id': student_id
        }
    )
    if res is None:
        return 'no such user'
    return res


def update_user_info(student_id, key, value):
    try:
        info.update_one(
            {
                '_id': student_id
            },
            {
                '$set': {
                    key: value
                }
            }
        )
    except WriteError:
        return False
    else:
        return True


def delete_user_info(student_id, key):
    try:
        info.update_one(
            {
                '_id': student_id
            },
            {
                '$unset': {
                    key: 1
                }
            }
        )
    except WriteError:
        return False
    else:
        return True


def database_change_from_operation(operation):
    student_id = operation.get_student_id()
    op = operation.get_op()
    field = operation.get_field()
    data = operation.get_data()

    if op == 'update':
        update_user_info(student_id, field, data)
    elif op == 'add':
        update_user_info(student_id, field, data)
    elif op == 'delete':
        delete_user_info(student_id, field)
    return


def database_change_from_operations(operations):
    for operation in operations:
        database_change_from_operation(operation)
    return


if __name__ == '__main__':
    print(create_new_user(2018210807, {'name': 'hunter', 'age': 22}))
    print(query_user_info(2018230807))
    print(update_user_info(2018210807, 'nickname', 'hunterr'))
    print(delete_user_info(2018210807, 'nickname'))

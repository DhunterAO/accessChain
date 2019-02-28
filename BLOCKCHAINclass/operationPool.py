import threading

from BLOCKCHAINclass.operation import Operation


class OperationPool:
    def __init__(self, operations=None):
        if operations is None:
            self._operations = []
        else:
            self._operations = operations
        self._lock = threading.Lock()

    def contain_operation(self, operation):
        op_hash = operation.calc_hash()
        with self._lock:
            for op in self._operations:
                if op_hash == op.calc_hash():
                    return True
        return False

    def add_operation(self, operation):
        op_hash = operation.calc_hash()
        with self._lock:
            for op in self._operations:
                if op_hash == op.calc_hash():
                    return False
            self._operations.append(operation)
        return True

    def get_operations(self):
        with self._lock:
            return self._operations

    def delete_operation(self, operation):
        op_hash = operation.calc_hash()
        with self._lock:
            for op in self._operations:
                if op_hash == op.calc_hash():
                    self._operations.remove(op)
                    return True
        return False

    def delete_operations(self, operations):
        for operation in operations:
            self.delete_operation(operation)
        return

    def to_json(self):
        operation_pool_json = []
        for operation in self._operations:
            operation_pool_json.append(operation.to_json())
        return operation_pool_json


if __name__ == '__main__':
    OpPool = OperationPool()
    print(OpPool.to_json())
    op = Operation()
    print(op.to_json())
    OpPool.add_operation(op)
    print(OpPool.to_json())


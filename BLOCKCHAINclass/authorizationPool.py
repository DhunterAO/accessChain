import threading

from BLOCKCHAINclass.authorization import Authorization
from BLOCKCHAINclass.attribute import Attribute
from BLOCKCHAINclass.duration import Duration

from util.fastkey import FastKey


class AuthorizationPool:
    def __init__(self, authorizations=None):
        if authorizations is None:
            self._authorizations = []
        else:
            self._authorizations = authorizations
        self._lock = threading.Lock()

    def add_authorization(self, authorization):
        with self._lock:
            for authorization_existed in self._authorizations:
                if str(authorization_existed) == str(authorization):
                    return False
            self._authorizations.append(authorization)
        return True

    def get_authorizations(self):
        with self._lock:
            return self._authorizations

    def delete_authorization(self, authorization_deleted):
        with self._lock:
            for authorization in self._authorizations:
                if authorization_deleted.calc_hash() == authorization.calc_hash():
                    self._authorizations.remove(authorization)
                    return

    def delete_authorizations(self, authorizations):
        for authorization in authorizations:
            self.delete_authorization(authorization)

    def pre_add_authorization(self):
        attribute = Attribute(name='2013823932_privacy', duration=Duration(-1, 0))

        authorization = Authorization(input='c8f36ab884514b6068070c9fd8f14cf5349194d29a22baf7f4d2d932715f21f6b7b2146c5f69a32c2cebb8c7bf3f82f3',
                                      output='1d89771346e71ebd82a2595033e44daa671a53523d423448d47ebc4ebe78cb42415dd6427fe786604da9969664fcf519')
        # print(authorization.to_json())
        authorization.add_attribute(attribute)
        # print(authorization.to_json())
        key = FastKey()
        key.load_key()
        authorization.sign(key.sign_message(str(authorization)))
        self.add_authorization(authorization)

    def to_json(self):
        pool_json = []
        with self._lock:
            for authorization in self._authorizations:
                pool_json.append(authorization.to_json())
            return pool_json


if __name__ == '__main__':
    auPool = AuthorizationPool()
    print(auPool.to_json())
    auPool.pre_add_authorization()
    print(auPool.to_json())

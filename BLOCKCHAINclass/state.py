import logging
import json
import threading

from util.tool import check_address

from BLOCKCHAINclass.duration import Duration
from BLOCKCHAINclass.attribute import Attribute
from BLOCKCHAINclass.account_state import AccountState
from BLOCKCHAINclass.authorization import Authorization


class State:
    def __init__(self, gm_list=None, accounts=None):
        if gm_list is None:
            self._gmList = []
        else:
            self._gmList = gm_list

        if accounts is None:
            self.accounts = []
            for gm in self._gmList:
                gm_state = AccountState(address=gm, attributes=[], nonce=0)
                self.accounts.append(gm_state)
        else:
            self.accounts = accounts
        # self.lock = threading.Lock()

    def add_account_state(self, account_state):
        # with self.lock:
        self.accounts.append(account_state)
        return

    def get_accounts(self):
        return self.accounts

    def get_account_from_address(self, address):
        for account_state in self.accounts:
            if account_state.address == address:
                return account_state
        return None

    def get_account_index_from_address(self, address):
        for (index, account) in enumerate(self.accounts):
            if account.address == address:
                return index
        return -1

    def check_authorization(self, authorization):
        input_address = authorization.input_address
        output_address = authorization.output_address
        if not check_address(input_address) or not check_address(output_address):
            logging.warning('state.py line 50: the input or output of authorization is invalid')
            return False

        input_account = self.get_account_from_address(input_address)

        if input_account is None:
            logging.warning('state.py line 58: the input account of authorization is not existed')
            return False

        # print('state.py line 54:', input_account.to_json())
        if input_address in self._gmList:
            if input_account.nonce == authorization.nonce:
                return True
            logging.warning('state.py line 63: the nonce of authorization does not match: ' +
                            str(input_account.nonce) + ' vs ' + str(authorization.nonce))
            return False

        return input_account.check_authorization(authorization)

    def check_operation(self, operation):
        address = operation.address
        if not check_address(address):
            logging.warning('state.py line 79: the address of operation is invalid')
            return False

        account_state = self.get_account_from_address(address)
        if account_state is None:
            logging.warning(f'state.py line 83: account not exist')
            return False
        return account_state.check_operation(operation)

    def check_authorizations(self, authorizations):
        for authorization in authorizations:
            if not self.check_authorization(authorization):
                return False
            self.change_from_authorization(authorization)
        return True

    def check_operations(self, operations):
        for operation in operations:
            if not self.check_operation(operation):
                return False
            self.change_from_operation(operation)
        return True

    def change_from_authorization(self, authorization):
        input_address = authorization.input_address
        input_account_index = self.get_account_index_from_address(input_address)
        if input_account_index == -1:
            logging.error('state.py line 89: input account is not existed')
            return False

        self.accounts[input_account_index].increase_nonce()

        output_address = authorization.output_address
        output_account_index = self.get_account_index_from_address(output_address)
        authorized_attributes = authorization.attributes
        # print('state.py line 98: ', authorized_attributes[0].to_json())

        if output_account_index >= 0:
            self.accounts[output_account_index].add_attributes(authorized_attributes)
        else:
            new_account_state = AccountState(address=output_address, attributes=authorized_attributes, nonce=0)
            # print(new_account_state.to_json())
            self.add_account_state(new_account_state)
        return

    def change_from_operation(self, operation):
        address = operation.address
        account_state = self.get_account_from_address(address)
        if account_state is None:
            logging.error('state.py line 89: input account is not existed')
            return False
        account_state.increase_nonce()
        return

    def change_from_authorizations(self, authorizations):
        for authorization in authorizations:
            self.change_from_authorization(authorization)
        return

    def change_from_operations(self, operations):
        for operation in operations:
            self.change_from_operation(operation)
        return

    def to_json(self):
        state_json = {
            'gmList': [],
            'accountState': []
        }
        for gm in self._gmList:
            state_json['gmList'].append(gm)
        for account in self.accounts:
            state_json['accountState'].append(account.to_json())
        return state_json

    def from_json(self, state_json):
        required = ['gmList', 'accountState']
        if not all(k in state_json for k in required):
            logging.warning(f"state.py line 141: value missing in {required}")
            return False

        account_state_json = state_json['accountState']
        gm_list_json = state_json['gmList']
        for gm_json in gm_list_json:
            self._gmList.append(gm_json)

        self.accounts = []
        for account_json in account_state_json:
            new_account_state = AccountState()
            new_account_state.from_json(account_json)
            self.accounts.append(new_account_state)

    def get_nonce_from_address(self, address):
        for account in self.accounts:
            if account.address == address:
                return account.nonce
        return -1

    def get_valid_attributes_from_address(self, address):
        attributes = self.get_attributes_from_address(address)
        valid_attributes = []
        for attribute in attributes:
            # print(attribute.to_json())
            duration = attribute.get_duration()
            if duration.valid_now():
                valid_attributes.append(attribute.get_name())
        return valid_attributes

    def get_attributes_from_address(self, address):
        for account in self.accounts:
            if account.get_address() == address:
                return account.get_attributes()
        return []

    # def check_attribute(self, address, attribute):
    #     account_state = self.get_account_from_address(address)
    #     return account_state.check_attribute(attribute)
    #
    # def check_attributes(self, address, attributes):
    #     for attribute in attributes:
    #         if not self.check_attribute(address, attribute):
    #             return False
    #     return True


if __name__ == '__main__':
    name = 'student'
    d = Duration()
    att = Attribute(name, d)
    att.set_duration(Duration(200, 1))

    s = State(gm_list=["d32f637a66da5829a007df4de5aa0s1b120c0aa440ad6062"])
    a = Authorization(input="d32f637a66da5829a007df4de5aa0s1b120c0aa440ad6062",
                      output="ases637a66da5829a007df4de5aa0s1b120c0aa440ad6062",
                      attributes=[att],
                      nonce=0,
                      signature='')

    print(s.to_json())
    print(s.check_authorization(a))
    s.change_from_authorization(a)
    print(s.to_json())
    print(s.check_authorization(a))

    att2 = Attribute()
    att2.from_json(att.to_json())
    att2.set_duration(Duration(190, 1))
    b = Authorization(input="ases637a66da5829a007df4de5aa0s1b120c0aa440ad6062",
                      output="bbbb637a66da5829a007df4de5aa0s1b120c0aa440ad6062",
                      attributes=[att2],
                      nonce=0,
                      signature='')
    print(s.check_authorization(b))
    print(s.change_from_authorization(b))
    print(s.to_json())
    print(s.get_nonce_from_address('ases637a66da5829a007df4de5aa0s1b120c0aa440ad6062'))
    atts = s.get_attributes_from_address('bbbb637a66da5829a007df4de5aa0s1b120c0aa440ad6062')
    for att in atts:
        print(att.to_json())



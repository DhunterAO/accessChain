import logging
import copy

from util.tool import check_address
from BLOCKCHAINclass.attribute import Attribute


class AccountState:
    def __init__(self, address='', attributes=None, nonce=0, code=None, data=None):
        self.address = address
        if attributes is not None:
            self.attributes = copy.deepcopy(attributes)
        else:
            self.attributes = []
        self.nonce = nonce

    def add_attributes(self, attributes):
        for attribute in attributes:
            self.attributes.append(copy.deepcopy(attribute))
        return

    def check_attribute(self, attribute):
        for att in self.attributes:
            if att.name == attribute.name and att.get_duration().contain(attribute.get_duration()):
                return True
        return False

    def check_authorization(self, authorization):
        if authorization.nonce != self.nonce:
            logging.warning(f'account_state.py line 49: authorization nonce mismatch the newest nonce '
                            f'{authorization.nonce} vs {str(self.nonce)}')
            return False

        attributes = authorization.attributes
        for attribute in attributes:
            if not self.check_attribute(attribute):
                logging.warning('account_state.py line 56: attribute ' + attribute.get_name() + ' is not matched')
                return False
        return True

    def check_operation(self, operation):
        if operation.nonce != self.nonce:
            logging.warning('account_state.py line 49: authorization nonce mismatch the newest nonce' +
                            str(operation.nonce) + ' vs ' + str(self.nonce))
            return False
        return True

    def increase_nonce(self):
        self.nonce += 1
        return

    def to_json(self):
        attributes_json = []
        for attribute in self.attributes:
            attributes_json.append(attribute.to_json())

        state_account_json = {
            'address': self.address,
            'attributes': attributes_json,
            'nonce': self.nonce
        }
        return state_account_json

    def from_json(self, state_account_json):
        required = ['address', 'attributes', 'nonce', 'code', 'data']
        if not all(k in state_account_json for k in required):
            logging.warning(f"account_state.py line 87: value missing in {required}")
            return False

        if not check_address(state_account_json['address']):
            logging.warning('account_state.py line 93: invalid address in state_account_json')
            return False

        if not isinstance(state_account_json['nonce'], int):
            logging.warning('account_state.py line 98: account_state.py line 111: nonce should be int type')
            return False

        self.attributes = []
        attributes_json = state_account_json['attributes']
        for attribute_json in attributes_json:
            new_attribute = Attribute()
            new_attribute.from_json(attribute_json)
            self.attributes.append(new_attribute)

        self.address = state_account_json['address']
        self.nonce = state_account_json['nonce']
        return True

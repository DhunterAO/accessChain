import copy
import logging

from BLOCKCHAINclass.duration import Duration


class Attribute:
    def __init__(self, name='', duration=None):
        self.name = name
        if duration is not None:
            self.duration = copy.deepcopy(duration)
        else:
            self.duration = Duration()

    def get_name(self):
        return self.name

    def set_name(self, name=''):
        self.name = name

    def get_duration(self):
        return self.duration

    def set_duration(self, duration):
        self.duration = duration

    def to_json(self):
        attribute_json = {
            'name': self.name,
            'duration': self.duration.to_json()
        }
        return attribute_json

    def from_json(self, attribute_json):
        required = ['name', 'duration']
        if not all(k in attribute_json for k in required):
            logging.warning(f"attribute.py line 37: value missing in {required}")
            return False

        if not isinstance(attribute_json['name'], str) or not self.duration.from_json(attribute_json['duration']):
            logging.warning("attribute.py line 39: invalid attribute_json format")
            return False

        self.name = attribute_json['name']
        return True

    def __str__(self):
        return str(self.name) + str(self.duration)


if __name__ == '__main__':
    attr_name = 'student'
    d = Duration()
    a = Attribute(attr_name, d)
    a.set_duration(Duration(200, 1))
    print(a)

    b = Attribute()
    print(b.to_json())
    b.from_json(a.to_json())
    print(b.to_json())
    print(str(b))



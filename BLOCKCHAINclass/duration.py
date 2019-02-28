import logging

from util.tool import current_time


class Duration:
    def __init__(self, end=-1, start=0):
        self._start = start
        self._end = end

    def get_start(self):
        return self._start

    def get_end(self):
        return self._end

    def set(self, end=-1, start=0):
        self._start = start
        self._end = end

    def contain(self, duration):
        if self._start > duration.get_start():
            logging.warning('duration.py line 23: duration.start is earlier than could')
            return False
        if self._end != -1 and self._end < duration.get_end():
            logging.warning('duration.py line 26: duration.end is later than could')
            return False
        return True

    def contained(self, duration):
        if self._start < duration.get_start():
            logging.warning('duration.py line 32: self.start is earlier than could')
            return False
        if duration.get_end() != -1 and self._end > duration.get_end():
            logging.warning('duration.py line 35: self.end is later than could')
            return False
        return True

    def valid_now(self):
        return self._start <= current_time() and (self._end == -1 or current_time() <= self._end)

    def to_json(self):
        duration_json = {
            'start': self._start,
            'end': self._end
        }
        return duration_json

    def from_json(self, duration_json):
        required = ['start', 'end']
        if not all(k in duration_json for k in required):
            logging.warning(f"duration.py line 52: value missing in {required}")
            return False

        if not isinstance(duration_json['start'], int):
            logging.warning(f"duration.py line 56: start time should be type<int>, but " + str(type(duration_json['start'])))
            return False

        if not isinstance(duration_json['end'], int):
            logging.warning("duration.py line 60: end time should be type<int>, but " + str(type(duration_json['end'])))
            return False

        self._start = duration_json['start']
        self._end = duration_json['end']
        return True

    def __str__(self):
        return str(self._start) + str(self._end)


if __name__ == '__main__':
    d = Duration(1000)
    print(d.to_json())
    d.set(10000000000000000, 20)
    print(d.to_json())

    c = Duration()
    print(c.to_json())
    c.from_json(d.to_json())
    print(c.to_json())

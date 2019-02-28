import threading
import time


def fun_timer():
    print('Hello Timer!')
    global timer
    timer = MyTimer(1, fun_timer)
    timer.start()


class MyTimer:
    def __init__(self, name, interval, f):
        self.interval = interval
        self.f = f
        self.name = name
        self.timer = None
        return

    def start(self, interval=None, args=None):
        if interval is None:
            interval = self.interval
        if args is None:
            self.timer = threading.Timer(interval, self.f)
        else:
            self.timer = threading.Timer(interval, self.f, args)

        self.timer.start()
        print(self.name + ' timer ' + ' started,' + str(interval) + 's later will run ' + self.f.__name__)
        return

    def stop(self):
        if self.timer is not None:
            self.timer.cancel()
        print(self.name + ' timer ' + 'stop ', self.f.__name__)
        return

    def restart(self, interval=None, args=None):
        self.stop()
        self.start(interval, args)
        return


if __name__ == '__main__':
    timer = MyTimer(1, fun_timer)
    timer.start()
    # time.sleep(3)
    # timer.stop()
    # time.sleep(3)
    # timer.start()
    # time.sleep(3)
    # timer.stop()
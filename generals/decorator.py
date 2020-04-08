from functools import wraps
from datetime import datetime


def logged(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        print(f'[{datetime.now().isoformat()}] Before calling {f.__name__}()')
        result = f(*args, **kwargs)
        print(f'[{datetime.now().isoformat()}] After {f.__name__}() called')
        return result
    return wrapper

class logged:
    _logfile = 'out.log'

    def __init__(self, f):
        self.f = f

    def __call__(self, *args, **kwargs):
        logstr = f'[{datetime.now().isoformat()}] Calling {self.f.__name__}()'
        with open(self._logfile, 'a') as file:
            file.write(logstr + '\n')
        self.notify(logstr)
        return self.f(*args)

    def notify(self, logstr):
        print(logstr)


if __name__ == "__main__":
    logged._logfile ='log'

    @logged
    def f1():
        pass

    f1()
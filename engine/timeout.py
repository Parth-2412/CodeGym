import signal

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException()

# Set the signal handler
signal.signal(signal.SIGALRM, timeout_handler)

def timeout(timeout):
    def wrapper(func):
        def execute(*args,**kwargs):
            signal.alarm(timeout)  # seconds
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)  # disable alarm
            return result
        return execute
    return wrapper
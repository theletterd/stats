from functools import wraps

class StatException(Exception): pass


def stat_exception_override(error_message):
    
    def callable(func):
        
        @wraps(func)
        def wrapped(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(e)
                raise StatException(error_message)
        return wrapped

    return callable


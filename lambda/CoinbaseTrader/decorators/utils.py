import time

def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        execution_time = 'Function: %r Executed Time: %2.2f ms' % (method.__name__, (te - ts) * 1000)
        print(execution_time)
        return result
    return timed

import urllib3


def get_pool_manager():
    return urllib3.PoolManager()

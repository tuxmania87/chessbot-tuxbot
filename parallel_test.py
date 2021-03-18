import ray


@ray.remote
def rec(x):
    print(x)
    return -x




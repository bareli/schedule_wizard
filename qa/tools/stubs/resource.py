RLIMIT_NOFILE=7
def getrlimit(*a):
    return (4096, 4096)
def setrlimit(*a):
    return None

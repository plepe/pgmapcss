import pghstore

def format(value):
    return pghstore.dumps(value).replace("'", "''")

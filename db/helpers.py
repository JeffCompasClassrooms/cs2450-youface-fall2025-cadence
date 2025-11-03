import tinydb
# IMPORTANT: Import Query to ensure the environment for TinyDB is fully set up
from tinydb import Query 

def load_db():
    return tinydb.TinyDB('db.json', sort_keys=True, indent=4, separators=(',', ': '))

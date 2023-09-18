import logging
from datetime import datetime
from hashlib import sha256

from pymongo import MongoClient
from pymongo.errors import PyMongoError

log = logging.getLogger(__name__)


class MongoCache(object):
    """Implements the httplib2 cache interface for mongodb.

    Note: this class does not provide a way to delete entries from the cache.
    You should implement your own way to delete entries from the cache,
    e.g. by using a TTL index.
    """

    def __init__(self, uri, database, collection):
        self.client = MongoClient(host=uri)
        self.database = database
        self.collection = collection
        self.id_f = lambda x: sha256(x.encode("utf-8")).hexdigest()

    def get(self, key):
        retval = None
        try:
            coll = self.client.get_database(self.database).get_collection(
                self.collection
            )
            retval = coll.find_one({"_id": self.id_f(key)})
            if not retval:
                return None
            return retval.get("value")
        except PyMongoError:
            log.exception(f"ERROR getting {key=}")
        return retval

    def set(self, key, value):
        try:
            coll = self.client.get_database(self.database).get_collection(
                self.collection
            )
            coll.update_one(
                filter={"_id": self.id_f(key)},
                update={"$set": {"value": value, "uri": key, "ts": datetime.utcnow()}},
                upsert=True,
            )
        except PyMongoError:
            log.exception(f"ERROR setting {key=}")

    def delete(self, key):
        try:
            coll = self.client.get_database(self.database).get_collection(
                self.collection
            )
            coll.delete_one({"_id": self.id_f(key)})
        except PyMongoError:
            log.exception(f"ERROR deleting {key=}")

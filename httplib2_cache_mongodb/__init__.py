import email
import json
import logging
from datetime import datetime
from hashlib import sha256

from pymongo import MongoClient
from pymongo.errors import PyMongoError

log = logging.getLogger(__name__)


def parse_http_response(response: bytes):
    info, content = response.split(b"\r\n\r\n", 1)
    info = email.message_from_bytes(info)
    return dict(info), content


def get_json_content(value):
    try:
        headers, content = parse_http_response(value)
        if headers.get("content-type", "").startswith("application/json"):
            return json.loads(content.decode("utf-8"))
    except Exception:
        log.exception(f"ERROR parsing content  {value=}")
        return


class MongoCache(object):
    """Implements the httplib2 cache interface for mongodb.

    Note: this class does not provide a way to delete entries from the cache.
    You should implement your own way to delete entries from the cache,
    e.g. by using a TTL index.
    """

    def __init__(self, uri, database, collection, store_json=False):
        self.id_f = lambda x: sha256(x.encode("utf-8")).hexdigest()
        self.client = MongoClient(host=uri)
        self.database = database
        self.collection = collection
        self.store_json = store_json

    @property
    def _default_collection(self):
        return self.client.get_database(self.database).get_collection(self.collection)

    def _raw_get(self, key):
        return self._default_collection.find_one({"_id": self.id_f(key)})

    def get(self, key):
        retval = None
        try:
            retval = self._default_collection.find_one({"_id": self.id_f(key)})
            if not retval:
                return None
            return retval.get("value")
        except PyMongoError:
            log.exception(f"ERROR getting {key=}")
        return retval

    def set(self, key, value):
        update = {"value": value, "uri": key, "ts": datetime.utcnow()}
        if self.store_json:
            if json_content := get_json_content(value):
                update["json_content"] = json_content

        try:
            self._default_collection.update_one(
                filter={"_id": self.id_f(key)},
                update={"$set": update},
                upsert=True,
            )
        except PyMongoError:
            log.exception(f"ERROR setting {key=}")

    def delete(self, key):
        try:
            self._default_collection.delete_one({"_id": self.id_f(key)})
        except PyMongoError:
            log.exception(f"ERROR deleting {key=}")

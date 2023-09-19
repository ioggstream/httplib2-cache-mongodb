import email
import email.utils
import os
import uuid
from time import sleep
from urllib.parse import urlencode

import httplib2
import pytest

from httplib2_cache_mongodb import MongoCache


def parse_http_response(response: bytes):
    info, content = response.split(b"\r\n\r\n", 1)
    info = email.message_from_bytes(info)
    return dict(info), content


@pytest.fixture
def cache():
    failfast_params = urlencode(
        {
            "connectTimeoutMS": 1000,
            "serverSelectionTimeoutMS": 1000,
            "socketTimeoutMS": 1000,
        }
    )
    uri = f'{os.environ["TEST_MONGODB_URI"]}/?{failfast_params}'
    database_name = f"httplib2_{uuid.uuid4()}"
    collection_name = f"cache_{uuid.uuid4()}"
    cache = MongoCache(
        uri=uri,
        database=database_name,
        collection=collection_name,
    )
    yield cache
    cache.client.drop_database(database_name)


@pytest.fixture
def http(cache) -> httplib2.Http:
    return httplib2.Http(cache=cache)


def test_mongocache_does_not_work_with_post(http: httplib2.Http, cache):
    url = "https://postman-echo.com/post"
    response, content = http.request(
        url,
        "POST",
        body="foo1=bar1&foo2=bar2",
        headers={
            "cache-control": "public, max-age=860000",
            "content-type": "application/x-www-form-urlencoded",
        },
    )
    assert response.status == 200

    entry = cache.get(url)
    assert entry is None


def test_mongocache_populates_and_uses_cache(http, cache):
    url = "https://postman-echo.com/get?foo1=bar1&foo2=bar2"
    headers = {"cache-control": "max-age=860000"}
    response, _ = http.request(url, "GET", headers=headers)
    assert response.status == 200
    entry = cache.get(url)
    assert entry is not None

    response, _ = http.request(url, "GET", headers=headers)
    cache_headers, _ = parse_http_response(entry)
    assert cache_headers["date"] == response["date"]
    assert cache_headers.get("etag") == response.get("etag")


def test_mongocache_respects_no_cache(http, cache):
    url = "https://postman-echo.com/get?foo1=bar1&foo2=bar2"
    headers = {"cache-control": "no-cache"}

    # cache.delete(url)
    assert cache.get(url) is None

    response, _ = http.request(url, "GET", headers=headers)
    assert response.status == 200
    entry = cache.get(url)
    assert entry is not None

    sleep(1)
    response, _ = http.request(url, "GET", headers=headers)
    cache_headers, _ = parse_http_response(entry)
    assert cache_headers["date"] != response["date"]
    assert cache_headers.get("etag") != response.get("etag")


def test_store_json_content(http, cache):
    cache.store_json = True

    url = "https://postman-echo.com/get?foo1=bar1&foo2=bar2"
    headers = {"cache-control": "max-age=860000"}
    response, _ = http.request(url, "GET", headers=headers)
    assert response.status == 200
    entry = cache._raw_get(url)
    assert entry is not None

    assert entry["json_content"] is not None
    assert entry["json_content"]["args"] == {"foo1": "bar1", "foo2": "bar2"}

# Mongo cache for httplib2

A mongodb cache for httplib2.

## Installation

```bash
pip install httplib2_cache_mongo
```

## Usage

```python
from httplib2 import Http
from httplib2_cache_mongo import MongoCache

# Configure your cache.
cache = MongoCache(uri='mongodb://localhost:27017/cache-db', collection='cache')
client = Http(cache=cache)

# Issue a request
url = 'http://httpbin.org/get'
client.request(url, 'GET', headers={'cache-control': 'max-age=3600'})

entry = cache.get(url)
print(entry)
```

## Contributing

Please, see [CONTRIBUTING.md](CONTRIBUTING.md) for more details on:

- using [pre-commit](CONTRIBUTING.md#pre-commit);
- following the git flow and making good [pull requests](CONTRIBUTING.md#making-a-pr);
- test locally using `docker-compose up test`.
- test CI locally using [`act`](https://github.com/nektos/act)

## Using this repository

You can create new projects starting from this repository,
so you can use a consistent CI and checks for different projects.

Besides all the explanations in the [CONTRIBUTING.md](CONTRIBUTING.md) file, you can use the docker-compose file
(e.g. if you prefer to use docker instead of installing the tools locally)

```bash
docker-compose run pre-commit
```

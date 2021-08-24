"""pyth
Project page: https://pypi.org/project/redis/
GitHub: https://github.com/andymccurdy/redis-py
Install redis library
> pip install redis

Run Redis with Docker:
> docker run --name some-redis-4 -d -p 6379:6379 redis
> docker exec -it some-redis-4 bash
> redis-cli

Set for key 'limit' value of 150 with expiration time 5 s.
> SET limit 150 EX 5
"""
import time
import redis


class RedisConnection:

    def __init__(self, host='127.0.0.1', port=6379):
        self.r = redis.Redis(host, port, db=0, decode_responses=True)

    def get(self, value, default=None):
        return self.r.get(value) or default


if __name__ == '__main__':
    from itertools import count

    rc = RedisConnection()
    c = count(start=1, step=1)

    try:
        while True:
            limit = rc.get('limit')
            print(f'{next(c)}) {limit}')
            time.sleep(0.5)
    except KeyboardInterrupt:
        print('Shutting down...')
    finally:
        print('Done')

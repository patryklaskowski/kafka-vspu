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
import os

import redis


class RedisGateway:

    HOST_KEY = 'REDIS_IP'
    PORT_KEY = 'REDIS_PORT'
    PASSWD_KEY = 'REDIS_PASSWD'

    def __init__(self, host=None, port=None, password=None):
        self.host = host or os.getenv(self.HOST_KEY, None)
        self.port = port or os.getenv(self.PORT_KEY, 6379)
        self.password = password or os.getenv(self.PASSWD_KEY, None)

        self.r = redis.Redis(self.host, self.port, password=self.password, db=0, decode_responses=True)

        try:
            self.r.echo('test_value')
        except redis.exceptions.AuthenticationError:
            raise redis.exceptions.AuthenticationError('Authentication required. Provide password.') from None
        except redis.exceptions.ResponseError:
            raise redis.exceptions.ResponseError('Invalid username-password pair or user is disabled') from None
        except redis.exceptions.ConnectionError:
            raise redis.exceptions.ConnectionError(f'Cannot connect to {self.host}:{self.port}. Connection refused.') from None

    def get(self, value, default=None):
        return self.r.get(value) or default
        

if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-ip', '--redis_ip', type=str, default=None, help='Redis server ip')
    parser.add_argument('-port', '--redis_port', type=int, default=6379, help='Redis server port')
    parser.add_argument('-passwd', '--redis_passwd', type=str, default=None, help='Redis server ip')
    parser.add_argument('-limit_key', '--redis_limit_key', type=str, default='limit', help='Key in Redis to get')
    args = parser.parse_args()

    rg = RedisGateway(host=args.redis_ip, port=args.redis_port, password=args.redis_passwd)

    while True:
        limit = rg.get(args.redis_limit_key)
        print(limit)
        time.sleep(0.5)

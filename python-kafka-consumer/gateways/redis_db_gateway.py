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
import argparse
import time
import os

import redis


class RedisGateway:

    HOST_ENV_KEY = 'REDIS_IP'
    PORT_ENV_KEY = 'REDIS_PORT'
    PASSWD_ENV_KEY = 'REDIS_PASSWD'

    def __init__(self, host=None, port=6379, password=None):
        self.host = host
        self.port = port
        self.password = password

        self.r = redis.Redis(self.host, self.port, password=self.password, db=0, decode_responses=True)
        self._test_connection()

    def __str__(self):
        return f'<{self.__class__.__name__} instance connected to server {self.host}:{self.port}>'

    def _test_connection(self):
        try:
            self.r.echo('test_value')
        except redis.exceptions.AuthenticationError:
            raise redis.exceptions.AuthenticationError('Authentication required. Provide password.') from None
        except redis.exceptions.ResponseError:
            raise redis.exceptions.ResponseError('Invalid username-password pair or user is disabled') from None
        except redis.exceptions.ConnectionError:
            raise redis.exceptions.ConnectionError(f'Cannot connect to {self.host}:{self.port}. Connection refused.') from None

    def get(self, key, default=None, map_type=int):
        return map_type(self.r.get(key)) or default

    @classmethod
    def create_redis_parser(cls):
        """
        Helps to build command line interface common arguments for RedisGateway.

        To combine two parsers use 'parents' argument of argparse.ArgumentParser
        e.g.
            final_parser = argparse.ArgumentParser(conflict_handler='resolve', parents=[parser_A, parser_B])
            args = final_parser.parse_args()
        """
        parser = argparse.ArgumentParser()

        parser.add_argument('--redis_ip', type=str, default=None,
                            help=f'Redis server ip. Possible to use ENV var {cls.HOST_ENV_KEY}.')
        parser.add_argument('--redis_port', type=int, default=None,
                            help=f'Redis server port. Possible to use ENV var {cls.PORT_ENV_KEY}.')
        parser.add_argument('--redis_passwd', type=str, default=None,
                            help=f'Redis server ip. Possible to use ENV var {cls.PASSWD_ENV_KEY}.')

        parser.add_argument('--redis_limit_key', type=str, default='limit', help='Key in Redis to get')

        return parser


if __name__ == '__main__':

    parser = RedisGateway.create_redis_parser()
    args = parser.parse_args()

    # From args or read from ENV variables
    host = args.redis_ip or os.getenv(RedisGateway.HOST_ENV_KEY, '127.0.0.1')
    port = args.redis_port or os.getenv(RedisGateway.PORT_ENV_KEY, 6379)
    passwd = args.redis_passwd or os.getenv(RedisGateway.PASSWD_ENV_KEY)

    rg = RedisGateway(host, port, passwd)
    print(rg)

    while True:
        limit = rg.get(args.redis_limit_key)
        print(limit)
        time.sleep(0.5)

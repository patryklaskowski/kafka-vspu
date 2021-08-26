"""
Reset offset with Kafka CLI:
> kafka-consumer-groups.sh --bootstrap-server 149.81.197.180:9092 \
 --topic example.001.age.sum \
 --group graph-app \
 --reset-offsets --to-earliest --execute
"""

import argparse

from actions.dynamic_line_plot import DynamicLinePlot
from confluent_kafka_consumer.kafka_consumer_thread import MyKafkaConsumerThread

BOOTSTRAP_SERVER = '149.81.197.180:9092'
TOPIC = 'example.001.age.sum'
GROUP_ID = 'graph-app'

conf = {
    'bootstrap.servers': BOOTSTRAP_SERVER,
    'group.id': GROUP_ID,
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False,
}


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int, default=10000, help='Limit line value')
    parser.add_argument('--window', type=int, default=50, help='Window size. Number of visible data points')
    parser.add_argument('--interval_ms', type=int, default=500, help='Wait milliseconds between plot refresh')

    # Redis
    parser.add_argument('--redis', action='store_true')
    parser.add_argument('--redis_ip', type=str, default=None, help='Redis server ip e.g. 127.0.0.1')
    parser.add_argument('--redis_port', type=int, default=6379, help='Redis server port.')
    parser.add_argument('--redis_passwd', type=str, default=None, help='Redis server ip.')
    parser.add_argument('--redis_limit_key', type=str, default='limit', help='Key in Redis to get limit integer value.')

    return parser.parse_args()


if __name__ == '__main__':

    args = parse_args()

    limit_func = None

    # Redis
    if args.redis:
        redis_ip = args.redis_ip
        redis_port = args.redis_port
        redis_passwd = args.redis_passwd
        redis_limit_key = args.redis_limit_key

        from gateways.redis_db_gateway import RedisGateway
        redis_gateway = RedisGateway(host=redis_ip, port=redis_port, password=redis_passwd)

        from functools import partial
        get_limit_from_redis = partial(redis_gateway.get, redis_limit_key)
        limit_func = get_limit_from_redis

    try:

        # Kafka consumer to establish incoming data
        consumer_t = MyKafkaConsumerThread(TOPIC, conf, poll_timeout_s=1,
                                           key_deserializer=lambda x: x.decode('utf-8'),
                                           value_deserializer=lambda x: int.from_bytes(x, 'big'))
        consumer_t.start()

        # Dynamic line plot connected to Kafka server through Kafka consumer
        # If limit_func is provided it's value may be defined dynamically
        dlp = DynamicLinePlot(func=consumer_t.newest_datapoint,
                              limit=args.limit,
                              window_size=args.window,
                              limit_func=limit_func)
        dlp.run(interval_ms=args.interval_ms)

    except KeyboardInterrupt:
        print('Keyboard interrupt, closing...')
    except BaseException as e:
        raise Exception('Unknown exception occurred.') from e
    finally:
        consumer_t.stop()
        consumer_t.join(timeout=10)

    print('\nDone!')

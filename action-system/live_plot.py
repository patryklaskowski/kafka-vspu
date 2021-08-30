"""
Live plot system for VSPU project.
Plots stream of incoming data provided by callable object.
Possible to set limit value (both static and dynamic).

Based on matplotlib

@author: Patryk Jacek Laskowski
"""

import argparse
import os


def create_parser():
    """Parameters specific for live plot"""
    parser = argparse.ArgumentParser()

    bootstrap_server_env_key = 'BOOTSTRAP_SERVER'
    parser.add_argument('--bootstrap_server', type=str, default=os.getenv(bootstrap_server_env_key, '127.0.0.1:9092'),
                        help=f'Kafka bootstrap server e.g. 127.0.0.1:9092. '
                             f'Possible of use {bootstrap_server_env_key} env variable.')

    parser.add_argument('--limit', type=int, default=100, help='Static limit line value')
    parser.add_argument('--window', type=int, default=20, help='Window size. Number of visible data points')
    parser.add_argument('--interval_ms', type=int, default=500, help='Wait milliseconds between plot refresh')

    return parser


if __name__ == '__main__':

    from functools import partial

    from actions.dynamic_line_plot import DynamicLinePlot
    from confluent_kafka_consumer.kafka_consumer_thread import MyKafkaConsumerThread
    from gateways.redis_db_gateway import RedisGateway

    # Read arguments from cli
    parser = create_parser()
    redis_parser = RedisGateway.create_redis_parser()
    # Merge and parse arguments
    final_parser = argparse.ArgumentParser(conflict_handler='resolve', parents=[parser, redis_parser])
    args = final_parser.parse_args()

    # Limit function setup to make possible to change limit dynamically
    limit_func = None
    if args.redis:
        redis_gateway = RedisGateway(args.redis_host, args.redis_port, args.redis_passwd)
        get_limit_from_redis = partial(redis_gateway.get, args.redis_limit_key)
        limit_func = get_limit_from_redis

    BOOTSTRAP_SERVER = args.bootstrap_server
    TOPIC = 'example.001.age.sum'
    GROUP_ID = 'graph-app'

    conf = {
        'bootstrap.servers': BOOTSTRAP_SERVER,
        'group.id': GROUP_ID,
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': False,
    }

    try:
        # Kafka consumer to establish incoming data
        consumer_t = MyKafkaConsumerThread(TOPIC, conf, poll_timeout_s=1,
                                           key_deserializer=lambda x: x.decode('utf-8'),
                                           value_deserializer=lambda x: int.from_bytes(x, 'big'))
        consumer_t.start()

        # Dynamic line plot connected to Kafka server through Kafka consumer
        # If limit_func is provided it's value may be defined dynamically
        live_plot = DynamicLinePlot(func=consumer_t.newest_datapoint,
                                    limit=args.limit,
                                    window_size=args.window,
                                    limit_func=limit_func,
                                    interval_ms=args.interval_ms)
        live_plot.run()

    except KeyboardInterrupt:
        print('Keyboard interrupt, closing...')
    except BaseException as e:
        raise Exception('Unknown exception occurred.') from e
    finally:
        if 'consumer_t' in vars():
            consumer_t.stop()
            consumer_t.join(timeout=10)

    print('\nDone!')

"""
Email notification system for VSPU project.
Send email based on incoming data stream and either dynamic or static limit value.
System sources data from Kafka topic and compare to current limit.
If data value exceeds limit value, sends email.

@Author: Patryk Jacek Laskowski
"""

import argparse
import os


def create_parser():
    parser = argparse.ArgumentParser()

    bootstrap_server_env_key = 'BOOTSTRAP_SERVER'
    parser.add_argument('--bootstrap_server', type=str, default=os.getenv(bootstrap_server_env_key, '127.0.0.1:9092'),
                        help=f'Kafka bootstrap server e.g. 127.0.0.1:9092. '
                             f'Possible of use {bootstrap_server_env_key} env variable.')

    parser.add_argument('--interval_s', type=int, default=1,
                        choices=[1, 5, 10, 60],
                        help='How often validate the data.')
    parser.add_argument('--limit', type=int, default=100,
                        help='Static limit value')

    return parser


if __name__ == '__main__':

    import time

    from datetime import datetime
    from functools import partial

    from actions.send_gmail import Gmail
    from gateways.redis_db_gateway import RedisGateway
    from confluent_kafka_consumer.kafka_consumer_thread import MyKafkaConsumerThread

    # Read arguments from cli
    parser = create_parser()
    gmail_parser = Gmail.create_gmail_parser()
    redis_parser = RedisGateway.create_redis_parser()

    final_parser = argparse.ArgumentParser(conflict_handler='resolve', parents=[parser, gmail_parser, redis_parser])
    args = final_parser.parse_args()

    # Create message sender interface
    gmail = Gmail(args.gmail_user, args.gmail_passwd)

    # Create redis limit key caller
    limit_func = None
    if args.redis:
        redis_gateway = RedisGateway(args.redis_host, args.redis_port, args.redis_passwd)
        limit_func = partial(redis_gateway.get, key=args.redis_limit_key, default=None, map_type=int)
    else:
        limit_func = lambda: args.limit

    BOOTSTRAP_SERVER = args.bootstrap_server
    TOPIC = 'example.001.age.sum'
    GROUP_ID = 'gmail-app'

    conf = {
        'bootstrap.servers': BOOTSTRAP_SERVER,
        'group.id': GROUP_ID,
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': False,
    }

    try:

        # Create Kafka consumer Thread to read incoming data in background
        consumer_t = MyKafkaConsumerThread(TOPIC, conf, poll_timeout_s=1,
                                           key_deserializer=lambda x: x.decode('utf-8'),
                                           value_deserializer=lambda x: int.from_bytes(x, 'big'))
        # Start Kafka consumer Thread (non-blocking)
        consumer_t.start()

        print(f'[{datetime.now().strftime(Gmail.date_format)}] Sleep 3s. to warmup') or time.sleep(3)

        # Create send email loop
        while True:
            recent_max = consumer_t.recent_max_value() or 0
            limit = limit_func()

            print(f'[{datetime.now().strftime(Gmail.date_format)}] '
                  f'Recent max {recent_max} (top{consumer_t.maxlen} values). '
                  f'Limit: {limit}. '
                  f'Interval: {args.interval_s} s.')

            if recent_max > limit:
                gmail.send(to=args.gmail_to,
                           body=args.gmail_message or args.gmail_message_from_file,
                           subject=args.gmail_subject)
                print(f'[{datetime.now().strftime(Gmail.date_format)}] Closing...')
                break
            time.sleep(args.interval_s)

    except KeyboardInterrupt:
        print('Keyboard interrupt, closing...')
    except BaseException as e:
        raise Exception('Unknown exception occurred.') from e
    finally:
        consumer_t.stop()
        consumer_t.join(timeout=10)

    print('\nDone!')

"""
Email notification system for VSPU project.
Send email based on incoming data stream and either dynamic or static limit value.
System sources data from Kafka topic and compare to current limit.
If data value exceeds limit value, sends email.

@Author: Patryk Jacek Laskowski
"""

import argparse
import os


INTERVAL_S_ENV_KEY = 'EMAIL_NOTIFICATION_INTERVAL_S'
LIMIT_ENV_KEY = 'EMAIL_NOTIFICATION_LIMIT'
VERBOSE_ENV_KEY = 'EMAIL_NOTIFICATION_VERBOSE'

DEFAULT_VALUE = 0


def create_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument('--interval_s', type=int, default=os.getenv(INTERVAL_S_ENV_KEY, 1),
                        help='How often validate the data.'
                             f'Possible of use {INTERVAL_S_ENV_KEY} env variable.')

    parser.add_argument('--limit', type=int, default=os.getenv(LIMIT_ENV_KEY),
                        help='Static limit value'
                             f'Possible of use {LIMIT_ENV_KEY} env variable.')

    parser.add_argument('--verbose', action='store_true',
                        default=True if os.getenv(VERBOSE_ENV_KEY) else False,
                        help='Verbose flag for stout.')

    return parser


if __name__ == '__main__':

    import time

    from functools import partial

    from common import log, export_env_var_from, KafkaConfig, CONFIG_FILE
    from actions.send_email.send_gmail import Gmail
    from gateways.redis_db_gateway import RedisGateway
    from confluent_kafka_consumer.kafka_consumer_thread import MyKafkaConsumerThread

    export_env_var_from(CONFIG_FILE)

    # Read arguments from cli
    parser = create_parser()
    kafka_parser = KafkaConfig.create_kafka_parser()
    gmail_parser = Gmail.create_gmail_parser()
    redis_parser = RedisGateway.create_redis_parser()

    final_parser = argparse.ArgumentParser(conflict_handler='resolve',
                                           parents=[parser, kafka_parser, gmail_parser, redis_parser])
    args = final_parser.parse_args()

    # Create message sender interface
    gmail = Gmail(args.gmail_user, args.gmail_passwd)

    # Create redis limit key caller
    limit_func = None
    if args.redis:
        redis_gateway = RedisGateway(args.redis_host, args.redis_port, args.redis_passwd)
        limit_func = partial(redis_gateway.get, key=args.redis_limit_key, default=None, map_type=int)
    elif args.limit:
        limit_func = lambda: args.limit

    TOPIC = 'example.001.age.sum'
    GROUP_ID = 'gmail-app'

    conf = {
        'bootstrap.servers': args.kafka_bootstrap_server,
        'group.id': GROUP_ID,
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': False,
    }

    if args.verbose:
        for key, val in vars(args).items():
            val = str(val).replace("\n", " ")
            log(f'args    {key}: {val}')
        for key, val in conf.items():
            log(f'conf    {key}={val}')

    try:

        # Create Kafka consumer Thread to read incoming data in background
        consumer_t = MyKafkaConsumerThread(TOPIC, conf, poll_timeout_s=1,
                                           key_deserializer=lambda x: x.decode('utf-8'),
                                           value_deserializer=lambda x: int.from_bytes(x, 'big'))
        # Start Kafka consumer Thread (non-blocking)
        consumer_t.start()

        log('Sleep 3s. to warmup') or time.sleep(3)

        # Create send email loop
        while True:
            recent_max = consumer_t.recent_max_value() or DEFAULT_VALUE
            limit = limit_func() or DEFAULT_VALUE

            log(f'Recent max {recent_max} (among top{consumer_t.maxlen} values). '
                f'Limit: {limit}. '
                f'Interval: {args.interval_s} s.')

            if recent_max > limit:
                gmail.send(to=args.gmail_to,
                           body=args.gmail_message or args.gmail_message_from_file,
                           subject=args.gmail_subject)
                log('Closing...')
                break
            time.sleep(args.interval_s)

    except KeyboardInterrupt:
        log('Keyboard interrupt, closing...')
    except BaseException as e:
        raise Exception('Unknown exception occurred.') from e
    finally:
        consumer_t.stop()
        consumer_t.join(timeout=10)

    log('Done!')

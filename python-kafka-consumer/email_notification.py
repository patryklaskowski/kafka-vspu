"""
Reset offset with Kafka CLI:
> kafka-consumer-groups.sh --bootstrap-server 149.81.197.180:9092 \
 --topic example.001.age.sum \
 --group graph-app \
 --reset-offsets --to-earliest --execute
"""

import argparse

BOOTSTRAP_SERVER = '149.81.197.180:9092'
TOPIC = 'example.001.age.sum'
GROUP_ID = 'gmail-app'

conf = {
    'bootstrap.servers': BOOTSTRAP_SERVER,
    'group.id': GROUP_ID,
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False,
}


def create_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument('--interval_s', type=int, default=1,
                        choices=[1, 5, 10, 60],
                        help='How often to try send an email in seconds.')
    parser.add_argument('--maxlen', type=int, default=30,
                        choices=[10, 20, 30, 40, 50, 100],
                        help='Data collector maximum length.')

    return parser


if __name__ == '__main__':

    import time

    from datetime import datetime
    from functools import partial
    from collections import deque

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
    redis_gateway = RedisGateway(args.redis_ip, args.redis_port, args.redis_passwd)
    limit_from_redis = partial(redis_gateway.get, key=args.redis_limit_key, default=None, map_type=int)

    try:

        # Create Kafka consumer Thread to read incoming data in background
        consumer_t = MyKafkaConsumerThread(TOPIC, conf, poll_timeout_s=1,
                                           key_deserializer=lambda x: x.decode('utf-8'),
                                           value_deserializer=lambda x: int.from_bytes(x, 'big'))
        # Start Kafka consumer Thread (non-blocking)
        consumer_t.start()

        # Create send email loop
        received_data = deque(maxlen=args.maxlen)
        # TODO: Same for redis - to prevent delays. Create list and collect future objects tat eventually become values
        while True:
            # TODO: Not sure if received_data is necessary
            received_data.append(consumer_t.newest_datapoint() or 0)
            recent_max = max(received_data)
            limit = limit_from_redis()  # redis call through web. Might cause delays
            print(f'[{datetime.now().strftime(Gmail.date_format)}] '
                  f'Max top{args.maxlen} last values: {recent_max}. '
                  f'Last value: {received_data[-1]}.'
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

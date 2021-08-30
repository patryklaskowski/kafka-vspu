"""
Kafka-Python based Kafka producer.
Produces messages into Kafka topic.
Built to mockup data for testing purposes.

@Author: Patryk Jacek Laskowski
"""
import json
import time
import random
import argparse
import os

from datetime import datetime
from kafka import KafkaProducer

from common import KafkaDeliveryCallback


def log(msg, date_format='%m/%d/%Y %H:%M:%S', return_msg=False):
    message = f'[{datetime.now().strftime(date_format)}] {msg}'
    if return_msg:
        return message
    print(message)


def parse_args():
    parser = argparse.ArgumentParser()

    bootstrap_server_env_key = 'BOOTSTRAP_SERVER'
    parser.add_argument('--bootstrap_server', type=str, default=os.getenv(bootstrap_server_env_key, '127.0.0.1:9092'),
                        help=f'Kafka bootstrap server e.g. 127.0.0.1:9092. '
                             f'Possible of use {bootstrap_server_env_key} env variable.')

    # Manual
    parser.add_argument('--manual', action='store_true', required=False,
                        help='Flag to determine manual data producing')
    # or automatic
    parser.add_argument('--n', type=int, default=20, help='Number of messages to send')
    parser.add_argument('-s', '--sleep', type=float, default=0.0, help='Time to sleep between sends')
    parser.add_argument('--min', type=int, default=0, help='Lower bound of random value')
    parser.add_argument('--max', type=int, default=10, help='Upper bound of random value')

    return parser.parse_args()


def generate_record(number):
    """
    Value structure for Kafka topic which is exact feeder of sumTheAge Kafka Streams app.
    e.g. {'name': 'Patryk_13', 'surname': 'Laskowski_13', 'age': 13}
    """
    assert isinstance(number, int), 'number argument must be integer type'
    return dict(name=f'Patryk_{number}', surname=f'Laskowski_{number}', age=number)


def generate_random_record(lower_limit, upper_limit):
    number = random.randint(int(lower_limit), int(upper_limit))
    return generate_record(number)


def send_manually_with(producer):
    i = 1
    while True:
        number = input(f'{log("Input value and press Enter to send (q to quit):", return_msg=True)}')
        if number == 'q':
            break
        try:
            number = int(number)
        except ValueError:
            print(f'Provided value must be number. Provided {number}, try again.')
            number = None
        else:
            value = generate_record(number)
            future = producer.send(topic=TOPIC, key=KEY, value=value, partition=None)\
                .add_callback(f=KafkaDeliveryCallback.print_metadata, value=value, before=log(msg='', return_msg=True))\
                .add_errback(f=KafkaDeliveryCallback.handle_exception, value=value, before=log(msg='', return_msg=True))

            log(f'{str(i).zfill(3)}) value {value} synchronously. Waiting for future.\n'
                f'{"-" * 42}')
            future.get(timeout=30)
            i += 1


def send_automatically_with(producer, n, lower_limit, upper_limit, seconds):
    for i in range(1, n + 1):
        value = generate_random_record(lower_limit, upper_limit)
        producer.send(topic=TOPIC, key=KEY, value=value, partition=None)\
            .add_callback(f=KafkaDeliveryCallback.print_metadata, value=value, before=log(msg='', return_msg=True))\
            .add_errback(f=KafkaDeliveryCallback.handle_exception, value=value, before=log(msg='', return_msg=True))

        log(f'{str(i).zfill(3)}) value {value} asynchronously. Waiting for callback.\n'
            f'{"-" * 42}')
        time.sleep(seconds)


if __name__ == '__main__':

    args = parse_args()

    ##########################################
    TOPIC = 'example.001'
    BOOTSTRAP_SERVER = args.bootstrap_server
    KEY = 'cam-001-example-001'
    ##########################################

    log(f'Bootstrap server: {BOOTSTRAP_SERVER}, topic: {TOPIC}, key: {KEY}')

    config = dict(
        bootstrap_servers=[BOOTSTRAP_SERVER],
        key_serializer=lambda x: x.encode('utf-8'),
        value_serializer=lambda x: json.dumps(x).encode('utf-8'),
        acks=1,
        retries=3,
        max_in_flight_requests_per_connection=1
    )

    producer = KafkaProducer(**config)
    log(f'Producer connected: {producer.bootstrap_connected()}')

    start = time.perf_counter()
    try:

        if args.manual:
            send_manually_with(producer)
        else:
            send_automatically_with(producer, args.n, args.min, args.max, args.sleep)

    except KeyboardInterrupt:
        print('Keyboard interruption.')
    except BaseException as e:
        raise Exception(f'Unexpected exception occurred') from e
    finally:
        log('Flushing messages...')
        producer.flush(timeout=30)  # block until all async messages are sent
        log(f'Elapsed time: {round(time.perf_counter() - start, 2)} seconds.')
        log('Closing producer...')
        producer.close(timeout=30)

    log('Done!')

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

from kafka.errors import NoBrokersAvailable
from kafka import KafkaProducer

from common import KafkaDeliveryCallback, log, export_env_var_from, CONFIG_FILE


BOOTSTRAP_SERVER_ENV_KEY = 'BOOTSTRAP_SERVER'
KAFKA_TOPIC_ENV_KEY = 'KAFKA_TOPIC'

MANUAL_FLAG_ENV_EKY = 'MANUAL_FLAG'
N_MESSAGES_ENV_KEY = 'N_MESSAGES'
SLEEP_ENV_KEY = 'SLEEP'
MIN_RANDOM_VAL_ENV_KEY = 'MIN_RANDOM_VAL'
MAX_RANDOM_VAL_ENV_KEY = 'MAX_RANDOM_VAL'


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--bootstrap_server', type=str,
                        default=os.getenv(BOOTSTRAP_SERVER_ENV_KEY, '127.0.0.1:9092'),
                        help=f'Kafka bootstrap server e.g. 127.0.0.1:9092. '
                             f'Possible of use {BOOTSTRAP_SERVER_ENV_KEY} env variable.')
    parser.add_argument('--kafka_topic', type=str,
                        default=os.getenv(KAFKA_TOPIC_ENV_KEY),
                        help=f'Kafka topic to connect.'
                             f'Possible of use {KAFKA_TOPIC_ENV_KEY} env variable.')

    # Manual
    parser.add_argument('--manual', action='store_true',
                        default=True if os.getenv(MANUAL_FLAG_ENV_EKY) else False,
                        help='Flag to determine manual data producing'
                             f'Possible of use {MANUAL_FLAG_ENV_EKY} env variable.')
    # or automatic
    parser.add_argument('--n_messages', type=int,
                        default=os.getenv(N_MESSAGES_ENV_KEY, 20),
                        help='Number of messages to send.'
                             f'Possible of use {N_MESSAGES_ENV_KEY} env variable.')
    parser.add_argument('-s', '--sleep', type=float,
                        default=os.getenv(SLEEP_ENV_KEY, 0),
                        help='Time to sleep between sends.'
                             f'Possible of use {SLEEP_ENV_KEY} env variable.')
    parser.add_argument('--min_random_val', type=int,
                        default=os.getenv(MIN_RANDOM_VAL_ENV_KEY, 0),
                        help='Lower bound of random value.'
                             f'Possible of use {MIN_RANDOM_VAL_ENV_KEY} env variable.')
    parser.add_argument('--max_random_val', type=int,
                        default=os.getenv(MAX_RANDOM_VAL_ENV_KEY, 10),
                        help='Upper bound of random value.'
                             f'Possible of use {MAX_RANDOM_VAL_ENV_KEY} env variable.')

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

            log(f'{str(i).zfill(3)}) value {value} synchronously. Waiting for future.')
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

    export_env_var_from(CONFIG_FILE)

    args = parse_args()

    for key, val in vars(args).items():
        log(f'args    {key}: {val}')

    ##########################################
    TOPIC = args.kafka_topic
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

    try:
        producer = KafkaProducer(**config)
    except NoBrokersAvailable as e:
        raise NoBrokersAvailable(f'Cannot connect to broker {config["bootstrap_servers"]}.') from None

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

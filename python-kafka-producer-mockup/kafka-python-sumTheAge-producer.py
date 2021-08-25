"""
Run Threaded Producer

https://github.com/dpkp/kafka-python/blob/master/example.py
"""
import json
import time
import random
import argparse

from kafka import KafkaProducer


class Message:
    """
    JSON creator.
    e.g. {"name": "Patryk_3", "surname": "Laskowski_3", "age": 17}
    """
    def __init__(self, name, surname, age):
        self.name = str(name)
        self.surname = str(surname)
        self.age = int(age)


class Callback:
    """Callbacks for message delivery"""
    @staticmethod
    def print_metadata(record_metadata, *args, **kwargs):
        val = kwargs.get('value', '>not provided<')

        print(f'SUCCESS! Record sent successfully. Record Metadata:'
              f' topic={record_metadata.topic},'
              f' partition= {record_metadata.partition},'
              f' offset={record_metadata.offset}\n'
              f'\tvalue: {val}')

    @staticmethod
    def handle_exception(exception, *args, **kwargs):
        val = kwargs.get('value', '>not provided<')

        print(f'ERROR! Failed to send record with value: {val}\n'
              f'\tException: {exception}')


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', type=int, default=50, help='number of messages to send')
    parser.add_argument('-s', '--sleep', type=float, default=0.0, help='time to sleep between sends')
    parser.add_argument('--min', type=int, default=0, help='Lower bound of random value')
    parser.add_argument('--max', type=int, default=10, help='Upper bound of random value')

    return parser.parse_args()


def generate_record(lower_limit, upper_limit):
    lower_limit = int(lower_limit)
    upper_limit = int(upper_limit)
    number = random.randint(lower_limit, upper_limit)
    msg = Message(name=f'Patryk_{number}',
                  surname=f'Laskowski_{number}',
                  age=number)
    return vars(msg)


if __name__ == '__main__':

    ##########################################
    TOPIC = 'example.001'
    BOOTSTRAP_SERVER = '149.81.197.180:9092'
    KEY = 'cam-001-example-001'
    ##########################################

    args = parse_args()
    n = args.n
    seconds = args.sleep
    min = args.min
    max = args.max

    config = dict(
        bootstrap_servers=[BOOTSTRAP_SERVER],
        key_serializer=lambda x: x.encode('utf-8'),
        value_serializer=lambda x: json.dumps(x).encode('utf-8'),
        acks=1,
        retries=3,  # default: 2147483647
        max_in_flight_requests_per_connection=1,  # default: 5
        # client_id='kafka-python-producer-13',
    )

    producer = KafkaProducer(**config)
    print(f'Producer connected: {producer.bootstrap_connected()}')

    try:

        start = time.perf_counter()
        for i in range(1, n+1):
            value = generate_record(lower_limit=min, upper_limit=max)

            producer.send(topic=TOPIC, key=KEY, value=value, partition=None)\
                .add_callback(f=Callback.print_metadata, value=value)\
                .add_errback(f=Callback.handle_exception, value=value)

            before = f'{str(i).zfill(3)}) '
            print(f'{before}Record has been sent asynchronously. Waiting for response.\n'
                  f'{"-"*len(before)}{value}')
            time.sleep(seconds)

        print(f'Async elapsed time: {round(time.perf_counter() - start, 2)} s.')

        print('Flushing messages...')
        # block until all async messages are sent
        producer.flush(timeout=30)
        print(f'Sent {n} records in {round(time.perf_counter() - start, 2)} seconds total.')

    except Exception as e:
        print(f'Exception occurred: {e}')
    finally:
        print('Closing producer')
        producer.close(timeout=30)

    # kafka-console-consumer.sh --bootstrap-server 149.81.197.180:9092 --topic example.001 --from-beginning

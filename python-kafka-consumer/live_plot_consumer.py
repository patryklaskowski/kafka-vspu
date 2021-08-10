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
    parser.add_argument('--interval', type=int, default=100, help='Wait milliseconds between plot refresh')

    return parser.parse_args()


if __name__ == '__main__':

    args = parse_args()
    limit = args.limit
    window = args.window
    interval = args.interval

    try:
        consumer_t = MyKafkaConsumerThread(TOPIC, conf, poll_timeout_s=1,
                                           key_deserializer=lambda x: x.decode('utf-8'),
                                           value_deserializer=lambda x: int.from_bytes(x, 'big'))
        consumer_t.start()

        dlp = DynamicLinePlot(consumer_t.newest_datapoint, limit=limit, window_size=window)
        dlp.run(interval_ms=interval)
    except KeyboardInterrupt:
        print('Keyboard interrupt, closing...')
        consumer_t.stop()
    except Exception as e:
        print(f'Exception occured: {e}')
        consumer_t.stop()
    finally:
        consumer_t.stop()
        consumer_t.join(timeout=10)
    print('Done!')

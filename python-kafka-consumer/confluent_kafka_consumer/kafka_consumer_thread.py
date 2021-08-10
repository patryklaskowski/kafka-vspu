"""
Uses confluent_kafka
"""

import time

from confluent_kafka import Consumer
from confluent_kafka.error import KafkaError, KafkaException
from threading import Thread, Event
from collections import deque


class MyKafkaConsumerThread(Thread):
    """Consumer thread subscribes to Kafka topic and polls for data until `_stop_event` is not set.
    Data is held in `data` deque with size of `window_size`

    To get the data read it right from `data` deque or use `.newest_datapoint()` function
    """

    _population = 0

    def __init__(self, topic, conf, poll_timeout_s=1, window_size=10, name=None, **kwargs):
        """
        :param topic:
        :param conf:
        :param poll_timeout_s:
        :param window_size:
        :param name:
        :param kwargs: key_deserializer, value_deserializer
        """
        Thread.__init__(self)

        self.topic = topic
        self.consumer = Consumer(**conf)
        self.poll_timeout_s = int(poll_timeout_s)
        # Deque data container
        self.data = deque(maxlen=window_size)
        self.name = name or f'MyConsumer-Thread-{self._population}'

        self.key_deserializer_fn = kwargs.get('key_deserializer', lambda x: x)
        self.value_deserializer_fn = kwargs.get('value_deserializer', lambda x: x)

        self._stop_event = Event()
        self._population += 1

        print(f'[{self.name}] Thread named {self.name} has been initialized.')

    def stop(self):
        """Stop event triggers data sourcing loop off"""
        print(f'[{self.name}] Stopping thread...')
        self._stop_event.set()

    def start(self):
        """Overwrites original Threads .start() function to make it easier to run
        This invokes the run() method in a separate thread of control.

        RuntimeError if called more than once on the same thread object."""
        super().start()
        return self

    def _consume_data(self):
        """Poll data from Kafka topic
        If no errors returns message """
        message = self.consumer.poll(timeout=self.poll_timeout_s)

        if not message:
            return

        if message.error():
            if message.error().code() == KafkaError._PARTITION_EOF:
                # End of partition event
                print(f'{message.topic()} [{message.partition()}] reached end at offset {message.offset()}.\n')
            elif message.error():
                raise KafkaException(message.error())
        else:
            print(f'[{self.name}] Received message ['
                  f'topic: {message.topic()}, '
                  f'partition: {message.partition()}, '
                  f'offset: {message.offset()}]: '
                  f'{self.key_deserializer_fn(message.key())}, {self.value_deserializer_fn(message.value())}')
            return message

    def run(self):
        """Subscribe and run consume loop that fills `data` queue."""
        try:
            self.consumer.subscribe([self.topic],
                                    on_assign=lambda *args: print(f'[{self.name}] Subscription callback: '
                                                                  f'Subscribed topic {self.topic}| args: {args}'),
                                    on_revoke=lambda *args: print(f'[{self.name}] Subscription callback: '
                                                                  f'Revoking topic {self.topic}| args: {args}'),
                                    on_lost=lambda *args: print(f'[{self.name}] Subscription callback: '
                                                                f'Lost topic {self.topic}| args: {args}'))

            while not self._stop_event.is_set():
                msg = self._consume_data()  # Raises Exceptions
                if msg: self.data.append((self.key_deserializer_fn(msg.key()),
                                          self.value_deserializer_fn(msg.value())))

        except KeyboardInterrupt:
            print(f'[{self.name}] Keyboard interruption')
        except Exception as e:
            print(f'[{self.name}] Exception occured: {e}')
        finally:
            print(f'[{self.name}] Closing consumer gracefully')
            self.consumer.close()

    def newest_datapoint(self, value_only=True):
        """Returns the newest datapoint. None if `data` is empty"""
        x = self.data[-1] if len(self.data) > 0 else None
        if x and value_only:
            return x[1]
        return x


if __name__ == '__main__':

    BOOTSTRAP_SERVER = '149.81.197.180:9092'
    TOPIC = 'example.001.age.sum'
    GROUP_ID = 'graph-app'

    conf = {
        'bootstrap.servers': BOOTSTRAP_SERVER,
        'group.id': GROUP_ID,
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': False,
    }

    consumer_t = MyKafkaConsumerThread(TOPIC, conf, poll_timeout_s=1,
                                       key_deserializer=lambda x: x.decode('utf-8'),
                                       value_deserializer=lambda x: int.from_bytes(x, 'big')).start()

    print('Sleeping...')
    time.sleep(2)
    for _ in range(5):
        print(consumer_t.newest_datapoint())
        time.sleep(0.2)

    print('Stopping')
    consumer_t.stop()
    consumer_t.join(timeout=20)
    print('Done!')

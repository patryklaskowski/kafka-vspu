import argparse
import os


LIMIT_ENV_KEY = 'DASH_LIVE_PLOT_LIMIT'
WINDOW_ENV_KEY = 'DASH_LIVE_PLOT_WINDOW'
INTERVAL_MS_ENV_KEY = 'DASH_LIVE_PLOT_INTERVAL_MS'


def create_parser():
    """Parameters specific for dash live plot"""
    parser = argparse.ArgumentParser()

    parser.add_argument('--limit', type=int,
                        default=os.getenv(LIMIT_ENV_KEY),
                        help='Static limit line value'
                             f'Possible use of {LIMIT_ENV_KEY} env variable.')
    parser.add_argument('--window', type=int,
                        default=os.getenv(WINDOW_ENV_KEY, 100),
                        help='Window size. Number of visible data points'
                             f'Possible use of {WINDOW_ENV_KEY} env variable.')
    parser.add_argument('--interval_ms', type=int,
                        default=os.getenv(INTERVAL_MS_ENV_KEY, 200),
                        help='Wait milliseconds between plot refresh'
                             f'Possible use of {INTERVAL_MS_ENV_KEY} env variable.')

    return parser


if __name__ == '__main__':

    from functools import partial

    from common import export_env_var_from, log, KafkaConfig, CONFIG_FILE
    from actions.dash_live_plot.live_plot import DashDynamicLinePlot
    from confluent_kafka_consumer.kafka_consumer_thread import MyKafkaConsumerThread
    from gateways.redis_db_gateway import RedisGateway

    export_env_var_from(CONFIG_FILE, verbose=0)

    parser = create_parser()
    kafka_parser = KafkaConfig.create_kafka_parser()
    redis_parser = RedisGateway.create_redis_parser()
    final_parser = argparse.ArgumentParser(conflict_handler='resolve', parents=[parser, kafka_parser, redis_parser])
    args = final_parser.parse_args()

    TOPIC = 'example.001.age.sum'
    GROUP_ID = 'graph-app'

    conf = {
        'bootstrap.servers': args.kafka_bootstrap_server,
        'group.id': GROUP_ID,
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': False,
    }

    for key, val in conf.items():
        log(f'conf   {key}={val}')

    limit_func = None
    if args.redis:
        redis_gateway = RedisGateway(args.redis_host, args.redis_port, args.redis_passwd)
        limit_func = partial(redis_gateway.get, args.redis_limit_key, default=None, map_type=int)
    elif args.limit:
        limit_func = lambda: args.limit

    try:
        # Kafka consumer to establish incoming data
        consumer_t = MyKafkaConsumerThread(TOPIC, conf, poll_timeout_s=1,
                                           key_deserializer=lambda x: x.decode('utf-8'),
                                           value_deserializer=lambda x: int.from_bytes(x, 'big'))
        consumer_t.start()

        plot = DashDynamicLinePlot(func=consumer_t.newest_datapoint,
                                   limit_func=limit_func,
                                   max_len=args.window,
                                   interval_ms=args.interval_ms)
        plot.run(host='0.0.0.0', port=8050, debug=False)

    except KeyboardInterrupt:
        log('Keyboard interrupt, closing...')
    except BaseException as e:
        raise Exception('Unknown exception occurred.') from e
    finally:
        if 'consumer_t' in vars():
            consumer_t.stop()
            consumer_t.join(timeout=10)

    log('Done!')

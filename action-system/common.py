import os
import yaml
import argparse

from datetime import datetime


CONFIG_FILE = 'config.yaml'


class KafkaConfig:

    BOOTSTRAP_SERVER_ENV_KEY = 'BOOTSTRAP_SERVER'

    @classmethod
    def create_kafka_parser(cls):
        parser = argparse.ArgumentParser()

        # Required if env variable not specified
        parser.add_argument('--kafka_bootstrap_server',
                            default=os.getenv(cls.BOOTSTRAP_SERVER_ENV_KEY, '127.0.0.1:9092'),
                            type=str,
                            action=None,
                            help=f'Bootstrap server <ip>:<port> for connection with Kafka e.g. 127.0.0.1:9092'
                                 f'Possible use of {cls.BOOTSTRAP_SERVER_ENV_KEY} env variable.')

        return parser


def log(msg, date_format='%m/%d/%Y %H:%M:%S', return_str=False):
    """
    Logging function to standardize stdout
    """
    txt = f'[{datetime.now().strftime(date_format)}] {msg}'
    if return_str:
        return txt
    print(txt)


def export_env_var_from(config_file, verbose=0):
    """
    Exports environmental variables based on configuration (YAML) file
    """
    log(f'Exporting env variables based on {config_file}')
    # Read
    with open(config_file, 'r') as f:
        conf = yaml.safe_load(f)

    # Export
    iterator = iter(walk_trough_nested(conf, verbose=verbose))
    while True:
        try:
            key, value = next(iterator)
            if not value:
                continue
            os.environ[key] = str(value)
            if not verbose:
                log(f'from {config_file} export {key}={value}')
        except StopIteration:
            break


def walk_trough_nested(dictionary, level=0, verbose=0):
    """
    Recursively walks through nested dict-like structure
    Returns non-nested key, value pairs.
    """
    prefix = level * '    '
    for key, val in dictionary.items():
        if isinstance(val, dict):
            if verbose:
                log(f'{prefix} {key}:')
            yield from iter(walk_trough_nested(dictionary=val, level=level+1, verbose=verbose))
        else:
            if verbose:
                log(f'{prefix} {key}: {val}')
            yield key, val


if __name__ == '__main__':
    export_env_var_from('config.yaml')

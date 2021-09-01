import os
import yaml

from datetime import datetime


CONFIG_FILE = 'config.yaml'


class KafkaDeliveryCallback:
    """Callbacks for message delivery"""
    @staticmethod
    def print_metadata(record_metadata, *args, **kwargs):
        val = kwargs.get('value', '>not provided<')
        before = kwargs.get('before', '')

        print(f'{before}SUCCESS! Record sent successfully. Record Metadata:'
              f'topic={record_metadata.topic}, '
              f'partition={record_metadata.partition}, '
              f'offset={record_metadata.offset}, '
              f'value={val}')

    @staticmethod
    def handle_exception(exception, *args, **kwargs):
        val = kwargs.get('value', '>not provided<')
        before = kwargs.get('before', '')

        print(f'{before}ERROR! Failed to send record with value: {val}. Exception: {exception}')


def log(msg, date_format='%m/%d/%Y %H:%M:%S', return_msg=False):
    message = f'[{datetime.now().strftime(date_format)}] {msg}'
    if return_msg:
        return message
    print(message)


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

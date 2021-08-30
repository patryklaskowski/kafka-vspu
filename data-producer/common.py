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

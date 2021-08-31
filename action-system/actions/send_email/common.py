import argparse


class JoinNargsCustomAction(argparse.Action):
    """
    Custom action for argparse
    Made with: https://docs.python.org/3/library/argparse.html#action

    Joins nargs arguments list with join_with.
    Converts multiple space separated arguments from cli into single string value.

    Convenient to use like:
        from functools import partial
        join_with_comma = partial(JoinNargsCustomAction, join_with=', ')
    """
    def __init__(self, option_strings, dest, join_with='', **kwargs):
        if not kwargs.get('nargs'):
            raise ValueError(f'nargs argument for {option_strings} in parser.add_argument(...) required!')

        super().__init__(option_strings, dest, **kwargs)
        self.join_with = join_with

    def __call__(self,  er, namespace, values, option_string=None):
        new_values = self.join_with.join(values)
        setattr(namespace, self.dest, new_values)

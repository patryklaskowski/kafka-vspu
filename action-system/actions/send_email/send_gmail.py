"""
Action for notification system action of VSPU project.
Sends email using Gmail SMTP protocol.

@author: Patryk Jacek Laskowski
"""
import argparse
import smtplib
import os

from datetime import datetime
from email.message import EmailMessage


class Gmail:
    """
    Sends emails using Gmail SMTP protocol.

    User is Your Gmail email address.
    Password has to be generated upfront using Google account settings:

    1) Two-step verification has to be turned on first.
    Manage your Google Account > Security > Signing in to Google > 2-Step Verification > On
    2) Generate app password for application use
    Manage your Google Account > Security > Signing in to Google > App passwords > GENERATE
    """

    USER_ENV_KEY = 'GMAIL_USER'
    PASSWD_ENV_KEY = 'GMAIL_PASSWD'

    GMAIL_TO_ENV_KEY = 'GMAIL_TO'
    GMAIL_SUBJECT_ENV_KEY = 'GMAIL_SUBJECT'
    GMAIL_MESSAGE_ENV_KEY = 'GMAIL_MESSAGE'
    GMAIL_MESSAGE_FROM_FILE_ENV_KEY = 'GMAIL_MESSAGE_FROM_FILE'

    date_format = '%m/%d/%Y %H:%M:%S'

    def __init__(self, user=None, password=None):
        self.user = user
        self.password = password
        assert self.user and self.password, 'User and password have to be declared'

    def __str__(self):
        return f'<{self.__class__.__name__} instance with username {self.user}>'

    def send(self, to, body, subject='Default subject') -> Exception or None:
        """
        to: string of single email address or multiple email addresses separated with comma
            e.g. to='hello@gmail.com'
                 to='first@gmail.com, second@gmail.com'

        body: string representing email body
        subject: string representing email subject
        """
        msg = EmailMessage()
        msg.set_content(body)

        msg['from'] = self.user
        msg['to'] = to
        msg['subject'] = subject

        try:

            with smtplib.SMTP(host='smtp.gmail.com', port=587) as server:
                server.starttls()  # Transport Layer Security mode. All SMTP commands that follow will be encrypted.
                server.login(user=self.user, password=self.password)  # Log in SMTP server that requires authentication
                server.send_message(msg)

        except smtplib.SMTPHeloError:
            raise Exception('The server didn’t reply properly to the HELO greeting.') from None
        except smtplib.SMTPAuthenticationError:
            raise Exception('The server didn’t accept the username/password combination.') from None
        except smtplib.SMTPSenderRefused:
            raise Exception('The server didn’t accept the from_addr. Wrong sender email.') from None
        except smtplib.SMTPRecipientsRefused:
            raise Exception(f'Not all provided reciepents are correct {to}') from None
        except Exception as e:
            raise Exception('Unexpected exception') from e

        else:
            addresses = [x.strip() for x in to.split(',')] if ',' in to else [to]
            for address in addresses:
                print(f'[{datetime.now().strftime(self.date_format)}] Email sent to {address} titled "{subject}"')

    @classmethod
    def create_gmail_parser(cls):
        """
        Helps to build command line interface common arguments for RedisGateway.

        To combine two parsers use 'parents' argument of argparse.ArgumentParser
        e.g.
            final_parser = argparse.ArgumentParser(conflict_handler='resolve', parents=[parser_A, parser_B])
            args = final_parser.parse_args()
        """
        from functools import partial
        if __name__ == '__main__':
            from common import JoinNargsCustomAction
        else:
            from .common import JoinNargsCustomAction

        parser = argparse.ArgumentParser()

        # User and password required when env variable weren't set
        parser.add_argument('--gmail_user', type=str,
                            default=os.getenv(cls.USER_ENV_KEY),
                            required=not already_defined_env_var(cls.USER_ENV_KEY),
                            help=f'Gmail account username. By default reads from "{cls.USER_ENV_KEY}" env variable.')
        parser.add_argument('--gmail_passwd', type=str,
                            default=os.getenv(cls.PASSWD_ENV_KEY),
                            required=not already_defined_env_var(cls.PASSWD_ENV_KEY),
                            help=f'Gmail account password. By default reads from "{cls.PASSWD_ENV_KEY}" env variable.')

        # Required only when env variable wasn't set
        join_with_comma = partial(JoinNargsCustomAction, join_with=', ')
        parser.add_argument('--gmail_to', nargs='+', type=str,
                            default=os.getenv(cls.GMAIL_TO_ENV_KEY),
                            required=not already_defined_env_var(cls.GMAIL_TO_ENV_KEY),
                            action=join_with_comma,
                            help='Receiver address(es). '
                                 'If multiple addresses type them in one after another using space to separate them.'
                                 f'By default reads from "{cls.GMAIL_TO_ENV_KEY}" env variable.')

        # Required only when env variable wasn't set
        join_with_space = partial(JoinNargsCustomAction, join_with=' ')
        parser.add_argument('--gmail_subject', nargs='+', type=str,
                            default=os.getenv(cls.GMAIL_SUBJECT_ENV_KEY),
                            required=not already_defined_env_var(cls.GMAIL_SUBJECT_ENV_KEY),
                            action=join_with_space,
                            help='Message subject'
                                 f'By default reads from "{cls.GMAIL_SUBJECT_ENV_KEY}" env variable.')

        # Mutually exclusive - one argument required when none was defined in env variables
        mutually_exclusive = (cls.GMAIL_MESSAGE_ENV_KEY, cls.GMAIL_MESSAGE_FROM_FILE_ENV_KEY)
        body_group = parser.add_mutually_exclusive_group(
            required=not any(already_defined_env_var(key) for key in mutually_exclusive))
        body_group.add_argument('--gmail_message', nargs='+', type=str,
                                default=os.getenv(cls.GMAIL_MESSAGE_ENV_KEY),
                                action=join_with_space,
                                help='Message body.'
                                     f'By default reads from "{cls.GMAIL_MESSAGE_ENV_KEY}" env variable.')
        body_group.add_argument('--gmail_message_from_file', type=str,
                                default=read_text_file(os.getenv(cls.GMAIL_MESSAGE_FROM_FILE_ENV_KEY)),
                                action=ReadFileCustomAction,
                                help='Path to text file storing message body.'
                                     f'By default reads from "{cls.GMAIL_MESSAGE_FROM_FILE_ENV_KEY}" env variable.')

        return parser


class ReadFileCustomAction(argparse.Action):
    """
    Custom action for argparse
    Made with: https://docs.python.org/3/library/argparse.html#action

    Read whole file based on filepath.
    Converts filepath argument from cli into single string value.
    """
    def __call__(self,  er, namespace, values, option_string=None):
        try:
            with open(values, 'r') as f:
                new_values = f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f'Cannot find {values} in current dir ({os.path.abspath(os.curdir)}).') from None
        except IOError:
            raise IOError(f'Error when trying to open {values}.') from None
        except BaseException as e:
            raise Exception('Undefined exception occured.') from e

        setattr(namespace, self.dest, new_values)


def read_text_file(path):
    if not path:
        return None
    if os.path.isfile(path):
        with open(path, 'r') as f:
            txt = f.read()
        return txt
    raise FileNotFoundError(f'Provided path ({path}) is not correct.')


def already_defined_env_var(key):
    """Returns boolean if key is defined env variable"""
    value = os.getenv(key, None)
    return True if value else False


if __name__ == '__main__':

    gmail_parser = Gmail.create_gmail_parser()
    args = gmail_parser.parse_args()

    user = args.gmail_user
    passwd = args.gmail_passwd

    gmail = Gmail(user, passwd)
    gmail.send(to=args.gmail_to,
               body=args.gmail_message or args.gmail_message_from_file,
               subject=args.gmail_subject)

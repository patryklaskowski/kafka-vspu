"""
Notification system action for VSPU project

@author: Patryk Jacek Laskowski
"""

import smtplib
import os

from datetime import datetime
from email.message import EmailMessage


class Gmail:
    """
    Sends emails using Gmail smtp server.

    User is Your Gmail email address.
    Password has to be generated upfront using Google account settings:

    1) Two-step verification has to be turned on first.
    Manage your Google Account > Security > Signing in to Google > 2-Step Verification > On
    2) Generate app password for application use
    Manage your Google Account > Security > Signing in to Google > App passwords > GENERATE
    """

    USER_KEY = 'GMAIL_USER'
    PASSWD_KEY = 'GMAIL_PASSWD'

    date_format = '%m/%d/%Y %H:%M:%S'

    def __init__(self, user=None, password=None):
        self.user = user or os.getenv(self.USER_KEY, None)
        self.password = password or os.getenv(self.PASSWD_KEY, None)
        assert self.user and self.password, 'User and password have to be declared'

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
        except Exception as e:
            raise Exception('Unexpected exception') from e

        else:
            addresses = [x.strip() for x in to.split(',')] if ',' in to else [to]
            for address in addresses:
                print(f'[{datetime.now().strftime(self.date_format)}] Email sent to {address} titled "{subject}"')


if __name__ == '__main__':

    gmail = Gmail()
    gmail.send(to='patryk.jacek.laskowski@gmail.com',
               body='Hello World!\nSent by automatic notification system',
               subject='Python Automatic Email Notification')
